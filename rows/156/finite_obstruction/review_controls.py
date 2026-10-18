#!/usr/bin/env python3
"""Exhaustively cross-check two RUP propagation engines on two variables.

Copyright (c) 2026 Alexander Richard Towell. MIT license.
Substantial OpenAI Codex assistance. This is explicitly an implementation
cross-check; the standalone independent_check.py imports neither primary tool.
All failure checks remain active with python -O.
"""
import argparse
from itertools import combinations, product
import json

from independent_check import conflict, pack
from rup import Database


class FailedComparison(ValueError):
    pass


def check(negative_control=False):
    clauses = [tuple((i + 1) * sign for i, sign in enumerate(signs) if sign)
               for signs in product((-1, 0, 1), repeat=2)]
    assumptions = [subset for size in range(5)
                   for subset in combinations((-2, -1, 1, 2), size)]
    assignments = tuple(product((False, True), repeat=2))
    cases = reported_conflicts = 0
    for selected in range(1 << len(clauses)):
        base = [clause for i, clause in enumerate(clauses) if selected & (1 << i)]
        watched = Database(2, base)
        packed = [pack(clause, 2) for clause in base]
        for assumed in assumptions:
            true_bits, false_bits = pack(assumed, 2)
            scan_result = conflict(packed, true_bits, false_bits)
            if negative_control and cases == 0:
                scan_result = True  # Deliberate false conflict on the empty base.
            watch_result = watched.conflict(assumed)
            if scan_result != watch_result:
                raise FailedComparison(
                    f'checker disagreement: base={base!r}, assumptions={assumed!r}')
            if scan_result:
                reported_conflicts += 1
                for values in assignments:
                    assumptions_hold = all(values[abs(lit) - 1] == (lit > 0)
                                           for lit in assumed)
                    clauses_hold = all(any(values[abs(lit) - 1] == (lit > 0)
                                           for lit in clause) for clause in base)
                    if assumptions_hold and clauses_hold:
                        raise FailedComparison(
                            f'unsound conflict: base={base!r}, assumptions={assumed!r}, '
                            f'model={values!r}')
            cases += 1
    return {'variables': 2, 'available_nontautological_clauses': len(clauses),
            'formula_subsets': 1 << len(clauses), 'assumption_sets': len(assumptions),
            'compared_cases': cases,
            'reported_conflicts_checked_unsatisfiable': reported_conflicts,
            'persistent_watch_state': True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--negative-control', action='store_true',
                        help='force a false conflict; rejection and exit 1 are expected')
    args = parser.parse_args()
    try:
        result = check(args.negative_control)
    except ValueError as exc:
        print(f'FAIL: {exc}')
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
