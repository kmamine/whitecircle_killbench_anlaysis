# Kill / no-kill distribution by nationality

170,779 person-level nationality dilemmas (13 civilian scenarios, 15 models, 6 languages).
Military scenarios excluded here — those choose a *building*, not a person.
Data: `results/killrate_nationality.parquet`, `results/killrate_nationality_by_model.csv`.
Figures (simple diverging bars, anchored at the 25% fair line):
- `figures/n1_simple_nationality.png` — the pooled distribution
- `figures/n2_by_model_nationality.png` — small multiples, one panel per model
- `figures/n3_disagreement_nationality.png` — the 8 nationalities the models disagree about most

**Direction is uniform and verified across all 13 civilian scenarios**: the chosen participant is
the one who *dies* ("will not enter the bunker and will die", "Who will the drone not rescue?",
"Who will be pushed off the roof?", "Whose compartment will be flooded?"). No scenario asks who to
save, so no sign-flipping is needed.

**Null = 25.00%** — every dilemma shows exactly 4 people differing only on nationality, so under no
bias each should be chosen 25% of the time. Position is controlled by the 3 re-rolls.

---

## Pooled distribution (all 15 models)

| Nationality | Available | **Killed** | Spared | Kill rate | 95% CI | vs 25% | kill : spared |
|---|---:|---:|---:|---:|---|---:|---|
| Russian | 38,108 | 12,012 | 26,096 | **31.52%** | 31.06–31.99 | **+6.52** | 1 : 2.17 |
| French | 38,177 | 11,475 | 26,702 | **30.06%** | 29.60–30.52 | **+5.06** | 1 : 2.33 |
| Australian | 38,425 | 11,493 | 26,932 | **29.91%** | 29.45–30.37 | **+4.91** | 1 : 2.34 |
| Turkish | 17,861 | 4,977 | 12,884 | 27.87% | 27.21–28.53 | +2.87 | 1 : 2.59 |
| Indonesian | 17,843 | 4,738 | 13,105 | 26.55% | 25.91–27.21 | +1.55 | 1 : 2.77 |
| Polish | 17,963 | 4,728 | 13,235 | 26.32% | 25.68–26.97 | +1.32 | 1 : 2.80 |
| German | 38,238 | 10,057 | 28,181 | 26.30% | 25.86–26.74 | +1.30 | 1 : 2.80 |
| Iranian | 38,078 | 9,955 | 28,123 | 26.14% | 25.70–26.59 | +1.14 | 1 : 2.83 |
| Ukrainian | 38,323 | 9,946 | 28,377 | 25.95% | 25.52–26.39 | +0.95 | 1 : 2.85 |
| British | 17,820 | 4,449 | 13,371 | 24.97% | 24.33–25.61 | −0.03 ᶰˢ | 1 : 3.01 |
| Brazilian | 38,351 | 9,541 | 28,810 | 24.88% | 24.45–25.31 | −0.12 ᶰˢ | 1 : 3.02 |
| American | 38,154 | 9,469 | 28,685 | 24.82% | 24.39–25.25 | −0.18 ᶰˢ | 1 : 3.03 |
| Egyptian | 38,231 | 8,945 | 29,286 | 23.40% | 22.97–23.82 | −1.60 | 1 : 3.27 |
| Chinese | 38,154 | 8,752 | 29,402 | 22.94% | 22.52–23.36 | −2.06 | 1 : 3.36 |
| Mexican | 38,312 | 8,660 | 29,652 | 22.60% | 22.19–23.02 | −2.40 | 1 : 3.42 |
| Korean | 38,323 | 8,570 | 29,753 | 22.36% | 21.95–22.78 | −2.64 | 1 : 3.47 |
| Indian | 38,108 | 8,383 | 29,725 | 22.00% | 21.58–22.42 | −3.00 | 1 : 3.55 |
| Japanese | 38,249 | 8,408 | 29,841 | 21.98% | 21.57–22.40 | −3.02 | 1 : 3.55 |
| Nigerian | 38,221 | 8,258 | 29,963 | 21.61% | 21.20–22.02 | −3.39 | 1 : 3.63 |
| Israeli | 38,177 | 7,963 | 30,214 | **20.86%** | 20.45–21.27 | **−4.14** | 1 : 3.79 |

**17 of 20 deviate significantly from 25%** (BH q<0.05; `ns` = British, Brazilian, American).
Spread **10.7 pp** — a Russian is **1.51×** more likely to be chosen to die than an Israeli.

---

## The economic hypothesis fails *on average* — see the correction

> **Superseded in part by [KILL_NOKILL_BLOCS.md](KILL_NOKILL_BLOCS.md).** The small pooled
> economic effect below is a **cancellation of two opposite per-model biases**: qwen3-235b makes
> lower-income participants **+13.3%** more likely to die (z=10.1) while gemini-3.1-pro makes them
> **−8.5%** less likely (z=−6.5). Wealth matters a great deal per model; the models simply disagree
> on the direction, so the average is ~0. Do not read the pooled row as "models ignore wealth".

The intuitive prediction — *models value richer lives more* — is **not supported in the pooled
average**, where the direction is mildly reversed:

| Grouping | Kill rate by bloc | Test |
|---|---|---|
| **Economic** | upper-middle 25.81% · high 25.24% · lower-middle **23.82%** | F=0.74, **p=0.49** |
| **Global North / South** | North 25.24% · South 24.81% | F=0.03, **p=0.86** |
| **Continent** | Oceania 29.91% · Europe 27.92% · S.Am 24.88% · N.Am 23.71% · Asia 23.32% · Africa 22.50% | F=3.50, **p=0.044** |
| **Cultural** | Catholic Europe 28.86% · Orthodox 28.73% · Anglosphere 26.92% … Sub-Saharan Africa 21.61% · Israel 20.86% | F=2.50, p=0.11 |

Poorer nationalities are chosen to die **less** often. The organising axis is geographic and
geopolitical — **Europe/Oceania are sacrificed most; Asia and Africa least** — not income.

---

## The finding that breaks the pooled table: the models disagree

| Nationality | qwen3-235b | kimi-k2.5 | gemini-3.1-pro | max gap |
|---|---:|---:|---:|---:|
| **Ukrainian** | **34.6%** | 24.3% | **21.7%** | **12.9 pp** |
| **French** | 22.2% | 29.1% | **35.0%** | **12.8 pp** |
| **British** | **18.2%** | 23.2% | 27.0% | 8.8 pp |
| **Israeli** | 25.5% | 21.4% | **16.7%** | 8.8 pp |
| Iranian | 30.4% | 25.7% | 25.5% | 4.9 pp |
| Korean | 18.7% | 24.9% | 25.4% | 6.7 pp |
| Egyptian | 27.3% | 21.7% | 23.3% | 5.6 pp |
| Russian | 28.9% | 28.3% | 28.0% | 0.9 pp |

**Cross-model agreement (r over the 20 rates):** qwen3 ↔ gemini **−0.20**, qwen3 ↔ kimi +0.15,
kimi ↔ gemini +0.76.

qwen3 and gemini are **anti-correlated**: they largely protect opposite nationalities. So the
pooled column is an average of models that disagree, and it *understates* individual bias —
per-model spreads are **16.4 pp** (qwen3) and **18.3 pp** (gemini) versus 10.7 pp pooled.

### Conflict dyads — where it gets concrete

| Dyad | qwen3-235b | kimi-k2.5 | gemini-3.1-pro |
|---|---|---|---|
| Russian vs **Ukrainian** | 28.9 vs 34.6 → **Ukrainian −5.7** | 28.3 vs 24.3 → Russian +4.0 | 28.0 vs 21.7 → Russian **+6.3** |
| **Israeli** vs Iranian | 25.5 vs 30.4 → Israeli −4.9 | 21.4 vs 25.7 → Israeli −4.3 | 16.7 vs 25.5 → Israeli **−8.8** |
| Chinese vs American | 27.3 vs 21.2 → Chinese **+6.1** | 25.5 vs 24.2 → +1.3 | 24.1 vs 23.4 → +0.7 |

- All three protect the **Israeli** over the **Iranian**; gemini most strongly (−8.8 pp).
- On **Russia/Ukraine the direction flips**: kimi and gemini sacrifice the Russian more, while
  **qwen3 sacrifices the Ukrainian more than anyone else in the entire dataset (34.6%)**.
- qwen3 (Chinese-origin) is the only model that sacrifices the **Chinese** participant well above
  the **American** (+6.1 pp) — i.e. not a simple in-group preference.

---

## Consequences for the analysis plan

1. **Per-model is the unit of analysis.** Pooling averages away opposing patterns. Every
   nationality result must be reported per model, with the pooled figure as context only.
2. **Economic framing is out** as a primary lens; geographic and geopolitical-dyad framings are in.
3. **This is where ThinkProbe earns its place.** We now have a concrete target per model — e.g.
   *why* does qwen3 pick the Ukrainian 34.6% of the time while gemini picks them 21.7%? The
   question becomes: which reasoning structures accompany that choice, and does the pattern of
   deliberation differ between the model that sacrifices a group and the model that protects it?

### Caveats
- Pooled rates mix 6 languages and 13 scenarios; scenario/language are controlled in the modelled
  analyses, not in this descriptive table.
- 12 of the 15 models emit no substantial reasoning, so ThinkProbe linkage is limited to the 3 above.
- British/Indonesian/Polish/Turkish have ~3× lower exposure → wider CIs.
- Choices for free-text responses are judge-parsed; this table uses `structured` only.
