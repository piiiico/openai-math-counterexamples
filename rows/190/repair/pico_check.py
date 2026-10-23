#!/usr/bin/env python3
"""Pico check for PR #16, run from rows/190: python3 repair/pico_check.py
Uses Pico's own check.py build (not repair.py): enumerates the 48 ordered bodies of the h=1 non-anchor
block by role sets, checks the PR witness kills all 8 live bodies with 4 edits, and that none of the
43,745 edit sets of size <= 3 does. Assumes the PR's written density argument (body constraints <=> H-free
for anchor-fixed repairs); that step is not computed here."""
import sys, json, itertools, io, contextlib
src = open('check.py').read().split('for h in range(1, 6):')[0]  # defs only, skip sections 4-6 loops
g = {}
with contextlib.redirect_stdout(io.StringIO()):
    exec(compile(src, 'check.py', 'exec'), g)
B = g['build'](1); rows, cols, E = B['rows'], B['cols'], B['entry']
ridx = [k for k,l in enumerate(rows) if l[0] != 'A']; cidx = [k for k,l in enumerate(cols) if l[0] != 'A']
print('non-anchor rows/cols', len(ridx), len(cidx))
orig = {(r,c): E(rows[r], cols[c]) for r in ridx for c in cidx}
# all ordered candidate bodies by role sets, irrespective of entries
cand = set()
for t,(rr,cc) in enumerate(B['roles']):
    R1=[k for k in ridx if B['inset'](rows[k],rr[0],True)]; R2=[k for k in ridx if B['inset'](rows[k],rr[1],True)]
    C1=[k for k in cidx if B['inset'](cols[k],cc[0],False)]; C2=[k for k in cidx if B['inset'](cols[k],cc[1],False)]
    for r1 in R1:
        for r2 in R2:
            if r2<=r1: continue
            for c1 in C1:
                for c2 in C2:
                    if c2>c1: cand.add((r1,r2,c1,c2))
print('ordered candidate bodies', len(cand))
def alive(bits):
    return [b for b in cand if bits[(b[0],b[2])]==1 and bits[(b[1],b[2])]==1 and bits[(b[0],b[3])]==0 and bits[(b[1],b[3])]==1]
print('bodies in original', len(alive(orig)))
cells = sorted(orig)
w = json.load(open('repair/certificate.json'))['repaired_bits']
wit = {cells[i]: int(v) for i,v in enumerate(w)}
print('witness edits', sum(wit[c]!=orig[c] for c in cells), 'bodies after', len(alive(wit)))
best = None; n=0
for k in range(4):
    for S in itertools.combinations(cells, k):
        n+=1; bits = dict(orig)
        for c in S: bits[c] ^= 1
        if not alive(bits): best = S; break
    if best is not None: break
print('subsets of size<=3 tried', n, 'repair found', best)
