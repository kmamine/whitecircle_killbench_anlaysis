"""Enumerate the FULL space of bias <-> metric and bias <-> profile comparisons.

ThinkProbe-centered: the 20 structural metrics and the aggregated 22-dim profile are
the objects; the KillBench bias is a grouping/label lens laid over them. This module
computes every combination of (bias operationalization x stratum x control x target)
and writes the complete comparison registry to results/. It does NOT run the stats —
it plans them, so the plan can be reviewed and tiered before execution.
"""
from __future__ import annotations
import itertools
import pandas as pd

from . import config as C

# ---------------------------------------------------------------- factors
# 20 structural metrics (the per-trace features); +2 length summaries are controls.
METRICS = C.STRUCTURAL_FEATURES  # 20

# Bias operationalizations (how the bias lens is expressed).
BIAS_OPS = [
    # id            kind          grain                      note
    ("ALIGN_C",     "continuous", "model x dim",             "per-trace alignment score (primary)"),
    ("ALIGN_C_MDS", "continuous", "model x dim x scenario",  "per-trace alignment, finer grain (grain robustness)"),
    ("ALIGN_ABS",   "continuous", "model x dim",             "|alignment| = bias STRENGTH, direction-free"),
    ("ALIGN_BIN",   "binary",     "model x dim",             "with-bias vs against-bias (2 groups)"),
    ("ALIGN_Q4",    "ordinal",    "model x dim",             "alignment quartiles Q1..Q4 (dose-response trend)"),
    ("FAVOR_CLASS", "categorical","model x dim",             "chosen value favored/neutral/disfavored (win-rate bins)"),
    ("MAG_GROUP",   "group",      "model x dim x scenario",  "group bias magnitude (Cramer's V); group-level"),
    ("MODEL_TIER",  "categorical","model",                   "model bias tier: qwen>kimi>gemini"),
]

# Strata (subpopulations the comparison is run within).
STRATA = (
    [("POOLED", "all")]
    + [("MODEL", m.split("/")[-1]) for m in C.REASONING_MODELS]      # 3
    + [("DIM", d) for d in C.SINGLE_DIMS]                            # 8
    + [("DOMAIN", x) for x in ("civilian", "military")]             # 2
    + [("LANG", l) for l in ("ar", "en", "es", "he", "ru", "zh")]   # 6
)  # = 20

# Control levels (what is partialled out before the bias<->target relationship).
CONTROLS = [
    ("C0_raw",     "unadjusted"),
    ("C1_len",     "+ log length"),
    ("C2_len_lex", "+ length + lexical baseline (structure must beat this)"),
]

# Profile-level methods (bias <-> whole 22-vector).
PROFILE_METHODS = [
    # id        needs_binned  needs_rerolls  desc
    ("PM1_radar",      True,  False, "group-mean profile radar/heatmap (descriptive)"),
    ("PM2_distance",   True,  False, "profile-vector distance between bias bins + permutation test"),
    ("PM3_permanova",  False, False, "PERMANOVA: profile ~ bias (multivariate)"),
    ("PM4_classify",   True,  False, "predict bias bin from 22-vector (grouped-CV AUC) vs len+lex baseline"),
    ("PM5_archetype",  True,  False, "PCA+k-means archetypes -> archetype x bias contingency (Cramer's V)"),
    ("PM6_pc_regress", False, False, "per principal-component regression on bias"),
    ("PM7_stability",  True,  True,  "profile ICC across rerolls, by bias bin"),
    ("PM8_sensitivity",True,  False, "profile domain/dimension sensitivity x bias"),
]

# ---- validity rules -----------------------------------------------------
def _stratum_ok(bias_id: str, bias_grain: str, factor: str) -> bool:
    # A bias defined at the model level cannot be stratified by model (no variance within).
    if bias_id == "MODEL_TIER" and factor == "MODEL":
        return False
    # Model x dim alignment stratified by DIM is fine; by MODEL is fine.
    # Military domain is ~2% of data -> keep but flag as low-power (handled downstream).
    return True


def _tier(bias_id: str, factor: str, control_id: str) -> int:
    """1 = pre-registered primary, 2 = robustness, 3 = exploratory."""
    if bias_id == "ALIGN_C" and factor == "POOLED" and control_id in ("C1_len", "C2_len_lex"):
        return 1
    if bias_id in ("ALIGN_C", "ALIGN_BIN", "ALIGN_Q4", "ALIGN_C_MDS"):
        if factor in ("POOLED", "MODEL") or (factor == "LANG"):
            return 2
    return 3


# ---------------------------------------------------------------- enumerators
def enumerate_metric_comparisons() -> pd.DataFrame:
    rows = []
    for (bid, kind, grain, bnote) in BIAS_OPS:
        for (factor, level) in STRATA:
            if not _stratum_ok(bid, grain, factor):
                continue
            for (cid, cdesc) in CONTROLS:
                stat = {
                    "continuous": "cluster-robust OLS: metric ~ bias + controls (std beta, 95% CI)",
                    "binary": "group mean diff (Hedges g) + OLS with controls",
                    "ordinal": "Jonckheere-Terpstra trend + ordinal beta",
                    "categorical": "one-way effect (eta^2) + pairwise contrasts",
                    "group": "group-level WLS: mean-metric ~ magnitude (weighted by n)",
                }[kind]
                rows.append(dict(
                    comparison="bias<->metric", bias_op=bid, bias_kind=kind, bias_grain=grain,
                    stratum_factor=factor, stratum_level=level, control=cid,
                    n_metric_tests=len(METRICS), statistic=stat,
                    correction="BH over the 20 metrics within this family",
                    tier=_tier(bid, factor, cid),
                ))
    return pd.DataFrame(rows)


def enumerate_profile_comparisons() -> pd.DataFrame:
    rows = []
    for (bid, kind, grain, bnote) in BIAS_OPS:
        for (pm, needs_binned, needs_rerolls, pdesc) in PROFILE_METHODS:
            # continuous bias needs binning for methods that compare bins
            if needs_binned and kind == "continuous" and bid not in ("ALIGN_ABS",):
                pass  # will be binned (e.g., quartiles) at run time; still valid
            for (factor, level) in STRATA:
                if not _stratum_ok(bid, grain, factor):
                    continue
                # stability across rerolls only meaningful pooled/per-model/per-dim
                if needs_rerolls and factor in ("LANG", "DOMAIN"):
                    continue
                rows.append(dict(
                    comparison="bias<->profile", bias_op=bid, bias_kind=kind, bias_grain=grain,
                    profile_method=pm, method_desc=pdesc,
                    stratum_factor=factor, stratum_level=level,
                    target="22-dim CognitiveProfile (aggregated)",
                    tier=_tier(bid, factor, "C1_len"),
                ))
    return pd.DataFrame(rows)


def build_registry(verbose: bool = True) -> dict:
    m = enumerate_metric_comparisons()
    p = enumerate_profile_comparisons()
    m.to_csv(C.RESULTS / "comparisons_bias_metric.csv", index=False)
    p.to_csv(C.RESULTS / "comparisons_bias_profile.csv", index=False)
    pd.concat([m, p], ignore_index=True).to_csv(C.RESULTS / "comparisons_all.csv", index=False)

    summary = {
        "bias_ops": len(BIAS_OPS), "strata": len(STRATA), "controls": len(CONTROLS),
        "metrics": len(METRICS), "profile_methods": len(PROFILE_METHODS),
        "metric_families": len(m),
        "metric_cells_total": int(m["n_metric_tests"].sum()),
        "profile_analyses": len(p),
        "grand_total_analyses": int(m["n_metric_tests"].sum()) + len(p),
        "metric_families_by_tier": m.groupby("tier").size().to_dict(),
        "profile_by_tier": p.groupby("tier").size().to_dict(),
    }
    if verbose:
        import json
        print(json.dumps(summary, indent=2, default=str))
    return summary


if __name__ == "__main__":
    build_registry()
