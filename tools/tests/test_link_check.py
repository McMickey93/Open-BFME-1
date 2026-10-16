"""link_check: the per-file LINKED preview agrees with link.exe's rules."""
import collections
import copy
import sys
from unittest.mock import patch
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import link_check as C  # noqa: E402
import link_census as L
import pytest
from test_weak_fallback_truth import fixture, provider_coff, add_symbol


def index(strong=None, comdat=None, blockers=None, sizes=None):
    return {"meta": {"date": "d", "commit": "c"}, "objects": ["a.obj", "b.obj", "c.obj"],
            "strong": strong or {}, "comdat": comdat or {}, "blockers": blockers or {}, "bytes": sizes or {},
            "common_schema": C.COMMON_SCHEMA, "common": {}}


def test_two_inline_copies_fold_silently():
    ix = index(comdat={"f": [(0, "x", None), (1, "y", None)]})
    assert not C.duplicate("f", 2, False, None, ix)


def test_exclusive_definition_collides_with_the_first_definition():
    ix = index(strong={"f": [0]}, comdat={"f": [(0, "x", None)]})
    assert C.duplicate("f", 2, False, None, ix)   # an inline copy after an exclusive first one
    assert C.duplicate("f", 2, True, None, ix)
    ix = index(comdat={"f": [(0, "x", None)]})
    assert C.duplicate("f", 2, True, None, ix)    # an exclusive definition after an inline first one
    assert not C.duplicate("f", 0, False, 0, ix)  # its own old copy is not a second definition


def test_first_definition_is_charged_when_a_later_one_is_exclusive():
    ix = index(strong={"f": [2]}, comdat={"f": [(2, "x", None)]})
    assert C.duplicate("f", 0, False, None, ix)


def test_next_counts_only_files_with_a_single_blocker(capsys):
    blockers = {
        "one.cpp": {"object": "a.obj", "linked": False, "unresolved": ["_htons@4"], "duplicates": [], "losers": [],
                    "addresses": 0},
        "two.cpp": {"object": "b.obj", "linked": False, "unresolved": ["_htons@4", "_x"], "duplicates": [],
                    "losers": [], "addresses": 0},
        "lit.cpp": {"object": "c.obj", "linked": False, "unresolved": [], "duplicates": [], "losers": [],
                    "addresses": 3},
    }
    C.next_names(index(blockers=blockers, sizes={"one.cpp": 100, "two.cpp": 500, "lit.cpp": 40}), 10)
    out = capsys.readouterr().out
    assert "100     1  unresolved  _htons@4" in out
    assert C.ADDRESSES in out and "_x" not in out


def test_stale_object_is_never_evidence(tmp_path, monkeypatch):
    """A source edited after its object was compiled: link_census.object_current
    says no (with or without a dependency record) and link_check refuses it."""
    import json
    import os
    import link_census
    source, obj = tmp_path / "f.cpp", tmp_path / "f.obj"
    obj.write_bytes(b"old object")
    source.write_text("int f() { return 2; }\n")
    os.utime(obj, (1_000_000, 1_000_000))
    assert not link_census.object_current(source, obj)  # no sidecar: older than its source
    os.utime(obj, None)
    os.utime(source, (1_000_000, 1_000_000))
    assert not link_census.object_current(source, obj)  # timestamps do not replace a receipt
    monkeypatch.setattr(link_census.build, "compiler_command", lambda s, o: (["cl"], {}))
    monkeypatch.setattr(link_census.build, "_cmd_fingerprint", lambda command, env: "cmd")
    sidecar = link_census.build._deps_sidecar(obj)
    sidecar.write_text(json.dumps({"source": link_census.build._hash_file(str(source)), "deps": {}, "cmd": "cmd"}))
    assert link_census.object_current(source, obj)
    source.write_text("int f() { return 3; }\n")  # edited after the compile
    assert not link_census.object_current(source, obj)
    monkeypatch.setattr(C, "ROOT", tmp_path)
    ix = index(blockers={"f.cpp": {"object": "f.obj", "linked": True, "unresolved": [], "duplicates": [],
                                   "losers": [], "addresses": 0}})
    import pytest
    with pytest.raises(SystemExit, match="not current"):
        C.resolve(str(obj), ix)


def test_a_missing_object_is_never_an_empty_clean_one(tmp_path):
    # falsifier from the 2026-09-29 linking audit: object_facts turned a read failure into empty
    # facts, and link_check reported LINKS for an object that does not exist
    import pytest
    import link_census
    missing = tmp_path / "does_not_exist.obj"
    with pytest.raises(link_census.MissingObject):
        link_census.object_facts(missing)
    ix = {**index(), "objects": [], "selection": {"exceptions": {}, "owners": {}},
          "excuses": {"runtime": set(), "imported": {}, "stubs": {}}}
    with pytest.raises(link_census.MissingObject):
        C.check_object(missing, ix, None)
    with pytest.raises(SystemExit):
        C.resolve(str(missing), ix)


def test_families_follow_the_name_scope_not_its_arguments():
    assert C.family_of("?_M_deallocate@?$__node_alloc@$00$0A@@_STL@@CAXPAXI@Z") == "stlport"
    assert C.family_of("??1facet@locale@_STL@@MAE@XZ") == "stlport"
    assert C.family_of("?_Stl_atod@_STL@@YANPADHH@Z") == "stlport"
    assert C.family_of("?bfmeBitVectorEqual@@YA_NABV?$vector@_NV?$allocator@_N@_STL@@@_STL@@0@Z") == ""
    assert C.family_of("??1AsciiString@@QAE@XZ") == "strings"
    assert C.family_of("?compareNoCase@?$StringBase@D@@QBEHABV1@@Z") == "strings"
    assert C.family_of("?getPingValue@GameSpyInfo@@UAEHABVAsciiString@@@Z") == ""
    assert C.family_of("?TheScriptEngine@@3PAVScriptEngine@@A") == "globals"
    assert C.claim_key("x") >= 0xF0000000


def test_publish_and_serve_skip_changed_landed_and_family_rows(tmp_path, monkeypatch, capsys):
    import claims
    blockers = {name + ".cpp": {"object": "a.obj", "linked": False, "unresolved": [name], "duplicates": [],
                                "losers": [], "addresses": 0}
                for name in ("changed", "landed", "open", "??1AsciiString@@QAE@XZ")}
    sizes = {"changed.cpp": 400, "landed.cpp": 300, "??1AsciiString@@QAE@XZ.cpp": 250, "open.cpp": 100}
    queue = tmp_path / "q.csv"
    monkeypatch.setattr(C, "linked_since", lambda census: (frozenset(), "", "no tracked link census"))
    C.publish(index(blockers=blockers, sizes=sizes), queue)
    monkeypatch.setattr(claims, "_fetch_master", lambda: "tip")
    monkeypatch.setattr(C, "_git", lambda *a, **k: "changed.cpp\n" if a[0] == "diff"
                        else f"Claim-Lease: 0x{C.claim_key('landed'):08X}=abcdef12\n")
    monkeypatch.setattr(claims, "owner", lambda: "me")
    monkeypatch.setattr(claims, "active", lambda: {})
    assert C.main(["next", "--no-claim", "--queue", str(queue)]) == 0
    out = capsys.readouterr().out
    assert "link queue #4 (census c; no tracked link census): open" in out and "1 family strings" in out
    assert "1 every file linked or changed since the census" in out
    assert C.main(["next", "--no-claim", "--family", "strings", "--queue", str(queue)]) == 0
    assert "??1AsciiString@@QAE@XZ" in capsys.readouterr().out


def test_refresh_replaces_a_passed_objects_census_definitions(monkeypatch):
    """A duplicate removed from b.obj since the census no longer charges a.obj."""
    import link_census
    from types import SimpleNamespace
    ix = index(strong={"f": [0, 1], "g": [1]}, comdat={"h": [(1, "x", None)]})
    assert C.duplicate("f", 0, True, 0, ix)
    monkeypatch.setattr(link_census, "object_facts", lambda obj, truth, **kwargs: ([], ["g"], [], []))
    monkeypatch.setattr(link_census, "common_definitions", lambda obj, **kwargs: {})
    C.refresh(ix, [SimpleNamespace(name="b.obj", read_bytes=lambda: b"frozen"), SimpleNamespace(name="new.obj")], None)
    assert ix["strong"] == {"f": [0], "g": [1]} and ix["comdat"] == {"h": []}
    assert not C.duplicate("f", 0, True, 0, ix)


def _refresh_fixture(monkeypatch, tmp_path, stale):
    import os
    import time
    import build
    import link_census
    ix = index(strong={"f": [0, 1]})
    ix["meta"]["date"] = "2026-10-14 07:27"
    census = time.mktime(time.strptime("2026-10-14 07:27", "%Y-%m-%d %H:%M"))   # local, as census writes it
    sources = {name: tmp_path / name.replace(".obj", ".cpp") for name in ("a.obj", "b.obj", "c.obj")}
    for name, stamp in (("a.obj", census - 60), ("b.obj", census + 3600)):
        obj = tmp_path / name
        obj.write_bytes(b"")
        os.utime(obj, (stamp, stamp))
    monkeypatch.setattr(link_census, "ledger", lambda: [{"source": str(s)} for s in sources.values()])
    monkeypatch.setattr(build, "obj_path", lambda s, member=None: tmp_path / s.name.replace(".cpp", ".obj"))
    monkeypatch.setattr(build, "stale_sources", lambda *a: [sources[n] for n in stale])
    monkeypatch.setattr(build, "compile_rows",
                        lambda rows, srcs: {s: tmp_path / s.name.replace(".cpp", ".obj") for s in srcs})
    passed = []
    monkeypatch.setattr(C, "refresh", lambda index_, objects, truth: passed.extend(o.name for o in objects))
    C.refresh_stale(ix, None)
    return passed


def test_refresh_stale_replaces_objects_rebuilt_since_the_census(monkeypatch, tmp_path):
    """Ported from Open-BFME-2 36cd4e5fff: an object another build rebuilt after
    the census is not stale, but its census definitions are old: --refresh
    replaces them all the same. One built before the census, or missing, is not."""
    assert _refresh_fixture(monkeypatch, tmp_path, stale=()) == ["b.obj"]


def test_refresh_stale_recompiles_stale_objects_once(monkeypatch, tmp_path):
    assert _refresh_fixture(monkeypatch, tmp_path, stale=("c.obj", "b.obj")) == ["c.obj", "b.obj"]


def test_built_since_fails_closed_on_an_unreadable_census_date(tmp_path):
    obj = tmp_path / "x.obj"
    obj.write_bytes(b"")
    assert not C.built_since(obj, index())                   # meta date "d"
    assert not C.built_since(tmp_path / "missing.obj", {"meta": {"date": "2026-10-14 07:27"}})


def test_serve_fails_closed_when_freshness_cannot_be_read(tmp_path, monkeypatch):
    """No origin/master, or a census commit git cannot find: exit, never claim."""
    import claims
    import pytest
    queue = tmp_path / "q.csv"
    C.publish(index(blockers={"a.cpp": {"object": "a.obj", "linked": False, "unresolved": ["x"], "duplicates": [],
                                        "losers": [], "addresses": 0}}, sizes={"a.cpp": 1}), queue)
    monkeypatch.setattr(claims, "claim", lambda *a, **k: pytest.fail("claimed a stale queue"))
    monkeypatch.setattr(claims, "_fetch_master", lambda: None)
    with pytest.raises(SystemExit):
        C.main(["next", "--queue", str(queue)])
    monkeypatch.setattr(claims, "_fetch_master", lambda: "HEAD")   # census "c" is not a commit
    with pytest.raises(SystemExit, match="nothing claimed"):
        C.main(["next", "--queue", str(queue)])


def _preview(monkeypatch, tmp_path, names):
    import link_census
    ix = index(blockers={"a.cpp": {"object": "a.obj", "linked": False, "unresolved": [], "duplicates": [],
                                   "losers": [], "addresses": 0}}, sizes={"a.cpp": 100})
    monkeypatch.setattr(C, "load_index", lambda: ix)
    monkeypatch.setattr(C, "resolve", lambda path, _: (path.replace(".obj", ".cpp"), tmp_path / path))
    monkeypatch.setattr(link_census, "ledger", lambda: None)
    monkeypatch.setattr(link_census, "RetailTruth", lambda _: None)
    monkeypatch.setattr(C, "refresh", lambda *a: None)
    monkeypatch.setattr(C, "source_bytes", lambda sources: {s: 100 for s in sources})
    monkeypatch.setattr(C, "check_object", lambda *a: {k: [] for k in
                        ("unresolved", "duplicates", "comdat", "addresses", "selected")})
    return C.main(names)


def test_a_file_named_twice_counts_once(monkeypatch, tmp_path, capsys):
    assert _preview(monkeypatch, tmp_path, ["a.obj", "a.obj"]) == 0
    assert "1 of 1 link cleanly; LINKED 0 -> 100 bytes" in capsys.readouterr().out


def _coff(defines=(), refers=()):
    import struct
    body = b"\xc3"
    header = struct.pack("<HHIIIHH", 0x14C, 1, 0, 60 + len(body), len(defines) + len(refers), 0, 0)
    sec = b".text\0\0\0" + struct.pack("<IIIIIIHHI", 0, 0, len(body), 60, 0, 0, 0, 0, 0x60500020)
    symbols = b"".join(name.encode().ljust(8, b"\0") + struct.pack("<IhHBB", 0, 1 if name in defines else 0, 0x20, 2, 0)
                       for name in (*defines, *refers))
    return header + sec + body + symbols + struct.pack("<I", 4)


def _new_files(monkeypatch, tmp_path, objects, order):
    """A census of a.obj and b.obj (a.obj defines _g); `objects` {name: coff}
    are new files whose current link order is `order`. Nothing but compiling
    is stubbed: refresh and check_object run for real."""
    import link_census
    ix = {**index(strong={"_g": [0]}), "objects": ["a.obj", "b.obj"], "aliases": {},
          "selection": {"exceptions": {}, "owners": {}},
          "excuses": {"runtime": set(), "imported": {}, "stubs": {}}}
    for name, raw in objects.items():
        (tmp_path / name).write_bytes(raw)
    monkeypatch.setattr(C, "load_index", lambda: ix)
    monkeypatch.setattr(C, "resolve", lambda path, _: (path, tmp_path / path.replace(".cpp", ".obj")))
    monkeypatch.setattr(C, "note_evaluated", lambda *a: None)
    monkeypatch.setattr(link_census, "ledger", lambda: [])
    monkeypatch.setattr(link_census, "data_ledger", lambda: [])
    monkeypatch.setattr(link_census, "link_order", lambda rows, data: [Path(name) for name in order])
    monkeypatch.setattr(C, "source_bytes", lambda sources: {s: 100 for s in sources})
    return ix


def test_two_new_files_defining_one_exclusive_symbol_both_collide(monkeypatch, tmp_path, capsys):
    """Every new object is placed and refreshed in a normal check, so two new
    files defining one symbol both fail as link.exe fails them (LNK2005), and
    a new file's reference resolves against a census definition."""
    ix = _new_files(monkeypatch, tmp_path, {"n1.obj": _coff(["_f"], ["_g"]), "n2.obj": _coff(["_f"])},
                    ["a.obj", "n1.obj", "b.obj", "n2.obj"])
    assert C.main(["n1.cpp", "n2.cpp"]) == 1
    out = capsys.readouterr().out
    assert "new since census c, previewed at its link-order place: n1.cpp, n2.cpp" in out
    assert out.count("duplicate   _f") == 2 and "unresolved" not in out
    assert ix["objects"] == ["a.obj", "n1.obj", "b.obj", "n2.obj"]


def test_a_new_file_links_when_its_references_resolve_in_the_census(monkeypatch, tmp_path, capsys):
    _new_files(monkeypatch, tmp_path, {"n1.obj": _coff(["_f"], ["_g"])}, ["n1.obj", "a.obj", "b.obj"])
    assert C.main(["n1.cpp"]) == 0
    assert "n1.cpp: LINKS  LINKED 0 -> 100 bytes" in capsys.readouterr().out


def test_census_only_still_reads_a_new_file_s_own_object(monkeypatch, tmp_path, capsys):
    _new_files(monkeypatch, tmp_path, {"n1.obj": _coff(["_g"])}, ["a.obj", "b.obj", "n1.obj"])
    assert C.main(["--census-only", "n1.cpp"]) == 1
    assert "duplicate   _g" in capsys.readouterr().out


def test_a_new_file_no_matched_row_places_is_refused(monkeypatch, tmp_path):
    _new_files(monkeypatch, tmp_path, {"n1.obj": _coff(["_f"])}, ["a.obj", "b.obj"])
    with pytest.raises(SystemExit, match="no matched ledger or data row places it.*n1.cpp"):
        C.main(["n1.cpp"])


def test_a_new_object_goes_to_its_link_order_place_not_last():
    """Which definition is first decides a duplicate: a new SELECT_ANY copy
    linked before an ANY copy that precedes an exclusive one collides, the
    same copy linked last folds silently (??4AsciiString@@QAEAAV0@PBD@Z)."""
    ix = {**index(strong={"x": [1]}, comdat={"x": [(0, "d", None)]}), "objects": ["a.obj", "b.obj"],
          "aliases": {"y": [(1, "x")]}, "common": {"z": [(1, 4)]},
          "selection": {"exceptions": {"x": 1, "w": None}, "owners": {}}}
    C.place_new(ix, ["n.obj"], ["n.obj", "a.obj", "b.obj"])
    assert ix["objects"] == ["n.obj", "a.obj", "b.obj"]
    assert ix["strong"] == {"x": [2]} and ix["comdat"] == {"x": [(1, "d", None)]}
    assert ix["aliases"] == {"y": [(2, "x")]} and ix["common"] == {"z": [(2, 4)]}
    assert ix["selection"]["exceptions"] == {"x": 2, "w": None}
    assert C.duplicate("x", 0, False, 0, ix)
    last = {**index(strong={"x": [1]}, comdat={"x": [(0, "d", None)]}), "objects": ["a.obj", "b.obj"]}
    C.place_new(last, ["n.obj"], ["a.obj", "b.obj", "n.obj"])
    assert last["objects"][2] == "n.obj" and not C.duplicate("x", 2, False, 2, last)


def test_an_object_with_no_known_source_outside_the_census_is_refused(tmp_path):
    obj = tmp_path / "handmade.obj"
    obj.write_bytes(_coff(["_f"]))
    with pytest.raises(SystemExit, match="no source is known"):
        C.resolve(str(obj), index())


# Prediction-only previews avoid building global weak-provider contexts.

PREDICTION = ("prediction", "wrong_comdat", "strong_duplicate", "common_primary", "local_primary")
INVALID_RECEIPTS = ("missing_addresses", "missing_locations", "missing_ambiguous", "inconsistent_keys",
                    "wrong_address_type", "wrong_raw_holder", "mismatched_receipt", "missing_receipt")
VALID_RECEIPTS = ("actual", "alias_same", "foreign_primary", "stale_inventory", "stale_truth",
                  "stale_inputs", "stale_schema", "stale_root", "stale_token")
MALFORMED = ("strong_oob", "strong_negative_oob", "strong_position_type", "strong_rows_type",
             "comdat_oob", "comdat_position_type", "comdat_entry_short", "comdat_entries_type",
             "object_unhashable", "owners_type", "owner_members_type", "exceptions_type",
             "exception_unhashable", "selection_none", "compound_selection", "compound_missing_comdat")


def make_case(module, root, mode):
    """Real COFF and independent RetailTruth; no compiler or production writes."""
    raw, truth, _ = fixture()
    owner, table = root / "owner.obj", root / "table.obj"
    owner.write_bytes(provider_coff())
    table.write_bytes(raw)
    selection = {"owners": {"default": {owner.name}}, "exceptions": {}}
    if mode in INVALID_RECEIPTS + VALID_RECEIPTS:
        selection.update(weak_kept={"default": owner.name}, weak_locations={"default": owner.name},
                         weak_addresses={"default": 0x401040}, weak_ambiguous=set())
        if mode in ("alias_same", "foreign_primary"):
            holder = owner.name if mode == "alias_same" else "foreign.obj"
            selection["weak_kept"]["primary"] = holder
            selection["weak_locations"]["primary"] = holder
            selection["weak_addresses"]["primary"] = 0x401040 if mode == "alias_same" else 0x402000
    objects = [owner, table]
    index = module.index_tables(objects, [L.object_facts(obj, truth) for obj in objects], selection)
    index["excuses"] = {"runtime": set(), "imported": {}, "stubs": {}}
    module.refresh(index, objects, truth)
    selection = index["selection"]
    if mode == "wrong_comdat":
        index["objects"].append("foreign.obj")
        index["comdat"]["table"].append((2, "other-retail-copy", "retail"))
    elif mode == "strong_duplicate":
        index["objects"].append("foreign.obj")
        index["strong"]["table"] = [2]
    elif mode == "common_primary":
        index["common"]["primary"] = [(0, 4)]
    elif mode == "local_primary":
        table.write_bytes(add_symbol(raw, "primary"))
    elif mode.startswith("missing_"):
        selection.pop("weak_" + mode[len("missing_"):])
    elif mode == "inconsistent_keys":
        selection["weak_addresses"]["foreign"] = 0x402000
    elif mode == "wrong_address_type":
        selection["weak_addresses"]["default"] = "00401040"
    elif mode == "wrong_raw_holder":
        selection["weak_locations"]["default"] = "foreign.obj"
    elif mode == "mismatched_receipt":
        selection["weak_receipt"] = "wrong"
    elif mode == "stale_inventory":
        owner.write_bytes(provider_coff(b"\x90"))
    elif mode == "stale_truth":
        index["weak_truth"] = "previous-truth"
    elif mode == "stale_inputs":
        truth._weak_inputs = "previous-inputs"
    elif mode == "stale_schema":
        index["weak_schema"] = module.WEAK_SCHEMA - 1
    elif mode == "stale_root":
        index["weak_root"] = str(root / "other")
    elif mode == "stale_token":
        index["_weak_token"] = object()
    elif mode == "strong_oob":
        index["strong"]["unrelated"] = [99]
    elif mode == "strong_negative_oob":
        index["strong"]["unrelated"] = [-99]
    elif mode == "strong_position_type":
        index["strong"]["unrelated"] = ["0"]
    elif mode == "strong_rows_type":
        index["strong"]["unrelated"] = 1
    elif mode == "comdat_oob":
        index["comdat"]["unrelated"] = [(99, "d", "retail")]
    elif mode == "comdat_position_type":
        index["comdat"]["unrelated"] = [("0", "d", "retail")]
    elif mode == "comdat_entry_short":
        index["comdat"]["unrelated"] = [(0, "d")]
    elif mode == "comdat_entries_type":
        index["comdat"]["unrelated"] = None
    elif mode == "object_unhashable":
        index["objects"].append([])
    elif mode == "owners_type":
        selection["owners"] = []
    elif mode == "owner_members_type":
        selection["owners"]["default"] = 1
    elif mode == "exceptions_type":
        selection["exceptions"] = []
    elif mode == "exception_unhashable":
        selection["exceptions"]["default"] = []
    elif mode == "selection_none":
        index["selection"] = None
    elif mode == "compound_selection":
        index["strong"]["unrelated"] = [99]
        index["selection"] = None
    elif mode == "compound_missing_comdat":
        index["strong"]["unrelated"] = [99]
        del index["comdat"]
    truth._cache.clear()
    return table, index, truth


def observe(module, obj, index, truth, *, force_full_context=False):
    """Capture the complete preview and actual fact verdicts with empty cache."""
    truth._cache.clear()
    original_facts = L.object_facts
    facts = []
    def record(*args, **kwargs):
        if force_full_context:
            kwargs["weak_context"] = module.weak_context(index, truth)
        result = original_facts(*args, **kwargs)
        facts.append(tuple(result))
        return result
    with patch.object(module, "weak_context", wraps=module.weak_context) as full:
        with patch.object(L, "object_facts", side_effect=record):
            try:
                output = {"result": module.check_object(obj, index, truth)}
            except (IndexError, TypeError, ValueError, AttributeError) as exc:
                output = {"exception": type(exc).__name__, "message": str(exc)}
    return output, facts, full.call_count


@pytest.mark.parametrize("mode", PREDICTION + INVALID_RECEIPTS)
def test_prediction_result_equals_full_context_without_weak_promotion(tmp_path, monkeypatch, mode):
    monkeypatch.setattr(C, "ROOT", tmp_path)
    obj, index, truth = make_case(C, tmp_path, mode)
    # Independent truth state ensures neither branch reuses the other's verdict.
    reference_truth = copy.deepcopy(truth)
    optimized, facts, calls = observe(C, obj, index, truth)
    reference, original_facts, _ = observe(C, obj, index, reference_truth, force_full_context=True)
    assert optimized == reference and facts == original_facts
    assert calls == 0
    assert next(copy_[3] for copy_ in facts[0][0] if copy_[0] == "table") == "unknown"
    if mode == "wrong_comdat":
        assert optimized["result"]["comdat"]
    if mode == "strong_duplicate":
        assert optimized["result"]["duplicates"] == ["table"]


@pytest.mark.parametrize("mode", VALID_RECEIPTS)
def test_actual_receipt_keeps_full_validation_and_stale_proofs_fail(tmp_path, monkeypatch, mode):
    monkeypatch.setattr(C, "ROOT", tmp_path)
    obj, index, truth = make_case(C, tmp_path, mode)
    reference_truth = copy.deepcopy(truth)
    result, facts, calls = observe(C, obj, index, truth)
    reference, original_facts, _ = observe(C, obj, index, reference_truth, force_full_context=True)
    assert result == reference and facts == original_facts and calls == 1
    expected = "retail" if mode in ("actual", "alias_same") else "unknown"
    assert next(copy_[3] for copy_ in facts[0][0] if copy_[0] == "table") == expected


@pytest.mark.parametrize("mode", MALFORMED)
def test_malformed_global_tables_keep_original_failure(tmp_path, monkeypatch, mode):
    monkeypatch.setattr(C, "ROOT", tmp_path)
    obj, index, truth = make_case(C, tmp_path, mode)
    reference_truth = copy.deepcopy(truth)
    result, _, calls = observe(C, obj, index, truth)
    reference, _, _ = observe(C, obj, index, reference_truth, force_full_context=True)
    assert "exception" in result and result == reference and calls == 1


def test_mapping_subclass_preserves_original_access_pattern(tmp_path, monkeypatch):
    monkeypatch.setattr(C, "ROOT", tmp_path)
    obj, index, truth = make_case(C, tmp_path, "prediction")
    class CustomIndex(dict):
        def get(self, key, *args):
            if key == "objects":
                raise AssertionError("new get access on noncanonical index")
            return super().get(key, *args)
    index = CustomIndex(index)
    result, facts, calls = observe(C, obj, index, truth)
    reference, original_facts, _ = observe(C, obj, index, copy.deepcopy(truth), force_full_context=True)
    assert result == reference and facts == original_facts and calls == 1


def _status(tmp_path, monkeypatch, status_commit, linked):
    """A tracked link_status.csv measured at `status_commit` with `linked` files linked."""
    import link_census
    path = tmp_path / "link_status.csv"
    path.write_text("source,linked\n" + "".join(f"{s},{'yes' if s in linked else 'no'}\n"
                                                for s in ("a.cpp", "b.cpp", "c.cpp")), encoding="utf-8")
    monkeypatch.setattr(link_census, "STATUS", path)
    monkeypatch.setattr(link_census, "read_history", lambda: [{"commit": status_commit}] if status_commit else [])


def test_linked_since_trusts_only_a_status_at_or_after_the_census(tmp_path, monkeypatch):
    _status(tmp_path, monkeypatch, "bbbbbbbbbb", {"a.cpp"})
    order = {("aaaaaaaaaa", "bbbbbbbbbb"): True, ("cccccccccc", "bbbbbbbbbb"): False}
    monkeypatch.setattr(C, "_is_ancestor", lambda old, new: order.get((old, new)))
    assert C.linked_since("bbbbbbbbbbbbbbbb")[0] == {"a.cpp"}            # the same census, abbreviated
    assert C.linked_since("aaaaaaaaaa") == ({"a.cpp"}, "bbbbbbbbbb", "")   # a later census
    linked, status, note = C.linked_since("cccccccccc")                   # an older one
    assert linked == frozenset() and "not after census cccccccccc" in note
    linked, _, note = C.linked_since("dddddddddd")                        # one git cannot order
    assert linked == frozenset() and "cannot order" in note
    _status(tmp_path, monkeypatch, "", set())
    assert C.linked_since("aaaaaaaaaa")[0] == frozenset()


def test_queue_and_serve_drop_files_a_later_census_saw_link(tmp_path, monkeypatch, capsys):
    import claims
    blockers = {s: {"object": "a.obj", "linked": False, "unresolved": [name], "duplicates": [], "losers": [],
                    "addresses": 0}
                for s, name in (("a.cpp", "gone"), ("b.cpp", "shared"), ("c.cpp", "shared"))}
    sizes = {"a.cpp": 900, "b.cpp": 300, "c.cpp": 200}
    queue = tmp_path / "q.csv"
    monkeypatch.setattr(C, "linked_since", lambda census: (frozenset(), "", "no tracked link census"))
    C.publish(index(blockers=blockers, sizes=sizes), queue)        # the census's own queue: both rows
    monkeypatch.setattr(C, "linked_since", lambda census: (frozenset({"a.cpp"}), "later", ""))
    assert [r["name"] for r in C.queue_rows(index(blockers=blockers, sizes=sizes), {"a.cpp"})] == ["shared"]
    monkeypatch.setattr(claims, "_fetch_master", lambda: "tip")
    monkeypatch.setattr(C, "_git", lambda *a, **k: "b.cpp\n" if a[0] == "diff" else "")
    monkeypatch.setattr(claims, "owner", lambda: "me")
    monkeypatch.setattr(claims, "active", lambda: {})
    assert C.main(["next", "--no-claim", "--queue", str(queue)]) == 0
    out = capsys.readouterr().out
    # a.cpp linked at a later census; b.cpp changed, but c.cpp still stands on the census's evidence
    assert "#2 (census c; files linked at census later dropped): shared" in out
    assert "files: 1 open; 1 other(s) linked or changed since the census: c.cpp" in out
    assert "1 linked at census later" in out
    monkeypatch.setattr(C, "_git", lambda *a, **k: "b.cpp\nc.cpp\n" if a[0] == "diff" else "")
    assert C.main(["next", "--no-claim", "--queue", str(queue)]) == 1
    assert "every file linked or changed since the census" in capsys.readouterr().out


def _near_index():
    blank = {"duplicates": [], "losers": [], "wrong_selected": [], "alias_target": [], "addresses": 0,
             "linked": False}
    return {"blockers": {s: {**blank, "unresolved": ["?d_00000500@@YAXXZ"]}
                         for s in ("game/T/a.cpp", "game/T/b.cpp", "game/T/c.cpp")},
            "bytes": {"game/T/a.cpp": 30, "game/T/b.cpp": 20, "game/T/c.cpp": 10}}


class _Judge:
    def __init__(self, target="?one@@YAXXZ", note="", address=0x500):
        self.target, self.note, self.address = target, note, address

    def respell(self, name, caller=None):
        return self.target, self.note, ""

    def pinned(self, name):
        return self.address

    def normal(self, address):
        return address


def test_near_drops_files_linked_later_or_blocked_at_this_census():
    skipped = collections.Counter()
    rows = C.near_rows(_near_index(), _Judge(), skipped=skipped, linked={"game/T/a.cpp"},
                       blocked={"game/T/b.cpp": "blocked 0x00000700 at census c"})
    assert [r["source"] for r in rows] == ["game/T/c.cpp"]
    assert skipped == {C.LINKED_LATER: 1, C.BLOCKED_NOW: 1}


def _records(*verdicts):
    """re_log.latest_link_records() of these verdict rows, in log order."""
    import re_log
    return {(int(fields[1], 16), fields[0], re_log.census_source_of(fields[4])): (index, list(fields))
            for index, fields in enumerate(verdicts)}


def test_a_blocked_verdict_stands_only_at_its_own_census():
    import re_log
    callers = {"game/T/b.cpp": [_row("?b@@YAXXZ", 0x700, "game/T/b.cpp")],
               "game/T/c.cpp": [_row("?c@@YAXXZ", 0x800, "game/T/c.cpp")],
               "game/T/d.cpp": [_row("?d@@YAXXZ", 0x900, "game/T/d.cpp")]}
    latest = _records(["?b@@YAXXZ", "0x00000700", "9", "blocked", "link_check t=2 census=5f10bce6ba"],
                      ["?c@@YAXXZ", "0x00000800", "9", "blocked", "link_check t=2 census=7d308168db"],
                      ["?d@@YAXXZ", "0x00000900", "9", "landed", "link_check LINKS census=5f10bce6ba"])
    assert set(C.blocked_files(callers, latest, "5f10bce6ba0123")) == {"game/T/b.cpp"}
    assert set(C.blocked_files(callers, latest, "7d308168db")) == {"game/T/c.cpp"}
    assert C.blocked_files(callers, latest, "") == {}
    assert "blocked" in re_log.DEFERRED_STATUSES


def test_a_blocked_verdict_blocks_only_the_row_and_file_it_was_judged_in():
    """385 RVAs carry rows of several sources (0x0013A450: W3DBufferManager.cpp
    and wwmemlog.cpp); a verdict on one never suppresses the other (GPT-6.1-Sol, round 3)."""
    w3d, log = "game/W/W3DBufferManager.cpp", "game/L/wwmemlog.cpp"
    callers = {w3d: [_row("?alloc@W3DBufferManager@@QAEXXZ", 0x13A450, w3d)],
               log: [_row("?alloc@WWMemLog@@QAEXXZ", 0x13A450, log)]}
    blocked = ["?alloc@W3DBufferManager@@QAEXXZ", "0x0013A450", "9", "blocked",
               f"link_check t=2 census=5f10bce6ba census-source={w3d}"]
    assert set(C.blocked_files(callers, _records(blocked), "5f10bce6ba")) == {w3d}
    # a verdict judged in a file the row has since left blocks neither
    moved = blocked[:4] + ["link_check t=2 census=5f10bce6ba census-source=game/W/Old.cpp"]
    assert C.blocked_files(callers, _records(moved), "5f10bce6ba") == {}
    # a later resolution naming no file releases it
    landed = blocked[:3] + ["landed", "link_check LINKS 0 -> 9"]
    assert C.blocked_files(callers, _records(blocked, landed), "5f10bce6ba") == {}
    # one name at one RVA in two sources: a verdict naming no file is unsure, so it blocks nothing
    twins = {source: [_row("?alloc@Shared@@QAEXXZ", 0x13A450, source)] for source in callers}
    unnamed = ["?alloc@Shared@@QAEXXZ", "0x0013A450", "9", "blocked", "link_check t=2 census=5f10bce6ba"]
    assert C.blocked_files(twins, _records(unnamed), "5f10bce6ba", shared={(0x13A450, "?alloc@Shared@@QAEXXZ")}) == {}
    assert len(C.blocked_files(twins, _records(unnamed), "5f10bce6ba")) == 2   # the same pair, not shared
    # GPT-6.1-Sol, round 4: blocks judged in two files at one RVA both stand
    one = unnamed[:4] + [f"link_check t=2 census=5f10bce6ba census-source={w3d}"]
    two = unnamed[:4] + [f"link_check t=2 census=5f10bce6ba census-source={log}"]
    shared = {(0x13A450, "?alloc@Shared@@QAEXXZ")}
    assert set(C.blocked_files(twins, _records(one, two), "5f10bce6ba", shared)) == {w3d, log}


def test_latest_link_records_keeps_each_file_s_verdict_and_voids_the_row(tmp_path):
    import re_log
    log = tmp_path / "re_attempts.log"
    log.write_text("\r\n".join([
        "?a@@YAXXZ\t0x00000700\t9\tblocked\tlink_check census=5f10bce6ba census-source=game/A.cpp",
        "?a@@YAXXZ\t0x00000700\t9\tblocked\tlink_check census=5f10bce6ba census-source=game/B.cpp",
        "?a@@YAXXZ\t0x00000700\t9\tnote\tan annotation never votes"]) + "\r\n", encoding="utf-8")
    records = re_log.latest_link_records(log)
    assert set(records) == {(0x700, "?a@@YAXXZ", "game/A.cpp"), (0x700, "?a@@YAXXZ", "game/B.cpp")}
    with log.open("a", encoding="utf-8", newline="") as handle:
        handle.write("?a@@YAXXZ\t0x00000700\t9\tvoid\tboth rows were typed wrong\r\n")
    assert re_log.latest_link_records(log) == {}


def test_convention_reads_the_letter_after_the_scope():
    assert C.convention("??1QueuedDownload@@QAE@XZ") == "thiscall"
    assert C.convention("?getFoo@Bar@@QBEHXZ") == "thiscall"
    assert C.convention("?update@Module@@UAEXXZ") == "thiscall"
    assert C.convention("?parse@Store@@SAXPAVINI@@@Z") == "cdecl"     # static member
    assert C.convention("?releaseCodecState@@YAXPAPAUCodecState@@@Z") == "cdecl"
    assert C.convention("?Init@@YGXXZ") == "stdcall"
    assert C.convention("?f@C@@QAIXXZ") == "fastcall"
    assert C.convention("_memcpy") == "cdecl" and C.convention("_Sleep@4") == "stdcall"
    # a template scope is read by name_regression's full reader (GPT-6.1-Sol, round 5)
    assert C.convention("??A?$hash_map@VAsciiString@@H@_STL@@QAEAAHABVAsciiString@@@Z") == "thiscall"
    assert C.convention("?f@?$Box@H@@QAEXH@Z") == "thiscall" and C.convention("?g@?$Crate@H@@QAAXH@Z") == "cdecl"
    assert C.convention("?TheGlobalData@@3PAVGlobalData@@A") == ""                              # data
    # adjustor thunks encode an adjustment before the cv letter: unknown, never a wrong guess
    assert C.convention("?f@C@@W3AEXXZ") == "" and C.convention("?f@C@@W3AGXXZ") == ""
    assert C.convention("?f@C@@G7AEXXZ") == "" and C.convention("?f@C@@O3AEXXZ") == ""


def _ctx(rows_at, changed=(), refused=(), latest=None, census="5f10bce6ba"):
    by_rva, by_source = collections.defaultdict(list), collections.defaultdict(list)
    for row in rows_at:
        by_rva[int(row["target_rva"], 16)].append(row)
        by_source[row["source"]].append(row)
    return {"by_rva": by_rva, "by_source": by_source, "latest": latest or {}, "census": census,
            "changed": set(changed), "refused": set(refused)}


def _row(name, rva, source, notes=""):
    return {"name": name, "target_rva": f"0x{rva:08X}", "target_size": "128", "source": source, "notes": notes}


def test_packet_serves_a_plain_respelling_and_says_why_it_will_not_serve_the_rest():
    caller = _row("?queue@DownloadManager@@QAEXXZ", 0x627810, "game/D/Q.cpp")
    target = _row("??1QueuedDownload@@QAE@XZ", 0x500, "game/D/DownloadManager.cpp")
    near = {"source": "game/D/Q.cpp", "bytes": 334,
            "fixes": [("??1BfmeErasedValue_00627200@@QAE@XZ", "??1QueuedDownload@@QAE@XZ", "")]}
    judge = _Judge("??1QueuedDownload@@QAE@XZ")
    item = C.packet(near, judge, _ctx([caller, target]))
    assert item["verdict"] == "serve" and item["reasons"] == []
    assert item["callers"] == [caller] and item["packet_fixes"][0]["row"] == target
    assert item["packet_fixes"][0]["kind"] == "authored"
    assert item["packet_fixes"][0]["conventions"] == ("thiscall", "thiscall")
    # changed since the census, or in a family: another lane's (skip)
    assert C.packet(near, judge, _ctx([caller, target], changed={"game/D/Q.cpp"}))["verdict"] == "skip"
    family = {**near, "fixes": [("?d_00000500@@YAXXZ", "??1AsciiString@@QAE@XZ", "")]}
    item = C.packet(family, _Judge("??1AsciiString@@QAE@XZ"), _ctx([caller, target]))
    assert item["verdict"] == "skip" and "family strings" in item["reasons"][0]
    # a generated row, a convention change, a refused rename: more than a respelling (escalate)
    generated = _row("??1QueuedDownload@@QAE@XZ", 0x500, "game/gen_small/thunks_001.cpp")
    item = C.packet(near, judge, _ctx([caller, generated]))
    assert item["verdict"] == "escalate" and "gen_small" in item["reasons"][0]
    alias = _row("??1QueuedDownload@@QAE@XZ", 0x500, "game/D/DownloadManager.cpp",
                 "gen-alias;object-symbol=??1QueuedDownload@@QAE@XZ")
    assert "gen-alias" in C.packet(near, judge, _ctx([caller, alias]))["reasons"][0]
    cdecl = {**near, "fixes": [("?f@@YAXXZ", "??1QueuedDownload@@QAE@XZ", "")]}
    assert any("cdecl call to a thiscall row" in r for r in C.packet(cdecl, judge, _ctx([caller, target]))["reasons"])
    # a rename the hook refuses, whether the owner, an operator's owner or an argument type carries it
    for call, target in (("?release@CodecState@@QAEXXZ", "?release@BfmeThingJT@@QAEXXZ"),
                         ("??RCodecState@@QBE_NH@Z", "??RBfmeThingJT@@QBE_NH@Z"),
                         ("?releaseCodecState@@YAXPAPAUCodecState@@@Z", "?releaseCodecState@@YAXPAPAUBfmeThingJT@@@Z")):
        item = C.packet({**near, "fixes": [(call, target, "")]}, _Judge(target),
                        _ctx([caller, _row(target, 0x500, "game/D/D.cpp")], refused={("CodecState", "BfmeThingJT")}))
        assert item["verdict"] == "escalate", call
        assert "name_regression refuses CodecState -> BfmeThingJT" in item["reasons"], call
    # a call of another shape (here one class argument fewer) is a declaration change, not a respelling
    item = C.packet({**near, "fixes": [("?run@Display@@QAEXPBVImage@@H@Z", "?run@Bfme5Host@@QAEXHH@Z", "")]},
                    _Judge("?run@Bfme5Host@@QAEXHH@Z"), _ctx([caller, _row("?run@Bfme5Host@@QAEXHH@Z", 0x500, "D.cpp")]))
    assert item["verdict"] == "escalate" and "differ in shape" in item["reasons"][0]
    # same identifier counts, another declaration (GPT-6.1-Sol, round 2): a free function called
    # as a class's operator delete with one argument fewer, and a void(Class*) called as Class()
    for call, target in (("?bfmeDeleteVMP@@YAXPAXI@Z", "??3Gen007F0170@@SAXPAX@Z"),
                         ("?f@?$Box@H@@QAEXPAU1@@Z", "?g@?$Crate@M@@QAEXPAU1@@Z"),     # <int> against <float>, round 3
                         ("?bfmeCallDQF@BfmeSubDQF@@QAEXPAVBfmeOtherDQF@@@Z",
                          "?Get_Texture@ParticleBufferClass@@QBE?AVTextureHandleClass@1@XZ")):
        item = C.packet({**near, "fixes": [(call, target, "")]}, _Judge(target),
                        _ctx([caller, _row(target, 0x500, "D.cpp")]))
        assert item["verdict"] == "escalate" and any("differ in shape" in r for r in item["reasons"]), call
    # and a name the reader cannot parse (a function-pointer argument) is left to the hook
    pointer = "?run@Host@@QAEXP6AXXZ@Z"
    item = C.packet({**near, "fixes": [("?run@Shim@@QAEXP6AXXZ@Z", pointer, "")]}, _Judge(pointer),
                    _ctx([caller, _row(pointer, 0x500, "D.cpp")]))
    assert item["verdict"] == "escalate" and "cannot read" in item["reasons"][0]


def test_packet_marks_prior_verdicts_current_or_stale():
    caller = _row("?queue@DownloadManager@@QAEXXZ", 0x627810, "game/D/Q.cpp")
    target = _row("??1QueuedDownload@@QAE@XZ", 0x500, "game/D/DownloadManager.cpp")
    near = {"source": "game/D/Q.cpp", "bytes": 334,
            "fixes": [("??1BfmeErasedValue_00627200@@QAE@XZ", "??1QueuedDownload@@QAE@XZ", "")]}
    verdict = [caller["name"], "0x00627810", "334", "blocked", "link_check t=3 census=7d308168db"]
    item = C.packet(near, _Judge("??1QueuedDownload@@QAE@XZ"), _ctx([caller, target], latest=_records(verdict)))
    assert item["prior"][0]["when"] == "stale: census 7d308168db" and item["verdict"] == "serve"
    verdict[4] = "link_check t=3"
    assert C.packet(near, _Judge(), _ctx([caller, target], latest=_records(verdict)))["prior"][0]["when"] == "no census"


def test_near_lists_served_files_and_prints_a_packet(monkeypatch, capsys, tmp_path):
    ix = {**_near_index(), "meta": {"date": "d", "commit": "5f10bce6ba"}, "alias_schema": C.ALIAS_SCHEMA}
    monkeypatch.setattr(C, "INDEX", tmp_path / "link_census" / "link_index.pkl")   # its receipts land here
    rows = [_row("?a@@YAXXZ", 0x600, "game/T/a.cpp"), _row("?b@@YAXXZ", 0x700, "game/T/b.cpp"),
            _row("?c@@YAXXZ", 0x800, "game/T/c.cpp"), _row("?one@@YAXXZ", 0x500, "game/T/one.cpp")]
    monkeypatch.setattr(C, "load_index", lambda: ix)
    monkeypatch.setattr(C, "_git", lambda *a, **k: "game/T/c.cpp\n")
    monkeypatch.setattr(C, "linked_since", lambda census: (frozenset({"game/T/a.cpp"}), census, ""))
    monkeypatch.setattr(C, "alias_judge", lambda: _Judge())
    monkeypatch.setattr(C.link_census, "ledger", lambda: rows)
    import name_regression
    import re_log
    monkeypatch.setattr(re_log, "latest_link_records", lambda path=None: {})
    monkeypatch.setattr(name_regression, "refused_respellings", lambda pairs, root=None, ref="HEAD": set())
    assert C.main(["near"]) == 0
    out = capsys.readouterr().out
    assert "2 files, 30 bytes; 1 serve, 1 skip, 0 escalate; 1 skipped: linked at a later census" in out
    assert "game/T/b.cpp  [serve]" in out and "game/T/c.cpp" not in out.split("\n", 1)[1]
    assert C.main(["near", "--verdict", "skip"]) == 0
    assert "game/T/c.cpp  [skip (changed since the index's census" in capsys.readouterr().out
    assert C.main(["near", "--packet", "game/T/b.cpp"]) == 0
    out = capsys.readouterr().out
    assert "verdict: serve" in out and "caller  ?b@@YAXXZ 0x00000700 128 B" in out
    assert "row 0x00000500 128 B authored game/T/one.cpp; convention cdecl -> cdecl" in out
    assert "python3 tools/re_log.py record '?b@@YAXXZ' 0x00000700 128 blocked" in out
    assert "census=5f10bce6ba" in out
    receipt = tmp_path / "link_census" / C.RECEIPTS / C.receipt_name(0x700, "?b@@YAXXZ", "game/T/b.cpp")
    assert receipt.exists()                                                         # the packet judged it
    assert C.main(["near", "--packet", "game/T/a.cpp"]) == 1
    assert "game/T/a.cpp is not a near file at census 5f10bce6ba: linked at census 5f10bce6ba" in (
        capsys.readouterr().out)
    monkeypatch.setattr(re_log, "latest_link_records", lambda path=None: _records(
        ["?b@@YAXXZ", "0x00000700", "128", "blocked", "link_check t=2 census=5f10bce6ba"]))
    assert C.main(["near", "--packet", "game/T/b.cpp"]) == 1
    assert "blocked: blocked 0x00000700 at census 5f10bce6ba" in capsys.readouterr().out
    # a verdict judged against an older index blocks nothing once near serves from a newer one,
    # even when link_status.csv is newer still (GPT-6.1-Sol, review round 1)
    monkeypatch.setattr(re_log, "latest_link_records", lambda path=None: _records(
        ["?b@@YAXXZ", "0x00000700", "128", "blocked", "link_check t=2 census=7d308168db"]))
    monkeypatch.setattr(C, "linked_since", lambda census: (frozenset({"game/T/a.cpp"}), "9999999999", ""))
    assert C.main(["near", "--packet", "game/T/b.cpp"]) == 0
    assert "prior   blocked 0x00000700 (stale: census 7d308168db)" in capsys.readouterr().out


def test_a_check_leaves_per_row_receipts_re_log_tags_from(tmp_path, monkeypatch):
    """The census comes from the index that judged the row's file, per row:
    a later check of another file at another census does not retag it."""
    import re_log
    monkeypatch.setattr(C, "INDEX", tmp_path / "link_census" / "link_index.pkl")
    monkeypatch.setattr(re_log, "EVALUATED", tmp_path / "link_census" / C.RECEIPTS)
    b = ("7d308168db", "game/T/b.cpp")
    C.note_evaluated([_row("?b@@YAXXZ", 0x700, "game/T/b.cpp"), _row("?b2@@YAXXZ", 0x704, "game/T/b.cpp")],
                     "7d308168db")
    C.note_evaluated([_row("?c@@YAXXZ", 0x800, "game/T/c.cpp")], "5f10bce6ba")
    assert re_log.evaluated_census("0x00000700", "?b@@YAXXZ") == re_log.evaluated_census("0x704", "?b2@@YAXXZ") == b
    assert re_log.evaluated_census("0x00000800", "?c@@YAXXZ") == ("5f10bce6ba", "game/T/c.cpp")
    assert re_log.evaluated_census("0x00000900", "?d@@YAXXZ") == ("", "")     # never judged here: no tag
    assert re_log.evaluated_census("0x00000700", "?other@@YAXXZ") == ("", "")  # another row at that RVA
    # another source's row at the same RVA has its own receipt and never retags this one
    C.note_evaluated([_row("?x@@YAXXZ", 0x700, "game/T/x.cpp")], "5f10bce6ba")
    assert re_log.evaluated_census("0x00000700", "?b@@YAXXZ") == b
    C.note_evaluated([_row("?b@@YAXXZ", 0x700, "game/T/b.cpp")], "5f10bce6ba")   # re-judged
    assert re_log.evaluated_census("0x00000700", "?b@@YAXXZ") == ("5f10bce6ba", "game/T/b.cpp")
    # the same row judged in a second file (rehomed, or a twin): unsure, so no tag
    C.note_evaluated([_row("?b@@YAXXZ", 0x700, "game/T/moved.cpp")], "5f10bce6ba")
    assert re_log.evaluated_census("0x00000700", "?b@@YAXXZ") == ("", "")
    C.note_evaluated([_row("?d@@YAXXZ", 0x900, "game/T/d.cpp")], "")             # no census: no receipt
    assert re_log.evaluated_census("0x00000900", "?d@@YAXXZ") == ("", "")


def test_the_printed_record_command_records_a_census_bound_block(tmp_path, monkeypatch):
    """Filled in as printed, the packet's command passes re_log's tag rules and
    carries the census near served from, whatever words its evidence uses."""
    import shlex
    import re_log
    log = tmp_path / "re_attempts.log"
    log.write_text("", encoding="utf-8")
    monkeypatch.setattr(re_log, "RE_ATTEMPTS", log)
    monkeypatch.setattr(re_log, "EVALUATED", tmp_path / "absent.json")
    monkeypatch.delenv("BFME_RUN_ID", raising=False)
    re_log._reset()
    try:
        command = C.record_command(_row("?b@@YAXXZ", 0x700, "game/T/b.cpp"), "7d308168db")
        filled = (command.replace("<what stopped it>", "ABI mismatch").replace("<family>/<detail>", "identity/abi")
                  .replace("<min>", "20").replace("<model>", "test-model"))
        argv = shlex.split(filled)
        assert argv[:4] == ["python3", "tools/re_log.py", "record", "?b@@YAXXZ"]
        re_log._record(argv[3:])
        fields = log.read_text(encoding="utf-8").splitlines()[-1].split("\t")
        assert fields[3] == "blocked" and re_log.census_of(fields[4]) == "7d308168db"
        assert re_log.census_source_of(fields[4]) == "game/T/b.cpp"
        assert C.blocked_files({"game/T/b.cpp": [_row("?b@@YAXXZ", 0x700, "game/T/b.cpp")]}, re_log.latest_link_records(log),
                               "7d308168db") == {"game/T/b.cpp": "blocked 0x00000700 at census 7d308168db"}
    finally:
        re_log._reset()


def test_census_only_refreshes_every_new_file_so_new_files_see_each_other(monkeypatch, tmp_path, capsys):
    """owner verdict 2026-10-13 (adversarial review round 2: test gaps): under
    --census-only the census holds nothing for new files, so each one is
    refreshed from its own object; a reference between two new files resolves."""
    _new_files(monkeypatch, tmp_path, {"n1.obj": _coff(["_f"], ["_h"]), "n2.obj": _coff(["_h"])},
               ["a.obj", "b.obj", "n1.obj", "n2.obj"])
    assert C.main(["--census-only", "n1.cpp", "n2.cpp"]) == 0
    out = capsys.readouterr().out
    assert "unresolved" not in out and "2 of 2 link cleanly" in out
