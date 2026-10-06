"""Stage 3b: run the FULL bias<->metric and bias<->profile comparison sweep (all tiers)."""
import json
import numpy as np
import pandas as pd
from kbtp import comparisons as X, config as C

if __name__ == "__main__":
    df = X.derive_bias_vars(X.load_full_frame())
    print(f"frame: {len(df)}", flush=True)

    print("== metric sweep ==", flush=True)
    m = X.run_metric_sweep(df, tiers=(1, 2, 3))
    m.to_parquet(C.RESULTS / "comparisons_metric_results.parquet", index=False)
    print(f"metric: {len(m)} tests", flush=True)

    print("== profile sweep ==", flush=True)
    p = X.run_profile_sweep(df, tiers=(1, 2, 3))
    p.to_parquet(C.RESULTS / "comparisons_profile_results.parquet", index=False)
    print(f"profile: {len(p)} analyses", flush=True)

    # ---- summaries centered on the bias LENS ops (exclude MODEL_TIER = pure model identity)
    lens = ["ALIGN_C", "ALIGN_C_MDS", "ALIGN_ABS", "ALIGN_BIN", "ALIGN_Q4", "FAVOR_CLASS", "MAG_GROUP"]
    mv = m.dropna(subset=["effect", "pval"])
    summary = {
        "metric_tests": int(len(m)),
        "metric_valid": int(mv.shape[0]),
        "metric_signif_bh": int((m["q_bh"] < 0.05).sum()),
        "metric_max_abs_effect_lens": float(mv[mv.bias_op.isin(lens)]["effect"].abs().max()),
        "metric_median_abs_effect_lens": float(mv[mv.bias_op.isin(lens)]["effect"].abs().median()),
        "metric_max_abs_effect_modeltier": float(mv[mv.bias_op == "MODEL_TIER"]["effect"].abs().max()),
        "profile_analyses": int(len(p)),
        "profile_ok": int((p["status"] == "ok").sum()),
        "profile_signif_bh": int((p["q_bh"] < 0.05).sum()),
    }
    # PM4 predictive delta (profile over length+lexical baseline), lens ops only
    if "auc_delta" in p.columns:
        pm4 = p[(p.profile_method == "PM4_classify") & p.bias_op.isin(lens) & p.auc_delta.notna()]
        summary["pm4_auc_delta_median"] = float(pm4["auc_delta"].median()) if len(pm4) else None
        summary["pm4_auc_delta_max"] = float(pm4["auc_delta"].max()) if len(pm4) else None
    (C.RESULTS / "sweep_summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2), flush=True)
    print("== sweep done ==", flush=True)
