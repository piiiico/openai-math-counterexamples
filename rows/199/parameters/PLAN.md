# Seed-resolution parameter audit

Alexander Richard Towell, with substantial OpenAI Codex assistance.

Conservative timing anchor: 2026-10-23T22:10:00Z, including orientation.
First recovered clock reading: 22:15:59Z. Hard stop: 23:10:00Z;
verification and handoff begin no later than 22:55:00Z. No further cycle.
Workspace base: `31da1d2681f926e3b921520302f9c21184c5c97e`.
Isolated branch: `research/family199-parameters-20261023`.

## Proposition and purpose

Over any field of characteristic two, specialize the ten-dimensional algebra
table C at q. Classify exactness of the displayed augmented complex
R_0=Cf, R_i=Ce (i>0), d_1=(right u), d_(i+2)=(right x+q^i y).
Hypothesis: exactness holds precisely when q=0 or q has infinite multiplicative
order. For a nontrivial root of order d, the first failure is degree d-1;
q=1 already fails at the augmentation kernel. At q=0 the resolution remains
exact but the asserted dual Ext concentration changes. This identifies limits
of a naive specialization, not an error in the transcendental source theorem.

## Dependencies and overlap

Source: openai/math@1581d4cbdd69a0faf34b2089614fe2a814316a6a,
03-algebra.tex and 04-resolution.tex, Lemma res:base. Preserve earlier packets.
Existing Lean Resolutions/Resolution.lean already gives multiplication formulas
and sufficient nonvanishing conditions over general characteristic-two fields.
Parameters.lean obtains these conditions for the source fraction field. New
scope is the exceptional homology classification and independent exact replay.
No open issues or PRs in the counterexample destination at 22:18 UTC.

## Method, success, and stop

Derive all kernels/images by coordinates before inferring all-degree results.
Implement a separate binary-polynomial finite-field and matrix checker using
the source table as structured data. Exhaust q in fields of sizes 2,4,8,16
through two periods plus endpoints; compare actual kernels, images and homology
representatives. Check polynomial associativity and formula identities directly.
Use negative controls for an incorrect generic profile and a mutated product.
One focused reviewer checks mathematical meaning and hidden assumptions.

Success: a written uniform classification plus exact finite evidence, rejecting
controls and scoped review. Computation alone is not a universal proof. Do not
compute Ext with a nonexact complex. Do not infer impossibility of alternative
resolutions or the full counterexample over finite fields. Lean is optional only
if already practical; do not rebuild the large source project this visit.
Stop on overlap, an unresolved mathematical obstruction, or the deadline.
Publish at most one focused computation PR if distinct and fully verified;
otherwise preserve the exact blocker and a clean handoff.
