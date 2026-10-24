"""The publish window is off (2026-10-11, as Open-BFME-2 did in e037b8cacb): pre-push
asks no window before a push to master and gates it like any other push, and a
leftover window ref (refs/landing/*) still passes ungated, as a claim ref does."""
import subprocess
import sys
from pathlib import Path

import pytest

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
import bash_path  # noqa: E402

ZERO = "0" * 40
# every checker the hook's ordinary path runs, passing
PASS = ("check_csv", "one_identity", "target_hooks", "conversion_gate", "name_regression",
        "name_history", "name_oracle", "retired_guard", "doc_budget", "ea_name_guard",
        "pin_consistency", "b_pin_check", "delta_sources", "header_dependents", "ledger_guard",
        "check_case_collisions", "empty_commits", "duplicate_global")


def git(cwd, *args, stdin=None):
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True,
                          input=stdin).stdout.strip()


@pytest.fixture
def repo(tmp_path):
    """One claimed source; build.sh records what it verifies and fails while the
    ignored, #included game/generated.h says bad."""
    repo = tmp_path / "repo"
    git(tmp_path, "init", "-q", str(repo))
    for key, value in (("user.name", "t"), ("user.email", "t@example.com"), ("core.hooksPath", "no-hooks")):
        git(repo, "config", key, value)
    for sub_dir in ("tools", "game", "targets/game/reverse"):
        (repo / sub_dir).mkdir(parents=True)
    (repo / "targets/game/reverse/functions.csv").write_text("name,source,status\nf,game/a.cpp,matched\n")
    for name in PASS:
        (repo / f"tools/{name}.py").write_text("import sys\nsys.exit(0)\n")
    (repo / "tools/layout_migration.py").write_text("import sys\nsys.exit(1)\n")
    (repo / "tools/verification_cache.py").write_text(
        "import sys\nargs = sys.argv\n"
        "if 'prepare' in args:\n    print(open(args[args.index('--selectors-file') + 1]).read(), end='')\n")
    (repo / "build.sh").write_text("#!/usr/bin/env bash\nprintf '%s\\n' \"$@\" >> built\n"
                                   "grep -q bad game/generated.h && exit 1\nexit 0\n", newline="\n")
    (repo / ".gitignore").write_text("game/generated.h\nbuilt\n")
    (repo / "game/generated.h").write_text("good\n")
    (repo / "game/a.cpp").write_text('#include "generated.h"\nint a;\n')
    git(repo, "add", ".")
    git(repo, "update-index", "--chmod=+x", "build.sh")
    (repo / "build.sh").chmod(0o755)  # the hook executes this worktree file directly
    git(repo, "commit", "-q", "-m", "base")
    return repo


def hook(repo, refs, env=None):
    try:
        bash = bash_path.bash()
    except RuntimeError:
        pytest.skip("Bash is required to exercise hooks")
    return subprocess.run([bash, str(TOOLS.parent / ".githooks" / "pre-push"), "origin", "unused"],
                          cwd=repo, input=refs, capture_output=True, text=True,
                          env={**bash_path.env(), **(env or {})})


def change(repo):
    base = git(repo, "rev-parse", "HEAD")
    (repo / "game/a.cpp").write_text('#include "generated.h"\nint a = 1;\n')
    git(repo, "commit", "-q", "-am", "change")
    return base, git(repo, "rev-parse", "HEAD")


def built(repo):
    return (repo / "built").read_text().split() if (repo / "built").exists() else []


def test_a_push_to_master_asks_no_window(repo):
    # what `publish_window.py check` answered while someone else held the window
    (repo / "tools/publish_window.py").write_text("import sys\nsys.exit(1)\n")
    git(repo, "add", "tools/publish_window.py")
    git(repo, "commit", "-q", "-m", "a window checker that refuses")
    base, tip = change(repo)
    result = hook(repo, f"refs/heads/master {tip} refs/heads/master {base}\n")
    assert result.returncode == 0, result.stderr
    assert "publish window" not in result.stderr
    assert built(repo) == ["game/a.cpp"]                          # gated as before


def test_a_leftover_window_ref_passes_ungated(repo):
    for name in ("ledger_guard", "check_case_collisions", "check_csv"):
        (repo / f"tools/{name}.py").write_text("import sys\nsys.exit(1)\n")   # every gate refuses
    empty = git(repo, "mktree", stdin="")
    marker = git(repo, "commit-tree", empty, "-m", '{"owner": "old tooling"}')   # as a window commit
    for remote_sha in (ZERO, marker):                             # open, then renew or close
        result = hook(repo, f"refs/heads/window {marker} refs/landing/window {remote_sha}\n")
        assert result.returncode == 0, result.stderr
    assert built(repo) == []
    gated = hook(repo, f"refs/heads/window {marker} refs/heads/master {ZERO}\n")
    assert gated.returncode != 0                                  # control: the stubs do refuse


def test_an_ignored_included_input_that_changes_is_caught_by_the_next_push(repo):
    # Review cycle 6/7: the reverted ordinary-path reuse (6089f82afc) let a push
    # skip byte verification after an ignored, #included file changed. Kept as
    # a permanent guard (from test_publish_window.py, retired with gate_evidence.py):
    # even with BFME_REUSE_GATE_EVIDENCE=1 set, pre-push byte-verifies every push.
    base, tip = change(repo)
    refs = f"refs/heads/topic {tip} refs/heads/topic {base}\n"
    assert hook(repo, refs, {"BFME_REUSE_GATE_EVIDENCE": "1"}).returncode == 0
    (repo / "game/generated.h").write_text("bad\n")              # ignored, included, changed
    again = hook(repo, refs, {"BFME_REUSE_GATE_EVIDENCE": "1"})
    assert again.returncode != 0 and "reused" not in again.stdout


def test_the_same_tip_onto_an_older_base_gates_the_wider_set(tmp_path):
    # From test_publish_window.py (test_a_narrow_scoped_record_never_skips_a_wider_gate, review
    # 2026-09-30, review_five_probes.py), which is retired with gate_evidence.py: the same tip
    # pushed onto an older base changes two headers instead of one, and a record of the narrow
    # gate once let the wider one (which fails on b.cpp) be skipped. No record exists any more;
    # what stays is that pre-push selects the dependents against the base of THIS push.
    repo = tmp_path / "repo"
    git(tmp_path, "init", "-q", str(repo))
    for key, value in (("user.name", "t"), ("user.email", "t@example.com"), ("core.hooksPath", "no-hooks")):
        git(repo, "config", key, value)
    for sub_dir in ("tools", "game", "targets/game/reverse"):
        (repo / sub_dir).mkdir(parents=True)
    (repo / "targets/game/reverse/functions.csv").write_text("name,source,status\n")
    for name in PASS + ("protected_paths",):
        (repo / f"tools/{name}.py").write_text("import sys\nsys.exit(0)\n")
    (repo / "tools/layout_migration.py").write_text("import sys\nsys.exit(1)\n")
    (repo / "tools/header_dependents.py").write_text(
        "import subprocess,sys\n"
        "paths=subprocess.check_output(['git','diff','--name-only',sys.argv[2],sys.argv[3],'--','game'])"
        ".decode().splitlines()\n"
        "for p in paths:\n if p.endswith('.h'): print(p[:-2]+'.cpp')\n")
    (repo / "build.sh").write_text('#!/usr/bin/env bash\nprintf "%s\\n" "$@" >> gate_calls.txt\n'
                                   'case "$*" in *b.cpp*) exit 1;; esac\n', newline="\n")
    (repo / "game/a.h").write_text("old\n")
    (repo / "game/b.h").write_text("old\n")
    git(repo, "add", "--", "tools", "build.sh", "game", "targets")
    git(repo, "update-index", "--chmod=+x", "build.sh")
    (repo / "build.sh").chmod(0o755)  # index mode does not change the worktree mode
    git(repo, "commit", "-q", "-m", "initial")
    older = git(repo, "rev-parse", "HEAD")
    (repo / "game/b.h").write_text("bad b\n")
    git(repo, "commit", "-q", "-am", "header b")
    newer = git(repo, "rev-parse", "HEAD")
    (repo / "game/a.h").write_text("new a\n")
    git(repo, "commit", "-q", "-am", "header a")
    tip = git(repo, "rev-parse", "HEAD")

    def gate_calls():
        path = repo / "gate_calls.txt"
        calls = path.read_text().split() if path.exists() else []
        path.unlink(missing_ok=True)
        return calls

    def push(base, reuse=True):
        return hook(repo, f"refs/heads/topic {tip} refs/heads/topic {base}\n",
                    {"BFME_REUSE_GATE_EVIDENCE": "1" if reuse else "0"})
    assert push(newer).returncode == 0                  # narrow: only a.cpp, green
    assert gate_calls() == ["game/a.cpp"]
    assert push(older).returncode != 0                  # wider: b.cpp is red and is not skipped
    assert "game/b.cpp" in gate_calls()
    assert push(older, reuse=False).returncode != 0
    gate_calls()
    again = push(newer)                                  # and the narrow push gates again
    assert again.returncode == 0 and "REUSING" not in again.stderr
    assert gate_calls() == ["game/a.cpp"]
