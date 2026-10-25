"""Link staging must not mutate the generations of consumed object files."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import cycle_source as cs
from test_bfme2_port_r1_regressions import checkout
from test_bfme2_port_r5_regressions import isolated


@pytest.mark.parametrize('tamper', [False, True])
def test_link_staging_preserves_audited_inputs(checkout, tmp_path, cycle_python_installation, tamper):
    root, _ = checkout
    audit = tmp_path / 'audit'
    audit.mkdir()
    program = '''import cycle_source as cs, link_cycle as lc
root = tools.parent
cs.input_epoch(root, prepare=True)
p = root / 'build/input.obj'
p.parent.mkdir(exist_ok=True)
lc.write_coff(p, [('.text', 0x60000020, b'\\xc3', 0)], [('_entry', 1, 0, lc.EXTERNAL)])
out = root / 'build/link_cycle'
cs.input_epoch(root, outputs=out)
objs = lc.Objects([p])
original = objs.get(p)[2]
placed = [{'obj': str(p), 'sec': 1}]
# Stable, quarantined, then placed again: every transition must keep the
# source's content and inode generation intact.
for units in (placed, placed, [], placed):
    staged, renamed = lc.zz_objects(objs, units, set(), out / 'zzobj')
    assert p.read_bytes() == original
    if units:
        assert staged[0].read_bytes() == original
    else:
        assert renamed == 1
        assert staged[0].read_bytes() != original
'''
    if tamper:
        program += "p.write_bytes(b'tampered')\np.write_bytes(original)\n"
    program += 'cs.consumed_inputs(root)\n'
    result = isolated(root / 'tools', audit, program, python=cycle_python_installation[0])
    if tamper:
        assert result.returncode != 0
        assert 'consumed input changed' in result.stderr
    else:
        assert result.returncode == 0, result.stdout + result.stderr
        cs.audit_runtime(audit, roots=(root / 'tools',))
