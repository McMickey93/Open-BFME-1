"""Nearby supported and refused cases for the round-1 defect classes."""
import struct

import pytest

from test_cycle_review2b_evidence import case, outcome
from test_cycle_review2_evidence import (
    F, A, DATA, RDATA, TYPE, ACTION, dword, lc, eh_case, verified_eh_providers,
)


@pytest.mark.parametrize("target_offset,closed", [(1, False), (2, False), (3, True)])
def test_adjacent_rows_do_not_cover_the_gap_between_them(case, target_offset, closed):
    body = b"\xc3\x90\x90\xc3"
    obj = case.object("provider.obj", [(".text", body, [])],
                      [("_head", 1, 0, lc.EXTERNAL), ("_middle", 1, target_offset, lc.EXTERNAL),
                       ("_tail", 1, 3, lc.EXTERNAL)])
    case.row(obj, "_head", A, 1)
    case.row(obj, "_tail", A + 3, 1)
    case.public(obj, "_head", A)
    case.public(obj, "_middle", A + target_offset)
    case.public(obj, "_tail", A + 3)
    case.put(A, body, retail=body)
    raw = b"\xe8" + bytes(4) + b"\xc3"
    caller = case.object("caller.obj", [(".text", raw, [(1, "_middle", lc.REL32)])],
                         [("_caller", 1, 0, lc.EXTERNAL), ("_middle", 0, 0, lc.EXTERNAL)])
    case.row(caller, "_caller", F, len(raw))
    case.public(caller, "_caller", F)
    code = b"\xe8" + dword(A + target_offset - F - 5) + b"\xc3"
    case.put(F, code, retail=code)
    _, row = outcome(case)
    assert row["closed_strict"] == str(int(closed))


@pytest.mark.parametrize("fault", [None, "inner-state", "inner-type", "inner-funclet", "catch-cap"])
def test_nested_eh_tables_require_every_inner_dependency(case, fault):
    eh_case(case, states=3)
    verified_eh_providers(case)
    descriptor = bytes(8) + b".?AVRight@@\0"
    obj = case.object("type.obj", [(".rdata", descriptor, [])], [("_type", 1, 0, lc.EXTERNAL)])
    case.public(obj, "_type", TYPE)
    case.put(TYPE, descriptor)
    case.R[TYPE + 64:TYPE + 64 + len(descriptor)] = descriptor
    case.retail_extent('_type', TYPE + 64, 19)  # independent EH descriptor extent
    for image, fi, ty in ((case.I, DATA, TYPE), (case.R, RDATA, TYPE + 64)):
        image[fi + 12:fi + 20] = dword(2) + dword(lc.BASE + fi + 0x200)
        for n, (lo, hi, ch) in enumerate(((0, 2, 3), (1, 1, 2))):
            at, handlers = fi + 0x200 + 20 * n, fi + 0x250 + 16 * n
            image[at:at + 20] = struct.pack("<iiiiI", lo, hi, ch, 1, lc.BASE + handlers)
            image[handlers:handlers + 16] = struct.pack("<IIiI", 0, lc.BASE + ty, 0, lc.BASE + ACTION)
            if image is case.I:
                case.shift_sites.update({at + 16, handlers + 4, handlers + 12})
    case.shift_sites.add(DATA + 16)
    if fault == "inner-state":
        case.I[DATA + 0x214:DATA + 0x218] = dword(0)
    elif fault == "inner-type":
        case.I[TYPE + 12] = ord("X")
    elif fault == "inner-funclet":
        case.ptr(DATA + 0x26C, ACTION + 16)
        case.put(ACTION + 16, b"\xc3")  # Unledgered even though it returns.
    elif fault == "catch-cap":
        case.I[DATA + 0x220:DATA + 0x224] = dword(21)
    _, row = outcome(case)
    assert row["closed_strict"] == str(int(fault is None))


@pytest.mark.parametrize("symbolic", [False, True])
def test_packed_unaligned_data_pointer_requires_symbolic_evidence(case, symbolic):
    leaf = case.object("leaf.obj", [(".text", b"\xc3", [])], [("_a", 1, 0, lc.EXTERNAL)])
    case.row(leaf, "_a", A, 1)
    case.public(leaf, "_a", A)
    case.put(A, b"\xc3", retail=b"\xc3")
    body = b"x" + (bytes(4) if symbolic else dword(lc.BASE + A))
    rels = [(1, "_a", lc.DIR32)] if symbolic else []
    data = case.object("packed.obj", [(".data", body, rels)],
                       [("_packed", 1, 0, lc.EXTERNAL), ("_a", 0, 0, lc.EXTERNAL)])
    case.public(data, "_packed", DATA)
    case.put(DATA, b"x" + dword(lc.BASE + A))
    if symbolic:
        case.ptr(DATA + 1, A)
    case.R[RDATA:RDATA + 5] = b"x" + dword(lc.BASE + A)
    raw = b"\xa1" + dword(1) + b"\xff\xd0\xc3"
    caller = case.object("caller.obj", [(".text", raw, [(1, "_packed", lc.DIR32)])],
                         [("_caller", 1, 0, lc.EXTERNAL), ("_packed", 0, 0, lc.EXTERNAL)])
    case.row(caller, "_caller", F, len(raw))
    case.public(caller, "_caller", F)
    case.put(F, raw, retail=raw)
    case.ptr(F + 1, DATA + 1)
    case.R[F + 1:F + 5] = dword(lc.BASE + RDATA + 1)
    case.R[:2] = b"MZ"
    case.patch.setattr(lc.retail_relocs, "site_rvas", lambda: (RDATA + 1,))
    _, row = outcome(case)
    assert row["closed_strict"] == str(int(symbolic))


@pytest.mark.parametrize("axis", [0, 1])
@pytest.mark.parametrize("same_offset", [False, True])
def test_overlapping_datum_intervals_keep_the_same_translation(axis, same_offset):
    # Exercise the production global overlap pass with abstract provider
    # extents, including overlap chains where first and last do not overlap.
    m = lc.Measure.__new__(lc.Measure)
    m._init_state()
    keys = [(100, 200, 8), (104, 204, 8), (110, 210 if same_offset else 240, 8)]
    if axis:
        keys = [(b, a, size) for a, b, size in keys]
    m.dnodes.update({k: {} for k in keys})
    m.discover([])
    assert m.datum_conflicts == (set() if same_offset else set(keys))


@pytest.mark.parametrize("generated", [False, True])
def test_distinct_body_twin_reached_only_through_a_vtable_is_refused(case, generated):
    from test_cycle_review2_evidence import B
    raw = b"\x31\xc0\xc3"
    leaf = case.object("leaf.obj", [(".text", raw, [])], [("_a", 1, 0, lc.EXTERNAL)])
    case.row(leaf, "_a", A, len(raw), source="game/gen_small/leaf.cpp" if generated else "game/leaf.cpp")
    case.public(leaf, "_a", A)
    case.put(A, raw, retail=raw)
    case.R[B:B + len(raw)] = raw  # Byte twin with a distinct retail identity.
    table = case.object("table.obj", [(".rdata", bytes(4), [(0, "_a", lc.DIR32)])],
                        [("_table", 1, 0, lc.EXTERNAL), ("_a", 0, 0, lc.EXTERNAL)])
    case.public(table, "_table", DATA)
    case.ptr(DATA, A)
    case.R[RDATA:RDATA + 4] = dword(lc.BASE + B)
    raw = b"\xa1" + bytes(4) + b"\xff\xd0\xc3"
    caller = case.object("caller.obj", [(".text", raw, [(1, "_table", lc.DIR32)])],
                         [("_caller", 1, 0, lc.EXTERNAL), ("_table", 0, 0, lc.EXTERNAL)])
    case.row(caller, "_caller", F, len(raw))
    case.public(caller, "_caller", F)
    case.put(F, raw, retail=raw)
    case.ptr(F + 1, DATA)
    case.R[F + 1:F + 5] = dword(lc.BASE + RDATA)
    _, row = outcome(case)
    assert row["closed_strict"] == "0"
