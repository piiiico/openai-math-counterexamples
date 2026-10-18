# Family 156: independent finite ten-label obstruction certificate

Alexander Richard Towell, with substantial OpenAI Codex assistance.

The last combinatorial step of the claimed nine-dimensional Borsuk
counterexample has a small independently replayable certificate. A direct
encoding of the source's `TenSystem` conditions has **330 Boolean variables
and 31,201 clauses**. A **327-clause RUP refutation** excludes every nonempty
ten-label system obeying them. Replay requires only Python's standard library.

This checks a finite step currently outside the census's metric computation.
OpenAI already provides both a written proof and a Lean finite-case development;
this is independent computational corroboration, not a new theorem or a
missing-proof claim. The topology linking these conditions to a cover, the
full Borsuk theorem, and a finite Euclidean counterexample remain outside the
check. We did not rebuild OpenAI's Lean project.

## Reproduce

From this directory, Python 3.10.20, standard library only:

```sh
python3 checker.py --finite-controls
python3 independent_check.py
python3 review_controls.py
python3 -m unittest discover -s . -v
python3 -O checker.py --negative-control false-clause
```

The first exits zero with
`RESULT: certified finite ten-label obstruction`.
The separate bitmask encoder and full-scan replay check the same 327 additions
without importing the primary encoder or propagation engine. The exhaustive
two-variable control compares 8,192 propagation cases with truth tables.
All fifteen unit/integration tests pass. Recorded combined statement/branch
coverage is 91%; [coverage.txt](coverage.txt) lists the unexercised paths,
mostly defensive checks. Coverage is an implementation diagnostic, not a
mathematical guarantee.
The negative command must exit one. Other rejecting modes are `truncated`,
`empty-family`, `simplex-boundary`, and `six-system`. The two weakened-formula
controls have explicit satisfying assignments; their rejection of the original
refutation is not merely a failed solver search.

The optional finite controls exhaust all 1,024 complementary-triple choices
on six labels. Exactly twelve satisfy the axioms; all the source's four local
properties pass. All 720 relabellings form one orbit with sixty automorphisms.
The full ten-label refutation does not assume this classification.

Optional regeneration, separate from verification:

```sh
python3 -m pip install -r requirements-generation.txt
python3 generate.py
python3 checker.py --finite-controls
```

Generation uses `python-sat==1.9.dev6` and Glucose 4. Its exact heuristics are
not trusted: every saved added clause must independently pass RUP replay.
No solver is imported by the entry command. Regeneration replaces the local
certificate and generation receipt; replay alone preserves all files.

## Why the encoding matches the claim

Each variable denotes membership of a triple or tetrahedron. The clauses
express downward closure, purity, absence of boundary triangles, complementary
triple selection, and exact pair counts on every facet complement. They do not
assume the manuscript's later short-link or partner-block conclusions. The
only symmetry choice fixes one tetrahedron, justified by relabelling any
nonempty family. [PROOF.md](PROOF.md) gives the full encoding and replay argument.

The complete finite Boolean domain is certified; there is no random sampling
or unsuccessful-search inference. Tests, meaningful corrupted/relaxed inputs,
and separate AI review check the implementation and interpretation. The
certificate is not a Lean proof and AI review is not human peer review.

Source: `openai/math@1581d4cbdd69a0faf34b2089614fe2a814316a6a`, especially
`six-labels.tex`, `ten-labels.tex` and `TenLabels/Labels.lean`.
The manuscript's `ten-labels.tex:177-179` states, “There is no admissible map
RP³ → Δ⁹.” This package checks only the finite obstruction used in that proof:
the six fields of `TenLabels/Labels.lean:13-22`, with a nonempty tetrahedron
family. [PROOF.md](PROOF.md) states the exact proposition and its encoding.
[source-pins.json](source-pins.json) records exact hashes and overlap scope.
The [coordination claim](https://github.com/piiiico/openai-math-counterexamples/issues/9)
identifies this independent check. The destination is the counterexample census;
its existing metric checker and `not-finite` classification are preserved.

Credit OpenAI for the construction and prior written/formal finite proof,
Pico/Håkon Åmdal for the census and metric checker, and the Glucose/PySAT authors
for optional certificate generation. The independent code/prose are MIT
licensed. Substantial OpenAI Codex assistance and review are disclosed above.
The [DRAT/RUP documentation](https://www.cs.utexas.edu/~marijn/drat-trim/)
describes the certificate principle; no DRAT checker code was copied.
