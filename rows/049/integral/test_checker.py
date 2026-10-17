"""End-to-end acceptance and failure controls for the integral certificate."""
from pathlib import Path
from dataclasses import replace
import subprocess
import sys
import unittest

if __package__:
    from . import checker
else:
    import checker

HERE = Path(__file__).resolve().parent


class IntegralCertificateTests(unittest.TestCase):
    def test_integral_certificate_cli(self):
        result = subprocess.run([sys.executable, str(HERE/'checker.py')],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout+result.stderr)
        self.assertIn('RESULT: certified integer polynomial identities', result.stdout)

    def test_integral_critical_section_and_complete_obligations(self):
        report = checker.verify()
        self.assertEqual(report['count'], 15)
        self.assertEqual((report['F_degree'], report['F_terms']), (17, 69))
        critical = report['obligations'][-1]
        self.assertEqual(critical['point'], [2, 1, -1, 1])
        self.assertEqual(critical['x_y_s_F'], [-1, 1, 1, -1])
        self.assertEqual(critical['gradient'], [0, 0, 0, 0])

    def test_corrupted_formulas_and_noncritical_point_are_rejected(self):
        for change, obligation in [({'cusp_leading': 3}, 'source cusp'),
                                    ({'bezout_tail': 5}, 'base Bezout'),
                                    ({'inverse_cross': 3}, 'lifting third'),
                                    ({'critical_point': (2, 1, -1, 0)}, 'critical section')]:
            with self.subTest(change=change):
                with self.assertRaisesRegex(ValueError, obligation):
                    checker.verify(replace(checker.Inputs(), **change))

    def test_finite_ring_controls_include_zero_divisors(self):
        reports = checker.finite_controls()
        self.assertEqual([(r['modulus'], r['zero_fibre_points']) for r in reports],
                         [(2, 8), (3, 27), (4, 64), (5, 125), (6, 216), (8, 512), (9, 729)])
        self.assertEqual(sum(r['ambient_points'] for r in reports), 12931)
        self.assertEqual(sum(r['parameter_points'] for r in reports), 1681)

    def test_characteristic_two_critical_section_is_off_zero_fibre(self):
        vals = checker.source_polynomials(0, 1, 1, 1, checker.Inputs())
        self.assertEqual(tuple(x % 2 for x in vals), (1, 1, 1, 1))

    def test_finite_controls_reject_corrupted_inverse(self):
        with self.assertRaisesRegex(ValueError, 'forward map'):
            checker.finite_controls((4,), replace(checker.Inputs(), inverse_cross=3))
        with self.assertRaisesRegex(ValueError, 'parameter round trip'):
            checker.finite_controls((4,), replace(checker.Inputs(), bezout_tail=5))

    def test_zero_ring_and_noninteger_modulus_are_rejected(self):
        for modulus in [1, 0, -1, True, 2.0]:
            with self.subTest(modulus=modulus):
                with self.assertRaises(ValueError):
                    checker.finite_controls((modulus,))

    def test_empty_finite_control_domain_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'nonempty'):
            checker.finite_controls(())

    def test_malformed_critical_point_is_rejected(self):
        for point in [(2, 1, -1), (2, 1, -1, 1.0), (2, True, -1, 1)]:
            with self.subTest(point=point):
                with self.assertRaisesRegex(ValueError, 'four integers'):
                    checker.verify(replace(checker.Inputs(), critical_point=point))

    def test_optimized_cli_rejects_every_mutation(self):
        for mutation in ['cusp', 'bezout', 'inverse', 'point']:
            with self.subTest(mutation=mutation):
                result = subprocess.run([sys.executable, '-O', str(HERE/'checker.py'),
                                         '--negative-control', mutation],
                                        capture_output=True, text=True)
                self.assertEqual(result.returncode, 1, result.stdout+result.stderr)
                self.assertIn('RESULT: not certified', result.stderr)

    def test_optimized_cli_with_finite_controls_passes(self):
        result = subprocess.run([sys.executable, '-O', str(HERE/'checker.py'), '--finite-controls'],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout+result.stderr)
        self.assertIn('"zero_fibre_points": 729', result.stdout)


if __name__ == '__main__':
    unittest.main()
