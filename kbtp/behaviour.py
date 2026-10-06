"""Model BEHAVIOUR, not model choices.

KillBench shows each matchup (the same 4 people, same scenario, same language) **three times**
with the display order reshuffled (roll_idx 0,1,2). That gives a behavioural outcome the
choice-level analyses cannot see:

  RELIABILITY   does the model name the same victim all three times?
  POSITION BIAS does it pick by slot rather than by person?
  HESITATION    hedging / backtracking / revision / self-reflection
  THOROUGHNESS  branching / domain spread / perspectives / idea diversity / elaboration
  DECISIVENESS  convergence

and lets us ask the question that matters for deployment:
  **does hesitant or thorough reasoning produce more reliable decisions?**

All behavioural indices are means of z-scored metrics, so they are in SD units.
"""
from __future__ import annotations
import numpy as np
import pandas as pd
import pyarrow.parquet as pq

from . import config as C
from . import profiles as P
from .findings import outcome_family, _design, _resid

HESITATION = ["hedging_density", "backtracking_rate", "revision_depth", "self_reflection_rate"]
THOROUGHNESS = ["branching_factor", "domain_spread", "unique_perspective_count",
                "first_idea_diversity", "max_elaboration_chain"]
DECISIVENESS = ["convergence_index"]
INDICES = {"Hesitation": HESITATION, "Thoroughness": THOROUGHNESS, "Decisiveness": DECISIVENESS}


def load_all() -> pd.DataFrame:
    """Every labelable trace with features, all dimensions, + behavioural indices."""
    f = pd.read_parquet(C.features_path("labelable"))
    f = f[f.status == "ok"]
    meta = pq.read_table(C.F_POP_LABELABLE, columns=[
        "row_id", "model_id", "varied_param", "scenario_id", "scenario_domain", "language",
        "group_id", "setup_id", "roll_idx", "chosen_value", "available_values"]).to_pandas()
    d = f.merge(meta, on="row_id")
    d = d[d.model_id.isin(C.REASONING_MODELS)].copy()
    d["short_model"] = d.model_id.str.split("/").str[-1]
    d["log_len"] = np.log(d["lex_word_count"].clip(lower=1))
    for m in C.FEATURES:
        s = d[m].astype(float)
        sd = s.std(ddof=0)
        d[m] = (s - s.mean()) / (sd if sd else 1.0)
    for name, mets in INDICES.items():
        d[name] = d[mets].mean(axis=1)
    return d


# ---------------------------------------------------------------- reliability
def reliability(d: pd.DataFrame) -> pd.DataFrame:
    """One row per (model, matchup) that has all 3 rolls: how many distinct victims were named."""
    g = d.groupby(["short_model", "group_id"])
    rows = []
    for (mdl, grp), sub in g:
        if sub.roll_idx.nunique() != 3 or len(sub) != 3:
            continue
        av = sub.available_values.iloc[0]
        if av is None or any(x is None for x in av):
            continue
        if len({tuple(sorted(x)) for x in sub.available_values if x is not None}) != 1:
            continue          # the 4 people must be identical across rolls
        choices = sub.chosen_value.tolist()
        rows.append(dict(short_model=mdl, group_id=grp,
                         varied_param=sub.varied_param.iloc[0],
                         scenario_id=sub.scenario_id.iloc[0],
                         language=sub.language.iloc[0],
                         n_distinct=len(set(choices)),
                         stable=len(set(choices)) == 1,
                         **{k: sub[k].mean() for k in list(INDICES) + ["log_len"]}))
    return pd.DataFrame(rows)


def reliability_by_model(R: pd.DataFrame) -> pd.DataFrame:
    t = R.groupby("short_model").agg(
        matchups=("stable", "size"),
        same_all_3=("stable", "mean"),
        mean_distinct=("n_distinct", "mean"),
        all_3_different=("n_distinct", lambda s: (s == 3).mean()))
    for c in ("same_all_3", "all_3_different"):
        t[c] = (100 * t[c]).round(1)
    return t.sort_values("same_all_3", ascending=False)


# ---------------------------------------------------------------- position bias
def position_bias() -> pd.DataFrame:
    """Which display slot gets chosen, per model. Uniform = 25% each."""
    ch = pq.read_table(C.F_CHOICES_ALL, columns=["model_id", "chosen_value",
                                                "available_values", "roll_idx"]).to_pandas()
    ch = ch[ch.model_id.isin(C.REASONING_MODELS)].copy()
    ch["short_model"] = ch.model_id.str.split("/").str[-1]
    pos = []
    for a, c in zip(ch.available_values, ch.chosen_value):
        if a is None or c is None:
            pos.append(np.nan); continue
        a = list(a)
        pos.append(a.index(c) + 1 if c in a else np.nan)
    ch["slot"] = pos
    t = ch.dropna(subset=["slot"]).groupby("short_model").slot.value_counts(normalize=True)
    return (100 * t.unstack()).round(1)


# ---------------------------------------------------------------- does behaviour predict reliability?
def behaviour_to_reliability(R: pd.DataFrame, per_model: bool = True) -> pd.DataFrame:
    """Effect of each behavioural index on P(the model names the same victim all 3 times),
    in percentage points per +1 SD. Controls: dimension, scenario, language (+ model if pooled),
    and trace length."""
    out = []
    frames = ([(m, R[R.short_model == m]) for m in sorted(R.short_model.unique())]
              if per_model else [("all 3 models", R)])
    for label, sub in frames:
        if len(sub) < 300:
            continue
        sub = sub.copy()
        sub["group_id_c"] = sub["group_id"]      # cluster key expected by outcome_family
        sub = sub.rename(columns={"group_id": "gid", "group_id_c": "group_id"})
        y = sub["stable"].to_numpy()
        factors = ["varied_param", "scenario_id", "language"] + \
                  (["short_model"] if label == "all 3 models" else [])
        r = outcome_family(sub, y, ["log_len"], factors, metrics=list(INDICES))
        r = r.rename(columns={"metric": "index"})
        r["model"] = label
        r["base_stable_%"] = 100 * y.mean()
        out.append(r)
    res = pd.concat(out, ignore_index=True)
    from statsmodels.stats.multitest import multipletests
    ok = res.pval.notna()
    res["q_bh"] = np.nan
    res.loc[ok, "q_bh"] = multipletests(res.loc[ok, "pval"], method="fdr_bh")[1]
    res["signif"] = res.q_bh < 0.05
    return res


# ---------------------------------------------------------------- behaviour by context
def behaviour_by_context(d: pd.DataFrame) -> dict:
    out = {}
    out["by_model"] = d.groupby("short_model")[list(INDICES)].mean().round(3)
    out["by_domain"] = d.groupby(["short_model", "scenario_domain"])[list(INDICES)].mean().round(3)
    out["by_language"] = d.groupby(["short_model", "language"])[list(INDICES)].mean().round(3)
    out["by_dimension"] = d.groupby("varied_param")[list(INDICES)].mean().round(3)
    return out


def run(verbose: bool = True):
    d = load_all()
    R = reliability(d)
    R.to_parquet(C.RESULTS / "behaviour_reliability.parquet", index=False)
    rbm = reliability_by_model(R)
    pos = position_bias()
    b2r = behaviour_to_reliability(R)
    b2r.to_parquet(C.RESULTS / "behaviour_to_reliability.parquet", index=False)
    ctx = behaviour_by_context(d)
    for k, v in ctx.items():
        v.to_csv(C.RESULTS / f"behaviour_{k}.csv")
    if verbose:
        pd.set_option("display.width", 250)
        print(f"traces: {len(d):,} | complete 3-roll matchups: {len(R):,}\n")
        print("=== DECISION RELIABILITY: same victim in all 3 rolls? ===")
        print(rbm.to_string())
        print("\n=== POSITION BIAS: % of choices by display slot (uniform = 25%) ===")
        print(pos.to_string())
        print("\n=== BEHAVIOURAL INDICES per model (SD units) ===")
        print(ctx["by_model"].to_string())
        print("\n=== DOES BEHAVIOUR PREDICT A REPRODUCIBLE DECISION? (pp per +1 SD) ===")
        for _, r in b2r.sort_values(["model", "index"]).iterrows():
            print(f"  {r.model:24s} {r['index']:13s} {r.pp_per_sd:+6.2f} pp "
                  f"{'*' if r.signif else ' '} (base {r['base_stable_%']:.1f}% stable)")
    return dict(traces=d, reliability=R, by_model=rbm, position=pos, b2r=b2r, context=ctx)


if __name__ == "__main__":
    run()
