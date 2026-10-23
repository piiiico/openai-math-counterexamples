#!/usr/bin/env python3
"""Pico check for PR #14, written from 08-cones.tex:375-418 without reading exact/check.py.
2-forms as vectors in the basis e12,e13,e14,e23,e24,e34; exact Fractions; no sqrt (r^2 kept).
Run from rows/342: python3 exact/pico_check.py"""
import random, sys
from fractions import Fraction as Fr
B = ["12", "13", "14", "23", "24", "34"]
def form(**c): return [Fr(c.get("e" + b, 0)) for b in B]
def add(*fs): return [sum(x) for x in zip(*fs)]
def sc(a, f): return [a * x for x in f]
def star(f): a12, a13, a14, a23, a24, a34 = f; return [a34, -a24, a23, a14, -a13, a12]
def wedge(a, b):  # coefficient of e1234 in a ^ b
    return a[0]*b[5] - a[1]*b[4] + a[2]*b[3] + a[3]*b[2] - a[4]*b[1] + a[5]*b[0]
def dot(a, b): return sum(x * y for x, y in zip(a, b))
U, V0, W = form(e12=1, e34=1), form(e13=1, e24=-1), form(e14=1, e23=1)
def checks(f, k, tw=1):
    r2 = 1 + f*f + k*k
    rF = add(U, sc(f, V0), sc(k, W))                       # r F
    eta = add(U, form(e13=2*f*tw), form(e23=2*k))
    sd = sc(Fr(1, 2), add(eta, star(eta))); asd = sc(Fr(1, 2), add(eta, sc(-1, star(eta))))
    ok = {
        "F self-dual, |F|^2 = 2": star(rF) == rF and dot(rF, rF) == 2 * r2,
        "SD(eta) = rF": sd == rF,
        "ASD(eta) = f(e13+e24) + k(e23-e14)": asd == add(form(e13=f, e24=f), form(e23=k, e14=-k)),
        # invariant projection of an SD form onto F is <a,F>F/2; with rF: <a,rF>/(2 r^2) * rF
        "proj(U +- V0) = (1 +- f)F/r": all(dot(add(U, sc(sg, V0)), rF) == 2 * (1 + sg * f) for sg in (1, -1)),
        "tamers positive with margin 1/sqrt2 (|f|,|k| <= 1/4)": all(2 * (1 + sg * f)**2 >= r2 for sg in (1, -1)),
    }
    return ok
random.seed(342); allok = True
pts = [(Fr(random.randint(-25, 25), 100), Fr(random.randint(-25, 25), 100)) for _ in range(200)]
pts += [(Fr(sf, 4), Fr(sk, 4)) for sf in (-1, 1) for sk in (-1, 1)]       # extremes: margin is tight here
for name in checks(Fr(0), Fr(0)):
    good = all(checks(f, k)[name] for f, k in pts); allok &= good
    print(("ok   " if good else "FAIL ") + name + f"  [{len(pts)} rational points]")
pair = wedge(add(U, V0), add(U, sc(-1, V0)))
print(("ok   " if pair == 0 else "FAIL ") + f"[U+V0].[U-V0] = U^2 - V0^2 = {pair}"); allok &= pair == 0
neg = all(checks(f, k, tw=2)["SD(eta) = rF"] for f, k in pts if f)
print(("ok   " if not neg else "FAIL ") + "negative arm (eta with 4f e13) rejected"); allok &= not neg
print("RESULT:", "holds" if allok else "DISAGREES"); sys.exit(0 if allok else 1)
