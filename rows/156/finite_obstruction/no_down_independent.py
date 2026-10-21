#!/usr/bin/env python3
"""Separate bitmask CNF and full-scan replay for the down-omission claim.

Alexander Richard Towell; substantial OpenAI Codex assistance. MIT.
Adapted from the prior independently written bitmask encoder. Its full-scan
propagation engine is imported unchanged; no primary encoder/checker is used.
"""
import argparse
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import time

from independent_check import RejectedProof, canonical_digest, verify


def build_cnf():
    labels = tuple(1 << i for i in range(10))
    universe = sum(labels)
    triples = tuple(sum(subset) for subset in combinations(labels, 3))
    facets = tuple(sum(subset) for subset in combinations(labels, 4))
    variable = {subset: i + 1 for i, subset in enumerate(triples + facets)}
    clauses = []
    for triangle in triples:
        clauses.append((-variable[triangle],
                        *(variable[triangle | bit] for bit in labels if not triangle & bit)))
    for facet in facets:
        q = variable[facet]
        for triangle in triples:
            if triangle & facet == triangle:
                # The no-boundary premise is Q(facet), regardless of T(triangle).
                clauses.append((-q, *(variable[triangle | bit] for bit in labels if not facet & bit)))
        complement = universe ^ facet
        for triangle in triples:
            if triangle & complement == triangle:
                opposite = complement ^ triangle
                if triangle < opposite:
                    a, b = variable[triangle], variable[opposite]
                    clauses.extend(((-q, a, b), (-q, -a, -b)))
        remaining = tuple(bit for bit in labels if complement & bit)
        for a, b in combinations(remaining, 2):
            choices = tuple(variable[a | b | c] for c in remaining if c != a and c != b)
            clauses.extend((-q, *subset) for subset in combinations(choices, 3))
            clauses.extend((-q, *(-v for v in subset)) for subset in combinations(choices, 3))
    clauses.append(tuple(variable[facet] for facet in facets))
    return len(variable), clauses


def check(negative_control=None):
    payload = Path(__file__).with_name("no_down_certificate.json").read_bytes()
    certificate = json.loads(payload)
    variables, clauses = build_cnf()
    expected_keys = {"schema_version", "variables", "clauses", "cnf_sha256",
                     "canonical_cnf_sha256", "proof"}
    if not isinstance(certificate, dict) or set(certificate) != expected_keys:
        raise RejectedProof("unsupported no-down certificate fields")
    for key, value in {"schema_version": 1, "variables": variables, "clauses": len(clauses)}.items():
        if type(certificate[key]) is not int or certificate[key] != value:
            raise RejectedProof("certificate dimensions or schema mismatch")
    if certificate["canonical_cnf_sha256"] != canonical_digest(clauses):
        raise RejectedProof("independent clause multiset mismatch")
    proof = certificate["proof"]
    if negative_control == "false-clause":
        proof = [[]]
    elif negative_control == "truncated":
        proof = proof[:-1]
    elif negative_control == "empty-family":
        clauses = clauses[:-1]
    elif negative_control is not None:
        raise RejectedProof("unsupported negative control")
    additions = verify(variables, clauses, proof)
    return {"variables": variables, "independently_generated_clauses": len(clauses),
            "verified_rup_additions": additions, "final_empty_clause": True,
            "canonical_cnf_sha256": canonical_digest(clauses),
            "certificate_sha256": sha256(payload).hexdigest(),
            "scope": "no down; no symmetry reduction; finite claim only"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--negative-control", choices=["false-clause", "truncated", "empty-family"])
    args = parser.parse_args()
    started = time.monotonic()
    try:
        result = check(args.negative_control)
    except (ValueError, OSError, KeyError, TypeError) as error:
        print(f"FAIL: {error}")
        return 1
    print(json.dumps(result, indent=2))
    print(f"Independent full-scan replay completed in {time.monotonic() - started:.3f} seconds.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
