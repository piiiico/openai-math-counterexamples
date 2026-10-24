# Attribution and scope

Alexander Richard Towell, with substantial OpenAI Codex assistance in code,
derivation, tests and exposition. A separately tasked AI reviewer examined the
mathematical reduction and finite completeness; this is not human peer review.

OpenAI's *A product counterexample to the simplex maximum for projection-body
volume* supplies the product mechanism, simplex value, dimension-20 example,
and exponential-growth observation. This packet adds exact finite optimization
of all simplex-factor partitions through dimension 40, with certificate
verification and a separate exhaustive algorithm. No new geometric mechanism
or global novelty claim is made. Cauchy's projection formula and Fubini are
classical; the written reduction preserves their normalization constants.

Pico (AI agent operated by Håkon Åmdal) supplied the earlier exact facet-vector
and zonotope-determinant computation. That implementation is not used here;
its scope docstring and the beginning of its determinant routine were read.
The two coordinating algorithms share a formula and runtime; their distinct
methods and common authorship are disclosed. The separate review's method and
shared dependencies are identified in review/REVIEW.md.

The source credits Brannen's conjecture and other researchers' prior work,
including Feng, Hu, Liu and Xu counterexamples in dimensions at least nine.
See the pinned source and bibliography; this packet's minimal dimension is
only for the restricted product class with factors of dimension at least two.

New packet code and writing are MIT (LICENSE). Included OpenAI extracts retain
Apache-2.0 (source/LICENSE-openai). Python and pytest retain their respective
licenses and contributor attribution. Finite computation, written proof,
AI review, upstream acceptance and archival publication are distinct states.
