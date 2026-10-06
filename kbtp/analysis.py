"""Controlled analysis: does trace structure track demographic bias, beyond length/lexical?

Two complementary framings, both with mandatory controls (CLaude.md):

1. Per-feature association (interpretable primary): for each of the 20 structural
   features, cluster-robust OLS of the standardized feature on the standardized
   per-trace bias-alignment score, controlling for length + model + dim + language
   (clustered by group_id). BH-corrected over features; effect sizes + 95% CIs + MDE.

2. Predictive baseline-vs-structure (CLaude.md "must beat the baseline"): grouped
   5-fold CV. Do the 20 structural features add predictive power for the bias-alignment
   score (Ridge R2) and with/against-bias (LogReg AUC) OVER a length+lexical baseline?

Plus a group-level robustness check (bias magnitude vs group-mean structure) and an
English-only robustness re-run (cleanest ThinkProbe validity).
"""
from __future__ import annotations
import json
import numpy as np
import pandas as pd
import pyarrow.parquet as pq
import statsmodels.formula.api as smf
from statsmodels.stats.multitest import multipletests
from scipy.stats import norm

from . import config as C
from .lexical import LEX_FEATURES

_Z = norm.ppf(0.975) + norm.ppf(0.80)  # ~2.80, for 80%-power MDE


# ---------------- data assembly ----------------
def load_frame(english_only: bool = False, valid_col: str = "valid_md") -> pd.DataFrame:
    feats = pd.read_parquet(C.features_path("labelable"))
    labels = pd.read_parquet(C.F_LABELS)
    meta = pq.read_table(
        C.F_POP_LABELABLE,
        columns=["row_id", "language", "scenario_domain", "group_id", "rlen"],
    ).to_pandas()
    df = feats.merge(labels, on="row_id").merge(meta, on="row_id")
    df = df[(df["status"] == "ok") & (df[valid_col])].copy()
    df["log_len"] = np.log(df["lex_word_count"].clip(lower=1))
    if english_only:
        df = df[df["language"] == "en"].copy()
    return df


def _winsor_z(s: pd.Series, lo=0.01, hi=0.99) -> np.ndarray:
    x = s.astype(float)
    ql, qh = x.quantile(lo), x.quantile(hi)
    x = x.clip(ql, qh)
    sd = x.std(ddof=0)
    return (x - x.mean()) / sd if sd > 0 else np.full(len(x), np.nan)


# ---------------- per-feature association (primary) ----------------
def per_feature_association(df: pd.DataFrame, predictor: str = "align_md",
                            features: list[str] | None = None) -> pd.DataFrame:
    features = features or C.STRUCTURAL_FEATURES
    rows = []
    base = pd.DataFrame({
        "x": _winsor_z(df[predictor]),
        "ll": _winsor_z(df["log_len"]),
        # categorical dtype -> patsy treats as factors WITHOUT C() (which is
        # shadowed here by `import config as C`).
        "model": df["model_id"].astype("category").values,
        "dim": df["varied_param"].astype("category").values,
        "lang": df["language"].astype("category").values,
        "grp": df["group_id"].values,
    })
    for f in features:
        yz = _winsor_z(df[f])
        if np.all(np.isnan(yz)):
            rows.append(dict(feature=f, beta=np.nan, ci_low=np.nan, ci_high=np.nan,
                             se=np.nan, pval=np.nan, n=0, note="degenerate"))
            continue
        d = base.copy()
        d["y"] = yz
        d = d.dropna()
        m = smf.ols("y ~ x + ll + model + dim + lang", data=d).fit(
            cov_type="cluster", cov_kwds={"groups": d["grp"]})
        ci = m.conf_int().loc["x"]
        rows.append(dict(feature=f, beta=float(m.params["x"]),
                         ci_low=float(ci[0]), ci_high=float(ci[1]),
                         se=float(m.bse["x"]), pval=float(m.pvalues["x"]),
                         n=int(m.nobs), note=""))
    res = pd.DataFrame(rows)
    ok = res["pval"].notna()
    res["q_bh"] = np.nan
    if ok.any():
        res.loc[ok, "q_bh"] = multipletests(res.loc[ok, "pval"], method="fdr_bh")[1]
    res["signif_bh"] = res["q_bh"] < 0.05
    res["mde_beta"] = _Z * res["se"]  # ~80%-power detectable standardized slope
    return res.sort_values("q_bh").reset_index(drop=True)


# ---------------- predictive: structure vs baseline (CLaude.md) ----------------
def predictive_comparison(df: pd.DataFrame, seed: int = C.SEED) -> pd.DataFrame:
    from sklearn.linear_model import Ridge, LogisticRegression
    from sklearn.model_selection import cross_val_score, GroupKFold
    from sklearn.preprocessing import StandardScaler
    from sklearn.pipeline import make_pipeline

    groups = df["group_id"].values
    gkf = GroupKFold(n_splits=5)
    y_reg = df["align_md"].values
    y_clf = df["with_bias"].astype(int).values

    sets = {
        "baseline(len+lex)": LEX_FEATURES,
        "structure(20)": C.STRUCTURAL_FEATURES,
        "baseline+structure": LEX_FEATURES + C.STRUCTURAL_FEATURES,
    }
    rows = []
    for name, cols in sets.items():
        X = df[cols].fillna(0.0).values
        r2 = cross_val_score(make_pipeline(StandardScaler(), Ridge(alpha=1.0)),
                             X, y_reg, cv=gkf, groups=groups, scoring="r2")
        auc = cross_val_score(
            make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000)),
            X, y_clf, cv=gkf, groups=groups, scoring="roc_auc")
        rows.append(dict(feature_set=name, n_features=len(cols),
                         cv_r2_mean=float(r2.mean()), cv_r2_sd=float(r2.std()),
                         cv_auc_mean=float(auc.mean()), cv_auc_sd=float(auc.std())))
    return pd.DataFrame(rows)


# ---------------- group-level robustness ----------------
def group_level(df: pd.DataFrame, features: list[str] | None = None) -> pd.DataFrame:
    features = features or C.STRUCTURAL_FEATURES
    mags = pd.read_parquet(C.F_BIAS_GROUPS)  # model_id,varied_param,scenario_id,magnitude,n_trials
    keys = C.BIAS_UNIT_ROBUST
    agg = {f: "mean" for f in features}
    agg["log_len"] = "mean"
    gm = df.groupby(keys).agg(agg)
    gm["n"] = df.groupby(keys).size()
    gm = gm.reset_index().merge(mags[keys + ["magnitude", "n_trials"]], on=keys, how="inner")
    gm = gm[gm["n"] >= 5]
    rows = []
    for f in features:
        d = pd.DataFrame({
            "y": _winsor_z(gm[f]), "mag": _winsor_z(gm["magnitude"]),
            "ll": _winsor_z(gm["log_len"]), "w": gm["n_trials"].values})
        d = d.dropna()
        if len(d) < 20 or d["y"].std() == 0:
            rows.append(dict(feature=f, beta=np.nan, pval=np.nan, n_groups=len(d)))
            continue
        m = smf.wls("y ~ mag + ll", data=d, weights=d["w"]).fit()
        rows.append(dict(feature=f, beta=float(m.params["mag"]),
                         pval=float(m.pvalues["mag"]), n_groups=int(m.nobs)))
    res = pd.DataFrame(rows)
    ok = res["pval"].notna()
    res["q_bh"] = np.nan
    if ok.any():
        res.loc[ok, "q_bh"] = multipletests(res.loc[ok, "pval"], method="fdr_bh")[1]
    res["signif_bh"] = res["q_bh"] < 0.05
    return res.sort_values("q_bh").reset_index(drop=True)


# ---------------- refusal vs engagement (secondary) ----------------
def refusal_vs_engagement(seed: int = C.SEED) -> pd.DataFrame:
    """Structural difference between long refusals and (length-matched) engaged traces."""
    eng = pd.read_parquet(C.features_path("labelable"))
    ref = pd.read_parquet(C.features_path("refusal"))
    eng = eng[eng["status"] == "ok"].copy(); eng["is_refusal"] = 0
    ref = ref[ref["status"] == "ok"].copy(); ref["is_refusal"] = 1
    both = pd.concat([eng, ref], ignore_index=True)
    both["log_len"] = np.log(both["lex_word_count"].clip(lower=1))
    rows = []
    for f in C.STRUCTURAL_FEATURES:
        d = pd.DataFrame({"y": _winsor_z(both[f]), "ll": _winsor_z(both["log_len"]),
                          "ref": both["is_refusal"].values}).dropna()
        if d["y"].std() == 0:
            rows.append(dict(feature=f, beta=np.nan, pval=np.nan)); continue
        m = smf.ols("y ~ ref + ll", data=d).fit(cov_type="HC1")
        rows.append(dict(feature=f, beta=float(m.params["ref"]),
                         pval=float(m.pvalues["ref"]), n=int(m.nobs)))
    res = pd.DataFrame(rows)
    ok = res["pval"].notna()
    res["q_bh"] = np.nan
    if ok.any():
        res.loc[ok, "q_bh"] = multipletests(res.loc[ok, "pval"], method="fdr_bh")[1]
    res["signif_bh"] = res["q_bh"] < 0.05
    return res.sort_values("beta", key=lambda s: s.abs(), ascending=False).reset_index(drop=True)


# ---------------- driver ----------------
def run_analysis(verbose: bool = True) -> dict:
    df = load_frame()
    assoc = per_feature_association(df)
    pred = predictive_comparison(df)
    grp = group_level(df)
    df_en = load_frame(english_only=True)
    assoc_en = per_feature_association(df_en)
    refeng = refusal_vs_engagement()

    assoc.to_parquet(C.F_ANALYSIS, index=False)
    assoc_en.to_parquet(C.RESULTS / "analysis_assoc_en.parquet", index=False)
    pred.to_parquet(C.RESULTS / "analysis_predictive.parquet", index=False)
    grp.to_parquet(C.RESULTS / "analysis_grouplevel.parquet", index=False)
    refeng.to_parquet(C.RESULTS / "analysis_refusal.parquet", index=False)

    summary = {
        "n_traces_primary": int(len(df)),
        "n_traces_english": int(len(df_en)),
        "mde_beta_median": float(np.nanmedian(assoc["mde_beta"])),
        "n_assoc_signif_bh": int(assoc["signif_bh"].sum()),
        "top_assoc": assoc.head(5)[["feature", "beta", "q_bh"]].to_dict("records"),
        "predictive": pred.to_dict("records"),
        "n_grouplevel_signif_bh": int(grp["signif_bh"].sum()),
        "n_refusal_signif_bh": int(refeng["signif_bh"].sum()),
    }
    (C.RESULTS / "analysis_summary.json").write_text(json.dumps(summary, indent=2))
    if verbose:
        print(json.dumps(summary, indent=2))
    return summary


if __name__ == "__main__":
    run_analysis()
