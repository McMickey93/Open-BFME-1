"""Finalization must preserve directory evidence collected by measurement."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import cycle_launch as launch
import cycle_artifacts as ca
import cycle_stamp as stamp
from cycle_fixture import NOW
from test_bfme2_port_r1_regressions import checkout, git, synthetic_snapshot_checkout


@pytest.mark.parametrize('late_change', [False, True])
def test_workspace_listing_survives_finalization(checkout, tmp_path, monkeypatch, late_change):
    root, _ = synthetic_snapshot_checkout(checkout)
    (root / 'game/f.cpp').write_text('// stlport\n// inert source\n')
    policy = tmp_path / 'external-runtime'
    policy.mkdir()
    driver = root / 'tools/link_cycle.py'
    # Exercise the native build's real case lookup with an inert measurement,
    # followed by the real launcher, validation and signing path.
    driver.write_text(driver.read_text().replace(
        '    receipt["synthetic_execution"] = ',
        '    import build\n'
        '    assert build._case_resolve(str(ROOT / "game/f.cpp").swapcase()) == str(ROOT / "game/f.cpp")\n'
        '    assert build._case_resolve(str(ROOT).swapcase()) == str(ROOT)\n'
        '    assert ROOT.parent / "include" in build._include_search_roots(ROOT / "game/f.cpp", ["cl", "-I" + str(ROOT)], {})\n'
        f'    list(Path({str(policy)!r}).iterdir())\n'
        '    receipt["synthetic_execution"] = '))
    git(root, 'add', 'tools/link_cycle.py', 'game/f.cpp')
    git(root, '-c', 'core.hooksPath=.githooks', '-c', 'user.name=fixture',
        '-c', 'user.email=fixture@example.invalid', 'commit', '-qm', 'Observe workspace')
    git(root, 'update-ref', 'refs/remotes/origin/master', git(root, 'rev-parse', 'HEAD'))
    snapshots = tmp_path / 'snapshots'
    snapshots.mkdir()
    out = tmp_path / 'bundle'
    if late_change:
        original = launch.pc.make_bundle
        def changed(*args, **kwargs):
            result = original(*args, **kwargs)
            (policy / 'unexpected-runtime-entry').write_text('changed')
            return result
        monkeypatch.setattr(launch.pc, 'make_bundle', changed)
        with pytest.raises(ca.BundleError, match='unchanged observed runtime'):
            launch.measure(out, 'workspace fixture', root=root,
                           key=stamp.configured_keys()[0], snapshot_dir=snapshots)
        assert not out.exists()
    else:
        launch.measure(out, 'workspace fixture', root=root,
                       key=stamp.configured_keys()[0], snapshot_dir=snapshots)
        _, freshness, _ = ca.serve(out, root=root, now=NOW)
        assert freshness['authoritative']
