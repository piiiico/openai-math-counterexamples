#!/usr/bin/env python3
"""Separate finite oracle: unordered partitions and exact rational products.

Does not import the DP checker or use its scaled-integer recurrence.
Written in the coordinating AI session, with the same factorial formula and
Python standard library; algorithmic corroboration, not separate authorship.
"""
from fractions import Fraction
from math import factorial
import json
import sys


def partitions(total, minimum=2):
    if total >= minimum:
        yield (total,)
    for first in range(minimum,total//2+1):
        for tail in partitions(total-first,first):
            yield (first,*tail)


def enumerate_all(max_dimension=40):
    dimensions=[]
    for total in range(2,max_dimension+1):
        maximum=None;best=[];count=0
        for parts in partitions(total):
            count+=1
            value=Fraction(1)
            for d in parts:
                value*=Fraction((d+1)*d**d,factorial(d))
            if maximum is None or value>maximum:
                maximum=value;best=[list(parts)]
            elif value==maximum:
                best.append(list(parts))
        dimensions.append({'dimension':total,'partitions_examined':count,
                           'maximum_numerator':maximum.numerator,
                           'maximum_denominator':maximum.denominator,
                           'best_partitions':sorted(best)})
    return {'max_dimension':max_dimension,'minimum_factor':2,
            'total_partitions_examined':sum(d['partitions_examined'] for d in dimensions),
            'dimensions':dimensions}


if __name__=='__main__':
    json.dump(enumerate_all(),sys.stdout,indent=2)
    print()
