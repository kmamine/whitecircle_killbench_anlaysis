# Body type — where the law breaks, and why that matters most

Table: `BODY_TYPE_PROFILE_METRIC_TABLE.md` · Data: `results/body_type_profiles_metrics_kill_vs_notkill.csv`
Figure: `figures/r4_bodytype_disability.png` · Code: `kbtp/tables.py`

4,570 traces with profiles. **Only 2 line-ups, and they share no members** — so cross-line-up
comparisons have no anchor and only within-line-up shares are valid.

---

## 1. Who gets chosen to die

Per line-up (each sums to 100% — the only valid comparison):

| Line-up | Shares |
|---|---|
| Athletic, Muscular, **Obese**, Overweight | **Obese 71.5%** · Overweight 11.1% · Muscular 9.2% · Athletic 8.3% |
| Amputee, Skinny, Slim, **Wheelchair user** | **Wheelchair user 36.9%** · Skinny 29.9% · Slim 26.8% · **Amputee 6.4%** |

**The obese participant is chosen 71.5% of the time — the most extreme demographic preference in the
entire dataset.** Against the three others in its own line-up (8–11% each) that is roughly **7–8×**.

The wheelchair user leads its line-up at 36.9%. The amputee is the *least* chosen at 6.4% — note
that, it becomes the decisive fact below.

## 2. The law does NOT hold here

For religion and politics, the reasoning signature tracked kill rate at r ≈ 0.9. For body type:

| Metric | corr with kill rate | p |
|---|---:|---:|
| branching factor | −0.423 | 0.30 ᶰˢ |
| hedging density | +0.315 | 0.45 ᶰˢ |
| exploration / exploitation | −0.445 | 0.27 ᶰˢ |
| Breadth | −0.493 | 0.21 ᶰˢ |
| avg tokens | −0.288 | 0.49 ᶰˢ |

Nothing. But the effects themselves are the **largest in the study** (max **1.262 SD**, median
0.195 SD). So there is a huge signal that kill rate cannot explain.

## 3. What explains it: disability

![body type disability](figures/r4_bodytype_disability.png)

| Metric | disabled mean (amputee, wheelchair user) | non-disabled mean | gap |
|---|---:|---:|---:|
| branching factor | **−0.662** | +0.292 | 0.95 SD |
| hedging density | **+0.765** | −0.283 | **1.05 SD** |
| exploration / exploitation | **−0.626** | +0.283 | 0.91 SD |
| Breadth | −0.395 | +0.192 | 0.59 SD |
| avg tokens | **+0.728** | −0.076 | 0.80 SD |

**Both disabled participants get narrow, heavily-hedged, longer reasoning when chosen — regardless
of how often they are chosen.**

### The decisive case: the Amputee

| Victim | Kill % | branching | hedging | exploration | tokens | n killed |
|---|---:|---:|---:|---:|---:|---:|
| **Amputee** | **4.6%** | **−0.615** | **+0.801** | **−0.564** | **+1.262** | 109 |
| Wheelchair user | 48.5% | −0.709 | +0.730 | −0.689 | +0.194 | 1,149 |
| Skinny | 25.4% | +0.293 | −0.501 | +0.326 | −0.194 | 601 |
| Slim | 21.5% | +0.881 | −0.728 | +0.801 | −0.397 | 508 |

The amputee is the **rarest** victim in the line-up yet carries **the same signature as the most
common one**. Remove the amputee and line-up 2 is near-perfectly monotonic (branching r = **−0.971**);
include it and the correlation collapses to −0.172. It is the single point that breaks the law.

**Rarity-matched check** — all four of these are chosen 4.6–6.9% of the time, so "rare choices are
just unusual traces" cannot explain the difference:

| Victim | Kill % | | branching | hedging | tokens |
|---|---:|---|---:|---:|---:|
| **Amputee** | 4.6% | **disabled** | **−0.615** | **+0.801** | **+1.262** |
| Overweight | 5.3% | | +0.293 | −0.085 | +0.152 |
| Muscular | 6.6% | | +0.451 | −0.559 | −0.255 |
| Athletic | 6.9% | | +0.197 | −0.135 | +0.320 |

Among equally-rare victims, only the disabled one shows the hedged/narrow pattern — and it points
the opposite way from all three others.

Not small-n noise: at n=109 the SE is ≈0.096 SD, so avg_tokens is **13×** SE, hedging **8×**,
branching **6×**.

## 4. Why this is the most important result in the study

It **partially de-confounds the question I said needed an intervention.**

The open problem was that "the model's stigmatised target" and "the model's *modal* choice" are the
same thing for religion and politics, so the hedged/narrow signature could mean either *motivated
reasoning about a disfavoured group* or merely *this is the default, no search required*.

The amputee separates them. It is **not** the modal choice — it is the rarest — yet it produces the
full hedged/narrow signature. So the signature can be driven by **who the person is**, not only by
**how often they are picked**.

Revised picture — two independent drivers:

| Driver | Evidence |
|---|---|
| **Being the model's default victim** | religion r≈0.93, politics r≈0.92, Obese, Wheelchair user |
| **Being disabled** | Amputee (rarest victim, full signature); disabled−non-disabled gap ≈1.0 SD; survives rarity matching |

And it fits the earlier line-up-level result: the disability line-up drew **+0.26 SD** more thought
units than the body-size line-up — the largest such gap in the data. Disability makes this model
reason differently whether or not it ends up choosing the disabled person.

## Limitations

- **2 line-ups sharing no members.** "Obese 81.2%" vs "Wheelchair user 48.5%" in the pooled table is
  **not** a valid comparison; only the within-line-up shares are. The pooled table is retained for
  completeness but should not be quoted across line-ups.
- **n=109 for the amputee.** Effects are 6–13× SE and directionally match the wheelchair user, but
  this rests on one small cell and deserves replication.
- **Unadjusted means** — model, scenario and language not partialled out. The rarity-matched
  comparison controls the main alternative explanation but not model mix.
- **"Disabled" is my own grouping** of amputee + wheelchair user, applied after seeing the data. It
  is a 2-value category, so this is a hypothesis generated here, not a pre-registered test. The clean
  confirmation is a fresh line-up with more disability values.
- Association, not causation; reasoning and choice are one forward pass.
