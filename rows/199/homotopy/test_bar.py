"""Boundary, module-action and corrupt-formula tests for the explicit G."""
import unittest

from bar import Bar, Homotopy, add_tensors, ONE, monomial, IdentityFailure
from dependency.check import accumulate, mul


class BarTests(unittest.TestCase):
    def setUp(self):
        self.bar = Bar.load()

    def test_generator_counts(self):
        self.assertEqual([sum(1 for _ in self.bar.generators(n)) for n in range(5)],
                         [2, 18, 170, 1610, 15250])

    def test_bottom_degrees_are_unaugmented(self):
        for n in (0, 1):
            for tensor in self.bar.generators(n):
                self.assertEqual(self.bar.residual(tensor), {})
        self.assertEqual(self.bar.d({('e', 'u'): ONE}), {})

    def test_explicit_g1(self):
        self.assertEqual(self.bar.g({('e', 'u', 'f'): ONE}),
                         {('e', 'u'): monomial(1, 1)})

    def test_inverse_twist_on_terminal(self):
        # u N = (1+q)T, since t u=(1+q)n; H^-1 cancels z's H.
        self.assertEqual(self.bar.g({('e', 'u', 'N'): ONE}),
                         {('e', 'T'): monomial(1) ^ monomial(2)})

    def test_degree_two_direct_expansion(self):
        tensor = {('e', 'u', 'j', 'e'): ONE}
        self.assertEqual(self.bar.residual(tensor), {})
        self.assertNotEqual(self.bar.p(self.bar.b(tensor)), {})

    def test_differential_squared_low_degrees(self):
        for n in (2, 3):
            for tensor in self.bar.generators(n):
                self.assertEqual(self.bar.d(self.bar.d(tensor)), {})

    def test_g_bimodule_actions(self):
        self.assertEqual(self.bar.check_actions(2), 7600)

    def test_twist_mutation_fails(self):
        bad = Bar.load(Homotopy.OMIT_INVERSE_TWIST)
        with self.assertRaises(IdentityFailure):
            bad.verify(2)

    def test_z_coefficient_mutation_fails(self):
        bad = Bar.load(Homotopy.OMIT_H)
        with self.assertRaises(IdentityFailure):
            bad.verify(2)

    def test_z_support_mutation_fails(self):
        bad = Bar.load(Homotopy.DROP_U)
        with self.assertRaises(IdentityFailure):
            bad.verify(2)

    def test_zero_g1_mutation_fails(self):
        bad = Bar.load(Homotopy.ZERO_G1)
        with self.assertRaises(IdentityFailure):
            bad.verify(2)

    def test_sum_cancels(self):
        tensor = {('e', 'u', 'f'): ONE}
        self.assertEqual(add_tensors(tensor, tensor), {})

    def test_prefix_is_not_the_source_comparison(self):
        tensor = {('e', 'x', 'u', 'j', 'e'): ONE}
        prefix_value = {}
        for word, coefficient in self.bar.b(tensor).items():
            for value, factor in self.bar.cochain.get(word[1:4], {}).items():
                for left, product_factor in self.bar.alg.table.get((word[0], value), {}).items():
                    accumulate(prefix_value, (left,) + word[4:],
                               mul(coefficient, mul(factor, product_factor)))
        residual = add_tensors(prefix_value, self.bar.d(self.bar.g(tensor)),
                               self.bar.g(self.bar.d(tensor)))
        self.assertEqual(residual, {('e', 'x', 'z'): monomial(1, 1)})

    def test_b_endpoint_actions(self):
        for degree in range(3):
            for tensor in self.bar.generators(degree):
                for letter in self.bar.alg.basis:
                    self.assertEqual(self.bar.b(self.bar.left(letter, tensor)),
                                     self.bar.left(letter, self.bar.b(tensor)))
                    self.assertEqual(self.bar.b(self.bar.right(tensor, letter, twisted=True)),
                                     self.bar.right(self.bar.b(tensor), letter))

    def test_bad_g_right_action_has_nonzero_witness(self):
        bad = Bar.load(Homotopy.OMIT_INVERSE_TWIST)
        tensor = {('e', 'u', 'f'): ONE}
        residual = add_tensors(bad.g(bad.right(tensor, 'U', twisted=True)),
                               bad.right(bad.g(tensor), 'U'))
        self.assertEqual(residual, {('e', 'E'): monomial(1, 1) ^ monomial(1, 2)})
        with self.assertRaises(IdentityFailure):
            bad.check_actions(1)


if __name__ == '__main__':
    unittest.main()
