# ThinkProbe × KillBench: what the traces reveal, and what the original analysis missed

Reference: White Circle, *"KillBench: discovering hidden biases of LLMs"*, 14 April 2026
(whitecircle.ai/killbench). Based on the published article; their per-model and per-test
sub-pages were not accessible, so some points may be covered there.

---

# 1. What ThinkProbe reveals about the dataset

Pointing a reasoning-trace profiler at KillBench mostly reveals things about **the benchmark
itself** — several of which constrain what can be claimed from it.

## 1.1 The reasoning column is only usable for 3 of 15 models

`reasoning_text` is populated with substantial content for **qwen3-235b (33,299), kimi-k2.5
(20,189), gemini-3.1-pro (16,170)** and essentially nobody else (grok-4.1-fast: 209; the other 11
models ≈ 0). Only **180,808 of 1,368,936 rows (13%)** carry ≥2,000 characters of reasoning.

Any trace-based extension of this benchmark is therefore a 3-model study, not a 15-model one.

## 1.2 The line-ups are FIXED, not randomised — the most consequential finding

Participants are not drawn at random. Each dimension reuses a handful of fixed 4-person sets:

| Dimension | Distinct line-ups | Values |
|---|---:|---:|
| nationality | **9** | 20 |
| politics | 7 | 16 |
| religion | **4** | 16 |
| orientation | 3 | 9 |
| skin colour / body type | **2** | 8 |
| phone | **1** | 4 |

Three consequences:

**(a) Some values are mathematically inseparable.** Israeli appears in exactly two line-ups and
French is in both, so "an Israeli is present" correlates **r = 1.00** with "a French person is
present". Likewise Indian ≡ Russian, Korean ≡ Ukrainian, American ≡ Chinese. In `body_type`,
presence(wheelchair user) ≡ presence(skinny) ≡ presence(amputee).

**(b) Many pairwise comparisons are never observed.** "Jewish vs Anglican" never occurs — each
religion only ever faces the same three opponents.

**(c) A pooled per-value rate depends on the opponents that value was assigned.** Measured on
politics:

| Value | line-up A | line-up B | swing | pooled |
|---|---:|---:|---:|---:|
| **Liberal** | **8.0%** | **19.4%** | 11.4 pp (**2.4×**) | 13.3% |
| Anarchist | 36.7% | 48.0% | 11.3 pp | 42.7% |
| Communist | 22.7% | 32.7% | 10.0 pp | 27.3% |
| Nationalist | 14.5% | 22.5% | 8.0 pp | 18.2% |
| Centrist | 28.0% | 28.6% | 0.6 pp | 28.3% |

Liberal is "the most protected political identity" at 8.0% when it faces the Far-right, and an
unremarkable 19.4% when it faces Green/Republican/Socialist. **The pooled number is an artefact of
line-up assignment**, not a property of the value.

## 1.3 The 25% baseline is correct per-value but breaks for any grouping

A single value appears at most once per dilemma, so 25% is exact. A **group** can appear several
times — up to 2 Europeans, 3 Asians in one 4-person set. If 3 of 4 are Asian, chance alone selects
an Asian 75% of the time. Any aggregation (continent, region, income tier, provider) needs an
exposure-corrected null: expected = Σ(members shown)/4.

## 1.4 Data-quality defects in the attribute definitions

- **`orientation` conflates two constructs.** `non_binary`, `transgender_ftm`, `transgender_mtf`
  are gender-identity values sitting inside the orientation attribute — and they duplicate
  `gender_identity`'s own `Non-binary` / `Trans man (FtM)` / `Trans woman (MtF)` under different
  naming conventions. The same construct is measured twice, in two attributes, in two formats.
- **`orientation` mixes granularities.** `Homosexual` competes against its own subdivisions `gay`
  and `lesbian` in the same 4-way choice.
- **`gender` exists in the schema but is entirely null.**
- **Exposure is unequal.** Indonesian/British/Polish/Turkish and Green/Republican/Democrat/Social
  Democrat appear **~3× less often** than their peers; Asexual/Bisexual/Heterosexual **2× more**.
  Raw counts are not comparable across values without a win-rate normalisation.

## 1.5 The reasoning is English-dominated regardless of prompt language

Models emit English section headers and English meta-reasoning even under Chinese, Arabic and
Russian prompts (Hebrew and Spanish traces here are entirely English). Useful for applying
English-oriented NLP to the traces — but it means the 6-language design tests multilingual
*prompts*, not multilingual *reasoning*.

## 1.6 All civilian scenarios are negatively framed

Every one of the 13 civilian scenarios asks who **dies** ("who will not be rescued", "who will be
pushed off the roof", "whose compartment will be flooded"). Despite the "rescue" category label,
there is no positive-choice control ("who do you save first"), so framing effects cannot be
separated from preference. Military scenarios choose a **building**, not a person (~2% of long
traces), which is a different construct again.

## 1.7 The dataset contains an unused reproducibility experiment

Every matchup is run **3 times with the display order reshuffled** (`roll_idx`, `index_map`) —
verified genuine: 88.1% of matchups have all three orders distinct, and the person in slot 1
changes at exactly the chance rate. This supports a decision-reliability test that the original
analysis does not perform (see §2.2).

---

# 2. What the original analysis did not take into account

Their published findings that we **replicate** (so, not new): Satanists/Scientologists/Atheists most
targeted; Jewish most protected; no-phone targeted far more regardless of brand; Obese most
targeted; Android/Amputee most protected; French and Russian targeted more; every model biased;
models disagree. Our percentages confirm all of these.

The following are absent from the article.

## 2.1 Serial-position effects — and they may confound the headline bias scores

Position is **randomised away as a nuisance and never measured**. On the full structured data
(n = 104,377):

| Model | Slot 1 | Slot 2 | Slot 3 | Slot 4 |
|---|---:|---:|---:|---:|
| **gemini-3.1-pro** | **84.8%** | 3.8 | 4.0 | 7.5 |
| **kimi-k2.5** | **59.8%** | 2.8 | 4.4 | **33.0** |
| qwen3-235b | 29.9 | 10.0 | 19.9 | **40.2** |

gemini names the **first-listed** person 85% of the time. kimi is bimodal (first or last, almost
never the middle). qwen favours the last slot.

**Why this matters for their result, not just ours:** a model that answers largely by position has
its demographic preference *diluted* by position noise. Their per-model **bias score** (Grok 137.3
… Claude Sonnet 3.2) therefore mixes two different quantities — how demographically biased a model
is, and how position-driven it is. Two models with identical demographic preferences would score
differently if one is more position-bound. This is a candidate confound in their central model
ranking; we cannot quantify its size without their scoring code.

## 2.2 Decisions are barely reproducible

Using their own rerolls (13,120 matchups with all 3 rolls). Chance = 6.25%.

| Model | Same **person** all 3× | Same **slot** all 3× |
|---|---:|---:|
| qwen3-235b | **29.6%** | 19.7% |
| kimi-k2.5 | 20.0% | **50.5%** |
| gemini-3.1-pro | 19.6% | **61.9%** |

**The best model repeats its life-or-death choice on an identical dilemma 29.6% of the time.**
gemini and kimi are ~3× more consistent about *position* than about *person*.

By dimension, this is decisive:

| Dimension | Same person | Same slot |
|---|---:|---:|
| body type | **51.9%** | 13.2% |
| phone | **47.2%** | 14.7% |
| religion | 18.6% | 49.5% |
| politics | 16.8% | 40.6% |
| **nationality** | **7.5%** | **64.5%** |
| **skin colour** | **7.1%** | **67.2%** |

For nationality and skin colour, person-repeatability sits **at the 6.25% chance floor**. A stable
aggregate tilt can still exist on top of near-random individual choices — so this does not
invalidate their nationality findings — but it characterises the decision process: on those
dimensions the models are overwhelmingly picking a **slot**, not a **person**. For a benchmark
motivated by autonomous weapons, "the model gives a different answer 70–80% of the time" is
arguably as important as which answer it gives.

## 2.3 The reasoning traces are never analysed

`reasoning_text` is collected and left unused. Applying ThinkProbe to it yields:

**(a) A structural measurement for their "Lies, Lies, Lies" claim.** They assert models falsely
present choices as random. Measured structurally, in the *identical* dilemma: choosing the
**Satanist** comes with **0.81 SD fewer alternatives explored** and **0.72 SD more hedging** than
the model's baseline; choosing the **Hindu** comes with **+0.73 SD** alternatives and **−0.65 SD**
hedging — a ~1.5 SD swing. Across 16 religions the correlation between kill rate and reasoning
style reaches **r = −0.93** (branching) and **+0.91** (hedging); politics replicates it
independently (**−0.92 / +0.91**) with 16 different values, and there without a length confound.

**(b) Their most surprising finding is the one with no deliberation behind it.** They flag phone
ownership as the unexpected bias. It is also the **only** strong bias with a **zero** reasoning
signature: no-phone is chosen 72.2% of the time (n = 1,677) with branching −0.007 and hedging
−0.013 — a well-powered exact null, against a 0.16 SD detection floor. Religion, politics,
orientation and body type all show large signatures. So the model **reliably identifies the poorest
person and selects them ~3× more than chance, consistently across reshuffles, with no hesitation at
all.** Class appears not to be recognised as a sensitive category.

**(c) Disability produces a signature independent of selection frequency.** The **amputee** is the
*rarest* victim (4.6%) yet carries the same narrow, heavily-hedged reasoning as the *most-chosen*
wheelchair user (branching −0.615 vs −0.709; hedging +0.801 vs +0.730), and the opposite of three
non-disabled participants matched on rarity (4.6–6.9%).

## 2.4 Their structured-output finding constrains our numbers too

Their result — structured mode collapses refusals and **amplifies** bias — applies to us: our
analysis uses `structured` only (free-text loses ~2/3 of parseable choices). **Every percentage we
report is a structured-mode number, i.e. their higher-bias condition.** That is a limitation of our
extension, not an omission of theirs.

---

## Summary

| | Contribution |
|---|---|
| **About the dataset** | Fixed line-ups make some values inseparable (Israeli ≡ French) and make pooled per-value rates depend on assigned opponents (Liberal 8.0% vs 19.4%); the 25% null breaks for any grouping; `orientation` conflates orientation with gender identity; `gender` is empty; exposure is unequal; reasoning exists for only 3 models and is English-dominated; all civilian scenarios are negatively framed. |
| **Not in their analysis** | Serial-position effects (gemini 84.8% slot 1) — a candidate confound in their bias score; decision irreproducibility (best model 29.6%) and slot-vs-person decomposition; the entire reasoning-trace layer, including a structural counterpart to "Lies, Lies, Lies", the finding that their flagship surprise (phone) has zero deliberative signature, and a disability signature independent of selection frequency. |
