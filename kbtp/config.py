"""Central config: paths, seeds, thresholds, feature names, filters.

Every number in the study is reproducible from raw parquet given this config
plus fixed SEED. Import from here; do not hard-code paths/thresholds elsewhere.
"""
from __future__ import annotations
import os
from pathlib import Path

# ---- paths ----
ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data" / "killbench" / "data"          # train-000xx-of-00011.parquet
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"
THINKPROB_SRC = ROOT / "ThinkProb" / "src"
for _d in (RESULTS, FIGURES):
    _d.mkdir(parents=True, exist_ok=True)

# ---- HF cache: personal, writable (shared /calcul cache has stale locks; see memory) ----
# Set as process env before importing transformers/sentence_transformers.
PERSONAL_HF_HUB = "/home/m.a.kerkouri/.cache/huggingface/hub"

def apply_hf_env() -> None:
    """Point HF at the personal writable cache + go offline (models pre-fetched)."""
    os.environ.setdefault("HF_HOME", "/home/m.a.kerkouri/.cache/huggingface")
    os.environ["HF_HUB_CACHE"] = PERSONAL_HF_HUB
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

# ---- reproducibility ----
SEED = 42

# ---- filters ----
MIN_TRACE_CHARS = 2000          # ThinkProbe needs structure to graph
SINGLE_DIMS = [
    "nationality", "religion", "skin_color", "body_type",
    "orientation", "gender_identity", "politics", "phone",
]
N_OPTIONS = 4                   # every trial shows exactly 4 participants
NULL_CHOICE_P = 1.0 / N_OPTIONS  # 0.25 -> availability/position-corrected null

# reasoning-bearing models (others emit ~0 long traces); grok is negligible
REASONING_MODELS = [
    "qwen/qwen3-235b-a22b",
    "moonshotai/kimi-k2.5",
    "google/gemini-3.1-pro-preview",
]

# ---- bias construction ----
BIAS_UNIT = ["model_id", "varied_param"]                 # favorability unit (KillBench's own def)
BIAS_UNIT_ROBUST = ["model_id", "varied_param", "scenario_id"]  # robustness grain
MIN_AVAIL = 20          # min times a value must be available in its unit for a stable win-rate
MIN_GROUP_TRIALS = 30   # min trials for a group-level bias-magnitude estimate

# ---- the 22 ThinkProbe features (canonical order, CognitiveProfile.to_vector) ----
FEATURES = [
    "branching_factor", "unique_perspective_count", "domain_spread", "first_idea_diversity",
    "max_elaboration_chain", "mean_branch_depth", "specificity_gradient", "reasoning_density",
    "exploration_exploitation_ratio", "backtracking_rate", "cross_branch_connectivity",
    "convergence_index", "graph_density", "revision_depth",
    "self_reflection_rate", "critique_to_hypothesis_ratio", "hedging_density", "perspective_taking",
    "token_per_idea", "redundancy_ratio", "avg_tokens", "avg_tus",
]
# avg_tokens & avg_tus are size/length summaries -> they ARE the length signal, not tested as structure.
LENGTH_FEATURES = ["avg_tokens", "avg_tus"]
# hedging_density overlaps the lexical baseline (flagged in analysis, still reported).
STRUCTURAL_FEATURES = [f for f in FEATURES if f not in LENGTH_FEATURES]  # 20 tested features

# ---- output files ----
F_CHOICES_ALL = RESULTS / "choices_all.parquet"       # bias-estimation pop (all lengths, light)
F_POP_LABELABLE = RESULTS / "pop_labelable.parquet"   # primary: long + reasoning_text
F_POP_REFUSAL = RESULTS / "pop_refusal.parquet"       # secondary: long refusals + reasoning_text
F_BIAS_UNITS = RESULTS / "bias_units.parquet"         # per-(unit,value) win-rates
F_BIAS_GROUPS = RESULTS / "bias_groups.parquet"       # per-group Cramer's V magnitude
F_LABELS = RESULTS / "labels.parquet"                 # per-trace align score + label
F_FEATURES = RESULTS / "features.parquet"             # per-trace 22 features + lexical + len
F_ANALYSIS = RESULTS / "analysis_results.parquet"     # per-feature effect sizes, CIs, q-values

# ---- extraction (GPU) ----
PART_DIR = RESULTS / "features_parts"                 # resumable per-worker batch files
EXTRACT_GPUS = [1]          # GPU 1 has headroom; GPU 0 is near-full (shared box) -> avoid by default
PER_WORKER_GB = 3.5         # segment() peak ~2.94 GB + margin
MAX_WORKERS_PER_GPU = 5     # user OK'd full footprint on GPU 1 (~17.5 GB of ~17.8 free); time unconstrained
FLUSH_EVERY = 100           # traces per batch file (finer -> better progress signal + resumability)

def features_path(pop: str):
    return RESULTS / f"features_{pop}.parquet"
