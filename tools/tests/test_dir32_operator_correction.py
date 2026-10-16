"""The dir32 record's operator-correction route (approved by the project lead
2026-10-16): a misrecorded primary vtable moves to the address retail proves,
in a commit that changes nothing else in the record and carries its proof.

The motivating case: ??_7BattlePlanUpdateModuleData@@6B@ is recorded at
0x010A5C78, which is ReplenishUnitsBehaviorModuleData's table; its ctor
0x00285F10 stores 0x010BBFC0, whose slots reach the matched ??_G 0x00285FE0.
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
EVIDENCE = "targets/game/reverse/identity_evidence/010bbfc0-battleplan-moduledata-vtable.md"
PROOF = (f"# {NAME}\n\nRecorded 0x{OLD_VA:08X} is ReplenishUnitsBehaviorModuleData's table. "
         f"Retail's ctor=0x{CTOR:08X} stores 0x{NEW_VA:08X}; its slots reach the matched "
         f"deleting destructor dtor=0x{DTOR:08X}.\n")
TREE = "HEAD:"


@pytest.fixture(scope="module")
def record():
    return G.read_at(f"HEAD:{G.REL}")


@pytest.fixture
def evidence(monkeypatch):
    """Serve the evidence file from the judged tree without a commit."""
    texts = {EVIDENCE: PROOF}
    real = G.git_show_text

    def show(spec):
        for path, text in texts.items():
            if spec.endswith(":" + path):
                return text
        return real(spec)
    monkeypatch.setattr(G, "git_show_text", show)
    return texts


def corrected(record, va=NEW_VA, name=NAME):
    new = dict(record)
    new[name] = va
    return new


def claim(name=NAME, old=OLD_VA, new=NEW_VA, evidence=EVIDENCE):
    return G.parse_corrections(
        f"x\n\nDir32-Operator-Correction: {name} 0x{old:08X} -> 0x{new:08X} evidence={evidence}\n")


def judge(record, new, claims, changed=frozenset({EVIDENCE, G.REL})):
    return G.correction_problems(record, new, claims, TREE, set(changed))


def test_the_battleplan_case_is_accepted(record, evidence):
    assert record[NAME] == OLD_VA
    assert judge(record, corrected(record), claim()) == []


def test_a_wrong_new_va_is_refused(record, evidence):
    wrong = NEW_VA + 4
    found = judge(record, corrected(record, wrong), claim(new=wrong))
    assert any("is not proven" in p for p in found)


def test_an_unproven_new_va_is_refused(record, evidence):
    """A real table start, but another class's (BattlePlanUpdateModuleDataBase)."""
    other = record["??_7BattlePlanUpdateModuleDataBase@@6B@"]
    found = judge(record, corrected(record, other), claim(new=other))
    assert any("is not proven" in p for p in found)
    assert any("also recorded for" in p for p in found)


def test_extra_record_changes_are_refused(record, evidence):
    new = corrected(record)
    new["??_7ReplenishUnitsBehaviorModuleData@@6B@"] = 0x010BBFC4
    assert any("moved names" in p for p in judge(record, new, claim()))
    new = corrected(record)
    new["?fake@@3HA"] = 0x01000000
    assert any("add or delete" in p for p in judge(record, new, claim()))
    new = corrected(record)
    del new["??_7ReplenishUnitsBehaviorModuleData@@6B@"]
    assert any("add or delete" in p for p in judge(record, new, claim()))


def test_missing_or_uncommitted_evidence_is_refused(record, evidence):
    found = judge(record, corrected(record), claim(), changed={G.REL})
    assert any("not added or changed in this commit" in p for p in found)
    found = judge(record, corrected(record), claim(evidence="targets/x/missing.md"),
                  changed={G.REL, "targets/x/missing.md"})
    assert any("not in the committed tree" in p for p in found)


def test_evidence_must_cite_and_prove(record, evidence):
    evidence[EVIDENCE] = PROOF.replace(f"0x{OLD_VA:08X}", "the old address")
    assert any("old VA" in p for p in judge(record, corrected(record), claim()))
    evidence[EVIDENCE] = PROOF.replace(f"ctor=0x{CTOR:08X}", "ctor=0x00285FE0")
    assert any("never stores" in p for p in judge(record, corrected(record), claim()))
    evidence[EVIDENCE] = PROOF.replace(f"dtor=0x{DTOR:08X}", "dtor=0x00286010")
    assert any("not a matched, non-generated ??_G" in p
               for p in judge(record, corrected(record), claim()))
    evidence[EVIDENCE] = PROOF.replace(f"dtor=0x{DTOR:08X}", "no dtor cited")
    assert any("no dtor=" in p for p in judge(record, corrected(record), claim()))


def test_a_trailer_that_does_not_match_the_change_is_refused(record, evidence):
    new = corrected(record)
    assert any("moved names" in p for p in judge(record, new, claim(name="??_7Other@@6B@")))
    assert any("the trailer says" in p for p in judge(record, new, claim(old=OLD_VA + 8)))
    assert any("the trailer says" in p for p in judge(record, new, claim(new=NEW_VA + 8)))
    assert "one correction per commit" in judge(record, new, claim() + claim())[0]
    assert "one correction per commit" in judge(record, new, [])[0]


def test_a_secondary_table_has_no_correction_route(record, evidence):
    name = "??_7BattlePlanUpdate@@6BObjectModule@@@"
    new = corrected(record, record[name] + 4, name)
    found = judge(record, new, claim(name=name, old=record[name], new=record[name] + 4))
    assert any("not a primary vtable" in p for p in found)


def test_without_a_claim_a_move_is_still_refused_and_a_stale_claim_is_ignored(record):
    found = G.problems(record, corrected(record))
    assert any("rewritten to" in p for p in found)
    assert G.problems(record, dict(record), corrections=claim()) == []


def _git(repo, *args):
    return subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True).stdout


def test_pre_push_judges_every_commit(tmp_path, monkeypatch):
    repo = tmp_path / "r"
    (repo / Path(G.REL).parent).mkdir(parents=True)
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "t@example.invalid")
    _git(repo, "config", "user.name", "t")
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
    repo = tmp_path / "c"
    (repo / Path(G.REL).parent).mkdir(parents=True)
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "t@example.invalid")
    _git(repo, "config", "user.name", "t")
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
