"""Behavioral checks: exact arithmetic, dual orientation, and corruption detection."""
import copy
from collections import Counter
import json
from pathlib import Path
import random
import subprocess
import sys
import unittest

import check as c

HERE = Path(__file__).resolve().parent


class ArithmeticTests(unittest.TestCase):
    def test_characteristic_two_cancellation(self):
        self.assertEqual(c.add(c.Q, c.Q), c.ZERO)

    def test_laurent_inverse_and_distributivity(self):
        self.assertEqual(c.mul(c.H, c.monomial(0, -1)), c.ONE)
        self.assertEqual(c.mul(c.Q, c.add(c.ONE, c.Q)),
                         frozenset({(1, 0), (2, 0)}))

    def test_mixed_product_cancels_cross_terms(self):
        p = c.add(c.Q, c.H)
        self.assertEqual(c.mul(p, p), frozenset({(2, 0), (0, 2)}))

    def test_seeded_products_against_integer_convolution(self):
        # A different arithmetic oracle: count integer multiplicities then reduce mod 2.
        rng = random.Random(19901)
        domain = [(q, h) for q in range(6) for h in range(-3, 4)]
        for _ in range(1000):
            a = frozenset(rng.sample(domain, rng.randrange(13)))
            b = frozenset(rng.sample(domain, rng.randrange(13)))
            counts = Counter((i + k, j + l) for i, j in a for k, l in b)
            want = frozenset(x for x, count in counts.items() if count % 2)
            self.assertEqual(c.mul(a, b), want)

    def test_vector_zero_terms_are_removed(self):
        self.assertEqual(c.sum_vectors({'x': c.Q}, {'x': c.Q}), {})
        self.assertEqual(c.scale({'x': c.ONE}, c.ZERO), {})


class InterfaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((HERE / 'data.json').read_text())
        cls.alg, cls.p, cls.support = c.load_data(cls.data)

    def test_dual_actions_have_correct_orientation(self):
        self.assertEqual(self.alg.table['x', 'J'], {'T': c.ONE})
        self.assertEqual(self.alg.table['y', 'J'], {'T': c.monomial(2)})
        self.assertEqual(self.alg.table.get(('J', 'x'), {}), {})

    def test_displayed_cycle_and_nonzero_evaluation(self):
        boundary, value = c.cycle(self.alg, self.p)
        self.assertEqual(boundary, {})
        self.assertEqual(value, {'f': c.monomial(3)})

    def test_trace_dual_corruption_rejected(self):
        alg = copy.deepcopy(self.alg)
        alg.dual['x'] = 'Y'
        with self.assertRaises(c.IdentityFailure) as failure:
            c.check_algebra(alg)
        self.assertEqual(failure.exception.stage, 'trace duality')

    def test_dual_product_corruption_rejected(self):
        alg = copy.deepcopy(self.alg)
        alg.table['x', 'J'] = {'T': c.Q}
        with self.assertRaises(c.IdentityFailure) as failure:
            c.check_algebra(alg)
        self.assertEqual(failure.exception.stage, 'associativity')

    def test_duplicate_cochain_input_rejected(self):
        bad = copy.deepcopy(self.data)
        bad['cochain'].append(bad['cochain'][0])
        with self.assertRaises(c.InvalidData):
            c.load_data(bad)

    def test_wrong_corner_rejected(self):
        bad = copy.deepcopy(self.data)
        bad['cochain'][0]['output'] = 'e'
        with self.assertRaises(c.InvalidData):
            c.load_data(bad)

    def test_negative_degree_rejected(self):
        bad = copy.deepcopy(self.data)
        bad['cochain'][0]['q_degree'] = -1
        with self.assertRaises(c.InvalidData):
            c.load_data(bad)

    def test_wrong_weight_rejected(self):
        bad = copy.deepcopy(self.data)
        # EuN has e,f endpoints; lower-case u has those endpoints but wrong weight.
        bad['cochain'][0]['output'] = 'u'
        with self.assertRaisesRegex(c.InvalidData, 'weight'):
            c.load_data(bad)

    def test_duplicate_product_rejected(self):
        bad = copy.deepcopy(self.data)
        bad['products'].append(bad['products'][0])
        with self.assertRaisesRegex(c.InvalidData, 'duplicate product'):
            c.load_data(bad)

    def test_invalid_coefficient_rejected(self):
        for exponents in ([-1], [0, 0], [True], []):
            bad = copy.deepcopy(self.data)
            bad['products'][0]['output']['z'] = exponents
            with self.assertRaisesRegex(c.InvalidData, 'polynomial'):
                c.load_data(bad)

    def test_full_domain(self):
        result = c.verify(self.alg, self.p, self.support)
        self.assertEqual(result['cocycle_quadruples'], 104976)
        self.assertEqual(result['composable_quadruples'], 15250)
        self.assertEqual(result['boundary_pairs'], 324)
        self.assertEqual(result['associativity_triples'], 8000)

    def test_changed_cochain_rejected_by_identity(self):
        p = copy.deepcopy(self.p)
        p['t', 'y', 'J'] = {'f': c.monomial(2)}
        with self.assertRaises(c.IdentityFailure):
            c.verify(self.alg, p, self.support)

    def test_missing_twist_rejected_by_boundary(self):
        with self.assertRaises(c.IdentityFailure):
            c.check_boundary(self.alg, self.p, self.support, twist=False)

    def test_zero_cochain_does_not_certify_full_interface(self):
        self.assertEqual(c.check_cocycle(self.alg, {}), (104976, 15250))
        self.assertEqual(c.cycle(self.alg, {})[1], {})
        with self.assertRaises(c.IdentityFailure):
            c.verify(self.alg, {}, self.support)

    def test_q_zero_does_not_preserve_nonvanishing(self):
        value = c.cycle(self.alg, self.p)[1]['f']
        at_zero = frozenset((q, h) for q, h in value if q == 0)
        self.assertEqual(at_zero, c.ZERO)

    def test_twist_mutation_is_invisible_at_H_one(self):
        try:
            c.check_boundary(self.alg, self.p, self.support, twist=False)
        except c.IdentityFailure as error:
            self.assertEqual(error.inputs, ('u', 'j'))
            self.assertEqual(error.residual, {'z': frozenset({(1, 0), (1, 1)})})
            at_one = {}
            for q, _h in error.residual['z']:
                at_one[q] = at_one.get(q, 0) + 1
            self.assertTrue(all(count % 2 == 0 for count in at_one.values()))
        else:
            self.fail('missing twist must be detected symbolically')

    def test_cli_negative_control_fails_with_optimization(self):
        run = subprocess.run([sys.executable, '-O', str(HERE / 'check.py'),
                              '--mutate', 'cochain'], text=True,
                             capture_output=True)
        self.assertEqual(run.returncode, 1, run.stderr)
        self.assertIn('RESULT: FAIL', run.stdout)


if __name__ == '__main__':
    unittest.main()
