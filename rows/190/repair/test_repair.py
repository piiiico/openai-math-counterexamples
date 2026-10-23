"""Independent controls for the fixed-anchor repair certificate."""

from itertools import product
from pathlib import Path
import json
import unittest
import tempfile
import shutil
import subprocess
import sys
import contextlib
import io
from unittest.mock import patch

import repair


class ModelTests(unittest.TestCase):
    def test_h1_domain(self):
        model = repair.Model(1)
        self.assertEqual(len(model.rows), 8)
        self.assertEqual(len(model.columns), 8)
        self.assertEqual(len(model.bodies), 48)
        self.assertEqual(len(model.violations(model.original)), 8)
        self.assertEqual(len(model.modes), 6)

    def test_repair_and_hitting_set(self):
        for h in [1, 2, 3]:
            with self.subTest(h=h):
                model = repair.Model(h)
                fixed = model.dummy_leaf_repair()
                self.assertEqual(model.cost(fixed), 4**h)
                self.assertEqual(model.violations(fixed), [])
                hit = model.leaf_hitting_set()
                self.assertEqual(model.cost(hit), 2**h)
                violations = model.violations(hit)
                self.assertTrue(violations)
                self.assertTrue(
                    all(
                        b.mode.kind is repair.Kind.W and b.mode.sign is repair.Sign.PLUS
                        for b in violations
                    )
                )

    def test_bit_order_and_objective(self):
        model = repair.Model(1)
        self.assertEqual(len(model.original), 64)
        self.assertEqual(model.cost(model.original), 0)
        bits = list(model.original)
        bits[0] = not bits[0]
        self.assertEqual(model.cost(bits), 1)
        with self.assertRaises(ValueError):
            model.cost(bits[:-1])

    def test_counter_semantics(self):
        for n in range(1, 7):
            for bound in range(n + 1):
                cnf, highest, counter = repair.at_most(list(range(1, n + 1)), bound, n)
                for bits in product([False, True], repeat=n):
                    assignment = {i + 1: b for i, b in enumerate(bits)}
                    assignment.update(
                        {var: sum(bits[:i]) >= j for (i, j), var in counter.items()}
                    )
                    valid = all(
                        any(assignment[abs(lit)] == (lit > 0) for lit in clause)
                        for clause in cnf
                    )
                    self.assertEqual(valid, sum(bits) <= bound)

    def test_rup(self):
        self.assertTrue(repair.is_rup([(1,), (-1,)], ()))
        self.assertFalse(repair.is_rup([(1, 2)], ()))
        self.assertTrue(repair.is_rup([(1, 2), (-1,)], (2,)))
        with self.assertRaises(ValueError):
            repair.replay([(1,)], [(1,)])
        with self.assertRaises(ValueError):
            repair.replay([(1,)], [()])

    def test_source_matrix_entries(self):
        m = repair.Model(1)
        # Child leaf diagonal is shared by the two signs.
        leaves = [p for p in m.rows if p.kind is repair.PositionKind.LEAF]
        self.assertEqual(len(leaves), 2)
        for p in leaves:
            self.assertTrue(m.entry(p, p))
        rootminus = next(
            p
            for p in m.rows
            if p.kind is repair.PositionKind.INTERNAL and p.sign is repair.Sign.MINUS
        )
        rootplus = next(
            p
            for p in m.rows
            if p.kind is repair.PositionKind.INTERNAL and p.sign is repair.Sign.PLUS
        )
        self.assertFalse(m.entry(rootminus, rootminus))
        self.assertTrue(m.entry(rootplus, rootplus))


class PacketTests(unittest.TestCase):
    packet = Path(__file__).parent

    def test_complete_certificate(self):
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(repair.verify(self.packet), 25)

    def test_strict_controls(self):
        for control in ["truncate", "weaken", "witness"]:
            with self.subTest(control=control), self.assertRaises(ValueError):
                repair.verify(self.packet, control)

    def test_binding_and_schema_controls(self):
        original = json.loads((self.packet / "certificate.json").read_text())
        changes = [
            ("depth", 2),
            ("excluded_budget", 2),
            ("cnf_sha256", "0" * 64),
            ("repaired_bits", [True] * 63),
            ("rup_additions", [[0], []]),
        ]
        for key, value in changes:
            with self.subTest(key=key), tempfile.TemporaryDirectory() as temp:
                packet = Path(temp)
                record = dict(original)
                record[key] = value
                (packet / "certificate.json").write_text(json.dumps(record))
                with self.assertRaises(ValueError):
                    repair.verify(packet)

    def test_satisfiable_weakening_witness(self):
        model = repair.Model(1)
        witness = list(model.original)
        for i, r in enumerate(model.rows):
            for j, c in enumerate(model.columns):
                if (
                    r.kind is repair.PositionKind.DUMMY
                    and c.kind is repair.PositionKind.LEAF
                    and c.node == 1
                ):
                    witness[i * 8 + j] = False
        self.assertEqual(model.cost(witness), 2)
        retained = [
            b
            for b in model.bodies
            if not (
                b.mode.kind is repair.Kind.W
                and b.mode.sign is repair.Sign.MINUS
                and b.mode.parity == 0
            )
        ]
        self.assertFalse(
            any(
                tuple(witness[c] for c in b.cells) == (True, False, True, True)
                for b in retained
            )
        )

    def test_cli_optimized(self):
        result = subprocess.run(
            [sys.executable, "-O", str(self.packet / "repair.py")],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("RESULT: certified fixed-anchor repair optimum 4", result.stdout)
        for control in ["truncate", "weaken", "witness"]:
            result = subprocess.run(
                [
                    sys.executable,
                    "-O",
                    str(self.packet / "repair.py"),
                    "--negative-control",
                    control,
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("RESULT: rejected", result.stdout)

    def test_main_paths(self):
        for control in [None, "truncate", "weaken", "witness"]:
            args = ["repair.py"] + (["--negative-control", control] if control else [])
            with (
                patch.object(sys, "argv", args),
                contextlib.redirect_stdout(io.StringIO()),
            ):
                self.assertEqual(repair.main(), int(control is not None))

    def test_rup_input_validation(self):
        for candidate in [(0,), (1, -1, 0), (True,), (1.0,)]:
            with self.assertRaises(ValueError):
                repair.is_rup([], candidate)
        self.assertTrue(repair.is_rup([], (1, -1)))
        with self.assertRaises(ValueError):
            repair.at_most([1], -1, 1)
        with self.assertRaises(ValueError):
            repair.Model(0)
        with self.assertRaises(ValueError):
            repair.Model(1).cost([0] * 64)

    def test_signed_cardinality(self):
        clauses, _, counter = repair.at_most([-1, 2], 1, 2)
        for x, y in product([False, True], repeat=2):
            bits = [not x, y]
            assignment = {1: x, 2: y}
            assignment.update({v: sum(bits[:i]) >= j for (i, j), v in counter.items()})
            self.assertEqual(
                all(any(assignment[abs(l)] == (l > 0) for l in c) for c in clauses),
                sum(bits) <= 1,
            )


class IndependentTests(unittest.TestCase):
    def test_complete_domain(self):
        import independent

        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(independent.run(), 43745)
        with self.assertRaises(RuntimeError):
            independent.run(True)

    def test_independent_cli(self):
        import independent

        for control in [False, True]:
            argv = ["independent.py"] + (["--negative-control"] if control else [])
            with (
                patch.object(sys, "argv", argv),
                contextlib.redirect_stdout(io.StringIO()),
            ):
                self.assertEqual(independent.main(), int(control))
        result = subprocess.run(
            [
                sys.executable,
                "-O",
                str(Path(independent.__file__)),
                "--negative-control",
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("repair within budget three", result.stdout)


if __name__ == "__main__":
    unittest.main()
