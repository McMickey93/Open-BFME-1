"""Round-2 independent measurement counterexamples; no native build or link.

Assertions express the required safe behavior and intentionally fail on the
reviewed implementation. ImageCase stubs only input images and object paths;
production COFF parsing, measurement, shift checks, graph and credit all run.
"""
import json

import pytest

from test_cycle_review2_evidence import (
    ImageCase, F, A, B, DATA, RDATA, dword, lc,
)


@pytest.fixture
def case(tmp_path, monkeypatch):
    return ImageCase(tmp_path, monkeypatch)


def outcome(case, name="_caller"):
    result, rows = case.measure()
    row = next(r for r in rows if r["name"] == name)
    print(json.dumps({"credit": result["credit_unique_bytes"], "row": row}, sort_keys=True))
    return result, row


@pytest.mark.parametrize("offset,width", [(0, 4), (1, 4), (3, 4), (0, 8)])
def test_memory_access_must_cover_its_entire_width(case, offset, width):
    # The named four-byte object matches. Bytes immediately after it do not.
    prefix = b"\xa1" if width == 4 else b"\xdd\x05"  # mov eax / fld qword
    raw = prefix + dword(offset) + b"\xc3"
    site = len(prefix)
    caller = case.object("caller.obj", [(".text", raw, [(site, "_g", lc.DIR32)])],
                         [("_caller", 1, 0, lc.EXTERNAL), ("_g", 0, 0, lc.EXTERNAL)])
    data = case.object("data.obj", [(".data", bytes(4), [])], [("_g", 1, 0, lc.EXTERNAL)])
    case.row(caller, "_caller", F, len(raw))
    case.public(caller, "_caller", F)
    case.public(data, "_g", DATA)
    case.put(F, raw, retail=raw)
    case.ptr(F + site, DATA + offset)
    case.R[F + site:F + site + 4] = dword(lc.BASE + RDATA + offset)
    case.put(DATA, bytes(4) + b"\x02" * 8)
    case.R[RDATA:RDATA + 12] = bytes(4) + b"\x01" * 8
    _, row = outcome(case)
    assert row["closed_strict"] == str(int(offset + width <= 4)), "load crosses into unverified storage"


@pytest.mark.parametrize("through_table", [False, True])
def test_interior_code_entry_must_have_its_control_flow_followed(case, through_table):
    # Entry A returns. Entry A+1 calls an unledgered, wrong local helper B.
    # Such entries are also how switch-table destinations reach case arms.
    body = b"\xc3\xe8" + dword(B - A - 6) + b"\xc3"
    obj = case.object("provider.obj", [(".text", body, [])], [("_a", 1, 0, lc.EXTERNAL)])
    case.row(obj, "_a", A, len(body))
    case.public(obj, "_a", A)
    case.put(A, body, retail=body)
    case.put(B, b"\xb8\x02\0\0\0\xc3", retail=b"\xb8\x01\0\0\0\xc3")
    if through_table:
        table = case.object("table.obj", [(".rdata", dword(1), [(0, "_a", lc.DIR32)])],
                            [("_table", 1, 0, lc.EXTERNAL), ("_a", 0, 0, lc.EXTERNAL)])
        case.public(table, "_table", DATA)
        case.ptr(DATA, A + 1)
        case.R[RDATA:RDATA + 4] = dword(lc.BASE + A + 1)
        raw, target, lt, rt = b"\xa1" + bytes(4) + b"\xff\xd0\xc3", "_table", DATA, RDATA
    else:
        raw, target, lt, rt = b"\xb8" + dword(1) + b"\xff\xd0\xc3", "_a", A + 1, A + 1
    caller = case.object("caller.obj", [(".text", raw, [(1, target, lc.DIR32)])],
                         [("_caller", 1, 0, lc.EXTERNAL), (target, 0, 0, lc.EXTERNAL)])
    case.row(caller, "_caller", F, len(raw))
    case.public(caller, "_caller", F)
    case.put(F, raw, retail=raw)
    case.ptr(F + 1, lt)
    case.R[F + 1:F + 5] = dword(lc.BASE + rt)
    _, row = outcome(case)
    assert row["closed_strict"] == "0", "interior entry hides an unverified direct-call dependency"


@pytest.mark.parametrize("inline_data", [False, True])
def test_reachable_literal_address_after_inline_data_must_not_close(case, inline_data):
    prefix = b"\xeb\x02\x0f\x0f" if inline_data else b""
    raw = prefix + b"\xa1" + dword(lc.BASE + DATA) + b"\xc3"
    obj = case.object("caller.obj", [(".text", raw, [])], [("_caller", 1, 0, lc.EXTERNAL)])
    case.row(obj, "_caller", F, len(raw))
    case.public(obj, "_caller", F)
    case.put(F, raw, retail=raw)
    case.put(DATA, dword(2), retail=dword(1))
    # Even retained retail HIGHLOW evidence does not feed the code scanner.
    case.R[:2] = b"MZ"
    case.patch.setattr(lc.retail_relocs, "site_rvas", lambda: (F + len(prefix) + 1,))
    _, row = outcome(case)
    assert row["closed_strict"] == "0", "linear hardcoded scanner misses reachable code after inline data"


def test_direct_calls_via_multiple_ilt_routes_keep_allowed_credit(case):
    # BFME1 build.py build_call_thunks/load_symbol_map explicitly permits this:
    # incremental links leave several ILT routes to the same retail body.
    obj = case.object("leaf.obj", [(".text", b"\xc3", [])], [("_a", 1, 0, lc.EXTERNAL)])
    case.row(obj, "_a", A, 1)
    case.public(obj, "_a", A)
    case.put(A, b"\xc3", retail=b"\xc3")
    for i, thunk in enumerate((0x20000, 0x20010)):
        case.R[thunk:thunk + 5] = b"\xe9" + dword(A - thunk - 5)
        name, at = f"_caller{i}", F + i * 16
        raw = b"\xe8" + bytes(4) + b"\xc3"
        caller = case.object(f"caller{i}.obj", [(".text", raw, [(1, "_a", lc.REL32)])],
                             [(name, 1, 0, lc.EXTERNAL), ("_a", 0, 0, lc.EXTERNAL)])
        case.row(caller, name, at, len(raw))
        case.public(caller, name, at)
        case.put(at, b"\xe8" + dword(A - at - 5) + b"\xc3",
                 retail=b"\xe8" + dword(thunk - at - 5) + b"\xc3")
        case.patch.setattr(lc.build, "read_target_bytes", lambda at, size: bytes(case.R[at:at + size]))
        checked = lc.build.compile_function(case.rows[-1], {"_a": [A, 0x20000, 0x20010]}, caller)
        assert checked["bytes"] == checked["target"] and not checked["unresolved"]
    result, _ = outcome(case, "_caller0")
    assert result["credit_unique_bytes"] == 13, "allowed direct-call routes lost C++ credit"


def test_one_retail_code_pointer_must_not_split_between_thunk_and_body(case):
    # Each provider has its own legitimate retail identity; no duplicate ledger
    # home is needed. One use keeps the ILT and another substitutes its body.
    thunk = 0x20000
    case.sections = lc.SectionList([
        (".text", 0x1000, 0x6F000), (".rdata", 0x80000, 0x10000), (".stubd", 0x90000, 0x1000)])
    leaf = case.object("leaf.obj", [(".text", b"\xc3", [])], [("_a", 1, 0, lc.EXTERNAL)])
    case.row(leaf, "_a", A, 1)
    case.public(leaf, "_a", A)
    case.put(A, b"\xc3", retail=b"\xc3")
    name = "?j_00020000@@YAXXZ"
    jump = b"\xe9" + dword(A - thunk - 5)
    obj = case.object("thunk.obj", [(".text", b"\xe9" + bytes(4), [(1, "_a", lc.REL32)])],
                      [(name, 1, 0, lc.EXTERNAL), ("_a", 0, 0, lc.EXTERNAL)])
    case.row(obj, name, thunk, len(jump))
    case.public(obj, name, thunk)
    case.put(thunk, jump, retail=jump)
    raw = b"\xb8" + bytes(4) + b"\x3d" + bytes(4) + b"\x0f\x94\xc0\xc3"
    caller = case.object("caller.obj", [(".text", raw, [(1, "_a", lc.DIR32), (6, name, lc.DIR32)])],
                         [("_caller", 1, 0, lc.EXTERNAL), ("_a", 0, 0, lc.EXTERNAL), (name, 0, 0, lc.EXTERNAL)])
    case.row(caller, "_caller", F, len(raw))
    case.public(caller, "_caller", F)
    case.put(F, raw, retail=raw)
    case.ptr(F + 1, A)
    case.ptr(F + 6, thunk)
    case.R[F + 1:F + 5] = case.R[F + 6:F + 10] = dword(lc.BASE + thunk)
    assert lc.u32(case.R, F + 1) == lc.u32(case.R, F + 6)
    assert lc.u32(case.I, F + 1) != lc.u32(case.I, F + 6)
    _, row = outcome(case)
    assert row["closed_strict"] == "0", "one retail pointer split into unequal linked pointers"


@pytest.mark.parametrize("notes", ["gen-tgrid", "gen-funclet", "gen-import", "gen-alias"])
@pytest.mark.parametrize("through_library", [False, True])
def test_all_generated_kinds_must_block_source_closure(case, notes, through_library):
    leaf = case.object("leaf.obj", [(".text", b"\xc3", [])], [("_leaf", 1, 0, lc.EXTERNAL)])
    case.row(leaf, "_leaf", B, 1, source="game/gen_small/leaf.cpp", notes=notes)
    case.public(leaf, "_leaf", B)
    case.put(B, b"\xc3", retail=b"\xc3")
    target, at_target = "_leaf", B
    if through_library:
        raw = b"\xe8" + bytes(4) + b"\xc3"
        obj = case.object("library.obj", [(".text", raw, [(1, "_leaf", lc.REL32)])],
                          [("_library", 1, 0, lc.EXTERNAL), ("_leaf", 0, 0, lc.EXTERNAL)])
        case.row(obj, "_library", A, 6, source="inputs/vendor/example/example.lib")
        case.public(obj, "_library", A)
        case.put(A, b"\xe8" + dword(B - A - 5) + b"\xc3",
                 retail=b"\xe8" + dword(B - A - 5) + b"\xc3")
        target, at_target = "_library", A
    raw = b"\xe8" + bytes(4) + b"\xc3"
    caller = case.object("caller.obj", [(".text", raw, [(1, target, lc.REL32)])],
                         [("_caller", 1, 0, lc.EXTERNAL), (target, 0, 0, lc.EXTERNAL)])
    case.row(caller, "_caller", F, 6)
    case.public(caller, "_caller", F)
    case.put(F, b"\xe8" + dword(at_target - F - 5) + b"\xc3",
             retail=b"\xe8" + dword(at_target - F - 5) + b"\xc3")
    result, row = outcome(case)
    import closure_report as cr
    graph = cr.load_graph(case.root / "measurement" / cr.GRAPH_FILE)
    assert cr.credit_of(*graph[:3]) == result["credit_unique_bytes"]
    assert row["closed_strict"] == "0", "early gen-* classification bypasses generated dependency exclusion"


def test_padding_only_extent_change_cannot_increase_progress(case):
    # Identical source, object and images; only the ledger's claimed extent grows.
    # progress.py explicitly subtracts 0xCC in every numerator/denominator.
    import progress
    raw = b"\xc3" + b"\xcc" * 15
    obj = case.object("caller.obj", [(".text", raw, [])], [("_caller", 1, 0, lc.EXTERNAL)])
    case.row(obj, "_caller", F, 1)
    case.public(obj, "_caller", F)
    case.put(F, raw, retail=raw)
    before_image = bytes(case.I)
    case.patch.setattr(lc.build, "read_target_bytes", lambda at, size: bytes(case.R[at:at + size]))
    for size in (1, len(raw)):
        checked = lc.build.compile_function(dict(case.rows[0], target_size=str(size)), {}, obj,
                                            retain_compiled=True)
        assert checked["bytes"] == checked["target"]
        assert lc.build.claimed_boundary_issue(checked["compiled"], size) is None
    before, _ = outcome(case)
    case.rows[0]["target_size"] = str(len(raw))
    after, _ = outcome(case)
    assert bytes(case.I) == before_image
    case.patch.setattr(progress, "_text_image", lambda: (F, raw))
    key = ("_caller", f"0x{F:08X}")
    official = [progress.decompiled(progress.real_split(
        {key: (size, "game/caller.cpp")}, {key: ""}, F, len(raw))) for size in (1, len(raw))]
    print({"BFME1_nonpadding_credit": official,
           "cycle_credit": [before["credit_unique_bytes"], after["credit_unique_bytes"]]})
    assert official == [1, 1]
    assert after["credit_unique_bytes"] == before["credit_unique_bytes"], "ledger padding alone earns progress"
