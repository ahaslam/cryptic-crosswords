"""Editorial review signals, not a dictionary blacklist.

These flags describe *how to review a proposed clue*, never whether an
American word, proper name, or abbreviation is inherently unacceptable.
A clue editor must verify context, wordplay and tone before publication.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class EditorialSignal:
    answer: str
    review_required: bool
    topics: tuple
    guidance: str

# Narrow, explicit examples discovered in a real draft. These are NOT
# general lexical filters; unknown names and US references remain eligible.
CONTEXT_REVIEW = {
    'NEGRO': ('historical_sensitive_usage',
              'Historically attested but dated and potentially offensive when referring to people; require an exceptional, clearly contextualised clue or replace.'),
}
CULTURAL_REFERENCES = {
    'NBC': ('american_institution',
            'Valid US broadcaster initialism; a fair clue can play on the transatlantic reference.'),
}

def review_signal(answer):
    word=''.join(c for c in answer.upper() if c.isalpha())
    if word in CONTEXT_REVIEW:
        topic,guidance=CONTEXT_REVIEW[word]
        return EditorialSignal(word,True,(topic,),guidance)
    if word in CULTURAL_REFERENCES:
        topic,guidance=CULTURAL_REFERENCES[word]
        return EditorialSignal(word,False,(topic,),guidance)
    return EditorialSignal(word,False,(),
                           'Check definition, cryptic wordplay, surface reading and overall puzzle variety.')

def review_draft(draft):
    return [
        {'direction':direction,'number':clue['number'],
         'answer':clue['answer'],'review_required':signal.review_required,
         'topics':list(signal.topics),'guidance':signal.guidance}
        for direction,clues in draft['clues'].items()
        for clue in clues
        for signal in [review_signal(clue['answer'])]
    ]
