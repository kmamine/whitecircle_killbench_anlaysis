"""Figures for the report. Each is skipped gracefully if its input is missing.

Scientific matplotlib figures (clear labels, error bars, colorblind-safe); saved to figures/.
"""
from __future__ import annotations
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from . import config as C

plt.rcParams.update({"figure.dpi": 130, "savefig.bbox": "tight", "font.size": 10})
_POS, _NEG, _NULL = "#2166ac", "#b2182b", "#999999"


def _short(m: str) -> str:
    return m.split("/")[-1]


def fig_bias_landscape():
    """Per-trace bias-alignment distribution by model (who reasons more 'with' its bias)."""
    labels = pd.read_parquet(C.F_LABELS)
    labels = labels[labels["model_id"].isin(C.REASONING_MODELS) & labels["valid_md"]]
    order = labels.groupby("model_id")["align_md"].mean().sort_values().index.tolist()
    data = [labels.loc[labels.model_id == m, "align_md"].values for m in order]
    fig, ax = plt.subplots(figsize=(7, 3.6))
    parts = ax.violinplot(data, vert=False, showmeans=True, showextrema=False)
    for b in parts["bodies"]:
        b.set_facecolor("#4393c3"); b.set_alpha(0.6)
    ax.axvline(0, color=_NULL, ls="--", lw=1, label="no bias (win-rate = 0.25)")
    ax.set_yticks(range(1, len(order) + 1)); ax.set_yticklabels([_short(m) for m in order])
    ax.set_xlabel("per-trace bias-alignment score  (chosen value's win-rate − 0.25)")
    ax.set_title("How strongly each model's chosen demographic is systematically (dis)favored")
    ax.legend(loc="lower right", fontsize=8)
    fig.savefig(C.FIGURES / "fig1_bias_landscape.png"); plt.close(fig)


def fig_winrate_heatmap():
    """Most-favored / most-avoided demographic win-rate per reasoning model x dim."""
    u = pd.read_parquet(C.F_BIAS_UNITS)
    u = u[u.model_id.isin(C.REASONING_MODELS) & (u.available >= 50)]
    dims = ["nationality", "religion", "politics", "orientation", "skin_color", "gender_identity"]
    models = [m for m in C.REASONING_MODELS if m in u.model_id.unique()]
    span = np.full((len(models), len(dims)), np.nan)
    for i, m in enumerate(models):
        for j, d in enumerate(dims):
            g = u[(u.model_id == m) & (u.varied_param == d)]
            if len(g):
                span[i, j] = g["winrate"].max() - g["winrate"].min()
    fig, ax = plt.subplots(figsize=(7, 2.8))
    im = ax.imshow(span, cmap="magma", aspect="auto", vmin=0)
    ax.set_xticks(range(len(dims))); ax.set_xticklabels(dims, rotation=30, ha="right")
    ax.set_yticks(range(len(models))); ax.set_yticklabels([_short(m) for m in models])
    for i in range(len(models)):
        for j in range(len(dims)):
            if not np.isnan(span[i, j]):
                ax.text(j, i, f"{span[i,j]:.2f}", ha="center", va="center",
                        color="white" if span[i, j] < np.nanmax(span) * 0.6 else "black", fontsize=8)
    fig.colorbar(im, ax=ax, label="win-rate spread (max−min)")
    ax.set_title("Demographic-choice bias magnitude (win-rate spread) by model × dimension")
    fig.savefig(C.FIGURES / "fig2_winrate_heatmap.png"); plt.close(fig)


def fig_association_forest():
    """Forest plot: standardized association of each structural feature with bias-alignment."""
    a = pd.read_parquet(C.F_ANALYSIS).dropna(subset=["beta"]).sort_values("beta")
    fig, ax = plt.subplots(figsize=(7, 6))
    y = np.arange(len(a))
    colors = [_POS if s else _NULL for s in a["signif_bh"]]
    ax.errorbar(a["beta"], y, xerr=[a["beta"] - a["ci_low"], a["ci_high"] - a["beta"]],
                fmt="o", ecolor="#bbbbbb", elinewidth=1.2, capsize=2, mfc="none", mec="none")
    ax.scatter(a["beta"], y, c=colors, s=28, zorder=3)
    ax.axvline(0, color="k", lw=0.8)
    ax.set_yticks(y); ax.set_yticklabels(a["feature"], fontsize=8)
    ax.set_xlabel("standardized association with bias-alignment (β, 95% CI)\ncontrolling length, model, dim, language; cluster-robust")
    ax.set_title("Which reasoning-structure features track demographic bias?\n(blue = BH-significant)")
    fig.savefig(C.FIGURES / "fig3_association_forest.png"); plt.close(fig)


def fig_predictive():
    """Baseline (length+lexical) vs structure vs both: CV R² and AUC."""
    p = pd.read_parquet(C.RESULTS / "analysis_predictive.parquet")
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.4))
    x = np.arange(len(p))
    for ax, col, ttl in ((axes[0], "cv_r2_mean", "predict alignment score (Ridge R²)"),
                         (axes[1], "cv_auc_mean", "predict with/against bias (LogReg AUC)")):
        sd = col.replace("mean", "sd")
        ax.bar(x, p[col], yerr=p[sd], color=["#999999", "#4393c3", "#2166ac"], capsize=3)
        ax.set_xticks(x); ax.set_xticklabels(p["feature_set"], rotation=20, ha="right", fontsize=8)
        ax.set_title(ttl, fontsize=9)
        if "auc" in col: ax.axhline(0.5, color=_NEG, ls="--", lw=1)
    fig.suptitle("Does trace structure beat a length+lexical baseline? (grouped 5-fold CV)")
    fig.savefig(C.FIGURES / "fig4_predictive.png"); plt.close(fig)


def fig_refusal():
    """Top structural features separating long refusals from engaged deliberation."""
    r = pd.read_parquet(C.RESULTS / "analysis_refusal.parquet").dropna(subset=["beta"])
    r = r.reindex(r["beta"].abs().sort_values(ascending=False).index).head(12).iloc[::-1]
    fig, ax = plt.subplots(figsize=(7, 4.5))
    colors = [_POS if b > 0 else _NEG for b in r["beta"]]
    ax.barh(range(len(r)), r["beta"], color=colors)
    ax.set_yticks(range(len(r))); ax.set_yticklabels(r["feature"], fontsize=8)
    ax.axvline(0, color="k", lw=0.8)
    ax.set_xlabel("standardized difference (refusal − engagement), length-controlled")
    ax.set_title("Refusal vs engagement: structural signature (secondary analysis)")
    fig.savefig(C.FIGURES / "fig5_refusal.png"); plt.close(fig)


def make_all():
    made = []
    for name, fn in [("fig1_bias_landscape", fig_bias_landscape),
                     ("fig2_winrate_heatmap", fig_winrate_heatmap),
                     ("fig3_association_forest", fig_association_forest),
                     ("fig4_predictive", fig_predictive),
                     ("fig5_refusal", fig_refusal)]:
        try:
            fn(); made.append(name)
        except Exception as e:  # noqa: BLE001
            print(f"[figures] skip {name}: {type(e).__name__}: {e}")
    print(f"[figures] made: {made}")
    return made


if __name__ == "__main__":
    make_all()
