


# CLAUDE.md — KillBench × ThinkProbe

## Purpose
Test whether the *structure* of a model's reasoning trace carries a signature of motivated
reasoning that the final decision hides — using **ThinkProbe** (non-generative structural
profiling of reasoning traces via Thought Graphs) on **KillBench** (White Circle's decision-bias
benchmark).

Concrete, falsifiable question: **do ThinkProbe structural features separate KillBench's biased
decisions from fair ones?**

This is a *supervised* test, not exploratory pattern-hunting. Read "Experimental design" and
"What NOT to do" before writing any analysis code.

## Gate — do this FIRST (blocking)
Before any analysis, confirm the dataset actually contains model **reasoning text**, not just a
parsed decision + a judge verdict.
- Dataset: `whitecircle-ai/killbench` on HuggingFace (~1.37M rows, single train split, **gated** —
  accept the license first; EU-region flagged).
- Known: ~91% of rows have response strings of 0–2k chars; the usable subset is the **~9%** with
  longer traces.
- Check: open the dataset viewer or stream a sample, and find the column holding the model's full
  free-text response. If it's decision + verdict only (no multi-sentence reasoning), **STOP** —
  there are no traces to profile, and this run needs a different data source (re-running KillBench
  scenarios to generate traces, which is out of scope for a fast weekend analysis). Report this
  before doing anything else.
- Also confirm the long traces are genuine reasoning (multi-sentence deliberation), not long
  boilerplate/refusal text. ThinkProbe needs structure to graph.

## Data
- **Do not download the full 1.37M rows.** Stream and filter to the long-trace subset (~9%):
  `load_dataset(..., streaming=True)` → filter on response length → materialize only the filtered
  subset locally.
- Needed columns: the response **text** (traces), the **decision**, and KillBench's **bias/fairness
  ground truth** per row (the label being predicted). Confirm which columns encode the bias label
  and how "biased vs fair" is defined — check the dataset card and the builder repo
  (`whitecircle/killbench`); do not assume the schema.
- Their pipeline parses free-text with a Gemini judge via OpenRouter, so a "verdict" column may be
  **judge output**, distinct from the raw model response. Keep the two separate.

## ThinkProbe
- ThinkProbe is the maintainer's own tool (arXiv:2606.29067). Use the **actual implementation/API** —
  consult its repo/README. Do not reimplement or guess the interface.
- **Validate before trusting the numbers:** ThinkProbe was built on open-ended reasoning traces;
  KillBench traces are shorter and argumentative/decisional. Manually inspect a handful of
  constructed graphs on KillBench traces first and confirm they're sensible. If graphs are
  degenerate on this trace type, note it — the metrics would then reflect that, not deliberation.

## Experimental design (the point of this file — keep it honest)
Question: do structural features of the trace separate **biased** from **fair** decisions?
- Supervised analysis/classification with KillBench's labels as ground truth. This is what makes it
  falsifiable rather than a trawl.
- **Controls are mandatory, not optional:**
  - *Length.* Biased vs fair traces likely differ in length, and structural features correlate with
    length. Either length-match the groups or residualize structural features on length, and report
    the effect **beyond** length.
  - *Lexical baseline.* Fit a baseline using only length + simple lexical features (e.g.
    hedging/uncertainty word counts). The ThinkProbe structural signal must **beat** this baseline to
    matter. Report both.
- **Multiple comparisons.** With many structural features you'll find *some* correlation by chance.
  Pre-register the features/hypotheses in the repo, correct for multiple tests (Bonferroni/BH), and
  report effect sizes + confidence intervals, not just p-values.
- Fixed seeds and error bars on everything.

## Reporting standard
- A **null result is a valid, postable result**: "trace structure does not add over length/lexical
  baselines here" is honest and still demonstrates the method and the rigor. Do not manufacture a
  positive finding.
- State limitations explicitly: single benchmark, judge-labeled ground truth, ThinkProbe validity on
  this trace type, subsample only.
- Keep claims proportional to a weekend analysis on a subsample. No "models rationalize bias"
  headline unless the *controlled* effect actually holds.

## Stack & conventions
- Python; HuggingFace `datasets`; MLflow for tracking; clean, reusable modules.
- Reproducible: fixed seeds, saved configs, and one script that regenerates every figure/number.
- Structure as separate modules: data loading/filtering, ThinkProbe feature extraction, controlled
  analysis, figures.

## Deliverable
- A short written report in the repo: result + controls + limitations.
- A LinkedIn post: measured, code visible, tag White Circle. Frame as "I ran my reasoning-trace tool
  on your KillBench data — here's one thing I found." Curiosity, not a takedown; if a finding is
  unflattering to the benchmark, say it as a generous observation.
- Skim the KillBench license before publishing any derived results.

## What NOT to do
- Don't run on the full 1.37M rows — use the ~9% long-trace subset.
- Don't report correlations without the length and lexical controls.
- Don't proceed if the dataset has no real reasoning traces (see Gate).
- Don't anthropomorphize: the trace's structure is a *signal*, not the model's "psychology," and the
  trace may not reflect the actual computation (unfaithful-CoT caveat). Avoid "cognitive profile"
  framing in the writeup.
- Don't overclaim a positive result on a single subsample, and don't let the analysis drift into a
  fishing expedition.



  ### KILLBench dataset link 
  ![https://huggingface.co/datasets/whitecircle/killbench](https://huggingface.co/datasets/whitecircle/killbench
  )

  ### Thinkprob repo 
  ![https://github.com/kmamine/ThinkProb](https://github.com/kmamine/ThinkProb)