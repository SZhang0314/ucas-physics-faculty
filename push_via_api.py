#!/usr/bin/env python3
"""Push the current working tree to GitHub via the Git Data REST API.

Used when git-over-HTTPS is blocked but `gh` (which uses its own transport)
can reach the API. Requires an authenticated `gh` CLI on PATH.
"""
import base64
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OWNER = "SZhang0314"
REPO = "ucas-physics-faculty"
BRANCH = "main"

INCLUDE = None  # all tracked files
SKIP_DIRS = {".git", "__pycache__"}
SKIP_FILES = {"data/raw/preview.png", "_apitest.py", "_init.py"}


def gh(*args, input=None, method=None):
    cmd = ["gh", "api"] + list(args)
    if method:
        cmd += ["-X", method]
    if input is not None:
        cmd += ["--input", "-"]
    p = subprocess.run(cmd, input=input, capture_output=True, text=True, encoding="utf-8")
    if p.returncode != 0:
        print("GH ERROR:", p.stderr, file=sys.stderr)
        raise SystemExit(1)
    return p.stdout


def collect():
    files = []
    for fp in sorted(HERE.rglob("*")):
        if not fp.is_file():
            continue
        rel = fp.relative_to(HERE).as_posix()
        parts = set(rel.split("/"))
        if parts & SKIP_DIRS:
            continue
        if rel in SKIP_FILES:
            continue
        files.append((rel, fp))
    return files


def main():
    files = collect()
    print(f"Uploading {len(files)} files")

    blobs = {}
    for rel, fp in files:
        content = fp.read_bytes()
        b64 = base64.b64encode(content).decode("ascii")
        payload = json.dumps({"content": b64, "encoding": "base64"})
        out = gh(f"/repos/{OWNER}/{REPO}/git/blobs", input=payload, method="POST")
        sha = json.loads(out)["sha"]
        blobs[rel] = sha
        print(f"  blob {rel} -> {sha[:8]}")

    # build tree
    tree = [{"path": rel, "mode": "100644", "type": "blob", "sha": sha} for rel, sha in blobs.items()]
    payload = json.dumps({"tree": tree})
    out = gh(f"/repos/{OWNER}/{REPO}/git/trees", input=payload, method="POST")
    tree_sha = json.loads(out)["sha"]
    print("tree:", tree_sha)

    # parent commit (may not exist yet)
    parent = None
    try:
        out = gh(f"/repos/{OWNER}/{REPO}/git/ref/heads/{BRANCH}")
        parent = json.loads(out)["object"]["sha"]
    except SystemExit:
        pass

    commit_obj = {
        "message": "Add UCAS physics & physical sciences faculty directory (314 professors)",
        "tree": tree_sha,
    }
    if parent:
        commit_obj["parents"] = [parent]
    out = gh(f"/repos/{OWNER}/{REPO}/git/commits", input=json.dumps(commit_obj), method="POST")
    commit_sha = json.loads(out)["sha"]
    print("commit:", commit_sha)

    if parent:
        payload = json.dumps({"sha": commit_sha, "force": False})
        gh(f"/repos/{OWNER}/{REPO}/git/refs/heads/{BRANCH}", input=payload, method="PATCH")
    else:
        payload = json.dumps({"ref": f"refs/heads/{BRANCH}", "sha": commit_sha})
        gh(f"/repos/{OWNER}/{REPO}/git/refs", input=payload, method="POST")
    print(f"Pushed to {BRANCH}")


if __name__ == "__main__":
    main()
