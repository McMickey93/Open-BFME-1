"""duplicate_global --staged/--range: refuse only an ADDED invented global at a named VA."""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import duplicate_global as D  # noqa: E402

DIR32_PATH = "targets/game/reverse/dir32_addresses.csv"
NAMED = "name,va\n?TheThing@@3PAVThing@@A,0x0130BF40\n"


def git(root, *args):
    subprocess.run(["git", *args], cwd=root, check=True, capture_output=True)


def repo(tmp_path, monkeypatch, files):
    root = tmp_path / "repo"
    root.mkdir()
    git(root, "init", "-q")
    git(root, "config", "user.email", "t@example.com")
    git(root, "config", "user.name", "t")
    for path, text in files.items():
        (root / path).parent.mkdir(parents=True, exist_ok=True)
        (root / path).write_text(text)
        git(root, "add", path)
    git(root, "commit", "-q", "-m", "base")
    monkeypatch.setattr(D, "ROOT", root)
    monkeypatch.setattr(D, "DIR32", root / DIR32_PATH)
    return root


def stage(root, path, text):
    (root / path).parent.mkdir(parents=True, exist_ok=True)
    (root / path).write_text(text)
    git(root, "add", path)


def test_added_invented_global_at_a_named_va_is_refused(tmp_path, monkeypatch):
    root = repo(tmp_path, monkeypatch, {DIR32_PATH: NAMED, "game/A.cpp": "int x;\n"})
    stage(root, "game/A.cpp", "int x;\nThing *g_rva0130BF40Object = 0;\n")
    hits = D.added_hits("HEAD", ":")
    assert [(h[0], h[2], h[3]) for h in hits] == [("game/A.cpp", "g_rva0130BF40Object", 0x0130BF40)]
    assert D.gate("HEAD", ":") == 1


def test_existing_hit_is_debt_not_refused(tmp_path, monkeypatch):
    old = "Thing *g_rva0130BF40Object = 0;\n"
    root = repo(tmp_path, monkeypatch, {DIR32_PATH: NAMED, "game/A.cpp": old})
    stage(root, "game/A.cpp", "// moved\nint y;\n" + old)
    assert D.gate("HEAD", ":") == 0


def test_recording_the_invented_name_in_the_same_change_does_not_admit_it(tmp_path, monkeypatch):
    root = repo(tmp_path, monkeypatch, {DIR32_PATH: NAMED, "game/A.cpp": "int x;\n"})
    stage(root, DIR32_PATH, NAMED + "?g_rva0130BF40Object@@3PAVThing@@A,0x0130BF40\n")
    stage(root, "game/A.cpp", "Thing *g_rva0130BF40Object = 0;\n")
    assert D.gate("HEAD", ":") == 1


def test_recorded_name_extern_static_and_unnamed_va_pass(tmp_path, monkeypatch):
    root = repo(tmp_path, monkeypatch, {DIR32_PATH: NAMED, "game/A.cpp": "int x;\n"})
    stage(root, "game/A.cpp", "extern Thing *g_rva0130BF40Object;\n"
                              "static Thing *s_rva0130BF40Copy;\n"
                              "int g_rva0120AAAAOther;\n")
    stage(root, "game/gen_small/B.cpp", "Thing *g_rva0130BF40Object = 0;\n")
    assert D.added_hits("HEAD", ":") == []


def test_range_judges_commits(tmp_path, monkeypatch):
    root = repo(tmp_path, monkeypatch, {DIR32_PATH: NAMED, "game/A.cpp": "int x;\n"})
    base = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, capture_output=True,
                          text=True, check=True).stdout.strip()
    stage(root, "game/New.c", "struct Thing *g_rva0130BF40Object;\n")
    git(root, "commit", "-q", "-m", "invent")
    assert D.gate(base, "HEAD") == 1
    assert D.gate("HEAD", "HEAD") == 0
