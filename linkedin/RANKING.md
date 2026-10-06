# Interest analysis and rerank

Scored 1 to 5 on four axes. **Novel** = absent from White Circle's published analysis.
**Surprise** = would a sharp reader at White Circle be genuinely startled.
**Evidence** = will it survive being probed by someone who owns this dataset.
**Hiring** = how well it demonstrates what their job ad actually asks for.

| # | Post | Novel | Surprise | Evidence | Hiring | Verdict |
|---|---|:-:|:-:|:-:|:-:|---|
| 07 | Gemini picks slot 1, 85% | 5 | 5 | 5 | 4 | **A — lead** |
| 09 | No bias can mean no decision | 5 | 5 | 5 | 5 | **A — lead** |
| 03 | The bias with no thinking behind it | 5 | 5 | 5 | 4 | **A — lead** |
| 08 | Three answers to the same question | 5 | 4 | 5 | 4 | **A** |
| 06 | I was wrong | 3 | 3 | 5 | 5 | **B — keep** |
| 02 | The trace tells you who gets picked | 5 | 3 | 4 | 4 | **B — keep** |
| 01 | When it kills a disabled person | 5 | 4 | 3 | 4 | **B — keep** |
| 10 | A design detail worth knowing | 5 | 4 | 5 | 3 | **B — but time it** |
| 04 | What makes a model refuse | 5 | 3 | 3 | 3 | **C — demote** |
| 05 | When identity beats frequency | 5 | 4 | **2** | 3 | **C — risky** |
| 11 | The experiment that would settle it | 1 | 1 | n/a | 4 | **D — closer only** |

---

## The uncomfortable conclusion

**Your strongest material is not the ThinkProbe material.**

Posts 07, 08, 09 score 5 on both novelty and evidence. They are also the three that need **no trace
analysis at all** — they are facts about position and repeatability, computed from columns White
Circle already published, using their own reshuffle design. Anyone can verify them in an afternoon,
which is exactly why they are safe.

The ThinkProbe posts (01, 02, 05) are the intellectual centre of the project but they are
evidentially softer, and they share two weaknesses:

**1. The co-generation objection.** The reasoning trace and the choice come out of the same forward
pass. A sharp reader says "of course they correlate, one is not causing the other, they are the same
event." This does not kill the finding, but it means "reasoning predicts the choice" is less
startling to an expert than it sounds. Post 02 is most exposed to this.

**2. They are all unadjusted.** Model, scenario and language are not partialled out in the
kill-versus-not-kill tables. The within-line-up ordering rules out composition, but not model mix.
If one gets challenged on this, all three wobble together.

That is a correlated risk. Do not put 01, 02 and 05 in the first three days.

---

## Reranked running order

| Day | Post | Why here |
|---:|---|---|
| 1 | **07 Position bias** | Biggest number, bulletproof, and it implicates their own bias score. Opens with maximum credibility. |
| 2 | **09 No bias can mean no decision** | Deepest insight in the project. Follows naturally from day 1. |
| 3 | **03 Silent bias, phone** | Lands on the finding they themselves called surprising, and deepens it. Most likely to get their attention directly. |
| 4 | **08 Three answers** | Same behavioural thread, keeps momentum, easy to verify. |
| 5 | **06 I was wrong** | Best hiring post. Placed after four solid results so the retraction reads as rigour, not as inexperience. |
| 6 | **01 Disabled person** | Introduces ThinkProbe on your most resonant single finding. |
| 7 | **02 Trace predicts the choice** | The statistically strongest trace result. Now the audience trusts the instrument. |
| 8 | **10 Design detail** | Critique lands only after seven posts of credit. Never earlier. |
| 9 | **04 Refusal drivers** | Solid, less striking, fine mid-series. |
| 10 | **05 Amputee** | Conceptually the best post in the set and the thinnest evidence. Late, clearly flagged. |
| 11 | **11 Next experiment** | Closer. Not a finding, and does not pretend to be. |

Note what moved: ThinkProbe now starts on **day 6**, not day 1. That contradicts the original plan
of leading with ThinkProbe. I think the original plan was wrong. Lead with what cannot be argued
with, then introduce the instrument to an audience that already trusts you.

---

## Post by post

### Tier A

**07 Position bias.** The best post you have. 84.8 percent is a number people repeat. n = 104,377,
verified on the full dataset, reproducible in ten lines of code. And it raises a real question about
their headline metric: a bias score may be mixing prejudice with position-following. High stakes,
zero fragility.

**09 No bias can mean no decision.** The most intellectually valuable finding in the project. Person
repeatability at the 6.25 percent chance floor for nationality and skin colour means those attributes
were never measuring a person-level decision. It reframes part of their analysis rather than
contradicting it, and you already have the right caveat attached. Keep that caveat, it is what makes
the post land as insight rather than attack.

**03 Silent bias.** Strategically the smartest post. It takes the finding they publicly flagged as
their most unexpected and shows there is nothing behind it in the reasoning. A well-powered zero
(n = 1,677 against a 0.16 SD floor) is a much harder thing to argue with than a positive effect.

**08 Three answers.** Striking and safe. Slightly lower surprise than the other three only because
"LLMs are inconsistent" is a known genre. What makes it land is the person-versus-slot contrast:
61.9 percent consistent about position, 19.6 percent about people.

### Tier B

**06 I was wrong.** Scores 3 on novelty and surprise because it is not a finding about the world. It
scores 5 on hiring because their ad asks for "distinguishing genuine signal from artifact" and this
is a worked example with the corrected number attached. Placement matters enormously: day 5, after
real results. On day 1 it reads as someone who makes mistakes.

**02 Trace predicts the choice.** Your most rigorous trace result (two attributes, 32 values,
r around 0.9, length confound ruled out on politics) but the least surprising to an expert because
of the co-generation objection. Consider adding one line pre-empting it: the direction is the
interesting part, not the correlation.

**01 Disabled person.** Most emotionally resonant post in the set and the coarse-versus-granular
reversal is a genuinely good measurement lesson. Marked down on evidence because "disabled" is a
post-hoc grouping of two values and the means are unadjusted.

**10 Design detail.** Rock solid and directly useful to them. Marked down on hiring only because
critique alone does not demonstrate research skill. Timing is everything: day 8, not day 2.

### Tier C, and be honest about why

**04 Refusal drivers.** The self-reflection reversal is nice but the post has no single memorable
number, and the refusal population pools all attributes together. Fine mid-series filler. Would be
the first to cut if you shortened the run.

**05 Amputee.** This is the post I would argue about. Conceptually it is the most important thing in
the project, because it is the only evidence that the pattern tracks **identity** rather than **being
the default**, which is the central open question. But it rests on **109 traces in one cell**, with a
grouping I invented after seeing the data. If someone at White Circle pulls that thread, it is thin.
Keep it, keep the warning in the last paragraph, and place it late so it reads as a lead worth
chasing rather than a claim you are staking.

### Tier D

**11 Next experiment.** Zero novelty and zero surprise by design. It stays because ending a series
by naming the experiment that would falsify your own interpretation is a strong close, and because
their ad explicitly asks for people who can turn a vague question into a falsifiable experiment.

---

## If you cut

**To 7 posts:** 07, 09, 03, 08, 06, 01, 11. Drops the two weakest (04, 05), the softest trace post
(02) and the critique (10).

**To 5 posts:** 07, 09, 03, 06, 11. All bulletproof, plus the retraction and the close.

**To 3 posts:** 07, 09, 03. Nothing here can be argued with, and all three are novel to them.
