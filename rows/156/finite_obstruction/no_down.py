#!/usr/bin/env python3
"""Certify the nonempty ten-label system after deleting only `down`.

Alexander Richard Towell; substantial OpenAI Codex assistance. MIT.
Pico's solver observation motivates this certificate. The original encoder
and watched-literal RUP checker are reused unchanged and credited in NO_DOWN.md.
"""
import argparse
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path

from encoding import build, satisfies
from rup import InvalidProof, verify


def build_cnf():
    encoding = build()
    clauses = encoding.clauses({"down", "nonempty"})
    clauses.append(tuple(encoding.tetrahedra.values()))
    return encoding.variables, clauses


def dimacs(variables, clauses):
    return f"p cnf {variables} {len(clauses)}\n" + "".join(
        " ".join(map(str, clause)) + " 0\n" for clause in clauses)


def canonical_digest(clauses):
    ordered = sorted(tuple(sorted(clause)) for clause in clauses)
    return sha256(json.dumps(ordered, separators=(",", ":")).encode()).hexdigest()


def semantic_violations(triangles, tetrahedra, omitted=frozenset()):
    """Evaluate the retained source axioms directly, without CNF or a solver.

    The first argument can contain nontriples: Lean's T is a predicate on all
    subsets. Complement and pair-count conditions still query only triples.
    """
    labels = frozenset(range(10))
    if any(not subset <= labels for subset in triangles | tetrahedra):
        raise ValueError("label outside the ten-label universe")
    failures = set()
    if not tetrahedra and "nonempty" not in omitted:
        failures.add("nonempty")
    if any(len(facet) != 4 for facet in tetrahedra):
        failures.add("tetra_card")
    if "pure" not in omitted and any(
            not any(triangle <= facet for facet in tetrahedra)
            for triangle in triangles):
        failures.add("pure")
    for facet in tetrahedra:
        if "no_boundary" not in omitted:
            for subset in combinations(sorted(facet), 3):
                triangle = frozenset(subset)
                if not any(triangle <= other and other != facet for other in tetrahedra):
                    failures.add("no_boundary")
        complement = labels - facet
        if "complementary" not in omitted:
            for subset in combinations(sorted(complement), 3):
                triangle = frozenset(subset)
                if (triangle in triangles) == ((complement - triangle) in triangles):
                    failures.add("complementary")
        if "pair_count" not in omitted:
            for subset in combinations(sorted(complement), 2):
                pair = frozenset(subset)
                if sum(pair | {label} in triangles for label in complement - pair) != 2:
                    failures.add("pair_count")
    return tuple(sorted(failures))


def verify_controls():
    controls = json.loads(Path(__file__).with_name("no_down_models.json").read_text())
    if set(controls) != {"nonempty", "pure"}:
        raise InvalidProof("unexpected weakened-model controls")
    encoding = build()
    for omitted, model in controls.items():
        triangles = {frozenset(subset) for subset in model["triangles"]}
        tetrahedra = {frozenset(subset) for subset in model["tetrahedra"]}
        if semantic_violations(triangles, tetrahedra, {omitted}):
            raise InvalidProof(f"invalid satisfying model without {omitted}")
        if omitted not in semantic_violations(triangles, tetrahedra):
            raise InvalidProof(f"control does not require omission of {omitted}")
        assignment = {**{v: subset in triangles for subset, v in encoding.triples.items()},
                      **{v: subset in tetrahedra for subset, v in encoding.tetrahedra.items()}}
        clauses = encoding.clauses({"down", "nonempty", omitted})
        if omitted != "nonempty":
            clauses.append(tuple(encoding.tetrahedra.values()))
        if not satisfies(clauses, assignment):
            raise InvalidProof(f"CNF disagrees with semantic {omitted} control")
    return {"satisfying_models": len(controls), "missing_axioms": sorted(controls)}


def check(certificate=None, negative_control=None):
    if certificate is None:
        certificate = json.loads(Path(__file__).with_name("no_down_certificate.json").read_text())
    keys = {"schema_version", "variables", "clauses", "cnf_sha256",
            "canonical_cnf_sha256", "proof"}
    if not isinstance(certificate, dict) or set(certificate) != keys:
        raise InvalidProof("unsupported no-down certificate fields")
    variables, clauses = build_cnf()
    expected = {"schema_version": 1, "variables": variables, "clauses": len(clauses)}
    if any(type(certificate[key]) is not int or certificate[key] != value
           for key, value in expected.items()):
        raise InvalidProof("certificate dimensions or schema mismatch")
    if (certificate["cnf_sha256"] != sha256(dimacs(variables, clauses).encode()).hexdigest()
            or certificate["canonical_cnf_sha256"] != canonical_digest(clauses)):
        raise InvalidProof("certificate/encoding hash mismatch")
    proof = certificate["proof"]
    if negative_control == "false-clause":
        proof = [[]]
    elif negative_control == "truncated":
        proof = proof[:-1]
    elif negative_control == "empty-family":
        clauses = clauses[:-1]
    elif negative_control is not None:
        raise InvalidProof("unsupported negative control")
    verified = verify(variables, clauses, proof)
    controls = verify_controls()
    return {"variables": variables, "clauses": len(clauses),
            "omitted_source_fields": ["down"],
            "nonempty": "unrestricted OR over all 210 tetrahedra",
            "symmetry_reduction": False,
            "verified_rup_additions": verified, "final_empty_clause": True,
            "canonical_cnf_sha256": canonical_digest(clauses),
            "controls": controls,
            "scope": "finite weakened TenSystem only; no topology or Lean verification"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--negative-control", choices=["false-clause", "truncated", "empty-family"])
    args = parser.parse_args()
    try:
        result = check(negative_control=args.negative_control)
    except (ValueError, OSError, KeyError, TypeError) as error:
        print(f"FAIL: {error}")
        return 1
    print(json.dumps(result, indent=2))
    print("RESULT: certified finite ten-label obstruction without down")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
