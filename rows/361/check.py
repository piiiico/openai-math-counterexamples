#!/usr/bin/env python3
"""Check family 361's finite spectral selection, not its metric theorem.

Source: openai/math fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb,
preprints/A-counterexample-to-integer-degree-harmonic-dimension-comparison-September-25-2026/
build/sections/counting.tex (eq:selection) and finite-selection.tex.

The checked claim is that the explicit finite multiplicities admit a total
dimension above the Euclidean comparator, with each selected degree's mean
exponent strictly below 50000. See spectral/README.md for the exact scope.
"""
from spectral.check import main


if __name__ == "__main__":
    main()
    print("RESULT: holds (finite spectral selection only; metric theorem unchecked)")
