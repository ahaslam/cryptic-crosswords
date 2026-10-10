"""Create or update the benchmark comment on a same-repository pull request."""
import json
import os
import sys
import urllib.request
from benchmark_summary import summary

MARKER="<!-- cryptic-crossword-benchmark -->"

def request(url,method="GET",payload=None):
    token=os.environ["GH_TOKEN"]
    body=json.dumps(payload).encode() if payload is not None else None
    req=urllib.request.Request(url,data=body,method=method,headers={
        "Authorization":f"Bearer {token}",
        "Accept":"application/vnd.github+json",
        "X-GitHub-Api-Version":"2022-11-28",
        "User-Agent":"cryptic-crossword-benchmark",
        **({"Content-Type":"application/json"} if body is not None else {})})
    with urllib.request.urlopen(req,timeout=30) as response:
        raw=response.read()
        return json.loads(raw) if raw else None

def main(path):
    repo=os.environ["GH_REPO"]
    pr=os.environ["PR_NUMBER"]
    url=f"https://api.github.com/repos/{repo}/issues/{pr}/comments"
    body=MARKER+"\n"+summary(path)
    existing=None
    page=1
    while page<=10:
        comments=request(f"{url}?per_page=100&page={page}")
        for comment in comments:
            if MARKER in comment.get("body",""):
                existing=comment["id"]
        if len(comments)<100:
            break
        page+=1
    if existing:
        request(f"https://api.github.com/repos/{repo}/issues/comments/{existing}",
                "PATCH",{"body":body})
    else:
        request(url,"POST",{"body":body})

if __name__=="__main__":
    main(sys.argv[1] if len(sys.argv)>1 else "fill-benchmark.json")
