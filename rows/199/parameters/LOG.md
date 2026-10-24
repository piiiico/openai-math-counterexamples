# Bounded audit log

Alexander Richard Towell, with substantial OpenAI Codex assistance.

- Conservative start anchor 2026-10-23 22:10 UTC; exact recovered clock at
  22:15:59. Deadline 23:10; verification begins by 22:55. The earlier
  orientation timestamp was unavailable after compaction, so elapsed time
  uses a conservative anchor rather than pretending it was measured exactly.
- By 22:18: inspected source Lean Resolution.lean and Parameters.lean. Generic
  sufficiency is already formalized. No open destination issues/PRs overlap.
  Claim24 narrows the contribution to exceptional parameters and exact replay.
- Coordinate attempt: the right-map coefficient 1+q^(i+2) identifies t cycles
  and missing j boundaries. This yields first failure d-1 at order d>1 and
  augmentation failure at q=1. At q=0 no right coefficient vanishes.
- Dual attempt: left multiplication loses its z-producing x/y coefficient
  for i>=1 at q=0, yielding two-dimensional Ext in all degrees >=2. The
  original generic dual profile cannot simply be specialized. No pivot needed.
- By 22:23: production replay passes all 30 q in F2,F4,F8,F16 through degree
  2(|k|-1)+2, totaling710 degrees per complex. All cycle representatives and
  image/kernel spaces are checked, not only ranks.
- Review: one separately tasked reviewer finds no mathematical blocker and
  corroborates526 degree cases by restriction to F2 and XOR elimination.
  The reviewer notes grading positivity/maximality was implicit; explicit
  source-data checks are added. The final suite has12 tests under normal/-O.
- Verification from22:24: full reproduction, source readback and code coverage.
  Readback detects one extra trailing newline in three copied sources; raw
  pinned bytes restore exact copies and source hashes. Reproduction passes
  after this correction. No mathematical claim changed.
- Rejected controls: modified ty breaks associativity; demanding exactness at
  a nontrivial root and demanding the generic dual profile at q=0 both fail.
  These are tests of deliberately false claims, not defects in the source.
- Publication and final closeout are recorded separately in HANDOFF.md and
  submission/publication receipts. No further research cycle is authorized here.
