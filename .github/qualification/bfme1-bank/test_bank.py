"""Bank scope and exact-object tests; no network, credentials or native probes."""

import contextlib
import copy
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import types
import unittest
from unittest import mock


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("native_attempt_bank", HERE / "bank.py")
bank = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(bank)
REPOSITORY = HERE.parents[2]
sys.path.insert(0, str(REPOSITORY / "tools"))
import name_regression


def request():
    result = json.loads((HERE / "request.json").read_bytes())
    result["enabled"] = True
    return result


def workflow():
    return {"GITHUB_REPOSITORY": bank.t.FORK, "GITHUB_SHA": "a" * 40,
            "GITHUB_RUN_ID": "77", "GITHUB_RUN_ATTEMPT": "1",
            "GITHUB_ACTOR": "McMickey93", "GITHUB_TRIGGERING_ACTOR": "McMickey93",
            "RUNNER_OS": "Windows", "ImageVersion": "fixture-image"}


def row(alternative, measured="0.87", preferred="0.95"):
    evidence = (bank.EVIDENCE + " score=" + preferred + " stash=" + bank.BANK
                + " submitted=0.893 measured=" + measured + " alternative=" + alternative)
    return ("\t".join((bank.SYMBOL, bank.RVA, "233", "partial", evidence)) + "\n").encode()


class BoundaryTests(unittest.TestCase):
    def test_disabled_request_and_scope_overrides_reject(self):
        with self.assertRaisesRegex(bank.Rejected, "disabled"):
            bank.read_request(json.dumps({**request(), "enabled": False}).encode())
        valid = request()
        self.assertEqual(bank.read_request(json.dumps(valid).encode())[0], valid)
        changes = [lambda r: r.update(enabled=False), lambda r: r.update(destination="refs/heads/master"),
                   lambda r: r["support_files"][0].update(blob="b" * 40),
                   lambda r: r["support_files"].append(r["support_files"][0]),
                   lambda r: r["identity_correction"]["evidence"].update(path="docs/other.md"),
                   lambda r: r["identity_correction"].update(reason="arbitrary override"),
                   lambda r: r["claims"][0].update(owner="github:someone:bfme1:test"),
                   lambda r: r["claims"][0].update(lease=42),
                   lambda r: r["base_rows"][0].update(target_rva="0x008C6AD1")]
        for change in changes:
            with self.subTest(change=change), self.assertRaises(bank.Rejected):
                changed = copy.deepcopy(valid)
                change(changed)
                bank.read_request(json.dumps(changed).encode())

    def test_log_is_one_append_only_partial_for_fixed_body(self):
        before = b"historical\trow\n"
        addition = row(bank.HISTORY + "b" * 64 + ".json")
        bank.validate_append(before, before + addition)
        alternatives = [addition, before + addition * 2, before + addition.replace(b"\n", b"\r\n"),
                        before + addition.replace(b"\tpartial\t", b"\tlanded\t"),
                        before + addition.replace(b"\t233\t", b"\t234\t"),
                        before + addition.replace(b"measured=0.87 ", b"measured=0.87junk "),
                        before + addition.replace(b"measured=0.87 ", b"measured=0.87 measured=0.87 "),
                        before + addition.replace(bank.BANK.encode(), b"targets/game/reverse/attempts/other.cpp")]
        for after in alternatives:
            with self.subTest(after=after[-120:]), self.assertRaises(bank.Rejected):
                bank.validate_append(before, after)

    def test_only_fixed_run_actor_and_workflow_are_accepted(self):
        env = {**workflow(), "GITHUB_REF": "refs/heads/master", "GITHUB_EVENT_NAME": "workflow_dispatch"}
        self.assertEqual(bank.context(env), workflow())
        for change in ({"GITHUB_ACTOR": "another", "GITHUB_TRIGGERING_ACTOR": "another"},
                       {"RUNNER_OS": "Linux"}, {"GITHUB_EVENT_NAME": "pull_request"},
                       {"GITHUB_REPOSITORY": bank.t.OFFICIAL}):
            with self.subTest(change=change), self.assertRaises(bank.Rejected):
                bank.context({**env, **change})
        metadata = {"id": 77, "run_attempt": 1, "head_sha": env["GITHUB_SHA"], "path": bank.WORKFLOW,
                    "event": "workflow_dispatch", "head_branch": "master",
                    "repository": {"full_name": bank.t.FORK, "fork": True, "private": False},
                    "head_repository": {"full_name": bank.t.FORK}, "actor": {"login": "McMickey93"},
                    "triggering_actor": {"login": "McMickey93"}}
        api = types.SimpleNamespace(json=mock.Mock(return_value=metadata))
        bank.check_run(api, workflow())
        for key, value in (("run_attempt", 2), ("path", bank.t.WORKFLOW), ("head_sha", "b" * 40)):
            with self.subTest(key=key), self.assertRaises(bank.Rejected):
                api.json.return_value = {**metadata, key: value}
                bank.check_run(api, workflow())

    def test_fixed_destination_uses_empty_lease_and_ordinary_push(self):
        commit = "b" * 40
        ref = bank.target_ref(workflow(), commit)
        self.assertEqual(ref, "refs/heads/banked/bfme1-008c6ad0-77-1-" + commit)
        self.assertEqual(bank.push_command(workflow(), commit),
                         ["git", "push", "--porcelain", "--force-with-lease=" + ref + ":",
                          bank.t.FORK_URL, commit + ":" + ref])
        runner = types.SimpleNamespace(git=mock.Mock(return_value=b""))
        self.assertFalse(bank.existing_ref(runner, workflow(), commit))
        runner.git.return_value = (commit + "\t" + ref + "\n").encode()
        self.assertTrue(bank.existing_ref(runner, workflow(), commit))
        runner.git.return_value = ("c" * 40 + "\t" + ref + "\n").encode()
        with self.assertRaises(bank.Rejected):
            bank.existing_ref(runner, workflow(), commit)

    def test_unavailable_native_measurement_cannot_reach_staging_or_publication(self):
        runner = types.SimpleNamespace(run=mock.Mock(), git=mock.Mock(), source=Path("unused"))
        def run(label, argv, **kwargs):
            if label == "unmodified-native-re-log":
                self.assertEqual(argv, [sys.executable, "tools/re_log.py", "record", bank.SYMBOL,
                                       bank.RVA, "233", "partial", bank.EVIDENCE,
                                       "--stash", bank.BEST, "--score", "0.893"])
                raise bank.Rejected("measurement unavailable")
        runner.run.side_effect = run
        with mock.patch.object(bank, "initial_checkout"), mock.patch.object(bank, "check_run"), \
             mock.patch.object(bank, "prepare_native", return_value="bash"), \
             mock.patch.object(bank, "current_claims"), mock.patch.object(bank, "changed_paths") as paths, \
             mock.patch.object(bank, "publication_for") as publication:
            with self.assertRaisesRegex(bank.Rejected, "measurement unavailable"):
                bank.bank_job(runner, object(), request(), "c" * 64, workflow())
        paths.assert_not_called()
        publication.assert_not_called()
        self.assertEqual([call.args[1] for call in runner.git.call_args_list], ["switch"])

    def test_native_environment_overrides_reject_before_any_command(self):
        runner = types.SimpleNamespace(run=mock.Mock())
        for name in ("CL", "_CL_", "BUILD_RECOMPILE_ONLY", "MSYS_NO_PATHCONV", "MSYS2_ARG_CONV_EXCL"):
            with self.subTest(name=name), mock.patch.dict(bank.os.environ, {name: "1"}, clear=True):
                with self.assertRaisesRegex(bank.Rejected, "environment override: " + name):
                    bank.prepare_native(runner)
                self.assertEqual(bank.os.environ[name], "1", "Override must be rejected, not silently cleared")
        runner.run.assert_not_called()


class GitResultTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.source = self.root / "source"
        self.source.mkdir()
        self.git("init", "-q")
        self.git("config", "user.name", "Fixture")
        self.git("config", "user.email", "fixture@example.invalid")
        self.git("config", "core.autocrlf", "false")
        self.old = b"// old symbol\n// partial score=0.92 date=2026-10-01\nint old_body() { return 1; }\n"
        self.incoming = b"int new_body() { return 2; }\n"
        self.write(bank.BANK, self.old)
        self.write(bank.BEST, self.incoming)
        self.write(bank.LOG, b"historical\trow\n")
        # Copy the unchanged parser into the temporary repository so its ROOT
        # resolves here. No canonical repository log or bank is redirected.
        self.write("tools/re_log.py", (REPOSITORY / "tools/re_log.py").read_bytes())
        self.git("add", bank.BANK, bank.BEST, bank.LOG, "tools/re_log.py")
        self.git("commit", "-qm", "fixture base")
        self.base = self.git("rev-parse", "HEAD").decode().strip()
        self.git("branch", "fixture-base", self.base)
        self.request = request()
        self.request.update(expected_base=self.base,
                            previous_bank_blob=self.git("rev-parse", "HEAD:" + bank.BANK).decode().strip())
        candidate = ("// " + bank.SYMBOL + "\n// partial score=0.87 date=2026-10-25\n").encode() + self.incoming
        self.old_history = self.archive(self.old, 0.92, "author-estimate")
        self.alternative = self.archive(candidate, 0.87, "measured")
        self.write(bank.BANK, self.old.replace(b"score=0.92", b"score=0.95"))
        self.write(bank.LOG, b"historical\trow\n" + row(self.alternative))
        self.paths = [bank.BANK, bank.LOG, self.old_history, self.alternative]
        self.git("add", *self.paths)
        self.message = "Bank fixture\n\n" + "".join(
            "Claim-Lease: %s=%s\n" % (c["rva"], c["lease"]) for c in self.request["claims"])
        self.git("commit", "-qm", self.message)
        self.commit = self.git("rev-parse", "HEAD").decode().strip()
        self.raw = self.git("cat-file", "commit", self.commit)
        self.publication = {"kind": "native-attempt-bank", "repository": bank.t.OFFICIAL, "published": False,
                            "base": self.base, "commit": self.commit,
                            "tree": self.git("rev-parse", "HEAD^{tree}").decode().strip(),
                            "message": self.raw.split(b"\n\n", 1)[1].decode(), "workflow": workflow(),
                            "claims": self.request["claims"], "native_re_log_passed": True,
                            "normal_commit_passed": True, "full_normal_pre_push_passed": True,
                            "progress": {"base": self.base, "head": self.commit, "cpp_exact_before": 10,
                                         "cpp_exact_after": 10, "cpp_exact_delta": 0},
                            "files": [self.entry(path) for path in self.paths]}
        self.runner = bank.Runner(self.source)
        spec = importlib.util.spec_from_file_location("fixture_bank_parser", self.source / "tools/re_log.py")
        self.parser = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.parser)

    def git(self, *args, cwd=None):
        result = subprocess.run(["git", *args], cwd=cwd or self.source, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr.decode(errors="replace"))
        return result.stdout

    def write(self, path, raw):
        destination = self.source / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(raw)

    def archive(self, raw, score, kind):
        sha = bank.t.digest(raw)
        path = bank.HISTORY + sha + ".json"
        self.write(path, json.dumps({"schema": 1, "sha256": sha, "symbol": raw.splitlines()[0].decode()[3:],
                                    "score_kind": kind, "score": score, "source": raw.decode()}).encode())
        return path

    def entry(self, path):
        raw = (self.source / path).read_bytes()
        return {"path": path, "mode": "100644", "size": len(raw), "sha256": bank.t.digest(raw),
                "blob": self.git("rev-parse", "HEAD:" + path).decode().strip()}

    def validate_contents(self):
        with mock.patch.object(bank.importlib, "import_module", return_value=self.parser), \
             contextlib.redirect_stdout(io.StringIO()):
            return bank.validate_result_contents(self.runner, self.base, self.commit, self.request)

    def test_existing_better_bank_and_measured_alternative_are_preserved(self):
        result = self.validate_contents()
        self.assertEqual(result["incoming_measured_score"], 0.87)
        self.assertEqual(result["preferred_score"], 0.95)
        self.assertEqual(result["alternative"], self.alternative)
        self.assertEqual(self.parser._source_body((self.source / bank.BANK).read_bytes()),
                         self.parser._source_body(self.old))
        old_record = json.loads((self.source / self.old_history).read_bytes())
        self.assertEqual(old_record["source"].encode(), self.old)

    def test_unrelated_body_false_score_or_corrupt_history_are_rejected(self):
        path = self.source / bank.BANK
        original = path.read_bytes()
        for replacement in (original.replace(b"int old_body", b"int other_body"),
                            original.replace(b"score=0.95", b"score=0.96")):
            path.write_bytes(replacement)
            with self.assertRaises(bank.Rejected):
                self.validate_contents()
        path.write_bytes(original)
        path = self.source / self.alternative
        item = json.loads(path.read_bytes())
        path.write_text(json.dumps({**item, "score_kind": "author-estimate"}))
        with self.assertRaises(bank.Rejected):
            self.validate_contents()

    def test_incoming_preferred_bank_must_use_its_actual_measured_score(self):
        item = json.loads((self.source / self.alternative).read_bytes())
        self.write(bank.BANK, item["source"].encode())
        self.write(bank.LOG, b"historical\trow\n" + row(self.alternative, preferred="0.87"))
        self.assertEqual(self.validate_contents()["preferred_score"], 0.87)
        self.write(bank.BANK, item["source"].encode().replace(b"score=0.87", b"score=0.95"))
        self.write(bank.LOG, b"historical\trow\n" + row(self.alternative, preferred="0.95"))
        with self.assertRaisesRegex(bank.Rejected, "contradicts"):
            self.validate_contents()

    def test_scope_modes_gate_claim_and_progress_tamper_reject(self):
        bank.validate_publication(self.publication, self.request, workflow())
        mutations = [lambda p: p.update(full_normal_pre_push_passed=False),
                     lambda p: p["progress"].update(cpp_exact_after=11, cpp_exact_delta=1),
                     lambda p: p["files"][0].update(path=bank.GAME_SOURCE),
                     lambda p: p["files"][0].update(path=bank.t.LEDGER),
                     lambda p: p["files"][0].update(path="tools/re_log.py"),
                     lambda p: p["files"][0].update(mode="120000"),
                     lambda p: p.update(message="Claim-Lease: wrong\n"),
                     lambda p: p["workflow"].update(GITHUB_RUN_ATTEMPT="2")]
        for change in mutations:
            with self.subTest(change=change), self.assertRaises(bank.Rejected):
                publication = copy.deepcopy(self.publication)
                change(publication)
                bank.validate_publication(publication, self.request, workflow())

    def test_exact_bundle_roundtrip_retains_raw_commit_and_all_bank_bytes(self):
        self.git("branch", bank.LOCAL_REF.removeprefix("refs/heads/"), self.commit)
        bundle = self.root / "candidate.bundle"
        self.git("bundle", "create", "--version=2", str(bundle), self.base + ".." + bank.LOCAL_REF)
        raw = bundle.read_bytes()
        bank.validate_bundle(raw, self.publication)
        for altered in (raw.replace(bank.LOCAL_REF.encode(), b"refs/heads/master", 1),
                        raw.replace(b"\n\n", b"\n" + self.base.encode() + b" refs/heads/extra\n\n", 1)):
            with self.assertRaises(bank.Rejected):
                bank.validate_bundle(altered, self.publication)
        destination = self.root / "destination"
        self.git("clone", "-q", "--no-local", "--single-branch", "--branch", "fixture-base",
                 str(self.source), str(destination))
        absent = subprocess.run(["git", "cat-file", "-e", self.commit], cwd=destination, capture_output=True)
        self.assertNotEqual(absent.returncode, 0, "Fixture must not already contain the transferred commit")
        self.git("bundle", "verify", str(bundle), cwd=destination)
        self.git("fetch", "--no-tags", "--no-write-fetch-head", "--recurse-submodules=no",
                 str(bundle), bank.LOCAL_REF, cwd=destination)
        imported = bank.Runner(destination)
        with contextlib.redirect_stdout(io.StringIO()):
            bank.t.validate_objects(imported, self.publication)
        self.assertEqual(self.git("cat-file", "commit", self.commit, cwd=destination), self.raw)
        for entry in self.publication["files"]:
            self.assertEqual(self.git("show", self.commit + ":" + entry["path"], cwd=destination),
                             (self.source / entry["path"]).read_bytes())

    def test_diagnostics_preserve_actual_output_before_later_gate_refusal(self):
        with contextlib.redirect_stdout(io.StringIO()):
            bank.retain_native_outputs(self.runner, self.base, self.paths)
            with self.assertRaisesRegex(bank.Rejected, "fixture-gate-refusal"):
                self.runner.run("fixture-gate-refusal", [sys.executable, "-c", "raise SystemExit(7)"], log=True)
        output = self.runner.evidence / "native-output"
        self.assertEqual((output / "before-bank.cpp").read_bytes(), self.old)
        self.assertEqual((output / "after-bank.cpp").read_bytes(), (self.source / bank.BANK).read_bytes())
        self.assertEqual((output / "appended-verdict.log").read_bytes(), row(self.alternative))
        for path in (self.old_history, self.alternative):
            self.assertEqual((output / "history" / Path(path).name).read_bytes(), (self.source / path).read_bytes())
        manifest = json.loads((output / "manifest.json").read_bytes())
        self.assertEqual(manifest["base"], self.base)
        for entry in manifest["files"]:
            raw = (output / entry["path"]).read_bytes()
            self.assertEqual((len(raw), bank.t.digest(raw)), (entry["size"], entry["sha256"]))
        self.assertFalse((self.root / "banked-attempt").exists())

    def test_diagnostics_reject_extra_scope_and_oversized_native_output(self):
        with self.assertRaisesRegex(bank.Rejected, "scope"):
            bank.retain_native_outputs(self.runner, self.base, self.paths + ["tools/re_log.py"])
        self.write(bank.BANK, b"x" * (bank.DIAGNOSTIC_MEMBER_LIMIT + 1))
        with contextlib.redirect_stdout(io.StringIO()), self.assertRaisesRegex(bank.Rejected, "diagnostic file"):
            bank.retain_native_outputs(self.runner, self.base, self.paths)


class IdentityCorrectionTests(unittest.TestCase):
    """Use the unmodified canonical name checker on real staged Git snapshots."""
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.source = self.root / "source"
        self.source.mkdir()
        self.git("init", "-q")
        self.git("config", "user.name", "Fixture")
        self.git("config", "user.email", "fixture@example.invalid")
        self.git("config", "core.autocrlf", "false")
        self.registry = b'[\r\n {"prior": "first"},\n {"prior": "second"}\r\n]\r\n'
        self.old = (b"// fixture symbol\n// partial score=0.833 date=2026-09-26\n"
                    b"extern int g_bfmeCount1233;\nextern int gOtherCount;\n"
                    b"int count() { return g_bfmeCount1233 + gOtherCount; }\n")
        self.after = self.old.replace(b"g_bfmeCount1233", b"Rva008AE770TheStack").replace(
            b"score=0.833 date=2026-09-26", b"score=0.8952 date=2026-10-25")
        self.write(bank.BANK, self.old)
        self.write(bank.CORRECTIONS, self.registry)
        self.write(bank.IDENTITY_EVIDENCE, b"Pinned independent stack identity evidence.\n")
        self.git("add", bank.BANK, bank.CORRECTIONS, bank.IDENTITY_EVIDENCE)
        self.git("commit", "-qm", "identity fixture base")
        self.base = self.git("rev-parse", "HEAD").decode().strip()
        self.request = request()
        self.request.update(expected_base=self.base,
                            previous_bank_blob=self.git("rev-parse", self.base + ":" + bank.BANK).decode().strip())
        for key, path in (("registry", bank.CORRECTIONS), ("evidence", bank.IDENTITY_EVIDENCE)):
            raw = (self.source / path).read_bytes()
            self.request["identity_correction"][key] = {
                "path": path, "blob": self.git("rev-parse", self.base + ":" + path).decode().strip(),
                "size": len(raw), "sha256": bank.t.digest(raw)}
        self.runner = bank.Runner(self.source)
        self.write(bank.BANK, self.after)
        self.git("add", bank.BANK)

    def git(self, *args):
        result = subprocess.run(["git", *args], cwd=self.source, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr.decode(errors="replace"))
        return result.stdout

    def write(self, path, raw):
        destination = self.source / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(raw)

    def document(self):
        with contextlib.redirect_stdout(io.StringIO()):
            return bank.document_identity_correction(self.runner, self.base, self.request)

    def validate(self, ref=":"):
        with contextlib.redirect_stdout(io.StringIO()):
            return bank.validate_identity_correction(self.runner, self.base, ref, self.request)

    def test_fixed_correction_preserves_registry_and_hashes_complete_tool_snapshots(self):
        before, accepted = name_regression.check(self.source, self.base, ":")
        self.assertEqual(len(before), 1)
        self.assertEqual(accepted, 0)
        result = self.document()
        entry = result["entry"]
        self.assertEqual(entry["before_sha256"], bank.t.digest(self.old))
        self.assertEqual(entry["after_sha256"], bank.t.digest(self.after))
        self.assertEqual((entry["old_name"], entry["new_name"]), (bank.OLD_NAME, bank.NEW_NAME))
        actual = (self.source / bank.CORRECTIONS).read_bytes()
        prefix, suffix = self.registry.rsplit(b"}\r\n]", 1)
        self.assertTrue(actual.startswith(prefix + b"},\r\n"))
        self.assertTrue(actual.endswith(b"}\r\n]" + suffix))
        self.assertEqual(json.loads(actual), json.loads(self.registry) + [entry])
        self.assertEqual(name_regression.check(self.source, self.base, ":"), ([], 1))
        self.git("commit", "-qm", "fixture exact snapshot correction")
        commit = self.git("rev-parse", "HEAD").decode().strip()
        self.assertEqual(self.validate(commit), result, "Import validation must repeat the same exact snapshot check")

    def test_zero_findings_leaves_the_entire_registry_unchanged(self):
        self.write(bank.BANK, self.old.replace(b"score=0.833", b"score=0.8952"))
        self.git("add", bank.BANK)
        self.assertIsNone(self.document())
        self.assertIsNone(self.validate())
        self.assertEqual((self.source / bank.CORRECTIONS).read_bytes(), self.registry)

    def test_other_or_additional_findings_cannot_write_a_correction(self):
        for changed in (self.after.replace(b"Rva008AE770TheStack", b"Rva00123456Other"),
                        self.after.replace(b"gOtherCount", b"Rva00123456Other")):
            with self.subTest(changed=changed):
                self.write(bank.BANK, changed)
                self.git("add", bank.BANK)
                with self.assertRaisesRegex(bank.Rejected, "different or additional"):
                    self.document()
                self.assertEqual((self.source / bank.CORRECTIONS).read_bytes(), self.registry)

    def test_changed_header_line_endings_or_registry_delta_reject_on_revalidation(self):
        self.document()
        registry = (self.source / bank.CORRECTIONS).read_bytes()
        for changed in (self.after.replace(b"0.8952", b"0.8953"),
                        self.after.replace(b"2026-10-25", b"2026-10-26"),
                        self.after.replace(b"\n", b"\r\n")):
            with self.subTest(changed=changed[-80:]):
                self.write(bank.BANK, changed)
                self.git("add", bank.BANK)
                with self.assertRaisesRegex(bank.Rejected, "Registry delta"):
                    self.validate()
        self.write(bank.BANK, self.after)
        self.git("add", bank.BANK)
        mutations = [registry.replace(b'"first"', b'"changed"'),
                     registry.replace(bank.CORRECTION_REASON.encode(), b"unreviewed reason"),
                     json.dumps(json.loads(registry)).encode()]
        for changed in mutations:
            with self.subTest(changed=changed[:100]):
                self.write(bank.CORRECTIONS, changed)
                self.git("add", bank.CORRECTIONS)
                self.git("commit", "-qm", "fixture invalid imported registry")
                with self.assertRaisesRegex(bank.Rejected, "Registry delta"):
                    self.validate("HEAD")

    def test_registry_preimage_and_committed_evidence_are_required(self):
        original = copy.deepcopy(self.request)
        for key in ("registry", "evidence"):
            with self.subTest(key=key):
                self.request = copy.deepcopy(original)
                self.request["identity_correction"][key]["sha256"] = "0" * 64
                with self.assertRaisesRegex(bank.Rejected, "Qualified file"):
                    self.document()
        self.request = original
        self.write(bank.IDENTITY_EVIDENCE, b"changed evidence\n")
        self.git("add", bank.IDENTITY_EVIDENCE)
        with self.assertRaisesRegex(bank.Rejected, "evidence changed"):
            self.document()


if __name__ == "__main__":
    unittest.main()
