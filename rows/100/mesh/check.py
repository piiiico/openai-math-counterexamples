#!/usr/bin/env python3
"""Exact algebra and parameter budgets; continuum coverage uses PROOF.md."""
from fractions import Fraction as F
from pathlib import Path
import argparse
import hashlib
import json
import sys
import sympy as sp


def budget(tau, eta, gap):
    if not (0 < tau < 1 and 0 <= eta <= F(1, 8) and 0 < gap <= 2):
        raise ValueError('invalid tilt, margin or mesh bound')
    coverage_gap = 2*eta - (F(7,4)+2*eta)*tau - gap/(4*tau) - gap/4
    saving = (F(1,240)-2*eta)*tau**2-F(59,64)*tau**4-tau**2*gap
    if coverage_gap < 0:
        raise ValueError('sufficient coverage budget fails; not a counterexample')
    if saving <= 0:
        raise ValueError('strict area saving not certified')
    return {'coverage_gap': coverage_gap, 'area_saving': saving}


def identities(fault=None):
    l,r,q,p,x,y,t,e,aj,ak,bj,bk,eta,D=sp.symbols('l r q p x y t e aj ak bj bk eta D')
    alpha=(1+l*r)/4; beta=(l+r)/4
    d=lambda z:z*z*(1+z*z)/16
    phi=lambda z:(1-z*z)/4
    Aq=(1+q*q)**2/16+q*q/2
    t0=t-e*x*bj; s0=1-t+e*y*bk
    a=t0-sp.Rational(1,2); b=s0-sp.Rational(1,2)
    radial=a*(1-e*x*q)+b*(1+e*y*p)-(e*e*(x*x*aj+y*y*ak)-e*x*(bj-q/2)+e*y*(bk-p/2))
    if fault=='radial_sign': radial+=2*e*x*(bj-q/2)
    radial=radial.subs({q:(y-e*x*aj)/t0,p:(x+e*y*ak)/s0})
    A,M,z=sp.symbols('A M z',nonnegative=True)
    f=(sp.Rational(1,2)+M*z)**2/sp.sqrt(1+A*z)
    second=2*M*M/sp.sqrt(1+A*z)-2*A*M*(sp.Rational(1,2)+M*z)/(1+A*z)**sp.Rational(3,2)+3*A*A*(sp.Rational(1,2)+M*z)**2/(4*(1+A*z)**sp.Rational(5,2))
    G=2*eta-(sp.Rational(7,4)+2*eta)*e-D/(4*e)-D/4
    residues={
        'left shared side':alpha-l*beta-phi(l)+(2*l*beta if fault=='secant_sign' else 0),
        'right shared side':alpha-r*beta-phi(r),
        'radial budget':radial,
        'quartic majorant':d(p)+d(q)-(p*p+q*q+2*p*p*q*q)/16-(p*p-q*q)**2/16,
        'd derivative':sp.diff(d(q),q)-(q+2*q**3)/8,
        'integral d':sp.integrate(d(q),(q,-1,1))-sp.Rational(1,15),
        'integral A':sp.integrate(Aq,(q,-1,1))-(sp.Rational(17,30) if fault!='integral' else sp.Rational(16,30)),
        'Taylor second derivative':sp.diff(f,z,2)-second,
        'coverage lower bound':(2*eta+d(p)+d(q))*(1-e)-D/(4*e)-(d(p)+d(q)+sp.Rational(3,2)*e+D/4)-G-e*(sp.Rational(1,4)-d(p)-d(q)),
    }
    for name,residue in residues.items():
        if sp.simplify(residue)!=0:
            raise ValueError('identity fails: '+name)
    return len(residues)


def first_crossing(values,target):
    if len(values)<2 or not values[0]<=target<=values[-1]:
        raise ValueError('endpoints do not bracket target')
    for i in range(1,len(values)):
        if values[i]>=target:
            return i-1
    raise ValueError('no crossing')


def covered(point,nodes,tau,eta,enlarge=True):
    x,y,t=point
    if len(nodes)<2 or nodes[0]!=-1 or nodes[-1]!=1 or any(a>=b for a,b in zip(nodes,nodes[1:])):
        raise ValueError('invalid partition')
    if not (0<=t<=1 and abs(x)<=1-t and abs(y)<=t):
        raise ValueError('point outside tetrahedron')
    for l,r in zip(nodes,nodes[1:]):
        alpha=(1+l*r)/4;beta=(l+r)/4
        d=lambda q:q*q*(1+q*q)/16
        cap=F(1,2)+tau*tau*(eta+max(d(l),d(r))) if enlarge else F(1,2)
        t0=t-tau*x*beta;y0=y-tau*x*alpha
        s0=1-t+tau*y*beta;x0=x+tau*y*alpha
        if 0<=t0<=cap and l*t0<=y0<=r*t0:return True
        if 0<=s0<=cap and l*s0<=x0<=r*s0:return True
    return False


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--negative-control',choices=['radial_sign','secant_sign','integral','mesh','area'])
    args=parser.parse_args(argv)
    try:
        root=Path(__file__).resolve().parent
        for item in json.loads((root/'sources.json').read_text())['files']:
            raw=(root/item['local']).read_bytes()
            if len(raw)!=item['bytes'] or hashlib.sha256(raw).hexdigest()!=item['sha256']:
                raise ValueError('source hash mismatch')
        count=identities(args.negative_control)
        if args.negative_control=='mesh':budget(F(1,2000),F(1,1000),F(1,1000))
        if args.negative_control=='area':budget(F(1,100),F(1,8),F(1,10000))
        result=budget(F(1,2000),F(1,1000),F(1,500000))
        point=(F(1,10),F(3,10),F(21,40));nodes=[F(-1),F(0),F(1)]
        if covered(point,nodes,F(1,2),F(0),False) or not covered(point,nodes,F(1,2),F(0)):
            raise ValueError('uncovered-point control failed')
        output={'symbolic_identities':count,'sector_count_per_family':1000000,'cylinders':2000000,**{k:str(v) for k,v in result.items()},'unenlarged_control_point':[str(v) for v in point],'scope':'Written continuum proof plus exact algebra/budget checks; no finite sampling claim of universal coverage.'}
        print(json.dumps(output,indent=2))
        print('RESULT: mesh-aware algebra, complete budgets and uncovered-point control verified')
        return 0
    except ValueError as error:
        print('RESULT: rejected: '+str(error))
        return 1


if __name__=='__main__':
    sys.exit(main())
