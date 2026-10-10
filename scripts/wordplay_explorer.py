#!/usr/bin/env python3
"""Explore verifiable wordplay mechanisms, without pretending to generate good clues."""
import argparse
import json
import re
from collections import Counter

def clean(value):
    return re.sub(r"[^A-Z]", "", value.upper())

def verify(answer, mechanism, fodder, *, container=None, position=None):
    answer, fodder = clean(answer), clean(fodder)
    if mechanism == "reversal":
        return fodder[::-1] == answer
    if mechanism == "anagram":
        return Counter(fodder) == Counter(answer)
    if mechanism == "hidden":
        return answer in fodder and len(answer) < len(fodder)
    if mechanism == "deletion":
        if container is None:
            return False
        source = clean(container)
        return Counter(source) == Counter(answer) + Counter(fodder) and len(source) == len(answer) + len(fodder)
    if mechanism == "charade":
        return fodder == answer
    if mechanism == "container":
        if container is None or position is None:
            return False
        outer, inner = clean(container), fodder
        return 0 <= position <= len(outer) and outer[:position] + inner + outer[position:] == answer
    return False

def explore(answer, vocabulary):
    """Generate literal reversal/anagram possibilities; no invented synonym claims."""
    answer = clean(answer)
    if not answer:
        raise ValueError("Answer must contain letters")
    seen = set()
    result = []
    for word in vocabulary:
        fodder = clean(word)
        if not fodder or fodder == answer:
            continue
        for mechanism in ("reversal", "anagram"):
            if verify(answer, mechanism, fodder):
                key = (mechanism, fodder)
                if key not in seen:
                    seen.add(key)
                    result.append({"mechanism": mechanism, "fodder": fodder,
                                   "answer": answer, "verified": True,
                                   "surface": None, "definition": None,
                                   "indicator": None, "editorial_status": "needs-development"})
    return result

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("answer")
    parser.add_argument("--words", nargs="*", default=[], help="Candidate fodder words")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    results = explore(args.answer, args.words)
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        for item in results:
            print(f"{item['mechanism']}: {item['fodder']} -> {item['answer']} [verified; needs editorial work]")

if __name__ == "__main__":
    main()
