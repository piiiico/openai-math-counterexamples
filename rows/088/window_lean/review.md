# Scoped independent AI review

One separately tasked OpenAI Codex reviewer examined all four Lean modules,
source generation, ten tests, replay, four false controls and predecessor proof.
No correctness defect was found at the reviewer's reporting threshold.

The reviewer directly compiled every module, checked standard axiom lists,
replayed the four rejecting fixtures and reran ten generator tests in each
Python mode. The supplied independent consumer proofs cover zero width/scale,
negative scaling, natural subtraction underflow, guard semantics, and a
counterexample to dropping the last window equation. They are preserved in
Consumers.lean and recompiled by the required build.

The defined cappedValue is well-founded, with explicit initial conditions.
The concrete arithmetic covers 130 recurrence states, 19 window identities,
strict failure at 99 and minimal uniform cutoff 100. The source binding covers
132 array entries, including the explicit zero sentinel at 1. Every final
printed dependency list contains only the standard Lean axioms.

The reviewer checked the pinned Lean implementation of `decide +kernel`:
it builds a decidability proof and submits it to the kernel; it does not use
the native-evaluation route. Its arithmetic shares the same pinned Lean/Mathlib
runtime as the author's build. A separate Python transcription checked the
padding convention against the predecessor. None of these is human peer review.

The analytic cap-19 reduction, identification with unrestricted optimizer
values, and witness uniqueness remain outside the formalization. No new
analytic proof or global novelty determination is implied by this review.
