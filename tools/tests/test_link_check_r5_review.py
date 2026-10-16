"""Round-5 review probes kept as regression tests. Round-4 re-verification probes (build/review_linkcheck_r4). Run from the
ds-10 root: build/venv/bin/python -m pytest -q <this file>. test_FAILOPEN_*
assert the CORRECT behaviour; they fail on a36e7bd82e."""
import hashlib, json, sys
from pathlib import Path
WT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(WT / "tools" / "tests")); sys.path.insert(0, str(WT / "tools"))
from test_link_check import _rule_fixture, _Path, ROWS, _judge, C  # noqa: E402
import build  # noqa: E402

S = "?shared@@YAXXZ"


def _changed(paths, added=()):
    ch = C.Changed(paths); ch.added = frozenset(added); return ch


def test_FAILOPEN_deleted_shadowing_header_moves_object():
    """census: a.cpp includes "Common/Debug.h" which resolved to the sweep
    shim. The shim was DELETED since the census; a.obj now (rebuilt, sidecar
    digest-current) resolves the reference tree's Common/Debug.h, unchanged.
    The include resolution changed, so a.obj changed; inputs_moved says no."""
    inputs = {"game/a.cpp", "inputs/reference/CnC/Code/Include/Common/Debug.h"}
    since = _changed({"inputs/reference/shims/sweep/Common/Debug.h"})      # status D
    assert C.inputs_moved(inputs, since), "deleted same-name header shadowed an input: object not re-read"


def test_FAILOPEN_sidecar_cmd_ignored(tmp_path, monkeypatch):
    """object_inputs trusts a sidecar whose source/deps digests match but whose
    recorded compile command is not today's (a build.py flag change, a -D)."""
    src = tmp_path / "a.cpp"; src.write_text("int a;\n")
    hdr = tmp_path / "a.h"; hdr.write_text("#define X 1\n")
    obj = tmp_path / "a.obj"; obj.write_bytes(b"x")
    (tmp_path / "a.deps.json").write_text(json.dumps({
        "version": 2, "cmd": "NOT-TODAYS-COMMAND", "source": build._hash_file(str(src)),
        "deps": {str(hdr): build._hash_file(str(hdr))}}))
    inputs = C.object_inputs(obj, {obj: src}, None)
    assert inputs is None or C.inputs_moved(inputs, _changed(set())), \
        "a sidecar built with another command is trusted and the object counts unchanged"


def test_FAILOPEN_flag_only_change_false_links(monkeypatch):
    """End to end through the rule: b.obj links first and the census saw it
    keep the retail copy of S. Since then only tools/build.py changed (a flag);
    b.obj's real copy is now wrong. No input of b changed -> never re-read."""
    census = {"b.obj": ([(S, "dB", "retail")], []), "mine.obj": ([(S, "dB", "retail")], [])}
    now = {"b.obj": ([(S, "dX", "wrong")], []), "mine.obj": ([(S, "dB", "retail")], [])}
    ix, refreshed, facts_of = _rule_fixture(monkeypatch, list(census), census, now,
                                            since={"tools/build.py"}, inputs={"b.obj": {"game/b.cpp"}})
    mine = _Path("mine.obj")
    C.apply_selection_rule(ix, [mine], None, ROWS)
    selected, unknown = _judge(ix, mine, facts_of)
    assert selected or unknown, "false LINKS: a build.py flag change is invisible"


def test_FAILOPEN_ignored_input_change_invisible():
    """An input git ignores (inputs/reference/shims/sweep/mss.h, D3DX8Math.h:
    21 ds-10 objects) never appears in changed_since, so editing it never
    moves its includers."""
    inputs = {"game/a.cpp", "inputs/reference/shims/sweep/mss.h"}
    since = _changed(set())          # what changed_since returns after editing the ignored header
    assert C.inputs_moved(inputs, since), "an ignored input's edit is invisible"
