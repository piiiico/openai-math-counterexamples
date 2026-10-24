# Exact rotation moments and a triangular-base obstruction

Alexander Richard Towell, with substantial OpenAI Codex assistance.

**Result:** three rotated copies of any centered isotropic planar base have
vanishing weighted zeroth and mixed derivative moments. For an equilateral
triangle, the remaining moment is `diag(0,3,3)`. This gives a nine-point
configuration with an exact tensor-criterion obstruction, using one
transcendental parameter and the algebraic constant sqrt(3).

The [written proof](PROOF.md) establishes the algebraic lemma and distinctness
for transcendental `0<t<1/4`. Its **non-Ramsey consequence is conditional on
OpenAI's classification theorem**, which this packet does not verify. It is
not a smallest-example claim: the source discusses earlier seven-point work.
At rational parameters the derivation argument cannot simply be specialized.

This independently checks the source's twelve-point square example and extends
its moment calculation to triangles. It retains OpenAI's derivation mechanism
and Pico's prior square checks; see [NOTICE.md](NOTICE.md). The source is
`openai/math@fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb`, Proposition cons:twelve
and equations cons:derivation-moments/obstruction in07-consequences.tex.
Exact source hashes and comparisons with two later pins are in sources.json.

## Reproduce

Python3.13.15 was used. In a virtual environment:

```sh
python -m pip install -r requirements-dev.txt
python reproduce.py
python -m pytest -q test_check.py
```

The replay must end with
`RESULT: exact rotation obstruction, six rejecting runs and independent evidence reproduced`.
The checker verifies54 moment entries and72 product-rule coefficients over
Q(sqrt(3))(t). Six negative runs alter the weight, rotation sign or derivation,
under ordinary and optimized Python. The tests also reject invalid bases and
distinguish coincident points at t=0 from a nine-point sample at t=1/9; that
rational sample is a geometric control, not a non-Ramsey witness.

The [separate AI review](review/REVIEW.md) includes independent differentiation
of a nonconstant coefficient example and36 pairwise distance checks. It is not
human peer review or Lean verification. Exact symbolic identities are checked;
the classification theorem, transcendence and full coloring quantifiers are
not computationally verified here. See verification.json for actual commands.
