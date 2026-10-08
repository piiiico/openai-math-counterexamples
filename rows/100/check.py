#!/usr/bin/env python3
"""C002 row 100: the finite cylinder covering of the regular tetrahedron, at eps = 1/2000 (stdlib only).

Claim (preprints/Finite-angular-cylinder-covers-below-the-half-area-bound-September-27-2026/
build/sections/introduction.tex:32-43, construction in build/sections/construction.tex:53-125):
K = {(x,y,Ht): 0<=t<=1, |x|<=1-t, |y|<=t}, H = sqrt2, has A_min(K) = sqrt2, and for 0 < eps <= 1/2000
the 2n cylinders P_j + R v_j, Q_j + R w_j (n = ceil(2/eps^2)) cover K with
    (1/sqrt2) * sum |B_i| = 1/2 - 13/6000 eps^2 + O(eps^4),  remainder at most 2 eps^4,
so the total base area is strictly below A_min(K)/2.

What this script computes, at the paper's own boundary value eps = 1/2000 (n = 8,000,000 sectors):
  A. A_min(K): face area vectors rebuilt from the four vertices; A(u) = 1/2 sum |N.u| minimised on a
     sphere grid plus local refinement. Must be sqrt2, attained at u = (1,0,0).
  B. AREA, without the paper's Taylor argument: every one of the 2n perpendicular bases is built as a
     3D triangle, projected onto the plane perpendicular to its axis, and its area summed (math.fsum).
     Checked on a sample of bases against the paper's closed form (area.tex:15-19); then the full sum
     from that closed form. Must sit within 2 eps^4 of 1/2 - 13/6000 eps^2 AND below 1/2.
  C. COVERAGE, sampled, exact rational arithmetic: random rational points of K, concentrated in the band
     |t - 1/2| <= 4 eps^2 where the two families hand over (coverage.tex:46-70), plus the four vertices
     and edge midpoints. A point counts as covered only if an exact Fraction test puts it inside some
     cylinder. This is evidence, not a proof: sampling cannot see a gap smaller than its spacing.
  Negative arm: the same sampler with the radial enlargement removed (T_j = 1/2, i.e. the tilt without
     the cutoffs T_j of construction.tex:98-102) must FIND uncovered points, or the sampler is blind.
"""
from fractions import Fraction as Fr
from math import ceil, sqrt, fsum, floor
import random, sys

EPS = Fr(1, 2000)
ETA = Fr(1, 1000)
N = ceil(2 / EPS**2)            # 8,000,000
DELTA = Fr(2, N)
H = sqrt(2.0)

def q(i): return -1 + i * DELTA
def alpha(j): return (1 + q(j) * q(j + 1)) / 4
def beta(j): return (q(j) + q(j + 1)) / 4
def dfun(x): return x * x * (1 + x * x) / 16
def M(j): return ETA + max(dfun(q(j)), dfun(q(j + 1)))   # d is even and increasing in |q|
def T(j, enlarge=True): return Fr(1, 2) + (EPS**2 * M(j) if enlarge else 0)

out = []
def say(s): out.append(s); print(s)

# ---------- A. A_min(K) ----------
V = [(1, 0, 0), (-1, 0, 0), (0, 1, H), (0, -1, H)]
def sub(a, b): return tuple(x - y for x, y in zip(a, b))
def cross(a, b): return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
def dot(a, b): return sum(x * y for x, y in zip(a, b))
cent = tuple(sum(v[k] for v in V) / 4 for k in range(3))
faces = []
for skip in range(4):
    a, b, c = [V[i] for i in range(4) if i != skip]
    n = tuple(x / 2 for x in cross(sub(b, a), sub(c, a)))      # area vector, |n| = face area
    if dot(n, sub(a, cent)) < 0: n = tuple(-x for x in n)
    faces.append(n)
assert all(abs(sqrt(dot(n, n)) - sqrt(3)) < 1e-12 for n in faces), "faces must be equilateral, side 2"
def A(u): return 0.5 * sum(abs(dot(n, u)) for n in faces)
best = (9, None)
G = 400
from math import pi, sin, cos
for a in range(G + 1):
    th = pi * a / G
    for b in range(2 * G):
        ph = pi * b / G
        u = (sin(th) * cos(ph), sin(th) * sin(ph), cos(th))
        best = min(best, (A(u), u))
u = best[1]
for step in [1e-3, 1e-4, 1e-5, 1e-6, 1e-7]:   # local refinement
    for _ in range(200):
        cand = [tuple(u[k] + step * random.Random(7).uniform(-1, 1) * (k == i) for k in range(3)) for i in range(3)]
        cand += [tuple(u[k] - step * (k == i) for k in range(3)) for i in range(3)]
        cand += [tuple(u[k] + step * (k == i) for k in range(3)) for i in range(3)]
        cand = [tuple(c / sqrt(dot(w, w)) for c in w) for w in cand]
        nb = min((A(w), w) for w in cand)
        if nb[0] < best[0]: best, u = nb, nb[1]
        else: break
amin = best[0]
ok_A = abs(amin - H) < 1e-9 and abs(A((1, 0, 0)) - H) < 1e-15
say(f"A. A_min(K) by grid+refine = {amin:.12f}; sqrt2 = {H:.12f}; A(1,0,0) = {A((1,0,0)):.12f} -> {'ok' if ok_A else 'MISMATCH'}")

# ---------- B. area ----------
from decimal import Decimal as Dc, getcontext
getcontext().prec = 50
HD = Dc(2).sqrt()
def tri_perp_area(P0, P1, P2, v):
    """Area of the projection of triangle P0P1P2 onto v-perp, by projecting the three VERTICES (50 digits:
    the sector triangles are 2.5e-7 wide, so double precision loses ~9 digits to cancellation)."""
    vn = dot(v, v).sqrt(); v = tuple(x / vn for x in v)
    def pr(p): d = dot(p, v); return tuple(p[k] - d * v[k] for k in range(3))
    a, b, c = pr(P0), pr(P1), pr(P2)
    cr = cross(sub(b, a), sub(c, a))
    return dot(cr, cr).sqrt() / 2
def D_(f): return Dc(f.numerator) / Dc(f.denominator)
def base_areas_geometric(j):
    Tj, qa, qb, al, be, ed = D_(T(j)), D_(q(j)), D_(q(j + 1)), D_(alpha(j)), D_(beta(j)), D_(EPS)
    Z = Dc(0)
    P = [(Z, Z, Z), (Z, qa * Tj, HD * Tj), (Z, qb * Tj, HD * Tj)]                  # P_j, construction.tex eq first-family
    Qt = [(Z, Z, HD), (qa * Tj, Z, HD * (1 - Tj)), (qb * Tj, Z, HD * (1 - Tj))]     # Q_j at s0 = 0 and s0 = T_j
    return (tri_perp_area(*P, (Dc(1), ed * al, HD * ed * be)), tri_perp_area(*Qt, (-ed * al, Dc(1), HD * ed * be)))
e = float(EPS)
def base_area_closed(j):
    Tj = float(T(j)); al, be = float(alpha(j)), float(beta(j))
    return H * float(DELTA) * Tj * Tj / 2 / sqrt(1 + e * e * (al * al + 2 * be * be))
rng = random.Random(100)
sample_js = [0, 1, N // 2, N - 1] + [rng.randrange(N) for _ in range(2000)]
worst = max(max(abs(float(g) - base_area_closed(j)) for g in base_areas_geometric(j)) / base_area_closed(j) for j in sample_js)
say(f"B. per-base geometric area vs closed form area.tex:15-19, {len(sample_js)} sampled sectors: max rel diff {worst:.2e}")
# full sum, exact-rational coefficients, float only in the final sqrt
d2 = float(DELTA); e2 = e * e
def term(j, eta=0.001):
    qa = -1 + j * d2; qb = qa + d2                   # float grid; exact-rational cross-check below
    al = (1 + qa * qb) / 4; be = (qa + qb) / 4
    m = eta + max(qa * qa * (1 + qa * qa), qb * qb * (1 + qb * qb)) / 16
    Tj = 0.5 + e2 * m
    return d2 * Tj * Tj / sqrt(1 + e2 * (al * al + 2 * be * be))
S = fsum(term(j) for j in range(N))                   # = (1/sqrt2) * sum |B_i|, both families
for j in sample_js[:50]:                              # grid rounding is far below the margin
    assert abs(term(j) - d2 * float(T(j))**2 / sqrt(1 + e2 * float(alpha(j)**2 + 2 * beta(j)**2))) < 1e-22
pred = 0.5 - 13 / 6000 * e2
rem = S - pred
S_mut = fsum(term(j, eta=1/400) for j in range(N))   # mutation: 2*eta - 1/240 > 0 must push the sum ABOVE 1/2
ok_B = abs(rem) <= 2 * e2 * e2 and S < 0.5 and worst < 1e-12 and S_mut > 0.5
say(f"B. n = {N} sectors, 2n = {2*N} cylinders: S/H = {S!r}")
say(f"   1/2 - 13/6000 eps^2 = {pred!r}; remainder = {rem:.3e}; paper's bound 2 eps^4 = {2*e2*e2:.3e}")
say(f"   mutation eta=1/400 (enlargement larger than the tilt saves): S/H = {S_mut!r} > 1/2: {S_mut > 0.5}")
say(f"   margin below 1/2: {0.5 - S:.6e} (= {(0.5 - S) / e2:.6f} eps^2; paper 13/6000 = {13/6000:.6f}) -> {'ok' if ok_B else 'MISMATCH'}")

# ---------- C. coverage, exact ----------
def candidates(x, y, t, fam, span=5):
    """Sectors near the fixed point q = (y - eps x (1+q^2)/4) / (t - eps x q/2) of the tilted intercept
    (alpha ~ (1+q^2)/4, beta ~ q/2, construction.tex eq. axis-coefficients). Only a SEARCH hint: the exact
    Fraction test in slack() decides. On the family's own apex edge (t=0 resp. s=0) the covering sector is
    an outer one (phi(+-1) = 0), so try both ends."""
    if fam == 1: a, b, c = float(y), float(t), float(x)
    else: a, b, c = float(x), float(1 - t), -float(y)
    if b <= 0: return list(range(0, span)) + list(range(N - span, N))
    qq = a / b
    for _ in range(60): qq = (a - e * c * (1 + qq * qq) / 4) / (b - e * c * qq / 2)
    j0 = int(floor((qq + 1) / float(DELTA)))
    return range(max(0, j0 - span), min(N - 1, j0 + span) + 1)

def slack(x, y, t, enlarge=True, span=5):
    """max over cylinders whose angular sector holds the point of (T - radial intercept); >= 0 iff covered.
    Exact Fraction arithmetic; None if no sector near the point's angle holds it."""
    best = None
    for fam in (1, 2):
        for j in candidates(x, y, t, fam, span):
            if fam == 1: r = t - EPS * x * beta(j); w = y - EPS * x * alpha(j)          # coverage.tex eq lower-intercept
            else: r = (1 - t) + EPS * y * beta(j); w = x + EPS * y * alpha(j)    # coverage.tex eq upper-intercept
            if r >= 0 and q(j) * r <= w <= q(j + 1) * r:
                sl = T(j, enlarge) - r
                if best is None or sl > best: best = sl
    return best

D = 10**9
rng = random.Random(2000)
pts = [(Fr(1), Fr(0), Fr(0)), (Fr(-1), Fr(0), Fr(0)), (Fr(0), Fr(1), Fr(1)), (Fr(0), Fr(-1), Fr(1)),
       (Fr(0), Fr(0), Fr(1, 2)), (Fr(1, 2), Fr(1, 2), Fr(1, 2)), (Fr(-1, 2), Fr(-1, 2), Fr(1, 2))]
pts += [(Fr(rng.randrange(-D, D + 1), D), Fr(0), Fr(0)) for _ in range(20)]       # bottom edge
pts += [(Fr(0), Fr(rng.randrange(-D, D + 1), D), Fr(1)) for _ in range(20)]       # top edge
for _ in range(1000):                                                             # uniform in K
    t = Fr(rng.randrange(1, D), D)
    pts.append((Fr(rng.randrange(-D, D + 1), D) * (1 - t), Fr(rng.randrange(-D, D + 1), D) * t, t))
NPAIR, STEPS = 25, 801                                                            # handover band
for _ in range(NPAIR):
    u, v = Fr(rng.randrange(-D, D + 1), D), Fr(rng.randrange(-D, D + 1), D)
    for k in range(STEPS):
        t = Fr(1, 2) + Fr(2 * k - (STEPS - 1), STEPS - 1) * 2 * EPS**2              # t - 1/2 in [-2eps^2, 2eps^2]
        pts.append((u * (1 - t), v * t, t))
on = [slack(*p) for p in pts]
on = [s if s is not None and s >= 0 else slack(*p, span=5000) for s, p in zip(on, pts)]   # widen before failing
off = [slack(*p, enlarge=False) for p in pts]
unc = sum(1 for s in on if s is None or s < 0)
unc_off = sum(1 for s in off if s is None or s < 0)
mn_on = min(s for s in on if s is not None) / EPS**2
mn_off = min(s for s in off if s is not None) / EPS**2
ok_C = unc == 0 and unc_off > 0
say(f"C. coverage at eps=1/2000, exact rationals: {len(pts)} points (7 vertices/fixed, 40 on the two edges t=0,1, 1000 uniform,")
say(f"   {NPAIR} lines x {STEPS} heights across the handover band |t-1/2| <= 2eps^2): uncovered {unc}; min slack {float(mn_on):.6f} eps^2")
say(f"   negative arm, radial enlargement removed (T_j = 1/2): uncovered {unc_off}; min slack {float(mn_off):.6f} eps^2 -> sampler {'sees' if unc_off else 'CANNOT see'} the gap the enlargement closes")
ok = ok_A and ok_B and ok_C
say(f"RESULT: {'holds' if ok else 'fails'} | A_min=sqrt2: {ok_A} | area below half, within 2eps^4 of paper: {ok_B} | sampled coverage, gap-seeing control: {ok_C}")
sys.exit(0 if ok else 1)
