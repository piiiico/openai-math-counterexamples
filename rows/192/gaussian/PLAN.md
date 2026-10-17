# Family 192: explicit finite Gaussian gain

Alexander Richard Towell, with substantial OpenAI Codex assistance.

Start: 2026-10-17T08:04:18Z. Target deadline: 08:49:18Z.
Verification/handoff reserved from 08:34:18Z. Maximum extension to 09:04:18Z
only for a concrete, checkable advance and an imminent milestone. One visit.
Archive base: 4cac5b0c97ab608c21c889a3b240f7465513d6a3.
Branch: research/family192-gaussian-20261017; isolated existing managed worktree.

## Target and scope

Specify a finite grid, positive interval radius, selector, and predictor for
Family 192's coarse reporting rule, and prove a strictly positive Gaussian
retained-variance gain by rigorous arithmetic. Preserve the distinction
between this Gaussian intermediate construction and an explicit Boolean
counterexample. Full averaging counts, amplification and Boolean readout are
outside the target. No new asymptotic theorem or minimality is claimed.

Current source: openai/math 1581d4cbdd69a0faf34b2089614fe2a814316a6a,
preprints/Unbounded-Violations-of-the-Square-Root-Degree-Bound-September-26-2026/
build/sections/{01-observations,02-reporting,03-alternatives,06-small-width}.tex.
Section 02 is unchanged from earlier pin fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb.
Destination: piiiico/openai-math-counterexamples, base
dbd2e8f440ac8f4a7fe4a4b6515a9d95065eceb7. Its Family 192 row only checks small
Boolean dimensions and remains not-explicit. No open issue or PR was present
at initial refresh. Follow its required family claim before substantial work.

## Three candidates and decision

1. Instantiate the main proof's shift-one, large-m schedule literally.
   Its coarse estimates have severe exponential cutoff penalties.
2. Certify every cell in the source's small-width schedule, using exact
   Gaussian restricted moments. This may need a very large cell list.
3. Keep the same coarse reporting rule, use a smaller rational shift c,
   and certify uniform bounds for an explicit dyadic grid. The gain becomes
   Q(c^2-J_c), derived independently from the reporting partition. A few
   scalar inequalities cover all cells, avoiding a large enumeration.

Choose (3). This changes the explicit parameter schedule and predictor,
not the reporting rule or its coordinate-cost argument. Initial floating
cost probe (not a certificate) examined m=2^k+1 for k=20,...,25 at cutoff 8,
shift 3/8, and dyadic radii near h/(2 sqrt(m)). k=24 had a favorable lower
margin about .0267. The concrete first candidate has m=16777217, spacing
2^-20, radius 2^-33. The intervals are enormous in number and their product
probability is tiny; practical Boolean construction is not implied.

## Method, success and stopping

Derive the complete predictor deficit, including both exceptional reports,
ordinary reports, all Gaussian tails, conditional means and variances, and
the finite-input coordinate cost. Bound J_c centrally by a density ratio and
in the tails by Gaussian integration by parts. Verify the resulting scalar
inequalities with exact rational Taylor bounds for exp, and use an independent
Arb implementation/reviewer where helpful. Bound every interval probability
uniformly below so positivity is quantitative without multiplying millions
of tiny numbers. No new analytic source theorem is assumed as a black box.

Success: a written sufficient-condition proof and exact certificate of a
positive gain, with changed-parameter controls and a reproducible command.
A failed sufficient bound is inconclusive about the actual gadget. Stop if
the bridge fails, no affordable rigorous certificate emerges by 08:34:18,
or distinctness from current work disappears. Permit one evidence-driven
pivot only. Do not increase small-Boolean brute force or claim a full finite
Boolean witness. At most one separate reviewer, confined to this claim.

Publication: one focused PR only if the arithmetic, proof scope, review and
destination checks are complete. Leave Family 192's overall not-explicit
classification unchanged. Otherwise preserve a clean local packet and exact
blocker. Update the required claim once with the result.
