"""Format a compact GitHub Actions benchmark report from JSON."""
import json
import sys
from pathlib import Path

def summary(path):
    p=Path(path)
    if not p.is_file():
        return "### Crossword benchmark\n\nNo benchmark report was produced. Check the job logs.\n"
    try:
        data=json.loads(p.read_text(encoding="utf-8"))
    except (ValueError,OSError) as exc:
        return f"### Crossword benchmark\n\nUnable to read report: {exc}\n"
    lines=["### Crossword benchmark", "",
           f"**Result:** {data.get('status','unknown')}  ",
           f"**Elapsed:** {data.get('elapsed_seconds','?')} seconds  ",
           f"**Grid trials:** {len(data.get('trials',[]))}  ",
           f"**Total node budget:** {data.get('max_nodes_total','?')}", "",
           "| Seed | Entries | Result | Nodes | Seconds |",
           "|---:|---:|---|---:|---:|"]
    for t in data.get('trials',[]):
        nodes=t.get('feasibility_nodes',t.get('node_budget','—'))
        secs=t.get('feasibility_seconds',t.get('fill_seconds','—'))
        lines.append(f"| {t.get('seed','?')} | {t.get('entries','?')} | "
                     f"{t.get('status','?')} | {nodes} | {secs} |")
    for t in data.get('trials',[]):
        if t.get('status')=='filled_unreviewed':
            lines.extend(["",f"**Selected fill:** {t.get('selected','?')}  ",
                          f"**Uncommon answers:** {t.get('exception_count','?')}  ",
                          f"**Quality target met:** {t.get('quality_target_met','?')}"])
            exceptions=t.get('exceptions',[])
            if exceptions:
                lines.append("\n**Answers requiring review:** "+", ".join(
                    f"{e['answer']} ({e['frequency']})" for e in exceptions[:25]))
            break
    lines.append("\nDrafts are unreviewed and are not published.")
    return "\n".join(lines)+"\n"

if __name__=="__main__":
    print(summary(sys.argv[1] if len(sys.argv)>1 else 'fill-benchmark.json'))
