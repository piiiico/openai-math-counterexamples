#!/usr/bin/env python3
"""Exact algebra/density evidence for the written all-dimensions proof."""
import argparse
from copy import deepcopy
from fractions import Fraction as F
import hashlib
import json
from math import factorial
from pathlib import Path
import sys
import sympy as sp


def require(condition,message):
    if not condition:
        raise ValueError(message)


def c(d):
    require(type(d) is int and d>=2,'invalid simplex dimension')
    return F((d+1)*d**d,factorial(d))


def encode(value):
    return {'numerator':value.numerator,'denominator':value.denominator}


def decode(value):
    require(isinstance(value,dict) and type(value.get('numerator')) is int and
            type(value.get('denominator')) is int and value['denominator']>0,
            'invalid rational encoding')
    return F(value['numerator'],value['denominator'])


def difference(winner,d):
    return ((winner+1)*winner**winner)**d*factorial(d)**winner-((d+1)*d**d)**winner*factorial(winner)**d


def generate(winner=13):
    require(type(winner) is int and 2<=winner<=19,'invalid density candidate')
    lower,upper=F(2),F(4)
    for _ in range(80):
        middle=(lower+upper)/2
        if middle**winner<=c(winner):lower=middle
        else:upper=middle
    e_lower=sum((F(1,factorial(k)) for k in range(21)),F(0))
    return {'schema_version':1,'winner':winner,'factor_domain':[2,19],
            'comparisons':[{'dimension':d,'difference':difference(winner,d)} for d in range(2,20)],
            'root':{'lower':encode(lower),'upper':encode(upper),'bisection_steps':80},
            'e_terms':20,'e_lower':encode(e_lower),'e_upper':encode(e_lower+F(1,20*factorial(20)))}


def identities(fault=None):
    x,t,s,m,u=sp.symbols('x t s m u',positive=True)
    g=sp.log((x+2)/(x+1))+x*sp.log((x+1)/x)
    derivative=sp.log((x+1)/x)+1/(x+2)-2/(x+1)
    slack=(m+2)**2*(2*m+1)**2-2*(2*m+3)*(m+1)**3
    positive=sp.expand(slack.subs(m,u+1))
    if fault=='split_sign':positive=-positive
    require(all(k>0 for k in sp.Poly(positive,u).all_coeffs()),'split slack has nonpositive coefficient')
    residues=[sp.diff(g,x)-derivative,
              s/(1-t)-s/(1-s)-s*(t-s)/((1-t)*(1-s)),
              t+t*t/(2*(1-t))+t/(1+t)-2*t-t*t*(3*t-1)/(2*(1-t*t)),
              slack-(2*m**3+3*m**2-2*m-2),
              positive-(2*u**3+9*u**2+10*u+1)]
    for residue in residues:
        require(sp.simplify(residue)==0,'symbolic identity fails')
    return len(residues)


def split_ratio(d):
    require(type(d) is int and d>=4,'split requires dimensions at least two')
    return c(d//2)*c(d-d//2)/c(d)


def construct(n):
    require(type(n) is int and n>=2,'invalid total dimension')
    k,r=divmod(n,13)
    if r==0:parts={13:k}
    elif r==1:parts={13:k-1,14:1}
    else:parts={13:k,r:1}
    return {d:count for d,count in parts.items() if count}


def verify(cert):
    require(cert.get('schema_version')==1 and cert.get('factor_domain')==[2,19], 'certificate domain differs')
    winner=cert.get('winner')
    require(type(winner) is int and 2<=winner<=19,'invalid density candidate')
    require([r['dimension'] for r in cert.get('comparisons',[])]==list(range(2,20)),'density coverage incomplete')
    for row in cert['comparisons']:
        d=row['dimension'];gap=difference(winner,d)
        require(type(row['difference']) is int and row['difference']==gap,'integer density certificate differs')
        require(gap==0 if d==winner else gap>0,'density candidate is not the unique winner')
    lower,upper=decode(cert['root']['lower']),decode(cert['root']['upper'])
    require(0<lower<upper and lower**winner<=c(winner)<=upper**winner,'root enclosure is false')
    require(cert.get('e_terms')==20,'unexpected exponential-series domain')
    e_lower=sum((F(1,factorial(k)) for k in range(21)),F(0));e_upper=e_lower+F(1,20*factorial(20))
    require(decode(cert['e_lower'])==e_lower and decode(cert['e_upper'])==e_upper,'exponential enclosure certificate differs')
    require(c(winner)>F(11,4)**winner,'strict excess not certified')
    return {'winner':winner,'rate_lower':lower/e_upper,'rate_upper':upper/e_lower}


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-certificate',type=Path)
    parser.add_argument('--negative-control',choices=['density','split19','split_sign','root'])
    args=parser.parse_args(argv);root=Path(__file__).resolve().parent
    try:
        for item in json.loads((root/'sources.json').read_text())['files']:
            raw=(root/item['local']).read_bytes()
            require(len(raw)==item['bytes'] and hashlib.sha256(raw).hexdigest()==item['sha256'],'source pin differs')
        cert=generate() if args.write_certificate else json.loads((root/'certificate.json').read_text())
        if args.write_certificate:args.write_certificate.write_text(json.dumps(cert,indent=2)+'\n')
        if args.negative_control=='density':cert=generate(12)
        if args.negative_control=='root':
            cert=deepcopy(cert);cert['root']['lower']=encode(F(4));cert['root']['upper']=encode(F(5))
        count=identities(args.negative_control)
        result=verify(cert)
        if args.negative_control=='split19':require(split_ratio(19)>1,'balanced split at dimension19 is not an improvement')
        require(split_ratio(19)<1<split_ratio(20) and split_ratio(21)>1,'split boundary control differs')
        for n in range(2,41):
            parts=construct(n)
            require(sum(d*k for d,k in parts.items())==n and all(d>=2 and k>0 for d,k in parts.items()),'residue control fails')
        require(F(103,100)<result['rate_lower']<result['rate_upper']<F(26,25),'displayed rate interval fails')
        print(json.dumps({'unique_density_winner':result['winner'],'finite_density_obligations':18,
                          'symbolic_identities':count,'rate_rational_enclosure':{key:encode(result[key]) for key in ['rate_lower','rate_upper']},
                          'rate_display_interval':['1.03','1.04'],'split19_ratio':str(split_ratio(19)),
                          'all_dimensions_scope':'Written analytic splitting, equality and residue proof; not inferred from a finite sweep.'},indent=2))
        print('RESULT: density certificate, split identities, rate enclosure and residue controls verified')
        return 0
    except ValueError as error:
        print('RESULT: rejected: '+str(error));return 1


if __name__=='__main__':
    sys.exit(main())
