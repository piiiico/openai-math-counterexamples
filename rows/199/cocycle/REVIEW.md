# Separate AI review

Date: 2026-10-23. Reviewer: separately tasked OpenAI Codex agent,
`family199_cocycle_review`. This is AI mathematical/code review, not human
peer review or kernel verification. No additional reviewer was dispatched.

**Verdict: ready for the stated finite audit; no unresolved correctness
blocker.** The reviewer read the pinned sources, data, checker, tests,
README and proof note. Pico's checker was not inspected. The reviewer
did not modify the shared worktree; its temporary independent implementation
was subsequently copied into this packet as `review_oracle.py`.

## Independent evidence

- All 179 cochain entries were manually retranscribed from
  `sources/09-cochain.tex:19–38` and compared exactly with `data.json`.
  The twelve base products, basis, corners, grading and nine-letter z
  support also match the manuscript.
- A second polynomial implementation uses binary integers for F₂[q]
  coefficients and pushes each nonzero cochain contribution into a sparse
  differential coefficient table. It imports no main-checker code. Every
  differential coefficient is zero. A separate expansion by H degree
  checks the boundary identity on all 324 pairs.
- The hand check (u,N) confirms the inverse twist: uN=(1+q)T; four qHT
  terms cancel on the left, leaving (q+q²)T. The right side is
  z(u)h⁻¹(N)=qHu·H⁻¹N=(q+q²)T.
- The reviewer reran the main complete check, all 22 final tests, and all
  three main controls in normal and optimized Python. It checked all four
  source snapshots against their recorded lengths and SHA-256 hashes.
- Its independent oracle also passes in both modes; changing p(t,y,J) to
  q²f fails with coefficient (q²+q³)F at (F,t,y,J), exit 1.

Oracle SHA-256:
`e71929e5a983d90b06785bf1e80d9005a4c56f0fa37b39ce078c39909a172b99`.
Run `python review_oracle.py` or `python -O review_oracle.py`; add
`--mutate cochain` for the deliberately failing control.

## Mathematical assessment

Dual actions and reversed corners match the source. Full basis enumeration
and the verified endpoint/weight conditions support the stated multilinear
extension. The Laurent-polynomial boundary calculation retains H⁻¹ correctly.
The displayed bar differential cancels and evaluation gives q³f. After
extension to the source field, the standard relative-bar resolution and
cycle-pairing argument justify the nonzero evaluated degree-three class.
No all-degree Ext computation follows from this alone.

## Findings and disposition

1. **Important, resolved:** a prose revision dropped a negation from the
   exclusions. The final note explicitly says the later explicit resolution,
   all-degree vanishing, cone/lift steps and full counterexample are not checked.
2. **Minor, resolved:** the semisimplicity paragraph now explicitly changes
   scalars from R to k=F₂(q,H₁,H₂) and Iₖ=ke⊕kf.
3. **Minor, resolved:** inaccurate source line ranges in the checker docstring
   were corrected against the pinned file.
4. **Nonblocking limitation:** coverage is 224/226 statements and 84/86
   branches. The final cycle-boundary/evaluation rejection raises were not
   exercised after all earlier checks passed. Positive cycle behavior and
   the zero-cochain vacuity control were exercised separately.

The reviewer declined to assess the later construction, global novelty,
publication acceptance, human review or formal proof status. Remaining trust
includes source identification, the two reviewed implementations, Python
execution, and the written relative-bar argument.
