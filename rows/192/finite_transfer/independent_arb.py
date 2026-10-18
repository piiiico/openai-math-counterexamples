#!/usr/bin/env python3
"""Separately derived fixed-parameter Arb replay; does not import checker.py.

Supplied by the separately tasked AI reviewer; assertion checks adapted to
explicit rejection, including under python -O. MIT, Alexander Richard Towell.
Substantial OpenAI Codex assistance. This certifies arithmetic, not the proof.
"""
import argparse
import sys
import flint
from flint import arb, ctx, fmpq


def B(p, q=1):
    return arb(fmpq(p, q))


def require(condition, label):
    if not condition:
        raise ValueError(label)


def positive(label, x):
    require(x.is_finite() and x.lower().fmpq() > 0, label)
    print(label, x.str(40))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--negative-control', action='store_true')
    args = parser.parse_args()
    try:
        m, N = 2**24+1, 2**512
        require((2**256)**2 == N, 'block normalization')
        require(86*m == 1442840662, 'product-mass exponent')
        require(m*N == 2**536+2**512, 'cell degree')
        require((m+1)*N == 2**536+2**513, 'total signs')
        with ctx.workprec(384):
            M, T, R = B(m), B(8), B(16)
            c, h, r = B(3,8), B(1,2**20), B(1,2**33)
            e, b, sR = B(1,2**256), B(1,2**85), B(1,2**128)
            K, eps = T+c+r, h/2+r
            lam = 1-2*e/b
            DN = M*(K*r*r+6*K*e/(b-2*e))
            AN = (eps+DN)**2+M*r*r
            BN = 2*(r+DN)**2+M*r*r
            CN = (AN*((c+eps)**2/2+(c+eps)*T).exp()
                  /(2*r*(c-eps))+2*M*e*AN/b)/lam
            Etail = 8*R*R*e+4*(R*R+2)*sR+2*e*BN
            TN = ((2*(T+1/T)+BN/T)
                  *(((c+r)**2-T*T)/2).exp()/r
                  +3*((c+r)**2/2).exp()*Etail/(2*r))/lam
            gain = c*c-2*c*DN-CN-TN
            positive('density-ratio margin', 3-(2*K*r).exp())
            positive('Gaussian mass minus b', (2*r/3)*(-K*K/2).exp()-b)
            positive('finite mass minus 2^-86', b-2*e-B(1,2**86))
            positive('lambda', lam)
            positive('c-epsilon', c-eps)
            positive('R-T', R-T)
            positive('tail envelope margin', sR-(-R*R/2).exp())
            positive('normalization margin', 3-(2*arb.pi()).sqrt())
            print('C_N', CN.str(40))
            print('T_N', TN.str(40))
            print('gain/Q_N lower expression', gain.str(40))
            positive('gain margin', gain-B(1,5 if args.negative_control else 50))
    except ValueError as error:
        print('RESULT: independent replay not certified ('+str(error)+')', file=sys.stderr)
        return 1
    print('Python',sys.version.split()[0],'python-flint',flint.__version__,'FLINT',flint.__FLINT_VERSION__)
    print('RESULT: independent Arb scalar inequalities certified')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
