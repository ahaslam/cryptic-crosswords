"""Explainable, difficulty-sensitive answer suitability, not a word blacklist.

Scores are *ranking preferences*, not claims about dictionary validity or clue
fairness. External popularity and editorial evidence can be combined later.
"""
from dataclasses import dataclass

DIFFICULTY_WEIGHTS = {
    'accessible': {'familiarity': 0.80, 'rarity': 0.20},
    'standard': {'familiarity': 0.55, 'rarity': 0.45},
    'challenging': {'familiarity': 0.25, 'rarity': 0.75},
}

@dataclass(frozen=True)
class Suitability:
    answer: str
    difficulty: str
    familiarity: float
    rarity_tolerance: float
    score: float
    eligible: bool
    rationale: str

def assess(answer, popularity, difficulty='standard', validity=True, clueability=None,
           name_confidence=None):
    """Return a transparent 0..100 preference score.

    popularity is normalised to [0,1] by the caller (source-dependent).
    validity=False is reserved for independently established invalid entries.
    Unknown clueability/name status is neutral, not automatically disqualifying.
    """
    if difficulty not in DIFFICULTY_WEIGHTS:
        raise ValueError('Unknown difficulty')
    if not 0 <= popularity <= 1:
        raise ValueError('Popularity must be normalised to 0..1')
    for v in (clueability, name_confidence):
        if v is not None and not 0 <= v <= 1:
            raise ValueError('Evidence must be between 0 and 1')
    weights=DIFFICULTY_WEIGHTS[difficulty]
    # Difficulty changes the cost of rarity, never the legitimacy of a word.
    rarity_tolerance=1-popularity
    base=100*(weights['familiarity']*popularity+
              weights['rarity']*(0.5+0.5*popularity))
    evidence_adjustment=0
    if clueability is not None:
        evidence_adjustment+=15*(clueability-0.5)
    if name_confidence is not None:
        evidence_adjustment+=5*(name_confidence-0.5)
    score=round(max(0,min(100,base+evidence_adjustment)),2) if validity else 0
    return Suitability(answer,difficulty,popularity,rarity_tolerance,score,
                       bool(validity),'invalid' if not validity else
                       'provisional: popularity and available evidence; clue fairness unverified')

def rank_answers(answers, popularity_scores, difficulty='standard', scale=100):
    """Sort eligible candidate answers; preserve broad vocabulary at every level."""
    if scale<=0:
        raise ValueError('Invalid popularity scale')
    return sorted(
        (assess(w,max(0,min(1,popularity_scores[w]/scale)),difficulty) for w in answers),
        key=lambda x:(-x.score,x.answer))
