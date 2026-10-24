# Family 199 parameter audit handoff

The written classification identifies exactly when the displayed seed complex
is a resolution: q=0 or infinite multiplicative order. Nontrivial root order d
first fails at degree d-1; q=1 already fails at the augmentation. The q=0
resolution has two-dimensional Ext(s,C) in every degree >=2. This explains a
specific obstruction to naive finite-field specialization, without excluding
alternative constructions or contradicting the source's transcendental case.

Reproduce from this directory: `python reproduce.py`. Expected final line:
`RESULT: Family 199 parameter strata, independent oracle and rejecting controls reproduced`.
The full finite domain, source pins,12 tests, negative controls, separate AI
review and its distinct binary-matrix oracle are in README.md/verification.json.
This is not a Lean proof, human peer review, or a check of the full theorem.

Workspace base31da1d2681f926e3b921520302f9c21184c5c97e;
OpenAI source1581d4cbdd69a0faf34b2089614fe2a814316a6a.
Upstream baseb19a1429ece4c35026b789b519ff219bc57b9bc5. Earlier evidence packets
and their archived files are unchanged. Canonical curation uses the existing
`family199-cocycle-interface` record at
https://github.com/queelius/research-records/tree/main/records/family199-cocycle-interface.
The earlier DOI10.5281/zenodo.23597123 does not contain this new audit.

Publication readiness: complete and computationally reviewable; prepared for
one focused supplement PR under claim24. The status in this file is a prepared
snapshot; subsequent submission/archive receipts in the owning project record
actual publication, review and dates. Do not infer acceptance from local checks.

Next action after submission: respond to substantive feedback. Do not repeat
finite-field sweeps to infer an unrestricted theorem; the remaining opportunity
would be a focused Lean exceptional-parameter lemma or a genuinely different
seed mechanism. Stop this bounded audit without launching either task.

Credit Alexander Richard Towell and OpenAI's source construction; substantial
OpenAI Codex assistance and the precise AI review scope are disclosed in NOTICE.md.
