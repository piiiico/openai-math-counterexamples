"""Replay both exact implementations, matrix bindings and ten rejection runs."""
from pathlib import Path
import json
import subprocess
import sys

ROOT=Path(__file__).resolve().parent
CONTROLS=('point','tangent','zero_tangent','minor','corner')
RANK_KEYS=('G1','G2','D','bordered')


def main():
    normal=None
    for optimized in (False,True):
        prefix=[sys.executable]+(['-O'] if optimized else [])
        primary=subprocess.run(prefix+['check.py'],cwd=ROOT,capture_output=True,text=True)
        if primary.returncode:raise RuntimeError(primary.stdout+primary.stderr)
        if primary.stdout!=(ROOT/'output.txt').read_text():raise ValueError('recorded primary output differs')
        result=json.loads(primary.stdout.partition('\nRESULT:')[0])
        independent=subprocess.run(prefix+['review/independent_check.py','certificate.json'],cwd=ROOT,capture_output=True,text=True)
        if independent.returncode:raise RuntimeError(independent.stderr)
        other=json.loads(independent.stdout)
        if result['seed_matrix_hashes']!=other['seed_matrix_hashes']:raise ValueError('seed matrix binding differs')
        if result['seed_rank']!=other['seed_rank'] or result['L_det']!=other['L_det']:raise ValueError('seed invariants differ')
        if len(other['weights'])!=10 or other['rank_totals']!=[result['rank_sums'][key] for key in RANK_KEYS]:raise ValueError('independent rank totals differ')
        for a,b in zip(result['weights'],other['weights']):
            if (a['weight']!=b['weight'] or a['matrix_hashes']!=b['matrix_hashes']
                    or [a['ranks'][key] for key in RANK_KEYS]!=b['ranks']):
                raise ValueError('weight matrices/ranks differ')
            if a['weight']<=5 and (a['corner']!=b['corner'] or a['bordered_minor_det']!=b['direct_bordered_det']):
                raise ValueError('independent corner/bordered determinant differs')
        if normal is not None and other!=normal:raise ValueError('optimized independent output differs')
        normal=other
        print(f'PASS: both exact reconstructions and 42 matrix bindings; optimized={optimized}')
        for control in CONTROLS:
            bad=subprocess.run(prefix+['check.py','--control',control],cwd=ROOT,capture_output=True,text=True)
            if bad.returncode==0 or 'ValueError:' not in bad.stderr:raise ValueError('control did not reject: '+control)
            print(f'REJECTED: {control}; optimized={optimized}')
    print('RESULT: modular Hankel seed, all displayed minors and ten rejecting runs independently reproduced')


if __name__=='__main__':main()
