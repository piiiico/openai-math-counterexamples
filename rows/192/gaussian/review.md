# Separate AI review

One separately tasked OpenAI Codex agent reviewed the analytic claim and
implemented a 256-bit Arb scalar replay without importing the rational
checker. This is not human peer review or a kernel-checked proof.

The reviewer found no analytic blocker in the report partition, identity
`Q(c^2+2c*delta-J_delta)`, mean-bias estimate, central/tail bounds, endpoint
conventions or finite-alphabet coordinate-cost accounting. In particular,
the ordinary-report error baseline and both tails are included.

Arb independently enclosed the gain/Q lower expression above
`0.0264675620040983` and the uniform interval-mass lower expression above
`4.56116398254787e-26`, which exceeds `2^-85`. It checked `85m=1426063445`
and `m+1=16777218`. The reproducible implementation is `independent_arb.py`.

The reviewer emphasized the reciprocal directions: for `L<=exp(x)<=U`,
the tail upper bound uses `1/L`, whereas the interval-mass lower bound uses
`1/U`. The primary checker already used these directions; the final proof
now spells them out. The final prose also defines predictor deficit explicitly.
Neither clarification changes the mathematics or certificate.

Reviewed SHA-256 pins before those two explanatory additions:

- PROOF.md: `8b387c1c34f78b29a3ad0bfffe7e95e2163065ac506e742b9e5377093b846add`
- certificate.json: `ac23f344d48cd50a0b22c15542451add637ebc467bfb0c0a374b320e7d6752f4`

The review does not establish a transfer to finite alphabets with explicit
copy counts, a Boolean readout, amplification costs, or correctness of the
source's full theorem. The Arb script checks the scalar expressions
independently, not the implementation of the primary Taylor checker.
