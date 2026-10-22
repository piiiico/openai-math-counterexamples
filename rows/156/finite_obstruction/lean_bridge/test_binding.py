"""The binding must reject lost/changed clauses and changed variable meanings.

Alexander Richard Towell; substantial OpenAI Codex assistance. MIT.
"""
from copy import deepcopy
from contextlib import redirect_stdout, redirect_stderr
import io
import json
import os
from pathlib import Path
import unittest

from check_lean_binding import InvalidBinding, check_export, load_reference, main


class BindingTests(unittest.TestCase):
    # Hand-written small formula: (T0 OR not Q0) AND Q0, with two variables.
    variables = [
        {"kind": "triangle", "labels": [0, 1, 2]},
        {"kind": "tetrahedron", "labels": [0, 1, 2, 3]},
    ]
    clauses = [[1, -2], [2]]

    def data(self):
        return {"variables": deepcopy(self.variables),
                "raw_obligations": 2, "well_formed_obligations": 2,
                "clauses": deepcopy(self.clauses)}

    def check(self, data):
        return check_export(data, self.variables, self.clauses)

    def test_accepts_exact_formula(self):
        result = self.check(self.data())
        self.assertEqual(result["variables"], 2)
        self.assertEqual(result["clauses"], 2)

    def test_accepts_clause_and_literal_reordering(self):
        data = self.data()
        data["clauses"] = [[2], [-2, 1]]
        self.check(data)

    def test_rejects_missing_clause_even_when_counts_are_adjusted(self):
        data = self.data()
        data["clauses"].pop()
        data["raw_obligations"] = data["well_formed_obligations"] = 1
        with self.assertRaises(InvalidBinding):
            self.check(data)

    def test_rejects_duplicate_clause_in_place_of_another(self):
        data = self.data()
        data["clauses"] = [[1, -2], [1, -2]]
        with self.assertRaises(InvalidBinding):
            self.check(data)

    def test_rejects_sign_change(self):
        data = self.data()
        data["clauses"][0][1] = 2
        with self.assertRaises(InvalidBinding):
            self.check(data)

    def test_rejects_changed_variable_meaning(self):
        data = self.data()
        data["variables"][0]["labels"] = [0, 1, 3]
        with self.assertRaises(InvalidBinding):
            self.check(data)

    def test_rejects_changed_variable_order(self):
        data = self.data()
        data["variables"].reverse()
        with self.assertRaises(InvalidBinding):
            self.check(data)

    def test_rejects_filtered_out_obligation(self):
        data = self.data()
        data["raw_obligations"] = 3
        with self.assertRaises(InvalidBinding):
            self.check(data)

    def test_rejects_invalid_literals(self):
        for literal in (0, 3, -3, True, "1", 1.0):
            with self.subTest(literal=literal):
                data = self.data()
                data["clauses"][0][0] = literal
                with self.assertRaises(InvalidBinding):
                    self.check(data)

    def test_rejects_duplicate_literal(self):
        data = self.data()
        data["clauses"][0].append(1)
        with self.assertRaises(InvalidBinding):
            self.check(data)

    def test_rejects_invalid_counts_and_schema(self):
        for key, value in (("raw_obligations", True),
                           ("well_formed_obligations", "2"),
                           ("clauses", None), ("variables", {})):
            with self.subTest(key=key):
                data = self.data()
                data[key] = value
                with self.assertRaises(InvalidBinding):
                    self.check(data)
        data = self.data()
        data["extra"] = 0
        with self.assertRaises(InvalidBinding):
            self.check(data)

    def test_preserves_clause_multiplicity(self):
        data = self.data()
        data["clauses"] = [[2], [2]]
        result = check_export(data, self.variables, [[2], [2]])
        self.assertEqual(result["clauses"], 2)

    def test_rejects_malformed_variable_rows(self):
        for row in (None, {}, {"kind": "triangle", "labels": [True, 1, 2]},
                    {"kind": "triangle", "labels": [0, 1, 10]},
                    {"kind": "triangle", "labels": [0, 1, 1]},
                    {"kind": "triangle", "labels": [2, 1, 0]},
                    {"kind": "triangle", "labels": [0, 1]},
                    {"kind": "unknown", "labels": [0, 1, 2]},
                    {"kind": "triangle", "labels": "012"}):
            with self.subTest(row=row):
                data = self.data()
                data["variables"][0] = row
                with self.assertRaises(InvalidBinding):
                    self.check(data)

    def test_rejects_non_list_clause(self):
        data = self.data()
        data["clauses"][0] = "1 -2"
        with self.assertRaises(InvalidBinding):
            self.check(data)


@unittest.skipUnless(os.environ.get("FAMILY156_PACKET_DIR"),
                     "set FAMILY156_PACKET_DIR for pinned-predecessor integration checks")
class IntegrationTests(unittest.TestCase):
    def setUp(self):
        self.packet = Path(os.environ["FAMILY156_PACKET_DIR"]).resolve()
        self.root = Path(__file__).resolve().parent
        self.pins = json.loads((self.root / "source-pins.json").read_text())

    def test_full_binding_and_cli_rejection_controls(self):
        for control in (None, "drop-clause", "flip-literal", "swap-variables"):
            with self.subTest(control=control), redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                args = ["--packet-dir", str(self.packet)]
                if control:
                    args += ["--negative-control", control]
                self.assertEqual(main(args), 1 if control else 0)

    def test_rejects_each_wrong_source_hash(self):
        for name in self.pins["source_files"]:
            with self.subTest(name=name):
                pins = deepcopy(self.pins)
                pins["source_files"][name] = "0" * 64
                with self.assertRaisesRegex(InvalidBinding, "source hash mismatch"):
                    load_reference(self.packet, pins)

    def test_rejects_wrong_reference_cnf_hash(self):
        pins = deepcopy(self.pins)
        pins["canonical_cnf_sha256"] = "0" * 64
        with self.assertRaisesRegex(InvalidBinding, "reference CNF hash mismatch"):
            load_reference(self.packet, pins)


if __name__ == "__main__":
    unittest.main()
