# Separate AI mathematical review

One separately tasked OpenAI Codex reviewer examined the finite-transfer
argument and hidden assumptions. Completed October 17, 2026, before publication.
This is not human peer review or formal proof.

Reviewed `PROOF.md` SHA-256:
`a487a8211fe6a47e7cd8bac3dfc71df5ba7971c5d5897f5d94ab024bb9dd01bc`.

The reviewer found no blocker in the endpoint conventions, rare-event
denominators, truncation at R=16, exact deficit, or sign/degree accounting.
It independently checked the restricted-moment factors, the m-cell CDF error,
and the tail coefficients, and inspected Shevtsova's Corollary 1 directly.
The left/right CDF convention change is valid by normal-CDF continuity.

It supplied a separate 384-bit Arb implementation, preserved in
`independent_arb.py` with explicit rejection replacing Python assertions and
an excessive-margin negative control added. The coordinator reran that script;
the fresh command, environment, result and hash are in `verification.json`.
No functions or bounds were imported from the primary checker.

The reviewer also reported 440 exact endpoint-moment identities and an exact
83,521-tuple deficit check in its own scratch calculations. Those scratch
experiments are not the archived reproducible controls and are not counted as
the packet's certified coverage. The archived controls independently cover
2,750 weighted tuples, 612 endpoint cases and three second-moment cases.

The review does not independently prove Berry--Esseen, formally verify the
written argument, or provide the later amplification and Boolean readout.
The main implementation is covered separately by exact tests and failure
controls; agreement between AI reviewers alone is not evidence of correctness.
