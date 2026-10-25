from fractions import Fraction as F
from copy import deepcopy
import pytest
import check


def test_unique_density_winner():
    cert=check.generate()
    result=check.verify(cert)
    assert result['winner']==13
    assert len(cert['comparisons'])==18
    assert next(r for r in cert['comparisons'] if r['dimension']==13)['difference']==0


@pytest.mark.parametrize('winner',[2,10,12,14,19])
def test_false_density_winners(winner):
    with pytest.raises(ValueError,match='density'):
        check.verify(check.generate(winner))


def test_symbolic_all_variable_identities():
    assert check.identities()==5
    with pytest.raises(ValueError,match='split slack'):
        check.identities('split_sign')


def test_split_boundary_cannot_be_lowered_to_nineteen():
    assert check.split_ratio(19)<1
    assert check.split_ratio(20)==F(5588869,5505024)
    assert check.split_ratio(21)>1


def test_rate_is_rigorously_above_one():
    result=check.verify(check.generate())
    assert F(103,100)<result['rate_lower']<result['rate_upper']<F(26,25)
    assert check.c(13)>F(11,4)**13


def test_false_root_enclosure():
    cert=check.generate();cert['root']['lower']={'numerator':4,'denominator':1};cert['root']['upper']={'numerator':5,'denominator':1}
    with pytest.raises(ValueError,match='root enclosure'):check.verify(cert)


def test_missing_density_obligation_and_corrupted_integer():
    cert=check.generate();cert['comparisons'].pop()
    with pytest.raises(ValueError,match='coverage'):check.verify(cert)
    cert=check.generate();cert['comparisons'][0]['difference']+=1
    with pytest.raises(ValueError,match='integer'):check.verify(cert)


@pytest.mark.parametrize('n',[2,12,13,14,25,26,27,39,40,10**12+1])
def test_residue_construction(n):
    parts=check.construct(n)
    assert sum(d*k for d,k in parts.items())==n
    assert all(d>=2 and k>0 for d,k in parts.items())
    assert len(parts)<=2
    assert set(parts)<={13,14,n%13}


def test_residue_one_uses_fourteen_not_one():
    assert check.construct(14)=={14:1}
    assert check.construct(27)=={13:1,14:1}


@pytest.mark.parametrize('n',[0,1,-2,2.0,True])
def test_invalid_dimensions(n):
    with pytest.raises(ValueError):check.construct(n)
    with pytest.raises(ValueError):check.c(n)


def test_invalid_fraction_encoding():
    with pytest.raises(ValueError):check.decode({'numerator':1,'denominator':0})
