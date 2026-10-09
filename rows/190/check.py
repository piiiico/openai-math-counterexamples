#!/usr/bin/env python3
"""Family 190: 'Polynomial removal fails for ordered binary matrices' (Sept 25 2026).

H (66x66) and A_h (n_h x n_h, n_h = (386h+2)2^h) are written down rule by rule in
02-construction.tex. This script builds both from those rules and computes:
  1. lem:anchor-properties on S (03-pinning.tex:20-27), exactly.
  2. the paper's claim that the variable-entry table has no conflicting assignments
     (02-construction.tex:190-199), over every pair of variable positions, h = 1..5.
  3. lem:nonanchor-traces (03-pinning.tex:73-77), exhaustively, h = 1, 2.
  4. prop:copy-count (03b-count.tex:8-20): every body (rows r1<r2 in R_1(t),R_2(t), columns
     c1<c2 in C_1(t),C_2(t), entries forming P) of every mode puts (r1,c1) on the leaf
     diagonal L_h; all bodies enumerated, h = 1..5.
  5. h = 1, the whole 776x776 matrix: every body found in 4 completes, with one position per
     anchor group of its mode, to a 66x66 submatrix equal to H at strictly increasing indices
     (so A_1 contains H, and each body in 4 is a real copy).
  6. the headline inequality N_H(A_h)/n^132 <= eps_h 2^-h, exact, for h = 1..5, with N_H counted
     as (bodies) * m^128. That count assumes lem:anchor-rigidity, a proof step that is NOT computed.
The distance bound dist_H(A_h) >= eps_h (prop:distance) quantifies over all edits; not computed.
Negative arms: S with two equal rows (1 must fail); minus-table rule [p<q] -> [p<=q] (4 must
find bodies off the diagonal); a body whose (r1,c1) is moved off the diagonal (5 must fail).
"""
import itertools, math, sys, time
from fractions import Fraction as Fr
t0 = time.time()
s = 64
def eta(b, a): return (a >> (5 - b)) & 1
def S_entry(u, v):
    if 33 <= u <= 64 and 60 <= v <= 64: return eta(v - 59, u - 33)
    return int(u != v)
S = [[S_entry(u, v) for v in range(1, s + 1)] for u in range(1, s + 1)]
H = [S[u] + [int(u == 0), int(u == 1)] for u in range(s)] + [[int(v == 0) for v in range(s)] + [1, 0], [int(v == 1) for v in range(s)] + [1, 1]]
P = [[1, 0], [1, 1]]

def anchor_props(S):
    rows_distinct = len({tuple(r) for r in S}) == s
    cols_distinct = len({tuple(c) for c in zip(*S)}) == s
    col32 = all(sum(1 - S[u][v] for u in range(32)) <= 1 for v in range(s))
    row32 = all(sum(1 - S[u][v] for v in range(32)) <= 1 for u in range(s))
    ones = min(map(sum, S)) >= 58 and min(map(sum, zip(*S))) >= 48
    words = sorted(tuple(S[u][59:64]) for u in range(32, 64)) == sorted(itertools.product((0, 1), repeat=5))
    return [rows_distinct, cols_distinct, col32, row32, ones, words]
ok = True
r = anchor_props(S); print("1. lem:anchor-properties [rows distinct, cols distinct, col<=1 zero in rows 1-32, row<=1 zero in cols 1-32, ones>=58/48, 32 words]:", r); ok &= all(r)
Sbad = [row[:] for row in S]; Sbad[1] = Sbad[0][:]
r = anchor_props(Sbad); print("1. negative arm (row 2 := row 1):", r, "->", "rejected" if not all(r) else "NOT REJECTED"); ok &= not all(r)

def build(h, minus_rule_le=False):
    m = 2 ** h
    modes = []
    for i in range(1, h + 1):
        modes += [("V+", i, None), ("V-", i, None), ("W+", i, 0), ("W+", i, 1), ("W-", i, 0), ("W-", i, 1)]
    # labels: ('A', mode_index, u) | ('D',) | ('X', i, p, signs)  (signs = frozenset)
    def var_order(i, p, rowaxis):
        if i == h: return [("X", h, p, frozenset("+-"))]
        bsize = m >> i
        first, last = ("-", "+") if rowaxis else ("+", "-")
        out = [("X", i, p, frozenset(first))] * bsize
        out += var_order(i + 1, 2 * p, rowaxis) + var_order(i + 1, 2 * p + 1, rowaxis)
        return out + [("X", i, p, frozenset(last))] * bsize
    anchors = [("A", t, u) for t in range(len(modes)) for u in range(1, s + 1) for _ in range(m)]
    rows = anchors + var_order(0, 0, True) + [("D",)] * m
    cols = anchors + [("D",)] * m + var_order(0, 0, False)
    assert len(rows) == len(cols) == (386 * h + 2) * m
    def inset(lab, spec, row):  # spec: (sign, depth, parity or None) or 'D'
        if spec == "D": return lab[0] == "D"
        sg, dep, par = spec
        return lab[0] == "X" and lab[1] == dep and sg in lab[3] and (par is None or lab[2] % 2 == par)
    def roles(t):
        kind, i, d = modes[t]
        if kind == "V+": return [("+", i, None), ("+", i - 1, None)], ["D", ("+", i - 1, None)]
        if kind == "V-": return [("-", i - 1, None), ("-", i, None)], ["D", ("-", i - 1, None)]
        if kind == "W+": return [("+", i, d), "D"], [("+", i - 1, None), ("+", i, d)]
        return [("-", i, d), "D"], [("-", i, d), ("-", i - 1, None)]
    R = [roles(t) for t in range(len(modes))]
    def var_entry(rl, cl, collect=None):
        _, i, p, rs = rl; _, j, q, cs = cl
        vals = set()
        for sr in rs:
            for sc in cs:
                if sr != sc: continue
                if sr == "+" and j == i: vals.add(int(p <= q))
                if sr == "-" and j == i and i < h: vals.add(int(p <= q) if minus_rule_le else int(p < q))
                if sr == "+" and j == i - 1: vals.add(int(p // 2 <= q))
                if sr == "-" and j == i - 1: vals.add(int(p // 2 < q))
        if collect is not None: collect.append(len(vals) <= 1)
        return vals.pop() if vals else 0
    def entry(rl, cl, collect=None):
        if rl[0] == "A" and cl[0] == "A": return S[rl[2] - 1][cl[2] - 1] if rl[1] == cl[1] else 0
        if cl[0] == "A":
            t, v = cl[1], cl[2]
            return int(any(inset(rl, R[t][0][j], True) and v == j + 1 for j in range(2)))
        if rl[0] == "A":
            t, u = rl[1], rl[2]
            return int(any(inset(cl, R[t][1][j], False) and u == j + 1 for j in range(2)))
        if rl[0] == "D" or cl[0] == "D": return 1
        return var_entry(rl, cl, collect)
    return dict(m=m, modes=modes, rows=rows, cols=cols, roles=R, entry=entry, inset=inset)

# 2. no conflicting assignments
for h in range(1, 6):
    B = build(h); col = []
    vr = sorted(set(l for l in B["rows"] if l[0] == "X")); vc = sorted(set(l for l in B["cols"] if l[0] == "X"))
    for a in vr:
        for b in vc: B["entry"](a, b, col)
    ok &= all(col)
    print(f"2. h={h}: variable block pairs checked {len(col)}, conflicting {col.count(False)}")

# 3. non-anchor traces
for h in (1, 2):
    B = build(h); E = B["entry"]
    nr = [l for l in B["rows"] if l[0] != "A"]; nc = [l for l in B["cols"] if l[0] != "A"]
    colvec = [tuple(E(r, c) for r in nr) for c in nc]
    shattered = 0
    for five in itertools.combinations(range(len(nc)), 5):
        if len({tuple(colvec[c][k] for c in five) for k in range(len(nr))}) == 32: shattered += 1
    print(f"3. h={h}: {len(nc)} non-anchor columns, 5-sets shattered by non-anchor rows: {shattered}")
    ok &= shattered == 0

def bodies(B):
    E, rows, cols = B["entry"], B["rows"], B["cols"]
    out = []
    ridx = [k for k, l in enumerate(rows) if l[0] != "A"]; cidx = [k for k, l in enumerate(cols) if l[0] != "A"]
    for t, (rr, cc) in enumerate(B["roles"]):
        R1 = [k for k in ridx if B["inset"](rows[k], rr[0], True)]; R2 = [k for k in ridx if B["inset"](rows[k], rr[1], True)]
        C1 = [k for k in cidx if B["inset"](cols[k], cc[0], False)]; C2 = [k for k in cidx if B["inset"](cols[k], cc[1], False)]
        for r1 in R1:
            for r2 in R2:
                if r2 <= r1: continue
                for c1 in C1:
                    if E(rows[r1], cols[c1]) != 1 or E(rows[r2], cols[c1]) != 1: continue
                    for c2 in C2:
                        if c2 > c1 and E(rows[r1], cols[c2]) == 0 and E(rows[r2], cols[c2]) == 1:
                            out.append((t, r1, r2, c1, c2))
    return out
def on_diag(B, r1, c1):
    a, b = B["rows"][r1], B["cols"][c1]
    return a[0] == b[0] == "X" and a[1] == b[1] == B_h(B) and a[2] == b[2]
def B_h(B): return B["modes"][-1][1]
for h in range(1, 6):
    B = build(h); bl = bodies(B); m = B["m"]; n = len(B["rows"])
    off = [b for b in bl if not on_diag(B, b[1], b[3])]
    kinds = sorted({B["modes"][b[0]][0] + str(B["modes"][b[0]][1]) for b in bl})
    print(f"4. h={h}: bodies {len(bl)} (modes {kinds}), off the leaf diagonal {len(off)}")
    ok &= len(off) == 0 and len(bl) > 0
    NH = len(bl) * m ** 128; eps = Fr(1, (386 * h + 2) ** 2)
    lhs = Fr(NH, n ** 132)
    print(f"6. h={h}: n={n}, N_H = {len(bl)}*m^128 (assumes lem:anchor-rigidity), N_H/n^132 <= eps*2^-h: {lhs <= eps / 2 ** h}  (log10 of ratio {__import__('math').log10(lhs.numerator) - __import__('math').log10(lhs.denominator) - __import__('math').log10((eps / 2 ** h).numerator) + __import__('math').log10((eps / 2 ** h).denominator):.1f})")
    ok &= lhs <= eps / 2 ** h
Bn = build(3, minus_rule_le=True); bn = bodies(Bn); offn = [b for b in bn if not on_diag(Bn, b[1], b[3])]
print("4. negative arm (minus rule [p<=q], h=3): bodies off the diagonal", len(offn), "->", "rejected" if offn else "NOT REJECTED"); ok &= len(offn) > 0

# 5. h = 1: full matrix, extract each body's 66x66 copy
B = build(1); rows, cols, E = B["rows"], B["cols"], B["entry"]
def copy_ok(t, r1, r2, c1, c2):
    ar = [next(k for k, l in enumerate(rows) if l == ("A", t, u)) for u in range(1, s + 1)]
    ac = [next(k for k, l in enumerate(cols) if l == ("A", t, u)) for u in range(1, s + 1)]
    ri, ci = ar + [r1, r2], ac + [c1, c2]
    inc = all(x < y for x, y in zip(ri, ri[1:])) and all(x < y for x, y in zip(ci, ci[1:]))
    return inc and [[E(rows[a], cols[b]) for b in ci] for a in ri] == H
bl = bodies(B); res = [copy_ok(*b) for b in bl]
print(f"5. h=1 (n={len(rows)}): bodies completed to an ordered 66x66 copy equal to H: {sum(res)} of {len(bl)}")
ok &= all(res) and len(res) > 0
t, r1, r2, c1, c2 = bl[0]
c1b = next(k for k in range(len(cols)) if cols[k][0] == "X" and cols[k] != cols[c1] and k < c2)
negc = copy_ok(t, r1, r2, c1b, c2)
print("5. negative arm (body column c1 moved to another variable column):", "rejected" if not negc else "NOT REJECTED"); ok &= not negc
print("RESULT:", "holds" if ok else "FAILS")
print(f"runtime {time.time()-t0:.1f}s", file=sys.stderr)
sys.exit(0 if ok else 1)
