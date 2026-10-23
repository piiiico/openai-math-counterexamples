"""Boundary, rejection and finite-field tests; standard-library unittest."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import unittest

if __package__:
    from . import check
else:
    import check

HERE = Path(__file__).resolve().parent
DATA = json.loads((HERE / 'algebra.json').read_text())


class ParameterTests(unittest.TestCase):
    def test_complete_declared_domain(self):
        report = check.run(DATA)
        self.assertEqual(report['case_count'], 30)
        self.assertEqual(report['degrees_per_complex'], 710)
        for size in (2, 4, 8, 16):
            cases = [c for c in report['cases'] if c['field_size'] == size]
            self.assertEqual([c['q_bits'] for c in cases], list(range(size)))
            self.assertTrue(all(c['maximum_degree'] == 2 * (size - 1) + 2 for c in cases))

    def test_invalid_domains(self):
        for modulus in (0, 1, 2, 4):
            with self.subTest(modulus=modulus), self.assertRaises(ValueError):
                check.BinaryField(modulus)
        f = check.BinaryField(3)
        with self.assertRaises(ValueError):
            f.pow(1, -1)
        with self.assertRaises(check.VerificationError):
            check.verify_case(DATA, f, 2, 8)
        with self.assertRaises(check.VerificationError):
            check.verify_case(DATA, f, 0, 1)

    def test_empty_and_zero_matrices(self):
        f = check.BinaryField(7)
        self.assertEqual(check.rank(f, []), 0)
        self.assertEqual(check.kernel(f, [(0, 0), (0, 0)]), [(1, 0), (0, 1)])
        with self.assertRaises(check.VerificationError):
            check.apply_matrix(f, [(0, 0)], (0, 0))

    def test_field_rejects_reducible_modulus(self):
        with self.assertRaises(ValueError):
            check.BinaryField(0b10101)

    def test_field_inverse_and_zero(self):
        f = check.BinaryField(0b10011)
        for a in range(1, f.size):
            self.assertEqual(f.mul(a, f.inv(a)), 1)
        with self.assertRaises(ZeroDivisionError):
            f.inv(0)
        self.assertEqual(f.pow(0, 0), 1)

    def test_zero_preserves_resolution_but_not_dual_profile(self):
        r = check.verify_case(DATA, check.BinaryField(0b11), 0, 8)
        self.assertEqual(r['chain_homology_dimensions'], [0] * 9)
        self.assertEqual(r['dual_cohomology_dimensions'], [0, 0] + [2] * 7)

    def test_one_fails_at_augmentation(self):
        r = check.verify_case(DATA, check.BinaryField(0b11), 1, 8)
        self.assertEqual(r['chain_homology_dimensions'], [1] + [2] * 8)

    def test_primitive_cube_root_first_failure_degree_two(self):
        r = check.verify_case(DATA, check.BinaryField(0b111), 2, 8)
        self.assertEqual(r['order'], 3)
        self.assertEqual(r['chain_homology_dimensions'], [0, 0, 1, 1, 0, 1, 1, 0, 1])

    def test_order_seven_first_failure_degree_six(self):
        r = check.verify_case(DATA, check.BinaryField(0b1011), 2, 15)
        self.assertEqual(r['order'], 7)
        self.assertEqual(next(i for i, h in enumerate(r['chain_homology_dimensions']) if h), 6)

    def test_mutated_product_breaks_polynomial_associativity(self):
        data = copy.deepcopy(DATA)
        next(p for p in data['products'] if p['inputs'] == ['t', 'y'])['output']['j'] = [1]
        with self.assertRaisesRegex(check.VerificationError, 'associativity'):
            check.verify_polynomial_algebra(data)

    def test_false_generic_profiles_rejected(self):
        for mode in ('root', 'zero-dual'):
            with self.subTest(mode=mode), self.assertRaises(check.VerificationError):
                check.run(DATA, mode)

    def test_cli_controls_exit_nonzero(self):
        for optimization in ([], ['-O']):
            for mode in ('product', 'root', 'zero-dual'):
                with self.subTest(optimization=optimization, mode=mode):
                    r = subprocess.run([sys.executable, *optimization, str(HERE / 'check.py'),
                                        '--negative-control', mode], capture_output=True, text=True)
                    self.assertNotEqual(r.returncode, 0)
                    self.assertIn('REJECT:', r.stderr)


if __name__ == '__main__':
    unittest.main()
