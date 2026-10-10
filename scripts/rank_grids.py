"""Rank valid crossword patterns by measurable structural fill difficulty.

This is a heuristic, not a proof of dictionary fillability. We record scores
in the benchmark to test whether it predicts actual successful fills.
"""
from collections import Counter
from generate_grid import generate, slots

def metrics(grid):
    entries=slots(grid)
    lengths=[len(entry) for entry in entries]
    crossing_counts=Counter(cell for entry in entries for cell in entry)
    # Very long answers are relatively scarce in ordinary dictionaries.
    # Dense intersections make early word choices constrain many other slots.
    long_excess=sum(max(0,length-9)**2 for length in lengths)
    short_entries=sum(length==3 for length in lengths)
    crossing_ratio=sum(count==2 for count in crossing_counts.values())/len(crossing_counts)
    score=long_excess*4+short_entries*2+crossing_ratio*20
    return {'score':round(score,3),'long_excess':long_excess,
            'three_letter_entries':short_entries,
            'crossing_ratio':round(crossing_ratio,3),
            'max_entry_length':max(lengths),'entries':len(entries)}

def candidates(seed, count=8, attempts=20000):
    if count<1:
        raise ValueError('Candidate count must be positive')
    results=[]
    for i in range(count):
        candidate_seed=seed+i*1009
        pattern=generate(seed=candidate_seed,attempts=attempts)
        results.append((metrics(pattern)['score'],candidate_seed,pattern))
    results.sort(key=lambda item:(item[0],item[1]))
    return results

def select(seed,count=8,attempts=20000):
    _,candidate_seed,pattern=candidates(seed,count,attempts)[0]
    return pattern,candidate_seed,metrics(pattern)

def vocabulary_metrics(grid, common_counts):
    """Estimate slot difficulty from available common-word counts by length.

    Uses dictionary counts only; it does not claim a pattern is solvable.
    """
    import math
    lengths=[len(entry) for entry in slots(grid)]
    # Penalise scarcity multiplicatively: ten available words is much harder
    # than ten thousand, particularly for longer crossing entries.
    scarcity=sum(1.0/math.log1p(max(1,common_counts.get(length,0)))
                 for length in lengths)
    return {'vocabulary_scarcity':round(scarcity,4),
            'least_common_candidates':min(common_counts.get(n,0) for n in lengths)}

def select_vocabulary(seed,common_counts,count=8,attempts=20000):
    """Rank exactly the same candidates as select(), using vocabulary scarcity."""
    options=candidates(seed,count,attempts)
    scored=[]
    for _,candidate_seed,pattern in options:
        vm=vocabulary_metrics(pattern,common_counts)
        # Keep a modest geometric tie-breaker while prioritising vocabulary.
        score=vm['vocabulary_scarcity']+metrics(pattern)['score']/1000
        scored.append((score,candidate_seed,pattern,vm))
    _,chosen,pattern,vm=min(scored,key=lambda x:(x[0],x[1]))
    return pattern,chosen,{**metrics(pattern),**vm}
