#!/usr/bin/env python3
"""Separate-reviewer's Arb replay; no import of the rational checker.

Copyright 2026 Alexander Richard Towell. MIT licensed; see LICENSE.
Written by a separately tasked OpenAI Codex agent, adapted only for a local
certificate path, explicit non-asserting guards and a RESULT line.
This is an independent scalar check, not a formal analytic proof.
"""
import json
from fractions import Fraction as F
from pathlib import Path
from flint import arb, ctx, fmpq

p = json.loads(Path(__file__).with_name('certificate.json').read_text())


def q(name):
    v = p[name]
    return F(v['numerator'], v['denominator'])


def ball(x):
    x = F(x)
    return arb(fmpq(x.numerator, x.denominator))


def require(condition, label):
    if not condition:
        raise ValueError(label)


def positive(label, x):
    require(x.is_finite() and x.lower().fmpq() > 0, label)
    print(label, x.str(30))


m, T, c, r = p['leaf_count'], q('cutoff'), q('shift'), q('radius')
h = 2*T/(m-1)
require((m, T, c, r, h) == (2**24+1, F(8), F(3, 8), F(1, 2**33), F(1, 2**20)),
        'fixed candidate parameters')
require((m-1)//2*h == T and m+1 == 16777218, 'grid endpoints and input count')
require((m-1)*c == 6291456 and m*c == F(50331651, 8), 'rational predictors')
require(85*m == 1426063445, 'product exponent')

with ctx.workprec(256):
    M, T, c, r, h = map(ball, (m, T, c, r, h))
    K, eps = T+c+r, h/2+r
    D = M*K*r*r
    positive('density ratio margin', 3-(2*K*r).exp())
    positive('central denominator margin', c-eps)
    C0 = ((eps+D)**2+M*r*r)/(2*r*(c-eps))
    C0 *= ((c+eps)**2/2+(c+eps)*T).exp()
    C1 = (2*(T+1/T)+(2*(r+D)**2+M*r*r)/T)/r
    C1 *= (((c+r)**2-T*T)/2).exp()
    gain = c*c-2*c*D-C0-C1
    mass = (2*r/3)*(-K*K/2).exp()
    print('gain/Q lower expression', gain.str(30))
    print('interval mass lower expression', mass.str(30))
    positive('gain margin', gain-ball(q('gain_ratio_lower')))
    positive('mass margin', mass-ball(F(1, 2**p['interval_mass_binary_exponent'])))
    positive('normalization margin', 3-(2*arb.pi()).sqrt())
print('RESULT: independent Arb scalar certificate passed')
