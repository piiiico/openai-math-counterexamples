# Independent scoped AI review

One separately tasked OpenAI Codex reviewer read the pinned appendix, numeric
transcription, primary checker, tests, runner and findings. No correctness
issue was found. This is AI review, not human peer review.

The reviewer independently implemented exponent-vector polynomials generated
by weak compositions and finite-field matrices using SymPy DomainMatrix/GF(7).
The primary uses sorted variable-index tuples and its own standard-library
modular elimination. No primary checker import or copied arithmetic helper
was used in the independent replay.

The reviewer separately transcribed weights, point, pivots and tangent from
TeX. Expected minor/basis data are shared through certificate.json, and both
methods share the source formulas and Python runtime. The coordinating session
added canonical matrix-fingerprint reporting only to the supplied arithmetic.
All 42 matrix fingerprints agree, as do every rank vector, displayed determinant,
corner entry and direct bordered determinant. Full kernel, tangency and
first-derivative equations vanish in both implementations.

Final review included printed monomial lists and signed pivot traces,
J/H0/projected-J dimension guards, zero-tangent rejection and the raw integer
negative principal-minor boundary control. The latter rejects only a naive
PSD interpretation: the source's later real form is different.

The reviewer reran ordinary/optimized implementations, all ten rejecting
controls and 28 tests in each mode. The final runner and README were reviewed.
Source hashes and mathematical transcription were examined. Characteristic-zero
lifting, real-form genericity, real PSD deformation and final nonliftability
remain outside review scope. No global novelty claim is made.
