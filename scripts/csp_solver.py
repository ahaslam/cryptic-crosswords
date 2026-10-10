"""Crossword CSP with crossing arc consistency and bounded uncommon answers.

Each slot is a variable, its dictionary words are its domain. AC-3 propagates
letter constraints between crossing slots after each assignment. A node is a
branch choice, not an individual arc revision.
"""
from collections import defaultdict, deque
from grid_editorial_quality import candidate_penalty

def solve_csp(slots, words_by_length, scores=None, preferred_score=None,
              max_exceptions=None, max_nodes=10000, ranking_scores=None, editorial_order=False):
    domains=[set(words_by_length[len(slot[4])]) for slot in slots]
    crossing=defaultdict(list)
    for i,slot in enumerate(slots):
        for pos,cell in enumerate(slot[4]):
            crossing[cell].append((i,pos))
    neighbors=[{} for _ in slots]
    for occupants in crossing.values():
        if len(occupants)==2:
            (a,pa),(b,pb)=occupants
            neighbors[a][b]=(pa,pb)
            neighbors[b][a]=(pb,pa)
    arcs=[(a,b) for a in range(len(slots)) for b in neighbors[a]]
    nodes=0

    def propagate(ds, initial=None):
        queue=deque(arcs if initial is None else initial)
        while queue:
            a,b=queue.popleft()
            pa,pb=neighbors[a][b]
            letters={word[pb] for word in ds[b]}
            reduced={word for word in ds[a] if word[pa] in letters}
            if not reduced:
                return False
            if len(reduced)!=len(ds[a]):
                ds[a]=reduced
                for k in neighbors[a]:
                    if k!=b:
                        queue.append((k,a))
        return True

    def search(ds, assigned, used, rare_used):
        nonlocal nodes
        if len(assigned)==len(slots):
            return assigned
        if nodes>=max_nodes:
            return None
        # All-different propagation: no other slot can reuse a fixed answer.
        changed=[]
        for i in range(len(ds)):
            if i in assigned:
                continue
            reduced=ds[i]-used
            if not reduced:
                return None
            if len(reduced)!=len(ds[i]):
                ds[i]=reduced
                changed.extend((k,i) for k in neighbors[i])
        if changed and not propagate(ds,changed):
            return None
        if max_exceptions is not None:
            remaining=max_exceptions-rare_used
            if remaining<0:
                return None
            forced=sum(not any(scores.get(w,0)>=preferred_score for w in ds[i])
                       for i in range(len(ds)) if i not in assigned)
            if forced>remaining:
                return None
        i=min((i for i in range(len(ds)) if i not in assigned),
              key=lambda i:(len(ds[i]),-len(neighbors[i]),i))
        order=ranking_scores if ranking_scores is not None else scores
        options=sorted(ds[i],key=lambda w:(
            -(order.get(w,0) if order is not None else 0)
            +(candidate_penalty(w,used) * (editorial_order if isinstance(editorial_order,(int,float)) else 1) if editorial_order else 0),w))
        for word in options:
            rare=(max_exceptions is not None and scores.get(word,0)<preferred_score)
            if rare and rare_used>=max_exceptions:
                continue
            nodes+=1
            next_ds=ds.copy()
            next_ds[i]={word}
            next_ds=[set(d) if j!=i else d for j,d in enumerate(next_ds)]
            # Assignment also propagates the all-different constraint.
            changed_arcs=[(k,i) for k in neighbors[i]]
            viable=True
            for j in range(len(next_ds)):
                if j==i or j in assigned:
                    continue
                if word in next_ds[j]:
                    next_ds[j].remove(word)
                    if not next_ds[j]:
                        viable=False
                        break
                    changed_arcs.extend((k,j) for k in neighbors[j])
            if viable and propagate(next_ds,changed_arcs):
                result=search(next_ds,{**assigned,i:word},used|{word},rare_used+int(rare))
                if result is not None:
                    return result
            if nodes>=max_nodes:
                break
        return None

    if not propagate(domains):
        return None,nodes
    return search(domains,{},set(),0),nodes
