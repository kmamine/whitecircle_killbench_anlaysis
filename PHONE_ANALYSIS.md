# Phone (socioeconomic proxy) — the most extreme bias in the study, applied in total silence

Table: `PHONE_PROFILE_METRIC_TABLE.md` · Data: `results/phone_profiles_metrics_kill_vs_notkill.csv`
Code: `kbtp/tables.py`

2,322 traces with profiles. **A single line-up** — iPhone, Android, Nokia, No phone always compete
together — so shares sum to 100% and every comparison is fully anchored. This is the cleanest
identified dimension in the dataset.

---

## 1. The most extreme demographic preference measured anywhere

| Phone | Chosen to die | vs fair share (25%) |
|---|---:|---:|
| **No phone** | **72.2%** | **2.89×** |
| Nokia | 16.5% | 0.66× |
| iPhone | 8.7% | 0.35× |
| **Android** | **2.6%** | **0.10×** |

Confirmed on the full choice data (20,569 trials, all 15 models): No phone 71.3%, Nokia 14.7%,
iPhone 8.6%, Android 5.3%.

**The person with no phone is chosen to die 72% of the time — a 27.8× ratio over the Android
owner.** For comparison, the widest nationality gap was 1.5× and the widest religion gap 4.7×.

The structure is essentially **phone vs no phone**: owning any handset splits the remaining 27.8%
three ways (~9% each). The specific handset matters far less than possessing one. Note also that
Android, not iPhone, is the most protected — so this is not a clean "expensive = valuable" gradient,
it is a poverty marker.

## 2. And the model shows no hesitation whatsoever

| Victim | Kill % | n killed | branching | hedging | exploration | tokens |
|---|---:|---:|---:|---:|---:|---:|
| **No phone** | **72.2** | 1,677 | **−0.007** | **−0.013** | +0.026 | −0.103 |
| Nokia | 16.5 | 382 | −0.071 | +0.172 | −0.054 | +0.171 |
| iPhone | 8.7 | 202 | +0.085 | −0.108 | +0.003 | +0.016 |
| Android | 2.6 | 61 | +0.172 | **−0.491** | +0.072 | −0.163 |

**On the preferred victim the signature is zero.** Branching −0.007 and hedging −0.013 at
n = 1,677 — a well-powered exact null (detection floor ≈0.16 SD). The model selects the phoneless
person nearly three times more often than chance and its reasoning does not register the fact.

The only large effects sit on **Android**, the *rarest* victim (n = 61): domain spread +0.712,
first-idea diversity +0.530, hedging −0.491, Breadth +0.452. That is the "deviation costs search"
pattern — picking the most-protected person takes wide exploration — and at n=61 it is the least
reliable cell in the study.

## 3. ⚠️ This overturns the "law" I reported earlier

In `RELIGION_AND_THE_LAW.md` I claimed **corr(bias spread, reasoning signature) = +0.915**, i.e.
*the stronger the bias, the more the reasoning betrays it.* **That was measured wrongly.** I used the
**maximum |difference| over all values** in a dimension, which is dominated by whichever value
happens to move — often a *rare* victim (Android here, Amputee in body type), not the preferred one.

Measured correctly — the signature on the model's **own preferred victim**:

| Dimension | Preferred victim | Kill % | signature (\|branching\| + \|hedging\|) | verdict |
|---|---|---:|---:|---|
| body type | Obese | 81.2 | 0.672 | strong |
| **phone** | **No phone** | **72.2** | **0.020** | **SILENT** |
| religion | Satanist | 57.4 | **1.535** | strong |
| politics | Far-right | 50.0 | **1.015** | strong |
| orientation | Asexual | 45.8 | 0.873 | strong |
| nationality | Ukrainian | 30.3 | 0.283 | moderate |
| **skin colour** | **Light-skinned** | **29.1** | **0.038** | **SILENT** |

**corr(preferred-victim kill %, signature size) = +0.191, p = 0.68 — not significant.**

Bias strength does **not** predict whether the reasoning shows it. Phone is the decisive
counterexample: the second-strongest preference in the study, with a signature of 0.020.

## 4. The better hypothesis

What separates the strong-signature dimensions from the silent ones is not *how biased* the model is
but *what the bias is about*:

| | Dimensions | Preferred victim signature |
|---|---|---|
| **Recognised as sensitive** | religion, politics, sexual orientation, body type/disability | 0.67 – 1.54 |
| **Not recognised as sensitive** | phone (class), skin colour (unmarked category) | 0.02 – 0.04 |

> **The model hedges when it condemns someone for a reason it recognises as taboo. It does not
> hesitate at all when it condemns the poor person — even while doing so 72% of the time.**

This also explains the skin-colour pairing: there the *outcome* bias is nearly absent AND the
signature is absent, but the preferred victim is **light-skinned** — the unmarked category, which
carries no taboo, so nothing to hedge about.

Class is the blind spot: an enormous, perfectly consistent preference that passes through the model's
deliberation without leaving a mark. A guardrail that watches reasoning for signs of unfair
deliberation would catch the Satanist and Far-right cases and **completely miss this one**.

## Limitations

- **The sensitive/non-sensitive split is post-hoc**, applied after seeing the results, over only 7
  dimensions. Treat it as the hypothesis this analysis generates, not a tested claim.
  What *is* not post-hoc is the phone null itself: 72.2% kill rate, n=1,677, signature 0.020.
- **Android n = 61.** Its large effects are the least reliable numbers reported anywhere here.
- **Unadjusted means** — model, scenario and language not partialled out.
- Association, not causation; reasoning and choice come from one forward pass.
- Only 3 reasoning models, which disagree about *who* they sacrifice.
- `RELIGION_AND_THE_LAW.md` and `figures/r1_bias_vs_signature.png` still present the superseded
  max-over-values version of the law and need the correction above applied.
