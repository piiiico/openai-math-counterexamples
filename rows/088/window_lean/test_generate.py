import hashlib
import json
from pathlib import Path
import shutil
import pytest
import generate


def test_exact_generated_binding():
    assert generate.render() == (generate.ROOT/'lean/ConcreteCertificate.lean').read_text()


@pytest.fixture
def packet(tmp_path):
    for name in ['source/certificate.json','source-pins.json','lean/ConcreteCertificate.template']:
        dst=tmp_path/name;dst.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(generate.ROOT/name,dst)
    return tmp_path


def change_source(packet, edit):
    p=packet/'source/certificate.json';data=json.loads(p.read_text());edit(data);p.write_text(json.dumps(data))
    pins=json.loads((packet/'source-pins.json').read_text());pins['certificate_sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
    (packet/'source-pins.json').write_text(json.dumps(pins))


def test_corrupt_source_rejects(packet):
    with (packet/'source/certificate.json').open('a') as f:f.write(' ')
    with pytest.raises(ValueError,match='hash'):
        generate.render(packet)


def test_false_cutoff_rejects(packet):
    change_source(packet,lambda c:c.update(cutoff=99))
    with pytest.raises(ValueError,match='parameters'):
        generate.render(packet)


def test_missing_state_rejects(packet):
    change_source(packet,lambda c:c['states'].pop())
    with pytest.raises(ValueError,match='domain'):
        generate.render(packet)


@pytest.mark.parametrize('value', [[-1,1],[1,0],[True,1],[2,2]])
def test_invalid_rational_rejects(packet,value):
    change_source(packet,lambda c:c['states'][0].update(value=value))
    with pytest.raises(ValueError,match='rational'):
        generate.render(packet)


def test_duplicate_template_marker_rejects(packet):
    p=packet/'lean/ConcreteCertificate.template';p.write_text(p.read_text()+'@@VALUES@@')
    with pytest.raises(ValueError,match='template'):
        generate.render(packet)


def test_cli_rejects_changed_lean_and_write_restores_binding(packet):
    import subprocess
    import sys
    shutil.copyfile(generate.ROOT/'generate.py', packet/'generate.py')
    target=packet/'lean/ConcreteCertificate.lean'
    target.write_text(generate.render()+'\n-- unbound edit\n')
    rejected=subprocess.run([sys.executable,str(packet/'generate.py')],capture_output=True,text=True)
    assert rejected.returncode != 0 and 'differs from pinned certificate' in rejected.stderr
    repaired=subprocess.run([sys.executable,str(packet/'generate.py'),'--write'],capture_output=True,text=True)
    assert repaired.returncode == 0
    checked=subprocess.run([sys.executable,str(packet/'generate.py')],capture_output=True,text=True)
    assert checked.returncode == 0 and target.read_text() == generate.render()
