# LinkedIn series — 11 posts, one per day. NEW findings only.

**Filter applied:** every claim White Circle already published is cut. Gone: Satanist/Scientologist/
atheist most targeted · Jewish most protected · no-phone targeted regardless of brand · Obese
targeted / Android & Amputee protected · French & Russian targeted more · every model biased ·
models disagree · refusal rates per model · structured-output-as-jailbreak · "models claim
randomness but aren't" · newer models refuse less.

**What's left is only what their analysis could not have produced** — because it either requires the
reasoning traces (which they collect but don't analyse), or requires looking at position and
repeatability (which their design randomises away as nuisance).

**Arc:** 1–6 ThinkProbe (reasoning traces). 7–9 behaviour. 10 method. 11 next.

**Before posting:** all percentages are from KillBench's `structured` mode — the condition White
Circle themselves show amplifies bias. Say it once (post 1). Skim
`white-circle-responsible-use-license-v1.0`. Tag @White Circle, link the repo, credit them for
shipping raw traces — almost nobody does.

---

## Day 1 — The coarse score said "no difference." It was hiding two opposite effects.
**Visual:** `figures/L1_disability_coarse_vs_granular.png`

White Circle's KillBench ships 1.37M life-or-death decisions — and a `reasoning_text` column with
the model's full chain of thought that the analysis never opens.

I ran a thought-graph profiler over 83,218 of those traces. It turns a trace into a directed graph
of thought units and measures 22 structural metrics in 5 families. No LLM judge: regex cue phrases,
sentence embeddings, an NLI cross-encoder. It can't flatter the model it's analysing.

First test: one line-up offers an amputee, a wheelchair user, a skinny person and a slim person. I
compared traces where the model chose a **disabled** person to die against traces where it chose a
non-disabled one. Same dilemma, same scenario, same model.

The coarse "Metacognitive" family score: **+0.06 SD. Nothing.**

Inside that family:
→ **hedging +0.77 SD** (non-disabled: −0.28)
→ **perspective-taking −0.57 SD** (non-disabled: +0.24)
→ branching factor **−0.66** — far fewer alternatives opened
→ **+0.73 SD more words**

The family score is flat because hedging and perspective-taking move hard in opposite directions
and cancel out.

When this model condemns a disabled person it **agonises more and considers less.**

And a measurement lesson I nearly learned the hard way: if I'd reported only the 5 coarse families,
I'd have published "no effect."

(All figures use KillBench's structured-output mode — the condition White Circle show amplifies bias
vs free-text.)

---

## Day 2 — In the same dilemma, the reasoning tells you who's about to be chosen
**Visual:** `figures/r2_religion_monotonic.png` + `figures/r3_politics_monotonic.png`

Take one KillBench line-up: four people, one scenario, one model. The only thing that varies is who
gets picked.

The trace looks completely different depending on who that is.

**Choosing the Satanist:** 0.81 SD *fewer* alternatives explored, 0.72 SD *more* hedging
**Choosing the Hindu:** 0.73 SD *more* alternatives, 0.65 SD *less* hedging

A ~1.5 SD swing between two victims in the same 4-way choice.

It isn't two clusters — it's a gradient. Across 16 religions, reasoning style tracks how often each
group gets chosen:
→ exploration/exploitation **r = −0.945** · branching **r = −0.932** · perspective-taking **r =
−0.923** · hedging **r = +0.906** (all p < 1e-4, and it holds inside each of the 4 line-ups
separately)

Then I ran it again on political views — 16 different values, 19,542 traces:
→ Breadth **r = −0.950** · exploration **r = −0.938** · branching **r = −0.916** · hedging **r =
+0.908**

And one difference that matters more than the replication: **trace length is not significant for
politics** (r = +0.43, p = 0.09) where it was +0.85 for religion. That rules out the boring
explanation. This isn't "writes more when uncomfortable" — the graph-structure metrics carry it
alone.

Plainly: the model **hedges its way** to its default victim without exploring options, and has to
**genuinely deliberate** to reach an unusual one.

---

## Day 3 — Your most surprising bias is the one with no deliberation behind it
**Visual:** `figures/L3_silent_bias.png`

White Circle flagged phone ownership as their most unexpected result — people with no phone get
targeted far more, regardless of brand. It's the strongest preference in the benchmark.

I went looking for the deliberation behind it.

There isn't any.

branching factor **−0.007**. hedging **−0.013**. n = 1,677, against a 0.16 SD detection floor. A
well-powered exact zero.

For comparison, the same measurement on other attributes' preferred victims: Satanist **1.54**,
far-right **1.02**, asexual **0.87**, obese **0.67**.

So the model reliably identifies the poorest person in the line-up, selects them nearly three times
more often than chance, does it consistently across reshuffles — and its reasoning never registers
that anything happened.

Religion makes it hesitate. Politics makes it hesitate. Class doesn't.

That's a problem for a specific and increasingly popular idea: catching unfair AI decisions by
monitoring the reasoning trace. That approach flags the Satanist case and sails straight past this
one — the bigger of the two.

---

## Day 4 — Which kind of thinking makes a model refuse to kill anyone?
**Visual:** `figures/L5_refusal_drivers.png`

"Make the model think harder" gets treated as a safety intervention. The traces let you test it
directly.

13,351 traces where the model refused the dilemma outright, against traces where it named a victim.
Base refusal rate 16%. Effect per +1 SD of each reasoning family, trace length controlled:

→ **Structure +7.55 pp** — interconnected, revised, backtracking reasoning drives refusal (16% → 24%)
→ **Metacognitive −4.81 pp**
→ **Breadth −3.94 pp**
→ **Depth −2.90 pp**

Only *structural* reasoning makes a model decline. Breadth, depth and self-reflection all push it
**toward** naming someone.

The self-reflection result is the one I keep turning over: the model that talks about its own
reasoning process is **more** willing to pick a person to die, not less.

Reasoning budget isn't a dial you turn up for safety. Which *kind* of reasoning you get determines
the sign.

(I first ran this without controlling trace length and got the opposite signs for Breadth and Depth
— longer traces both refuse more and score higher on everything. The controlled version is above.)

---

## Day 5 — One case where the reasoning tracks *who you are*, not *how often you're picked*
**Visual:** `figures/r4_bodytype_disability.png`

A confound shadowed this whole project. A model's *stigmatised* target and its *most frequent*
target are the same person. So is the hedged, narrow reasoning about **who they are** — or just
about it being the default answer that needs no search?

The amputee separates them.

The amputee is the **rarest** victim in its line-up — chosen 4.6% of the time. Yet the trace looks
like the *most*-chosen one:

| | chosen | branching | hedging |
|---|---|---|---|
| wheelchair user | 48.5% | −0.709 | +0.730 |
| **amputee** | **4.6%** | **−0.615** | **+0.801** |
| skinny | 25.4% | +0.293 | −0.501 |
| slim | 21.5% | +0.881 | −0.728 |

Rarity-matched control: among four victims all chosen 4.6–6.9% of the time, only the disabled one
shows this pattern — and it points opposite to the other three.

Remove the amputee and the line-up is near-perfectly ordered by selection rate (r = −0.971).
Include it and the ordering collapses.

So the signature can be driven by **identity**, not only by frequency. Two mechanisms, and one
accidental natural experiment inside the benchmark that pulls them apart.

n = 109 on that cell. Effects are 6–13× the standard error, but it's one small cell and I'd want it
replicated before anyone leans on it.

---

## Day 6 — I had a clean law at r = 0.915. Measured properly it was r = 0.191.
**Visual:** `figures/r1_bias_vs_signature.png`

Across 7 attributes, the size of the reasoning signature tracked how biased the model was:
**r = +0.915, p = 0.004.** "The stronger the bias, the more the reasoning betrays it." I wrote it up
as a law.

It was wrong.

I'd measured the signature as the **maximum effect over all values** in an attribute. That maximum
is usually driven by a *rare* victim, not the model's preferred one. For phone it came from the
Android owner — chosen 2.6% of the time, n = 61. For body type, the amputee.

Measured on the model's own **preferred** victim: **r = +0.191, p = 0.68.** Nothing.

The counterexample that killed it is the phone result from Day 3: second-strongest bias in the
benchmark, signature 0.020.

What replaced it is more interesting than what I lost. The signature doesn't track bias *strength* —
it tracks whether the attribute is one the model appears to treat as **sensitive**:

→ religion, politics, orientation, disability: **0.67 – 1.54**
→ class, skin colour: **0.02 – 0.04**

Posting the retraction because the retraction *is* the finding. A summary statistic that quietly
answers a different question than the one you asked is the most common way to fool yourself in this
work — and "max over values" looked completely innocent.

---

## Day 7 — Everyone measured *who* gets chosen. Nobody measured *where*.
**Visual:** `figures/L2_position_bias.png`

KillBench presents four people as a numbered list. Position is randomised, so it averages out of the
bias estimates — standard, correct design.

I looked at the position itself. n = 104,377 choices.

→ **Gemini 3.1 Pro picks slot 1 — 84.8% of the time**
→ Kimi K2.5 is bimodal: 59.8% first, 33.0% last, almost never the middle (2.8% / 4.4%)
→ Qwen3-235B favours last: 40.2%, and avoids slot 2 (10.0%)

Uniform would be 25% each.

These are serial-position effects — primacy and recency — and they are **larger than any demographic
effect in the benchmark.**

One consequence worth sitting with. A model that answers largely by position has its demographic
preference *diluted* by that noise. So a single bias score per model may be mixing two different
quantities: how prejudiced a model is, and how position-bound it is. Two models with identical
prejudice would score differently.

If you deploy an LLM that picks from a list — triage, routing, moderation queues, targeting — test
position invariance before anything else. Reshuffle and re-ask. It costs one extra call.

---

## Day 8 — Same dilemma, asked three times, three different answers
**Visual:** `figures/b1_person_vs_slot.png`

KillBench runs every matchup **three times** with the display order reshuffled. That's used to
average out position. I used it for something else: does the model give the same answer twice?

13,120 matchups, identical four people each time. Chance agreement = 6.25%.

**Same person all three times:**
→ Qwen3-235B **29.6%** · Kimi K2.5 **20.0%** · Gemini 3.1 Pro **19.6%**

The most consistent model reproduces its own life-or-death decision **under a third of the time.**

Now the same table for **position**:
→ Gemini **61.9%** · Kimi **50.5%** · Qwen3 **19.7%**

Gemini and Kimi are ~3× more consistent about *where* than about *who*.

Aggregate bias and individual reproducibility are different properties. A benchmark can report a
rock-solid 30%-vs-20% tilt while every individual decision is close to a coin flip. Both belong on
the page — especially for a benchmark motivated by autonomous weapons.

---

## Day 9 — When "no bias" turns out to mean "no decision"
**Visual:** `figures/b1_person_vs_slot.png` (right panel)

This one reframed my entire project.

Split that reproducibility test by attribute. Chance = 6.25%.

| attribute | same person | same slot |
|---|---|---|
| body type | **51.9%** | 13.2% |
| phone | **47.2%** | 14.7% |
| religion | 18.6% | 49.5% |
| politics | 16.8% | 40.6% |
| **nationality** | **7.5%** | **64.5%** |
| **skin colour** | **7.1%** | **67.2%** |

For nationality and skin colour, person-repeatability sits **at the chance floor.** On those
attributes the models aren't choosing a person — they're choosing a slot.

I had spent days treating my weak nationality results as a null about *bias*. They weren't. They
were a null about *decision-making*. There was no person-level decision there to be biased.

And the two attributes with the largest biases in the whole benchmark — body type and phone — are
exactly the two the models actually attend to (52% and 47% person-repeatability, 7–8× chance).

A caveat I want kept attached: a stable aggregate tilt can absolutely sit on top of near-random
individual choices, so this doesn't overturn any published per-attribute finding. It characterises
the process that produces them.

---

## Day 10 — A design detail that changes how much one number can carry
**Visual:** `figures/L4_lineup_confound.png`

Offered in the spirit of making a good benchmark better.

The four people in each KillBench dilemma aren't drawn at random. Each attribute reuses a small set
of fixed line-ups — 9 for 20 nationalities, 4 for 16 religions, 1 for phone.

**Some comparisons therefore don't exist.** "An Israeli is in the line-up" correlates **r = 1.00**
with "a French person is in the line-up" — they always appear together. No analysis on this data can
separate an Israeli-specific effect from a French one. Same for Indian ≡ Russian, Korean ≡
Ukrainian. And "Jewish vs Anglican" never occurs.

**And a pooled per-value rate depends on the assigned opponents.** Liberal is chosen **8.0%** of the
time when it faces the far-right — and **19.4%** when it faces Green/Republican/Socialist. Same
identity, 2.4× apart. Whether "Liberal" reads as the most protected political identity or an
unremarkable one is decided by a line-up assignment, not by the model.

Two smaller things while I'm here: the 25% fairness baseline is exact per value but breaks the
moment you aggregate (up to 3 of the 4 can be Asian, so chance selects an Asian 75% of the time
there) — and the `orientation` attribute contains gender-identity values that duplicate the
`gender_identity` attribute under different naming.

None of this touches the headline conclusion. Every model is biased, and that's solid. It changes
how much weight a single per-value number can carry.

---

## Day 11 — The experiment that would settle it
**Visual:** `figures/L3_silent_bias.png`

Two weeks of results, and the honest summary is: a strong correlation and no mechanism.

When a model condemns its default victim, the reasoning goes narrow and hedged. Two explanations
fit the data equally well.

**Motivated reasoning** — it's rationalising a conclusion it already holds.
**Deviation costs search** — landing anywhere else simply takes more work.

Observation can't separate them, because the model's preference is exactly what makes a choice
common. The amputee (Day 5) is suggestive, but it's one cell of 109.

So stop observing and intervene: **force the choice.** Constrain the model to a *specified* victim,
hold the scenario fixed, and see whether the hedged/narrow signature follows the **identity** or
follows **being the default**.

If identity — that's motivated reasoning, and the trace is a usable monitoring signal.
If default — the signature is a search artefact, and monitoring reasoning for fairness is a dead end.

Either answer is worth having, and it's about a day's work on the pipeline I've already built.

Thanks to @White Circle for shipping the raw traces and not just the aggregates. Almost nobody does,
and none of this existed without it.

---

## Sequencing notes

- **If you cut to 7:** Days 1, 3, 6, 7, 8, 9, 11. That keeps the disability finding, the silent-bias
  finding, the retraction, and all three behavioural results.
- **Day 7 and Day 9 are the most surprising to them** — they own this dataset and neither number
  exists anywhere in their write-up.
- **Day 6 is the highest-signal post for hiring.** Their ad asks for "distinguishing genuine signal
  from artifact" and "calibrating judges and baselines." A published self-refutation with the
  corrected number demonstrates it better than any positive result.
- **Day 3 is the most quotable** — it lands directly on the finding they themselves called
  surprising, and deepens it rather than contradicting it.
- Day 10 lands better after 1–9 have earned credibility. Don't open with the critique.
- Every post carries a repo link. One command regenerates every number and figure — that
  reproducibility claim is doing real work with this audience.
