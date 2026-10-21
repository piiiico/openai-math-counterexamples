# Visit log: family 047 exact certificate (first Claude pilot)

All times are UTC on 2026-10-21 unless marked. Agent: Claude Code (Opus 5.5),
working with Alexander Richard Towell.

## Selection (before 22:54)

- Read `piiiico/openai-math-counterexamples` at `f3e88206…` (AGENTS.md,
  CONTRIBUTING.md, rows.tsv, census.tsv, issues and PRs). The destination's own
  priority list asks first for second implementations of rows only Pico has
  checked: 047, 059, 088, 100 and 172. The workspace already has supplements
  for 049, 190 and 342.
- **Not chosen:**
  - **059** is already exact (sieve valuations).
  - **088** is already exact by an independent zonotope route.
  - **172** has exact ℚ(t) and dual-number checks, and Codex rejected it on
    10-21.
  - **100**'s area is a float `fsum`, numerically sound but not rigorous, and
    its coverage is sampled. However, OpenAI's Lean formalization covers the
    theorem, and `rpinho/tetrahedron-cylinder-cover` certifies a larger saving
    with a different cover. Its marginal value is moderate.
- **Chosen:** 047. Row 047 decides its identities by Schwartz–Zippel at five
  random points, and leaves local nilpotency to the proof. A deterministic
  certificate is a qualitative upgrade. The user approved A, with the policy
  "claim now, PR later", because PRs #12, #14 and #16 are still open.

## Work

- **22:54** Worktree `research/family047-exact-identities-20261021` at
  `130334c`.
- **Feasibility probe** (scratch `probe.py`, standard library). Term counts:
  H has 45 terms; H(L*) 266; H(L*+p³E) 381; e₀ 187. Round trip 1 closed
  exactly. W(e₀) − w has 19,859 terms and is an exact ℤ-multiple of
  H + p³w with no extra power of p: the quotient has 6,641 terms, and the run
  took about 2 s. So the domain-based cancellation can be replaced by a
  certificate.
- **Claim** posted as [issue #17](https://github.com/piiiico/openai-math-counterexamples/issues/17).
  Source hashes match row 047's pins.
- **`check.py` written.** It has 16 checks: the manuscript identities, plus
  Φ = exp(±wΔ) on generators with exact factorial division, both Φ
  composites, Φ(H), and both T round trips.
- **Independent implementation.** A separate agent was given only the two
  manuscript files and wrote a SymPy 1.14.0 `ring` checker (25 checks). It
  found no false identity and agrees on every term count.
- **Hash comparison.** The first hashes of q differed only because the two
  scripts serialized q differently. After `check.py` adopted the documented
  `[[[e_p,e_s,e_u,e_M,e_L,e_w],c],…]` format, both give
  `a74adf01…f6`.

## Mistakes caught and fixed

- **Count guard.** `check.py` first required 15 checks while emitting 16, so
  the first run printed `RESULT: fails`. The constant is now `EXPECTED_CHECKS`,
  and a test ties it to the emitted checks.
- **A garbled test.** One draft unit test for non-integral factorial division
  was garbled. It was replaced by two clear tests (non-nilpotent; 1/2! not
  integral) before the first test run.
- **Nondeterministic output.** `output.txt` first contained the runtime, which
  would have broken the destination's output-SHA-256 convention. The runtime
  now goes to stderr. Normal and `-O` stdout are byte-identical.
- **Untested early exits.** Coverage found three early-exit branches. Tests
  now cover them: the exponential limit, the non-integral Φ path, and a
  missing Q₁. Branch coverage is 99%.

## Review round (about 23:12–23:35)

- **The review:** a separate reviewer agent found no mathematical gap. It
  reported five should-fix items and nine nits, all fixed (see `REVIEW.md`).
  The main ones:
  - the scope was narrowed, and an H mod p check added;
  - the specification given to the independent agent is now disclosed;
  - q's hash is pinned in `check.py`;
  - a new `linear-inverse` control propagates to six checks.
- **Independent-side fixes:** the independent implementation's own fixes were
  sent back to its author agent, which made them without opening `check.py`.
- **A bug in my own fix:** the first `INDEPENDENT=1` reproduction failed with
  exit status 2. My new shell helper passed `--negative-control` before the
  script path. After fixing the argument order, the full two-implementation
  reproduction passes.

## Not completed

- **End-to-end composite.** I tried to compute the composite
  A[w] → ℤ[p,s,u,M,E] on the five explicit coordinates Φ⁻¹(p), …, Φ⁻¹(e₀)
  with the standard-library engine (scratch `e2e.py`). It printed nothing in
  several minutes, and I stopped it at about 23:10. The step-by-step
  certificate makes it unnecessary. A faster engine (SymPy or FLINT) could
  attempt it later.

## Pilot observations

- **What helped:**
  - **Pricing first.** The two-minute probe ruled out the main risk,
    expression swell, before the claim went out.
  - **Real independence.** The second implementation was delegated to an
    agent that never saw `check.py`, and it was then cross-checked by hash.
  - **Second-guessing the reports.** I reran the agent's claimed results
    (output reproducibility, all eight control exits) instead of trusting its
    report.
- **What went wrong:** the four mistakes above. Each was caught by running the
  checks, not by inspection.
