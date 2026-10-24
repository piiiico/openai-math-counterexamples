# Parameter strata of the displayed seed resolution

Alexander Richard Towell, with substantial OpenAI Codex assistance.
Written proof, not a Lean proof. Source and predecessor credit: OpenAI,
`03-algebra.tex`, `04-resolution.tex`, Lemma `res:base`, and the already
formalized coordinate identities in `Resolutions/Resolution.lean`, at the
commit in `sources.json`. The exceptional classification below concerns the
same polynomial table; no novelty beyond the inspected sources is claimed.

## Statement and convention

Let k be a field of characteristic two and q any element. Let C_q have the
ten-element basis and polynomial multiplication table in `algebra.json`.
Let s be its one-dimensional left f-simple. Set ell_i=x+q^i y for i>=0,
with q^0=1 even at q=0. Define R_0=C_q f, R_n=C_q e for n>=1,
d_1(a)=au, d_n(a)=a ell_(n-2) for n>=2, and augmentation
epsilon:C_q f -> s taking the f coefficient. Write
D_0=ker(epsilon)/im(d_1), D_n=ker(d_n)/im(d_(n+1)) for n>=1.
Thus D_0 is the augmentation defect, not the unaugmented H_0.

**Theorem.** This augmented complex is exact if and only if q=0 or q has
infinite multiplicative order. More precisely:

* At q=0 all D_n vanish.
* At q=1, D_0 has basis [n]; every D_n for n>=1 has basis [t],[j].
* If q has finite order d>1, D_0=D_1=0. For n>=2, a basis of D_n
  consists of [t] when d divides n, and [j] when d divides n+1; otherwise
  it is empty. The first failure is degree d-1. In characteristic two d
  is odd, hence d>=3.

When the complex is exact, it is a projective resolution. In all exact cases
Ext^0(s,s)=k and Ext^n(s,s)=0 for n>0. If q has infinite order, the
source's Ext^n(s,C_q) profile holds: the right f-simple in degree two,
zero otherwise. At q=0, its vector-space dimensions instead are zero in
degrees zero and one and **two in every degree n>=2**.

## Algebra and coordinate identities

The source associativity computation consists of polynomial identities over
F2[q], so it survives every specialization. The checker independently
exhausts all 10^3 basis triples in that polynomial ring, verifies the unit,
corners and positive grading, and uses bilinearity. The positive-degree
ideal N has N^5=0 and C_q/N=k x k, so N is the radical at every q.
In particular the displayed basis does not shrink at q=0 or q=1. The
source's stronger nonzero fourth radical product is not asserted there.
The idempotent summands C_q e and C_q f are projective.

In bases Ce=(e,x,y,z,t,j), Cf=(f,u,v,n), multiplication gives

| a | e | x | y | z | t | j |
|---|---|---|---|---|---|---|
| au | u | v | v | 0 | (1+q)n | 0 |
| a ell_i | ell_i | q^(i+1)z | z | 0 | (1+q^(i+2))j | 0 |

The identities ell_0 u=0 and ell_(i+1) ell_i=0 show this is a complex
for every q, without division. The augmentation is surjective and kills u,v,n.

Set b_i=1+q^(i+2). The second row directly gives, uniformly in i,

    im(right ell_i) = span(ell_i,z), plus span(j) if b_i != 0;
    ker(right ell_i) = span(ell_(i+1),z,j), plus span(t) if b_i = 0.

Indeed the e coefficient must vanish, the y coefficient equals
q^(i+1) times the x coefficient, and b_i times the t coefficient is zero.
The three displayed kernel vectors are independent. The image vectors
ell_i,z are independent, and j appears precisely when b_i is nonzero.
Similarly right u has image span(u,v), with n added if q!=1, and kernel
span(ell_0,z,j), with t added if q=1.

## Exactness and exceptional homology

The formulas give dim D_0 = [q=1]. In degree one, q!=1 implies
q^2!=1 in a characteristic-two field, so ker(right u)=im(right ell_0).
If q=1 their quotient has representatives t,j.

For every n>=2, the common kernel/image part is span(ell_(n-1),z).
The kernel additionally contains j and contains t precisely when q^n=1;
the incoming image contains j precisely when q^(n+1)!=1. Therefore

    basis D_n = { [t] : q^n=1 } union { [j] : q^(n+1)=1 }.

This proves all asserted strata. These are genuinely nonboundary cycles:
the incoming image never has a t coefficient, and when its j coefficient
vanishes it cannot contain j. If q=0, every relevant 1+q^m equals 1;
if q has infinite order none vanishes. Conversely, a nonzero q not of
infinite order has a least positive order d. A finite order in characteristic
two is odd: an even order would satisfy (q^(d/2)+1)^2=0, contradicting
minimality in a field. For d>1, the first divisible n+1 is n=d-1.

## The dual complex, including q=0

Evaluation identifies Hom_C(Cf,C)=fC and Hom_C(Ce,C)=eC. Precomposition
becomes left multiplication. Let E^0=fC, E^n=eC (n>=1), with
delta^0=u left multiplication and delta^n=ell_(n-1) left multiplication.
It is a cochain complex at every q; it computes Ext only when R is exact.

In bases fC=(f,t,j,n), eC=(e,x,y,z,u,v), u sends the first basis to
(u,y+qx,z,v), always four independent vectors. The remaining maps are

| a | e | x | y | z | u | v |
|---|---|---|---|---|---|---|
| ell_i a | ell_i | q^i z | qz | 0 | (1+q^i)v | 0 |

For every q, ker(left ell_0)=span(qx+y,z,u,v)=im(left u), and
im(left ell_0)=span(ell_0,z). Thus H^0(E)=H^1(E)=0.

For q!=0 and i>=1, the kernel is span(ell_(i-1),z,v), with u
added if q^i=1; the image is span(ell_i,z), with v added if q^i!=1.
Consequently, for n>=2 the cohomology has independent representatives

    { [u] : q^(n-1)=1 } union { [v] : q^(n-2)=1 }.

At infinite order this leaves only v in degree two. Its right action has
vf=v, ve=0 and vt=qz a boundary, giving exactly the right f-simple.
At roots of unity these are cohomology statements about E, **not Ext
calculations**, since R is not a resolution.

At q=0, ell_0=x+y and ell_i=x for i>=1. For every i>=1,
ker(left ell_i)=span(x,y,z,v) and im(left ell_i)=span(x,v).
In degree two the preceding image is span(x+y,z), so classes x,v form
a basis. In every degree n>=3 the preceding image is span(x,v), so
classes y,z form a basis. This proves the two-dimensional Ext assertion.
We make no further claim about its right module isomorphism type.

Finally, when R is a resolution, Hom_C(Ce,s)=0 and Hom_C(Cf,s)=k;
the self-Ext assertion follows in all degrees.

## Consequence and limits

No choice of nonzero q in a finite characteristic-two field makes this
particular infinite complex exact; q=0 restores exactness but loses the
exceptional dual Ext profile used downstream. This is an obstruction to
specializing this seed mechanism unchanged. It does not rule out another
resolution, altered algebra/module, or another finite-field counterexample.
Neither the generic sufficiency argument nor the coordinate formulas are
new relative to the source Lean development. The finite replay is evidence
for the transcription and indexing; the argument above supplies the
all-degree conclusion. No human peer review or Lean checking of this note
has occurred.
