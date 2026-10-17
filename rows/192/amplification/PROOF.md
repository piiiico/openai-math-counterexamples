# Explicit copy counts for amplification and Boolean readout

Alexander Richard Towell, with substantial OpenAI Codex assistance.
Written mathematics and finite scalar checks, not a Lean/kernel proof.

## Statement

Fix m=2^24+1, s=m+1, T=8, c=3/8, h=2^-20 and r=2^-33.
Let F be a deterministic finite-valued map on n independent uniform signs,
n>=1; no external randomness is allowed. Write
H for their sum, U_F=E[H|F], v=E[U_F^2], and assume v>=1. Suppose every
value-cell indicator of F has real Boolean Fourier degree at most D>0.

Set M=2^512*n^2. Take s independent blocks, each containing M independent
copies of F, and feed their normalized score sums into the fixed report below.
The new observation F' satisfies

    n' = s M n,
    D' = m M D,
    v' > M v (m + eta),       eta = 2^(-86m)/50.

D' is an upper bound, not a claim of exact degree. In particular v'>=1,
so the operation iterates with the same explicit copy-count formula.

For an integer target A>=1, put E=86m+30=1,442,840,692 and
k=4 A^2 2^E. Start with one observed sign, n_0=D_0=v_0=1. Define

    M_j = 2^512 n_j^2,
    n_(j+1) = s 2^512 n_j^3,
    D_(j+1) = m 2^512 n_j^2 D_j.

After k stages, take L=n_k^2 independent copies of F_k and set f equal to
the sign of the sum of their conditional scores, with sign(0)=1. Then f is
a nonconstant {-1,1}-valued function of n_final=n_k^3 uniform signs, with

    degree(f) <= D_final = n_k^2 D_k,
    sum_i FourierCoefficient(f,{i}) > A sqrt(D_final)
                                     >= A sqrt(degree(f)).

This is an explicit recursive evaluation recipe and cost bound for the source
mechanism. The astronomically large score tables and final function are not
evaluated by this packet. No efficient evaluation or minimal dimension is claimed.

## Uniform normal approximation from bounded scores

Since |H|<=n, conditional expectation gives |U_F|<=n. It is centered,
and v<=n by projection in L2. For Y=U_F/sqrt(v),

    E[Y]=0, E[Y^2]=1,
    E|Y|^3 <= n/sqrt(v) <= n,
    E[Y^4] <= n^2/v <= n^2.

For Z=(Y_1+...+Y_M)/sqrt(M), the classical iid Berry--Esseen theorem,
with the deliberately loose constant one, gives

    sup_t |P(Z<=t)-Phi(t)| <= e := 2^-256.

This uses independent copies of the same F, not independence of the score and
its underlying signs. Shevtsova, arXiv:1111.6554v1, Corollary1 gives a stronger
constant0.4748. It is an inherited classical theorem, not proved here.

Expansion of the fourth power, with all mixed odd terms zero, gives

    E[Z^4] = E[Y^4]/M + 3(M-1)/M < 3+2^-512 < 4.

Consequently for every R>0,

    E[Z^2 1_{|Z|>R}] <= E[Z^4]/R^2 < 4/R^2.

The crucial point is uniformity over all F with v>=1 after the prescribed M.
There is no stage-specific unspecified limit and no inherited subgaussian
assumption on a normalized conditional score.

## Fixed report and quantitative transfer

Index m leaves by -2^23<=j<=2^23 and set I_j=[c+jh-r,c+jh+r].
For a central input U with |U|<=T, choose i(U) as the nearest jh, assigning
ties to the smaller j. Outside [-T,T], choose j=0. Let B be the event that
all leaves pass their intervals and P the event that all unselected leaves
pass. The report has distinct marks on B and on A=P\B, and on P-complement
reports U, its selected index, and every unselected leaf. The input laws are
independent copies of Z. Use predictor mc on B, (m-1)c on A, and the sum
of reported inputs otherwise. All intervals are closed; both cutoff endpoints
belong to the central region.

The Gaussian predecessor certifies, uniformly in j, beta_j^G>b=2^-85 and
|mu_j^G-(c+jh)|<=K r^2, where K=T+c+r. Its density-ratio estimate uses
exp(2Kr)<3. These scalar obligations are rechecked from pinned files.

The CDF bound, including left limits, yields |beta_j-beta_j^G|<=2e.
The restricted first-moment identity on [a,b],

    E[X 1_[a,b](X)] = b F(b)-a F(a-) - integral_a^b F(t)dt,

gives error <=4Ke for endpoints in [-K,K]. Hence

    beta_j > b-2e > 2^-86,
    beta_j >= lambda beta_j^G,       lambda=1-2e/b,
    |mu_j-mu_j^G| <= 6Ke/(b-2e).

The Gaussian centers sum to mc. Thus, with delta=sum_j mu_j-mc,

    |delta| <= d0 := m(Kr^2 + 6Ke/(b-2e)).

Every conditional leaf variance a_j is <=r^2 by support. Put S=sum_j a_j,
Q=product_j beta_j, epsilon=h/2+r,
A0=(epsilon+d0)^2+mr^2 and B0=2(r+d0)^2+mr^2.

For any independent centered variance-one inputs, direct expansion gives

    1-E[(sum inputs - predictor)^2] = Q(c^2+2c delta-J),
    J=E[((U+c+delta-mu_i(U))^2+S-a_i(U))/beta_i(U)].

Indeed ordinary reports contribute exactly P(P-complement) to squared error.
On P the selected leaf remains unrestricted. Treating all P with predictor
(m-1)c gives total error 1+QJ; replacing that predictor by mc on B changes
error by -Q(c^2+2c delta). This also proves the identity for discrete laws.

On each central selector interval the numerator is <=A0, and its probability
differs from its Gaussian value by <=2e. The Gaussian density-ratio integral
therefore gives the central upper bound

    C0 = [A0 exp((c+epsilon)^2/2+(c+epsilon)T)/(2r(c-epsilon))
          + 2m e A0/b] / lambda.

This sums over all m selector cells, including the half-open boundary choices.
The displayed Gaussian bound follows by integrating
exp(cu+epsilon|u|+(c+epsilon)^2/2)/(2r) on [-T,T]; c>epsilon.

Set R=2^64. Restricted second-moment integration on (T,R] and [-R,-T)
gives discrepancy <=4R^2 e, including atoms at +/-R but not +/-T. Thus

    P(|Z|>T) <= 2 phi(T)/T + 2e,
    E[Z^2 1_{|Z|>T}] <= 2(T+1/T)phi(T)+4R^2 e+4/R^2.

On both tails the fallback mean is within r of c, so the numerator is at
most 2U^2+B0. Its finite interval probability is at least
lambda*2r*phi(c+r). With sqrt(2pi)<3, the tail upper bound is

    E_tail = 8R^2 e + 8/R^2 + 2e B0,
    T0 = [(2(T+1/T)+B0/T) exp(((c+r)^2-T^2)/2)/r
          +3 exp((c+r)^2/2) E_tail/(2r)] / lambda.

Here 8R^2 e=8/R^2=2^-125. Exact rational exponential enclosures verify

    c^2 - 2c d0 - C0 - T0 > 1/50.

Projection onto the report cannot have larger squared error than our predictor.
The input sum has variance m+1, so its retained variance is >m+Q/50.
Because Q>2^(-86m), this is >m+eta. The estimates account for all cells,
both tails, all conditional means, and the endpoint atoms.

## Amplification, normalization and complete degree accounting

For each input block, the sum of M conditional scores is a finite numerical
observation. Its score with respect to that block's raw signs is exactly the
same sum: first condition on the tuple of F labels, then on its score sum.
Its normalized value is Z=score_sum/sqrt(Mv). This rescaling is invertible
and does not change cells or their degree bound MD.

For the tuple of s blocks, the total raw-sign conditional score is
sqrt(Mv) times the sum of normalized values. Conditioning further on the
report therefore proves v'>Mv(m+eta).

Every function of one block's M labels has degree at most MD: expand it in
products of the finite cell indicators on disjoint sign blocks. The B cell
uses m input blocks. The A-cell identity is

    1_A=sum_i 1_{i(U)=i} product_{j!=i}1_{I_j}(Z_j)
            - product_j 1_{I_j}(Z_j).

Each summand uses at most m input blocks. Each attained ordinary cell fixes
the central block and m-1 leaves, with one failing leaf among those fixed;
it imposes no condition on the omitted block. All report cells therefore have
degree <=mMD. Empty labels have zero indicators. Numerical score collisions
only add cell indicators and preserve the bound.

All sM copies consume n signs each; no helper randomness or unpriced child
observation is required. Thus n'=sMn and D'=mMD. This is a sign-count and
Fourier-degree accounting, not a CPU-time bound for computing score tables.

## Number of stages and finite Boolean readout

Since 50m<2^30, eta/m>2^-E. The variance-to-degree ratio multiplies by
more than 1+2^-E at each stage. Bernoulli's inequality gives

    v_k/D_k >= (1+2^-E)^k >= 1+k 2^-E = 1+4A^2 >4A^2.

No huge integer or product of rare probabilities need be expanded to check
this identity. For k>=0, put a_k=(3^k-1)/2. Induction solves the size recurrence:

    n_k=(s 2^512)^a_k,
    D_k=m^k s^(a_k-k) 2^(512 a_k),
    D_k/n_k=(m/s)^k.

The exponent a_k-k is nonnegative, since a_0=0 and a_(k+1)=3a_k+1.

The final readout needs no central limit theorem. For any centered score U
with |U|<=n and variance v>=1, take L=n^2 independent copies and put
W=(U_1+...+U_L)/sqrt(Lv). Its fourth moment is

    E[W^4] <= n^2/(Lv)+3(L-1)/L <=4-3/L <4.

Hölder's inequality gives
1=E[W^2] <= (E|W|)^(2/3)(E[W^4])^(1/3), hence E|W|>1/2.
The sign of the score sum is a Boolean function of the L observations, of
degree at most LD. Conditioning on their tuple gives

    sum_i FourierCoefficient(f,{i})
      = E[f H_total] = E|U_1+...+U_L| > sqrt(Lv)/2.

At stage k, v>4A^2D, which proves the claimed violation against sqrt(LD)
and hence against sqrt(degree(f)). The positive coefficient sum implies that
f is nonconstant. The prescribed readout consumes exactly L*n=n^3 signs.

## Exact finite evaluation recipe

The construction does not ask an oracle for a conditional expectation or for
an unspecified sufficiently large integer. F_0 observes its one input sign.
Given a complete finite table for F_j on n_j signs, group inputs by their
labels. In each cell its score is the integer sum of H over the cell divided
by its integer cardinality. The variance is the corresponding exact rational
weighted sum of squared scores. Enumerate all cells, not a sampled subset.

Partition the next input into the specified sM_j ordered blocks; compute their
previous labels and rational scores, then their M_j-fold rational sums. Each
normalized input is a/sqrt(b), with rational a and positive rational b=M_j v_j.
To compare it with a rational endpoint q, first compare signs; if both are
positive compare a^2 with q^2 b, and if both are negative reverse that
comparison. Zero is handled exactly. Selector thresholds are rational
midpoints, with equality assigned to the smaller index. No approximate square
root, finite-precision choice, or inaccessible real parameter is needed.

Ordinary report labels may store the raw rational score sums instead of their
normalized versions; the common nonzero scaling is injective. Use distinct
tags for A, B and ordinary labels. This defines a finite rational-label table
for F_(j+1), so the next conditional-score computation is again finite.
At the final readout compare the rational score sum with zero exactly.

This is a terminating recursive algorithm on each fixed integer target A.
Enumerating even an early full table is infeasible. The packet implements and
tests the scalar obligations and exact comparison primitive, not this enormous
end-to-end evaluation. Table precomputation has no claimed efficient complexity.

## Scope and credit

OpenAI's source already proves the qualitative amplification and readout in
01-observations.tex, and supplies the reporting mechanism and finite transfer
in 03-alternatives.tex and 06-small-width.tex. The dyadic Gaussian and initial
finite-sign packets are preceding contributions by Alexander Richard Towell,
with Codex assistance. Pico/Håkon Åmdal supplied the census and original search.
The quantitative approximation dependency is credited to the classical
Berry--Esseen theorem and Shevtsova's explicit constant.

The addition is a uniform copy-count bound, complete recursive budget and
elementary explicit readout bound for that mechanism. It is not a new
unbounded-violation theorem, a globally novel moment inequality, a computed
truth table or a verified Lean development. A comparator target with `sorry`
is a statement, not a kernel proof. Independent AI review and finite controls
do not formally verify the quantified written argument. The census remains
unchanged pending the maintainer's interpretation of its checkability scope.
