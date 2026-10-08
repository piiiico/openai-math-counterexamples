#!/usr/bin/env python3
"""C002 row 192: square-root degree bound -- result: not-explicit.

Theorem (preprints/Unbounded-Violations-of-the-Square-Root-Degree-Bound-September-26-2026/build/sections/
00-introduction.tex:23-34): for every C > 0 there is f:{-1,1}^n -> {-1,1} with sum_i fhat({i}) > C sqrt(deg f).
00-introduction.tex:41-42: "The dimension and all copy counts in the construction are finite; we do not obtain
useful bounds on their growth."  No explicit f is given, so the violation cannot be checked by a program.
What a program CAN do: exhaust every Boolean function on n <= 4 inputs (2^16 = 65,536 at n=4) and report the
largest ratio sum_i fhat({i}) / sqrt(deg f).  This bounds from below how large any explicit witness must be
for a given C; it says nothing about the theorem.  Exact arithmetic (Fractions; sqrt compared by squaring).
"""
from fractions import Fraction as Fr
from itertools import product, combinations
import sys

def best(n):
    pts = list(product((-1, 1), repeat=n)); N = len(pts)
    subsets = [S for k in range(n + 1) for S in combinations(range(n), k)]
    chi = {S: [1 if sum(p[i] == -1 for i in S) % 2 == 0 else -1 for p in pts] for S in subsets}
    top = (Fr(-1), 1, None)
    for mask in range(1, 2 ** N - 1):  # nonconstant
        f = [1 if (mask >> t) & 1 else -1 for t in range(N)]
        coef = {S: sum(a * b for a, b in zip(f, chi[S])) for S in subsets}  # N * fhat(S)
        deg = max(len(S) for S, c in coef.items() if c)
        lin = Fr(sum(coef[(i,)] for i in range(n)), N)
        # compare lin/sqrt(deg) via lin^2/deg with sign
        r2 = lin * lin / deg if lin > 0 else -lin * lin / deg
        if r2 > top[0]: top = (r2, deg, mask)
    return top
ok = True
for n in range(1, 5):
    r2, deg, mask = best(n)
    print(f"n={n}: max sum_i fhat(i)/sqrt(deg) = sqrt({r2}) = {float(r2) ** 0.5:.6f} at deg {deg} (truth-table mask {mask})")
ok &= best(3)[0] >= Fr(3, 4)  # control: majority of 3 gives (3/2)/sqrt3, ratio^2 = 3/4
print("control MAJ3 ratio^2 >= 3/4:", ok)
print("RESULT: not-explicit (theorem gives no explicit f; exhaustive n<=4 shows no small witness for C >= the maxima above)")
sys.exit(0 if ok else 1)
