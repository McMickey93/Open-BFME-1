"""Compiler diagnostics must remain inspectable by the snapshot input audit."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import cycle_source as cs
from test_bfme2_port_r1_regressions import checkout
from test_bfme2_port_r5_regressions import isolated

pytestmark = pytest.mark.skipif(sys.platform != 'linux', reason='Linux descriptor audit')


@pytest.mark.parametrize('merge', [False, True])
@pytest.mark.parametrize('prepare', [False, True])
def test_compiler_output_passes_real_input_audit(checkout, tmp_path, cycle_python_installation, merge, prepare):
    root, _ = checkout
    audit = tmp_path / 'audit'
    audit.mkdir()
    program = f'''import build, cycle_source
cycle_source.input_epoch(tools.parent, prepare={prepare})
r = build.watch_compiler(['/bin/sh', '-c', 'printf output; printf diagnostic >&2'],
                         cycle_source.clean_environment({{}}), merge_output={merge})
assert r.returncode == 0
assert r.stdout == {b'outputdiagnostic' if merge else b'output'!r}
assert r.stderr == {b'' if merge else b'diagnostic'!r}
assert not sys._bfme_cycle_io['read_errors'], sys._bfme_cycle_io['read_errors']
cycle_source.consumed_inputs(tools.parent)
'''
    result = isolated(root / 'tools', audit, program, python=cycle_python_installation[0])
    assert result.returncode == 0, result.stdout + result.stderr
    cs.audit_runtime(audit, roots=(root / 'tools',))


def test_unlinked_existing_input_still_refused(checkout, tmp_path, cycle_python_installation):
    root, _ = checkout
    audit = tmp_path / 'audit'
    audit.mkdir()
    policy = root / 'inputs/policy'
    policy.parent.mkdir()
    policy.write_bytes(b'input')
    program = '''import os, cycle_source
p = tools.parent / 'inputs/policy'
fd = os.open(p, os.O_RDONLY)
p.unlink()
with open(fd, 'rb') as stream:
    assert stream.read() == b'input'
cycle_source.consumed_inputs(tools.parent)
'''
    result = isolated(root / 'tools', audit, program, python=cycle_python_installation[0])
    assert result.returncode != 0
    assert 'unresolved opened descriptor' in result.stderr
