"""Portable source-hash, evidence, test and rejecting-control replay."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent


def run(arguments, expected=0, marker=None):
    result = subprocess.run([sys.executable, *arguments], cwd=HERE, capture_output=True, text=True)
    print('$ python ' + ' '.join(arguments), flush=True)
    print(result.stdout, end='')
    print(result.stderr, end='')
    if result.returncode != expected:
        raise RuntimeError(f'Expected exit {expected}, received {result.returncode}')
    if marker and marker not in result.stdout + result.stderr:
        raise RuntimeError(f'Missing result marker: {marker}')
    return result.stdout


def main():
    sources = json.loads((HERE / 'sources.json').read_text())
    for item in sources['files']:
        if hashlib.sha256((HERE / item['local']).read_bytes()).hexdigest() != item['sha256']:
            raise RuntimeError(f'Source hash mismatch: {item["local"]}')
    print(f'Pinned source hashes: {len(sources["files"])} verified')
    with tempfile.TemporaryDirectory(prefix='family199-parameters-') as temporary:
        report = Path(temporary) / 'evidence.json'
        for flags in ([], ['-O']):
            output = run([*flags, 'check.py', '--report', str(report)], marker='RESULT:')
            if output != (HERE / 'output.txt').read_text():
                raise RuntimeError('Positive output differs from recorded output')
            if json.loads(report.read_text()) != json.loads((HERE / 'evidence.json').read_text()):
                raise RuntimeError('Computed finite evidence differs from recorded evidence')
            run([*flags, '-m', 'unittest', '-v', 'test_check'], marker='OK')
            for mode in ('product', 'root', 'zero-dual'):
                run([*flags, 'check.py', '--negative-control', mode], 1, 'REJECT:')
            run([*flags, 'verification/independent_oracle.py', 'algebra.json'], marker='30')
    print('RESULT: Family 199 parameter strata, independent oracle and rejecting controls reproduced')


if __name__ == '__main__':
    main()
