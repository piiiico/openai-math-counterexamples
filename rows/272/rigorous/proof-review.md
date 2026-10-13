# Family 272 certificate: mathematical design review

Contributor: Alexander Richard Towell. Review date: 2026-10-13.
This review was written by a separate OpenAI Codex agent from the agent building
the verifier. It is an agent review, not independent human or Lean verification.

## Scope and conclusion

The proposed exact-algebra and interval-determinant route is mathematically
sound. It proves the geometric proposition below if its stated computational
obligations pass. This document reviews that implication; it does not claim that
an executable verifier or the exhaustive determinant run has passed.

The source is Proposition `prop:twenty-directions` in
[`certificate.tex` at OpenAI commit `fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb`](https://github.com/openai/math/blob/fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb/preprints/Entanglement-with-zero-distillable-secret-key-in-local-dimension-ten-September-27-2026/build/source/sections/certificate.tex).
The reviewed local copy has SHA-256
`ea74b4f09a963b92b33ec9d67c0a87c235ccb332b61c53636a6eaf0a53a40506`.
The four matrices in [`pencil.json`](pencil.json) agree with the displayed source
matrices on visual inspection; the reviewed JSON has SHA-256
`96d9e33f225437f6bb4d1287881aac1f16cb626c0e700c9cd04c7254d555e740`.
The source already states and supplies a proof of the complex geometric assertion
using modular and Galois arguments. This alternative certificate does not establish a previously
unclaimed theorem. Pico's numerical family-272 computation in
[`piiiico/openai-math-counterexamples@d565f646470b5352d25c95e7793ad40157c3276f`](https://github.com/piiiico/openai-math-counterexamples/tree/d565f646470b5352d25c95e7793ad40157c3276f)
is the campaign's immediate computational predecessor.

## A sufficient certificate

Let `M(x) = x0 M0 + x1 M1 + x2 M2 + x3 M3` be the specified integer
six-by-four pencil. Let `p1,...,p15` be all four-by-four row minors of
`M(1,t1,t2,t3)`, recomputed from the matrices. Let `v` contain every monomial of
total degree at most three, and `w` every monomial of degree four. Their lengths
are 20 and 15. Write `p = D v + H w` over the integers.

The following checks suffice:

1. `det(H) != 0`, by exact integer/rational arithmetic or a nonzero determinant
   residue. Every degree-four monomial must be represented in `w`.
2. An exactly represented monic `f in Q[z]` has degree 20; exactly represented
   polynomials `h2,h3 in Q[z]` satisfy
   `pi(z,h2(z),h3(z)) = 0 mod f` for all 15 minors. Degrees below 20 for the
   coordinate polynomials are a convenient canonical representation.
3. There are 20 pairwise-disjoint closed rational intervals `[ai,bi]`, each with
   `ai < bi` and the strict, exact sign check `f(ai) f(bi) < 0`.
4. Evaluate each point `(lambda_i,h2(lambda_i),h3(lambda_i))` by enclosing
   `lambda_i` in its certified interval and using inclusion-preserving interval
   arithmetic. For every ten-element subset of the 20 points, enclose the
   determinant of the ten-by-ten evaluation matrix for all monomials of degree
   at most two. Each resulting finite determinant enclosure excludes zero.

Condition 3 can instead be established by another rigorously justified complete
real-root-isolation procedure. The sign-change form is especially easy to
verify independently of the numerical routine proposing the intervals.

## Proof

Set `A = Q[t1,t2,t3]/(p1,...,p15)`. Since `H` is invertible, the relations
`w = -H^-1 D v` hold in `A`. For any monomial of degree at least four, choose a
degree-four divisor and substitute its relation. Every resulting term has
strictly lower total degree. Induction therefore shows that the 20 entries of
`v` span `A`, so `dim_Q A <= 20`. No uniqueness of these reductions is assumed.

The exact identities in condition 2 induce a unital algebra homomorphism

`A -> B = Q[z]/(f),   (t1,t2,t3) -> (z,h2(z),h3(z))`.

This map is surjective because its image contains `z` and the rational
constants. Since a monic degree-20 polynomial gives `dim_Q B = 20`, the map is
an isomorphism and `dim_Q A = 20`. In particular `A` is nonzero. Irreducibility
of `f`, consistency of a formal multiplication operator, and a separate
existence argument for a common zero are unnecessary for this implication.

The intermediate value theorem gives at least one real root in each interval
in condition 3. Disjointness makes these 20 roots distinct. A degree-20
polynomial has only 20 complex roots counted with multiplicity, so each interval
contains exactly one root, every root is real, and every root is simple. The
Chinese remainder theorem, after extending scalars to `C`, gives

`C[t1,t2,t3]/(p1,...,p15) ~= C[z]/(f) ~= C^20`.

The coordinate evaluations are exactly the 20 triples
`(lambda_i,h2(lambda_i),h3(lambda_i))`. Conversely, any common zero defines a
unital `C`-algebra map from this quotient to `C`; a map from `C^20` to `C`
selects one factor. Thus there are no additional affine complex common zeros,
and the affine ideal is reduced. Distinct first coordinates make the 20
triples distinct.

Let `Delta_i` denote the homogeneous minors of `M(x)`. Homogeneity gives
`(Delta_i(0,t))_i = H w(t)`. If these vanish, invertibility of `H` forces
`w(t)=0`. The entries `t1^4,t2^4,t3^4` force `t=0`, which is not a projective
point. Hence there are no common zeros with `x0=0`. Every projective common zero
has a unique representative with `x0=1`. Vanishing of all maximal minors is
equivalent to `rank M(x)<4`, completing the count of projective rank-loss points.

There are exactly ten monomials of total degree at most two in three variables.
For any ten of the points, the true evaluation determinant belongs to the
enclosure in condition 4 and is therefore nonzero. The evaluation matrix is
invertible over both `R` and `C`. Dehomogenization `q(x) -> q(1,t)` identifies
homogeneous quadratics in four variables with polynomials of degree at most two
in three variables. Consequently a complex homogeneous quadratic vanishing at
those ten points has zero coefficient vector. Every nonzero such quadratic
vanishes on at most nine of the twenty points.

## Obligations at the software boundary

- **Exact algebra stays exact.** Store rational coefficients as exact numerator
  and denominator data. All 15 substitution remainders must be exactly zero.
  An interval containing zero or a small residual does not prove a polynomial
  identity. A characteristic polynomial of a proposed multiplication matrix
  alone is not this certificate.
- **Realness is certified.** Small imaginary midpoints, or imaginary intervals
  containing zero, do not by themselves prove a root is real. FLINT documents
  a separate real-root validation contract after complex root isolation. Its
  root finder also returns an isolation count that must reach the full degree.
  The rational endpoint sign test above supplies an alternative complete
  argument. See the [FLINT root-isolation documentation](https://flintlib.org/doc/acb_poly.html#root-finding).
- **Enclosures contain the exact points.** Convert rational endpoints and
  coefficients directly to outward-rounded balls. A displayed decimal midpoint
  is not a certified interval; do not narrow a ball by a print-and-parse
  roundtrip or by discarding its radius. Evaluating rational-coefficient
  polynomials requires rounding-enclosing conversion of those coefficients.
- **The determinant routine preserves inclusion.** Use the library's rigorous
  ball matrix determinant, or separately justify the interval algorithm.
  Gaussian elimination with a pivot ball containing zero cannot be treated as
  ordinary floating-point elimination. Dependencies between entries can widen
  the enclosure but cannot invalidate inclusion-preserving arithmetic.
- **Zero exclusion is the success predicate.** Require a finite determinant
  ball with zero excluded. Testing that a ball is not exactly the singleton
  zero, or that its midpoint is nonzero, is insufficient. Zero-containing or
  nonfinite results are inconclusive failures, not counterexamples.
- **Coverage is complete.** Enumerate every ten-element subset of a fixed list
  of 20 disjoint root intervals, with exactly `C(20,10)=184756` distinct subsets.
  A benchmark prefix, sample, or rerun of only the smallest floating-point
  determinants cannot satisfy condition 4. Preserve the ordering and source
  hashes tying the run to its exact algebraic certificate.

## Review status and remaining checks

The mathematical implication above is resolved by the written proof. At the
time of this design review, exact generated coefficients, interval endpoints,
exhaustive output, implementation tests, dependency pins, and corrupted-input
failure controls have not been inspected by this reviewer. The implementing
agent must record those checks separately. Useful controls include a nonzero
substitution remainder, overlapping root intervals, a root interval without a
strict sign change, and duplicate evaluation rows giving a determinant that
cannot exclude zero.

This result covers the projective rank-loss locus and its quadratic evaluation
property, with reality if condition 3 passes. It does not check the complete
entanglement or secret-key theorem, the tensor criterion, or its application.
The main follow-up is a compact exact or algebraic certificate for all
ten-point determinants that can be checked by a second implementation.

## Implementation-review addendum — 2026-10-13 06:44 UTC

The same separate Codex reviewer subsequently inspected `algebra.py`,
`enclosures.py`, `certificate.py`, `__main__.py`, and their tests. No material
correctness defect was found in their intended composition. This updates the
earlier design-only status; it remains an agent review using the same arithmetic
libraries, not human or proof-assistant verification.

The exact verifier recomputes all minors, checks the invertible quartic matrix,
requires a monic degree-20 polynomial and first coordinate exactly `z`, and
requires every substituted minor remainder to vanish exactly. Root verification
uses exact rational signs and strict interval separation. Coordinate evaluation
uses rational-to-Arb conversion and Horner arithmetic. The JSON parser requires
canonical integer numerator/positive-denominator pairs and rejects floats,
booleans, unreduced fractions, extra fields, and unsupported schema versions.
The CLI binds the certificate to the input digest and composes these checks
before requiring 20 points and all 184,756 subsets. Generation is absent from
its verification path.

The implementation normalizes each quadratic evaluation row. If `q_i` is its
true row, the true normalizer is `n_i = sqrt(sum_j q_ij^2) > 0`, since the row
contains `x0^2=1`. Its interval normalizer is required to be finite and exclude
zero. Therefore `det(normalized E) = det(E)/product_i n_i`, and zero exclusion
for the normalized determinant proves the required unnormalized nonvanishing.
The reported numerical lower bound refers to the normalized matrix.

The library boundary was checked against Python-FLINT 0.9.0 sources. Rational
conversion calls `arb_set_fmpq`; a rational radius is added with `arb_add_error`,
preserving the midpoint's rounding enclosure. `arb_mat.det()` calls the rigorous
`arb_mat_det`, and `abs_lower()` returns a downward-rounded exact dyadic value
that `.fmpq()` preserves. See the pinned
[`arb.pyx`](https://github.com/flintlib/python-flint/blob/0.9.0/src/flint/types/arb.pyx),
[`arb_mat.pyx`](https://github.com/flintlib/python-flint/blob/0.9.0/src/flint/types/arb_mat.pyx),
and [FLINT matrix contract](https://flintlib.org/doc/arb_mat.html).
Trust remains in Python, SymPy, Python-FLINT/FLINT, and their underlying runtime;
this review does not formally verify those implementations.

Observed verification:

- An independent 24-permutation integer coefficient expansion matched all 15
  minors. It is preserved in [`independent_minor_check.py`](independent_minor_check.py)
  with callable `check(matrices, minors)`. Run
  `python -m research.family272.independent_minor_check`. Altering a coefficient
  or removing a minor was rejected.
- A fresh run through the reviewed algebra/enclosure functions at proposal
  precision 512 bits and ball precision 1024 bits certified all 184,756 subsets
  in 14.69 seconds. Its smallest normalized absolute-determinant lower bound was
  approximately `1.4436826691981071e-11`, at zero-based subset
  `(2,5,7,8,11,12,13,14,15,19)`. Exact midpoint/radius comparisons confirmed that
  the first-coordinate balls contain all 20 certified rational intervals.
- The initial 25 arithmetic tests passed. Branch-enabled coverage of the two
  arithmetic modules was 95% overall: algebra 96%, enclosures 94%. Uncovered
  rejection paths included singular Krylov matrices, the verifier's invalid or
  singular quartic input, proposal precision below 32, repeated/nonfinite root
  proposals, and invalid prefix limits. This is a historical coverage snapshot,
  not a claim that all boundary cases were tested.
- After JSON/CLI tests and the independent-minor controls were added,
  `python -m pytest research/family272 -q` passed **44 tests**. These include
  subprocess rejection of altered polynomial coefficients and source digests.
  Additional injected-report checks confirmed the CLI rejects both a partial
  `1/184756` report and a superficially complete `92378/92378` report.

Reviewed implementation SHA-256 pins:

| File | SHA-256 |
|---|---|
| `algebra.py` | `3d42e4274d74fe2356e8c5265d1597445a69b26125bacd81adb862f15c8d959f` |
| `enclosures.py` | `fe0699c32e380b3986c3cea5029374d6b21727bc52beb7dff51860a49ec84f8d` |
| `certificate.py` | `08a6647e08e5e1ae1c5cfabcd8c6d5cea06f4ee5c00500988455b7e887b798a3` |
| `__main__.py` | `abf98f6f57e47c9d04df3d9a75949bd200692b6a19674eca41aa4205b966d328` |
| `independent_minor_check.py` | `4aa5af4195e0ea455fe222ec377f6aba3d4cda7c443c188bc16010c61a2f2d40` |
| `certificate.json` | `01f1558476f106aa14c359b3671f0d56ed9924553f661da3719948c9ca595607` |

The full success-path CLI report, final packaging, and final coverage run remain
the implementing agent's handoff obligations. The scoped mathematical assertion
and limits stated above are unchanged.
