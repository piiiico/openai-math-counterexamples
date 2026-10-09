#!/usr/bin/env python3
"""C002 row 342: the four-torus example OpenAI added on 7 October to repair a retracted claim (stdlib only).

Retracted claim (previous edition, still in the repo at the pinned commit):
  preprints/Taming-implies-compatibility-on-four-manifolds-September-23-2026/build/sections/01-introduction.tex:39-47
  Corollary cor:taming-cones, for every tamed J on a closed four-manifold: K_J^t = K_J^c + H_J^-.
Repair (current edition): preprints/Taming-implies-compatibility-on-four-manifolds-October-6-2026/build/sections/
  01-introduction.tex:73-77 restricts the equality to h_J^- = b_2^+ - 1 and says the inclusion can be strict;
  08-cones.tex:375-418, Example ex:strict-cones, gives the explicit four-torus. If the example holds, it is a
  counterexample to the retracted corollary (b_2^+(T^4) = 3, h_J^- = 0, and K^c + H^- is strictly smaller than K^t).

Every pointwise claim of the example is checked here. All forms depend only on (x1, x2), so a grid on the
(x1, x2) torus covers the whole manifold. Forms are 4x4 antisymmetric matrices, w(X, Y) = X^T W Y, Euclidean g.
  1. U, V0, W are self-dual; F = (U + f V0 + k W)/r is self-dual with |F|^2 = 2; J := -F (F(X,Y) = g(JX,Y))
     satisfies J^2 = -I and J^T J = I.
  2. eta = U + 2f e13 + 2k e23 is closed (d eta by central differences, h = 1e-5; reported x1e-3 against TOL).
  3. Its self-dual part is r F and its anti-self-dual part is f(e13+e24) + k(e23-e14).
  4. eta is J-compatible: eta(JX, JY) = eta(X, Y) and eta(X, JY) is positive definite, with eigenvalues
     r +- sqrt(f^2 + k^2) (each twice), all > 0.
  5. [eta] = [U]: eta - U = d((G(x1) + K(x2)) dx3) with periodic G = -cos(2 pi x1)/(4 pi), K = -cos(2 pi x2)/(4 pi)
     (derivatives by central differences, reported x1e-3).
  6. U + V0 and U - V0 tame J (symmetric part of w(X, JY) positive definite); their J-invariant parts are
     (1 +- f) F / r.
  7. [U + V0] . [U - V0] = integral of (U+V0) ^ (U-V0) = 0, exact integer arithmetic; both classes square to 4.
  8. H_J^- = 0: constant self-dual forms orthogonal to F are anti-invariant, and a + b f + c k = 0 at the
     three points (0,0), (1/4,0), (0,1/4) forces a = b = c = 0 (exact rationals, determinant 1/16).
     Not computed: the paper's step that a closed anti-invariant form is self-dual harmonic, hence constant.
  The last step ("neither class has a compatible representative") is the two-line argument in the paper:
  a compatible form wedges strictly positively with a tamer, so its class would pair positively with the other.
  Negative arms (each must fire, or the check is blind):
     2-: e13 and e23 coefficients swapped is not closed.        4-: eta without the factor 2 is not J-invariant.
     6-: amplitude 5/4 in place of 1/4: U - V0 stops taming.  7-: (U+V0)^(U+V0) is not zero.
"""
import math, sys
from fractions import Fraction as Q

out = []
def say(s): out.append(s); print(s)
IDX = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]
def form(c):  # c: dict {(i,j): coeff}, i<j zero-based
    W = [[0.0] * 4 for _ in range(4)]
    for (i, j), v in c.items(): W[i][j] += v; W[j][i] -= v
    return W
def coeffs(W): return {p: W[p[0]][p[1]] for p in IDX}
STAR = {(0, 1): ((2, 3), 1), (0, 2): ((1, 3), -1), (0, 3): ((1, 2), 1), (1, 2): ((0, 3), 1), (1, 3): ((0, 2), -1), (2, 3): ((0, 1), 1)}
def star(W):
    c = coeffs(W); o = {}
    for p, v in c.items():
        q, s = STAR[p]; o[q] = o.get(q, 0) + s * v
    return form(o)
def wedge(A, B):  # coefficient of e1234, works on dicts of ints/Fractions too
    a, b = (A if isinstance(A, dict) else coeffs(A)), (B if isinstance(B, dict) else coeffs(B))
    g = lambda d, i, j: d.get((i, j), 0)
    return (g(a,0,1)*g(b,2,3) - g(a,0,2)*g(b,1,3) + g(a,0,3)*g(b,1,2)
            + g(a,1,2)*g(b,0,3) - g(a,1,3)*g(b,0,2) + g(a,2,3)*g(b,0,1))
def mm(A, B): return [[sum(A[i][k] * B[k][j] for k in range(4)) for j in range(4)] for i in range(4)]
def T(A): return [list(r) for r in zip(*A)]
def add(*As, w=None):
    w = w or [1] * len(As)
    return [[sum(wi * A[i][j] for wi, A in zip(w, As)) for j in range(4)] for i in range(4)]
def maxabs(A): return max(abs(v) for r in A for v in r)
def inner(A, B): return sum(coeffs(A)[p] * coeffs(B)[p] for p in IDX)
def eig_sym(S):  # cyclic Jacobi, 4x4
    A = [r[:] for r in S]
    for _ in range(100):
        off = sum(A[i][j] ** 2 for i in range(4) for j in range(4) if i != j)
        if off < 1e-30: break
        for p in range(4):
            for q in range(p + 1, 4):
                if abs(A[p][q]) < 1e-300: continue
                th = 0.5 * math.atan2(2 * A[p][q], A[q][q] - A[p][p])
                c, s = math.cos(th), math.sin(th)
                for k in range(4):
                    akp, akq = A[k][p], A[k][q]; A[k][p] = c * akp - s * akq; A[k][q] = s * akp + c * akq
                for k in range(4):
                    apk, aqk = A[p][k], A[q][k]; A[p][k] = c * apk - s * aqk; A[q][k] = s * apk + c * aqk
    return sorted(A[i][i] for i in range(4))
def sym(A): return [[(A[i][j] + A[j][i]) / 2 for j in range(4)] for i in range(4)]

U = form({(0, 1): 1, (2, 3): 1}); V0 = form({(0, 2): 1, (1, 3): -1}); Wf = form({(0, 3): 1, (1, 2): 1})
TOL = 1e-12
ok = True
sd_ok = all(maxabs(add(star(X), X, w=[1, -1])) == 0 for X in (U, V0, Wf))
N = 96
def fields(x1, x2, amp=0.25):
    f = amp * math.sin(2 * math.pi * x1); k = amp * math.sin(2 * math.pi * x2)
    fp = amp * 2 * math.pi * math.cos(2 * math.pi * x1); kp = amp * 2 * math.pi * math.cos(2 * math.pi * x2)
    return f, k, fp, kp, math.sqrt(1 + f * f + k * k)
H = 1e-5
def d_of(coef, x1, x2):  # coef(x1, x2) -> {(i,j): value}; gradients by central differences -> max |d omega| component
    c1p, c1m, c2p, c2m = coef(x1 + H, x2), coef(x1 - H, x2), coef(x1, x2 + H), coef(x1, x2 - H)
    grad = {p: ((c1p.get(p, 0) - c1m.get(p, 0)) / (2 * H), (c2p.get(p, 0) - c2m.get(p, 0)) / (2 * H)) for p in IDX}
    worst = 0.0
    for a in range(4):
        for b in range(a + 1, 4):
            for c in range(b + 1, 4):
                gd = lambda i, j, m: grad.get((i, j), (0, 0))[m] if m < 2 else 0.0
                v = gd(b, c, a) - gd(a, c, b) + gd(a, b, c)
                worst = max(worst, abs(v))
    return worst
w = {k: 0.0 for k in ["F_sd", "F_norm", "J", "d_eta", "parts", "inv", "eigdev", "exact", "tproj"]}
min_eig_eta = min_tame_p = min_tame_m = math.inf
neg_closed = neg_inv = 0.0; neg_tame = math.inf
for i in range(N):
    for j in range(N):
        x1, x2 = i / N, j / N
        f, k, fp, kp, r = fields(x1, x2)
        F = add(U, V0, Wf, w=[1 / r, f / r, k / r])
        w["F_sd"] = max(w["F_sd"], maxabs(add(star(F), F, w=[1, -1])))
        w["F_norm"] = max(w["F_norm"], abs(inner(F, F) - 2))
        J = [[-v for v in row] for row in F]
        I = [[float(a == b) for b in range(4)] for a in range(4)]
        w["J"] = max(w["J"], maxabs(add(mm(J, J), I)), maxabs(add(mm(T(J), J), I, w=[1, -1])))
        eta = form({(0, 1): 1, (2, 3): 1, (0, 2): 2 * f, (1, 2): 2 * k})
        eta_c = lambda a, b: coeffs(form({(0, 1): 1, (2, 3): 1, (0, 2): 2 * fields(a, b)[0], (1, 2): 2 * fields(a, b)[1]}))
        bad_c = lambda a, b: coeffs(form({(0, 1): 1, (2, 3): 1, (1, 2): 2 * fields(a, b)[0], (0, 2): 2 * fields(a, b)[1]}))
        w["d_eta"] = max(w["d_eta"], d_of(eta_c, x1, x2) * 1e-3)  # finite-difference noise ~1e-10: scaled into TOL
        neg_closed = max(neg_closed, d_of(bad_c, x1, x2))  # 2f e23 (and 2k e13): not closed
        sd = add(eta, star(eta), w=[.5, .5]); asd = add(eta, star(eta), w=[.5, -.5])
        asd_paper = form({(0, 2): f, (1, 3): f, (1, 2): k, (0, 3): -k})
        w["parts"] = max(w["parts"], maxabs(add(sd, F, w=[1, -r])), maxabs(add(asd, asd_paper, w=[1, -1])))
        def inv_part(X): return add(X, mm(mm(T(J), X), J), w=[.5, .5])
        w["inv"] = max(w["inv"], maxabs(add(inv_part(eta), eta, w=[1, -1])))
        S = mm(eta, J)
        w["inv"] = max(w["inv"], maxabs(add(S, T(S), w=[1, -1])))
        ev = eig_sym(sym(S)); s = math.sqrt(f * f + k * k)
        w["eigdev"] = max(w["eigdev"], max(abs(a - b) for a, b in zip(ev, [r - s, r - s, r + s, r + s])))
        min_eig_eta = min(min_eig_eta, ev[0])
        eta_bad = form({(0, 1): 1, (2, 3): 1, (0, 2): f, (1, 2): k})
        neg_inv = max(neg_inv, maxabs(add(inv_part(eta_bad), eta_bad, w=[1, -1])))
        G = lambda x: -math.cos(2 * math.pi * x) / (4 * math.pi)  # primitive, by finite differences below
        G_p = (G(x1 + H) - G(x1 - H)) / (2 * H); K_p = (G(x2 + H) - G(x2 - H)) / (2 * H)
        w["exact"] = max(w["exact"], abs(G_p - 2 * f) * 1e-3, abs(K_p - 2 * k) * 1e-3)
        for sgn in (1, -1):
            X = add(U, V0, w=[1, sgn])
            w["tproj"] = max(w["tproj"], maxabs(add(inv_part(X), F, w=[1, -(1 + sgn * f) / r])))
            m = eig_sym(sym(mm(X, J)))[0]
            if sgn == 1: min_tame_p = min(min_tame_p, m)
            else: min_tame_m = min(min_tame_m, m)
        fb, kb, _, _, rb = fields(x1, x2, amp=1.25)
        Fb = add(U, V0, Wf, w=[1 / rb, fb / rb, kb / rb]); Jb = [[-v for v in row] for row in Fb]
        neg_tame = min(neg_tame, eig_sym(sym(mm(add(U, V0, w=[1, -1]), Jb)))[0])
# G, K periodic: values at x = 0 and x = 1 agree
per = abs(-math.cos(0) / (4 * math.pi) + math.cos(2 * math.pi) / (4 * math.pi))
say(f"grid: {N}x{N} points on the (x1, x2) torus; tolerance {TOL:g}")
say(f"1. U, V0, W self-dual (exact): {sd_ok}; F self-dual max dev {w['F_sd']:.1e}; |F|^2 = 2 max dev {w['F_norm']:.1e}; J^2 = -I, J^T J = I max dev {w['J']:.1e}")
say(f"2. d eta = 0: max |component| x1e-3 {w['d_eta']:.1e}   2-. coefficients swapped: max |d| {neg_closed:.3f} (must be > 0.1)")
say(f"3. SD part = r F and ASD part = f(e13+e24) + k(e23-e14): max dev {w['parts']:.1e}")
say(f"4. eta J-invariant max dev {w['inv']:.1e}; eigenvalues of eta(X,JY) vs r -+ sqrt(f^2+k^2): max dev {w['eigdev']:.1e}; smallest eigenvalue {min_eig_eta:.6f}")
say(f"   4-. eta without the factor 2: J-invariance dev {neg_inv:.3f} (must be > 0.1)")
say(f"5. eta - U = d((G+K) dx3): max |G'-2f|, |K'-2k| {w['exact']:.1e}; G, K periodic, dev {per:.1e}")
say(f"6. invariant part of U +- V0 = (1 +- f) F / r max dev {w['tproj']:.1e}; min eigenvalue of sym(w(X,JY)): U+V0 {min_tame_p:.6f}, U-V0 {min_tame_m:.6f}")
say(f"   6-. amplitude 5/4: min eigenvalue for U-V0 {neg_tame:.6f} (must be < 0)")
P = {(0, 1): 1, (2, 3): 1, (0, 2): 1, (1, 3): -1}; M_ = {(0, 1): 1, (2, 3): 1, (0, 2): -1, (1, 3): 1}
pair, sqp, sqm = wedge(P, M_), wedge(P, P), wedge(M_, M_)
say(f"7. (U+V0)^(U-V0) = {pair} e1234 (exact); (U+V0)^2 = {sqp}, (U-V0)^2 = {sqm}   7-. control: (U+V0)^(U+V0) != 0: {sqp != 0}")
# 8. anti-invariant constant SD forms: for every point, aU+bV0+cW orthogonal to F is anti-invariant (sampled), and exact rank
f_, k_, _, _, r_ = fields(0.3, 0.7)
F_ = add(U, V0, Wf, w=[1 / r_, f_ / r_, k_ / r_]); J_ = [[-v for v in row] for row in F_]
basis_perp = [add(U, V0, w=[-f_, 1]), add(U, Wf, w=[-k_, 1])]  # (a,b,c) = (-f,1,0), (-k,0,1): orthogonal to (1,f,k)
anti = max(maxabs(add(mm(mm(T(J_), X), J_), X)) for X in basis_perp)
Mx = [[Q(1), Q(0), Q(0)], [Q(1), Q(1, 4), Q(0)], [Q(1), Q(0), Q(1, 4)]]
det = (Mx[0][0] * (Mx[1][1] * Mx[2][2] - Mx[1][2] * Mx[2][1]) - Mx[0][1] * (Mx[1][0] * Mx[2][2] - Mx[1][2] * Mx[2][0])
       + Mx[0][2] * (Mx[1][0] * Mx[2][1] - Mx[1][1] * Mx[2][0]))
say(f"8. SD forms orthogonal to F are anti-invariant (point (0.3,0.7)): dev {anti:.1e}; det[(1,f,k) at (0,0),(1/4,0),(0,1/4)] = {det} (exact, != 0 => H_J^- = 0)")
ok = (sd_ok and all(v < TOL for v in w.values()) and per < TOL and min_eig_eta > 0 and min_tame_p > 0 and min_tame_m > 0
      and neg_closed > 0.1 and neg_inv > 0.1 and neg_tame < 0 and pair == 0 and sqp == 4 and sqm == 4 and anti < TOL and det != 0)
say(f"RESULT: {'holds' if ok else 'fails'}")
open(__file__.replace("check.py", "output.txt"), "w").write("\n".join(out) + "\n")
sys.exit(0 if ok else 1)
