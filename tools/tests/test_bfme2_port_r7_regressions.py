"""Round 7 review reproductions and controls; no game build or real cycle.

Defect cases now require observed runtime binding or refusal. Python
installations, native fixtures, snapshots and signing keys are disposable.
The tiny ELF fixtures use the host C compiler, never cl.exe/link.exe or Wine.
"""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import cycle_source as cs
import cycle_stamp as stamp
from cycle_fixture import NOW
from test_bfme2_port_r1_regressions import checkout, synthetic_snapshot_checkout
from test_bfme2_port_r2_regressions import commit_fixture
from test_bfme2_port_r4_regressions import small_snapshot
from test_bfme2_port_r5_regressions import isolated, private_python

pytestmark = pytest.mark.skipif(sys.platform != "linux", reason="private Linux installation/ELF fixtures")


def fresh(py, program, *args):
    return subprocess.run([str(py), "-I", "-S", "-B", "-c", program, *map(str, args)],
                          env=cs.clean_environment({}), capture_output=True, text=True,
                          check=True, timeout=60)


def identity(py):
    program = ("import sys,json; p=sys.argv[1]; ns={'__file__':p,'__name__':'r7_preflight'}; "
               "exec(compile(open(p,'rb').read(),p,'exec'),ns); "
               "print(json.dumps({'identity':ns['runtime_identity'](), 'roots':ns['runtime_roots']()}))")
    return json.loads(fresh(py, program, cs.__file__).stdout)


def observation(result):
    assert result.returncode == 0, result.stdout + result.stderr
    return json.loads(next(line.removeprefix("OBSERVATION=") for line in result.stdout.splitlines()
                           if line.startswith("OBSERVATION=")))


def completed(audit):
    records = [json.loads(path.read_bytes()) for path in audit.glob("*.json")]
    assert records and all(record["complete"] for record in records)
    return records


def native_fixture(tmp_path, stdlib):
    """A declared package's immutable bridge has a real, private RUNPATH edge.

    The dependency lives directly under this Python installation's lib/, not
    in libc/libssl or any other excluded OS installation. Only its bytes vary.
    """
    compiler = shutil.which("cc", path=os.defpath)
    if not compiler:
        pytest.skip("native fixture needs a host C compiler")
    build = tmp_path / "native-fixture-build"
    build.mkdir()
    versions = []
    for value in (0, 1):
        source = build / f"leaf{value}.c"
        source.write_text(f"int r7_current(void) {{ return {value}; }}\n")
        output = build / f"leaf{value}.so"
        subprocess.run([compiler, "-shared", "-fPIC", "-Wl,-soname,libr7leaf.so",
                        str(source), "-o", str(output)], check=True, capture_output=True)
        versions.append(output)
    leaf = stdlib.parent / "libr7leaf.so"
    shutil.copyfile(versions[0], leaf)
    source = build / "bridge.c"
    source.write_text("extern int r7_current(void);\nint r7_bridge(void) { return r7_current(); }\n")
    bridge = stdlib / "site-packages/capstone/r7bridge.so"
    subprocess.run([compiler, "-shared", "-fPIC", str(source), "-L" + str(leaf.parent),
                    "-lr7leaf", "-Wl,-rpath,$ORIGIN/../../..", "-o", str(bridge)],
                   check=True, capture_output=True)
    return bridge, leaf, versions


def test_defect_transitive_native_library_outside_roots_keeps_identity(tmp_path):
    tools, audit = small_snapshot(tmp_path)
    py, stdlib = private_python(tmp_path)
    bridge, leaf, versions = native_fixture(tmp_path, stdlib)
    program = f'''import ctypes, cycle_source, json
provider = ctypes.CDLL({str(bridge)!r})
assert {str(leaf)!r} not in cycle_source.runtime_inventory(cycle_source.runtime_roots())[1]
print('OBSERVATION=' + json.dumps({{'current': bool(provider.r7_bridge()),
                                  'identity': cycle_source.runtime_identity()}}))
'''
    before = observation(isolated(tools, audit, program, python=py))
    shutil.copyfile(versions[1], leaf)
    after = observation(isolated(tools, audit, program, python=py))
    assert before["current"] is False and after["current"] is True
    assert before["identity"] == after["identity"]  # Static installation inventory alone is unchanged.
    records = completed(audit)
    assert len(records) == 2 and records[0]["runtime_modules"] == records[1]["runtime_modules"]
    assert "capstone.__native__.r7bridge.so" in records[0]["runtime_modules"]
    assert records[0]["runtime_evidence"]["mapped_files"][str(leaf)] != records[1]["runtime_evidence"]["mapped_files"][str(leaf)]
    print("R7 native: private lib/libr7leaf.so changes False -> True; mapped runtime evidence changes; complete module records unchanged")


def test_defect_launcher_signs_native_predicate_under_unchanged_rules(checkout, tmp_path):
    root, _ = synthetic_snapshot_checkout(checkout)  # Physically removes cycle().
    driver = root / "tools/link_cycle.py"
    driver.write_text(driver.read_text().replace(
        '    receipt["synthetic_execution"] = ',
        '    receipt["startup_object_current"] = context.current_object(ROOT / "game/absent.cpp", ROOT / "build/absent.obj")\n'
        '    receipt["synthetic_execution"] = '))
    commit_fixture(root, "inert R7 native predicate probe; real cycle removed")
    py, stdlib = private_python(tmp_path)
    bridge, leaf, versions = native_fixture(tmp_path, stdlib)
    startup = stdlib / "encodings/__init__.py"
    # One fixed installed provider before BOTH identities. No auditor, digest,
    # signer or origin/loader metadata is patched; only the real currency
    # predicate gets the inert native result when its canonical module loads.
    startup.write_text(startup.read_text() + f'''
import sys
def r7_profile(frame, event, result):
    if event == 'return' and frame.f_code.co_name == '<module>' and frame.f_code.co_filename.endswith('/tools/build.py'):
        import ctypes
        bridge = ctypes.CDLL({str(bridge)!r})
        frame.f_globals['compile_is_current'] = lambda *a, **kw: bool(bridge.r7_bridge())
if sys.flags.isolated:
    sys.setprofile(r7_profile)
''')
    program = '''import sys, json, shutil
sys.path.insert(0, sys.argv[1])
import cycle_launch as launch
import link_cycle_context as ctx
root, out, key, leaf, v0, v1 = map(launch.Path, sys.argv[2:])
launch.stamp._reader_key_for_tests = key
rules = launch.ca.local_rules(root)
observed = []
for value, source in enumerate((v0, v1)):
    shutil.copyfile(source, leaf)
    assert launch.ca.local_rules(root) == rules
    assert not ctx.current_object(root / 'game/absent.cpp', root / 'build/absent.obj')
    bundle_path = out / str(value)
    launch.measure(bundle_path, 'R7 native dependency', root=root, key=key)
    bundle, freshness, _ = launch.ca.serve(bundle_path, root=root, now=NOW)
    assert freshness['authoritative']
    assert bundle.receipt['rule_identity'] == rules
    observed.append(bundle.receipt['startup_object_current'])
    if value:
        try:
            launch.ca.serve(out / '0', root=root, now=NOW)
        except launch.ca.Refused as error:
            assert error.reason == 'incompatible-rules'
        else:
            raise AssertionError('old mapped runtime accepted after leaf mutation')
        old = launch.ca.read_json(out / '0' / launch.ca.RECEIPT)
        assert old['runtime_evidence']['mapped_files'][str(leaf)] != bundle.receipt['runtime_evidence']['mapped_files'][str(leaf)]
assert observed == [False, True]
print('R7 launcher: absent object False -> True; both authoritative; observed runtime identity changed; old bundle refused; reader False')
'''.replace("now=NOW", "now=" + repr(NOW))
    # Ordinary launcher/reader, isolated preflight and two real snapshot
    # bootstraps; only the fixture's inert measurement body is substituted.
    result = subprocess.run([str(py), "-B", "-c", program, str(Path(cs.__file__).parent),
                             str(root), str(tmp_path / "signed"), str(stamp.configured_keys()[0]),
                             str(leaf), *map(str, versions)], env=cs.clean_environment({}),
                            capture_output=True, text=True, timeout=90)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "observed runtime identity changed" in result.stdout
    print(result.stdout.strip())


@pytest.mark.parametrize("location", ["lib-resource", "sysconfig-header"])
def test_defect_installation_data_outside_library_trees_is_unbound(tmp_path, location):
    tools, audit = small_snapshot(tmp_path)
    py, stdlib = private_python(tmp_path)
    if location == "lib-resource":
        data = stdlib.parent / "runtime-policy.json"
        read = f"json.loads(Path({str(data)!r}).read_text())['current']"
        content = lambda value: json.dumps({"current": value})
    else:
        data = Path(fresh(py, "import sysconfig; print(sysconfig.get_config_h_filename())").stdout.strip())
        assert data.is_relative_to(py.parent.parent)
        read = "bool(sysconfig.parse_config_h(open(sysconfig.get_config_h_filename()))['R7_CURRENT'])"
        content = lambda value: f"#define R7_CURRENT {int(value)}\n"
    data.parent.mkdir(parents=True, exist_ok=True)
    provider = stdlib / "site-packages/ordlookup/__init__.py"
    provider.write_text(provider.read_text() + "\nimport json, sysconfig\nfrom pathlib import Path\n"
                        f"def r7_current():\n    return {read}\n")
    program = f'''import json, ordlookup, cycle_source
assert {str(data)!r} not in cycle_source.runtime_inventory(cycle_source.runtime_roots())[1]
print('OBSERVATION=' + json.dumps({{'current': ordlookup.r7_current(), 'identity': cycle_source.runtime_identity()}}))
'''
    data.write_text(content(False))
    before = observation(isolated(tools, audit, program, python=py))
    data.write_text(content(True))
    after = observation(isolated(tools, audit, program, python=py))
    assert before["current"] is False and after["current"] is True
    assert before["identity"] == after["identity"]  # Static installation inventory alone is unchanged.
    records = completed(audit)
    assert len(records) == 2 and records[0]["runtime_modules"] == records[1]["runtime_modules"]
    assert records[0]["runtime_evidence"]["opened_files"][str(data)] != records[1]["runtime_evidence"]["opened_files"][str(data)]
    print(f"R7 {location}: read False -> True outside digested roots; opened-file evidence changes; complete module records unchanged")


def test_sound_fresh_identity_stable_and_unrelated_prefix_files_ignored(tmp_path):
    tools, audit = small_snapshot(tmp_path)
    py, _ = private_python(tmp_path)
    program = ("import cycle_source,json; print('OBSERVATION=' + "
               "json.dumps({'identity':cycle_source.runtime_identity()}))")
    observations = [observation(isolated(tools, audit, program, python=py)) for _ in range(3)]
    prefix = py.parent.parent
    # An isolated analogue of an unrelated non-Python package installed under
    # /usr. Do not modify /usr or the user's actual Python installation.
    unrelated = prefix / "share/unrelated-package/payload"
    unrelated.parent.mkdir(parents=True)
    unrelated.write_bytes(b"unrelated host package")
    tool = prefix / "bin/unrelated-tool"
    tool.write_text("not executed\n")
    observations.append(observation(isolated(tools, audit, program, python=py)))
    unrelated.write_bytes(b"unrelated package upgraded")
    observations.append(observation(isolated(tools, audit, program, python=py)))
    assert all(value == observations[0] for value in observations)
    records = completed(audit)
    assert len(records) == 5
    assert all(record["runtime_modules"] == records[0]["runtime_modules"] for record in records)
    assert all(record["runtime_evidence"] == records[0]["runtime_evidence"] for record in records)
    print("R7 observed cost: " + json.dumps(records[0]["runtime_cost"], sort_keys=True))
    print("R7 stability: five fresh measurements identical across unrelated share/ and bin/ changes")


@pytest.mark.parametrize("cfg_directory", ["prefix", "bin"])
def test_sound_pyvenv_home_redirection_changes_identity(tmp_path, cfg_directory):
    tools, audit = small_snapshot(tmp_path)
    base_a, stdlib_a = private_python(tmp_path / "base-a")
    base_b, stdlib_b = private_python(tmp_path / "base-b")
    (stdlib_a / "r7_home_provider.py").write_text("current = False\n")
    (stdlib_b / "r7_home_provider.py").write_text("current = True\n")
    py = tmp_path / "venv/bin/python"
    py.parent.mkdir(parents=True)
    shutil.copy2(base_a, py)
    cfg = (py.parent.parent if cfg_directory == "prefix" else py.parent) / "pyvenv.cfg"
    program = ("import r7_home_provider, cycle_source,json; print('OBSERVATION=' + "
               "json.dumps({'current':r7_home_provider.current, 'identity':cycle_source.runtime_identity(), "
               "'roots':cycle_source.runtime_roots()}))")
    results = []
    for base in (base_a, base_b):
        cfg.write_text(f"home = {base.parent}\ninclude-system-site-packages = false\n")
        results.append(observation(isolated(tools, audit, program, python=py)))
    assert results[0]["current"] is False and results[1]["current"] is True
    assert results[0]["identity"] != results[1]["identity"]
    assert all(str(cfg) in result["roots"] for result in results)
    assert len(completed(audit)) == 2


@pytest.mark.parametrize("layout", ["pth", "debian-dist-packages"])
def test_sound_unselected_package_locations_do_not_execute(tmp_path, layout):
    tools, audit = small_snapshot(tmp_path)
    py, stdlib = private_python(tmp_path)
    if layout == "pth":
        outside = tmp_path / "unselected-provider"
        outside.mkdir()
        (stdlib / "site-packages/r7_paths.pth").write_text(
            str(outside) + "\nimport r7_outside\n")
    else:
        outside = stdlib.parent / "python3/dist-packages"
        outside.mkdir(parents=True)
    source = outside / "r7_outside.py"
    source.write_text("raise RuntimeError('unselected code executed')\n")
    program = '''import cycle_source, json
assert 'site' not in sys.modules
try:
    import r7_outside
except ModuleNotFoundError:
    pass
else:
    raise AssertionError('unselected root was imported')
print('OBSERVATION=' + json.dumps({'identity':cycle_source.runtime_identity()}))
'''
    before = observation(isolated(tools, audit, program, python=py))
    source.write_text("raise RuntimeError('changed unselected code executed')\n")
    after = observation(isolated(tools, audit, program, python=py))
    assert before == after
    assert len(completed(audit)) == 2


def test_sound_sysconfig_code_and_makefile_are_bound(tmp_path):
    tools, audit = small_snapshot(tmp_path)
    py, stdlib = private_python(tmp_path)
    locations = fresh(py, "import sysconfig,json; print(json.dumps([sysconfig._get_sysconfigdata_name(), "
                          "sysconfig.get_makefile_filename()]))").stdout
    module, makefile = json.loads(locations)
    provider = stdlib / (module + ".py")
    provider.write_text(provider.read_text() + "\nbuild_time_vars['R7_CURRENT'] = False\n")
    makefile = Path(makefile)
    assert makefile.is_relative_to(stdlib)
    makefile.parent.mkdir(parents=True, exist_ok=True)
    makefile.write_text("R7_CURRENT = 0\n")
    program = ("import sysconfig,cycle_source,json; print('OBSERVATION=' + "
               "json.dumps({'current':sysconfig.get_config_var('R7_CURRENT'), "
               "'identity':cycle_source.runtime_identity()}))")
    before = observation(isolated(tools, audit, program, python=py))
    provider.write_text(provider.read_text().replace("['R7_CURRENT'] = False", "['R7_CURRENT'] = True"))
    changed_code = observation(isolated(tools, audit, program, python=py))
    makefile.write_text("R7_CURRENT = 1\n")
    changed_data = observation(isolated(tools, audit, program, python=py))
    assert before['current'] is False and changed_code['current'] is True
    assert before['identity'] != changed_code['identity'] != changed_data['identity']
    assert len(completed(audit)) == 3


def test_sound_real_host_identity_stable_across_clean_processes():
    # No host writes: exactly the independent preflight algorithm used by the
    # launcher. The private-installation controls above cover unrelated writes.
    results = [identity(sys.executable) for _ in range(3)]
    assert results[0] == results[1] == results[2]
    assert not {sys.prefix, sys.base_prefix, sys.exec_prefix, sys.base_exec_prefix} & set(results[0]['roots'])
    print("R7 host: three fresh clean preflight identities identical; bare prefixes excluded")


@pytest.mark.parametrize('late', [False, True])
def test_opened_runtime_mutation_refuses_completed_record(tmp_path, late):
    tools, audit = small_snapshot(tmp_path)
    policy = tmp_path / 'outside/runtime-policy.json'
    policy.parent.mkdir()
    policy.write_text('original')
    program = f'''from pathlib import Path
p = Path({str(policy)!r})
assert p.read_text() == 'original'
def mutate():
    p.write_text('changed!')
'''
    program += 'import atexit; atexit.register(mutate)\n' if late else 'mutate()\n'
    result = isolated(tools, audit, program)
    assert 'opened runtime file changed' in result.stderr
    with pytest.raises(ValueError, match='incomplete'):
        cs.audit_runtime(audit, roots=(tools,))


def test_python_helper_reports_external_reads_and_maps(tmp_path):
    tools, audit = small_snapshot(tmp_path)
    policy = tmp_path / 'runtime-policy.json'
    policy.write_text('bound helper data')
    helper = tools / 'probe.py'
    helper.write_text(f"if __name__ == '__main__':\n    from pathlib import Path\n    assert Path({str(policy)!r}).read_text() == 'bound helper data'\n")
    result = isolated(tools, audit, f"import subprocess; subprocess.run([sys.executable, {str(helper)!r}], check=True)")
    assert result.returncode == 0, result.stdout + result.stderr
    records = completed(audit)
    assert len(records) == 2
    assert all(record['runtime_evidence']['mapped_files'] for record in records)
    union = cs.audit_runtime(audit, roots=(tools,))
    assert union['opened_files'][str(policy)] == cs.file_hash(policy)
    assert sum(str(policy) in record['runtime_evidence']['opened_files'] for record in records) == 1


@pytest.mark.parametrize('listing', ['listdir', 'scandir'])
def test_directory_listing_is_bound_and_rechecked(tmp_path, listing):
    tools, audit = small_snapshot(tmp_path)
    directory = tmp_path / 'outside-policy-directory'
    directory.mkdir()
    (directory / 'first').touch()
    program = f"import os; list(os.{listing}({str(directory)!r}))"
    assert isolated(tools, audit, program).returncode == 0
    before = completed(audit)[0]['runtime_evidence']
    assert before['directories'][str(directory)] == ['first']
    (directory / 'second').touch()
    assert cs.current_runtime_evidence(before) != before
    result = isolated(tools, audit, program + f"; open({str(directory / 'third')!r}, 'w').close()")
    assert result.returncode != 0
    assert 'runtime file changed' in result.stderr or 'runtime directory changed' in result.stderr


def test_known_input_roots_are_not_rule_identity(tmp_path):
    tools, audit = small_snapshot(tmp_path)
    external = tmp_path / 'objects'
    external.mkdir()
    (tools.parent / 'build').symlink_to(external, target_is_directory=True)
    obj = external / 'f.obj'
    obj.write_bytes(b'input object')
    result = isolated(tools, audit, f"from pathlib import Path; Path({str(obj)!r}).read_bytes()")
    assert result.returncode == 0, result.stderr
    record = completed(audit)[0]
    assert str(obj) not in record['runtime_evidence']['opened_files']
    assert record['runtime_cost']['classified']['measurement-input'] >= 1


def test_windows_mapped_modules_uses_loaded_module_list_with_resize(tmp_path):
    import ctypes
    from ctypes import wintypes
    paths = [tmp_path / 'bridge.dll', tmp_path / 'RUNPATH-leaf.dll']
    for path in paths:
        path.write_bytes(b'mocked native module')
    calls = []
    def enumerate_modules(process, handles, capacity, needed):
        assert process == 0x123456789
        calls.append(capacity)
        if len(calls) == 1:
            ctypes.cast(needed, ctypes.POINTER(wintypes.DWORD))[0] = capacity + 8
        else:
            handles[0], handles[1] = 1, 2
            ctypes.cast(needed, ctypes.POINTER(wintypes.DWORD))[0] = 2 * ctypes.sizeof(wintypes.HMODULE)
        return 1
    def filename(process, module, buffer, capacity):
        buffer.value = str(paths[module - 1])
        return len(buffer.value)
    observed = cs.mapped_files_windows((lambda: 0x123456789, enumerate_modules, filename))
    assert observed == set(map(str, paths))
    assert len(calls) == 2 and calls[1] > calls[0]


def test_real_host_observed_identity_three_runs_and_cost(tmp_path):
    tools, audit = small_snapshot(tmp_path)
    for _ in range(3):
        result = isolated(tools, audit, 'import cycle_source')
        assert result.returncode == 0, result.stderr
    records = completed(audit)
    assert len(records) == 3
    assert all(record['runtime_evidence'] == records[0]['runtime_evidence'] for record in records)
    assert all(record['runtime_evidence']['mapped_files'] for record in records)
    print('R7 host opened/mapped cost: ' + json.dumps([r['runtime_cost'] for r in records], sort_keys=True))


@pytest.mark.parametrize('location', ['lib-resource', 'sysconfig-header'])
def test_reader_refuses_changed_opened_runtime(checkout, tmp_path, location):
    import cycle_artifacts as ca
    import link_cycle as lc
    from test_bfme2_port_r1_regressions import run_for
    root, _ = checkout
    _, receipt = run_for(checkout, tmp_path / 'synthetic-run')
    data = tmp_path / ('lib/runtime-policy.json' if location == 'lib-resource' else 'include/python/pyconfig.h')
    data.parent.mkdir(parents=True)
    data.write_text('original policy')
    receipt['runtime_evidence'] = {'opened_files': {str(data): cs.file_hash(data)},
                                   'mapped_files': {}, 'directories': {}}
    before = lc.digest_of(lc.receipt_core(receipt))
    assert ca.freshness(receipt, root=root, now=NOW)['rules_match']
    data.write_text('changed policy')
    assert not ca.freshness(receipt, root=root, now=NOW)['rules_match']
    receipt['runtime_evidence']['opened_files'][str(data)] = cs.file_hash(data)
    assert lc.digest_of(lc.receipt_core(receipt)) != before
    assert ca.freshness(receipt, root=root, now=NOW)['rules_match']


@pytest.mark.parametrize('file_type', [1, 3])
def test_windows_open_audit_resolves_disk_fds_and_ignores_pipes(tmp_path, monkeypatch, file_type):
    import ctypes
    import types
    target = tmp_path / 'opened-policy.json'
    target.write_text('policy')
    def filename(handle, buffer, capacity, flags):
        assert handle.value == 0x123456789
        buffer.value = str(target)
        return len(buffer.value)
    monkeypatch.setattr(ctypes, 'windll', types.SimpleNamespace(kernel32=types.SimpleNamespace(
        GetFileType=lambda handle: file_type, GetFinalPathNameByHandleW=filename)), raising=False)
    monkeypatch.setitem(sys.modules, 'msvcrt', types.SimpleNamespace(get_osfhandle=lambda fd: 0x123456789))
    monkeypatch.setattr(sys, '_bfme_cycle_io', None, raising=False)
    namespace = {}
    # Exercise the exact early hook without adding a permanent pytest hook.
    exec(cs.IO_BOOTSTRAP.replace('sys.addaudithook(_cycle_open_audit)', ''), namespace)
    namespace['_io_os'] = types.SimpleNamespace(name='nt', path=os.path, fsdecode=os.fsdecode,
                                               stat=os.stat, listdir=os.listdir)
    namespace['_cycle_open_audit']('open', (7, 'r', 0))
    assert list(namespace['_cycle_io']['events']) == ([str(target)] if file_type == 1 else [])


def test_abnormal_exit_never_completes_runtime_evidence(tmp_path):
    tools, audit = small_snapshot(tmp_path)
    result = isolated(tools, audit, "raise RuntimeError('inert abnormal measurement')")
    assert result.returncode != 0
    with pytest.raises(ValueError, match='incomplete'):
        cs.audit_runtime(audit, roots=(tools,))
