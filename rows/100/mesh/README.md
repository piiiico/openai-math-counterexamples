# Mesh-aware coverage for the parabolic cylinder family

Alexander Richard Towell, with substantial OpenAI Codex assistance.

**Result:** the source's parabolic secant construction covers the entire closed
regular tetrahedron for an arbitrary finite partition with maximum gap D when

    2eta-(7/4+2eta)tau-D/(4tau)-D/4 >= 0,

with 0<tau<1 and eta>=0. For eta<=1/8, the complete normalized area error is
`59tau^4/64+tau^2 D`. The written proof removes the source's additional
`D<=tau^2` restriction and permits nonuniform partitions.

At tau=1/2000, eta=1/1000, and n=1,000,000 equal sectors per family,
there are 2,000,000 cylinders with certified normalized cost at most
`1/2 - 1662287/3072000000000000`. This is fewer than the source example's
16,000,000 cylinders. **It is not a new best cover:** Pinho's distinct
4,096-cylinder construction has a much greater saving.

## What is verified

[PROOF.md](PROOF.md) supplies the continuum argument, all geometric membership
steps and area error bounds. `check.py` checks nine exact symbolic identities,
rational budgets and an actual rational point uncovered when enlargement is
removed. These computations alone are not a formal proof of continuum coverage.
A negative sufficient budget does not establish that a cover fails. A separate
AI reviewer independently summed exact polynomial bounds over all million
sectors and solved the control membership systems barycentrically; its code
and scope are in `review/`.

The source argument already proves uniform coverage at its own parameters;
this packet does not allege a gap in that theorem. It is a modest parameter
relaxation, a written extension to arbitrary finite partitions, and a reproducible
algebra/parameter audit. No optimality or global novelty claim is made.

## Reproduce

Python 3.13.15; dependencies are pinned. In this directory:

```sh
python -m pip install -r requirements-dev.txt
python reproduce.py
python -m pytest -q test_check.py
python -O -m pytest -q test_check.py
```

Expected reproduction result:
`RESULT: positive certificate, ten rejecting runs and independent area/geometry replay reproduced`.
The tests cover exact budget boundaries, a genuine uncovered point, vertices,
nonuniform sector membership, nonmonotone first crossing, three symbolic
mutations and invalid parameter regimes. No million-sector enumeration or
random search is needed for the written all-partition argument.

The first public coordination claim is
[issue #30](https://github.com/piiiico/openai-math-counterexamples/issues/30).
See `sources.json`, [NOTICE.md](NOTICE.md), and the verification/review records
for pins, attribution, scope and limitations. This is not Lean verification or
human peer review. Upstream acceptance, when recorded, is separate from proof.
