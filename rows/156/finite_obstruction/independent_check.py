#!/usr/bin/env python3
"""Independent finite-obstruction replay, using label and literal bitmasks.

Copyright (c) 2026 Alexander Richard Towell. MIT license.
Substantial OpenAI Codex assistance. Standard library only.
This module does not import the primary encoder, checker, or RUP engine.
"""
import argparse
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path


class RejectedProof(ValueError):
    pass


def build_cnf():
    """Generate the axioms with integer masks for label subsets.

    Variable numbering is lexicographic triples followed by quadruples.
    Clause order deliberately differs from encoding.py; literal/clause order
    has no effect on the proposition or reverse unit propagation.
    """
    labels = tuple(1 << i for i in range(10))
    universe = sum(labels)
    triples = tuple(sum(c) for c in combinations(labels, 3))
    tetrahedra = tuple(sum(c) for c in combinations(labels, 4))
    variable = {s: i + 1 for i, s in enumerate(triples + tetrahedra)}
    clauses = []
    for triangle in triples:
        extensions = tuple(triangle | bit for bit in labels if not triangle & bit)
        clauses.append((-variable[triangle], *(variable[s] for s in extensions)))
    for tetrahedron in tetrahedra:
        q = variable[tetrahedron]
        for triangle in triples:
            if triangle & tetrahedron != triangle:
                continue
            clauses.append((-q, variable[triangle]))
            others = tuple(variable[triangle | bit] for bit in labels
                           if not tetrahedron & bit)
            clauses.append((-q, *others))
        complement = universe ^ tetrahedron
        for triangle in triples:
            if triangle & complement != triangle:
                continue
            opposite = complement ^ triangle
            if triangle < opposite:
                a, b = variable[triangle], variable[opposite]
                clauses.extend(((-q, a, b), (-q, -a, -b)))
        remaining = tuple(bit for bit in labels if complement & bit)
        for a, b in combinations(remaining, 2):
            choices = tuple(variable[a | b | c] for c in remaining if c != a and c != b)
            # At least k: every n-k+1 variables include a true one.
            # At most k: no k+1 variables are all true. Here n=4, k=2.
            clauses.extend((-q, *subset) for subset in combinations(choices, len(choices) - 2 + 1))
            clauses.extend((-q, *(-v for v in subset)) for subset in combinations(choices, 2 + 1))
    clauses.append((variable[tetrahedra[0]],))
    return len(variable), clauses


def pack(clause, variables):
    """Represent positive and negative literals by two arbitrary-size integers."""
    if type(variables) is not int or variables < 0:
        raise RejectedProof('invalid variable domain')
    if not isinstance(clause, (list, tuple)):
        raise RejectedProof('clause is not a list or tuple')
    positive = negative = 0
    for literal in clause:
        if type(literal) is not int or not 1 <= abs(literal) <= variables:
            raise RejectedProof('literal outside variable domain')
        bit = 1 << (abs(literal) - 1)
        if (positive if literal > 0 else negative) & bit:
            raise RejectedProof('duplicate literal')
        if literal > 0:
            positive |= bit
        else:
            negative |= bit
    return positive, negative


def conflict(database, true_bits=0, false_bits=0):
    """Full-scan unit propagation: no watches, solver, cache, or mutable clauses."""
    if true_bits & false_bits:
        return True
    while True:
        changed = False
        for positive, negative in database:
            # Tautological clauses are true under every completion.
            if positive & negative or positive & true_bits or negative & false_bits:
                continue
            live_positive = positive & ~false_bits
            live_negative = negative & ~true_bits
            live = live_positive | live_negative
            if not live:
                return True
            if live & (live - 1) == 0:
                true_bits |= live_positive
                false_bits |= live_negative
                changed = True
        if not changed:
            return False


def verify(variables, original, proof):
    """Inductively verify additions, including an explicitly checked empty end."""
    if not isinstance(proof, list) or not proof or proof[-1] != []:
        raise RejectedProof('proof must end with an empty clause')
    database = [pack(clause, variables) for clause in original]
    for step, clause in enumerate(proof, 1):
        positive, negative = pack(clause, variables)
        if not clause and step != len(proof):
            raise RejectedProof('empty clause before proof end')
        # Falsify every literal in the proposed clause, then derive a conflict.
        if not conflict(database, true_bits=negative, false_bits=positive):
            raise RejectedProof(f'addition {step} is not RUP')
        database.append((positive, negative))
    return len(proof)


def canonical_digest(clauses):
    """Hash the clause multiset, independent of clause and literal ordering."""
    ordered = sorted(tuple(sorted(clause)) for clause in clauses)
    payload = json.dumps(ordered, separators=(',', ':')).encode()
    return sha256(payload).hexdigest()


def check(certificate_path=None, negative_control=None):
    path = Path(certificate_path) if certificate_path else Path(__file__).with_name('certificate.json')
    payload = path.read_bytes()
    certificate = json.loads(payload)
    keys = {'schema_version', 'variables', 'clauses', 'cnf_sha256', 'proof'}
    if not isinstance(certificate, dict) or set(certificate) != keys:
        raise RejectedProof('unsupported certificate fields')
    variables, clauses = build_cnf()
    if (type(certificate['schema_version']) is not int or certificate['schema_version'] != 1 or
            type(certificate['variables']) is not int or certificate['variables'] != variables or
            type(certificate['clauses']) is not int or certificate['clauses'] != len(clauses)):
        raise RejectedProof('certificate dimensions or schema mismatch')
    proof = certificate['proof']
    if negative_control == 'unsound-clause':
        # A satisfiable base with model x1=x2=True does not imply not-x1.
        verify(2, [(1, 2)], [[-1], []])
        raise RuntimeError('unsound-clause control unexpectedly accepted')
    if negative_control == 'false-clause':
        proof = [[]]
    elif negative_control == 'truncated':
        proof = proof[:-1]
    verified = verify(variables, clauses, proof)
    return {'variables': variables, 'independently_generated_clauses': len(clauses),
            'verified_rup_additions': verified, 'final_empty_clause': True,
            'canonical_cnf_sha256': canonical_digest(clauses),
            'certificate_sha256': sha256(payload).hexdigest(),
            'scope': 'finite TenSystem only; no geometry, topology, or Lean build'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--certificate', type=Path)
    parser.add_argument('--negative-control', choices=['unsound-clause', 'false-clause', 'truncated'])
    args = parser.parse_args()
    try:
        result = check(args.certificate, args.negative_control)
    except (RejectedProof, OSError, ValueError, KeyError, TypeError) as exc:
        print(f'FAIL: {exc}')
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
