"""Reproduce this packet, including explicit failure controls. Standard library only."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent


def run(arguments, expected=0, marker=None):
    command = [sys.executable, *arguments]
    result = subprocess.run(command, cwd=HERE, capture_output=True, text=True)
    print('$ python ' + ' '.join(arguments), flush=True)
    print(result.stdout, end='')
    print(result.stderr, end='')
    if result.returncode != expected:
        raise RuntimeError(f'Expected exit {expected}; got {result.returncode}')
    if marker is not None and marker not in result.stdout:
        raise RuntimeError(f'Missing expected output marker: {marker}')
    return result.stdout


def main():
    sources = json.loads((HERE / 'sources.json').read_text())
    for entry in sources['files']:
        actual = hashlib.sha256((HERE / entry['local']).read_bytes()).hexdigest()
        if actual != entry['sha256']:
            raise RuntimeError(f'Source hash mismatch: {entry["local"]}')
    print(f'Source hashes: {len(sources["files"])} verified')
    for flags in ([], ['-O']):
        output = run([*flags, 'check.py'], marker='RESULT: holds')
        if output != (HERE / 'output.txt').read_text():
            raise RuntimeError('Positive output differs from the recorded result')
        run([*flags, '-m', 'unittest', 'discover', '-s', '.', '-p', 'test_check.py'])
        for mutation in ('cochain', 'twist', 'dual'):
            run([*flags, 'check.py', '--mutate', mutation], 1, 'RESULT: FAIL')
        run([*flags, 'review_oracle.py'], marker='RESULT: holds')
        run([*flags, 'review_oracle.py', '--mutate', 'cochain'], 1, 'RESULT: FAIL')
    print('RESULT: Family 199 exact identities and rejecting controls reproduced')


if __name__ == '__main__':
    main()
