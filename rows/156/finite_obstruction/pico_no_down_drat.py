#!/usr/bin/env python3
# Pico's check of the K002 / PR #11 certificate, sharing no code with the packet's encoders or checkers.
# 1. Builds the CNF for TenSystem minus `down` from the five Lean fields (Labels.lean:13-22), written
#    from rows/156/pico_sat_crosscheck.py (direct exactly-2-of-4 clauses, no cardinality library),
#    in the packet's variable numbering (triples 1..120, tetrahedra 121..330, itertools order).
# 2. Compares its canonical clause digest with no_down_certificate.json (a faithfulness check by a third encoder).
# 3. Checks the certificate with drat-trim (Marijn Heule, github.com/marijnheule/drat-trim), forward mode.
# 4. Controls: proof cut to its first 9,000 lines, proof with lines 2..9,000 removed, a bare empty clause,
#    and the CNF without `pure` must all fail; the packet's no-pure model must satisfy the CNF without `pure`.
# Usage: python3 pico_no_down_drat.py /path/to/drat-trim     Pico (AI agent), MIT.
import itertools, json, hashlib, subprocess, sys, tempfile, os
here = os.path.dirname(os.path.abspath(__file__)); D = sys.argv[1]
L = range(10); tri = list(itertools.combinations(L, 3)); tet = list(itertools.combinations(L, 4))
T = {frozenset(u): i + 1 for i, u in enumerate(tri)}; Q = {frozenset(s): 121 + i for i, s in enumerate(tet)}
fam = {k: set() for k in ('nonempty', 'no_boundary', 'complementary', 'pair_count', 'pure')}
add = lambda f, c: fam[f].add(tuple(sorted(c)))
add('nonempty', Q.values())
for s in map(frozenset, tet):
    comp = frozenset(L) - s
    for u in map(frozenset, itertools.combinations(s, 3)):
        add('no_boundary', [-Q[s]] + [Q[u | {x}] for x in L if x not in s])
    for u in map(frozenset, itertools.combinations(sorted(comp), 3)):
        v = comp - u; add('complementary', [-Q[s], T[u], T[v]]); add('complementary', [-Q[s], -T[u], -T[v]])
    for p in map(frozenset, itertools.combinations(sorted(comp), 2)):
        for three in itertools.combinations([T[p | {w}] for w in comp - p], 3):
            add('pair_count', [-Q[s], *three]); add('pair_count', [-Q[s], *(-x for x in three)])
for u in map(frozenset, tri):
    add('pure', [-T[u]] + [Q[u | {x}] for x in L if x not in u])
def cnf(skip=()):
    return sorted(c for f, cs in fam.items() if f not in skip for c in cs)
full = cnf(); cert = json.load(open(os.path.join(here, 'no_down_certificate.json')))
digest = hashlib.sha256(json.dumps(full, separators=(",", ":")).encode()).hexdigest()
print('pico clauses', len(full), 'canonical sha256', digest)
ok = digest == cert['canonical_cnf_sha256']; print('matches certificate canonical_cnf_sha256:', ok)
tmp = tempfile.mkdtemp()
def write(name, lines): p = os.path.join(tmp, name); open(p, 'w').write(''.join(lines)); return p
dim = lambda cs: [f"p cnf 330 {len(cs)}\n"] + [" ".join(map(str, c)) + " 0\n" for c in cs]
proof = [" ".join(map(str, c)) + " 0\n" for c in cert['proof']]
def drat(cnf_p, proof_p):
    out = subprocess.run([D, cnf_p, proof_p, '-f'], capture_output=True, text=True).stdout
    return 'VERIFIED' if '\ns VERIFIED' in '\n' + out else 'NOT VERIFIED'
F = write('f.cnf', dim(full))
res = drat(F, write('p.drat', proof)); print('drat-trim forward, full proof:', res); ok &= res == 'VERIFIED'
for name, cnf_p, pr in [('truncated to 9000 lines', F, proof[:9000]), ('lines 2..9000 removed', F, proof[:1] + proof[9000:]),
                        ('bare empty clause', F, ["0\n"]), ('CNF without pure', write('np.cnf', dim(cnf(('pure',)))), proof)]:
    r = drat(cnf_p, write('c.drat', pr)); print('control', name + ':', r); ok &= r == 'NOT VERIFIED'
m = json.load(open(os.path.join(here, 'no_down_models.json')))['pure']
true = {T[frozenset(t)] for t in m['triangles'] if len(t) == 3} | {Q[frozenset(s)] for s in m['tetrahedra']}
sat = all(any((l > 0) == (abs(l) in true) for l in c) for c in cnf(('pure',)))
viol = sum(not any((l > 0) == (abs(l) in true) for l in c) for c in fam['pure'])
print('packet no-pure model satisfies CNF without pure:', sat, '| violates pure clauses:', viol); ok &= sat and viol > 0
print('RESULT:', 'PASS' if ok else 'FAIL'); sys.exit(0 if ok else 1)
