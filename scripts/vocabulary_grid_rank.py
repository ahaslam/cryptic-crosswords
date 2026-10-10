"""Vocabulary-aware grid pre-ranking.

This is a cheap *necessary-condition* heuristic, not a promise of a fill.
A slot with no preferred-length candidates must consume an exception; longer
slots with few preferred words are penalised before expensive CSP search.
"""
from collections import Counter, defaultdict, deque
from generate_grid import slots
from rank_grids import metrics

def vocabulary_metrics(grid, scores, preferred_score, max_exceptions):
    lengths=Counter(len(s) for s in slots(grid))
    preferred=Counter(len(w) for w,v in scores.items() if v>=preferred_score)
    available=Counter(len(w) for w in scores)
    forced=sum(n for length,n in lengths.items() if preferred[length]==0)
    scarce=sum(n/max(1,preferred[length]) for length,n in lengths.items())
    impossible=sum(n for length,n in lengths.items() if available[length]<n)
    # A low structural score remains desirable, but vocabulary feasibility
    # dominates when evaluating candidate grids for Accessible difficulty.
    structural=metrics(grid)['score']
    return {'forced_exceptions_lower_bound':forced,
            'preferred_scarcity':round(scarce,5),
            'insufficient_length_supply':impossible,
            'structural_score':structural,
            'vocabulary_rank':round(10000*impossible+
                                    1000*max(0,forced-max_exceptions)+
                                    20*scarce+structural,5)}

def crossing_feasibility(grid, preferred_words, candidate_cap=300):
    """Bounded AC-3 on common-word domains; estimate crossing difficulty.

    A truncated domain makes this a ranking heuristic, NOT proof that a
    grid is impossible. Word choices are deterministic and frequency-ranked.
    """
    entries=slots(grid)
    pools=defaultdict(list)
    for word,score in preferred_words.items():
        pools[len(word)].append((score,word))
    domains=[]
    for entry in entries:
        ranked=sorted(pools[len(entry)],key=lambda item:(-item[0],item[1]))
        domains.append({w for _,w in ranked[:candidate_cap]})
    cell_owners=defaultdict(list)
    for i,entry in enumerate(entries):
        for pos,cell in enumerate(entry):
            cell_owners[cell].append((i,pos))
    neighbors=defaultdict(dict)
    for owners in cell_owners.values():
        if len(owners)==2:
            (a,pa),(b,pb)=owners
            neighbors[a][b]=(pa,pb)
            neighbors[b][a]=(pb,pa)
    queue=deque((a,b) for a in neighbors for b in neighbors[a])
    revisions=0
    while queue:
        a,b=queue.popleft()
        if not domains[a] or not domains[b]:
            continue
        pa,pb=neighbors[a][b]
        supported={w[pb] for w in domains[b]}
        reduced={w for w in domains[a] if w[pa] in supported}
        if len(reduced)<len(domains[a]):
            revisions+=1
            domains[a]=reduced
            for k in neighbors[a]:
                if k!=b:
                    queue.append((k,a))
    empty=sum(not domain for domain in domains)
    scarcity=sum(1/(1+len(domain)) for domain in domains)
    return {'empty_preferred_domains':empty,
            'crossing_scarcity':round(scarcity,5),
            'arc_revisions':revisions,
            'candidate_cap':candidate_cap}

def select_vocabulary_aware(candidates, scores, preferred_score, max_exceptions):
    """Accept (structural_score, seed, pattern) tuples; return best with metrics."""
    ranked=[]
    preferred={w:v for w,v in scores.items() if v>=preferred_score}
    for _,seed,pattern in candidates:
        v=vocabulary_metrics(pattern,scores,preferred_score,max_exceptions)
        crossing=crossing_feasibility(pattern,preferred)
        v['crossing']=crossing
        # Empty domains indicate trouble under the bounded common-word sample;
        # prefer grids with broad crossing support before structural tie-breaks.
        rank=(crossing['empty_preferred_domains'],crossing['crossing_scarcity'],
              v['vocabulary_rank'])
        ranked.append((rank,v['structural_score'],seed,pattern,v))
    if not ranked:
        raise ValueError('No candidate grids')
    _,_,seed,pattern,v=min(ranked,key=lambda x:(x[0],x[1],x[2]))
    return pattern,seed,{**metrics(pattern),'vocabulary':v}
