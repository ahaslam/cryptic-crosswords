#!/usr/bin/env python3
"""Compare reference grid distributions with independently generated grids."""
import argparse
import json
from pathlib import Path
from analyse_reference_grids import analyse
from generate_grid import generate
from rank_grids import metrics


def compare(references, seeds=range(6)):
    observed = analyse(references)
    generated = {f'seed-{seed}': metrics(generate(seed=seed)) for seed in seeds}
    keys = observed['summary']
    generated_summary = {
        key: {'min': min(g[key] for g in generated.values()),
              'max': max(g[key] for g in generated.values()),
              'mean': round(sum(g[key] for g in generated.values()) / len(generated), 3)}
        for key in keys
    }
    return {'references': observed['summary'], 'generated': generated_summary,
            'reference_count': observed['reference_count'],
            'generated_count': len(generated),
            'generated_grids': generated}


if __name__ == '__main__':
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser()
    parser.add_argument('--samples', type=int, default=100)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.samples < 1:
        parser.error('--samples must be positive')
    refs = json.loads((root/'data'/'reference-grids.json').read_text())
    result = compare(refs, range(args.samples))
    payload = json.dumps(result, indent=2) + '\n'
    if args.output:
        args.output.write_text(payload)
    else:
        print(payload, end='')
