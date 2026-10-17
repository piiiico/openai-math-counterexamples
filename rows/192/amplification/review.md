# One separately tasked AI mathematical review

The reviewer found no mathematical blocker in the uniform score-moment bounds,
Berry--Esseen normalization, central/tail estimates, score-conditioning identity,
report-cell degree, recursive counts, Hölder readout or exact table recursion.
It checked both cutoff endpoints, tail endpoints and the rare-event denominators.
It explicitly did not review the checker implementation or evaluate the target
Boolean function. This is OpenAI Codex review, not human peer review or a kernel
proof; the classical Berry--Esseen theorem remains an inherited dependency.

Reviewed proof SHA-256 before the requested clarification:
`c0cb9d320306c8e8cac8e348b2c6eec7c96c411f3e66e321221962ece799bf9a`.
The reviewer requested spelling out that F is a deterministic map on the sign
cube, excluding external randomness. That clarification was applied; final
proof SHA-256 is
`00b6db19c3f5f6fde4a012aa5dd7224d5275b0df0e992d216da910a1bddfb0ac`.
No mathematical formula changed after review.

The reviewer supplied independent384-bit Arb arithmetic and a distinct exact
asymmetric-score example on three signs, with variance9/7 and third moment162/49.
It checks the two-copy score-conditioning identity and nine-copy readout, plus
seven symbolic recurrence-exponent identities. `independent_arb.py` preserves
that implementation with assertions replaced by explicit failure checks and
an excessive-gain negative control. The coordinator reran both modes; execution
logs and versions are in `verification.json`.

The independent gain lower expression is
`0.026467562004098319934030119339958044...`, exceeding1/50.
Its two fourth-moment tail terms equal2^-125 exactly. Arithmetic agreement
supports the scalar budget; it does not independently formalize the written
quantifiers or establish novelty.
