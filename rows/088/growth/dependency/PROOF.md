# A finite optimality certificate for products of simplices

Alexander Richard Towell, with substantial OpenAI Codex assistance.
Written geometric reduction plus exact finite arithmetic; not a kernel proof.

## Precise class and result

Let T_r=conv(0,e_1,...,e_r) in R^r. For a partition of d into integers
r_1,...,r_k >=2, consider the orthogonal Cartesian product
K=T_(r_1) x ... x T_(r_k). Write

    R_d(K)=|Pi K|/|K|^(d-1), c_d=(d+1)d^d/d!.

This packet certifies all factor partitions in each dimension 2<=d<=40.
In this class the first dimension with R_d(K)>c_d is 20. The unique maximizing
unordered partition in dimension 20 is (10,10), giving

    R_20(K)/c_20 = 5588869/5505024 > 1.

All products in dimensions 2 through 19 have R_d(K)<=c_d. This includes the
one-factor partition (d), which has equality. At dimension 33 the unique
optimum is (11,11,11), and 33 is the first checked dimension with any optimal
partition having three factors. At dimension 40 the unique optimum is
(13,13,14). All intermediate exact maxima and all optimal partitions are
recorded in certificate.json and corroborated by enumeration.json.

These are statements about this explicitly defined product class, with no
one-dimensional factors. They do not bound arbitrary polytopes or convex
bodies. The source already cites different counterexamples in dimensions
at least nine. Neither a globally smallest counterexample nor a new mechanism
is claimed. Global novelty of this finite classification is not established.

## Geometric reduction, with constants retained

The following written argument restates the source's product mechanism and
simplex value to identify exactly what the integer certificate means.

For a full-dimensional polytope P in dimension d>=2, let N_F be the outward
unit normal times the (d-1)-volume of facet F. Cauchy's formula is

    h_(Pi P)(u) = (1/2) sum_F |N_F dot u|.

Indeed, almost every line in a fixed direction meeting the body has an entry
and an exit facet; the face projections cover its shadow with multiplicity
two. Exceptions lie in projections of lower-dimensional faces or parallel
facets, which have (d-1)-measure zero. The projection Jacobian of each facet
is the absolute scalar product of its unit normal with the unit direction.
Integration proves the formula, and homogeneity extends it to arbitrary u.
Thus Pi P is the Minkowski sum of the centered segments [-N_F/2,N_F/2].
The factor 1/2 is retained throughout.

For polytopes A in R^r, B in R^s, every facet of A x B is either F x B or
A x G: dimensions of exposed product faces add, and exposing proper faces
in both factors gives codimension at least two. Their area-normal vectors
are (|B|N_F,0) and (0,|A|N_G). The formula above therefore gives

    Pi(A x B) = (|B| Pi A) x (|A| Pi B).

Support functions establish equality here: the segment sums in orthogonal
coordinate spaces have the sum support function of the indicated product.
Taking volumes and dividing by |A x B|^(r+s-1) gives exactly

    R_(r+s)(A x B)=R_r(A) R_s(B).                       (1)

There is no binomial coefficient at this geometric step. Those coefficients
appear only when we later rescale rational numbers by factorials.

For T_r, |T_r|=1/r!, and its facet area-normal vectors are
-e_i/(r-1)! and (e_1+...+e_r)/(r-1)!. Translating the centered segment sum
shows that Pi T_r is a translate of

    ([0,1]^r + [0,e_1+...+e_r])/(r-1)!.

Write w=e_1+...+e_r and Q=[0,1]^r. On every nonempty fiber parallel to w,
adding [0,w] increases its interval length by ||w||, without changing the
base projection. Fubini gives

    |Q+[0,w]|=1+||w|| |proj_(w-perp) Q|=1+h_(Pi Q)(w)=1+r,

because the cube has two unit-area facets in each coordinate direction.
Consequently

    |Pi T_r|=(r+1)/((r-1)!)^r, R_r(T_r)=c_r.            (2)

Equations (1) and (2) prove R_d(K)=product_i c_(r_i) for the class stated
above. This written reduction does not require either source theorem as an
unproved premise, but it is not machine-verified geometry. It explicitly
uses Cauchy's projection/facet argument, Fubini, and the elementary simplex
volume and facet calculation, as the source does.

If arbitrary full-dimensional simplices or invertible affine images of these
products are considered, the standard covariance also preserves this ratio:
area-normal vectors transform by |det L| L^(-T), so Pi(LP) has that image.
Its volume scales by |det L|^(d-1), cancelling the denominator. Translation
changes no projection volume. Thus shapes within those affine classes do not
alter the comparison; the finite certificate itself indexes factor dimensions.

## Complete integer recurrence

Let M_d be the largest product of simplex constants over the allowed unordered
partitions of d, and put A_d=d! M_d. Use the auxiliary empty-product state
A_0=1 and no state at dimension 1. It is an algorithmic base case, not a
geometric definition of a zero-dimensional projection functional.
For each d>=2,

    A_d = max over 2<=r<=d, d-r !=1 of
          binom(d,r) (r+1) r^r A_(d-r).                (3)

To prove completeness, remove any one factor of a product partition. Its
remaining total dimension is zero or at least two, and its product is at
most M_(d-r). Conversely, append a factor T_r to any attaining remaining
partition. This constructs a feasible partition attaining each candidate.
Multiplying c_r M_(d-r) by d! gives precisely the integer in (3).
Both inequalities prove equality. Every scaled product is an integer since
it is a multinomial coefficient times product_i (r_i+1)r_i^(r_i).

Starting at zero, the checker verifies every state in the exact sequence
0,2,3,...,40. For each state it checks all recurrence candidates, that every
listed partition is valid and attains the scaled maximum, and that the listed
optimal set includes all partitions formed from all tied optimal candidates.
Permutations are identified by sorting. Induction on d proves both the bound
and completeness of the optimal witness sets. A missing state, incorrect
maximum, unattaining factorization or spurious optimal partition rejects.
The geometric benchmark at dimension d has scaled value (d+1)d^d.
Thus A_d=(d+1)d^d for all 2<=d<=19 excludes a violation anywhere in that
finite range. A_20>(21)20^20, attained only by (10,10), proves the threshold.

## Separate exhaustive enumeration and controls

The separate enumerator generates each nondecreasing partition of a total d
with parts>=2 once: either the sole part d, or its first part r with
2<=r<=floor(d/2), followed by a partition of d-r whose parts are at least r.
The first part and remaining tail are unique, proving disjointness and
completeness inductively. It evaluates product_i (r_i+1)r_i^(r_i)/r_i! using
exact Fraction arithmetic, with no scaled recurrence or checker imports.

Across all dimensions 2 through 40 this examines 37,337 partitions and agrees
with the DP on all 39 maxima and complete optimal sets. This is a fixed finite
domain, not a random search, and there is no inference about dimensions above
40 beyond the independently proved general recurrence. Both programs share
the source formula and Python standard library; they were written in the same
coordinating AI session, not by independent human authors.

Mutations change the dimension-20 maximum, replace its factorization by the
wrong-total (10,11), remove a domain state, or falsely add (9,11) as an optimum.
All must reject under ordinary and optimized Python. Alternate products such
as (9,10) in dimension 19 and (2,2) in dimension 4 check strict comparison
and the factorial scaling. A finite exact certificate plus a written reduction
is not a kernel proof, human peer review, or unrestricted extremal theorem.
