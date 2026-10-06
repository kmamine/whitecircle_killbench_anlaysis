# KillBench × ThinkProbe

Does the **structure** of an LLM's reasoning trace reveal decision bias that the final answer hides?

This project runs [ThinkProbe](https://github.com/kmamine/ThinkProb) (non-generative structural
profiling of reasoning traces via Thought Graphs) on [KillBench](https://huggingface.co/datasets/whitecircle/killbench)
(White Circle's life-or-death decision-bias benchmark). The question is supervised and falsifiable:
**do ThinkProbe structural features separate biased choices from unbiased ones, beyond a
length + lexical baseline?**

## Headline result

A well-powered, controlled **null**:

- KillBench choices are strongly and model-differentially biased (qwen3-235b most, gemini least).
- ThinkProbe trace structure does **not** separate biased from unbiased choices beyond a
  length + lexical baseline (all |β| ≤ 0.036 at MDE ≈ 0.01).
- The instrument itself is validated: refusal vs. engagement moves 18/20 structural features
  (|β| up to ~1.0).

Side findings about the benchmark itself (fixed line-ups that confound per-value rates, strong
serial-position bias, only 3 of 15 models emitting usable reasoning) are written up in
[WHAT_WE_ADD.md](WHAT_WE_ADD.md) and [BEHAVIOUR_ANALYSIS.md](BEHAVIOUR_ANALYSIS.md).

## Repository layout

```
kbtp/        analysis package (config, data loading, bias labels, feature extraction,
             controlled analysis, comparisons, profiles, figures)
scripts/     numbered pipeline stages + run_all.py
paper/       scripts that build the PDF reports
docs/        analysis plan and design spec
results/     derived tables (CSV/JSON; parquet outputs are gitignored)
figures/     all generated figures
*.md         per-topic analyses and profile metric tables
*.pdf        compiled paper and full analysis
```

Not tracked: `data/` (the 1.7 GB KillBench dataset), `ThinkProb/` (separate repo),
and all `*.parquet` files.

## Setup

1. Python 3.12 environment with `torch`, `transformers`, `sentence-transformers`, `networkx`,
   `scikit-learn`, `scipy`, `pandas`, `pyarrow`, `matplotlib`, `seaborn`.
2. Clone ThinkProb into the project root and install it:
   ```bash
   git clone https://github.com/kmamine/ThinkProb
   pip install -e ThinkProb
   ```
3. Download the KillBench parquet shards into `data/killbench/data/`
   (`train-000xx-of-00011.parquet`) from
   [`whitecircle/killbench`](https://huggingface.co/datasets/whitecircle/killbench).
4. Check paths and the HF cache location in [`kbtp/config.py`](kbtp/config.py).

## Reproduce

```bash
python -m scripts.run_all                 # full pipeline (stage 2 extraction needs a GPU, resumable)
python -m scripts.run_all --skip-extract  # reuse existing features_*.parquet
python -m scripts.run_all --stage 3       # start from a given stage (1 labels · 2 extract · 3 analyze · 4 figures)
```

All randomness uses a fixed seed (`SEED = 42` in `kbtp/config.py`).

## Limitations

Single benchmark; judge-parsed choices; group-level (not per-row) bias labels; ThinkProbe was
built for open-ended reasoning and is applied here to shorter decisional traces; the reasoning
trace may not reflect the model's actual computation.

## License / data

KillBench is released under the White Circle Responsible Use License v1.0. Respect it when
using or publishing derived results.
