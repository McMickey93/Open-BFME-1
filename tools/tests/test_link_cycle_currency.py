"""Cycle currency uses BFME1's witnessed inputs; no real compiler or link."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import build
import census_receipts
import cycle_artifacts as ca
import cycle_source
import link_census as census
import link_cycle as lc
import link_cycle_context as context
import publish_cycle as pc
from cycle_fixture import measured_run, rehash, save_receipt
from test_build_include_inventory import _fixture
from test_census_receipts import fixture


def witnessed(tmp_path, monkeypatch):
    source, header, obj, command, env, run = fixture(tmp_path, monkeypatch)
    monkeypatch.setattr(lc, "ROOT", tmp_path)
    monkeypatch.setattr(census, "_object_sources", lambda rows: {obj: source})
    monkeypatch.setattr(build, "obj_path", lambda s: obj)
    monkeypatch.setattr(build, "extract_lib_members", lambda rows: None)
    monkeypatch.delenv("BUILD_RECOMPILE_ONLY", raising=False)
    out = tmp_path / "cycle"
    out.mkdir()
    receipts, failed = lc.compile_cycle_rows([], [source], out)
    assert not failed and not build.compile_is_current(source, obj)
    return source, header, obj, out, receipts


def test_receipt_proves_cycle_object_and_is_owned_by_cycle(tmp_path, monkeypatch):
    source, _, obj, out, receipts = witnessed(tmp_path, monkeypatch)
    monkeypatch.setattr(census, "input_receipts", lambda: pytest.fail("used census receipts"))
    assert context.current_object(source, obj, receipts=receipts)
    _, proofs, _ = lc.provenance([], [obj], lc.Objects([obj]), out, receipts=receipts)
    assert proofs == {"receipt": 1}
    record = json.loads((out / "provenance.json").read_text())["unit.obj"]
    assert record["proof"] == "receipt" and record["deps_sha256"] is None
    assert receipts.path == out / "compile_inputs.json"
    binding = lc.compile_input_binding(receipts)
    assert binding["compile_inputs_sha256"] == lc.sha256(receipts.path)
    (out / "receipt.json").write_text(json.dumps(binding))
    loaded = lc.cycle_input_receipts(out)
    assert loaded.run == receipts.run
    assert context.current_object(source, obj, receipts=loaded)


@pytest.mark.parametrize("change", ["no-receipt", "source", "header", "object"])
def test_cycle_refuses_without_a_current_proof(tmp_path, monkeypatch, change):
    source, header, obj, out, receipts = witnessed(tmp_path, monkeypatch)
    if change == "no-receipt":
        receipts = None
    elif change == "source":
        source.write_text(source.read_text() + "int changed;\n")
    elif change == "header":
        header.write_text("#define VALUE 18\n")
    else:
        obj.write_bytes(b"")
    assert not context.current_object(source, obj, receipts=receipts)
    with pytest.raises(SystemExit, match="not current.*--build"):
        lc.provenance([], [obj], lc.Objects([obj]), out, receipts=receipts)


@pytest.mark.parametrize("damage", ["missing", "empty", "header", "sections", "strings", "machine"])
@pytest.mark.parametrize("incremental", [False, True])
def test_invalid_cached_object_is_requested_for_recompile(tmp_path, monkeypatch, damage, incremental):
    source, obj, *_ = _fixture(tmp_path, monkeypatch)
    lc.write_coff(obj, [(".text", 0x60500020, b"\xc3", 0)], [("_f", 1, 0, lc.EXTERNAL)])
    good = obj.read_bytes()
    assert build.compile_is_current(source, obj)
    if damage == "missing":
        obj.unlink()
    else:
        damaged = {"empty": b"", "header": good[:19], "sections": good[:40],
                   "strings": good[:-1], "machine": b"xx" + good[2:]}
        obj.write_bytes(damaged[damage])
    monkeypatch.setattr(build, "compiler_command", lambda *a: pytest.fail("discovered compiler for invalid object"))
    assert not build.compile_is_current(source, obj)
    monkeypatch.setattr(build, "extract_lib_members", lambda rows: None)
    monkeypatch.setattr(build, "obj_path", lambda s: obj)
    if incremental:
        monkeypatch.setenv("BUILD_RECOMPILE_ONLY", "")
    else:
        monkeypatch.delenv("BUILD_RECOMPILE_ONLY", raising=False)
    requests = []
    monkeypatch.setattr(build, "compile_source", lambda s, o: requests.append((s, o)))
    assert build.compile_rows([], [source]) == {source: obj}
    assert requests == [(source, obj)]


@pytest.mark.parametrize("raw", [b"", b"\x4c\x01" + b"\0" * 17])
def test_cycle_names_invalid_object_without_struct_traceback(tmp_path, raw):
    obj = tmp_path / "killed.obj"
    obj.write_bytes(raw)
    with pytest.raises(SystemExit, match=r"invalid COFF object .*killed.obj.*--build"):
        lc.Objects([obj]).get(obj)


def test_receipt_cannot_prove_an_unchanged_invalid_object(tmp_path, monkeypatch):
    source, _, obj, _, receipts = witnessed(tmp_path, monkeypatch)
    obj.write_bytes(b"")
    receipts.entries[str(obj.resolve())]["object"] = census_receipts.digest(obj)
    assert not receipts.current(source, obj)
    assert "complete COFF" in receipts.why[str(obj)]


def test_compile_failure_keeps_receipt_proven_successes(tmp_path, monkeypatch):
    source, _, obj, out, _ = witnessed(tmp_path, monkeypatch)
    bad = source.with_name("bad.cpp")
    bad.write_text("int broken;\n")
    bad_obj = obj.with_name("bad.obj")
    monkeypatch.setattr(build, "obj_path", lambda s: obj if s == source else bad_obj)

    def partial(rows, sources, *, input_proof):
        assert build.try_compile_source(source, obj, input_proof=input_proof)[0]
        raise SystemExit("synthetic failed TU")

    monkeypatch.setattr(build, "compile_rows", partial)
    receipts, failed = lc.compile_cycle_rows([], [source, bad], out)
    assert failed == ["game/bad.cpp"]
    assert receipts.current(source, obj)
    assert receipts.path.is_file()


@pytest.mark.parametrize("attack", ["missing", "tamper", "rehash-manifest"])
def test_compile_receipts_are_bound_in_run_archive_and_bundle(tmp_path, monkeypatch, attack):
    run, receipt = measured_run(tmp_path / "run")
    receipts = census_receipts.Receipts(run / ca.COMPILE_INPUTS)
    receipts.save()
    (run / ca.PROVENANCE).write_text("{}")
    receipt["provenance_sha256"] = lc.sha256(run / ca.PROVENANCE)
    receipt.update(lc.compile_input_binding(receipts))
    save_receipt(run, receipt)
    original_core = receipt["core_sha256"]
    receipt["compile_inputs_sha256"] = "0" * 64
    assert lc.digest_of(lc.receipt_core(receipt)) != original_core
    receipt.update(lc.compile_input_binding(receipts))
    monkeypatch.setattr(lc.time, "time_ns", lambda: receipt["measured_end_ns"])
    identity = lc.write_receipt(run, receipt)
    archived = run / "measurements" / identity["tag"]
    assert (archived / ca.COMPILE_INPUTS).read_bytes() == receipts.path.read_bytes()
    bundle = tmp_path / "bundle"
    manifest = pc.make_bundle(run, bundle, "synthetic")
    assert ca.COMPILE_INPUTS in manifest["members"]
    assert manifest["binding"]["compile_inputs_sha256"] == receipt["compile_inputs_sha256"]
    ca.validate(bundle)
    for directory in (run, bundle):
        path = directory / ca.COMPILE_INPUTS
        if attack == "missing":
            path.unlink()
        else:
            path.write_text(path.read_text() + "\n")
    if attack == "rehash-manifest":
        rehash(bundle, ca.COMPILE_INPUTS)
    with pytest.raises(ca.BundleError) as error:
        ca.validate(bundle)
    assert error.value.reason == "corrupt"
    with pytest.raises(ca.BundleError, match="compile input receipts"):
        pc.validate_run(run)
    with pytest.raises(SystemExit, match="corrupt compile input receipts"):
        lc.cycle_input_receipts(run)


def test_snapshot_subprocess_uses_its_own_receipt_currency(tmp_path):
    """Run the snapshot's source-only bootstrap with inert compiler transcripts."""
    snapshot = tmp_path / "snapshot"
    tools = snapshot / "tools"
    tools.mkdir(parents=True)
    provider_names = set(context.MEASUREMENT_FILES)
    for name in provider_names:
        source = Path(lc.__file__).parent / name
        if source.is_file():
            shutil.copyfile(source, tools / name)
    program = r'''
import json
from pathlib import Path
from types import SimpleNamespace
import build
import census_receipts as cr
import link_cycle as lc
root = lc.ROOT
assert Path(lc.__file__).parent == root / "tools"
assert build.ROOT == root
source = root / "unit.cpp"
source.write_text("int f(){return 17;}\n")
obj = lc.write_coff(root / "unit.obj", [(".text", 0x60500020, b"\xc3", 0)], [("_f", 1, 0, lc.EXTERNAL)])
command, env = ["synthetic", "-c", "-Fo" + str(obj), str(source)], {}
build.compiler_command = lambda *a: (command, env)
build._cmd_fingerprint = lambda *a: "synthetic flags"
cr.capture_preprocessor = lambda *a: SimpleNamespace(returncode=0, stderr=b"", stdout=(f'#line 1 "{source}"\n'.encode() + source.read_bytes()))
out = root / "cycle"
out.mkdir()
receipts = cr.Receipts(out / lc.COMPILE_INPUTS)
witness = cr.snapshot(source, command, env)
receipts.after(source, obj, command, env, witness, "")
receipts.save()
(out / "receipt.json").write_text(json.dumps(lc.compile_input_binding(receipts)))
lc.census._object_sources = lambda rows: {obj: source}
lc.census.input_receipts = lambda: (_ for _ in ()).throw(AssertionError("census proof leaked"))
loaded = lc.cycle_input_receipts(out)
assert lc.provenance([], [obj], lc.Objects([obj]), out, receipts=loaded)[1] == {"receipt": 1}
source.write_text("int f(){return 18;}\n")
try:
    lc.provenance([], [obj], lc.Objects([obj]), out, receipts=loaded)
except SystemExit as error:
    assert "not current" in str(error)
else:
    raise AssertionError("snapshot accepted stale source")
print("receipt accepted; changed source refused")
'''
    result = subprocess.run(cycle_source.command(tools, program), cwd=snapshot,
                            env=dict(os.environ, LINK_CYCLE_ROOT=str(snapshot)),
                            capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stderr
    assert "receipt accepted; changed source refused" in result.stdout
