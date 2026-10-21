# A matching repair for the ordered binary matrix construction

**Written finding:** zeroing the dummy-row × shared-leaf-column block makes
OpenAI's host H-free with exactly m² edits, for every h>=1 and m=2^h. All
anchor-incident entries stay fixed. The argument checks that anchor rigidity
survives this particular edit, then rules out every possible body mode.

Combining this upper bound with the source's separate all-edits lower bound
would give exact minimum m² and normalized distance 1/(386h+2)². That equality
inherits the source lower bound; it is not established by a finite replay.
The source supplied the removal counterexample; no new counterexample or
exhaustive novelty assessment is claimed. Read [PROOF.md](PROOF.md).

**Independent finite result:** at h=1, every fixed-anchor repair with at most
three edits fails and an explicit four-edit repair succeeds. This conclusion
does not assume the source's distance lower bound. A written density argument
proves that all allowed repairs of the full 776×776 host are faithfully
represented by the 8×8 non-anchor model. It avoids assuming that arbitrary
edits preserve dummy-row twins.

## Reproduce

Python 3.13.15, standard library only:

```sh
bash reproduce.sh
```

Expected exit 0: sixteen unit/integration tests in normal and optimized Python,
25 RUP additions replayed, all 43,745 repairs with 0 through 3 edits exhausted,
a valid four-edit witness, and all four deliberate mutations rejected.
Individual entry points:

```sh
python3 repair.py
python3 independent.py
python3 -O repair.py --negative-control weaken
python3 -O independent.py --negative-control
```

The first two exit 0; the last two must exit 1. Primary controls also include
`truncate` and `witness`. The independent control pre-applies one genuine
repair edit and correctly finds a repair with three remaining edits. The
constraint weakening has an explicit two-edit satisfying witness, so its
rejection is more than an input-hash test.

The exact lower-bound CNF has 314 variables and 981 clauses: 64 cell variables,
48 body constraints, and a fully constrained prefix-count circuit excluding
more than three edits. The saved 25-step RUP proof is checked from scratch
without a solver. The independently derived bitmask enumerator imports
neither the primary model nor its certificate. Its domain consists of every
subset of the 64 editable cells of size 0,1,2,3, in lexicographic order, with no
random seed and a completion stopping rule (43,745 cases). The four witness
cell indices in row-major, zero-based order are 52,53,60,61.

Optional regeneration and coverage:

```sh
uv run --with python-sat==1.8.dev24 python generate.py
uv tool run --from coverage==7.10.7 coverage run --branch --source=repair,independent -m unittest discover -s .
uv tool run --from coverage==7.10.7 coverage report -m
```

Generation uses Glucose 4; its result is verified before writing. Solver proof
deletions are ignored soundly, retaining only already-proved clauses. The
finite checker and tests also check the proposed repair at depths 1,2,3; these
finite instances corroborate rather than prove the written all-depth claim.

## Pins, independence, attribution and scope

OpenAI source commit `1581d4cbdd69a0faf34b2089614fe2a814316a6a`:
`preprints/Polynomial-removal-fails-for-ordered-binary-matrices-September-25-2026/build/sections/`.
Read `02-construction.tex` for the exact host/roles, `03-pinning.tex` for
rigidity, `03b-count.tex` for body localization and the hitting-set warning,
and `04-distance.tex` for the inherited lower bound. Exact file hashes are
in `source-pins.json`; original sources and Apache-2.0 notices are included.
Counterexamples base: `f3e88206eb0c1ca065eb7106e06602d1aaa4c25b`.
Workspace base: `f41b85951b4d45596f09b9c4914323aa6d5eed13`.
[Coordination claim](https://github.com/piiiico/openai-math-counterexamples/issues/15).

The primary model was derived before inspecting Pico's implementation. A
separately tasked AI reviewer compared all 64 original entries, all 48 ordered
bodies and all 8 original bodies against that implementation, with exact
agreement. Its pinned checker hash is recorded, but its code is not copied.
The original leaf-diagonal hitting set uses two edits and creates eight new
bodies, providing a meaningful non-repair control.

Credit **OpenAI** for the construction, lower bound and pinning mechanism,
and **Pico / Håkon Åmdal** for the prior finite replay. **Alexander Richard
Towell** (ORCID 0000-0001-6443-9897) contributed with substantial **OpenAI Codex**
assistance in derivation, code, tests, writing and one scoped separate AI
review; that reviewer also supplied the independent exhaustive checker.
Original contribution code/prose are MIT; included OpenAI source is Apache-2.0.

The all-depth repair is a written proof. The h=1 result is exact finite
computation plus a written model-to-host bridge. Neither is a Lean/kernel
proof or human peer review. The source includes Lean lower-bound files;
they were inspected for overlap, not rebuilt here. AI review, repository
acceptance, archival publication and novelty assessment are separate events.
