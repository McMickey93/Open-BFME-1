"""link_debt: new hard-coded image addresses fail; renames and removals pass."""
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import link_debt as L  # noqa: E402


def git(root, *args):
    subprocess.run(["git", *args], cwd=root, check=True, capture_output=True)


@pytest.fixture
def repo(tmp_path, monkeypatch):
    git(tmp_path, "init", "-q")
    git(tmp_path, "config", "user.name", "Fixture")
    git(tmp_path, "config", "user.email", "fixture@example.invalid")
    monkeypatch.setattr(L, "ROOT", tmp_path)
    return tmp_path


def put(root, path, text):
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text)
    git(root, "add", "--", path)


LITERAL = "int f() { return *(int *)0x012ED5C8; }\n"
NAMED = "extern int g_012ED5C8;\nint f() { return g_012ED5C8; }\n"


def test_new_literal_fails(repo):
    put(repo, "game/A.cpp", NAMED)
    git(repo, "commit", "-qm", "base")
    put(repo, "game/A.cpp", LITERAL)
    assert L.staged() == 1


def test_replacing_a_literal_passes(repo):
    put(repo, "game/A.cpp", LITERAL)
    git(repo, "commit", "-qm", "base")
    put(repo, "game/A.cpp", NAMED)
    assert L.staged() == 0


def test_moving_a_file_keeps_its_count(repo):
    put(repo, "game/A.cpp", LITERAL)
    git(repo, "commit", "-qm", "base")
    git(repo, "mv", "game/A.cpp", "game/B.cpp")
    assert L.staged() == 0


def test_new_literal_cannot_hide_behind_removal_in_another_file(repo):
    put(repo, "game/A.cpp", LITERAL)
    put(repo, "game/B.cpp", NAMED)
    git(repo, "commit", "-qm", "base")
    put(repo, "game/A.cpp", NAMED)
    put(repo, "game/B.cpp", LITERAL)
    assert L.staged() == 1


def test_new_address_cannot_replace_an_old_one_in_the_same_file(repo):
    put(repo, "game/A.cpp", LITERAL)
    git(repo, "commit", "-qm", "base")
    put(repo, "game/A.cpp", LITERAL.replace("0x012ED5C8", "0x012ED5CC"))
    assert L.staged() == 1


def test_moving_literal_into_watched_tree_fails(repo):
    put(repo, "scratch/A.cpp", LITERAL)
    git(repo, "commit", "-qm", "base")
    (repo / "game").mkdir(exist_ok=True)
    git(repo, "mv", "scratch/A.cpp", "game/A.cpp")
    assert L.staged() == 1


def test_generated_roots_are_not_watched(repo):
    put(repo, "game/A.cpp", NAMED)
    git(repo, "commit", "-qm", "base")
    put(repo, "game/gen_small/x.cpp", LITERAL)
    assert L.staged() == 0


def test_same_address_with_different_hex_format_is_allowed(repo):
    put(repo, "game/A.cpp", LITERAL)
    git(repo, "commit", "-qm", "base")
    put(repo, "game/A.cpp", LITERAL.replace("0x012ED5C8", "0x12ed5c8"))
    assert L.staged() == 0


def test_failed_staged_listing_refuses_instead_of_treating_it_as_empty(repo, monkeypatch, capsys):
    put(repo, "game/A.cpp", NAMED)
    git(repo, "commit", "-qm", "base")
    put(repo, "game/A.cpp", LITERAL)
    # An unreadable index is not evidence that no sources were staged.
    broken_index = repo / "broken-index"
    broken_index.write_bytes(b"not a git index\n")
    monkeypatch.setenv("GIT_INDEX_FILE", str(broken_index))
    assert L.main(["--staged"]) == 1
    error = capsys.readouterr().err
    assert "git diff" in error and "index" in error


def test_failed_report_listing_refuses_instead_of_reporting_no_debt(repo, monkeypatch, capsys):
    broken_index = repo / "broken-index"
    broken_index.write_bytes(b"not a git index\n")
    monkeypatch.setenv("GIT_INDEX_FILE", str(broken_index))
    assert L.main(["--report"]) == 1
    output = capsys.readouterr()
    assert "git ls-files" in output.err and "index" in output.err
    assert "0 hard-coded image addresses" not in output.out


def test_git_cannot_start_refuses_with_a_diagnostic(repo, monkeypatch, capsys):
    def unavailable(*args, **kwargs):
        raise FileNotFoundError("fixture: git is unavailable")

    monkeypatch.setattr(L.subprocess, "run", unavailable)
    assert L.main(["--staged"]) == 1
    error = capsys.readouterr().err
    assert "cannot run git" in error and "git is unavailable" in error


@pytest.mark.parametrize("ref", ["HEAD", ""])
def test_failed_source_read_refuses_instead_of_treating_it_as_empty(repo, monkeypatch, capsys, ref):
    source = "game/source with spaces.cpp"
    put(repo, source, NAMED)
    git(repo, "commit", "-qm", "base")
    put(repo, source, NAMED + "// changed\n")
    run = subprocess.run

    def fail_one_read(command, *args, **kwargs):
        if command == ["git", "show", f"{ref}:{source}"]:
            return subprocess.CompletedProcess(command, 128, "", "fixture: cannot read object")
        return run(command, *args, **kwargs)

    monkeypatch.setattr(L.subprocess, "run", fail_one_read)
    assert L.main(["--staged"]) == 1
    error = capsys.readouterr().err
    assert "git show" in error and source in error and "cannot read object" in error


def test_first_commit_needs_no_head_blob(repo):
    put(repo, "game/A.cpp", NAMED)
    assert L.main(["--staged"]) == 0
    put(repo, "game/A.cpp", LITERAL)
    assert L.main(["--staged"]) == 1


def test_deleting_source_needs_no_index_blob(repo):
    put(repo, "game/A.cpp", LITERAL)
    git(repo, "commit", "-qm", "base")
    git(repo, "rm", "game/A.cpp")
    assert L.main(["--staged"]) == 0


def test_renaming_source_with_spaces_and_unicode_keeps_its_count(repo):
    put(repo, "game/old name.cpp", LITERAL)
    git(repo, "commit", "-qm", "base")
    git(repo, "mv", "game/old name.cpp", "game/Größe name.cpp")
    assert L.main(["--staged"]) == 0


def test_masks_and_comments_are_not_addresses():
    assert L.literals("if (x & 0x80000000) {}  // *(int *)0x012ED5C8\n") == []


@pytest.mark.parametrize("suffix", ["", "u", "U", "l", "L", "ul", "UL", "lu", "LU", "ll", "LL", "ull", "ULL", "llu", "LLU"])
@pytest.mark.parametrize("cast", ["(int *)", "(const void * volatile)", "(void (*)(void))",
                                  "reinterpret_cast<void *>", "reinterpret_cast<void (*)()>"])
def test_pointer_casts_include_integer_suffixes(cast, suffix):
    source = f"return {cast}(0x0043C9CF{suffix});"
    assert len(L.literals(source)) == 1


@pytest.mark.parametrize("cast", ["(void (*)(void))", "reinterpret_cast<void (*)()>"])
def test_new_callback_literal_fails(repo, cast):
    put(repo, "game/A.cpp", NAMED)
    git(repo, "commit", "-qm", "base")
    put(repo, "game/A.cpp", f"return {cast}(0x0043C9CFu);")
    assert L.staged() == 1


def test_suffix_and_cast_changes_preserve_existing_address_debt(repo):
    put(repo, "game/A.cpp", "return (void (*)(void))0x0043C9CFu;")
    git(repo, "commit", "-qm", "base")
    put(repo, "game/A.cpp", "return reinterpret_cast<void (*)()>(0x0043c9cfUL);")
    assert L.staged() == 0
    put(repo, "game/A.cpp", "return reinterpret_cast<void (*)()>(0x0043c9d0UL);")
    assert L.staged() == 1


def test_extended_casts_do_not_capture_plain_constants_or_documentation():
    assert L.literals('''
        unsigned color = 0x00B4B0A5u;
        return 0x0043C9CF;
        (unsigned)0x0043C9CFu;
        /* (void (*)(void))0x0043C9CFu */
        "reinterpret_cast<void (*)()>(0x0043C9CFu)";
        // (void *)0x0043C9CFu
    ''') == []


def test_addresses_catch_every_form_of_an_image_address():
    text = """
    *(unsigned *)this = 0x0113C340;          // vftable stored as an integer
    m_vptr = 0x0111ff78u;
    float f = BFME_AT(float, 0x01076C24);
    return reinterpret_cast<void (*)()>(0x0043c9cf);
    """
    assert L.addresses(text) == ["0x0113C340", "0x0111ff78u", "0x01076C24", "0x0043c9cf"]


def test_addresses_skip_flags_masks_sizes_comments_and_strings():
    text = """
    m_flags |= 0x1000100;      // two bits: a flag word
    unsigned m = v & 0xffffff; // one repeated digit: a mask
    size_t n = 0x00401000;     // low 12 bits clear
    const char *s = "0x0113C340";
    /* 0x0113C340 */
    int small = 0x3FC;
    """
    assert L.addresses(text) == []


def test_contiguous_bit_run_sentinels_are_not_addresses():
    # re_attempts.log: PolygonTrigger::updateBounds BIG_INT 0x7ffff0 and
    # ScriptActions transport capacity 0x7fffff are integer bounds.
    text = """
    const Int BIG_INT = 0x7ffff0;
    if (slots == 0) slots = 0x7fffff;
    """
    assert L.addresses(text) == []
    # An address with a broken bit run is still one.
    assert L.addresses("m_vptr = 0x007ffef0;") == ["0x007ffef0"]
