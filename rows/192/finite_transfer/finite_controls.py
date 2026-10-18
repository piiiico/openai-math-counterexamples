"""Exact small discrete controls, not an enumeration of N=2^512 inputs.

Copyright 2026 Alexander Richard Towell. MIT licensed; substantial Codex assistance.
"""
from fractions import Fraction as F
from itertools import product
from math import comb, isqrt, prod


def require(condition, message):
    if not condition:
        raise ValueError(message)


def binomial_law(n):
    root = isqrt(n)
    require(root*root == n and n > 0, 'control block size must be a positive square')
    law = tuple((F(2*k-n,root),F(comb(n,k),2**n)) for k in range(n+1))
    require(sum(p for x,p in law)==1, 'binomial mass')
    require(sum(x*p for x,p in law)==0, 'binomial mean')
    require(sum(x*x*p for x,p in law)==1, 'binomial variance')
    return law


def selector(t):
    grid=(-1,0,1)
    return min(range(3),key=lambda i:(abs(t-grid[i]),i)) if abs(t)<=1 else 1


def interval_moments(law, left, right):
    restricted=[(x,p) for x,p in law if left<=x<=right]
    beta=sum((p for x,p in restricted),F(0))
    require(beta>0, 'control interval must have positive mass')
    mean=sum(x*p for x,p in restricted)/beta
    variance=sum((x-mean)**2*p for x,p in restricted)/beta
    return beta,mean,variance


def report_control(central_n, corrupt=False):
    central,leaf=binomial_law(central_n),binomial_law(4)
    c,r,m=F(1,2),F(1,2),3
    intervals=tuple((c+j-r,c+j+r) for j in (-1,0,1))
    moments=tuple(interval_moments(leaf,*interval) for interval in intervals)
    betas,means,variances=zip(*moments)
    Q=prod(betas);delta=sum(means)-m*c;S=sum(variances)
    J=sum(p*((t+c+delta-means[selector(t)])**2+S-variances[selector(t)])
          /betas[selector(t)] for t,p in central)
    expected=Q*(c*c+(3 if corrupt else 2)*c*delta-J)
    error=F(0);groups={};count=0
    for weighted in product(central,leaf,leaf,leaf):
        point=tuple(x for x,p in weighted);weight=prod(p for x,p in weighted)
        t,*leaves=point;i=selector(t);L=sum(point)
        passes=[left<=x<=right for x,(left,right) in zip(leaves,intervals)]
        if all(passes):
            label=('B',);predictor=m*c
        elif all(passes[j] for j in range(m) if j!=i):
            label=('A',);predictor=(m-1)*c
        else:
            observed=tuple(leaves[j] for j in range(m) if j!=i)
            label=('ordinary',t,i,observed);predictor=t+sum(observed)
        error+=weight*(L-predictor)**2
        mass,score=groups.get(label,(F(0),F(0)))
        groups[label]=(mass+weight,score+weight*L);count+=1
    direct=1-error
    require(direct==expected, 'exact discrete deficit identity failed')
    retained=sum(score*score/mass for mass,score in groups.values())
    require(retained>=m+direct, 'conditional expectation did not improve predictor')
    require(retained<=m+1, 'retained variance exceeds total variance')
    require(sum(mass for mass,score in groups.values())==1, 'report cells do not partition')
    return {'central_block':central_n,'leaf_blocks':4,'weighted_input_tuples':count,
            'report_cells':len(groups),'deficit':str(direct),'retained_variance':str(retained),
            'interval_atoms_included':True,'identity_checked_exactly':True}


def restricted_moment_controls():
    a,b=binomial_law(4),binomial_law(16)
    points=sorted({x for x,p in a}|{x for x,p in b})
    def cdf(law,t,closed):
        return sum((p for x,p in law if (x<=t if closed else x<t)),F(0))
    e=max(abs(cdf(a,t,closed)-cdf(b,t,closed)) for t in points for closed in (False,True))
    checked=0
    for left in points:
        for right in points:
            if left>right: continue
            K=max(abs(left),abs(right))
            for closed_left,closed_right in product((False,True),repeat=2):
                def moment(law,k):
                    return sum((x**k*p for x,p in law
                                if (x>=left if closed_left else x>left)
                                and (x<=right if closed_right else x<right)),F(0))
                require(abs(moment(a,0)-moment(b,0))<=2*e, 'interval CDF control')
                require(abs(moment(a,1)-moment(b,1))<=4*K*e, 'restricted first-moment control')
                checked+=1
    for T,R in [(F(1,2),F(3,2)),(F(1),F(2)),(F(2),F(4))]:
        difference=abs(sum((x*x*p for x,p in a if T<abs(x)<=R),F(0))
                       -sum((x*x*p for x,p in b if T<abs(x)<=R),F(0)))
        require(difference<=4*R*R*e, 'restricted second-moment control')
    return {'interval_endpoint_cases':checked,'two_sided_second_moment_cases':3,
            'exact_CDF_distance':str(e)}


def run_controls(corrupt=False):
    require(selector(F(-1,2))==0 and selector(F(1,2))==1, 'lower-index tie convention')
    return {'reports':[report_control(n,corrupt) for n in (4,16)],
            'restricted_moments':restricted_moment_controls(),
            'scope':'complete small weighted binomial examples; not proof by sampling or large-N enumeration'}
