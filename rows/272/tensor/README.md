# Family 272: an exact certificate for the PPT tensor construction

Alexander Richard Towell, with substantial OpenAI Codex assistance.

**Independent finite verification, with a written mathematical bridge.**
Starting from the integer pencil already checked in row 272, this packet
constructs a `100 × 100` integer Choi matrix `Z0`. It verifies complete
positivity, the required transpose identities, nonzeroness, and 100 polynomial
kernel identities. Combined with the existing twenty-direction geometry
certificate, these establish that `Z0` is entangled and is the Choi matrix of a
composition of two PPT maps on `Mat(10)`.
Here “PPT maps” means completely positive linear maps whose output-transposed
maps are also completely positive; no trace-preserving or quantum-channel
condition is imposed or established.

This checks the geometry-to-tensor step requested in
[the maintainer's PR #1 response](https://github.com/piiiico/openai-math-counterexamples/pull/1#issuecomment-6170707922).
It does not check the operational secret-key theorem, protocols, or asymptotic
distillation. It does not claim a new counterexample, a Lean proof, or human
peer review.

## Exact result

The [certificate](certificate.json) contains the 36 integer Kraus matrices of
the intermediate map, the signed exterior complement, the full integer Choi
matrix, all fifteen homogeneous maximal minors, and rational coefficients for
every polynomial kernel identity. All arithmetic uses arbitrary-precision
integers and rationals.

- `rank(Z0) = 80`, computed by exact integer linear algebra.
- `trace(Z0) = 1,381,419,987,480`.
- `Z0[0,0] = 40,310,784 = 4 × 6 × 36^4 > 0`.
- Both intermediate Choi partial-transpose identities hold entry by entry.
- The composite Choi matrix equals a Gram matrix of 1,296 composed Kraus
  vectors, and its output partial transpose equals itself.
- All 100 coordinates of `Z0 (v(x) ⊗ v(x))` are exact rational linear
  combinations of the fifteen maximal minors of the pencil.

The [result](result.json) records structured values and evidence digests.
Runtime of the first complete finite tensor replay was about 0.11 seconds on
the recorded environment; this excludes the separate geometry replay.

## Reproduce

Install `tensor/requirements-dev.txt` in a virtual environment, then from this
repository's `rows/272` directory run:

```sh
python -m rigorous verify && python -m tensor rigorous/pencil.json
```

In the original research workspace the same check is:

```sh
.venv/bin/python -m research.family272 verify && .venv/bin/python -m research.family272_tensor research/family272/pencil.json
```

Expected: both commands exit zero. The first certifies twenty distinct real
points and all 184,756 ten-point subsets. The second reports `status: certified`,
the values above, and 100 polynomial identities. Its status refers only to the
finite tensor obligations. The geometry prerequisite is deliberately reported
separately. No claimed zero-secret-key consequence is verified by these commands.

Run `python -m pytest tensor -q` upstream, or
`.venv/bin/python -m pytest research/family272_tensor -q` in this workspace.
Controls break block symmetry, replace the exterior complement by the identity,
and use a zero pencil. Additional certificate and command-line controls are
recorded in the verification receipt.

The separate review's explicit tensor embeddings and SymPy determinant check
are reproducible with `python tensor/review_check.py` from `rows/272`.
This script imports no code from the primary checker. It uses assertions and
explicitly refuses optimized Python; the primary verifier remains active under
`python -O`.

## Written bridge from the certificate to the claimed consequence

All maps and vector spaces below are over the complex numbers. The matrices
in the certificate happen to have integer or rational entries.

1. Let `M_i` be the four supplied `6 × 4` matrices and define
   `L(E_ij) = M_i^T M_j`. For row `r`, let column `i` of `Q_r` be row `r`
   of `M_i`, transposed. Then `L(A) = Σ_r Q_r A Q_r*`.
   The checked block symmetries give `L ∘ T = L = T ∘ L`.

2. Let `U0` have columns `e_i ⊗ e_i` for diagonal pairs and
   `e_i ⊗ e_j + e_j ⊗ e_i` for `i < j`. Let `V0` have columns
   `e_i ⊗ e_j - e_j ⊗ e_i` for `i < j`. Define
   `S0(A) = V0* (L ⊗ L)(U0 A U0*) V0`.
   The 36 Kraus matrices are `H_rs = V0* (Q_r ⊗ Q_s) U0`.
   The checker obtains `J(S0)` both from their Gram matrix and directly from
   the matrix-unit blocks of `L`. The resulting matrices agree exactly.
   The partial-transpose checks on every matrix unit establish the complex
   linear-map identities `S0 ∘ T = S0 = T ∘ S0`; these are not tests only on
   real or Hermitian inputs.

3. Let `K` send each exterior pair to its complementary pair with the sign
   of the corresponding permutation of `0,1,2,3`. Set
   `R0(A) = K S0(A)^T K* = K S0(A) K*`.
   Both maps are CP and fixed by output transpose, hence PPT.
   The input-transpose identity for `R0` gives
   `T ∘ R0† = (R0 ∘ T)† = R0†`, so its CP adjoint is also PPT.
   For the real coordinate inclusion `E : C^6 → C^10`, define
   `Phi1(A) = E S0(A^T) E*` and `Phi2(B) = R0†(E* B E)`.
   Their complete positivity and PPT properties follow from these identities
   and CP conjugation. Since `E*E = I`, their composition is `R0† ∘ S0 ∘ T`.

4. Use the input-first Choi convention
   `J(F) = Σ_ij E_ij ⊗ F(E_ij)`. The checker constructs `Z0` from the
   superoperator composition and separately as the Gram matrix of the
   vectorized matrices `H_rs* K* H_tu`. Equality proves `Z0 ≥ 0`.
   Its strictly positive `(0,0)` entry proves it is nonzero. No numerical
   eigenvalue tolerance or rank threshold is used.

5. Write `v(x) = (x_i x_j)_(i≤j)` in lexicographic pair order.
   If `Delta_rho(x)` are the fifteen maximal minors of `M(x)`, the saved
   rational matrix `C` is checked coefficient by coefficient in the identity

   `Z0 (v(x) ⊗ v(x)) = C (Delta_rho(x))_rho`.

   This is an identity of homogeneous degree-four polynomials in four
   variables over Q, hence also over C. Thus every certified singular
   direction gives a kernel vector `v(x) ⊗ v(x)`.

6. Suppose a nonzero product `u ⊗ w` belongs to `range(Z0)`.
   Since `Z0` is Hermitian, it is orthogonal to every kernel vector, so
   `(u* v(x)) (w* v(x)) = 0` at each of the twenty certified directions.
   Both factors are nonzero homogeneous quadratic polynomials: their
   coefficients are the fixed conjugates of the nonzero vectors' coordinates,
   and the ten monomials are distinct. The previous geometry certificate
   proves that each factor vanishes at at most nine points. Their zero sets
   cannot cover twenty points. This contradiction excludes every nonzero
   complex product vector from the range.

A nonzero separable positive matrix is a sum of product-vector rank-one
matrices; each summand's vector lies in its range. Product exclusion therefore
proves nonseparability. Equivalently, the CP composition is not entanglement
breaking. This last equivalence is the standard Choi separability criterion.

## Relation to the source's orthonormal coordinates

The source uses orthonormal embeddings `U,V`. Let `D` be diagonal with entry
`1` on diagonal pairs and `sqrt(2)` on off-diagonal pairs. Then
`U0 = U D`, `V0 = sqrt(2) V`, and

`S0(A) = 2 S(D A D)`, `R0(A) = 2 R(D A D)`,

`Z0 = 4 (D ⊗ D) Z (D ⊗ D)`.

This is an invertible local congruence. It preserves positivity, nonzeroness,
and whether the range contains a nonzero product vector. Also `D v(x)` is
the source's normalized quadratic vector. The factor four explains the
difference between our positive test value and the source's `10,077,696`.
No claim that the two matrices are numerically identical is made.

## Scope and provenance

The primary source is `openai/math` at
`fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb`, the September 27, 2026 manuscript
*Entanglement with zero distillable secret key in local dimension ten*,
especially `sections/geometry.tex` (Proposition `prop:tensor-criterion`),
`certificate.tex`, and `foundations.tex`.

The geometric predecessor is Alexander Richard Towell's rigorous packet,
merged in `piiiico/openai-math-counterexamples` PR #1, and Pico's preceding
numerical audit. Destination base: `f8fd99fcb55c044c645083b162af9fd323d189cf`.
The source credits classical Choi/PPT machinery and product-exclusion
arguments; this packet adds an explicit independent finite verification.

The trust boundary includes Python and FLINT exact integer/rational linear
algebra, plus Arb for the separately replayed geometry certificate. The
written bridge is not machine-checked. A separately tasked AI review is
recorded independently from kernel verification and human peer review.
See [verification.json](verification.json) for source pins and executed checks,
and [review.md](review.md) for the separate AI review.

Apache-2.0; see `LICENSE` and `NOTICE`. Substantial OpenAI Codex assistance
covered the derivation, implementation, tests, documentation, and AI review.
