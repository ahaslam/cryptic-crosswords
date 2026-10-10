#!/usr/bin/env python3
"""Backtracking crossword filler. Output is an UNPUBLISHED draft, not a clued puzzle."""
import argparse
import json
import random
import re
from collections import defaultdict
from pathlib import Path
from word_index import WordIndex

def slots_of(grid):
    n=len(grid); numbers={}; slots=[]
    for r in range(n):
        for c in range(n):
            if grid[r][c]=='#': continue
            across=(c==0 or grid[r][c-1]=='#') and c+1<n and grid[r][c+1]!='#'
            down=(r==0 or grid[r-1][c]=='#') and r+1<n and grid[r+1][c]!='#'
            if across or down: numbers[r,c]=len(numbers)+1
    for direction,dr,dc in [('across',0,1),('down',1,0)]:
        for (r,c),number in numbers.items():
            if direction=='across' and (c>0 and grid[r][c-1]!='#' or c+1>=n or grid[r][c+1]=='#'): continue
            if direction=='down' and (r>0 and grid[r-1][c]!='#' or r+1>=n or grid[r+1][c]=='#'): continue
            cells=[];rr,cc=r,c
            while rr<n and cc<n and grid[rr][cc]!='#':
                cells.append((rr,cc));rr+=dr;cc+=dc
            slots.append((direction,number,r,c,cells))
    return slots

def fill(pattern,dictionary,seed=0,max_nodes=250000,word_scores=None,min_score=None,
         preferred_score=None,max_exceptions=None):
    n=len(pattern)
    if n<3 or any(len(row)!=n or any(ch not in '#.' for ch in row) for row in pattern):
        raise ValueError('Expected square pattern of # and .')
    slots=slots_of(pattern);words=defaultdict(set)
    lengths={len(s[4]) for s in slots}
    for raw in Path(dictionary).read_text(encoding='utf-8').splitlines():
        word=raw.strip().upper()
        if re.fullmatch('[A-Z]+',word) and len(word) in lengths: words[len(word)].add(word)
    if any(not words[length] for length in lengths): raise ValueError('Dictionary lacks required word lengths')
    if min_score is not None and word_scores is None:
        raise ValueError('min_score requires word_scores')
    if word_scores is not None:
        words={length:{w for w in pool if min_score is None or word_scores.get(w,0)>=min_score}
               for length,pool in words.items()}
        if any(not words[length] for length in lengths):
            raise ValueError('Quality filter removed every candidate for a required length')
    if max_exceptions is not None and (word_scores is None or preferred_score is None or max_exceptions < 0):
        raise ValueError('Exceptions require scores, preferred_score and a nonnegative limit')
    index=WordIndex(words)
    board=[list(row) for row in pattern];used=set();assigned={};rng=random.Random(seed);nodes=0
    cell_to_slots=defaultdict(list)
    for j,slot in enumerate(slots):
        for cell in slot[4]: cell_to_slots[cell].append(j)
    degree=[len({other for cell in slot[4] for other in cell_to_slots[cell] if other!=j})
            for j,slot in enumerate(slots)]
    exceptions_used=0
    def candidates(i):
        cells=slots[i][4]
        return index.candidates(''.join(board[r][c] for r,c in cells),used)
    def solve():
        nonlocal nodes,exceptions_used
        if len(assigned)==len(slots): return True
        if nodes>=max_nodes:return False
        options=[]
        unavoidable_exceptions=0
        for i in range(len(slots)):
            if i in assigned:continue
            possible=candidates(i)
            if max_exceptions is not None and exceptions_used >= max_exceptions:
                possible=[w for w in possible if word_scores.get(w,0)>=preferred_score]
            if not possible:return False
            if max_exceptions is not None and not any(
                    word_scores.get(w,0)>=preferred_score for w in possible):
                unavoidable_exceptions+=1
                if exceptions_used+unavoidable_exceptions>max_exceptions:
                    return False
            options.append((len(possible),-degree[i],i,possible))
        _,_,i,possible=min(options,key=lambda x:(x[0],x[1],x[2]))
        if word_scores is None:
            rng.shuffle(possible)
        else:
            # Most familiar candidates first; ties stable for reproducible results.
            possible.sort(key=lambda w:(-word_scores.get(w,0),w))
        for word in possible:
            exception=(max_exceptions is not None and word_scores.get(word,0)<preferred_score)
            if exception and exceptions_used>=max_exceptions:continue
            nodes+=1;changed=[]
            if exception:exceptions_used+=1
            for (r,c),ch in zip(slots[i][4],word):
                if board[r][c]=='.':board[r][c]=ch;changed.append((r,c))
            assigned[i]=word;used.add(word)
            if solve():return True
            used.remove(word);del assigned[i]
            if exception:exceptions_used-=1
            for r,c in changed:board[r][c]='.'
            if nodes>=max_nodes:break
        return False
    if not solve():raise RuntimeError(f'No fill found after {nodes} attempts; try another grid, dictionary or node limit')
    clues={'across':[],'down':[]}
    for i,(direction,number,r,c,_) in enumerate(slots):
        clues[direction].append({'number':number,'row':r,'col':c,'answer':assigned[i],'text':'[CRYPTIC CLUE REQUIRED]'})
    return {'size':n,'grid':[''.join(row) for row in board],'clues':clues},nodes

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('pattern')
    parser.add_argument('--dictionary',required=True)
    parser.add_argument('--output',required=True)
    parser.add_argument('--seed',type=int,default=0)
    parser.add_argument('--max-nodes',type=int,default=250000)
    args=parser.parse_args()
    output=Path(args.output).resolve()
    published=(Path(__file__).resolve().parents[1]/'site'/'puzzles').resolve()
    if output==published or published in output.parents:parser.error('Draft output must not be inside site/puzzles')
    grid=Path(args.pattern).read_text().strip().splitlines()
    result,nodes=fill(grid,args.dictionary,args.seed,args.max_nodes)
    result.update(id='draft-001',title='Unreviewed draft')
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(result,indent=2)+'\n')
    print(f'Wrote {output} after {nodes} attempts; clues still require editorial review.')

if __name__=='__main__':main()
