"""Round 6 regressions: temporary runtimes, inert snapshots and fake links.

Reviewer test names are retained; passing cases require the class-level fix. No real cycle,
compiler, linker, census CLI or Wine is executed. Keys/installations are temporary.
"""
import ast
import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import zipfile

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import cycle_artifacts as ca
import cycle_source as cs
import cycle_stamp as stamp
import link_cycle as lc
from cycle_fixture import NOW
from test_bfme2_port_r1_regressions import checkout, synthetic_snapshot_checkout
from test_bfme2_port_r2_regressions import commit_fixture
from test_bfme2_port_r4_regressions import small_snapshot
from test_bfme2_port_r5_regressions import isolated, private_python, scheduling_namespace


def startup_zip(stdlib, hook, *, disguise=False):
    """Use CPython's real pre-bootstrap ZIP search entry; never modify host files.

    Keep ordinary encoding submodules on disk. The attack sets only its module's
    __file__; __spec__.origin and loader still honestly identify the ZIP.
    """
    source = stdlib / "encodings/__init__.py"
    prefix = f"__path__[:] = [{str(source.parent)!r}]\n"
    if disguise:
        prefix += f"__file__ = {str(source)!r}\n"
    raw = source.read_text()
    # Leave the module docstring intact and set the package search before its
    # relative import of aliases. No importer/auditor/signing API is patched.
    raw = raw.replace("import codecs", prefix + "import codecs", 1)
    archive = stdlib.parent / f"python{sys.version_info.major}{sys.version_info.minor}.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_STORED) as stream:
        stream.writestr("encodings/__init__.py", raw + "\n" + hook)
    return archive


def identity_line(result):
    return next(line for line in result.stdout.splitlines() if line.startswith("IDENTITY="))


@pytest.mark.skipif(os.name == "nt", reason="disposable POSIX Python installation")
def test_defect_prebootstrap_zip_can_claim_disk_file_and_keep_identity(tmp_path):
    tools, audit = small_snapshot(tmp_path)
    py, stdlib = private_python(tmp_path)
    program = ("import json, cycle_source, encodings\n"
               "print('IDENTITY=' + json.dumps(cycle_source.runtime_identity(), sort_keys=True))\n"
               "print('HOOK=' + str(getattr(sys, 'r6_zip_hook', False)))\n"
               "print('SPEC=' + encodings.__spec__.origin)\n")
    before = isolated(tools, audit, program, python=py)
    assert before.returncode == 0, before.stderr
    startup_zip(stdlib, "import sys\nsys.r6_zip_hook = True\n", disguise=True)
    after = isolated(tools, audit, program, python=py)
    assert after.returncode != 0
    assert "preloaded module file/spec origin mismatch: encodings" in after.stderr
    assert "HOOK=True" not in after.stdout
    assert any(not json.loads(p.read_bytes())["complete"] for p in audit.glob("*.json"))
    probe = "import sys; sys.path.insert(0,sys.argv[1]); import cycle_source as c; print(c.runtime_identity())"
    changed = subprocess.run([str(py), "-I", "-S", "-B", "-c", probe, str(Path(cs.__file__).parent)],
                             env=cs.clean_environment({}), capture_output=True, text=True, check=True)
    assert json.loads(identity_line(before).removeprefix("IDENTITY=")) != ast.literal_eval(changed.stdout)



@pytest.mark.skipif(os.name == "nt", reason="disposable POSIX Python installation")
def test_sound_prebootstrap_zip_with_honest_file_is_refused(tmp_path):
    tools, audit = small_snapshot(tmp_path)
    py, stdlib = private_python(tmp_path)
    startup_zip(stdlib, "import sys\nsys.r6_zip_hook = True\n")
    result = isolated(tools, audit, "print('measurement ran')", python=py)
    assert result.returncode != 0
    assert "unsupported preloaded ZIP module: encodings" in result.stderr
    assert "measurement ran" not in result.stdout


@pytest.mark.skipif(os.name == "nt", reason="disposable POSIX Python installation")
def test_defect_launcher_signs_zip_predicate_under_unchanged_rules(checkout, tmp_path):
    root, _ = synthetic_snapshot_checkout(checkout)
    driver = root / "tools/link_cycle.py"
    driver.write_text(driver.read_text().replace(
        '    receipt["synthetic_execution"] = ',
        '    receipt["startup_object_current"] = context.current_object(ROOT / "game/absent.cpp", ROOT / "build/absent.obj")\n'
        '    receipt["synthetic_execution"] = '))
    commit_fixture(root, "inert R6 currency probe; real cycle removed")
    py, stdlib = private_python(tmp_path)
    probe = ("import sys, json; sys.path.insert(0, sys.argv[1]); import cycle_artifacts; "
             "print(json.dumps(cycle_artifacts.local_rules(cycle_artifacts.Path(sys.argv[2])), sort_keys=True))")
    before = subprocess.run([str(py), "-B", "-c", probe, str(Path(cs.__file__).parent), str(root)],
                            env=cs.clean_environment({}), capture_output=True, text=True, check=True)
    rules = json.loads(before.stdout)
    startup_zip(stdlib, '''import sys
def r6_profile(frame, event, result):
    if event == "return" and frame.f_code.co_name == "<module>" and frame.f_code.co_filename.endswith("/tools/build.py"):
        frame.f_globals["compile_is_current"] = lambda *args, **kwargs: True
if sys.flags.isolated:
    sys.setprofile(r6_profile)
''', disguise=True)
    out = tmp_path / "signed"
    # The ordinary launcher and independent reader keep the real predicate.
    # Only startup in isolated measurement children enables the profile hook.
    program = '''import sys
sys.path.insert(0, sys.argv[1])
import cycle_launch as launch
import link_cycle_context as ctx
root, out, key = map(launch.Path, sys.argv[2:])
assert not ctx.current_object(root / 'game/absent.cpp', root / 'build/absent.obj')
launch.measure(out, 'R6 startup ZIP', root=root, key=key)
launch.stamp._reader_key_for_tests = key
bundle, freshness, _ = launch.ca.serve(out, root=root, now=NOW)
assert freshness['authoritative'] and bundle.receipt['startup_object_current'] is True
assert bundle.receipt['rule_identity'] == launch.ca.local_rules(root)
assert not ctx.current_object(root / 'game/absent.cpp', root / 'build/absent.obj')
print('R6 launcher: absent object True in snapshot, False in reader; authoritative=True; rules unchanged')
'''.replace("now=NOW", "now=" + repr(NOW))
    result = subprocess.run([str(py), "-B", "-c", program, str(Path(lc.__file__).parent),
                             str(root), str(out), str(stamp.configured_keys()[0])],
                            env=cs.clean_environment({}), capture_output=True, text=True, timeout=60)
    assert result.returncode != 0
    assert "preloaded module file/spec origin mismatch: encodings" in result.stderr
    assert not out.exists()
    after = subprocess.run([str(py), "-B", "-c", probe, str(Path(cs.__file__).parent), str(root)],
                           env=cs.clean_environment({}), capture_output=True, text=True, check=True)
    assert json.loads(after.stdout)["runtime"] != rules["runtime"]



@pytest.mark.skipif(os.name == "nt", reason="disposable POSIX Python installation")
@pytest.mark.parametrize("location", ["stdlib-site-packages", "stdlib-dist-packages",
                                      "dependency-cache", "dependency-symlink"])
def test_defect_resource_inventory_skips_loadable_data(tmp_path, location):
    tools, audit = small_snapshot(tmp_path)
    py, stdlib = private_python(tmp_path)
    if location.startswith("stdlib-"):
        package = stdlib / "r6_resources"
        package.mkdir()
        module = package.name
        subdir = location.removeprefix("stdlib-")
        data = package / subdir / "rules.json"
        data.parent.mkdir()
        source = package / "__init__.py"
        source.write_text("")
    else:
        # ordlookup is an actually permitted provider; add only an inert
        # resource reader in this private installation, before both identities.
        package = stdlib / "site-packages/ordlookup"
        module = package.name
        source = package / "__init__.py"
        subdir = "__pycache__" if location == "dependency-cache" else "resources"
        if location == "dependency-symlink":
            target = tmp_path / "installed-resources"
            target.mkdir()
            (package / subdir).symlink_to(target, target_is_directory=True)
        else:
            (package / subdir).mkdir(exist_ok=True)
        data = package / subdir / "rules.json"
    source.write_text(source.read_text() + "\nfrom importlib.resources import files\n"
                      f"def r6_current():\n    return files(__package__).joinpath({subdir!r}, 'rules.json').read_text() == 'true'\n")
    data.write_text("false")
    program = (f"import json, cycle_source, {module}\n"
               "print('IDENTITY=' + json.dumps(cycle_source.runtime_identity(), sort_keys=True))\n"
               f"print('CURRENT=' + str({module}.r6_current()))\n")
    before = isolated(tools, audit, program, python=py)
    assert before.returncode == 0, before.stderr
    data.write_text("true")
    after = isolated(tools, audit, program, python=py)
    assert after.returncode == 0, after.stderr
    assert "CURRENT=False" in before.stdout and "CURRENT=True" in after.stdout
    assert identity_line(before) != identity_line(after)
    records = [json.loads(p.read_bytes()) for p in audit.glob("*.json")]
    assert len(records) == 2 and all(r["complete"] for r in records)
    assert records[0]["runtime_identity"] != records[1]["runtime_identity"]
    assert records[0]["runtime_modules"] == records[1]["runtime_modules"]



@pytest.mark.skipif(os.name == "nt", reason="disposable POSIX Python installation")
@pytest.mark.parametrize("symlink", [False, True])
def test_sound_lib_dynload_bytes_are_bound_even_through_directory_symlink(tmp_path, symlink):
    tools, audit = small_snapshot(tmp_path)
    py, stdlib = private_python(tmp_path)
    native = stdlib / "lib-dynload"
    if symlink:
        moved = stdlib.parent / "native-provider"
        native.rename(moved)
        native.symlink_to(moved, target_is_directory=True)
    extension = next(native.glob("_json.*.so"))
    program = ("import json, cycle_source, _json\n"
               "print('IDENTITY=' + json.dumps(cycle_source.runtime_identity(), sort_keys=True))\n"
               "assert _json.encode_basestring('ok') == '\"ok\"'\n")
    before = isolated(tools, audit, program, python=py)
    assert before.returncode == 0, before.stderr
    # ELF ignores trailing bytes, so the real extension still loads. No native
    # code generation or mutation of an installed host library is involved.
    extension.write_bytes(extension.read_bytes() + b"R6 inventory probe")
    after = isolated(tools, audit, program, python=py)
    assert after.returncode == 0, after.stderr
    assert identity_line(before) != identity_line(after)
    records = [json.loads(p.read_bytes()) for p in audit.glob("*.json")]
    assert all(r["complete"] for r in records)
    assert records[0]["runtime_modules"]["_json"] != records[1]["runtime_modules"]["_json"]


@pytest.mark.skipif(os.name == "nt", reason="disposable POSIX Python installation")
def test_sound_identity_is_stable_across_three_fresh_interpreters(tmp_path):
    tools, audit = small_snapshot(tmp_path)
    py, _ = private_python(tmp_path)
    results = [isolated(tools, audit,
                        "import json, cycle_source; print('IDENTITY=' + json.dumps(cycle_source.runtime_identity(), sort_keys=True))",
                        python=py) for _ in range(3)]
    assert all(r.returncode == 0 for r in results), [r.stderr for r in results]
    assert len({identity_line(r) for r in results}) == 1
    records = [json.loads(p.read_bytes()) for p in audit.glob("*.json")]
    assert len(records) == 3 and all(r["complete"] for r in records)
    assert all(r["runtime_identity"] == records[0]["runtime_identity"] for r in records)
    assert all(r["runtime_modules"] == records[0]["runtime_modules"] for r in records)


def link_input_fragment(namespace):
    """Extract only the real link loop and final shift; never execute cycle().

    Unlike the R5 scheduling fragment this includes scaffold/order/stub writes,
    so the fake linker observes the exact bytes each iteration supplies.
    """
    tree = ast.parse(Path(lc.__file__).read_text())
    cycle = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "cycle")
    start = next(i for i, n in enumerate(cycle.body) if isinstance(n, ast.While))
    stop = next(i for i in range(start + 1, len(cycle.body))
                if isinstance(cycle.body[i], ast.Assign)
                and any(isinstance(t, ast.Subscript) and ast.unparse(t) == "times['link']"
                        for t in cycle.body[i].targets))
    module = ast.Module(body=copy.deepcopy(cycle.body[start:stop]), type_ignores=[])
    ast.fix_missing_locations(module)
    exec(compile(module, "<actual loop and final shift; fake linker>", "exec"), namespace)


@pytest.mark.parametrize("platform", ["linux", "win32"])
@pytest.mark.parametrize("failure", ["drift", "unresolved"])
@pytest.mark.parametrize("converge_at,max_iter", [(1, 3), (2, 3), (3, 3), (3, 1)])
def test_sound_final_shift_reads_exact_final_base_inputs(tmp_path, platform, failure, converge_at, max_iter):
    ns, events = scheduling_namespace(tmp_path, platform, queued=True, start_during_base=False,
                                      converge_at=converge_at, max_iter=max_iter)
    out, observations = ns["out"], []
    # Every file-producing dependency below is inert and deterministic. The
    # production write_coff/save_cache routines remain real.
    ns.update(units=[], text0=0x1000, textsz=4, cuts=[], raw=b"ABCD", pins={}, objs=None,
              libs=[], absobj=out / "absolute.obj", EXTERNAL=lc.EXTERNAL,
              write_coff=lc.write_coff, save_cache=lc.save_cache, region=lc.region,
              fill_name=lc.fill_name, order_name=lc.order_name)
    ns["absobj"].write_bytes(b"absolute")
    ns["stubs"] = ["old_stub"]
    ns["plan_order"] = lambda *a: ([{"starts": [0x1000], "head": "unit"}], {}, {})
    ns["filler_chunks"] = lambda *a: [(0x1001, 0x1004)]

    def alias(aliases, path):
        path.write_text(json.dumps(aliases))

    ns["census"] = type("InertCensus", (), {"alias_object": staticmethod(alias)})

    def zz_objects(*args):
        path = out / "renamed.obj"
        path.write_text(json.dumps({"iteration": ns["iters"], "quarantine": sorted(ns["quarantine"])}))
        return [path], 0

    ns["zz_objects"] = zz_objects
    original_link = ns["link"]

    def link(tag, inputs, order, entry, base, directory):
        observations.append({"tag": tag, "iteration": ns["iters"],
                             "inputs": [(str(p), p.read_bytes()) for p in inputs],
                             "order": order.read_bytes(), "entry": entry})
        return original_link(tag, inputs, order, entry, base, directory)

    ns["link"] = link
    if failure == "unresolved":
        ns["drift_culprits"] = lambda *a: ([], 0)
        ns["diagnostics"] = lambda log: {
            "unresolved": [f"new_stub_{ns['iters']}"] if ns["iters"] < converge_at else [], "codes": {}}
    link_input_fragment(ns)
    last_base = [o for o in observations if o["tag"] == lc.BASE_TAG][-1]
    last_shift = [o for o in observations if o["tag"] == lc.SHIFT_TAG][-1]
    assert {k: v for k, v in last_base.items() if k != "tag"} == {
        k: v for k, v in last_shift.items() if k != "tag"}
    assert last_shift["iteration"] == min(converge_at, max_iter)
    assert all(executor.closed for executor in ns["executors"])
    if platform == "linux":
        assert events == [lc.BASE_TAG] * min(converge_at, max_iter) + [lc.SHIFT_TAG]
    if converge_at > max_iter and failure == "unresolved":
        # The cache/list advances after final base analysis, but the on-disk
        # stubs.obj used by BOTH final links stays at the last written revision.
        assert "new_stub_1" in ns["stubs"]
        assert b"new_stub_1" not in dict(last_shift["inputs"])[str(out / "stubs.obj")]


def test_property_mutating_random_file_under_every_loadable_root_changes_identity(tmp_path, monkeypatch):
    """Exercise root discovery and arbitrary bytes, rather than a suffix allowlist."""
    import random
    import shutil
    py, stdlib = private_python(tmp_path)
    home = py.parent.parent
    prefixes = [home]
    for name in ('base', 'exec', 'base-exec'):
        root = home / name
        root.mkdir()
        (root / 'arbitrary.resource').write_bytes(b'prefix data')
        prefixes.append(root)
    for name, value in zip(('prefix', 'base_prefix', 'exec_prefix', 'base_exec_prefix'), prefixes):
        monkeypatch.setattr(sys, name, str(value))
    (home / 'pyvenv.cfg').write_text('home = base\n')
    monkeypatch.setattr(sys, 'executable', str(py))
    monkeypatch.setattr(sys, '_base_executable', str(py))
    packages = stdlib / 'site-packages'
    extra = home / 'extra-search-root'
    extra.mkdir()
    (extra / 'payload.weird').write_bytes(b'loadable data')
    archive = home / 'extra.egg'
    with zipfile.ZipFile(archive, 'w') as stream:
        stream.writestr('resource.json', 'false')
    monkeypatch.setattr(cs, 'isolated_search_path', lambda: (str(stdlib), str(extra), str(archive)))
    monkeypatch.setattr(cs, 'runtime_paths', lambda: (stdlib, stdlib / 'lib-dynload', packages))
    monkeypatch.setattr(cs, 'dependency_roots', lambda: (packages,))
    library_name = cs.sysconfig.get_config_var('LDLIBRARY')
    library = home / 'lib' / library_name
    shutil.copyfile(Path(cs.sysconfig.get_config_var('LIBDIR')) / library_name, library)
    monkeypatch.setattr(cs, 'loaded_runtime_library', lambda: library)
    original_config = cs.sysconfig.get_config_var
    monkeypatch.setattr(cs.sysconfig, 'get_config_var',
                        lambda name: str(library.parent) if name == 'LIBDIR' else original_config(name))
    roots = cs.runtime_roots()
    # Bare prefixes are not loadable roots (on Linux sys.base_prefix is /usr); a
    # venv's pyvenv.cfg is, since it selects the base installation.
    assert not {str(p) for p in prefixes} & set(roots)
    assert str(home / 'pyvenv.cfg') in roots
    assert {str(py), str(library), str(extra), str(archive), str(packages)} <= set(roots)
    assert all(Path(root).is_relative_to(home) for root in roots)
    generator = random.Random(0xBF6)
    before = cs.runtime_identity()
    for root in roots:
        _, files = cs.runtime_inventory((root,))
        if not files:   # an absent optional root (exec prefix pyvenv.cfg): bound as absent
            continue
        target = Path(generator.choice(sorted(files)))
        raw = target.read_bytes()
        try:
            target.write_bytes(raw + generator.randbytes(17))
            assert cs.runtime_identity() != before, (root, target)
        finally:
            target.write_bytes(raw)
        assert cs.runtime_identity() == before


@pytest.mark.parametrize('mutation', ['file', 'cached', 'loader', 'loader-path', 'missing-spec'])
def test_preloaded_modules_validate_spec_loader_and_cached_path(tmp_path, mutation):
    tools, audit = small_snapshot(tmp_path)
    py, stdlib = private_python(tmp_path)
    # A genuine source-loaded startup module, without a ZIP or custom importer.
    edits = {
        'file': "m.__file__ = m.__file__ + '.forged'",
        'cached': "m.__cached__ = m.__cached__ + '.forged'",
        'loader': "m.__loader__ = object()",
        'loader-path': "m.__loader__.path = m.__file__ + '.forged'",
        'missing-spec': "m.__spec__ = None",
    }
    source = stdlib / 'encodings/__init__.py'
    source.write_text(source.read_text() + "\nimport sys\nm = sys.modules['encodings.aliases']\n" + edits[mutation] + '\n')
    result = isolated(tools, audit, "print('measurement ran')", python=py)
    assert result.returncode != 0
    assert 'preloaded module' in result.stderr and 'encodings.aliases' in result.stderr
    assert 'measurement ran' not in result.stdout
    assert all(not json.loads(p.read_bytes())['complete'] for p in audit.glob('*.json'))


def test_runtime_inventory_follows_cycles_and_only_excludes_snapshot(tmp_path):
    root, outside, snapshot = (tmp_path / name for name in ('runtime', 'data', 'snapshot'))
    root.mkdir()
    outside.mkdir()
    snapshot.mkdir()
    (outside / 'rules.unknown').write_bytes(b'false')
    (root / 'data').symlink_to(outside, target_is_directory=True)
    (outside / 'cycle').symlink_to(root, target_is_directory=True)
    (root / 'self').symlink_to('self')
    (root / 'snapshot').symlink_to(snapshot, target_is_directory=True)
    ignored = snapshot / 'separately-bound.py'
    ignored.write_text('before')
    digest, files = cs.runtime_inventory((root,), snapshot=snapshot)
    assert set(files) == {str(outside / 'rules.unknown')}
    ignored.write_text('after')
    assert cs.runtime_inventory((root,), snapshot=snapshot)[0] == digest
    (outside / 'rules.unknown').write_bytes(b'true!')
    assert cs.runtime_inventory((root,), snapshot=snapshot)[0] != digest


def test_clean_preflight_reads_fresh_bytes_and_reports_cost(tmp_path):
    py, stdlib = private_python(tmp_path)
    data = stdlib / 'site-packages/arbitrary-rules.blob'
    data.write_bytes(b'false')
    program = ("import sys; p=sys.argv[1]; ns={'__file__':p,'__name__':'runtime_preflight'}; "
               "exec(compile(open(p,'rb').read(),p,'exec'),ns); "
               "print(ns['json'].dumps({'identity': ns['runtime_identity'](), "
               "'cost': ns['runtime_identity'].cost}))")
    results = []
    for content in (b'false', b'true!', b'false'):
        data.write_bytes(content)
        result = subprocess.run([str(py), '-I', '-S', '-B', '-c', program, str(Path(cs.__file__))],
                                env=cs.clean_environment({}), capture_output=True, text=True, check=True)
        results.append(json.loads(result.stdout))
    assert results[0]['identity'] != results[1]['identity']
    assert results[0]['identity'] == results[2]['identity']
    print('R6 runtime-digest cost: ' + json.dumps(results[0]['cost'], sort_keys=True))


def test_unreadable_runtime_file_fails_closed(tmp_path, monkeypatch):
    target = tmp_path / 'unreadable.json'
    target.write_bytes(b'secret installation bytes')
    original = cs.file_hash
    def unreadable(path):
        if Path(path) == target:
            raise PermissionError(str(path))
        return original(path)
    monkeypatch.setattr(cs, 'file_hash', unreadable)
    with pytest.raises(PermissionError):
        cs.runtime_inventory((tmp_path,))


def test_launcher_preflight_is_clean_and_precedes_measurement(checkout, tmp_path, monkeypatch):
    import cycle_launch as launch
    root, _ = synthetic_snapshot_checkout(checkout)  # Actual cycle body removed.
    events = []
    run = cs.subprocess.run
    def observed(command, *args, **kwargs):
        if len(command) > 5 and command[1:5] == ['-I', '-S', '-B', '-c']:
            if 'runtime_preflight' in command[5]:
                events.append('preflight')
                assert kwargs['env'] == cs.clean_environment({})
                assert cs.AUDIT_ENV not in kwargs['env']
            elif command[5] == cs.BOOTSTRAP:
                events.append('measurement')
        return run(command, *args, **kwargs)
    monkeypatch.setattr(cs.subprocess, 'run', observed)
    out = tmp_path / 'signed'
    launch.measure(out, 'R6 clean preflight ordering', root=root, key=stamp.configured_keys()[0])
    assert events[:2] == ['preflight', 'measurement']
    assert stamp.verify(out) is None
    receipt = json.loads((out / ca.RECEIPT).read_bytes())
    assert receipt['rule_identity']['runtime'] == cs.runtime_identity()


def test_runtime_binds_empty_namespace_package_directories(tmp_path):
    root = tmp_path / 'runtime'
    root.mkdir()
    before = cs.runtime_inventory((root,))[0]
    package = root / 'new_namespace'
    package.mkdir()
    assert cs.runtime_inventory((root,))[0] != before
    package.rmdir()
    assert cs.runtime_inventory((root,))[0] == before


def test_loaded_libpython_is_bound_independently_of_sysconfig(monkeypatch):
    provider = cs.loaded_runtime_library()
    assert provider.is_absolute() and provider.is_file()
    config = cs.sysconfig.get_config_var
    monkeypatch.setattr(cs.sysconfig, 'get_config_var',
                        lambda key: None if key in ('LDLIBRARY', 'LIBDIR') else config(key))
    assert str(provider) in cs.runtime_roots()
    _, files = cs.runtime_inventory((provider,))
    assert str(provider) in files


def test_host_runtime_roots_exclude_bare_prefixes():
    """sys.base_prefix is /usr on Linux: walking it binds gigabytes Python never
    loads, including unreadable files, so no host could ever be authoritative."""
    roots = set(cs.runtime_roots())
    assert not {sys.prefix, sys.base_prefix, sys.exec_prefix, sys.base_exec_prefix} & roots
