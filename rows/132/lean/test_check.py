"""Lean JSON transport regressions; mathematical controls live in Lean."""
import json
import unittest
from check import decode_output


class DiagnosticTests(unittest.TestCase):
    def test_lean_wraps_audit_json_in_information_diagnostic(self):
        report = {"kind": "axiom_audit", "count": 1, "declarations": []}
        wire = json.dumps({"severity": "information", "data": json.dumps(report) + "\n"})
        diagnostics, reports = decode_output(wire)
        self.assertEqual(reports, [report])
        self.assertEqual(diagnostics[0]["severity"], "information")

    def test_errors_are_diagnostics_not_success_reports(self):
        diagnostics, reports = decode_output(json.dumps(
            {"severity": "error", "data": "Owned axiom: Family132.injected"}))
        self.assertEqual(reports, [])
        self.assertEqual(diagnostics[0]["severity"], "error")

    def test_truncated_or_non_json_output_rejected(self):
        for wire in ['{', 'RESULT: holds', json.dumps({"severity":"information", "data":"not a report"})]:
            with self.subTest(wire=wire), self.assertRaises(json.JSONDecodeError):
                decode_output(wire)

    def test_empty_output_has_no_audit(self):
        self.assertEqual(decode_output("\n"), ([], []))


if __name__ == "__main__":
    unittest.main()
