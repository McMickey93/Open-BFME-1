"""Round-4 (final) adversarial review probes, kept as regression tests (build/review_linkcheck_final). Final adversarial review of apply_selection_rule (df389f5f27).
Run: python3 -m pytest -q build/review_linkcheck_final/test_final_review.py
     (from the ds-10 worktree root). Tests named test_FAILOPEN_* assert the
     CORRECT behaviour and are expected to FAIL on df389f5f27."""
import os
import sys
from pathlib import Path

WT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(WT / "tools" / "tests"))
sys.path.insert(0, str(WT / "tools"))
from test_link_check import _rule_fixture, _Path, ROWS, _judge, C  # noqa: E402

S = "?shared@@YAXXZ"


def _blocked_or_unknown(ix, mine, facts_of):
    selected, unknown = _judge(ix, mine, facts_of)
    return selected, unknown


# --- N1: a census object that was NOT a census definer of S starts defining S
def test_FAILOPEN_unchecked_census_object_newly_defines_name_multi(monkeypatch):
    """census: a.obj, mine.obj define S (retail, same copy). Since the census,
    b.obj (in the census, earlier in link order, NOT a definer then) was edited
    and now emits a wrong copy of S. Real link keeps b's wrong copy. b's inputs
    changed since the census, so the rule must re-read it."""
    census = {"b.obj": ([], ["?b@@YAXXZ"]), "a.obj": ([(S, "dA", "retail")], []),
              "mine.obj": ([(S, "dA", "retail")], [])}
    now = {**census, "b.obj": ([(S, "dX", "wrong")], ["?b@@YAXXZ"])}
    ix, refreshed, facts_of = _rule_fixture(monkeypatch, list(census), census, now,
                                            since={"game/b.cpp"}, inputs={"b.obj": {"game/b.cpp"}})
    mine = _Path("mine.obj")
    C.apply_selection_rule(ix, [mine], None, ROWS)
    selected, unknown = _judge(ix, mine, facts_of)
    print("refreshed:", list(refreshed), "selected:", selected, "unknown:", unknown)
    assert selected or unknown, "false LINKS: b.obj's new earlier wrong copy is never read"


def test_FAILOPEN_unchecked_census_object_newly_defines_name_single(monkeypatch):
    """Same, but mine.obj is the only census definer (one definition: the rule
    `continue`s before any input check)."""
    census = {"b.obj": ([], ["?b@@YAXXZ"]), "mine.obj": ([(S, "dM", "retail")], [])}
    now = {**census, "b.obj": ([(S, "dX", "wrong")], ["?b@@YAXXZ"])}
    ix, refreshed, facts_of = _rule_fixture(monkeypatch, list(census), census, now,
                                            since={"game/b.cpp"}, inputs={"b.obj": {"game/b.cpp"}})
    mine = _Path("mine.obj")
    C.apply_selection_rule(ix, [mine], None, ROWS)
    selected, unknown = _judge(ix, mine, facts_of)
    print("refreshed:", list(refreshed), "selected:", selected, "unknown:", unknown)
    assert selected or unknown, "false LINKS: single-definer skip hides b.obj's new copy"


def test_FAILOPEN_single_census_definer_body_changed(monkeypatch):
    """S has ONE definer a.obj (mine only references it). a.cpp changed since
    the census and a's copy is now wrong; judge_selected blocks a wrong kept
    copy even with one definer, but the rule skips one-definer names before
    checking inputs, so the census 'ok' stands."""
    census = {"a.obj": ([(S, "dA", "retail")], []), "mine.obj": ([], [], [S])}
    now = {"a.obj": ([(S, "dX", "wrong")], []), "mine.obj": ([], [], [S])}
    ix, refreshed, facts_of = _rule_fixture(monkeypatch, list(census), census, now,
                                            since={"game/a.cpp"}, inputs={"a.obj": {"game/a.cpp"}})
    mine = _Path("mine.obj")
    C.apply_selection_rule(ix, [mine], None, ROWS)
    selected, unknown = _judge(ix, mine, facts_of)
    print("refreshed:", list(refreshed), "selected:", selected, "unknown:", unknown)
    # what the census itself would say on the current objects:
    assert C.link_census.judge_selected("a.obj", {"a.obj": ("dX", "wrong")}, {"a.obj"}, set(), set()) == "wrong"
    assert selected or unknown, "false LINKS: one-definer name whose only body changed is never re-read"


# --- Judgement call: kept copy identical, plus a new earlier unreadable definer
def test_judgement_call_unreadable_new_definer_forces_unknown(monkeypatch):
    census = {"a.obj": ([(S, "d1", None)], []), "b.obj": ([(S, "d2", None)], []),
              "mine.obj": ([], [], [S])}
    now = {"n.obj": ([(S, "dN", "wrong")], []), **census}
    ix, refreshed, facts_of = _rule_fixture(monkeypatch, list(census), census, now,
                                            ledger=["n.obj", "a.obj", "b.obj", "mine.obj"],
                                            built={"a.obj", "b.obj", "mine.obj"},
                                            since={"game/a.cpp"}, inputs={"a.obj": {"game/a.cpp"}})
    mine = _Path("mine.obj")
    C.apply_selection_rule(ix, [mine], None, ROWS, compile_limit=0)
    assert _judge(ix, mine, facts_of) == ([], [S])


def test_judgement_call_readable_new_earlier_identical_object_name_differs(monkeypatch):
    """A readable new earlier definer with the SAME digest: kept object differs
    from the census's -> unknown (conservative), not census verdict."""
    census = {"a.obj": ([(S, "d1", None)], []), "b.obj": ([(S, "d2", None)], []),
              "mine.obj": ([], [], [S])}
    now = {"n.obj": ([(S, "d1", None)], []), **census}
    ix, refreshed, facts_of = _rule_fixture(monkeypatch, list(census), census, now,
                                            ledger=["n.obj", "a.obj", "b.obj", "mine.obj"])
    mine = _Path("mine.obj")
    C.apply_selection_rule(ix, [mine], None, ROWS)
    assert _judge(ix, mine, facts_of) == ([], [S])


def test_judgement_call_identical_kept_copy_now_wrong_by_truth(monkeypatch):
    """Kept copy identical (object+digest) but current truth says wrong: blocked."""
    census = {"a.obj": ([(S, "d1", None)], []), "b.obj": ([(S, "d2", None)], []),
              "mine.obj": ([], [], [S])}
    now = {**census, "a.obj": ([(S, "d1", "wrong")], []), "mine.obj": ([(S, "d2", None)], [], [S])}
    ix, refreshed, facts_of = _rule_fixture(monkeypatch, list(census), census, now)
    mine = _Path("mine.obj")
    C.apply_selection_rule(ix, [mine], None, ROWS)
    assert _judge(ix, mine, facts_of)[0] == [S]


# --- N2: object_inputs trusts a stale local sidecar
def test_FAILOPEN_object_inputs_from_stale_sidecar(monkeypatch, tmp_path):
    """object_inputs returns the local .deps.json even when the local object
    is not current (built at some other commit): its header list need not be
    the census build's. Show it does not consult currency."""
    obj = tmp_path / "a.obj"
    obj.write_bytes(b"x")
    (tmp_path / "a.deps.json").write_text('{"deps": {"game/x.h": "0"}}')
    import build
    monkeypatch.setattr(build, "_deps_sidecar", lambda o: Path(o).with_suffix(".deps.json"))
    got = C.object_inputs(obj, {obj: C.ROOT / "game/a.cpp"}, None)
    print("inputs:", got)
    assert got is None, "inputs read from an object never shown current (a stale build's include list)"


# --- N3: repo_path resolves relative sidecar keys against CWD, not ROOT
def test_FAILOPEN_repo_path_depends_on_cwd(monkeypatch):
    monkeypatch.chdir(C.ROOT / "tools")
    got = C.repo_path("game/Libraries/Source/WWVegas/WWLib/ascii_string.h")
    print("repo_path from tools/:", got)
    assert got == "game/Libraries/Source/WWVegas/WWLib/ascii_string.h"


# --- N4: rename detection hides the old path of a renamed header
def test_changed_since_rename_reports_only_new_path():
    import inspect
    src = inspect.getsource(C.changed_since)
    print("uses --no-renames:", "--no-renames" in src)
    assert "--no-renames" in src


# --- N5: a census object that MOVED in link order (its lowest matched RVA changed)
def test_FAILOPEN_census_object_reordered_in_link_order(monkeypatch):
    """census order [mine, b]: mine's retail copy of S is first (kept), b's
    wrong copy loses. Since the census b.cpp gained a matched row at a lower
    RVA, so the current ledger links [b, mine]: the link keeps b's wrong copy.
    Nothing about b's definitions or ownership changed; its .cpp did not
    change either (only functions.csv)."""
    census = {"mine.obj": ([(S, "dA", "retail")], []), "b.obj": ([(S, "dX", "wrong")], [])}
    ix, refreshed, facts_of = _rule_fixture(monkeypatch, list(census), census, census,
                                            ledger=["b.obj", "mine.obj"])
    mine = _Path("mine.obj")
    C.apply_selection_rule(ix, [mine], None, ROWS)
    print("index order:", ix["objects"])
    selected, unknown = _judge(ix, mine, facts_of)
    assert selected or unknown, "false LINKS: the preview links in the census's order, not the ledger's"


# --- N6: an object dropped from the ledger keeps its definitions for one-definer names
def test_FAILOPEN_dropped_object_still_resolves_references(monkeypatch):
    """census: gone.obj alone defines X; mine.obj references X. Since the
    census gone.cpp left the ledger (rows retired / file deleted). The link
    no longer has X (unresolved), but the index still lists gone.obj as its
    definer, so check_object's elsewhere()/resolves() find it."""
    X = "?only@@YAXXZ"
    census = {"gone.obj": ([], [X]), "mine.obj": ([], [], [X])}
    now = {"mine.obj": ([], [], [X])}
    ix, refreshed, facts_of = _rule_fixture(monkeypatch, list(census), census, now, ledger=["mine.obj"])
    C.apply_selection_rule(ix, [_Path("mine.obj")], None, ROWS)
    print("strong[X] after the rule:", ix["strong"].get(X))
    assert not ix["strong"].get(X), "X still resolves through an object the ledger no longer links"
