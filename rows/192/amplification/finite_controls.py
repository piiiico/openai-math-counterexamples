"""Exact small controls; no evaluation of the target recursive Boolean function.

Copyright 2026 Alexander Richard Towell. MIT; substantial OpenAI Codex assistance.
"""
from collections import defaultdict
from fractions import Fraction as F


def require(condition,message):
    if not condition:
        raise ValueError(message)


def signum(x):
    return (x>0)-(x<0)


def compare_normalized(a,b,q):
    """Compare a/sqrt(b) with q exactly, for rational a,q and positive rational b."""
    a,b,q=F(a),F(b),F(q)
    require(b>0,'positive normalization is required')
    sa,sq=signum(a),signum(q)
    if sa!=sq:return signum(sa-sq)
    if sa==0:return 0
    return sa*signum(a*a-q*q*b)


def coefficients(values):
    size=len(values);n=size.bit_length()-1
    require(size==1<<n,'truth table length must be a power of two')
    return tuple(sum(value*(-1 if (mask&x).bit_count()%2 else 1)
                     for x,value in enumerate(values))/F(size) for mask in range(size))


def degree(values):
    return max((mask.bit_count() for mask,value in enumerate(coefficients(values)) if value),default=0)


def observation(n,label):
    groups=defaultdict(list)
    for x in range(1<<n):groups[label(x)].append(x)
    scores=[F(0)]*(1<<n);law=defaultdict(F);D=0
    for cell in groups.values():
        score=F(sum(n-2*x.bit_count() for x in cell),len(cell))
        for x in cell:scores[x]=score
        law[score]+=F(len(cell),1<<n)
        points=set(cell);D=max(D,degree([int(x in points) for x in range(1<<n)]))
    return {'n':n,'scores':tuple(scores),'law':dict(law),'degree':D}


def convolve(law,copies):
    current={F(0):F(1)}
    for _ in range(copies):
        next_law=defaultdict(F)
        for x,p in current.items():
            for y,q in law.items():next_law[x+y]+=p*q
        current=dict(next_law)
    return current


def moment(law,k):
    return sum((x**k*p for x,p in law.items()),F(0))


def check_score_law(obs):
    n,law=obs['n'],obs['law'];v=moment(law,2);fourth=moment(law,4)
    require(v>=1,'score law must have variance at least one')
    require(moment(law,0)==1 and moment(law,1)==0,'score law mass or mean')
    require(v<=n and all(abs(x)<=n for x in law),'score projection bounds')
    require(sum(abs(x)**3*p for x,p in law.items())<=n*v,'third absolute-moment bound')
    require(fourth<=n*n*v,'fourth-moment bound')
    for copies in (1,2,3,4):
        summed=convolve(law,copies)
        require(moment(summed,1)==0 and moment(summed,2)==copies*v,'summed score moments')
        require(moment(summed,4)==copies*fourth+3*copies*(copies-1)*v*v,'fourth-moment identity')
    copies=n*n;summed=convolve(law,copies)
    absolute=sum(abs(x)*p for x,p in summed.items())
    require(moment(summed,4)<4*copies*copies*v*v,'readout fourth-moment estimate')
    require(absolute*absolute>copies*v/4,'readout half bound')
    return {'n':n,'variance':str(v),'degree':obs['degree'],'readout_copies':copies,
            'readout_mean_absolute_sum':str(absolute),'fourth_identity_cases':4}


def score_law_controls():
    observations=[observation(1,lambda x:x),observation(3,lambda x:x&1),
                  observation(2,lambda x:x==0),observation(4,lambda x:x==0)]
    reports=[check_score_law(o) for o in observations]
    law=observations[-1]['law'];v=moment(law,2);absolute=sum(abs(x)*p for x,p in law.items())
    require(absolute*absolute<v/4,'one-copy negative example did not fail')
    return {'examples':reports,'fourth_identity_cases':sum(r['fourth_identity_cases'] for r in reports),
            'one_copy_counterexample':{'n':4,'observation':'whether all four signs are +1',
                                      'variance':str(v),'mean_absolute_score':str(absolute),
                                      'half_bound_fails':True}}


def comparison_controls(corrupt=False):
    checked=0
    for root in (F(1),F(2),F(3,2)):
        for i in range(-5,6):
            for j in range(-5,6):
                a,q=F(i,3),F(j,7)
                result=compare_normalized(a,root*root,q)
                if corrupt and a<0:result=-result
                require(result==signum(a/root-q),'exact normalization comparison failed')
                checked+=1
    for a,q,expected in [(1,F(7,10),1),(1,F(5,7),-1),(-1,F(-7,10),-1),(-1,F(-5,7),1),(0,F(0),0)]:
        require(compare_normalized(a,2,q)==expected,'irrational comparison failed');checked+=1
    return {'exact_comparison_cases':checked,'scope':'rational-square controls plus irrational sqrt(2) boundaries'}


def fourier_controls(corrupt=False):
    observations=[observation(3,lambda x:x&1),observation(2,lambda x:x==0),observation(4,lambda x:x==0)]
    reports=[]
    for obs in observations:
        n=obs['n'];copies=2;ambient=n*copies;values=[];absolute=F(0)
        for x in range(1<<ambient):
            score=sum(obs['scores'][(x>>(n*j))&((1<<n)-1)] for j in range(copies))
            values.append(1 if score>=0 else -1);absolute+=abs(score)/F(1<<ambient)
        coeff=coefficients(values)
        singleton=sum(coeff[1<<j] for j in range(ambient))
        require(singleton==absolute,'readout Fourier/tower identity failed')
        actual=degree(values);bound=copies*(obs['degree']-(1 if corrupt else 0))
        require(actual<=bound,'readout degree accounting failed')
        reports.append({'ambient_signs':ambient,'truth_table_entries':1<<ambient,
                        'actual_degree':actual,'degree_upper':bound,'singleton_sum':str(singleton)})
    return {'examples':reports,'truth_table_entries':sum(r['truth_table_entries'] for r in reports)}


def recurrence_controls(corrupt=False):
    checked=0
    for m in (1,2,3):
        s=m+1
        for copy_log2 in (0,1,2):
            q=1<<copy_log2;n=D=1
            for k in range(4):
                a=(3**k-1)//2
                require(a>=k and n==(s*q)**a,'sign recurrence closed form')
                require(D==m**k*s**(a-k)*q**a,'degree recurrence closed form')
                require(F(D,n)==F(m,s)**k,'degree/dimension ratio recurrence')
                checked+=1;M=q*n*n
                n,D=s*M*n,(s if corrupt else m)*M*D
    return {'small_recurrence_cases':checked,'scope':'finite controls of formulas; full induction is written in PROOF.md'}


def run_controls():
    return {'score_laws':score_law_controls(),'comparisons':comparison_controls(),
            'fourier':fourier_controls(),'recurrences':recurrence_controls(),
            'scope':'complete stated small domains; no target Boolean truth table evaluated'}
