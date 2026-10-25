# Independent finite Hankel seed certificate for Family 095

Alexander Richard Towell, with substantial OpenAI Codex assistance.

**Finding:** the printed modular calculation in Appendix A of *Hyperbolicity
Cones Without Semidefinite Lifts* is independently reproducible. No discrepancy
was found in the audited finite ingredient.

| Check over F7 | Result |
|---|---|
| Seed T on quadratic forms | rank 20 |
| Restriction to L | determinant 6 |
| Kernel J; orthogonal space H0 | dimensions 16; 28 |
| Pure kernel-product matrix G1 | rank 136 |
| Pure cubic product matrix G2 | rank 84 |
| Product matrix D | rank 302 |
| Bordered first-variation matrix | rank 623 = 2·302+19 |

All ten weight blocks agree at the **same printed point and tangent**.
The checker reproduces all 24 displayed determinant values, every corner
entry, and six direct bordered determinants: 5, 5, 6, 2, 4, 4. It also verifies
the full kernel, tangency and differentiated basis equations, not just the
selected pivot equations. Quadratic and weight-zero quartic orders are checked
against the printed lists. No tenth root of unity in F7 is required: the source
moment formula defines the modular matrices directly.

## Scope and meaning

This checks a finite ingredient of the October 5 nonliftability manuscript,
not the earlier nonspectrahedral example or its separate semidefinite lift.
The characteristic-zero lifting, simultaneous real-form/genericity argument,
real positive semidefinite deformation and final no-lift proof are not checked.
The repository's overall `not-finite` classification should remain unchanged.
There is no new nonliftability theorem or global novelty claim.

A useful boundary control makes the distinction concrete. If the printed
integer parameters are used in the raw coordinate formula and treated as real,
the principal block on x0x2,x0x3 is [[0,1],[1,0]], with determinant -1.
The printed point does not satisfy the later conjugate-pair real-form condition.
This is **not a counterexample to the paper**: it shows why a modular replay
cannot be presented as an explicit real PSD witness. See FINDINGS.md.

## Two implementations

The primary checker uses sorted index-tuples, sparse polynomial multiplication
and standard-library modular elimination. A separately tasked AI reviewer
independently used exponent vectors, weak-composition enumeration and SymPy's
DomainMatrix over GF(7). All ten rank vectors, displayed minors, corners and
42 canonical matrix SHA-256 bindings agree. The independent arithmetic script
is preserved in review/independent_check.py. The coordinating session added
only canonical matrix-fingerprint reporting to that supplied script.

The implementations share the mathematical formulas, Python runtime and
structured certificate data for minor/basis expectations. The reviewer separately
transcribed the weights, point, pivots and tangent moments from TeX. This is
scoped AI review and exact finite computation, not human or kernel verification.

## Reproduce

Python 3.13.15, SymPy 1.14.0, mpmath 1.3.0; pytest 8.4.2 for tests.
From this directory:

```sh
python -m pip install -r requirements-dev.txt
python reproduce.py
python -m pytest -q test_check.py
python -O -m pytest -q test_check.py
```

Expected final line:
`RESULT: modular Hankel seed, all displayed minors and ten rejecting runs independently reproduced`.

Five corruptions reject under ordinary and optimized Python: changed point,
changed tangent, zero tangent (which preserves tangency but destroys the rank
increase), changed minor determinant and changed corner. Output and source
hashes are checked. certificate.json is a numeric transcription with source
anchors; no TeX is parsed by regular expressions. The all-ten-weight domain
and complete minor domains are enforced.

## Sources, availability and licensing

OpenAI source commit 1581d4cbdd69a0faf34b2089614fe2a814316a6a;
full file paths and SHA-256 values are in sources.json. Source copies and
Apache-2.0 license are included. source-availability.json inventories the pinned
family subtree: its advertised verify_certificate.py was not present there.
That does not establish absence elsewhere or a mathematical gap; the printed
formulas and minors suffice for this independent reconstruction.

OpenAI and cited predecessors retain attribution. New checker, certificate
transcription, review implementation and writing are MIT. See NOTICE.md.
