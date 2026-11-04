"""Pico's independent re-check of Lemma A for row 132 (PR #46). Shares no code with check.py.

Badness of a set I depends only on the labelled tournament induced on I, so Lemma A
("every bad set has at most h+1 elements", h = ceil(log2 k)) holds for EVERY tournament
on [k] iff no (h+2)-subset S of [k] is bad under ANY orientation of S. This script checks
that exhaustively for all k <= K (default 12), and that some (h+1)-set is bad (tightness).

Negative control: `--label const` (all labels 1) must exit 1.
Standard library only. Usage: python3 check.py [K] [--label xor|const]
"""
import sys
from itertools import combinations

def xor_label(i, j):
    return ((i - 1) ^ (j - 1)).bit_length()

def const_label(i, j):
    return 1

def some_orientation_bad(S, label):
    # Search orientations edge by edge; prune as soon as some head sees two distinct in-labels.
    pairs = list(combinations(range(len(S)), 2))
    inlab = [None] * len(S)
    def go(e):
        if e == len(pairs):
            return True
        x, y = pairs[e]
        for tail, head in ((x, y), (y, x)):
            L = label(S[tail], S[head])
            prev = inlab[head]
            if prev is None or prev == L:
                inlab[head] = L
                if go(e + 1):
                    return True
                inlab[head] = prev
        return False
    return go(0)

def main():
    args = sys.argv[1:]
    label = xor_label
    if "--label" in args:
        name = args[args.index("--label") + 1]
        label = {"xor": xor_label, "const": const_label}[name]
        args = [a for a in args if a not in ("--label", name)]
    K = int(args[0]) if args else 12
    violations, subsets, tight = [], 0, 0
    for k in range(2, K + 1):
        h = (k - 1).bit_length()  # ceil(log2 k)
        for S in combinations(range(1, k + 1), h + 2):
            subsets += 1
            if some_orientation_bad(S, label):
                violations.append((k, S))
        if any(some_orientation_bad(S, label) for S in combinations(range(1, k + 1), h + 1)):
            tight += 1
    print(f"k<=%d: (h+2)-subsets checked=%d, bad under some orientation=%d, k with a bad (h+1)-set=%d/%d"
          % (K, subsets, len(violations), tight, K - 1))
    if violations:
        print("first violation:", violations[0])
        print("RESULT: fails")
        sys.exit(1)
    print("RESULT: passes")

if __name__ == "__main__":
    main()
