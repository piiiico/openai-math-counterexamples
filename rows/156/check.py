#!/usr/bin/env python3
"""C002 row 156: Borsuk fails in dimension nine -- result: not-finite.

Theorem (preprints/A-nine-dimensional-counterexample-to-Borsuks-covering-assertion-September-23-2026/
build/sections/introduction.tex:18-26): X = {uu^T : u in R^4, |u|=1} in the trace-one hyperplane of Sym_4(R),
Frobenius metric, has diameter sqrt2 and cannot be covered by ten sets of diameter < sqrt2.
introduction.tex:30-31: "Its witness is the full compact projector image of real projective three-space."
The witness is a continuum and the covering bound is proved by mod-2 degree (topology.tex), so there is no
finite object to compute.  This script checks only the metric facts the proof starts from, exactly:
  ||uu^T - vv^T||_F^2 = 2 - 2 (u.v)^2 for unit u, v  (so diameter sqrt2, attained iff u is orthogonal to v),
  and the trace-one symmetric 4x4 matrices form a 9-dimensional affine space.
Rational unit vectors (Pythagorean quadruples / 4-term sums) make the check exact.
"""
from fractions import Fraction as Fr
from itertools import product
import sys

def unit_vectors(limit=6):
    out = []
    for v in product(range(-limit, limit + 1), repeat=4):
        n2 = sum(x * x for x in v)
        r = int(round(n2 ** 0.5))
        if n2 and r * r == n2:
            out.append(tuple(Fr(x, r) for x in v))
    return out
U = unit_vectors()
proj = lambda u: [[u[i] * u[j] for j in range(4)] for i in range(4)]
ok, maxd, n = True, Fr(0), 0
for a in range(0, len(U), 7):
    for b in range(0, len(U), 11):
        u, v = U[a], U[b]; P, Q = proj(u), proj(v)
        d2 = sum((P[i][j] - Q[i][j]) ** 2 for i in range(4) for j in range(4))
        dot = sum(x * y for x, y in zip(u, v))
        ok &= d2 == 2 - 2 * dot * dot and sum(P[i][i] for i in range(4)) == 1
        ok &= (d2 == 2) == (dot == 0)
        maxd = max(maxd, d2); n += 1
dim = 4 * 5 // 2 - 1
print(f"{len(U)} exact rational unit vectors, {n} pairs: identity ||P-Q||^2 = 2-2(u.v)^2 and tr=1:", ok)
print("max squared distance seen:", maxd, "(sqrt2 diameter attained iff orthogonal:", ok, ") ; affine dim of tr=1 Sym_4:", dim)
ok &= maxd == 2 and dim == 9
print("RESULT: not-finite (metric premises:", "hold" if ok else "FAIL", "; the ten-set covering bound is topological, no finite check)")
sys.exit(0 if ok else 1)
