# Separate AI review

Reviewer: a separately tasked OpenAI Codex agent, family361_spectral_review,
2026-10-15. This is AI review, not human peer review or kernel verification.
The reviewer was limited to this precise finite claim and its assumptions.

No outstanding mathematical or certificate findings remained after review.
The reviewer checked the variance implication, ordered real multiplicities,
the single even middle term, arbitrary integer partial selections, omitted
17 low-degree dimensions, strict partial boundaries, both degree cutoffs,
the elementary parameter checks, and the stated analytic limitations.

The preserved `review_check.py` imports no certificate implementation. Its
recurrence enumerator and seven-term Vandermonde/hockey-stick implementation
agree on all six fields of all 249 certificate degree records. It also checks
352,463 bidegrees against two multiplicity formulas, all small-degree prefixes
through degree 64, and the exact squared-charge moment identity. The primary
agent reran this saved file successfully with `--method both --certificate
research/family361_spectral/certificate.json`.

The review corrected two presentation issues before submission: the selected
prefix has the largest absolute Hopf charges (lowest eigenvalues), and
Markdown formulas were rewritten in plain inline notation after accidental
escape characters were detected. A scan confirms no control bytes remain.

The reviewed conclusion is the finite spectral inequality for the explicitly
defined multisets. Interpreting those multisets as the source's angular
eigenspaces uses its Hopf decomposition. The metric, transmission and growth
arguments remain unreviewed here.
