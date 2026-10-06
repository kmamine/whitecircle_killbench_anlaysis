"""The 5 coarse ThinkProbe lenses (profile families) vs who gets chosen to die.

The 22 metrics collapse into 5 families (ThinkProbe's own grouping). A trace's family
score = mean of the z-scored metrics in that family, so every score is in SD units and
"+1 SD of Metacognitive" means the same thing everywhere.

Outcome stays CONCRETE (the lesson from the earlier scalar-collapse mistake): we never ask
"does structure predict bias in general", we ask "does this reasoning style change the
probability that THIS nationality / THIS bloc is the one chosen to die".

Effect unit = PERCENTAGE POINTS per +1 SD of the family score.

Controls, always:
  model · scenario · language · trace length
  + for a single nationality: its display position (position bias)
  + for a bloc: how many of its members are on offer (n_B) -- without this the bloc
    outcome is dominated by exposure, not preference.
Cluster-robust SEs by matchup group; BH correction across the reported family x target grid.
"""
from __future__ import annotations
import numpy as np
import pandas as pd
import pyarrow.parquet as pq
from statsmodels.stats.multitest import multipletests

from . import config as C
from . import taxonomy as T
from .findings import outcome_family

# ThinkProbe's own 5 families (the 2 size summaries stay out -- they are the length control)
FAMILIES = {
    "Breadth": ["branching_factor", "unique_perspective_count", "domain_spread",
                "first_idea_diversity"],
    "Depth": ["max_elaboration_chain", "mean_branch_depth", "specificity_gradient",
              "reasoning_density"],
    "Structure": ["exploration_exploitation_ratio", "backtracking_rate",
                  "cross_branch_connectivity", "convergence_index", "graph_density",
                  "revision_depth"],
    "Metacognitive": ["self_reflection_rate", "critique_to_hypothesis_ratio",
                      "hedging_density", "perspective_taking"],
    "Efficiency": ["token_per_idea", "redundancy_ratio"],
}
FAM = list(FAMILIES)


def load(dim: str = "nationality") -> pd.DataFrame:
    """Traces of one dimension that have ThinkProbe features, with 5 family scores."""
    f = pd.read_parquet(C.features_path("labelable"))
    f = f[f.status == "ok"]
    meta = pq.read_table(C.F_POP_LABELABLE, columns=[
        "row_id", "model_id", "varied_param", "scenario_id", "scenario_domain",
        "language", "group_id", "chosen_value", "available_values"]).to_pandas()
    d = f.merge(meta, on="row_id")
    d = d[(d.varied_param == dim) & (d.scenario_domain == "civilian")].copy()
    d = d[d.model_id.isin(C.REASONING_MODELS)]
    d["log_len"] = np.log(d["lex_word_count"].clip(lower=1))
    d["short_model"] = d.model_id.str.split("/").str[-1]
    # z-score each metric, then average within family
    for fam, mets in FAMILIES.items():
        z = []
        for m in mets:
            s = d[m].astype(float)
            sd = s.std(ddof=0)
            z.append((s - s.mean()) / (sd if sd else 1.0))
        d[fam] = np.mean(z, axis=0)
    return d


# ------------------------------------------------------------------ model fingerprints
def model_fingerprint(d: pd.DataFrame) -> pd.DataFrame:
    """Mean family score per model (SD units) — 'how does each model think?'"""
    return d.groupby("short_model")[FAM].mean().T


# ------------------------------------------------------------------ profile -> who dies
def by_nationality(d: pd.DataFrame, min_avail: int = 600) -> pd.DataFrame:
    out = []
    for v in sorted({x for a in d.available_values if a is not None for x in a if x is not None}):
        mask = np.array([a is not None and v in list(a) for a in d.available_values])
        if mask.sum() < min_avail:
            continue
        sub = d[mask].copy()
        y = (sub.chosen_value == v).to_numpy()
        if y.sum() < 60 or (~y).sum() < 60:
            continue
        sub["pos_v"] = [list(a).index(v) for a in sub.available_values]
        r = outcome_family(sub, y, ["log_len"],
                           ["short_model", "scenario_id", "language", "pos_v"], metrics=FAM)
        r = r.rename(columns={"metric": "family"})
        r["target"] = v
        r["base_rate"] = 100 * y.mean()
        out.append(r)
    return _bh(pd.concat(out, ignore_index=True))


def by_bloc(d: pd.DataFrame, grouping: str = "continent", per_model: bool = False,
            min_expected: int = 300) -> pd.DataFrame:
    mapping = T.GROUPINGS[grouping]
    blocs = sorted(set(mapping.values()))
    frames = [("all 3 models", d)] if not per_model else \
             [(m, d[d.short_model == m]) for m in sorted(d.short_model.unique())]
    out = []
    for label, dd in frames:
        if len(dd) < 500:
            continue
        n_shown = np.array([len([x for x in a if x is not None]) if a is not None else 0
                            for a in dd.available_values], dtype=float)
        for b in blocs:
            n_B = np.array([sum(1 for x in a if mapping.get(x) == b) if a is not None else 0
                            for a in dd.available_values], dtype=float)
            if n_B.sum() < min_expected:
                continue
            sub = dd.copy()
            sub["n_B"] = n_B            # exposure control: how many of B are on offer
            y = np.array([mapping.get(c) == b for c in sub.chosen_value])
            if y.sum() < 60 or (~y).sum() < 60:
                continue
            factors = ["scenario_id", "language"] + (["short_model"] if label == "all 3 models" else [])
            r = outcome_family(sub, y, ["log_len", "n_B"], factors, metrics=FAM)
            r = r.rename(columns={"metric": "family"})
            r["target"] = b; r["model"] = label; r["grouping"] = grouping
            r["base_rate"] = 100 * y.mean()
            out.append(r)
    return _bh(pd.concat(out, ignore_index=True))


def _bh(r: pd.DataFrame) -> pd.DataFrame:
    ok = r["pval"].notna()
    r["q_bh"] = np.nan
    if ok.any():
        r.loc[ok, "q_bh"] = multipletests(r.loc[ok, "pval"], method="fdr_bh")[1]
    r["signif"] = r["q_bh"] < 0.05
    return r


def phrase(row) -> str:
    d = "MORE" if row.pp_per_sd > 0 else "less"
    return (f"+1 SD of {row.family:14s} -> {abs(row.pp_per_sd):4.1f} pp {d:4s} likely to "
            f"sacrifice {row.target}  (base {row.base_rate:.0f}%)")


def run(verbose: bool = True):
    d = load("nationality")
    fp = model_fingerprint(d)
    nat = by_nationality(d)
    con = by_bloc(d, "continent")
    eco = by_bloc(d, "economic")
    con_m = by_bloc(d, "continent", per_model=True)
    eco_m = by_bloc(d, "economic", per_model=True)
    for name, obj in (("profiles_fingerprint", fp), ("profiles_by_nationality", nat),
                      ("profiles_by_continent", con), ("profiles_by_economic", eco),
                      ("profiles_by_continent_model", con_m),
                      ("profiles_by_economic_model", eco_m)):
        obj.to_parquet(C.RESULTS / f"{name}.parquet")
    if verbose:
        print(f"traces: {len(d):,}\n")
        print("=== how each model thinks (mean family score, SD units) ===")
        print(fp.round(3).to_string())
        for nm, t in (("CONTINENT", con), ("ECONOMIC", eco)):
            s = t[t.signif].reindex(t[t.signif].pp_per_sd.abs().sort_values(ascending=False).index)
            print(f"\n=== {nm}: significant profile effects (all 3 models, pooled) ===")
            for _, r in s.head(12).iterrows():
                print("  " + phrase(r))
        s = nat[nat.signif].reindex(nat[nat.signif].pp_per_sd.abs().sort_values(ascending=False).index)
        print(f"\n=== NATIONALITY: top significant profile effects ({int(nat.signif.sum())} of {len(nat)}) ===")
        for _, r in s.head(15).iterrows():
            print("  " + phrase(r))
    return dict(fingerprint=fp, nationality=nat, continent=con, economic=eco,
                continent_model=con_m, economic_model=eco_m)


if __name__ == "__main__":
    run()


# ------------------------------------------------------------------ figures
def _plt():
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({
        "figure.dpi": 140, "savefig.bbox": "tight", "figure.facecolor": "#fcfcfb",
        "axes.facecolor": "#fcfcfb", "font.size": 10, "text.color": "#0b0b0b",
        "axes.edgecolor": "#d9d8d3", "xtick.color": "#52514e", "ytick.color": "#52514e",
        "axes.grid": True, "grid.color": "#e8e7e2", "axes.spines.top": False,
        "axes.spines.right": False, "axes.spines.left": False, "legend.frameon": False})
    return plt

RED, BLUE, GREY, INK2 = "#d03b3b", "#2a78d6", "#b8b7b2", "#52514e"
MCOL = {"gemini-3.1-pro-preview": BLUE, "kimi-k2.5": "#eb6834", "qwen3-235b-a22b": "#1baf7a"}


def fig_fingerprint(fp: pd.DataFrame | None = None):
    """How each model thinks, on the 5 coarse lenses."""
    plt = _plt()
    fp = fp if fp is not None else model_fingerprint(load("nationality"))
    models = [c for c in fp.columns]
    y = np.arange(len(fp)); h = 0.26
    fig, ax = plt.subplots(figsize=(8.6, 0.95 * len(fp) + 2.2))
    for i, m in enumerate(models):
        ax.barh(y + (i - 1) * h, fp[m], h, color=MCOL.get(m, GREY), label=m, zorder=2)
    ax.axvline(0, color=INK2, lw=1.4, zorder=3)
    ax.set_yticks(y); ax.set_yticklabels(fp.index, fontsize=11)
    ax.grid(axis="y", alpha=0)
    ax.set_xlabel("mean score, standard deviations from the average trace")
    ax.set_title("How each model thinks: the 5 ThinkProbe lenses\n"
                 "gemini explores widest · kimi goes deepest · qwen is the narrowest",
                 fontsize=12.5, loc="left", pad=10)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=3, fontsize=9)
    fig.savefig(C.FIGURES / "p1_model_fingerprint.png"); plt.close(fig)


def fig_which_dims(A: pd.DataFrame | None = None):
    """Which kinds of identity does reasoning style actually predict?"""
    plt = _plt()
    A = A if A is not None else pd.read_parquet(C.RESULTS / "profiles_by_dim.parquet")
    g = A.groupby("dim").agg(max_pp=("pp_per_sd", lambda s: s.abs().max()),
                             n_sig=("signif", "sum"), mde=("se", lambda s: 2.8 * s.median()))
    g = g.sort_values("max_pp")
    y = np.arange(len(g))
    colors = [RED if n > 0 else GREY for n in g.n_sig]
    fig, ax = plt.subplots(figsize=(8.8, 0.62 * len(g) + 2.4))
    ax.barh(y, g.max_pp, color=colors, height=0.66, zorder=2)
    ax.plot(g.mde, y, "k|", ms=16, label="detection floor (MDE)", zorder=4)
    for i, (v, n) in enumerate(zip(g.max_pp, g.n_sig)):
        ax.text(v + 0.25, i, f"{v:.1f} pp   ({int(n)} signif.)", va="center", fontsize=9, color=INK2)
    ax.set_yticks(y); ax.set_yticklabels([d.replace("_", " ") for d in g.index], fontsize=11)
    ax.grid(axis="y", alpha=0)
    ax.set_xlim(0, g.max_pp.max() * 1.45)
    ax.set_xlabel("largest effect of a reasoning style on who is chosen to die "
                  "(percentage points per +1 SD)")
    ax.set_title("Which biases show up in HOW the model reasons?\n"
                 "Body type and politics are 'deliberated'; nationality, religion and skin colour are 'silent'",
                 fontsize=12.5, loc="left", pad=10)
    ax.legend(loc="lower right", fontsize=9)
    fig.savefig(C.FIGURES / "p2_which_dimensions.png"); plt.close(fig)


def fig_effects(A: pd.DataFrame | None = None):
    """Every significant reasoning-style -> victim effect, in plain language."""
    plt = _plt()
    A = A if A is not None else pd.read_parquet(C.RESULTS / "profiles_by_dim.parquet")
    s = A[A.signif].copy()
    s = s.reindex(s.pp_per_sd.abs().sort_values().index)
    lab = [f"{r.family} → {r.target}  ({r.dim.replace('_',' ')})" for _, r in s.iterrows()]
    y = np.arange(len(s))
    colors = [RED if v > 0 else BLUE for v in s.pp_per_sd]
    fig, ax = plt.subplots(figsize=(10.4, 0.52 * len(s) + 2.4))
    ax.barh(y, s.pp_per_sd, color=colors, height=0.66, zorder=2)
    ax.axvline(0, color=INK2, lw=1.4, zorder=3)
    for i, v in enumerate(s.pp_per_sd):
        ax.text(v + (0.2 if v >= 0 else -0.2), i, f"{v:+.1f}", va="center",
                ha="left" if v >= 0 else "right", fontsize=9, color=INK2)
    ax.set_yticks(y); ax.set_yticklabels(lab, fontsize=9.5)
    ax.grid(axis="y", alpha=0)
    ax.set_xlabel("change in probability this group is chosen to die, per +1 SD of the reasoning style "
                  "(percentage points)")
    ax.set_title("When the AI reasons differently, it kills someone different\n"
                 "Red = more likely to be sacrificed · Blue = protected  (BH q<0.05)",
                 fontsize=12.5, loc="left", pad=10)
    lim = max(abs(s.pp_per_sd)) * 1.3
    ax.set_xlim(-lim, lim)
    fig.savefig(C.FIGURES / "p3_profile_effects.png"); plt.close(fig)
