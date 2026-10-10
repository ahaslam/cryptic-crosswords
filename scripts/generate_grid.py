#!/usr/bin/env python3
"""Generate 180-degree symmetric, connected 15x15 crossword grid patterns.

This produces EMPTY PATTERNS, not filled puzzles or cryptic clues.
"""
import argparse
import random

N = 15

def slots(grid):
    found = []
    for dr, dc in ((0, 1), (1, 0)):
        for r in range(N):
            for c in range(N):
                if grid[r][c] == '#':
                    continue
                pr, pc = r - dr, c - dc
                if 0 <= pr < N and 0 <= pc < N and grid[pr][pc] != '#':
                    continue
                cells = []
                rr, cc = r, c
                while rr < N and cc < N and grid[rr][cc] != '#':
                    cells.append((rr, cc))
                    rr += dr
                    cc += dc
                if len(cells) > 1:
                    found.append(cells)
    return found

def valid(grid, min_clues=26, max_clues=30):
    found = slots(grid)
    if not min_clues <= len(found) <= max_clues:
        return False
    if any(len(s) < 3 for s in found):
        return False
    white = {(r, c) for r in range(N) for c in range(N) if grid[r][c] != '#'}
    if {cell for s in found for cell in s} != white:
        return False
    seen = {next(iter(white))}
    queue = list(seen)
    for r, c in queue:
        for neighbor in ((r-1, c), (r+1, c), (r, c-1), (r, c+1)):
            if neighbor in white and neighbor not in seen:
                seen.add(neighbor)
                queue.append(neighbor)
    return seen == white

def generate(seed=0, attempts=20000, min_clues=50, max_clues=55):
    if not 1 <= min_clues <= max_clues <= 60:
        raise ValueError('Clue count must be between 1 and 60')
    rng = random.Random(seed)
    pairs = [(r, c) for r in range(N) for c in range(N)
             if (r, c) <= (N-1-r, N-1-c)]
    for _ in range(attempts):
        grid = [['.'] * N for _ in range(N)]
        rng.shuffle(pairs)
        for r, c in pairs:
            if rng.random() < 0.23:
                rr, cc = N-1-r, N-1-c
                grid[r][c] = grid[rr][cc] = '#'
                if any(len(s) < 3 for s in slots(grid)):
                    grid[r][c] = grid[rr][cc] = '.'
        if valid(grid, min_clues=min_clues, max_clues=max_clues):
            return [''.join(row) for row in grid]
    raise RuntimeError('No valid grid found: try a different seed or more attempts')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--seed', type=int, default=0)
    parser.add_argument('--attempts', type=int, default=20000)
    args = parser.parse_args()
    grid = generate(args.seed, args.attempts)
    print('\n'.join(grid))
    print(f'{len(slots(grid))} entries')
