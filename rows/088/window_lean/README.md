# Kernel-checked finite-window recurrence for simplex products

Alexander Richard Towell, with substantial OpenAI Codex assistance.

Lean proves the value recurrence underlying the accepted exact optimizer
packet. For the **defined cap19 dynamic-programming sequence** `cappedValue`,

    cappedValue(n+13) = c13 * cappedValue(n)  for every n>=100.

The strict failure at 99 and the minimality of the uniform cutoff 100 are also
kernel-checked. Here c_d=(d+1)d^d/d!; factor dimensions are 2..19.
The finite-to-infinite implication is a reusable theorem for rational maximum
recurrences, with arbitrary width, period and nonnegative scaling factor.

## Exact formal scope

- `WindowPeriodicity.lean`: maximum-fold homogeneity; strong induction from
  a window of width D; guarded versus unguarded recurrence; finite-prefix uniqueness.
- `ConcreteCertificate.lean`: all 130 recurrence states2..131, all 19 period
  equalities100..118 and strict failure99, proved with `decide +kernel`.
- `CappedValue.lean`: a well-founded, total definition with initial values 1,0;
  agreement with the table; unconditional period/minimality for that definition.
- `Consumers.lean`: 17 positive consumers/counterexamples. Four separate false
  propositions must fail to compile, including negative scaling and omission
  of the last window endpoint.

Printed theorem dependencies contain only `propext`, `Classical.choice` and
`Quot.sound`. No native-evaluation axiom or admitted proof is used. `decide +kernel`
checks a proof by kernel reduction; it is distinct from `native_decide`.

**The analytic exclusion of factors>=20 remains a written dependency.** Thus
identifying `cappedValue` with unrestricted simplex-product maxima uses the
accepted predecessor's written reduction. Optimal witness sets, the residue
partition formula and convex geometry are not formalized in this packet.
This is kernel verification of specified algebra, with separate AI review;
human peer review and global novelty are not claimed.

## Reproduce

Pinned Lean 4.33.1 (commit 819816b2e0a3bf405af45ae5c7af2491d8f5bee6),
Mathlib 0df444a360eaa60ab8c11dca51a86af692955474; all transitive pins in
`lean/lake-manifest.json`. On a fresh checkout, run `lake exe cache get`
from `lean/` after installing elan. Do not run `lake update`.
Then run from this packet:

```sh
python reproduce.py
python -m pip install -r requirements-dev.txt
python -m pytest -q test_generate.py
python -O -m pytest -q test_generate.py
```

Expected final line:
`RESULT: kernel recurrence certificate, concrete period and four false controls verified`.
The Python code uses the standard library; tests use pytest 8.4.2.
All 132 table entries are structurally generated from the pinned predecessor
JSON (zero sentinel at 1 added explicitly). `python generate.py` checks the
binding; `--write` regenerates it. Ten tests cover tampering and regeneration.
Source, toolchain and manifest hashes are checked before replay.

## Provenance

Predecessor source 653420103fb8856f81d7c6b1d7aeaf16a1ebd0b1,
[PR38](https://github.com/piiiico/openai-math-counterexamples/pull/38),
accepted 2026-10-25T06:29:52Z. `source/certificate.json` is unchanged.
Pico's independent review and classical/source predecessors retain credit.
See NOTICE.md and source-pins.json. The existing Family088 v1.1.0 archive
https://doi.org/10.5281/zenodo.23633115 contains neither this formalization nor
the exact-optimizer extension; those have separate public/archival states.
