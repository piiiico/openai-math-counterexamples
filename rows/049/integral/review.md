# Scoped independent AI review

One separately tasked OpenAI Codex reviewer examined the written theorem,
the primary checker and the pinned source. This is AI review, not human peer
review or a Lean kernel proof. No second reviewer was used.

The reviewer found no mathematical blocker:

- The W-elimination proves equality of ideals by explicit linear combinations;
  it never cancels h or y.
- The line parametrization has determinant `alpha*h+beta*y=1`, so its inverse
  works over arbitrary commutative rings.
- All remaining eliminations have unit leading coefficient. No flatness,
  domain, reducedness or characteristic hypothesis is needed.
- Standard-library dual arithmetic independently gives `F(2,1,-1,1)=-1`
  and gradient `(0,0,0,0)`. The chain-rule contradiction requires exactly
  that the base ring be nonzero and survives adjoining unused variables.
- The source already states the generic lifting lemma over arbitrary rings.
  Its credit and the prior integer inverse-map check must remain explicit.

The reviewer supplied a separate FLINT implementation of all fourteen free
integer polynomial identities and an exhaustive dual-ring implementation of
both zero-fibre maps. It passed over `F2[e]/(e^2)` and `F3[e]/(e^2)`, with
64 and 729 zero-fibre points respectively. `independent_replay.py` preserves
that arithmetic. The main agent replaced review-only assertions with explicit
failures and added three mutated-input controls, then reran the resulting file.
It imports neither SymPy nor the primary checker.

Review environment: Python 3.10.20, python-flint 0.9.0, FLINT 3.6.0.
The originally reviewed files had SHA256:

- `PROOF.md`: `13fe8f9c74335892cf4b755fcc59cda57acb86ea9b7c6f96638b02332911050c`.
- `checker.py`: `84fdcce4fee3bf35b9db1cff7fb1e7a56516b062b783fba0268aa031e10a292b`.
- Source `paper.tex`: `60993c0b524291b7f707e42eec89ec7e910c22760d81f1d3af007c229228c13c`.

Subsequent edits clarify predecessor credit and the source Lean scope, and
ensure the finite control domain cannot be empty. They change no mathematical
formula or proposition. Final file hashes and reruns are in `verification.json`.
Pointwise finite-ring bijections alone would not establish the universal-ring
claim; the ideal identities and explicit algebra maps supply that argument.
