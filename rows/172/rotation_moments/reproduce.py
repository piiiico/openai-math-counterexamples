#!/usr/bin/env python3
"""Reproduce positive identities, actual failure controls and reviewer evidence."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parent


def run(args, expected):
    result = subprocess.run([sys.executable, *args], cwd=ROOT, capture_output=True, text=True)
    if result.returncode != expected:
        raise RuntimeError(f"Unexpected exit {result.returncode} for {args}: {result.stdout}\n{result.stderr}")
    return result.stdout


def main():
    for item in json.loads((ROOT / "sources.json").read_text())["files"]:
        raw = (ROOT / item["local"]).read_bytes()
        if len(raw) != item["bytes"] or hashlib.sha256(raw).hexdigest() != item["sha256"]:
            raise RuntimeError(f"Source pin mismatch: {item['local']}")
    print(run(["check.py"], 0), end="")
    for mode in ([], ["-O"]):
        for fault in ("central_weight", "same_rotation", "plain_derivative"):
            output = run([*mode, "check.py", "--negative-control", fault], 1)
            if not output.startswith("RESULT: rejected: nonzero rational-function residual:"):
                raise RuntimeError(f"Control failed for an unexpected reason: {output}")
    output = run(["review/independent_check.py"], 0)
    expected = ("source/01-introduction.tex True True\n"
                "source/07-consequences.tex True True\n"
                "actual arbitrary-entry product derivative residual: 0\n"
                "pairwise squared distances nonzero as rational functions: True\n")
    if output != expected:
        raise RuntimeError(f"Independent evidence differs: {output}")
    print(output, end="")
    print("RESULT: exact rotation obstruction, six rejecting runs and independent evidence reproduced")


if __name__ == "__main__":
    main()
