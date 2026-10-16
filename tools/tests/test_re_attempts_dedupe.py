"""Union-merge duplicate runs in re_attempts.log and the guard's one-time
dedupe exemption (approved by the project lead 2026-10-16)."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import check_csv  # noqa: E402
import re_attempts_dedupe as D  # noqa: E402

A, B, C, E, F = (f"?{x}@@YAXXZ\t0x0000{n}000\t4\tblocked\t{x} t=1 model=m".encode()
                 for n, x in zip(range(1, 6), "abcef"))


def log(*rows):
    return b"".join(r + b"\n" for r in rows)


def test_runs_and_singles():
    raw = log(A, B, C, A, B, E, C, F)
    new, runs, singles = D.dedupe(raw)
    assert runs == [(3, 2, 0)]                  # A,B re-added after C: one run, first kept
    assert singles == [(6, 2)]                  # a lone repeat of C stays
    assert new == log(A, B, C, E, C, F)


def test_maximal_run_and_cr_insensitive():
    raw = A + b"\r\n" + B + b"\r\n" + C + b"\r\n" + log(A, B, C, E)
    new, runs, _ = D.dedupe(raw)
    assert runs == [(3, 3, 0)] and new == A + b"\r\n" + B + b"\r\n" + C + b"\r\n" + log(E)


def test_no_runs_no_change():
    raw = log(A, B, A, C)
    new, runs, singles = D.dedupe(raw)
    assert runs == [] and new == raw and singles == [(2, 0)]


def guard(base, new, claim):
    out = []
    check_csv.check_re_attempts_append_only(base, new, out, dedupe_claim=claim)
    return out


BASE = log(A, B, C, A, B, E)
BASE_ID = check_csv.git_blob_id(BASE)


def claim(runs, base=BASE):
    return (runs, check_csv.git_blob_id(base))


def test_blob_id_is_gits(tmp_path):
    path = tmp_path / "x"
    path.write_bytes(BASE)
    out = subprocess.run(["git", "hash-object", str(path)], capture_output=True, text=True)
    assert out.stdout.strip() == BASE_ID


def test_exact_dedupe_with_matching_claim_passes():
    assert guard(BASE, log(A, B, C, E), claim(1)) == []


def test_claim_count_mismatch_refused():
    assert "claims a dedupe of 2" in guard(BASE, log(A, B, C, E), claim(2))[0]


def test_fake_claim_with_a_non_duplicate_deletion_refused():
    assert guard(BASE, log(A, B, E), claim(1))                 # also dropped C, not a duplicate
    assert guard(BASE, log(A, B, C, A, E), claim(1))           # removed only half the run


def test_claim_without_duplicates_refused():
    assert guard(log(A, B, C), log(A, B), claim(0, log(A, B, C)))


def test_deletion_without_a_claim_refused():
    assert "removed" in guard(BASE, log(A, B, C, E), None)[0]


def test_the_claim_is_one_shot():
    """A claim names the blob it dedupes. Reused on a later log (here: the same
    duplicate shape re-added after the dedupe landed) it is no exemption, and
    the ordinary append-only rules refuse the deletion."""
    later = log(A, B, C, E, F, A, B)
    assert D.dedupe(later)[1], "the later log must have a run to delete"
    assert "removed" in guard(later, log(A, B, C, E, F), claim(1))[0]
    assert guard(later, log(A, B, C, E, F), claim(1, later)) == []


def test_a_stale_claim_never_refuses_an_unchanged_or_appended_log():
    """BFME_RE_ATTEMPTS_DEDUPE left in the environment must not refuse every
    --staged check: an unchanged log, or a plain append, is judged normally."""
    assert guard(BASE, BASE, claim(1)) == []
    later = log(A, B, C, E)
    assert guard(later, later + log(F), claim(1)) == []
    assert guard(later, later + log(F), claim(1, later)) != [], \
        "a claim on THIS base still demands exactly its dedupe"


def _repo(tmp_path):
    repo = tmp_path / "r"
    repo.mkdir()
    run = lambda *a: subprocess.run(["git", *a], cwd=repo, check=True, capture_output=True)
    run("init", "-q")
    return repo, run


def _commit(repo, run, raw, message):
    path = repo / check_csv.RE_ATTEMPTS_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)
    run("add", "-A")
    run("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", message, "--no-gpg-sign")
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, capture_output=True,
                          text=True).stdout.strip()


def test_claim_sources(monkeypatch, tmp_path):
    monkeypatch.setenv("BFME_RE_ATTEMPTS_DEDUPE", f"126 runs base={BASE_ID}")
    assert check_csv.re_attempts_dedupe_claim(None) == (126, BASE_ID)
    monkeypatch.setenv("BFME_RE_ATTEMPTS_DEDUPE", "126")
    assert check_csv.re_attempts_dedupe_claim(None) is None, "a claim must name its base"
    monkeypatch.delenv("BFME_RE_ATTEMPTS_DEDUPE")
    assert check_csv.re_attempts_dedupe_claim(None) is None
    repo, run = _repo(tmp_path)
    _commit(repo, run, BASE, f"dedupe\n\nRe-Attempts-Dedupe: 3 runs base={BASE_ID}\n"
                             "Co-Authored-By: x <x@x>")
    monkeypatch.setattr(check_csv, "ROOT", repo)
    assert check_csv.re_attempts_dedupe_claim("HEAD") == (3, BASE_ID)


def test_the_range_check_sees_a_deletion_below_the_tip(monkeypatch, tmp_path):
    """pre-push judged only tip-vs-first-parent; a deletion one commit below an
    innocent tip passed. Every commit in BASE..TIP is judged with its own trailer."""
    repo, run = _repo(tmp_path)
    monkeypatch.setattr(check_csv, "ROOT", repo)
    base = _commit(repo, run, BASE, "base")
    _commit(repo, run, log(A, B, C, E), "silent deletion")
    tip = _commit(repo, run, log(A, B, C, E, F), "innocent append")
    found = []
    check_csv.check_re_attempts_range(base, tip, found)
    assert len(found) == 1 and "removed" in found[0]
    run("reset", "-q", "--hard", base)
    _commit(repo, run, log(A, B, C, E), f"dedupe\n\nRe-Attempts-Dedupe: 1 runs base={BASE_ID}")
    tip = _commit(repo, run, log(A, B, C, E, F), "append after the dedupe")
    found = []
    check_csv.check_re_attempts_range(base, tip, found)
    assert found == [], "the dedupe need not be the tip any more"
