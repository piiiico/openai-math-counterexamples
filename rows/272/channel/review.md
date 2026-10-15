# Scoped independent AI review

Reviewer: the same separately tasked OpenAI Codex reviewer used for the
tensor contribution, now reviewing its channel extension. No additional
reviewer or subagent was launched. Only review_check.py was delegated.

The review derived the block formula independently and evaluated it on
all441 matrix units, once and twice, without importing primary code or
squaring a reshuffled superoperator. It also constructed actual integer
Gram witnesses for the two failure effects.

The reviewer found a blocking forward/inverse reshuffling error in the
initial primary implementation. The primary trace-preservation test also
failed on that error. A distinct inverse and a nonsymmetric tagged-matrix
regression test fixed it. The final complete sparse matrices agree with
the independent implementation, including their source and certificate
digests. No remaining blocker was reported.

Independently confirmed: D=4923191; both trace-preserving identities;
both Choi matrices fixed by partial transpose; the whole square corner
equals Z0/D²; D²=24237809622481; and the flag product eigenvector.
Failure controls reject missing failure branches, a lost flag, a
trace-preserving redirected flag, and corrupted saved Choi entries.
Normal and Python -O replay both pass.

The final review explicitly accepts the integer-coordinate provenance
qualification: this is the existing generic source construction applied
to the certified rescaled pair. Numerical equality to the source's
orthonormal-coordinate channel is neither asserted nor needed.
It confirms that no additional dimension factor enters the unnormalized
input-first Choi convention.

The non-entanglement-breaking implication is conditional on the separately
established nonseparability of Z0 and uses a written local-compression
argument. No secret-key, new-construction, full-range product-exclusion,
human-review or kernel-verification claim follows.
