# Scoped independent AI review

A separately tasked OpenAI Codex code-reviewer agent reviewed the source
statement, checker, tests, pins, and written soundness argument on 2026-10-23.
It had read-only access and did not edit the packet. This is AI review, not
human peer review or kernel verification.

## Verdict

No blocking or important defect found. The reviewer confirmed:

- All six signed factors reproduce the two source ratios.
- Admissibility, implicit zero coefficients and positive E match the lemma.
- GCD rewrites preserve both products; the stored basis is pairwise coprime.
- The positive-integer measure decreases on every split, proving termination.
- Empty residuals certify the identities; nonempty residuals detect failure.
- Exact metadata, malformed inputs and source-hash changes are checked.
- Unverified generation provenance and downstream topology are excluded.

Reviewed checker SHA-256:
`18bc2730b2110e6ea2d868c6bbaa2bd8c3a9a1c1b5db0c21410f5ca8fdf5d8f2`.
The full witness passed; all 22 tests passed under optimized Python, and all
five optimized CLI controls rejected for the expected reasons.

## Independent finite oracle

The reviewer independently wrote a direct-integer-power/rational-normalization
oracle and exhausted 729,000 cases: three ordered bases in 1..10, with each of
the six exponent components in {-1,0,1}. Every case preserved both rational
products, agreed on acceptance, and had pairwise-coprime nonunit/nonzero
residuals. This is exhaustive only in the stated small domain.

The supplied oracle is preserved, with formatting and variable-name cleanup,
in `review_oracle.py` and rerun by the coordinator. Reproduce it with:

```sh
python3 -O review_oracle.py
```

Expected exit 0 and `Independent exhaustive direct-rational checks passed: 729000`.
This calls the checker under test and compares with a different oracle; it is
not a second complete verifier of the original 849-row source witness.

The reviewer could not run coverage in its system Python environment; the
coordinator's separate pinned coverage run is recorded in `verification.json`.
