# Family 199: exact cocycle and twisted-boundary verification

The explicit degree-three cochain in OpenAI's proposed Auslander–Reiten
counterexample passes an independent exact check of its cocycle equation,
twisted boundary identity, and displayed nonzero cycle evaluation. This
extends the finite coverage beyond Pico's preceding starting-algebra check.
It does **not** verify the full counterexample theorem.

The source is pinned to OpenAI math
`1581d4cbdd69a0faf34b2089614fe2a814316a6a`:
`preprints/An-explicit-counterexample-to-the-Auslander-Reiten-conjecture-September-23-2026/build/03-algebra.tex`
(Lemma `coc:data`) and `09-cochain.tex` (the complete table).
[sources.json](sources.json) records file hashes and the destination base.

## Reproduce

Python 3.13.15 was used; the checker and tests need only the standard library.
From this packet's directory:

```sh
python reproduce.py
```

Expected: exit 0 and `RESULT: Family 199 exact identities and rejecting controls reproduced`.
This checks source hashes, both independent implementations, all 22 tests,
and deliberate corruptions under ordinary and optimized Python.
Individual checks are:

```sh
python check.py
python -m unittest discover -s . -p 'test_check.py' -v
python -O check.py --mutate twist  # expected exit 1 and nonzero residual
```

The positive command prints `RESULT: holds` after checking all 104,976
radical quadruples (15,250 composable), all 324 boundary pairs, 8,000
associativity triples and 400 trace-duality pairs. The displayed cycle has
zero boundary and evaluation q³f. `--mutate cochain` and `--mutate dual`
also deliberately fail. [PROOF.md](PROOF.md) gives the exact interpretation
and explicit residuals. [verification.json](verification.json) records the
completed coverage and the limited remaining software trust assumptions.

## Method and limits

`data.json` transcribes the source's ten-dimensional algebra and 179-entry
cochain. `check.py` derives the twenty-dimensional trivial extension from
dual evaluation and works over F₂[q,H,H⁻¹]. It computes the displayed
boundary identity directly, keeping H and H⁻¹ symbolic. There is no
floating point arithmetic or specialization-based acceptance.

Multilinearity extends the finite basis identities to all inputs. Nonzero
evaluation requires q≠0, as holds in the source's transcendental field;
H must be invertible. The interpretation as a nonzero Ext class uses the
standard relative bar resolution and a written cycle-pairing argument.
The source's later explicit resolution and cone/lift steps are outside scope.

## Attribution and status

Alexander Richard Towell, with substantial OpenAI Codex assistance in
implementation, mathematical exposition, testing and packaging. OpenAI
supplied the construction, table and finite recurrences. Pico, operated by
Håkon Åmdal, supplied the preceding independent starting-algebra check.
That algorithm body was not inspected when writing this implementation.

The [separate AI review](REVIEW.md) includes a second exact implementation
using binary polynomial coefficients and accumulating differential terms
from the nonzero table entries. It also independently retranscribes the
source data. This is not Lean/kernel verification or human peer review.
[Issue #22](https://github.com/piiiico/openai-math-counterexamples/issues/22)
records the scope claim. No new theorem or global novelty is claimed.
Source snapshots retain OpenAI's Apache-2.0 license; see [NOTICE.md](NOTICE.md).
