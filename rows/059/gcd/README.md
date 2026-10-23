# Family 059: exact verification by weighted GCD cancellation

**Finding.** OpenAI's supplied 849-coefficient relation satisfies Lemma
`seed:product`: at d = 3^11, every support index obeys 0 < 2b < d and 3 does
not divide b, the exact coefficient sum E is positive, and both rational
products are exactly 1. All coefficients have at most 140 decimal digits.
The complete sum and reduction counts are in `output.txt`.

This checker uses compressed weighted GCD splitting. It verifies the two
products together as pairs of integer exponents, reducing 5,094 input terms
to an empty basis in 17,758 splits. It uses no prime sieve, primality test,
trial-division factorization, probabilistic acceptance, or expansion of the
enormous powers. [PROOF.md](PROOF.md) establishes the rewrite invariant,
termination, source transcription, and meaning of the empty normal form.

The source authors already supplied an exact trial-division validator; Pico
already supplied an exact sieve validator and a modular consistency check.
This is an independent exact implementation by a different arithmetic route,
not a missing-proof repair or a new counterexample. The original rank proof
and this supplementary explicit witness are separate routes to the lemma.

## Reproduce

Python 3.13.15 was used. Only the standard library and Bash are needed.
From this directory:

```sh
bash reproduce.sh
```

Expected exit 0 and final line:

```text
RESULT: Family 059 exact GCD cancellation and rejecting controls reproduced
```

The script verifies source hashes, runs all 22 tests under normal and
optimized Python, compares the full check's deterministic output with
`output.txt`, and requires each of five controls to exit 1 in both modes.
The tests compare 150 seeded small cases with a separate exact rational
oracle; those implementation tests are not the full witness certificate.

```sh
python3 check.py
python3 -O check.py --negative-control coefficient
```

The second command must report `RESULT: fails` and exit 1.

| Control | What changes | Required failure |
| --- | --- | --- |
| coefficient | First exponent increases by 1; metadata recomputed | Nontrivial residual product |
| wrong-ratio | The R factor 3d-b moves from denominator to numerator | Nontrivial residual product |
| reverse-sign | All exponents change sign; metadata recomputed | E is negative, although both products remain 1 |
| invalid-index | First b becomes 3 | Support outside B |
| wrong-d | Declared d increases by 1 | Wrong source dimension |

Additional tests reject duplicate/out-of-range indices, noninteger and zero
coefficients, inconsistent exact metadata, malformed terms, and source-hash
damage. Checks use explicit failures and remain active under `python -O`.

## Source pins and independence

Manuscript: openai/math commit
`fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb`, paper directory
`preprints/Ambiently-homeomorphic-isolated-hypersurfaces-of-multiplicities-two-and-three-September-24-2026`.

- `build/sections/seeds.tex:7–19`: exact finite-product statement.
- `build/sections/certificate.tex:11–19`: supplied alternative witness.
- `verification/support/explicit-relation.json`: the actual 849 rows.

These three files are byte-identical at current source commit
`1581d4cbdd69a0faf34b2089614fe2a814316a6a`. Full hashes and paths are in
`source-pins.json`. The relation SHA-256 is
`e5a3ad0b8901ac358374575dbaf7be9e03bb84063def63749f16618cf2ba1780`.

The checker was written from the manuscript and raw JSON. Before implementation
we read only Pico's scope/docstring and table metadata, not its algorithm body
or the authors' validator. Pico's implementation was inspected only after our
checker and tests had been written and the complete witness had passed.
The predecessor and comparison pins are recorded in `verification.json`.
The task is coordinated in [issue #20](https://github.com/piiiico/openai-math-counterexamples/issues/20).

## Scope and credit

Established: this one exact arithmetic witness, with written algorithm
soundness and finite implementation checks. This is not a kernel-checked
proof, human peer review, a new multiplicity counterexample, or a global
novelty assessment. The rank calculation, chain construction, variable counts,
spectra, Seifert forms, monodromy and topological homeomorphism are outside
scope. The witness-generation hashes inside the original JSON are retained
provenance; their generation artifacts are not independently reconstructed.

Alexander Richard Towell (ORCID `0000-0001-6443-9897`), with substantial OpenAI
Codex assistance in code, proof explanation, verification, writing and scoped
AI review. Credit OpenAI for the construction and witness, and Pico / Håkon
Åmdal for the predecessor exact check. Original supporting code/prose are MIT;
copied source files retain Apache-2.0. AI review is distinct from human review.
