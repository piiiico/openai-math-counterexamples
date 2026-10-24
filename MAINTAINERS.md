# Maintainers

- **Pico** (AI agent, operated by Håkon Åmdal). Owner. Re-runs every row before merge.
- **Alexander Richard Towell** ([`queelius`](https://github.com/queelius), [metafunctor.com](https://metafunctor.com)). Co-maintainer from 2026-10-24, scoped as below, working with OpenAI Codex assistance. Proposed in [#26](https://github.com/piiiico/openai-math-counterexamples/issues/26).

## Alex's remit (first term, 2026-10-24 to 2026-11-24)

1. Triage: check a new issue or PR for scope, overlap with an open claim, a full-sha source pin, source hashes, pinned dependencies and a negative control. Label, ask for what is missing, close what is out of scope (with the reason and where it belongs).
2. Reproducibility: setup instructions and cold-load problems, following #19.
3. Docs: the contributor summary in the README, the list of rows that still need a second implementation in AGENTS.md, CONTRIBUTING.md.
4. Review of computational contributions he is competent to judge. A review says how it was re-run and what it shares with the submission (code, method, dependencies).

## Rules for both of us

- `main` is protected: every change from a collaborator is a PR with one approving review from someone other than its author. Alex's own rows are re-run by Pico before merge; that does not change.
- A row merges only after a re-run on a clean checkout by someone who did not write it. A review that shares the submission's code or method says so, and does not count as an independent implementation.
- Nobody here judges a proof by reading it. A row is a computation with a stated scope, never a verdict on a theorem, and never "certified" or "peer reviewed".
- Nobody edits another contributor's row. Contest it with a second implementation.
- AI assistance is disclosed in every PR, as now.

## Review

On 2026-11-24 we look at what the month produced and either renew, widen, narrow or end the role. Either side can end it earlier with a comment on #26.
