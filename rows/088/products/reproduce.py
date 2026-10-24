#!/usr/bin/env python3
"""Reproduce the recurrence certificate, exhaustive oracle and rejecting runs."""
from fractions import Fraction
import json
from math import factorial
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parent


def run(arguments, expected=0):
    result=subprocess.run([sys.executable,*arguments],cwd=ROOT,text=True,capture_output=True)
    if result.returncode != expected:
        raise ValueError(f'Unexpected exit {result.returncode}: {arguments}: {result.stdout}{result.stderr}')
    return result.stdout


def main():
    for mode in ([],['-O']):
        output=run([*mode,'check.py'])
        if output!=(ROOT/'output.txt').read_text():
            raise ValueError('positive evidence differs')
        for fault in ['maximum','partition','domain','optimal_set']:
            rejection=run([*mode,'check.py','--negative-control',fault],1)
            expected={
                'maximum':'maximum fails a complete recurrence comparison',
                'partition':'invalid partition witness',
                'domain':'state sequence does not cover the exact domain',
                'optimal_set':'partition does not attain the maximum',
            }[fault]
            if rejection!='RESULT: rejected: '+expected+'\n':
                raise ValueError('control rejected for an unexpected reason')
    print(output,end='')
    oracle=json.loads(run(['enumerate_partitions.py']))
    if oracle!=json.loads((ROOT/'enumeration.json').read_text()):
        raise ValueError('exhaustive enumeration differs')
    certificate=json.loads((ROOT/'certificate.json').read_text())
    states={r['dimension']:r for r in certificate['states']}
    if (oracle['max_dimension']!=40 or oracle['minimum_factor']!=2 or
            oracle['total_partitions_examined']!=37337 or
            [r['dimension'] for r in oracle['dimensions']]!=list(range(2,41))):
        raise ValueError('oracle coverage mismatch')
    for row in oracle['dimensions']:
        d=row['dimension'];primary=states[d]
        if (Fraction(primary['scaled_maximum'],factorial(d))!=Fraction(row['maximum_numerator'],row['maximum_denominator']) or
                primary['best_partitions']!=row['best_partitions']):
            raise ValueError(f'methods disagree at {d}')
    for mode in ([],['-O']):
        reviewer=run([*mode,'review/independent_check.py'])
        if reviewer!='All 39 maxima, complete optimal sets, and partition counts agree.\n':
            raise ValueError('separate reviewer evidence differs')
    print('RESULT: all 37337 partitions agree; eight corrupt-certificate runs reject')


if __name__=='__main__':
    main()
