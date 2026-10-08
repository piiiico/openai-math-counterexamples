#!/usr/bin/env python3
"""C002 row 088: Brannen's simplex maximum vs T10 x T10 (exact rational arithmetic, stdlib only).

Claim (preprints/A-product-counterexample-to-the-simplex-maximum-for-projection-body-volume-September-24-2026/
build/main.tex:90-100): K = T10 x T10 in R^20 has R_20(K)/c_20 = 121*C(20,10)/(21*2^20) = 22355476/22020096 > 1,
where R_d(K) = |Pi K| / |K|^(d-1) and c_d = (d+1) d^d / d!  (main.tex, eq. functional).

Independent route (does NOT use the paper's product lemma R(AxB)=R(A)R(B)):
for a polytope with facets F (outward unit normal u_F, area a_F), Cauchy's formula gives
h_{Pi K}(x) = 1/2 * sum_F a_F |<x,u_F>|, so Pi K is the zonotope sum_F [-v_F, v_F] with v_F = a_F u_F / 2,
and |zonotope| = 2^d * sum over d-subsets S of |det(v_S)|.  We build the 22 facet vectors of K in R^20,
sum all C(22,20)=231 determinants exactly, and divide.  Controls: the same code on the simplex T_d must
return exactly c_d (d = 2, 3, 20), and on the cube [0,1]^3 must return |Pi C|=8.
"""
from fractions import Fraction as Fr
from itertools import combinations
from math import comb, factorial
import sys

def det(M):
    """Exact determinant (Fraction Gaussian elimination)."""
    M = [row[:] for row in M]; n = len(M); d = Fr(1)
    for c in range(n):
        p = next((r for r in range(c, n) if M[r][c] != 0), None)
        if p is None: return Fr(0)
        if p != c: M[c], M[p] = M[p], M[c]; d = -d
        d *= M[c][c]
        for r in range(c + 1, n):
            f = M[r][c] / M[c][c]
            if f:
                M[r] = [a - f * b for a, b in zip(M[r], M[c])]
    return d

def zonotope_volume(gens, dim):
    return 2**dim * sum(abs(det([list(g) for g in S])) for S in combinations(gens, dim))

def simplex_area_vectors(n):
    """a_F * u_F for T_n = conv(0, e_1..e_n): n coordinate facets + 1 slanted facet."""
    s = Fr(1, factorial(n - 1))
    vs = [[-s if k == i else Fr(0) for k in range(n)] for i in range(n)]
    vs.append([s] * n)  # slanted facet: area sqrt(n)/(n-1)!, normal (1..1)/sqrt(n)
    assert all(abs(sum(v[k] for v in vs)) == 0 for k in range(n))  # Minkowski: sum a_F u_F = 0
    return vs

def R_simplex(n):
    vol = Fr(1, factorial(n))
    gens = [[x / 2 for x in v] for v in simplex_area_vectors(n)]
    return zonotope_volume(gens, n) / vol**(n - 1)

def R_product(n):
    """K = T_n x T_n in R^{2n}: facets F x T_n and T_n x G; area = a_F * vol(T_n)."""
    vol = Fr(1, factorial(n)); d = 2 * n
    gens = []
    for v in simplex_area_vectors(n):
        gens.append([x * vol / 2 for x in v] + [Fr(0)] * n)
        gens.append([Fr(0)] * n + [x * vol / 2 for x in v])
    return zonotope_volume(gens, d) / (vol * vol)**(d - 1)

def c(d): return Fr((d + 1) * d**d, factorial(d))

# controls
cube = [[Fr(1) if k == i else Fr(0) for k in range(3)] for i in range(3)]
cube = [[x / 2 for x in v] for v in cube + [[-x for x in v] for v in cube]]
assert zonotope_volume(cube, 3) == 8, "control: |Pi [0,1]^3| must be 8"
for d in (2, 3, 4, 20):
    assert R_simplex(d) == c(d), f"control: R_{d}(T_{d}) != c_{d}"
print("controls: |Pi cube|=8; R_d(T_d)=c_d for d=2,3,4,20 (c_3 =", c(3), ")")

ratio = R_product(10) / c(20)
paper = Fr(121 * comb(20, 10), 21 * 2**20)
print("computed R_20(T10xT10)/c_20 =", ratio, "=", float(ratio))
print("paper    121*C(20,10)/(21*2^20) =", paper, "; paper's decimal form 22355476/22020096 =", Fr(22355476, 22020096))
agree = ratio == paper == Fr(22355476, 22020096)
print("RESULT:", "holds" if agree and ratio > 1 else "fails", "| exact match with paper:", agree, "| ratio > 1:", ratio > 1)
sys.exit(0 if agree and ratio > 1 else 1)
