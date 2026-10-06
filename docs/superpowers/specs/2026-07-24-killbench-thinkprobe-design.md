# Design Spec — KillBench × ThinkProbe: does reasoning *structure* track demographic bias?

> Status: **approved, in build** · Date: 2026-07-24 · Supersedes the `SESSION_HANDOFF.md` §7 draft.
> Read alongside `CLaude.md` (project charter) and `ThinkProb/CLAUDE.md` (pipeline spec).

---

## 1. Question & hypothesis

`CLaude.md`'s falsifiable question: **do ThinkProbe structural features of a reasoning trace separate biased decisions from fair ones?**

KillBench has **no per-row bias label** — bias is a *statistical* property of many trials (systematic demographic preference, position controlled). So the label must be *constructed*. We reframe the question at two levels:

- **Primary (per-trace, motivated-reasoning framing):** When a model picks a demographic it *systematically favors*, does the trace that led there look structurally different from when it picks a demographic it *disfavors*? Operationalized by a continuous **bias-alignment score** per trace (§4).
- **Robustness (group-level, ecological framing — the handoff's original):** Across groups, does mean trace structure correlate with the group's overall **bias magnitude**?

Both are *supervised* tests with mandatory controls, not a trawl. **A controlled null is a valid deliverable** (`CLaude.md`); we will not manufacture a positive.

## 2. Data (verified across all 11 shards, 2026-07-24)

- Source: `whitecircle/killbench`, 11 parquet shards, 1,368,936 rows, in `data/killbench/data/`. **Not gated.**
- Primary key: **`row_id`**. Reasoning trace: **`reasoning_text`** (distinct from `response_text`). Filter `success == true`.
- Each trial: **exactly 4 participants** differing *only* on `varied_param`; identical age/role. `parsed_response.chosen_<dim>` = demographic value of the chosen participant. Positions reshuffled across `roll_idx` 0–2 (`index_map`).
- Reasoning is emitted by effectively **3 models**: `qwen/qwen3-235b-a22b`, `moonshotai/kimi-k2.5`, `google/gemini-3.1-pro-preview` (grok-4.1-fast contributes ~200; treat as negligible/robustness only).

### Filter cascade (verified counts, ≥2000-char traces)
| population | count | use |
|---|---:|---|
| long (≥2000 chars) | 180,808 | — |
| structured | 105,234 | — |
| structured, non-refusal | 88,035 | — |
| **structured, non-refusal, single-dim, `chosen_<dim>` present = LABELABLE** | **69,867** | **primary** |
| long refusals (`is_refusal`) | ~24,600 | secondary (refusal-vs-engagement) |

- **`structured` only** (freetext loses ~2/3 of choice labels).
- **Single-dim only** for the primary: 8 dims (`nationality, religion, skin_color, body_type, orientation, gender_identity, politics, phone`). Intersectional combos held for later.
- ≥2000 chars = ThinkProbe needs structure to graph (validity spot-check passed last session).

## 3. Populations extracted (Decision 1 — full, no time-forced sampling)

Compute is not the constraint (§7). We extract ThinkProbe features over:
1. **Labelable** — all 69,867 (primary).
2. **Long refusals** — for the refusal-vs-engagement secondary.

No subsampling. Length is controlled *in the model* (§6), not by discarding data. Extract once, filter downstream.

## 4. Bias construction (CPU, full 1.37M data)

Because every trial has **exactly 4 options**, the position-and-availability-corrected null choice probability of any demographic value is **0.25**.

**Per-value win-rate** within a unit: `winrate(v) = chosen(v) / available(v)`, expected 0.25 under no bias. Position bias does not manufacture value bias because value↔position is decorrelated across rerolls/setups (aggregated over a unit).

- **Unit for favorability = model × dim.** Matches KillBench's own definition ("does model M prefer value X on dimension D?"). Scenario/language enter analysis as controls (§6), not as part of the bias definition. `model × dim × scenario` computed too, for robustness.
- **Per-trace bias-alignment score** (primary predictor, continuous):
  `align_i = winrate_LOO(v_chosen_i) − 0.25`, where `winrate_LOO` excludes trace *i* itself (no self-leakage). `align > 0` ⇒ chose a favored value; `align < 0` ⇒ disfavored. Magnitude = strength.
  - Binary cut (`with_bias = align > 0`) kept for interpretability/robustness.
  - Require the chosen value to have availability ≥ `MIN_AVAIL` (e.g. 20) in the unit for a stable win-rate; else the trace is unlabeled (still extracted, excluded from primary).
- **Group bias magnitude** (robustness predictor): per `model × dim × scenario` group, **Cramér's V** (equivalently normalized G-test effect size) of the chosen-value count vector vs the availability-weighted null. Per-group CI via trial count / bootstrap.

All bias quantities are derived from the **full dataset** (all 1.37M rows contribute to win-rates/availability), not just the extracted subset — maximally precise, CPU-only.

## 5. Feature extraction (GPU)

- ThinkProbe `segment(reasoning_text, use_nli=True)` → `(TUs, edges, embeddings)` → `compute_profile` → **22-dim** `CognitiveProfile` (`ThinkProb/CLAUDE.md`). Per-trace output keyed by `row_id`.
- **Non-generative** (regex + MiniLM TextTiling + DeBERTa-large NLI) — no generative LLM in the loop; avoids circular validity.
- Benchmarked at **0.27 s/trace** on H100 (§7). Parallel, **VRAM-aware**: workers sized to *free* VRAM measured at run time (shared GPUs — GPU 1 has the headroom, ~2.94 GB/worker). Idempotent/resumable on `row_id`.
- Also record, per trace: `reasoning_text` length (chars + tokens) and a **lexical feature set** (hedging/uncertainty word counts, etc.) for the baseline in §6.

## 6. Controlled analysis (mandatory controls — `CLaude.md`)

**Primary — per-trace mixed-effects**, per structural feature *f* (of 22):
```
f  ~  align_score  +  log_len  +  (1 | model)  +  (1 | scenario)  +  (1 | group_id)
```
- **Length control**: `log_len` as covariate *and* a length-residualized robustness pass. Report the effect **beyond length**.
- **Lexical baseline**: a model using only length + lexical features. The structural signal must **beat** it (nested comparison / ΔR²). Report both.
- **Multiple comparisons**: 22 features pre-registered here; **Benjamini–Hochberg** across them. Report **effect sizes + CIs**, not just p.
- **MDE**: report the minimum detectable effect at this N per feature.

**Robustness — group-level**: `mean_f_group ~ bias_magnitude + mean_log_len` weighted by group trial count; BH across features. Concordance with the per-trace result is the headline evidence check.

**Secondary — refusal vs engagement**: same 22 features, `is_refusal` (long refusals vs matched non-refusals); cheap, near-certain to show *some* structural difference ⇒ guaranteed interpretable finding even if the primary is a valid null.

Fixed seeds; error bars on everything.

## 7. Compute budget (measured 2026-07-24)

- H100 NVL, `segment()`: mean 0.27 s/trace, p90 0.40 s, peak 2.94 GB VRAM.
- Full 69,867 labelable ≈ **~1.5 h** at ~4 parallel workers; well inside the 3–4 h budget. GPUs are **shared** (GPU0 ~3.6 GB free, GPU1 ~17.8 GB free at spec time) — size workers to live free VRAM; prefer GPU 1.

## 8. Reproducibility & layout

Package `kbtp/` + `scripts/`, per `CLaude.md` conventions:
```
kbtp/config.py     paths, seeds, thresholds, the 22 feature names, filter defs
kbtp/data.py       parquet filtering → labelable + refusal manifests (row_id keyed)
kbtp/bias.py       win-rates, per-trace align score, group Cramér's V
kbtp/extract.py    parallel VRAM-aware ThinkProbe extraction (resumable on row_id)
kbtp/lexical.py    length + lexical baseline features
kbtp/analysis.py   mixed-effects, baselines, BH, effect sizes/CIs, MDE
kbtp/figures.py    figures
scripts/01_build_labels.py 02_extract_features.py 03_analyze.py 04_figures.py
scripts/run_all.py     regenerates every number/figure from raw parquet
```
Fixed seeds, saved config snapshot per run, outputs to `results/` (parquet) + `figures/`. One script (`run_all.py`) reproduces everything.

## 9. Deliverables & limitations

- Short honest report: result + controls + limitations. Optional measured LinkedIn post (curiosity, not takedown; tag White Circle; skim license first).
- **Limitations stated up front**: single benchmark; judge/parser-derived choices; ThinkProbe validity on argumentative (vs open-ended) traces; reasoning from only 3 models (not model-diverse); constructed (not native) bias labels; unfaithful-CoT caveat (structure is a *signal*, not the model's "psychology" — avoid cognitive/psychological framing per `CLaude.md`).

## 10. Corrections to `CLaude.md` (carried from handoff, re-verified)

- Dataset id `whitecircle/killbench`; **not gated**; no token needed.
- **No per-row bias label** — constructed here (§4).
- Reasoning exists for **3 models**, not model-diverse.
- Full dataset *was* downloaded (user override); "subsample only" caveat kept accurate in writeup — we now extract the *full labelable set*, so that caveat is relaxed for extraction but the benchmark itself is still one dataset.

## Decisions locked
① structured-only, single-dim primary · ② full labelable + refusals, no time-sampling · ③ per-trace continuous bias-alignment as primary + group-level magnitude as robustness · ④ mandatory length + lexical controls, BH over 22, effect sizes/CIs/MDE · ⑤ refusal-vs-engagement secondary guarantees a reportable finding.
