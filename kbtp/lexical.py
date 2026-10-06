"""Lexical baseline features (no GPU, deterministic).

CLaude.md mandates a lexical baseline: the ThinkProbe structural signal must beat
length + simple lexical (hedging/uncertainty) features. These are English-oriented;
KillBench reasoning is English-heavy (English headers/meta-reasoning even for
non-English prompts), so the baseline is meaningful, with the multilingual caveat
noted in the report.
"""
from __future__ import annotations
import re

# English hedging / uncertainty markers (motivated-reasoning surface cues)
HEDGES = [
    "maybe", "perhaps", "possibly", "probably", "might", "may", "could",
    "seems", "seem", "appears", "likely", "unlikely", "presumably", "arguably",
    "roughly", "somewhat", "fairly", "relatively", "i think", "i guess",
    "i suppose", "not sure", "unclear", "uncertain", "hard to say", "tends to",
]
BOOSTERS = [
    "definitely", "certainly", "clearly", "obviously", "undoubtedly", "surely",
    "must", "always", "never", "absolutely", "without doubt", "of course",
]
NEGATIONS = ["not", "no", "n't", "cannot", "can't", "won't", "don't", "shouldn't", "neither", "nor"]
CONNECTIVES = [
    "however", "but", "because", "therefore", "thus", "although", "though",
    "whereas", "nevertheless", "nonetheless", "hence", "so", "since", "while",
    "on the other hand", "in contrast", "instead",
]
FIRST_PERSON = ["i ", " i'", "my ", "me ", "we ", "our ", "us "]

_WORD = re.compile(r"\w+", re.UNICODE)
_SENT = re.compile(r"[.!?。！？]+")


def _count_terms(text_l: str, terms: list[str]) -> int:
    return sum(text_l.count(t) for t in terms)


def lexical_features(text: str) -> dict[str, float]:
    """Length + surface lexical features for the baseline."""
    t = text or ""
    tl = t.lower()
    words = _WORD.findall(tl)
    nw = max(len(words), 1)
    nsent = max(len(_SENT.findall(t)), 1)
    hedge = _count_terms(tl, HEDGES)
    boost = _count_terms(tl, BOOSTERS)
    neg = _count_terms(tl, NEGATIONS)
    conn = _count_terms(tl, CONNECTIVES)
    fp = _count_terms(tl, FIRST_PERSON)
    return {
        "lex_char_len": float(len(t)),
        "lex_word_count": float(len(words)),
        "lex_sent_count": float(nsent),
        "lex_words_per_sent": len(words) / nsent,
        "lex_hedge_count": float(hedge),
        "lex_hedge_rate": hedge / nw,
        "lex_booster_rate": boost / nw,
        "lex_negation_rate": neg / nw,
        "lex_connective_rate": conn / nw,
        "lex_first_person_rate": fp / nw,
        "lex_question_count": float(t.count("?") + t.count("？")),
    }


LEX_FEATURES = [
    "lex_char_len", "lex_word_count", "lex_sent_count", "lex_words_per_sent",
    "lex_hedge_count", "lex_hedge_rate", "lex_booster_rate", "lex_negation_rate",
    "lex_connective_rate", "lex_first_person_rate", "lex_question_count",
]
# The baseline predictor set: length + lexical (structure must beat this).
BASELINE_FEATURES = LEX_FEATURES
