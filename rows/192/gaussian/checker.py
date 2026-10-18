#!/usr/bin/env python3
"""Certify explicit scalar sufficient inequalities for the Family 192 Gaussian rule.

Source: openai/math 1581d4cbdd69a0faf34b2089614fe2a814316a6a,
Unbounded-Violations-of-the-Square-Root-Degree-Bound-September-26-2026,
build/sections/03-alternatives.tex:47-58: Var(E[L | O]) >= m + E g.
PROOF.md derives the sufficient inequalities for our rational parameters.
This is not a Boolean witness or a formal verification of the analytic bridge.

Copyright 2026 Alexander Richard Towell. MIT licensed; see LICENSE.
Substantial OpenAI Codex assistance in derivation, implementation and verification.
"""

import argparse
from dataclasses import dataclass, fields
from fractions import Fraction
import json
from pathlib import Path
import sys


@dataclass(frozen=True)
class Parameters:
    schema_version: int
    leaf_count: int
    cutoff: Fraction
    shift: Fraction
    radius: Fraction
    gain_ratio_lower: Fraction
    interval_mass_binary_exponent: int
    exp_terms: int

    @classmethod
    def from_document(cls, document):
        if not isinstance(document, dict) or set(document) != {f.name for f in fields(cls)}:
            raise ValueError('certificate fields do not match the schema')
        parsed = {}
        for field in fields(cls):
            value = document[field.name]
            if field.type is Fraction:
                if (not isinstance(value, dict) or set(value) != {'numerator', 'denominator'}
                        or any(type(v) is not int for v in value.values())
                        or value['denominator'] <= 0):
                    raise ValueError(f'invalid rational parameter {field.name}')
                parsed[field.name] = Fraction(value['numerator'], value['denominator'])
            else:
                if type(value) is not int:
                    raise ValueError(f'invalid integer parameter {field.name}')
                parsed[field.name] = value
        p = cls(**parsed)
        if p.schema_version != 1:
            raise ValueError('unsupported certificate schema')
        if p.leaf_count < 3 or p.leaf_count % 2 != 1:
            raise ValueError('the grid needs an odd leaf count at least three')
        if min(p.cutoff, p.shift, p.radius, p.gain_ratio_lower) <= 0:
            raise ValueError('cutoff, shift, radius and requested gain must be positive')
        if p.exp_terms < 0 or p.interval_mass_binary_exponent < 0:
            raise ValueError('Taylor order and mass exponent must be nonnegative')
        return p


def exp_bounds(x, terms):
    """Exact rational lower/upper bounds for exp(x), for x >= 0.

    Sum through degree terms, then bound the remaining positive terms by a
    geometric series whose ratio is at most x/(terms+2).
    """
    x = Fraction(x)
    if type(terms) is not int or terms < 0 or x < 0 or x >= terms + 2:
        raise ValueError('Taylor enclosure requires x>=0 and x<terms+2')
    term = total = Fraction(1)
    for k in range(1, terms + 1):
        term = term * x / k
        total += term
    first_omitted = term * x / (terms + 1)
    return total, total + first_omitted / (1 - x / (terms + 2))


def decimal_bound(value, places=12, *, upper):
    """Outward decimal display; never used to decide certification."""
    value = Fraction(value)
    scale = 10**places
    scaled_num = value.numerator * scale
    units = (-((-scaled_num) // value.denominator) if upper
             else scaled_num // value.denominator)
    whole, remainder = divmod(abs(units), scale)
    return f'{"-" if units < 0 else ""}{whole}.{remainder:0{places}d}'


def verify(document):
    """Check all sufficient bounds, rejecting an uncertified or malformed input."""
    p = Parameters.from_document(document)
    m, T, c, r = p.leaf_count, p.cutoff, p.shift, p.radius
    h = 2 * T / (m - 1)
    epsilon = h / 2 + r
    K = T + c + r
    if c <= epsilon or T <= c + r:
        raise ValueError('geometry requires shift>half-spacing+radius and cutoff>shift+radius')

    _, density_ratio_upper = exp_bounds(2 * K * r, p.exp_terms)
    if density_ratio_upper >= 3:
        raise ValueError('conditional-mean density-ratio bound is not certified')
    D = m * K * r * r

    _, central_exp_upper = exp_bounds((c + epsilon)**2 / 2 + (c + epsilon) * T,
                                      p.exp_terms)
    central = ((epsilon + D)**2 + m * r * r) * central_exp_upper / (2*r*(c-epsilon))

    tail_exp_lower, _ = exp_bounds((T*T - (c+r)**2) / 2, p.exp_terms)
    tail = (2*(T+1/T) + (2*(r+D)**2 + m*r*r)/T) / (r*tail_exp_lower)
    gain = c*c - 2*c*D - central - tail
    if gain <= p.gain_ratio_lower:
        raise ValueError('requested gain not certified by the sufficient bound')

    _, interval_exp_upper = exp_bounds(K*K / 2, p.exp_terms)
    interval_lower = 2*r / (3*interval_exp_upper)
    if interval_lower <= Fraction(1, 2**p.interval_mass_binary_exponent):
        raise ValueError('requested interval probability lower bound is not certified')

    return {
        'status': 'certified_scalar_sufficient_inequalities',
        'leaf_count': m,
        'input_count': m+1,
        'predictor_on_A': str((m-1)*c),
        'predictor_on_B': str(m*c),
        'central_upper_enclosure': decimal_bound(central, upper=True),
        'tail_upper_enclosure': decimal_bound(tail, upper=True),
        'total_mean_bias_upper_enclosure': decimal_bound(D, 18, upper=True),
        'gain_ratio_lower_enclosure': decimal_bound(gain, upper=False),
        'certified_gain_ratio_lower': str(p.gain_ratio_lower),
        'interval_mass_binary_exponent': p.interval_mass_binary_exponent,
        'product_mass_binary_exponent': p.interval_mass_binary_exponent * m,
        'exp_terms': p.exp_terms,
        'arithmetic': 'exact rational Taylor bounds; outward decimal summaries',
        'scope': 'Gaussian predictor certificate; analytic bridge in PROOF.md; no Boolean witness',
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--certificate', type=Path,
                        default=Path(__file__).with_name('certificate.json'))
    parser.add_argument('--negative-control', choices=['coarse-grid', 'strong-margin'])
    args = parser.parse_args(argv)
    try:
        document = json.loads(args.certificate.read_text())
        if args.negative_control == 'coarse-grid':
            document['leaf_count'] = (document['leaf_count'] + 1) // 2
        elif args.negative_control == 'strong-margin':
            document['gain_ratio_lower'] = {'numerator': 1, 'denominator': 5}
        report = verify(document)
    except (ValueError, OSError, KeyError, TypeError) as error:
        print(f'RESULT: not certified ({error})', file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2, sort_keys=True))
    print(f"RESULT: certified Gaussian predictor gain > Q*{report['certified_gain_ratio_lower']}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
