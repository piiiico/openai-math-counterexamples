# Bounded experiment record

- Started2026-10-17 11:03:21 UTC. Deadline11:48:21, reserved verification from11:33:21.
- No substantive PR6 feedback, source change or competing repository claim was
  observed. The source already has qualitative amplification/readout; the
  inspected comparator main theorem contains `sorry`. No kernel proof is assumed.
- Compared raw-score subgaussian propagation, a Wasserstein approach, and a
  bounded-score fourth-moment approach. Selected the third because it gives
  explicit uniform tails with the same per-interval CDF mechanism.
- Before implementation, declared M(n)=2^512 n^2, R=2^64 and the complete
  sign/degree recurrences in PLAN.md and the coordination continuation.
- Exact feasibility passed at11:11 UTC, before the ten-minute gate: gain/Q
  lower bound0.026467562004>1/50. No optimization search over copy counts or
  Gaussian schedules was performed. The one prescribed candidate succeeded.
- First acceptance test failed before the checker existed, then passed.
  Small-domain tests failed before finite_controls.py existed, then all passed.
- Derived the explicit stage exponent and closed-form counts. Replaced the
  final qualitative readout limit by a direct fourth-moment/Hölder bound.
- Found an actual scoped negative result: for the all-positive indicator on
  four signs, v=16/15 and E|score|=1/2, so one-copy normalized readout need not
  exceed1/2. The prescribed n^2 copies pass. This is not a counterexample to
  the source, which permits additional copies.
- One separate AI review found no mathematical blocker and requested the
  explicit deterministic-map/no-external-randomness clarification, applied.
  Its independent Arb and asymmetric-law replay is archived and rerun.

No evidence-driven pivot was needed. Insufficient-budget controls are failures
of sufficient estimates, not impossibility theorems. The symbolic k and target
truth table were never expanded. Final checks and publication are recorded
separately. No new research cycle starts automatically.
