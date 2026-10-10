#!/usr/bin/env python3
"""Clue composition workbench: diverse proposals, transparent verification, no automatic sign-off."""
import argparse
import json
import re
from collections import Counter
from pathlib import Path

from wordplay_explorer import verify

FAMILIES = {
    "letter-manipulation": {"anagram", "reversal", "deletion", "substitution"},
    "assembly": {"charade", "container", "alternation"},
    "concealment": {"hidden", "acrostic", "telestich"},
    "sound-and-meaning": {"homophone", "double-definition", "cryptic-definition"},
    "lateral": {"visual", "reb us", "letter-shape", "other"},
}
FAMILIES["lateral"].remove("reb us")
FAMILIES["lateral"].add("rebus")
DEVICE_TO_FAMILY = {device: family for family, devices in FAMILIES.items() for device in devices}
LITERAL_DEVICES = {"anagram", "reversal", "deletion", "charade", "container", "hidden"}
REQUIRED = ("answer", "clue", "device", "definition", "parse", "surface_story")

def assess(candidate):
    errors = []
    for field in REQUIRED:
        if not isinstance(candidate.get(field), str) or not candidate[field].strip():
            errors.append("missing " + field)
    answer = re.sub("[^A-Z]", "", str(candidate.get("answer", "")).upper())
    if not answer:
        errors.append("answer must contain letters")
    device = candidate.get("device")
    family = DEVICE_TO_FAMILY.get(device)
    if family is None:
        errors.append("unknown device")
    status = "semantic-review-required"
    if device in LITERAL_DEVICES:
        if "fodder" not in candidate:
            errors.append("missing fodder for literal verification")
        else:
            kwargs = {}
            if device in ("deletion", "container"):
                kwargs["container"] = candidate.get("container")
            if device == "container":
                kwargs["position"] = candidate.get("position")
            try:
                passed = verify(answer, device, candidate["fodder"], **kwargs)
            except (TypeError, ValueError):
                passed = False
            if not passed:
                errors.append("letter operation does not yield answer")
            else:
                status = "letter-operation-verified"
    if errors:
        status = "invalid"
    return {
        "answer": answer, "device": device, "family": family,
        "status": status, "errors": errors,
        "editorially_approved": False,
    }

def review_portfolio(candidates):
    reviews = [assess(candidate) for candidate in candidates]
    by_answer = {}
    for candidate, review in zip(candidates, reviews):
        answer = review["answer"]
        item = by_answer.setdefault(answer, {"candidate_count": 0, "families": set(), "devices": set(), "valid": 0})
        item["candidate_count"] += 1
        if review["status"] != "invalid":
            item["valid"] += 1
            item["families"].add(review["family"])
            item["devices"].add(review["device"])
    summary = {}
    for answer, item in by_answer.items():
        summary[answer] = {
            "candidate_count": item["candidate_count"], "valid": item["valid"],
            "families": sorted(item["families"]), "devices": sorted(item["devices"]),
            "needs_broader_exploration": len(item["families"]) < 2,
        }
    return {"candidates": reviews, "by_answer": summary,
            "editorially_approved": False,
            "note": "Letter checks do not establish definition, indicator, surface or fairness."}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("candidates", type=Path, help="JSON array of clue proposals")
    args = parser.parse_args()
    proposals = json.loads(args.candidates.read_text())
    if not isinstance(proposals, list):
        parser.error("input must be a JSON array")
    print(json.dumps(review_portfolio(proposals), indent=2))

if __name__ == "__main__":
    main()
