"""Structurally bind the frozen JSON certificate to the generated Lean table."""
from pathlib import Path
from fractions import Fraction
import argparse
import hashlib
import json

ROOT = Path(__file__).resolve().parent


def render(root=ROOT):
    source = root/'source/certificate.json'
    pins = json.loads((root/'source-pins.json').read_text())
    if hashlib.sha256(source.read_bytes()).hexdigest() != pins['certificate_sha256']:
        raise ValueError('pinned certificate hash differs')
    cert = json.loads(source.read_text())
    if (cert['minimum_factor'], cert['maximum_factor'], cert['period'], cert['cutoff']) != (2,19,13,100):
        raise ValueError('unexpected certificate parameters')
    if [s['n'] for s in cert['states']] != [0] + list(range(2,132)):
        raise ValueError('incomplete state domain')
    values = {s['n']: s['value'] for s in cert['states']}
    values[1] = [0,1]
    expressions = []
    for n in range(132):
        a,b = values[n]
        if type(a) is not int or type(b) is not int or a < 0 or b <= 0:
            raise ValueError('invalid rational')
        q = Fraction(a,b)
        if [q.numerator,q.denominator] != [a,b]:
            raise ValueError('noncanonical rational')
        expressions.append(f'  ({a} : ℚ) / {b}')
    template = (root/'lean/ConcreteCertificate.template').read_text()
    if template.count('@@VALUES@@') != 1:
        raise ValueError('invalid generation template')
    return template.replace('@@VALUES@@', ',\n'.join(expressions))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    target = ROOT/'lean/ConcreteCertificate.lean'
    generated = render()
    if args.write:
        target.write_text(generated)
    elif target.read_text() != generated:
        raise ValueError('Lean table/template differs from pinned certificate')
    print('RESULT: all132 Lean table entries match the pinned JSON certificate, including zero sentinel1')


if __name__ == '__main__':
    main()
