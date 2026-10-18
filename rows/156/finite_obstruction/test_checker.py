"""Behavioral and failure controls for the finite Family 156 certificate."""
import json
from pathlib import Path
import subprocess
import sys
import unittest

HERE = Path(__file__).resolve().parent


class EntryTests(unittest.TestCase):
    def test_six_system_domain_and_properties(self):
        result = subprocess.run([sys.executable, str(HERE / 'checker.py'), '--finite-controls'],
                                text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('"six_systems": 12', result.stdout)

    def test_complete_refutation(self):
        result = subprocess.run([sys.executable, str(HERE / 'checker.py')],
                                text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('RESULT: certified finite ten-label obstruction', result.stdout)

    def test_corrupted_certificate_rejected(self):
        result = subprocess.run([sys.executable, '-O', str(HERE / 'checker.py'),
                                 '--negative-control', 'false-clause'],
                                text=True, capture_output=True)
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn('FAIL:', result.stdout)

    def test_remaining_rejecting_controls(self):
        for name in ('truncated', 'empty-family', 'simplex-boundary', 'six-system'):
            with self.subTest(name=name):
                result = subprocess.run([sys.executable, '-O', str(HERE / 'checker.py'),
                                         '--negative-control', name],
                                        text=True, capture_output=True)
                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertIn('FAIL:', result.stdout)


class RupTests(unittest.TestCase):
    def test_complete_toy_refutation(self):
        from rup import verify
        clauses = [[1, 2], [-1, 2], [1, -2], [-1, -2]]
        self.assertEqual(verify(2, clauses, [[2], []]), 2)

    def test_reject_incomplete_or_unsound_proof(self):
        from rup import InvalidProof, verify
        for proof in ([], [[1]], [[]], [[-1], []], [[], []]):
            with self.subTest(proof=proof), self.assertRaises(InvalidProof):
                verify(2, [[1, 2]], proof)

    def test_reject_invalid_literals(self):
        from rup import InvalidProof, verify
        for literal in (0, 3, -3, True, '1'):
            with self.subTest(literal=literal), self.assertRaises(InvalidProof):
                verify(2, [[1]], [[literal], []])
        with self.assertRaises(InvalidProof):
            verify(2, [[1]], [[1, 1], []])
        with self.assertRaises(InvalidProof):
            verify(2, [[1]], ['1', []])

    def test_empty_and_inconsistent_base(self):
        from rup import verify
        self.assertEqual(verify(0, [[]], [[]]), 1)
        self.assertEqual(verify(1, [[1], [-1]], [[]]), 1)

    def test_watch_movement_across_queries(self):
        from rup import Database
        from itertools import product
        clauses = [[1, 2, 3], [-1, 4], [-2, -4], [-3, 4], [2, 3, -4]]
        database = Database(4, clauses)
        for choices in product((0, -1, 1), repeat=4):
            assumptions = [i * sign for i, sign in enumerate(choices, 1) if sign]
            # A conflict must rule out every literal truth assignment.
            if database.conflict(assumptions):
                for truth in product((False, True), repeat=4):
                    evaluate = lambda lit: truth[abs(lit) - 1] == (lit > 0)
                    self.assertFalse(all(map(evaluate, assumptions)) and
                                     all(any(map(evaluate, c)) for c in clauses))

    def test_satisfiable_weakened_models(self):
        from encoding import assignment_for_facets, build, satisfies
        from itertools import combinations
        encoding = build()
        empty = assignment_for_facets(encoding, [])
        boundary = assignment_for_facets(encoding, combinations(range(5), 4))
        self.assertTrue(satisfies(encoding.clauses({'nonempty'}), empty))
        self.assertFalse(satisfies(encoding.clauses(), empty))
        self.assertTrue(satisfies(encoding.clauses({'complementary', 'pair_count'}), boundary))
        self.assertFalse(satisfies(encoding.clauses(), boundary))


import independent_check as independent
import encoding
import pathlib
from collections import Counter


class IndependentTests(unittest.TestCase):
    def test_clause_multiset_is_identical(self):
        n, clauses = independent.build_cnf()
        primary = encoding.build()
        self.assertEqual(n, primary.variables)
        self.assertEqual(Counter(map(frozenset, clauses)), Counter(map(frozenset, primary.clauses())))

    def test_packing_and_domain_rejections(self):
        self.assertEqual(independent.pack((1, -3, 4), 4), (9, 4))
        for clause in ([0], [True], [1, 1], [5], [-5], '1'):
            with self.subTest(clause=clause), self.assertRaises(independent.RejectedProof):
                independent.pack(clause, 4)

    def test_conflict_and_satisfiable_controls(self):
        cases = [([], 0, 0, False), ([[]], 0, 0, True), ([[1, -1]], 0, 0, False),
                 ([[1]], 0, 1, True), ([[-1]], 1, 0, True),
                 ([[1], [-1, 2], [-2, 3], [-3]], 0, 0, True),
                 ([[1, 2], [-1, 2]], 0, 0, False), ([], 1, 1, True)]
        for clauses, true, false, expected in cases:
            with self.subTest(clauses=clauses, true=true, false=false):
                database = [independent.pack(c, 3) for c in clauses]
                self.assertEqual(independent.conflict(database, true, false), expected)

    def test_refutation_and_unsound_clause(self):
        base = [[1, 2], [1, -2], [-1, 2], [-1, -2]]
        self.assertEqual(independent.verify(2, base, [[1], []]), 2)
        for original, proof in [([[1, 2]], [[-1], []]), (base, [[]]),
                                (base, [[1]]), (base, [[], []])]:
            with self.subTest(original=original, proof=proof), self.assertRaises(independent.RejectedProof):
                independent.verify(2, original, proof)

    def test_actual_certificate(self):
        n, clauses = independent.build_cnf()
        certificate = json.loads(pathlib.Path(encoding.__file__).with_name('certificate.json').read_text())
        self.assertEqual(independent.verify(n, clauses, certificate['proof']), 327)

if __name__ == '__main__':
    unittest.main()
