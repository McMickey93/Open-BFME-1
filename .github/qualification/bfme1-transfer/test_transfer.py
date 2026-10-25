"""Bounded trust-boundary tests; no network, credentials or native compilation."""

import contextlib
import copy
import importlib.util
import io
import json
import os
from pathlib import Path
import stat
import subprocess
import tempfile
import types
import unittest
from unittest import mock
import urllib.error
import urllib.request
import zipfile


SPEC = importlib.util.spec_from_file_location("qualified_transfer", Path(__file__).with_name("transfer.py"))
transfer = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(transfer)
ACTOR = "McMickey93"
SHA = "a" * 40
SHA256 = "b" * 64


def request():
    return {"schema": 1, "enabled": True, "qualification_run_id": 77, "qualification_run_attempt": 1,
            "qualification_head_sha": SHA, "artifact_id": 88, "artifact_sha256": SHA256,
            "expected_base": "c" * 40, "expected_commit": "d" * 40, "expected_tree": "e" * 40,
            "qualification_directory": "qualification-0"}


def workflow():
    return {"GITHUB_REPOSITORY": transfer.FORK, "GITHUB_SHA": SHA, "GITHUB_RUN_ID": "77",
            "GITHUB_RUN_ATTEMPT": "1", "GITHUB_ACTOR": ACTOR, "GITHUB_TRIGGERING_ACTOR": ACTOR,
            "RUNNER_OS": "Windows", "ImageVersion": "test-image"}


def source_run():
    return {"id": 77, "run_attempt": 1, "head_sha": SHA, "path": transfer.WORKFLOW,
            "event": "workflow_dispatch", "head_branch": "master", "status": "completed", "conclusion": "success",
            "repository": {"full_name": transfer.FORK, "fork": True, "private": False},
            "head_repository": {"full_name": transfer.FORK}, "actor": {"login": ACTOR},
            "triggering_actor": {"login": ACTOR}}


class SourceFixture(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.source = self.root / "source"
        self.source.mkdir()
        self.git("init", "-q")
        self.git("config", "user.name", "Fixture")
        self.git("config", "user.email", "fixture@example.invalid")
        self.git("config", "core.autocrlf", "false")
        self.path = "game/Test/body.cpp"
        self.write(self.path, b"int body() { return 0; }\r\n")
        self.write(transfer.LEDGER, b"name,export_rva,target_rva,target_size,source,status,notes\n"
                   b"?old@@YAHXZ,,0x00001000,5,game/gen_asm/old.asm,matched,fixture\n")
        self.write("targets/game/reverse/publisher_mode", b"off\n")
        self.git("add", ".")
        self.git("commit", "-qm", "base fixture")
        self.base = self.git("rev-parse", "HEAD").decode().strip()
        base_blob = self.git("rev-parse", "HEAD:" + self.path).decode().strip()
        base_tree = self.git("rev-parse", "HEAD^{tree}").decode().strip()
        self.content = b"int body() { return 1; }\r\n"
        self.write(self.path, self.content)
        self.git("add", self.path)
        self.tree = self.git("write-tree").decode().strip()
        self.blob = self.git("rev-parse", ":" + self.path).decode().strip()
        self.claim = {"rva": "0x00001000", "owner": "github:mcmickey93:bfme1:test", "lease": "1" * 32}
        self.message = "Recover fixture body\n\nClaim-Lease: 0x00001000=" + self.claim["lease"] + "\n"
        self.commit_bytes = ("tree %s\nparent %s\nauthor Fixture <fixture@example.invalid> 1700000000 +0000\n"
                             "committer Fixture <fixture@example.invalid> 1700000000 +0000\n\n%s"
                             % (self.tree, self.base, self.message)).encode()
        self.commit = transfer.object_id("commit", self.commit_bytes)
        # Restore the base checkout without creating the candidate commit yet.
        self.git("restore", "--source=HEAD", "--staged", "--worktree", self.path)
        self.request = request()
        self.request.update(expected_base=self.base, expected_tree=self.tree, expected_commit=self.commit)
        self.body = {"rva": "0x00001000", "source": self.path, "size": 5, "symbol": "?body@@YAHXZ", "replace": "rva"}
        self.data = {"schema_version": 1, "repository": transfer.FORK, "upstream": transfer.UPSTREAM,
                     "mode": "qualify", "base": self.base, "base_tree": base_tree, "patch_tree": self.tree,
                     "body": self.body, "claims": [self.claim], "model": "fixture",
                     "files": [{"path": self.path, "mode": "100644", "base_blob": base_blob,
                                "candidate_blob": self.blob, "sha256": transfer.digest(self.content)}],
                     "base_rows": [{"name": "?old@@YAHXZ", "export_rva": "", "target_rva": "0x00001000",
                                    "target_size": "5", "source": "game/gen_asm/old.asm", "status": "matched", "notes": "fixture"}]}
        self.publication = {"repository": transfer.OFFICIAL, "base": self.base, "commit": self.commit,
                            "tree": self.tree, "message": self.message, "published": False,
                            "normal_commit_passed": True, "normal_pre_push_passed": True,
                            "workflow": workflow(), "claims": [self.claim],
                            "progress": {"base": self.base, "head": self.commit, "cpp_exact_before": 1,
                                         "cpp_exact_after": 6, "cpp_exact_delta": 5},
                            "files": [{"path": self.path, "mode": "100644", "blob": self.blob,
                                       "size": len(self.content), "sha256": transfer.digest(self.content),
                                       "content_file": "qualification-0/candidate-files/" + self.path}]}
        self.runner = transfer.Runner(self.source)

    def git(self, *args, raw=None, okay=True):
        result = subprocess.run(["git", *args], cwd=self.source, input=raw, capture_output=True)
        if okay:
            self.assertEqual(result.returncode, 0, result.stderr.decode(errors="replace"))
        return result.stdout if okay else result

    def write(self, name, raw):
        path = self.source / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)

    def import_candidate(self):
        with contextlib.redirect_stdout(io.StringIO()):
            transfer.import_exact(self.runner, self.publication, self.commit_bytes, lambda _: self.content)

    def test_exact_import_preserves_raw_commit_tree_and_crlf_bytes(self):
        transfer.validate_manifests(self.request, self.data, self.publication, ACTOR)
        self.import_candidate()
        self.assertEqual(self.git("cat-file", "commit", self.commit), self.commit_bytes)
        self.assertEqual(self.git("cat-file", "blob", self.commit + ":" + self.path), self.content)
        self.assertEqual(self.git("rev-parse", "HEAD").decode().strip(), self.base)
        self.assertEqual(self.git("status", "--porcelain"), b"")

    def test_content_tamper_and_unlisted_tree_change_are_rejected(self):
        with self.assertRaises(transfer.Rejected), contextlib.redirect_stdout(io.StringIO()):
            transfer.import_exact(self.runner, self.publication, self.commit_bytes, lambda _: self.content + b"x")
        self.write("tools/hidden.py", b"raise SystemExit(0)\n")
        self.git("add", "tools/hidden.py")
        other_tree = self.git("write-tree").decode().strip()
        modified = copy.deepcopy(self.publication)
        modified["tree"] = other_tree
        raw = self.commit_bytes.replace(self.tree.encode(), other_tree.encode(), 1)
        modified["commit"] = transfer.object_id("commit", raw)
        with self.assertRaisesRegex(transfer.Rejected, "Reconstructed tree"), contextlib.redirect_stdout(io.StringIO()):
            transfer.import_exact(self.runner, modified, raw, lambda _: self.content)

    def test_raw_commit_rejects_second_parent_or_changed_message(self):
        raw = self.commit_bytes.replace(b"\nauthor ", b"\nparent " + self.base.encode() + b"\nauthor ")
        modified = {**self.publication, "commit": transfer.object_id("commit", raw)}
        with self.assertRaises(transfer.Rejected):
            transfer.raw_commit(raw, modified)
        with self.assertRaises(transfer.Rejected):
            transfer.raw_commit(self.commit_bytes, {**self.publication, "message": "different\n"})

    def test_manifest_rejects_explore_false_gates_extra_paths_and_modes(self):
        mutations = [lambda d, p: d.update(mode="explore"),
                     lambda d, p: p.update(normal_pre_push_passed=False),
                     lambda d, p: p["files"][0].update(mode="120000"),
                     lambda d, p: p["files"][0].update(path="tools/claims.py"),
                     lambda d, p: p["files"][0].update(content_file="qualification-0/../secret"),
                     lambda d, p: p["progress"].update(cpp_exact_delta=0, cpp_exact_after=1),
                     lambda d, p: p["workflow"].update(GITHUB_RUN_ID="78"),
                     lambda d, p: d["claims"][0].update(owner="github:another:bfme1:test")]
        for mutate in mutations:
            with self.subTest(mutation=mutate):
                data, pub = copy.deepcopy(self.data), copy.deepcopy(self.publication)
                mutate(data, pub)
                with self.assertRaises(transfer.Rejected):
                    transfer.validate_manifests(self.request, data, pub, ACTOR)

    def test_base_advance_accepts_unrelated_source_and_rejects_changed_gate(self):
        self.write("game/Test/unrelated.cpp", b"int unrelated;\n")
        self.git("add", ".")
        self.git("commit", "-qm", "unrelated source")
        advanced = self.git("rev-parse", "HEAD").decode().strip()
        with contextlib.redirect_stdout(io.StringIO()):
            transfer.validate_base(self.runner, self.data, {**self.publication, "base": advanced})
        self.write("tools/new_gate.py", b"raise SystemExit(0)\n")
        self.git("add", ".")
        self.git("commit", "-qm", "control change")
        advanced = self.git("rev-parse", "HEAD").decode().strip()
        with self.assertRaisesRegex(transfer.Rejected, "Controls"), contextlib.redirect_stdout(io.StringIO()):
            transfer.validate_base(self.runner, self.data, {**self.publication, "base": advanced})

    def test_claimed_row_or_source_preimage_change_is_rejected(self):
        self.write(transfer.LEDGER, (self.source / transfer.LEDGER).read_bytes().replace(b",5,", b",6,"))
        self.git("add", transfer.LEDGER)
        self.git("commit", "-qm", "changed row")
        advanced = self.git("rev-parse", "HEAD").decode().strip()
        with self.assertRaisesRegex(transfer.Rejected, "Claimed ledger rows"), contextlib.redirect_stdout(io.StringIO()):
            transfer.validate_base(self.runner, self.data, {**self.publication, "base": advanced})
        self.write(self.path, b"int body() { return 3; }\n")
        self.git("add", self.path)
        self.git("commit", "-qm", "changed source")
        advanced = self.git("rev-parse", "HEAD").decode().strip()
        with self.assertRaisesRegex(transfer.Rejected, "preimage"), contextlib.redirect_stdout(io.StringIO()):
            transfer.validate_base(self.runner, self.data, {**self.publication, "base": advanced})

    def test_ledger_selection_streams_lines_and_records_git_failure(self):
        class LineOnly:
            def __iter__(self):
                yield "name,export_rva,target_rva,target_size,source,status,notes\n"
                for rva in range(5000):
                    yield "?old@@YAHXZ,,0x%08X,5,game/gen_asm/old.asm,matched,fixture\n" % rva

            def read(self, *args):
                raise AssertionError("The complete ledger must not be loaded for selection")

        self.assertEqual(transfer.selected_claim_rows(LineOnly(), self.data), self.data["base_rows"])
        self.assertEqual(self.runner.claimed_rows(self.base, self.data), self.data["base_rows"])
        record = self.runner.receipt["commands"][-1]
        self.assertEqual(record["exit_code"], 0)
        self.assertEqual(record["selected_row_count"], 1)
        with self.assertRaisesRegex(transfer.Rejected, "Could not stream"):
            self.runner.claimed_rows("f" * 40, self.data)
        self.assertNotEqual(self.runner.receipt["commands"][-1]["exit_code"], 0)

    def test_bundle_has_only_the_exact_head_and_base_prerequisite(self):
        self.import_candidate()
        self.git("branch", transfer.LOCAL_REF.removeprefix("refs/heads/"), self.commit)
        bundle = self.root / "candidate.bundle"
        self.git("bundle", "create", str(bundle), self.base + ".." + transfer.LOCAL_REF)
        raw = bundle.read_bytes()
        transfer.validate_bundle_header(raw, self.publication)
        with self.assertRaises(transfer.Rejected):
            transfer.validate_bundle_header(raw.replace(transfer.LOCAL_REF.encode(), b"refs/heads/master", 1), self.publication)
        with self.assertRaises(transfer.Rejected):
            transfer.validate_bundle_header(raw.replace(b"\n\n", b"\n" + self.base.encode() + b" refs/heads/extra\n\n", 1), self.publication)

    def test_actual_git_empty_lease_creates_once_and_never_overwrites(self):
        remote = self.root / "fork.git"
        subprocess.run(["git", "init", "--bare", "-q", str(remote)], check=True, capture_output=True)
        self.import_candidate()
        hook = self.source / ".githooks/pre-push"
        hook.parent.mkdir()
        hook.write_text("#!/bin/sh\nprintf 'ordinary hook ran\\n' >> hook-receipt.txt\ncat >/dev/null\n", encoding="utf-8")
        hook.chmod(0o755)
        self.git("config", "core.hooksPath", ".githooks")
        ref = transfer.target_ref(self.request)
        self.git("push", "--porcelain", "--force-with-lease=" + ref + ":", str(remote), self.commit + ":" + ref)
        self.assertTrue((self.source / "hook-receipt.txt").is_file())
        # Even a legitimate descendant must not update the existing branch.
        later = self.commit_bytes.replace(b"parent " + self.base.encode(), b"parent " + self.commit.encode())
        later_id = self.git("hash-object", "-t", "commit", "-w", "--stdin", raw=later).decode().strip()
        result = self.git("push", "--porcelain", "--force-with-lease=" + ref + ":", str(remote), later_id + ":" + ref, okay=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.git("ls-remote", str(remote), ref).decode().strip(), self.commit + "\t" + ref)

    def test_claim_owner_lease_expiry_and_readback_must_all_hold(self):
        info = {"owner": self.claim["owner"], "lease": self.claim["lease"], "expires": 200}
        module = types.SimpleNamespace(fetch=lambda: True, _read_local=lambda: {0x1000: (SHA, info)}, holds=lambda rva, token: True)
        transfer.current_claims(self.runner, self.data, "fixture", module, now=100)
        for field, value in (("expires", 99), ("owner", "someone-else"), ("lease", "2" * 32)):
            with self.subTest(field=field):
                original = info[field]
                info[field] = value
                with self.assertRaises(transfer.Rejected):
                    transfer.current_claims(self.runner, self.data, "fixture", module, now=100)
                info[field] = original
        module.holds = lambda rva, token: False
        with self.assertRaises(transfer.Rejected):
            transfer.current_claims(self.runner, self.data, "fixture", module, now=100)

    def test_actual_official_base_is_not_replaced_by_stale_tracking_ref(self):
        with mock.patch.object(self.runner, "git", return_value=(SHA + "\trefs/heads/master\n").encode()):
            with self.assertRaises(transfer.Rejected):
                self.runner.assert_master(self.base)


class BoundaryTests(unittest.TestCase):
    def test_request_disabled_and_unexpected_overrides_fail_closed(self):
        valid = request()
        self.assertEqual(transfer.read_request(json.dumps(valid).encode())[0], valid)
        for changes in ({"enabled": False}, {"destination": transfer.UPSTREAM}, {"artifact_id": True},
                        {"expected_commit": "HEAD"}, {"qualification_directory": "qualification-0/../"}):
            with self.subTest(changes=changes), self.assertRaises(transfer.Rejected):
                transfer.read_request(json.dumps({**valid, **changes}).encode())
        with self.assertRaises(transfer.Rejected):
            transfer.json_bytes(b'{"schema":1,"schema":2}')

    def test_source_run_requires_exact_successful_manual_run_and_actor(self):
        transfer.check_run(source_run(), request(), ACTOR)
        for key, value in (("head_sha", "e" * 40), ("event", "pull_request"), ("run_attempt", 2),
                           ("conclusion", "failure"), ("path", "other-workflow.yml")):
            with self.subTest(key=key), self.assertRaises(transfer.Rejected):
                transfer.check_run({**source_run(), key: value}, request(), ACTOR)
        with self.assertRaises(transfer.Rejected):
            transfer.check_run(source_run(), request(), "another-user")

    def test_artifact_pin_includes_digest_run_head_and_name(self):
        meta = {"id": 88, "name": "bfme1-body-77-1", "expired": False, "digest": "sha256:" + SHA256,
                "workflow_run": {"id": 77, "head_sha": SHA}, "size_in_bytes": 100}
        transfer.check_artifact(meta, 88, SHA256, 77, SHA, "bfme1-body-77-1")
        for key, value in (("expired", True), ("digest", "sha256:" + "c" * 64), ("name", "bfme1-body-77-2")):
            with self.subTest(key=key), self.assertRaises(transfer.Rejected):
                transfer.check_artifact({**meta, key: value}, 88, SHA256, 77, SHA, "bfme1-body-77-1")

    def test_fork_branch_and_compare_create_lease_have_no_override(self):
        argv = transfer.push_command(request())
        ref = transfer.target_ref(request())
        self.assertEqual(argv, ["git", "push", "--porcelain", "--force-with-lease=" + ref + ":",
                                transfer.FORK_URL, request()["expected_commit"] + ":" + ref])
        self.assertNotIn("--force", argv)
        self.assertNotIn("--no-verify", argv)
        self.assertTrue(ref.startswith("refs/heads/qualified/bfme1-77-1-"))

    def test_existing_identical_branch_is_read_only_different_branch_rejects(self):
        wanted = request()
        runner = types.SimpleNamespace(git=mock.Mock(return_value=b""))
        self.assertFalse(transfer.existing_ref(runner, wanted))
        runner.git.return_value = (wanted["expected_commit"] + "\t" + transfer.target_ref(wanted) + "\n").encode()
        self.assertTrue(transfer.existing_ref(runner, wanted))
        runner.git.return_value = (SHA + "\t" + transfer.target_ref(wanted) + "\n").encode()
        with self.assertRaises(transfer.Rejected):
            transfer.existing_ref(runner, wanted)
        self.assertTrue(all(call.args[1] == "ls-remote" for call in runner.git.call_args_list))

    def test_token_is_url_scoped_and_removed_from_unrelated_child_environment(self):
        env, header = transfer.push_environment("ephemeral-fixture-token", {"GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": "core.autocrlf",
            "GIT_CONFIG_VALUE_0": "false", "BFME_TRANSFER_TOKEN": "ephemeral-fixture-token", "GIT_TRACE_CURL": "1", "GIT_CURL_VERBOSE": "1"})
        self.assertEqual(env["GIT_CONFIG_KEY_1"], "http." + transfer.FORK_URL + ".extraheader")
        self.assertNotIn("BFME_TRANSFER_TOKEN", env)
        self.assertNotIn("GIT_TRACE_CURL", env)
        self.assertNotIn("GIT_CURL_VERBOSE", env)
        self.assertNotIn("ephemeral-fixture-token", " ".join(transfer.push_command(request())))
        self.assertTrue(header.startswith("AUTHORIZATION: basic "))

    def test_authenticated_api_redirect_never_forwards_authorization(self):
        api = transfer.GitHub("ephemeral-fixture-token")
        body = b"artifact-bytes"
        signed = "https://example.blob.core.windows.net/artifact?signature=fixture"
        requests = []
        def api_open(req, timeout):
            requests.append(req)
            self.assertEqual(req.get_header("Authorization"), "Bearer ephemeral-fixture-token")
            raise urllib.error.HTTPError(req.full_url, 302, "redirect", {"Location": signed}, None)
        def blob_open(req, timeout):
            requests.append(req)
            self.assertIsNone(req.get_header("Authorization"))
            return io.BytesIO(body)
        api.api_opener = types.SimpleNamespace(open=api_open)
        api.download_opener = types.SimpleNamespace(open=blob_open)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "artifact.zip"
            api.artifact(88, transfer.digest(body), path)
            self.assertEqual(path.read_bytes(), body)
        self.assertEqual(len(requests), 2)
        follow = transfer.DownloadRedirect().redirect_request(requests[1], None, 302, "", {}, signed)
        self.assertIsNone(follow.get_header("Authorization"))
        for url in ("http://example.blob.core.windows.net/a", "https://evil.example/a",
                    "https://blob.core.windows.net.evil.example/a", "https://user:secret@example.blob.core.windows.net/a"):
            with self.subTest(url=url), self.assertRaises(transfer.Rejected):
                transfer.download_url(url)

    def test_progress_uses_real_repository_api_and_positive_exact_delta(self):
        root = Path(__file__).resolve().parents[3]
        spec = importlib.util.spec_from_file_location("bfme_progress_contract", root / "tools/progress.py")
        # Parse the actual module instead of running a full native gate here.
        import ast
        functions = {node.name for node in ast.parse(Path(spec.origin).read_text()).body if isinstance(node, ast.FunctionDef)}
        self.assertTrue({"retail_text", "matched_at", "coverage", "naked_cpp_rows_at"} <= functions)
        publication = {"base": "base", "commit": "candidate", "progress": {"base": "base", "head": "candidate",
            "cpp_exact_before": 10, "cpp_exact_after": 15, "cpp_exact_delta": 5}}
        module = types.SimpleNamespace(retail_text=lambda: (0, 100), matched_at=lambda ref: ref,
            naked_cpp_rows_at=lambda matched, ref: (), coverage=lambda matched, start, size, naked: {"cpp": 10 if matched == "base" else 15})
        with mock.patch.object(transfer.importlib, "import_module", return_value=module):
            self.assertEqual(transfer.cpp_progress(publication), publication["progress"])
            module.coverage = lambda *args: {"cpp": 10}
            with self.assertRaises(transfer.Rejected):
                transfer.cpp_progress(publication)


class ArchiveTests(unittest.TestCase):
    def zip_path(self, entries):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path = Path(directory.name) / "fixture.zip"
        with zipfile.ZipFile(path, "w") as archive:
            for name, data, mode in entries:
                info = zipfile.ZipInfo(name)
                info.create_system = 3
                info.external_attr = mode << 16
                archive.writestr(info, data)
        return path

    def test_valid_member_is_read_without_extracting_arbitrary_paths(self):
        path = self.zip_path([("qualification-0/candidate-files/game/a.cpp", b"exact", stat.S_IFREG | 0o644)])
        archive = transfer.Archive(path)
        self.addCleanup(archive.close)
        self.assertEqual(archive.read("qualification-0/candidate-files/game/a.cpp"), b"exact")
        with self.assertRaises(transfer.Rejected):
            archive.read("qualification-0/candidate-files/game/missing.cpp")

    def test_unsafe_names_and_symlinks_are_rejected(self):
        for name in ("../outside", "/absolute", "dir\\file", "dir/a:stream", "dir/CON.cpp", "dir/trailing.",
                     "dir//a", ".git/config", "dir/../../escape"):
            with self.subTest(name=name), self.assertRaises(transfer.Rejected):
                transfer.Archive(self.zip_path([(name, b"x", stat.S_IFREG | 0o644)]))
        with self.assertRaises(transfer.Rejected):
            transfer.Archive(self.zip_path([("link", b"../../outside", stat.S_IFLNK | 0o777)]))

    def test_case_collision_and_declared_expansion_limit_are_rejected(self):
        with self.assertRaises(transfer.Rejected):
            transfer.Archive(self.zip_path([("A.cpp", b"x", stat.S_IFREG | 0o644), ("a.cpp", b"y", stat.S_IFREG | 0o644)]))
        path = self.zip_path([("large", b"12345", stat.S_IFREG | 0o644)])
        with mock.patch.object(transfer, "MAX_EXPANDED", 4), self.assertRaises(transfer.Rejected):
            transfer.Archive(path)


if __name__ == "__main__":
    unittest.main()
