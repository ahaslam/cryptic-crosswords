#!/usr/bin/env python3
"""Validate published crossword grids, numbering, intersections and symmetry."""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1] / 'site' / 'puzzles'
def validate(p):
    n=p['size']; grid=p['grid']
    assert n>=3 and len(grid)==n and all(len(row)==n for row in grid)
    assert all(ch=='#' or ('A'<=ch<='Z') for row in grid for ch in row)
    starts={}; coverage=set(); used=set()
    for r in range(n):
        for c in range(n):
            if grid[r][c]=='#': continue
            a=(c==0 or grid[r][c-1]=='#') and c+1<n and grid[r][c+1]!='#'
            d=(r==0 or grid[r-1][c]=='#') and r+1<n and grid[r+1][c]!='#'
            if a or d: starts[(r,c)]=len(starts)+1
    for d in ('across','down'):
        expected={(r,c) for (r,c) in starts if ((c==0 or grid[r][c-1]=='#') and c+1<n and grid[r][c+1]!='#') if d=='across'} if d=='across' else {(r,c) for (r,c) in starts if (r==0 or grid[r-1][c]=='#') and r+1<n and grid[r+1][c]!='#'}
        seen=set()
        for clue in p['clues'][d]:
            r,c=clue['row'],clue['col']; answer=clue['answer']
            assert (r,c) in expected and (r,c) not in seen
            seen.add((r,c))
            assert clue['number']==starts[(r,c)] and len(answer)>=2 and answer.isalpha() and answer.isupper()
            assert clue['text'].strip()
            dr,dc=(0,1) if d=='across' else (1,0)
            for i,ch in enumerate(answer):
                rr,cc=r+i*dr,c+i*dc
                assert 0<=rr<n and 0<=cc<n and grid[rr][cc]==ch
                coverage.add((rr,cc)); used.add((d,rr,cc))
            rr,cc=r+len(answer)*dr,c+len(answer)*dc
            assert rr>=n or cc>=n or grid[rr][cc]=='#'
        assert seen==expected, f'missing or extra {d} clues'
    assert coverage=={(r,c) for r in range(n) for c in range(n) if grid[r][c]!='#'}
    for r in range(n):
        for c in range(n):
            assert (grid[r][c]=='#')==(grid[n-1-r][n-1-c]=='#')
    return len(p['clues']['across'])+len(p['clues']['down'])
def main():
    index=json.loads((ROOT/'index.json').read_text())
    ids=set()
    for item in index['puzzles']:
        assert item['id'] not in ids
        ids.add(item['id'])
        path=(ROOT/item['file']).resolve()
        assert path.parent==ROOT.resolve()
        p=json.loads(path.read_text())
        assert p['id']==item['id']
        print(f"{p['id']}: {validate(p)} clues OK")
if __name__=='__main__': main()
