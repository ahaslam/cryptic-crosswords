#!/usr/bin/env python3
"""Enumerate contiguous segmentations of an answer, ignoring spaces and punctuation.

The lexicon maps strings to possible meanings. This is a discovery tool, not
a semantic validator or an autonomous clue writer.
"""
import argparse
import json
import re
from pathlib import Path

def normalize(value):
    return re.sub(r"[^A-Z]", "", value.upper())

def segment(answer, lexicon, *, min_parts=2, max_parts=5, max_results=100):
    letters = normalize(answer)
    words = {normalize(k): v for k, v in lexicon.items()}
    if not letters:
        return []
    results = []
    def walk(pos, parts):
        if len(results) >= max_results:
            return
        if pos == len(letters):
            if min_parts <= len(parts) <= max_parts:
                results.append({"answer": letters, "parts": [
                    {"letters": p, "meanings": words[p]} for p in parts
                ], "operation": "charade", "verified": "".join(parts) == letters,
                "editorially_approved": False})
            return
        if len(parts) >= max_parts:
            return
        for end in range(pos + 1, len(letters) + 1):
            part = letters[pos:end]
            if part in words:
                walk(end, parts + [part])
    walk(0, [])
    return results

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("answer")
    parser.add_argument("--lexicon", type=Path, default=Path("editorial/segment-lexicon.json"))
    parser.add_argument("--max-results", type=int, default=100)
    args = parser.parse_args()
    lexicon = json.loads(args.lexicon.read_text())
    print(json.dumps(segment(args.answer, lexicon, max_results=args.max_results), indent=2))

if __name__ == "__main__":
    main()
