#!/usr/bin/env python3
"""Replay exact evidence and require mathematical rejection of false claims."""
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parent


def run(arguments,expected):
    result=subprocess.run([sys.executable,*arguments],cwd=ROOT,text=True,capture_output=True)
    if result.returncode!=expected:
        raise ValueError(f'Unexpected exit {result.returncode}: {arguments}: {result.stdout}{result.stderr}')
    return result.stdout


def main():
    output=run(['check.py'],0)
    if output!=(ROOT/'output.txt').read_text():
        raise ValueError('recorded positive evidence differs')
    print(output,end='')
    rejections={'density':'density candidate is not the unique winner',
                'split19':'balanced split at dimension19 is not an improvement',
                'split_sign':'split slack has nonpositive coefficient',
                'root':'root enclosure is false'}
    for mode in ([],['-O']):
        if run([*mode,'check.py'],0)!=output:raise ValueError('optimized evidence differs')
        for fault,message in rejections.items():
            if run([*mode,'check.py','--negative-control',fault],1)!='RESULT: rejected: '+message+'\n':
                raise ValueError('unexpected reason for rejection')
        if run([*mode,'review/independent_check.py'],0)!=(ROOT/'review/output.txt').read_text():
            raise ValueError('independent replay differs')
    print('RESULT: exact growth evidence, eight rejecting runs and independent corroboration reproduced')


if __name__=='__main__':
    main()
