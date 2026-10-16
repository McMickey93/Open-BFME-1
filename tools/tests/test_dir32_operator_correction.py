"""The dir32 record's operator-correction route (approved by the project lead
2026-10-16): a misrecorded primary vtable moves to the address retail proves,
in a commit an owner-approved list names, that changes nothing else in the
record or the ledgers, with every proof read from its PARENT tree.

The motivating case: ??_7BattlePlanUpdateModuleData@@6B@ is recorded at
0x010A5C78, which is ReplenishUnitsBehaviorModuleData's table; its ctor
0x00285F10 stores 0x010BBFC0, whose slot 0 is the matched ??_G 0x00285FE0.
The row ??0BattlePlanUpdateModuleData at 0x00204ED0 (Replenish's ctor, also
claimed under its real name) holds 0x010A5C78, so its identity is fixed in an
earlier commit; these tests simulate that parent by dropping the row.
"""
import subprocess
import sys
from pathlib import Path

import pytest

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
import dir32_record_guard as G  # noqa: E402

NAME = "??_7BattlePlanUpdateModuleData@@6B@"
OLD_VA, NEW_VA = 0x010A5C78, 0x010BBFC0
CTOR, DTOR = 0x00285F10, 0x00285FE0
MISNAMED = ("??0BattlePlanUpdateModuleData@@QAE@XZ", 0x00204ED0)
EVIDENCE = "targets/game/reverse/identity_evidence/010bbfc0-battleplan-moduledata-vtable.md"
PROOF = (f"# {NAME}\n\nRecorded 0x{OLD_VA:08X} is ReplenishUnitsBehaviorModuleData's table. "
         f"Retail's ctor=0x{CTOR:08X} stores 0x{NEW_VA:08X}; slot 0 is the matched "
         f"deleting destructor dtor=0x{DTOR:08X}.\n")
APPROVED_LINE = f"{NAME} 0x{OLD_VA:08X} -> 0x{NEW_VA:08X}  # approved by the project lead 2026-10-16\n"
# The tree the correction was judged against: the guard commit, before the
# identity fix (8f9a613c23) and the correction itself (d8769e2c75) landed.
# Judging HEAD would test a record that is already corrected.
PRE = "9334a049ab6c8fee39168c14793c467262f9445c"
PARENT = f"{PRE}:"


@pytest.fixture(scope="module")
def record():
    if subprocess.run(["git", "cat-file", "-e", f"{PRE}^{{commit}}"], cwd=TOOLS.parent,
                      capture_output=True).returncode:
        pytest.skip(f"{PRE[:10]} is not in this clone")
    return G.read_at(f"{PARENT}{G.REL}")


@pytest.fixture
def tree(monkeypatch):
    """Serve the evidence and the approved list from the judged trees, and
    drop the misnamed 0x00204ED0 row (the identity fix an earlier commit makes)."""
    texts = {EVIDENCE: PROOF, G.APPROVED: APPROVED_LINE}
    real_show, real_rows = G.git_show_text, G.function_rows

    def show(spec):
        for path, text in texts.items():
            if spec.endswith(":" + path):
                return text
        return real_show(spec)

    def rows(tree=":"):
        return [r for r in real_rows(tree) if (r[0], r[1]) != MISNAMED or texts.get("keep-misnamed")]
    monkeypatch.setattr(G, "git_show_text", show)
    monkeypatch.setattr(G, "function_rows", rows)
    return texts


def corrected(record, va=NEW_VA, name=NAME):
    new = dict(record)
    new[name] = va
    return new


def claim(name=NAME, old=OLD_VA, new=NEW_VA, evidence=EVIDENCE):
    return G.parse_corrections(
        f"x\n\nDir32-Operator-Correction: {name} 0x{old:08X} -> 0x{new:08X} evidence={evidence}\n")


def judge(record, new, claims, changed=frozenset({EVIDENCE, G.REL}), added=frozenset({EVIDENCE})):
    return G.correction_problems(record, new, claims, PARENT, PARENT, set(changed), set(added))


def test_the_battleplan_case_is_accepted(record, tree):
    assert record[NAME] == OLD_VA
    assert judge(record, corrected(record), claim()) == []


def test_r1_1_a_matched_tu_still_holding_the_old_va_blocks(record, tree):
    tree["keep-misnamed"] = "1"
    found = judge(record, corrected(record), claim())
    assert any("0x00204ED0" in p and "holds 0x010A5C78" in p for p in found)


def test_r1_2_a_correction_commit_may_not_touch_the_ledgers(record, tree):
    for ledger in (G.FUNCTIONS, G.DATA_ROWS):
        found = judge(record, corrected(record), claim(), changed={EVIDENCE, G.REL, ledger})
        assert any("may not change" in p for p in found)


def test_r1_3_the_ctor_must_decode_a_store_of_the_new_table(record, tree):
    tree[EVIDENCE] = PROOF.replace(f"ctor=0x{CTOR:08X}", f"ctor=0x{DTOR:08X}")
    assert any("no decoded `mov [mem]" in p for p in judge(record, corrected(record), claim()))
    tree[EVIDENCE] = PROOF.replace(f"ctor=0x{CTOR:08X}", "ctor=0x00204ED0")   # Replenish's
    assert any("0x00204ED0" in p for p in judge(record, corrected(record), claim()))


def test_r1_3_a_c7_byte_inside_another_instruction_is_no_store():
    # mov ecx, 0x00C70000 ; push 0x010BBFC0 -- a C7 three bytes before the immediate
    fake = bytes.fromhex("B90000C700") + bytes.fromhex("68") + NEW_VA.to_bytes(4, "little")
    assert not G.stores_table(fake, 0x00401000, NEW_VA)
    real = bytes.fromhex("C706") + NEW_VA.to_bytes(4, "little")      # mov dword ptr [esi], imm32
    assert G.stores_table(real, 0x00401000, NEW_VA)
    disp = bytes.fromhex("C74604") + NEW_VA.to_bytes(4, "little")    # mov dword ptr [esi+4], imm32
    assert G.stores_table(disp, 0x00401000, NEW_VA)


def test_r1_4_only_an_approved_line_is_a_correction(record, tree):
    tree[G.APPROVED] = "# empty\n"
    assert any("owner-approved" in p for p in judge(record, corrected(record), claim()))


def test_r1_4_a_wrong_or_unproven_new_va_is_refused(record, tree):
    for va in (NEW_VA + 4, record["??_7BattlePlanUpdateModuleDataBase@@6B@"]):
        tree[G.APPROVED] = f"{NAME} 0x{OLD_VA:08X} -> 0x{va:08X}\n"
        found = judge(record, corrected(record, va), claim(new=va))
        assert any("is not proven" in p for p in found), va
        assert any("slot 0" in p for p in found), va


def test_r1_7_undo_needs_a_guard_change(record, tree):
    """Reverting to the misrecorded address: even if approved, the old VA now
    passes the rule and the new one does not."""
    moved = corrected(record)
    tree[G.APPROVED] = f"{NAME} 0x{NEW_VA:08X} -> 0x{OLD_VA:08X}\n"
    found = judge(moved, dict(record), claim(old=NEW_VA, new=OLD_VA))
    assert any("still passes the primary-vtable rule" in p for p in found)
    assert any("is not proven" in p for p in found)


def test_extra_record_changes_are_refused(record, tree):
    new = corrected(record)
    new["??_7ReplenishUnitsBehaviorModuleData@@6B@"] = 0x010BBFC4
    assert any("moved names" in p for p in judge(record, new, claim()))
    new = corrected(record)
    new["?fake@@3HA"] = 0x01000000
    assert any("add or delete" in p for p in judge(record, new, claim()))


def test_r1_5_evidence_must_be_newly_added_under_identity_evidence(record, tree):
    found = judge(record, corrected(record), claim(), added=set())
    assert any("must be a file this commit ADDS" in p for p in found)
    elsewhere = "docs/proof.md"
    tree[elsewhere] = PROOF
    found = judge(record, corrected(record), claim(evidence=elsewhere),
                  changed={G.REL, elsewhere}, added={elsewhere})
    assert any("must be a file this commit ADDS" in p for p in found)


def test_evidence_must_cite_both_vas_and_a_proving_dtor(record, tree):
    tree[EVIDENCE] = PROOF.replace(f"0x{OLD_VA:08X}", "the old address")
    assert any("old VA" in p for p in judge(record, corrected(record), claim()))
    tree[EVIDENCE] = PROOF.replace(f"dtor=0x{DTOR:08X}", "dtor=0x00286010")
    assert any("not a matched, non-generated ??_G" in p for p in judge(record, corrected(record), claim()))
    tree[EVIDENCE] = PROOF.replace(f"dtor=0x{DTOR:08X}", "no dtor cited")
    assert any("no dtor=" in p for p in judge(record, corrected(record), claim()))


def test_a_trailer_that_does_not_match_the_change_is_refused(record, tree):
    new = corrected(record)
    assert any("moved names" in p for p in judge(record, new, claim(name="??_7Other@@6B@")))
    assert any("the trailer says" in p for p in judge(record, new, claim(old=OLD_VA + 8)))
    assert "one correction per commit" in judge(record, new, claim() + claim())[0]
    assert "one correction per commit" in judge(record, new, [])[0]


def test_a_secondary_table_has_no_correction_route(record, tree):
    name = "??_7BattlePlanUpdate@@6BObjectModule@@@"
    new = corrected(record, record[name] + 4, name)
    found = judge(record, new, claim(name=name, old=record[name], new=record[name] + 4))
    assert any("not a primary vtable" in p for p in found)


def test_without_a_claim_a_move_is_still_refused_and_a_stale_claim_is_ignored(record):
    assert any("rewritten to" in p for p in G.problems(record, corrected(record)))
    assert G.problems(record, dict(record), corrections=claim()) == []


def _git(repo, *args):
    return subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True).stdout


def _repo(tmp_path, name):
    repo = tmp_path / name
    (repo / Path(G.REL).parent).mkdir(parents=True)
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "t@example.invalid")
    _git(repo, "config", "user.name", "t")
    return repo


def test_pre_push_judges_every_commit(tmp_path, monkeypatch):
    monkeypatch.setattr(G, "_IMAGE", {})
    repo = _repo(tmp_path, "r")
    path = repo / G.REL
    path.write_text(f"name,va\n{NAME},0x{OLD_VA:08X}\n")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "base")
    base = _git(repo, "rev-parse", "HEAD").strip()
    path.write_text(f"name,va\n{NAME},0x{NEW_VA:08X}\n")
    _git(repo, "commit", "-qam", "silent move")
    (repo / "README").write_text("x")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "innocent tip")
    monkeypatch.chdir(repo)
    assert G.check_range(base, "HEAD") == 1, "a move below the tip without a trailer"
    _git(repo, "reset", "-q", "--hard", base)
    (repo / "README").write_text("y")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "no move")
    assert G.check_range(base, "HEAD") == 0


def test_commit_msg_refuses_a_move_without_a_trailer_and_a_trailer_without_a_move(
        tmp_path, monkeypatch):
    monkeypatch.setattr(G, "_IMAGE", {})     # a temp repo has no image: keep its empty cache local
    repo = _repo(tmp_path, "c")
    path = repo / G.REL
    path.write_text(f"name,va\n{NAME},0x{OLD_VA:08X}\n")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "base")
    monkeypatch.chdir(repo)
    message = tmp_path / "msg"
    message.write_text("x\n\nDir32-Operator-Correction: "
                       f"{NAME} 0x{OLD_VA:08X} -> 0x{NEW_VA:08X} evidence={EVIDENCE}\n")
    assert G.check_commit_msg(str(message)) == 1, "a trailer with no move"
    path.write_text(f"name,va\n{NAME},0x{NEW_VA:08X}\n")
    _git(repo, "add", "-A")
    message.write_text("x\n")
    assert G.check_commit_msg(str(message)) == 1, "a move with no trailer"


def test_r1_1_pre_push_rebuilds_every_tu_holding_a_moved_va(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(G, "_IMAGE", {})     # never a cache another test filled elsewhere
    G.read_retail(G.IMAGE_BASE, 0)          # the image, before leaving the real checkout
    repo = _repo(tmp_path, "s")
    (repo / G.FUNCTIONS).write_text(
        "name,export_rva,target_rva,target_size,source,status,notes\n"
        "??0ReplenishUnitsBehaviorModuleData@@QAE@XZ,,0x00204ED0,69,game/R.cpp,matched,\n"
        "??0BattlePlanUpdateModuleData@@QAE@XZ,,0x00285F10,164,game/B.cpp,matched,\n"
        "?unrelated@@YAXXZ,,0x00286010,239,game/U.cpp,matched,\n")
    path = repo / G.REL
    path.write_text(f"name,va\n{NAME},0x{OLD_VA:08X}\n")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "base")
    base = _git(repo, "rev-parse", "HEAD").strip()
    path.write_text(f"name,va\n{NAME},0x{NEW_VA:08X}\n")
    _git(repo, "commit", "-qam", "move")
    monkeypatch.chdir(repo)
    assert G.moved_sources(base, "HEAD") == 0
    assert capsys.readouterr().out.split() == ["source:game/B.cpp", "source:game/R.cpp"]
