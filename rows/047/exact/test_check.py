"""Unit and integration tests for check.py (standard library unittest)."""
import contextlib
import io
import random
import subprocess
import sys
import unittest
from pathlib import Path

import check
from check import Poly, p, s, u, F, J, M, L, w, E

HERE = Path(__file__).resolve().parent


def evaluate(poly, point):
    total = 0
    for e, c in poly.terms.items():
        term = c
        for name, k in zip(check.VARS, e):
            term *= point[name] ** k
        total += term
    return total


def random_poly(rng, names, n_terms=6, max_deg=3):
    poly = Poly()
    for _ in range(n_terms):
        mono = Poly.const(rng.randint(-5, 5))
        for name in names:
            mono = mono * Poly.var(name) ** rng.randint(0, max_deg)
        poly = poly + mono
    return poly


class PolyArithmetic(unittest.TestCase):
    """The proof is the expansion; these seeded evaluations test the implementation."""

    def setUp(self):
        self.rng = random.Random(47)

    def point(self):
        return {name: self.rng.randint(-9, 9) for name in check.VARS}

    def test_ring_operations_agree_with_evaluation(self):
        for _ in range(25):
            a = random_poly(self.rng, ("p", "s", "u", "w"))
            b = random_poly(self.rng, ("s", "F", "L"))
            pt = self.point()
            self.assertEqual(evaluate(a + b, pt), evaluate(a, pt) + evaluate(b, pt))
            self.assertEqual(evaluate(a - b, pt), evaluate(a, pt) - evaluate(b, pt))
            self.assertEqual(evaluate(a * b, pt), evaluate(a, pt) * evaluate(b, pt))
            self.assertEqual(evaluate(a**3, pt), evaluate(a, pt) ** 3)

    def test_substitution_is_simultaneous(self):
        swapped = (s + 2 * u**2).subst({"s": u, "u": s})
        self.assertTrue(swapped == u + 2 * s**2)
        for _ in range(15):
            a = random_poly(self.rng, ("p", "s", "u"))
            vs, vu = random_poly(self.rng, ("s", "w"), 3, 2), random_poly(self.rng, ("u", "p"), 3, 2)
            pt = self.point()
            inner = dict(pt, s=evaluate(vs, pt), u=evaluate(vu, pt))
            self.assertEqual(evaluate(a.subst({"s": vs, "u": vu}), pt), evaluate(a, inner))

    def test_derivative_and_coefficients(self):
        f = 3 * s**2 * u - 5 * u**4 + w
        self.assertTrue(f.diff("u") == 3 * s**2 - 20 * u**3)
        self.assertTrue(f.coeff("u", 4) == -5)
        self.assertEqual(f.degree("u"), 4)
        self.assertEqual(Poly().degree("u"), -1)
        self.assertTrue(f.uses_only(("s", "u", "w")))
        self.assertFalse(f.uses_only(("s", "u")))

    def test_exact_divisions_reject_non_multiples(self):
        self.assertTrue((p**3 * s + p**4).divide_by_var_power("p", 3) == s + p)
        self.assertIsNone((p**3 * s + p**2).divide_by_var_power("p", 3))
        self.assertTrue((6 * s + 4 * u).divide_integer(2) == 3 * s + 2 * u)
        self.assertIsNone((6 * s + 3 * u).divide_integer(2))

    def test_equality_and_canonical_hash(self):
        a = s * u + 1
        self.assertTrue(a == 1 + u * s)
        self.assertFalse(a == s * u)
        order = ("s", "u")
        self.assertEqual(a.canonical_sha256(order), (1 + u * s).canonical_sha256(order))
        self.assertNotEqual(a.canonical_sha256(order), (s * u + 2).canonical_sha256(order))
        with self.assertRaises(ValueError):
            (a + w).canonical_sha256(order)


class CertificateSteps(unittest.TestCase):

    def test_exponential_is_translation_in_u(self):
        # Delta = -d/du with Delta s = 0 gives exp(w Delta) u = u - w.
        delta = {"u": Poly.const(-1), "w": Poly()}
        self.assertTrue(check.exponential(delta, 1, u**2) == (u - w) ** 2)

    def test_exponential_rejects_non_nilpotent(self):
        # Delta s = s never reaches zero.
        self.assertIsNone(check.exponential({"s": s}, 1, s, limit=10))

    def test_exponential_rejects_non_integral_division(self):
        # Delta u = s, Delta s = 1: Delta^2(u) = 1, and 1/2! is not an integer.
        self.assertIsNone(check.exponential({"u": s, "s": Poly.const(1)}, 1, u, limit=10))

    def test_exponential_rejects_when_limit_is_exhausted(self):
        # Delta u = -1 kills u^3 only after four steps.
        self.assertIsNone(check.exponential({"u": Poly.const(-1)}, 1, u**3, limit=2))

    def test_non_integral_exponential_stops_and_fails(self):
        o = check.build()
        o["Delta"] = dict(o["Delta"], u=s, s=Poly.const(1))
        results = list(check.run_checks(o))
        self.assertLess(len(results), check.EXPECTED_CHECKS)
        self.assertFalse(results[-1][1])

    def test_missing_root_quotient_stops_and_fails(self):
        o = check.build()
        o["Q1"] = None
        results = list(check.run_checks(o))
        self.assertLess(len(results), check.EXPECTED_CHECKS)
        self.assertFalse(results[-1][1])

    def test_exact_quotient_in_w(self):
        divisor = p**3 * w + s
        self.assertTrue(check.exact_quotient_in_w((u + w) * divisor, divisor) == u + w)
        self.assertIsNone(check.exact_quotient_in_w(w + 1, divisor))
        self.assertIsNone(check.exact_quotient_in_w(w, 2 * p**3 * w + s))
        self.assertIsNone(check.exact_quotient_in_w(w**3, p**3 * w**2 + s))  # must not loop

    def test_lift_rejects_non_integers(self):
        for bad in (None, 1.5, "s"):
            with self.subTest(value=bad):
                with self.assertRaises(TypeError):
                    s + bad

    def test_construction_objects(self):
        o = check.build()
        self.assertTrue(o["H_L"].uses_only(("p", "s", "u", "M", "L")))
        self.assertTrue(o["e0"].uses_only(("p", "s", "u", "M", "L", "w")))
        self.assertTrue(o["L_star"].uses_only(("p", "s", "u", "M")))
        self.assertIsNotNone(o["Q1"])

    def test_every_check_passes_on_the_manuscript(self):
        results = list(check.run_checks(check.build()))
        self.assertEqual(len(results), check.EXPECTED_CHECKS)
        self.assertEqual([label for label, ok, _ in results if not ok], [])


class Integration(unittest.TestCase):

    def run_main(self, *argv):
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            status = check.main(list(argv))
        return status, buffer.getvalue()

    def test_holds(self):
        status, out = self.run_main()
        self.assertEqual(status, 0)
        self.assertIn("RESULT: holds", out)
        self.assertNotIn("FAIL", out)

    # Labels (prefixes) of the checks each control must break; README's table mirrors this.
    EXPECTED_FAILURES = {
        "H-coefficient": ["con:identity", "con:derivation", "Phi(H)", "con:h-expansion",
                          "con:root-divisibility", "H(L) + p^3 w", "con:e-certificate",
                          "p^3 divides"],
        "derivation-value": ["con:derivation", "Phi(H)"],
        "linear-coordinates": ["con:linear-coordinates"],
        "linear-inverse": ["con:linear-coordinates", "con:h-expansion", "con:root-divisibility",
                           "H(L) + p^3 w", "con:e-certificate", "p^3 divides"],
        "e0-sign": ["con:e-certificate", "round trip Z", "round trip T", "q equals"],
    }

    def test_controls_break_exactly_the_expected_checks(self):
        self.assertEqual(set(self.EXPECTED_FAILURES), set(check.NEGATIVE_CONTROLS))
        for name, prefixes in self.EXPECTED_FAILURES.items():
            with self.subTest(control=name):
                failed = [label for label, ok, _ in check.run_checks(check.build(name)) if not ok]
                self.assertEqual(len(failed), len(prefixes))
                for label, prefix in zip(failed, prefixes):
                    self.assertTrue(label.startswith(prefix), (label, prefix))

    def test_each_negative_control_rejects(self):
        for name in check.NEGATIVE_CONTROLS:
            with self.subTest(control=name):
                status, out = self.run_main("--negative-control", name)
                self.assertEqual(status, 1)
                self.assertIn("RESULT: fails", out)
                self.assertIn("FAIL", out)

    def test_negative_control_rejects_under_optimized_python(self):
        proc = subprocess.run([sys.executable, "-O", str(HERE / "check.py"),
                               "--negative-control", "e0-sign"],
                              capture_output=True, text=True, cwd=HERE)
        self.assertEqual(proc.returncode, 1)
        self.assertIn("RESULT: fails", proc.stdout)

    def test_unknown_control_is_rejected_by_argparse(self):
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                check.main(["--negative-control", "no-such-control"])


if __name__ == "__main__":
    unittest.main()
