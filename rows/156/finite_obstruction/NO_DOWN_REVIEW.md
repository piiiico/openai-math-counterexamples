# Scoped review of the down-omission certificate

2026-10-20. One separately tasked OpenAI Codex reviewer, with read-only scope.
This is AI review, not human peer review or proof-assistant verification.

The reviewer read the pinned Lean definition and verified its SHA-256,
the new written statement/CNF bridge, both new clause generators, the
unchanged predecessor checking engines, the proposed certificate, and the
explicit weakened models. No blocking issue was found.

The reviewer specifically checked:

- Restriction of the source's arbitrary subset-family T to triples, and
  extension back by false membership off triples.
- No-boundary's Q-only premise, without accidentally adding T(U).
- Omission of exactly `down`, and use of an unrestricted nonempty OR.
- Every clause against a fresh reconstruction of the source conditions:
  120 pure, 840 no-boundary, 4,200 complementary, 25,200 pair-count, and
  one nonempty clause.
- All 424 exhaustive local truth-table cases for the guarded clause forms.
- Eight targeted tests then available; independent immediate-empty and
  truncated controls rejected under optimized Python.
- Both explicit satisfying models and appropriate predecessor attribution.

The reconstruction reused the primary encoder's variable-to-subset mapping
and clause evaluator. It is an additional semantic audit, not a third fully
independent implementation. Translation of the Lean conditions was reviewed
manually, not formally verified.

The two local truth-table/reconstruction checks have been preserved as
`test_local_clause_truth_tables` and `test_source_driven_cnf_reconstruction`
in `test_no_down.py`, using unittest assertions that remain active under
optimized Python. They reproduce the review's finite audit offline. Source
hashes and the seven predecessor bindings are in `no_down_source_pins.json`.

Reviewed canonical CNF SHA-256:
`78e2bd711ec1c60222bb2e2962669d7cc755da38e07a256f27b555e073987a10`.
Reviewed certificate SHA-256:
`f98da2cbdc8584a180fee391e6a03dc8ee6367bd31828b22e6652e9b0fc4ddd1`.

The reviewer did not duplicate the full 18,302-step scan. Its completed
acceptance must be established by the separately recorded execution, not
inferred from this review. The reviewer did not audit topology, the
underlying geometry, or the complete source Lean project. Optional
regeneration and later test/packaging changes were checked by the primary
agent and are not represented as an additional independent review.
