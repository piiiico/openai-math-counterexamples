import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from .check import (Parameters, multiplicity, prefix_moments, sphere_dimension,
                    select_degree, generate, replay, eigenvalue_numerator)


class PrefixTests(unittest.TestCase):
    def test_closed_multiplicities_and_exact_prefix_sums(self):
        p = Parameters()
        for l in (14, 15, 28, 39):
            count = charge = 0
            for groups in range(l // 2 + 2):
                with self.subTest(degree=l, groups=groups):
                    self.assertEqual(prefix_moments(p, l, groups), (count, charge))
                if groups <= l // 2:
                    mult = multiplicity(p, l, groups) * (1 if 2 * groups == l else 2)
                    count += mult
                    charge += mult * (l - 2 * groups)**2
            self.assertEqual(count, sphere_dimension(p, l))

    def test_even_middle_charge_is_counted_once(self):
        p = Parameters()
        before = prefix_moments(p, 28, 14)
        after = prefix_moments(p, 28, 15)
        self.assertEqual(after[0] - before[0], multiplicity(p, 28, 14))
        self.assertEqual(after[1], before[1])

    def test_first_partial_degree_has_a_strict_integer_margin(self):
        p = Parameters()
        row = select_degree(p, 50000)
        self.assertGreater(row["count"], 0)
        self.assertLess(row["count"], sphere_dimension(p, 50000))
        self.assertGreater(row["slack"], 0)

    def test_invalid_domains_are_rejected(self):
        p = Parameters()
        for call in (lambda: prefix_moments(p, 13, 1),
                     lambda: prefix_moments(p, 28, 16),
                     lambda: multiplicity(p, 28, -1)):
            with self.assertRaises(ValueError):
                call()


class CertificateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.certificate = json.loads(Path(__file__).with_name("certificate.json").read_text())

    def mutated(self):
        return copy.deepcopy(self.certificate)

    def test_generator_reproduces_certificate(self):
        self.assertEqual(generate(), self.certificate)

    def test_literal_replay_has_a_strict_surplus(self):
        result = replay(self.certificate)
        self.assertEqual((result["checked_degrees"], result["full_degrees"], result["partial_degrees"]), (249, 16, 233))
        self.assertEqual(result["surplus"], 5828555530537406099602318657887444326207065199324152854)
        self.assertEqual(result["minimum_strict_slack"], 21909800000)

    def test_missing_degree_rejected(self):
        data = self.mutated()
        data["degrees"].pop()
        with self.assertRaisesRegex(ValueError, "degree coverage"):
            replay(data)

    def test_including_degrees_zero_and_one_rejected(self):
        data = self.mutated()
        data["low_count"] += 17
        with self.assertRaisesRegex(ValueError, "low-degree count"):
            replay(data)

    def test_changed_parameters_rejected(self):
        data = self.mutated()
        data["parameters"]["alpha_num"] += 1
        with self.assertRaisesRegex(ValueError, "parameters mismatch"):
            replay(data)

    def test_invalid_cutoffs_rejected(self):
        for field in ("full_cutoff", "last_degree"):
            data = self.mutated()
            data[field] += 1
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "cutoff boundary"):
                replay(data)

    def test_double_counting_even_middle_rejected(self):
        data = self.mutated()
        row = data["degrees"][0]
        p = Parameters()
        self.assertEqual(row["degree"] % 2, 0)
        middle = multiplicity(p, row["degree"], row["degree"] // 2)
        row["count"] += middle
        row["weighted_num"] += middle * eigenvalue_numerator(p, row["degree"], row["degree"] // 2)
        row["slack"] = p.target * row["count"] - row["weighted_num"]
        with self.assertRaisesRegex(ValueError, "degree arithmetic mismatch"):
            replay(data)

    def test_next_vector_breaks_strict_partial_bound(self):
        data = self.mutated()
        row = next(row for row in data["degrees"] if row["degree"] == 49980)
        p = Parameters()
        numerator = eigenvalue_numerator(p, row["degree"], row["full_groups"])
        row["partial_take"] += 1
        row["count"] += 1
        row["weighted_num"] += numerator
        row["slack"] = p.target * row["count"] - row["weighted_num"]
        self.assertLessEqual(row["slack"], 0)
        with self.assertRaisesRegex(ValueError, "not strict"):
            replay(data)

    def test_optimized_python_still_rejects_bad_certificate(self):
        data = self.mutated()
        data["low_count"] += 17
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "bad.json"
            path.write_text(json.dumps(data))
            result = subprocess.run([sys.executable, "-O", str(Path(__file__).with_name("check.py")), "--certificate", str(path)], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("low-degree count", result.stderr)


if __name__ == "__main__":
    unittest.main()
