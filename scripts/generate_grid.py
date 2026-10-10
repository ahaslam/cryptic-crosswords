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

def _lattice(top_unchecked, left_unchecked):
    """Exet-style chequered starting pattern; four parity variants."""
    return [['#' if ((r + int(top_unchecked)) % 2 == 1 and
                     (c + int(left_unchecked)) % 2 == 1) else '.'
             for c in range(N)] for r in range(N)]


def _british_checking(grid):
    """No consecutive unchecked letters, and at least half checked per entry."""
    entries = slots(grid)
    counts = {}
    for entry in entries:
        for cell in entry:
            counts[cell] = counts.get(cell, 0) + 1
    for entry in entries:
        unchecked = [counts.get(cell, 0) == 1 for cell in entry]
        if any(a and b for a, b in zip(unchecked, unchecked[1:])):
            return False
        if sum(unchecked) > (len(entry) + (len(entry) >= 9)) // 2:
            return False
    return True


def _structural(grid):
    """Validate connectivity and slots independently of the target clue count."""
    return valid(grid, min_clues=1, max_clues=60) and _british_checking(grid)


def generate(seed=0, attempts=20000, min_clues=26, max_clues=30):
    if not 1 <= min_clues <= max_clues <= 60:
        raise ValueError('Clue count must be between 1 and 60')
    rng = random.Random(seed)
    pairs = [(r, c) for r in range(N) for c in range(N)
             if (r, c) <= (N-1-r, N-1-c)]
    best = None
    # Limit preferred-count exploration so low-count fallbacks remain fast.
    for trial in range(min(max(1, attempts), 24)):
        variant = (seed + trial) % 4
        grid = _lattice(bool(variant & 1), bool(variant & 2))
        if not _structural(grid):
            continue
        order = pairs[:]
        rng.shuffle(order)
        # Add blocks to a valid chequered lattice rather than removing blocks
        # from an initially open grid. Every change preserves rotational symmetry.
        for r, c in order:
            if min_clues <= len(slots(grid)) <= max_clues:
                result = [''.join(row) for row in grid]
                if len(slots(grid)) >= 28:
                    return result
                if best is None:
                    best = result
                break
            rr, cc = N-1-r, N-1-c
            if grid[r][c] == '#' or grid[rr][cc] == '#':
                continue
            grid[r][c] = grid[rr][cc] = '#'
            if not _structural(grid) or len(slots(grid)) > max_clues:
                grid[r][c] = grid[rr][cc] = '.'
        if min_clues <= len(slots(grid)) <= max_clues:
            result = [''.join(row) for row in grid]
            if len(slots(grid)) >= 28:
                return result
            if best is None:
                best = result
    if best is not None:
        return best
    raise RuntimeError('No valid lattice grid found: try a different seed or more attempts')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--seed', type=int, default=0)
    parser.add_argument('--attempts', type=int, default=20000)
    args = parser.parse_args()
    grid = generate(args.seed, args.attempts)
    print('\n'.join(grid))
    print(f'{len(slots(grid))} entries')
