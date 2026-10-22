"""Bind the Lean export to the pinned predecessor CNF, preserving multiplicities.

Copyright (c) 2026 Alexander Richard Towell. MIT license.
Substantial OpenAI Codex assistance. This is not a SAT certificate checker.
"""
import argparse
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys


class InvalidBinding(ValueError):
    """The exported formula or its source pins do not match."""


def canonical_hash(clauses):
    payload = json.dumps(sorted(sorted(c) for c in clauses), separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


def check_export(data, expected_variables, expected_clauses):
    fields = {"variables", "raw_obligations", "well_formed_obligations", "clauses"}
    if not isinstance(data, dict) or set(data) != fields:
        raise InvalidBinding("unexpected export schema")
    variables, clauses = data["variables"], data["clauses"]
    if not isinstance(variables, list) or not isinstance(clauses, list):
        raise InvalidBinding("variables and clauses must be lists")
    for row in variables:
        if not isinstance(row, dict) or set(row) != {"kind", "labels"}:
            raise InvalidBinding("unexpected variable schema")
        labels = row["labels"]
        if (row["kind"] not in ("triangle", "tetrahedron")
                or not isinstance(labels, list)
                or any(type(x) is not int or not 0 <= x < 10 for x in labels)
                or labels != sorted(set(labels))
                or len(labels) != (3 if row["kind"] == "triangle" else 4)):
            raise InvalidBinding("invalid variable meaning")
    if variables != expected_variables:
        raise InvalidBinding("ordered variable meanings differ")
    for field in ("raw_obligations", "well_formed_obligations"):
        if type(data[field]) is not int or data[field] != len(clauses):
            raise InvalidBinding("obligation count differs; filtering must remove nothing")
    for clause in clauses:
        if not isinstance(clause, list):
            raise InvalidBinding("clause must be a list")
        if any(type(x) is not int or not 1 <= abs(x) <= len(variables) for x in clause):
            raise InvalidBinding("literal must be a nonzero in-range integer")
        if len(set(clause)) != len(clause):
            raise InvalidBinding("duplicate literal")
    actual = Counter(tuple(sorted(c)) for c in clauses)
    expected = Counter(tuple(sorted(c)) for c in expected_clauses)
    if actual != expected:
        missing = sum((expected - actual).values())
        extra = sum((actual - expected).values())
        raise InvalidBinding(f"clause multiset differs: missing={missing}, extra={extra}")
    return {"variables": len(variables), "clauses": len(clauses),
            "raw_obligations": data["raw_obligations"],
            "well_formed_obligations": data["well_formed_obligations"],
            "canonical_cnf_sha256": canonical_hash(clauses)}


def load_reference(packet_dir, pins):
    # Verify the original bytes before executing the small predecessor encoder.
    for name, expected in pins["source_files"].items():
        if hashlib.sha256((packet_dir / name).read_bytes()).hexdigest() != expected:
            raise InvalidBinding(f"source hash mismatch: {name}")
    spec = importlib.util.spec_from_file_location("_family156_pinned_encoding", packet_dir / "encoding.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    encoding = module.build()
    numbered = [(number, {"kind": kind, "labels": sorted(labels)})
                for kind, table in (("triangle", encoding.triples),
                                    ("tetrahedron", encoding.tetrahedra))
                for labels, number in table.items()]
    numbered.sort()
    if [number for number, _ in numbered] != list(range(1, encoding.variables + 1)):
        raise InvalidBinding("reference variable numbers are not consecutive")
    variables = [row for _, row in numbered]
    clauses = encoding.clauses({"down", "nonempty"}) + [tuple(encoding.tetrahedra.values())]
    if canonical_hash(clauses) != pins["canonical_cnf_sha256"]:
        raise InvalidBinding("reference CNF hash mismatch")
    return variables, clauses


def build_and_export(root):
    lean = root / "lean"
    output = lean / ".lake/build/lib/lean/Family156Bridge.olean"
    output.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["lake", "env", "lean", "-o", str(output), "Family156Bridge.lean"],
                   cwd=lean, check=True, timeout=120)
    subprocess.run(["lake", "env", "lean", "Consumers.lean"],
                   cwd=lean, check=True, timeout=120)
    result = subprocess.run(["lake", "env", "lean", "--run", "Export.lean"],
                            cwd=lean, check=True, timeout=120, capture_output=True, text=True)
    return json.loads(result.stdout)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packet-dir", required=True, type=Path,
                        help="pinned predecessor finite_obstruction directory")
    parser.add_argument("--export", type=Path, help="saved Lean JSON (default: bundled export)")
    parser.add_argument("--run-lean", action="store_true", help="rebuild proof and generate a fresh export")
    parser.add_argument("--negative-control", choices=("drop-clause", "flip-literal", "swap-variables"))
    args = parser.parse_args(argv)
    root = Path(__file__).resolve().parent
    try:
        pins = json.loads((root / "source-pins.json").read_text())
        if hashlib.sha256((root / "source/Labels.lean").read_bytes()).hexdigest() != pins["labels_sha256"]:
            raise InvalidBinding("original Labels.lean hash mismatch")
        variables, clauses = load_reference(args.packet_dir.resolve(), pins)
        if args.run_lean and args.export:
            raise InvalidBinding("choose fresh generation or a saved export, not both")
        data = build_and_export(root) if args.run_lean else json.loads(
            (args.export or root / "lean-export.json").read_text())
        if args.negative_control == "drop-clause":
            data["clauses"].pop()
            data["raw_obligations"] -= 1
            data["well_formed_obligations"] -= 1
        elif args.negative_control == "flip-literal":
            data["clauses"][0][0] *= -1
        elif args.negative_control == "swap-variables":
            data["variables"][0], data["variables"][1] = data["variables"][1], data["variables"][0]
        result = check_export(data, variables, clauses)
        print(json.dumps(result, indent=2))
        print("RESULT: exact source-to-CNF binding verified" +
              (" after fresh Lean build" if args.run_lean else " for saved export"))
        return 0
    except (InvalidBinding, OSError, ValueError, subprocess.SubprocessError) as error:
        print(f"RESULT: FAIL: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
