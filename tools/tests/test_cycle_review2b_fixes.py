"""Consumer and witnessed-include controls for the round-2 measurement repairs."""
import hashlib
import json

import pytest

from test_cycle_review2_currency import history
from test_cycle_review2_evidence import ImageCase, F, lc
import build
import closure_report as cr
import cycle_diff as cd
import repair_queue as rq
from cycle_fixture import measured_run, save_receipt, synthetic_host


def test_padding_exclusion_survives_graph_gains_and_diff(tmp_path):
    runs = []
    for extent in (1, 16):
        folder, receipt = measured_run(tmp_path / str(extent))
        graph = json.loads(cr.read_bytes(folder / cr.GRAPH_FILE))
        graph['rows'][0][4] = extent
        graph['padding'] = [[0x1001, 0x1010]]
        lc.write_closure_graph(folder / cr.GRAPH_FILE, graph)
        rows = cr.status_rows(folder / 'link_status.csv')
        rows[0]['size'] = str(extent)
        import csv
        with (folder / 'link_status.csv').open('w', newline='') as stream:
            writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
        receipt['series'].update(credit_unique_bytes=1, padding=graph['padding'],
                                 link_status_sha256=lc.sha256(folder / 'link_status.csv'))
        receipt['closure_graph_sha256'] = lc.sha256(folder / cr.GRAPH_FILE)
        receipt['series']['closure_graph_sha256'] = receipt['closure_graph_sha256']
        save_receipt(folder, receipt)
        spans = cd.verified_credit(receipt, (folder / 'link_status.csv').read_bytes())
        assert spans == [[0x1000, 0x1001]]
        parsed = cr.graph_from_doc(graph)
        if extent == 16:
            mismatched = dict(receipt, series=dict(receipt['series'], padding=[[0x1000, 0x100f]]))
            with pytest.raises(cr.ReportError, match='nonpadding weights'):
                cr.report(parsed, mismatched, rows, {'row_columns': ()})
        ok, edges, ledger_rows, describe = parsed
        assert cr.credit_of(ok, edges, ledger_rows) == 1
        unit = next(iter(ok))
        ok[unit] = False
        ledger_rows[0]['self_strict'] = False
        report, _ = cr.analyze(ok, edges, ledger_rows, describe)
        assert report['roots'][0]['conditional_gain_bytes'] == 1
        assert cr.credit_of(ok, edges, ledger_rows, forced=[unit]) == 1
        runs.append(spans)
    assert cd.difference(runs[1], runs[0]) == []


@pytest.mark.parametrize('change', ['dependency', 'earlier', 'unrelated'])
def test_queue_checks_witnessed_inputs_and_search_inventory(history, monkeypatch, change):
    root, measured, item, graph = history
    monkeypatch.setattr(build, 'ROOT', root)
    dep = root / 'shared/config.arbitrary'
    dep.parent.mkdir()
    dep.write_text('value 2')
    search = root / 'game/includes'
    search.mkdir()
    proof = {'deps': {'shared/config.arbitrary': hashlib.sha256(dep.read_bytes()).hexdigest()},
             'search_roots': ['game/includes'], 'inventory': build._inventory_for_roots([search])}
    ok, edges, rows, describe = graph
    descriptions = {node: dict(describe(node), include_proofs={'game/root.cpp': proof}) for node in ok}
    graph = ok, edges, rows, descriptions.__getitem__
    if change == 'dependency':
        dep.write_text('value 1')
    elif change == 'earlier':
        (search / 'settings.without_header_suffix').write_text('value 1')
    else:
        (root / 'unrelated.hh').write_text('unrelated')
    kept, skipped = rq.current_bundle_items([item], measured, root=root, graph=graph)
    assert bool(skipped) == (change != 'unrelated')
    assert bool(kept) == (change == 'unrelated')


def test_measure_serializes_deps_sidecar_for_candidate_currency(tmp_path, monkeypatch):
    case = ImageCase(tmp_path, monkeypatch)
    obj = case.object('root.obj', [('.text', b'\xc3', [])], [('_root', 1, 0, lc.EXTERNAL)])
    case.row(obj, '_root', F, 1)
    case.public(obj, '_root', F)
    case.put(F, b'\xc3', retail=b'\xc3')
    proof = {'deps': {'game/settings.hxx': 'a' * 64}, 'search_roots': ['game'], 'inventory': 'b' * 64}
    obj.with_suffix('.deps.json').write_text(json.dumps(proof))
    monkeypatch.setattr(build, 'row_object', lambda row: obj)
    case.measure()
    graph = cr.load_graph(tmp_path / 'measurement' / cr.GRAPH_FILE)
    unit = next(n for n in graph[0] if n[0] == 'unit')
    assert graph[3](unit)['include_proofs'] == {'game/root.cpp': proof}


def test_graph_cannot_hide_generated_notes_behind_functional_kind(tmp_path, monkeypatch):
    case = ImageCase(tmp_path, monkeypatch)
    obj = case.object('leaf.obj', [('.text', b'\xc3', [])], [('_leaf', 1, 0, lc.EXTERNAL)])
    case.row(obj, '_leaf', F, 1, notes='gen-funclet')
    case.public(obj, '_leaf', F)
    case.put(F, b'\xc3', retail=b'\xc3')
    case.measure()
    doc = json.loads(cr.read_bytes(tmp_path / 'measurement' / cr.GRAPH_FILE))
    key = next(iter(doc['nodes']))
    # Simulate a graph that kept the functional label but lost dump edges.
    doc['nodes']['unit:other'] = dict(kind='unit', ok=True, name='caller', source='game/caller.cpp', failures=[])
    doc['edges']['unit:other'] = [key]
    with pytest.raises(cr.ReportError, match='generated/assembly source closure'):
        cr.graph_from_doc(doc)


def test_pointer_collision_does_not_poison_route_only_call():
    measure = lc.Measure.__new__(lc.Measure)
    measure._init_state()
    measure.ilt_body = lambda rva: rva
    first, second, call = [], [], []
    measure.code_identity(0x1000, 0x2000, pointer=True, fails=first)
    measure.code_identity(0x1008, 0x2000, pointer=True, fails=second)
    measure.code_identity(0x1000, 0x2000, pointer=False, fails=call)
    measure.settle_code_identities()
    assert first and second
    assert call == []


@pytest.mark.parametrize('width,indexed,closed', [(4, False, True), (8, False, False), (4, True, False)])
def test_import_equivalence_does_not_prove_adjacent_storage(width, indexed, closed):
    from test_link_cycle import _import_measure
    identity = lc.import_key('kernel32.dll', 'Foo')
    measure = _import_measure({0x6000: identity}, {0x6100: identity})
    reference = (0x6000, 0x6100, '__imp__Foo', None, None, 0, 'read', width, indexed)
    measure.discover([reference])
    failures, _, _ = measure.ref_check(reference)
    assert bool(failures) == (not closed)


def test_data_only_provider_keeps_receipt_include_witness(tmp_path, monkeypatch):
    from test_cycle_review2_evidence import DATA, RDATA, dword
    case = ImageCase(tmp_path, monkeypatch)
    raw = b'\xa1' + bytes(4) + b'\xc3'
    obj = case.object('root.obj', [('.text', raw, [(1, '_g', lc.DIR32)])],
                      [('_root', 1, 0, lc.EXTERNAL), ('_g', 0, 0, lc.EXTERNAL)])
    data = case.object('data.obj', [('.data', bytes(4), [])], [('_g', 1, 0, lc.EXTERNAL)])
    case.row(obj, '_root', F, 6)
    case.public(obj, '_root', F)
    case.public(data, '_g', DATA)
    case.put(F, raw, retail=raw)
    case.ptr(F + 1, DATA)
    case.R[F + 1:F + 5] = dword(lc.BASE + RDATA)
    reverse = tmp_path / 'targets/game/reverse'
    reverse.mkdir(parents=True)
    (reverse / 'data_rows.csv').write_text(
        'name,address,address_kind,size,source,status\n_g,0x81000,rva,4,game/data.cpp,matched\n')
    output = tmp_path / 'measurement'
    output.mkdir()
    (output / 'compile_inputs.json').write_text(json.dumps({'entries': {'data.obj': {
        'source': str(tmp_path / 'game/data.cpp'), 'command': [],
        'input': {'files': {str(tmp_path / 'shared/config.ipp'): 'a' * 64}}}}}))
    monkeypatch.setattr(build, 'ROOT', tmp_path)
    monkeypatch.setattr(build, '_include_search_roots', lambda *a: [tmp_path / 'game'])
    monkeypatch.setattr(build, 'row_object', lambda row: data if row['source'] == 'game/data.cpp' else obj)
    case.measure()
    graph = cr.load_graph(output / cr.GRAPH_FILE)
    datum = next(node for node in graph[0] if node[0] == 'datum')
    description = graph[3](datum)
    assert description['sources'] == ['game/data.cpp']
    assert description['include_proofs']['game/data.cpp']['deps'] == {'shared/config.ipp': 'a' * 64}
