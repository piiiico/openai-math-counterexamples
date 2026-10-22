# Family 156: a formal source-to-CNF bridge without downward closure

**Finding, 2026-10-21:** Lean verifies that any arbitrary subset-family `T` and
nonempty `Q` satisfying exactly five retained `TenSystem` fields induces a
satisfying assignment of an explicitly generated numeric CNF. A complete external
comparison identifies that formula with the accepted no-down certificate input:
**330 variables and 30,361 clauses**. This closes the forward reduction obligation;
the UNSAT certificate and its checking engines remain external.

This formalizes part of the evidence for Pico's prior down-omission observation.
It does not claim a new Borsuk theorem, independent discovery of that observation,
or a kernel-checked refutation. The original certificate packet is unchanged.

## Exact statement and source

Let `T,Q : Finset (Fin 10) → Prop`. `FiveFields T Q` retains these source fields:

- `tetra_card`: every member of `Q` has cardinality four.
- `pure`: every member of `T` is contained in some member of `Q`.
- `no_boundary`: every three-subset of a member of `Q` is contained in another
  member of `Q`, whether or not that subset belongs to `T`.
- `complementary`: for a three-subset `U` of the complement of `S ∈ Q`,
  `T U ↔ ¬ T (Sᶜ \ U)`.
- `pair_count`: for each two-subset `P` of that complement, exactly two remaining
  labels `w` satisfy `T (insert w P)`.

The sole additional premise is `∃ S, Q S`. There is no `down` field, fixed facet,
restriction of `T` to triples, geometric premise, or added computational oracle.
The source is `openai/math` at
`1581d4cbdd69a0faf34b2089614fe2a814316a6a`,
`lean/OAI/Geometry/Borsuk/TenLabels/Labels.lean:13–22`.
Its unchanged bytes and license are in `source/`; SHA-256:
`2edf8f16845c943113b43f34542a4bcdd26872910067b35d184c76915882ebb0`.

The main theorem is:

```lean
encoded_model_satisfies_cnf {T Q : Family}
    (h : FiveFields T Q) (hne : ∃ S, Q S) :
    EncodedSatisfies (encodedModel T Q) encodedCNF
```

`encoded_unsat_implies_no_source_model` is a corollary **conditional on an explicit
UNSAT hypothesis**. This packet does not prove that hypothesis in Lean.

## Proof and binding

`lean/Family156Bridge.lean` proves enumeration completeness for subsets of each
cardinality, translates every well-formed clause family from its corresponding
source field, and proves that numeric variable lookup recovers the source truth
value. Exactly-two-of-four supplies both three-positive and three-negative clauses.
The nonempty clause ranges over all 210 tetrahedra, without symmetry reduction.

The generator filters its raw obligations by explicit well-formedness conditions.
Fresh execution produced **30,361 raw = 30,361 retained obligations**. The binding
check compares the entire ordered variable table and clause **multiset**, preserving
multiplicities and allowing only clause/literal permutation. Thus the finite check
confirms that no clause was lost. The kernel proof alone does not establish the
numeric count or equality to the Python file.

The canonical CNF SHA-256 is
`78e2bd711ec1c60222bb2e2962669d7cc755da38e07a256f27b555e073987a10`.
The predecessor is commit `c714c0a27e1cb668d63c6aa7a8c373aab0f2f9d9`,
`rows/156/finite_obstruction`; its encoder, no-down driver, checker and certificate
hashes are enforced by `source-pins.json` before importing its encoder.
Its 18,302-addition certificate has SHA-256
`f98da2cbdc8584a180fee391e6a03dc8ee6367bd31828b22e6652e9b0fc4ddd1`.

## Reproduce

Requirements: Python standard library (tested with 3.13.15), elan/Lake, Lean
`v4.33.1`, and Mathlib `0df444a360eaa60ab8c11dca51a86af692955474`.
All transitive revisions are retained in `lean/lake-manifest.json`. On a fresh
checkout, enter `lean/` and run `lake exe cache get` to obtain pinned dependencies
and cached Mathlib artifacts. Do not run `lake update` or replace the pins.

From this directory in the public construction repository:

```sh
python3 check_lean_binding.py --packet-dir .. --run-lean
```

Expected: exit 0, both theorem axiom lists contain only
`propext`, `Classical.choice`, `Quot.sound`, the counts/hash above, and
`RESULT: exact source-to-CNF binding verified after fresh Lean build`.
The command recompiles the core before its consumers and creates a fresh export;
without `--run-lean` it checks only the bundled JSON.

### Cold Mathlib loads and timeouts

`check_lean_binding.py` gives each of its three Lean subprocesses a 120-second
wall-clock limit. A first Mathlib load on a slow disk can exceed this limit even
after `lake exe cache get`. In his
[independent AI rerun](https://github.com/piiiico/openai-math-counterexamples/pull/12#issuecomment-6343497809),
Pico reported 6 minutes 49 seconds for the first core compilation and successful
reproduction with each limit increased to 1,800 seconds.

If the command reports a timeout, use a disposable checkout and
change all three `timeout=120` arguments in `build_and_export` to `timeout=1800`,
then rerun the command above. Retain `--run-lean` so the retry still compiles the
proof and consumers, generates a fresh export, and checks the complete binding.
This workaround changes only the time allowance; record the local modification
and actual runtime with the rerun. A timeout alone gives no verdict on the proof.

In the owning math-research workspace, use
`--packet-dir ../family156_down_omission/packet/rows/156/finite_obstruction` instead.

```sh
FAMILY156_PACKET_DIR=.. python3 -m unittest -v test_binding
python3 -O check_lean_binding.py --packet-dir .. --negative-control drop-clause
python3 -O check_lean_binding.py --packet-dir .. --negative-control flip-literal
python3 -O check_lean_binding.py --packet-dir .. --negative-control swap-variables
```

All 17 unit/integration tests pass with the environment variable set. Each negative
command must exit **1**. Tests also reject wrong source hashes, wrong reference
hash, malformed variables/literals, duplicate replacement clauses, and filtering
losses. `Consumers.lean` checks the empty-family boundary: the five fields alone
allow empty families, so nonempty `Q` is essential.

An additional proof mutation removes `⟨false, .triangle U⟩ ::` from the `.pure U`
clause. Compiling the resulting core fails with an unsolved goal `False` under
`¬ T U`. Its captured diagnostic is retained in `logs/negative-controls.json`.
`output.txt`, `verification.json`, and `REVIEW.md` record the completed checks.

## Trust boundary and limitations

The theorem is kernel checked against the copied five-field definition, whose
fidelity was separately reviewed against the pinned original. The source's entire
Lean project was not rebuilt. JSON export execution, Python comparison, source
parsers, compiler execution, and cryptographic bindings are not kernel proofs.
The external certificate's soundness and its existing successful replays are
inherited evidence; this visit does not rerun the expensive complete refutation.
There is no reverse CNF-to-source theorem, full Borsuk result, geometry/topology
verification, global novelty assessment, or human peer review. The census remains
`not-finite` for its original full claim.

## Credit, license, and publication

Alexander Richard Towell (ORCID `0000-0001-6443-9897`), with substantial OpenAI
Codex assistance in proof development, code, checks, writing, and a separately
tasked AI review. AI review is not human peer review. Credit OpenAI for the source
definition and finite lemmas; Pico / Håkon Åmdal for the prior omission observation,
independent encoder and later drat-trim reproduction; the earlier Towell/Codex
certificate packet for the reused encoding; and Lean/Mathlib contributors.

`Family156Bridge.lean` adapts OpenAI definitions and elementary finite lemmas and is
Apache-2.0, with inherited license in `source/LICENSE`. The vendored original
`source/Labels.lean` has the same license. Other original files are MIT under
`LICENSE`. No additional license is asserted over dependencies.

The prior certificate is archived at
[10.5281/zenodo.23498223](https://doi.org/10.5281/zenodo.23498223).
That exact archive predates and does **not** contain this formal bridge. A future
archive should be a substantive new version in the same coherent record family,
with its own publication date. The public index is
[research-records](https://github.com/queelius/research-records/tree/main/records/family156-down-omission).
