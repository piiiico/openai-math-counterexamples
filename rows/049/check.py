#!/usr/bin/env python3
"""Row 049: the family's two explicit four-variable polynomials.

PART 1 (section E below), the headline paper:
  preprints/A-stable-coordinate-that-is-not-a-coordinate-in-four-variables-October-5-2026/build/source/sections/
  01-introduction.tex:8-16 (thm:main): f = x1 - 2Q(Q(x2+x4) + x1x4), Q = x2^2 - x4^2 + x1x3; an automorphism
  of R[w] sends f to x1, none of R does. 02-construction.tex:11-164 builds the automorphism of R[w] from
  explicit coordinate changes. Section E computes every identity that chain rests on: the matrix change
  (con:matrix-change) and its inverse, x and p in the new coordinates (con:candidate, so p IS f), the
  quadric identity (con:quadric-identity), the localized inverse (con:localized-inverse), the derivation
  values (con:delta) giving Delta(x)=Delta(y)=Delta(z)=0 and Delta(H)=p, the determinant-one linear change
  (con:linear-coordinates/-inverse) and H = L - u + pQ0 (con:H-expansion). Not computed: "no automorphism
  of R sends f to x1" (sections 03-05, a filtration argument), and local nilpotency, which the paper gets
  from Delta = -p d/du in the localized coordinates that E3 checks.

PART 2 (sections A-D), the second paper: the explicit noncoordinate polynomial with affine-three-space zero fibre.

Source (openai/math fd4aeeb):
  preprints/An-explicit-noncoordinate-polynomial-with-affine-three-space-zero-fibre-September-24-2026/build/paper.tex
  - eq:xyz, eq:F (lines 87-99): x=u^3+hv, y=-u^2+hw, s=2u^3v+3u^4w+h(v^2-3u^2w^2)+h^2w^3,
    p=-2s^2x+3sy^2-3s^3y, F=h-p-1, in R=C[h,u,v,w].
  - thm:main (lines 103-111): R/(F) = C^[3] and grad F(2,0,-1/2,1/2)=0, so F is not a coordinate.
  - Appendix A (lines 342-374), eq:shiftidentity (265), eq:Bparam (285): the explicit maps both ways between the zero fibre and A^3.

What this script computes, all in exact rational arithmetic (fractions.Fraction, Python ints):
  A. the polynomial identities the paper uses: cusp x^2+y^3=hs, shift identity, Bezout certificate
     (eq:certificate), ambient identity X^2+Y^3=s(1+F)  -- by evaluation at random integer points.
  B. Phi: A^3 -> R (eq:explicitinverse) lands on F=0 and Psi(Phi(X,Y,T)) = (X,Y,T), with Psi the
     fibre coordinates (eq:fibercoords)  -- at random integer points.
  C. Phi(Psi(q)) = q for points q ON the zero fibre that Phi did not produce: fix random rational
     (u,v,w), let h be a root of F(h,u,v,w), compute exactly in Q[t]/(F(t,u,v,w)).
  D. F(P) = -1 and all four partial derivatives of F vanish at P=(2,0,-1/2,1/2) (exact, dual numbers).
Each check has a negative arm that must FAIL (a perturbed formula, a point off the fibre, a point
next to P), so a broken checker cannot print agreement.

Error bound for A and B (Schwartz-Zippel): a nonzero polynomial of total degree <= D vanishes at a
uniform random point of [0,N)^n with probability <= D/N. D is computed below by running the same
formulas on a degree tracker; N = 2^64; every identity is evaluated at K independent points.
What it does NOT compute: the last step of thm:main (a coordinate has nowhere-zero gradient) is a
one-line argument, not a computation.
"""
import random, sys, time
from fractions import Fraction as Q

random.seed(20261009)
t0 = time.time()

# ---------- the paper's formulas, written once, generic over any ring-like type ----------
def xys(h, u, v, w):
    x = u**3 + h*v
    y = -u**2 + h*w
    s = 2*u**3*v + 3*u**4*w + h*(v**2 - 3*u**2*w**2) + h**2*w**3
    return x, y, s

def pp(x, y, s):
    return -2*s**2*x + 3*s*y**2 - 3*s**3*y

def F(h, u, v, w):
    x, y, s = xys(h, u, v, w)
    return h - pp(x, y, s) - 1

def ab(x, y, s):
    alpha = 1 + 2*s**2*x + 4*s**5
    beta = (3*s**3 - 3*s*y)*(1 + 2*s**2*x) - 4*s**4*y**2
    return alpha, beta

def Psi(h, u, v, w):                       # eq:fibercoords: zero fibre -> A^3
    x, y, s = xys(h, u, v, w)
    alpha, beta = ab(x, y, s)
    return x + s**3, y - s**2, alpha*u + beta*(v + u*w)

def Phi(X, Y, T, twist=2):                 # eq:Bparam + eq:explicitinverse: A^3 -> zero fibre
    s = X**2 + Y**3
    x = X - s**3
    y = Y + s**2
    h = 1 + pp(x, y, s)
    alpha, beta = ab(x, y, s)
    u = h*T - beta*x
    g = y*T + alpha*x
    w = alpha*(1 + beta*y)*(y + u**2) + beta**2*(s - h*g**2 + twist*u*y*g)
    v = g - u*w
    return h, u, v, w

# ---------- a degree tracker (for the Schwartz-Zippel bound) ----------
class Deg:
    def __init__(s, d): s.d = d
    def _c(o): return o if isinstance(o, Deg) else Deg(0)
    def __add__(s, o): return Deg(max(s.d, Deg._c(o).d))
    __radd__ = __add__; __sub__ = __add__; __rsub__ = __add__
    def __neg__(s): return s
    def __mul__(s, o): return Deg(s.d + Deg._c(o).d)
    __rmul__ = __mul__
    def __pow__(s, k): return Deg(s.d*k)

V = [Deg(1)]*4
D = {
 "cusp": max(xys(*V)[0].__pow__(2).d, xys(*V)[1].__pow__(3).d, (V[0]*xys(*V)[2]).d),
 "certificate": (lambda h, x, y, s: max(c.d for c in [ab(x, y, s)[0]*h, ab(x, y, s)[1]*y,
                 (1 + 2*s**2*x)*(h - 1 - pp(x, y, s)), s**4*(x**2 + y**3 - s*h)]))(*V),
 "ambient": max(c.d for c in [Psi(*V)[0]**2, Psi(*V)[1]**3, xys(*V)[2]*F(*V)]),
 "F(Phi)": F(*Phi(*[Deg(1)]*3)).d,
 "Psi(Phi)": max(c.d for c in Psi(*Phi(*[Deg(1)]*3))),
}
N = 2**64
K = 5

def rnd(n): return [random.randrange(N) for _ in range(n)]

fails = []
def check(name, ok, neg_ok):
    print(f"{'ok  ' if ok and not neg_ok else 'FAIL'} {name}  (negative arm {'failed as it must' if not neg_ok else 'PASSED: checker broken'})")
    if not ok or neg_ok: fails.append(name)

# ---------- A. polynomial identities ----------
ok = all((lambda x, y, s, h: x**2 + y**3 == h*s)(*xys(*P), P[0]) for P in (rnd(4) for _ in range(K)))
neg = all((lambda x, y, s, h: x**2 + y**3 == h*(s + 1))(*xys(*P), P[0]) for P in (rnd(4) for _ in range(K)))
check(f"A1 cusp x^2+y^3 = h*s                  [D<={D['cusp']}, {K} pts]", ok, neg)

def shift_id(x, y, s): return (x + s**3)**2 + (y - s**2)**3 == x**2 + y**3 - s*pp(x, y, s)
check(f"A2 shift identity (eq:shiftidentity)    [free x,y,s, {K} pts]",
      all(shift_id(*rnd(3)) for _ in range(K)),
      all((lambda x, y, s: (x + s**3)**2 + (y - s**2)**3 == x**2 + y**3 + s*pp(x, y, s))(*rnd(3)) for _ in range(K)))

def cert(h, x, y, s, k4=4):
    a, b = ab(x, y, s)
    return a*h + b*y - 1 == (1 + 2*s**2*x)*(h - 1 - pp(x, y, s)) - k4*s**4*(x**2 + y**3 - s*h)
check(f"A3 Bezout certificate (eq:certificate)  [D<={D['certificate']}, {K} pts]",
      all(cert(*rnd(4)) for _ in range(K)), all(cert(*rnd(4), k4=5) for _ in range(K)))

def ambient(P, shift=0):
    X, Y, _ = Psi(*P); s = xys(*P)[2]
    return X**2 + Y**3 == s*(1 + F(*P) + shift)
check(f"A4 ambient X^2+Y^3 = s(1+F)             [D<={D['ambient']}, {K} pts]",
      all(ambient(rnd(4)) for _ in range(K)), all(ambient(rnd(4), 1) for _ in range(K)))

# ---------- B. Phi lands on F=0 and Psi o Phi = id on A^3 ----------
okF, okI = True, True
for _ in range(K):
    p3 = rnd(3); q4 = Phi(*p3)
    okF &= F(*q4) == 0
    okI &= tuple(Psi(*q4)) == tuple(p3)
negF, negI = True, True
for _ in range(K):
    p3 = rnd(3); q4 = Phi(*p3, twist=3)
    negF &= F(*q4) == 0
    negI &= tuple(Psi(*q4)) == tuple(p3)
check(f"B1 F(Phi(X,Y,T)) = 0                   [D<={D['F(Phi)']}, {K} pts]", okF, negF)
check(f"B2 Psi(Phi(X,Y,T)) = (X,Y,T)           [D<={D['Psi(Phi)']}, {K} pts]", okI, negI)

# ---------- C. Phi o Psi = id on fibre points Phi did not produce ----------
class UP:  # univariate polynomial over Q, optionally reduced mod a global modulus
    MOD = None
    def __init__(s, c):
        c = [Q(x) for x in c]
        while len(c) > 1 and c[-1] == 0: c.pop()
        s.c = c
        if UP.MOD is not None and len(s.c) >= len(UP.MOD): s._red()
    def _red(s):
        m = UP.MOD; c = s.c[:]; dm = len(m) - 1
        for i in range(len(c) - 1, dm - 1, -1):
            q = c[i] / m[-1]
            if q:
                for j in range(dm + 1): c[i - dm + j] -= q*m[j]
        c = c[:dm] or [Q(0)]
        while len(c) > 1 and c[-1] == 0: c.pop()
        s.c = c
    def _l(o): return o if isinstance(o, UP) else UP([o])
    def __add__(s, o):
        o = UP._l(o); n = max(len(s.c), len(o.c))
        return UP([(s.c[i] if i < len(s.c) else 0) + (o.c[i] if i < len(o.c) else 0) for i in range(n)])
    __radd__ = __add__
    def __neg__(s): return UP([-x for x in s.c])
    def __sub__(s, o): return s + (-UP._l(o))
    def __rsub__(s, o): return UP._l(o) - s
    def __mul__(s, o):
        o = UP._l(o); r = [Q(0)]*(len(s.c) + len(o.c) - 1)
        for i, a in enumerate(s.c):
            if a:
                for j, b in enumerate(o.c): r[i + j] += a*b
        return UP(r)
    __rmul__ = __mul__
    def __pow__(s, k):
        r = UP([1])
        for _ in range(k): r = r*s
        return r
    def __eq__(s, o): return (s - UP._l(o)).c == [0]

def fibre_roundtrip(lam):
    """Points with F = lam: h = t, t a root of F(t,u,v,w) - lam. Returns whether Phi(Psi(q)) == q."""
    u, v, w = (Q(random.randint(-9, 9), random.randint(1, 5)) for _ in range(3))
    UP.MOD = None
    f = F(UP([0, 1]), u, v, w) - lam
    UP.MOD = f.c[:]
    deg = len(f.c) - 1
    q = (UP([0, 1]), UP([u]), UP([v]), UP([w]))
    assert F(*q) == lam
    back = Phi(*Psi(*q))
    UP.MOD = None
    return deg, all(a == b for a, b in zip(back, q))

KC = 6
res = [fibre_roundtrip(0) for _ in range(KC)]
negc = [fibre_roundtrip(1) for _ in range(KC)]
check(f"C1 Phi(Psi(q)) = q at {KC} points of F=0 over Q[t]/(F(t,u,v,w)), deg {res[0][0]} in t",
      all(r[1] for r in res), all(r[1] for r in negc))

# ---------- D. the critical point ----------
class Dual:  # value + gradient in (h,u,v,w)
    def __init__(s, v, g): s.v, s.g = Q(v), [Q(x) for x in g]
    def _l(o): return o if isinstance(o, Dual) else Dual(o, [0]*4)
    def __add__(s, o): o = Dual._l(o); return Dual(s.v + o.v, [a + b for a, b in zip(s.g, o.g)])
    __radd__ = __add__
    def __neg__(s): return Dual(-s.v, [-a for a in s.g])
    def __sub__(s, o): return s + (-Dual._l(o))
    def __rsub__(s, o): return Dual._l(o) - s
    def __mul__(s, o): o = Dual._l(o); return Dual(s.v*o.v, [s.v*b + o.v*a for a, b in zip(s.g, o.g)])
    __rmul__ = __mul__
    def __pow__(s, k):
        r = Dual(1, [0]*4)
        for _ in range(k): r = r*s
        return r

def at(P): return [Dual(P[i], [1 if j == i else 0 for j in range(4)]) for i in range(4)]
P = [Q(2), Q(0), Q(-1, 2), Q(1, 2)]
Fp = F(*at(P)); xP, yP, sP = (c.v for c in xys(*at(P)))
Fn = F(*at([Q(2), Q(0), Q(-1, 2), Q(1, 2) + Q(1, 7)]))
print(f"   at P: x={xP} y={yP} s={sP} F={Fp.v} grad={[str(g) for g in Fp.g]}")
check("D1 F(P) = -1 and grad F(P) = 0 at P=(2,0,-1/2,1/2)",
      Fp.v == -1 and all(g == 0 for g in Fp.g) and (xP, yP, sP) == (-1, 1, 1),
      all(g == 0 for g in Fn.g))


# ---------- E. part 1: the stable-coordinate chain (02-construction.tex) ----------
def part1(p, s, u, F_, J, tw=1):
    x = s**2 - u**2 + p*F_
    H = x**2*F_ - (1 + 2*s*x)*J - p*J**2 - u
    M = [[F_, s - u], [s + u, -p]]
    e, n = [x, -J], [J, x]
    A = [[(1 if i == j else 0) - 2*n[i]*e[j] for j in range(2)] for i in range(2)]   # I - 2 n e^t
    Mp = [[sum(A[i][k]*M[k][j] for k in range(2)) for j in range(2)] for i in range(2)]
    Fp_, pp_ = Mp[0][0], -Mp[1][1]
    sp_, up_ = (Mp[0][1] + Mp[1][0])/2, (Mp[1][0] - Mp[0][1])/2
    B = [[(1 if i == j else 0) + 2*n[i]*e[j] for j in range(2)] for i in range(2)]   # inverse
    Mb = [[sum(B[i][k]*Mp[k][j] for k in range(2)) for j in range(2)] for i in range(2)]
    eMe = sum(e[i]*M[i][j]*e[j] for i in range(2) for j in range(2))
    r = {}
    r["E1 matrix change: -det M' = x, (I+2ne^t)M' = M, u' = u - e^tMe, H = -J-u'"] = (
        -(Mp[0][0]*Mp[1][1] - Mp[0][1]*Mp[1][0]) == x + (tw - 1) and Mb == M and up_ == u - eMe and H == -J - up_)
    # both identities hold in P; in A = P/(H) E1 gives u' = -J, which turns them into Q and f of thm:main
    r["E2 con:candidate: x = s'^2-u'^2+p'F' and p = p'-2x(x(s'-u')+p'J) in P"] = (
        x == sp_**2 - up_**2 + pp_*Fp_ and p == pp_ - 2*tw*x*(x*(sp_ - up_) + pp_*J))
    y, z = s + x*(x + u**2), s*x + p*J
    r["E3 quadric xy - z(z+1) = p(H+u); localized inverse F=(x-s^2+u^2)/p, J=(z-sx)/p"] = (
        x*y - z*(z + tw) == p*(H + u) and F_ == (x - s**2 + u**2)/p and J == (z - s*x)/p)
    x0 = s**2 - u**2
    L = x0**2*F_ - (1 + 2*s*x0)*J
    Nn = (1 - 2*s*x0)*F_ + 4*s**2*J
    Q0 = 2*x0*F_**2 + p*F_**3 - 2*s*F_*J - J**2
    r["E5 det = 1, con:linear-inverse, H = L - u + p*Q0"] = (
        4*s**2*x0**2 + (1 + 2*s*x0)*(1 - 2*s*x0) == 1
        and F_ == 4*s**2*L + (1 + 2*s*x0)*Nn and J == -(1 - 2*s*x0)*L + x0**2*Nn
        and H == L - u + tw*p*Q0)
    return r

class D1:  # value + one tangent: evaluates a derivation at a point
    def __init__(s, v, t): s.v, s.t = Q(v), Q(t)
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

def delta_check(p, s, u, F_, J, cF=2):
    x = s**2 - u**2 + p*F_
    tang = [0, 2*p*x*u, -p, -4*s*x*u - cF*u, -2*x**2*u]          # con:delta on (p,s,u,F,J)
    g = [D1(a, t) for a, t in zip((p, s, u, F_, J), tang)]
    P_, S_, U_, F2, J2 = g
    X = S_**2 - U_**2 + P_*F2
    H = X**2*F2 - (1 + 2*S_*X)*J2 - P_*J2**2 - U_
    Y, Z = S_ + X*(X + U_**2), S_*X + P_*J2
    return X.t == 0 and Y.t == 0 and Z.t == 0 and H.t == p

okE, negE = {}, {}
for _ in range(K):
    pt = [Q(v) for v in rnd(5)]
    for k, v in part1(*pt).items(): okE[k] = okE.get(k, True) and v
    for k, v in part1(*pt, tw=2).items(): negE[k] = negE.get(k, True) and v
    okE["E4 con:delta: Delta(x)=Delta(y)=Delta(z)=0, Delta(H)=p"] = okE.get("E4 con:delta: Delta(x)=Delta(y)=Delta(z)=0, Delta(H)=p", True) and delta_check(*pt)
    negE["E4 con:delta: Delta(x)=Delta(y)=Delta(z)=0, Delta(H)=p"] = negE.get("E4 con:delta: Delta(x)=Delta(y)=Delta(z)=0, Delta(H)=p", True) and delta_check(*pt, cF=3)
for k in sorted(okE):
    check(f"{k}  [{K} pts]", okE[k], negE[k])

pr = max(D[k] for k in D) / N
print(f"Schwartz-Zippel: largest D = {max(D.values())}; a false identity survives one point with prob <= {pr:.1e}, all {K} points <= {pr**K:.1e}")
print(f"runtime {time.time() - t0:.1f}s", file=sys.stderr)
if fails:
    print("RESULT: DISAGREES at", ", ".join(fails)); sys.exit(1)
print("RESULT: holds -- part 1: every identity in the stable-coordinate chain for f; part 2: the explicit maps of Appendix A are mutually inverse between F=0 and A^3, grad F(P)=0, F(P)=-1")
