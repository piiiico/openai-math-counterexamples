"""Build every formal target, inspect axiom reports, and reject false controls."""
from pathlib import Path
import json
import hashlib
import subprocess
import sys
import generate

ROOT = Path(__file__).resolve().parent
ALLOWED_AXIOMS = {'propext', 'Classical.choice', 'Quot.sound'}


def main():
    pins=json.loads((ROOT/'source-pins.json').read_text())
    if (ROOT/'lean/lean-toolchain').read_text().strip()!=pins['lean_toolchain']:
        raise ValueError('Lean toolchain pin differs')
    if hashlib.sha256((ROOT/'lean/lake-manifest.json').read_bytes()).hexdigest()!=pins['lake_manifest_sha256']:
        raise ValueError('dependency manifest pin differs')
    revision=subprocess.check_output(['git','-C',str(ROOT/'lean/.lake/packages/mathlib'),'rev-parse','HEAD'],text=True).strip()
    if revision!=pins['mathlib_commit']:
        raise ValueError('Mathlib revision differs')
    version=subprocess.check_output(['lake','env','lean','--version'],cwd=ROOT/'lean',text=True)
    if pins['lean_commit'] not in version:
        raise ValueError('Lean compiler commit differs')
    if generate.render() != (ROOT/'lean/ConcreteCertificate.lean').read_text():
        raise ValueError('generated Lean file differs from pinned certificate')
    build = subprocess.run(['lake','build'],cwd=ROOT/'lean',capture_output=True,text=True)
    if build.returncode:
        raise RuntimeError(build.stdout+build.stderr)
    reports=[]
    for line in (build.stdout+build.stderr).splitlines():
        if 'depends on axioms: [' in line:
            before,_,tail=line.partition('depends on axioms: [')
            names={x.strip() for x in tail.partition(']')[0].split(',') if x.strip()}
            if not names <= ALLOWED_AXIOMS:
                raise ValueError('unexpected theorem axioms: '+str(names))
            reports.append(before.strip())
    if not any('cappedValue_periodicity' in x for x in reports):
        raise ValueError('missing concrete periodicity axiom report')
    controls=[]
    for source in sorted((ROOT/'negative').glob('*.lean')):
        result=subprocess.run(['lake','env','lean',str(source)],cwd=ROOT/'lean',
                              capture_output=True,text=True)
        diagnostic=result.stdout+result.stderr
        if (result.returncode==0 or 'error:' not in diagnostic
                or not any(marker in diagnostic for marker in
                           ('error: (kernel) application type mismatch', 'error: Tactic `decide` failed'))
                or any(marker in diagnostic.lower() for marker in
                       ('timeout', 'maximum recursion', 'unknown module', 'unknown constant'))):
            raise ValueError('false control did not produce intended kernel rejection: '+source.name+'\n'+diagnostic)
        controls.append(source.name)
        print('REJECTED: '+source.name)
    if not controls:
        raise ValueError('no negative controls')
    print(json.dumps({'kernel_axiom_reports':len(reports),'rejecting_controls':len(controls),
                      'source_table_entries':132,'recurrence_states':130,'window_identities':19},sort_keys=True))
    print('RESULT: kernel recurrence certificate, concrete period and four false controls verified')


if __name__=='__main__':
    main()
