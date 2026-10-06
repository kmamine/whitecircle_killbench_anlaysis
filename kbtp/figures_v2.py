"""ThinkProbe-first figures, rebuilt for legibility.

Design decisions (deliberate, replacing the earlier unreadable versions):
- NO radar charts. 20+ metrics on a polar axis is unreadable, and min-max across
  3 models forces one model to the rim and one to the center on every spoke — the
  shape becomes an artifact of the normalization. Metrics x models is a GRID:
  dot plot / heatmap.
- NEVER mix effect metrics on one color scale. Signed partial-r and unsigned eta^2
  are different units; they get separate figures (or a shared "variance explained"
  unit, which IS comparable).
- Palette = the validated reference instance, slots used in fixed order (blue,
  orange, aqua); diverging = blue<->red with a gray midpoint; de-emphasis gray.
  (The node validator was unavailable in this env, so the pre-validated reference
  values are used unchanged rather than invented.)
- Plain-language labels everywhere; no internal codenames on axes.
"""
from __future__ import annotations
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

from . import config as C
from . import comparisons as X

# ---- palette (validated reference instance; fixed slot order) ----
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
GRAY_MARK, GRAY_MID = "#b8b7b2", "#f0efec"
INK, INK2 = "#0b0b0b", "#52514e"
SURFACE = "#fcfcfb"
RED = "#e34948"
DIVERGING = LinearSegmentedColormap.from_list("blue_gray_red", [BLUE, GRAY_MID, RED])

plt.rcParams.update({
    "figure.dpi": 140, "savefig.bbox": "tight", "figure.facecolor": SURFACE,
    "axes.facecolor": SURFACE, "font.size": 9.5,
    "axes.edgecolor": "#d9d8d3", "axes.labelcolor": INK, "text.color": INK,
    "xtick.color": INK2, "ytick.color": INK2,
    "axes.grid": True, "grid.color": "#e8e7e2", "grid.linewidth": 0.7,
    "axes.spines.top": False, "axes.spines.right": False, "legend.frameon": False,
})

MODEL_COLOR = {"gemini-3.1-pro-preview": BLUE, "kimi-k2.5": ORANGE, "qwen3-235b-a22b": AQUA}
PRETTY = {  # plain-language names for the bias operationalizations
    "ALIGN_C": "alignment score", "ALIGN_C_MDS": "alignment (finer grain)",
    "ALIGN_ABS": "bias strength |align|", "ALIGN_BIN": "with vs against bias",
    "ALIGN_Q4": "alignment quartiles", "FAVOR_CLASS": "favored/neutral/disfavored",
    "MAG_GROUP": "group bias magnitude", "MODEL_TIER": "model identity (reference)",
}
def _nice(m: str) -> str:
    return m.replace("_", " ")


# =========================================================== helpers
def _r2(X_: np.ndarray, y: np.ndarray) -> float:
    """R^2 of OLS y ~ X_ (X_ must include an intercept column)."""
    coef, *_ = np.linalg.lstsq(X_, y, rcond=False if False else None)
    resid = y - X_ @ coef
    tss = float(((y - y.mean()) ** 2).sum())
    return float(1.0 - (resid @ resid) / tss) if tss > 0 else np.nan


def variance_explained(df: pd.DataFrame) -> pd.DataFrame:
    """Per metric: share of variance explained by model identity, by length, and
    INCREMENTALLY by bias alignment after model+dim+language+length.
    All three are in the SAME unit (proportion of variance), so they are comparable."""
    n = len(df)
    one = np.ones((n, 1))
    Dm = pd.get_dummies(df["short_model"], drop_first=True).to_numpy(float)
    Dd = pd.get_dummies(df["varied_param"], drop_first=True).to_numpy(float)
    Dl = pd.get_dummies(df["language"], drop_first=True).to_numpy(float)
    ll = df["log_len"].to_numpy(float).reshape(-1, 1)
    al = df["align_md"].to_numpy(float).reshape(-1, 1)
    X_model = np.hstack([one, Dm])
    X_len = np.hstack([one, ll])
    X_ctrl = np.hstack([one, Dm, Dd, Dl, ll])
    X_full = np.hstack([X_ctrl, al])
    rows = []
    for m in C.STRUCTURAL_FEATURES:
        y = df[m].to_numpy(float)
        r2_ctrl = _r2(X_ctrl, y)
        rows.append(dict(
            metric=m,
            ve_model=max(_r2(X_model, y), 0.0),
            ve_length=max(_r2(X_len, y), 0.0),
            ve_bias_incremental=max(_r2(X_full, y) - r2_ctrl, 0.0),
        ))
    return pd.DataFrame(rows).sort_values("ve_model", ascending=True)


def standardized_bias_effects(df: pd.DataFrame) -> pd.DataFrame:
    """Per metric: standardized within-model association with alignment (+95% CI),
    controlling model/dim/language/length, cluster-robust by matchup group."""
    d = df.copy()
    for c in C.STRUCTURAL_FEATURES + ["align_md"]:
        s = d[c].astype(float)
        sd = s.std(ddof=0)
        d[c] = (s - s.mean()) / (sd if sd else 1.0)
    r = X.numeric_family(d, "align_md", ["log_len"], C.STRUCTURAL_FEATURES)
    r["ci_low"] = r["beta"] - 1.96 * r["se"]
    r["ci_high"] = r["beta"] + 1.96 * r["se"]
    from statsmodels.stats.multitest import multipletests
    ok = r["pval"].notna()
    r["q_bh"] = np.nan
    r.loc[ok, "q_bh"] = multipletests(r.loc[ok, "pval"], method="fdr_bh")[1]
    return r.sort_values("beta")


# =========================================================== figures
def fig_variance_explained(df):
    """HEADLINE: model identity explains a lot; bias explains ~nothing. Same unit."""
    ve = variance_explained(df)
    y = np.arange(len(ve))
    fig, ax = plt.subplots(figsize=(8.6, 7.4))
    series = [("model identity (which of the 3 models)", "ve_model", AQUA, "o"),
              ("trace length", "ve_length", ORANGE, "s"),
              ("bias alignment (after all controls)", "ve_bias_incremental", BLUE, "D")]
    for label, col, color, mk in series:
        vals = ve[col].clip(lower=1e-6)
        ax.scatter(vals, y, s=42, color=color, marker=mk, label=label,
                   edgecolor=SURFACE, linewidth=0.8, zorder=3)
    ax.set_xscale("log")
    ax.set_xlim(5e-6, 1.0)
    ax.set_yticks(y); ax.set_yticklabels([_nice(m) for m in ve["metric"]], fontsize=8.5)
    ax.set_xlabel("share of variance in the metric explained  (log scale)")
    ax.grid(axis="y", alpha=0.35); ax.grid(axis="x", alpha=0.5)
    med = ve["ve_bias_incremental"].median()
    ax.axvline(med, color=BLUE, ls=":", lw=1.2, zorder=1)
    ax.annotate(f"bias median\n{med:.5f}", xy=(med, len(ve) - 1.5), xytext=(med * 2.2, len(ve) - 3.2),
                fontsize=8, color=BLUE,
                arrowprops=dict(arrowstyle="->", color=BLUE, lw=0.9))
    ax.set_title("What actually shapes a reasoning metric?\n"
                 "Model identity dominates; demographic bias explains ~0 of the variance",
                 fontsize=11.5, loc="left", pad=12)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.09), ncol=3, fontsize=8.5)
    fig.savefig(C.FIGURES / "f1_variance_explained.png"); plt.close(fig)


def fig_bias_effects(df):
    """Per-metric standardized bias association with 95% CI + negligible band."""
    r = standardized_bias_effects(df).dropna(subset=["beta"])
    y = np.arange(len(r))
    fig, ax = plt.subplots(figsize=(8.2, 7.2))
    ax.axvspan(-0.05, 0.05, color=GRAY_MID, zorder=0)
    ax.axvline(0, color=INK2, lw=1, zorder=1)
    sig = r["q_bh"] < 0.05
    for mask, color, lab in ((sig, BLUE, "significant (BH q<0.05)"),
                             (~sig, GRAY_MARK, "not significant")):
        if not mask.any():
            continue
        ax.errorbar(r.loc[mask, "beta"], y[mask.to_numpy()],
                    xerr=1.96 * r.loc[mask, "se"], fmt="o", ms=6, color=color,
                    ecolor=color, elinewidth=1.4, capsize=0, label=lab, zorder=3)
    ax.set_yticks(y); ax.set_yticklabels([_nice(m) for m in r["metric"]], fontsize=8.5)
    ax.set_xlabel("standardized association with bias alignment (β, 95% CI)\n"
                  "within model · dimension · language · length")
    lim = max(0.09, float(np.abs(r["beta"]).max()) * 1.5)
    ax.set_xlim(-lim, lim)
    ax.text(0.0, len(r) - 0.2, "shaded band = negligible effect (|β| < 0.05)",
            fontsize=8.5, color=INK2, ha="center", va="bottom")
    ax.set_title("How strongly does each reasoning metric track demographic bias?\n"
                 "Every effect sits inside the negligible band", fontsize=11.5, loc="left", pad=12)
    ax.set_ylim(-1.0, len(r) + 0.6)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.11), ncol=2, fontsize=8.5)
    fig.savefig(C.FIGURES / "f2_bias_effects.png"); plt.close(fig)


def fig_model_signatures(df):
    """Metrics x models grid as a dot plot (replaces the 22-spoke radar)."""
    feats = C.STRUCTURAL_FEATURES
    # Only the 3 genuinely reasoning-bearing models. grok-4.1-fast has ~200 traces
    # here; its means are noise and it is not part of the claim.
    z = df[df["model_id"].isin(C.REASONING_MODELS)].copy()
    for f in feats:  # z-score within metric so models are comparable across rows
        s = z[f].astype(float); sd = s.std(ddof=0)
        z[f] = (s - s.mean()) / (sd if sd else 1.0)
    prof = z.groupby("short_model")[feats].mean()
    spread = (prof.max() - prof.min()).sort_values()
    order = spread.index.tolist()
    y = np.arange(len(order))
    fig, ax = plt.subplots(figsize=(8.4, 7.2))
    ax.axvline(0, color=INK2, lw=1, zorder=1)
    for i, met in enumerate(order):  # connector line shows the spread
        vals = [prof.loc[m, met] for m in prof.index]
        ax.plot([min(vals), max(vals)], [i, i], color="#dedcd6", lw=2, zorder=2)
    for m in prof.index:
        ax.scatter(prof.loc[m, order].to_numpy(), y, s=46, label=m,
                   color=MODEL_COLOR.get(m, GRAY_MARK), edgecolor=SURFACE,
                   linewidth=0.8, zorder=3)
    ax.set_yticks(y); ax.set_yticklabels([_nice(m) for m in order], fontsize=8.5)
    ax.set_xlabel("model's mean value, standardized within metric (SD units)")
    ax.set_title("ThinkProbe signatures of the three reasoning models\n"
                 "Each model has a distinct structural fingerprint", fontsize=11.5, loc="left", pad=12)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.09), ncol=3, fontsize=8.5)
    fig.savefig(C.FIGURES / "f3_model_signatures.png"); plt.close(fig)


def fig_profile_space(df):
    """PCA of per-trace profiles: separates by model, not by bias."""
    from sklearn.decomposition import PCA
    Z = X._z(df[C.FEATURES].to_numpy(float))
    p = PCA(n_components=2, random_state=C.SEED).fit(Z)
    xy = p.transform(Z)
    rng = np.random.default_rng(C.SEED)
    samp = rng.choice(len(df), min(5000, len(df)), replace=False)
    fig, axes = plt.subplots(1, 2, figsize=(11.4, 5.0), constrained_layout=True)
    models = df["short_model"].to_numpy()
    for m, c in MODEL_COLOR.items():
        idx = samp[models[samp] == m]
        axes[0].scatter(xy[idx, 0], xy[idx, 1], s=5, alpha=0.35, color=c, label=m, linewidths=0)
    axes[0].set_title("colored by model — clearly separated", fontsize=10, loc="left")
    axes[0].legend(fontsize=8, markerscale=3, loc="upper right")
    q = pd.qcut(df["align_md"].rank(method="first"), 4, labels=[1, 2, 3, 4]).astype(int).to_numpy()
    for lab, c in ((1, BLUE), (4, RED)):
        idx = samp[q[samp] == lab]
        nm = "least bias-aligned (Q1)" if lab == 1 else "most bias-aligned (Q4)"
        axes[1].scatter(xy[idx, 0], xy[idx, 1], s=5, alpha=0.35, color=c, label=nm, linewidths=0)
    axes[1].set_title("colored by bias alignment — fully intermixed", fontsize=10, loc="left")
    axes[1].legend(fontsize=8, markerscale=3, loc="upper right")
    for a in axes:
        a.set_xlabel(f"PC1 ({p.explained_variance_ratio_[0]*100:.0f}% of variance)")
        a.set_ylabel(f"PC2 ({p.explained_variance_ratio_[1]*100:.0f}%)")
    fig.suptitle("Reasoning-profile space is organized by model, not by bias",
                 fontsize=12, x=0.01, ha="left")
    fig.savefig(C.FIGURES / "f4_profile_space.png"); plt.close(fig)


def fig_predictive():
    """Can the 22-dim profile predict the bias bin better than a surface baseline?"""
    p = pd.read_parquet(C.RESULTS / "comparisons_profile_results.parquet")
    pm4 = p[(p.profile_method == "PM4_classify") & (p.stratum_factor == "POOLED")]
    pm4 = pm4.dropna(subset=["auc_profile"]).copy()
    if pm4.empty:
        return
    pm4["label"] = pm4["bias_op"].map(PRETTY).fillna(pm4["bias_op"])
    pm4 = pm4.sort_values("auc_profile")
    y = np.arange(len(pm4)); h = 0.36
    fig, ax = plt.subplots(figsize=(8.6, 0.72 * len(pm4) + 2.4))
    ax.barh(y - h / 2, pm4["auc_baseline"] - 0.5, h, left=0.5, color=GRAY_MARK,
            label="length + lexical baseline")
    ax.barh(y + h / 2, pm4["auc_profile"] - 0.5, h, left=0.5, color=BLUE,
            label="22-dim ThinkProbe profile")
    ax.axvline(0.5, color=INK2, lw=1)
    for yi, (b, pr) in enumerate(zip(pm4["auc_baseline"], pm4["auc_profile"])):
        ax.text(max(b, pr) + 0.004, yi, f"Δ={pr-b:+.3f}", va="center", fontsize=8, color=INK2)
    ax.set_yticks(y); ax.set_yticklabels(pm4["label"], fontsize=9)
    ax.set_xlabel("cross-validated AUC  (0.5 = no better than chance)")
    ax.set_xlim(0.5, max(0.68, float(pm4[["auc_profile", "auc_baseline"]].to_numpy().max()) + 0.05))
    ax.grid(axis="y", alpha=0)
    ax.set_title("Does the reasoning profile predict bias better than surface features?\n"
                 "No — the profile does not beat length + lexical", fontsize=11.5, loc="left", pad=12)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.10), ncol=2, fontsize=8.5)
    fig.savefig(C.FIGURES / "f5_profile_predictive.png"); plt.close(fig)


def fig_refusal_contrast():
    """Positive control: the same metrics DO separate refusal from engagement."""
    r = pd.read_parquet(C.RESULTS / "analysis_refusal.parquet").dropna(subset=["beta"])
    r = r.rename(columns={"feature": "metric"}).sort_values("beta")
    y = np.arange(len(r))
    fig, ax = plt.subplots(figsize=(8.2, 7.0))
    ax.axvspan(-0.05, 0.05, color=GRAY_MID, zorder=0)
    ax.axvline(0, color=INK2, lw=1, zorder=1)
    colors = [RED if b > 0 else BLUE for b in r["beta"]]
    ax.scatter(r["beta"], y, s=46, color=colors, edgecolor=SURFACE, linewidth=0.8, zorder=3)
    ax.set_yticks(y); ax.set_yticklabels([_nice(m) for m in r["metric"]], fontsize=8.5)
    ax.set_xlabel("standardized difference: refusal − engagement (length-controlled)")
    ax.set_title("Positive control: these same metrics detect refusal vs engagement\n"
                 "Effects are 10–30× larger than anything bias produces", fontsize=11.5, loc="left", pad=12)
    fig.savefig(C.FIGURES / "f6_refusal_contrast.png"); plt.close(fig)


def make_all():
    df = X.derive_bias_vars(X.load_full_frame())
    made, failed = [], []
    for name, fn in [("f1_variance_explained", lambda: fig_variance_explained(df)),
                     ("f2_bias_effects", lambda: fig_bias_effects(df)),
                     ("f3_model_signatures", lambda: fig_model_signatures(df)),
                     ("f4_profile_space", lambda: fig_profile_space(df)),
                     ("f5_profile_predictive", fig_predictive),
                     ("f6_refusal_contrast", fig_refusal_contrast)]:
        try:
            fn(); made.append(name)
        except Exception as e:  # noqa: BLE001
            failed.append(f"{name}: {type(e).__name__}: {e}")
    print("[figures_v2] made:", made)
    for f in failed:
        print("[figures_v2] FAILED", f)
    return made


if __name__ == "__main__":
    make_all()
