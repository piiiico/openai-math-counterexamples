# Scoped independent AI review

Reviewer: a separately tasked OpenAI agent, `family199_parameters_review`.
Date: 2026-10-23. Mathematical proof and source tables were reviewed before
public submission; this is not human peer review or kernel verification.

No mathematical blocker was found in the following scope:

* Validity of specialization of the polynomial ten-dimensional table to any
  characteristic-two field, retaining the displayed basis.
* Kernel/image calculation, the t,j homology representatives, degree-zero
  augmentation convention, odd root order, and first failure d-1.
* q=0 exactness and actual Ext dimensions two in every degree n>=2, with
  x,v representatives in degree two and y,z in higher degrees.
* Correct separation of Hom-complex cohomology from Ext at roots of unity.
* Source overlap: the sufficient generic conditions and coordinate formulas
  already occur in the source Lean development. No new generic sufficiency
  theorem or full counterexample is claimed.

The reviewer inspected the finite-field and matrix implementation, reran its
initial nine tests and the complete 30-parameter/710-degree replay, and found
no implementation blocker. A minor observation was that grading positivity
and maximum degree were visible in the data but not explicitly checked. The
final checker now requires positive degrees off the idempotents, zero degrees
on them, and maximum degree at most four. The final 12-test suite and full
reproduction were then rerun by the primary agent; this distinction is retained.

## Separate computational method

The reviewer wrote `verification/independent_oracle.py`, independently deriving
maps from `algebra.json`, expanding them over F2, and computing ranks by
XOR-only binary elimination. It imports no production checker and uses no
finite-field inverses. It checks adjacent compositions, dimensions, cycle
representatives and independence modulo boundaries.

Its domain is every q in fields of sizes 2,4,8,16, through degree
2*max(order(q),3)+2 (using zero in place of the undefined order of q=0).
This is 30 parameters, 526 degree cases and 1,052 chain/dual quotient checks.
Both ordinary and optimized Python pass. This domain differs from the
production checker's uniform field-size cutoff; neither is an all-degree proof.

```sh
python verification/independent_oracle.py algebra.json
python -O verification/independent_oracle.py algebra.json
```

All five source hashes matched their manifest; the reviewer also manually
matched all 12 listed non-idempotent products to `03-algebra.tex`. No
literature-wide novelty assessment or rebuild of the source Lean project
was part of this review.
