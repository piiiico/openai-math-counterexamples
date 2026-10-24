"""Reviewer arithmetic and finite corroboration; no main-checker imports.

Original algorithm preserved. Explicit exceptions replace assertions for -O.
The DP to120 corroborates the written theorem; it cannot prove its all-n tail.
"""
from fractions import Fraction
from math import factorial


def require(condition,message):
    if not condition:
        raise ValueError(message)


def c(d):
    return Fraction((d+1)*d**d,factorial(d))


for d in range(2,20):
    gap=c(13)**d-c(d)**13
    require(gap==0 if d==13 else gap>0,'density sign differs')
require(c(10)**2/c(20)==Fraction(5588869,5505024),'even base differs')
require(c(9)*c(10)<c(19),'dimension19 boundary differs')
require(c(10)**2>c(20) and c(10)*c(11)>c(21),'split base fails')
require(c(13)>Fraction(11,4)**13,'strict excess fails')


def mul(a,b):
    out=[0]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b):out[i+j]+=x*y
    return out


lhs=mul(mul([2,1],[2,1]),mul([1,2],[1,2]))
rhs=mul([6,4],mul(mul([1,1],[1,1]),[1,1]))
require([x-y for x,y in zip(lhs,rhs)]==[-2,-2,3,2,0],'split polynomial differs')
M={0:Fraction(1)};witnesses={0:{()}}
for n in range(2,121):
    candidates=[(c(d)*M[n-d],d) for d in range(2,n+1) if n-d in M]
    M[n]=max(value for value,_ in candidates)
    witnesses[n]={tuple(sorted((d,)+tail)) for value,d in candidates if value==M[n] for tail in witnesses[n-d]}
    require(M[n]**13<=c(13)**n,'finite upper bound differs')
    require((M[n]**13==c(13)**n)==(n%13==0),'finite equality classification differs')
    require(all(max(parts)<=19 for parts in witnesses[n]),'large optimal factor found')
    if n>=14:
        k,r=divmod(n,13)
        parts=([13]*k if r==0 else [13]*(k-1)+[14] if r==1 else [13]*k+[r])
        require(sum(parts)==n and min(parts)>=2,'residue witness fails')
print('RESULT: independent density, split algebra and finite dimensions2..120 corroboration pass')
