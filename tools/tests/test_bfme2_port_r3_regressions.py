"""Round 3 adversarial regressions, synthetic artifacts and temporary keys only.

Reviewer reproduction names are preserved; PASS now asserts the fix.
The imported snapshot fixture removes cycle() before any subprocess execution.
No compiler, linker, census, Wine, real cycle, or host key configuration writes.
"""
import importlib.util
import json
from pathlib import Path
import shutil
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import cycle_artifacts as ca
import cycle_diff as cd
import cycle_launch as launch
import cycle_source
import cycle_stamp as stamp
import link_cycle_context as ctx
import repair_queue as rq
from cycle_fixture import NOW, save_receipt
from test_bfme2_port_r1_regressions import (
    checkout, freeze, git, run_for, synthetic_snapshot_checkout,
)
from test_bfme2_port_r2_regressions import commit_fixture, failed_run


@pytest.mark.parametrize("formatting", ["compact", "crlf"])
def test_defect_stamp_upgrade_compares_json_not_signed_bytes(checkout, tmp_path, formatting):
    root, _ = checkout
    run, _ = failed_run(checkout, tmp_path / "run")
    good = freeze(run, tmp_path / "signed", root)
    unsigned = tmp_path / "unsigned"
    shutil.copytree(good, unsigned)
    (unsigned / stamp.STAMP).unlink()
    manifest = unsigned / ca.MANIFEST
    if formatting == "compact":
        manifest.write_text(json.dumps(ca.read_manifest(unsigned), separators=(",", ":")))
    else:
        manifest.write_bytes(manifest.read_bytes().replace(b"\n", b"\r\n"))
    assert ca.validate(unsigned, root=root) == ca.validate(good, root=root)
    assert manifest.read_bytes() != (good / ca.MANIFEST).read_bytes()
    assert ca.serve(good, root=root, now=NOW)[1]["authoritative"]
    store = tmp_path / "store"
    ca.install_local(unsigned, store, root=root, now=NOW)
    installed = ca.resolve(store, root=root, now=NOW)[0]
    original_payload = {p.name: p.read_bytes() for p in installed.iterdir()}
    assert installed.parent.name == ca.variant_id(ca.read_manifest(unsigned)["tag"], ca.sha256_file(manifest))
    with pytest.raises(ca.BundleError, match="stamp manifest bytes"):
        ca.attach_verified_stamp(good, installed)
    ca.install_local(good, store, root=root, now=NOW)
    assert all((installed / name).read_bytes() == raw for name, raw in original_payload.items())
    assert stamp.verify(installed) == "unstamped"
    selected = ca.resolve(store, root=root, now=NOW)[0]
    assert selected != installed and stamp.verify(selected) is None
    assert (selected / ca.MANIFEST).read_bytes() == (good / ca.MANIFEST).read_bytes()
    for closure in (False, True):
        result = rq.route_link_queue(store, closure=closure, now=NOW)
        assert result["status"] == "ok" and result["authoritative"]


@pytest.mark.parametrize("provider", ["build", "gen_case_shims"])
def test_defect_source_package_overrides_hashed_module(checkout, tmp_path, provider):
    root, _ = synthetic_snapshot_checkout(checkout)
    driver = root / "tools/link_cycle.py"
    source = driver.read_text()
    probe = ('context.current_object(ROOT / "game/absent.cpp", ROOT / "build/absent.obj")'
             if provider == "build" else '(ROOT / "helper-package-executed").exists()')
    source = source.replace('    receipt["synthetic_execution"] = ',
                            '    receipt["alternate_provider_verdict"] = ' + probe + '\n'
                            f'    receipt["alternate_provider_path"] = sys.modules["{provider}"].__file__\n'
                            '    receipt["synthetic_execution"] = ')
    driver.write_text(source)
    commit_fixture(root, "inert source-package probe")
    before = ca.local_rules(root)
    assert ctx.current_object(root / "game/absent.cpp", root / "build/absent.obj") is False
    package = root / "tools" / provider
    package.mkdir()
    if provider == "build":
        replacement = (root / "tools/build.py").read_text().replace(
            'ROOT = Path(__file__).resolve().parents[1]',
            'ROOT = Path(__file__).resolve().parents[2]')
        replacement += '\ndef compile_is_current(*args, **kwargs):\n    return True\n'
    else:
        replacement = ('from pathlib import Path\n'
                       'def ensure_case_shims(*args, **kwargs):\n'
                       '    (Path(__file__).resolve().parents[2] / "helper-package-executed").write_text("yes")\n')
    (package / "__init__.py").write_text(replacement)
    commit_fixture(root, "alternate package shadows declared semantic provider")
    assert ca.local_rules(root) == before
    assert f"{provider}/__init__.py" in ca.local_dependencies(root)
    cycle_source.reject_bytecode(root)
    out = tmp_path / "launched"
    # The real launcher's preflight must refuse the committed package before
    # executing any snapshot provider or helper, and must never emit a stamp.
    with pytest.raises(ValueError, match="package shadows declared module"):
        launch.measure(out, "R3 inert package probe", root=root, key=stamp.configured_keys()[0])
    assert not out.exists()
    assert not (root / "helper-package-executed").exists()


@pytest.mark.parametrize("variant", ["producer", "missing-provenance"])
def test_defect_unsigned_manifest_variant_reserves_receipt_id(checkout, tmp_path, variant):
    root, _ = checkout
    run, _ = failed_run(checkout, tmp_path / "run")
    good = freeze(run, tmp_path / "signed", root)
    unsigned = tmp_path / "unsigned"
    shutil.copytree(good, unsigned)
    (unsigned / stamp.STAMP).unlink()
    doc = ca.read_manifest(unsigned)
    if variant == "producer":
        doc["producer"] = "ordinary diagnostic producer"
    else:
        (unsigned / ca.PROVENANCE).unlink()
        del doc["members"][ca.PROVENANCE]
    (unsigned / ca.MANIFEST).write_text(ca.dumps(doc))
    ca.validate(unsigned, root=root)
    assert ca.bundle_id(doc["tag"]) == ca.bundle_id(ca.read_manifest(good)["tag"])
    store = tmp_path / "store"
    ca.install_local(unsigned, store, root=root, now=NOW)
    diagnostic = ca.resolve(store, root=root, now=NOW)[0]
    before = {p.name: (p.read_bytes(), p.stat().st_ino) for p in diagnostic.iterdir()}
    ca.install_local(good, store, root=root, now=NOW)
    assert {p.name: (p.read_bytes(), p.stat().st_ino) for p in diagnostic.iterdir()} == before
    assert stamp.verify(diagnostic) == "unstamped"
    for closure in (False, True):
        result = rq.route_link_queue(store, closure=closure, now=NOW)
        assert result["status"] == "ok" and result["authoritative"]


def test_sound_stamp_cannot_move_between_different_payloads(checkout, tmp_path):
    root, _ = checkout
    first, _ = failed_run(checkout, tmp_path / "first-run")
    second, _ = run_for(checkout, tmp_path / "second-run", now=NOW + 1)
    old = freeze(first, tmp_path / "old", root)
    new = freeze(second, tmp_path / "new", root, sign=False)
    shutil.copyfile(old / stamp.STAMP, new / stamp.STAMP)
    assert stamp.verify(new) == "bad-stamp"
    with pytest.raises(ca.Refused) as error:
        ca.serve(new, root=root, now=NOW + 1)
    assert error.value.sub_reason == "bad-stamp"


@pytest.mark.parametrize("signed", [False, True])
def test_sound_rule_incompatibility_is_not_hidden(checkout, tmp_path, signed):
    root, _ = checkout
    run, receipt = failed_run(checkout, tmp_path / "run")
    receipt["tool_dependencies"]["build.py"] = "f" * 64
    receipt["tool_digest"] = ctx.digest(receipt["tool_dependencies"])
    receipt["rule_identity"] = ctx.rule_identity(receipt["tool_dependencies"])
    save_receipt(run, receipt)
    out = freeze(run, tmp_path / "out", root, sign=signed)
    store = tmp_path / "store"
    ca.install_local(out, store, root=root, now=NOW)
    for path in (out, store):
        result = rq.route_link_queue(path, closure=True, now=NOW)
        assert result["reason"] == "incompatible-rules"
        assert result["route"] == "tooling seat / human review"


@pytest.mark.parametrize("failure", ["stale", "future", "ancestry-unknown", "dirty"])
def test_sound_diff_labels_refused_signed_inputs_diagnostic(checkout, tmp_path, monkeypatch, failure):
    root, _ = checkout
    old_run, old_receipt = failed_run(checkout, tmp_path / "old-run")
    new_run, _ = run_for(checkout, tmp_path / "new-run", now=NOW + 1)
    if failure == "dirty":
        old_receipt["run_options"]["allow_dirty"] = True
        save_receipt(old_run, old_receipt)
    old = freeze(old_run, tmp_path / "old", root)
    new = freeze(new_run, tmp_path / "new", root)
    if failure == "ancestry-unknown":
        git(root, "update-ref", "-d", "refs/remotes/origin/master")
    monkeypatch.setattr(ca, "ROOT", root)
    now = NOW + 86402 if failure == "stale" else NOW - 601 if failure == "future" else NOW + 1
    monkeypatch.setattr(ca.time, "time", lambda: now)
    doc = cd.cli_compare(old, new)
    assert doc["consistent"] and doc["diagnostic"] and not doc["authoritative"]
    assert doc["totals"]["gained"] == 10
    assert not doc["input_authority"]["old"]["authoritative"]
    cd.check_report(doc)


@pytest.mark.parametrize("newer_count", [ca.CLOSURE_LOOKBACK, ca.CLOSURE_LOOKBACK + 1])
def test_sound_signed_incompatible_history_still_consumes_lookback(checkout, tmp_path, newer_count):
    root, _ = checkout
    run, _ = failed_run(checkout, tmp_path / "good-run")
    good = freeze(run, tmp_path / "good", root)
    store = tmp_path / "store"
    ca.install_local(good, store, root=root, now=NOW)
    provider = root / "tools/build.py"
    original = provider.read_bytes()
    provider.write_bytes(original + b"\n# legitimate later rule implementation\n")
    later_commit = commit_fixture(root, "later semantic rules")
    for index in range(newer_count):
        run, _ = failed_run((root, later_commit), tmp_path / f"later-run-{index}", now=NOW + index + 1)
        out = freeze(run, tmp_path / f"later-{index}", root)
        ca.install_local(out, store, root=root, now=NOW + newer_count)
    # A reader on the older semantic rules, with both actual commits available.
    provider.write_bytes(original)
    entries = ca.installed(store, root=root, now=NOW + newer_count)
    assert all(entry["execution_eligible"] for entry in entries)
    assert sum(entry["authoritative"] for entry in entries) == 1
    result = rq.route_link_queue(store, closure=True, now=NOW + newer_count)
    if newer_count == ca.CLOSURE_LOOKBACK:
        assert result["status"] == "ok" and result["authoritative"]
    else:
        assert result["status"] == "refused" and result["reason"] == "incompatible-rules"
    assert rq.route_link_queue(store, now=NOW + newer_count)["status"] == "ok"


def test_sound_windows_profile_lookup_failure_has_no_environment_fallback(tmp_path, monkeypatch):
    import builtins
    import ctypes
    import types
    monkeypatch.setattr(ctypes, "windll", types.SimpleNamespace(shell32=types.SimpleNamespace(
        SHGetFolderPathW=lambda *args: -2147467259)), raising=False)
    original_import = builtins.__import__
    def no_pwd(name, *args, **kwargs):
        if name == "pwd":
            raise ImportError("Windows has no pwd")
        return original_import(name, *args, **kwargs)
    monkeypatch.setattr(builtins, "__import__", no_pwd)
    for name in ("HOME", "USERPROFILE", "XDG_CONFIG_HOME", "BFME_CYCLE_KEYS"):
        monkeypatch.setenv(name, str(tmp_path / "worker-controlled"))
    spec = importlib.util.spec_from_file_location("r3_windows_stamp", stamp.__file__)
    module = importlib.util.module_from_spec(spec)
    with pytest.raises(OSError, match="cannot resolve the account profile"):
        spec.loader.exec_module(module)


def test_executed_module_set_covers_bootstrap_measurement_and_helper(checkout, tmp_path, monkeypatch):
    root, _ = synthetic_snapshot_checkout(checkout)
    observed = []
    original = cycle_source.audit_modules

    def collect(directory, **kwargs):
        if not kwargs.get("runtime"):
            observed.extend(json.loads(p.read_bytes()) for p in Path(directory).glob("*.json"))
        return original(directory, **kwargs)

    monkeypatch.setattr(cycle_source, "audit_modules", collect)
    out = tmp_path / "launched"
    launch.measure(out, "R3 executed modules", root=root, key=stamp.configured_keys()[0])
    bundle, fr, _ = ca.serve(out, root=root, now=NOW)
    assert fr["authoritative"]
    declared = bundle.receipt["rule_identity"]["measurement_files"]
    expected = {name: {"origin": "tools/" + name, "sha256": ca.sha256_file(root / "tools" / name)}
                for name in declared}
    assert bundle.receipt["executed_modules"] == expected
    assert "capstone" in bundle.receipt["runtime_modules"]
    assert any(v["origin"].endswith((".so", ".pyd")) for v in bundle.receipt["runtime_modules"].values())
    assert len(observed) == 3  # seed bootstrap, shim helper, measurement process
    assert all(p["complete"] and p["modules"] == expected for p in observed)
    assert sum("/seed/tools" in p["tools"] for p in observed) == 1
    assert sum("/s/" in p["tools"] for p in observed) == 2


@pytest.mark.parametrize("variant", ["absent", "missing", "unexpected", "package", "outside", "digest"])
def test_signed_receipt_requires_exact_executed_module_set(checkout, tmp_path, variant):
    root, _ = checkout
    run, receipt = failed_run(checkout, tmp_path / "run")
    executed = receipt["executed_modules"]
    if variant == "absent":
        del receipt["executed_modules"]
    elif variant == "missing":
        del executed["build.py"]
    elif variant == "unexpected":
        executed["unexpected.py"] = {"origin": "tools/unexpected.py", "sha256": "0" * 64}
    elif variant == "package":
        executed["build.py"]["origin"] = "tools/build/__init__.py"
    elif variant == "outside":
        executed["build.py"]["origin"] = str(tmp_path / "outside/build.py")
    else:
        executed["build.py"]["sha256"] = "0" * 64
    save_receipt(run, receipt)
    out = freeze(run, tmp_path / "signed", root)
    assert stamp.verify(out) is None  # Even a signature cannot repair missing execution evidence.
    assert ("executed_modules" in ca.read_manifest(out)["binding"]) == (variant != "absent")
    ca.validate(out, root=root)  # Missing historical evidence is diagnostic, not corrupt.
    for closure in (False, True):
        result = rq.route_link_queue(out, closure=closure, now=NOW)
        assert result["status"] == "refused"
        assert result["sub_reason"] == "executed-module-mismatch"


@pytest.mark.parametrize("origin", ["package", "namespace", "outside", "outside-tools", "direct-package", "direct-native", "unexpected"])
def test_loader_refuses_noncanonical_origins_before_module_body(tmp_path, origin):
    import os
    import subprocess
    tools = tmp_path / "snapshot/tools"
    tools.mkdir(parents=True)
    shutil.copyfile(cycle_source.__file__, tools / "cycle_source.py")
    (tools / "link_cycle_context.py").write_text(
        "MEASUREMENT_FILES = ('cycle_source.py', 'link_cycle_context.py', 'probe.py')\n")
    (tools / "probe.py").write_text("value = False\n")
    audit = tmp_path / "audit"
    audit.mkdir()
    marker = tmp_path / "executed"
    body = f"from pathlib import Path\nPath({str(marker)!r}).write_text('executed')\n"
    # Add the alternate source only after the declared closure was preloaded.
    # Both the normal finder and spec_from_file_location must fail before exec.
    setup = "import sys, importlib.util\nsys.modules.pop('probe', None)\n"
    if origin in ("package", "direct-package"):
        path = tools / "probe/__init__.py"
        setup += "(tools / 'probe').mkdir()\n"
    elif origin == "namespace":
        path = None
        setup += "(tools / 'unlisted').mkdir()\nimport unlisted\n"
    elif origin == "outside":
        path = tmp_path / "outside/probe.py"
        setup += f"Path({str(path.parent)!r}).mkdir()\nsys.path.insert(0, {str(path.parent)!r})\n"
    elif origin == "outside-tools":
        path = tools.parent / "probe.py"
    elif origin == "direct-native":
        from importlib.machinery import EXTENSION_SUFFIXES
        path = tools / ("probe" + EXTENSION_SUFFIXES[0])
    else:
        path = tools / "unexpected.py"
    if path:
        setup += f"Path({str(path)!r}).write_text({body!r})\n"
        if origin in ("outside-tools", "direct-package", "direct-native"):
            setup += (f"spec = importlib.util.spec_from_file_location('probe', {str(path)!r})\n"
                      "module = importlib.util.module_from_spec(spec)\nspec.loader.exec_module(module)\n")
        else:
            setup += "import unexpected\n" if origin == "unexpected" else "import probe\n"
    proc = subprocess.run(cycle_source.command(tools, setup), capture_output=True, text=True,
                          env=dict(os.environ, **{cycle_source.AUDIT_ENV: str(audit)}))
    assert proc.returncode != 0
    assert "non-canonical snapshot module origin" in proc.stderr or "unexpected executed snapshot module" in proc.stderr
    assert not marker.exists()


@pytest.mark.parametrize("helper", ["script", "command"])
def test_python_helpers_cannot_skip_module_audit(tmp_path, helper):
    import os
    import subprocess
    tools = tmp_path / "snapshot/tools"
    tools.mkdir(parents=True)
    shutil.copyfile(cycle_source.__file__, tools / "cycle_source.py")
    (tools / "link_cycle_context.py").write_text(
        "MEASUREMENT_FILES = ('cycle_source.py', 'link_cycle_context.py', 'probe.py')\n")
    (tools / "probe.py").write_text("if __name__ == '__main__':\n    import unexpected\n")
    marker = tmp_path / "executed"
    (tools / "unexpected.py").write_text(f"from pathlib import Path\nPath({str(marker)!r}).touch()\n")
    audit = tmp_path / "audit"
    audit.mkdir()
    args = "[sys.executable, str(tools / 'probe.py')]" if helper == "script" else (
        "[sys.executable, '-c', 'import unexpected']")
    # Even an explicit fresh env must inherit this launcher's evidence sink.
    program = f"import subprocess\nsubprocess.run({args}, env={{'PATH': '/usr/bin'}}, check=True)\n"
    proc = subprocess.run(cycle_source.command(tools, program), capture_output=True, text=True,
                          env=dict(os.environ, **{cycle_source.AUDIT_ENV: str(audit)}))
    assert proc.returncode != 0
    assert not marker.exists()
    assert ("unexpected executed snapshot module" if helper == "script" else "unbootstrapped Python helper") in proc.stderr


def test_stamp_attachment_rechecks_destination_after_replace(checkout, tmp_path, monkeypatch):
    root, _ = checkout
    run, _ = failed_run(checkout, tmp_path / "run")
    good = freeze(run, tmp_path / "signed", root)
    unsigned = tmp_path / "unsigned"
    shutil.copytree(good, unsigned)
    (unsigned / stamp.STAMP).unlink()
    original = ca.os.replace

    def replace(source, destination):
        original(source, destination)
        # Simulate destination bytes changing after the pre-attachment check.
        (unsigned / ca.MANIFEST).write_bytes((unsigned / ca.MANIFEST).read_bytes() + b"\n")

    monkeypatch.setattr(ca.os, "replace", replace)
    with pytest.raises(ca.BundleError, match="attached stamp verification"):
        ca.attach_verified_stamp(good, unsigned)


@pytest.mark.parametrize("variant", ["missing", "incomplete", "changed", "foreign-root"])
def test_module_audit_requires_completed_consistent_snapshot_records(tmp_path, variant):
    audit = tmp_path / "audit"
    audit.mkdir()
    tools = tmp_path / "snapshot/tools"
    record = {"complete": True, "tools": str(tools),
              "modules": {"probe.py": {"origin": "tools/probe.py", "sha256": "0" * 64}}}
    expected = "missing executed-module evidence"
    if variant != "missing":
        if variant == "incomplete":
            record["complete"] = False
            expected = "incomplete executed-module evidence"
        elif variant == "foreign-root":
            record["tools"] = str(tmp_path / "outside/tools")
            expected = "origin outside snapshot tools"
        (audit / "first.json").write_text(json.dumps(record))
        if variant == "changed":
            record["modules"]["probe.py"]["sha256"] = "1" * 64
            (audit / "second.json").write_text(json.dumps(record))
            expected = "changed across subprocesses"
    with pytest.raises(ValueError, match=expected):
        cycle_source.audit_modules(audit, roots=(tools,))
