#!/usr/bin/env python3
"""Optional generator; verification uses only the standard library.

Requires python-sat==1.8.dev24. Solver output is checked before writing.
"""

import json
from pathlib import Path
from pysat.solvers import Solver
from repair import Model, canonical_hash, replay

model = Model(1)
clauses, highest = model.cnf(3)
with Solver(name="g4", bootstrap_with=clauses, with_proof=True) as solver:
    if solver.solve():
        raise RuntimeError("budget3 satisfiable: proposed optimum4 disproved")
    raw = solver.get_proof()
proof = []
deletions = 0
for line in raw:
    tokens = line.split()
    if tokens[0] == "d":
        deletions += 1
        continue
    values = [int(x) for x in tokens]
    if not values or values[-1] != 0:
        raise ValueError("malformed solver proof")
    proof.append(tuple(values[:-1]))
replay(clauses, proof)
clauses4, _ = model.cnf(4)
with Solver(name="g4", bootstrap_with=clauses4) as solver:
    if not solver.solve():
        raise RuntimeError("budget4 unexpectedly unsatisfiable")
witness = model.dummy_leaf_repair()
if model.cost(witness) != 4 or model.violations(witness):
    raise RuntimeError("explicit repair failed")
certificate = {
    "depth": 1,
    "excluded_budget": 3,
    "cnf_sha256": canonical_hash(clauses),
    "repaired_bits": list(witness),
    "rup_additions": proof,
    "generator": {
        "python_sat": "1.8.dev24",
        "solver": "Glucose4",
        "ignored_deletions": deletions,
    },
    "source_commit": "1581d4cbdd69a0faf34b2089614fe2a814316a6a",
}
Path(__file__).with_name("certificate.json").write_text(
    json.dumps(certificate, indent=2) + "\n"
)
print(
    "Generated and independently RUP-checked",
    len(proof),
    "additions;",
    highest,
    "variables;",
    len(clauses),
    "clauses",
)
