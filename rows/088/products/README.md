# Exact finite threshold for products of simplices

Alexander Richard Towell, with substantial OpenAI Codex assistance.

**Finding:** among Cartesian products of standard simplices with factor
dimensions at least two, the first violation of the simplex projection-volume
benchmark occurs in total dimension 20. The unique maximizing unordered factor
partition there is `(10,10)`, with ratio `5588869/5505024 > 1`.

The packet certifies all maxima and complete optimal factor sets through total
dimension 40. The first optimum with three factors occurs at dimension 33,
uniquely `(11,11,11)`; dimension 40 is uniquely maximized by `(13,13,14)`.
The separate exhaustive check visits **37,337 unordered partitions**.

This is a classification within the specified finite product class. The source
already gives the dimension-20 counterexample and general product formula,
and cites other constructions in dimensions at least nine. We make no claim
about the first counterexample among all convex bodies, or about global novelty.
No factor of dimension one is included. Values above dimension 40 are outside
the completed computation.

## Evidence and reproduction

[PROOF.md](PROOF.md) gives the written geometric reduction, exact recurrence,
and finite coverage argument. `certificate.json` records every scaled integer
maximum and optimal partition set; `check.py` verifies all recurrence obligations.
`enumerate_partitions.py` separately enumerates unordered partitions using
exact rational products. These two coordinating implementations share the
source formula and Python standard library and were written in the same AI
session. A separately tasked AI reviewer supplied a third algorithm based on
factor multiplicities, also matching every maximum, tie set and partition count.
See `review/` for the executable code and the precise review scope.

Python 3.13.15; the checkers need only the standard library. From this directory:

```sh
python reproduce.py
python -m pip install -r requirements-dev.txt
python -m pytest -q test_check.py
python -O -m pytest -q test_check.py
```

Expected final reproduction line:
`RESULT: all 37337 partitions agree; eight corrupt-certificate runs reject`.
The tests cover the threshold, three-factor transition, alternate product
values, wrong maxima, invalid or incomplete partition sets and domain truncation.
Rejection controls run under ordinary and optimized Python. A negative result
outside the declared finite class is not inferred.

Source: OpenAI Family 088 at the full commit in `sources.json`. The original
Pico checker is retained; this packet uses the manuscript's product reduction
rather than reproducing Pico's facet-determinant enumeration route. Its docstring
and the start of its determinant routine were read during orientation.
See [NOTICE.md](NOTICE.md) for attribution. This is written mathematics with
exact finite arithmetic, not a Lean proof or human peer review.
Claim: https://github.com/piiiico/openai-math-counterexamples/issues/33
