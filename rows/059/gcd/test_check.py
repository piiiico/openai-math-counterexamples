"""Independent small-rational oracle and finite-witness failure controls."""
from copy import deepcopy
from contextlib import redirect_stderr, redirect_stdout
from fractions import Fraction
from itertools import combinations
import json
import io
from math import gcd
from pathlib import Path
import random
import tempfile
import unittest

import check

HERE = Path(__file__).resolve().parent


def products(terms):
    values = [Fraction(1), Fraction(1)]
    for base, powers in terms:
        for k, exponent in enumerate(powers):
            values[k] *= Fraction(base) ** exponent
    return tuple(values)


def refresh_metadata(data):
    exponents = [int(row['e']) for row in data['relation']]
    data.update(sum_e=sum(exponents), sum_abs_e=sum(map(abs, exponents)),
                support_size=len(exponents),
                max_abs_e_digits=max(len(str(abs(e))) for e in exponents))
    return data


class CancellationTests(unittest.TestCase):
    def test_huge_exponents_cancel_without_expanding(self):
        k = 10**140 + 593
        terms = [(12, (k, 0)), (18, (k, 0)), (6, (-k, 0)), (36, (-k, 0))]
        self.assertEqual(check.cancel(terms).residual, {})

    def test_overlapping_powers_and_two_products(self):
        terms = [(8, (2, 1)), (4, (-3, 0)), (2, (0, -3))]
        self.assertEqual(check.cancel(terms).residual, {})

    def test_coprime_nonidentity_survives(self):
        result = check.cancel([(5, (1, 0)), (7, (-1, 2))])
        self.assertEqual(products(result.residual.items()), (Fraction(5, 7), Fraction(49)))
        self.assertTrue(result.residual)

    def test_units_zero_weights_and_duplicate_bases(self):
        terms = [(1, (9, -7)), (6, (0, 0)), (11, (5, 3)), (11, (-5, -3))]
        self.assertEqual(check.cancel(terms).residual, {})
        self.assertEqual(check.cancel([]).residual, {})

    def test_small_rational_oracle(self):
        rng = random.Random(5901)
        for _ in range(150):
            terms = [(rng.randint(1, 80), (rng.randint(-4, 4), rng.randint(-4, 4)))
                     for _ in range(rng.randint(0, 15))]
            result = check.cancel(terms)
            self.assertEqual(products(terms), products(result.residual.items()))
            self.assertEqual(not result.residual, products(terms) == (1, 1))
            self.assertTrue(all(gcd(a, b) == 1 for a, b in combinations(result.residual, 2)))

    def test_bad_terms_reject(self):
        for term in [(0, (1, 0)), (-2, (1, 0)), (True, (1, 0)),
                     (1.5, (1, 0)), (2, (1.5, 0)), (2, (True, 0)),
                     (2, (1,)), (2, (1, 2, 3))]:
            with self.subTest(term=term), self.assertRaises(check.InvalidCertificate):
                check.cancel([term])

    def test_malformed_term_structure_rejects(self):
        for term in [None, 3, (2,), (2, (1, 0), 3)]:
            with self.subTest(term=term), self.assertRaises(check.InvalidCertificate):
                check.cancel([term])


class RelationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((HERE / 'source/explicit-relation.json').read_text())

    def test_complete_witness(self):
        result = check.verify_relation(self.data)
        self.assertEqual(result.support_size, 849)
        self.assertEqual(result.sum_e, self.data['sum_e'])
        self.assertGreater(result.sum_e, 0)
        self.assertEqual(result.reduction.residual, {})

    def test_coefficient_mutation_with_consistent_metadata_rejects(self):
        data = deepcopy(self.data)
        data['relation'][0]['e'] = str(int(data['relation'][0]['e']) + 1)
        refresh_metadata(data)
        with self.assertRaisesRegex(check.InvalidCertificate, 'product'):
            check.verify_relation(data)

    def test_wrong_ratio_rejects(self):
        with self.assertRaisesRegex(check.InvalidCertificate, 'product'):
            check.verify_relation(self.data, wrong_ratio=True)

    def test_reverse_relation_passes_products_but_fails_positive_sum(self):
        data = deepcopy(self.data)
        for row in data['relation']:
            row['e'] = str(-int(row['e']))
        refresh_metadata(data)
        witness = check.parse_relation(data)
        self.assertEqual(check.cancel(check.product_terms(witness)).residual, {})
        with self.assertRaisesRegex(check.InvalidCertificate, 'positive'):
            check.verify_relation(data)

    def test_integer_exponents_and_row_order_preserve_witness(self):
        data = deepcopy(self.data)
        data['relation'].reverse()
        for row in data['relation']:
            row['e'] = int(row['e'])
        self.assertEqual(check.parse_relation(data), check.parse_relation(self.data))

    def test_wrong_dimension_rejects(self):
        for bad in [self.data['d'] + 1, float(self.data['d']), True]:
            data = deepcopy(self.data); data['d'] = bad
            with self.subTest(d=bad), self.assertRaisesRegex(check.InvalidCertificate, 'dimension'):
                check.parse_relation(data)

    def test_invalid_and_duplicate_indices_reject(self):
        for b in [0, -1, 3, 88574, 177147, True, 1.5, '1', self.data['relation'][1]['b']]:
            data = deepcopy(self.data); data['relation'][0]['b'] = b
            with self.subTest(b=b), self.assertRaises(check.InvalidCertificate):
                check.parse_relation(data)

    def test_noninteger_and_zero_exponents_reject(self):
        for e in [0, True, 1.5, '0', '1.5', ' 1', '+1', None, '', '01']:
            data = deepcopy(self.data); data['relation'][0]['e'] = e
            with self.subTest(e=e), self.assertRaises(check.InvalidCertificate):
                check.parse_relation(data)

    def test_all_exact_metadata_fields_are_checked(self):
        for key in ['sum_e', 'sum_abs_e', 'support_size', 'max_abs_e_digits']:
            for bad in [self.data[key] + 1, float(self.data[key]), True]:
                data = deepcopy(self.data); data[key] = bad
                with self.subTest(key=key, bad=bad), self.assertRaises(check.InvalidCertificate):
                    check.parse_relation(data)

    def test_malformed_schema_rejects(self):
        for value in [None, [], {}, dict(self.data, relation=[]),
                      dict(self.data, relation='invalid'),
                      dict(self.data, relation=[{'b': 1}]),
                      dict(self.data, relation=[[]])]:
            with self.subTest(value=type(value)), self.assertRaises(check.InvalidCertificate):
                check.parse_relation(value)

    def test_source_integrity(self):
        check.verify_sources(HERE)

    def test_wrong_source_hash_rejects(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'source').mkdir()
            for p in (HERE / 'source').iterdir():
                if p.is_file(): (root / 'source' / p.name).write_bytes(p.read_bytes())
            (root / 'source-pins.json').write_bytes((HERE / 'source-pins.json').read_bytes())
            source = root / 'source/explicit-relation.json'
            source.write_bytes(source.read_bytes() + b' ')
            with self.assertRaisesRegex(check.InvalidCertificate, 'hash'):
                check.verify_sources(root)


class CommandTests(unittest.TestCase):
    def test_real_command_accepts(self):
        out = io.StringIO()
        with redirect_stdout(out):
            status = check.main([])
        self.assertEqual(status, 0)
        self.assertIn('residual bases = 0', out.getvalue())
        self.assertIn('RESULT: holds', out.getvalue())

    def test_each_negative_control_fails_for_its_declared_reason(self):
        reasons = {'coefficient': 'product', 'wrong-ratio': 'product',
                   'reverse-sign': 'positive', 'invalid-index': 'index', 'wrong-d': 'dimension'}
        self.assertEqual(set(reasons), set(check.CONTROLS))
        for name, reason in reasons.items():
            err = io.StringIO()
            with self.subTest(control=name), redirect_stderr(err):
                status = check.main(['--negative-control', name])
                self.assertEqual(status, 1)
                self.assertIn('RESULT: fails', err.getvalue())
                self.assertIn(reason, err.getvalue())

    def test_unknown_control_rejects(self):
        with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
            check.main(['--negative-control', 'unknown'])
        self.assertEqual(error.exception.code, 2)


if __name__ == '__main__':
    unittest.main()
