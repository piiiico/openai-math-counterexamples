# Independent AI review

Reviewer: a separately tasked OpenAI Codex agent, 2026-10-15. This is AI
mathematical/software review, not human peer review or proof-assistant kernel
verification. The reviewer had read-only responsibility and made no edits.
Its independent computation is preserved in [review_check.py](review_check.py),
with a portable certificate path and an explicit optimized-mode guard.

No blocking mathematical flaw was found. Conditional on the previous geometry
certificate, the finite certificate and written bridge establish a nonzero
product-free Choi range for a composition of two PPT endomorphisms of `Mat(10)`
without invoking the manuscript's general tensor criterion.

The reviewer independently checked the following obligations:

- Real Kraus entries justify transpose as adjoint in the computation. Checking
  Choi partial-transpose identities on every matrix unit proves identities of
  complex-linear maps, not merely identities on real or Hermitian inputs.
- The two endomorphisms have Kraus matrices `E H_rs` and
  `H_rs* K* E*`; their positive, output-transpose-fixed Choi matrices and their
  composition reproduce the saved `Z0`.
- Direct construction of `U0,V0` reproduces all 36 intermediate Kraus matrices.
  Their Gram diagonals are 1 or 2 for symmetric pairs and uniformly 2 for
  exterior pairs. The formulas `S0 = 2 S o Ad_D` and
  `Z0 = 4(D tensor D) Z (D tensor D)` are correct.
- Independently, `S0(P_e00) = 2592 I6`, so
  `Z0[0,0] = 4 * 6 * 36^4 = 40310784`.
- Separate SymPy determinants reproduce all fifteen homogeneous minors;
  symbolic polynomial expansion confirms all 100 rational kernel identities.
- The tensor pencil equals the previously certified geometry pencil exactly.
  Any ten quadratic evaluations are independent, so each nonzero complex
  quadratic vanishes on at most nine of the twenty directions. Two such zero
  sets cannot cover all twenty directions.
- Fresh replay reproduces rank 80, trace 1381419987480, every saved result
  field, and evidence digest
  `3fb937f2977c14c6cf840e00a2f9cca9b02db077942c02ccc2ed7e2ac0fff650`.

The conjugation in `u* v(x)` conjugates fixed coefficients, leaving a quadratic
polynomial in `x`; the product exclusion therefore applies over C.

One nonblocking clarification was requested and applied: PPT maps here need
not preserve trace. No quantum-channel claim is made. The polynomial identities
were checked computationally, and the mathematical bridge was reviewed in
prose. Neither activity checks the operational secret-key theorem.
