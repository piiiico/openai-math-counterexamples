#!/usr/bin/env python3
"""Exact scalar certificate for one explicit finite-sign Family192 stage.

The probability argument and external Berry--Esseen dependency are in PROOF.md.
This checks the quantitative budget, not a Boolean truth table or a Lean proof.
The predecessor files are reused only after verifying their pinned hashes.
Copyright 2026 Alexander Richard Towell. MIT; see LICENSE.
Substantial OpenAI Codex assistance; predecessor credit in README.md.
"""
import argparse
from dataclasses import dataclass, fields
from fractions import Fraction
import hashlib
import importlib.util
import json
from pathlib import Path
import sys


@dataclass(frozen=True)
class TransferParameters:
    schema_version: int
    block_log2: int
    tail_cutoff: int
    finite_mass_binary_exponent: int
    gain_ratio_lower: Fraction

    @classmethod
    def from_document(cls, document):
        if not isinstance(document, dict) or set(document) != {f.name for f in fields(cls)} | {'predecessor'}:
            raise ValueError('transfer certificate fields do not match the schema')
        values = {}
        for f in fields(cls):
            v = document[f.name]
            if f.type is Fraction:
                if (not isinstance(v, dict) or set(v) != {'numerator', 'denominator'}
                        or any(type(x) is not int for x in v.values()) or v['denominator'] <= 0):
                    raise ValueError('invalid rational parameter')
                values[f.name] = Fraction(v['numerator'], v['denominator'])
            else:
                if type(v) is not int:
                    raise ValueError('invalid integer parameter')
                values[f.name] = v
        p = cls(**values)
        if p.schema_version != 1:
            raise ValueError('unsupported schema')
        if p.block_log2 < 2 or p.block_log2 % 2:
            raise ValueError('block exponent must be positive and even, giving a rational square root')
        if p.tail_cutoff <= 0 or p.finite_mass_binary_exponent < 0 or p.gain_ratio_lower <= 0:
            raise ValueError('invalid tail cutoff, probability exponent or gain')
        return p


def load_predecessor(document, directory):
    dependency = document['predecessor']
    if (not isinstance(dependency, dict) or set(dependency) != {'directory', 'files'}
            or not isinstance(dependency['directory'], str)
            or not isinstance(dependency['files'], dict)
            or set(dependency['files']) != {'checker.py', 'certificate.json'}):
        raise ValueError('invalid predecessor manifest')
    root = (Path(directory)/dependency['directory']).resolve()
    for name, expected in dependency['files'].items():
        if hashlib.sha256((root/name).read_bytes()).hexdigest() != expected:
            raise ValueError('predecessor hash mismatch: '+name)
    spec = importlib.util.spec_from_file_location('family192_pinned_gaussian', root/'checker.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    certificate = json.loads((root/'certificate.json').read_text())
    module.verify(certificate)
    return module, module.Parameters.from_document(certificate)


def verify(document, directory):
    p = TransferParameters.from_document(document)
    gaussian, source = load_predecessor(document, directory)
    m, T, c, r = source.leaf_count, source.cutoff, source.shift, source.radius
    R = p.tail_cutoff
    if R < T:
        raise ValueError('tail comparison cutoff must cover the selector cutoff')
    N = 1 << p.block_log2
    error = Fraction(1, 1 << (p.block_log2//2))
    b = Fraction(1, 1 << source.interval_mass_binary_exponent)
    finite_mass = b-2*error
    if finite_mass <= 0:
        raise ValueError('CDF error does not certify positive interval probabilities')
    rho = 2*error/b
    lam = 1-rho
    K = T+c+r
    spacing = 2*T/(m-1)
    epsilon = spacing/2+r
    D = m*(K*r*r+6*K*error/finite_mass)
    A = (epsilon+D)**2+m*r*r
    B = 2*(r+D)**2+m*r*r
    _, central_exp = gaussian.exp_bounds((c+epsilon)**2/2+(c+epsilon)*T, source.exp_terms)
    tail_exp_lower, _ = gaussian.exp_bounds((T*T-(c+r)**2)/2, source.exp_terms)
    _, fallback_exp = gaussian.exp_bounds((c+r)**2/2, source.exp_terms)
    central = (A*central_exp/(2*r*(c-epsilon))+2*m*error*A/b)/lam
    far_tail = Fraction(1, 1 << (R*R//2))
    tail_error = 8*R*R*error+4*(R*R+2)*far_tail+2*error*B
    tail = ((2*(T+1/T)+B/T)/(r*tail_exp_lower)
            +3*fallback_exp*tail_error/(2*r))/lam
    gain = c*c-2*c*D-central-tail
    if gain <= p.gain_ratio_lower:
        raise ValueError('finite-transfer gain not certified by the sufficient budget')
    if finite_mass <= Fraction(1, 1 << p.finite_mass_binary_exponent):
        raise ValueError('claimed finite interval-mass lower bound is not certified')
    return {
        'status': 'certified finite-sign scalar budget',
        'block_log2': p.block_log2, 'block_sign_count': N, 'input_blocks': m+1,
        'total_sign_count': (m+1)*N, 'cell_degree_upper_bound': m*N,
        'cdf_error_binary_exponent': p.block_log2//2, 'tail_cutoff': R,
        'finite_interval_mass_binary_exponent': p.finite_mass_binary_exponent,
        'product_mass_binary_exponent': m*p.finite_mass_binary_exponent,
        'gain_ratio_lower_enclosure': gaussian.decimal_bound(gain, upper=False),
        'certified_gain_ratio_lower': str(p.gain_ratio_lower),
        'central_upper_enclosure': gaussian.decimal_bound(central, upper=True),
        'tail_upper_enclosure': gaussian.decimal_bound(tail, upper=True),
        'mean_bias_upper_enclosure': gaussian.decimal_bound(D, 18, upper=True),
        'classical_dependency': 'iid Berry--Esseen C<=1; see Shevtsova arXiv:1111.6554v1 Corollary 1',
        'scope': 'one explicit finite observation stage; no amplification or final Boolean readout; written proof, not Lean',
        'arithmetic': 'exact rational sufficient inequalities; outward decimal summaries',
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--certificate', type=Path, default=Path(__file__).with_name('certificate.json'))
    parser.add_argument('--negative-control', choices=['small-block', 'short-tail', 'strong-margin', 'strong-mass'])
    parser.add_argument('--finite-controls', action='store_true')
    args = parser.parse_args(argv)
    try:
        document = json.loads(args.certificate.read_text())
        if args.negative_control == 'small-block':
            document['block_log2'] = 256
        elif args.negative_control == 'short-tail':
            document['tail_cutoff'] = 8
        elif args.negative_control == 'strong-margin':
            document['gain_ratio_lower'] = {'numerator': 1, 'denominator': 5}
        elif args.negative_control == 'strong-mass':
            document['finite_mass_binary_exponent'] = 85
        report = verify(document, args.certificate.parent)
        if args.finite_controls:
            from finite_controls import run_controls
            report['finite_controls'] = run_controls()
    except (ValueError, OSError, KeyError, TypeError) as error:
        print(f'RESULT: not certified ({error})', file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2, sort_keys=True))
    print('RESULT: certified finite-sign predictor gain > Q_N/'+str(Fraction(report['certified_gain_ratio_lower']).denominator)
          if Fraction(report['certified_gain_ratio_lower']).numerator == 1
          else 'RESULT: certified finite-sign predictor gain > Q_N*'+report['certified_gain_ratio_lower'])
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
