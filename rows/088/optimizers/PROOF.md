# Exact simplex-product optimizers in every dimension

Alexander Richard Towell, with substantial OpenAI Codex assistance.
Written proof with a finite exact certificate; not kernel verification.

## Statement

For integer d>=2 put c_d=(d+1)d^d/d!. For n>=2, let M_n be the largest
product of the c_d over unordered partitions of n with every part>=2, and
let W_n be the complete set of maximizing unordered partitions. Then

    M_(n+13)=c_13 M_n                    for every integer n>=100.       (1)

The cutoff100 is minimal for a recurrence valid at every subsequent integer:
M_112>c_13 M_99. Every maximizing partition is unique. The certificate gives
all maximizers for 2<=n<=131. For n>=100, write n=13q+r, 0<=r<=12:

- If 0<=r<=8: r factors14 and q-r factors13.
- If 9<=r<=12: 13-r factors12 and q+r-12 factors13.

All multiplicities are nonnegative in the stated range. These formulas and
the certified finite table2..99 completely solve this discrete product-class
optimization for every n>=2. They do not bound arbitrary convex bodies or
allow one-dimensional factors. No global mathematical novelty is claimed.

## Inherited analytic lemmas and finite recurrence

The accepted growth packet proves, by analytic inequalities for consecutive
ratios and balanced splits, that no maximizing partition contains a factor
d>=20. Its written proof is preserved at predecessor/PROOF.md, with dependencies,
licenses and hashes. This reduction is essential; numerical testing of large
factors is not a substitute. It also proves rho_d=c_(d+1)/c_d strictly decreases
for every d>=2, used for independent finite corroboration below.

Define M_0=1, W_0={()}; n=1 is unreachable and has no value or witnesses.
For all n>=2 the complete recurrence is

    M_n = max_{2<=d<=19, n-d reachable} c_d M_(n-d),
    W_n = union over maximizing d of {sort((d,)+w): w in W_(n-d)}.      (2)

A recurrence candidate gives an admissible partition. Conversely, remove any
part d of an optimal partition. Its tail must be optimal at n-d: otherwise
substitution strictly improves the product, since c_d>0. Thus (2) computes
both the exact value and every maximizing unordered partition. Deduplication
only identifies permutations. The empty partition is an internal base case,
not an assertion about a dimension-zero convex body.

## Finite-window induction

Let A(W)={sort((13,)+w):w in W}. The certificate checks for each integer
100<=n<=118 that

    M_(n+13)=c_13 M_n,       W_(n+13)=A(W_n).                          (3)

These19 consecutive checks involve states through131. Suppose (3) holds for
all indices from100 to n-1, with n>=119. For every d in2..19, n-d>=100 and
n-d<n; in particular both predecessor states are reachable. Using (2) and
then the inductive hypothesis gives

    M_(n+13) = max_d c_d M_(n+13-d)
              = max_d c_d c_13 M_(n-d) = c_13 M_n.

All factors are positive, so the maximizing choices of d in the two maxes
are exactly the same. Their witness sets are related by A by induction.
Appending d and appending13 commute after sorting, and A commutes with unions.
Thus W_(n+13)=A(W_n). Strong induction proves (3) for every n>=100.
This is a finite certificate of a stated induction hypothesis, not an
extrapolation from a longer sweep.

## Explicit witnesses and cutoff

The exact base witnesses at n100..112 are:

| n | Unique partition (dimension^multiplicity) |
|---|---|
|100|12^4,13^4|
|101|12^3,13^5|
|102|12^2,13^6|
|103|12^1,13^7|
|104|13^8|
|105|13^7,14^1|
|106|13^6,14^2|
|107|13^5,14^3|
|108|13^4,14^4|
|109|13^3,14^5|
|110|13^2,14^6|
|111|13^1,14^7|
|112|14^8|

Every n>=100 has a unique representative in100..112 modulo13. Appending13
as in (3) proves the stated formula and uniqueness. For r<=8, q>=r follows
from the first admissible representative in104..112; for r>=9, q+r-12>=0
already at representatives100..103. The certificate separately checks unique
maximizers in every state2..99.

At99 the unique optimum is12^5,13^3. At112 it is14^8. The exact strict
comparison c_14^8>c_12^5 c_13^4 disproves (1) at99. Thus no uniform starting
index below100 works. This does not say the recurrence fails at every n<100.

## Independent finite corroboration by balancing

Fix k parts with sum n. If two parts u<v satisfy v-u>=2, replacing them by
u+1,v-1 changes their product by rho_u/rho_(v-1)>1. Hence a maximizing
partition for fixed k is the unique balanced multiset: write n=ak+b,
0<=b<k, with k-b parts a and b parts a+1. Conversely successive balancing
terminates, for example because the sum of squared parts strictly decreases,
and yields that multiset. Therefore the maximum over all partitions is found
by comparing k=1..floor(n/2). This second exact method uses no cap19, does not
use the DP recurrence and permits all ties among the different values of k.
It checks every certificate state2..131. It shares the formula and the
inherited written ratio lemma, and is not a second independent analytic proof.

## Scope and attribution

The arithmetic result concerns explicitly defined positive rationals. Its
convex-geometric interpretation uses the predecessor's written Cauchy/Fubini
reduction. OpenAI supplied the product mechanism and simplex constants. The
finite and growth predecessors are preserved with full source pins. Pico,
operated by Hakon Amdal, suggested examining improved residue constructions
and observed mixtures of13s and14s; the present exact classification also
requires12s in residues9..12. The finite-to-infinite recurrence argument and
classical balancing reasoning are elementary; this packet makes no general
claim of invention of either method. AI review is not human peer review.
