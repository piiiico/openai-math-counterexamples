#!/usr/bin/env python3
"""Optional regeneration; use requirements-generation.txt and a 300s timeout.

The standard-library checkers do not import this module or trust the solver.
Regeneration overwrites only the new no_down certificate/models/receipt.
"""
from collections import Counter
from hashlib import sha256
from importlib.metadata import version
import json
from pathlib import Path
import platform
import time

from pysat.solvers import Glucose4
from encoding import build
from no_down import build_cnf, canonical_digest, dimacs


def main():
    here = Path(__file__).resolve().parent
    variables, clauses = build_cnf()
    started = time.monotonic()
    with Glucose4(bootstrap_with=clauses, with_proof=True) as solver:
        if solver.solve():
            raise RuntimeError("SAT: inspect the model; do not claim an obstruction")
        raw = solver.get_proof()
        stats = solver.accum_stats()
    proof = []
    deletions = 0
    for line in raw:
        fields = line.split()
        if fields[0] == "d":
            deletions += 1
            continue
        values = [int(value) for value in fields]
        if not values or values[-1] != 0 or 0 in values[:-1]:
            raise ValueError("invalid DRUP clause")
        proof.append(values[:-1])
    if not proof or proof[-1] != []:
        proof.append([])  # Both replayers must actually prove this final step.
    certificate = {"schema_version": 1, "variables": variables, "clauses": len(clauses),
                   "cnf_sha256": sha256(dimacs(variables, clauses).encode()).hexdigest(),
                   "proof": proof, "canonical_cnf_sha256": canonical_digest(clauses)}
    (here / "no_down_certificate.json").write_text(json.dumps(certificate, separators=(",", ":")) + "\n")

    encoding = build()
    weaker = encoding.clauses({"down", "pure", "nonempty"}) + [tuple(encoding.tetrahedra.values())]
    with Glucose4(bootstrap_with=weaker) as solver:
        if not solver.solve():
            raise RuntimeError("expected an independently checkable pure-omission model")
        assignment = {abs(literal): literal > 0 for literal in solver.get_model()}
    model = {"triangles": [sorted(subset) for subset, v in encoding.triples.items() if assignment[v]],
             "tetrahedra": [sorted(subset) for subset, v in encoding.tetrahedra.items() if assignment[v]]}
    controls = {"nonempty": {"triangles": [], "tetrahedra": []}, "pure": model}
    (here / "no_down_models.json").write_text(json.dumps(controls, indent=2) + "\n")
    receipt = {
        "python": platform.python_version(), "python_sat": version("python-sat"), "solver": "Glucose4",
        "elapsed_seconds": time.monotonic() - started, "stats": stats,
        "additions": len(proof), "ignored_deletions": deletions,
        "variables": variables, "clauses": len(clauses),
        "original_constraint_counts": dict(Counter(c.family for c in encoding.constraints)),
        "omitted": ["down"], "symmetry_reduction": False,
        "nonempty_encoding": "OR of all 210 tetrahedron variables",
        "seed": None, "heuristics": "pinned solver defaults; certificate replay does not trust them",
        "stopping_rule": "one finite-domain solve, externally capped at 300 seconds; then complete certificate replay",
        "model_control": {"omitted_additional_field": "pure", "triples": len(model["triangles"]),
                          "tetrahedra": len(model["tetrahedra"])}
    }
    (here / "no_down_generation.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
