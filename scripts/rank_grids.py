"""Structural measurements and ranking for British 15x15 cryptic grids.

These are editorial heuristics, not a claim that any particular published
grid layout is the only acceptable one. Vocabulary fillability is assessed
separately by the benchmark.
"""
from collections import Counter
from generate_grid import N, generate, slots


def metrics(grid):
    entries = slots(grid)
    lengths = [len(entry) for entry in entries]
    crossing_counts = Counter(cell for entry in entries for cell in entry)
    white = {(r, c) for r in range(N) for c in range(N) if grid[r][c] != '#'}
    across = sum(entry[0][0] == entry[-1][0] for entry in entries)
    down = len(entries) - across
    distribution = dict(sorted(Counter(lengths).items()))
    three = distribution.get(3, 0)
    long_entries = sum(length >= 9 for length in lengths)
    long_excess = sum(max(0, length - 13) ** 2 for length in lengths)
    crossing_ratio = (sum(crossing_counts.get(cell, 0) == 2 for cell in white)
                      / len(white)) if white else 0
    symmetric = all(grid[r][c] == grid[N-1-r][N-1-c]
                    for r in range(N) for c in range(N))
    block_count = N*N - len(white)
    # Soft preferences: do not reject a valid grid for a statistical outlier.
    score = (long_excess*4 + three*16 + abs(len(entries)-28)*10
             + abs(across-down)*7 + abs(crossing_ratio-0.35)*20
             + abs(block_count/(N*N)-0.29)*100
             + abs(long_entries-10)*5)
    return {'score': round(score, 3), 'entries': len(entries),
            'across': across, 'down': down, 'across_down_difference': abs(across-down),
            'length_distribution': distribution, 'three_letter_entries': three,
            'long_entries_9_plus': long_entries, 'long_excess': long_excess,
            'crossing_ratio': round(crossing_ratio, 3),
            'unchecked_ratio': round(1-crossing_ratio, 3),
            'block_count': block_count, 'block_ratio': round(block_count/(N*N), 3),
            'rotationally_symmetric': symmetric,
            'max_entry_length': max(lengths, default=0)}


def candidates(seed, count=8, attempts=20000):
    if count < 1:
        raise ValueError('Candidate count must be positive')
    results = []
    for i in range(count):
        candidate_seed = seed + i*1009
        pattern = generate(seed=candidate_seed, attempts=attempts)
        results.append((metrics(pattern)['score'], candidate_seed, pattern))
    results.sort(key=lambda item: (item[0], item[1]))
    return results


def select(seed, count=8, attempts=20000):
    _, candidate_seed, pattern = candidates(seed, count, attempts)[0]
    return pattern, candidate_seed, metrics(pattern)
