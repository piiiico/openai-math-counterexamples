#!/usr/bin/env python3
"""C002 row 161: Sidorenko counterexample -- the finite part.

Theorem (preprints/A-counterexample-to-Sidorenkos-conjecture-September-23-2026/build/sections/introduction.tex:18-25):
H = incidence graph of 22 triples on 13 points (Table tab:complex), 35 vertices, 66 edges;
"There is a finite simple undirected graph G ... such that t(H,G) < p(G)^66."
introduction.tex:29-30: "This route specifies H explicitly and proves existence of G".
So the host G is NOT given; no program can check t(H,G) < p^66.  What IS finite is H and
Proposition prop:complex (sections/complex.tex:73-89).  This script parses Table tab:complex and
Table tab:complex-orders straight from the .tex (pass the path), then checks every claim of the
proposition plus the vertex/edge counts and the degree table eq:complex-colors.
Usage: python3 check.py <path-to-openai-math>/preprints/A-counterexample-to-Sidorenkos-conjecture-September-23-2026/build/sections/complex.tex
"""
import re, sys
from itertools import combinations
from collections import Counter

tex = open(sys.argv[1], encoding="utf-8").read()
ok = True
def claim(name, cond):
    global ok; ok &= bool(cond); print(("PASS " if cond else "FAIL ") + name)

# --- parse Table tab:complex
body = tex[tex.index(r"\begin{tabular}"):tex.index(r"\label{tab:complex}")]
faces, opp, bits = {}, {}, {}
for m in re.finditer(r"^(\d+)\s*&(\d+)&(\d+)&(\d+)\s*&(\d+)&(\d+)&(\d+)\s*&([01]{3})\\\\", body, re.M):
    j, a, b, c, o12, o13, o23, bs = m.groups()
    j = int(j); faces[j] = (int(a), int(b), int(c)); opp[j] = (int(o12), int(o13), int(o23)); bits[j] = bs
claim("parsed 22 faces 0..21", sorted(faces) == list(range(22)))
I = set(x for f in faces.values() for x in f)
claim("13 points 0..12", I == set(range(13)))
nv, ne = len(I) + len(faces), sum(len(set(f)) for f in faces.values())
claim(f"H has 35 vertices and 66 edges (got {nv}, {ne})", (nv, ne) == (35, 66))
claim("faces are distinct 3-sets", len(set(frozenset(f) for f in faces.values())) == 22 and all(len(set(f)) == 3 for f in faces.values()))

# --- (1) every pair in exactly two faces, |E|=33, opposite-face columns right, face-neighbour graph connected
pairc = Counter(frozenset(p) for f in faces.values() for p in combinations(f, 2))
claim(f"|E| = 33 (got {len(pairc)})", len(pairc) == 33)
claim("every pair in exactly two faces", set(pairc.values()) == {2})
good = True
for j, (a, b, c) in faces.items():
    for (x, y), o in zip(((a, b), (a, c), (b, c)), opp[j]):
        others = [k for k, f in faces.items() if k != j and x in f and y in f]
        good &= others == [o]
claim("opposite-face columns j12,j13,j23 match the triples", good)
def connected(nodes, adj):
    nodes = list(nodes)
    if not nodes: return False
    seen, st = {nodes[0]}, [nodes[0]]
    while st:
        u = st.pop()
        for v in adj(u):
            if v in nodes and v not in seen: seen.add(v); st.append(v)
    return len(seen) == len(nodes)
share = lambda j, k: len(set(faces[j]) & set(faces[k])) == 2
claim("face-neighbour graph connected", connected(faces, lambda u: [k for k in faces if k != u and share(u, k)]))
Hadj = lambda u: ([("J", j) for j, f in faces.items() if u[1] in f] if u[0] == "I" else [("I", i) for i in faces[u[1]]])
claim("H connected (bipartite by construction)", connected([("I", i) for i in I] + [("J", j) for j in faces], Hadj))

# --- (2) bit classes: 11 faces covering 13 points, with an exposure order
orders_tex = tex[tex.index(r"\label{tab:complex}"):tex.index(r"\label{tab:complex-orders}")]
given = {(int(p), int(v)): [int(x) for x in o.split(",")]
         for p, v, o in re.findall(r"^(\d)&([01])&\$([\d,]+)\$", orders_tex, re.M)}
claim("parsed 6 given exposure orders", len(given) == 6)
def exposure_ok(order):
    seen = set(faces[order[0]]); used = [order[0]]
    for j in order[1:]:
        if not any(share(j, k) for k in used): return False
        new = set(faces[j]) - seen
        if len(new) != 1: return False
        seen |= new; used.append(j)
    return seen == I
def exposure_exists(cls):  # independent search, does not use the given order
    for root in cls:
        seen, used, rest, progress = set(faces[root]), [root], set(cls) - {root}, True
        while rest and progress:
            progress = False
            for j in sorted(rest):
                if any(share(j, k) for k in used) and len(set(faces[j]) - seen) == 1:
                    seen |= set(faces[j]); used.append(j); rest.discard(j); progress = True; break
        if not rest and seen == I: return True
    return False
for pos in range(3):
    for val in "01":
        cls = sorted(j for j in faces if bits[j][pos] == val)
        cov = set(x for j in cls for x in faces[j])
        claim(f"bit {pos+1} class {val}: 11 faces covering 13 points", len(cls) == 11 and cov == I)
        g = given.get((pos + 1, int(val)))
        claim(f"bit {pos+1} class {val}: paper's order is a permutation of the class and valid", g is not None and sorted(g) == cls and exposure_ok(g))
        claim(f"bit {pos+1} class {val}: an exposure order found by independent greedy search", exposure_exists(cls))

# --- (3) a_e >= 1/3 for all e, some > 1/3, a_{0,2} = 1
a = {}
for e in pairc:
    on = [j for j, f in faces.items() if e <= set(f)]
    if len(on) != 2: a[e] = 0.0; continue
    j, k = on
    a[e] = sum(x != y for x, y in zip(bits[j], bits[k])) / 3
claim("every a_e >= 1/3", min(a.values()) >= 1/3 - 1e-12)
claim("some a_e > 1/3", max(a.values()) > 1/3 + 1e-12)
claim("a_{0,2} = 1", abs(a[frozenset((0, 2))] - 1) < 1e-12)

# --- (4) colour refinement of H from part colours is discrete on each part
nodes = [("I", i) for i in I] + [("J", j) for j in faces]
col = {u: u[0] for u in nodes}
for _ in range(100):
    sig = {u: (col[u], tuple(sorted(Counter(col[v] for v in Hadj(u)).items()))) for u in nodes}
    ids = {s: n for n, s in enumerate(sorted(set(sig.values()), key=repr))}
    new = {u: ids[sig[u]] for u in nodes}
    if len(set(new.values())) == len(set(col.values())): break
    col = new
claim("colour refinement: all 13 point colours distinct", len(set(col[("I", i)] for i in I)) == 13)
claim("colour refinement: all 22 face colours distinct", len(set(col[("J", j)] for j in faces)) == 22)

# --- degree table eq:complex-colors
deg = {i: sum(1 for e in pairc if i in e) for i in I}
nb = {i: [next(iter(e - {i})) for e in pairc if i in e] for i in I}
arr = tex[tex.index(r"\begin{array}"):tex.index(r"\end{array}")]
rows = re.findall(r"(\d+)&(\d)&(\d)&(\d)&(\d)", arr)
claim("parsed 13 rows of eq:complex-colors", len(rows) == 13)
claim("point degrees and n4/n5/n6 match eq:complex-colors", all(
    deg[int(i)] == int(d) and [sum(deg[k] == t for k in nb[int(i)]) for t in (4, 5, 6)] == [int(x), int(y), int(z)]
    for i, d, x, y, z in rows))

print("RESULT:", "holds" if ok else "fails", "(finite part: H and Proposition prop:complex). Host G: not-explicit.")
sys.exit(0 if ok else 1)
