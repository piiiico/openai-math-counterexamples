# Family 272: rigorous verification of the twenty-point geometry

**Independent verification.** For the pinned integer pencil, this packet
certifies exactly twenty distinct projective rank-loss points, each with a real
representative, and proves that no nonzero complex homogeneous quadric contains
ten of them. It checks Proposition `prop:twenty-directions`, not the complete
entanglement or zero-distillable-key theorem.

Contributor: **Alexander Richard Towell** (`queelius`, `lex@metafunctor.com`).
Substantial OpenAI Codex assistance: mathematical analysis, implementation,
tests, documentation, and review by a separate agent. This is not an independent
human review or a Lean formalization. License: [Apache-2.0](LICENSE);
see [NOTICE](NOTICE) for predecessor credit.

## Reproduce

Python 3.10 or newer is required. From the root of the `math-research` workspace:

```sh
python -m venv .venv
.venv/bin/python -m pip install -r research/family272/requirements-dev.txt
.venv/bin/python -m research.family272 verify
```

The final command verifies the saved [certificate.json](certificate.json)
without running the generator. It must exit zero and print JSON containing
`"status": "certified"`, `"distinct_real_projective_points": 20`,
`"checked_subsets": 184756`, and `"complete": true`.
The recorded run took **14.603 seconds**; runtime is machine-dependent.
The exact normalized determinant lower bound in [result.json](result.json)
is greater than **1.4436 × 10⁻¹¹**. All determinant balls excluded zero.

For the prepared upstream layout, install
`rows/272/rigorous/requirements-dev.txt`, then run these commands from `rows/272`
using the environment's Python:

```sh
python -m rigorous verify
python -m rigorous.independent_minor_check
python -m pytest rigorous -q
```

The corresponding local checks are:

```sh
.venv/bin/python -m research.family272.independent_minor_check
.venv/bin/python -m pytest research/family272 -q
```

Expected: all fifteen minors match the independent permutation expansion and
all **47 tests pass**. Tests include corrupted exact identities, incorrect source
digests, malformed fractions, missing/overlapping root intervals, duplicate
points, points on a quadric, wide uncertain balls, and incomplete subset coverage.
A failure to certify is inconclusive; it is not reported as a counterexample.

## What is new relative to the predecessors

The [OpenAI source](https://github.com/openai/math/blob/fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb/preprints/Entanglement-with-zero-distillable-secret-key-in-local-dimension-ten-September-27-2026/build/source/sections/certificate.tex)
already states and proves the complex geometric proposition using modular
and Galois arguments. This packet supplies a different, exhaustive verification
route; it does not claim a new counterexample or theorem.

[Pico's row 272](https://github.com/piiiico/openai-math-counterexamples/tree/d565f646470b5352d25c95e7793ad40157c3276f/rows/272)
is the immediate computational predecessor: all 184,756 subsets were checked in
double precision, with the fifty smallest determinants refined at sixty digits.
The added evidence here consists of exact substitution identities, exact
certificates that all twenty roots are real and distinct, and rigorous
zero-excluding determinant enclosures for **every** subset. No predecessor
implementation code is copied. The separately implemented permutation expansion
also checks every coefficient of all fifteen symbolic minors.

## Why these checks suffice

The full argument and software review are in [proof-review.md](proof-review.md).
Its essential steps are:

1. Recompute the fifteen maximal minors of the four integer matrices in
   [pencil.json](pencil.json). Their degree-four coefficient matrix `H` is
   invertible over the rationals. Thus the affine coordinate algebra is spanned
   by the twenty monomials of degree at most three. The same matrix excludes
   projective common zeros at infinity.
2. Check all fifteen identities `p_i(z,h2(z),h3(z)) = 0 mod f` exactly, with
   `f` monic of degree twenty. These give a surjection from that coordinate
   algebra onto `Q[z]/(f)`. The dimension bound makes it an isomorphism.
3. Check strict endpoint sign changes in twenty disjoint rational intervals.
   The intermediate value theorem and the degree of `f` certify exactly twenty
   distinct, simple real roots. No floating-point root residual is trusted.
4. Enclose the coordinates by outward-rounded Arb arithmetic. For every
   ten-element subset, the determinant of the quadratic evaluation matrix
   excludes zero. Invertibility over the complex numbers rules out a nonzero
   quadratic vanishing at those ten points.

The ten columns are the products `x_i*x_j`, `0 <= i <= j < 4`, in lexicographic
order. Each row is divided by its certified nonzero Euclidean norm; this
preserves nonsingularity. Root indices are zero-based and ordered by `t1`.
The smallest certified determinant lower bound occurred for indices
`[2,5,7,8,11,12,13,14,15,19]`. This identifies the smallest **enclosure lower
bound**, not a separately proven ordering of exact determinant magnitudes.

## Certificate format and trust boundary

The versioned JSON stores every rational as a reduced integer pair
`[numerator, positive_denominator]`; polynomial coefficients are in increasing
degree, with no trailing zeros. It contains `f`, all three coordinate
polynomials `(z,h2,h3)`, twenty interval endpoint pairs, and the pencil SHA-256.
Both the format and every mathematical obligation are rechecked on replay.

The generator obtains a candidate from rational linear algebra and numerical
root proposals. To regenerate it without overwriting the saved artifact:

```sh
.venv/bin/python -m research.family272 generate --certificate /tmp/family272-candidate.json
cmp research/family272/certificate.json /tmp/family272-candidate.json
```

Generation reports `candidate_generated`, not `certified`: it has not checked
the determinants. No random search is used. Root proposal intervals use a
512-bit dyadic grid; verification uses 1024-bit ball arithmetic. The stopping
rule is either the first failed obligation or all `C(20,10) = 184756` subsets.
The completed coverage is the entire finite domain, not a sample.

The trust boundary includes Python, exact SymPy/FLINT arithmetic, Arb's
inclusion-preserving rational conversion and matrix determinant, and the
platform. See the [python-flint ball matrix documentation](https://python-flint.readthedocs.io/en/latest/arb_mat.html).
Pinned packages are in [requirements.txt](requirements.txt); the recorded
environment is Python 3.10.20, python-flint 0.9.0 with FLINT 3.6.0, and SymPy
1.14.0. This certificate does not remove those software assumptions.

Source checksums, the workspace base, and predecessor pins are in
[provenance.json](provenance.json). The tensor criterion, PPT implications,
and the full secret-key conclusion remain outside this packet's scope.
Potential next obligations are recorded in [follow-ups.md](follow-ups.md).
The final test and coverage record is [verification.json](verification.json).
