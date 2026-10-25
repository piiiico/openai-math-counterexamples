import copy
import json
from pathlib import Path
import pytest
import check

ROOT=Path(__file__).resolve().parent


def certificate():
    return json.loads((ROOT/'certificate.json').read_text())


def test_monomials_and_blocks():
    cert=certificate();model=check.build_model(cert)
    assert len(model.quadratics)==36
    assert len(model.quartics)==330
    assert model.blocks[0]==[(0,0),(1,1),(2,3),(4,5),(6,7)]


def test_modular_inverse_and_rank():
    a=[[1,2],[3,4]]
    assert check.mm(a,check.inverse(a,7),7)==[[1,0],[0,1]]
    assert check.determinant(a,7)==5
    assert check.rank([[1,2],[2,4]],7)==1
    assert check.rank([[0,0],[0,0]],7)==0
    with pytest.raises(ValueError):check.inverse([[1,2],[2,4]],7)


def test_weight_zero_complete():
    cert=certificate();model=check.build_model(cert);result=check.verify_weight(model,cert,0)
    assert result['D_minor_det']==6
    assert result['corner']==[[5]]
    assert result['G1_minor_det']==3
    assert result['G2_minor_det']==6
    assert result['bordered_minor_det']==(6*6*5)%7


def test_all_displayed_weights():
    cert=certificate();result=check.verify(cert)
    assert result['seed_rank']==20
    assert result['L_det']==6
    assert result['displayed_weights']==list(range(6))


@pytest.mark.parametrize('control',['point','tangent','minor','corner'])
def test_invalid_data_rejects(control):
    with pytest.raises(ValueError):check.verify(check.mutate(certificate(),control))


def test_rank_targets_cannot_be_omitted():
    bad=certificate();bad['generic_rank_lower_bounds']['bordered'].pop()
    with pytest.raises(ValueError, match='rank target domain'):
        check.verify(bad)


def test_direct_border_and_rank_sums():
    result=check.verify(certificate())
    assert result['rank_sums']=={'G1':136,'G2':84,'D':302,'bordered':623}
    assert all('bordered_minor_det' in r for r in result['weights'][:6])


def test_missing_minor_rejects():
    bad=certificate();bad['G1'].pop()
    with pytest.raises(ValueError,match='minor domain'):
        check.verify(bad)


def test_damaged_extra_index_rejects():
    bad=certificate();bad['D'][0]['extra_columns']=[1]
    with pytest.raises(ValueError):check.verify(bad)


def test_row_swap_determinant_sign():
    assert check.determinant([[0,1],[1,0]],7)==6


def test_non_square_and_bad_indices_reject():
    with pytest.raises(ValueError):check.determinant([[1,2]],7)
    with pytest.raises(ValueError):check.retained(3,[1,1])
    with pytest.raises(ValueError):check.retained(3,[0])


def test_zero_tangent_is_a_structural_failure():
    bad=certificate();bad['tangent_moments']=[0]*35
    with pytest.raises(ValueError,match='corner differs'):
        check.verify(bad)


def test_naive_integer_lift_is_not_a_psd_witness():
    result=check.naive_lift_probe(certificate())
    assert result['quadratics']==[[0,2],[0,3]]
    assert result['principal_minor']==[[0,1],[1,0]]
    assert result['integer_determinant']==-1


def test_ordinary_polynomial_product_coefficients():
    a={(0,0):1,(1,1):1}
    assert check.poly_product(a,a,7)=={(0,0,0,0):1,(0,0,1,1):2,(1,1,1,1):1}


def test_displayed_quartic_order_rejects_swap():
    bad=certificate();bad['zero_quartics'][0],bad['zero_quartics'][1]=bad['zero_quartics'][1],bad['zero_quartics'][0]
    with pytest.raises(ValueError,match='quartic order'):
        check.verify(bad)


def test_displayed_quadratic_order_rejects_swap():
    bad=certificate();bad['quadratic_blocks'][0].reverse()
    with pytest.raises(ValueError,match='quadratic order'):
        check.verify(bad)


def test_source_hash_control(tmp_path,monkeypatch):
    (tmp_path/'sources.json').write_text(json.dumps({'files':[{'local':'bad.txt','sha256':'0'*64}]}))
    (tmp_path/'bad.txt').write_text('not the pinned source')
    monkeypatch.setattr(check,'ROOT',tmp_path)
    with pytest.raises(ValueError,match='source hash'):
        check.check_sources()


def test_unknown_control_rejects():
    with pytest.raises(ValueError,match='unknown control'):
        check.mutate(certificate(),'unknown')


def test_invalid_coefficient_domain_rejects():
    bad=certificate();bad['point'][0]=True
    with pytest.raises(ValueError,match='coefficient'):
        check.verify(bad)


def test_high_false_rank_target_rejects():
    bad=certificate();bad['generic_rank_lower_bounds']['bordered'][0]=66
    with pytest.raises(ValueError,match='rank lower bound'):
        check.verify(bad)


def test_bad_tangent_domain_rejects():
    bad=certificate();bad['tangent_moments']=[0]*34
    with pytest.raises(ValueError,match='tangent moment domain'):
        check.verify(bad)


def test_boundary_probe_does_not_invent_negative_minor():
    data=certificate();data['weights']=[0]*8
    with pytest.raises(ValueError,match='negative naive-lift'):
        check.naive_lift_probe(data)


def test_printed_pivot_traces():
    c=certificate();r=check.verify_weight(check.build_model(c),c,0)
    assert r['G2_signed_pivots']==[x%7 for x in c['elimination_pivots']['G2_weight0']]
    assert r['D_signed_pivots']==[x%7 for x in c['elimination_pivots']['D_weight0']]


@pytest.mark.parametrize('key',['G2_weight0','D_weight0'])
def test_false_pivot_trace_rejects(key):
    bad=certificate();bad['elimination_pivots'][key][0]+=1
    with pytest.raises(ValueError,match='signed pivot trace'):
        check.verify(bad)
