#!/usr/bin/env python3
"""Independent reviewer-supplied arithmetic and asymmetric-score replay.

Adapted only to explicit failure checks and a negative control. No main-checker
imports. MIT, Alexander Richard Towell; substantial OpenAI Codex assistance.
"""
import argparse
import sys
from collections import defaultdict
from fractions import Fraction as Q
from itertools import product
from math import comb
import flint
from flint import arb,fmpq,ctx


def require(condition,message):
    if not condition:raise ValueError(message)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--negative-control',action='store_true')
    args=parser.parse_args()
    try:
        ctx.prec=384
        q=lambda n,d=1:arb(fmpq(n,d))
        m=2**24+1
        T,c,h,r=q(8),q(3,8),q(1,2**20),q(1,2**33)
        e,b,R=q(1,2**256),q(1,2**85),q(2**64)
        K=T+c+r;lam=1-2*e/b
        d=m*(K*r*r+6*K*e/(b-2*e));eps=h/2+r
        AA=(eps+d)**2+m*r*r;BB=2*(r+d)**2+m*r*r
        central=(AA*((c+eps)**2/2+(c+eps)*T).exp()/(2*r*(c-eps))+2*m*e*AA/b)/lam
        tail_error=8*R*R*e+8/(R*R)+2*e*BB
        tail=((2*(T+1/T)+BB/T)*(((c+r)**2-T*T)/2).exp()/r
              +3*((c+r)**2/2).exp()*tail_error/(2*r))/lam
        gain=c*c-2*c*d-central-tail;mass=(2*r/q(3))*(-K*K/2).exp()
        require((2*arb.pi()).sqrt()<3,'normalization')
        require((2*K*r).exp()<3,'density ratio')
        require(mass>b,'Gaussian mass')
        require(b-2*e>q(1,2**86),'finite mass')
        require(lam>0 and c>eps,'positive denominators')
        require(gain>q(1,5 if args.negative_control else 50),'gain margin')
        require(8*R*R*e==q(1,2**125) and 8/(R*R)==q(1,2**125),'tail terms')
        require(50*m<2**30 and 86*m+30==1442840692,'stage padding')
        print('Python',sys.version.split()[0],'python-flint',flint.__version__,'FLINT',flint.__FLINT_VERSION__)
        for name,ball in [('mass lower',mass),('central',central),('tail',tail),('gain lower',gain),('margin',gain-q(1,50))]:
            print(name,ball.str(70))
        words=list(product((-1,1),repeat=3));cells=defaultdict(list)
        for w in words:cells[w==(1,1,1)].append(sum(w))
        score={label:Q(sum(vals),len(vals)) for label,vals in cells.items()}
        law={score[label]:Q(len(vals),8) for label,vals in cells.items()}
        moment=lambda p:sum(prob*u**p for u,prob in law.items())
        v=moment(2)
        require(moment(1)==0 and v==Q(9,7) and moment(3)==Q(162,49),'asymmetric moments')
        sumcells=defaultdict(list)
        for x,y in product(words,repeat=2):
            z=score[x==(1,1,1)]+score[y==(1,1,1)]
            sumcells[z].append(sum(x)+sum(y))
        require(all(Q(sum(vals),len(vals))==z for z,vals in sumcells.items()),'score tower identity')
        n,L=3,9
        lawL={Q(24*j-3*L,7):Q(comb(L,j)*7**(L-j),8**L) for j in range(L+1)}
        mean=sum(p*x for x,p in lawL.items());m2=sum(p*x*x for x,p in lawL.items())
        m4=sum(p*x**4 for x,p in lawL.items());absolute=sum(p*abs(x) for x,p in lawL.items())
        require(mean==0 and m2==L*v,'summed moments')
        require(m4==L*moment(4)+3*L*(L-1)*v*v,'fourth-moment identity')
        require(m4/(L*v)**2<=Q(n*n,L)/v+Q(3*(L-1),L)<4,'fourth bound')
        require(absolute**2>m2/4,'readout moment')
        print('Asymmetric-law tower and readout controls passed; standardized fourth moment',m4/(L*v)**2)
        an,am,ass,ac=0,0,0,0
        for k in range(7):
            a=(3**k-1)//2
            require((an,am,ass,ac)==(a,k,a-k,a),'stage exponent recurrence')
            an,am,ass,ac=3*an+1,am+1,ass+2*an,ac+2*an+1
        print('Seven stage-exponent controls passed.')
    except ValueError as error:
        print('RESULT: independent replay not certified ('+str(error)+')',file=sys.stderr)
        return 1
    print('RESULT: independent amplification and readout replay certified')
    return 0


if __name__=='__main__':
    raise SystemExit(main())
