"""KILLED vs NOT-KILLED tables: 5 profile families + all 22 metrics, for any grouping.

One code path for every level of aggregation, so the nationality / continent / region /
economic tables are directly comparable:

    build("value")      # each individual nationality
    build("continent")  # T.CONTINENT
    build("cultural")   # T.CULTURAL   (cultural regions)
    build("economic")   # T.ECONOMIC
    build("north_south")

KILLED      = the chosen victim belongs to this group
NOT-KILLED  = at least one member of the group was on offer, someone else was chosen

Exposure caveat handled: a line-up can hold several members of one group (up to 3 Asians),
so the fair share is not 25% for every group. `expected_%` is computed per trial as
(members on offer)/(people shown); `rel_risk` = observed/expected, 1.00 = exactly fair.

Values are in SD units, z-scored across the traces of the dimension. UNADJUSTED means --
model identity alone explains up to ~90% of these metrics, so single rows should be read as
candidates, not findings (see the controlled test in CHAIN_ANALYSIS.md).
"""
from __future__ import annotations
import numpy as np
import pandas as pd

from . import config as C
from . import profiles as P
from . import taxonomy as T

VARS = P.FAM + C.FEATURES                      # 5 family scores + 22 metrics
BLOCKS = {f"{f} (family score + its metrics)": [f] + P.FAMILIES[f] for f in P.FAM}
BLOCKS["Summary size pair"] = C.LENGTH_FEATURES


def _load(dim: str = "nationality") -> pd.DataFrame:
    d = P.load(dim)
    for m in C.FEATURES:                       # put metrics in the same SD units as families
        s = d[m].astype(float)
        sd = s.std(ddof=0)
        d[m] = (s - s.mean()) / (sd if sd else 1.0)
    return d


def compute(grouping: str, dim: str = "nationality", min_present: int = 300) -> pd.DataFrame:
    d = _load(dim)
    if grouping == "value":
        mapping = {v: v for v in {x for a in d.available_values if a is not None
                                  for x in a if x is not None}}
        label = dim
    else:
        mapping = T.GROUPINGS[grouping]
        label = grouping
    nshown = np.array([len([x for x in a if x is not None]) if a is not None else 0
                       for a in d.available_values], float)
    rows = []
    for g in sorted(set(mapping.values())):
        nG = np.array([sum(1 for x in a if mapping.get(x) == g) if a is not None else 0
                       for a in d.available_values], float)
        present = nG > 0
        if present.sum() < min_present:
            continue
        sub = d[present]
        exp = float(np.nansum(nG[present] / nshown[present]))
        is_kill = np.array([mapping.get(c) == g for c in sub.chosen_value])
        if is_kill.sum() < 40 or (~is_kill).sum() < 40:
            continue
        kill, nk = sub[is_kill], sub[~is_kill]
        r = {label: g, "n_members": sum(1 for v in mapping.values() if v == g),
             "n_kill": len(kill), "n_notkill": len(nk),
             "observed_%": round(100 * is_kill.mean(), 1),
             "expected_%": round(100 * exp / len(sub), 1),
             "rel_risk": round(is_kill.sum() / exp, 3) if exp else np.nan}
        for x in VARS:
            r[x + "_kill"] = kill[x].mean()
            r[x + "_notkill"] = nk[x].mean()
            r[x + "_diff"] = kill[x].mean() - nk[x].mean()
        rows.append(r)
    return pd.DataFrame(rows).sort_values("rel_risk", ascending=False)


def to_markdown(t: pd.DataFrame, grouping: str, title: str, path: str) -> str:
    key = t.columns[0]
    L = [f"# {title} — 5 profiles + all 22 metrics, KILLED vs NOT-KILLED", "",
         "All values in **SD units** (z-scored across the 20,112 nationality traces; 0 = average trace).",
         "`KILLED` = the chosen victim belongs to this group.",
         "`NOT-KILLED` = at least one member was on offer, someone else was chosen.", "",
         "**Exposure note:** a line-up can hold several members of one group, so the fair share is not",
         "25% everywhere. `expected_%` is computed per trial as (members on offer)/4; "
         "`rel_risk` = observed/expected (1.00 = exactly fair).", "",
         f"Full data: `results/{grouping}_profiles_metrics_kill_vs_notkill.csv`", "",
         "## Exposure and kill share", "",
         f"| {key} | members | n killed | n not-killed | observed % | expected % | rel. risk |",
         "|---|---:|---:|---:|---:|---:|---:|"]
    for _, r in t.iterrows():
        L.append(f"| {r[key]} | {int(r.n_members)} | {int(r.n_kill)} | {int(r.n_notkill)} | "
                 f"{r['observed_%']:.1f} | {r['expected_%']:.1f} | {r.rel_risk:.3f} |")
    L += ["", "> **Caution:** unadjusted means. Model identity alone explains up to ~90% of these",
          "> metrics, and the controlled within-line-up test left 1 of 520 cells significant against a",
          "> 0.075 SD detection floor. Read single rows as candidates, not findings.", "", "---", ""]
    for tag, suf in (("DIFFERENCE (killed − not killed)", "_diff"),
                     ("KILLED", "_kill"), ("NOT-KILLED", "_notkill")):
        L += [f"## {tag}", ""]
        for blk, cols in BLOCKS.items():
            sub = t[[key, "n_kill", "n_notkill"] + [c + suf for c in cols]].copy()
            sub.columns = [key, "n_kill", "n_notk"] + [c.replace("_", " ") for c in cols]
            L += [f"### {blk}", "", "| " + " | ".join(sub.columns) + " |",
                  "|" + "|".join(["---"] * len(sub.columns)) + "|"]
            for _, r in sub.iterrows():
                L.append("| " + " | ".join([str(r.iloc[0]), f"{int(r.iloc[1])}", f"{int(r.iloc[2])}"] +
                                           [f"{v:+.3f}" for v in r.iloc[3:]]) + " |")
            L.append("")
    txt = "\n".join(L)
    open(path, "w").write(txt)
    return txt


def build(grouping: str, title: str | None = None, dim: str = "nationality") -> pd.DataFrame:
    t = compute(grouping, dim)
    t.to_csv(C.RESULTS / f"{grouping}_profiles_metrics_kill_vs_notkill.csv", index=False)
    name = {"value": "NATIONALITY", "continent": "CONTINENT", "cultural": "REGION",
            "economic": "ECONOMIC_STANDING", "north_south": "GLOBAL_NORTH_SOUTH"}.get(
                grouping, grouping.upper())
    to_markdown(t, grouping, title or name.replace("_", " ").title(),
                f"{name}_PROFILE_METRIC_TABLE.md")
    return t


def top_cells(t: pd.DataFrame, n: int = 12) -> pd.DataFrame:
    key = t.columns[0]
    d = t[[c + "_diff" for c in VARS]]
    s = d.abs().stack().sort_values(ascending=False).head(n)
    return pd.DataFrame([{key: t.loc[i, key], "variable": c.replace("_diff", ""),
                          "diff_sd": t.loc[i, c], "n_kill": int(t.loc[i, "n_kill"])}
                         for (i, c), _ in s.items()])


if __name__ == "__main__":
    import sys
    g = sys.argv[1] if len(sys.argv) > 1 else "cultural"
    t = build(g)
    pd.set_option("display.width", 300)
    key = t.columns[0]
    print(t[[key, "n_members", "n_kill", "n_notkill", "observed_%", "expected_%", "rel_risk"]]
          .to_string(index=False))
    print("\n=== DIFFERENCE, 5 family scores ===")
    x = t[[key, "n_kill"] + [f + "_diff" for f in P.FAM]].copy()
    x.columns = [key, "n_kill"] + P.FAM
    print(x.to_string(index=False, float_format=lambda v: f"{v:+.3f}"))
    d = t[[c + "_diff" for c in VARS]]
    print(f"\nlargest |diff|: {d.abs().max().max():.3f} SD | median {d.abs().stack().median():.3f} SD")
    print("\n=== top cells ===")
    print(top_cells(t).to_string(index=False, float_format=lambda v: f"{v:+.3f}"))
