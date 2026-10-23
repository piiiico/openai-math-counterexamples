#!/usr/bin/env python3
"""Pico check for PR #18, run from rows/047: python3 exact/pico_check.py
Rebuilds q with the PR code, then evaluates W(e0) - w = q (H(L) + p^3 w) at 4 random 64-bit points using
Pico's own row-047 objects() for H(L), Q, F, Q1, L*, W and e0. Negative arm: e0 with -2w must mismatch."""
import sys, random, io, contextlib, importlib.util
from fractions import Fraction as Fr
def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec)
    with contextlib.redirect_stdout(io.StringIO()):
        try: spec.loader.exec_module(m)
        except SystemExit: pass
    return m
ours = load('ours', 'check.py'); pr = load('pr', 'exact/check.py')
o = pr.build(); P = pr
HL, Ls, e0 = o["H_L"], o["L_star"], o["e0"]
D = HL + P.p**3 * P.w
W = -(HL.subst({"L": Ls + P.p**3 * P.E}).divide_by_var_power("p", 3))
R = W.subst({"E": e0}) - P.w
q = P.exact_quotient_in_w(R, D)
print('q terms', len(q.terms), 'sha', q.canonical_sha256(P.Q_HASH_ORDER))
def ev(poly, vals):
    tot = Fr(0)
    for e, c in poly.terms.items():
        t = Fr(c)
        for n, k in zip(P.VARS, e):
            if k: t *= vals[n]**k
        tot += t
    return tot
random.seed(1023); bad = 0; T = 4
for tw in (1, 2):
  bad = 0
  for _ in range(T):
    p, s, u, Mv, Lr, wv = (Fr(random.randrange(1, 2**64)) for _ in range(6))
    ob = ours.objects(p, s, u, Mv)
    Wf = lambda e: -ob["H"](ob["Ls"] + p**3*e)/p**3
    hv = u - p*ob["Q"](Lr) - p**3*ob["F"](Lr)**3 - p**2*wv
    e0v = -wv*tw - p*ob["F"](Lr)**3 - ob["Q1"](Lr)*hv   # tw=2 perturbs sign/scale of w in e0 (negative arm)
    lhs = Wf(e0v) - wv
    rhs = ev(q, dict(p=p, s=s, u=u, M=Mv, L=Lr, w=wv, F=0, J=0, E=0)) * (ob["H"](Lr) + p**3*wv)
    bad += lhs != rhs
  print('tw', tw, 'mismatches', bad, 'of', T)
