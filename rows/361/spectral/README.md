# Family 361: a square-root-free finite spectral selection

Alexander Richard Towell, with substantial OpenAI Codex assistance.

This packet independently certifies the finite selection in equation
`eq:selection` of *A counterexample to integer-degree harmonic dimension
comparison*. It supplies a **different, slightly smaller selection** using
only integer eigenvalue sums. It does not verify the metric, transmission,
curvature, or growth arguments needed for the paper's geometric theorem.

At the source's parameters, the selected dimension is

```text
46785537904676899645365728857267392956181699200186010789105
```

and the Euclidean comparator is

```text
46779709349146362239266126538609505511855492134986686636251.
```

Their strict difference is
`5828555530537406099602318657887444326207065199324152854`.
The source's square-root upper-bound checker gives the larger surplus
`5895695327978147822684719048311498859195231499531297860`.
Both suffice for the same finite inequality. This is an independent finite
verification and a simpler sufficient criterion, not a stronger geometric
theorem or a claim of mathematical novelty.

## Reproduce

Python 3.10 or later, standard library only. From this workspace:

```sh
python -m research.family361_spectral.check
python -m research.family361_spectral.review_check --method both --certificate research/family361_spectral/certificate.json
python -m unittest research.family361_spectral.test_check -v
```

In the destination repository, the packet lives in `rows/361/spectral`:

```sh
python rows/361/check.py
python rows/361/spectral/review_check.py --method both --certificate rows/361/spectral/certificate.json
python -m unittest discover -s rows/361 -p 'test_*.py' -v
```

Expected: `status: verified`, 249 individually checked degrees, 16 full and
233 partial selections, the exact surplus above, and passing tests.
The canonical certificate SHA-256 is
`d727e20a2df0bf24e0a1710ab9767502fa4dd5407af8d2b6a8a3ea83f09ed543`.
Use `check.py --write` to regenerate and replay before writing the certificate.
Checks use explicit exceptions and remain active under `python -O`.

## Precise finite statement

Set `m=15`, `s=8`, `k=50000`, `q=101/100`,
`alpha^2=99853/100000`. For `0 <= b <= l`, define

```text
h(l,b) = C(b+7,7) C(l-b+7,7) - C(b+6,7) C(l-b+6,7)
       = (l+7)/7 * C(b+6,6) C(l-b+6,6),

N_l = C(l+15,15) - C(l+13,15),

lambda(l,b) =
  100000 * (101*l*(l+14) - (l-2*b)^2) / (101*99853).
```

A binomial coefficient with nonnegative top smaller than its bottom is zero.
Let the multiset for degree `l` contain `lambda(l,b)` with multiplicity
`h(l,b)`, and order it increasingly. Define each exponent `d >= 0` by
`d(d+14)=lambda`.

The certificate specifies integers `0 < M_l <= N_l` for every
`2 <= l <= 50212`, with

```text
mean of the first M_l exponents < 50000,
sum of M_l > sum_{l=0}^{50000} N_l.
```

The statement is entirely about these explicit finite multisets. Their
identification with angular eigenspaces uses the source's Hopf decomposition.
No metric-existence or asymptotic spectral-surplus theorem is assumed to
verify the displayed finite inequalities.

## Why eigenvalue means suffice

For any nonempty finite collection of nonnegative exponents, write
`bar_d` for their mean. Then

```text
mean(lambda) = mean(d^2) + 14 mean(d)
             = bar_d^2 + 14 bar_d + variance(d)
             >= bar_d(bar_d + 14).
```

The function `x(x+14)` is strictly increasing for `x >= 0`.
Thus `mean(lambda) < k(k+14)` implies `bar_d < k`.
This written argument contains no approximation to a square root.

The sufficient condition is stronger than the required condition. For
example, exponents 0 and 9 have mean `9/2 < 5`, but their eigenvalues
0 and 207 have mean `207/2 > 5(5+14) = 95`. We do not claim maximality
among all valid exponent selections.

## Exact selection and complete accounting

The eigenvalues increase as `b` goes from 0 to `floor(l/2)`:
the lowest eigenvalues correspond to the largest absolute Hopf charges.
Pair `b` with `l-b`, using multiplicity `2h(l,b)`, except that the
even middle term has multiplicity `h(l,l/2)`. Since the operator is
real symmetric, complexification does not add a further factor of two
to a real eigenspace's dimension. Partial groups mean choosing that many
independent real vectors from a repeated eigenspace.

All degrees 2 through 49963 are selected in full, because

```text
100000*l*(l+14) < 99853*50000*(50000+14)
```

bounds every eigenvalue by the threshold. The verifier checks the strict
boundary at 49963 and its failure at 49964; monotonicity covers all smaller
degrees. Their total is the telescoping dimension sum through 49963 minus
17, removing degrees zero and one.

Degrees 49964 through 50212 are represented individually. Put
`T = 101*99853*k*(k+14)`, and write `A` for the selected sum of
integer eigenvalue numerators and `M` for its count. Every row has the
strict positive slack `TM-A`. At a partial group with numerator `v > T`,
the maximum additional count under this stronger criterion is

```text
floor((TM-A-1)/(v-T)).
```

The subtraction of one enforces strictness. The replay also checks that
one further vector fails the criterion. The minimum recorded slack is
21909800000. The first partial degree is 49980. The smallest eigenvalue
already reaches the threshold at degree 50213 and increases thereafter.

The exact identities for `N_l` telescope to the displayed comparator.
There are no uncounted costs, extrapolated search ranges, or random choices:
this is a deterministic, completed finite computation.

## Three arithmetic routes

1. The generator uses the factored multiplicity polynomial, of degree 12 in
   `b`; its squared-charge moment has degree 14. For a polynomial `p`
   of degree `D`,
   `sum_{b=0}^{B-1} p(b) = sum_{j=0}^D Delta^j p(0) C(B,j+1)`.
   Thirteen and fifteen samples therefore give exact prefix sums, not an
   interpolation heuristic. The sampler explicitly rejects degrees below 14.
   Binary search finds the last admissible complete group.
2. The replay uses literal sums of the unfactored binomial differences.
   It checks 2,490,430 charge groups, strict inequalities, every certificate
   field, degree coverage, both cutoffs, and total counts. It does not call
   the generator's polynomial summation or selection functions.
3. The separately tasked AI reviewer supplied `review_check.py`, which
   independently implements both multiplicity recurrence enumeration and
   a seven-term Vandermonde/hockey-stick sum. It compares all degree records,
   and additionally checks 352,463 individual bidegrees, small-degree
   prefixes, and exact second moments.

The arithmetic parameter checks also confirm the source's positive endpoint
margin `29/700000`, `101*99853^15 < 100*100000^15`, and
`147/199706 < 1/1000`. These are parameter checks, not a verification of the
geometric construction.

Negative controls remove a degree, include degrees zero and one, alter
parameters or cutoffs, double an even middle eigenspace, and admit one
extra vector at a strict partial boundary. The latter updates the dependent
arithmetic fields too, so rejection tests the inequality itself.

## Provenance and limitations

Primary source: [openai/math at fd4aeeb](https://github.com/openai/math/tree/fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb/preprints/A-counterexample-to-integer-degree-harmonic-dimension-comparison-September-25-2026),
especially `build/sections/counting.tex` (Hopf multiplicities and
`eq:selection`), `finite-selection.tex`, `links.tex`, and
`verification/counting-check.py`.
The source credits Tanno for the Hopf-charge decomposition; the finite
selection and parameters belong to the source authors. Vandermonde,
hockey-stick, finite-difference, and variance identities are classical.

Destination base:
`piiiico/openai-math-counterexamples f8fd99fcb55c044c645083b162af9fd323d189cf`.
Pico's row361 identified the finite counting script but had not rerun it.
The full metric theorem remains classified as not finite; this packet does
not change that classification or certify the unexamined analytic arguments.

This is executable exact arithmetic plus a written mathematical bridge.
Neither the Python verifier nor that bridge is a Lean/kernel proof. Separate
AI review is not human peer review. The reproducibility receipt records pins,
hashes, commands and observations; it is not a general correctness guarantee.

Apache-2.0; see LICENSE and NOTICE. Substantial OpenAI Codex assistance
covered derivation, implementation, tests, documentation and separate AI review.
