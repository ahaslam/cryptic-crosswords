"""Controlled comparison of grid ranking strategies with matched inputs."""
import argparse
import json
from pathlib import Path
from benchmark_fill import run

def compare(seed=0, max_nodes=10000, grid_trials=4, grid_candidates=8):
    results={}
    for strategy in ('ranked','vocabulary'):
        report=run(seed=seed,max_nodes=max_nodes,grid_trials=grid_trials,
                   grid_candidates=grid_candidates,grid_strategy=strategy)
        completed=next((t for t in report['trials'] if t['status']=='filled_unreviewed'),None)
        results[strategy]={
            'status':report['status'],
            'elapsed_seconds':report['elapsed_seconds'],
            'completed_seed':completed['seed'] if completed else None,
            'selected_grid_seed':completed['selected_grid_seed'] if completed else None,
            'uncommon_answers':completed['exception_count'] if completed else None,
            'mean_frequency':completed['mean_frequency'] if completed else None,
            'trials':len(report['trials'])}
    return {'seed':seed,'max_nodes_per_strategy':max_nodes,
            'grid_trials':grid_trials,'grid_candidates':grid_candidates,
            'results':results}

def summary(data):
    lines=['### Controlled grid-ranking comparison','',
           'Both strategies use identical seeds, candidate pools, dictionary and search budgets.','',
           '| Strategy | Filled? | Uncommon answers | Mean frequency | Seconds |',
           '|---|---|---:|---:|---:|']
    for name in ('ranked','vocabulary'):
        result=data['results'][name]
        lines.append(f"| {name} | {result['status']=='filled_unreviewed'} | "
                     f"{result['uncommon_answers'] if result['uncommon_answers'] is not None else '—'} | "
                     f"{result['mean_frequency'] if result['mean_frequency'] is not None else '—'} | "
                     f"{result['elapsed_seconds']} |")
    lines.append('\nEach strategy selects its own grid; differences are attributable to the selection strategy and solver variability, not to an identical filled grid.')
    return '\n'.join(lines)+'\n'

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--seed',type=int,default=0)
    parser.add_argument('--max-nodes',type=int,default=10000)
    parser.add_argument('--grid-trials',type=int,default=4)
    parser.add_argument('--grid-candidates',type=int,default=8)
    parser.add_argument('--output',default='ranking-comparison.json')
    args=parser.parse_args()
    result=compare(args.seed,args.max_nodes,args.grid_trials,args.grid_candidates)
    Path(args.output).write_text(json.dumps(result,indent=2)+'\n')
    print(summary(result))
