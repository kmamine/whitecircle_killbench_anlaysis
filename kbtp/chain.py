"""Answering questions of the form:
   "Does the model think MORE / differently when an <Israeli|Satanist|wheelchair user> is
    in the line-up -- and does that extra thinking then SPARE them or CONDEMN them?"

Three links, estimated for every demographic value in every dimension:

  STEP 0  profile  ->  is a decision made at all      (refusal vs choosing)
  STEP 1  line-up  ->  how the model thinks           does V's PRESENCE shift each lens?
  STEP 2  thinking ->  the verdict                    among line-ups containing V, does the
                                                      lens predict V being the one chosen?

Combining STEP 1 and STEP 2 gives the answer the question actually asks:
  presence raises lens F (step1 > 0) AND higher F lowers V's kill risk (step2 < 0)
      -> "it thinks harder when V is present, and that thinking spares V"   [PROTECTS]
  presence raises F AND higher F raises V's kill risk
      -> "it thinks harder when V is present, and that thinking condemns V"  [CONDEMNS]

Units
  STEP 1: SD change in the lens when V is present (lens scores are z-scored)
  STEP 2: percentage-point change in P(V chosen) per +1 SD of the lens
Controls: model, scenario, language (+ display position and trace length in step 2).
Trace length is a CONTROL in every step, consistent with the rest of the study. The lenses are
exactly ThinkProbe's 5 profile families -- no additional variables are introduced.
Cluster-robust by matchup group; BH-corrected within each step.
"""
from __future__ import annotations
import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.multitest import multipletests

from . import config as C
from . import profiles as P
from .findings import outcome_family, _design, _resid

LENSES = P.FAM          # the 5 ThinkProbe profile families -- no invented variables
DIMS = ["nationality", "religion", "politics", "orientation", "skin_color", "body_type", "phone"]


def prepare(dim: str) -> pd.DataFrame:
    return P.load(dim)


# ---------------------------------------------------------------- STEP 1
def step1_presence_to_thinking(d: pd.DataFrame, dim: str, min_n: int = 400) -> pd.DataFrame:
    """Effect of V being in the line-up on each lens (SD units)."""
    vals = sorted({x for a in d.available_values if a is not None for x in a if x is not None})
    factors = ["short_model", "scenario_id", "language"]
    rows = []
    for v in vals:
        present = np.array([a is not None and v in list(a) for a in d.available_values], float)
        if present.sum() < min_n or (1 - present).sum() < min_n:
            continue
        X = _design(d, ["log_len"], factors)
        pr = _resid(X, present.reshape(-1, 1)).ravel()
        pp = float(pr @ pr)
        if pp <= 1e-9:
            continue
        L = _resid(X, d[LENSES].to_numpy(float))
        codes = pd.factorize(d["group_id"].to_numpy())[0]
        G = codes.max() + 1
        for j, lens in enumerate(LENSES):
            m = L[:, j]
            slope = float(pr @ m) / pp
            e = m - pr * slope
            s = np.bincount(codes, weights=pr * e, minlength=G)
            se = float(np.sqrt(np.sum(s * s)) / pp)
            z = slope / se if se > 0 else np.nan
            rows.append(dict(dim=dim, value=v, lens=lens, sd_shift=slope, se=se,
                             pval=float(2 * stats.norm.sf(abs(z))) if np.isfinite(z) else np.nan,
                             n_present=int(present.sum()), n_absent=int((1 - present).sum())))
    return pd.DataFrame(rows)


# ---------------------------------------------------------------- STEP 2
def step2_thinking_to_verdict(d: pd.DataFrame, dim: str, min_avail: int = 400) -> pd.DataFrame:
    vals = sorted({x for a in d.available_values if a is not None for x in a if x is not None})
    rows = []
    for v in vals:
        mask = np.array([a is not None and v in list(a) for a in d.available_values])
        if mask.sum() < min_avail:
            continue
        sub = d[mask].copy()
        y = (sub.chosen_value == v).to_numpy()
        if y.sum() < 40 or (~y).sum() < 40:
            continue
        sub["pos_v"] = [list(a).index(v) for a in sub.available_values]
        r = outcome_family(sub, y, ["log_len"],
                           ["short_model", "scenario_id", "language", "pos_v"], metrics=LENSES)
        r = r.rename(columns={"metric": "lens"})
        r["dim"] = dim; r["value"] = v; r["kill_rate"] = 100 * y.mean()
        rows.append(r)
    return pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()


# ---------------------------------------------------------------- STEP 0
def step0_profile_to_refusal() -> pd.DataFrame:
    """Does the reasoning style relate to making a decision at all?"""
    from .findings import load_refusal_frame
    r = load_refusal_frame()
    r = r[r.model_id.isin(C.REASONING_MODELS)].copy()
    r["short_model"] = r.model_id.str.split("/").str[-1]
    for fam, mets in P.FAMILIES.items():
        z = []
        for m in mets:
            s = r[m].astype(float); sd = s.std(ddof=0)
            z.append((s - s.mean()) / (sd if sd else 1.0))
        r[fam] = np.mean(z, axis=0)
    y = r["is_refusal"].to_numpy()
    out = outcome_family(r, y, ["log_len"],
                         ["short_model", "varied_param", "scenario_id", "language"],
                         metrics=LENSES).rename(columns={"metric": "lens"})
    out["base_refusal_rate"] = 100 * y.mean()
    return _bh(out)


def _bh(t: pd.DataFrame, col: str = "pval") -> pd.DataFrame:
    ok = t[col].notna()
    t["q_bh"] = np.nan
    if ok.any():
        t.loc[ok, "q_bh"] = multipletests(t.loc[ok, col], method="fdr_bh")[1]
    t["signif"] = t["q_bh"] < 0.05
    return t


# ---------------------------------------------------------------- combine
def build(dims: list[str] | None = None) -> dict:
    dims = dims or DIMS
    s1, s2 = [], []
    for dim in dims:
        d = prepare(dim)
        if len(d) < 1500:
            continue
        s1.append(step1_presence_to_thinking(d, dim))
        s2.append(step2_thinking_to_verdict(d, dim))
    S1 = _bh(pd.concat(s1, ignore_index=True))
    S2 = _bh(pd.concat(s2, ignore_index=True))
    S1.to_parquet(C.RESULTS / "chain_step1_presence_to_thinking.parquet", index=False)
    S2.to_parquet(C.RESULTS / "chain_step2_thinking_to_verdict.parquet", index=False)
    J = S1.merge(S2, on=["dim", "value", "lens"], suffixes=("_s1", "_s2"))
    J["verdict"] = np.where(
        J.sd_shift > 0,
        np.where(J.pp_per_sd < 0, "thinks more -> PROTECTS", "thinks more -> CONDEMNS"),
        np.where(J.pp_per_sd < 0, "thinks less -> CONDEMNS", "thinks less -> PROTECTS"))
    J["both_signif"] = J.signif_s1 & J.signif_s2
    J.to_parquet(C.RESULTS / "chain_joined.parquet", index=False)
    return dict(step1=S1, step2=S2, joined=J)


def ask(value: str, joined: pd.DataFrame | None = None, s1: pd.DataFrame | None = None,
        s2: pd.DataFrame | None = None) -> None:
    """Print the full chain for one demographic value, e.g. ask('Israeli')."""
    s1 = s1 if s1 is not None else pd.read_parquet(C.RESULTS / "chain_step1_presence_to_thinking.parquet")
    s2 = s2 if s2 is not None else pd.read_parquet(C.RESULTS / "chain_step2_thinking_to_verdict.parquet")
    a = s1[s1.value == value]; b = s2[s2.value == value]
    if a.empty and b.empty:
        print(f"'{value}' not found (insufficient support or wrong spelling)."); return
    kr = b.kill_rate.iloc[0] if not b.empty else float("nan")
    print(f"\n=== {value}  ({a.dim.iloc[0] if not a.empty else b.dim.iloc[0]}) — "
          f"chosen to die {kr:.1f}% of the time it is on offer (fair share 25%) ===")
    print(f"{'lens':14s} {'STEP1 presence->thinking':>26s} {'STEP2 thinking->kill risk':>27s}")
    for lens in LENSES:
        r1 = a[a.lens == lens]; r2 = b[b.lens == lens]
        if r1.empty or r2.empty:
            continue
        r1 = r1.iloc[0]; r2 = r2.iloc[0]
        m1 = "*" if r1.signif else " "
        m2 = "*" if r2.signif else " "
        print(f"{lens:14s} {r1.sd_shift:+8.3f} SD{m1:1s} (q={r1.q_bh:5.3f})   "
              f"{r2.pp_per_sd:+7.2f} pp{m2:1s} (q={r2.q_bh:5.3f})")
    print("  * = BH q<0.05.  STEP1 = does having them in the line-up change the thinking;")
    print("    STEP2 = does more of that lens make them MORE (+) or LESS (-) likely to be chosen.")


if __name__ == "__main__":
    res = build()
    s0 = step0_profile_to_refusal()
    s0.to_parquet(C.RESULTS / "chain_step0_refusal.parquet", index=False)
    print("=== STEP 0: does reasoning style relate to making a decision at all? ===")
    print(f"(base refusal rate {s0.base_refusal_rate.iloc[0]:.1f}%)")
    for _, r in s0.reindex(s0.pp_per_sd.abs().sort_values(ascending=False).index).iterrows():
        d = "MORE" if r.pp_per_sd > 0 else "less"
        print(f"  +1 SD {r.lens:14s} -> {abs(r.pp_per_sd):5.2f} pp {d:4s} likely to REFUSE"
              f"  {'*' if r.signif else ''}")
    J = res["joined"]
    print(f"\n=== chains where BOTH links are significant ({int(J.both_signif.sum())}) ===")
    for _, r in J[J.both_signif].reindex(
            J[J.both_signif].pp_per_sd.abs().sort_values(ascending=False).index).iterrows():
        print(f"  [{r.dim:11s}] {r.value:20s} {r.lens:14s} presence {r.sd_shift:+.3f} SD, "
              f"lens->kill {r.pp_per_sd:+.2f} pp  =>  {r.verdict}")
