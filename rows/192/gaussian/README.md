# Family 192: an explicit Gaussian intermediate construction

Alexander Richard Towell, with substantial OpenAI Codex assistance.

This packet instantiates the source's asymptotic coarse-reporting step
with rational parameters and predictors
for `m+1 = 16,777,218` independent standard Gaussian inputs. A written proof
and an exact rational checker establish

`Var(E[L | report]) > m + Q/50`, where `Q > 2^(-1,426,063,445)`.

Here `L` is the sum of all inputs, `m=16,777,217`, and `Q` is the probability
that all leaf interval tests pass. The selector, intervals, both exceptional
predictors, ordinary reports and Gaussian tails are fully specified in
[PROOF.md](PROOF.md). The finite-alphabet report indicators use at most `m`
coordinates. The construction uses the source's reporting partition.

This makes the **Gaussian intermediate step** explicit. It does not supply
a Boolean function, averaging copy counts, amplification costs, or an efficient
construction. In particular, Family 192's full `not-explicit` classification
is not resolved. The observed Gaussian report is not finite-valued.

## Reproduce

From this directory, using Python 3.10.20 (standard library only):

```sh
python3 checker.py
python3 -m unittest discover -s . -v
```

Expected primary output ends with
`RESULT: certified Gaussian predictor gain > Q*1/50` (exit 0).
The conservative displayed gain ratio is `0.026467562004`; all acceptance
decisions use exact rational numbers, not that decimal summary.

Each deliberately changed input must exit 1:

```sh
python3 checker.py --negative-control coarse-grid
python3 checker.py --negative-control strong-margin
```

These reject, respectively, half as many grid intervals at the same radius
and a requested gain ratio of `1/5`. The latter exceeds even the optimistic
ceiling `c^2+2cD` in the exact predictor identity, since `J_delta>=0`.
Coarse-grid rejection concerns this sufficient bound and does not prove that
the changed construction has nonpositive gain.
Unit tests also reject false interval-mass bounds, insufficient Taylor order,
invalid geometry and malformed parameters, and check execution under `-O`.

An independent 256-bit Arb evaluation is optional:

```sh
python3 -m pip install -r requirements-arb.txt
python3 independent_arb.py
```

It must print `RESULT: independent Arb scalar certificate passed`.
The primary checker requires no third-party packages. Installation of the
optional dependency is not needed to replay the exact rational certificate.

## What is verified

The exact checker certifies four scalar obligations: a conditional-mean
density ratio, a strictly positive full gain bound including both tails, a
uniform interval-mass lower bound, and the integer dimension/product exponent.
A uniform written estimate covers every interval; no list of millions of
intervals or underflow-prone product is generated. It uses rational Taylor
enclosures, and remains fail-closed when Python assertions are disabled.

[PROOF.md](PROOF.md) supplies the analytic implication from those inequalities
to retained variance. It derives the predictor identity directly rather than
assuming the source's asymptotic theorem. That written proof has one separate
AI review, recorded in [review.md](review.md), not human peer review or kernel
verification. Arb is an independent implementation of the scalar arithmetic,
not a formal check of the probability argument.

[provenance.json](provenance.json) records the archive base, destination base,
source commit and every source-file hash. [verification.json](verification.json)
records the commands, outputs, versions and hashes. [attempts.md](attempts.md)
records the small preliminary parameter probe and its stopping rule. The
parameters are not claimed minimal, practical or globally novel.

## Credit and license

The reporting partition and coordinate-cost mechanism are from OpenAI's
Family 192 manuscript, pinned at
`1581d4cbdd69a0faf34b2089614fe2a814316a6a`. The precise source claim is
`Var(E[L | O]) >= m + E g` in
`Unbounded-Violations-of-the-Square-Root-Degree-Bound-September-26-2026/build/sections/03-alternatives.tex:47-58`.
The original row and small-Boolean search are Pico's work, operated by
Håkon Åmdal. This packet does not alter those results or attribute our new
certificate's output to a maintainer rerun.

The new parameter schedule, rational predictors, analytic bounds, checker and
documentation were prepared by Alexander Richard Towell with substantial
OpenAI Codex assistance. New files are MIT licensed; upstream source files
are linked and hashed, not copied or relicensed.
