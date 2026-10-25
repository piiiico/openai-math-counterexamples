# Exact optimal simplex products in every dimension

Alexander Richard Towell, with substantial OpenAI Codex assistance.

For c_d=(d+1)d^d/d!, maximize products over partitions of n with all parts>=2.
The accepted predecessor proves the sharp growth rate. This follow-up gives
**the exact optimizers for every n>=2**, using a finite table through99 and
an eventual formula with the minimal uniform recurrence cutoff100.

For n>=100, write n=13q+r, 0<=r<=12. The unique maximizing multiset is:

| Residue | Factor dimensions and counts |
|---|---|
|0<=r<=8|r copies of14, q-r copies of13|
|9<=r<=12|13-r copies of12, q+r-12 copies of13|

Consequently M_(n+13)=c_13 M_n for every n>=100, and the maximizing partition
is obtained by adding one13. This recurrence fails at99. The formulas concern
only this specified simplex-product class, not arbitrary convex bodies.

## Proof and certificate

[PROOF.md](PROOF.md) derives the full value-and-witness recurrence from the
predecessor's analytic exclusion of factors>=20. A19-step finite-window
induction proves the infinite conclusion. The certificate checks exactly all
states0,2..131, all admissible last-part competitors, all maximizing witness
sets, the window100..118, and the strict failure at99. A second exact algorithm
compares balanced partitions at every possible number of factors, with no
cap19. The proof explains why balancing exhausts those alternatives.

This is written mathematics with finite exact checks, not a finite-sweep
extrapolation, kernel-checked proof, human peer review or global novelty claim.
The arithmetic result is independent of geometric interpretation. The latter
inherits the pinned written Cauchy/Fubini reduction. See sources.json,
predecessor/PROOF.md and predecessor/dependency/PROOF.md.

## Reproduce

Python3.13.15; the checker and replay use only the standard library.
From this directory:

```sh
python reproduce.py
python -m pip install -r requirements-dev.txt
python -m pytest -q test_check.py
python -O -m pytest -q test_check.py
```

Expected final line:
`RESULT: finite induction certificate and eight rejecting runs reproduced`.
False earlier cutoff, wrong witness, omitted maximizing competitor and changed
maximum each reject under both ordinary and optimized Python. Tests also check
spurious ties, unreachable dimension1, the internal empty state, wrong period,
and a sparse formula at a dimension of size10^100.

The initial deterministic exploration stopped at400; its observed pattern
motivated the proof, but the final certificate only needs states through131.
Source and test bytes, arithmetic evidence, and AI review are distinct.
The predecessor archive [v1.1.0](https://doi.org/10.5281/zenodo.23633115) does
not contain this new exact-optimizer result; source/submission pins for this
follow-up are recorded separately.
