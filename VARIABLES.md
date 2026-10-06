# Variable inventory — what KillBench studies vs. what ThinkProbe studies

All levels/counts verified against the full dataset (1,368,936 rows, 11 shards) and the
ThinkProbe source, 2026-07-25.

---

## A. KillBench's variables (White Circle)

### A1. Manipulated — the experimental design

| Variable | Type | Levels | Notes |
|---|---|---:|---|
| `varied_param` | factor | **18** | the demographic axis under test: **8 single** + **10 intersectional** pairs |
| demographic value | factor (nested) | see below | the 4 participants differ *only* on this |
| `scenario_id` / `scenario_name` | factor | **20** | 13 civilian + 7 military dilemmas |
| `scenario_domain` | factor | **2** | `civilian` (~98% of rows), `military` |
| `language` | factor | **6** | `ar`, `en`, `es`, `he`, `ru`, `zh` |
| `model_id` | factor | **15** | the models under test |
| `roll_idx` | factor | **3** | position re-roll — the position-bias control |
| `index_map` | list[int] | — | which display slot each participant occupies |
| `source_kind` | factor | **2** | `structured` (forced format) vs `freetext` |
| `system_prompt` / `user_prompt` | text | — | the prompt actually sent |

**Demographic levels per single dimension** (the values being contrasted):

| Dimension | Levels | Rows | Examples |
|---|---:|---:|---|
| `nationality` | 20 | 302,040 | American, Australian, Brazilian, British … |
| `politics` | 16 | 220,428 | Anarchist, Centrist, Communist, Conservative … |
| `religion` | 16 | 189,720 | Anglican, Atheist, Buddhist, Catholic … |
| `orientation` | 9 | 129,168 | Asexual, Bisexual, Heterosexual, Homosexual … |
| `skin_color` | 8 | 87,048 | Brown-skinned, Dark-skinned, East Asian appearance … |
| `body_type` | 8 | 87,048 | Amputee, Athletic, Muscular, Obese … |
| `phone` | 4 | 43,524 | Android, No phone, Nokia, iPhone |
| `gender_identity` | 4 | 42,120 | Cisgender, Non-binary, Trans man (FtM), Trans woman (MtF) |

Held constant within a trial (so they can't confound the contrast): `gender`, `age`, `role`.
Military-only participant fields: `building_type`, `enemy_count`, `civilian_count`,
`civilian_nationality`, `civilian_religion`, `tactical_idx`, `item_kind`.

### A2. Measured — the outcomes

| Variable | Type | Meaning |
|---|---|---|
| `parsed_response.chosen_number` | int 1–4 | which displayed slot was chosen |
| `parsed_response.chosen_number_original` | int 1–4 | de-shuffled index (pre-`index_map`) |
| `parsed_response.chosen_<dim>` | factor | **the demographic value chosen** — the bias outcome |
| `parsed_response.is_refusal` | bool | model declined to choose |
| `parsed_response.reason` / `confidence` | text | judge-extracted justification |
| `parsed_response.parse_method` | factor | `structured` vs `gemini` (judge-parsed) |
| `response_text` | text | the final answer |
| **`reasoning_text`** | text | **the CoT trace — our input, unused by their bias metric** |
| `success`, `error`, `usage_json` | mixed | run bookkeeping |

### A3. Derived / bookkeeping
`row_id` (primary key), `run_id`, `setup_id` = `{varied_param}:{scenario_id}:{language}`, `group_id`.

### A4. Their dependent variable
Bias = **systematic demographic preference aggregated over trials**, with position controlled by
the 3 re-rolls. It is a *population-level* quantity: there is **no per-row bias label** in the data.

---

## B. ThinkProbe's variables (ours) — computed from `reasoning_text`

### B1. The 22-dim CognitiveProfile (the metrics)

| # | Metric | Family | Definition (from source) |
|---:|---|---|---|
| 1 | `branching_factor` | breadth | `\|E_BRCH\| / \|V\|` |
| 2 | `unique_perspective_count` | breadth | `\|N_RFR\|` (reframing nodes) |
| 3 | `domain_spread` | breadth | distinct semantic clusters among BRS+HYP nodes (agglomerative, cosine 0.45) |
| 4 | `first_idea_diversity` | breadth | mean pairwise cosine distance among first-HYP embeddings |
| 5 | `max_elaboration_chain` | depth | longest directed path of only ELAB edges |
| 6 | `mean_branch_depth` | depth | mean depth from root nodes in the semantic subgraph |
| 7 | `specificity_gradient` | depth | slope of lexical specificity vs sequential position |
| 8 | `reasoning_density` | depth | fraction of nodes in ≥1 semantic (non-SEQ) edge |
| 9 | `exploration_exploitation_ratio` | structure | `\|N_EXPLORATION\| / \|N_ELABORATION\|` |
| 10 | `backtracking_rate` | structure | `\|E_BACK\| / \|E_sem\|` |
| 11 | `cross_branch_connectivity` | structure | fraction of branch pairs joined by SYNT/SUPP |
| 12 | `convergence_index` | structure | `Σ d_in(SYN) / (\|V\| · mean d_in)` |
| 13 | `graph_density` | structure | `\|E_sem\| / (\|V\|·(\|V\|−1))` |
| 14 | `revision_depth` | structure | mean sequential distance across BACK edges |
| 15 | `self_reflection_rate` | metacognitive | proportion of MET nodes |
| 16 | `critique_to_hypothesis_ratio` | metacognitive | CRT / HYP nodes |
| 17 | `hedging_density` | metacognitive | proportion of TUs with uncertainty markers |
| 18 | `perspective_taking` | metacognitive | proportion of RFR nodes |
| 19 | `token_per_idea` | efficiency | total tokens / `\|N_RFR\|` |
| 20 | `redundancy_ratio` | efficiency | fraction of TU pairs with cosine > 0.90 |
| 21 | `avg_tokens` | summary | trace token count — **used as length control, not as structure** |
| 22 | `avg_tus` | summary | number of thought units — **length control** |

→ **20 structural metrics tested; 2 summaries reserved as controls.**

### B2. Graph primitives (intermediate, per trace)

| Object | Levels | Meaning |
|---|---:|---|
| Thought Unit (TU) | ~13–18/trace | segmented reasoning span |
| `BoundaryClass` | 8 | BACKTRACK, BRANCH, META, CONVERGENCE, ELABORATION, CONTRAST, SUPPORT, NONE |
| `NodeType` | 12 | HYP, RFR, ANA, BRS / JUS, SPC, IMP, CON / CRT, CMP, MET / SYN |
| `NodeFamily` | 4 | EXPLORATION, ELABORATION, EVALUATION, CONVERGENCE |
| `EdgeType` | 8 | ELAB, BRCH, BACK, SYNT, CRIT, SUPP, CONT, SEQ |
| embeddings | 384-dim | MiniLM per-TU vectors |

**Profile** = the 22-vector aggregated over a unit (per model, per group, per bias bin) — the object
used for radar/centroid, PERMANOVA, PCA archetypes, per-PC regression, stability (ICC), sensitivity.

---

## C. Variables we constructed to bridge A ↔ B

Because A4 gives no per-row bias label, these were derived:

| Variable | Built from | Definition |
|---|---|---|
| `winrate(value, unit)` | A2 `chosen_<dim>` + availability | chosen ÷ available; **0.25 = no bias** (always 4 options) |
| `align_md` | winrate | leave-one-out winrate of the chosen value − 0.25 (per-trace, continuous) |
| `align_abs` | align | \|alignment\| = bias *strength*, direction-free |
| `align_bin` / `align_q4` | align | with-vs-against bias; alignment quartiles |
| `favor_class` | winrate | favored / neutral / disfavored (win-rate bins) |
| `magnitude` (group) | choice distribution | availability-weighted RMS deviation from 0.25 + G-test |
| `model_tier` | A1 `model_id` | qwen=high, kimi=mid, gemini=low bias |
| `chose_<value>` | A2 | **binary per-demographic outcome** — the per-group analysis |
| 11 lexical features | `reasoning_text` | hedge/booster/negation/connective/first-person rates, counts, words-per-sentence — the **baseline structure must beat** |
| `log_len`, `pos_v` | `reasoning_text`, `index_map` | length control; display position of a value (position-bias control) |

---

## D. Coverage — what we used and what we left on the table

| KillBench variable | Our usage |
|---|---|
| `model_id` (15) | **3 used** — only qwen3-235b, kimi-k2.5, gemini-3.1-pro emit substantial reasoning (grok ~200 traces; 11 models ≈ 0) |
| `varied_param` (18) | **8 single used**; 10 intersectional **not analyzed** |
| `source_kind` (2) | **`structured` only** — `freetext` loses ~2/3 of choice labels to parse failure |
| `scenario_domain` (2) | both, but military is ~2% of long traces (underpowered) |
| `language` (6) | all, as a control; English-only robustness re-run |
| `roll_idx` / `index_map` | as position controls + profile stability (ICC) across re-rolls |
| `reasoning_text` | **the input** — the column their bias metric never touches |
| `response_text`, `reason` | not used |
| trace length | ≥2000 chars required (ThinkProbe needs structure to graph) |

**Analysed population:** 69,867 traces (structured · non-refusal · ≥2000 chars · single-dim ·
choice parsed) + 13,351 long refusals. From 1,368,936 total rows.

### The core asymmetry
They manipulate **who is in the dilemma** and measure **who gets chosen**.
We measure **the shape of the deliberation in between** — a variable present in their data
(`reasoning_text`) but absent from their bias metric.
