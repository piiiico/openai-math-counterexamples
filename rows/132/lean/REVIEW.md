# Focused AI statement review

A separately tasked OpenAI Codex reviewer read Proof.lean and Controls.lean
against predecessor PROOF.md and source/01-construction.tex on 2026-11-15.
It did not independently run Lean. This is AI review, not human peer review.

No blocking issue was found in the concrete XOR-size label, induced tournament
assumptions, incoming-label definition, arbitrary-size induction, or empty and
zero-bit cases. The reviewer checked that size(k-1) describes ceil(log₂ k)
for positive k; this identification remains prose, not a formal log theorem.

One wording improvement was applied: incoming-label witnesses in the formal
API range over natural numbers. Equivalence to the manuscript's bounded palette
requires a nonempty palette containing all edge labels. The README and theorem
comment now say so. Bounded witnesses imply unrestricted witnesses directly.

A follow-up review checked source_bad_card_le after its addition. It confirmed
that the one-based vertex lower bound makes i↦i−1 injective, the inverse shift
restores the vertices, the transported relation preserves hypotheses, and the
image has the same cardinality. No blocker was found. The source bridge was
then included in the full recompilation and axiom audit.

Remaining scope exclusions: parameter substitution, recurrence interfaces,
full separation theorem, all-h sharpness, novelty, and upstream acceptance.
