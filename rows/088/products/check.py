#!/usr/bin/env python3
"""Exact finite simplex-product certificate; geometry is justified in PROOF.md."""
import argparse
from copy import deepcopy
from fractions import Fraction
import hashlib
import json
from math import comb, factorial
from pathlib import Path
import sys

MAX_DIMENSION = 40


def scaled_value(parts):
    if not parts or any(type(d) is not int or d < 2 for d in parts):
        raise ValueError('factor dimensions must be integers at least two')
    dimension = sum(parts)
    value = Fraction(factorial(dimension))
    for d in parts:
        value *= Fraction((d+1)*d**d, factorial(d))
    if value.denominator != 1:
        raise ValueError('scaled partition value is not integral')
    return value.numerator


def candidates(dimension, prior):
    for factor in range(2, dimension+1):
        remainder = dimension-factor
        if remainder not in prior:
            continue
        row = prior[remainder]
        value = comb(dimension, factor)*(factor+1)*factor**factor*row['scaled_maximum']
        for parts in row['best_partitions']:
            yield value, tuple(sorted([factor, *parts]))


def generate(max_dimension=MAX_DIMENSION):
    if type(max_dimension) is not int or max_dimension < 2:
        raise ValueError('invalid maximum dimension')
    prior = {0:{'dimension':0, 'scaled_maximum':1, 'best_partitions':[[]]}}
    for dimension in range(2,max_dimension+1):
        choices = list(candidates(dimension,prior))
        maximum = max(v for v,_ in choices)
        parts = sorted({p for v,p in choices if v == maximum})
        prior[dimension] = {'dimension':dimension, 'scaled_maximum':maximum,
                            'best_partitions':[list(p) for p in parts]}
    return {'schema_version':1, 'max_dimension':max_dimension, 'min_factor_dimension':2,
            'states':list(prior.values())}


def verify(certificate, expected_max=MAX_DIMENSION):
    if (certificate.get('schema_version') != 1 or
            certificate.get('max_dimension') != expected_max or
            certificate.get('min_factor_dimension') != 2):
        raise ValueError('certificate schema or domain mismatch')
    states = certificate.get('states',[])
    if [row.get('dimension') for row in states] != [0,*range(2,expected_max+1)]:
        raise ValueError('state sequence does not cover the exact domain')
    if states[0] != {'dimension':0,'scaled_maximum':1,'best_partitions':[[]]}:
        raise ValueError('invalid empty-product base state')
    prior = {0:states[0]}
    for row in states[1:]:
        dimension = row['dimension']
        if type(row.get('scaled_maximum')) is not int:
            raise ValueError('maximum must be an exact integer')
        witnesses = row.get('best_partitions',[])
        if not witnesses:
            raise ValueError('missing attaining partition')
        for parts in witnesses:
            if (any(type(d) is not int or d<2 for d in parts) or
                    parts != sorted(parts) or sum(parts) != dimension):
                raise ValueError('invalid partition witness')
            if scaled_value(parts) != row['scaled_maximum']:
                raise ValueError('partition does not attain the maximum')
        choices = list(candidates(dimension,prior))
        bound = max(v for v,_ in choices)
        if row['scaled_maximum'] != bound:
            raise ValueError('maximum fails a complete recurrence comparison')
        all_optimal = [list(p) for p in sorted({p for v,p in choices if v == bound})]
        if witnesses != all_optimal:
            raise ValueError('optimal partition set is incomplete or redundant')
        prior[dimension] = row
    return prior


def corrupt(certificate, fault):
    target = next(r for r in certificate['states'] if r['dimension']==20)
    if fault == 'maximum':
        target['scaled_maximum'] = scaled_value((9,11))
        target['best_partitions'] = [[9,11]]
    elif fault == 'partition':
        target['best_partitions'] = [[10,11]]
    elif fault == 'domain':
        certificate['states'].pop()
    elif fault == 'optimal_set':
        target['best_partitions'].append([9,11])
    else:
        raise ValueError('unknown corruption')


def summary(prior):
    violations = [d for d,r in prior.items() if d>=2 and r['scaled_maximum']>(d+1)*d**d]
    three = [d for d,r in prior.items() if any(len(p)==3 for p in r['best_partitions'])]
    return {'domain':{'total_dimensions':[2,40], 'factor_dimensions_at_least':2},
            'first_violation':min(violations),
            'first_violation_partitions':prior[min(violations)]['best_partitions'],
            'ratio_in_dimension_20':str(Fraction(prior[20]['scaled_maximum'],21*20**20)),
            'first_three_factor_optimum':min(three),
            'partitions_at_three_factor_transition':prior[min(three)]['best_partitions'],
            'dimension_40_partitions':prior[40]['best_partitions'],
            'scope':'Finite complete simplex-product comparison; no statement about arbitrary convex bodies.'}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-certificate',type=Path)
    parser.add_argument('--negative-control',choices=['maximum','partition','domain','optimal_set'])
    args = parser.parse_args(argv)
    root = Path(__file__).resolve().parent
    try:
        for item in json.loads((root/'sources.json').read_text())['files']:
            raw = (root/item['local']).read_bytes()
            if len(raw)!=item['bytes'] or hashlib.sha256(raw).hexdigest()!=item['sha256']:
                raise ValueError('source hash mismatch')
        certificate = generate() if args.write_certificate else json.loads((root/'certificate.json').read_text())
        if args.write_certificate:
            args.write_certificate.write_text(json.dumps(certificate,indent=2)+'\n')
        if args.negative_control:
            certificate = deepcopy(certificate)
            corrupt(certificate,args.negative_control)
        prior = verify(certificate)
        print(json.dumps(summary(prior),indent=2))
        print('RESULT: all simplex-product recurrence obligations through dimension 40 verified')
        return 0
    except ValueError as error:
        print('RESULT: rejected: '+str(error))
        return 1


if __name__ == '__main__':
    sys.exit(main())
