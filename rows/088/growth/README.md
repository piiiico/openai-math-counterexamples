# Sharp growth rate for the simplex-product class

Alexander Richard Towell, with substantial OpenAI Codex assistance.

Let c_d=(d+1)d^d/d! and M_n maximize the product of these constants over
partitions of n with parts at least two. Set a=c_13^(1/13). The written proof
establishes M_n<=a^n for every n>=2, with equality exactly at multiples of 13,
uniquely attained by all-13 factors. Explicit residue constructions give
b a^n<=M_n for n>=14, b>0. Thus `lim (M_n/c_n)^(1/n)=a/e>1`.

The sharp excess rate lies between 1.03 and 1.04 by exact enclosures. The new
step is an analytic beneficial split for every factor dimension>=20, followed
by 18 exact density comparisons. It is not extrapolation from the finite sweep.
The interpretation is restricted to Cartesian products of simplices with
factor dimensions>=2. No universal convex-body bound, full residue-wise optimum
formula or global novelty claim is made.

## Reproduce

Python 3.13.15, with pinned requirements. From this directory:

```sh
python -m pip install -r requirements-dev.txt
python reproduce.py
python -m pytest -q test_check.py
python -O -m pytest -q test_check.py
```

Expected: `RESULT: exact growth evidence, eight rejecting runs and independent corroboration reproduced`, and 28 tests in each Python mode.
The checker validates 18 density comparisons, five symbolic identities, rigorous
root/exponential enclosures, the dimension 19 failure boundary and sparse
residue controls. A separately tasked reviewer used standard-library exact
arithmetic and finite DP through 120 for corroboration. The analytic proof
supplies the all-dimensional conclusion. Four false claims reject in both
Python modes. This is written proof and AI review, not Lean or human review.

See [PROOF.md](PROOF.md), [NOTICE.md](NOTICE.md) and [review/REVIEW.md](review/REVIEW.md).
Reused geometry and source files are byte-pinned in sources.json. The frozen
finite predecessor is https://doi.org/10.5281/zenodo.23627947; **that v1.0.0
archive does not contain this new theorem**. Claim:
https://github.com/piiiico/openai-math-counterexamples/issues/35
