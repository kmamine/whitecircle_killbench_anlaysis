"""ThinkProbe-first figures: the models' reasoning profiles are the centerpiece;
bias is the lens laid over them. Run after the sweep (kbtp.comparisons)."""
from __future__ import annotations
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from . import config as C
from . import comparisons as X

plt.rcParams.update({"figure.dpi": 130, "savefig.bbox": "tight", "font.size": 9})
_MODEL_COLORS = {"qwen3-235b-a22b": "#b2182b", "kimi-k2.5": "#ef8a62",
                 "gemini-3.1-pro-preview": "#2166ac"}


def _frame():
    return X.derive_bias_vars(X.load_full_frame())


def _radar(ax, labels, series: dict, title):
    n = len(labels)
    ang = np.linspace(0, 2 * np.pi, n, endpoint=False).tolist(); ang += ang[:1]
    for name, vals, color in series:
        v = list(vals) + [vals[0]]
        ax.plot(ang, v, color=color, lw=1.8, label=name)
        ax.fill(ang, v, color=color, alpha=0.08)
    ax.set_xticks(ang[:-1]); ax.set_xticklabels(labels, fontsize=6.5)
    ax.set_yticklabels([]); ax.set_title(title, fontsize=10, pad=14)
    ax.legend(loc="upper right", bbox_to_anchor=(1.28, 1.12), fontsize=7)


def fig_model_profiles(df=None):
    """ThinkProbe centerpiece: the 3 models' 22-dim cognitive profiles (min-max normalized)."""
    df = df if df is not None else _frame()
    feats = C.FEATURES
    prof = df.groupby("short_model")[feats].mean()
    norm = (prof - prof.min()) / (prof.max() - prof.min()).replace(0, 1)
    fig, ax = plt.subplots(figsize=(9, 7), subplot_kw=dict(polar=True))
    series = [(m, norm.loc[m].values, _MODEL_COLORS.get(m, "#666"))
              for m in norm.index if m in _MODEL_COLORS]
    _radar(ax, feats, series, "ThinkProbe cognitive profiles — the 3 reasoning models\n(min-max normalized across models)")
    fig.savefig(C.FIGURES / "fig6_model_profiles.png"); plt.close(fig)


def fig_archetypes(df=None):
    """PCA of per-trace profiles; archetypes are organized by MODEL, not by bias."""
    from sklearn.decomposition import PCA
    df = df if df is not None else _frame()
    Z = X._z(df[C.FEATURES].to_numpy(float))
    pc = PCA(n_components=2, random_state=C.SEED).fit(Z)
    xy = pc.transform(Z)
    samp = np.random.default_rng(C.SEED).choice(len(df), min(6000, len(df)), replace=False)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.6))
    # by model
    for m, c in _MODEL_COLORS.items():
        idx = samp[(df["short_model"].to_numpy()[samp] == m)]
        axes[0].scatter(xy[idx, 0], xy[idx, 1], s=3, alpha=0.3, color=c, label=m)
    axes[0].set_title("profiles colored by MODEL\n(clear separation)"); axes[0].legend(fontsize=7, markerscale=3)
    # by align quartile
    q = pd.qcut(df["align_md"].rank(method="first"), 4, labels=["Q1", "Q2", "Q3", "Q4"]).astype(str).to_numpy()
    cmap = {"Q1": "#2166ac", "Q2": "#92c5de", "Q3": "#f4a582", "Q4": "#b2182b"}
    for lab, c in cmap.items():
        idx = samp[q[samp] == lab]
        axes[1].scatter(xy[idx, 0], xy[idx, 1], s=3, alpha=0.3, color=c, label=f"align {lab}")
    axes[1].set_title("same profiles colored by BIAS-alignment quartile\n(no separation)"); axes[1].legend(fontsize=7, markerscale=3)
    for a in axes:
        a.set_xlabel(f"PC1 ({pc.explained_variance_ratio_[0]*100:.0f}%)")
        a.set_ylabel(f"PC2 ({pc.explained_variance_ratio_[1]*100:.0f}%)")
    fig.suptitle("Reasoning-profile space: structured by model, not by bias", fontsize=11)
    fig.savefig(C.FIGURES / "fig7_archetypes.png"); plt.close(fig)


def fig_effect_heatmap():
    """Effect sizes across the bias<->metric grid (pooled, length-controlled)."""
    m = pd.read_parquet(C.RESULTS / "comparisons_metric_results.parquet")
    sub = m[(m.stratum_factor == "POOLED") & (m.control == "C1_len")]
    piv = sub.pivot_table(index="metric", columns="bias_op", values="effect")
    order = ["ALIGN_C", "ALIGN_C_MDS", "ALIGN_ABS", "ALIGN_BIN", "ALIGN_Q4",
             "FAVOR_CLASS", "MAG_GROUP", "MODEL_TIER"]
    piv = piv[[c for c in order if c in piv.columns]]
    fig, ax = plt.subplots(figsize=(8.5, 7))
    vmax = np.nanpercentile(np.abs(piv.values), 98)
    im = ax.imshow(piv.values, cmap="RdBu_r", vmin=-vmax, vmax=vmax, aspect="auto")
    ax.set_xticks(range(piv.shape[1])); ax.set_xticklabels(piv.columns, rotation=40, ha="right", fontsize=8)
    ax.set_yticks(range(piv.shape[0])); ax.set_yticklabels(piv.index, fontsize=7)
    fig.colorbar(im, ax=ax, label="effect (partial r or η² / model-identity)")
    ax.set_title("bias ↔ metric effect sizes (pooled, length-controlled)\n"
                 "lens ops ≈ 0; only MODEL_TIER (= model identity) is large", fontsize=10)
    fig.savefig(C.FIGURES / "fig8_effect_heatmap.png"); plt.close(fig)


def fig_bias_profile_overlay(df=None):
    """Residualized profile centroids: most bias-aligned vs most bias-against traces."""
    df = df if df is not None else _frame()
    d = df.dropna(subset=["align_md"]).copy()
    Xnu = X._design(d, ["log_len"])
    R = X._resid(Xnu, d[C.FEATURES].to_numpy(float))
    R = X._z(R)
    q = pd.qcut(d["align_md"].rank(method="first"), 4, labels=["Q1", "Q2", "Q3", "Q4"]).astype(str).to_numpy()
    top = R[q == "Q4"].mean(0); bot = R[q == "Q1"].mean(0)
    fig, ax = plt.subplots(figsize=(9, 7), subplot_kw=dict(polar=True))
    # shift to positive for radar readability
    base = min(top.min(), bot.min())
    series = [("most bias-ALIGNED (Q4)", top - base, "#b2182b"),
              ("most bias-AGAINST (Q1)", bot - base, "#2166ac")]
    _radar(ax, C.FEATURES, series, "Profile of bias-aligned vs bias-against traces\n(model/dim/lang/length-residualized — the two nearly coincide)")
    fig.savefig(C.FIGURES / "fig9_bias_profile_overlay.png"); plt.close(fig)


def fig_profile_predictive():
    """PM4: does the profile predict the bias bin better than a length+lexical baseline?"""
    p = pd.read_parquet(C.RESULTS / "comparisons_profile_results.parquet")
    pm4 = p[(p.profile_method == "PM4_classify") & (p.stratum_factor == "POOLED")].dropna(subset=["auc_profile"])
    if pm4.empty:
        return
    pm4 = pm4.set_index("bias_op")
    fig, ax = plt.subplots(figsize=(8, 4))
    x = np.arange(len(pm4)); w = 0.38
    ax.bar(x - w / 2, pm4["auc_baseline"], w, label="length+lexical baseline", color="#999999")
    ax.bar(x + w / 2, pm4["auc_profile"], w, label="22-dim profile", color="#2166ac")
    ax.axhline(0.5, color="#b2182b", ls="--", lw=1)
    ax.set_xticks(x); ax.set_xticklabels(pm4.index, rotation=30, ha="right", fontsize=8)
    ax.set_ylabel("grouped-CV AUC"); ax.set_ylim(0.45, max(0.75, pm4[["auc_profile", "auc_baseline"]].values.max() + 0.05))
    ax.set_title("Can the reasoning profile predict the bias bin, vs a surface baseline? (pooled)")
    ax.legend(fontsize=8)
    fig.savefig(C.FIGURES / "fig10_profile_predictive.png"); plt.close(fig)


def make_all():
    df = _frame()
    made = []
    for name, fn in [("fig6_model_profiles", lambda: fig_model_profiles(df)),
                     ("fig7_archetypes", lambda: fig_archetypes(df)),
                     ("fig8_effect_heatmap", fig_effect_heatmap),
                     ("fig9_bias_profile_overlay", lambda: fig_bias_profile_overlay(df)),
                     ("fig10_profile_predictive", fig_profile_predictive)]:
        try:
            fn(); made.append(name)
        except Exception as e:  # noqa: BLE001
            print(f"[figures_profile] skip {name}: {type(e).__name__}: {e}")
    print(f"[figures_profile] made: {made}")
    return made


if __name__ == "__main__":
    make_all()
