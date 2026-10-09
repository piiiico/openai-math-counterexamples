#!/usr/bin/env python3
"""Family 199: the Auslander-Reiten and Tachikawa counterexamples over k = F_2(q,H1,H2).
The claim, Ext^i(Z,Z) = 0 = Ext^i(Z,Lambda) for EVERY i >= 1, rests on an infinite,
non-periodic resolution ('the powers of q give an infinite resolution', H1/H2 of infinite
multiplicative order: 01-introduction.tex:41-45). No finite computation decides it.
What is finite and written down is the starting algebra C (03-algebra.tex:13-38). This script
checks Lemma alg:C exactly: the multiplication table is associative on all 1000 basis
triples, unital, dimension 10, (rad C)^5 = 0 and utut = q(1+q)z != 0.
Scalars live in F_2[q] (only q, q^2, 1+q occur), as Python ints = bitmasks, carry-less product.
Negative arm: ut = y + x instead of y + qx must break associativity.
"""
import itertools, sys, time
t0 = time.time()
def pm(a, b):
    r = 0
    while b:
        if b & 1: r ^= a
        a <<= 1; b >>= 1
    return r
Q, ONE = 0b10, 0b1
B = ["e", "x", "y", "z", "u", "v", "f", "n", "t", "j"]
corner = {"e": "ee", "x": "ee", "y": "ee", "z": "ee", "u": "ef", "v": "ef", "t": "fe", "j": "fe", "f": "ff", "n": "ff"}
def table(ut_x_coeff):
    T = {("x", "y"): {"z": Q}, ("y", "x"): {"z": ONE}, ("x", "u"): {"v": ONE}, ("y", "u"): {"v": ONE},
         ("t", "x"): {"j": ONE}, ("t", "y"): {"j": pm(Q, Q)}, ("u", "t"): {"y": ONE, "x": ut_x_coeff},
         ("v", "t"): {"z": Q}, ("u", "j"): {"z": ONE}, ("t", "u"): {"n": ONE ^ Q}, ("n", "t"): {"j": Q},
         ("u", "n"): {"v": ONE}}
    def mul_basis(a, b):
        if a in "ef":
            return {b: ONE} if corner[b][0] == a else {}
        if b in "ef":
            return {a: ONE} if corner[a][1] == b else {}
        return dict(T.get((a, b), {}))
    return mul_basis
def mul(mb, X, Y):
    out = {}
    for a, ca in X.items():
        for b, cb in Y.items():
            for c, cc in mb(a, b).items():
                out[c] = out.get(c, 0) ^ pm(pm(ca, cb), cc)
    return {k: v for k, v in out.items() if v}
def assoc_failures(mb):
    bad = 0
    for a, b, c in itertools.product(B, repeat=3):
        bad += mul(mb, mul(mb, {a: ONE}, {b: ONE}), {c: ONE}) != mul(mb, {a: ONE}, mul(mb, {b: ONE}, {c: ONE}))
    return bad
mb = table(Q)
ok = True
af = assoc_failures(mb); print("associativity failures over 1000 basis triples:", af); ok &= af == 0
one = {"e": ONE, "f": ONE}
unit = all(mul(mb, one, {a: ONE}) == {a: ONE} == mul(mb, {a: ONE}, one) for a in B)
print("e + f is a two-sided unit:", unit, "  dimension:", len(B)); ok &= unit and len(B) == 10
rad = [a for a in B if a not in "ef"]
def span_products(k):  # all products of k radical basis vectors (spanning set of rad^k)
    cur = [{a: ONE} for a in rad]
    for _ in range(k - 1):
        cur = [p for p in (mul(mb, X, {a: ONE}) for X in cur for a in rad) if p]
    return cur
r4, r5 = span_products(4), span_products(5)
print("nonzero products of 5 radical basis vectors:", len(r5), "  of 4:", len(r4)); ok &= len(r5) == 0 and len(r4) > 0
# radical is nilpotent ideal: closed under multiplication by basis on both sides
ideal = all(set(mul(mb, {a: ONE}, {b: ONE})) <= set(rad) for a in B for b in rad) and all(set(mul(mb, {b: ONE}, {a: ONE})) <= set(rad) for a in B for b in rad)
print("span of the 8 non-idempotents is a two-sided ideal:", ideal); ok &= ideal
utut = mul(mb, mul(mb, mul(mb, {"u": ONE}, {"t": ONE}), {"u": ONE}), {"t": ONE})
print("utut =", {k: bin(v) for k, v in utut.items()}, " expected q(1+q)z =", bin(pm(Q, ONE ^ Q)))
ok &= utut == {"z": pm(Q, ONE ^ Q)}
neg = assoc_failures(table(ONE)); print("negative arm (ut = y + x): associativity failures", neg, "->", "rejected" if neg else "NOT REJECTED"); ok &= neg > 0
print("RESULT:", "holds" if ok else "FAILS", "(Lemma alg:C only; the Ext claim is not finite)")
print(f"runtime {time.time()-t0:.2f}s", file=sys.stderr)
sys.exit(0 if ok else 1)
