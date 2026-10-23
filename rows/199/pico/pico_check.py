"""Pico's check for PR #23 (Family 199 cocycle + homotopy packets).

1. Re-parses the cochain table in the vendored 09-cochain.tex directly from
   the TeX (not via data.json or review_oracle.py) and requires the set of
   (a, b, c, v, q-degree) entries to equal data.json's cochain exactly.
   Also checks the weight rule stated in the source: capitals in the input
   = capitals in the output + 1, for every entry.
2. Runs the packet's check.py on mutations outside the packet's own controls:
   (a) delete one entry (default zxJv, the last coefficient-1 entry),
   (b) add one spurious entry with the same endpoints and weight as an
       existing one but a new input triple,
       (the radical-input guard must not be what catches it),
   (c) shift one entry's q-degree by one (q^3 row -> q^2).
   Each must make check.py exit non-zero with a RESULT: FAIL line.
Standard library only. Run from the repo root: python3 rows/199/pico/pico_check.py
"""
import json, re, subprocess, sys, tempfile
from pathlib import Path

PKT = Path(__file__).resolve().parent.parent / 'cocycle'
tex = (PKT / 'sources' / '09-cochain.tex').read_text()
data = json.loads((PKT / 'data.json').read_text())

body = tex.split(r'\begin{tabular}', 1)[1].split(r'\end{tabular}', 1)[0]
DEG = {'$q^2$': 2, '$q$': 1, '$q^3$': 3, '$1$': 0}
tex_entries = set()
rows = 0
for line in body.splitlines():
    m = re.match(r'\s*(\$[^$]*\$)\s*&\s*\\texttt\{([^}]*)\}', line)
    if not m:
        continue
    rows += 1
    d = DEG[m.group(1)]
    for w in m.group(2).split():
        assert len(w) == 4, w
        tex_entries.add((w[0], w[1], w[2], w[3], d))
json_entries = {(*e['inputs'], e['output'], e['q_degree']) for e in data['cochain']}
ok = True
print(f'TeX table rows parsed: {rows}; entries: {len(tex_entries)}; data.json entries: {len(json_entries)}')
if len(tex_entries) != 179 or tex_entries != json_entries:
    ok = False
    print('MISMATCH tex-only:', sorted(tex_entries - json_entries)[:5], 'json-only:', sorted(json_entries - tex_entries)[:5])
triples = [e[:3] for e in tex_entries]
if len(set(triples)) != len(triples):
    ok = False; print('duplicate input triples')
caps = lambda s: sum(ch.isupper() for ch in s)
bad = [e for e in tex_entries if caps(''.join(e[:3])) != caps(e[3]) + 1]
print(f'weight rule violations: {len(bad)}')
ok &= not bad

def run(mut_data, label):
    with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False) as f:
        json.dump(mut_data, f)
    r = subprocess.run([sys.executable, str(PKT / 'check.py'), '--data', f.name], capture_output=True, text=True)
    last = [l for l in r.stdout.splitlines() if l.startswith('RESULT')]
    print(f'{label}: exit {r.returncode}; {last[-1] if last else "no RESULT line"}')
    return r.returncode, last

rc, _ = run(data, 'unmutated data.json')
ok &= rc == 0
# (a) delete
m = json.loads(json.dumps(data)); m['cochain'] = [e for e in m['cochain'] if (e['inputs'], e['output']) != (['z', 'x', 'J'], 'v')]
assert len(m['cochain']) == 178
rc, last = run(m, 'mutation a (delete zxJv)'); ok &= rc != 0 and bool(last) and 'FAIL' in last[-1]
# (b) add: take entry tyJf (q^3) and swap its middle letter for another basis
# letter with the same corners and case, giving an unused triple with valid
# endpoints and weight.
used = {tuple(e['inputs']) for e in data['cochain']}
B = {b['name']: (b['left'], b['right']) for b in data['basis']}
cands = [m2 for m2 in B if m2 != 'y' and m2 not in data['idempotents'] and m2.islower() and B.get(m2) == B.get('y') and ('t', m2, 'J') not in used]
assert cands, 'no same-corner letter for y'
cand = ('t', cands[0], 'J')
m = json.loads(json.dumps(data)); m['cochain'].append({'inputs': list(cand), 'output': 'f', 'q_degree': 3})
print('mutation b triple:', cand)
rc, last = run(m, f'mutation b (add {"".join(cand)} -> q^3 f)'); ok &= rc != 0 and bool(last) and 'FAIL' in last[-1]
# (c) degree shift on EyJT (q^3 -> q^2)
m = json.loads(json.dumps(data))
for e in m['cochain']:
    if e['inputs'] == ['E', 'y', 'J'] and e['output'] == 'T':
        assert e['q_degree'] == 3; e['q_degree'] = 2
rc, last = run(m, 'mutation c (EyJT q^3 -> q^2)'); ok &= rc != 0 and bool(last) and 'FAIL' in last[-1]

print('RESULT:', 'holds — TeX table = data.json (179/179), weight rule holds, 3 outside mutations rejected' if ok else 'FAIL')
sys.exit(0 if ok else 1)
