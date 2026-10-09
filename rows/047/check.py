#!/usr/bin/env python3
"""Row 047: an explicit failure of complex affine-space cancellation, A[w] = C^[5] with A = P/(H).

Source (openai/math fd4aeeb):
  preprints/An-explicit-failure-of-complex-affine-space-cancellation-September-23-2026/build/sections/
  01-introduction.tex:49-70 (eq:example, thm:main): P=C[p,s,u,F,J], x=s^2+u^3+p^2F,
      H = x^2F-(1+2sx)J-p^2J^2-pu, A=P/(H); A[w] = C^[5] and A is not C^[4].
  02-construction.tex:19-245: the explicit route to A[w] = C^[5] (prop:stabilization).

What this script computes, in exact rational arithmetic, every identity that route rests on:
  1 con:identity          xy - z(z+1) = p^2(H + pu)
  2 con:localized-coordinates   s = y - x(x-u^3), F = (x-s^2-u^3)/p^2, J = (z-sx)/p^2
  3 con:derivation        the stated Delta-values give Delta x = Delta y = Delta z = 0 and Delta H = p^3
  4 con:linear-coordinates/-inverse   determinant 1 and the inverse formulas
  5 con:h-expansion       H = L - pu + p^2 Q(L) + p^4 F(L)^3
  6 con:root              C = Q(0) = M^2(2x0+6sx0^2+4s^2x0^3-x0^4), Q1 = (Q(L)-C)/L is a polynomial in L
  7 con:root-divisibility H(L*) = p^3((u-pC)Q1(L*) + pF(L*)^3), L* = pu - p^2 C
  8 con:e-polynomial      H(L) + p^3 w = L - p h
  9 con:e-certificate     p^3 e0 - (L - L*) = (p^2 Q1(L) - 1)(H(L) + p^3 w)
 10 con:polynomial-cylinder, both directions at points of T: from (B, e): L = L* + p^3 e, w = W(e) gives
    e0(L, w) = e; from a point (B, L, w) with H(L)+p^3w = 0: e = e0 gives L* + p^3 e = L and W(e) = w.
Identities in free variables are checked at K random integer points in [0, 2^64): a false identity of
total degree <= D survives one point with probability <= D/2^64 (Schwartz-Zippel; D printed).
Every check has a negative arm (a perturbed formula) that must fail.
Not computed: that A is not C^[4] (sections 03-06, a degeneration/bundle argument), that A is a domain
of dimension 4 (con:domain, a factorization argument), and local nilpotency of Delta (the paper: Delta =
-p^2 d/du in the localized coordinates that check 2 confirms).
"""
import random, sys
from fractions import Fraction as Fr

random.seed(20261009)
N, K = 2**64, 5

class UP:  # univariate polynomial in L over Q (coefficients are evaluated B-values)
    def __init__(s, c):
        c = [Fr(v) if isinstance(v, (int, Fr)) else v for v in c]
        while len(c) > 1 and isinstance(c[-1], Fr) and c[-1] == 0: c.pop()
        s.c = c
    def _l(o): return o if isinstance(o, UP) else UP([o])
    def __add__(s, o):
        o = UP._l(o); n = max(len(s.c), len(o.c))
        return UP([(s.c[i] if i < len(s.c) else 0) + (o.c[i] if i < len(o.c) else 0) for i in range(n)])
    __radd__ = __add__
    def __neg__(s): return UP([-v for v in s.c])
    def __sub__(s, o): return s + (-UP._l(o))
    def __rsub__(s, o): return UP._l(o) - s
    def __mul__(s, o):
        o = UP._l(o); r = [Fr(0)]*(len(s.c) + len(o.c) - 1)
        for i, a in enumerate(s.c):
            for j, b in enumerate(o.c): r[i + j] += a*b
        return UP(r)
    __rmul__ = __mul__
    def __pow__(s, k):
        r = UP([1])
        for _ in range(k): r = r*s
        return r
    def __call__(s, v):
        r = 0
        for a in reversed(s.c): r = r*v + a
        return r

class D1:  # value + one tangent: evaluates a derivation at a point
    def __init__(s, v, t): s.v, s.t = Fr(v), Fr(t)
    def _l(o): return o if isinstance(o, D1) else D1(o, 0)
    def __add__(s, o): o = D1._l(o); return D1(s.v + o.v, s.t + o.t)
    __radd__ = __add__
    def __neg__(s): return D1(-s.v, -s.t)
    def __sub__(s, o): return s + (-D1._l(o))
    def __rsub__(s, o): return D1._l(o) - s
    def __mul__(s, o): o = D1._l(o); return D1(s.v*o.v, s.v*o.t + s.t*o.v)
    __rmul__ = __mul__
    def __pow__(s, k):
        r = D1(1, 0)
        for _ in range(k): r = r*s
        return r

class Deg:  # total-degree tracker for the Schwartz-Zippel bound; '==' records the degree and returns True
    SEEN = []
    def __init__(s, d): s.d = d
    def __eq__(s, o): Deg.SEEN.append(max(s.d, Deg._c(o).d)); return True
    def __truediv__(s, o): return Deg(s.d + Deg._c(o).d)   # clearing a denominator adds its degree
    def __rtruediv__(s, o): return Deg(s.d + Deg._c(o).d)
    __hash__ = object.__hash__
    def _c(o): return o if isinstance(o, Deg) else Deg(0)
    def __add__(s, o): return NotImplemented if isinstance(o, UP) else Deg(max(s.d, Deg._c(o).d))
    __radd__ = __add__; __sub__ = __add__; __rsub__ = __add__
    def __neg__(s): return s
    def __mul__(s, o): return NotImplemented if isinstance(o, UP) else Deg(s.d + Deg._c(o).d)
    __rmul__ = __mul__
    def __pow__(s, k): return Deg(s.d*k)
    def __rmul__(s, o): return s.__mul__(o)
    def __eq__(s, o): Deg.SEEN.append(max(s.d, Deg._c(o).d)); return True

def xH(p, s, u, F, J):
    x = s**2 + u**3 + p**2*F
    return x, x**2*F - (1 + 2*s*x)*J - p**2*J**2 - p*u

def FJ_of(L, Mv, s, x0):   # con:linear-inverse
    return 4*s**2*L + (1 + 2*s*x0)*Mv, -(1 - 2*s*x0)*L + x0**2*Mv

def objects(p, s, u, Mv, tw=1):
    """Everything in B[L] for a fixed point (p,s,u,M) of B: returns H(L), Q(L), F(L), C, Q1, L*."""
    x0 = s**2 + u**3
    Lv = UP([0, 1])
    F, J = FJ_of(Lv, Mv, s, x0)
    Q = 2*x0*F**2 - 2*s*F*J - J**2
    _, H = xH(p, s, u, F, J)
    C = Q.c[0]
    Q1 = UP(Q.c[1:])                       # (Q(L) - C)/L, a polynomial in L by construction
    Ls = p*u - p**2*C
    return dict(x0=x0, F=F, J=J, Q=Q, H=H, C=C, Q1=Q1, Ls=Ls, tw=tw)

def checks(tw, deg=False):
    """All identities at K random points; tw != 1 perturbs each one so it must fail.
    deg=True runs the same code on degree trackers to get the Schwartz-Zippel D."""
    out = {}
    def put(k, v): out[k] = out.get(k, True) and v
    for _ in range(1 if deg else K):
        if deg:
            p, s, u, F, J, w, Lr, Mv = (Deg(1) for _ in range(8))
        else:
            p, s, u, F, J, w, Lr, Mv = (Fr(random.randrange(1, N)) for _ in range(8))
        x, H = xH(p, s, u, F, J)
        y, z = s + x*(x - u**3), s*x + p**2*J
        put("1 con:identity", x*y - z*(z + tw) == p**2*(H + p*u))
        put("2 con:localized-coordinates", s == y - x*(x - u**3) and F == (x - s**2 - u**3)/p**2
            and J == (z - s*x)/p**2*tw)
        if deg:   # check 3: H has degree 7, the Delta-values degree <= 8, so Delta(H) has degree <= 14 <= 20
            Deg.SEEN.append(20)
        else:
          tang = [0, -3*p**2*x*u**2, -p**2, (6*s*x + 3*tw)*u**2, 3*x**2*u**2]   # con:derivation on (p,s,u,F,J)
          g = [D1(a, t) for a, t in zip((p, s, u, F, J), tang)]
          X, HH = xH(*g)
          Y, Z = g[1] + X*(X - g[2]**3), g[1]*X + g[0]**2*g[4]
          put("3 con:derivation: Delta x=y=z=0, Delta H = p^3", X.t == 0 and Y.t == 0 and Z.t == 0 and HH.t == p**3)
        x0 = s**2 + u**3
        L = x0**2*F - (1 + 2*s*x0)*J
        M = (1 - 2*s*x0)*F + 4*s**2*J
        put("4 det = 1 and con:linear-inverse", 4*s**2*x0**2 + (1 + 2*s*x0)*(1 - 2*s*x0) == 1
            and (F, J*tw) == FJ_of(L, M, s, x0))
        Qv = 2*x0*F**2 - 2*s*F*J - J**2
        put("5 con:h-expansion", H == L - p*u + p**2*Qv + tw*p**4*F**3)
        o = objects(p, s, u, Mv)
        put("6 con:root: C = Q(0) = M^2(2x0+6sx0^2+4s^2x0^3-x0^4), Q - C = L*Q1",
            o["C"] == Mv**2*(2*o["x0"] + 6*s*o["x0"]**2 + 4*s**2*o["x0"]**3 - tw*o["x0"]**4)
            and all((o["Q"] - o["C"])(t) == t*o["Q1"](t) for t in (Lr, Lr + 1)))
        Ls = o["Ls"]
        put("7 con:root-divisibility", o["H"](Ls) == p**3*((u - p*o["C"])*o["Q1"](Ls) + tw*p*o["F"](Ls)**3))
        h = u - p*o["Q"](Lr) - p**3*o["F"](Lr)**3 - p**2*w
        put("8 con:e-polynomial: H(L)+p^3w = L - p h", o["H"](Lr) + p**3*w == Lr - tw*p*h)
        e0 = -w - p*o["F"](Lr)**3 - o["Q1"](Lr)*h
        put("9 con:e-certificate", p**3*e0 - (Lr - Ls) == (p**2*o["Q1"](Lr) - tw)*(o["H"](Lr) + p**3*w))
        def e0f(Lv, wv):
            hv = u - p*o["Q"](Lv) - p**3*o["F"](Lv)**3 - p**2*wv
            return -wv - p*o["F"](Lv)**3 - o["Q1"](Lv)*hv
        W = lambda ev: -o["H"](Ls + p**3*ev)/p**3
        ev = w                                   # direction B[e] -> T -> e
        ok_a = e0f(Ls + p**3*ev, W(ev)) == ev*tw
        wv = -o["H"](Lr)/p**3                     # direction: a point of T -> e -> back
        ee = e0f(Lr, wv)
        ok_b = Ls + p**3*ee == Lr and W(ee) == wv
        put("10 con:polynomial-cylinder both ways at points of T", ok_a and ok_b)
    return out

ok, neg = checks(1), checks(2)
checks(1, deg=True)
assert len(Deg.SEEN) >= 10, "degree tracker saw too few identities"
Dbound = max(Deg.SEEN)
print(f"Schwartz-Zippel: largest total degree over the {len(Deg.SEEN)} comparisons, denominators cleared: D <= {Dbound}")
fails = []
for k in ok:
    good = ok[k] and not neg[k]
    print(f"{'ok  ' if good else 'FAIL'} {k}  [{K} pts]  (negative arm {'failed as it must' if not neg[k] else 'PASSED: checker broken'})")
    if not good: fails.append(k)
print(f"a false identity survives all {K} points with probability <= {(Dbound/N)**K:.1e}")
if fails:
    print("RESULT: DISAGREES at", ", ".join(fails)); sys.exit(1)
print("RESULT: holds -- every identity in the explicit route to A[w] = C^[5] (02-construction.tex) computes as stated")
