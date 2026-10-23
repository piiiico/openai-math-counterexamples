# Handoff: family 047 exact certificate

## State

- **Verified locally:**
  - both implementations;
  - 18 tests under normal and `-O` Python;
  - four negative controls under each, in both implementations;
  - 99% branch coverage;
  - one scoped AI review (see `REVIEW.md`).
- **Claimed** as [issue #17](https://github.com/piiiico/openai-math-counterexamples/issues/17)
  on piiiico/openai-math-counterexamples.
- **No PR opened.** By agreement with the author, the PR waits until one of the
  open PRs #12, #14 or #16 on that repository is resolved, or until the author
  approves earlier submission. The claim lapses after three days without an
  update, so post a status comment on issue #17 if submission slips past
  2026-10-24.

## Submitting

1. **Refresh.** Fetch destination `main` and reread `rows.tsv`, open issues and
   PRs. Confirm that nobody else has submitted a 047 check, and that the
   openai/math source hashes still match `source/SHA256SUMS`.
2. **Copy the packet into `rows/047/exact/`.** Follow the layout used by
   `rows/342/exact/`. Include `independent/`, `logs/`, `source/`,
   `output.txt`, `verification.json`, `PROOF.md`, `REVIEW.md` and `LICENSE`.
   Leave Pico's `rows/047/check.py` and `rows/047/output.txt` untouched.
3. **Extend row 047 in `rows.tsv`.** Append a supplement clause to
   `claim_checked` naming the deterministic certificate, the explicit Φ and q,
   the agreeing hash, the scope (A ≇ ℂ^[4] not computed), and this attribution:
   "Alexander Richard Towell, with Anthropic Claude". Add `queelius` to
   `agent`. Do not change Pico's result or output hash fields.
4. **Rebuild and rerun.** Run `python3 build.py`, then rerun `reproduce.sh`
   inside the copied directory. Record the refreshed pins in `submission.json`.
5. **Open the PR.** Use `PR-BODY.md` and link issue #17.

## Open items

- **End-to-end composite.** The composite on the five explicit coordinates
  Φ⁻¹(p), …, Φ⁻¹(e₀) is unfinished. It is optional.
- **Statement fidelity against OpenAI's Lean formalization** (`lean/docs/047.md`)
  is out of scope here. The destination routes Lean fidelity to MathVet.
