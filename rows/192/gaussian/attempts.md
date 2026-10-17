# Bounded parameter probe and stopping record

Visit started 2026-10-17T08:04:18Z. The selection and stopping plan is preserved
locally in PLAN.md. This was one refinement of the source coarse reporting
mechanism, with no pivot and no reopened Boolean brute-force search.

Before writing the exact checker, a deterministic floating-point cost probe
tested six schedules, all with cutoff 8 and shift 3/8. It used ideal
conditional-mean exceptional predictors and a coarser tail estimate.
These approximate numbers guided selection and certified nothing:

| k, with m=2^k+1 | radius | approximate sufficient margin |
|---|---|---|
| 20 | 2^-27 | -0.3076799107 |
| 21 | 2^-28 | -0.1955236318 |
| 22 | 2^-30 | -0.0836325573 |
| 23 | 2^-32 | -0.0283103116 |
| 24 | 2^-33 | +0.0267465476 |
| 25 | 2^-34 | +0.0528524720 |

The first positive schedule in this six-element probe was retained.
There was no random seed or claim of exhaustive parameter coverage.
The temporary exploratory calculation was not retained as a verifier.

The proof was then refined to use rational predictors and to bound their
conditional-mean bias explicitly. A simpler central estimate and the bias
allowance yield the rigorously enclosed final gain ratio
`>0.026467562004`, still `>1/50`. The primary computation is deterministic
and stops after four scalar Taylor enclosures at degree 128, covering the
single schedule in certificate.json; the analytic uniform estimate covers
all its intervals.

Changing to a coarser grid at the final fixed radius fails this sufficient
test. This does not rule out that grid's actual gain, other radii, other
predictors, or a better bound. No impossibility or optimality claim follows.

The next mathematically distinct task would quantify one finite-alphabet
transfer from this Gaussian schedule, including approximation error below
the explicitly tiny certified gain. Its optimistic size should be priced
before implementation. The present visit stops after verifying and handing
off the Gaussian intermediate construction.
