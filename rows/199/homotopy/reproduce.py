"""Reproduce finite identities, direct homotopy replay, and rejecting controls."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent


def run(arguments, expected=0, marker=None):
    result = subprocess.run([sys.executable, *arguments], cwd=HERE,
                            capture_output=True, text=True)
    print('$ python ' + ' '.join(arguments), flush=True)
    print(result.stdout, end='')
    print(result.stderr, end='')
    if result.returncode != expected:
        raise RuntimeError(f'Expected exit {expected}; got {result.returncode}')
    if marker is not None and marker not in result.stdout:
        raise RuntimeError(f'Missing expected marker: {marker}')
    return result.stdout


def main():
    sources = json.loads((HERE / 'sources.json').read_text())
    for entry in sources['files']:
        digest = hashlib.sha256((HERE / entry['local']).read_bytes()).hexdigest()
        if digest != entry['sha256']:
            raise RuntimeError(f'Pinned file hash mismatch: {entry["local"]}')
    print(f'Pinned source/dependency hashes: {len(sources["files"])} verified')
    for flags in ([], ['-O']):
        run([*flags, 'dependency/check.py'], marker='RESULT: holds')
        output = run([*flags, 'bar.py'], marker='RESULT: holds')
        if output != (HERE / 'output.txt').read_text():
            raise RuntimeError('Positive tensor replay differs from recorded output')
        run([*flags, '-m', 'unittest', 'discover', '-s', '.', '-p', 'test_bar.py'])
        for mutation in ('omit-inverse-twist', 'omit-H', 'drop-u', 'zero-G1'):
            run([*flags, 'bar.py', '--mutate', mutation], 1, 'RESULT: FAIL: pB+dG+Gd')
    print('RESULT: Family 199 explicit homotopy replay and rejecting controls reproduced')


if __name__ == '__main__':
    main()
