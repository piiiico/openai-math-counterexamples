"""Controls for the weakened statement; original packet tests remain unchanged."""
import copy
from collections import Counter
import importlib
import importlib.util
from itertools import combinations, product
import json
from pathlib import Path
import subprocess
import sys
import unittest


class NoDownTests(unittest.TestCase):
    def module(self, name="no_down"):
        self.assertIsNotNone(importlib.util.find_spec(name), "weakened-system checker required")
        return importlib.import_module(name)

    def test_unrestricted_nonempty_and_exact_omission(self):
        variables, clauses = self.module().build_cnf()
        self.assertEqual(variables, 330)
        self.assertEqual(len(clauses), 30361)
        self.assertFalse(any(len(c) <= 2 for c in clauses))
        self.assertIn(tuple(range(121, 331)), clauses)

    def test_distinct_encodings_agree(self):
        left = self.module().build_cnf()
        right = self.module("no_down_independent").build_cnf()
        self.assertEqual(left[0], right[0])
        self.assertEqual(sorted(tuple(sorted(c)) for c in left[1]),
                         sorted(tuple(sorted(c)) for c in right[1]))

    def test_no_boundary_applies_even_when_triangle_is_not_in_T(self):
        module = self.module()
        failures = module.semantic_violations(set(), {frozenset(range(4))})
        self.assertIn("no_boundary", failures)

    def test_tetra_card_and_pure_are_not_lost(self):
        module = self.module()
        self.assertIn("tetra_card", module.semantic_violations(set(), {frozenset(range(3))}))
        self.assertIn("pure", module.semantic_violations({frozenset(range(3))}, set()))

    def test_saved_satisfiable_controls(self):
        result = self.module().verify_controls()
        self.assertEqual(result["satisfying_models"], 2)
        self.assertEqual(set(result["missing_axioms"]), {"nonempty", "pure"})

    def test_control_with_nontriple_T_respects_source_family_domain(self):
        module = self.module()
        # T is an arbitrary subset-family in Lean. Empty Q and T={empty}
        # satisfies every retained condition when nonempty and pure are removed.
        failures = module.semantic_violations({frozenset()}, set(), {"pure", "nonempty"})
        self.assertEqual(failures, ())

    def test_complete_primary_refutation(self):
        result = self.module().check()
        self.assertTrue(result["final_empty_clause"])
        self.assertEqual(result["clauses"], 30361)
        self.assertEqual(result["verified_rup_additions"], 18302)

    def test_certificate_schema_and_pins_are_checked(self):
        module = self.module()
        certificate = json.loads(Path(__file__).with_name("no_down_certificate.json").read_text())
        for mutation in ("schema_version", "variables", "clauses", "cnf_sha256", "canonical_cnf_sha256"):
            altered = copy.deepcopy(certificate)
            altered[mutation] = False
            with self.subTest(field=mutation), self.assertRaises(ValueError):
                module.check(certificate=altered)
        with self.assertRaises(ValueError):
            module.check(certificate={})

    def test_invalid_label_is_rejected(self):
        with self.assertRaises(ValueError):
            self.module().semantic_violations({frozenset({10})}, set())

    def test_independent_checker_rejects_invalid_proofs(self):
        module = self.module("no_down_independent")
        for mode in ("false-clause", "truncated"):
            with self.subTest(mode=mode), self.assertRaises(ValueError):
                module.check(negative_control=mode)

    def test_corrupt_and_truncated_proofs_are_rejected(self):
        module = self.module()
        for mode in ("false-clause", "truncated", "empty-family"):
            with self.subTest(mode=mode), self.assertRaises(ValueError):
                module.check(negative_control=mode)

    def test_optimized_cli_failure_is_nonzero(self):
        script = Path(__file__).with_name("no_down.py")
        self.module()
        result = subprocess.run(
            [sys.executable, "-O", "-B", str(script), "--negative-control", "false-clause"],
            capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 1)
        self.assertIn("FAIL:", result.stdout)

    def test_local_clause_truth_tables(self):
        # Preserved from the separate AI review. The predicates state the
        # mathematics; the CNF side is evaluated independently of propagation.
        from encoding import satisfies
        cases = 0
        templates = [
            (8, [(-1, 2, 3, 4, 5, 6, 7, 8)], lambda x: not x[0] or any(x[1:])),
            (7, [(-1, 2, 3, 4, 5, 6, 7)], lambda x: not x[0] or any(x[1:])),
            (3, [(-1, 2, 3), (-1, -2, -3)], lambda x: not x[0] or x[1] != x[2]),
            (5, [(-1, *s) for s in combinations(range(2, 6), 3)]
             + [(-1, *(-v for v in s)) for s in combinations(range(2, 6), 3)],
             lambda x: not x[0] or sum(x[1:]) == 2),
        ]
        for size, clauses, predicate in templates:
            for values in product((False, True), repeat=size):
                self.assertEqual(satisfies(clauses, dict(enumerate(values, 1))), predicate(values))
                cases += 1
        self.assertEqual(cases, 424)

    def test_source_driven_cnf_reconstruction(self):
        # Additional semantic audit, not a third independent implementation:
        # reuse only the predecessor's variable-to-subset mapping.
        from encoding import build
        mapping = build()
        triples, facets = mapping.triples, mapping.tetrahedra
        universe = frozenset(range(10))
        expected = []
        for face, variable in triples.items():
            extensions = [q for facet, q in facets.items() if face <= facet]
            expected.append((-variable, *extensions))
        for facet, q in facets.items():
            for face in map(frozenset, combinations(facet, 3)):
                others = [r for other, r in facets.items() if other != facet and face <= other]
                expected.append((-q, *others))
            complement = universe - facet
            for face in map(frozenset, combinations(complement, 3)):
                opposite = complement - face
                if tuple(sorted(face)) < tuple(sorted(opposite)):
                    a, b = triples[face], triples[opposite]
                    expected.extend([(-q, a, b), (-q, -a, -b)])
            for pair in map(frozenset, combinations(complement, 2)):
                choices = [triples[pair | {w}] for w in complement - pair]
                for subset in combinations(choices, 3):
                    expected.extend([(-q, *subset), (-q, *(-v for v in subset))])
        expected.append(tuple(facets.values()))
        for module in (self.module(), self.module("no_down_independent")):
            variables, clauses = module.build_cnf()
            self.assertEqual(variables, 330)
            self.assertEqual(Counter(tuple(sorted(c)) for c in clauses),
                             Counter(tuple(sorted(c)) for c in expected))


if __name__ == "__main__":
    unittest.main()
