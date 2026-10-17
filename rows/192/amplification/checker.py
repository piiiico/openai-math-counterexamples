#!/usr/bin/env python3
"""Exact scalar obligations for an explicit recursive Family192 budget.

This does not enumerate the final function or formally prove the written bridge.
Classical Berry--Esseen is inherited. Copyright2026 Alexander Richard Towell.
MIT; substantial OpenAI Codex assistance. See PROOF.md and README.md.
"""
import argparse
from dataclasses import dataclass,fields
from fractions import Fraction as F
import hashlib
import importlib.util
import json
from pathlib import Path
import sys


@dataclass(frozen=True)
class Parameters:
    schema_version:int
    copy_log2:int
    tail_log2:int
    fourth_moment_upper:int
    mass_log2:int
    gain_denominator:int
    padding_log2:int

    @classmethod
    def from_document(cls,document):
        names={f.name for f in fields(cls)}
        if not isinstance(document,dict) or set(document)!=names|{'gaussian'}:
            raise ValueError('certificate fields do not match schema')
        if any(type(document[n]) is not int for n in names):
            raise ValueError('all scalar parameters must be integers')
        p=cls(**{n:document[n] for n in names})
        if p.schema_version!=1:
            raise ValueError('unsupported schema')
        if p.copy_log2<2 or p.copy_log2%2:
            raise ValueError('copy exponent must be positive and even')
        if min(p.tail_log2,p.mass_log2,p.padding_log2)<0 or min(p.fourth_moment_upper,p.gain_denominator)<=0:
            raise ValueError('invalid positive budget parameter')
        return p


def gaussian_dependency(document,directory):
    dep=document['gaussian']
    if (not isinstance(dep,dict) or set(dep)!={'directory','files'}
            or not isinstance(dep['directory'],str) or not isinstance(dep['files'],dict)
            or set(dep['files'])!={'checker.py','certificate.json'}):
        raise ValueError('invalid Gaussian dependency manifest')
    root=(Path(directory)/dep['directory']).resolve()
    for file,digest in dep['files'].items():
        if hashlib.sha256((root/file).read_bytes()).hexdigest()!=digest:
            raise ValueError('Gaussian dependency hash mismatch: '+file)
    spec=importlib.util.spec_from_file_location('pinned_gaussian_amplification',root/'checker.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    cert=json.loads((root/'certificate.json').read_text());module.verify(cert)
    return module,module.Parameters.from_document(cert)


def verify(document,directory,target=1):
    p=Parameters.from_document(document)
    if type(target) is not int or target<1:
        raise ValueError('target must be a positive integer')
    g,source=gaussian_dependency(document,directory)
    m,T,c,r=source.leaf_count,source.cutoff,source.shift,source.radius
    s=m+1;e=F(1,1<<(p.copy_log2//2));R=1<<p.tail_log2
    if R<T:
        raise ValueError('tail cutoff does not cover selector region')
    if 3+F(1,1<<p.copy_log2)>p.fourth_moment_upper:
        raise ValueError('uniform fourth-moment bound is insufficient')
    b=F(1,1<<source.interval_mass_binary_exponent)
    mass=b-2*e
    if mass<=0:
        raise ValueError('CDF budget does not certify positive leaf masses')
    lam=1-2*e/b;K=T+c+r;epsilon=T/(m-1)+r
    d0=m*(K*r*r+6*K*e/mass)
    A0=(epsilon+d0)**2+m*r*r;B0=2*(r+d0)**2+m*r*r
    central_exp=g.exp_bounds((c+epsilon)**2/2+(c+epsilon)*T,source.exp_terms)[1]
    tail_reciprocal=g.exp_bounds((T*T-(c+r)**2)/2,source.exp_terms)[0]
    fallback_exp=g.exp_bounds((c+r)**2/2,source.exp_terms)[1]
    central=(A0*central_exp/(2*r*(c-epsilon))+2*m*e*A0/b)/lam
    tail_error=8*R*R*e+F(2*p.fourth_moment_upper,R*R)+2*e*B0
    tail=((2*(T+1/T)+B0/T)/(r*tail_reciprocal)
          +3*fallback_exp*tail_error/(2*r))/lam
    gain=c*c-2*c*d0-central-tail
    if gain<=F(1,p.gain_denominator):
        raise ValueError('uniform gain not certified by the sufficient budget')
    if mass<=F(1,1<<p.mass_log2):
        raise ValueError('claimed leaf mass not certified')
    # Compare a power of two without expanding the enormous iteration count.
    if p.padding_log2<(m*p.gain_denominator-1).bit_length():
        raise ValueError('iteration padding does not cover inverse ratio gain')
    E=m*p.mass_log2+p.padding_log2
    return {
        'status':'certified scalar amplification and readout budget',
        'target_integer':target,'leaves':m,'inputs_per_report':s,
        'copy_count':{'binary_exponent':p.copy_log2,'power_of_current_sign_count':2},
        'next_sign_count':{'coefficient':s,'binary_exponent':p.copy_log2,'power_of_current_sign_count':3},
        'next_degree_bound':{'coefficient':m,'binary_exponent':p.copy_log2,'power_of_current_sign_count':2,'power_of_current_degree':1},
        'stage_count':{'coefficient':4*target*target,'binary_exponent':E},
        'ratio_gain_binary_exponent':E,'product_mass_binary_exponent':p.mass_log2*m,
        'readout_copies_power_of_current_sign_count':2,
        'final_sign_count_power_of_current_sign_count':3,
        'readout_normalized_absolute_moment_strict_lower':'1/2',
        'cdf_error_binary_exponent':p.copy_log2//2,'tail_cutoff_binary_exponent':p.tail_log2,
        'fourth_moment_upper':p.fourth_moment_upper,
        'certified_gain_ratio_lower':str(F(1,p.gain_denominator)),
        'gain_ratio_lower_enclosure':g.decimal_bound(gain,upper=False),
        'central_upper_enclosure':g.decimal_bound(central,upper=True),
        'tail_upper_enclosure':g.decimal_bound(tail,upper=True),
        'arithmetic':'exact rational scalar inequalities; symbolic stage count not expanded',
        'scope':'written recursive construction and costs; no target truth table or formal proof',
        'classical_dependency':'iid Berry--Esseen C<=1; Shevtsova1111.6554v1 Corollary1',
    }


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--certificate',type=Path,default=Path(__file__).with_name('certificate.json'))
    parser.add_argument('--target',type=int,default=1)
    parser.add_argument('--finite-controls',action='store_true')
    parser.add_argument('--negative-control',choices=['few-copies','short-tail','long-tail','strong-gain','strong-mass','few-stages','fourth-moment'])
    args=parser.parse_args(argv)
    try:
        document=json.loads(args.certificate.read_text())
        if args.negative_control=='few-copies': document['copy_log2']=256
        elif args.negative_control=='short-tail': document['tail_log2']=4
        elif args.negative_control=='long-tail': document['tail_log2']=128
        elif args.negative_control=='strong-gain': document['gain_denominator']=5
        elif args.negative_control=='strong-mass': document['mass_log2']=85
        elif args.negative_control=='few-stages': document['padding_log2']=29
        elif args.negative_control=='fourth-moment': document['fourth_moment_upper']=3
        report=verify(document,args.certificate.parent,args.target)
        if args.finite_controls:
            if __package__:
                from .finite_controls import run_controls
            else:
                from finite_controls import run_controls
            report['finite_controls']=run_controls()
    except (ValueError,OSError,KeyError,TypeError) as error:
        print('RESULT: not certified ('+str(error)+')',file=sys.stderr)
        return 1
    print(json.dumps(report,sort_keys=True,indent=2))
    print('RESULT: certified amplification and readout budgets')
    return 0


if __name__=='__main__':
    raise SystemExit(main())
