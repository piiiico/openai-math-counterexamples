"""Controls for the all-parameter Family 342 checker."""
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch
import contextlib
import io

import check


class ExactAlgebraTests(unittest.TestCase):
    def test_polynomial_ring(self):
        f, k, z = check.variables()
        self.assertEqual((f + k) ** 2, f*f + 2*f*k + k*k)
        self.assertEqual((f - k)*(f + k), f*f - k*k)
        self.assertNotEqual(f, k)
        self.assertEqual(1-f, check.Poly.constant(1)-f)
        self.assertEqual((f + 1).at((2, 3, 4)), 3)
        self.assertEqual(z ** 0, check.Poly.constant(1))

    def test_wedge_orientation(self):
        self.assertEqual(check.wedge_basis((0, 1), (2, 3)), ((0, 1, 2, 3), 1))
        self.assertEqual(check.wedge_basis((0, 2), (1, 3)), ((0, 1, 2, 3), -1))
        self.assertIsNone(check.wedge_basis((0, 1), (1, 2)))

    def test_all_identities(self):
        obligations = check.verify()
        expected = {
            'basis_self_dual', 'N_self_dual', 'N_square', 'N_norm',
            'eta_self_dual_part', 'eta_anti_self_dual_part',
            'eta_invariant', 'eta_metric_symmetric', 'eta_metric_square',
            'eta_characteristic_polynomial', 'eta_closed_separated_support',
            'taming_plus', 'taming_minus', 'invariant_projection_plus',
            'invariant_projection_minus', 'anti_invariant_perp_V',
            'anti_invariant_perp_W', 'zero_mixed_pairing',
            'positive_self_pairings', 'three_point_span',
        }
        self.assertEqual(set(obligations), expected)
        self.assertTrue(all(obligations.values()), obligations)

    def test_wrong_eta_coefficient(self):
        obligations = check.verify(eta_factor=1)
        self.assertFalse(obligations['eta_invariant'])
        self.assertFalse(obligations['eta_metric_square'])

    def test_wrong_derivative_support(self):
        self.assertTrue(check.closure_check(swapped=False))
        self.assertFalse(check.closure_check(swapped=True))

    def test_amplitude_boundary(self):
        from fractions import Fraction as Q
        self.assertEqual(check.taming_margin(Q(1, 4)), Q(3, 4))
        self.assertEqual(check.taming_margin(Q(1)), 0)
        self.assertLess(check.taming_margin(Q(5, 4)), 0)

    def test_cli(self):
        p = subprocess.run([sys.executable, str(Path(check.__file__))], capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, p.stderr + p.stdout)
        self.assertIn('RESULT: exact all-parameter identities verified', p.stdout)

    def test_rejects_cli_controls(self):
        for control in ['eta-factor', 'derivative-support', 'taming-amplitude']:
            with self.subTest(control=control):
                p = subprocess.run([sys.executable, '-O', str(Path(check.__file__)), '--negative-control', control], capture_output=True, text=True)
                self.assertNotEqual(p.returncode, 0)
                self.assertIn('RESULT: rejected', p.stdout)


class AdditionalAlgebraTests(unittest.TestCase):
    def test_main_in_process(self):
        for control in [None, 'eta-factor', 'derivative-support', 'taming-amplitude']:
            argv = ['check.py'] + (['--negative-control', control] if control else [])
            with patch.object(sys, 'argv', argv), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(check.main(), int(control is not None))

    def test_derivative(self):
        f, k, z = check.variables()
        self.assertEqual((f*f*k + 3*z).derivative(0), 2*f*k)
        self.assertEqual((f*f*k + 3*z).derivative(1), f*f)
        self.assertEqual((f*f*k + 3*z).derivative(2), check.Poly.constant(3))

    def test_invalid_inputs(self):
        f, _, _ = check.variables()
        with self.assertRaises(TypeError):
            f + 0.5
        with self.assertRaises(ValueError):
            f ** -1
        with self.assertRaises(ValueError):
            check.taming_margin(-1)

    def test_determinant_against_fraction_elimination(self):
        import random
        from fractions import Fraction as Q
        rng = random.Random(342)
        for n in range(1, 5):
            for _ in range(5):
                a = [[rng.randrange(-3, 4) for _ in range(n)] for _ in range(n)]
                b = [[Q(x) for x in row] for row in a]
                expected = Q(1)
                for col in range(n):
                    pivot = next((i for i in range(col, n) if b[i][col]), None)
                    if pivot is None:
                        expected = Q(0)
                        break
                    if pivot != col:
                        b[col], b[pivot] = b[pivot], b[col]
                        expected = -expected
                    p = b[col][col]
                    expected *= p
                    for i in range(col+1, n):
                        ratio = b[i][col]/p
                        b[i] = [x-ratio*y for x, y in zip(b[i], b[col])]
                actual = check.determinant(tuple(tuple(check.Poly.constant(x) for x in row) for row in a))
                self.assertEqual(actual, check.Poly.constant(expected))

    def test_star_on_basis(self):
        for p, q, sign in [((0,1),(2,3),1), ((0,2),(1,3),-1),
                           ((0,3),(1,2),1), ((1,2),(0,3),1),
                           ((1,3),(0,2),-1), ((2,3),(0,1),1)]:
            self.assertEqual(check.star(check.form({p: 1})), check.form({q: sign}))

    def test_star_and_wedge(self):
        f, k, _, u, v, w, n, eta = check.definitions()
        self.assertEqual(check.star(check.star(eta)), eta)
        for a in (u, v, w, eta):
            for b in (u, v, w, eta):
                self.assertEqual(check.wedge(check.coefficients(a), check.coefficients(b)),
                                 check.wedge(check.coefficients(b), check.coefficients(a)))

    def test_missing_generator_detected(self):
        f, k, _, u, v, w, n, eta = check.definitions()
        damaged = check.add(u, check.scale(f, v))
        r2 = 1+f*f+k*k
        self.assertNotEqual(check.multiply(damaged, damaged), check.scale(-r2, check.identity(4)))


if __name__ == '__main__':
    unittest.main()
