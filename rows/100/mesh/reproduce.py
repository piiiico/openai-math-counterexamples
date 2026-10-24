#!/usr/bin/env python3
"""Replay the certificate and require mathematical rejection of each mutation."""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent


def main():
    result = subprocess.run([sys.executable, 'check.py'], cwd=ROOT, text=True, capture_output=True)
    if result.returncode or not result.stdout.endswith('RESULT: mesh-aware algebra, complete budgets and uncovered-point control verified\n'):
        raise RuntimeError('positive check failed: '+result.stdout+result.stderr)
    if result.stdout != (ROOT/'output.txt').read_text():
        raise RuntimeError('recorded evidence differs from replay')
    print(result.stdout, end='')
    expected = {
        'radial_sign': 'identity fails: radial budget',
        'secant_sign': 'identity fails: left shared side',
        'integral': 'identity fails: integral A',
        'mesh': 'sufficient coverage budget fails; not a counterexample',
        'area': 'strict area saving not certified',
    }
    for mode in ([], ['-O']):
        for fault, message in expected.items():
            result = subprocess.run([sys.executable, *mode, 'check.py', '--negative-control', fault], cwd=ROOT, text=True, capture_output=True)
            if result.returncode != 1 or result.stdout != 'RESULT: rejected: '+message+'\n':
                raise RuntimeError(f'Control {fault}, mode {mode}: unexpected result {result}')
    for mode in ([], ['-O']):
        result = subprocess.run([sys.executable, *mode, 'review/independent_check.py'], cwd=ROOT, text=True, capture_output=True)
        if result.returncode or result.stdout != (ROOT/'review/output.txt').read_text():
            raise RuntimeError('Independent area/geometry replay differs')
    print('RESULT: positive certificate, ten rejecting runs and independent area/geometry replay reproduced')


if __name__ == '__main__':
    main()
