# Exact algebra and the scope of its geometric interpretation

Alexander Richard Towell, with substantial OpenAI Codex assistance.
The construction and qualitative cone conclusion are OpenAI's; this note
independently derives the algebra and records a parameter consequence.

## Conventions and exact reduction

Use the oriented orthonormal coframe e1,...,e4. A two-form is represented
by the skew matrix A with alpha(X,Y)=X^T A Y. Put

U=e12+e34, V=e13-e24, W=e14+e23,
N=U+fV+kW, s=f²+k², R=1+s, r=sqrt(R), F=N/r, J=-N/r.

Thus F(X,Y)=<JX,Y>; the minus sign in J is essential.
All quantities below are real, and r>0. The checker works in the polynomial
ring Z[f,k,z], with no floating arithmetic or finite parameter sampling.
Clearing denominators is legitimate because R>=1. Its exact identities
include N²=-R I, N^T=-N, *N=N and |N|²=2R. Consequently J²=-I,
J^T J=I and F has squared norm two.

For E=U+2f e13+2k e23, the identities

E+*E=2N, E-*E=2[f(e13+e24)+k(e23-e14)],
N^T E N=R E

prove the stated self-dual/anti-self-dual decomposition and J-invariance.
In particular, E's self-dual part is N=rF, as in the source; it is not F.

## Positivity without sampling

The symmetric matrix H=-EN represents r E(X,JY). The exact certificate is

(H-RI)²=Rs I,
det(zI-H)=((z-R)²-Rs)².

Since H is real symmetric, its eigenvalues are R±sqrt(Rs), with multiplicity
two when s>0; at s=0 all are one. Dividing by r yields r±sqrt(s).
Both are positive for every real f,k, since r²-s=1. If |f|,|k|<=1/4,
then s<=1/8 and

r-sqrt(s)=1/(sqrt(1+s)+sqrt(s)) >= 1/sqrt(2).

This lower bound is attained where f=k=1/4. It is an elementary inequality
applied to the checked characteristic polynomial, not a machine-checked
inequality theorem.

For B±=U±V the checker proves

sym(-B±N)=(1±f)I,
R B± + N^T B± N=2(1±f)N.

It follows that B± tame J exactly where 1±f>0 and their invariant
projections are (1±f)N/R=(1±f)F/r. In the source's amplitude range their
taming metrics also have minimum at least (3/4)/sqrt(9/8)=1/sqrt(2).
The tests include f=1 (loss of strict taming) and amplitude 5/4 (negative
value), distinguishing strict positivity from a nonnegative bound.

## Differential and global steps

Set f=(1/4)sin(2 pi x1), k=(1/4)sin(2 pi x2) on R^4/Z^4. They are smooth
periodic functions. The exterior derivative of E is zero: df is a multiple
of dx1, dk a multiple of dx2, and both corresponding wedges contain a
repeated coordinate. The checker verifies each coefficient of the two
independent derivatives exactly. Swapping the supports makes it reject.

The periodic one-form

A=-(cos(2 pi x1)+cos(2 pi x2))/(4 pi) dx3

satisfies dA=2f e13+2k e23, by the usual derivative of cosine. Hence [E]=[U].
This last trigonometric differentiation and periodicity are written
arguments, not a symbolic trigonometric or kernel proof in the checker.

For completeness, the following explains the **global interpretation**,
which the finite checker does not prove. A J-anti-invariant two-form for
this orthogonal, orientation-compatible J is self-dual and perpendicular
to F. This is the standard pointwise four-dimensional decomposition.
Closedness plus self-duality implies coclosedness, so such a form is harmonic.
For the flat torus the Hodge Laplacian acts coefficientwise; integration by
parts shows each harmonic coefficient is constant. Thus it is aU+bV+cW.
Perpendicularity becomes a+bf+ck=0 everywhere. Evaluation at (x1,x2)
=(0,0),(1/4,0),(0,1/4) gives determinant 1/16, checked exactly, so a=b=c=0.
The checker also verifies that V-fU and W-kU are pointwise anti-invariant;
it does not replace the stated differential/Hodge facts with a computation.

Finally B+ wedge B-=0 and B± wedge B±=4 vol, both checked exactly.
A compatible form wedges positively with every tamer: in an orthonormal
J-frame diagonalizing the positive Hermitian compatible form, the wedge is
lambda1 beta(e3,Je3)+lambda2 beta(e1,Je1), times positive oriented volume.
Here lambda1,lambda2>0 and the two tamer evaluations are positive. Integrating,
a compatible representative of [B+] would pair positively with the closed
tamer B-, contradicting their zero cohomological pairing; likewise for [B-].
Since H_J^-=0 and E is compatible, this independently explains the source's
strict inclusion for this example. It does not verify the general cone
theorem or the manuscript's other analytic arguments.

## Immediate parameter consequence (written corollary)

The same calculation applies to f=a sin(2 pi x1), k=b sin(2 pi x2), for real
a,b. E is compatible for every a,b. Both fixed forms U±V tame J everywhere
**if and only if |a|<1**, independently of b. If a and b are nonzero, the
three-point evaluation determinant is ab, so the same global argument gives
H_J^-=0 and the strict inclusion whenever 0<|a|<1 and b!=0. The primitive is
-(a cos(2 pi x1)+b cos(2 pi x2))/pi dx3. At |a|=1 strict taming fails at an
extremum, and for |a|>1 one fixed form has a negative evaluation somewhere.
For a=0 or b=0 the three-point argument loses rank; we make no H_J^-=0
claim in those cases. This is a transparent parameter consequence of the
source mechanism, not a claim of a new counterexample or global novelty.

## Trust and limitations

Exact polynomial computation verifies the listed identities over all real
parameters by evaluation of integer-polynomial identities. This is stronger
coverage than a finite grid, but it trusts Python and this small algebra
implementation. Tests, an independent determinant implementation, and
mutations reduce implementation risk; they are not a formal soundness proof.
The geometric deductions above are written mathematics, with explicitly
listed standard facts. There is no Lean/kernel proof or human peer review.
