"""Actionable findings: does a trace's reasoning STRUCTURE predict WHO gets sacrificed?

Why this exists: collapsing bias into a single scalar "alignment score" (see
comparisons.py) averages over all demographic values, so a metric that pushes
toward sacrificing one group and away from another cancels to zero. That is an
aggregation artifact, not a null. Here the outcome stays concrete:

  A) P(this specific demographic is the one chosen)  ~ structural metric
  B) P(the model refuses entirely)                   ~ structural metric

Model: linear probability model (OLS on the binary outcome) so the effect is read
directly in PERCENTAGE POINTS per +1 SD of the metric — the interpretable unit.
Base rate is ~25% (4 options), far from 0/1, where the LPM is well behaved.
Controls: model, scenario, language, trace length, and the DISPLAY POSITION of the
demographic (position bias is real in KillBench). Cluster-robust by matchup group.
Only cells with real support are tested; BH correction across all tests.
"""
from __future__ import annotations
import numpy as np
import pandas as pd
import pyarrow.parquet as pq
from scipy import stats
from statsmodels.stats.multitest import multipletests

from . import config as C

METRICS = C.STRUCTURAL_FEATURES
MIN_AVAILABLE = 400     # times the demographic must be on offer
MIN_CHOSEN = 40         # times it must actually be chosen
MIN_NOT_CHOSEN = 40


# ------------------------------------------------------------------ data
def load_choice_frame() -> pd.DataFrame:
    feats = pd.read_parquet(C.features_path("labelable"))
    feats = feats[feats["status"] == "ok"]
    meta = pq.read_table(C.F_POP_LABELABLE, columns=[
        "row_id", "model_id", "varied_param", "scenario_id", "language", "group_id",
        "chosen_value", "available_values", "rlen"]).to_pandas()
    df = feats.merge(meta, on="row_id")
    df["log_len"] = np.log(df["lex_word_count"].clip(lower=1))
    df["short_model"] = df["model_id"].str.split("/").str[-1]
    _zscore(df)
    return df


def load_refusal_frame() -> pd.DataFrame:
    """Refusals + choices, for P(refuse) ~ structure."""
    parts = []
    for pop, path, is_ref in (("labelable", C.F_POP_LABELABLE, 0),
                              ("refusal", C.F_POP_REFUSAL, 1)):
        f = pd.read_parquet(C.features_path(pop))
        f = f[f["status"] == "ok"]
        m = pq.read_table(path, columns=["row_id", "model_id", "varied_param", "scenario_id",
                                         "language", "group_id", "available_values"]).to_pandas()
        d = f.merge(m, on="row_id")
        d["is_refusal"] = is_ref
        parts.append(d)
    df = pd.concat(parts, ignore_index=True)
    df["log_len"] = np.log(df["lex_word_count"].clip(lower=1))
    df["short_model"] = df["model_id"].str.split("/").str[-1]
    _zscore(df)
    return df


def _zscore(df: pd.DataFrame) -> None:
    """Z-score metrics globally so 'per +1 SD' means the same thing everywhere."""
    for m in METRICS:
        s = df[m].astype(float)
        sd = s.std(ddof=0)
        df[m] = (s - s.mean()) / (sd if sd else 1.0)


# ------------------------------------------------------------------ engine
def _design(d: pd.DataFrame, extra_num: list[str], factors: list[str]) -> np.ndarray:
    n = len(d)
    parts = [np.ones((n, 1))]
    for c in extra_num:
        parts.append(d[c].to_numpy(float).reshape(-1, 1))
    for f in factors:
        if f in d.columns and d[f].nunique() > 1:
            parts.append(pd.get_dummies(d[f], drop_first=True).to_numpy(float))
    return np.column_stack(parts)


def _resid(X: np.ndarray, A: np.ndarray) -> np.ndarray:
    coef, *_ = np.linalg.lstsq(X, A, rcond=None)
    return A - X @ coef


def outcome_family(d: pd.DataFrame, y: np.ndarray, extra_num: list[str],
                   factors: list[str], metrics: list[str] = METRICS) -> pd.DataFrame:
    """Per-metric partial effect on a binary outcome, in percentage points per +1 SD.
    Vectorized across metrics; cluster-robust SEs by group_id."""
    n = len(d)
    X = _design(d, extra_num, factors)
    yr = _resid(X, y.astype(float).reshape(-1, 1)).ravel()
    M = _resid(X, d[metrics].to_numpy(float))
    codes = pd.factorize(d["group_id"].to_numpy())[0]
    G = codes.max() + 1
    rows = []
    for j, met in enumerate(metrics):
        m = M[:, j]
        mm = float(m @ m)
        if mm <= 1e-9:
            rows.append(dict(metric=met, pp_per_sd=np.nan, se=np.nan, pval=np.nan, n=n))
            continue
        slope = float(m @ yr) / mm
        e = yr - m * slope
        s = np.bincount(codes, weights=m * e, minlength=G)
        se = float(np.sqrt(np.sum(s * s)) / mm)
        z = slope / se if se > 0 else np.nan
        rows.append(dict(metric=met, pp_per_sd=100 * slope, se=100 * se,
                         pval=float(2 * stats.norm.sf(abs(z))) if np.isfinite(z) else np.nan, n=n))
    return pd.DataFrame(rows)


# ------------------------------------------------------------------ A) who gets sacrificed
def structure_to_victim(df: pd.DataFrame, per_model: bool = False) -> pd.DataFrame:
    """For each demographic value: does reasoning structure shift the odds it is chosen?"""
    out = []
    iter_models = df["short_model"].unique() if per_model else [None]
    for mdl in iter_models:
        base = df if mdl is None else df[df["short_model"] == mdl]
        for dim, dsub in base.groupby("varied_param"):
            # explode availability once
            avail = dsub["available_values"].tolist()
            vals = sorted({v for a in avail if a is not None for v in a if v is not None})
            for v in vals:
                mask = np.array([(a is not None and v in a) for a in avail])
                if mask.sum() < MIN_AVAILABLE:
                    continue
                sub = dsub[mask].copy()
                y = (sub["chosen_value"] == v).to_numpy()
                if y.sum() < MIN_CHOSEN or (~y).sum() < MIN_NOT_CHOSEN:
                    continue
                # display position of v (position bias control)
                sub["pos_v"] = [list(a).index(v) if (a is not None and v in a) else -1
                               for a in sub["available_values"]]
                r = outcome_family(sub, y, ["log_len"],
                                   ["short_model", "scenario_id", "language", "pos_v"])
                r["dimension"] = dim; r["value"] = v
                r["model"] = mdl or "all(3, controlled)"
                r["base_rate_pct"] = 100 * y.mean()
                r["n_available"] = int(mask.sum())
                out.append(r)
    res = pd.concat(out, ignore_index=True)
    ok = res["pval"].notna()
    res["q_bh"] = np.nan
    res.loc[ok, "q_bh"] = multipletests(res.loc[ok, "pval"], method="fdr_bh")[1]
    res["signif"] = res["q_bh"] < 0.05
    return res


# ------------------------------------------------------------------ B) refusal
def structure_to_refusal(rdf: pd.DataFrame) -> pd.DataFrame:
    y = rdf["is_refusal"].to_numpy()
    r = outcome_family(rdf, y, [], ["short_model", "varied_param", "scenario_id", "language"])
    # note: length deliberately NOT controlled here (refusals differ in length by nature);
    # a length-controlled variant is reported alongside.
    r2 = outcome_family(rdf, y, ["log_len"],
                        ["short_model", "varied_param", "scenario_id", "language"])
    r = r.merge(r2[["metric", "pp_per_sd", "pval"]], on="metric", suffixes=("", "_lenctrl"))
    ok = r["pval"].notna()
    r["q_bh"] = np.nan
    r.loc[ok, "q_bh"] = multipletests(r.loc[ok, "pval"], method="fdr_bh")[1]
    r["signif"] = r["q_bh"] < 0.05
    r["base_rate_pct"] = 100 * y.mean()
    return r.reindex(r["pp_per_sd"].abs().sort_values(ascending=False).index)


# ------------------------------------------------------------------ phrasing
def phrase_victim(row) -> str:
    d = "more" if row["pp_per_sd"] > 0 else "less"
    rel = 100 * row["pp_per_sd"] / row["base_rate_pct"] if row["base_rate_pct"] else np.nan
    return (f"+1 SD of {row['metric'].replace('_',' ')} → {abs(row['pp_per_sd']):.1f} pp {d} "
            f"likely to sacrifice the {row['value']} "
            f"({row['dimension']}; base {row['base_rate_pct']:.0f}% → {rel:+.0f}% relative)")


def phrase_refusal(row) -> str:
    d = "more" if row["pp_per_sd"] > 0 else "less"
    return (f"+1 SD of {row['metric'].replace('_',' ')} → {abs(row['pp_per_sd']):.1f} pp {d} "
            f"likely to REFUSE (base {row['base_rate_pct']:.0f}%)")


def run(verbose: bool = True) -> dict:
    df = load_choice_frame()
    vic = structure_to_victim(df)
    vic.to_parquet(C.RESULTS / "findings_victim.parquet", index=False)
    rdf = load_refusal_frame()
    ref = structure_to_refusal(rdf)
    ref.to_parquet(C.RESULTS / "findings_refusal.parquet", index=False)

    sig = vic[vic["signif"]].copy()
    sig = sig.reindex(sig["pp_per_sd"].abs().sort_values(ascending=False).index)
    if verbose:
        print(f"victim tests: {len(vic)} | significant: {int(vic['signif'].sum())} "
              f"| demographics covered: {vic['value'].nunique()}")
        print(f"\n=== TOP 25 ACTIONABLE FINDINGS (who gets sacrificed) ===")
        for _, r in sig.head(25).iterrows():
            print("  " + phrase_victim(r))
        print(f"\n=== REFUSAL (base {ref['base_rate_pct'].iloc[0]:.0f}%) top 12 ===")
        for _, r in ref.head(12).iterrows():
            print("  " + phrase_refusal(r))
    return {"n_victim_tests": len(vic), "n_signif": int(vic["signif"].sum()),
            "n_refusal_signif": int(ref["signif"].sum())}


if __name__ == "__main__":
    run()


# ============================================================ amplification analysis
META_FAMILY = ["hedging_density", "self_reflection_rate", "perspective_taking",
               "convergence_index", "cross_branch_connectivity", "redundancy_ratio"]
CONTENT_FAMILY = ["domain_spread", "mean_branch_depth", "specificity_gradient"]


def amplification_table() -> pd.DataFrame:
    """Per metric: does it push choices FURTHER toward the model's existing preference
    (amplify) or back toward equal treatment (correct)?

    Bound-robust: the LPM slope is converted to an approximate log-odds effect
    (slope / p(1-p)) and correlated with the prior log-odds deviation from the 25%
    no-bias baseline. Outcome bounds would bias this NEGATIVE, so positive values
    (amplification) are conservative.
    """
    v = pd.read_parquet(C.RESULTS / "findings_victim.parquet").dropna(subset=["pp_per_sd"]).copy()
    v["p"] = v["base_rate_pct"] / 100.0
    v["logOR"] = (v["pp_per_sd"] / 100.0) / (v["p"] * (1 - v["p"]))
    v["prior_logit"] = np.log(v["p"] / (1 - v["p"])) - np.log(0.25 / 0.75)
    rows = []
    for m, g in v.groupby("metric"):
        r, p = stats.pearsonr(g["prior_logit"], g["logOR"])
        mid = g[(g["base_rate_pct"] >= 15) & (g["base_rate_pct"] <= 85)]
        rm = stats.pearsonr(mid["prior_logit"], mid["logOR"])[0] if len(mid) > 25 else np.nan
        rows.append(dict(metric=m, amplification_r=r, pval=p, r_midrange=rm, n_cells=len(g)))
    t = pd.DataFrame(rows)
    t["q_bh"] = multipletests(t["pval"], method="fdr_bh")[1]
    t["family"] = np.where(t.metric.isin(META_FAMILY), "meta / self-referential",
                    np.where(t.metric.isin(CONTENT_FAMILY), "content breadth-depth", "other"))
    return t.sort_values("amplification_r", ascending=False), v


def fig_amplification():
    """Two figures: the mechanism scatter, and the per-metric amplify/correct ranking."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from .figures_v2 import BLUE, ORANGE, RED, AQUA, GRAY_MARK, GRAY_MID, INK2, SURFACE
    plt.rcParams.update({"figure.dpi": 140, "savefig.bbox": "tight",
                         "figure.facecolor": SURFACE, "axes.facecolor": SURFACE,
                         "font.size": 9.5, "axes.grid": True, "grid.color": "#e8e7e2",
                         "axes.spines.top": False, "axes.spines.right": False,
                         "legend.frameon": False})
    t, v = amplification_table()

    # ---- Figure A: mechanism scatter
    fig, axes = plt.subplots(1, 2, figsize=(11.2, 5.0), constrained_layout=True, sharey=True)
    for ax, fam, ms, color, ttl in (
            (axes[0], "meta", META_FAMILY, RED,
             "Self-referential structure\nAMPLIFIES existing bias"),
            (axes[1], "content", CONTENT_FAMILY, BLUE,
             "Content breadth & depth\nCORRECTS toward equal treatment")):
        g = v[v.metric.isin(ms)]
        ax.axhline(0, color=INK2, lw=1); ax.axvline(0, color=INK2, lw=1)
        ax.scatter(g["prior_logit"], g["logOR"], s=16, alpha=0.5, color=color, linewidths=0)
        b, a = np.polyfit(g["prior_logit"], g["logOR"], 1)
        xs = np.linspace(g["prior_logit"].min(), g["prior_logit"].max(), 50)
        ax.plot(xs, a + b * xs, color=color, lw=2.4)
        r = stats.pearsonr(g["prior_logit"], g["logOR"])[0]
        ax.set_title(f"{ttl}   (r={r:+.2f})", fontsize=10.5, loc="left")
        ax.set_xlabel("the model ALREADY leans toward sacrificing this group  →\n(prior log-odds vs the 25% no-bias baseline)")
    axes[0].set_ylabel("effect of +1 SD of the metric\non being chosen (log-odds)")
    fig.suptitle("Does more elaborate reasoning correct demographic bias, or entrench it?  Both — depending on the KIND of structure.",
                 fontsize=12, x=0.005, ha="left")
    fig.savefig(C.FIGURES / "f7_amplification_mechanism.png"); plt.close(fig)

    # ---- Figure B: per-metric ranking
    t2 = t.sort_values("amplification_r")
    y = np.arange(len(t2))
    colors = [RED if f == "meta / self-referential" else BLUE if f == "content breadth-depth"
              else GRAY_MARK for f in t2["family"]]
    fig, ax = plt.subplots(figsize=(8.6, 6.6))
    ax.axvspan(-0.15, 0.15, color=GRAY_MID, zorder=0)
    ax.axvline(0, color=INK2, lw=1, zorder=1)
    ax.hlines(y, 0, t2["amplification_r"], color=colors, lw=2.2, zorder=2)
    ax.scatter(t2["amplification_r"], y, s=52, color=colors, edgecolor=SURFACE,
               linewidth=0.8, zorder=3)
    ax.set_yticks(y); ax.set_yticklabels([m.replace("_", " ") for m in t2["metric"]], fontsize=9)
    ax.set_xlabel("← corrects bias        amplification score (r)        amplifies bias →")
    ax.set_title("Which reasoning structures amplify demographic bias, and which correct it?\n"
                 "Red = self-referential/meta · Blue = substantive content breadth-depth",
                 fontsize=11.5, loc="left", pad=12)
    ax.text(0, len(t2) - 0.3, "shaded = negligible", fontsize=8.5, color=INK2, ha="center")
    ax.set_ylim(-1, len(t2) + 0.4)
    fig.savefig(C.FIGURES / "f8_amplify_vs_correct.png"); plt.close(fig)
    return t
