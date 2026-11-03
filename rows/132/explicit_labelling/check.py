#!/usr/bin/env python3
"""Exact finite checks for the explicit family 132 labelling.

The manuscript (source/01-construction.tex:27-47) labels each edge i -> j of a
tournament on [k] by a(i, j) in [r] and needs that no set I of size t is
"bad": there are no choices m_j (j in I) with a(i, j) = m_j for every edge
i -> j inside I.

The explicit labelling checked here is

    a(i, j) = bit_length((i - 1) XOR (j - 1)),

the 1-based position of the most significant bit in which the binary
expansions of i - 1 and j - 1 differ.  Its values lie in [h] with
h = bit_length(k - 1) = ceil(log2 k).  PROOF.md shows that for every
tournament on [k] every bad set has at most h + 1 elements, so t = h + 2
works.  This script confirms that bound by exhaustive search on small
tournaments and checks the parameter inequalities the manuscript needs.

Everything uses Python integers; no floating point is involved.  Verification
logic does not rely on ``assert``, so results are the same under ``python -O``.
"""

from __future__ import annotations

import argparse
import math
import sys
from typing import Callable, Iterable, Sequence

Label = Callable[[int, int], int]
Tournament = list[list[bool]]  # adj[i][j] is True when i -> j (1-based, row 0 unused)


# ----------------------------------------------------------------------------
# The labelling and the parameters
# ----------------------------------------------------------------------------

def msb_label(i: int, j: int) -> int:
    """Explicit label: 1-based most significant differing bit of i-1 and j-1."""
    if i == j:
        raise ValueError("labels are defined only for distinct vertices")
    return ((i - 1) ^ (j - 1)).bit_length()


def height(k: int) -> int:
    """h = ceil(log2 k) = number of bits of k - 1 (labels lie in [h])."""
    if k < 2:
        raise ValueError("need k >= 2")
    return (k - 1).bit_length()


def isqrt_ceil(n: int) -> int:
    s = math.isqrt(n)
    return s if s * s == n else s + 1


# ----------------------------------------------------------------------------
# Tournaments
# ----------------------------------------------------------------------------

def cyclic_tournament(M: int) -> Tournament:
    """Manuscript tournament: k = 2M^2 + 1, i -> i+1, ..., i+M^2 (mod k)."""
    k = 2 * M * M + 1
    adj = [[False] * (k + 1) for _ in range(k + 1)]
    for i in range(1, k + 1):
        for s in range(1, M * M + 1):
            j = (i - 1 + s) % k + 1
            adj[i][j] = True
    return adj


def transitive_tournament(k: int, reverse: bool = False) -> Tournament:
    adj = [[False] * (k + 1) for _ in range(k + 1)]
    for i in range(1, k + 1):
        for j in range(1, k + 1):
            if i != j:
                adj[i][j] = (i > j) if reverse else (i < j)
    return adj


def pseudorandom_tournament(k: int, seed: int) -> Tournament:
    """Deterministic tournament from a 64-bit linear congruential generator."""
    adj = [[False] * (k + 1) for _ in range(k + 1)]
    state = seed & ((1 << 64) - 1)
    for i in range(1, k + 1):
        for j in range(i + 1, k + 1):
            state = (6364136223846793005 * state + 1442695040888963407) % (1 << 64)
            if state >> 63:
                adj[i][j] = True
            else:
                adj[j][i] = True
    return adj


def is_tournament(adj: Tournament) -> bool:
    k = len(adj) - 1
    for i in range(1, k + 1):
        if adj[i][i]:
            return False
        for j in range(i + 1, k + 1):
            if adj[i][j] == adj[j][i]:
                return False
    return True


def outdegrees(adj: Tournament) -> list[int]:
    k = len(adj) - 1
    return [sum(adj[i][1:]) for i in range(1, k + 1)]


# ----------------------------------------------------------------------------
# Bad sets
# ----------------------------------------------------------------------------

def is_bad(adj: Tournament, label: Label, I: Iterable[int]) -> bool:
    """Direct definition: for each j in I the labels a(i, j), i -> j in I, agree."""
    members = list(I)
    for j in members:
        seen = {label(i, j) for i in members if i != j and adj[i][j]}
        if len(seen) > 1:
            return False
    return True


def max_bad_set(adj: Tournament, label: Label, stop_at: int | None = None) -> list[int]:
    """Exact maximum bad set by backtracking over increasing vertex sequences.

    Bad sets are closed under taking subsets, so every bad set is reached by
    adding its vertices in increasing order.  If ``stop_at`` is given, the
    search returns as soon as a bad set of that size is found.
    """
    k = len(adj) - 1
    best: list[int] = []
    current: list[int] = []
    required: dict[int, int] = {}  # j -> common label of its in-neighbours so far

    def extend(start: int) -> bool:
        nonlocal best
        if len(current) > len(best):
            best = list(current)
            if stop_at is not None and len(best) >= stop_at:
                return True
        if len(current) + (k - start + 1) <= len(best):
            return False
        for v in range(start, k + 1):
            # Labels on edges into v from the current set must agree.
            into_v = {label(i, v) for i in current if adj[i][v]}
            if len(into_v) > 1:
                continue
            # Edges v -> j must match j's existing requirement.
            updates: list[int] = []
            ok = True
            for j in current:
                if adj[v][j]:
                    lab = label(v, j)
                    if j in required:
                        if required[j] != lab:
                            ok = False
                            break
                    else:
                        updates.append(j)
            if not ok:
                continue
            for j in updates:
                required[j] = label(v, j)
            if into_v:
                required[v] = next(iter(into_v))
            current.append(v)
            if extend(v + 1):
                return True
            current.pop()
            required.pop(v, None)
            for j in updates:
                del required[j]
        return False

    extend(1)
    return best


def max_bad_size_bruteforce(adj: Tournament, label: Label) -> int:
    """Independent check: test every subset of [k] with the direct definition."""
    k = len(adj) - 1
    best = 0
    for mask in range(1 << k):
        size = mask.bit_count()
        if size <= best:
            continue
        members = [v + 1 for v in range(k) if mask >> v & 1]
        if is_bad(adj, label, members):
            best = size
    return best


def tight_example(k: int) -> list[int]:
    """A bad set of size h + 1 for the transitive tournament i -> j iff i < j.

    In 0-based terms the members are 2^p - 1 for p = 0, ..., h - 1, together
    with k - 1.  Every smaller member of the set first differs from a member
    in that member's top bit, so each vertex sees a single label from its
    in-neighbours (the smaller members).  Returned 1-based.
    """
    h = height(k)
    return [(1 << p) for p in range(h)] + [k]


# ----------------------------------------------------------------------------
# Parameter inequalities used by 03-separation.tex
# ----------------------------------------------------------------------------

def manuscript_parameters(M: int) -> dict[str, int]:
    k = 2 * M * M + 1
    h = height(k)
    return {"M": M, "k": k, "h": h, "t": h + 2, "r_manuscript": isqrt_ceil(M)}


def epsilon_condition(M: int, r: int, t: int) -> bool:
    """max(r, t) <= 2 sqrt(M), the bound used at 03-separation.tex:55-60."""
    m = max(r, t)
    return m * m <= 4 * M


# ----------------------------------------------------------------------------
# Checks and negative controls
# ----------------------------------------------------------------------------

def const_label(i: int, j: int) -> int:
    return 1


def lsb_parity_label(i: int, j: int) -> int:
    """A wrong labelling with values in [2]: parity of the MSB position."""
    return 1 + (msb_label(i, j) % 2)


CONTROLS = {
    # All labels equal: every set is bad, so the bound h + 1 must fail.
    "constant-label": dict(label=const_label, bound_shift=0),
    # Claim the bound h instead of h + 1: fails because h + 1 is attained.
    "bound-too-small": dict(label=msb_label, bound_shift=-1),
    # Coarsen the labelling to two values: larger bad sets appear.
    "parity-label": dict(label=lsb_parity_label, bound_shift=0),
    # Claim the inequality of 03-separation.tex:56 from M = 50; it fails for M <= 56.
    "epsilon-below-57": dict(label=msb_label, bound_shift=0, epsilon_from=50),
}


def run(control: str | None) -> bool:
    spec = CONTROLS.get(control, dict(label=msb_label, bound_shift=0)) if control else \
        dict(label=msb_label, bound_shift=0)
    label: Label = spec["label"]
    shift: int = spec["bound_shift"]
    epsilon_from: int = spec.get("epsilon_from", 81)
    ok = True

    def report(name: str, passed: bool, detail: str) -> None:
        nonlocal ok
        ok = ok and passed
        print(f"[{'ok' if passed else 'FAIL'}] {name}: {detail}")

    # 1. Labels lie in [h] and are symmetric.
    for k in (2, 3, 9, 19, 33, 51, 64, 65):
        h = height(k)
        vals = {label(i, j) for i in range(1, k + 1) for j in range(1, k + 1) if i != j}
        report(f"labels in [h], k={k}", vals <= set(range(1, h + 1)) and
               all(label(i, j) == label(j, i) for i in range(1, k + 1)
                   for j in range(1, k + 1) if i != j),
               f"h={h}, values={sorted(vals)}")

    # 2. Manuscript tournaments are regular tournaments with outdegree M^2.
    for M in (2, 3, 4, 5):
        adj = cyclic_tournament(M)
        report(f"cyclic tournament M={M}", is_tournament(adj) and
               set(outdegrees(adj)) == {M * M}, f"k={2 * M * M + 1}, outdegree {M * M}")

    # 3. Exact maximum bad sets: bound h + 1 (+ shift) for several tournaments.
    cases: list[tuple[str, Tournament]] = []
    for M in (2, 3, 4, 5):
        cases.append((f"cyclic M={M}", cyclic_tournament(M)))
    for k in (8, 16, 17, 32, 33):
        cases.append((f"transitive k={k}", transitive_tournament(k)))
        cases.append((f"reverse-transitive k={k}", transitive_tournament(k, reverse=True)))
    for k, seed in ((16, 1), (17, 2), (24, 3), (32, 4), (33, 5), (40, 6)):
        cases.append((f"pseudorandom k={k} seed={seed}", pseudorandom_tournament(k, seed)))
    for name, adj in cases:
        k = len(adj) - 1
        bound = height(k) + 1 + shift
        found = max_bad_set(adj, label, stop_at=bound + 1)
        passed = len(found) <= bound and is_bad(adj, label, found)
        detail = f"k={k}, h={height(k)}, bound={bound}, largest found={len(found)}"
        if len(found) > bound:
            detail += f", violating set {found}"
        report(f"max bad set, {name}", passed, detail)

    # 4. Tightness: the bound h + 1 is attained (transitive tournament).
    for k in (8, 16, 32, 64, 1024):
        h = height(k)
        ex = tight_example(k)
        adj_ok = all(1 <= v <= k for v in ex) and len(set(ex)) == h + 1
        # Bad for i -> j iff i < j: in-neighbours of v are the smaller members.
        bad = adj_ok and all(len({label(i, v) for i in ex if i < v}) <= 1 for v in ex)
        report(f"tight example k={k}", bad, f"bad set of size h+1={h + 1}: {ex[:6]}...")

    # 5. Parameter inequality at 03-separation.tex:55-60 with t = h + 2.
    #    Finite range here; PROOF.md gives the argument for all M >= 81.
    bad_eps = [M for M in range(epsilon_from, 20001)
               if not epsilon_condition(M, isqrt_ceil(M), manuscript_parameters(M)["t"])]
    report("max(ceil(sqrt M), h+2) <= 2 sqrt M", not bad_eps,
           f"M in [{epsilon_from}, 20000], failures={bad_eps[:5]}")
    # 6. h <= ceil(sqrt M) once M >= 290 (it fails at M = 289), so the labels fit in the manuscript's [r].
    bad_fit = [M for M in range(290, 20001)
               if manuscript_parameters(M)["h"] > isqrt_ceil(M)]
    report("h <= ceil(sqrt M) for M >= 290", not bad_fit, f"failures={bad_fit[:5]}")
    smallest = manuscript_parameters(9 ** 2)
    report("smallest theorem case d=1, M=9^2=81", smallest == {
        "M": 81, "k": 13123, "h": 14, "t": 16, "r_manuscript": 9},
        f"{smallest}; h > r here, so use r = max(ceil(sqrt M), h) or M >= 290")
    d2 = manuscript_parameters(9 ** 3)
    report("d=2, M=9^3=729: labels fit in [ceil(sqrt M)]", d2["h"] <= d2["r_manuscript"] and
           epsilon_condition(729, d2["r_manuscript"], d2["t"]), f"{d2}")

    print(f"RESULT: {'passes' if ok else 'fails'}")
    return ok


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--negative-control", choices=sorted(CONTROLS))
    args = parser.parse_args(argv)
    return 0 if run(args.negative_control) else 1


if __name__ == "__main__":
    sys.exit(main())
