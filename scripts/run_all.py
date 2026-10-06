"""Regenerate every number and figure from raw parquet.

Usage:
    python -m scripts.run_all                # full pipeline (extraction is the long step)
    python -m scripts.run_all --skip-extract # reuse existing features_*.parquet
    python -m scripts.run_all --stage 3      # run from a given stage onward (1..4)

Stages: 1 build labels · 2 extract features (GPU) · 3 analyze · 4 figures.
Stage 2 is resumable; rerunning continues where it stopped.
"""
from __future__ import annotations
import argparse


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--skip-extract", action="store_true")
    ap.add_argument("--stage", type=int, default=1, help="start from stage 1..4")
    args = ap.parse_args()

    if args.stage <= 1:
        from kbtp import data, bias
        data.build_populations()
        bias.build_bias()
    if args.stage <= 2 and not args.skip_extract:
        from kbtp import extract
        extract.run_extraction("labelable")
        extract.run_extraction("refusal")
    if args.stage <= 3:
        from kbtp import analysis, comparisons, config as C
        analysis.run_analysis()
        # full enumerated sweep: 9,420 bias<->metric tests + 1,192 bias<->profile analyses
        df = comparisons.derive_bias_vars(comparisons.load_full_frame())
        comparisons.run_metric_sweep(df).to_parquet(
            C.RESULTS / "comparisons_metric_results.parquet", index=False)
        comparisons.run_profile_sweep(df).to_parquet(
            C.RESULTS / "comparisons_profile_results.parquet", index=False)
    if args.stage <= 4:
        from kbtp import figures, figures_v2, plan
        plan.build_registry()      # comparison registry CSVs
        figures.fig_bias_landscape(); figures.fig_winrate_heatmap()  # bias-descriptive
        figures_v2.make_all()      # the ThinkProbe-first figures (f1-f6)
        from kbtp import findings
        findings.run(verbose=False)      # per-demographic actionable findings
        findings.fig_amplification()     # f7, f8
    print("== run_all complete ==")


if __name__ == "__main__":
    main()
