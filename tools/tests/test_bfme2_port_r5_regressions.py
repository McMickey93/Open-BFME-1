"""Round-5 regressions: reviewer names retained; assertions require the fixes.

Only inert Python children, temporary installations/keys, and extracted link
control flow with fake links. Never execute cycle(), Wine or a compiler/linker.
"""
import ast
import concurrent.futures
import copy
import json
import os
from pathlib import Path
import py_compile
import shutil
import subprocess
import sys
import sysconfig
import types

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import cycle_artifacts as ca
import cycle_launch as launch
import cycle_source as cs
import cycle_stamp as stamp
import link_cycle as lc
from cycle_fixture import NOW
from test_bfme2_port_r1_regressions import checkout, synthetic_snapshot_checkout
from test_bfme2_port_r2_regressions import commit_fixture
from test_bfme2_port_r4_regressions import small_snapshot


def isolated(tools, audit, program, *, python=None, timeout=45):
    command = cs.command(tools, program)
    if python:
        command[0] = str(python)
    return subprocess.run(command, env=cs.clean_environment({cs.AUDIT_ENV: str(audit)}),
                          cwd=tools.parent, capture_output=True, text=True, timeout=timeout)


@pytest.mark.parametrize("transport", ["process", "pool"])
def test_defect_cycle_build_pool_setting_rejects_spawn(tmp_path, transport):
    tools, audit = small_snapshot(tmp_path)
    (tools / "probe.py").write_text("def value():\n    return 7\n")
    tree = ast.parse(Path(lc.__file__).read_text())
    cycle = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "cycle")
    build_branch = next(n for n in cycle.body if isinstance(n, ast.If)
                        and ast.unparse(n.test) == "args.build")
    setting = next(n for n in build_branch.body if "os.environ.setdefault" in ast.unparse(n))
    program = "import os, multiprocessing, concurrent.futures, probe\n" + ast.unparse(setting) + "\n"
    if transport == "process":
        program += "p = multiprocessing.get_context('spawn').Process(target=probe.value)\np.start()\np.join()\nassert p.exitcode == 0\n"
    else:
        program += ("with concurrent.futures.ProcessPoolExecutor(1, mp_context=multiprocessing.get_context('spawn')) as pool:\n"
                    "    assert pool.submit(probe.value).result() == 7\n")
    result = isolated(tools, audit, program)
    assert result.returncode == 0, result.stdout + result.stderr
    assert cs.audit_modules(audit, roots=(tools,))
    records = [json.loads(p.read_bytes()) for p in audit.glob("*.json")]
    assert len(records) >= 3 and all(r["complete"] for r in records)


def test_defect_build_pool_breaks_actual_stale_selection(checkout, tmp_path):
    root, _ = checkout
    audit = tmp_path / "stale-selection-audit"
    audit.mkdir()
    program = '''import build, os
os.environ.setdefault('BUILD_POOL', str(max(1, (os.cpu_count() or 2) - 2)))
sources = [build.ROOT / 'game' / ('missing%d.cpp' % i) for i in range(200)]
outputs = {source: build.ROOT / 'build' / ('missing%d.obj' % i) for i, source in enumerate(sources)}
# Missing objects fail preflight before any compiler or winepath discovery.
assert all(not path.exists() for path in outputs.values())
assert set(build.stale_sources(sources, outputs, workers=2)) == set(sources)
'''
    result = isolated(root / "tools", audit, program)
    assert result.returncode == 0, result.stdout + result.stderr
    assert cs.audit_modules(audit, roots=(root / "tools",))
    assert len(list(audit.glob("*.json"))) >= 4


def link_fragment(source, namespace):
    """Compile only the scheduling/convergence statements, never cycle()."""
    cycle = next(n for n in ast.parse(source).body if isinstance(n, ast.FunctionDef) and n.name == "cycle")
    loop = next(n for n in cycle.body if isinstance(n, ast.While))
    start = next(i for i, n in enumerate(loop.body) if isinstance(n, ast.Assign)
                 and any(isinstance(t, ast.Name) and t.id == "shift" for t in n.targets))
    loop = copy.deepcopy(loop)
    loop.body = ast.parse("iters += 1").body + loop.body[start:]
    after = next(n for n in cycle.body if isinstance(n, (ast.Assign, ast.If))
                 and any(isinstance(t, ast.Name) and t.id == "shift_res" and isinstance(t.ctx, ast.Store)
                         for t in ast.walk(n)))
    module = ast.Module(body=[loop, copy.deepcopy(after)], type_ignores=[])
    ast.fix_missing_locations(module)
    exec(compile(module, "<actual link scheduling fragment, fake link>", "exec"), namespace)


def scheduling_namespace(tmp_path, platform, *, converge_at=2, max_iter=3, shift_base=lc.SHIFT_BASE,
                         queued=False, start_during_base=True):
    events, pending, executors = [], [], []
    out = tmp_path / "run"
    out.mkdir(parents=True)
    (out / "base.map").write_text("synthetic map")

    def link(tag, *args):
        events.append(tag)
        # A worker queued before a slow base link has started by its completion.
        # A worker queued AFTER the base may legally still be pending when the
        # immediately following map/convergence checks finish.
        if tag == lc.BASE_TAG and start_during_base:
            for future, fn, argv in pending:
                if not future.done() and future.set_running_or_notify_cancel():
                    future.set_result(fn(*argv))
        return "synthetic", 0, 1

    class Executor:
        def __init__(self, workers):
            assert workers == 1
            self.closed = False
            executors.append(self)

        def shutdown(self, wait):
            assert wait
            for future, fn, argv in pending:
                if not future.done() and future.set_running_or_notify_cancel():
                    try:
                        future.set_result(fn(*argv))
                    except Exception as error:
                        future.set_exception(error)
            self.closed = True

        def submit(self, fn, *argv):
            future = concurrent.futures.Future()
            if queued:
                pending.append((future, fn, argv))
            else:
                try:
                    future.set_result(fn(*argv))
                except Exception as error:
                    future.set_exception(error)
            return future

    namespace = dict(args=types.SimpleNamespace(shift_base=shift_base, max_iter=max_iter),
                     concurrent=types.SimpleNamespace(futures=types.SimpleNamespace(ThreadPoolExecutor=Executor)),
                     sys=types.SimpleNamespace(platform=platform), link=link,
                     BASE=lc.BASE, BASE_TAG=lc.BASE_TAG, SHIFT_TAG=lc.SHIFT_TAG,
                     inputs=[], order=out / "order.txt", entry="_f", out=out, items=[], placed=[],
                     iters=0, history=[], quarantine=set(), stubs=[], obj_digest="synthetic",
                     sfile=out / "stubs.json", qfile=out / "quarantine.json",
                     diagnostics=lambda log: {"unresolved": [], "codes": {}},
                     zz_names=lambda out: ({}, []), read_map=lambda *a: ({}, {}),
                     save_cache=lambda *a: None, executors=executors)
    namespace["drift_culprits"] = lambda *a: ((["drifter"] if namespace["iters"] < converge_at else []), 0)
    return namespace, events


@pytest.mark.parametrize("platform", ["linux", "win32"])
@pytest.mark.parametrize("failure", ["drift", "unresolved"])
@pytest.mark.parametrize("start_during_base", [False, True])
def test_defect_serial_shift_cancellation_aborts_convergence(tmp_path, failure, platform, start_during_base):
    namespace, events = scheduling_namespace(tmp_path, platform, queued=True,
                                             start_during_base=start_during_base)
    if failure == "unresolved":
        namespace["drift_culprits"] = lambda *a: ([], 0)
        namespace["diagnostics"] = lambda log: {
            "unresolved": ["new_stub"] if namespace["iters"] == 1 else [], "codes": {}}
    link_fragment(Path(lc.__file__).read_text(), namespace)
    assert namespace["iters"] == 2
    assert namespace["quarantine"] == ({"drifter"} if failure == "drift" else set())
    assert namespace["stubs"] == (["new_stub"] if failure == "unresolved" else [])
    if platform == "linux":
        assert events == [lc.BASE_TAG, lc.BASE_TAG, lc.SHIFT_TAG]
    elif start_during_base:
        assert events == [lc.BASE_TAG, lc.SHIFT_TAG, lc.BASE_TAG, lc.SHIFT_TAG]
    else:
        # First shift cancelled while queued; final shift completed at shutdown.
        assert events == [lc.BASE_TAG, lc.BASE_TAG, lc.SHIFT_TAG]
    assert namespace["shift_res"] == ("synthetic", 0, 1)
    assert all(executor.closed for executor in namespace["executors"])


@pytest.mark.parametrize("platform", ["linux", "win32"])
@pytest.mark.parametrize("failure", ["drift", "unresolved"])
@pytest.mark.parametrize("queued", [False, True])
@pytest.mark.parametrize("converge_at,max_iter,shift_base", [(1, 3, lc.SHIFT_BASE), (2, 3, lc.SHIFT_BASE),
                                                           (3, 1, lc.SHIFT_BASE), (1, 3, None)])
def test_sound_shift_scheduling_preserves_completed_results(tmp_path, platform, failure, queued,
                                                           converge_at, max_iter, shift_base):
    namespace, events = scheduling_namespace(tmp_path, platform, converge_at=converge_at,
                                             max_iter=max_iter, shift_base=shift_base, queued=queued,
                                             start_during_base=False)
    if failure == "unresolved":
        namespace["drift_culprits"] = lambda *a: ([], 0)
        namespace["diagnostics"] = lambda log: {
            "unresolved": ["new_stub"] if namespace["iters"] < converge_at else [], "codes": {}}
    link_fragment(Path(lc.__file__).read_text(), namespace)
    count = min(converge_at, max_iter)
    if not shift_base:
        expected = [lc.BASE_TAG] * count
    elif platform == "win32" and not queued:
        expected = [lc.SHIFT_TAG, lc.BASE_TAG] * count
    else:
        expected = [lc.BASE_TAG] * count + [lc.SHIFT_TAG]
    assert events == expected
    assert namespace["iters"] == count
    assert (namespace["shift_res"] is not None) == bool(shift_base)
    assert namespace["quarantine"] == ({"drifter"} if count > 1 and failure == "drift" else set())
    assert namespace["stubs"] == (["new_stub"] if failure == "unresolved" and converge_at > 1 else [])
    assert all(executor.closed for executor in namespace["executors"])


@pytest.mark.parametrize("failure", ["base", "map", "analysis", "shift"])
def test_shift_executor_is_joined_on_failure(tmp_path, failure):
    namespace, events = scheduling_namespace(tmp_path, "win32", queued=True, start_during_base=False)
    if failure in ("base", "shift"):
        link = namespace["link"]
        def fail(tag, *args):
            if tag == (lc.BASE_TAG if failure == "base" else lc.SHIFT_TAG):
                raise RuntimeError("synthetic link failure")
            return link(tag, *args)
        namespace["link"] = fail
    elif failure == "map":
        (namespace["out"] / "base.map").unlink()
    else:
        def fail(*args):
            raise RuntimeError("synthetic map analysis failure")
        namespace["read_map"] = fail
    with pytest.raises((RuntimeError, SystemExit)):
        link_fragment(Path(lc.__file__).read_text(), namespace)
    assert all(executor.closed for executor in namespace["executors"])


def private_python(tmp_path):
    """A disposable stdlib, executable and dependency installation; no host writes."""
    home = tmp_path / "private-python"
    executable = home / "bin/python"
    executable.parent.mkdir(parents=True)
    shutil.copy2(Path(sys.executable).resolve(), executable)
    stdlib = home / "lib" / f"python{sys.version_info.major}.{sys.version_info.minor}"
    shutil.copytree(sysconfig.get_path("stdlib"), stdlib,
                    ignore=shutil.ignore_patterns("site-packages", "dist-packages", "__pycache__", "test", "tests"))
    packages = stdlib / "site-packages"
    packages.mkdir()
    for name, source in cs.dependency_locations().items():
        if source.is_dir():
            shutil.copytree(source, packages / name, ignore=shutil.ignore_patterns("__pycache__"))
        elif source.is_file():
            shutil.copy2(source, packages / name)
    return executable, stdlib


def encoding_bytecode(stdlib, hook):
    encoding = stdlib / "encodings/__init__.py"
    raw = encoding.read_bytes()
    try:
        encoding.write_bytes(raw + b"\n" + hook.encode())
        py_compile.compile(str(encoding), doraise=True, invalidation_mode=py_compile.PycInvalidationMode.UNCHECKED_HASH)
    finally:
        encoding.write_bytes(raw)


@pytest.mark.skipif(os.name == "nt", reason="disposable POSIX Python layout")
def test_defect_prebootstrap_encoding_bytecode_is_outside_runtime_identity(tmp_path):
    tools, audit = small_snapshot(tmp_path)
    py, stdlib = private_python(tmp_path)
    program = "import cycle_source; print('IDENTITY=' + json.dumps(cycle_source.runtime_identity(), sort_keys=True)); print('POISON=' + str(getattr(sys, 'r5_encoding_hook', False)))"
    # json is imported into cycle_source's namespace, not the -c namespace.
    program = "import json\n" + program
    first = isolated(tools, audit, program, python=py)
    assert first.returncode == 0, first.stderr
    encoding_bytecode(stdlib, "import sys\nsys.r5_encoding_hook = True\n")
    second = isolated(tools, audit, program, python=py)
    assert second.returncode == 0, second.stderr
    identity = lambda result: next(line for line in result.stdout.splitlines() if line.startswith("IDENTITY="))
    assert identity(first) != identity(second)
    assert "POISON=False" in first.stdout and "POISON=True" in second.stdout
    records = [json.loads(p.read_bytes()) for p in audit.glob("*.json")]
    assert all(r["complete"] for r in records)
    assert all(r["runtime_modules"]["encodings"]["origin"] == "stdlib/encodings/__init__.py"
               for r in records)
    assert records[0]["runtime_identity"] != records[1]["runtime_identity"]
    for record in records:
        assert {"__main__", "sys", "encodings", "encodings.aliases", "encodings.utf_8"} <= record["runtime_modules"].keys()


@pytest.mark.skipif(os.name == "nt", reason="disposable POSIX Python layout")
def test_defect_launcher_signs_changed_predicate_from_startup_bytecode(checkout, tmp_path):
    root, _ = synthetic_snapshot_checkout(checkout)
    driver = root / "tools/link_cycle.py"
    driver.write_text(driver.read_text().replace(
        '    receipt["synthetic_execution"] = ',
        '    receipt["startup_object_current"] = context.current_object(ROOT / "game/absent.cpp", ROOT / "build/absent.obj")\n'
        '    receipt["synthetic_execution"] = '))
    commit_fixture(root, "inert R5 object currency probe; real cycle removed")
    py, stdlib = private_python(tmp_path)
    clean = subprocess.run([str(py), "-B", "-c",
                            "import sys, json; sys.path.insert(0, sys.argv[1]); import cycle_source; "
                            "print(json.dumps(cycle_source.runtime_identity()))", str(Path(cs.__file__).parent)],
                           env=cs.clean_environment({}), capture_output=True, text=True, check=True)
    clean_runtime = json.loads(clean.stdout)
    encoding_bytecode(stdlib, '''import sys
def r5_profile(frame, event, result):
    if event == "return" and frame.f_code.co_name == "<module>" and frame.f_code.co_filename.endswith("/tools/build.py"):
        frame.f_globals["compile_is_current"] = lambda *args, **kwargs: True
if sys.flags.isolated:
    sys.setprofile(r5_profile)
''')
    out = tmp_path / "signed"
    # Ordinary launcher/reader are not poisoned. Only its actual isolated
    # children activate the hook; no key or authority/audit function is changed.
    program = '''import sys
sys.path.insert(0, sys.argv[1])
import cycle_launch as launch
import link_cycle_context as ctx
root, out, key = map(launch.Path, sys.argv[2:])
before = launch.ca.local_rules(root)
assert not ctx.current_object(root / 'game/absent.cpp', root / 'build/absent.obj')
launch.measure(out, 'R5 startup bytecode', root=root, key=key)
launch.stamp._reader_key_for_tests = key
bundle, freshness, _ = launch.ca.serve(out, root=root, now=NOW)
assert freshness['authoritative'] and bundle.receipt['startup_object_current'] is True
assert before == bundle.receipt['rule_identity'] == launch.ca.local_rules(root)
assert not ctx.current_object(root / 'game/absent.cpp', root / 'build/absent.obj')
print('R5 launcher: changed runtime identity recorded before measurement')
'''.replace("now=NOW", "now=" + repr(NOW))
    result = subprocess.run([str(py), "-B", "-c", program, str(Path(lc.__file__).parent),
                             str(root), str(out), str(stamp.configured_keys()[0])],
                            env=cs.clean_environment({}), capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, result.stdout + result.stderr
    assert stamp.verify(out) is None
    receipt = json.loads((out / ca.RECEIPT).read_bytes())
    assert receipt["rule_identity"]["runtime"] != clean_runtime
    assert receipt["runtime_modules"]["encodings"]["origin"] == "stdlib/encodings/__init__.py"
    with pytest.raises(ca.Refused) as refused:
        ca.serve(out, root=root, now=NOW)
    assert refused.value.reason == "incompatible-rules"


@pytest.mark.skipif(os.name == "nt", reason="disposable POSIX Python layout")
def test_defect_stdlib_resource_changes_behavior_without_rule_change(tmp_path):
    tools, audit = small_snapshot(tmp_path)
    py, stdlib = private_python(tmp_path)
    package = stdlib / "r5_resource_provider"
    package.mkdir()
    (package / "__init__.py").write_text(
        "from importlib.resources import files\n"
        "def current():\n    return files(__package__).joinpath('rules.json').read_text() == 'true'\n")
    data = package / "rules.json"
    data.write_text("false")
    program = ("import json, cycle_source, r5_resource_provider\n"
               "print('IDENTITY=' + json.dumps(cycle_source.runtime_identity(), sort_keys=True))\n"
               "print('CURRENT=' + str(r5_resource_provider.current()))\n")
    before = isolated(tools, audit, program, python=py)
    assert before.returncode == 0, before.stderr
    data.write_text("true")
    after = isolated(tools, audit, program, python=py)
    assert after.returncode == 0, after.stderr
    identity = lambda result: next(line for line in result.stdout.splitlines() if line.startswith("IDENTITY="))
    assert identity(before) != identity(after)
    assert "CURRENT=False" in before.stdout and "CURRENT=True" in after.stdout
    records = [json.loads(p.read_bytes()) for p in audit.glob("*.json")]
    assert all(r["complete"] for r in records)
    assert records[0]["runtime_modules"] == records[1]["runtime_modules"]
    assert records[0]["runtime_identity"] != records[1]["runtime_identity"]


def test_sound_sys_executable_script_helper_has_its_own_complete_record(tmp_path):
    tools, audit = small_snapshot(tmp_path)
    (tools / "probe.py").write_text('''if __name__ == '__main__':
    import sys, os
    assert sys.flags.isolated and sys.flags.no_site and sys.flags.dont_write_bytecode
    assert 'CL' not in os.environ and 'LD_PRELOAD' not in os.environ
    print('inert helper audited')
''')
    result = isolated(tools, audit, '''import subprocess
subprocess.run([sys.executable, str(tools / 'probe.py')], check=True,
               env={'PATH': '/caller/poison', 'CL': '/DPOISON', 'LD_PRELOAD': '/caller/poison.so'})
''')
    assert result.returncode == 0, result.stderr
    assert "inert helper audited" in result.stdout
    records = [json.loads(p.read_bytes()) for p in audit.glob("*.json")]
    assert len(records) == 2 and all(r["complete"] for r in records)
    assert records[0]["modules"] == records[1]["modules"]


@pytest.mark.skipif(os.name == "nt", reason="POSIX forkserver transport")
def test_sound_forkserver_fails_closed_before_unrecorded_worker(tmp_path):
    tools, audit = small_snapshot(tmp_path)
    marker = tools.parent / "worker-ran"
    (tools / "probe.py").write_text(f"def work():\n    open({str(marker)!r}, 'w').close()\n")
    result = isolated(tools, audit, '''import multiprocessing, probe
try:
    process = multiprocessing.get_context('forkserver').Process(target=probe.work)
    process.start()
    process.join()
except ValueError as error:
    print(str(error))
''')
    assert result.returncode == 0, result.stderr
    assert "unbootstrapped multiprocessing program" in result.stdout
    assert not marker.exists()
    with pytest.raises(ValueError, match="incomplete"):
        cs.audit_modules(audit, roots=(tools,))


@pytest.mark.parametrize("absolute", [False, True])
def test_sound_native_library_outside_dependency_is_refused(tmp_path, absolute):
    tools, audit = small_snapshot(tmp_path)
    native = tools.parent / "untracked.so"
    native.write_bytes(b"inert; must be refused before loading")
    name = str(native) if absolute else native.name
    result = isolated(tools, audit, f"import ctypes\nctypes.CDLL({name!r})")
    assert result.returncode != 0
    assert "non-canonical snapshot module origin: native library" in result.stderr
    with pytest.raises(ValueError, match="incomplete"):
        cs.audit_modules(audit, roots=(tools,))


@pytest.mark.skipif(os.name == "nt", reason="POSIX fixed executable lookup")
def test_sound_launcher_drops_compiler_wine_loader_and_path_environment(checkout, tmp_path, monkeypatch):
    root, _ = synthetic_snapshot_checkout(checkout)
    driver = root / "tools/link_cycle.py"
    insertion = '''    import shutil
    from unittest.mock import patch
    # Path conversion alone is replaced; no winepath or Wine is started.
    with patch.object(build, 'wine_path', lambda path: 'Z:' + str(path).replace('/', chr(92))):
        compiler_env = build.compiler_environment(ROOT / 'inputs/toolchains/vc71')
    receipt['r5_environment'] = compiler_env
    receipt['r5_which'] = {name: shutil.which(name) for name in ('wine', 'winepath')}
'''
    # unittest.mock is a stdlib dependency; all local providers remain canonical.
    driver.write_text(driver.read_text().replace('    bind_evidence(run, receipt, ROOT)\n',
                                                insertion + '    bind_evidence(run, receipt, ROOT)\n'))
    commit_fixture(root, "inert environment and executable lookup probe")
    poison = tmp_path / "caller-bin"
    poison.mkdir()
    for name in ("wine", "winepath"):
        executable = poison / name
        executable.write_text("#!/bin/sh\nexit 99\n")
        executable.chmod(0o700)
    contaminated = ("CL", "_CL_", "LINK", "_LINK_", "INCLUDE", "LIB", "WINEPREFIX", "WINEPATH",
                    "WINEDLLOVERRIDES", "WINEDLLPATH", "WINELOADER", "WINESERVER", "WINEARCH",
                    "LD_PRELOAD", "LD_LIBRARY_PATH", "DYLD_INSERT_LIBRARIES", "VC71_ROOT", "STLPORT_ROOT")
    for name in contaminated:
        monkeypatch.setenv(name, "R5_CALLER_POISON")
    monkeypatch.setenv("PATH", str(poison) + os.pathsep + os.defpath)
    out = tmp_path / "env-bundle"
    launch.measure(out, "R5 environment", root=root, key=stamp.configured_keys()[0])
    bundle, freshness, _ = ca.serve(out, root=root, now=NOW)
    assert freshness["authoritative"]
    env = bundle.receipt["r5_environment"]
    assert env["PATH"] == os.defpath
    assert all("R5_CALLER_POISON" not in value for value in env.values())
    assert not (set(contaminated) - {"INCLUDE", "LIB", "WINEPATH"}) & set(env)
    for name, selected in bundle.receipt["r5_which"].items():
        assert selected == shutil.which(name, path=os.defpath)
        assert selected is None or not Path(selected).is_relative_to(poison)


@pytest.mark.parametrize("kind", ["data", "native"])
def test_sound_package_resources_and_native_bytes_change_runtime_identity(tmp_path, monkeypatch, kind):
    stdlib, packages = tmp_path / "stdlib", tmp_path / "site-packages"
    stdlib.mkdir()
    package = packages / "capstone"
    package.mkdir(parents=True)
    (package / "__init__.py").write_text("# inert installation")
    data = package / ("rules.json" if kind == "data" else "libcapstone.so")
    data.write_bytes(b"before")
    monkeypatch.setattr(cs, "runtime_paths", lambda: (stdlib, stdlib / "lib-dynload", packages))
    monkeypatch.setattr(cs, "dependency_locations", lambda: {"capstone": package})
    before = cs.runtime_identity()
    data.write_bytes(b"after")
    assert cs.runtime_identity() != before


@pytest.mark.parametrize('relative', ['encodings/__pycache__/__init__.pyc', 'provider/rules.json',
                                      'test/payload.bin', 'tests/sample.dat', 'source.py',
                                      '../native/provider.pyd', '../bin/python', '../lib/libpython.so'])
def test_runtime_inventory_binds_all_stdlib_and_interpreter_inputs(tmp_path, monkeypatch, relative):
    stdlib, native, packages = tmp_path / 'stdlib', tmp_path / 'native', tmp_path / 'stdlib/site-packages'
    for path in (stdlib, native, packages, tmp_path / 'bin', tmp_path / 'lib'):
        path.mkdir(parents=True, exist_ok=True)
    executable, library = tmp_path / 'bin/python', tmp_path / 'lib/libpython.so'
    executable.write_bytes(b'inert interpreter')
    library.write_bytes(b'inert shared runtime')
    monkeypatch.setattr(cs, 'runtime_paths', lambda: (stdlib, native, packages))
    monkeypatch.setattr(cs, 'dependency_locations', lambda: {})
    monkeypatch.setattr(sys, 'executable', str(executable))
    monkeypatch.setattr(sys, '_base_executable', str(executable))
    monkeypatch.setattr(sys, 'base_prefix', str(tmp_path))
    values = {'LDLIBRARY': library.name, 'LIBDIR': str(library.parent)}
    monkeypatch.setattr(cs.sysconfig, 'get_config_var', values.get)
    target = stdlib / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(b'before')
    before = cs.runtime_identity()
    target.write_bytes(b'after!')  # Same size still invalidates the in-memory cache.
    changed = cs.runtime_identity()
    assert changed != before
    # Undeclared packages cannot enter through the stdlib inventory.
    ignored = packages / 'not_a_provider'
    ignored.mkdir()
    (ignored / 'rules.json').write_bytes(b'caller data')
    assert cs.runtime_identity() == changed
    (ignored / 'rules.json').write_bytes(b'changed caller data')
    assert cs.runtime_identity() == changed


@pytest.mark.parametrize('contamination', [{'BUILD_POOL': '0'}, {'BUILD_POOL': '-1'},
                                          {'BUILD_POOL': '2', 'CL': '/DPOISON'},
                                          {'BUILD_POOL': '2', 'PYTHONPATH': '/poison'}])
def test_spawn_guard_still_refuses_caller_environment(tmp_path, contamination):
    tools, audit = small_snapshot(tmp_path)
    (tools / 'probe.py').write_text('def value():\n    return 7\n')
    assert 'BUILD_POOL' not in cs.clean_environment({'BUILD_POOL': '999'})
    program = f'''import multiprocessing, os, probe
os.environ.update({contamination!r})
p = multiprocessing.get_context('spawn').Process(target=probe.value)
p.start()
'''
    result = isolated(tools, audit, program)
    assert result.returncode != 0
    assert 'unbootstrapped multiprocessing environment' in result.stderr
    with pytest.raises(ValueError, match='incomplete'):
        cs.audit_modules(audit, roots=(tools,))


def test_recorder_inventories_every_prebootstrap_module(tmp_path):
    tools, audit = small_snapshot(tmp_path)
    command = cs.command(tools, "import json; print(json.dumps(r5_startup_names))")
    command[5] = command[5].replace('import sys\n', 'import sys\nr5_startup_names = tuple(sys.modules)\n', 1)
    result = subprocess.run(command, env=cs.clean_environment({cs.AUDIT_ENV: str(audit)}),
                            cwd=tools.parent, capture_output=True, text=True, timeout=45)
    assert result.returncode == 0, result.stdout + result.stderr
    startup = set(json.loads(result.stdout))
    records = list(audit.glob('*.json'))
    assert len(records) == 1
    record = json.loads(records[0].read_bytes())
    assert record['complete']
    assert startup <= record['runtime_modules'].keys()
    assert all(entry['origin'] and len(entry['sha256']) == 64
               for entry in record['runtime_modules'].values())


def test_installed_hash_cache_is_memory_only_and_invalidates_on_file_generation(tmp_path, monkeypatch):
    path = tmp_path / 'rules.json'
    path.write_bytes(b'before')
    read_bytes = Path.read_bytes
    reads = []
    def read(candidate):
        if candidate == path:
            reads.append(candidate)
        return read_bytes(candidate)
    monkeypatch.setattr(Path, 'read_bytes', read)
    before = cs.file_hash(path)
    assert cs.file_hash(path) == before
    assert len(reads) == 1
    path.write_bytes(b'after!')
    assert cs.file_hash(path) != before
    assert len(reads) == 2
    # A fresh process must read its own bytes, even for a previously cached path.
    code = ('import sys; sys.path.insert(0, sys.argv[1]); import cycle_source; '
            'print(cycle_source.file_hash(sys.argv[2]))')
    result = subprocess.run([sys.executable, '-I', '-S', '-B', '-c', code, str(Path(cs.__file__).parent), str(path)],
                            capture_output=True, text=True, check=True)
    assert result.stdout.strip() == cs.file_hash(path)
