"""Round-8 correctness review: inert audited children, no game build or link.

Regression assertions require the expected behavior; failures demonstrate open
defects. All writes are to pytest temporary paths, including Python fixtures.
The optional real-run test reads only the owner's diagnostic run7 archive.
"""
import ast
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import cycle_source as cs
import link_cycle_context as ctx
from cycle_fixture import NOW
from test_bfme2_port_r1_regressions import checkout, synthetic_snapshot_checkout
from test_bfme2_port_r2_regressions import commit_fixture
from test_bfme2_port_r4_regressions import small_snapshot
from test_bfme2_port_r5_regressions import isolated

pytestmark = pytest.mark.skipif(sys.platform != "linux", reason="Linux audit fixtures")


def audited(tmp_path, installation, program):
    tools, audit = small_snapshot(tmp_path)
    result = isolated(tools, audit, program, python=installation[0])
    assert result.returncode == 0, result.stdout + result.stderr
    evidence = cs.audit_runtime(audit, roots=(tools,))
    return tools, audit, evidence, result


@pytest.mark.parametrize("name", ["build/f.obj", "inputs/retail.exe", "targets/game/reverse/functions.csv",
                                  "build/link_cycle/compile_inputs.json"])
def test_sound_ordinary_input_reads_are_not_rules(tmp_path, cycle_python_installation, name):
    tools, audit = small_snapshot(tmp_path)
    path = tools.parent / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"input-v1")
    evidence = []
    for content in (b"input-v1", b"input-v2"):
        path.write_bytes(content)
        result = isolated(tools, audit, f"Path({str(path)!r}).read_bytes()", python=cycle_python_installation[0])
        assert result.returncode == 0, result.stderr
        evidence.append(cs.audit_runtime(audit, roots=(tools,)))
    assert evidence[0] == evidence[1]
    assert str(path) not in evidence[0]["opened_files"]


@pytest.mark.parametrize("name", ["build/f.obj", "inputs/retail.exe", "targets/game/reverse/functions.csv",
                                  "build/link_cycle/compile_inputs.json"])
def test_mapped_measurement_inputs_are_not_rules(tmp_path, cycle_python_installation, name):
    tools, audit = small_snapshot(tmp_path)
    path = tools.parent / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"input-v1")
    result = isolated(tools, audit, f"import mmap\nf = open({str(path)!r}, 'rb')\n"
                      "mapping = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)\n"
                      "assert mapping[:] == b'input-v1'\n", python=cycle_python_installation[0])
    assert result.returncode == 0, result.stderr
    evidence = cs.audit_runtime(audit, roots=(tools,))
    assert str(path) not in evidence["opened_files"]
    assert str(path) not in evidence["mapped_files"], "measurement input entered runtime/rule evidence"


@pytest.mark.parametrize("late", [False, True])
def test_sound_late_external_read_is_bound(tmp_path, cycle_python_installation, late):
    policy = tmp_path / "external-policy"
    policy.write_bytes(b"policy-v1")
    program = f"def read_policy():\n    assert Path({str(policy)!r}).read_bytes() == b'policy-v1'\n"
    program += "import atexit; atexit.register(read_policy)\n" if late else "read_policy()\n"
    _, _, evidence, _ = audited(tmp_path, cycle_python_installation, program)
    assert evidence["opened_files"][str(policy)] == cs.file_hash(policy)


@pytest.mark.parametrize("transport", ["measurement", "helper", "exit"])
def test_directory_relative_external_read_is_bound(tmp_path, cycle_python_installation, transport):
    outside = tmp_path / "external-policy-directory"
    outside.mkdir()
    policy = outside / "policy.json"
    policy.write_bytes(b"policy-v1")
    read = f"""import os
directory = os.open({str(outside)!r}, os.O_RDONLY | os.O_DIRECTORY)
fd = os.open('policy.json', os.O_RDONLY, dir_fd=directory)
assert os.read(fd, 100) == b'policy-v1'
os.close(fd)
os.close(directory)
"""
    tools, audit = small_snapshot(tmp_path)
    if transport == "helper":
        (tools / 'probe.py').write_text("if __name__ == '__main__':\n" +
                                      ''.join('    ' + line + '\n' for line in read.splitlines()))
        program = "import subprocess; subprocess.run([sys.executable, str(tools / 'probe.py')], check=True)"
    elif transport == "exit":
        program = "import atexit; atexit.register(lambda: exec(" + repr(read) + "))"
    else:
        program = read
    result = isolated(tools, audit, program, python=cycle_python_installation[0])
    assert result.returncode == 0, result.stderr
    evidence = cs.audit_runtime(audit, roots=(tools,))
    assert evidence["opened_files"].get(str(policy)) == cs.file_hash(policy), evidence


@pytest.mark.parametrize("name", ["build/f.obj", "inputs/retail.exe", "targets/game/reverse/functions.csv",
                                  "build/link_cycle/compile_inputs.json"])
def test_restored_input_mutation_is_not_complete(tmp_path, cycle_python_installation, name):
    tools, audit = small_snapshot(tmp_path)
    path = tools.parent / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"input-v1")
    result = isolated(tools, audit, f"""import os
p = Path({str(path)!r})
before = p.stat()
assert p.read_bytes() == b'input-v1'
p.write_bytes(b'input-v2')
assert p.read_bytes() == b'input-v2'
p.write_bytes(b'input-v1')
os.utime(p, ns=(before.st_atime_ns, before.st_mtime_ns))
assert p.read_bytes() == b'input-v1'
""", python=cycle_python_installation[0])
    # The generic audit sees changed generations even after bytes/mtime restore.
    # An accepted run must not silently discard that evidence for bound inputs.
    with pytest.raises(ValueError, match="incomplete|changed"):
        cs.audit_runtime(audit, roots=(tools,))


def full_snapshot(tmp_path):
    tools = tmp_path / "snapshot/tools"
    tools.mkdir(parents=True)
    for name in ctx.MEASUREMENT_FILES:
        shutil.copyfile(Path(cs.__file__).parent / name, tools / name)
    audit = tmp_path / "audit"
    audit.mkdir()
    return tools, audit


def miniature_pe():
    pe = bytearray(0x400)
    pe[:2] = b"MZ"
    struct.pack_into("<I", pe, 0x3c, 0x40)
    pe[0x40:0x44] = b"PE\0\0"
    struct.pack_into("<HHIIIHH", pe, 0x44, 0x14c, 1, 0, 0, 0, 224, 0x102)
    struct.pack_into("<H", pe, 0x58, 0x10b)
    struct.pack_into("<I", pe, 0x58 + 28, 0x400000)
    struct.pack_into("<II", pe, 0x58 + 32, 0x1000, 0x200)
    struct.pack_into("<II", pe, 0x58 + 56, 0x2000, 0x200)
    pe[0x138:0x140] = b".text\0\0\0"
    struct.pack_into("<IIII", pe, 0x140, 0x100, 0x1000, 0x200, 0x200)
    struct.pack_into("<I", pe, 0x138 + 36, 0x60000020)
    pe[0x200] = 0xcc
    return bytes(pe)


@pytest.mark.parametrize("retain", [True, False])
def test_production_pe_view_does_not_turn_input_into_rules(tmp_path, cycle_python_installation, retain):
    tools, audit = full_snapshot(tmp_path)
    path = tools.parent / "build/base.exe"
    path.parent.mkdir()
    path.write_bytes(miniature_pe())
    program = f"import link_cycle as lc\nview = lc.pe_view(Path({str(path)!r}))\nassert view[1][0x1000] == 0xcc\n"
    if not retain:
        program += "del view\n"
    result = isolated(tools, audit, program, python=cycle_python_installation[0])
    assert result.returncode == 0, result.stderr
    evidence = cs.audit_runtime(audit, roots=(tools,))
    assert str(path) not in evidence["mapped_files"], "real pe_view mmap is classified as a shared library"


def test_actual_input_state_and_byte_verdict_refuse_restored_retail(tmp_path, cycle_python_installation):
    tools, audit = full_snapshot(tmp_path)
    root = tools.parent
    target = root / "inputs/baselines/bfme1/retail-1.03-unpacked/files/lotrbfme.exe"
    target.parent.mkdir(parents=True)
    target.write_bytes(miniature_pe())
    reverse = root / "targets/game/reverse"
    reverse.mkdir(parents=True)
    for name in ("functions", "symbols", "data_rows"):
        (reverse / (name + ".csv")).write_text("fixture\n")
    toolchain = root / "inputs/inert-toolchain/Vc7/bin"
    toolchain.mkdir(parents=True)
    for name in ("cl.exe", "link.exe", "lib.exe"):
        (toolchain / name).write_bytes(b"inert hash fixture; never executed")
    program = '''import json, os
from types import SimpleNamespace
import link_cycle as lc
lc.build.vc71_root = lambda: lc.ROOT / 'inputs/inert-toolchain'
mark = {'commit': 'e' * 40, 'submodules': {}, 'tree_manifest': lc.tree_manifest(lc.ROOT)}
(lc.ROOT / lc.SNAPSHOT_MARK).write_text(json.dumps(mark))
before = lc.input_state()
p = lc.build.EXE
st, original = p.stat(), p.read_bytes()
changed = bytearray(original)
changed[0x200] = 0xc3
p.write_bytes(changed)
pe, consumed, _, _ = lc.pe_view(p)
pe.close()
p.write_bytes(original)
os.utime(p, ns=(st.st_atime_ns, st.st_mtime_ns))
after = lc.input_state(final=True)
assert before == after
# Run the production non-relocation byte verdict on exactly the image read
# between the authentic start/end identity checks. No verifier is replaced.
linked = bytearray(consumed)
linked[0x1000] = 0xc3
judge = lc.Measure.__new__(lc.Measure)
judge._init_state()  # reachable-entry and relocation-evidence state
judge.I, judge.R = linked, consumed
judge.lbase = judge.rbase = lc.BASE
obj = ([SimpleNamespace(relocs=[], size=1)], {}, b'')
assert not judge.relocs(0x1000, 0x1000, 1, obj, 1, 0, '_f')[0]
pe, restored, _, _ = lc.pe_view(p)
pe.close()
judge.R = restored
assert judge.relocs(0x1000, 0x1000, 1, obj, 1, 0, '_f')[0]
assert str(p) in sys._bfme_cycle_io['errors']
print('R8 input: equal real start/end states; consumed target passes; restored target fails; audit saw mutation')
'''
    result = isolated(tools, audit, program, python=cycle_python_installation[0])
    assert result.returncode == 0, result.stdout + result.stderr
    print(result.stdout.strip())
    with pytest.raises(ValueError, match="incomplete|changed"):
        cs.audit_runtime(audit, roots=(tools,))


@pytest.mark.parametrize("retain", [False, True])
def test_launcher_pe_inputs_remain_readable_and_identity_stable(checkout, tmp_path, cycle_python_installation, retain):
    """Actual launcher/reader, with cycle() removed by the inherited fixture."""
    import cycle_stamp
    root, _ = synthetic_snapshot_checkout(checkout)
    target = root / "inputs/retail.exe"
    target.parent.mkdir()
    target.write_bytes(miniature_pe())
    driver = root / "tools/link_cycle.py"
    driver.write_text(driver.read_text().replace('    bind_evidence(run, receipt, ROOT)\n',
                      "    view = pe_view(ROOT / 'inputs/retail.exe')\n"
                      "    assert view[1][0x1000] == 0xcc\n" +
                      ("    lc._r8_input_view = view\n" if retain else "") +
                      "    del view\n"
                      '    bind_evidence(run, receipt, ROOT)\n'))
    # commit_fixture stages only fixture paths; include the new retail fixture.
    subprocess.run(["git", "-C", str(root), "add", "inputs/retail.exe"], check=True)
    commit_fixture(root, "inert R8 PE observation; real cycle removed")
    program = '''import json, sys
sys.path.insert(0, sys.argv[1])
import cycle_launch as launch
root, out, key = map(launch.Path, sys.argv[2:])
launch.stamp._reader_key_for_tests = key
facts = []
for index in range(3):
    dest = out / str(index)
    launch.measure(dest, 'R8 real PE parser, inert measurement', root=root, key=key)
    receipt = launch.ca.read_json(dest / launch.ca.RECEIPT)
    try:
        launch.ca.serve(dest, root=root, now=NOW)
        reason = 'authoritative'
    except launch.ca.Refused as error:
        reason = error.reason
    facts.append({'reason': reason, 'evidence': receipt['runtime_evidence'],
                  'rules': receipt['rule_identity'], 'core': receipt['core_sha256'],
                  'inputs': receipt['consumed_inputs']})
print('FACTS=' + json.dumps(facts))
'''.replace('now=NOW', 'now=' + repr(NOW))
    result = subprocess.run([str(cycle_python_installation[0]), "-B", "-c", program,
                             str(Path(cs.__file__).parent), str(root), str(tmp_path / 'bundles'),
                             str(cycle_stamp.configured_keys()[0])], env=cs.clean_environment({}),
                            capture_output=True, text=True, timeout=90)
    assert result.returncode == 0, result.stdout + result.stderr
    facts = json.loads(next(line.removeprefix('FACTS=') for line in result.stdout.splitlines()
                            if line.startswith('FACTS=')))
    assert all(f['rules'] == facts[0]['rules'] for f in facts)
    print('R8 launcher PE: reader=' + repr([f['reason'] for f in facts]) +
          '; stable observed identity=' + str(facts[0]['evidence'] == facts[1]['evidence']) +
          '; stable core=' + str(facts[0]['core'] == facts[1]['core']))
    assert [f['reason'] for f in facts] == ['authoritative'] * 3
    assert all(f['evidence'] == facts[0]['evidence'] for f in facts)
    assert all(f['core'] == facts[0]['core'] for f in facts)
    assert all(f['inputs']['inputs/retail.exe'] == cs.hashlib.sha256(miniature_pe()).hexdigest()
               for f in facts)


def test_sound_real_run7_graph_credit_and_roots(monkeypatch):
    import closure_report as cr
    import link_cycle as lc
    project = Path(__file__).resolve().parents[5]
    run = project / "build/bfme2_port/cycle_test/run7"
    if not run.is_dir():
        pytest.skip("owner's read-only run7 archive is unavailable")
    receipt = json.loads((run / "receipt.json").read_bytes())
    saved = json.loads((run / "closure/closure_roots.json").read_bytes())
    assert receipt["rules"] == ctx.RULES == "bfme1-link-cycle-1"
    assert receipt["target"]["image_base"] == 0x400000
    assert receipt["target"]["machine"] == 0x14c
    assert receipt["series"]["retail_text_bytes"] == 13_049_856
    # This diagnostic predates the new witness/runtime core. Verify its own
    # serializer, without invoking old/new cycle() or claiming current authority.
    source = subprocess.run(["git", "show", receipt["commit"] + ":tools/link_cycle.py"],
                            cwd=Path(lc.__file__).parents[1], check=True, capture_output=True, text=True).stdout
    tree = ast.parse(source)
    selected = ast.Module(body=[n for n in tree.body if isinstance(n, ast.FunctionDef)
                                and n.name in {"receipt_core", "receipt_canon_core", "row_kind"}], type_ignores=[])
    namespace = {}
    exec(compile(selected, '<run7 core serializers only>', 'exec'), namespace)
    assert lc.digest_of(namespace["receipt_core"](receipt)) == receipt["core_sha256"]
    assert lc.digest_of(namespace["receipt_canon_core"](receipt)) == receipt["core_canon_sha256"]
    assert lc.sha256(run / "link_status.csv") == receipt["series"]["link_status_sha256"]
    # Review 2 rejects the archive's prebuilt-library "real" rows under
    # today's provenance policy. Preserve this historical serializer check
    # with the archive's own classifier; this grants no current admission.
    with pytest.raises(cr.ReportError, match="cannot be real credit"):
        cr.load_graph(run / cr.GRAPH_FILE, receipt["closure_graph_sha256"])
    with monkeypatch.context() as patch:
        patch.setattr(cr.context, "source_kind", namespace["row_kind"])
        # Reproduce this historical artifact with the pre-round-2b reader.
        # Current admission above must still reject it; functional gen-* kinds
        # alone are no longer sufficient provenance for a new source closure.
        prior = subprocess.run(["git", "show", "1f2a94bcc9:tools/closure_report.py"],
                               cwd=Path(lc.__file__).parents[1], check=True, capture_output=True, text=True).stdout
        reader = ast.Module(body=[n for n in ast.parse(prior).body
                                  if isinstance(n, ast.FunctionDef) and n.name == "graph_from_doc"], type_ignores=[])
        old_reader = dict(cr.__dict__)
        exec(compile(reader, '<historical graph reader only>', 'exec'), old_reader)
        graph = old_reader["graph_from_doc"](json.loads(cr.read_bytes(run / cr.GRAPH_FILE)))
    ok, edges, rows, describe = graph
    closed = cr.reference_closure(ok, edges)
    assert closed == lc.greatest_closure(ok, edges)
    status = cr.status_rows(run / "link_status.csv")
    assert cr.check_rows(rows, closed, status) == len(status)
    assert cr.credit_of(ok, edges, rows) == receipt["series"]["credit_unique_bytes"] == 1_081_798
    body, blockers = cr.analyze(*graph)
    assert body["summary"] == saved["summary"]
    assert len(blockers) == saved["blockers"]["rows"]
    assert cr.sha256_bytes(cr.blockers_csv(blockers)) == saved["blockers"]["sha256"]
    assert len(body["roots"]) == 3083
    strip_check = lambda roots: [{k: v for k, v in row.items() if k != "verified"} for row in roots]
    assert strip_check(body["roots"]) == strip_check(saved["roots"])
    assert body["unscored"] == saved["unscored"]
    for row in saved["roots"][:5]:
        nodes = [n for n in ok if cr.scorable(n, ok) and describe(n)["group"] == row["root"]]
        assert cr.forced_gain(ok, edges, rows, nodes) == row["conditional_gain_bytes"]
    assert saved["summary"]["joint_only"]["non_additive"] is True
    import cycle_stamp
    assert not (run / cycle_stamp.STAMP).exists()
    print(f'R8 run7: {len(status)} rows; {len(ok)} nodes; 1,081,798 credit bytes; '
          f'3,083 root scores reproduced; five leading roots independently forced; {len(blockers)} blockers')


@pytest.mark.parametrize('kind', ['object', 'retail', 'ledger', 'compile-receipt', 'toolchain'])
def test_consumed_content_is_bound_to_receipt(tmp_path, cycle_python_installation, kind):
    tools, audit = small_snapshot(tmp_path)
    names = {'object': 'build/f.obj', 'retail': 'inputs/retail.exe', 'ledger': 'targets/game/reverse/functions.csv',
             'compile-receipt': 'build/link_cycle/compile_inputs.json',
             'toolchain': 'inputs/toolchain/Vc7/bin/cl.exe'}
    name = names[kind]
    path = tools.parent / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b'consumed\r\nbytes\n')
    result = isolated(tools, audit, f'Path({str(path)!r}).read_bytes()', python=cycle_python_installation[0])
    assert result.returncode == 0, result.stderr
    kwargs = {'target': name} if kind == 'retail' else {}
    receipt = {'retail_sha256': cs.file_hash(path), 'compile_inputs_sha256': cs.file_hash(path),
               'consumed_inputs': {name: cs.file_hash(path)} if kind == 'object' else {},
               'toolchain_sha256': {'cl.exe': cs.file_hash(path)},
               'inputs': {name: cs.hashlib.sha256(b'consumed\nbytes\n').hexdigest()} if kind == 'ledger' else {}}
    evidence = cs.audit_inputs(audit, roots=(tools,), receipt=receipt, **kwargs)
    assert evidence[str(path)]['sha256'] == cs.file_hash(path)
    assert cs.audit_inputs(audit, roots=(tools,), canonical=True) == {name: cs.file_hash(path)}
    if kind == 'object':
        receipt['consumed_inputs'][name] = '0' * 64
    elif kind == 'ledger':
        receipt['inputs'][name] = '0' * 64
    elif kind == 'toolchain':
        receipt['toolchain_sha256']['cl.exe'] = '0' * 64
    else:
        receipt['retail_sha256' if kind == 'retail' else 'compile_inputs_sha256'] = '0' * 64
    with pytest.raises(ValueError, match='moved_during_run.*differs from receipt'):
        cs.audit_inputs(audit, roots=(tools,), receipt=receipt, **kwargs)


def test_consumed_input_mutation_after_child_exit_is_refused(tmp_path, cycle_python_installation):
    tools, audit = small_snapshot(tmp_path)
    path = tools.parent / 'inputs/retail.exe'
    path.parent.mkdir()
    path.write_bytes(b'original')
    result = isolated(tools, audit, f'Path({str(path)!r}).read_bytes()', python=cycle_python_installation[0])
    assert result.returncode == 0, result.stderr
    before = path.stat()
    path.write_bytes(b'changed!')
    path.write_bytes(b'original')
    os.utime(path, ns=(before.st_atime_ns, before.st_mtime_ns))
    with pytest.raises(ValueError, match='moved_during_run.*changed'):
        cs.audit_inputs(audit, roots=(tools,))


def test_unresolvable_successful_open_refuses_completion(tmp_path, cycle_python_installation):
    tools, audit = small_snapshot(tmp_path)
    policy = tmp_path / 'external-policy'
    policy.write_bytes(b'policy')
    program = f'''import os
saved = os.readlink
def unavailable(path, *args, **kwargs):
    if str(path).startswith('/proc/self/fd/'):
        raise OSError('inert descriptor resolution failure')
    return saved(path, *args, **kwargs)
os.readlink = unavailable
fd = os.open({str(policy)!r}, os.O_RDONLY)
assert os.read(fd, 100) == b'policy'
os.close(fd)
os.readlink = saved
'''
    result = isolated(tools, audit, program, python=cycle_python_installation[0])
    assert result.returncode == 0, result.stderr
    with pytest.raises(ValueError, match='incomplete'):
        cs.audit_runtime(audit, roots=(tools,))


@pytest.mark.parametrize('changed_after_consumption', [False, True])
def test_input_epoch_allows_preparation_but_protects_measurement(tmp_path, cycle_python_installation,
                                                               changed_after_consumption):
    tools, audit = small_snapshot(tmp_path)
    path = tools.parent / 'build/f.obj'
    path.parent.mkdir()
    path.write_bytes(b'old object')
    program = f'''import cycle_source as cs
p = Path({str(path)!r})
cs.input_epoch(tools.parent, prepare=True)
assert p.read_bytes() == b'old object'
p.write_bytes(b'new object')
cs.input_epoch(tools.parent)
assert p.read_bytes() == b'new object'
'''
    if changed_after_consumption:
        program += "p.write_bytes(b'bad object')\np.write_bytes(b'new object')\n"
    result = isolated(tools, audit, program, python=cycle_python_installation[0])
    assert result.returncode == 0, result.stderr
    if changed_after_consumption:
        with pytest.raises(ValueError, match='incomplete'):
            cs.audit_runtime(audit, roots=(tools,))
    else:
        cs.audit_inputs(audit, roots=(tools,))


def test_executable_mapping_in_input_directory_is_still_runtime(tmp_path, cycle_python_installation):
    tools, audit = small_snapshot(tmp_path)
    path = tools.parent / 'build/native-provider'
    path.parent.mkdir()
    path.write_bytes(b'inert executable mapping fixture')
    program = f'''import mmap
f = open({str(path)!r}, 'rb')
mapping = mmap.mmap(f.fileno(), 0, prot=mmap.PROT_READ | mmap.PROT_EXEC)
assert mapping[:] == b'inert executable mapping fixture'
'''
    result = isolated(tools, audit, program, python=cycle_python_installation[0])
    assert result.returncode == 0, result.stderr
    assert cs.audit_runtime(audit, roots=(tools,))['mapped_files'][str(path)] == cs.file_hash(path)
    assert str(path) in cs.audit_inputs(audit, roots=(tools,))
