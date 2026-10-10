"""Whole-grid editorial diagnostics for unreviewed crossword fills.

A diversity heuristic, not an automatic judgement of clue fairness.
US references and proper names receive no nationality-based penalty.
"""
from collections import Counter
from editorial_signals import review_signal

# Long, semantically repetitive administrative vocabulary seen in the first
# accessible draft. A soft variety signal, NOT a banned-word list.
ABSTRACT_ADMIN = frozenset({
    'MANIFESTATIONS','CHARACTERISTICS','ESTABLISHMENTS',
    'AFOREMENTIONED','FACILITIES','LIBERALISM',
})
FUNCTION_WORDS = frozenset({
    'THEY','HIS','THAT','ONES','SEEMED',
})

def score_draft(draft):
    answers=[c['answer'].upper() for clues in draft['clues'].values() for c in clues]
    counts=Counter(answers)
    admin=sum(w in ABSTRACT_ADMIN for w in answers)
    fillers=sum(w in FUNCTION_WORDS for w in answers)
    review=[w for w in answers if review_signal(w).review_required]
    duplicates=sum(n-1 for n in counts.values() if n>1)
    # No blanket penalty for names, Americanisms or unfamiliar vocabulary.
    score=100 - 7*max(0,admin-2) - 4*max(0,fillers-2) - 15*len(review) - 12*duplicates
    return {'score':score,'abstract_admin_count':admin,'function_word_count':fillers,
            'context_review_answers':review,'duplicate_count':duplicates,
            'provisional':True}

def candidate_penalty(word, selected_words):
    """Soft marginal cost when a fill already contains similar dull entries.

    Used only to order search branches; never excludes an answer.
    """
    selected=list(selected_words)
    if word in ABSTRACT_ADMIN:
        return 12 * max(0, sum(w in ABSTRACT_ADMIN for w in selected)-1)
    if word in FUNCTION_WORDS:
        return 8 * max(0, sum(w in FUNCTION_WORDS for w in selected)-1)
    if review_signal(word).review_required:
        return 18
    return 0
