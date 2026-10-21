# Scoped AI review

One separately tasked OpenAI Codex reviewer examined the source example,
checker and written derivation. This was independent AI review, not human
peer review or a second proof assistant.

The reviewer independently checked the sign convention J=-N/r, the
characteristic polynomial, the two 1/sqrt(2) bounds, and the parameter
corollary. An integer-matrix/Laplace determinant implementation agreed on an
interpolation grid sufficient for the relevant polynomial degree bounds;
that reviewer report is supporting evidence, not a second archived checker.
The final written geometric argument, Hodge input and wedge signs were read.
No blocker was reported.

The reviewer ran the then-current fourteen tests and optimized rejection
controls. Suggested regression improvements were addressed: the test now
requires the complete expected obligation-name set, and direct derivatives
and all six Hodge-star basis cases are covered. The maintainer agent then ran
the final fifteen tests in both normal and optimized Python. The reviewer did
not perform human peer review, kernel verification, or a full manuscript audit.

All global/differential facts and inequalities remain written arguments,
separate from the exact integer-polynomial checker. Repository acceptance
and any DOI publication are separate events recorded in the handoff.
