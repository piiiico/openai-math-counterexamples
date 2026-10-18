#!/usr/bin/env python3
"""Optional certificate generation; verification never imports python-sat."""
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import time
from importlib.metadata import version

from pysat.solvers import Glucose4
from encoding import build, dimacs


def main():
    here = Path(__file__).resolve().parent
    encoding = build()
    text = dimacs(encoding)
    started = time.monotonic()
    with Glucose4(bootstrap_with=encoding.clauses(), with_proof=True) as solver:
        satisfiable = solver.solve()
        if satisfiable:
            raise RuntimeError('SAT: save and inspect the model before claiming an obstruction')
        raw = solver.get_proof()
        stats = solver.accum_stats()
    proof = []
    deletions = 0
    for line in raw:
        fields = line.split()
        if fields[0] == 'd':
            deletions += 1
            continue
        values = [int(x) for x in fields]
        if not values or values[-1] != 0 or 0 in values[:-1]:
            raise ValueError('invalid DRUP line')
        proof.append(values[:-1])
    if not proof or proof[-1] != []:
        proof.append([])  # Replay must independently establish this final contradiction.
    result = {'schema_version': 1, 'variables': encoding.variables,
              'clauses': len(encoding.constraints), 'cnf_sha256': sha256(text.encode()).hexdigest(),
              'proof': proof}
    (here / 'certificate.json').write_text(json.dumps(result, separators=(',', ':')) + '\n')
    receipt = {'solver': 'Glucose4', 'python_sat': version('python-sat'),
               'seconds': time.monotonic() - started, 'stats': stats,
               'proof_additions': len(proof), 'ignored_deletions': deletions,
               'constraint_counts': dict(Counter(c.family for c in encoding.constraints))}
    (here / 'generation.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
