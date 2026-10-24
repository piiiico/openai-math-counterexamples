"""Independent reviewer sector-sum and barycentric replay; no checker imports.

Reviewer's algorithm preserved; assertions replaced by explicit rejection so
failure checks remain active under python -O. Symbolic dependency is shared.
"""
import json
import sympy as s


def require(condition, message):
    if not condition:
        raise ValueError(message)


k = s.symbols('k', integer=True, nonnegative=True)
n = 1_000_000
tau = s.Rational(1, 2000)
eta = s.Rational(1, 1000)
h = s.Rational(2, n)
l, r = h*k, h*(k+1)
alpha = (1+l*r)/4
beta = (l+r)/4
T = s.Rational(1, 2)+tau**2*(eta+r*r*(1+r*r)/16)
z = tau**2*(alpha**2+2*beta**2)


def exact_sector_sum(poly):
    return 2*h*sum(coefficient*s.summation(k**powers[0], (k, 0, n//2-1))
                   for powers, coefficient in s.Poly(poly, k).terms())


lower = exact_sector_sum(T*T*(1-z/2))
upper = exact_sector_sum(T*T*(1-z/2+3*z*z/8))
claimed_saving = s.Rational(1662287, 3072000000000000)
require(lower <= upper < s.Rational(1, 2)-claimed_saving, 'area enclosure fails')
print(json.dumps({'area_lower':str(lower), 'area_upper':str(upper),
                  'positive_saving_lower':str(s.Rational(1,2)-upper)}, indent=2))
point = s.Matrix([s.Rational(1,10),s.Rational(3,10),s.Rational(21,40)])
for enlarged in (False,True):
    memberships=[]
    for left,right in ((-1,0),(0,1)):
        a=s.Rational(1+left*right,4); b=s.Rational(left+right,4)
        e=s.Rational(1,2)
        d=lambda q:s.Rational(q*q*(1+q*q),16)
        cap=s.Rational(1,2)+(e*e*max(d(left),d(right)) if enlarged else 0)
        for family in ('lower','upper'):
            if family=='lower':
                origin=s.zeros(3,1);v1=s.Matrix([0,left*cap,cap]);v2=s.Matrix([0,right*cap,cap]);axis=s.Matrix([1,e*a,e*b])
            else:
                origin=s.Matrix([0,0,1]);v1=s.Matrix([left*cap,0,-cap]);v2=s.Matrix([right*cap,0,-cap]);axis=s.Matrix([-e*a,1,e*b])
            u,v,w=s.Matrix.hstack(v1,v2,axis).inv()*(point-origin)
            inside=bool(u>=0 and v>=0 and u+v<=1);memberships.append(inside)
            print(enlarged,(left,right),family,(u,v,1-u-v),inside)
    require(memberships==([False,False,True,True] if enlarged else [False]*4),'barycentric membership differs')
for sectors,expected in ((890124,False),(890125,True)):
    D=s.Rational(2,sectors);G=2*eta-(s.Rational(7,4)+2*eta)*tau-D/(4*tau)-D/4
    require(bool(G>=0)==expected,'budget threshold differs')
    print('Threshold:',sectors,G)
print('RESULT: independent finite area enclosure and barycentric controls verified')
