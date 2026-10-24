# Separately tasked AI review

A separate OpenAI Codex reviewer examined the written proof, both coordinating
algorithms, test suite, exact certificates, source manifest and source geometry.
No blocking correctness issue was found. The review checked the Cauchy factor
1/2, simplex facet normals, product volume cancellation, affine covariance,
finite-domain restriction and complete reconstruction of tied optimal sets.
It reproduced 16 tests, the full partition enumeration and eight rejecting
controls in ordinary/optimized Python, including a feasible inferior maximum.

The reviewer independently implemented a third algorithm: process factor sizes
in increasing order, then total dimensions in increasing order, keeping the
best rational product and all attaining multiplicity vectors. This unbounded
knapsack ordering permits repeated factors while giving each multiset one
representation. The parallel count recurrence is the coefficient recurrence
for product_(r=2)^40 (1-z^r)^(-1). It agrees with every individual partition
count, all 39 exact maxima and all tie sets, totaling 37,337 partitions.

The script is preserved in independent_check.py. The coordinating agent changed
only path resolution and explicit rejection/presentation: assertions became
exceptions so checks remain active under optimized Python. It shares the
simplex formula and Python/Fraction with the other implementations. Distinct
algorithm and separately tasked AI authorship do not establish independence of
all assumptions, a human peer review, or kernel verification of the geometry.
