# Kill / no-kill by continent, cultural region, and economic standing

170,779 nationality dilemmas · 13 civilian scenarios · 15 models.
Data: `results/killrate_blocs.parquet` · Code: `kbtp/blocs.py`, `kbtp/taxonomy.py`
Figures: `b_continent.png`, `b_region.png`, `b_economic.png`, `b_north_south.png`
(+ `_by_model` versions). All bloc figures share one x-scale so bar lengths are comparable
between groupings.

## How the "fair share" is computed (this is not a sum of the per-nationality rates)

A single nationality appears at most once per dilemma, so its fair share is exactly 25%.
A **bloc can appear several times** — verified: up to **2 Europeans** and up to **3 Asians**
are shown in the same 4-person dilemma. If 3 of the 4 people on offer are Asian, then under no
bias an Asian is chosen **75%** of the time. Comparing a bloc's raw rate to 25% would brand every
large bloc "biased" purely because of how often its members are on the table.

So the null is computed per trial: with `n_B` of the 4 displayed belonging to bloc B,
P(chosen ∈ B) = `n_B/4`. Summed over trials this gives the **expected** number of kills; the
effect size is the **relative risk** = observed / expected, reported as **% above/below fair share**.

---

## 1. By continent (all 15 models)

| Continent | Nations | Exposures | Killed | Expected | **vs fair share** | z |
|---|---:|---:|---:|---:|---:|---:|
| Oceania (Australia) | 1 | 38,425 | 11,493 | 9,606 | **+19.6%** | 22.2 |
| Europe | 6 | 188,629 | 52,667 | 47,157 | **+11.7%** | 30.3 |
| South America | 1 | 38,351 | 9,541 | 9,588 | −0.5% ᶰˢ | −0.6 |
| North America | 2 | 76,466 | 18,129 | 19,117 | −5.2% | −8.2 |
| Asia | 8 | 264,793 | 61,746 | 66,198 | −6.7% | −24.4 |
| Africa | 2 | 76,452 | 17,203 | 19,113 | **−10.0%** | −16.0 |

## 2. By cultural region (all 15 models)

| Region | Nations | **vs fair share** | z |
|---|---:|---:|---:|
| Catholic Europe (FR, PL) | 2 | **+15.4%** | 21.1 |
| Orthodox / Eurasian (RU, UA) | 2 | **+14.9%** | 23.8 |
| Anglosphere (US, UK, AU) | 3 | +7.7% | 14.6 |
| Muslim Southeast Asia (ID) | 1 | +6.2% | 4.8 |
| Protestant Europe (DE) | 1 | +5.2% | 5.9 |
| Middle East & North Africa (EG, IR, TR) | 3 | +1.4% | 2.5 |
| Latin America (BR, MX) | 2 | −5.0% | −8.0 |
| Confucian East Asia (CN, JP, KR) | 3 | −10.3% | −21.3 |
| South Asia (IN) | 1 | −12.0% | −13.5 |
| Sub-Saharan Africa (NG) | 1 | −13.6% | −15.3 |
| **Israel** | 1 | **−16.6%** | −18.7 |

Spread **32 pp** — the widest of any grouping. Europe's three zones occupy three of the top five
slots; the three most-protected zones are Sub-Saharan Africa, South Asia and Israel.

## 3. By economic standing (all 15 models)

| Tier | Nations | **vs fair share** | z |
|---|---:|---:|---:|
| Upper-middle income | 6 | +3.2% | 8.4 |
| High income | 9 | +1.0% | 3.9 |
| Lower-middle income | 5 | −4.7% | −13.4 |

| Global North / South | Nations | vs fair share | z |
|---|---:|---:|---:|
| Global North | 9 | +1.0% | 3.9 |
| Global South | 11 | −0.8% | −3.9 |

**Effect sizes are 4–6× smaller than continent or region** (±5% vs ±20%, ±33%). Everything is
"significant" at this N, so read the effect size, not the p-value. Pooled, wealth is a weak
predictor of who an AI picks to die — and pointing the "wrong" way.

---

## The correction: the economic effect is real, but only *per model* — and it inverts

**This overturns the pooled reading.** The small pooled economic effect is a **cancellation of two
strong, opposite biases**:

| Bloc | qwen3-235b | kimi-k2.5 | gemini-3.1-pro |
|---|---:|---:|---:|
| **Lower-middle income** | **+13.3%** (z=10.1) | −4.7% (z=−3.2) | **−8.5%** (z=−6.5) |
| Upper-middle income | −0.8% ᶰˢ | +5.2% | +4.4% |
| **High income** | **−7.8%** (z=−8.5) | −0.3% ᶰˢ | **+2.5%** (z=2.8) |
| Global South | **+6.3%** (z=8.5) | +0.2% ᶰˢ | −2.0% (z=−2.8) |

- **qwen3-235b behaves exactly as the intuitive hypothesis predicts**: participants from
  lower-middle-income countries are **13.3% more likely** to be chosen to die, and high-income
  participants **7.8% less** likely. A clean "poorer lives count for less" gradient, z=10.
- **gemini-3.1-pro does the opposite**: it *protects* lower-income participants (−8.5%) and
  sacrifices high-income ones slightly more (+2.5%).
- kimi sits between, closer to gemini.

Averaging them yields ≈0 and the false conclusion that models are indifferent to wealth. They are
not — **they disagree about which direction to be biased in.**

### The same reversal on Africa and South America

| Bloc | qwen3-235b | kimi-k2.5 | gemini-3.1-pro |
|---|---:|---:|---:|
| **Africa** | **+8.1%** (z=3.5) | −11.0% (z=−4.2) | −10.2% (z=−4.4) |
| **South America** | **−17.0%** (z=−5.2) | +2.1% ᶰˢ | +1.9% ᶰˢ |
| North America | −12.9% (z=−5.5) | −4.1% ᶰˢ | −3.3% ᶰˢ |

A **19-point swing** on Africa: qwen3 sacrifices Africans above their fair share while both other
models protect them.

### What all three models agree on

| Bloc | qwen3 | kimi | gemini | verdict |
|---|---:|---:|---:|---|
| **Oceania (Australia)** | +9.7% | +13.3% | +13.4% | sacrificed more by all three |
| **Europe** | +7.7% | +5.1% | +9.6% | sacrificed more by all three |
| Asia | −3.0% | −1.6% ᶰˢ | −5.2% | protected by all three |

**Europeans and Australians are chosen to die above their fair share by every model tested.** That
is the one robust, direction-consistent geographic finding.

---

## Reading this honestly

- **Report effect sizes, not p-values.** With 170k trials, a 1% deviation reaches z=3.9. Only
  differences of roughly ±5% or more are worth discussing.
- **Never pool across models on this data.** Two of the three headline patterns (economic, Africa)
  are sign-reversed between models, so the pooled number is an artifact of averaging.
- **Blocs are not independent tests.** Continent, region and economic tier are three views of the
  same 20 nationalities, and they overlap (Europe ≈ Catholic + Orthodox + Protestant Europe +
  part of the Anglosphere). Treat them as three lenses on one dataset, not as three findings.
- **Single-nation blocs are just that nation**: Oceania = Australia, Israel = Israel,
  South Asia = India, Sub-Saharan Africa = Nigeria, Muslim SE Asia = Indonesia. The bloc label
  makes them sound broader than they are.
- **Economic tiers are annually reassigned**; Russia, Iran, Ukraine and Poland sit near
  thresholds (`taxonomy.ECONOMIC_BORDERLINE`), and Ukraine's wartime GNI makes its tier unstable.
- 12 of the 15 models emit no substantial reasoning, so ThinkProbe linkage covers only the three
  models broken out above.
