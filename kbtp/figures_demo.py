"""Simple, non-technical-friendly figures for the kill/no-kill distributions.

Form choice: the data's job is "above/below a baseline" (each group's kill rate vs the
25% fair share), which is a DIVERGING BAR anchored at the baseline — not a dot plot with
connector lines. One bar per group, sorted, value labelled directly. Colour carries the
sign only (red = chosen to die more than its fair share, blue = protected), with a neutral
grey band for "within a point of fair".
"""
from __future__ import annotations
import numpy as np
import pandas as pd
import pyarrow.parquet as pq
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from . import config as C

NULL = 25.0
RED, BLUE, GREY = "#d03b3b", "#2a78d6", "#b8b7b2"
GREY_BAND, INK, INK2, SURFACE = "#f0efec", "#0b0b0b", "#52514e", "#fcfcfb"

plt.rcParams.update({
    "figure.dpi": 140, "savefig.bbox": "tight", "figure.facecolor": SURFACE,
    "axes.facecolor": SURFACE, "font.size": 10, "text.color": INK,
    "axes.edgecolor": "#d9d8d3", "xtick.color": INK2, "ytick.color": INK2,
    "axes.grid": True, "grid.color": "#e8e7e2", "grid.linewidth": 0.7,
    "axes.spines.top": False, "axes.spines.right": False, "axes.spines.left": False,
    "legend.frameon": False,
})


def _rates(sub: pd.DataFrame, min_n: int = 200) -> pd.Series:
    out = {}
    for v in sorted({x for a in sub.available_values if a is not None for x in a if x is not None}):
        m = np.array([a is not None and v in list(a) for a in sub.available_values])
        n = int(m.sum())
        if n < min_n:
            continue
        out[v] = 100 * (sub[m].chosen_value == v).sum() / n
    return pd.Series(out)


def load_dimension(dim: str, civilian_only: bool = True) -> pd.DataFrame:
    ch = pq.read_table(C.F_CHOICES_ALL).to_pandas()
    sub = ch[ch.varied_param == dim]
    if civilian_only:
        sub = sub[sub.scenario_domain == "civilian"]
    return sub


def _nonsignificant(sub: pd.DataFrame, alpha: float = 0.05) -> set:
    """Groups whose kill rate is not significantly different from 25% (BH-corrected)."""
    from scipy import stats
    from statsmodels.stats.multitest import multipletests
    rows = []
    for v in sorted({x for a in sub.available_values if a is not None
                     for x in a if x is not None}):
        m = np.array([a is not None and v in list(a) for a in sub.available_values])
        n = int(m.sum())
        if n < 200:
            continue
        k = int((sub[m].chosen_value == v).sum())
        rows.append((v, stats.binomtest(k, n, NULL / 100).pvalue))
    if not rows:
        return set()
    q = multipletests([p for _, p in rows], method="fdr_bh")[1]
    return {v for (v, _), qq in zip(rows, q) if qq >= alpha}


def _bar_panel(ax, s: pd.Series, title: str, show_values: bool = True,
               xlabel: str | None = None, fontsize: float = 10,
               ns: set | None = None, sort: bool = True):
    """ns = groups whose deviation from 25% is NOT statistically significant -> grey.
    sort=False keeps the caller's row order (required for small multiples, so bars and
    y-labels stay aligned across panels)."""
    if sort:
        s = s.sort_values()
    y = np.arange(len(s))
    dev = s.values - NULL
    ns = ns or set()
    colors = [GREY if g in ns else (RED if d > 0 else BLUE)
              for g, d in zip(s.index, dev)]
    ax.barh(y, dev, left=NULL, color=colors, height=0.72, zorder=2)
    ax.axvline(NULL, color=INK2, lw=1.4, zorder=3)
    ax.set_yticks(y)
    ax.set_yticklabels(s.index, fontsize=fontsize)
    if show_values:
        for i, (val, d) in enumerate(zip(s.values, dev)):
            off = 0.35 if d >= 0 else -0.35
            ax.text(val + off, i, f"{val:.1f}%", va="center",
                    ha="left" if d >= 0 else "right", fontsize=fontsize - 1.2, color=INK2)
    ax.set_title(title, fontsize=fontsize + 1.5, loc="left", pad=10)
    if xlabel:
        ax.set_xlabel(xlabel)
    ax.grid(axis="y", alpha=0)
    lo, hi = s.min(), s.max()
    pad = max(2.2, (hi - lo) * 0.16)
    ax.set_xlim(min(lo, NULL) - pad, max(hi, NULL) + pad)


def fig_simple(dim: str = "nationality", fname: str | None = None):
    """One diverging bar per group, pooled over models — the simplest read."""
    sub = load_dimension(dim)
    s = _rates(sub)
    fig, ax = plt.subplots(figsize=(8.4, 0.42 * len(s) + 2.3))
    _bar_panel(ax, s,
               f"Who does the AI choose to die?  ({dim.replace('_',' ')})\n"
               "Bars right of the line are chosen more often than their fair share",
               xlabel="% of times this group is the one chosen to die  "
                      "(25% = fair share, 4 people per dilemma)",
               ns=_nonsignificant(sub))
    ax.text(NULL, len(s) - 0.35, "25% = fair share", fontsize=9, color=INK2,
            ha="center", va="bottom")
    ax.set_ylim(-0.8, len(s) + 0.5)
    fig.savefig(C.FIGURES / (fname or f"n1_simple_{dim}.png"))
    plt.close(fig)


def fig_by_model(dim: str = "nationality", fname: str | None = None):
    """Small multiples: same bar form, one panel per reasoning model, shared row order."""
    sub = load_dimension(dim)
    order = _rates(sub).sort_values().index.tolist()
    models = list(C.REASONING_MODELS)
    series = {m: _rates(sub[sub.model_id == m]).reindex(order) for m in models}
    ns = {m: _nonsignificant(sub[sub.model_id == m]) for m in models}
    lo = min(min(v.min() for v in series.values()), NULL) - 2
    hi = max(max(v.max() for v in series.values()), NULL) + 2
    fig, axes = plt.subplots(1, len(models), figsize=(4.3 * len(models), 0.36 * len(order) + 2.6),
                             sharey=True)
    for ax, mdl in zip(axes, models):
        _bar_panel(ax, series[mdl], mdl.split("/")[-1], show_values=False,
                   fontsize=9, ns=ns[mdl], sort=False)
        ax.set_xlim(lo, hi)
    fig.supxlabel("% of times this group is the one chosen to die   (25% = fair share)",
                  fontsize=10)
    fig.suptitle(f"The models disagree about who to protect  ({dim.replace('_',' ')})",
                 fontsize=13, x=0.005, ha="left")
    fig.tight_layout()
    fig.savefig(C.FIGURES / (fname or f"n2_by_model_{dim}.png"))
    plt.close(fig)


def fig_disagreement(dim: str = "nationality", top: int = 8, fname: str | None = None):
    """The simplest view of the disagreement: grouped bars for the groups the models
    most disagree about."""
    sub = load_dimension(dim)
    models = list(C.REASONING_MODELS)
    series = pd.DataFrame({m.split("/")[-1]: _rates(sub[sub.model_id == m]) for m in models})
    series["spread"] = series.max(axis=1) - series.min(axis=1)
    d = series.sort_values("spread").tail(top)
    cols = [m.split("/")[-1] for m in models]
    COL = {"gemini-3.1-pro-preview": "#2a78d6", "kimi-k2.5": "#eb6834",
           "qwen3-235b-a22b": "#1baf7a"}
    y = np.arange(len(d)); h = 0.26
    fig, ax = plt.subplots(figsize=(9.0, 0.86 * len(d) + 2.4))
    for i, c in enumerate(cols):
        off = (i - 1) * h
        ax.barh(y + off, d[c] - NULL, h, left=NULL, color=COL[c], label=c, zorder=2)
        for yy, val in zip(y + off, d[c]):
            ax.text(val + (0.25 if val >= NULL else -0.25), yy, f"{val:.0f}%", va="center",
                    ha="left" if val >= NULL else "right", fontsize=8, color=INK2)
    ax.axvline(NULL, color=INK2, lw=1.4, zorder=3)
    ax.set_yticks(y); ax.set_yticklabels(d.index, fontsize=10.5)
    ax.grid(axis="y", alpha=0)
    ax.set_xlabel("% of times this group is the one chosen to die   (25% = fair share)")
    ax.set_title(f"Where the AIs disagree most about who should die  ({dim.replace('_',' ')})\n"
                 "Same dilemma, same 4 people — different model, different victim",
                 fontsize=12.5, loc="left", pad=10)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.10), ncol=3, fontsize=9)
    fig.savefig(C.FIGURES / (fname or f"n3_disagreement_{dim}.png"))
    plt.close(fig)


if __name__ == "__main__":
    fig_simple("nationality")
    fig_by_model("nationality")
    fig_disagreement("nationality")
    print("saved n1_simple, n2_by_model, n3_disagreement (nationality)")
