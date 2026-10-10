#!/usr/bin/env python3
"""Analyse independent 15x15 reference grids without training on their layouts.

Input: JSON mapping reference names to arrays of 15 rows ('.' light, '#' block).
Does not reproduce reference patterns or use them as generation templates.
"""
import argparse
import json
from pathlib import Path
from rank_grids import metrics
from generate_grid import N, slots


def inspect_reference(name, rows):
    if len(rows) != N or any(not isinstance(row, str) or len(row) != N
                             or set(row) - {'.', '#'} for row in rows):
        raise ValueError(f'{name}: expected exactly 15 rows of 15 dots/blocks')
    result = metrics(rows)
    if not slots(rows):
        raise ValueError(f'{name}: no entries')
    return result


def analyse(references):
    if not isinstance(references, dict) or not references:
        raise ValueError('Expected a nonempty mapping of reference names to grids')
    measurements = {name: inspect_reference(name, rows)
                    for name, rows in references.items()}
    keys = ('entries', 'across', 'down', 'three_letter_entries',
            'long_entries_9_plus', 'crossing_ratio', 'block_ratio')
    summary = {key: {'min': min(m[key] for m in measurements.values()),
                     'max': max(m[key] for m in measurements.values()),
                     'mean': round(sum(m[key] for m in measurements.values())
                                   / len(measurements), 3)}
               for key in keys}
    return {'reference_count': len(measurements),
            'summary': summary, 'grids': measurements}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('references', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = analyse(json.loads(args.references.read_text(encoding='utf-8')))
    payload = json.dumps(result, indent=2) + '\n'
    if args.output:
        args.output.write_text(payload, encoding='utf-8')
    else:
        print(payload, end='')


if __name__ == '__main__':
    main()
