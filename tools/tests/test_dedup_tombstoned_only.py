"""dedup_csv --tombstoned-only: drop resurrected rows without reordering anything."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import dedup_csv  # noqa: E402


def test_only_tombstoned_lines_go_and_order_and_eol_survive(tmp_path):
    ledger = tmp_path / "functions.csv"
    ledger.write_bytes(b"name,export_rva,target_rva,target_size,source,status,notes\r\n"
                       b"?z@@YAXXZ,,0x00000200,4,b.cpp,matched,\r\n"
                       b"?d_00000100@@YAXXZ,,0x00000100,8,d.asm,matched,\r\n"
                       b"?a@@YAXXZ,,0x00000100,8,a.cpp,matched,\n")
    dropped = dedup_csv.drop_tombstoned_in_place(ledger, {("?d_00000100@@YAXXZ", 0x100)})
    assert dropped == [("?d_00000100@@YAXXZ", 0x100)]
    assert ledger.read_bytes() == (b"name,export_rva,target_rva,target_size,source,status,notes\r\n"
                                   b"?z@@YAXXZ,,0x00000200,4,b.cpp,matched,\r\n"
                                   b"?a@@YAXXZ,,0x00000100,8,a.cpp,matched,\n")


def test_nothing_tombstoned_leaves_the_file_untouched(tmp_path):
    ledger = tmp_path / "functions.csv"
    ledger.write_bytes(b"name,export_rva,target_rva\r\n?a@@YAXXZ,,0x00000100\r\n")
    before = ledger.stat().st_mtime_ns
    assert dedup_csv.drop_tombstoned_in_place(ledger, {("?b@@YAXXZ", 0x100)}) == []
    assert ledger.stat().st_mtime_ns == before


def test_merge_repair_drops_tombstones_and_exact_duplicates_only(tmp_path):
    ledger = tmp_path / "functions.csv"
    ledger.write_bytes(b"name,export_rva,target_rva,target_size,source,status,notes\r\n"
                       b"?a@@YAXXZ,,0x00000100,8,a.cpp,matched,\r\r\n"
                       b"?d_00000200@@YAXXZ,,0x00000200,8,d.asm,matched,\r\n"
                       b"?b@@YAXXZ,,0x00000300,8,b.cpp,matched,\r\n"
                       b"?a@@YAXXZ,,0x00000100,8,a.cpp,matched,\r\n")
    dropped = dedup_csv.merge_repair(ledger, {("?d_00000200@@YAXXZ", 0x200)})
    assert dropped == ["tombstoned ?d_00000200@@YAXXZ", "duplicate ?a@@YAXXZ"]
    assert ledger.read_bytes() == (b"name,export_rva,target_rva,target_size,source,status,notes\r\n"
                                   b"?a@@YAXXZ,,0x00000100,8,a.cpp,matched,\r\r\n"
                                   b"?b@@YAXXZ,,0x00000300,8,b.cpp,matched,\r\n")


@pytest.mark.parametrize("tombstone,removed", [(0x5F590, True), (0x16F86, False)])
def test_merge_repair_uses_target_address_not_export_address(tmp_path, tombstone, removed):
    # Real ledger rows have different export and target addresses. A tombstone
    # names the target; matching the export either resurrects or deletes a row.
    ledger = tmp_path / "functions.csv"
    before = (b"name,export_rva,target_rva,target_size,source,status,notes\r\n"
              b"?z@@YAXXZ,,0x00000200,4,z.cpp,matched,\r\r\n")
    row = b"?mapped@@YAXXZ,0x00016F86,0x0005F590,52,m.cpp,matched,evidence\r\n"
    after = b"?a@@YAXXZ,,0x00000300,8,a.cpp,matched,\n"
    ledger.write_bytes(before + row + after)
    original_mtime = ledger.stat().st_mtime_ns

    dropped = dedup_csv.merge_repair(ledger, {("?mapped@@YAXXZ", tombstone)})

    assert dropped == (["tombstoned ?mapped@@YAXXZ"] if removed else [])
    assert ledger.read_bytes() == before + (b"" if removed else row) + after
    if not removed:
        assert ledger.stat().st_mtime_ns == original_mtime


@pytest.mark.parametrize("row", [
    b"?bad@@YAXXZ,0x00000100,,8,a.cpp,matched,evidence\r\n",
    b"?bad@@YAXXZ,0x00000100,not-an-rva,8,a.cpp,matched,evidence\r\n",
    b"?bad@@YAXXZ,0x00000100,0x00000100,8,a.cpp,matched\r\n",
    b"?bad@@YAXXZ,0x00000100,0x00000100,8,a.cpp,matched,evidence,extra\r\n",
])
def test_merge_repair_leaves_invalid_target_records_for_validation(tmp_path, row):
    ledger = tmp_path / "functions.csv"
    original = b"name,export_rva,target_rva,target_size,source,status,notes\r\n" + row
    ledger.write_bytes(original)
    original_mtime = ledger.stat().st_mtime_ns

    assert dedup_csv.merge_repair(ledger, {("?bad@@YAXXZ", 0x100)}) == []

    assert ledger.read_bytes() == original
    assert ledger.stat().st_mtime_ns == original_mtime
