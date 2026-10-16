"""abi-scaffold=yes;semantic-hierarchy=unresolved: the notes tag for rows whose
source invents a class hierarchy only to drive codegen (approved by the project
lead 2026-10-16). check_csv validates its shape; progress.py reports those
bytes apart without changing what counts as matched."""
import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import check_csv  # noqa: E402

spec = importlib.util.spec_from_file_location("progress", ROOT / "tools" / "progress.py")
progress = importlib.util.module_from_spec(spec)
spec.loader.exec_module(progress)

TAG = "abi-scaffold=yes;semantic-hierarchy=unresolved"
SRC = "game/GameEngine/Source/GameLogic/Object/Update/AutoFindHealingUpdateConstructor.cpp"


def test_notes_keys_reads_key_value_fields():
    assert check_csv.notes_keys(f"clean C++ (x);{TAG};model=m") == {
        "abi-scaffold": "yes", "semantic-hierarchy": "unresolved", "model": "m"}


def test_untagged_rows_and_the_full_tag_pass():
    assert check_csv.scaffold_problems("plain notes", SRC, "matched") == []
    assert check_csv.scaffold_problems(f"x;{TAG};model=m", SRC, "matched") == []


@pytest.mark.parametrize("notes,source,status,why", [
    ("abi-scaffold=yes", SRC, "matched", "go together"),
    ("semantic-hierarchy=unresolved", SRC, "matched", "go together"),
    ("abi-scaffold=maybe;semantic-hierarchy=unresolved", SRC, "matched", "is not one of"),
    ("abi-scaffold=yes;semantic-hierarchy=resolved", SRC, "matched", "is not one of"),
    (TAG, SRC, "partial", "matched, hand-written row"),
    (TAG, "game/gen_small/x.cpp", "matched", "matched, hand-written row"),
])
def test_malformed_tags_are_refused(notes, source, status, why):
    assert any(why in p for p in check_csv.scaffold_problems(notes, source, status))


def test_check_functions_reports_a_bad_tag():
    raw = ("name,export_rva,target_rva,target_size,source,status,notes\n"
           f"?f@@YAXXZ,,0x00401000,4,{SRC},matched,abi-scaffold=yes\n")
    problems = []
    check_csv.check_functions(raw.encode(), problems, sources_ok={SRC})
    assert any("go together" in p for p in problems)


def test_scaffold_split_counts_only_tagged_rows(monkeypatch):
    image = bytes(0x100)
    monkeypatch.setattr(progress, "_text_image", lambda: (0x1000, image))
    matched = {("?a@@YAXXZ", "0x1000"): (0x10, SRC), ("?b@@YAXXZ", "0x1020"): (0x20, SRC)}
    notes = {("?a@@YAXXZ", "0x1000"): f"x;{TAG}", ("?b@@YAXXZ", "0x1020"): "x"}
    whole = progress.real_split(matched, notes, 0x1000, 0x100)
    part = progress.scaffold_split(matched, notes, 0x1000, 0x100)
    assert whole["authored"] == 0x30 and part["authored"] == 0x10
    # the tag never moves a row out of the authored lane
    assert progress.source_lane(SRC, f"x;{TAG}", False) == "authored"


def test_headline_prints_the_scaffold_line(capsys):
    split = {lane: 0 for lane in progress.SOURCE_LANES}
    split["authored"] = 100
    progress.print_headline(0, 1000, split, split, None, None,
                            {**split, "authored": 0}, {**split, "authored": 77})
    out = capsys.readouterr().out
    assert "77 bytes of that are ABI scaffolds" in out and "delta +77 bytes" in out


def test_real_ledger_tags_validate():
    raw = (ROOT / "targets/game/reverse/functions.csv").read_bytes()
    sources = {line.split(b",")[4].decode() for line in raw.splitlines()[1:] if line.count(b",") >= 6}
    problems = []
    check_csv.check_functions(raw, problems, sources_ok=sources)
    assert not [p for p in problems if "abi-scaffold" in p or "semantic-hierarchy" in p]
