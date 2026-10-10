#!/usr/bin/env python3
"""Validate structure of the growing editorial example library (not clue fairness)."""
import json
import re
import sys
from pathlib import Path

REQUIRED = {"id","clue","answer","device","parse","definition","surface","lesson","provenance","status","tags"}
STATUSES = {"reference","draft","rejected"}

def validate(document):
    errors=[]
    if document.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    examples=document.get("examples")
    if not isinstance(examples,list):
        return ["examples must be an array"]
    seen=set()
    for i,entry in enumerate(examples):
        ref=f"examples[{i}]"
        if not isinstance(entry,dict):
            errors.append(f"{ref} must be an object")
            continue
        for field in REQUIRED:
            if field not in entry:
                errors.append(f"{ref} missing {field}")
        identifier=entry.get("id")
        if not isinstance(identifier,str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*",identifier):
            errors.append(f"{ref} invalid id")
        elif identifier in seen:
            errors.append(f"{ref} duplicate id")
        else:
            seen.add(identifier)
        for field in ("clue","answer","parse","definition","surface","lesson","provenance"):
            if not isinstance(entry.get(field),str) or not entry[field].strip():
                errors.append(f"{ref} empty {field}")
        if entry.get("status") not in STATUSES:
            errors.append(f"{ref} invalid status")
        for field in ("device","tags"):
            values=entry.get(field)
            if not isinstance(values,list) or not values or any(not isinstance(v,str) or not v.strip() for v in values):
                errors.append(f"{ref} invalid {field}")
    return errors

def main():
    path=Path(sys.argv[1]) if len(sys.argv)>1 else Path("editorial/clue-examples.json")
    errors=validate(json.loads(path.read_text()))
    if errors:
        print("\n".join(errors))
        return 1
    print("Validated editorial example library")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
