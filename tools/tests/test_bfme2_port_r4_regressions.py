"""Round-4 regressions: inert measurements, synthetic compilers, temporary keys.

Original reproduction names are retained; assertions now require the fixes.
"""
import copy
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import types
import venv
import zipfile

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import build
import census_receipts as cr
import cycle_artifacts as ca
import cycle_launch as launch
import cycle_source as cs
import cycle_stamp as stamp
import link_census as census
import link_cycle as lc
import link_cycle_context as ctx
from cycle_fixture import NOW, save_receipt
from test_bfme2_port_r1_regressions import checkout, freeze, git, run_for, synthetic_snapshot_checkout
from test_bfme2_port_r2_regressions import commit_fixture


def receipt_proven_run(checkout, tmp_path, monkeypatch):
    root, _ = checkout
    source = root / "game/f.cpp"
    obj = root / "build/f.obj"
    obj.parent.mkdir()
    lc.write_coff(obj, [(".text", 0x60500020, b"\xc3", 0)], [("_f", 1, 0, lc.EXTERNAL)])
    command, env = ["inert-transcript", "-c", "-Fo" + str(obj), str(source)], {}
    monkeypatch.setattr(build, "compiler_command", lambda *a: (command, env))
    monkeypatch.setattr(build, "_cmd_fingerprint", lambda *a: "synthetic-flags")
    monkeypatch.setattr(cr, "capture_preprocessor", lambda *a: types.SimpleNamespace(
        returncode=0, stderr=b"", stdout=f'#line 1 "{source}"\n'.encode() + source.read_bytes()))
    run, receipt = run_for(checkout, tmp_path / "run")
    witness = cr.Receipts(run / ca.COMPILE_INPUTS)
    before = cr.snapshot(source, command, env)
    # Represent a successful inert compile with unchanged before/after inputs.
    witness.after(source, obj, command, env, before, "")
    witness.save()
    assert witness.current(source, obj)
    assert not build.compile_is_current(source, obj)
    monkeypatch.setattr(lc, "ROOT", root)
    monkeypatch.setattr(census, "_object_sources", lambda rows: {obj: source})
    (run / ca.PROVENANCE).unlink()
    objects = lc.Objects([obj])
    prov_hash, proofs, canon = lc.provenance([], [obj], objects, run, receipts=witness)
    receipt.update(canon, provenance_sha256=prov_hash, currency_proofs=proofs,
                   objects_digest=lc.objects_digest(objects, [obj]), **lc.compile_input_binding(witness))
    save_receipt(run, receipt)
    assert proofs == {"receipt": 1}
    return root, run, receipt, witness


def test_defect_authority_rejects_valid_receipt_proven_object(checkout, tmp_path, monkeypatch):
    root, run, receipt, witness = receipt_proven_run(checkout, tmp_path, monkeypatch)
    bundle = freeze(run, tmp_path / "bundle", root)
    ca.validate(bundle, root=root)
    assert stamp.verify(bundle) is None
    assert ca.run_evidence_failure(bundle, receipt, root) is None
    assert ca.serve(bundle, root=root, now=NOW)[1]["authoritative"]


@pytest.mark.parametrize("bss,symbol_table", [(False, False), (True, False), (False, True), (True, True)])
def test_sound_symbol_free_coff(tmp_path, bss, symbol_table):
    # i386 section-only objects and BSS are legal without a symbol table.
    data = b"" if bss else b"\xc3"
    symptr = 60 + len(data) if symbol_table else 0
    raw = (struct.pack("<HHIIIHH", 0x14c, 1, 0, symptr, 0, 0, 0)
           + struct.pack("<8sIIIIIIHHI", b".bss" if bss else b".text", 0, 0,
                         32 if bss else 1, 0 if bss else 60, 0, 0, 0, 0,
                         0xC0300080 if bss else 0x60500020)
           + data + (struct.pack("<I", 4) if symbol_table else b""))
    build.validate_coff(raw)


@pytest.mark.parametrize("startup", ["pth", "sitecustomize", "zip-sitecustomize"])
def test_defect_site_startup_changes_executed_provider_without_changing_rules(checkout, tmp_path, startup):
    root, _ = synthetic_snapshot_checkout(checkout)
    driver = root / "tools/link_cycle.py"
    source = driver.read_text().replace(
        '    receipt["synthetic_execution"] = ',
        '    receipt["startup_object_current"] = context.current_object(ROOT / "game/absent.cpp", ROOT / "build/absent.obj")\n'
        '    receipt["synthetic_execution"] = ')
    driver.write_text(source)
    commit_fixture(root, "inert object currency probe")
    rules = ca.local_rules(root)
    environment = tmp_path / "python-environment"
    venv.EnvBuilder(with_pip=False).create(environment)
    py = environment / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    site = next(environment.glob("lib/python*/site-packages")) if os.name != "nt" else environment / "Lib/site-packages"
    # Share installed dependencies read-only, without touching the host venv.
    dependency_dirs = [p for p in sys.path if p.endswith(("site-packages", "dist-packages"))]
    (site / "dependencies.pth").write_text("\n".join(dependency_dirs) + "\n")
    hook = '''import sys
def profile(frame, event, result):
    if event == "return" and frame.f_code.co_name == "<module>" and frame.f_code.co_filename.endswith("/tools/build.py"):
        frame.f_globals["compile_is_current"] = lambda *args, **kwargs: True
if sys.flags.isolated:
    sys.setprofile(profile)
'''
    if startup == "pth":
        (site / "review_startup.py").write_text(hook)
        (site / "review.pth").write_text("import review_startup\n")
    elif startup == "sitecustomize":
        (site / "sitecustomize.py").write_text(hook)
    else:
        archive = tmp_path / "startup.zip"
        with zipfile.ZipFile(archive, "w") as stream:
            stream.writestr("sitecustomize.py", hook)
        (site / "review.pth").write_text(str(archive) + "\n")
    out = tmp_path / "launched"
    # Launch normally from this interpreter. Only isolated children activate the
    # startup hook; the launcher, signer and independent reader are unmodified.
    program = ("import sys; sys.path.insert(0, sys.argv[1]); import cycle_launch as launch; "
               "launch.measure(sys.argv[3], 'R4 startup probe', root=sys.argv[2], key=sys.argv[4]); "
               "launch.stamp._reader_key_for_tests = launch.Path(sys.argv[4]); "
               f"b, fr, _ = launch.ca.serve(sys.argv[3], root=sys.argv[2], now={NOW}); "
               "assert fr['authoritative'] and b.receipt['startup_object_current'] is False")
    result = subprocess.run([str(py), "-B", "-c", program, str(Path(lc.__file__).parent), str(root),
                             str(out), str(stamp.configured_keys()[0])],
                            capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, result.stdout + result.stderr
    bundle = ca.load_bundle(out, root=root)
    assert stamp.verify(out) is None
    assert bundle.receipt["startup_object_current"] is False
    assert ca.local_rules(root) == rules
    assert rules["implementation_sha256"] == bundle.receipt["rule_identity"]["implementation_sha256"]
    # Editing venv startup files changes compatibility, even though -S prevented
    # their execution and the original object predicate remained in effect.
    assert rules["runtime"] != bundle.receipt["rule_identity"]["runtime"]
    with pytest.raises(ca.Refused) as refused:
        ca.serve(out, root=root, now=NOW)
    assert refused.value.reason == "incompatible-rules"
    assert not ctx.current_object(root / "game/absent.cpp", root / "build/absent.obj")
    assert set(bundle.receipt["executed_modules"]) == set(ctx.MEASUREMENT_FILES)


def small_snapshot(tmp_path):
    tools = tmp_path / "snapshot/tools"
    tools.mkdir(parents=True)
    shutil.copyfile(cs.__file__, tools / "cycle_source.py")
    (tools / "link_cycle_context.py").write_text(
        "MEASUREMENT_FILES = ('cycle_source.py', 'link_cycle_context.py', 'probe.py')\n")
    (tools / "probe.py").write_text("current = False\n")
    audit = tmp_path / "audit"
    audit.mkdir()
    return tools, audit


@pytest.mark.parametrize("late", [False, True])
def test_defect_custom_meta_loader_escapes_executed_module_record(tmp_path, late):
    """Component probe: a startup-installed hook can run even after completion.

    The whole-launcher startup test above supplies the concrete entry point.
    Here the inert program installs a virtual finder to isolate loader coverage.
    """
    tools, audit = small_snapshot(tmp_path)
    program = '''import importlib.util
class Loader:
    def create_module(self, spec):
        return None
    def exec_module(self, module):
        module.current = True
class Finder:
    def find_spec(self, name, path=None, target=None):
        if name == "probe":
            return importlib.util.spec_from_loader(name, Loader(), origin="virtual:startup")
def replace():
    sys.meta_path.insert(0, Finder())
    sys.modules.pop("probe")
    import probe
    assert probe.current is True
    print("virtual loader executed")
'''
    program += "import atexit; atexit.register(replace)\n" if late else "replace()\n"
    result = subprocess.run(cs.command(tools, program), capture_output=True, text=True,
                            env=dict(os.environ, **{cs.AUDIT_ENV: str(audit)}), timeout=30)
    assert "virtual loader executed" not in result.stdout
    assert "custom meta-path loader" in result.stderr
    with pytest.raises(ValueError, match="incomplete"):
        cs.audit_modules(audit, roots=(tools,))


@pytest.mark.parametrize("origin", ["zip", "native", "late-source"])
def test_sound_normal_alternative_loaders_fail_closed(tmp_path, origin):
    tools, audit = small_snapshot(tmp_path)
    marker = tmp_path / "marker"
    if origin == "zip":
        archive = tmp_path / "alternate.zip"
        with zipfile.ZipFile(archive, "w") as stream:
            stream.writestr("probe.py", f"from pathlib import Path\nPath({str(marker)!r}).touch()\n")
        program = f"sys.modules.pop('probe'); sys.path.insert(0, {str(archive)!r}); import probe"
    elif origin == "native":
        import _json
        native = Path(_json.__file__)
        copied = tmp_path / ("probe" + native.name[len("_json"):])
        shutil.copyfile(native, copied)
        program = (f"import importlib.util\nspec = importlib.util.spec_from_file_location('probe', {str(copied)!r})\n"
                   "module = importlib.util.module_from_spec(spec)\nspec.loader.exec_module(module)\n")
    else:
        # An unlisted normal source import after write(True) is still refused
        # before its module body runs, even in an atexit callback.
        (tools / "unexpected.py").write_text(f"from pathlib import Path\nPath({str(marker)!r}).touch()\n")
        program = "import atexit\ndef late():\n    import unexpected\natexit.register(late)\n"
    result = subprocess.run(cs.command(tools, program), capture_output=True, text=True,
                            env=dict(os.environ, **{cs.AUDIT_ENV: str(audit)}), timeout=30)
    assert "non-canonical snapshot module origin" in result.stderr or "unexpected executed snapshot module" in result.stderr
    assert not marker.exists()
    if origin != "late-source":
        assert result.returncode != 0
        with pytest.raises(ValueError, match="incomplete"):
            cs.audit_modules(audit, roots=(tools,))


def test_sound_launcher_strips_python_environment_and_usercustomize(checkout, tmp_path, monkeypatch):
    root, _ = synthetic_snapshot_checkout(checkout)
    poison = tmp_path / "poison"
    poison.mkdir()
    marker = tmp_path / "startup-executed"
    for name in ("sitecustomize.py", "usercustomize.py"):
        (poison / name).write_text(f"from pathlib import Path\nPath({str(marker)!r}).touch()\nraise RuntimeError('poison')\n")
    # A genuine user-site path under a caller-selected base; -I disables it.
    usersite = poison / f"lib/python{sys.version_info.major}.{sys.version_info.minor}/site-packages"
    usersite.mkdir(parents=True)
    shutil.copyfile(poison / "usercustomize.py", usersite / "usercustomize.py")
    for name, value in {"PYTHONPATH": poison, "PYTHONHOME": poison, "PYTHONUSERBASE": poison,
                        "PYTHONSTARTUP": poison / "sitecustomize.py", "PYTHONINSPECT": "1"}.items():
        monkeypatch.setenv(name, str(value))
    out = tmp_path / "bundle"
    launch.measure(out, "R4 environment isolation", root=root, key=stamp.configured_keys()[0])
    assert ca.serve(out, root=root, now=NOW)[1]["authoritative"]
    assert not marker.exists()


def baseline_module(name, monkeypatch):
    module = types.ModuleType("r4_baseline_" + name)
    module.__file__ = str(Path(lc.__file__).parent / (name + ".py"))
    monkeypatch.setitem(sys.modules, module.__name__, module)
    source = git(Path(lc.__file__).parents[1], "show", "aef2f16877:tools/" + name + ".py")
    exec(compile(source, module.__file__, "exec"), module.__dict__)
    return module


@pytest.mark.parametrize("change", ["none", "source", "header", "object", "command", "pp", "restore"])
def test_sound_census_receipt_currency_matches_baseline(tmp_path, monkeypatch, change):
    old_census = baseline_module("link_census", monkeypatch)
    old_build = baseline_module("build", monkeypatch)
    from test_census_receipts import fixture
    source, header, obj, command, env, transcript = fixture(tmp_path, monkeypatch)
    witness = cr.Receipts(tmp_path / "compile_inputs.json")
    assert build.try_compile_source(source, obj, input_proof=witness)[0]
    if change == "source":
        source.write_text(source.read_text() + "// changed\n")
    elif change == "header":
        header.write_text("#define VALUE 19\n")
    elif change == "object":
        lc.write_coff(obj, [(".text", 0x60500020, b"\xcc", 0)], [])
    elif change == "command":
        monkeypatch.setattr(build, "compiler_command", lambda *a: ([*command, "-DCHANGED=1"], env))
    elif change == "pp":
        capture = cr.capture_preprocessor
        def changed(*args):
            result = capture(*args)
            result.stdout += b"// different preprocessor output\n"
            return result
        monkeypatch.setattr(cr, "capture_preprocessor", changed)
    elif change == "restore":
        raw = header.read_bytes()
        header.write_bytes(raw + b"// change\n")
        header.write_bytes(raw)
    # Both versions check this same valid object and the same input witness.
    # Baseline build must not accidentally use the new validity preflight.
    monkeypatch.setattr(old_census, "build", old_build)
    monkeypatch.setattr(old_census, "input_receipts", lambda: witness)
    monkeypatch.setattr(census, "input_receipts", lambda: witness)
    old = old_census.object_current(source, obj)
    new = census.object_current(source, obj)
    assert old == new == (change in {"none", "restore"})
    why_old, why_new, proofs = {}, {}, {}
    assert old_census.stale_objects([obj], {obj: source}, why_old) == census.stale_objects(
        [obj], {obj: source}, why_new, proofs=proofs)
    assert why_old == why_new
    assert proofs == ({obj: "receipt"} if new else {})


def test_defect_empty_compile_witness_randomizes_reproducible_cores(tmp_path):
    from cycle_fixture import measured_run
    run, receipt = measured_run(tmp_path / "run")
    first = cr.Receipts(run / ca.COMPILE_INPUTS)
    first.save()
    a = dict(copy.deepcopy(receipt), **lc.compile_input_binding(first))
    second = cr.Receipts(run / ca.COMPILE_INPUTS)
    second.save()
    b = dict(copy.deepcopy(receipt), **lc.compile_input_binding(second))
    assert first.entries == second.entries == {}
    assert {k: v for k, v in a.items() if not k.startswith("compile_input")} == {
        k: v for k, v in b.items() if not k.startswith("compile_input")}
    lc.stamp_cores(a)
    lc.stamp_cores(b)
    assert a["core_sha256"] == b["core_sha256"]
    assert a["core_canon_sha256"] == b["core_canon_sha256"]


def test_sound_malformed_object_is_only_new_cache_refusal(tmp_path, monkeypatch):
    old_build = baseline_module("build", monkeypatch)
    from test_build_include_inventory import _fixture
    source, obj, _, _, command, env = _fixture(tmp_path, monkeypatch)
    monkeypatch.setattr(old_build, "ROOT", build.ROOT)
    monkeypatch.setattr(old_build, "compiler_command", lambda *a: (command, env))
    monkeypatch.setattr(old_build, "_cmd_fingerprint", lambda *a: "command")
    assert old_build.compile_is_current(source, obj) is True
    assert build.compile_is_current(source, obj) is True
    obj.write_bytes(b"")
    assert old_build.compile_is_current(source, obj) is True
    assert build.compile_is_current(source, obj) is False


@pytest.mark.parametrize("change", ["missing-entry", "object", "source", "command", "source-input", "reference", "semantic"])
def test_receipt_authority_requires_the_corresponding_witness(checkout, tmp_path, monkeypatch, change):
    root, run, receipt, witness = receipt_proven_run(checkout, tmp_path, monkeypatch)
    prov = ca.read_json(run / ca.PROVENANCE)
    rec = prov["build/f.obj"]
    ref = rec["receipt_ref"]
    entry = witness.entries[ref]
    if change == "missing-entry":
        witness.entries.clear()
    elif change == "reference":
        rec["receipt_ref"] = str(tmp_path / "foreign/build/f.obj")
    elif change == "semantic":
        rec["witness_semantic_sha256"] = "0" * 64
    else:
        if change == "object":
            entry["object"] = "0" * 64
        elif change == "source":
            entry["source"] = str(root / "game/foreign.cpp")
        elif change == "command":
            entry["command"] = [*entry["command"], "-DOTHER"]
        else:
            entry["input"]["files"][entry["source"]] = "0" * 64
        # Rebind the edited exact witness and its deterministic summary. The
        # independent object/source/command associations must still reject it.
        rec["receipt_sha256"] = lc.digest_of(entry)
        rec["witness_semantic_sha256"] = lc.digest_of(lc.compile_input_semantics({ref: entry}))
    witness.save()
    (run / ca.PROVENANCE).write_text(ca.dumps(prov))
    receipt.update(lc.compile_input_binding(witness), **lc.canonical_digests(prov),
                   provenance_sha256=ca.sha256_file(run / ca.PROVENANCE))
    save_receipt(run, receipt)
    bundle = freeze(run, tmp_path / "bundle", root)
    assert stamp.verify(bundle) is None
    ca.validate(bundle, root=root)
    assert ca.run_evidence_failure(bundle, receipt, root) == "object-source-mismatch"
    with pytest.raises(ca.Refused) as refused:
        ca.serve(bundle, root=root, now=NOW)
    assert refused.value.sub_reason == "object-source-mismatch"


def test_runtime_records_dependencies_extensions_and_bootstrap_imports(tmp_path):
    tools, audit = small_snapshot(tmp_path)
    result = subprocess.run(cs.command(tools, "import pefile, capstone, _json"),
                            env=cs.clean_environment({cs.AUDIT_ENV: str(audit)}), capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stderr
    modules = cs.audit_modules(audit, roots=(tools,), runtime=True)
    assert modules["pathlib"]["origin"].startswith("stdlib/")  # imported before cycle_source itself
    assert modules["pefile"] == {"origin": "packages/pefile.py", "sha256": cs.file_hash(cs.dependency_locations()["pefile.py"])}
    assert modules["capstone"]["origin"] == "packages/capstone/__init__.py"
    assert any(name.startswith("capstone.__native__.") and entry["origin"].startswith("packages/capstone/")
               for name, entry in modules.items())
    assert modules["_json"]["origin"].endswith((".so", ".pyd"))
    assert modules["sys"] == {"origin": "built-in:sys", "sha256": cs.file_hash(sys.executable)}
    assert all(set(v) == {"origin", "sha256"} and len(v["sha256"]) == 64 for v in modules.values())


def test_nonempty_witness_cores_ignore_run_generations_and_export_paths(tmp_path, monkeypatch):
    from cycle_fixture import measured_run
    _, baseline = measured_run(tmp_path / "baseline")
    outputs = []
    for index in range(2):
        root = tmp_path / str(index)
        source, obj = root / "game/f.cpp", root / "build/f.obj"
        command = ["compiler", "-c", str(source), "-Fo" + str(obj)]
        entry = {"source": str(source), "object": str(index) * 64, "command": command,
                 "input": {"files": {str(source): "f" * 64}, "preprocessed": str(index) * 64,
                           "preprocessed_canon": "e" * 64, "generations": {str(source): [index]},
                           "signature": {"command": command, "fingerprint": str(index),
                                         "environment": {"include": str(root)}, "implicit_flags": ["", ""]}}}
        witness = cr.Receipts(root / ca.COMPILE_INPUTS, entries={str(obj): entry})
        witness.save()
        monkeypatch.setattr(lc, "ROOT", root)
        receipt = dict(copy.deepcopy(baseline), **lc.compile_input_binding(witness))
        prov = {"build/f.obj": {"object": "a" * 64, "object_canon": "b" * 64, "proof": "receipt",
                                "receipt_ref": str(obj), "receipt_sha256": lc.digest_of(entry),
                                "object_sha256": entry["object"], "witness_semantic_sha256":
                                lc.digest_of(lc.compile_input_semantics(witness.entries))}}
        receipt.update(lc.canonical_digests(prov), provenance_sha256=lc.digest_of(prov))
        lc.stamp_cores(receipt)
        outputs.append(receipt)
    a, b = outputs
    assert a["compile_inputs_sha256"] != b["compile_inputs_sha256"]
    assert a["provenance_sha256"] != b["provenance_sha256"]
    assert a["core_sha256"] == b["core_sha256"]
    assert a["core_canon_sha256"] == b["core_canon_sha256"]
    changed = dict(b, compile_inputs_semantic_sha256="0" * 64)
    lc.stamp_cores(changed)
    assert changed["core_sha256"] != a["core_sha256"]
    assert changed["core_canon_sha256"] != a["core_canon_sha256"]


def test_clean_environment_is_an_allowlist(tmp_path, monkeypatch):
    for key in ("PYTHONPATH", "PYTHONHOME", "LD_PRELOAD", "LD_LIBRARY_PATH", "DYLD_INSERT_LIBRARIES",
                "PATH", "HOME", "_PYTHON_SYSCONFIGDATA_NAME", "VC71_ROOT", "BFME_CYCLE_KEYS"):
        monkeypatch.setenv(key, str(tmp_path))
    clean = cs.clean_environment({})
    assert clean["PATH"] == os.defpath
    assert clean["HOME"] != str(tmp_path)
    assert not set(clean).intersection({"PYTHONPATH", "PYTHONHOME", "LD_PRELOAD", "LD_LIBRARY_PATH",
                                       "DYLD_INSERT_LIBRARIES", "_PYTHON_SYSCONFIGDATA_NAME", "VC71_ROOT", "BFME_CYCLE_KEYS"})


@pytest.mark.parametrize("late", [False, True])
def test_caught_loader_violation_never_restores_completed_audit(tmp_path, late):
    tools, audit = small_snapshot(tmp_path)
    (tools / "unlisted.py").write_text("raise AssertionError('must not execute')")
    program = """def attempt():
    try:
        import unlisted
    except ImportError:
        pass
"""
    program += "import atexit; atexit.register(attempt)" if late else "attempt()"
    result = subprocess.run(cs.command(tools, program), env=cs.clean_environment({cs.AUDIT_ENV: str(audit)}),
                            capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stderr
    with pytest.raises(ValueError, match="incomplete"):
        cs.audit_modules(audit, roots=(tools,))


@pytest.mark.parametrize("change", ["dependency", "extension", "startup", "executable"])
def test_runtime_installation_changes_make_rules_incompatible(tmp_path, monkeypatch, change):
    stdlib, packages = tmp_path / "stdlib", tmp_path / "site-packages"
    stdlib.mkdir()
    packages.mkdir()
    capstone = packages / "capstone"
    capstone.mkdir()
    dependency, extension, startup = capstone / "__init__.py", capstone / "native.so", packages / "startup.pth"
    executable = tmp_path / "python"
    for path in (dependency, extension, startup, executable):
        path.write_bytes(b"inert installation fixture")
    monkeypatch.setattr(cs, "runtime_paths", lambda: (stdlib, stdlib / "lib-dynload", packages))
    monkeypatch.setattr(cs, "dependency_locations", lambda: {"capstone": capstone})
    monkeypatch.setattr(sys, "executable", str(executable))
    deps = dict.fromkeys(ctx.MEASUREMENT_FILES, "e" * 64)
    before = ctx.rule_identity(deps)
    {"dependency": dependency, "extension": extension, "startup": startup, "executable": executable}[change].write_bytes(b"changed")
    after = ctx.rule_identity(deps)
    assert before["implementation_sha256"] == after["implementation_sha256"]
    assert before["runtime"] != after["runtime"]
    assert before != after


@pytest.mark.parametrize("hook", ["path-hooks", "cached-finder", "direct-loader"])
def test_custom_import_loaders_are_refused_before_execution(tmp_path, hook):
    tools, audit = small_snapshot(tmp_path)
    marker = tmp_path / "executed"
    program = f"""class Loader:
    def create_module(self, spec):
        Path({str(marker)!r}).touch()
    def exec_module(self, module):
        Path({str(marker)!r}).touch()
class Finder:
    def find_spec(self, *args):
        Path({str(marker)!r}).touch()
"""
    if hook == "path-hooks":
        program += "sys.path_hooks.insert(0, lambda *args: Finder()); sys.modules.pop('probe'); import probe"
    elif hook == "cached-finder":
        program += "sys.path_importer_cache[str(tools)] = Finder(); sys.modules.pop('probe'); import probe"
    else:
        program += "import importlib.util; spec = importlib.util.spec_from_loader('replacement', Loader(), origin='virtual'); importlib.util.module_from_spec(spec)"
    result = subprocess.run(cs.command(tools, program), env=cs.clean_environment({cs.AUDIT_ENV: str(audit)}),
                            capture_output=True, text=True, timeout=30)
    assert result.returncode != 0
    assert "non-canonical snapshot module origin" in result.stderr
    assert not marker.exists()
    with pytest.raises(ValueError, match="incomplete"):
        cs.audit_modules(audit, roots=(tools,))


def test_witness_semantics_validate_after_wine_path_cache_is_gone(checkout, tmp_path, monkeypatch):
    root, run, receipt, witness = receipt_proven_run(checkout, tmp_path, monkeypatch)
    wine_root = "Z:" + str(root).replace("/", "\\")
    monkeypatch.setitem(build._WINE_PATH_CACHE, str(root), wine_root)
    ref, entry = next(iter(witness.entries.items()))
    entry["command"] = [value.replace(str(root), wine_root) for value in entry["command"]]
    entry["input"]["signature"]["command"] = list(entry["command"])
    witness.save()
    prov = ca.read_json(run / ca.PROVENANCE)
    prov["build/f.obj"].update(receipt_sha256=lc.digest_of(entry), witness_semantic_sha256=
                              lc.digest_of(lc.compile_input_semantics(witness.entries)))
    (run / ca.PROVENANCE).write_text(ca.dumps(prov))
    receipt.update(lc.compile_input_binding(witness), **lc.canonical_digests(prov),
                   provenance_sha256=ca.sha256_file(run / ca.PROVENANCE))
    save_receipt(run, receipt)
    monkeypatch.delitem(build._WINE_PATH_CACHE, str(root))
    bundle = freeze(run, tmp_path / "bundle", root)
    assert stamp.verify(bundle) is None
    assert ca.serve(bundle, root=root, now=NOW)[1]["authoritative"]


def test_spawned_process_pool_and_resource_tracker_use_isolated_recorder(tmp_path):
    tools, audit = small_snapshot(tmp_path)
    (tools / "probe.py").write_text('''def inspect_runtime(value):
    import sys
    import pefile
    return (value, sys.flags.isolated, sys.flags.no_site, sys.flags.dont_write_bytecode)
''')
    program = '''import concurrent.futures
import multiprocessing
import probe
with concurrent.futures.ProcessPoolExecutor(1, mp_context=multiprocessing.get_context('spawn')) as pool:
    assert list(pool.map(probe.inspect_runtime, [7])) == [(7, 1, 1, 1)]
'''
    result = subprocess.run(cs.command(tools, program), env=cs.clean_environment({cs.AUDIT_ENV: str(audit)}),
                            capture_output=True, text=True, timeout=45)
    assert result.returncode == 0, result.stderr
    modules = cs.audit_modules(audit, roots=(tools,), runtime=True)
    assert modules["pefile"]["origin"] == "packages/pefile.py"
    records = [json.loads(p.read_bytes()) for p in audit.glob("*.json")]
    assert len(records) == 3  # parent, worker, resource tracker
    assert all(r["complete"] for r in records)
    assert all(set(r["modules"]) == {"cycle_source.py", "link_cycle_context.py", "probe.py"} for r in records)


def test_key_validation_uses_the_clean_environment(tmp_path, monkeypatch):
    key = stamp.keygen(tmp_path / "key")
    original = subprocess.run
    observed = []

    def run(*args, **kwargs):
        observed.append(kwargs["env"])
        return original(*args, **kwargs)

    monkeypatch.setattr(subprocess, "run", run)
    monkeypatch.setenv("PATH", str(tmp_path / "empty-search-path"))
    monkeypatch.setenv("LD_LIBRARY_PATH", str(tmp_path))
    monkeypatch.setenv("PYTHONPATH", str(tmp_path))
    monkeypatch.setenv("GIT_CONFIG_COUNT", "999")
    assert stamp.read_key(key) == key.read_bytes()
    assert observed and all(env == cs.clean_environment({}) for env in observed)


def test_ctypes_cannot_load_a_working_tree_native_provider(tmp_path):
    tools, audit = small_snapshot(tmp_path)
    (tools.parent / "libcapstone.so").write_bytes(b"inert shadow library")
    result = subprocess.run(cs.command(tools, "import ctypes; ctypes.CDLL('libcapstone.so')"),
                            cwd=tools.parent, env=cs.clean_environment({cs.AUDIT_ENV: str(audit)}),
                            capture_output=True, text=True, timeout=30)
    assert result.returncode != 0
    assert "non-canonical snapshot module origin: native library" in result.stderr
    with pytest.raises(ValueError, match="incomplete"):
        cs.audit_modules(audit, roots=(tools,))


def test_custom_finder_cannot_spoof_standard_hook_equality(tmp_path):
    tools, audit = small_snapshot(tmp_path)
    marker = tmp_path / "finder-executed"
    program = f'''class Finder:
    def __eq__(self, other):
        return True
    def find_spec(self, *args):
        Path({str(marker)!r}).touch()
sys.meta_path[0] = Finder()
sys.modules.pop('probe')
import probe
'''
    result = subprocess.run(cs.command(tools, program), env=cs.clean_environment({cs.AUDIT_ENV: str(audit)}),
                            capture_output=True, text=True, timeout=30)
    assert result.returncode != 0
    assert "custom meta-path loader" in result.stderr
    assert not marker.exists()
    with pytest.raises(ValueError, match="incomplete"):
        cs.audit_modules(audit, roots=(tools,))
