"""header_dependents: a header change reaches exactly the sources that can include it, and
every doubt widens the set or falls back to the full gate."""
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
import bash_path  # noqa: E402
import header_dependents as H  # noqa: E402


def git(root, *args):
    subprocess.run(["git", *args], cwd=root, check=True, capture_output=True)


@pytest.fixture
def repo(tmp_path, monkeypatch):
    git(tmp_path, "init", "-q")
    git(tmp_path, "config", "user.name", "Fixture")
    git(tmp_path, "config", "user.email", "fixture@example.invalid")
    monkeypatch.setattr(H, "ROOT", tmp_path)
    return tmp_path


def put(root, path, text):
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text)
    git(root, "add", "--", path)


def ledger(root, *sources):
    put(root, "targets/game/reverse/functions.csv",
        "name,export_rva,target_rva,target_size,source,status,notes\n"
        + "".join(f"?f{i}@@YAXXZ,,0x{0x1000 + i:08X},4,{s},matched,x\n" for i, s in enumerate(sources)))


def run(root, capsys, *args):
    code = H.main(list(args))
    out = capsys.readouterr()
    return code, [line for line in out.out.splitlines() if line]


def base(repo):
    put(repo, "game/Inc/Low.h", "int low;\n")
    put(repo, "game/Inc/Mid.h", '#include "../Inc/LOW.H"\n')
    put(repo, "game/A.cpp", '#include "Inc/Mid.h"\nvoid a() {}\n')
    put(repo, "game/B.cpp", "void b() {}\n")
    put(repo, "game/C.cpp", "// cl: /FIForced.h\nvoid c() {}\n")
    put(repo, "game/Forced.h", "int forced;\n")
    ledger(repo, "game/A.cpp", "game/B.cpp", "game/C.cpp")
    git(repo, "commit", "-qm", "base")


def test_transitive_case_insensitive_include(repo, capsys):
    base(repo)
    put(repo, "game/Inc/Low.h", "int low2;\n")
    assert run(repo, capsys, "--staged") == (0, ["game/A.cpp"])


def test_forced_include_counts(repo, capsys):
    base(repo)
    put(repo, "game/Forced.h", "int forced2;\n")
    assert run(repo, capsys, "--staged") == (0, ["game/C.cpp"])


def test_deleted_header_still_finds_its_includers(repo, capsys):
    base(repo)
    git(repo, "rm", "-q", "game/Inc/Low.h")
    assert run(repo, capsys, "--staged") == (0, ["game/A.cpp"])


def test_new_unincluded_header_reaches_nothing(repo, capsys):
    base(repo)
    put(repo, "game/Inc/Unused.h", "int unused;\n")
    assert run(repo, capsys, "--staged") == (0, [])


def test_macro_include_counts_as_including_everything(repo, capsys):
    base(repo)
    put(repo, "game/D.cpp", "#define H \"x.h\"\n#include H\nvoid d() {}\n")
    ledger(repo, "game/A.cpp", "game/B.cpp", "game/C.cpp", "game/D.cpp")
    git(repo, "commit", "-qm", "macro")
    put(repo, "game/Inc/Low.h", "int low3;\n")
    assert run(repo, capsys, "--staged") == (0, ["game/A.cpp", "game/D.cpp"])


def test_toolchain_or_vendor_change_needs_the_full_gate(repo, capsys):
    base(repo)
    put(repo, "inputs/vendor/stlport/stl/_vector.h", "x\n")
    assert run(repo, capsys, "--staged")[0] == 2


def test_limit_falls_back_to_the_full_gate(repo, capsys):
    base(repo)
    put(repo, "game/Inc/Low.h", "int low4;\n")
    assert run(repo, capsys, "--staged", "--limit", "0")[0] == 2


def test_mod_headers_are_not_game_dependencies(repo, capsys):
    base(repo)
    put(repo, "mods/features/x/feature.h", "int mod;\n")
    assert run(repo, capsys, "--staged") == (0, [])


def included_base(repo):
    put(repo, "game/Net/Inc.cpp", "void inc() {}\n")
    put(repo, "game/Net/Host.cpp", '#include "Inc.cpp"\nvoid host() {}\n')
    put(repo, "game/Lib/Outer.cpp", '#include "../Net/Host.cpp"\n')
    put(repo, "game/Lib/henc.tbl", "1, 2, 3,\n")
    put(repo, "game/Lib/Huff.inl", '#include "henc.tbl"\n')
    put(repo, "game/Lib/Huff.cpp", '#include "Huff.inl"\nvoid huff() {}\n')
    ledger(repo, "game/Net/Inc.cpp", "game/Net/Host.cpp", "game/Lib/Outer.cpp", "game/Lib/Huff.cpp")
    git(repo, "commit", "-qm", "base")


def test_an_included_source_reaches_its_includers_through_sources(repo, capsys):
    included_base(repo)
    put(repo, "game/Net/Inc.cpp", "void inc2() {}\n")
    assert run(repo, capsys, "--staged") == (0, ["game/Lib/Outer.cpp", "game/Net/Host.cpp"])


def test_an_included_table_reaches_through_a_header(repo, capsys):
    included_base(repo)
    put(repo, "game/Lib/henc.tbl", "4, 5, 6,\n")
    assert run(repo, capsys, "--staged") == (0, ["game/Lib/Huff.cpp"])


def test_a_renamed_included_source_still_reaches_the_old_includers(repo, capsys):
    included_base(repo)
    git(repo, "mv", "game/Net/Inc.cpp", "game/Net/Moved.cpp")
    assert run(repo, capsys, "--staged") == (0, ["game/Lib/Outer.cpp", "game/Net/Host.cpp"])


def test_a_source_nothing_includes_skips_the_graph(repo, capsys, monkeypatch):
    included_base(repo)
    monkeypatch.setattr(H, "graph", lambda: pytest.fail("graph built for an unincluded source"))
    put(repo, "game/Lib/Huff.cpp", '#include "Huff.inl"\nvoid huff2() {}\n')
    assert run(repo, capsys, "--staged") == (0, [])


def test_an_included_vendored_file_needs_the_full_gate(repo, capsys):
    included_base(repo)
    put(repo, "game/Alloc.cpp", "#include <stl/_alloc.c>\n")
    git(repo, "commit", "-qm", "alloc")
    put(repo, "inputs/vendor/stlport/stl/_alloc.c", "x\n")
    assert run(repo, capsys, "--staged")[0] == 2


STUBS = ("check_case_collisions", "conversion_gate", "name_regression", "name_oracle", "name_history",
         "eol_guard", "retired_guard", "doc_budget", "ea_name_guard", "name_lane", "link_debt", "target_hooks",
         "layout_migration", "check_csv", "pin_consistency", "b_pin_check", "find_declared_unmatched",
         "delta_sources", "identity_guard", "adopt_header", "one_identity", "gate_baseline",
         "class_gate", "ledger_guard", "ilt_guard", "alias_guard", "duplicate_global",
         "hatch_counters", "tu_ownership", "empty_commits")


@pytest.fixture
def hook_repo(repo):
    """The real hooks with every other checker stubbed; build.sh records what it verifies."""
    for tool in STUBS:
        put(repo, f"tools/{tool}.py", "raise SystemExit(0)\n")
    shutil.copyfile(TOOLS / "header_dependents.py", repo / "tools/header_dependents.py")
    put(repo, "build.sh", "#!/usr/bin/env bash\nprintf '%s\\n' \"$@\" >> built\n")
    (repo / "build.sh").chmod(0o755)
    git(repo, "add", "tools", "build.sh")
    included_base(repo)
    return repo


def hook(repo, name, refs=""):
    try:
        bash = bash_path.bash()
    except RuntimeError:
        pytest.skip("Bash is required to exercise hooks")
    return subprocess.run([bash, str(TOOLS.parent / ".githooks" / name)], cwd=repo, input=refs,
                          capture_output=True, text=True, env=bash_path.env())


def head(repo):
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, capture_output=True,
                          text=True, check=True).stdout.strip()


def test_pre_commit_verifies_the_includers_of_a_staged_source(hook_repo):
    put(hook_repo, "game/Net/Inc.cpp", "void inc2() {}\n")
    result = hook(hook_repo, "pre-commit")
    assert result.returncode == 0, result.stderr
    assert "newer than this tree" not in result.stderr  # STUBS covers every checker the hook runs
    assert "scoped gate over 2 dependent source(s)" in result.stderr
    assert (hook_repo / "built").read_text().splitlines()[:2] == ["game/Lib/Outer.cpp", "game/Net/Host.cpp"]


def test_pre_commit_refuses_unstaged_edits_in_an_included_table(hook_repo):
    put(hook_repo, "game/Lib/henc.tbl", "4, 5, 6,\n")
    (hook_repo / "game/Lib/henc.tbl").write_text("7, 8, 9,\n")
    result = hook(hook_repo, "pre-commit")
    assert result.returncode != 0
    assert "unstaged edits in game/Lib/henc.tbl" in result.stderr
    assert not (hook_repo / "built").exists()


def test_pre_push_verifies_the_includer_of_a_pushed_table(hook_repo):
    base_sha = head(hook_repo)
    put(hook_repo, "game/Lib/henc.tbl", "4, 5, 6,\n")
    git(hook_repo, "commit", "-qm", "table")
    result = hook(hook_repo, "pre-push", f"refs/heads/main {head(hook_repo)} refs/heads/main {base_sha}\n")
    assert result.returncode == 0, result.stderr
    assert (hook_repo / "built").read_text().splitlines() == ["game/Lib/Huff.cpp"]


def test_a_crash_fails_the_commit_instead_of_passing_it(hook_repo):
    put(hook_repo, "tools/header_dependents.py", "raise SystemExit(1)\n")
    git(hook_repo, "commit", "-qm", "broken tool")
    put(hook_repo, "game/Net/Inc.cpp", "void inc2() {}\n")
    result = hook(hook_repo, "pre-commit")
    assert result.returncode != 0
    assert "header_dependents (see above)" in result.stderr
    assert not (hook_repo / "built").exists()


# Every include the scanner cannot read with certainty must still be selected or widen,
# and selection must bind to the index or commit being verified, never the worktree.

def one_includer(repo, includer, text, extra=None):
    put(repo, "game/shared.h", "#define VALUE 1\n")
    put(repo, includer, text)
    for path, body in (extra or {}).items():
        put(repo, path, body)
    ledger(repo, includer)
    git(repo, "commit", "-qm", "base")


@pytest.mark.parametrize("suffix", ["cc", "cxx"])
def test_other_cxx_suffixes_are_selected(repo, capsys, suffix):
    one_includer(repo, f"game/a.{suffix}", '#include "shared.h"\n')
    put(repo, "game/shared.h", "#define VALUE 2\n")
    assert run(repo, capsys, "--staged") == (0, [f"game/a.{suffix}"])


def test_a_chain_through_an_included_non_header_is_followed(repo, capsys):
    one_includer(repo, "game/a.cpp", '#include "bridge.def"\n', {"game/bridge.def": '#include "shared.h"\n'})
    put(repo, "game/shared.h", "#define VALUE 2\n")
    assert run(repo, capsys, "--staged") == (0, ["game/a.cpp"])


@pytest.mark.parametrize("text", ['#include \\\n"shared.h"\n', '#inc\\\nlude "shared.h"\n',
                                  '#\\\ninclude "shared.h"\n', '/* x */ #include "shared.h"\n',
                                  '#include /* x */ "shared.h"\n', '﻿#include "shared.h"\n',
                                  '??=include "shared.h"\n', '#include \\\r\n"shared.h"\r\n'])
def test_spliced_commented_or_bom_includes_are_seen(repo, capsys, text):
    put(repo, "game/shared.h", "#define VALUE 1\n")
    (repo / "game/a.cpp").write_bytes(text.encode("utf-8"))
    git(repo, "add", "game/a.cpp")
    ledger(repo, "game/a.cpp")
    git(repo, "commit", "-qm", "base")
    put(repo, "game/shared.h", "#define VALUE 2\n")
    assert run(repo, capsys, "--staged") == (0, ["game/a.cpp"])


@pytest.mark.parametrize("text", ['#include "shared.h"\n', '#inc\\\nlude "shared.h"\n', '#\\\ninclude "shared.h"\n'])
def test_git_without_pcre_falls_back_to_the_same_selection(repo, capsys, monkeypatch, text):
    monkeypatch.setattr(H, "GREP_PCRE", "(")  # git grep -P fails as it does without PCRE
    one_includer(repo, "game/a.cpp", text)
    put(repo, "game/shared.h", "#define VALUE 2\n")
    assert run(repo, capsys, "--staged") == (0, ["game/a.cpp"])


def test_a_binary_looking_source_is_still_scanned(repo, capsys):
    one_includer(repo, "game/a.cpp", '#include "shared.h"\nchar z = 0;\0\n')
    put(repo, "game/shared.h", "#define VALUE 2\n")
    assert run(repo, capsys, "--staged") == (0, ["game/a.cpp"])


def test_an_unparseable_include_needs_the_full_gate(repo, capsys):
    one_includer(repo, "game/a.cpp", '#include "shared.h\n')
    put(repo, "game/shared.h", "#define VALUE 2\n")
    assert run(repo, capsys, "--staged")[0] == 2


def test_a_utf16_source_needs_the_full_gate(repo, capsys):
    put(repo, "game/shared.h", "#define VALUE 1\n")
    (repo / "game/a.cpp").write_bytes('#include "shared.h"\n'.encode("utf-16"))
    git(repo, "add", "game/a.cpp")
    ledger(repo, "game/a.cpp")
    git(repo, "commit", "-qm", "base")
    put(repo, "game/shared.h", "#define VALUE 2\n")
    assert run(repo, capsys, "--staged")[0] == 2


def test_a_macro_include_reaches_a_changed_non_header(repo, capsys):
    one_includer(repo, "game/a.cpp", '#define BODY "part.data"\nint f(){return\n#include BODY\n;}\n',
                 {"game/part.data": "1\n"})
    put(repo, "game/part.data", "2\n")
    assert run(repo, capsys, "--staged") == (0, ["game/a.cpp"])


def test_staged_selection_reads_the_index_not_the_worktree(repo, capsys):
    one_includer(repo, "game/a.cpp", '#include "shared.h"\n')
    put(repo, "game/shared.h", "#define VALUE 2\n")
    (repo / "game/a.cpp").write_text("int f() { return 1; }\n")
    (repo / "targets/game/reverse/functions.csv").write_text("name,export_rva,target_rva\n")
    assert run(repo, capsys, "--staged") == (0, ["game/a.cpp"])


def test_range_selection_reads_the_commits_not_the_worktree(repo, capsys):
    one_includer(repo, "game/a.cpp", '#include "shared.h"\n')
    old = head(repo)
    put(repo, "game/shared.h", "#define VALUE 2\n")
    git(repo, "commit", "-qm", "header")
    (repo / "game/a.cpp").write_text("int f() { return 1; }\n")
    (repo / "targets/game/reverse/functions.csv").write_text("name,export_rva,target_rva\n")
    assert run(repo, capsys, "--range", old, head(repo)) == (0, ["game/a.cpp"])


def test_range_sees_the_old_name_of_a_renamed_header(repo, capsys):
    base(repo)
    old = head(repo)
    git(repo, "mv", "game/Inc/Low.h", "game/Inc/Lower.h")
    git(repo, "commit", "-qm", "rename")
    git(repo, "config", "diff.renames", "true")
    assert run(repo, capsys, "--range", old, head(repo)) == (0, ["game/A.cpp"])


def test_pre_commit_refuses_an_unstaged_edit_in_a_selected_source(hook_repo):
    put(hook_repo, "game/Lib/henc.tbl", "4, 5, 6,\n")
    (hook_repo / "game/Lib/Huff.cpp").write_text("void huff() {}\n")
    result = hook(hook_repo, "pre-commit")
    assert result.returncode != 0
    assert "game/Lib/Huff.cpp" in result.stderr
    assert not (hook_repo / "built").exists()


def test_pre_push_refuses_a_dirty_includer_of_a_pushed_header(hook_repo):
    put(hook_repo, "game/Lib/Shared.h", "int s;\n")
    put(hook_repo, "game/Lib/Bridge.def", '#include "Shared.h"\n')
    put(hook_repo, "game/Lib/Huff.inl", '#include "henc.tbl"\n#include "Bridge.def"\n')
    git(hook_repo, "commit", "-qm", "bridge")
    base_sha = head(hook_repo)
    put(hook_repo, "game/Lib/Shared.h", "int s2;\n")
    git(hook_repo, "commit", "-qm", "header")
    (hook_repo / "game/Lib/Bridge.def").write_text("\n")
    result = hook(hook_repo, "pre-push", f"refs/heads/main {head(hook_repo)} refs/heads/main {base_sha}\n")
    assert result.returncode != 0
    assert "working tree differs" in result.stderr
    assert not (hook_repo / "built").exists()


# A vendored source or archive that no scanned file includes (inputs/vendor/nbench/hardware.c,
# d3dx9.lib, whose members the ledger claims) reaches TUs no #include names. Only a header or
# an included file was a root, so such a change alone selected nothing and both hooks took
# their narrow path: the full gate never ran.
VENDORED = ["inputs/vendor/nbench/hardware.c", "inputs/vendor/d3dx9/d3dx9.lib"]


def vendored_change(repo, path, operation):
    """Commit the base, then stage `operation` on `path`. A rename moves it out of
    inputs/vendor/ or into it (the other side under no scanned or gated root), or within it."""
    elsewhere = (path.rsplit("/", 1)[0] + "/moved/" if operation == "rename-within" else "attic/") + path.rsplit("/", 1)[-1]
    if operation != "add":
        put(repo, elsewhere if operation == "rename-in" else path, "x\n")
    base(repo)
    if operation == "delete":
        git(repo, "rm", "-q", path)
    elif operation.startswith("rename"):
        source, target = (elsewhere, path) if operation == "rename-in" else (path, elsewhere)
        (repo / target).parent.mkdir(parents=True, exist_ok=True)
        git(repo, "mv", source, target)
    else:
        put(repo, path, "y\n")


@pytest.mark.parametrize("path", VENDORED)
@pytest.mark.parametrize("operation", ["add", "modify", "delete", "rename-out", "rename-in", "rename-within"])
@pytest.mark.parametrize("staged", [True, False])
def test_a_vendored_file_nothing_includes_needs_the_full_gate(repo, capsys, path, operation, staged):
    vendored_change(repo, path, operation)
    if staged:
        assert run(repo, capsys, "--staged")[0] == 2
    else:
        old = head(repo)
        git(repo, "commit", "-qm", operation)
        assert run(repo, capsys, "--range", old, head(repo))[0] == 2


def record_full_gate(repo):
    """The full gate (gate_baseline.py --check) records that it ran; pre-push's evidence
    cache around it passes."""
    put(repo, "tools/gate_baseline.py", "import sys\nopen('full-gate', 'a').write(' '.join(sys.argv[1:]) + '\\n')\n")
    put(repo, "tools/verification_cache.py", "raise SystemExit(0)\n")


def full_gate(repo):
    path = repo / "full-gate"
    return path.read_text().splitlines() if path.exists() else []


def vendored_commit(repo, path, operation):
    record_full_gate(repo)
    put(repo, path, "x\n")
    git(repo, "commit", "-qm", "vendored")
    if operation == "delete":
        git(repo, "rm", "-q", path)
    elif operation == "rename":
        moved = path.rsplit("/", 1)[0] + "/moved/" + path.rsplit("/", 1)[-1]
        (repo / moved).parent.mkdir(parents=True)
        git(repo, "mv", path, moved)
    else:
        put(repo, path, "y\n")


@pytest.mark.parametrize("path", VENDORED)
@pytest.mark.parametrize("operation", ["modify", "delete", "rename"])
def test_pre_commit_runs_the_full_gate_for_a_vendored_change_alone(hook_repo, path, operation):
    """pre-commit asks the selector before its early exit, so the selector alone decides."""
    vendored_commit(hook_repo, path, operation)
    result = hook(hook_repo, "pre-commit")
    assert result.returncode == 0, result.stderr
    assert full_gate(hook_repo) == ["--check"], result.stderr


@pytest.mark.parametrize("path", VENDORED)
@pytest.mark.parametrize("operation", ["modify", "delete", "rename"])
def test_pre_push_runs_the_full_gate_for_a_vendored_change_alone(hook_repo, path, operation):
    vendored_commit(hook_repo, path, operation)
    base_sha = head(hook_repo)
    git(hook_repo, "commit", "-qm", operation)
    result = hook(hook_repo, "pre-push", f"refs/heads/main {head(hook_repo)} refs/heads/main {base_sha}\n")
    assert result.returncode == 0, result.stderr
    assert full_gate(hook_repo) == ["--check"], result.stdout + result.stderr


# ---- review round 2 (GPT-6.1-Sol and GPT-6-Astra, 2026-10-11): path shapes that still selected nothing ----
import os  # noqa: E402

POSIX_ONLY = pytest.mark.skipif(os.name == "nt", reason="Windows cannot create this file name")
# Without -z git lists each of these quoted and escaped ("inputs/vendor/caf\303\251.lib"), so the
# listed path began with a double quote and matched no root.
QUOTED = [
    "inputs/vendor/café.lib",
    pytest.param('inputs/vendor/a"b.lib', marks=POSIX_ONLY),
    pytest.param("inputs/vendor/a\tb.lib", marks=POSIX_ONLY),
    pytest.param("inputs/vendor/a\nb.lib", marks=POSIX_ONLY),
    pytest.param("inputs/vendor/a\\b.lib", marks=POSIX_ONLY),
]
# The same directories to the compiler on a case-insensitive host; check_case_collisions.py
# refuses only a whole-path collision, so nothing else stops one of these.
CASE_VARIANTS = ["Inputs/vendor/nbench/hardware.c", "inputs/Vendor/nbench/hardware.c",
                 "Inputs/Toolchains/vc71/bin/c1xx.dll"]


def selector_exit(repo, capsys, staged, message="change"):
    """The selector's exit code and output for what is staged now, or for that committed."""
    if staged:
        return run(repo, capsys, "--staged")
    old = head(repo)
    git(repo, "commit", "-qm", message)
    return run(repo, capsys, "--range", old, head(repo))


@pytest.mark.parametrize("path", QUOTED)
@pytest.mark.parametrize("operation", ["add", "modify", "delete", "rename-out", "rename-in", "rename-within"])
@pytest.mark.parametrize("staged", [True, False])
def test_a_vendored_name_git_would_quote_needs_the_full_gate(repo, capsys, path, operation, staged):
    vendored_change(repo, path, operation)
    assert selector_exit(repo, capsys, staged)[0] == 2


@pytest.mark.parametrize("path", CASE_VARIANTS)
@pytest.mark.parametrize("operation", ["add", "modify", "delete"])
@pytest.mark.parametrize("staged", [True, False])
def test_a_full_gate_root_in_another_letter_case_needs_the_full_gate(repo, capsys, path, operation, staged):
    vendored_change(repo, path, operation)
    assert selector_exit(repo, capsys, staged)[0] == 2


@pytest.mark.parametrize("root", ["inputs/vendor", "inputs/toolchains", "Inputs/Vendor"])
@pytest.mark.parametrize("entry", ["symlink", "gitlink"])
@pytest.mark.parametrize("staged", [True, False])
def test_an_entry_at_a_full_gate_root_itself_needs_the_full_gate(repo, capsys, root, entry, staged):
    """A symlink or gitlink where the directory was: git lists `inputs/vendor`, no slash after it."""
    base(repo)
    if entry == "symlink":
        blob = subprocess.run(["git", "hash-object", "-w", "--stdin"], cwd=repo, input="elsewhere",
                              capture_output=True, text=True, check=True).stdout.strip()
        git(repo, "update-index", "--add", "--cacheinfo", f"120000,{blob},{root}")
    else:
        git(repo, "update-index", "--add", "--cacheinfo", f"160000,{head(repo)},{root}")
    assert selector_exit(repo, capsys, staged)[0] == 2


@pytest.mark.parametrize("path", ["inputs/vendor2/file.lib", "inputs/vendorx", "inputs/toolchains-old/cl.exe",
                                  "attic/inputs/vendor/file.lib", "mods/inputs/vendor/file.lib"])
@pytest.mark.parametrize("staged", [True, False])
def test_a_path_that_only_resembles_a_full_gate_root_selects_nothing(repo, capsys, path, staged):
    """The slash boundary holds, a root is matched from the start of the path, ignored roots stay ignored."""
    vendored_change(repo, path, "add")
    assert selector_exit(repo, capsys, staged) == (0, [])


@pytest.mark.parametrize("staged", [True, False])
def test_a_header_git_would_quote_still_reaches_its_includers(repo, capsys, staged):
    """The quoted listing hid more than vendored paths: a header named with a non-ASCII
    character was no header (its listed name ended in a double quote) and selected nothing."""
    base(repo)
    header = "game/Inc/Café.h"
    put(repo, header, "int cafe;\n")
    (repo / "game/D.cpp").write_bytes('#include "Inc/Café.h"\nvoid d() {}\n'.encode("utf-8"))
    git(repo, "add", "--", "game/D.cpp")
    ledger(repo, "game/A.cpp", "game/B.cpp", "game/C.cpp", "game/D.cpp")
    git(repo, "commit", "-qm", "a header with a non-ASCII name")
    put(repo, header, "int cafe2;\n")
    assert selector_exit(repo, capsys, staged) == (0, ["game/D.cpp"])


# Coverage the reviewers probed that the selector already had; kept so it stays.
@pytest.mark.parametrize("shape", ["space", "mode", "copy", "symlink", "gitlink"])
@pytest.mark.parametrize("staged", [True, False])
def test_other_changes_under_a_full_gate_root_need_the_full_gate(repo, capsys, shape, staged):
    path = "inputs/vendor/a file.lib" if shape == "space" else "inputs/vendor/file.lib"
    put(repo, path, "x\n")
    base(repo)
    if shape == "space":
        put(repo, path, "y\n")
    elif shape == "mode":
        git(repo, "update-index", "--chmod=+x", path)
    elif shape == "copy":
        put(repo, "inputs/vendor/copied.lib", "x\n")
    elif shape == "symlink":   # the file becomes a link, by index entry so that Windows can run it
        blob = subprocess.run(["git", "hash-object", "-w", "--stdin"], cwd=repo, input="elsewhere.lib",
                              capture_output=True, text=True, check=True).stdout.strip()
        git(repo, "update-index", "--cacheinfo", f"120000,{blob},{path}")
    else:
        git(repo, "update-index", "--add", "--cacheinfo", f"160000,{head(repo)},inputs/vendor/submodule")
    assert selector_exit(repo, capsys, staged)[0] == 2


def test_a_vendored_change_that_arrives_by_merge_needs_the_full_gate(repo, capsys):
    base(repo)
    old = head(repo)
    git(repo, "checkout", "-qb", "vendor-branch")
    put(repo, "inputs/vendor/merge.lib", "x\n")
    git(repo, "commit", "-qm", "vendor")
    git(repo, "checkout", "-q", "--detach", old)
    put(repo, "README.md", "independent\n")
    git(repo, "commit", "-qm", "main")
    git(repo, "merge", "--no-ff", "-qm", "merge", "vendor-branch")
    assert run(repo, capsys, "--range", old, head(repo))[0] == 2


HOOK_SHAPES = ["inputs/vendor/café.lib", pytest.param("inputs/vendor/a\tb.lib", marks=POSIX_ONLY),
               "Inputs/vendor/nbench/hardware.c"]


def with_the_real_case_guard(repo):
    """The stub would prove nothing here: the real guard is what lets these paths through."""
    shutil.copyfile(TOOLS / "check_case_collisions.py", repo / "tools/check_case_collisions.py")
    git(repo, "add", "tools/check_case_collisions.py")


@pytest.mark.parametrize("path", HOOK_SHAPES)
def test_pre_commit_runs_the_full_gate_for_a_quoted_or_case_variant_vendored_path(hook_repo, path):
    with_the_real_case_guard(hook_repo)
    vendored_commit(hook_repo, path, "modify")
    result = hook(hook_repo, "pre-commit")
    assert result.returncode == 0, result.stderr
    assert full_gate(hook_repo) == ["--check"], result.stderr


@pytest.mark.parametrize("path", HOOK_SHAPES)
def test_pre_push_runs_the_full_gate_for_a_quoted_or_case_variant_vendored_path(hook_repo, path):
    with_the_real_case_guard(hook_repo)
    vendored_commit(hook_repo, path, "modify")
    base_sha = head(hook_repo)
    git(hook_repo, "commit", "-qm", "modify")
    result = hook(hook_repo, "pre-push", f"refs/heads/main {head(hook_repo)} refs/heads/main {base_sha}\n")
    assert result.returncode == 0, result.stderr
    assert full_gate(hook_repo) == ["--check"], result.stdout + result.stderr


# ---- review round 3 (GPT-6.1-Sol, 2026-10-11): a routed root in another letter case ----
# A ledger source includes Inputs/reference/fixture.tbl and only that table changes: the path
# began with no root the selector knows, so it selected nothing and both hooks passed without
# verifying the includer. The selector cannot follow such a path, so it asks for the full gate.

def index_entry(repo, path, text):
    """Stage `path` by index entry alone, so that a case-insensitive file system cannot
    fold its spelling into a directory that already exists."""
    blob = subprocess.run(["git", "hash-object", "-w", "--stdin"], cwd=repo, input=text,
                          capture_output=True, text=True, check=True).stdout.strip()
    git(repo, "update-index", "--add", "--cacheinfo", f"100644,{blob},{path}")


@pytest.mark.parametrize("path", ["inputs/reference/fixture.tbl", "Inputs/reference/fixture.tbl"])
@pytest.mark.parametrize("staged", [True, False])
def test_an_included_table_under_a_miscased_root_is_not_dropped(repo, capsys, path, staged):
    put(repo, path, "1, 2, 3,\n")
    put(repo, "game/A.cpp", '#include "../' + path + '"\n')
    ledger(repo, "game/A.cpp")
    git(repo, "commit", "-qm", "base")
    put(repo, path, "4, 5, 6,\n")
    result = selector_exit(repo, capsys, staged)
    if path.startswith("inputs/"):
        assert result == (0, ["game/A.cpp"])      # control: the lowercase root is followed
    else:
        assert result[0] == 2


def miscased_hook_change(repo, path):
    with_the_real_case_guard(repo)
    record_full_gate(repo)
    put(repo, path, "1, 2, 3,\n")
    put(repo, "game/D.cpp", '#include "../' + path + '"\n')
    ledger(repo, "game/Lib/Outer.cpp", "game/Net/Host.cpp", "game/Lib/Huff.cpp", "game/D.cpp")
    git(repo, "commit", "-qm", "base")
    put(repo, path, "4, 5, 6,\n")


def verified_by(repo, path, result):
    """The lowercase path's includer is built by the scoped gate; the other spelling runs the full gate."""
    assert result.returncode == 0, result.stderr
    built = (repo / "built").read_text().splitlines() if (repo / "built").exists() else []
    if path.startswith("inputs/"):
        assert built == ["game/D.cpp"] and full_gate(repo) == []
    else:
        assert full_gate(repo) == ["--check"], result.stdout + result.stderr


@pytest.mark.parametrize("path", ["inputs/reference/fixture.tbl", "Inputs/reference/fixture.tbl"])
def test_pre_commit_verifies_the_includer_of_a_table_under_a_miscased_root(hook_repo, path):
    miscased_hook_change(hook_repo, path)
    verified_by(hook_repo, path, hook(hook_repo, "pre-commit"))


@pytest.mark.parametrize("path", ["inputs/reference/fixture.tbl", "Inputs/reference/fixture.tbl"])
def test_pre_push_verifies_the_includer_of_a_table_under_a_miscased_root(hook_repo, path):
    miscased_hook_change(hook_repo, path)
    base_sha = head(hook_repo)
    git(hook_repo, "commit", "-qm", "change")
    verified_by(hook_repo, path,
                hook(hook_repo, "pre-push", f"refs/heads/main {head(hook_repo)} refs/heads/main {base_sha}\n"))


# every routed root, miscased at each of its components
MISCASED = ["Game/Lib/table.tbl", "GAME/Inc/New.h", "Inputs/table.tbl", "inputs/Reference/fixture.tbl",
            "Inputs/reference/shims/shim.cpp", "inputs/reference/Shims/shim.cpp", "inputs/Reference/shims/shim.h"]


@pytest.mark.parametrize("path", MISCASED)
@pytest.mark.parametrize("operation", ["add", "modify", "delete"])
@pytest.mark.parametrize("staged", [True, False])
def test_a_routed_root_in_another_letter_case_needs_the_full_gate(repo, capsys, path, operation, staged):
    if operation != "add":
        index_entry(repo, path, "x\n")
    base(repo)
    if operation == "delete":
        git(repo, "update-index", "--force-remove", "--", path)
    else:
        index_entry(repo, path, "y\n")
    assert selector_exit(repo, capsys, staged)[0] == 2


@pytest.mark.parametrize("root", ["game", "Game", "inputs", "inputs/reference", "inputs/reference/shims",
                                  "Inputs/Reference/Shims"])
@pytest.mark.parametrize("staged", [True, False])
def test_an_entry_at_a_routed_root_itself_needs_the_full_gate(repo, capsys, root, staged):
    put(repo, "README.md", "x\n")
    git(repo, "commit", "-qm", "base")
    blob = subprocess.run(["git", "hash-object", "-w", "--stdin"], cwd=repo, input="elsewhere",
                          capture_output=True, text=True, check=True).stdout.strip()
    git(repo, "update-index", "--add", "--cacheinfo", f"120000,{blob},{root}")
    assert selector_exit(repo, capsys, staged)[0] == 2


@pytest.mark.parametrize("path", ["mods/Game/table.tbl", "worldbuilder/Inputs/table.tbl",   # ignored, as spelt
                                  "Mods/table.tbl", "Mods/game/table.tbl",   # not ignored, and under no routed root
                                  "docs/Game/table.tbl", "gamex/table.tbl", "Gamex/table.tbl", "inputsx/table.tbl"])
@pytest.mark.parametrize("staged", [True, False])
def test_letter_case_outside_the_routed_roots_selects_nothing(repo, capsys, path, staged):
    base(repo)
    index_entry(repo, path, "x\n")
    assert selector_exit(repo, capsys, staged) == (0, [])


@pytest.mark.parametrize("staged", [True, False])
def test_a_header_under_a_miscased_ignored_root_is_still_followed(repo, capsys, staged):
    """Mods/ is not mods/: the ignored roots are not folded, so its header is a changed header."""
    base(repo)
    index_entry(repo, "Mods/Inc/Low.h", "int low3;\n")
    assert selector_exit(repo, capsys, staged) == (0, ["game/A.cpp"])
