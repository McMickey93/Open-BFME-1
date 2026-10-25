"""A fresh signed build must not retain temporary process-pool semaphores."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import cycle_source as cs
from test_bfme2_port_r1_regressions import checkout
from test_bfme2_port_r5_regressions import isolated

pytestmark = pytest.mark.skipif(sys.platform != 'linux', reason='Linux runtime audit')


def test_cold_selection_survives_final_runtime_recheck(checkout, tmp_path,
                                                     cycle_python_installation):
    root, _ = checkout
    audit = tmp_path / 'audit'
    audit.mkdir()
    for i in range(200):
        (root / f'game/f{i}.cpp').write_text('int f() { return 0; }\n')
    program = '''import build
sources = [tools.parent / f'game/f{i}.cpp' for i in range(200)]
outputs = {source: tools.parent / 'build' / (source.stem + '.obj') for source in sources}
assert set(build.stale_sources(sources, outputs, workers=2)) == set(sources)
'''
    result = isolated(root / 'tools', audit, program, python=cycle_python_installation[0])
    assert result.returncode == 0, result.stdout + result.stderr
    # Recheck after the measurement process exits: process-pool semaphores
    # are gone by this point, exactly as they are when the launcher signs.
    cs.audit_runtime(audit, roots=(root / 'tools',))
