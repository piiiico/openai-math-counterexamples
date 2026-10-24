# A centered-isotropic rotation obstruction

Alexander Richard Towell, with substantial OpenAI Codex assistance.
Written proof; not Lean-checked or independently human-refereed.

## Algebraic lemma

Let F be a characteristic-zero field with a Q-linear derivation delta. Let
Q=(q_j) be a finite labelled family in the delta-constant plane, such that

    sum q_j = 0,       sum q_j q_j^T = c I_2,       c != 0.

Let u,v belong to F with u^2+v^2=1, delta u=-v and delta v=u. Define

    R+ = [[u,-v],[v,u]],  R- = [[u,v],[-v,u]],  R0=I,
    x_(epsilon,j)=R_epsilon q_j,
    p_(epsilon,j)=(1,x_(epsilon,j))^T,
    beta_(+,j)=beta_(-,j)=1, beta_(0,j)=-2.

Then, with the sums over all labels,

    M00 = sum beta p p^T = 0,
    M10 = sum beta (delta p) p^T = 0,
    M11 = sum beta (delta p)(delta p)^T = diag(0,2c,2c).

Proof: put J=[[0,-1],[1,0]]. The rotation matrices commute with J and satisfy
delta R+=R+ J, delta R-=-R- J, delta R0=0. Each rotated base has zero first
moment and spatial second moment cI. Thus M00 is zero in the constant entry,
the cross entries and the spatial block. For M10, its first row is zero and
its first column is zero because delta(sum x)=0. The spatial block is
c R+ J R+^T - c R- J R-^T = cJ-cJ=0. The last moment's spatial block is
c R+ JJ^T R+^T + c R- JJ^T R-^T = 2cI; its other entries vanish.
No distinctness, ordering or transcendence assertion is needed for this lemma.

## Obstruction for arbitrary coefficient tensors

Let B=F tensor_Q F and let m:B->F be multiplication. The Q-bilinear map
(a,b) |-> (delta a)(delta b) induces a Q-linear map Phi:B->F. It need not be
multiplicative or F-linear. For every P in Mat_3(B), the moments imply

    sum_i beta_i Phi((p_i tensor 1)^T P (1 tensor p_i))
       = 2c [m(P_11)+m(P_22)].                         (1)

For a single matrix entry P_(alpha,beta)=a tensor b, expand the relevant term:

    delta(p_i,alpha a) delta(p_i,beta b)
      = (delta p_i,alpha)(delta p_i,beta) ab
        + (delta p_i,alpha)p_i,beta a(delta b)
        + p_i,alpha(delta p_i,beta)(delta a)b
        + p_i,alpha p_i,beta(delta a)(delta b).

After multiplying by beta_i and summing, the four coefficients are respectively
M11, M10, M10^T and M00. The last three vanish. Every tensor is a finite sum of
pure tensors, so Q-linearity proves (1) for arbitrary P, without symmetry or
restricted coefficient assumptions. The checker verifies all four coefficient
slots for all nine matrix entries directly, in addition to the moment matrices.

Consequently no P can have every tensor evaluation equal to zero and multiplied
spatial block I_2: the left side would be zero and the right side 4c, nonzero
in characteristic zero. This is an unconditional algebraic obstruction under
the displayed hypotheses; it does not invoke a Ramsey classification theorem.

## Nine distinct points from an equilateral base

Let t be any real number transcendental over Q with 0<t<1/4, and set

    F=Q(sqrt(3),t),  u=(1-t^2)/(1+t^2),  v=2t/(1+t^2),
    delta = ((1+t^2)/2) d/dt,
    Q={(1,0),(-1/2,sqrt(3)/2),(-1/2,-sqrt(3)/2)}.

Transcendence over Q implies transcendence over Q(sqrt(3)), since that extension
is algebraic. Thus the derivation on the rational function field is well-defined
and fixes sqrt(3). Direct differentiation gives delta u=-v and delta v=u.
The base has zero centroid, unit norms and sum qq^T=(3/2)I. The lemma therefore
gives M11=diag(0,3,3), and the identity spatial block would force 0=6.

Write theta=2 arctan t. Then 0<theta<pi/3, since t<1/4<1/sqrt(3).
An equilateral triangle on the unit circle is unchanged exactly by rotations
through multiples of2pi/3. Differences between the three rotation angles
-theta,0,theta are nonzero and have absolute value at most2theta<2pi/3.
Thus the three triangles are pairwise disjoint: X has exactly nine points,
all on the unit circle. The unrotated triangle affinely spans the plane.

The coordinate field of X is exactly F: its coordinates lie in F; the
unrotated triangle recovers sqrt(3), and the rotation of (1,0) supplies u,v,
from which t=v/(1+u). Here 1+u=2/(1+t^2)>0. Hence the obstruction is over
the actual coordinate field, not an unrelated larger coefficient field.

For a specific parameter one may use the source's Liouville constant
sum_(m>=1)10^(-m!), whose standard transcendence proof and bound
0.11<t<0.12 are reproduced in the pinned source. The finite checker treats
the symbolic parameter; it does not numerically certify transcendence.

## Conditional geometric consequence and predecessor scope

The source's Theorem thm:classification asserts that for an injective finite
configuration affinely spanning the plane, being Euclidean Ramsey is equivalent
to existence of the above tensor matrix with multiplied spatial block I_2.
**Conditional on that source theorem**, this nine-point configuration is not
Ramsey. The algebraic obstruction and distinctness proof above do not verify
the classification theorem, nor does the platform's Proved badge do so here.

OpenAI's Proposition cons:twelve already applies precisely this derivation
mechanism to three square bases (c=2, twelve points, contradiction0=8).
This note extracts the centered-isotropic hypothesis and substitutes a triangle.
It is a small construction refinement and independent exact verification, not
a new general method or a claim of the smallest non-Ramsey set. The same source
discusses earlier seven-point work by Palvolgyi and a separate nine-point
construction using nine algebraically independent parameters. Those earlier
results and OpenAI's construction retain their credit. We have not established
global novelty of the triangle specialization.

At a rational numerical parameter, the displayed symbolic derivative cannot be
reinterpreted as a nonzero derivation of Q: every Q-linear derivation on Q is
zero. At t=0 the three triangles coincide. These are meaningful boundaries;
symbolic identity checks alone must not assert a nine-point non-Ramsey example
at every real specialization.
