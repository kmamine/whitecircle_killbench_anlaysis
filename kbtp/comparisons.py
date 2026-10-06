"""Execute the full bias <-> metric and bias <-> profile comparison sweep.

ThinkProbe-centered. Fast, vectorized, cluster-robust core so the entire ~10.6k-cell
grid runs in minutes. Each analysis is error-isolated and tagged with its tier; results
land in results/ and drive the ThinkProbe-first report.

Inference notes:
- Numeric bias (continuous/binary/ordinal): residualize metric & bias on the control set,
  take the partial correlation as the effect size, with a *cluster-robust* slope test
  (clustered by matchup group_id) — computed vectorially across all 20 metrics at once.
- Categorical bias: partial eta^2 from adding the class dummies over the control model (F-test).
- Group bias magnitude: group-level WLS (weighted by trials).
BH within each family; effect sizes + CIs throughout; MDE reported.
"""
from __future__ import annotations
import warnings
import numpy as np
import pandas as pd
import pyarrow.parquet as pq
from scipy import stats
from statsmodels.stats.multitest import multipletests

from . import config as C
from .lexical import LEX_FEATURES
from . import plan as P

warnings.filterwarnings("ignore")
RNG = np.random.default_rng(C.SEED)
FEATURES22 = C.FEATURES  # profile = full 22-dim


# ------------------------------------------------------------ data
def load_full_frame() -> pd.DataFrame:
    feats = pd.read_parquet(C.features_path("labelable"))
    labels = pd.read_parquet(C.F_LABELS)
    meta = pq.read_table(C.F_POP_LABELABLE, columns=[
        "row_id", "language", "scenario_domain", "group_id", "setup_id", "roll_idx", "rlen",
    ]).to_pandas()
    df = feats.merge(labels, on="row_id").merge(meta, on="row_id")
    df = df[(df["status"] == "ok") & (df["valid_md"])].copy()
    df["log_len"] = np.log(df["lex_word_count"].clip(lower=1))
    return df


def derive_bias_vars(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["align_abs"] = df["align_md"].abs()
    df["align_bin"] = (df["align_md"] > 0).astype(float)
    df["align_q4"] = pd.qcut(df["align_md"].rank(method="first"), 4, labels=[1, 2, 3, 4]).astype(int)
    wr = df["align_md"] + C.NULL_CHOICE_P  # chosen value's win-rate
    df["favor_class"] = np.where(wr > 0.30, "favored", np.where(wr < 0.20, "disfavored", "neutral"))
    tier = {"qwen/qwen3-235b-a22b": "high", "moonshotai/kimi-k2.5": "mid",
            "google/gemini-3.1-pro-preview": "low"}
    df["model_tier"] = df["model_id"].map(tier)
    # group magnitude onto traces
    mag = pd.read_parquet(C.F_BIAS_GROUPS)[C.BIAS_UNIT_ROBUST + ["magnitude", "n_trials"]]
    df = df.merge(mag, on=C.BIAS_UNIT_ROBUST, how="left")
    df["short_model"] = df["model_id"].str.split("/").str[-1]
    return df


_BIAS_COL = {"ALIGN_C": "align_md", "ALIGN_C_MDS": "align_mds", "ALIGN_ABS": "align_abs",
             "ALIGN_BIN": "align_bin", "ALIGN_Q4": "align_q4"}


def _subset(df: pd.DataFrame, factor: str, level: str) -> pd.DataFrame:
    if factor == "POOLED":
        return df
    col = {"MODEL": "short_model", "DIM": "varied_param",
           "DOMAIN": "scenario_domain", "LANG": "language"}[factor]
    return df[df[col] == level]


def _controls(control: str) -> list[str]:
    return {"C0_raw": [], "C1_len": ["log_len"],
            "C2_len_lex": ["log_len"] + LEX_FEATURES}[control]


def _resid(X: np.ndarray, A: np.ndarray) -> np.ndarray:
    """Residualize columns of A on design X (with intercept) via least squares."""
    coef, *_ = np.linalg.lstsq(X, A, rcond=None)
    return A - X @ coef


# Study-design nuisances always partialled out (only 3 models -> model is a major
# confounder; a bias<->structure link must be WITHIN model/dim/language, not between).
_NUISANCE = ["short_model", "varied_param", "language"]


def _design(d: pd.DataFrame, num_cols: list[str], exclude: list[str] | None = None) -> np.ndarray:
    """Intercept + numeric controls + dummies for any non-constant nuisance factor."""
    exclude = exclude or []
    n = len(d)
    parts = [np.ones((n, 1))]
    for c in num_cols:
        parts.append(d[c].to_numpy(float).reshape(-1, 1))
    for f in _NUISANCE:
        if f in exclude:
            continue
        if f in d.columns and d[f].nunique() > 1:
            parts.append(pd.get_dummies(d[f], drop_first=True).to_numpy(float))
    return np.column_stack(parts)


# ------------------------------------------------------------ numeric-bias family (vectorized, cluster-robust)
def numeric_family(df: pd.DataFrame, bias_col: str, control_cols: list[str],
                   metrics: list[str]) -> pd.DataFrame:
    cols = [bias_col, "group_id"] + control_cols + metrics + \
           [c for c in _NUISANCE if c in df.columns]
    d = df[list(dict.fromkeys(cols))].dropna()
    n = len(d)
    if n < 50 or d[bias_col].std() == 0:
        return pd.DataFrame([dict(metric=m, partial_r=np.nan, beta=np.nan, se=np.nan,
                                  pval=np.nan, n=n) for m in metrics])
    X = _design(d, control_cols)
    b = _resid(X, d[bias_col].to_numpy(float).reshape(-1, 1)).ravel()
    Y = _resid(X, d[metrics].to_numpy(float))            # n x k
    bb = float(b @ b)
    slope = (b @ Y) / bb                                  # k
    E = Y - np.outer(b, slope)                            # residuals n x k
    # cluster-robust meat: sum_g (sum_i in g b_i E_ij)^2
    codes = pd.factorize(d["group_id"].to_numpy())[0]
    G = codes.max() + 1
    contrib = b[:, None] * E                              # n x k
    meat = np.zeros(Y.shape[1])
    # group sums via bincount per column
    for j in range(Y.shape[1]):
        s = np.bincount(codes, weights=contrib[:, j], minlength=G)
        meat[j] = np.sum(s * s)
    se = np.sqrt(meat) / bb
    yy = np.einsum("ij,ij->j", Y, Y)
    partial_r = (b @ Y) / np.sqrt(bb * yy)
    with np.errstate(divide="ignore", invalid="ignore"):
        t = slope / se
    pval = 2 * stats.norm.sf(np.abs(t))
    return pd.DataFrame(dict(metric=metrics, partial_r=partial_r, beta=slope, se=se,
                             pval=pval, n=n))


# ------------------------------------------------------------ categorical-bias family
def categorical_family(df: pd.DataFrame, class_col: str, control_cols: list[str],
                       metrics: list[str]) -> pd.DataFrame:
    cols = [class_col] + control_cols + metrics + [c for c in _NUISANCE if c in df.columns]
    d = df[list(dict.fromkeys(cols))].dropna()
    n = len(d)
    rows = []
    if n < 50 or d[class_col].nunique() < 2:
        return pd.DataFrame([dict(metric=m, eta2=np.nan, pval=np.nan, n=n) for m in metrics])
    # MODEL_TIER is derived from model -> exclude short_model nuisance to avoid collinearity
    excl = ["short_model"] if class_col == "model_tier" else []
    dummies = pd.get_dummies(d[class_col], drop_first=True).to_numpy(float)
    Xc = _design(d, control_cols, exclude=excl)
    Xf = np.column_stack([Xc, dummies])
    Y = d[metrics].to_numpy(float)
    Rr = _resid(Xc, Y); Rf = _resid(Xf, Y)
    rss_r = np.einsum("ij,ij->j", Rr, Rr)
    rss_f = np.einsum("ij,ij->j", Rf, Rf)
    df1 = dummies.shape[1]; df2 = n - Xf.shape[1]
    # guard numerical rank-deficiency (rss_f should be <= rss_r); clip partial eta^2 to [0,1]
    gain = np.clip(rss_r - rss_f, 0.0, None)
    eta2 = np.clip(gain / rss_r, 0.0, 1.0)
    with np.errstate(divide="ignore", invalid="ignore"):
        F = (gain / df1) / (rss_f / df2)
    pval = np.where(np.isfinite(F), stats.f.sf(F, df1, df2), np.nan)
    return pd.DataFrame(dict(metric=metrics, eta2=eta2, pval=pval, n=n))


# ------------------------------------------------------------ group-level magnitude family
def group_family(df: pd.DataFrame, control_cols: list[str], metrics: list[str]) -> pd.DataFrame:
    keys = C.BIAS_UNIT_ROBUST
    g = df.groupby(keys).agg({**{m: "mean" for m in metrics},
                              **{c: "mean" for c in control_cols},
                              "magnitude": "first", "n_trials": "first"})
    g["n"] = df.groupby(keys).size()
    g = g[g["n"] >= 5].dropna(subset=["magnitude"])
    rows = []
    if len(g) < 20:
        return pd.DataFrame([dict(metric=m, beta=np.nan, pval=np.nan, n_groups=len(g)) for m in metrics])
    mag = (g["magnitude"] - g["magnitude"].mean()) / g["magnitude"].std()
    Xctrl = [((g[c] - g[c].mean()) / g[c].std()).to_numpy() for c in control_cols]
    # Partial out model / dimension identity at the group level too, so this is
    # consistent with the per-trace path. Without it, "group bias magnitude"
    # correlations are largely BETWEEN-model differences (ecological confound).
    gi = g.reset_index()
    nu_parts = []
    for f in ("model_id", "varied_param"):
        if f in gi.columns and gi[f].nunique() > 1:
            nu_parts.append(pd.get_dummies(gi[f], drop_first=True).to_numpy(float))
    X = np.column_stack([np.ones(len(g)), mag.to_numpy()] + Xctrl + nu_parts)
    # Group-level fits get unstable (|std beta| can exceed 1 via suppression) when the
    # design has many dummies relative to the number of groups. Require 4x headroom.
    if len(g) < 4 * X.shape[1]:
        return pd.DataFrame([dict(metric=m, beta=np.nan, pval=np.nan, n_groups=len(g),
                                 note="underpowered_group_design") for m in metrics])
    w = g["n_trials"].to_numpy(float); w = w / w.mean()
    for m in metrics:
        y = (g[m] - g[m].mean()) / (g[m].std() or 1)
        sw = np.sqrt(w)
        coef, *_ = np.linalg.lstsq(X * sw[:, None], y.to_numpy() * sw, rcond=None)
        resid = y.to_numpy() * sw - (X * sw[:, None]) @ coef
        dof = len(g) - X.shape[1]
        sigma2 = (resid @ resid) / dof
        xtx_inv = np.linalg.inv((X * sw[:, None]).T @ (X * sw[:, None]))
        se = np.sqrt(sigma2 * xtx_inv[1, 1])
        t = coef[1] / se
        rows.append(dict(metric=m, beta=float(coef[1]), pval=float(2 * stats.t.sf(abs(t), dof)),
                         n_groups=int(len(g))))
    return pd.DataFrame(rows)


# ------------------------------------------------------------ metric sweep driver
def run_metric_sweep(df: pd.DataFrame, tiers=(1, 2, 3)) -> pd.DataFrame:
    reg = P.enumerate_metric_comparisons()
    reg = reg[reg["tier"].isin(tiers)]
    out = []
    for _, fam in reg.iterrows():
        sub = _subset(df, fam["stratum_factor"], fam["stratum_level"])
        ctrl = _controls(fam["control"])
        bid = fam["bias_op"]; kind = fam["bias_kind"]
        try:
            if kind in ("continuous", "binary", "ordinal"):
                res = numeric_family(sub, _BIAS_COL[bid], ctrl, P.METRICS)
                res["effect"] = res["partial_r"]
            elif kind == "categorical":
                col = "favor_class" if bid == "FAVOR_CLASS" else "model_tier"
                res = categorical_family(sub, col, ctrl, P.METRICS)
                res["effect"] = res["eta2"]
            elif kind == "group":
                res = group_family(sub, ctrl, P.METRICS)
                res["effect"] = res["beta"]
            else:
                continue
        except Exception as e:  # noqa: BLE001
            res = pd.DataFrame([dict(metric=m, effect=np.nan, pval=np.nan, err=str(e)[:80])
                                for m in P.METRICS])
        res["bias_op"] = bid; res["stratum_factor"] = fam["stratum_factor"]
        res["stratum_level"] = fam["stratum_level"]; res["control"] = fam["control"]
        res["tier"] = fam["tier"]
        ok = res["pval"].notna()
        res["q_bh"] = np.nan
        if ok.any():
            res.loc[ok, "q_bh"] = multipletests(res.loc[ok, "pval"], method="fdr_bh")[1]
        out.append(res)
    allres = pd.concat(out, ignore_index=True)
    allres["signif_bh"] = allres["q_bh"] < 0.05
    return allres


# ============================================================ PROFILE SWEEP
N_CAP, N_CAP_CLF, MIN_N, N_PERM, PCA_K = 6000, 20000, 300, 499, 5


def _bin_labels(d: pd.DataFrame, bias_op: str):
    if bias_op in ("ALIGN_C", "ALIGN_C_MDS", "ALIGN_ABS"):
        col = _BIAS_COL[bias_op]
        return pd.qcut(d[col].rank(method="first"), 4, labels=["Q1", "Q2", "Q3", "Q4"]).astype(str)
    if bias_op == "ALIGN_BIN":
        return np.where(d["align_bin"] > 0.5, "with", "against")
    if bias_op == "ALIGN_Q4":
        return d["align_q4"].map({1: "Q1", 2: "Q2", 3: "Q3", 4: "Q4"}).astype(str)
    if bias_op == "FAVOR_CLASS":
        return d["favor_class"].astype(str)
    if bias_op == "MODEL_TIER":
        return d["model_tier"].astype(str)
    if bias_op == "MAG_GROUP":
        return pd.qcut(d["magnitude"].rank(method="first"), 3, labels=["low", "mid", "high"]).astype(str)
    return None


def _z(A: np.ndarray) -> np.ndarray:
    sd = A.std(0); sd[sd == 0] = 1.0
    return (A - A.mean(0)) / sd


def _pillai(Z: np.ndarray, codes: np.ndarray) -> float:
    """Pillai's trace for one-way MANOVA on Z (n x p) with integer group codes."""
    p = Z.shape[1]; gmean = Z.mean(0)
    H = np.zeros((p, p)); groups = np.unique(codes)
    for g in groups:
        Zg = Z[codes == g]; d = (Zg.mean(0) - gmean).reshape(-1, 1)
        H += len(Zg) * (d @ d.T)
    T = (Z - gmean).T @ (Z - gmean)
    try:
        return float(np.trace(H @ np.linalg.pinv(T)))
    except Exception:
        return np.nan


def _centroid_spread(Z: np.ndarray, codes: np.ndarray) -> float:
    cents = np.array([Z[codes == g].mean(0) for g in np.unique(codes)])
    if len(cents) < 2:
        return np.nan
    from itertools import combinations
    return float(max(np.linalg.norm(cents[i] - cents[j]) for i, j in combinations(range(len(cents)), 2)))


def _perm_p(Z, codes, stat_fn, obs):
    cnt = 1
    for _ in range(N_PERM):
        if stat_fn(Z, RNG.permutation(codes)) >= obs:
            cnt += 1
    return cnt / (N_PERM + 1)


def _profile_one(d: pd.DataFrame, bias_op: str, method: str) -> dict:
    bins = _bin_labels(d, bias_op)
    if bins is None:
        return dict(effect=np.nan, pval=np.nan, status="no_bins")
    d = d.assign(_bin=np.asarray(bins))
    d = d[d["_bin"] != "nan"].dropna(subset=["_bin"])
    if len(d) < MIN_N or d["_bin"].nunique() < 2:
        return dict(effect=np.nan, pval=np.nan, status="insufficient_n", n=len(d))
    feats = d[FEATURES22].to_numpy(float)
    # nuisance+length-residualized profile (valid within-model/dim/lang test)
    Xnu = _design(d, ["log_len"])
    featsR = _resid(Xnu, feats)
    d = d.reset_index(drop=True)

    if method in ("PM2_distance", "PM3_permanova"):
        idx = RNG.choice(len(d), min(len(d), N_CAP), replace=False)
        Z = _z(featsR[idx]); codes = pd.factorize(d["_bin"].to_numpy()[idx])[0]
        fn = _centroid_spread if method == "PM2_distance" else _pillai
        obs = fn(Z, codes)
        return dict(effect=obs, pval=_perm_p(Z, codes, fn, obs), status="ok", n=len(idx))

    if method == "PM4_classify":
        from sklearn.linear_model import LogisticRegression
        from sklearn.model_selection import cross_val_score, GroupKFold
        from sklearn.preprocessing import StandardScaler
        from sklearn.pipeline import make_pipeline
        s = d.sample(min(len(d), N_CAP_CLF), random_state=C.SEED)
        y = pd.factorize(s["_bin"])[0]; groups = s["group_id"].values
        multi = len(np.unique(y)) > 2
        scoring = "roc_auc_ovr" if multi else "roc_auc"
        gkf = GroupKFold(n_splits=5)
        def auc(cols):
            X = s[cols].fillna(0).values
            return cross_val_score(make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000)),
                                   X, y, cv=gkf, groups=groups, scoring=scoring).mean()
        a_prof = auc(FEATURES22); a_base = auc(LEX_FEATURES)
        return dict(effect=float(a_prof), pval=np.nan, auc_profile=float(a_prof),
                    auc_baseline=float(a_base), auc_delta=float(a_prof - a_base),
                    status="ok", n=len(s))

    if method == "PM5_archetype":
        from sklearn.cluster import KMeans
        from sklearn.decomposition import PCA
        from sklearn.metrics import silhouette_score
        idx = RNG.choice(len(d), min(len(d), N_CAP), replace=False)
        s = d.iloc[idx]
        Z = _z(featsR[idx]); pcs = PCA(n_components=min(10, Z.shape[1]),
                                       random_state=C.SEED).fit_transform(Z)
        best_k, best_sil, best_lab = 2, -1, None
        for k in range(2, 7):
            lab = KMeans(n_clusters=k, n_init=5, random_state=C.SEED).fit_predict(pcs)
            sil = silhouette_score(pcs, lab, sample_size=min(2000, len(pcs)), random_state=C.SEED)
            if sil > best_sil:
                best_k, best_sil, best_lab = k, sil, lab
        ct = pd.crosstab(best_lab, s["_bin"].values)
        chi2, p, *_ = stats.chi2_contingency(ct)
        cv = np.sqrt(chi2 / (ct.values.sum() * (min(ct.shape) - 1)))
        return dict(effect=float(cv), pval=float(p), k=best_k, silhouette=float(best_sil),
                    status="ok", n=len(s))

    if method == "PM6_pc_regress":
        from sklearn.decomposition import PCA
        Z = _z(feats); pcs = PCA(n_components=PCA_K, random_state=C.SEED).fit_transform(Z)
        dd = d.copy()
        for i in range(PCA_K):
            dd[f"_pc{i}"] = pcs[:, i]
        if bias_op in _BIAS_COL:
            r = numeric_family(dd, _BIAS_COL[bias_op], ["log_len"], [f"_pc{i}" for i in range(PCA_K)])
            r = r.dropna(subset=["pval"])
            if r.empty:
                return dict(effect=np.nan, pval=np.nan, status="degenerate")
            best = r.reindex(r["partial_r"].abs().sort_values(ascending=False).index).iloc[0]
            return dict(effect=float(best["partial_r"]), pval=float(best["pval"]),
                        q_bh=float(multipletests(r["pval"], method="fdr_bh")[1].min()), status="ok", n=len(dd))
        col = "favor_class" if bias_op == "FAVOR_CLASS" else ("model_tier" if bias_op == "MODEL_TIER" else None)
        if col is None:
            return dict(effect=np.nan, pval=np.nan, status="na_for_group")
        r = categorical_family(dd, col, ["log_len"], [f"_pc{i}" for i in range(PCA_K)]).dropna(subset=["pval"])
        if r.empty:
            return dict(effect=np.nan, pval=np.nan, status="degenerate")
        best = r.reindex(r["eta2"].abs().sort_values(ascending=False).index).iloc[0]
        return dict(effect=float(best["eta2"]), pval=float(best["pval"]), status="ok", n=len(dd))

    if method == "PM7_stability":
        # ICC across the up-to-3 rerolls of each setup, averaged over the 22 features, per bin
        iccs = []
        for _, g in d.groupby("_bin"):
            per = []
            for f in FEATURES22:
                sub = g[["setup_id", "roll_idx", f]].dropna()
                if sub["setup_id"].nunique() < 5:
                    continue
                grp = sub.groupby("setup_id")[f]
                msw = grp.var(ddof=1).mean()               # within-setup (reroll) variance
                msb = sub.groupby("setup_id")[f].mean().var(ddof=1)  # between-setup variance
                if not np.isfinite(msw) or (msb + msw) == 0:
                    continue
                per.append(msb / (msb + msw))
            if per:
                iccs.append(np.mean(per))
        if len(iccs) < 2:
            return dict(effect=np.nan, pval=np.nan, status="insufficient_n")
        return dict(effect=float(np.ptp(iccs)), pval=np.nan, icc_min=float(min(iccs)),
                    icc_max=float(max(iccs)), status="ok", n=len(d))

    if method in ("PM1_radar", "PM8_sensitivity"):
        Z = _z(featsR)
        spread = _centroid_spread(Z, pd.factorize(d["_bin"])[0])
        if method == "PM1_radar":
            return dict(effect=float(spread), pval=np.nan, status="ok", n=len(d))
        # PM8: sensitivity = mean across bins of the profile's std across domains
        sens = []
        for b, gb in d.groupby("_bin"):
            if gb["scenario_domain"].nunique() < 2:
                continue
            dm = gb.groupby("scenario_domain")[FEATURES22].mean()
            sens.append(dm.std(0).mean())
        if not sens:
            return dict(effect=np.nan, pval=np.nan, status="single_domain")
        return dict(effect=float(np.mean(sens)), pval=np.nan, status="ok", n=len(d))
    return dict(effect=np.nan, pval=np.nan, status="unknown_method")


def run_profile_sweep(df: pd.DataFrame, tiers=(1, 2, 3)) -> pd.DataFrame:
    reg = P.enumerate_profile_comparisons()
    reg = reg[reg["tier"].isin(tiers)]
    out = []
    for _, a in reg.iterrows():
        sub = _subset(df, a["stratum_factor"], a["stratum_level"])
        try:
            r = _profile_one(sub, a["bias_op"], a["profile_method"])
        except Exception as e:  # noqa: BLE001
            r = dict(effect=np.nan, pval=np.nan, status=f"err:{type(e).__name__}:{str(e)[:60]}")
        r.update(bias_op=a["bias_op"], profile_method=a["profile_method"],
                 stratum_factor=a["stratum_factor"], stratum_level=a["stratum_level"], tier=a["tier"])
        out.append(r)
    res = pd.DataFrame(out)
    ok = res["pval"].notna()
    res["q_bh"] = np.nan
    if ok.any():
        res.loc[ok, "q_bh"] = multipletests(res.loc[ok, "pval"], method="fdr_bh")[1]
    return res


if __name__ == "__main__":
    df = derive_bias_vars(load_full_frame())
    print("frame:", len(df))
    t1 = run_metric_sweep(df, tiers=(1,))
    print("\n== Tier-1 metric sweep (top) ==")
    print(t1[["bias_op", "control", "metric", "effect", "q_bh", "signif_bh"]]
          .sort_values("q_bh").head(8).round(4).to_string(index=False))
    p1 = run_profile_sweep(df, tiers=(1,))
    print("\n== Tier-1 profile sweep ==")
    print(p1[["bias_op", "profile_method", "stratum_level", "effect", "pval", "status"]]
          .round(4).to_string(index=False))
