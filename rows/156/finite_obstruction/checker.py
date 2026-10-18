#!/usr/bin/env python3
"""Independently replay Family 156's finite obstruction; not its topology."""
import argparse
from collections import Counter
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path

from encoding import assignment_for_facets, build, dimacs, satisfies
from finite_controls import six_system_controls
from rup import InvalidProof, verify


def check(negative_control=None, finite_controls=False):
    encoding = build()
    certificate = json.loads(Path(__file__).with_name('certificate.json').read_text())
    expected_keys = {'schema_version', 'variables', 'clauses', 'cnf_sha256', 'proof'}
    if set(certificate) != expected_keys or certificate['schema_version'] != 1:
        raise InvalidProof('unsupported certificate schema')
    if (certificate['variables'] != encoding.variables or
            certificate['clauses'] != len(encoding.constraints) or
            certificate['cnf_sha256'] != sha256(dimacs(encoding).encode()).hexdigest()):
        raise InvalidProof('certificate/encoding pin mismatch')
    proof = certificate['proof']
    clauses = encoding.clauses()
    if negative_control == 'false-clause':
        proof = [[]]
    elif negative_control == 'truncated':
        proof = proof[:-1]
    elif negative_control == 'empty-family':
        clauses = encoding.clauses({'nonempty'})
        # Every learned clause is checked again; this satisfiable base cannot refute.
    elif negative_control == 'simplex-boundary':
        clauses = encoding.clauses({'complementary', 'pair_count'})
    if negative_control == 'six-system':
        six_system_controls(corrupt=True)
    verified = verify(encoding.variables, clauses, proof)
    empty = assignment_for_facets(encoding, [])
    boundary = assignment_for_facets(encoding, combinations(range(5), 4))
    if not satisfies(encoding.clauses({'nonempty'}), empty):
        raise InvalidProof('empty-family control')
    if satisfies(encoding.clauses(), empty):
        raise InvalidProof('nonempty guard ineffective')
    if not satisfies(encoding.clauses({'complementary', 'pair_count'}), boundary):
        raise InvalidProof('simplex-boundary control')
    if satisfies(encoding.clauses(), boundary):
        raise InvalidProof('local-system guard ineffective')
    result = {'variables': encoding.variables, 'clauses': len(clauses),
            'constraint_counts': dict(Counter(c.family for c in encoding.constraints)),
            'verified_rup_additions': verified, 'final_empty_clause': True,
            'weakened_axiom_models_checked': 2,
            'scope': 'finite TenSystem only; geometric and topological bridge not checked'}
    if finite_controls:
        result['finite_controls'] = six_system_controls()
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--finite-controls', action='store_true')
    parser.add_argument('--negative-control', choices=['false-clause', 'truncated',
                                                     'empty-family', 'simplex-boundary', 'six-system'])
    args = parser.parse_args()
    try:
        result = check(args.negative_control, args.finite_controls)
    except (InvalidProof, OSError, ValueError, KeyError, TypeError) as exc:
        print(f'FAIL: {exc}')
        return 1
    print(json.dumps(result, indent=2))
    print('RESULT: certified finite ten-label obstruction')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
