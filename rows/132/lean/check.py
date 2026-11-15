#!/usr/bin/env python3
"""Recompile Family 132's XOR-size bad-set lemma and rejecting controls.

Source: explicit_labelling/PROOF.md Lemma A, repository commit
ea346085fbd714ee5c4d09fc1e899836bc41f3cf. Not the separation theorem.
Default: use this packet's pinned Lake environment. --environment accepts a
JSON object with compiler and LEAN_PATH from an existing pinned environment.
All owned modules are rebuilt in a fresh temporary directory in either mode.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import tempfile


def decode_output(stdout):
    """Decode Lean JSON diagnostics and the JSON payloads emitted by Audit."""
    diagnostics = [json.loads(line) for line in stdout.splitlines() if line.strip()]
    reports = [json.loads(r["data"]) for r in diagnostics
               if r.get("severity") == "information"]
    return diagnostics, reports


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--environment", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    manifest = json.loads((root / "lake-manifest.json").read_text())
    controls = json.loads((root / "controls.json").read_text())
    declared = {entry["path"] for entry in controls}
    present = {str(path.relative_to(root)) for path in (root / "negative").glob("*.lean")}
    if not controls or declared != present or len(declared) != len(controls):
        raise SystemExit("Negative-control manifest is empty, incomplete, or duplicated")
    if args.environment:
        config = json.loads(args.environment.read_text())
        compiler = config["compiler"]
        search_path = config["LEAN_PATH"]
    else:
        compiler = subprocess.check_output(
            ["lake", "env", "which", "lean"], cwd=root, text=True).strip()
        search_path = subprocess.check_output(
            ["lake", "env", "printenv", "LEAN_PATH"], cwd=root, text=True).strip()
    version = subprocess.check_output([compiler, "--version"], text=True).strip()
    if not version.startswith("Lean (version 4.33.1,"):
        raise SystemExit(f"Wrong compiler: {version}")
    # Locate the pinned package checkout, without importing any platform modules.
    candidates = [Path(part).resolve() for part in search_path.split(os.pathsep)]
    mathlib = next((part.parents[3] for part in candidates
                    if part.parts[-5:] == ("mathlib", ".lake", "build", "lib", "lean")), None)
    if mathlib is None:
        raise SystemExit("Pinned Mathlib package not found in LEAN_PATH")
    package_paths = []
    for package in manifest["packages"]:
        checkout = mathlib.parent / package["name"]
        revision = subprocess.check_output(
            ["git", "-C", str(checkout), "rev-parse", "HEAD"], text=True).strip()
        if revision != package["rev"]:
            raise SystemExit(f"Dependency pin mismatch: {package['name']}")
        subprocess.run(["git", "-C", str(checkout), "diff", "--quiet", "HEAD"], check=True)
        package_paths.append(str(checkout / ".lake/build/lib/lean"))
    print("Pinned compiler and dependency commits verified.")
    with tempfile.TemporaryDirectory(prefix="family132-replay-") as build:
        env = dict(os.environ, LEAN_PATH=os.pathsep.join([build] + package_paths))

        def compile_module(name, expected_failure=None):
            source = root / (name + ".lean")
            output = Path(build) / (name + ".olean")
            output.parent.mkdir(parents=True, exist_ok=True)
            result = subprocess.run(
                [compiler, "--json", "-DwarningAsError=true", "-o", str(output), str(source)],
                cwd=root, env=env, text=True, capture_output=True)
            records, reports = decode_output(result.stdout)
            errors = [r for r in records if r.get("severity") == "error"]
            if expected_failure is not None:
                if result.returncode == 0 or not errors:
                    raise RuntimeError(f"Control did not reject with a Lean diagnostic: {name}")
                # Require the intended failure, not an import or environment failure.
                messages = [r.get("data", "") for r in errors]
                if not any(expected_failure in message for message in messages):
                    raise RuntimeError(f"Wrong rejection for {name}: {records}")
                print(f"REJECTED: {name}")
            else:
                if result.returncode or errors or result.stderr:
                    raise RuntimeError(f"Build failed for {name}: {records}\n{result.stderr}")
                for record in reports:
                    print(json.dumps(record, sort_keys=True, separators=(",", ":")))
                print(f"PASS: {name}")
            return reports

        for name in ["Proof", "Controls"]:
            compile_module(name)
        audit = compile_module("Audit")
        if not any(r.get("kind") == "axiom_audit" for r in audit):
            raise RuntimeError("Missing declaration audit")
        for control in controls:
            compile_module(str(Path(control["path"]).with_suffix("")),
                           expected_failure=control["expected_diagnostic_fragment"])
    print("RESULT: holds — arbitrary-size XOR-label bad-set bound kernel-checked; "
          f"{len(controls)} negative controls rejected; full separation theorem unchecked.")


if __name__ == "__main__":
    main()
