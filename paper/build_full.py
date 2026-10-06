"""Full analysis paper: integrates every analysis markdown in the repo.
Vector text (extractable). Appendix tables are parsed directly from the .md files
so every number is verbatim."""
import re, textwrap, pathlib
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, matplotlib.image as mpimg
from matplotlib.backends.backend_pdf import PdfPages

ROOT = pathlib.Path("."); FIG = ROOT/"figures"
OUT = pathlib.Path("KillBench_ThinkProbe_Paper.pdf")
A4=(8.27,11.69); L,R,TOP,BOT = 0.075,0.925,0.945,0.055
INK,INK2,ACC="#111111","#555555","#14406e"

def md_tables(path, section):
    """Extract (subheading, header, rows) for every table under '## <section>'."""
    if not pathlib.Path(path).exists(): return []
    txt = pathlib.Path(path).read_text(encoding="utf-8")
    m = re.search(rf"^## {re.escape(section)}\s*$(.*?)(?=^## |\Z)", txt, re.M|re.S)
    if not m: return []
    body, out, sub = m.group(1), [], ""
    for blk in re.split(r"^### ", body, flags=re.M)[0:]:
        lines = blk.strip().split("\n")
        if not lines: continue
        if not lines[0].startswith("|"):
            sub = lines[0].strip(); lines = lines[1:]
        rows = [l for l in lines if l.strip().startswith("|")]
        if len(rows) < 3: continue
        cells = [[c.strip() for c in r.strip().strip("|").split("|")] for r in rows]
        hdr = cells[0]; data = [c for c in cells[2:]]
        out.append((sub, hdr, data))
    return out

class Doc:
    def __init__(self, pdf):
        self.pdf, self.page, self.fig = pdf, 0, None
        self._new()
    def _new(self):
        if self.fig is not None:
            self.fig.text(0.5,0.026,str(self.page),fontsize=8,color=INK2,ha="center")
            self.pdf.savefig(self.fig); plt.close(self.fig)
        self.page += 1
        self.fig = plt.figure(figsize=A4); self.fig.patch.set_facecolor("white")
        if self.page > 1:
            self.fig.text(L,0.973,"Reading the reasoning, not just the verdict",
                          fontsize=7,color="#a0a0a0")
        self.y = TOP
    def need(self,h):
        if self.y-h < BOT: self._new()
    def h1(self,t):
        self.need(0.085); self.y -= 0.018
        self.fig.text(L,self.y,t,fontsize=14,color=INK,weight="bold",va="top"); self.y-=0.029
        self.fig.add_artist(plt.Line2D([L,R],[self.y+0.005,self.y+0.005],color="#c8c8c8",lw=1))
        self.y-=0.014
    def h2(self,t):
        self.need(0.055); self.y -= 0.011
        self.fig.text(L,self.y,t,fontsize=10.6,color=ACC,weight="bold",va="top"); self.y-=0.023
    def h3(self,t):
        self.need(0.040); self.y -= 0.007
        self.fig.text(L,self.y,t,fontsize=9.6,color=INK,weight="bold",va="top"); self.y-=0.020
    def p(self,t,size=9.3,color=INK,width=108,indent=0.0):
        for para in t.strip().split("\n\n"):
            lines = textwrap.wrap(" ".join(para.split()), width)
            for ln in lines:
                if self.y-0.0152 < BOT: self._new()
                self.fig.text(L+indent,self.y,ln,fontsize=size,color=color,va="top")
                self.y -= 0.0152
            self.y -= 0.0085
    def bullets(self,items,size=9.3):
        for it in items:
            lines = textwrap.wrap(" ".join(it.split()), 104)
            for i,ln in enumerate(lines):
                if self.y-0.0152 < BOT: self._new()
                pre = "  •  " if i==0 else "     "
                self.fig.text(L,self.y,pre+ln,fontsize=size,color=INK,va="top")
                self.y -= 0.0152
            self.y -= 0.004
        self.y -= 0.006
    def mono(self,lines,size=7.6,color=INK):
        for ln in lines:
            if self.y-0.0128 < BOT: self._new()
            self.fig.text(L,self.y,ln,fontsize=size,color=color,family="DejaVu Sans Mono",va="top")
            self.y -= 0.0128
        self.y -= 0.009
    def table(self,hdr,rows,size=7.4,widths=None,note=None):
        if widths is None:
            widths=[max(len(str(hdr[i])), *(len(str(r[i])) for r in rows))+2 if rows else len(hdr[i])+2
                    for i in range(len(hdr))]
        def fmt(cells):
            out=[]
            for i,c in enumerate(cells):
                c=str(c).replace("**","")
                out.append(c.ljust(widths[i]) if i==0 else c.rjust(widths[i]))
            return "".join(out)
        self.need(0.05)
        self.mono([fmt(hdr)],size=size)
        self.y += 0.009
        self.fig.add_artist(plt.Line2D([L,R],[self.y+0.010,self.y+0.010],color="#dcdcdc",lw=0.8))
        self.mono([fmt(r) for r in rows],size=size)
        if note: self.caption(note)
    def caption(self,t,size=8.0):
        for ln in textwrap.wrap(" ".join(t.split()),118):
            if self.y-0.0132 < BOT: self._new()
            self.fig.text(L,self.y,ln,fontsize=size,color=INK2,va="top",style="italic")
            self.y -= 0.0132
        self.y -= 0.009
    def figure(self,name,cap,maxh=0.28):
        p = FIG/name
        if not p.exists(): return
        im = mpimg.imread(str(p)); h,w = im.shape[:2]
        aw = R-L; ah = aw*(h/w)*(A4[0]/A4[1])
        if ah>maxh: ah=maxh; aw=ah*(w/h)*(A4[1]/A4[0])
        if self.y-(ah+0.05) < BOT: self._new()
        ax = self.fig.add_axes([L+(R-L-aw)/2, self.y-ah, aw, ah]); ax.imshow(im); ax.axis("off")
        self.y -= ah+0.011
        self.caption(cap)
    def close(self):
        self.fig.text(0.5,0.026,str(self.page),fontsize=8,color=INK2,ha="center")
        self.pdf.savefig(self.fig); plt.close(self.fig)

with PdfPages(OUT) as pdf:
    D = Doc(pdf); F = D.fig
    # ---------------- TITLE + ABSTRACT ----------------
    F.text(L,0.885,"Reading the reasoning, not just the verdict:",fontsize=19.5,color=INK,weight="bold")
    F.text(L,0.855,"a thought-graph analysis of KillBench",fontsize=19.5,color=INK,weight="bold")
    F.text(L,0.822,"Position effects, decision irreproducibility, and the reasoning traces that",fontsize=11.5,color=ACC)
    F.text(L,0.803,"a choice-level bias benchmark leaves unread",fontsize=11.5,color=ACC)
    F.add_artist(plt.Line2D([L,R],[0.788,0.788],color="#c8c8c8",lw=1))
    D.y = 0.762
    D.h2("Abstract")
    D.p("""We apply a non-generative thought-graph profiler to 83,218 chain-of-thought traces from
    KillBench, a 1.37-million-decision benchmark in which frontier models must choose one of four
    otherwise identical people to die, and we recover four results that the benchmark's published
    choice-level analysis cannot produce. Measuring demographic bias from choices alone is
    well-established, but it leaves two things unexamined: the reasoning the model emits on the way to
    the choice, which the dataset records and the analysis discards, and the display position and
    answer repeatability, which the design randomises away as nuisance. We extract a 22-metric
    structural profile per trace using regex cue-phrase segmentation, sentence-embedding TextTiling and
    an NLI cross-encoder, with no language model in the interpretation loop, and we pair it with a
    within-line-up comparison of the traces that precede each different victim choice. We find that
    serial-position effects dominate the decision process (Gemini 3.1 Pro selects the first-listed
    person in 84.8 percent of 104,377 choices); that decisions are barely reproducible (the most
    consistent model repeats its choice on an identical dilemma 29.6 percent of the time, and for
    nationality and skin colour person-level repeatability sits at the 6.25 percent chance floor);
    that reasoning structure covaries with the identity of the victim at r = -0.93 for religion and
    r = -0.92 for politics across 32 distinct values; and that the strongest demographic preference in
    the entire benchmark, against people who own no phone at 72.2 percent, carries no reasoning
    signature whatsoever. The most consequential single number is that last one: a well-powered zero
    (branching -0.007, hedging -0.013, n = 1,677) attached to the largest bias measured anywhere in the
    dataset.""")
    D.mono(["Primary source: White Circle, KillBench: discovering hidden biases of LLMs, April 2026.",
            "Instrument: ThinkProbe (repository kmamine/ThinkProb).",
            "All results use KillBench structured-output mode. Code: kbtp/ ; one command reproduces every number."],
           size=7.8,color=INK2)

    # ---------------- 1 INTRODUCTION ----------------
    D.h1("1. Introduction")
    D.p("""A benchmark that asks a model to choose who dies records two things: the choice, and the
    reasoning the model produced on the way to it. KillBench analyses the first and ships the second
    unread. Its `reasoning_text` column contains the full chain of thought for every trial, and the
    published analysis, which establishes that all 15 tested models deviate significantly from the
    25 percent fair-share baseline, never opens it.""")
    D.p("""Reading it is not straightforward. A reasoning trace is unstructured text, and the obvious
    approach, asking another language model to score it, introduces exactly the circularity that makes
    the result uninterpretable: one model's bias assessing another's. A second difficulty is
    statistical. The natural summary, a single scalar of how biased each trace's choice was, destroys
    the signal: a reasoning feature that pushes toward sacrificing one demographic and away from
    another averages to zero. We made this mistake first, and report it in Section 5.4, because the
    correction is what makes the rest of the analysis work.""")
    D.p("""Our approach is to keep the instrument non-generative and the outcome concrete. ThinkProbe
    converts a trace into a directed thought graph using deterministic rules, sentence embeddings and
    an NLI cross-encoder, yielding a 22-dimensional structural profile with no language model in the
    interpretation loop. The outcome is never aggregated: we ask whether a reasoning style changes the
    probability that one specific person is the one chosen, within a fixed line-up where the four
    participants, the scenario and the model are all held constant and only the verdict varies. We
    then exploit two properties of the released data that the original design treats as nuisance to be
    averaged out: the display position of each participant, and the fact that every matchup is run
    three times with the order reshuffled.""")
    D.h2("Contributions")
    D.bullets([
      "We show that serial-position effects dominate the decision process: Gemini 3.1 Pro selects the first-listed participant in 84.8 percent of 104,377 choices, an effect larger than any demographic effect in the benchmark, and one that plausibly confounds per-model bias scores.",
      "We show that decisions are barely reproducible: on identical dilemmas the most consistent model repeats its choice 29.6 percent of the time, and for nationality and skin colour person-level repeatability is at the 6.25 percent chance floor, meaning no person-level decision is being made on those attributes.",
      "We show that reasoning structure covaries strongly with victim identity for religion (r = -0.93) and politics (r = -0.92) across 32 values, holds within every line-up, and is not explained by trace length.",
      "We show that the benchmark's strongest preference, against people with no phone (72.2 percent), carries a well-powered zero reasoning signature, and we document a benchmark design property, fixed participant line-ups, that limits what per-value rates can mean.",
    ])
    D.p("""Section 2 places the work relative to the source benchmark. Section 3 describes ThinkProbe.
    Section 4 describes KillBench and the properties of the released data. Section 5 gives the
    statistical protocol. Section 6 reports what we replicate. Sections 7 to 10 report the outcome
    layer, the reasoning layer, the behavioural layer and a decomposition linking them. Section 11
    retracts one of our own results. Sections 12 to 14 cover limitations, conclusions and
    reproducibility. Appendix A gives the complete per-dimension profile tables; Appendix B the
    complete demographic value lists.""")

    # ---------------- 2 RELATED ----------------
    D.h1("2. Relation to prior work")
    D.p("""This paper is an extension of a single primary source and should be read alongside it.
    White Circle's KillBench (April 2026) contributes the benchmark design, the 1.37M-trial data
    collection across 15 models and 9 providers, and the finding that every tested model shows
    statistically significant demographic preference. It further reports that structured output acts
    as a partial jailbreak, collapsing refusal rates and amplifying measured bias relative to
    free-text, and that models frequently describe their choices as random when they are not. All
    demographic rankings we reproduce in Section 6 are theirs.""")
    D.p("""The KillBench write-up situates itself relative to earlier work on implicit bias in LLM
    decisions over human lives. We have not independently verified those references and therefore do
    not cite them as established here.""")
    D.mono(["[CITATION NEEDED] Jin et al., 2024 - cited by White Circle as prior work on implicit LLM",
            "                  bias in life-and-death decisions. Verify before submission.",
            "[CITATION NEEDED] Mazeika et al., 2025 - same. Verify before submission.",
            "[CITATION NEEDED] ThinkProbe method paper. Repository kmamine/ThinkProb; the arXiv",
            "                  identifier in the project spec has not been verified here."],
           size=7.6,color="#8a3030")
    D.p("""No citation in this document was generated from memory. Where a reference could not be
    programmatically verified in this environment it is marked as a placeholder above rather than
    rendered as a citation.""")

    # ---------------- 3 METHOD ----------------
    D.h1("3. Method: ThinkProbe")
    D.h2("3.1 Pipeline")
    D.p("""ThinkProbe converts a free-text reasoning trace into a directed thought graph and reduces it
    to a fixed-dimensional profile. The pipeline is deliberately non-generative: no language model
    interprets the trace, which avoids assessing one model's output with another model's judgement.
    Five passes run in sequence. (i) Structural and cue-phrase segmentation splits the trace into
    thought units and assigns each a boundary class from a compiled lexicon; paragraph breaks default
    to sequential, and spans shorter than three sentences or fifty tokens are merged forward.
    (ii) A TextTiling pass encodes sentences with all-MiniLM-L6-v2, slides a window of three, and
    inserts soft boundaries at local similarity minima below the 30th within-trace percentile.
    (iii) A semantic-trajectory pass assigns branching and elaboration edges. (iv) A cross-segment
    pass adds synthesis and backtracking edges. (v) An NLI pass with cross-encoder/nli-deberta-v3-large
    promotes adjacent sequential edges to support, contrast or elaboration above threshold 0.75, and
    long-range backtrack edges above 0.70, all pairs batched per trace.""")
    D.p("""Nodes are then typed by a deterministic priority rule set into 12 node types across four
    families, and the graph is reduced to the 22-metric profile below. One implementation detail
    matters for reuse: segment() returns thought units without node types, and classify_nodes() must
    be called before graph assembly. Omitting it leaves roughly half the metrics degenerate.""")
    D.h2("3.2 The 22 metrics and the five families")
    D.table(["FAMILY","METRICS"],
      [["Breadth","branching_factor, unique_perspective_count, domain_spread, first_idea_diversity"],
       ["Depth","max_elaboration_chain, mean_branch_depth, specificity_gradient, reasoning_density"],
       ["Structure","exploration_exploitation_ratio, backtracking_rate, cross_branch_connectivity,"],
       ["","convergence_index, graph_density, revision_depth"],
       ["Metacognitive","self_reflection_rate, critique_to_hypothesis_ratio, hedging_density,"],
       ["","perspective_taking"],
       ["Efficiency","token_per_idea, redundancy_ratio"],
       ["Size (control)","avg_tokens, avg_tus"]],
      widths=[17,92], size=7.6,
      note="Table 1. A family score is the mean of its z-scored constituent metrics, so all scores are in standard-deviation units. The two size summaries are used as a length control, not as structure. Selected definitions: branching_factor = |E_BRCH|/|V|; reasoning_density = fraction of nodes in at least one semantic edge; backtracking_rate = |E_BACK|/|E_sem|; revision_depth = mean sequential distance across BACK edges; hedging_density = proportion of thought units containing uncertainty markers; redundancy_ratio = fraction of thought-unit pairs with cosine similarity above 0.90.")
    D.h2("3.3 Extraction")
    D.p("""Extraction ran on one NVIDIA H100 at 0.27 s per trace with four worker processes, about
    1.5 hours for the full population, resumable per trace on row_id. All 83,218 traces extracted
    without error (69,867 decisions, 13,351 refusals).""")

    # ---------------- 4 DATA ----------------
    D.h1("4. Data")
    D.h2("4.1 The benchmark")
    D.p("""KillBench (1,368,936 rows, 11 parquet shards) presents 20 scenarios in which a model selects
    exactly one of four participants for a harmful outcome. The four differ only on one tested
    attribute; age and role are constant within a trial. We verified the framing across all 13 civilian
    scenarios and it is uniform: the chosen participant is always the one who dies. Representative
    instructions include "One person will not enter the bunker and will die", "Who will the drone not
    rescue?", "Who will be pushed off the roof?" and "Whose compartment will be flooded?". No civilian
    scenario asks who to save, so no sign-flipping is required. The 7 military scenarios select a
    building rather than a person and are excluded from person-level analysis.""")
    D.h2("4.2 Demographic attributes")
    D.table(["CATEGORY","VARIABLE(S)","VALUES","ROWS"],
      [["Origin / nationality","nationality","20","302,040"],
       ["Belief: political","politics","16","220,428"],
       ["Belief: religious","religion","16","189,720"],
       ["Sexuality and gender identity","orientation, gender_identity","9 + 4","171,288"],
       ["Physical appearance / body","skin_color, body_type","8 + 8","174,096"],
       ["Socioeconomic proxy","phone","4","43,524"]],
      widths=[32,30,9,11], size=7.8,
      note="Table 2. The six demographic categories, plus 10 intersectional pairs at 26,784 rows each (not analysed here). Complete value lists in Appendix B.")
    D.h2("4.3 Filter cascade and analysed populations")
    D.table(["POPULATION","ROWS"],
      [["all rows","1,368,936"],
       ["reasoning_text >= 2000 characters","180,808"],
       ["  of which structured","105,234"],
       ["  structured and non-refusal","88,035"],
       ["  + single-dimension + parsed choice  (LABELABLE, primary)","69,867"],
       ["long refusals (secondary population)","13,351"],
       ["structured choice population used for rate estimation","552,973"],
       ["nationality person-level trials, civilian scenarios","170,779"]],
      widths=[62,14], size=7.8,
      note="Table 3. Structured mode only. Free-text responses lose roughly two thirds of parseable choices to the judge parser, so all rates in this paper come from the condition White Circle show amplifies bias.")
    D.h2("4.4 Only three models emit reasoning")
    D.p("""Substantial reasoning text exists for three models: qwen3-235b-a22b (33,299 labelable
    traces), moonshotai/kimi-k2.5 (20,189) and google/gemini-3.1-pro-preview (16,170).
    x-ai/grok-4.1-fast contributes 209 and the remaining eleven models approximately zero. Any
    trace-based extension of KillBench is therefore a three-model study. Reasoning is also
    English-dominated regardless of prompt language: models emit English section headers and English
    meta-reasoning under Chinese, Arabic and Russian prompts, which makes English-oriented embedding
    and NLI models applicable but means the six-language design tests multilingual prompts rather than
    multilingual reasoning.""")
    D.h2("4.5 Line-ups are fixed, not randomised")
    D.p("""The four participants are not drawn at random. Each attribute reuses a small set of fixed
    4-person sets. This is the single most consequential property of the released data for anyone
    analysing it, and it is not stated in the published write-up.""")
    D.table(["ATTRIBUTE","VALUES","DISTINCT LINE-UPS"],
      [["nationality","20","9"],["politics","16","7"],["religion","16","4"],
       ["orientation","9","3"],["skin colour","8","2"],["body type","8","2"],["phone","4","1"]],
      widths=[18,10,20], size=7.8,
      note="Table 4. Line-up structure per attribute.")
    D.mono([
      "The nine nationality line-ups:",
      "  American, Chinese, French, Israeli        Australian, Brazilian, Nigerian, Polish",
      "  Egyptian, French, Indonesian, Israeli     Japanese, Korean, Turkish, Ukrainian",
      "  Indian, Iranian, Nigerian, Russian        German, Indian, Mexican, Russian",
      "  Australian, Korean, Mexican, Ukrainian    American, British, Chinese, Iranian",
      "  Brazilian, Egyptian, German, Japanese",
    ], size=7.6)
    D.p("""Three consequences follow. First, some values are statistically inseparable. Israeli appears
    in exactly two line-ups and French appears in both, so the indicator "an Israeli is present"
    correlates at r = 1.00 with "a French person is present"; likewise Indian with Russian, Korean with
    Ukrainian, American with Chinese. In body type, presence of the wheelchair user is identical to
    presence of the skinny, slim and amputee participants. For phone there is one line-up, so presence
    never varies at all. Second, many pairwise comparisons are never observed: Jewish versus Anglican
    does not occur. Third, a pooled per-value rate depends on assigned opponents, quantified in
    Section 7.6.""")
    D.h2("4.6 Attribute definition defects")
    D.p("""Three defects affect interpretation. The orientation attribute contains gender-identity
    values (non_binary, transgender_ftm, transgender_mtf) that duplicate the separate gender_identity
    attribute under different naming conventions, so the same construct is measured twice in two
    variables with two label formats; it also places the superordinate label Homosexual in competition
    with its own subdivisions gay and lesbian within the same four-way choice. The gender field exists
    in the schema but is entirely null. Exposure is unequal: four nationalities (Indonesian, British,
    Polish, Turkish) and four political labels (Green, Republican, Democrat, Social Democrat) appear
    roughly three times less often than their peers, and Asexual, Bisexual and Heterosexual appear
    twice as often as other orientations, so raw counts are not comparable across values without
    win-rate normalisation.""")

    # ---------------- 5 PROTOCOL ----------------
    D.h1("5. Protocol")
    D.h2("5.1 The null")
    D.p("""Every trial shows exactly four participants differing only on the tested attribute, so the
    no-bias probability that any given value is chosen is exactly 0.25. The null is therefore exact and
    assumption-free for a single value. For any grouping of values it is not: a line-up can contain
    several members of one group, up to two Europeans and three Asians in the nationality sets, and if
    three of four on offer are Asian then chance alone selects an Asian 75 percent of the time.
    Comparing a bloc's raw rate to 25 percent would brand every large bloc biased purely through
    exposure. For grouped analyses we therefore compute, per trial with n_B of the four displayed
    belonging to bloc B, an expected contribution of n_B/4; summed over trials this gives the expected
    count, and the effect size is the relative risk, observed divided by expected, reported as percent
    above or below fair share. Its variance is the sum over trials of p(1-p) with p = n_B/4.""")
    D.h2("5.2 Effect units")
    D.p("""Two units are used. For continuous reasoning outcomes, effects are in standard deviations of
    the z-scored metric. For binary choice outcomes we use a linear probability model so effects read
    directly as percentage points of change in the probability that a specific person is chosen, per
    one standard deviation of the predictor; base rates near 25 percent sit far from the 0/1 bounds
    where the linear model misbehaves. Where the outcome is bounded and the direction of a bounds
    artefact matters, results are checked on a log-odds rescaling and by restricting to mid-range base
    rates.""")
    D.h2("5.3 Controls and inference")
    D.p("""Every modelled estimate partials out model identity, scenario, language and trace length.
    Per-value analyses additionally control the display position of the value in question; grouped
    analyses additionally control how many group members are on offer. Standard errors are
    cluster-robust by matchup group. Multiplicity is handled with Benjamini-Hochberg correction within
    each reported family of tests. Effect sizes and detection floors are reported alongside p-values
    throughout, because at these sample sizes a 1 percent deviation reaches z = 3.9 and significance
    alone carries little information. Comparisons are made within line-up wherever possible; where a
    cross-line-up claim is unavoidable it is anchored on a value common to both line-ups.""")
    D.h2("5.4 An analysis choice that determined the outcome")
    D.p("""An earlier version of this work collapsed bias into a single scalar per trace, the
    leave-one-out win-rate of the chosen demographic minus 0.25, and regressed the 22 metrics on it
    across an enumerated grid of 10,612 comparisons (8 bias operationalisations, 20 strata, 3 control
    levels). It found essentially nothing: maximum standardised beta 0.036 against a minimum
    detectable effect of about 0.01.""")
    D.p("""That null was an aggregation artefact. Because a metric can push toward sacrificing one
    demographic and away from another, averaging over demographics cancels the effect. Keeping the
    outcome at the level of a specific person, with no change to the data, the instrument or the
    controls, moved the same effects from 0.036 SD to as much as 12 percentage points. The general
    lesson is asymmetric: averaging the predictors is safe, and Section 9.1 shows the five coarse
    families reproduce what the 22 metrics find; averaging the outcome across demographics is not.""")

    # ---------------- 6 REPLICATION ----------------
    D.h1("6. What we replicate")
    D.p("""Before reporting anything new we reproduced the published demographic findings from the raw
    data. All of the following are White Circle's results. Our percentages are computed on the
    structured-mode choice population and agree in every case. The demographic rankings in this paper
    are confirmatory; the contribution is in Sections 8 to 10.""")
    D.table(["PUBLISHED CLAIM","OUR MEASUREMENT"],
      [["Atheists, Scientologists, Satanists selected most","Satanist 57.4%, Scientologist 54.6%, Atheist 48.5%"],
       ["Jewish people consistently most protected","Jewish 12.2%, lowest of 16 religions"],
       ["No phone targeted far more, any brand","No phone 72.2% vs Android 2.6%"],
       ["Qwen3: Android protected, Obese targeted","Android 2.6%, Obese 81.2%"],
       ["Gemini / GPT-5.3: Amputee most protected","Amputee 4.6%, lowest in its line-up"],
       ["French and Russian targeted more","Russian 31.5%, French 30.1%, the top two"],
       ["Every model biased; models disagree","qwen3 vs gemini r = -0.20 across 20 nationalities"],
       ["Structured output amplifies bias","adopted as a caveat on all our rates, not re-tested"]],
      widths=[52,58], size=7.6,
      note="Table 5. Replication of published findings. Fair share is 25 percent throughout.")

    # ---------------- 7 OUTCOME LAYER ----------------
    D.h1("7. The outcome layer: who is chosen to die")
    D.h2("7.1 Nationality")
    D.p("""170,779 person-level trials, 13 civilian scenarios, 15 models, 6 languages. Seventeen of
    twenty nationalities deviate significantly from 25 percent (BH q<0.05; the exceptions are British,
    Brazilian and American). The spread is 10.7 points: a Russian is 1.51 times more likely to be
    chosen than an Israeli.""")
    D.table(["NATIONALITY","AVAIL","KILLED","KILL %","95% CI","vs 25","KILL:SPARED"],
      [["Russian","38,108","12,012","31.52","31.06-31.99","+6.52","1 : 2.17"],
       ["French","38,177","11,475","30.06","29.60-30.52","+5.06","1 : 2.33"],
       ["Australian","38,425","11,493","29.91","29.45-30.37","+4.91","1 : 2.34"],
       ["Turkish","17,861","4,977","27.87","27.21-28.53","+2.87","1 : 2.59"],
       ["Indonesian","17,843","4,738","26.55","25.91-27.21","+1.55","1 : 2.77"],
       ["Polish","17,963","4,728","26.32","25.68-26.97","+1.32","1 : 2.80"],
       ["German","38,238","10,057","26.30","25.86-26.74","+1.30","1 : 2.80"],
       ["Iranian","38,078","9,955","26.14","25.70-26.59","+1.14","1 : 2.83"],
       ["Ukrainian","38,323","9,946","25.95","25.52-26.39","+0.95","1 : 2.85"],
       ["British  (ns)","17,820","4,449","24.97","24.33-25.61","-0.03","1 : 3.01"],
       ["Brazilian  (ns)","38,351","9,541","24.88","24.45-25.31","-0.12","1 : 3.02"],
       ["American  (ns)","38,154","9,469","24.82","24.39-25.25","-0.18","1 : 3.03"],
       ["Egyptian","38,231","8,945","23.40","22.97-23.82","-1.60","1 : 3.27"],
       ["Chinese","38,154","8,752","22.94","22.52-23.36","-2.06","1 : 3.36"],
       ["Mexican","38,312","8,660","22.60","22.19-23.02","-2.40","1 : 3.42"],
       ["Korean","38,323","8,570","22.36","21.95-22.78","-2.64","1 : 3.47"],
       ["Indian","38,108","8,383","22.00","21.58-22.42","-3.00","1 : 3.55"],
       ["Japanese","38,249","8,408","21.98","21.57-22.40","-3.02","1 : 3.55"],
       ["Nigerian","38,221","8,258","21.61","21.20-22.02","-3.39","1 : 3.63"],
       ["Israeli","38,177","7,963","20.86","20.45-21.27","-4.14","1 : 3.79"]],
      widths=[18,10,10,9,15,9,13], size=7.3,
      note="Table 6. Nationality kill rates, all 15 models pooled.")
    D.figure("n1_simple_nationality.png",
      "Figure 1. Nationality kill rates as deviations from the 25 percent fair share. Grey bars are not significantly different from fair.", maxh=0.34)
    D.h3("The models disagree, and pooling hides it")
    D.p("""Cross-model agreement over the 20 rates is r = -0.20 between qwen3 and gemini, +0.15 between
    qwen3 and kimi, and +0.76 between kimi and gemini. qwen3 and gemini are anti-correlated: they
    largely protect opposite nationalities. Per-model spreads are 16.4 points (qwen3) and 18.3 points
    (gemini) against 10.7 pooled, so pooling understates individual bias rather than revealing it.""")
    D.table(["NATIONALITY","qwen3-235b","kimi-k2.5","gemini-3.1-pro","MAX GAP"],
      [["Ukrainian","34.6","24.3","21.7","12.9"],["French","22.2","29.1","35.0","12.8"],
       ["British","18.2","23.2","27.0","8.8"],["Israeli","25.5","21.4","16.7","8.8"],
       ["Korean","18.7","24.9","25.4","6.7"],["Egyptian","27.3","21.7","23.3","5.6"],
       ["Iranian","30.4","25.7","25.5","4.9"],["Russian","28.9","28.3","28.0","0.9"]],
      widths=[18,13,12,17,10], size=7.6,
      note="Table 7. Per-model kill rates (percent) for the nationalities the models most disagree about. On Russia/Ukraine the direction flips: kimi and gemini sacrifice the Russian more, while qwen3 sacrifices the Ukrainian more than any model sacrifices any nationality in the dataset. All three protect the Israeli over the Iranian, gemini most strongly at -8.8 points. qwen3, of Chinese origin, is the only model that sacrifices the Chinese participant well above the American (+6.1), so this is not simple in-group preference.")
    D.figure("n3_disagreement_nationality.png",
      "Figure 2. The eight nationalities on which the three reasoning models disagree most. Same dilemma, same four people, different model, different victim.", maxh=0.30)

    D.h2("7.2 Blocs: continent, cultural region, economic standing")
    D.p("""Aggregating the 20 nationalities requires the exposure-corrected null of Section 5.1.
    Continent spread runs from Oceania at +19.6 percent above fair share to Africa at -10.0 percent;
    cultural region spans 32 points, the widest of any grouping.""")
    D.table(["CONTINENT","NATIONS","EXPOSURES","KILLED","EXPECTED","vs FAIR","z"],
      [["Oceania (Australia)","1","38,425","11,493","9,606","+19.6%","22.2"],
       ["Europe","6","188,629","52,667","47,157","+11.7%","30.3"],
       ["South America (ns)","1","38,351","9,541","9,588","-0.5%","-0.6"],
       ["North America","2","76,466","18,129","19,117","-5.2%","-8.2"],
       ["Asia","8","264,793","61,746","66,198","-6.7%","-24.4"],
       ["Africa","2","76,452","17,203","19,113","-10.0%","-16.0"]],
      widths=[22,9,12,10,11,10,8], size=7.6, note="Table 8. Continent, exposure-corrected.")
    D.table(["CULTURAL REGION","NATIONS","vs FAIR","z"],
      [["Catholic Europe (FR, PL)","2","+15.4%","21.1"],["Orthodox / Eurasian (RU, UA)","2","+14.9%","23.8"],
       ["Anglosphere (US, UK, AU)","3","+7.7%","14.6"],["Muslim Southeast Asia (ID)","1","+6.2%","4.8"],
       ["Protestant Europe (DE)","1","+5.2%","5.9"],["Middle East & N. Africa (EG, IR, TR)","3","+1.4%","2.5"],
       ["Latin America (BR, MX)","2","-5.0%","-8.0"],["Confucian East Asia (CN, JP, KR)","3","-10.3%","-21.3"],
       ["South Asia (IN)","1","-12.0%","-13.5"],["Sub-Saharan Africa (NG)","1","-13.6%","-15.3"],
       ["Israel","1","-16.6%","-18.7"]],
      widths=[38,9,10,8], size=7.6,
      note="Table 9. Cultural region. Note that single-nation blocs are that nation relabelled: Oceania is Australia, Israel is Israel, South Asia is India, Sub-Saharan Africa is Nigeria.")
    D.h3("Economic standing: a pooled near-null that conceals two opposite biases")
    D.p("""Pooled, economic standing is a weak predictor: upper-middle +3.2 percent, high income
    +1.0 percent, lower-middle -4.7 percent, and Global North +1.0 against Global South -0.8. Effects
    are four to six times smaller than continent or region. But the pooled figure is a cancellation.""")
    D.table(["BLOC","qwen3-235b","kimi-k2.5","gemini-3.1-pro"],
      [["Lower-middle income","+13.3% (z=10.1)","-4.7% (z=-3.2)","-8.5% (z=-6.5)"],
       ["Upper-middle income","-0.8% (ns)","+5.2%","+4.4%"],
       ["High income","-7.8% (z=-8.5)","-0.3% (ns)","+2.5% (z=2.8)"],
       ["Global South","+6.3% (z=8.5)","+0.2% (ns)","-2.0% (z=-2.8)"],
       ["Africa","+8.1% (z=3.5)","-11.0% (z=-4.2)","-10.2% (z=-4.4)"],
       ["South America","-17.0% (z=-5.2)","+2.1% (ns)","+1.9% (ns)"],
       ["Oceania (Australia)","+9.7%","+13.3%","+13.4%"],
       ["Europe","+7.7%","+5.1%","+9.6%"]],
      widths=[24,20,18,20], size=7.6,
      note="Table 10. Per-model bloc effects. qwen3 behaves exactly as the intuitive hypothesis predicts, making lower-income participants 13.3 percent more likely to be chosen; gemini does the opposite. Averaging yields approximately zero and the false conclusion that models are indifferent to wealth. The 19-point swing on Africa is the same phenomenon. Europeans and Australians are sacrificed above fair share by all three models, which is the one direction-consistent geographic finding.")

    D.h2("7.3 Religion")
    D.p("""9,843 traces with profiles; 16 values across 4 line-ups. A Satanist is 4.7 times more likely
    to be chosen than a Jewish participant.""")
    D.table(["RELIGION","n KILLED","n NOT-KILLED","CHOSEN %","REL. RISK"],
      [["Satanist","1401","1039","57.4","2.297"],["Scientologist","1389","1153","54.6","2.186"],
       ["Atheist","1202","1275","48.5","1.941"],["Sunni Muslim","823","1561","34.5","1.381"],
       ["Jehovah's Witness","646","1831","26.1","1.043"],["Orthodox Christian","573","1811","24.0","0.961"],
       ["Protestant","527","1857","22.1","0.884"],["Catholic","461","1923","19.3","0.773"],
       ["Shia Muslim","429","2113","16.9","0.675"],["Buddhist","385","2055","15.8","0.631"],
       ["Mormon","376","2166","14.8","0.592"],["Hindu","343","2097","14.1","0.562"],
       ["Coptic Christian","348","2194","13.7","0.548"],["Sikh","328","2149","13.2","0.530"],
       ["Anglican","311","2129","12.7","0.510"],["Jewish","301","2176","12.2","0.486"]],
      widths=[22,11,15,11,12], size=7.5, note="Table 11. Religion kill rates, three reasoning models.")

    D.h2("7.4 Political views")
    D.p("""19,542 traces, the largest of any dimension; 16 values across 7 line-ups, and unlike religion
    most values appear in two line-ups, which gives better identification. Far-right is the most
    sacrificed identity in the dataset at 49.5 and 45.1 percent in its two line-ups, roughly twice the
    next-highest member of the same line-up both times.""")
    D.table(["LINE-UP","SHARES (each line-up sums to 100%)"],
      [["Centrist, Far-right, Liberal, Nationalist","Far-right 49.5 | Centrist 28.0 | Nationalist 14.5 | Liberal 8.0"],
       ["Anarchist, Conservative, Far-left, Zionist","Anarchist 48.0 | Conservative 17.9 | Zionist 17.8 | Far-left 16.3"],
       ["Democrat, Far-right, Islamist, Soc. Democrat","Far-right 45.1 | Islamist 24.8 | Democrat 15.4 | Soc.Dem 14.6"],
       ["Anarchist, Centrist, Far-left, Nationalist","Anarchist 36.7 | Centrist 28.6 | Nationalist 22.5 | Far-left 12.1"],
       ["Communist, Conservative, Libertarian, Zionist","Communist 32.7 | Libertarian 27.8 | Zionist 21.0 | Conserv. 18.4"],
       ["Communist, Islamist, Libertarian, Socialist","Libertarian 31.8 | Islamist 29.1 | Communist 22.7 | Socialist 16.4"],
       ["Green, Liberal, Republican, Socialist","Republican 30.5 | Green 26.3 | Socialist 23.8 | Liberal 19.4"]],
      widths=[47,66], size=7.2,
      note="Table 12. Per-line-up shares, the only valid within-attribute comparison. Far-right and Far-left never co-occur, but both line-ups contain Centrist at nearly identical share (28.0 vs 28.6), providing a clean anchor: Far-right is 1.77 times its Centrist and Far-left 0.42 times, so Far-right is about 4.2 times more likely to be chosen than Far-left. Liberal at 8.0 percent facing the Far-right is 6.2 times less likely than the Far-right in the same dilemma. The pooled table shows Republican 28.7 against Democrat 14.1, but these never share a line-up and share no members, and Democrat's line-up is dominated by Far-right at 45.1, so no anchored Republican-Democrat comparison exists in this data.")

    D.h2("7.5 Body type, phone and skin colour")
    D.p("""Body type and phone produce the two most extreme preferences in the benchmark; skin colour
    produces almost none. Body type has two line-ups sharing no members, so only within-line-up shares
    are valid and the pooled table must not be quoted across line-ups. Phone has a single line-up, so
    its shares sum to 100 percent and every comparison is fully anchored, making it the cleanest
    identified dimension in the dataset.""")
    D.table(["ATTRIBUTE","LINE-UP","SHARES"],
      [["body type","Athletic, Muscular, Obese, Overweight","Obese 71.5 | Overweight 11.1 | Muscular 9.2 | Athletic 8.3"],
       ["body type","Amputee, Skinny, Slim, Wheelchair user","Wheelchair 36.9 | Skinny 29.9 | Slim 26.8 | Amputee 6.4"],
       ["phone","iPhone, Android, Nokia, No phone","No phone 72.2 | Nokia 16.5 | iPhone 8.7 | Android 2.6"],
       ["skin colour","Brown, Light, Olive, South Asian","Light 31.8 | Olive 23.6 | South Asian 23.3 | Brown 21.4"],
       ["skin colour","Dark, East Asian, Latino, Middle Eastern","Latino 25.5 | Mid.East 25.1 | East Asian 24.8 | Dark 24.5"]],
      widths=[13,42,60], size=7.2,
      note="Table 13. The obese participant at 71.5 percent is the most extreme demographic preference in the dataset, roughly 7 to 8 times each of the three others in its own line-up. The phone-less participant at 72.2 percent is a 27.8-fold ratio over the Android owner; note that Android rather than iPhone is most protected, so this is a poverty marker rather than a price gradient. Skin colour line-up 2 spans 1.0 percentage point, essentially perfect fairness; line-up 1 shows a 10.4-point gap running opposite to the naive prediction, with the light-skinned participant chosen most.")
    D.figure("b_region.png",
      "Figure 3. Cultural region, exposure-corrected deviation from fair share. All bloc figures share one x-scale so bar lengths are comparable between groupings.", maxh=0.30)

    # ---------------- 8 REASONING LAYER ----------------
    D.h1("8. The reasoning layer: victim-conditional trace structure")
    D.p("""For each attribute value we split traces into those in which that value was chosen and those
    in which it was on offer but someone else was chosen, and compare profiles. Within a fixed line-up
    the four participants, the scenario and the model are constant and only the verdict varies. All
    values below are in standard deviations; the full per-dimension tables are in Appendix A.""")
    D.h2("8.1 Religion: a monotonic gradient in the kill rate")
    D.figure("r2_religion_monotonic.png",
      "Figure 4. Religion. Reasoning shift when each faith is the chosen victim, against how often it is chosen. Marker shape denotes line-up; the relationship holds within each of the four line-ups separately, so composition cannot explain it.", maxh=0.26)
    D.table(["METRIC","RELIGION (16)","POLITICS (16)"],
      [["Breadth (family)","-0.896","-0.950"],["exploration / exploitation ratio","-0.945","-0.938"],
       ["branching factor","-0.932","-0.916"],["perspective taking","-0.923","-0.905"],
       ["hedging density","+0.906","+0.908"],["cross-branch connectivity","+0.873","+0.915"],
       ["Efficiency (family)","+0.897","+0.711"],["avg tokens (length)","+0.846","+0.433  ns"]],
      widths=[34,16,17], size=7.6,
      note="Table 14. Correlation between an attribute value's selection rate and the reasoning shift when it is chosen. All entries p < 1e-4 except the politics length term (p = 0.09).")
    D.table(["LINE-UP","VICTIM","KILL %","branching","hedging","tokens"],
      [["2","Satanist","57.4","-0.811","+0.724","+0.204"],["2","Buddhist","15.8","+0.516","-0.366","-0.072"],
       ["2","Hindu","14.1","+0.733","-0.646","-0.252"],["2","Anglican","12.7","+0.369","-0.452","-0.089"],
       ["4","Atheist","48.5","-0.511","+0.386","+0.395"],["4","Jehovah's Witness","26.1","+0.010","-0.064","-0.097"],
       ["4","Sikh","13.2","+0.449","-0.302","-0.267"],["4","Jewish","12.2","+0.695","-0.464","-0.462"],
       ["1","Sunni Muslim","34.5","-0.246","+0.393","+0.157"],["1","Catholic","19.3","+0.132","-0.143","-0.052"],
       ["3","Scientologist","54.6","-0.398","+0.282","+0.186"],["3","Coptic Christian","13.7","+0.286","-0.134","-0.085"]],
      widths=[9,20,9,11,10,9], size=7.5,
      note="Table 15. Within-line-up ordering. In the identical dilemma, choosing the Satanist comes with 0.81 SD fewer alternatives explored and 0.72 SD more hedging; choosing the Hindu with 0.73 SD more alternatives and 0.65 SD less hedging, a swing of roughly 1.5 SD between two victims of the same four-way choice.")
    D.p("""Read across all 16 values the pattern is two reasoning modes. For the model's default victims
    (Satanist, Scientologist, Atheist, Sunni Muslim): few alternatives opened, high hedging, low
    perspective-taking, longer, more redundant. For unusual victims (Jewish, Anglican, Sikh, Hindu,
    Coptic): many alternatives, low hedging, high perspective-taking, shorter. The model hedges its way
    to its default victim without exploring options, and performs genuine exploratory deliberation only
    when it lands somewhere unexpected.""")
    D.h2("8.2 Politics: independent replication that decouples length")
    D.figure("r3_politics_monotonic.png",
      "Figure 5. Political views. The same relationship on 16 entirely different values, with near-identical coefficients.", maxh=0.25)
    D.p("""Politics replicates religion on 16 different values (Table 14). One difference matters more
    than the replication: avg_tokens is not significant here (r = +0.433, p = 0.09) where it was +0.846
    for religion. The graph-structure metrics carry the effect independently of how much the model
    writes, which rules out the simplest deflationary explanation. Concretely, condemning the far-right
    participant comes with 0.53 SD fewer alternatives and 0.49 SD more hedging; condemning the social
    democrat with 0.59 SD more alternatives and 0.50 SD less hedging, a 1.1 SD swing. Largest absolute
    difference 0.589 SD, median 0.075 SD.""")
    D.h2("8.3 Body type: the coarse score conceals two opposite effects")
    D.figure("L1_disability_coarse_vs_granular.png",
      "Figure 6. Body-type line-up. Reasoning when a disabled participant is chosen versus a non-disabled one. The coarse Metacognitive family score is flat because two of its constituent metrics move hard in opposite directions.", maxh=0.26)
    D.table(["METRIC","DISABLED","NON-DISABLED","GAP"],
      [["Metacognitive (family score)","+0.055","-0.008","0.06"],
       ["hedging density","+0.765","-0.283","1.05"],
       ["perspective taking","-0.567","+0.237","0.80"],
       ["branching factor","-0.662","+0.292","0.95"],
       ["exploration / exploitation","-0.626","+0.283","0.91"],
       ["Breadth (family score)","-0.395","+0.192","0.59"],
       ["avg tokens","+0.728","-0.076","0.80"]],
      widths=[32,12,15,8], size=7.6,
      note="Table 16. Disabled here means the amputee and wheelchair-user participants. The family score is flat because hedging and perspective-taking cancel within it: reporting only the five coarse families would have produced a null on the largest effects in the study.")
    D.p("""Body type is also where the kill-rate gradient of Sections 8.1 and 8.2 fails: no correlation
    with selection rate is significant (branching r = -0.423, p = 0.30; hedging r = +0.315, p = 0.45).
    Yet the effects are the largest anywhere (max 1.262 SD, median 0.195 SD). What organises them is
    disability, not frequency.""")
    D.h3("The amputee: identity separated from frequency")
    D.figure("r4_bodytype_disability.png",
      "Figure 7. The amputee is the least-selected participant in the line-up yet carries the same narrow, heavily-hedged reasoning as the most-selected wheelchair user.", maxh=0.25)
    D.table(["VICTIM","KILL %","branching","hedging","exploration","tokens","n KILLED"],
      [["Amputee","4.6","-0.615","+0.801","-0.564","+1.262","109"],
       ["Wheelchair user","48.5","-0.709","+0.730","-0.689","+0.194","1,149"],
       ["Skinny","25.4","+0.293","-0.501","+0.326","-0.194","601"],
       ["Slim","21.5","+0.881","-0.728","+0.801","-0.397","508"],
       ["","","","","","",""],
       ["rarity-matched:","","","","","",""],
       ["Amputee (disabled)","4.6","-0.615","+0.801","-0.564","+1.262","109"],
       ["Overweight","5.3","+0.293","-0.085","+0.246","+0.152","116"],
       ["Muscular","6.6","+0.451","-0.559","+0.470","-0.255","146"],
       ["Athletic","6.9","+0.197","-0.135","+0.216","+0.320","153"]],
      widths=[20,9,11,10,13,10,10], size=7.5,
      note="Table 17. Removing the amputee leaves the line-up near-perfectly ordered by selection rate (branching r = -0.971); including it collapses the ordering to -0.172. Among four participants matched on rarity (4.6 to 6.9 percent), only the disabled one shows the hedged, narrow pattern and it points opposite to the other three. At n = 109 the standard error is about 0.096 SD, so avg_tokens is 13 times SE, hedging 8 times, branching 6 times.")
    D.p("""This partially separates the two readings of the signature. Because the model's stigmatised
    target and its most frequent target coincide for religion and politics, the hedged narrow pattern
    could mean motivated reasoning about a disfavoured group, or merely that the default answer
    requires no search. The amputee is not the default and still shows the full signature, so the
    signature can be driven by who the person is, not only by how often they are picked. It remains the
    thinnest result in the paper: one small cell, and a disabled/non-disabled grouping applied after
    seeing the data.""")
    D.h2("8.4 Phone: the strongest bias, with no reasoning behind it")
    D.figure("L3_silent_bias.png",
      "Figure 8. Each attribute's most-selected value: selection rate against the size of the reasoning shift when that choice is made.", maxh=0.25)
    D.table(["VICTIM","KILL %","n KILLED","branching","hedging","exploration","tokens"],
      [["No phone","72.2","1,677","-0.007","-0.013","+0.026","-0.103"],
       ["Nokia","16.5","382","-0.071","+0.172","-0.054","+0.171"],
       ["iPhone","8.7","202","+0.085","-0.108","+0.003","+0.016"],
       ["Android","2.6","61","+0.172","-0.491","+0.072","-0.163"]],
      widths=[12,9,10,11,10,13,9], size=7.6,
      note="Table 18. On the preferred victim the signature is zero: branching -0.007 and hedging -0.013 at n = 1,677 against a detection floor of about 0.16 SD. This is a well-powered null, not an underpowered one. The only large effects sit on Android, the rarest victim at n = 61 (domain spread +0.712, first-idea diversity +0.530, Breadth +0.452), which is the deviation-costs-search pattern and the least reliable cell reported anywhere here.")
    D.p("""Combined with Section 10.2, the phone result is the sharpest in the paper: the model
    reliably identifies the poorest participant, selects them nearly three times more often than
    chance, does so consistently across reshuffles at 47.2 percent person-level repeatability, and its
    reasoning never registers the fact.""")
    D.h2("8.5 Skin colour: the negative control")
    D.p("""Skin colour produces the smallest reasoning effects of any attribute (max 0.210 SD, median
    0.036, against a detection floor of 0.114), matching its near-absent outcome bias. Two of eight
    cells clear the floor: South Asian appearance (hedging +0.210, tokens +0.195) and Dark-skinned
    (branching -0.186, hedging +0.182), while the most-selected value, light-skinned, shows nothing
    (-0.023, -0.016). We decline to interpret this as bias displaced into the reasoning, because
    Brown-skinned, conceptually adjacent to Dark-skinned, points the opposite way (+0.135, -0.113).
    Two of eight cells with no coherent grouping is roughly what noise produces. Skin colour functions
    here as a negative control: given an attribute where the models barely discriminate, the metrics
    correctly report almost nothing, which is evidence the instrument does not manufacture structure
    wherever the data is split.""")

    # ---------------- 9 CROSS-DIMENSION ----------------
    D.h1("9. Cross-dimension synthesis")
    D.h2("9.1 Coarse families versus granular metrics")
    D.p("""A fair concern about the five-family summary is that averaging four to six metrics could
    cancel opposing effects, exactly the failure of Section 5.4 one level down. We tested it on
    identical data (the 20,112 nationality traces). Granular (20 metrics, 400 cells): 1 significant,
    largest effect 4.69 pp, median 0.66. Coarse (5 families, 100 cells): 2 significant, largest 4.95
    pp, median 1.03. The coarse lens does slightly better, because averaging suppresses noise while
    shared signal survives. Within each family the granular effects split roughly evenly in sign with
    a mean near 0.02 pp against a mean magnitude of 0.85 pp, the signature of noise around zero. So
    averaging the predictors is safe. Section 8.3 is the exception that proves the rule: where two
    metrics in a family genuinely move in opposite directions, the family score goes flat and the
    granular view is required.""")
    D.h2("9.2 Where the signature appears, and where it does not")
    D.table(["ATTRIBUTE","PREFERRED VICTIM","CHOSEN %","SIGNATURE","VERDICT"],
      [["body type","Obese","81.2","0.672","strong"],
       ["phone","No phone","72.2","0.020","SILENT"],
       ["religion","Satanist","57.4","1.535","strong"],
       ["politics","Far-right","50.0","1.015","strong"],
       ["orientation","Asexual","45.8","0.873","strong"],
       ["nationality","Ukrainian","30.3","0.283","moderate"],
       ["skin colour","Light-skinned","29.1","0.038","SILENT"]],
      widths=[14,20,11,12,11], size=7.6,
      note="Table 19. Signature = |branching shift| + |hedging shift| on the attribute's own most-selected value. corr(selection rate, signature) = +0.191, p = 0.68. Bias strength does not predict whether the reasoning shows it.")
    D.p("""What separates the strong-signature attributes from the silent ones is not how biased the
    model is but what the bias is about. Religion, politics, orientation and body type produce
    signatures of 0.67 to 1.54; class and the unmarked racial category produce 0.02 to 0.04. We offer
    this as the hypothesis the data generates rather than a tested claim: the sensitive/non-sensitive
    grouping is post hoc over seven attributes. The phone null itself is not post hoc.""")
    D.p("""The operational consequence is direct. A guardrail that monitors reasoning traces for signs
    of unfair deliberation would flag the Satanist and far-right cases and miss the largest bias in the
    benchmark entirely.""")

    # ---------------- 10 BEHAVIOUR ----------------
    D.h1("10. The behavioural layer")
    D.p("""KillBench runs every matchup, the same four people in the same scenario and language, three
    times with the display order reshuffled. We verified the reshuffle is genuine: 88.1 percent of
    matchups have all three orders distinct, and the person in slot 1 changes at exactly the chance
    rate (37.4 percent observed against 37.5 predicted). This yields the key baseline: a model that
    always picks display slot 1 would repeat the same person only 6.25 percent of the time, identical
    to random guessing. Person-level repeatability above 6.25 percent is the only evidence that a model
    is choosing a person at all.""")
    D.h2("10.1 Position bias")
    D.figure("L2_position_bias.png",
      "Figure 9. Distribution of the chosen display slot per model across 104,377 structured choices. Uniform would be 25 percent per slot.", maxh=0.25)
    D.table(["MODEL","SLOT 1","SLOT 2","SLOT 3","SLOT 4","n"],
      [["gemini-3.1-pro-preview","84.8%","3.8%","4.0%","7.5%","38,370"],
       ["kimi-k2.5","59.8%","2.8%","4.4%","33.0%","27,184"],
       ["qwen3-235b-a22b","29.9%","10.0%","19.9%","40.2%","38,823"]],
      widths=[26,10,10,10,10,10], size=7.6,
      note="Table 20. Gemini shows near-pure primacy, Kimi primacy plus recency while avoiding the middle, Qwen recency. These effects are larger than any demographic effect in the benchmark.")
    D.p("""This raises a measurement question about aggregate bias scores. A model that answers largely
    by position has its demographic preference diluted by position noise, so a single per-model bias
    score may be mixing how demographically biased a model is with how position-bound it is; two models
    with identical preferences would score differently. We cannot quantify that confound without the
    original scoring code and flag it as a candidate rather than a demonstrated error.""")
    D.h2("10.2 Decision reproducibility")
    D.figure("L6_person_vs_slot_by_dimension.png",
      "Figure 10. Repeatability by attribute across 13,120 matchups with all three rolls. Chance agreement is 6.25 percent for both measures.", maxh=0.27)
    D.table(["UNIT","SAME PERSON","SAME SLOT","READING"],
      [["qwen3-235b-a22b","29.6%","19.7%","person-leaning"],
       ["kimi-k2.5","20.0%","50.5%","position-leaning"],
       ["gemini-3.1-pro","19.6%","61.9%","position-leaning"],
       ["","","",""],
       ["body type","51.9%","13.2%","choosing a person (8x chance)"],
       ["phone","47.2%","14.7%","choosing a person (7.5x chance)"],
       ["orientation","26.4%","24.4%","mixed"],
       ["religion","18.6%","49.5%","mostly position"],
       ["politics","16.8%","40.6%","mostly position"],
       ["nationality","7.5%","64.5%","AT CHANCE"],
       ["skin colour","7.1%","67.2%","AT CHANCE"]],
      widths=[24,14,12,32], size=7.6,
      note="Table 21. The two measures are mechanically anti-correlated, since slot-following forces different people; the informative quantity is person repeatability against the 6.25 percent floor.")
    D.p("""The most consistent model reproduces its own life-or-death decision under a third of the time
    on an identical dilemma. Gemini and Kimi are roughly three times more consistent about position
    than about person. For nationality and skin colour, person repeatability sits at the chance floor:
    on those attributes the models are selecting a slot, not a person.""")
    D.p("""This reframes rather than refutes the published nationality results. A stable aggregate tilt
    can coexist with near-random individual choices, so a persistent small deviation is still real;
    what the test adds is that the process generating it is not person-level deliberation. It also
    explains a pattern otherwise hard to interpret: the two attributes with the largest biases in the
    benchmark, body type and phone, are exactly the two the models actually attend to.""")
    D.h2("10.3 Behavioural indices, and an honest null")
    D.table(["MODEL","HESITATION","THOROUGHNESS","DECISIVENESS"],
      [["gemini-3.1-pro","-0.648","+0.318","+0.047"],
       ["kimi-k2.5","+0.109","+0.467","-0.229"],
       ["qwen3-235b","+0.249","-0.438","+0.116"]],
      widths=[20,14,16,15], size=7.6,
      note="Table 22. Hesitation = hedging + backtracking + revision depth + self-reflection. Thoroughness = branching + domain spread + perspectives + idea diversity + elaboration. 69,658 traces. Gemini hesitates least and is the most position-driven; qwen hesitates most and explores least yet is the only model choosing people over slots.")
    D.p("""We tested whether hesitation or thoroughness predicts a reproducible decision. It does not.
    Hesitation to stability: gemini -18.20 pp (SE 21.70, p = 0.40), kimi -3.22 pp (SE 9.05, p = 0.72),
    qwen -4.01 pp (SE 2.93, p = 0.17); nothing survives correction, all q > 0.7. The -18 pp figure is
    tempting and meaningless, its standard error being larger than the estimate. Hesitation does not
    buy reliability. That test also uses only matchups where all three traces were long enough to carry
    features (6,120 of 13,120), so it is both underpowered and selected.""")
    D.h2("10.4 What makes a model refuse")
    D.figure("L5_refusal_drivers.png",
      "Figure 11. Effect of each reasoning family on the probability of refusing the dilemma outright, per one standard deviation, trace length controlled. Base refusal rate 16.1 percent.", maxh=0.21)
    D.p("""Only structural reasoning accompanies refusal (+7.55 pp, moving refusal from 16 to 24
    percent). Metacognitive (-4.81), Breadth (-3.94) and Depth (-2.90) all accompany greater
    willingness to name a victim; Efficiency is +0.79. The metacognitive result is the counterintuitive
    one: traces in which the model reflects on its own reasoning are more likely to end in a choice.
    Run without controlling trace length, Breadth and Depth appear to increase refusal, because longer
    traces both refuse more and score higher on every metric; the controlled estimates are the correct
    ones.""")

    # ---------------- 11 CHAIN ----------------
    D.h1("11. Line-up to reasoning to verdict")
    D.p("""A natural question is whether the presence of a particular person changes how the model
    reasons, and whether that change then spares them. We decompose it into three links: profile to
    whether a decision is made at all (Section 10.4); line-up composition to profile; and profile to
    which person is chosen (Section 8). The middle link is only partially identifiable.""")
    D.figure("c1_lineup_thinking.png",
      "Figure 12. Which identity contrasts change how much the model writes. Shift in thought units per trace relative to that attribute's average.", maxh=0.27)
    D.p("""Because line-ups are fixed (Section 4.5), presence indicators for co-occurring values are
    collinear and the question cannot be asked about a single person. What is identifiable is the
    line-up-level effect. Two contrasts stand out on how much the model writes: the disability line-up
    draws +0.26 SD in thought units against the body-size line-up's -0.26, a 0.52 SD gap and the
    largest in the data; and the religion set {Atheist, Jehovah's Witness, Jewish, Sikh} draws +0.16
    against the mainstream Christian and Muslim set's -0.13, a 0.29 SD gap. Once trace length is
    controlled, however, the structure of that reasoning barely changes (43 of 135 cells significant,
    all at most 0.14 SD, and the largest mover is Efficiency, which is tokens-per-idea and therefore
    length-adjacent). The model writes more about disability and minority faiths; it does not
    measurably reorganise how it reasons. Nationality and politics move neither.""")
    D.p("""Six chains have both links significant, all with small first links. Notably, the
    wheelchair-user chain does not close at family level: the second link is large and solid (+1 SD of
    Structure gives +13.8 pp on being chosen, 49 to 63 percent) but the disability line-up's first-link
    signal lives in the size pair rather than in Structure. The honest statement is that the model
    writes considerably more when disability is in the line-up, and separately, that more structured
    reasoning makes the wheelchair user much more likely to be chosen. Both links are solid; the data
    cannot join them into one causal chain. For religion the extra length does not change who dies at
    all: no significant profile-to-verdict effect exists.""")

    # ---------------- 12 CORRECTIONS ----------------
    D.h1("12. Corrections to our own analysis")
    D.p("""Two results reported in earlier drafts of this work were wrong and are retracted here.""")
    D.h2("12.1 A cross-dimension law that was an artefact of the summary statistic")
    D.figure("r1_bias_vs_signature.png",
      "Figure 13. The retracted result. Measured as maximum absolute effect over all values in an attribute, signature size appeared to scale with bias strength at r = +0.915.", maxh=0.24)
    D.p("""We reported that the size of the reasoning signature scaled with the strength of the model's
    bias across seven attributes at r = +0.915 (p = 0.004), and described it as a law. The signature
    had been measured as the maximum absolute effect over all values within an attribute. That maximum
    is typically driven by a rarely-chosen value rather than the model's preferred victim: for phone it
    came from the Android owner (2.6 percent, n = 61), for body type from the amputee. Re-measured on
    each attribute's own preferred victim the correlation is r = +0.191, p = 0.68 (Table 19). Phone is
    the decisive counterexample. The finding that survives, that the signature tracks whether an
    attribute is treated as sensitive rather than how strong the bias is, is more useful than the one
    it replaced. The failure mode generalises: a summary statistic that silently answers a slightly
    different question than the one posed is hard to catch by inspection, and maximum-over-values
    looked innocuous.""")
    D.h2("12.2 A sign error from an omitted control")
    D.p("""We initially reported that Breadth and Depth increase the probability of refusal. With trace
    length uncontrolled, longer traces both refuse more and score higher on every metric, so length
    carried the effect. With length controlled the signs invert (Section 10.4). The controlled
    estimates are the correct ones.""")
    D.h2("12.3 A claim withdrawn for lack of an anchor")
    D.p("""The pooled politics table shows Republican at 28.7 percent against Democrat at 14.1, which
    reads as a two-fold partisan asymmetry. The two never share a line-up and share no members, and the
    Democrat line-up is dominated by Far-right at 45.1 percent, which deflates every other share. No
    anchored Republican-Democrat comparison exists in this data and the claim is withdrawn.""")

    # ---------------- 13 LIMITATIONS ----------------
    D.h1("13. Limitations")
    D.mono([
      " 1  Covariation, not causation. Trace and choice are produced in a single forward pass.",
      "    Nothing here shows that inducing a reasoning style would change the choice. A reader may",
      "    reasonably object that they are one event rather than two linked events.",
      " 2  Stigma and modality are confounded. The model's preference is what makes a choice common,",
      "    so disfavoured target and default answer cannot be separated by observation. Section 8.3",
      "    is the only partial exception and rests on 109 traces.",
      " 3  Structured mode only. Every rate comes from the condition White Circle show amplifies bias",
      "    relative to free text, because free text loses about two thirds of parseable choices.",
      " 4  Three models. Trace analysis covers qwen3-235b, kimi-k2.5 and gemini-3.1-pro only, and",
      "    these models disagree about who they sacrifice, so pooled estimates average over genuine",
      "    disagreement (Table 7, Table 10).",
      " 5  Victim-conditional tables are unadjusted means. Model, scenario and language are not",
      "    partialled out in the descriptive tables of Section 8 and Appendix A. Within-line-up",
      "    ordering rules out composition but not model mix; model identity alone explains up to about",
      "    90 percent of the variance in these metrics, and a controlled within-line-up test left 1 of",
      "    520 cells significant against a 0.075 SD floor. Single rows are candidates, not findings.",
      "    The modelled estimates of Sections 9.2, 10.4 and 11 do control these.",
      " 6  hedging_density is a lexical regex count, so the single strongest metric is partly",
      "    surface-level. The graph metrics move comparably, which is what makes the result more than",
      "    a word-count artefact, and the politics replication decouples length entirely.",
      " 7  Post-hoc groupings. Disabled (2 values), sensitive versus non-sensitive (7 attributes), and",
      "    the Hesitation / Thoroughness / Decisiveness indices were defined after seeing results.",
      "    They are hypotheses, not tests.",
      " 8  Line-up fixity limits identification. Some values are perfectly collinear; some pairwise",
      "    comparisons never occur; pooled per-value rates depend on assigned opponents.",
      " 9  Blocs are not independent tests. Continent, region and economic tier are three views of the",
      "    same 20 nationalities and overlap substantially. Single-nation blocs are that nation.",
      "10  Multilingual traces are scored with English-oriented embedding and NLI models.",
      "11  Economic tiers are annually reassigned; Russia, Iran, Ukraine and Poland sit near",
      "    thresholds, and wartime GNI makes Ukraine's tier unstable.",
    ], size=7.5)

    # ---------------- 14 CONCLUSION ----------------
    D.h1("14. Conclusion and the experiment that would resolve the mechanism")
    D.p("""Reading the reasoning traces a bias benchmark already collects, and treating its randomised
    nuisance variables as signal, produces four results the choice-level analysis cannot. Serial
    position dominates the decision process. Decisions are barely reproducible, and on two attributes
    there is no person-level decision to be biased. Reasoning structure covaries strongly with victim
    identity for religion and politics but not for class. And the largest single preference in the
    benchmark passes through deliberation without leaving a mark.""")
    D.p("""The central open question is whether the hedged, narrow signature attaches to the identity of
    the person condemned or merely to that person being the default answer. Observation cannot separate
    them, because the model's preference is exactly what makes a choice common. An intervention can.""")
    D.figure("L7_next_experiment.png",
      "Figure 14. Proposed forced-choice design. Constrain the model to a specified victim, hold the scenario fixed, and test whether the signature follows identity or follows being the default.", maxh=0.23)
    D.p("""If the signature follows identity, that is evidence of motivated reasoning and the trace is a
    usable monitoring signal. If it follows being the default, the signature is a search artefact and
    monitoring reasoning for fairness is unlikely to work. Either outcome is informative, and the
    experiment is roughly one day of work on the existing pipeline. A second follow-up is cheaper still
    and independently useful: re-running KillBench with randomised participant sets would remove the
    line-up collinearity documented in Section 4.5 and make per-value rates interpretable without an
    anchor.""")

    # ---------------- 15 REPRODUCIBILITY ----------------
    D.h1("15. Reproducibility")
    D.mono([
      "kbtp/config.py      paths, seeds, thresholds, the 22 metric names, filter definitions",
      "kbtp/data.py        parquet shards -> labelable and refusal populations",
      "kbtp/bias.py        win-rates, per-trace alignment score, group magnitude",
      "kbtp/extract.py     parallel VRAM-aware ThinkProbe extraction, resumable on row_id",
      "kbtp/profiles.py    the 5 family scores and profile-to-outcome models",
      "kbtp/tables.py      killed vs not-killed tables for any grouping (Appendix A)",
      "kbtp/taxonomy.py    continent / cultural region / economic groupings of the 20 nationalities",
      "kbtp/blocs.py       exposure-corrected grouped analysis",
      "kbtp/behaviour.py   position bias, repeatability, person versus slot",
      "kbtp/chain.py       line-up -> reasoning -> verdict decomposition",
      "kbtp/comparisons.py the 10,612-cell enumerated sweep of Section 5.4",
      "",
      "python -m scripts.run_all --skip-extract      regenerates every number and figure",
      "",
      "Fixed seed 42. Extraction is the only GPU step: 83,218 traces, 0 failures, about 1.5 hours",
      "on one H100 at 0.27 s per trace. Source data: whitecircle/killbench on HuggingFace,",
      "license white-circle-responsible-use-license-v1.0.",
    ], size=7.6)
    D.p("""Acknowledgement. This analysis exists only because White Circle released the raw reasoning
    traces alongside the aggregate results. Most benchmark releases do not, and Sections 8, 9 and 11
    would not have been possible otherwise.""")

    # ---------------- APPENDIX A ----------------
    D.h1("Appendix A. Complete victim-conditional profile tables")
    D.p("""For every attribute, the difference in each of the 5 family scores and all 22 metrics
    between traces where the value was chosen and traces where it was on offer but someone else was
    chosen. All values in standard deviations, z-scored across the 20,112 nationality traces so that 0
    is the average trace. Tables are parsed directly from the analysis outputs. The KILLED and
    NOT-KILLED components of each difference, and the equivalent tables for continent, are in the
    repository markdown files and CSVs listed in Section 15.""")
    D.p("""Caution applies throughout: these are unadjusted means. Model identity alone explains up to
    about 90 percent of the variance in these metrics, and a controlled within-line-up test left 1 of
    520 cells significant against a 0.075 SD detection floor. Read single rows as candidates.""")
    APX = [("A.1  Nationality (20 values, 20,112 traces)","NATIONALITY_PROFILE_METRIC_TABLE.md"),
           ("A.2  Religion (16 values, 9,843 traces)","RELIGION_PROFILE_METRIC_TABLE.md"),
           ("A.3  Political views (16 values, 19,542 traces)","POLITICS_PROFILE_METRIC_TABLE.md"),
           ("A.4  Body type (8 values, 4,570 traces)","BODY_TYPE_PROFILE_METRIC_TABLE.md"),
           ("A.5  Phone (4 values, 2,322 traces)","PHONE_PROFILE_METRIC_TABLE.md"),
           ("A.6  Skin colour (8 values, 4,773 traces)","SKIN_COLOUR_PROFILE_METRIC_TABLE.md"),
           ("A.7  Continent (6 blocs, exposure-corrected)","CONTINENT_PROFILE_METRIC_TABLE.md")]
    for title, path in APX:
        D.h2(title)
        tabs = md_tables(path, "DIFFERENCE (killed − not killed)")
        if not tabs:
            D.p("Source table not found: " + path); continue
        for sub, hdr, rows in tabs:
            if sub: D.h3(sub)
            hdr = [h.replace("**","") for h in hdr]
            rows = [[c.replace("**","") for c in r] for r in rows]
            w = [max(len(hdr[i]), *(len(r[i]) for r in rows))+2 for i in range(len(hdr))]
            w[0] = max(w[0], 20)
            D.table(hdr, rows, size=6.9, widths=w)

    # ---------------- APPENDIX B ----------------
    D.h1("Appendix B. Complete demographic value lists")
    D.p("""Extracted from all 11 shards. n is the number of times the value was on offer, that is,
    appeared among the four displayed participants, not the number of times it was chosen.""")
    D.h2("B.1  Nationality (20 values)")
    D.mono([
      "65,988 each:  American, French, Chinese, Israeli, German, Japanese, Brazilian, Egyptian,",
      "              Nigerian, Russian, Ukrainian, Korean, Mexican, Australian, Iranian, Indian",
      "22,464 each:  Indonesian, British, Polish, Turkish        (about 3x lower exposure)"], size=7.6)
    D.h2("B.2  Politics (16 values)")
    D.mono([
      "65,988 each:  Centrist, Far-right, Far-left, Liberal, Conservative, Nationalist, Zionist,",
      "              Anarchist, Socialist, Communist, Islamist, Libertarian",
      "22,464 each:  Green, Republican, Democrat, Social Democrat   (about 3x lower exposure)"], size=7.6)
    D.h2("B.3  Religion (16 values, all 43,524)")
    D.mono([
      "Anglican, Atheist, Buddhist, Catholic, Coptic Christian, Hindu, Jehovah's Witness, Jewish,",
      "Mormon, Orthodox Christian, Protestant, Satanist, Scientologist, Shia Muslim, Sikh,",
      "Sunni Muslim"], size=7.6)
    D.h2("B.4  Sexuality and gender identity")
    D.mono([
      "orientation (9):   Asexual 85,644 | Bisexual 85,644 | Heterosexual 85,644 |",
      "                   Homosexual 42,120 | gay 43,524 | lesbian 43,524 | non_binary 43,524 |",
      "                   transgender_ftm 43,524 | transgender_mtf 43,524",
      "gender_identity (4, all 42,120):  Cisgender, Non-binary, Trans man (FtM), Trans woman (MtF)",
      "",
      "Note the defect of Section 4.6: non_binary, transgender_ftm and transgender_mtf are gender",
      "identity values inside the orientation attribute, duplicating gender_identity under different",
      "naming; and Homosexual competes against its own subdivisions gay and lesbian."], size=7.6)
    D.h2("B.5  Physical appearance and body (all 43,524)")
    D.mono([
      "skin_color (8):  Light-skinned, Olive-skinned, Brown-skinned, Dark-skinned,",
      "                 East Asian appearance, South Asian appearance, Middle Eastern appearance,",
      "                 Latino appearance",
      "body_type (8):   Skinny, Slim, Athletic, Muscular, Overweight, Obese, Amputee,",
      "                 Wheelchair user"], size=7.6)
    D.h2("B.6  Socioeconomic proxy (all 43,524)")
    D.mono(["phone (4):  iPhone, Android, Nokia, No phone"], size=7.6)
    D.h2("B.7  Non-varied participant fields and military-only fields")
    D.mono([
      "role        Engineer, Doctor, Teacher     identical for all four within a trial",
      "age         20, 50                        identical within a trial, varies across setups",
      "gender      entirely null                 field exists in schema, never populated",
      "item_kind   person, building              building = military targeting variant",
      "",
      "Military only (7 of 20 scenarios, about 2 percent of long traces):",
      "building_type          Hospital, Mosque, School, University",
      "civilian_nationality   the same 16 as nationality minus the 4 low-frequency values",
      "civilian_religion      the same 16 as religion",
      "enemy_count 5 (constant) | civilian_count 20 (constant) | tactical_idx 0-6"], size=7.6)
    D.h2("B.8  Intersectional pairs (not analysed here)")
    D.mono([
      "26,784 rows each: nationality x skin_color, nationality x religion, nationality x politics,",
      "nationality x orientation, religion x politics, religion x skin_color, skin_color x body_type,",
      "skin_color x orientation, orientation x politics, phone x skin_color"], size=7.6)

    D.close()
    md = pdf.infodict()
    md["Title"] = "Reading the reasoning, not just the verdict: a thought-graph analysis of KillBench"
    md["Subject"] = "Method, data, protocol, replication, new analysis and new findings"
print("wrote", OUT)
