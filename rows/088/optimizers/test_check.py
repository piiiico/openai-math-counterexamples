"""Exact controls for the finite hypotheses of the written induction."""
import copy
from fractions import Fraction
import pytest
import check


@pytest.fixture(scope='module')
def certificate():
    return check.make_certificate()


def test_complete_certificate(certificate):
    result = check.verify(certificate)
    assert result['cutoff'] == 100
    assert result['states'] == 131
    assert result['window_checks'] == 19


def test_true_boundary_and_residues(certificate):
    values = {s['n']: Fraction(*s['value']) for s in certificate['states']}
    assert values[112] > check.c(13) * values[99]
    assert check.formula(100) == ((12, 4), (13, 4))
    assert check.formula(112) == ((14, 8),)
    assert check.formula(113) == ((12, 4), (13, 5))
    assert check.formula(104) == ((13, 8),)
    assert sum(d*k for d,k in check.formula(10**100)) == 10**100


def test_empty_and_unreachable(certificate):
    assert certificate['states'][0] == {'n': 0, 'value': [1, 1], 'witnesses': [[]], 'last_parts': []}
    assert 1 not in {s['n'] for s in certificate['states']}


@pytest.mark.parametrize('n', [True, 1, -1, 2.5])
def test_invalid_simplex_dimension(n):
    with pytest.raises(ValueError):
        check.c(n)


@pytest.mark.parametrize('n', [True, 99, -1, 100.5])
def test_invalid_formula_dimension(n):
    with pytest.raises(ValueError):
        check.formula(n)


@pytest.mark.parametrize('control', ['early_cutoff', 'wrong_witness', 'omit_competitor', 'wrong_value'])
def test_mutations_rejected(certificate, control):
    with pytest.raises(ValueError):
        check.verify(check.mutate(certificate, control))


def test_late_cutoff_not_minimal():
    with pytest.raises(ValueError, match='minimal'):
        check.verify(check.make_certificate(cutoff=101))


def test_missing_state(certificate):
    bad=copy.deepcopy(certificate);bad['states'].pop()
    with pytest.raises(ValueError, match='state domain'):
        check.verify(bad)


def test_invalid_period(certificate):
    bad=copy.deepcopy(certificate);bad['period']=12
    with pytest.raises(ValueError, match='parameters'):
        check.verify(bad)


def test_spurious_tie(certificate):
    bad=copy.deepcopy(certificate)
    state=next(s for s in bad['states'] if s['n']==26)
    state['witnesses'].append([12,14])
    with pytest.raises(ValueError, match='witness'):
        check.verify(bad)


def test_balanced_oracle(certificate):
    for s in certificate['states'][1:]:
        value, witnesses = check.balanced_oracle(s['n'])
        assert value == Fraction(*s['value'])
        assert [list(w) for w in witnesses] == s['witnesses']


def test_balancing_candidates_nonoptimal_ties_are_not_witnesses():
    value, witnesses = check.balanced_oracle(20)
    assert witnesses == ((10, 10),)
    assert value == check.c(10)**2


@pytest.mark.parametrize('raw', [[0,1], [-1,1], [1,0], [True,1], [2,2]])
def test_invalid_rational(certificate, raw):
    bad=copy.deepcopy(certificate);bad['states'][1]['value']=raw
    with pytest.raises(ValueError, match='rational'):
        check.verify(bad)


def test_bad_empty_state(certificate):
    bad=copy.deepcopy(certificate);bad['states'][0]['witnesses']=[]
    with pytest.raises(ValueError, match='empty base'):
        check.verify(bad)


def test_invalid_cutoff(certificate):
    bad=copy.deepcopy(certificate);bad['cutoff']=True
    with pytest.raises(ValueError, match='cutoff'):
        check.verify(bad)


def test_unknown_control(certificate):
    with pytest.raises(ValueError, match='unknown'):
        check.mutate(certificate, 'not-a-control')


def test_source_failure(tmp_path, monkeypatch):
    import json
    (tmp_path/'sources.json').write_text(json.dumps({'files':[{'local':'source.txt','sha256':'0'*64}]}))
    (tmp_path/'source.txt').write_text('deliberately wrong source')
    monkeypatch.setattr(check,'ROOT',tmp_path)
    with pytest.raises(ValueError, match='source hash'):
        check.check_sources()


def test_balanced_oracle_preserves_ties(monkeypatch):
    monkeypatch.setattr(check, 'c', lambda d: Fraction(1))
    value, witnesses = check.balanced_oracle(6)
    assert value == 1
    assert witnesses == ((2, 2, 2), (3, 3), (6,))
