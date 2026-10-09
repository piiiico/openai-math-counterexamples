#!/usr/bin/env python3
"""Family 172: the computable parts of the two non-Ramsey examples in
'A classification of finite Euclidean Ramsey configurations' (07-consequences.tex).

The kites K_a (cons:kites) that disprove Leader-Russell-Walters' Conjecture A need a
transcendental a and the Ramsey property quantifies over all colourings: nothing to compute.
What a program can check is the finite algebra the paper's two NON-Ramsey proofs rest on:

 A. cons:nine (lines 154-197): the 9x9 tensor-evaluation matrix D with rows
    (p_a(T_i) p_b(U_i))_{a,b}, p(t) = (1, (1-t^2)/(1+t^2), 2t/(1+t^2)), specialised to the grid
    {0,1,-1}^2, equals C (x) C and has determinant 64 (so det D != 0 generically).
 B. cons:twelve (lines 206-266): with u,v from t, d = (1+t^2)/2 d/dt, the twelve points
    R_e q (e in +,-,0; q in Q0) and weights 1,1,-2: d u = -v, d v = u, and the three moment
    identities  sum b p p^T = 0,  sum b (dp) p^T = 0,  sum b (dp)(dp)^T = diag(0, 4, 4).
    Route 1: exact polynomial arithmetic in Q[t] over powers of (1+t^2) (an identity of
    rational functions, no sampling). Route 2: dual numbers over Fractions at 30 seeded
    random rationals (no symbolic derivative).
Negative arms: grid with a repeated value (det must be 0); weight -1 instead of -2 (the
first moment must fail); derivation without the (1+t^2)/2 factor (d u = -v must fail).
"""
import random, sys, time
from fractions import Fraction as Fr
t0 = time.time()
ok = True

def det(M):
    M = [[Fr(x) for x in r] for r in M]; n = len(M); s = Fr(1)
    for c in range(n):
        p = next((r for r in range(c, n) if M[r][c] != 0), None)
        if p is None: return Fr(0)
        if p != c: M[c], M[p] = M[p], M[c]; s = -s
        s *= M[c][c]
        for r in range(c + 1, n):
            f = M[r][c] / M[c][c]
            M[r] = [a - f * b for a, b in zip(M[r], M[c])]
    return s

def p(t):
    t = Fr(t); return [Fr(1), (1 - t * t) / (1 + t * t), 2 * t / (1 + t * t)]

def Dmat(pairs):
    return [[p(T)[a] * p(U)[b] for a in range(3) for b in range(3)] for T, U in pairs]

order = [0, 1, -1]
grid = [(T, U) for T in order for U in order]
D = Dmat(grid)
C = [[1, 1, 0], [1, 0, 1], [1, 0, -1]]
kron = [[C[i // 3][j // 3] * C[i % 3][j % 3] for j in range(9)] for i in range(9)]
dg = det(D)
print("A. D(grid) == C (x) C:", D == [[Fr(x) for x in r] for r in kron], " det C =", det(C), " det D(grid) =", dg)
ok &= D == [[Fr(x) for x in r] for r in kron] and dg == 64 and det(C) == 2
rng = random.Random(172)
rnd = [(Fr(rng.randint(-99, 99), rng.randint(1, 99)), Fr(rng.randint(-99, 99), rng.randint(1, 99))) for _ in range(9)]
print("A. det D at 9 random rational pairs != 0:", det(Dmat(rnd)) != 0)
neg = det(Dmat([(T, U) for T in [0, 1, 1] for U in order]))
print("A. negative arm (grid T-values 0,1,1): det =", neg, "->", "rejected" if neg == 0 else "NOT REJECTED")
ok &= neg == 0

# ---- B, route 1: polynomials in t (lists of Fractions, low degree first) over (1+t^2)^k
def padd(a, b):
    n = max(len(a), len(b)); return [(a[i] if i < len(a) else 0) + (b[i] if i < len(b) else 0) for i in range(n)]
def pmul(a, b):
    r = [Fr(0)] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b): r[i + j] += x * y
    return r
def psc(a, c): return [c * x for x in a]
def pder(a): return [i * a[i] for i in range(1, len(a))] or [Fr(0)]
def pzero(a): return all(x == 0 for x in a)
W = [Fr(1), Fr(0), Fr(1)]  # 1 + t^2
class RF:  # N / W^k
    def __init__(s, N, k): s.N, s.k = [Fr(x) for x in N], k
    def lift(s, k): N = s.N
    def to(s, k):
        N = s.N
        for _ in range(k - s.k): N = pmul(N, W)
        return N
    def __add__(s, o): k = max(s.k, o.k); return RF(padd(s.to(k), o.to(k)), k)
    def __neg__(s): return RF(psc(s.N, -1), s.k)
    def __sub__(s, o): return s + (-o)
    def __mul__(s, o): return RF(pmul(s.N, o.N), s.k + o.k) if isinstance(o, RF) else RF(psc(s.N, Fr(o)), s.k)
    def d(s, factor=True):  # d/dt of N/W^k = (N' W - 2k t N)/W^(k+1); times (1+t^2)/2 if factor
        num = padd(pmul(pder(s.N), W), psc(pmul([Fr(0), Fr(1)], s.N), -2 * s.k))
        return RF(psc(num, Fr(1, 2)), s.k) if factor else RF(num, s.k + 1)
    def iszero(s): return pzero(s.N)
ONE, ZERO = RF([1], 0), RF([0], 0)
u, v = RF([1, 0, -1], 1), RF([0, 2], 1)
print("B1. d u == -v:", (u.d() + v).iszero(), "  d v == u:", (v.d() - u).iszero())
ok &= (u.d() + v).iszero() and (v.d() - u).iszero()
Q0 = [(1, 0), (-1, 0), (0, 1), (0, -1)]

def points(u, v):
    Rp = [[u, -v], [v, u]]; Rm = [[u, v], [-v, u]]; R0 = [[ONE, ZERO], [ZERO, ONE]]
    out = []
    for e, R, beta in (("+", Rp, 1), ("-", Rm, 1), ("0", R0, -2)):
        for q in Q0:
            x = [R[0][0] * q[0] + R[0][1] * q[1], R[1][0] * q[0] + R[1][1] * q[1]]
            out.append((beta, [ONE] + x))
    return out

def moments(pts, dfun, w0=-2):
    m = [[[ZERO] * 3 for _ in range(3)] for _ in range(3)]
    for beta, pv in pts:
        if beta == -2: beta = w0
        dp = [dfun(x) for x in pv]
        for a in range(3):
            for b in range(3):
                m[0][a][b] = m[0][a][b] + pv[a] * pv[b] * beta
                m[1][a][b] = m[1][a][b] + dp[a] * pv[b] * beta
                m[2][a][b] = m[2][a][b] + dp[a] * dp[b] * beta
    return m
target = [[0, 0, 0], [0, 4, 0], [0, 0, 4]]
def check_moments(m):
    return [all((m[0][a][b]).iszero() for a in range(3) for b in range(3)),
            all((m[1][a][b]).iszero() for a in range(3) for b in range(3)),
            all((m[2][a][b] - ONE * target[a][b]).iszero() for a in range(3) for b in range(3))]
pts = points(u, v)
r = check_moments(moments(pts, lambda x: x.d()))
print("B1. exact in Q(t): sum b pp^T = 0, sum b (dp)p^T = 0, sum b (dp)(dp)^T = diag(0,4,4):", r)
ok &= r == [True, True, True]
rn = check_moments(moments(pts, lambda x: x.d(), w0=-1))
print("B1. negative arm (weight -1 for Q0): first moment zero?", rn[0], "->", "rejected" if not rn[0] else "NOT REJECTED")
ok &= not rn[0]
rd = (u.d(factor=False) + v).iszero()
print("B1. negative arm (plain d/dt, no (1+t^2)/2): d u == -v?", rd, "->", "rejected" if not rd else "NOT REJECTED")
ok &= not rd

# ---- B, route 2: dual numbers a + b*eps over Fractions, evaluated at random rationals
class Du:
    def __init__(s, a, b=0): s.a, s.b = Fr(a), Fr(b)
    def __add__(s, o): o = o if isinstance(o, Du) else Du(o); return Du(s.a + o.a, s.b + o.b)
    __radd__ = __add__
    def __neg__(s): return Du(-s.a, -s.b)
    def __sub__(s, o): return s + (-(o if isinstance(o, Du) else Du(o)))
    def __rsub__(s, o): return Du(o) - s
    def __mul__(s, o): o = o if isinstance(o, Du) else Du(o); return Du(s.a * o.a, s.a * o.b + s.b * o.a)
    __rmul__ = __mul__
    def __truediv__(s, o): o = o if isinstance(o, Du) else Du(o); return Du(s.a / o.a, (s.b * o.a - s.a * o.b) / (o.a * o.a))
bad = 0
for _ in range(30):
    t = Fr(rng.randint(-10**6, 10**6), rng.randint(1, 10**6)); T = Du(t, 1); h = (1 + t * t) / 2
    U = (1 - T * T) / (1 + T * T); V = 2 * T / (1 + T * T)
    bad += (h * U.b != -V.a) + (h * V.b != U.a)
    P = []
    for R, beta in (([[U, -V], [V, U]], 1), ([[U, V], [-V, U]], 1), ([[Du(1), Du(0)], [Du(0), Du(1)]], -2)):
        for q in Q0:
            x = [R[0][0] * q[0] + R[0][1] * q[1], R[1][0] * q[0] + R[1][1] * q[1]]
            P.append((beta, [Fr(1)] + [y.a for y in x], [Fr(0)] + [h * y.b for y in x]))
    for a in range(3):
        for b in range(3):
            bad += sum(be * pa[a] * pa[b] for be, pa, _ in P) != 0
            bad += sum(be * dp[a] * pa[b] for be, pa, dp in P) != 0
            bad += sum(be * dp[a] * dp[b] for be, _, dp in P) != target[a][b]
print("B2. dual numbers at 30 random rationals: failed identities =", bad)
ok &= bad == 0
print("RESULT:", "holds" if ok else "FAILS")
print(f"runtime {time.time()-t0:.2f}s", file=sys.stderr)
