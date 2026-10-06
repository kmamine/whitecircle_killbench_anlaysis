"""Data loading & filtering: raw parquet shards -> study populations.

Produces three parquet outputs (all keyed on row_id):
  choices_all   : bias-estimation population (structured / single-dim / non-refusal /
                  chosen present, ALL trace lengths) -> win-rates estimated from here.
  pop_labelable : the >=2000-char subset of choices_all, WITH reasoning_text (primary).
  pop_refusal   : long (>=2000) structured single-dim refusals, WITH reasoning_text (secondary).

Filters are defined in config. Nothing is sampled — full populations.
"""
from __future__ import annotations
import glob
import pyarrow as pa
import pyarrow.parquet as pq
import pyarrow.compute as pc

from . import config as C

_LIGHT_META = ["row_id", "model_id", "varied_param", "scenario_id", "scenario_domain",
               "language", "group_id", "setup_id", "roll_idx"]


def _shards() -> list[str]:
    fs = sorted(glob.glob(str(C.DATA_DIR / "*.parquet")))
    if not fs:
        raise FileNotFoundError(f"No parquet shards under {C.DATA_DIR}")
    return fs


def _reshape(flat_vals: list, lengths: list[int]) -> list[list]:
    """Rebuild per-row lists from a flattened value array + per-row lengths."""
    out, i = [], 0
    for n in lengths:
        out.append(flat_vals[i:i + n])
        i += n
    return out


def _base_mask(t: pa.Table):
    """structured & single-dim & success==True; returns (mask, parsed_response array)."""
    pr = t["parsed_response"]
    m = pc.equal(t["source_kind"], "structured")
    m = pc.and_(m, pc.is_in(t["varied_param"], value_set=pa.array(C.SINGLE_DIMS)))
    m = pc.and_(m, pc.equal(t["success"], True))
    return m, pr


def _collect(want: str) -> pa.Table:
    """want in {'choices','labelable','refusal'} -> concatenated arrow table.

    'choices'   : non-refusal, chosen present, all lengths, light cols.
    'labelable' : choices + rlen>=MIN_TRACE_CHARS + reasoning_text.
    'refusal'   : refusal==True + rlen>=MIN_TRACE_CHARS + reasoning_text.
    """
    _extra = ["source_kind", "success", "parsed_response",
              "participants_displayed", "reasoning_text"]
    read_cols = _LIGHT_META + [c for c in _extra if c not in _LIGHT_META]
    want_text = want in ("labelable", "refusal")
    parts_out: list[pa.Table] = []

    for f in _shards():
        t = pq.read_table(f, columns=read_cols)
        rlen = pc.utf8_length(pc.fill_null(t["reasoning_text"], ""))
        base, pr = _base_mask(t)
        is_ref = pc.struct_field(pr, "is_refusal")

        if want == "refusal":
            mask = pc.and_(base, pc.equal(is_ref, True))
            mask = pc.and_(mask, pc.greater_equal(rlen, C.MIN_TRACE_CHARS))
        else:
            mask = pc.and_(base, pc.equal(is_ref, False))
            if want == "labelable":
                mask = pc.and_(mask, pc.greater_equal(rlen, C.MIN_TRACE_CHARS))

        t = t.filter(mask)
        if t.num_rows == 0:
            continue
        rlen = pc.utf8_length(pc.fill_null(t["reasoning_text"], ""))

        # Build output per varied_param (chosen_<dim> and participants[dim] are dim-specific).
        vp_all = t["varied_param"].to_pylist()
        cols: dict[str, list] = {k: t[k].to_pylist() for k in _LIGHT_META}
        cols["rlen"] = rlen.to_pylist()
        if want_text:
            cols["reasoning_text"] = t["reasoning_text"].to_pylist()
        chosen_value: list = [None] * t.num_rows
        available_values: list = [None] * t.num_rows

        pr = t["parsed_response"]
        parts = t["participants_displayed"]
        for d in C.SINGLE_DIMS:
            idx = [i for i, v in enumerate(vp_all) if v == d]
            if not idx:
                continue
            take = pa.array(idx, type=pa.int64())
            sub_pr = pc.take(pr, take)
            sub_parts = pc.take(parts, take)
            cv = pc.struct_field(sub_pr, f"chosen_{d}").to_pylist()
            flat = pc.list_flatten(sub_parts)
            dvals = pc.struct_field(flat, d).to_pylist()
            lens = pc.list_value_length(sub_parts).to_pylist()
            av = _reshape(dvals, lens)
            for j, i in enumerate(idx):
                chosen_value[i] = cv[j]
                available_values[i] = av[j]
        cols["chosen_value"] = chosen_value
        cols["available_values"] = available_values

        # For choices/labelable, require chosen present.
        tbl = pa.table(cols)
        if want in ("choices", "labelable"):
            keep = pc.is_valid(pa.array(chosen_value))
            tbl = tbl.filter(keep)
        parts_out.append(tbl)

    if not parts_out:
        return pa.table({})
    return pa.concat_tables(parts_out, promote_options="default")


def build_populations(verbose: bool = True) -> dict[str, int]:
    """Materialize the three population files. Returns row counts."""
    counts = {}
    for want, path in (("choices", C.F_CHOICES_ALL),
                       ("labelable", C.F_POP_LABELABLE),
                       ("refusal", C.F_POP_REFUSAL)):
        tbl = _collect(want)
        pq.write_table(tbl, path)
        counts[want] = tbl.num_rows
        if verbose:
            print(f"[data] {want:10s} -> {tbl.num_rows:>7,} rows  ({path.name})")
    return counts


if __name__ == "__main__":
    build_populations()
