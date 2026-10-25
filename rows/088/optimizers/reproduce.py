"""Replay the exact certificate and rejection controls in both Python modes."""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent


def main():
    for optimized in (False, True):
        prefix = [sys.executable] + (['-O'] if optimized else [])
        good = subprocess.run(prefix + ['check.py'], cwd=ROOT, capture_output=True, text=True)
        if good.returncode != 0:
            raise RuntimeError(good.stderr)
        if good.stdout != (ROOT/'output.txt').read_text():
            raise ValueError('recorded output differs')
        print(f'PASS: checker output matches; optimized={optimized}')
        for control in ('early_cutoff', 'wrong_witness', 'omit_competitor', 'wrong_value'):
            bad = subprocess.run(prefix + ['check.py', '--control', control], cwd=ROOT,
                                 capture_output=True, text=True)
            if bad.returncode == 0 or 'ValueError:' not in bad.stderr:
                raise ValueError(f'control did not reject as intended: {control}')
            print(f'REJECTED: {control}; optimized={optimized}')
    reviewer = ROOT/'review/independent_check.py'
    for optimized in (False, True):
        prefix = [sys.executable] + (['-O'] if optimized else [])
        result = subprocess.run(prefix + [str(reviewer)], cwd=ROOT,
                                capture_output=True, text=True)
        if result.returncode:
            raise RuntimeError(result.stderr)
        print(result.stdout.strip())
    print('RESULT: finite induction certificate and eight rejecting runs reproduced')


if __name__ == '__main__':
    main()
