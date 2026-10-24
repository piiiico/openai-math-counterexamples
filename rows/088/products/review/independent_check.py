"""Separately tasked reviewer's multiplicity-vector knapsack/count oracle.

Preserved algorithm; explicit exceptions replace assertions for python -O.
Does not import either coordinating implementation. Shares Python/Fraction.
"""
import json
from fractions import Fraction
from math import factorial
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
certificate=json.loads((ROOT/'certificate.json').read_text())
enumeration=json.loads((ROOT/'enumeration.json').read_text())


def require(condition,message):
    if not condition:
        raise ValueError(message)


values=[Fraction(0)]*41
values[0]=Fraction(1)
witnesses=[set() for _ in range(41)]
witnesses[0]={()}
counts=[0]*41
counts[0]=1
for factor in range(2,41):
    constant=Fraction((factor+1)*factor**factor,factorial(factor))
    for dimension in range(factor,41):
        counts[dimension]+=counts[dimension-factor]
        candidate=values[dimension-factor]*constant
        if candidate>values[dimension]:
            values[dimension]=candidate
            witnesses[dimension]={tuple(sorted(parts+(factor,))) for parts in witnesses[dimension-factor]}
        elif candidate==values[dimension] and candidate:
            witnesses[dimension]|={tuple(sorted(parts+(factor,))) for parts in witnesses[dimension-factor]}
for row,other in zip(certificate['states'][1:],enumeration['dimensions'],strict=True):
    dimension=row['dimension']
    require(values[dimension]*factorial(dimension)==row['scaled_maximum'],'maximum differs')
    require(sorted(map(list,witnesses[dimension]))==row['best_partitions']==other['best_partitions'],'optimal sets differ')
    require(Fraction(other['maximum_numerator'],other['maximum_denominator'])==values[dimension],'rational value differs')
    require(counts[dimension]==other['partitions_examined'],'count differs')
require(sum(counts[2:])==37337,'total count differs')
require(next(d for d in range(2,41) if values[d]>Fraction((d+1)*d**d,factorial(d)))==20,'first violation differs')
require(next(d for d in range(2,41) if any(len(parts)>=3 for parts in witnesses[d]))==33,'three-factor transition differs')
require(values[20]/Fraction(21*20**20,factorial(20))==Fraction(5588869,5505024),'witness ratio differs')
print('All 39 maxima, complete optimal sets, and partition counts agree.')
