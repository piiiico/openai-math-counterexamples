# One explicit finite-sign observation stage

Alexander Richard Towell, with substantial OpenAI Codex assistance.
Written proof plus an exact scalar certificate; not a Lean proof.

## Statement and complete input cost

Keep the predecessor's rational schedule

`m=2^24+1`, `T=8`, `c=3/8`, `h=2^-20`, `r=2^-33`.

For each of the m+1 inputs use an independent block of **N=2^512** uniform
signs and set `Z=N^(-1/2) sum(signs)`. Thus Z has mean zero, variance one
and a finite dyadic alphabet; `sqrt(N)=2^256`. The total sign count is
`(m+1)N`. This is an explicit, enormous construction, not an efficient one.

Index leaves by `-2^23 <= j <= 2^23` and give leaf j the closed interval
`I_j=[c+jh-r,c+jh+r]`. On `|U|<=T`, select the nearest jh, with ties
assigned to the smaller j. Outside that range select j=0. Put B equal to
the event that every leaf passes, P equal to the event that every unselected
leaf passes, and A=P\B. The report returns a distinct mark on A or B and,
on P-complement, returns U, its selected index and all unselected leaves.
Use the fixed rational predictors `(m-1)c` on A, `mc` on B, and the sum of
reported coordinates otherwise. Let L be the sum of the normalized inputs.

We prove

`Var(E[L | report]) > m + Q_N/50`,

where `Q_N=product_j P(Z in I_j) > 2^(-86m)` and `86m=1,442,840,662`.
For the sum H of all raw signs this becomes

`Var(E[H | report]) > mN + N*Q_N/50`.

Every report-cell indicator has Boolean Fourier degree at most **mN**.
Indeed the exceptional-cell identity

`1_A = sum_i 1_{selector(U)=i} product_{j!=i} 1_{I_j}(Z_j)
       - product_j 1_{I_j}(Z_j)`

uses at most m normalized input blocks in each summand. The B cell ignores U.
An attained ordinary report fixes U and m-1 leaves, at least one of which
fails; it therefore imposes no restriction on the omitted leaf. Its indicator
also depends on at most m blocks. Any function of m blocks of N signs has
Fourier degree at most mN. Empty report labels have zero indicator. All
normalization, ties, interval boundaries and predictors use exact rational
comparisons; no numerical precision or helper randomness is implicit.

This supplies one finite observation with retained variance larger than its
cell-degree budget. Subsequent amplification and final Boolean sign readout
are not supplied, so this is not the full Family 192 Boolean counterexample.

## Classical approximation dependency and elementary tail bound

For iid uniform signs, the Berry--Esseen theorem gives

`sup_t |P(Z<=t)-Phi(t)| <= e`, where `e=N^(-1/2)=2^-256`.

We use only the loose constant 1. A primary reference is Irina Shevtsova,
*On the absolute constants in the Berry--Esseen type inequalities for
identically distributed summands*, arXiv:1111.6554v1 (2011), Corollary 1,
which gives the stronger constant 0.4748. The third absolute moment of each
sign is one. That paper uses left-continuous distribution functions; taking
right limits gives the same bound for the right-continuous convention above,
because Phi is continuous. Berry--Esseen is an inherited classical theorem,
not proved or kernel-checked by this packet.

The subgaussian estimate needed below has a direct proof. The inequality
`log cosh(t)<=t^2/2` follows by integrating `tanh(t)<=t` for t>=0 and
using evenness. Therefore `E exp(tZ)<=exp(t^2/2)`. Markov's inequality,
with parameter t=s, and the same argument for -Z give

`P(|Z|>s) <= 2 exp(-s^2/2)`.

Integrating this tail bound yields

`E[Z^2 1_{|Z|>R}] <= 2(R^2+2) exp(-R^2/2)`.

Specifically, the expectation equals
`R^2 P(|Z|>R) + integral_R^infinity 2s P(|Z|>s) ds`, also for atoms.
We choose R=16 and use the weaker rational upper bound
`s_R=2^(-floor(R^2/2))=2^-128` for `exp(-R^2/2)`. Euler's number is
greater than two, so this inequality has the required direction.

## Interval and restricted-moment estimates, including atoms

If two CDFs differ by at most e, and the second law is continuous, the same
bound holds for left limits. Every interval, with any choice of open or
closed endpoints, consequently has probability discrepancy at most 2e.

For a closed interval [a,b], integration of a restricted first moment gives

`E[X 1_[a,b](X)] = b F(b)-a F(a-) - integral_a^b F(t) dt`.

Subtract the two formulas. For `a,b in [-K,K]` the discrepancy is at most
`(|a|+|b|+b-a)e <= 4Ke`. Open endpoints use the corresponding one-sided
CDF and obey the same bound. For the positive interval `(T,R]`, the analogous
second-moment formula gives discrepancy at most
`(R^2+T^2+integral_T^R 2t dt)e = 2R^2 e`.
Applying it also to `[-R,-T)` gives

`|E[Z^2 1_{T<|Z|<=R}]-E[G^2 1_{T<|G|<=R}]| <= 4R^2 e`.

Here G is a standard normal. In particular,

`P(|Z|>T) <= 2 phi(T)/T + 2e`,

`E[Z^2 1_{|Z|>T}] <= 2(T+1/T)phi(T) + 4R^2 e + 2(R^2+2)s_R`.

The Gaussian estimates follow by integration by parts and the usual
`integral_T^infinity phi(t)dt <= phi(T)/T`. We upper bound the truncated
Gaussian second moment by its full tail moment, and add the finite-law
tail beyond R. No convergence limit remains in these estimates.

## Uniform leaf bounds

Set `K=T+c+r`, `b=2^-85`, `rho=2e/b` and `lambda=1-rho`.
The predecessor's exact Gaussian certificate proves, uniformly in j,

`beta_j^G > b`, `|mu_j^G-(c+jh)| <= K r^2`.

The latter follows from the verified density-ratio bound
`exp(2Kr)<3`; its written derivation is preserved in the predecessor.
The interval discrepancy gives

`beta_j^N > b-2e > 0`, `beta_j^N >= lambda beta_j^G`.

For the conditional means, the first-moment estimate and `|mu_j^G|<=K`
give

`|mu_j^N-mu_j^G| <= (4Ke+2Ke)/(b-2e)`.

The interval centers sum to mc. Thus, writing
`delta=sum_j mu_j^N-mc`, we have

`|delta| <= D_N := m*(K r^2+6Ke/(b-2e))`.

All conditional variances are at most r^2, simply from their supports.
The checker verifies `b-2e > 2^-86`, giving the claimed product lower bound.
Neither Q_N nor an exponentially large binomial table is explicitly formed.

## Exact deficit and quantitative budget

Let `a_j` be the conditional leaf variances and `S=sum_j a_j`. Independence
and the fixed predictors give the same exact identity as the predecessor:

`1-E[(L-predictor)^2] = Q_N*(c^2+2c delta-J_N)`,

where

`J_N=E[((U+c+delta-mu_{i(U)}^N)^2+S-a_{i(U)})/beta_{i(U)}^N]`.

This identity uses only centered, variance-one independent inputs. Ordinary
reports contribute exactly P(P-complement) to squared error; on P, the
omitted leaf is unrestricted. On B, U is unrestricted. Subtracting the
P predictor contribution on B and replacing it by the B predictor gives
the displayed expression. Thus no Gaussian theorem is used to assert it
for finite inputs. The finite controls verify this identity independently
on small exact discrete examples, including atoms at interval endpoints.

Put `epsilon=h/2+r`, `A_N=(epsilon+D_N)^2+mr^2`, and
`B_N=2(r+D_N)^2+mr^2`. On [-T,T], the numerator defining J_N is at
most A_N. Each clipped selector cell is an interval, so its mass differs
from its Gaussian mass by at most 2e. The Gaussian density-ratio integral
from the predecessor, with D_N in place of D, then gives

`C_N = [ A_N*exp((c+epsilon)^2/2+(c+epsilon)T)/(2r(c-epsilon))
         + 2me*A_N/b ] / lambda`

as an upper bound for the central contribution. The m-cell error sum uses
`beta_j^G>b`; it covers the entire selector partition, not sampled cells.

On the tails, the fallback interval has mean within r of c, so its numerator
is at most `2U^2+B_N`. Its Gaussian probability is at least
`2r phi(c+r)`, and its finite probability is at least lambda times that.
Define

`E_tail = 8R^2 e + 4(R^2+2)s_R + 2e B_N`.

The previous moment bounds, and `sqrt(2pi)<3`, give the tail upper bound

`T_N = [ (2(T+1/T)+B_N/T)*exp(((c+r)^2-T^2)/2)/r
         + 3*exp((c+r)^2/2)*E_tail/(2r) ] / lambda`.

The scalar checker verifies using exact rational exponential enclosures that

`c^2 - 2c D_N - C_N - T_N > 1/50`.

It follows that the specified predictor's error is less than `1-Q_N/50`.
Conditional expectation minimizes squared error and Var(L)=m+1, proving
the stated retained-variance bound. Multiplying by N gives the raw-sign
statement. Every block, both tails, interval boundary and cell-degree cost
has been accounted for.

## Scope and credit

The reporting partition, factorization by Q and qualitative restricted-moment
transfer are OpenAI's Family 192 source work, especially
`03-alternatives.tex:42-81` and `06-small-width.tex:193-270`, at commit
`1581d4cbdd69a0faf34b2089614fe2a814316a6a`. The fixed dyadic Gaussian schedule
and exact exponential checker are the predecessor packet, public head
`71f02660684fe63b82b55ada1fff81b66baa0afa`. Pico/Håkon Åmdal supplied the
existing census and small-Boolean search. The classical normal-approximation
input is credited above. None of these mechanisms is claimed as new.

The addition is a concrete averaging count and a quantitative, checkable
error budget for this fixed stage. It does not claim minimal N, efficient
construction, a global novelty theorem, or a complete explicit Boolean
counterexample. Exact scalar computation supports the written probability
argument but does not formally verify it or reprove Berry--Esseen. Separate
AI review is not human peer review.
