"""Tests of arithmetic enclosures, complete parameters and fail-closed certification."""

from fractions import Fraction
import json
from pathlib import Path
import subprocess
import sys
import unittest

if __package__:
    from . import checker as certificate_checker
else:
    import checker as certificate_checker

HERE = Path(__file__).resolve().parent


class CertificateTests(unittest.TestCase):
    def test_standard_certificate_cli(self):
        run = subprocess.run([sys.executable, str(HERE / 'checker.py')],
                             capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertIn('RESULT: certified', run.stdout)

    def checker(self):
        return certificate_checker

    def certificate(self):
        return json.loads((HERE / 'certificate.json').read_text())

    def test_exponential_zero_and_known_rational_enclosure(self):
        check = self.checker()
        self.assertEqual(check.exp_bounds(Fraction(0), 8), (1, 1))
        lo, hi = check.exp_bounds(Fraction(1), 32)
        self.assertGreater(lo, Fraction(2718281828, 10**9))
        self.assertLess(hi, Fraction(2718281829, 10**9))

    def test_exponential_tail_direction_and_refinement(self):
        check = self.checker()
        lo, hi = check.exp_bounds(Fraction(32), 64)
        lo2, hi2 = check.exp_bounds(Fraction(32), 128)
        self.assertLess(lo, lo2)
        self.assertLess(hi2, hi)
        self.assertLess(lo2, hi2)

    def test_complete_certificate_and_derived_dimension(self):
        report = self.checker().verify(self.certificate())
        self.assertEqual(report['input_count'], 16777218)
        self.assertEqual(report['product_mass_binary_exponent'], 1426063445)
        self.assertGreater(Fraction(report['gain_ratio_lower_enclosure']), Fraction(1, 50))

    def test_coarser_grid_is_not_certified(self):
        cert = self.certificate()
        cert['leaf_count'] = 2**23 + 1
        with self.assertRaisesRegex(ValueError, 'gain'):
            self.checker().verify(cert)

    def test_false_strengthened_margin_is_rejected(self):
        cert = self.certificate()
        cert['gain_ratio_lower'] = {'numerator': 1, 'denominator': 5}
        p = self.checker().Parameters.from_document(cert)
        bias = p.leaf_count * (p.cutoff+p.shift+p.radius) * p.radius**2
        # J_delta >= 0 in the exact identity, so even the optimistic ceiling
        # c^2+2cD rules out this demand, independently of the integral bound.
        self.assertLess(p.shift**2 + 2*p.shift*bias, Fraction(1, 5))
        with self.assertRaisesRegex(ValueError, 'gain'):
            self.checker().verify(cert)

    def test_false_interval_mass_is_rejected(self):
        cert = self.certificate()
        cert['interval_mass_binary_exponent'] = 20
        with self.assertRaisesRegex(ValueError, 'interval'):
            self.checker().verify(cert)

    def test_insufficient_taylor_order_is_rejected(self):
        cert = self.certificate()
        cert['exp_terms'] = 1
        with self.assertRaisesRegex(ValueError, 'Taylor'):
            self.checker().verify(cert)

    def test_invalid_geometry_is_rejected(self):
        for key, value in [('leaf_count', 4), ('cutoff', {'numerator': 0, 'denominator': 1}),
                           ('radius', {'numerator': -1, 'denominator': 2}),
                           ('shift', {'numerator': 0, 'denominator': 1})]:
            with self.subTest(key=key):
                cert = self.certificate()
                cert[key] = value
                with self.assertRaises(ValueError):
                    self.checker().verify(cert)

    def test_missing_and_unrecognized_parameters_are_rejected(self):
        cert = self.certificate()
        del cert['radius']
        with self.assertRaises(ValueError):
            self.checker().verify(cert)

    def test_malformed_parameter_types_and_schema_are_rejected(self):
        for key, value in [('schema_version', 2), ('leaf_count', True),
                           ('radius', {'numerator': 1, 'denominator': 0}),
                           ('shift', {'numerator': True, 'denominator': 8}),
                           ('exp_terms', -1), ('interval_mass_binary_exponent', -1)]:
            with self.subTest(key=key, value=value):
                cert = self.certificate()
                cert[key] = value
                with self.assertRaises(ValueError):
                    self.checker().verify(cert)

    def test_geometric_and_density_ratio_conditions_are_enforced(self):
        for radius, message in [(8, 'geometry'), (1, 'geometry'),
                                (Fraction(1, 5), 'density-ratio')]:
            with self.subTest(radius=radius):
                cert = self.certificate()
                radius = Fraction(radius)
                cert['radius'] = {'numerator': radius.numerator,
                                  'denominator': radius.denominator}
                with self.assertRaisesRegex(ValueError, message):
                    self.checker().verify(cert)
        cert = self.certificate()
        cert['unchecked_extra'] = True
        with self.assertRaises(ValueError):
            self.checker().verify(cert)

    def test_cli_failure_and_optimized_python(self):
        for args, expected in [(['--negative-control', 'coarse-grid'], 1),
                               (['--negative-control', 'strong-margin'], 1),
                               ([], 0)]:
            with self.subTest(args=args):
                run = subprocess.run([sys.executable, '-O', str(HERE / 'checker.py'), *args],
                                     capture_output=True, text=True)
                self.assertEqual(run.returncode, expected, run.stdout + run.stderr)

    def test_outward_decimal_rounding(self):
        check = self.checker()
        for q in [Fraction(1, 3), Fraction(-1, 3), Fraction(1, 10**15)]:
            lo = Fraction(check.decimal_bound(q, 12, upper=False))
            hi = Fraction(check.decimal_bound(q, 12, upper=True))
            self.assertLessEqual(lo, q)
            self.assertGreaterEqual(hi, q)
            self.assertLessEqual(hi-lo, Fraction(1, 10**12))


if __name__ == '__main__':
    unittest.main()
