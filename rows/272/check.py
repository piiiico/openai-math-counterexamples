#!/usr/bin/env python3
"""C002 row 272: the explicit 4x4 PPT map behind the C^10 (x) C^10 state, checked by a route the paper skips (stdlib only).

Claims (preprints/Entanglement-with-zero-distillable-secret-key-in-local-dimension-ten-September-27-2026/
build/source/sections/certificate.tex):
  Lemma lem:pencil-ppt (39-76): with the integer 6x4 matrices M_0..M_3 of eq. explicit-matrices (19-31),
      M_i^T M_j = M_j^T M_i for all i,j  (so L(E_ij) = M_i^T M_j is PPT), and L(P_e0) = M_0^T M_0 = 36 I_4.
  Proposition prop:twenty-directions (78-85): the directions [x] in P^3(C) with rank M(x) < 4 are exactly
      twenty distinct points, each with a representative (1,t1,t2,t3), and every nonzero homogeneous
      quadratic vanishes on at most nine of them.
The paper proves the proposition through modular reductions at 41, 131, 139 and a Galois argument; it says
(certificate.tex:105-107) its checker "does not enumerate the twenty complex directions or their ten-point
determinants". This script does exactly that, and nothing modular:

  A. Exact integer arithmetic: all 16 products M_i^T M_j, their symmetry, and M_0^T M_0 = 36 I.
  B. The twenty points, numerically: Newton's method in complex double precision on the square system
     M(x) y = 0, s.x = 1, r.y = 1 (8 equations, 8 unknowns, random charts s, r), from seeded random starts
     until 3000 starts in a row add no new point; each point is then rescaled to (1, t1, t2, t3).
     Each point is accepted only if the smallest singular value of M(x)/|M(x)| (via the 4x4 Gram matrix)
     is below 1e-10, and the points must be pairwise far apart. Twenty is also the Porteous degree C(6,3)
     of a zero-dimensional rank<=3 locus of a 6x4 linear pencil on P^3, so twenty distinct points is all of them.
  C. The quadric claim, by brute force: for every one of the C(20,10) = 184,756 ten-point subsets, the 10x10
     matrix of quadratic monomials evaluated at the unit-normalised points must be nonsingular. Reported as
     the minimum, over subsets, of |det| divided by the product of row norms (Hadamard ratio, in (0,1]).
     A subset on which some quadric vanishes has ratio 0 up to rounding (~1e-13).
  Negative arms (each must fire, or the check is blind):
     A-: one entry of M_3 changed by 1 breaks the symmetry check.
     C-: ten of the twenty points replaced by points on the quadric x0*x1 = x2*x3 gives a ratio near 0.
"""
import cmath, itertools, random, sys
from math import comb

M = [
 [[6,0,0,0],[0,6,0,0],[0,0,6,0],[0,0,0,6],[0,0,0,0],[0,0,0,0]],
 [[-12,0,0,0],[0,-6,0,0],[0,0,6,0],[0,0,0,12],[-6,0,6,6],[-6,-6,6,0]],
 [[0,6,-2,0],[6,6,0,2],[-2,0,10,0],[0,2,0,24],[0,0,0,6],[0,-6,6,-6]],
 [[0,0,-4,-3],[0,-2,-3,-4],[-4,-3,11,6],[-3,-4,6,25],[6,6,0,0],[0,-6,6,6]],
]
out = []
def say(s): out.append(s); print(s)
ok = True

# ---------- A. exact block identities ----------
def gram(A, B): return [[sum(A[r][a] * B[r][b] for r in range(6)) for b in range(4)] for a in range(4)]
def sym_ok(Ms):
    return all(gram(Ms[i], Ms[j]) == gram(Ms[j], Ms[i]) for i in range(4) for j in range(4))
symA = sym_ok(M)
idA = gram(M[0], M[0]) == [[36 if a == b else 0 for b in range(4)] for a in range(4)]
Mbad = [[row[:] for row in Mi] for Mi in M]; Mbad[3][0][2] += 1
negA = not sym_ok(Mbad)
say(f"A. M_i^T M_j symmetric for all 16 (i,j): {symA}; M_0^T M_0 = 36 I: {idA}; negative arm (M_3[0][2]+1) breaks symmetry: {negA}")
ok &= symA and idA and negA

# ---------- B. the twenty rank-loss directions ----------
def Mx(x): return [[sum(x[k] * M[k][r][c] for k in range(4)) for c in range(4)] for r in range(6)]
def solve(A, b):
    n = len(A); A = [row[:] + [b[i]] for i, row in enumerate(A)]
    for i in range(n):
        p = max(range(i, n), key=lambda j: abs(A[j][i])); A[i], A[p] = A[p], A[i]
        if A[i][i] == 0: return None
        for j in range(i + 1, n):
            f = A[j][i] / A[i][i]
            for k in range(i, n + 1): A[j][k] -= f * A[i][k]
    x = [None] * n
    for i in reversed(range(n)): x[i] = (A[i][n] - sum(A[i][k] * x[k] for k in range(i + 1, n))) / A[i][i]
    return x
def det(A):
    A = [row[:] for row in A]; n = len(A); d = 1 + 0j
    for i in range(n):
        p = max(range(i, n), key=lambda j: abs(A[j][i]))
        if A[p][i] == 0: return 0j
        if p != i: A[i], A[p] = A[p], A[i]; d = -d
        d *= A[i][i]
        for j in range(i + 1, n):
            f = A[j][i] / A[i][i]
            for k in range(i, n): A[j][k] -= f * A[i][k]
    return d
def smin_ratio(x):
    """smallest/largest singular value of M(x), from the 4x4 Hermitian Gram matrix via char-poly-free power steps."""
    A = Mx(x); G = [[sum(A[r][a].conjugate() * A[r][b] for r in range(6)) for b in range(4)] for a in range(4)]
    tr = sum(G[i][i].real for i in range(4))
    # det(G) = prod of squared singular values; with the other three bounded by tr, s_min^2 >= det/tr^3
    # det/(sum of 3x3 principal minors) = 1/sum(1/lambda_i) lies in [lambda_min/4, lambda_min]: within 2x of s_min.
    d = det(G).real
    m3 = sum(det([[G[a][b] for b in idx] for a in idx]).real for idx in itertools.combinations(range(4), 3))
    return (max(d, 0) / m3) ** 0.5 / tr ** 0.5 if m3 > 0 else 0.0
rng = random.Random(272)
r = [complex(rng.gauss(0, 1), rng.gauss(0, 1)) for _ in range(4)]   # random charts for y and for x, so no
s_ = [complex(rng.gauss(0, 1), rng.gauss(0, 1)) for _ in range(4)]  # point is missed for sitting near x0 = 0
pts = []; kers = []
starts = 0; since_new = 0
while since_new < 3000 and starts < 20000:
    starts += 1; since_new += 1
    z = [complex(rng.gauss(0, 1), rng.gauss(0, 1)) for _ in range(8)]   # x0..x3, y0..y3
    for _ in range(200):
        x, y = z[:4], z[4:]; A = Mx(x)
        F = [sum(A[i][c] * y[c] for c in range(4)) for i in range(6)]
        F += [sum(s_[c] * x[c] for c in range(4)) - 1, sum(r[c] * y[c] for c in range(4)) - 1]
        J = [[sum(M[k][i][c] * y[c] for c in range(4)) for k in range(4)] + [A[i][c] for c in range(4)] for i in range(6)]
        J += [s_[:] + [0] * 4, [0] * 4 + r[:]]
        dz = solve(J, [-f for f in F])
        if dz is None or any(abs(v) > 1e8 for v in z): break
        z = [a + b for a, b in zip(z, dz)]
        if max(abs(v) for v in dz) < 1e-15 * (1 + max(abs(v) for v in z)): break
    if dz is None or abs(z[0]) < 1e-8: continue
    x = [v / z[0] for v in z[:4]]                                        # representative (1, t1, t2, t3)
    if any(abs(v) > 1e6 for v in x) or smin_ratio(x) > 1e-10: continue
    if all(max(abs(a - b) for a, b in zip(x, p)) > 1e-6 for p in pts):
        pts.append(x); kers.append(z[4:]); since_new = 0
worst = max(smin_ratio(p) for p in pts)
sep = min(max(abs(a - b) for a, b in zip(p, q)) for p, q in itertools.combinations(pts, 2))
say(f"B. Newton starts: {starts}; distinct rank-loss points found: {len(pts)} (Porteous degree C(6,3) = {comb(6,3)}); "
    f"max s_min/|M(x)| over them: {worst:.1e}; min pairwise distance: {sep:.3f}; real points: {sum(all(abs(v.imag) < 1e-9 for v in p) for p in pts)}")
ok &= len(pts) == 20 and worst < 1e-10 and sep > 1e-3

# ---------- C. no quadric through ten of them ----------
from decimal import Decimal as D, getcontext
getcontext().prec = 60
def quad_row(x):
    n = sum(abs(v) ** 2 for v in x) ** 0.5; x = [v / n for v in x]
    return [x[i] * x[j] for i in range(4) for j in range(i, 4)]
def ratio_of(rows):
    d = abs(det(rows))
    for row in rows: d /= sum(abs(v) ** 2 for v in row) ** 0.5
    return d
def refine_real(x, y):
    """Newton in 60-digit Decimal on M(1,t) y = 0, y.y0-chart, for a REAL point; returns (t, residual)."""
    t = [D(repr(v.real)) for v in x[1:]]; yy = [D(repr((v / y[0]).real)) for v in y]
    for _ in range(8):
        xx = [D(1)] + t
        A = [[sum(xx[k] * M[k][i][c] for k in range(4)) for c in range(4)] for i in range(6)]
        F = [sum(A[i][c] * yy[c] for c in range(4)) for i in range(6)] + [yy[0] - 1]
        J = [[sum(M[k + 1][i][c] * yy[c] for c in range(4)) for k in range(3)] + [A[i][c] for c in range(4)] for i in range(6)]
        J.append([D(0)] * 3 + [D(1), D(0), D(0), D(0)])
        dz = solve(J, [-f for f in F])
        t = [a + b for a, b in zip(t, dz[:3])]; yy = [a + b for a, b in zip(yy, dz[3:])]
    return [D(1)] + t, max(abs(f) for f in F)
def quad_row_dec(x):
    n = sum(v * v for v in x).sqrt(); x = [v / n for v in x]
    return [x[i] * x[j] for i in range(4) for j in range(i, 4)]
if len(pts) == 20:
    real = all(abs(v.imag) < 1e-9 for p in pts for v in p)
    rows = [quad_row(p) for p in pts]
    norms = [sum(abs(v) ** 2 for v in row) ** 0.5 for row in rows]
    allr = []
    for S in itertools.combinations(range(20), 10):
        d = abs(det([rows[i] for i in S]))
        for i in S: d /= norms[i]
        allr.append((d, S))
    allr.sort()
    say(f"C. ten-point subsets: {len(allr)}; float min Hadamard ratio |det|/prod(row norms) = {allr[0][0]:.3e}")
    ok &= len(allr) == comb(20, 10)
    if real:   # all twenty are real: refine each to 60 digits and recompute the 50 smallest subsets exactly-ish
        ref = [refine_real(p, k) for p, k in zip(pts, kers)]
        resid = max(r_ for _, r_ in ref)
        drows = [quad_row_dec(x) for x, _ in ref]
        worst_dis = D(0); dmin = None
        for fr, S in allr[:50]:
            sub_ = [r_[:] for r_ in (drows[i] for i in S)]
            # Decimal determinant by elimination
            n = 10; dd = D(1)
            for i in range(n):
                piv = max(range(i, n), key=lambda j: abs(sub_[j][i]))
                if piv != i: sub_[i], sub_[piv] = sub_[piv], sub_[i]; dd = -dd
                dd *= sub_[i][i]
                for j in range(i + 1, n):
                    f = sub_[j][i] / sub_[i][i]
                    for k in range(i, n): sub_[j][k] -= f * sub_[i][k]
            for i in S: dd /= sum(v * v for v in drows[i]).sqrt()
            dd = abs(dd)
            dmin = dd if dmin is None or dd < dmin else dmin
            worst_dis = max(worst_dis, abs(D(repr(fr)) - dd) / dd)
        say(f"   60-digit refinement: max minor residual {float(resid):.1e}; 50 smallest subsets recomputed at 60 digits: "
            f"min ratio {float(dmin):.4e}, worst float-vs-60-digit relative disagreement {float(worst_dis):.1e} (subset {list(allr[0][1])})")
        ok &= resid < D("1e-40") and dmin > D("1e-30") and worst_dis < D("1e-2")
    else:
        ok = False; say("   non-real points present: 60-digit arm not implemented, no verdict")
    # negative arm: ten points on the quadric x0*x1 = x2*x3
    bad = [[1, a * b, a, b] for a, b in [(complex(rng.gauss(0, 1), rng.gauss(0, 1)), complex(rng.gauss(0, 1), rng.gauss(0, 1))) for _ in range(10)]]
    nr = ratio_of([quad_row(p) for p in bad])
    say(f"C-. negative arm: ten points on the quadric x0*x1 - x2*x3 = 0 give float ratio {nr:.1e} (must be < 1e-14, i.e. the noise floor sits far below the true minimum)")
    ok &= nr < 1e-14
pts_s = sorted(pts, key=lambda p: (round(p[1].real, 6), round(p[1].imag, 6)))
for p in pts_s: say("   t = (" + ", ".join(f"{v.real:+.9f}{v.imag:+.9f}i" for v in p[1:]) + ")")
res = "holds" if ok else "fails"
say(f"RESULT: {res}")
open(__file__.replace("check.py", "output.txt"), "w").write("\n".join(out) + "\n")
sys.exit(0 if ok else 1)
