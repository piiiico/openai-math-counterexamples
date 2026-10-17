# Bounded experiment record

- Start: 2026-10-17 10:37:43 UTC. Target deadline: 11:22:43 UTC.
  Verification and handoff reserved from 11:07:43 UTC. No automatic continuation.
- Selected task: quantify the finite-input transfer of the completed fixed
  Gaussian schedule. The source already factors Q and transfers restricted
  moments qualitatively. Merely repeating that argument would not be new.
- Proposed candidate before implementation: N=2^512 signs per input, tail
  truncation R=16, inherited m=2^24+1, T=8, c=3/8, r=2^-33.
  The optimistic budget counts every sign and every report-cell block.
- At 10:42:13 UTC the exact rational feasibility calculation gave a lower
  gain ratio above 0.026467562004, exceeding 1/50. This passed the ten-minute
  feasibility gate. No search over block sizes was performed or needed.
- The written proof handles all selector cells through the CDF error, all
  leaf means through restricted moments, and both tails through a truncated
  moment comparison plus a proved subgaussian bound. No enormous-N sample or
  binomial enumeration was run.
- The first CLI acceptance test failed before the checker existed and passed
  after implementation. Further tests cover schema and pin failures, positive
  denominator failure, insufficient tail cutoffs, and four inadequate budgets.
- The exact identity was tested on complete weighted small-binomial domains,
  including parameters with negative predictor gain. Deliberately
  changing its coefficient fails. A failed sufficient budget is not a
  counterexample to the underlying finite construction.
- One separate AI review found no blocker and supplied an independent Arb
  replay. Final verification and the publication receipt are recorded separately.

Outcome: an explicit sufficient finite-input count and a quantitative error
budget for one observation stage. Remaining stages are amplification and final
Boolean readout. No claim of optimal N, complete Boolean witness, human review,
or global novelty. No evidence-driven pivot was necessary.
