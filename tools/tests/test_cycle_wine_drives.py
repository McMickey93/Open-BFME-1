"""Wine device discovery must not bind unrelated mutable directory entries."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import cycle_source as cs
import build
from test_bfme2_port_r1_regressions import checkout
from test_bfme2_port_r5_regressions import isolated

pytestmark = pytest.mark.skipif(sys.platform != 'linux', reason='Wine drive mappings')


def test_drive_candidates_preserve_glob_semantics(tmp_path):
    drives = tmp_path / 'dosdevices'
    drives.mkdir()
    (drives / 'c:').symlink_to(tmp_path, target_is_directory=True)
    (drives / 'x:').symlink_to(tmp_path / 'absent')
    (drives / 'b:').write_text('non-symlink mapping')
    (drives / 'd::').symlink_to('/dev/null')
    (drives / 'X:').symlink_to(tmp_path)
    assert build.wine_drives({'WINEPREFIX': str(tmp_path)}) == sorted(drives.glob('[a-z]:'))


def test_device_churn_preserves_drive_fingerprints_and_runtime_audit(checkout, tmp_path,
                                                                  cycle_python_installation):
    root, _ = checkout
    audit = tmp_path / 'audit'
    audit.mkdir()
    prefix = tmp_path / 'wine'
    drives = prefix / 'dosdevices'
    drives.mkdir(parents=True)
    (drives / 'c:').symlink_to(root, target_is_directory=True)
    program = f'''import build, census_receipts as receipts
prefix = Path({str(prefix)!r})
drives = prefix / 'dosdevices'
# Supply winepath's cached ROOT result; no native Wine is needed for this
# regression of the real fingerprint/signature and runtime-audit paths.
build._WINE_PATH_CACHE[str(build.ROOT)] = 'Z:' + str(build.ROOT).replace('/', chr(92))
env = {{'WINEPREFIX': str(prefix)}}
before = receipts.signature(['cl.exe'], env)
(drives / 'd::').symlink_to('/dev/null')
assert receipts.signature(['cl.exe'], env) == before
(drives / 'd::').unlink()
assert receipts.signature(['cl.exe'], env) == before
# Adding or remapping an actual drive must still invalidate both proofs.
(drives / 'x:').symlink_to(tools.parent)
added = receipts.signature(['cl.exe'], env)
assert added['fingerprint'] != before['fingerprint']
assert added['environment']['drive_mappings'] != before['environment']['drive_mappings']
(drives / 'c:').unlink()
(drives / 'c:').symlink_to(tools.parent / 'game')
changed = receipts.signature(['cl.exe'], env)
assert changed['fingerprint'] != added['fingerprint']
assert changed['environment']['drive_mappings'] != added['environment']['drive_mappings']
'''
    result = isolated(root / 'tools', audit, program, python=cycle_python_installation[0])
    assert result.returncode == 0, result.stdout + result.stderr
    cs.audit_runtime(audit, roots=(root / 'tools',))
