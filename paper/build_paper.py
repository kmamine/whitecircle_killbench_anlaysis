"""Build the full analysis paper as a PDF (vector text, extractable)."""
import textwrap, pathlib
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, matplotlib.image as mpimg
from matplotlib.backends.backend_pdf import PdfPages

FIG = pathlib.Path("figures")
OUT = pathlib.Path("KillBench_ThinkProbe_Full_Analysis.pdf")
A4 = (8.27, 11.69)
L, R, TOP, BOT = 0.085, 0.915, 0.945, 0.058
INK, INK2, ACC, RED = "#111111", "#555555", "#1a4f8a", "#a03020"

class Doc:
    def __init__(self, pdf):
        self.pdf = pdf; self.page = 0; self.fig = None; self.y = 0
        self._new()
    def _new(self):
        if self.fig is not None:
            self.fig.text(0.5, 0.028, str(self.page), fontsize=8, color=INK2, ha="center")
            self.pdf.savefig(self.fig); plt.close(self.fig)
        self.page += 1
        self.fig = plt.figure(figsize=A4); self.fig.patch.set_facecolor("white")
        if self.page > 1:
            self.fig.text(L, 0.972, "KillBench x ThinkProbe: full analysis",
                          fontsize=7.5, color="#999999")
        self.y = TOP
    def need(self, h):
        if self.y - h < BOT: self._new()
    def gap(self, h=0.012): self.y -= h
    def h1(self, t):
        self.need(0.075); self.gap(0.016)
        self.fig.text(L, self.y, t, fontsize=14.5, color=INK, weight="bold", va="top")
        self.y -= 0.030
        self.fig.add_artist(plt.Line2D([L, R], [self.y+0.004, self.y+0.004], color="#cccccc", lw=1))
        self.y -= 0.014
    def h2(self, t):
        self.need(0.055); self.gap(0.012)
        self.fig.text(L, self.y, t, fontsize=11, color=ACC, weight="bold", va="top")
        self.y -= 0.024
    def para(self, t, size=9.5, color=INK, width=104):
        for para in t.strip().split("\n\n"):
            lines = textwrap.wrap(" ".join(para.split()), width)
            self.need(len(lines)*0.0155 + 0.008)
            for ln in lines:
                if self.y - 0.0155 < BOT: self._new()
                self.fig.text(L, self.y, ln, fontsize=size, color=color, va="top")
                self.y -= 0.0155
            self.y -= 0.009
    def mono(self, lines, size=7.8, color=INK):
        self.need(min(len(lines), 8)*0.0132 + 0.006)
        for ln in lines:
            if self.y - 0.0132 < BOT: self._new()
            self.fig.text(L, self.y, ln, fontsize=size, color=color,
                          family="DejaVu Sans Mono", va="top")
            self.y -= 0.0132
        self.y -= 0.010
    def caption(self, t):
        for ln in textwrap.wrap(" ".join(t.split()), 112):
            if self.y - 0.0135 < BOT: self._new()
            self.fig.text(L, self.y, ln, fontsize=8.2, color=INK2, va="top", style="italic")
            self.y -= 0.0135
        self.y -= 0.010
    def figure(self, name, cap, maxh=0.30):
        p = FIG / name
        if not p.exists(): return
        im = mpimg.imread(str(p)); h, w = im.shape[:2]
        aw = R - L; ah = aw * (h/w) * (A4[0]/A4[1])
        if ah > maxh:
            ah = maxh; aw = ah * (w/h) * (A4[1]/A4[0])
        need = ah + 0.045
        if self.y - need < BOT: self._new()
        ax = self.fig.add_axes([L + (R-L-aw)/2, self.y - ah, aw, ah])
        ax.imshow(im); ax.axis("off")
        self.y -= ah + 0.010
        self.caption(cap)
    def close(self):
        self.fig.text(0.5, 0.028, str(self.page), fontsize=8, color=INK2, ha="center")
        self.pdf.savefig(self.fig); plt.close(self.fig)

# ============================================================ CONTENT
with PdfPages(OUT) as pdf:
    D = Doc(pdf)
    F = D.fig
    # ---------- title
    F.text(L, 0.86, "Reading the reasoning, not just the verdict", fontsize=22, color=INK, weight="bold")
    F.text(L, 0.822, "A thought-graph analysis of KillBench, and what it reveals that", fontsize=13.5, color=ACC)
    F.text(L, 0.798, "the choice-level analysis could not", fontsize=13.5, color=ACC)
    F.add_artist(plt.Line2D([L, R], [0.780, 0.780], color="#cccccc", lw=1))
    D.y = 0.755
    D.para("""ABSTRACT. White Circle's KillBench presents 15 frontier models with 1.37 million forced
    life-or-death choices between four otherwise identical people, and shows that every model tested
    deviates from the 25 percent fair-share baseline. The dataset also ships each model's full chain of
    thought, which the published analysis does not use. We apply ThinkProbe, a non-generative
    thought-graph profiler, to 83,218 of those traces (69,867 decisions and 13,351 refusals), and we
    exploit two further properties of the released data that the original analysis treats as nuisance:
    the display position of each participant, and the fact that every matchup is run three times with
    the order reshuffled.""")
    D.para("""We replicate the published demographic rankings. Beyond them we report four results.
    (i) Serial-position effects dominate the decision process: Gemini 3.1 Pro selects the
    first-listed person in 84.8 percent of 104,377 choices, an effect larger than any demographic
    effect in the benchmark. (ii) Decisions are barely reproducible: on identical dilemmas the most
    consistent model repeats its choice 29.6 percent of the time, and for nationality and skin colour
    person-level repeatability sits at the 6.25 percent chance floor, indicating that no person-level
    decision is being made on those attributes. (iii) Reasoning structure covaries strongly with which
    person is chosen for religion (r = -0.93) and politics (r = -0.92), replicating across 32 distinct
    values and not explained by trace length. (iv) The single strongest bias in the benchmark, against
    people with no phone, carries no reasoning signature at all, while religion, politics and
    disability carry large ones.""")
    D.para("""We also document a design property with consequences for the published per-value
    rankings: participants are drawn from a small number of fixed line-ups rather than at random, so
    some attribute values are statistically inseparable and pooled per-value rates depend on assigned
    opponents. Finally we retract one of our own headline results after re-measurement.""",)
    D.gap(0.010)
    D.mono(["Code and data: kbtp/ package, one command reproduces every number and figure.",
            "All results use KillBench structured-output mode.",
            "Source benchmark: White Circle, KillBench, April 2026."], size=8, color=INK2)

    # ---------- 1 METHOD
    D.h1("1. Method")
    D.h2("1.1 ThinkProbe")
    D.para("""ThinkProbe converts a free-text reasoning trace into a directed thought graph and
    computes a fixed profile from it. The pipeline is deliberately non-generative: no language model
    is used to interpret the trace, which avoids the circularity of analysing one model's output with
    another model's judgement. It has five passes. Structural and cue-phrase segmentation splits the
    trace into thought units and assigns a boundary class from a compiled lexicon. A TextTiling pass
    using all-MiniLM-L6-v2 sentence embeddings inserts soft boundaries at local similarity minima. A
    semantic-trajectory pass assigns branching and elaboration edges. A cross-segment pass adds
    synthesis and backtracking edges. Finally an NLI pass with cross-encoder/nli-deberta-v3-large
    promotes edges to support, contrast and elaboration types above a confidence threshold.""")
    D.para("""Nodes are then typed by a deterministic rule set (12 node types in 4 families) and the
    graph is reduced to a 22-dimensional profile. The 22 metrics group into five families plus a
    two-element size summary that we use as a length control rather than as structure.""")
    D.mono([
      "FAMILY          METRICS",
      "Breadth         branching_factor, unique_perspective_count, domain_spread,",
      "                first_idea_diversity",
      "Depth           max_elaboration_chain, mean_branch_depth, specificity_gradient,",
      "                reasoning_density",
      "Structure       exploration_exploitation_ratio, backtracking_rate,",
      "                cross_branch_connectivity, convergence_index, graph_density,",
      "                revision_depth",
      "Metacognitive   self_reflection_rate, critique_to_hypothesis_ratio,",
      "                hedging_density, perspective_taking",
      "Efficiency      token_per_idea, redundancy_ratio",
      "Size (control)  avg_tokens, avg_tus",
    ])
    D.caption("Table 1. The 22 ThinkProbe metrics and their five families. A family score is the mean of its z-scored metrics, so every score is in standard-deviation units.")
    D.h2("1.2 Extraction")
    D.para("""Extraction ran on a single NVIDIA H100 at 0.27 s per trace, four worker processes,
    approximately 1.5 hours for the full population, with per-trace resumability keyed on row_id.
    All 83,218 traces extracted without error. One implementation note that matters for anyone
    reusing the pipeline: segment() returns thought units without node types, and classify_nodes()
    must be called before graph assembly. Omitting it leaves roughly half the 22 metrics degenerate.""")

    # ---------- 2 DATA
    D.h1("2. Data")
    D.para("""KillBench (whitecircle/killbench, 1,368,936 rows, 11 parquet shards) presents 20
    scenarios in which a model must select exactly one of four participants for a harmful outcome.
    The four differ only on one tested attribute; age and role are held constant within a trial. We
    verified the framing across all 13 civilian scenarios: the chosen participant is always the one
    who dies. Military scenarios (7 of 20) select a building rather than a person and are excluded
    from person-level analysis.""")
    D.h2("2.1 Filter cascade")
    D.mono([
      "POPULATION                                                          ROWS",
      "all rows                                                       1,368,936",
      "reasoning_text >= 2000 chars                                     180,808",
      "  of which structured                                            105,234",
      "  structured and non-refusal                                      88,035",
      "  + single-dimension + parsed choice  (LABELABLE, primary)         69,867",
      "long refusals (secondary population)                              13,351",
      "structured choice population for rate estimation                 552,973",
    ])
    D.caption("Table 2. Filter cascade. Structured mode only: free-text responses lose roughly two thirds of parseable choices to the judge parser.")
    D.h2("2.2 Only three models reason")
    D.para("""Substantial reasoning text exists for three models only: qwen3-235b-a22b (33,299
    labelable traces), moonshotai/kimi-k2.5 (20,189) and google/gemini-3.1-pro-preview (16,170).
    x-ai/grok-4.1-fast contributes 209 and the remaining eleven models approximately zero. Any
    trace-based extension of this benchmark is therefore a three-model study. Reasoning is also
    English-dominated regardless of prompt language: models emit English section headers and English
    meta-reasoning under Chinese, Arabic and Russian prompts.""")
    D.h2("2.3 Line-ups are fixed, not randomised")
    D.para("""The four participants are not drawn at random. Each attribute reuses a small set of
    fixed 4-person sets. This is the single most consequential property of the dataset for anyone
    analysing it, and it is not stated in the published write-up.""")
    D.mono([
      "ATTRIBUTE        VALUES   DISTINCT LINE-UPS",
      "nationality          20                   9",
      "politics             16                   7",
      "religion             16                   4",
      "orientation           9                   3",
      "skin colour           8                   2",
      "body type             8                   2",
      "phone                 4                   1",
    ])
    D.caption("Table 3. Line-up structure. Consequences: some values never co-occur, some are perfectly collinear, and a pooled per-value rate depends on assigned opponents (Section 6.5).")
    D.h2("2.4 Other data properties")
    D.para("""Three further properties affect interpretation. The orientation attribute contains
    gender-identity values (non_binary, transgender_ftm, transgender_mtf) that duplicate the separate
    gender_identity attribute under different naming, and it places the superordinate label
    Homosexual in competition with its own subdivisions gay and lesbian. The gender field exists in
    the schema but is entirely null. Exposure is unequal: four nationalities and four political
    labels appear roughly three times less often than their peers, so raw counts are not comparable
    across values without win-rate normalisation.""")

    # ---------- 3 PROTOCOL
    D.h1("3. Protocol")
    D.h2("3.1 The null")
    D.para("""Every trial shows exactly four participants differing only on the tested attribute, so
    the no-bias probability that any given value is chosen is exactly 0.25. This is assumption-free
    and does not require a model of the scenario. For a single value the fair share is therefore 25
    percent. For any grouping of values (continent, region, income tier) it is not: a line-up can
    contain several members of one group, up to three Asians in a four-person set, so chance alone
    selects an Asian 75 percent of the time there. For grouped analyses we compute the expected count
    per trial as (members shown / 4), and report relative risk = observed / expected.""")
    D.h2("3.2 Effect units")
    D.para("""Two units are used throughout. For continuous reasoning outcomes, effects are in
    standard deviations of the z-scored metric. For binary choice outcomes we use a linear probability
    model so effects read directly as percentage points of change in the probability that a given
    person is chosen, per one standard deviation of the predictor. Base rates are near 25 percent,
    far from the 0/1 bounds where the linear model misbehaves.""")
    D.h2("3.3 Controls")
    D.para("""Every modelled estimate partials out model identity, scenario, language and trace
    length. Per-value analyses additionally control the display position of the value in question.
    Grouped analyses additionally control how many group members are on offer, without which the
    outcome is dominated by exposure rather than preference. Standard errors are cluster-robust by
    matchup group. Multiplicity is handled with Benjamini-Hochberg correction within each reported
    family of tests. Effect sizes and detection floors are reported alongside p-values, because at
    these sample sizes a 1 percent deviation reaches z = 3.9 and significance carries little
    information on its own.""")
    D.h2("3.4 Two analysis choices that matter")
    D.para("""First, comparisons are made within line-up wherever possible. Because line-ups are
    fixed, cross-line-up comparisons of pooled rates are confounded by assigned opponents; where a
    cross-line-up claim is unavoidable we anchor it on a value common to both line-ups.""")
    D.para("""Second, the outcome is kept concrete. An early version of this analysis collapsed bias
    into a single scalar per trace (how favoured the chosen demographic was) and found nothing across
    10,612 comparisons. That null was an aggregation artefact: a metric that pushes toward sacrificing
    one group and away from another cancels to zero when averaged over demographics. Keeping the
    outcome at the level of a specific person raised the same effects from 0.036 SD to 12 percentage
    points with no change to the data or the controls. Averaging predictors is safe; averaging the
    outcome across demographics is not.""")

    # ---------- 4 REPLICATED
    D.h1("4. What we replicate")
    D.para("""Before reporting anything new we reproduced the published demographic findings from the
    raw data. All of the following are White Circle's results, not ours. Our percentages are computed
    on the structured-mode choice population and agree with them in every case.""")
    D.mono([
      "PUBLISHED CLAIM                                        OUR MEASUREMENT",
      "Atheists, Scientologists, Satanists selected most      Satanist 57.4%, Scientologist 54.6%,",
      "                                                       Atheist 48.5%  (fair share 25%)",
      "Jewish people consistently most protected              Jewish 12.2%, lowest of 16 religions",
      "No phone targeted far more, regardless of brand        No phone 72.2% vs Android 2.6%",
      "Qwen3: Android most protected, Obese most targeted     Android 2.6%, Obese 81.2%",
      "Gemini / GPT-5.3: Amputee most protected               Amputee 4.6%, lowest in its line-up",
      "French and Russian targeted more                       Russian 31.5%, French 30.1%, top two",
      "Every model biased; models disagree                    qwen3 vs gemini correlate at r = -0.20",
      "                                                       across the 20 nationalities",
    ])
    D.caption("Table 4. Replication of published findings. The demographic rankings in this paper are confirmatory, not novel; the contribution is in Sections 5 and 6.")
    D.para("""One published finding constrains our own numbers rather than being replicated by them.
    White Circle show that structured output collapses refusal rates and amplifies bias relative to
    free text. Our analysis uses structured mode exclusively, because free-text responses lose roughly
    two thirds of parseable choices. Every percentage in this paper is therefore from the higher-bias
    condition, and should not be read as a general estimate of model bias.""")

    # ---------- 5 NEW ANALYSIS
    D.h1("5. What we add")
    D.para("""Four analyses that the published work does not perform. Two require the reasoning
    traces. Two require treating position and repeatability as signal rather than nuisance.""")
    D.h2("5.1 Trace profiling (new instrument)")
    D.para("""We extract the 22-metric profile for every trace and ask, within a fixed line-up, how
    the reasoning differs depending on which of the four people is chosen. The comparison is
    same-scenario, same-model, same four participants; only the verdict varies. We report both the
    coarse five-family scores and the individual metrics, because they can disagree (Section 6.3).""")
    D.h2("5.2 Victim-conditional reasoning (new question)")
    D.para("""For each attribute value we split traces into those where that value was chosen and
    those where it was on offer but someone else was chosen, and compare profiles. This is the
    concrete form of the question and it is identified within line-up, since the composition is fixed
    while the choice varies.""")
    D.h2("5.3 Position (nuisance treated as signal)")
    D.para("""KillBench randomises display order so that position averages out of the bias estimates.
    We recover the display slot of the chosen participant for all 104,377 structured choices by the
    three reasoning models and tabulate the distribution per model.""")
    D.h2("5.4 Repeatability (an unused experiment in the released data)")
    D.para("""Every matchup is run three times with the order reshuffled. We verified the reshuffle is
    genuine: 88.1 percent of matchups have all three display orders distinct, and the person in slot 1
    changes at exactly the chance rate (37.4 percent observed against 37.5 percent predicted). This
    supports a decision-reliability test. Crucially it also defines a hard baseline: a model that
    always picks slot 1 would repeat the same person only 6.25 percent of the time, identical to
    random guessing. Person-level repeatability above 6.25 percent is the only evidence that a model
    is choosing a person at all.""")

    # ---------- 6 FINDINGS
    D.h1("6. New findings")
    D.h2("6.1 Serial-position effects dominate the decision")
    D.figure("L2_position_bias.png",
             "Figure 1. Distribution of the chosen display slot, per model, across 104,377 structured choices. Uniform would be 25 percent per slot.", maxh=0.27)
    D.mono([
      "MODEL                   SLOT 1   SLOT 2   SLOT 3   SLOT 4        n",
      "gemini-3.1-pro-preview   84.8%     3.8%     4.0%     7.5%   38,370",
      "kimi-k2.5                59.8%     2.8%     4.4%    33.0%   27,184",
      "qwen3-235b-a22b          29.9%    10.0%    19.9%    40.2%   38,823",
    ])
    D.caption("Table 5. Position bias. Gemini shows near-pure primacy; Kimi shows primacy plus recency and avoids the middle; Qwen shows recency.")
    D.para("""These effects are larger than any demographic effect in the benchmark. They also raise a
    measurement question about aggregate bias scores. A model that answers largely by position has its
    demographic preference diluted by position noise, so a single per-model bias score may be mixing
    two distinct quantities: how demographically biased a model is, and how position-bound it is. Two
    models with identical demographic preferences would score differently if one is more
    position-driven. We cannot quantify the size of that confound without the original scoring code,
    and we flag it as a candidate rather than a demonstrated error.""")
    D.h2("6.2 Decisions are barely reproducible, and on two attributes there is no person-level decision")
    D.figure("L6_person_vs_slot_by_dimension.png",
             "Figure 2. Repeatability by attribute across 13,120 matchups with all three rolls. Chance agreement is 6.25 percent for both measures.", maxh=0.28)
    D.mono([
      "                    SAME PERSON   SAME SLOT      (chance = 6.25%)",
      "BY MODEL",
      "  qwen3-235b-a22b         29.6%       19.7%",
      "  kimi-k2.5               20.0%       50.5%",
      "  gemini-3.1-pro          19.6%       61.9%",
      "BY ATTRIBUTE",
      "  body type               51.9%       13.2%      person-driven",
      "  phone                   47.2%       14.7%      person-driven",
      "  religion                18.6%       49.5%      mostly position",
      "  politics                16.8%       40.6%      mostly position",
      "  nationality              7.5%       64.5%      AT CHANCE",
      "  skin colour              7.1%       67.2%      AT CHANCE",
    ])
    D.caption("Table 6. Person-level versus slot-level repeatability. The two measures are mechanically anti-correlated; the informative quantity is person repeatability against the 6.25 percent floor.")
    D.para("""The most consistent model reproduces its own life-or-death decision under a third of the
    time on an identical dilemma. Gemini and Kimi are roughly three times more consistent about
    position than about person. For nationality and skin colour, person repeatability sits at the
    chance floor: on those attributes the models are selecting a slot, not a person.""")
    D.para("""This reframes rather than refutes the published nationality results. A stable aggregate
    tilt can coexist with near-random individual choices, so a persistent small demographic deviation
    is still real. What the repeatability test adds is that the process generating it is not
    person-level deliberation. It also explains a pattern we could not otherwise interpret: the two
    attributes with the largest biases in the whole benchmark, body type and phone, are exactly the
    two that models actually attend to at 52 and 47 percent person repeatability, seven to eight times
    chance.""")

    D.h2("6.3 Reasoning structure covaries with the verdict, and the coarse score can hide it")
    D.figure("L1_disability_coarse_vs_granular.png",
             "Figure 3. Body-type line-up. Reasoning when a disabled person is chosen versus a non-disabled person. The coarse Metacognitive family score is flat because two of its constituent metrics move in opposite directions.", maxh=0.27)
    D.para("""In the line-up containing an amputee, a wheelchair user, a skinny and a slim participant,
    traces where a disabled person is chosen differ sharply from traces where a non-disabled person is
    chosen. Hedging is +0.77 SD against -0.28; perspective-taking is -0.57 against +0.24; branching
    factor is -0.66 against +0.29; words written +0.73 against -0.08. The coarse Metacognitive family
    score, however, is +0.06 SD, effectively flat, because hedging and perspective-taking cancel
    within the family. Reporting only the five coarse families would have produced a null.""")
    D.para("""Read plainly, when this model condemns a disabled person it hesitates more and considers
    less: more words, more hedging, fewer alternatives opened, less perspective-taking.""")
    D.h2("6.4 The pattern is a gradient, and it replicates")
    D.figure("r2_religion_monotonic.png",
             "Figure 4. Religion. Reasoning shift when each faith is the one chosen, against how often it is chosen. Marker shape indicates line-up; the relationship holds within each of the four line-ups separately.", maxh=0.26)
    D.mono([
      "METRIC                            RELIGION (16)   POLITICS (16)",
      "Breadth (family)                        -0.896          -0.950",
      "exploration_exploitation_ratio          -0.945          -0.938",
      "branching_factor                        -0.932          -0.916",
      "perspective_taking                      -0.923          -0.905",
      "hedging_density                         +0.906          +0.908",
      "cross_branch_connectivity               +0.873          +0.915",
      "avg_tokens (length)                     +0.846          +0.433 ns",
    ])
    D.caption("Table 7. Correlation between an attribute value's selection rate and the reasoning shift when it is chosen. All entries p < 1e-4 except the politics length term (p = 0.09).")
    D.para("""In the identical dilemma, choosing the Satanist comes with 0.81 SD fewer alternatives
    explored and 0.72 SD more hedging; choosing the Hindu comes with 0.73 SD more alternatives and
    0.65 SD less hedging, a swing of roughly 1.5 SD between two victims in the same four-way choice.
    The relationship is monotonic across all 16 religions and holds inside each of the four line-ups
    separately, so line-up composition cannot explain it.""")
    D.para("""Politics replicates it on 16 entirely different values with near-identical coefficients.
    One difference matters more than the replication itself: trace length is not significant for
    politics (r = +0.43, p = 0.09) where it was +0.85 for religion. The graph-structure metrics carry
    the effect independently of how much the model writes, which rules out the simplest deflationary
    explanation.""")
    D.para("""Interpretation is constrained. The trace and the choice are produced in the same forward
    pass, so this is covariation, not causation, and a reader may reasonably object that they are the
    same event rather than two linked events. What the direction adds is that the model produces
    hedged, narrow text when it selects its usual target, and genuinely exploratory text when it
    selects an unusual one.""")
    D.h2("6.5 The strongest bias in the benchmark has no reasoning signature")
    D.figure("L3_silent_bias.png",
             "Figure 5. Each attribute's most-selected value: how often it is chosen, against how much the reasoning changes when it is chosen. Class and the unmarked racial category are silent.", maxh=0.26)
    D.mono([
      "ATTRIBUTE      PREFERRED VICTIM    CHOSEN     SIGNATURE   VERDICT",
      "body type      Obese                81.2%         0.672   strong",
      "phone          No phone             72.2%         0.020   SILENT",
      "religion       Satanist             57.4%         1.535   strong",
      "politics       Far-right            50.0%         1.015   strong",
      "orientation    Asexual              45.8%         0.873   strong",
      "nationality    Ukrainian            30.3%         0.283   moderate",
      "skin colour    Light-skinned        29.1%         0.038   SILENT",
      "",
      "corr(selection rate, signature size) = +0.191, p = 0.68  (not significant)",
    ])
    D.caption("Table 8. Signature = |branching shift| + |hedging shift| on the attribute's own most-selected value. Bias strength does not predict whether the reasoning shows it.")
    D.para("""For the phone attribute the preferred victim is chosen 72.2 percent of the time on
    n = 1,677 traces, and the reasoning shift is branching -0.007, hedging -0.013, against a detection
    floor of about 0.16 SD. This is a well-powered zero, not an underpowered null. The model reliably
    identifies the poorest person, selects them nearly three times more often than chance, does so
    consistently across reshuffles (47.2 percent person repeatability, Table 6), and its reasoning
    never registers the fact.""")
    D.para("""What separates the strong-signature attributes from the silent ones is not how biased the
    model is but what the bias is about. Religion, politics, orientation and body type produce
    signatures of 0.67 to 1.54; class and the unmarked racial category produce 0.02 to 0.04. We offer
    this as the hypothesis the data generates, not as a tested claim: the grouping is post hoc over
    seven attributes. The phone null itself is not post hoc.""")
    D.para("""The practical consequence is direct. A guardrail that monitors reasoning traces for
    signs of unfair deliberation would flag the religion and politics cases and miss the largest bias
    in the benchmark entirely.""")
    D.h2("6.6 One case where the signature tracks identity rather than frequency")
    D.figure("r4_bodytype_disability.png",
             "Figure 6. Body type. The amputee is the least-selected participant in the line-up yet carries the same narrow, heavily-hedged reasoning as the most-selected wheelchair user.", maxh=0.26)
    D.para("""Throughout, the model's stigmatised target and its most frequent target are the same
    person, so the hedged narrow signature admits two readings: motivated reasoning about a
    disfavoured group, or simply that the default answer requires no search. The amputee partially
    separates them. Chosen only 4.6 percent of the time, the rarest in its line-up, it nonetheless
    shows branching -0.615 and hedging +0.801, close to the wheelchair user's -0.709 and +0.730 at
    48.5 percent. Among four participants matched on rarity (4.6 to 6.9 percent selection), only the
    disabled one shows this pattern, and it points opposite to the other three. Removing the amputee
    leaves the line-up near-perfectly ordered by selection rate (r = -0.971); including it collapses
    the ordering to -0.172.""")
    D.para("""This is the thinnest result in the paper. It rests on 109 traces in a single cell with a
    disabled/non-disabled grouping we applied after seeing the data. The effects are 6 to 13 times
    their standard error and directionally match the wheelchair user, but it should be treated as a
    lead for replication rather than an established finding.""")
    D.h2("6.7 Which kind of reasoning precedes a refusal")
    D.figure("L5_refusal_drivers.png",
             "Figure 7. Effect of each reasoning family on the probability of refusing the dilemma outright, per one standard deviation, trace length controlled. Base refusal rate 16.1 percent.", maxh=0.22)
    D.para("""Only structural reasoning accompanies refusal (+7.55 pp, moving refusal from 16 to 24
    percent). Metacognitive (-4.81), Breadth (-3.94) and Depth (-2.90) all accompany a greater
    willingness to name a victim. The metacognitive result is the counterintuitive one: traces in
    which the model reflects on its own reasoning are more likely to end in a choice, not less.""")
    D.para("""A methodological note. Run without controlling trace length, Breadth and Depth appear to
    increase refusal. Longer traces both refuse more and score higher on every metric, so length
    carries the effect. The controlled estimates are reported here and the uncontrolled ones are
    wrong.""")
    D.h2("6.8 A design property that affects published per-value rankings")
    D.figure("L4_lineup_confound.png",
             "Figure 8. Politics. For each value, the selection rate against each of its two line-ups, and the pooled figure. Same identity, different opponents, materially different rate.", maxh=0.26)
    D.para("""Because line-ups are fixed (Table 3), a pooled per-value rate depends on which opponents
    that value was assigned. Liberal is chosen 8.0 percent of the time when it faces the far-right and
    19.4 percent when it faces Green, Republican and Socialist: the same identity, 2.4 times apart.
    Whether Liberal reads as the most protected political identity or an unremarkable one is decided
    by line-up assignment. Communist swings 22.7 to 32.7 percent, Nationalist 14.5 to 22.5 percent.""")
    D.para("""The same structure makes some comparisons unavailable in principle. The indicator for an
    Israeli being present correlates at r = 1.00 with a French person being present, because they
    always appear together; the same holds for Indian with Russian and Korean with Ukrainian. No
    analysis of this dataset can separate an Israeli-specific effect from a French one. Jewish versus
    Anglican is never observed. For phone there is a single line-up, so presence never varies at
    all.""")
    D.para("""None of this affects the headline conclusion that every model is biased, which is
    robust. It bounds how much weight any individual per-value number can carry, and it is
    straightforward to fix in a future run by randomising participant sets.""")

    # ---------- 7 CORRECTION
    D.h1("7. A correction to our own analysis")
    D.para("""An earlier version of this work reported that the size of the reasoning signature scaled
    with the strength of the model's bias, across seven attributes, at r = +0.915 (p = 0.004), and
    described it as a general law. That result was an artefact of the summary statistic.""")
    D.para("""The signature had been measured as the maximum absolute effect over all values within an
    attribute. That maximum is typically driven by a rarely-chosen value rather than the model's
    preferred victim: for phone it came from the Android owner (2.6 percent, n = 61), for body type
    from the amputee. Re-measured on each attribute's own preferred victim, the correlation is
    r = +0.191 (p = 0.68), reported in Table 8. Phone is the decisive counterexample: the
    second-strongest bias in the benchmark with a signature of 0.020.""")
    D.para("""We report this because the failure mode generalises. A summary statistic that silently
    answers a slightly different question than the one posed is difficult to catch by inspection;
    "maximum over values" looked innocuous. The finding that survives, that the signature tracks
    whether an attribute is treated as sensitive rather than how strong the bias is, is more useful
    than the one it replaced.""")

    # ---------- 8 LIMITATIONS
    D.h1("8. Limitations")
    D.mono([
      "1  Covariation, not causation. Trace and choice are produced in a single forward pass.",
      "   Nothing here shows that inducing a reasoning style would change the choice.",
      "2  Stigma and modality are confounded. The model's preference is exactly what makes a",
      "   choice common, so 'disfavoured target' and 'default answer' cannot be separated by",
      "   observation. Section 6.6 is the only partial exception and rests on 109 traces.",
      "3  Structured mode only. All rates come from the condition White Circle show amplifies",
      "   bias relative to free text.",
      "4  Three models. Trace analysis covers qwen3-235b, kimi-k2.5 and gemini-3.1-pro only,",
      "   and these models disagree about who they sacrifice, so pooled estimates average over",
      "   genuine disagreement.",
      "5  Victim-conditional tables are unadjusted means. Model, scenario and language are not",
      "   partialled out in the descriptive tables; within-line-up ordering rules out composition",
      "   but not model mix. Modelled estimates (Sections 6.5, 6.7) do control these.",
      "6  hedging_density is a lexical regex count, so the single strongest metric is partly",
      "   surface-level. The graph metrics move comparably, which is what makes the result more",
      "   than a word-count artefact.",
      "7  Post-hoc groupings. 'Disabled' (2 values) and 'sensitive versus non-sensitive'",
      "   (7 attributes) were defined after seeing results and are hypotheses, not tests.",
      "8  Multilingual traces are scored with English-oriented embedding and NLI models.",
    ])

    # ---------- 9 NEXT
    D.h1("9. The experiment that would resolve the mechanism")
    D.para("""The central open question is whether the hedged, narrow signature attaches to the
    identity of the person being condemned or merely to that person being the default answer.
    Observation cannot separate them. An intervention can.""")
    D.figure("L7_next_experiment.png",
             "Figure 9. Proposed forced-choice design. Constrain the model to a specified victim, hold the scenario fixed, and test whether the signature follows identity or follows being the default.", maxh=0.24)
    D.para("""If the signature follows identity, it is evidence of motivated reasoning and the trace is
    a usable monitoring signal. If it follows being the default, the signature is a search artefact
    and monitoring reasoning for fairness is unlikely to work. Either outcome is informative, and the
    experiment is roughly one day of work on the existing pipeline.""")

    # ---------- 10 REPRODUCIBILITY
    D.h1("10. Reproducibility")
    D.mono([
      "kbtp/config.py      paths, seeds, thresholds, the 22 metric names, filter definitions",
      "kbtp/data.py        parquet shards -> labelable and refusal populations",
      "kbtp/bias.py        win-rates, per-trace alignment, group magnitude",
      "kbtp/extract.py     parallel VRAM-aware ThinkProbe extraction, resumable on row_id",
      "kbtp/profiles.py    the 5 family scores and profile-to-outcome models",
      "kbtp/tables.py      killed vs not-killed tables for any grouping",
      "kbtp/behaviour.py   position bias, repeatability, person versus slot",
      "kbtp/blocs.py       exposure-corrected grouped analysis",
      "kbtp/chain.py       line-up to reasoning to verdict decomposition",
      "",
      "python -m scripts.run_all --skip-extract     regenerates every number and figure",
      "",
      "Fixed seed 42. Extraction is the only GPU step: 83,218 traces, 0 failures,",
      "approximately 1.5 hours on one H100 at 0.27 s per trace.",
    ])
    D.para("""Acknowledgement. This analysis exists only because White Circle released the raw
    reasoning traces alongside the aggregate results. Most benchmark releases do not, and none of
    Sections 6.3 through 6.7 would have been possible otherwise.""")
    D.close()

    md = pdf.infodict()
    md["Title"] = "Reading the reasoning, not just the verdict: a thought-graph analysis of KillBench"
    md["Subject"] = "ThinkProbe applied to KillBench: method, data, protocol, replication, new analysis, new findings"
print("wrote", OUT)
