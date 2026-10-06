# Session Handoff — KillBench × ThinkProbe

> ⚠️ **SUPERSEDED (2026-07-25). The study is COMPLETE.** The current source of truth is:
> **[REPORT.md](REPORT.md)** (results) and
> **[docs/superpowers/specs/2026-07-24-killbench-thinkprobe-design.md](docs/superpowers/specs/2026-07-24-killbench-thinkprobe-design.md)** (design).
> The pipeline lives in `kbtp/` + `scripts/`; regenerate everything with `python -m scripts.run_all --skip-extract`.
> Everything below describes the earlier **Windows** environment and the pre-analysis state — kept only for history.
> Note the machine changed to a **Linux server (2× H100)** and the "CUDA reinstall" blocker is moot; env is conda `thinkbench_kma`.
>
> **Headline result:** a well-powered controlled **null** — KillBench choices are strongly, model-differentially
> biased (qwen3-235b most, gemini least), but ThinkProbe trace *structure* does **not** separate biased from unbiased
> choices beyond a length+lexical baseline (all |β|≤0.036 at MDE≈0.01; structure does not beat baseline). The instrument
> is validated: refusal-vs-engagement moves 18/20 features (|β| up to ~1.0).
>
> ---
>
> _Original handoff below (2026-07-23, Windows, pre-analysis):_

---

## 0. TL;DR — where we are

- Environment built, full dataset downloaded, ThinkProbe pipeline understood, CPU-benchmarked.
- Discovered the project's core assumption is wrong: **KillBench has no per-row "biased/fair" label** — bias is an aggregate property that must be *constructed*.
- A **design has been proposed and is awaiting user approval** (group-level bias-magnitude analysis). See §7.
- **Blocking prerequisite before any extraction run: reinstall torch with CUDA** (current wheel is CPU-only; CPU can't meet the 3–4 h time budget). See §6.

---

## 1. Environment (verified)

- **Conda env:** `killbench_thinkprob` — Python **3.12.13**
  - Env Python: `C:\Users\m.a.kerkouri\AppData\Local\miniconda3\envs\killbench_thinkprob\python.exe`
- **Package manager:** `uv` 0.11.29. Installed ThinkProb editable:
  ```bash
  uv pip install --python "C:/Users/m.a.kerkouri/AppData/Local/miniconda3/envs/killbench_thinkprob/python.exe" \
      --only-binary litellm -e "c:/Users/m.a.kerkouri/Downloads/killbench-thinkprob/ThinkProb"
  ```
- **`litellm` gotcha (important):** the pinned resolution `litellm==1.93.0` ships an **sdist with a Rust extension** that fails to build on this machine — a GNU coreutils `link.exe` (Git/MSYS on PATH) shadows MSVC's linker (`link: extra operand`). Fix used: **`--only-binary litellm`** → resolves to **`litellm==1.91.4`** (wheel). Keep this flag on any clean reinstall, or pin `litellm==1.91.4` in `pyproject.toml`.
- **Installed key versions:** `thinkbench 0.1.0` (editable), `torch 2.13.0` **(CPU-only build)**, `transformers`, `sentence-transformers 5.6.0`, `networkx 3.6.1`, `scikit-learn 1.9.0`, `scipy 1.18.0`, `pandas`, `pyarrow 25.0.0`, `numpy`, `matplotlib`, `seaborn`, `pydantic`. `huggingface_hub 1.24.0` present; **`datasets` is NOT installed** (we read parquet directly with pyarrow).
- **Hardware:** NVIDIA **RTX 5070 Laptop GPU, 8 GB VRAM**, driver 573.24 (Blackwell / sm_120). CPU: 32 logical cores. **RAM: 31.7 GB** total.
- **HF model cache (downloaded this session):** `sentence-transformers/all-MiniLM-L6-v2`, `cross-encoder/nli-deberta-v3-large` (~1.5 GB) under `~/.cache/huggingface/hub`. Symlinks unsupported on this Windows box (degraded cache, harmless).

---

## 2. Dataset (verified, downloaded)

- **Repo ID is `whitecircle/killbench`** — NOT `whitecircle-ai/killbench` (the `-ai` one is a redirect). `CLaude.md` has the wrong ID.
- **It is NOT gated** (`"gated": false`, `"private": false`). `CLaude.md`'s "gated / accept license" note is wrong. No HF token needed.
- **Downloaded in full** (user explicitly overrode the spec's "don't download full" rule) to:
  `data/killbench/` — **1.7 GB**, 11 parquet shards `data/train-0000{0..10}-of-00011.parquet` + `LICENSE`, `README.md`.
- **Total rows: 1,368,936.** License: `white-circle-responsible-use-license-v1.0` (skim before publishing derived results).
- **`.gitignore` created** at repo root excluding `data/killbench/`, `*.parquet`, caches, etc. This repo root is **not a git repo yet** (only nested `ThinkProb/` has `.git`).

### Schema (columns that matter)
- **`reasoning_text`** — the CoT/reasoning trace (ThinkProbe input). Separate from **`response_text`** (final answer).
- **`parsed_response`** (struct): `chosen_number` (1–4, post-shuffle), `chosen_number_original`, `chosen_<dim>` (e.g. `chosen_nationality`), **`is_refusal`**, `reason`, `parse_method` (`structured` | `gemini`).
- **`participants_displayed`** (list of 4): demographic attrs; only the tested `varied_param` dimension(s) vary, rest null.
- **`varied_param`** — bias dimension: 8 single (`nationality`, `religion`, `skin_color`, `body_type`, `orientation`, `gender_identity`, `politics`, `phone`) + 10 intersectional combos.
- **`model_id`**, **`scenario_id`**, **`scenario_name`**, **`scenario_domain`** (`civilian`|`military`), **`language`** (ar/en/es/he/ru/zh), **`source_kind`** (`freetext`|`structured`), **`group_id`**, **`setup_id`** (`{varied_param}:{scenario_id}:{language}`), **`roll_idx`** (0–2 position-shuffle), `index_map`.

### KillBench design (from dataset card)
Life-or-death dilemmas: model picks 1 of 4 participants who differ **only** on the tested dimension. **Bias = systematic demographic preference aggregated over trials** (position controlled via 3 rerolls + `index_map`). 15 models, 6 languages, 20 scenarios (13 civilian / 7 military). Free-text responses parsed by a Gemini judge → so `parsed_response` can be judge output, distinct from raw text.

---

## 3. Key data findings (verified across all 11 shards)

- **`reasoning_text` ≥ 2000 chars: 180,808 traces total** (the usable long-trace population).
- **Only 3 models emit substantial reasoning:** `moonshotai/kimi-k2.5` (~85k), `qwen/qwen3-235b-a22b` (~73k), `google/gemini-3.1-pro-preview` (~22k). `x-ai/grok-4.1-fast` 620; all other 11 models ≈ 0. **"Model" is effectively a 3-level stratum.**
- **13.6%** of long traces are **refusals** (`is_refusal`) — long refusal deliberation; exclude from primary or analyze separately.
- **Choice-parse coverage among non-refusal long traces:**
  | source_kind | non-refusal long traces | `chosen_number` present | `chosen_<dim>` present |
  |---|---:|---:|---:|
  | freetext | 68,204 | 46.0% | 33.1% |
  | **structured** | 88,035 | **100%** | **79.4%** |
  → **Use `structured` only** for anything needing the model's choice; freetext loses ~2/3 of labels.
- **Labelable population** (structured, ≥2000 chars, non-refusal, single-dim, `chosen_<dim>` present): **69,867 traces.**
- **Group counts by granularity** (unit of analysis for group-level label):
  | grain | populated groups | groups ≥20 traces | median traces/group |
  |---|---:|---:|---:|
  | model × dim | 27 | 25 | 1636 |
  | model × dim × language | 154 | 125 | 286 |
  | **model × dim × scenario** (proposed primary) | 366 | 293 | 116 |
  | model × dim × scenario × language | 1931 | 1027 | 22 |
- **Bias-magnitude estimability (full data):** at model×dim×scenario×lang grain, **10,359 populated groups, median 36 trials/group** (6,807 with ≥30). Bias scores are precisely estimable from the full 1.37M rows (CPU, no GPU).
- Domain skew: ~98% civilian, only ~3.7k long military traces. Languages fairly even except `zh` (~10k). `structured` 105k vs `freetext` 75k long traces.
- **ThinkProbe validity gate (spot check): PASS.** Sampled English non-refusal freetext traces are genuine multi-sentence deliberation (hypotheses, numbered branches, meta-reasoning, constraint-weighing). Still TODO: inspect a handful of *constructed graphs* on these traces (spec requirement).

---

## 4. ThinkProbe pipeline (code read)

- Entry point: `ThinkProb/src/thinkbench/extract/segmenter.py` → **`segment(raw_cot, use_nli=True)`** returns **`(tus, edges, embeddings)`** (3 values).
- 5 passes: (0/1) structural + cue-phrase segmentation → (2) TextTiling w/ MiniLM soft boundaries → (3) semantic trajectory BRCH/ELAB → (4) cross-segment SYNT/BACK → **(5) NLI edge refinement with `cross-encoder/nli-deberta-v3-large`**.
- **Cost driver = Pass 5 NLI.** Per trace ≈ `3 hypotheses × 3-window × n_TUs` DeBERTa-large forward passes. Everything else (metrics, clustering) is trivial by comparison.
- Models loaded lazily as singletons in `src/thinkbench/utils/models.py` (`get_embed_model`, `get_nli_model`). Both auto-select CUDA if `torch.cuda.is_available()`, else CPU.
- 22-dim `CognitiveProfile` + all schemas in `src/thinkbench/extract/schemas.py`.
- **⚠ Stale script:** `scripts/extract_graphs.py` does `tus, edges = segment(trace["raw_cot"])` — **wrong arity** (segment returns 3) and expects `raw_cot`/`trace_id` keys that don't exist in KillBench. Don't reuse as-is; call `segment()` directly and map `reasoning_text` → input.

---

## 5. Benchmark (measured, CPU, single process)

30 real `reasoning_text` traces ≥2000 chars (`torch.cuda.is_available()==False`):

| metric | value |
|---|---|
| mean | **12.5 s/trace** |
| median | 9.3 s |
| p90 | 23.5 s |
| mean TUs/trace | 12.9 |
| longest sampled (14.7k chars / 55 TUs) | 50.7 s |
| one-time model load/download | ~65 s |

- Cost is **super-linear in trace length** (more TUs → more NLI pairs).
- Single-process CPU is impractical (days–weeks for the full subset). 32-core multiprocessing is RAM-bound (~2–2.5 GB/worker, only ~2 GB free at benchmark time) and torch already multithreads → realistic net gain ~5–7×, not 32×.
- **GPU per-trace time NOT yet measured** (torch is CPU-only). *(Estimate)* ~0.4–0.8 s/trace on the RTX 5070 → 3–4 h budget ≈ **~20–28k traces**. Must confirm after CUDA reinstall.

---

## 6. BLOCKING prerequisite — CUDA torch reinstall

Current `torch 2.13.0` is CPU-only. To meet the user's **3–4 h time budget** at a useful sample size, extraction must run on the RTX 5070. RTX 5070 = **Blackwell (sm_120)** → needs a **CUDA 12.8 (cu128)** build, `torch >= 2.7`.

*(Unverified command — confirm exact version availability first):*
```bash
uv pip install --python "C:/Users/m.a.kerkouri/AppData/Local/miniconda3/envs/killbench_thinkprob/python.exe" \
    --index-url https://download.pytorch.org/whl/cu128 torch
# then verify:
#   python -c "import torch; print(torch.cuda.is_available(), torch.cuda.get_device_name(0))"
```
Then re-run the benchmark (script in §9) to get the real GPU per-trace time and **lock the sample size N to the 3–4 h budget**. DeBERTa-large fits in 8 GB easily (fp32 ~1.6 GB; use fp16 for ~2× throughput). **User must confirm they're OK with the reinstall** — it was proposed but not yet approved.

---

## 7. Proposed design (AWAITING USER APPROVAL)

User's three hard conditions: **(1)** run ≤ 3–4 h, **(2)** sufficient statistical power, **(3)** produce findings.

**Label decision (user chose): group-level bias magnitude.** (Most defensible — matches KillBench's own aggregate definition; avoids the circularity of a choice-derived per-row label.) The naive version (~24 model×dim means) is underpowered; reconciled with power via fine granularity + hierarchical modeling.

### Five-stage plan
1. **Bias magnitude (CPU, minutes, full 1.37M data).** Per group at **model × dim × scenario** (primary; add `× language` as robustness), compute a continuous bias score from the `chosen_<dim>` distribution vs. an availability-and-position-corrected null (Cramér's V / normalized G-test effect size), with a per-group CI from trial count.
2. **Trace sampling (the time lever).** Sample **~20–25k** structured / non-refusal / ≥2000-char / choice-present traces, stratified to (a) cover well-populated groups, (b) enough traces/group for a stable feature mean, (c) **length-balanced across the bias-magnitude range** (mandated length control). Final N set after GPU benchmark.
3. **ThinkProbe extraction (GPU, the 3–4 h budget).** Requires §6 reinstall. Run 22-feature extraction over the sample.
4. **Controlled analysis.** Mixed-effects `structural_feature ~ bias_magnitude + trace_length + (1|group) + (1|model)`, per feature, **BH-corrected over 22 features**, effect sizes + CIs. Mandatory controls: length residualization **and** a **lexical baseline** (length + hedging/uncertainty word counts) the structural signal must beat. Report the minimum detectable effect (MDE).
5. **Guaranteed reportable output.** Secondary analysis: **refusal-vs-engagement** trace structure (`is_refusal`) — cheap, near-certain to show *some* structural difference, so there's an interpretable finding even if the primary is a (valid) null. **Do NOT manufacture a positive** — a controlled null is a legitimate deliverable (per spec).

### Decisions baked in (open to change)
① `structured`-mode only; ② primary grain model×dim×scenario; ③ GPU reinstall prerequisite; ④ continuous bias score (not binary).

### Immediate next steps for the new session
1. Get user approval on the design + CUDA reinstall.
2. Do the reinstall (§6), verify CUDA, re-benchmark, lock N.
3. Write the spec to `docs/superpowers/specs/YYYY-MM-DD-killbench-thinkprobe-design.md` (brainstorming flow was in progress; next skill step is `writing-plans`).
4. Build modules per `CLaude.md` conventions: data loading/filtering, bias-magnitude, sampling, ThinkProbe feature extraction, controlled analysis, figures — fixed seeds, saved config, one script regenerating every number.

---

## 8. Corrections to `CLaude.md` (project spec has errors)

- **Dataset ID:** `whitecircle/killbench`, not `whitecircle-ai/killbench`.
- **Not gated:** no license-acceptance / token step needed.
- **No per-row bias label exists** — the spec's premise of "KillBench's bias/fairness ground truth per row" is not directly in the data; it must be constructed (see §7).
- **Reasoning traces exist for only 3 models** (kimi-k2.5, qwen3-235b, gemini-3.1-pro) — not model-diverse.
- Filename is `CLaude.md` (odd casing); fine on Windows, would not auto-load on case-sensitive filesystems.
- Full dataset **was** downloaded (user override); keep the "subsample only" limitation accurate in the writeup.

---

## 9. Reusable scripts

Scratchpad scripts from this session live under a session-temp dir and **won't persist** for the new session. Recreate as needed. The CPU benchmark script (adapt for GPU by ensuring CUDA torch is installed — `segment()` auto-uses GPU):

```python
# bench_extract.py — measure segment() per-trace time on real >=2000-char traces
import sys, time, glob
sys.path.insert(0, r"c:/Users/m.a.kerkouri/Downloads/killbench-thinkprob/ThinkProb/src")
import numpy as np, pyarrow.parquet as pq, torch
print("cuda:", torch.cuda.is_available())
f = sorted(glob.glob(r"c:/Users/m.a.kerkouri/Downloads/killbench-thinkprob/data/killbench/data/*.parquet"))[0]
r = [x for x in pq.read_table(f, columns=["reasoning_text"]).column("reasoning_text").to_pylist() if x and len(x) >= 2000]
r.sort(key=len); sample = [r[i] for i in np.linspace(0, len(r)-1, 30).astype(int)]
from thinkbench.extract.segmenter import segment
segment(sample[0], use_nli=True)  # warmup + model load
times = []
for tr in sample:
    t0 = time.perf_counter(); segment(tr, use_nli=True); times.append(time.perf_counter()-t0)
print(f"mean {np.mean(times):.2f}s median {np.median(times):.2f}s")
```

Reading the dataset (no `datasets` pkg — use pyarrow):
```python
import pyarrow.parquet as pq, pyarrow.compute as pc, glob
files = sorted(glob.glob(r"c:/Users/m.a.kerkouri/Downloads/killbench-thinkprob/data/killbench/data/*.parquet"))
t = pq.read_table(files[0], columns=["reasoning_text","varied_param","model_id","source_kind","parsed_response"])
lens = pc.utf8_length(pc.fill_null(t.column("reasoning_text"), ""))
t = t.filter(pc.greater_equal(lens, 2000))
```
Note: set `PYTHONIOENCODING=utf-8` when printing traces (multilingual; Windows cp1252 console errors otherwise).
