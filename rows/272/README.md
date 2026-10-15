# Family 272 verification artifacts

- [`check.py`](check.py) and [`output.txt`](output.txt): Pico's original numerical
  audit, with exact block identities and numerical rank-loss/quadratic checks.
- [`rigorous/`](rigorous/README.md): Alexander Richard Towell's independent
  exact-algebra and interval certificate, developed with substantial OpenAI
  Codex assistance. It certifies all twenty real projective rank-loss points
  and every one of the 184,756 ten-point quadratic evaluation determinants.
- [`tensor/`](tensor/README.md): Towell's follow-up exact integer/rational
  certificate for the explicit PPT composition, developed with substantial
  OpenAI Codex assistance. Combined with `rigorous/`, its 100 polynomial kernel
  identities and written argument show that the composite Choi matrix has no
  nonzero complex product vector in its range. This closes the finite
  geometry-to-tensor interface; it does not check the secret-key theorem or
  claim trace-preserving maps.
- [channel/](channel/README.md): Towell's exact instantiation of the source's
  existing absorbing-flag completion, developed with substantial OpenAI
  Codex assistance. It certifies a trace-preserving PPT channel in dimension
  21, its full square, and the entangled corner inherited from tensor/.
  An independent matrix-unit implementation reproduces both saved Choi
  matrices. The full square range contains the flag product vector; the
  non-entanglement-breaking consequence uses local compression, and no
  secret-key conclusion is checked.

The packets preserve the original audit and its attribution. See their READMEs
for pinned dependencies, reproduction, proofs, and limitations.
