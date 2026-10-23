"""Round-3 currency counterexample, in a temporary Git repository only."""
import json

import pytest

from test_cycle_review2_admission import initialize, commit
from test_cycle_review2_evidence import ImageCase, F, DATA, RDATA, dword, lc
import closure_report as cr
import repair_queue as rq


@pytest.mark.parametrize('renamed', [False, True])
@pytest.mark.parametrize('change', ['source', 'include'])
def test_secondary_datum_in_an_admitted_data_tu_retains_provider_currency(tmp_path, monkeypatch, change, renamed):
    initialize(tmp_path)
    case = ImageCase(tmp_path, monkeypatch)
    raw = b'\xa1' + bytes(4) + b'\xc3'
    root = case.object('root.obj', [('.text', raw, [(1, '_g', lc.DIR32)])],
                       [('_root', 1, 0, lc.EXTERNAL), ('_g', 0, 0, lc.EXTERNAL)])
    data = case.object('zz000001.obj' if renamed else 'data.obj', [('.data', dword(2) + dword(0), [])],
                       [('_g', 1, 0, lc.EXTERNAL), ('_anchor', 1, 4, lc.EXTERNAL)])
    case.row(root, '_root', F, len(raw))
    case.public(root, '_root', F)
    case.public(data, '_g', DATA)
    case.public(data, '_anchor', DATA + 4)
    if renamed:
        case.publics.update(_g=(DATA, 'data.obj'), _anchor=(DATA + 4, 'data.obj'))
        original_objects = lc.Objects
        class RenamedObjects(original_objects):
            def __init__(self, paths):
                super().__init__(paths)
                self.by_base['data.obj'] = data
        monkeypatch.setattr(lc, 'Objects', RenamedObjects)
    case.put(F, raw, retail=raw)
    case.ptr(F + 1, DATA)
    case.R[F + 1:F + 5] = dword(lc.BASE + RDATA)
    case.put(DATA, dword(2) + dword(0))
    case.R[RDATA:RDATA + 8] = dword(1) + dword(0)
    (tmp_path / 'game').mkdir()
    (tmp_path / 'game/root.cpp').write_text('extern int g; int root() { return g; }\n')
    source = tmp_path / 'game/data.cpp'
    source.write_text('int g = 2; int anchor = 0;\n')
    reverse = tmp_path / 'targets/game/reverse'
    reverse.mkdir(parents=True)
    # _anchor admits/compiles this TU through link_census.data_sources(). _g is
    # a second public in the same selected object, independently scanned.
    (reverse / 'data_rows.csv').write_text(
        'name,address,address_kind,size,source,status\n_anchor,0x81004,rva,4,game/data.cpp,matched\n')
    header = tmp_path / 'game/settings.ipp'
    header.write_text('const int value = 2;\n')
    proof = {'deps': {'game/settings.ipp': lc.sha256(header)}, 'search_roots': ['game'], 'inventory': 'b' * 64}
    data.with_suffix('.deps.json').write_text(json.dumps(proof))
    monkeypatch.setattr(lc.build, 'row_object', lambda row: data if row['source'] == 'game/data.cpp' else root)
    measured = commit(tmp_path, ['game', 'targets'], 'measured data provider')
    result, _ = case.measure()
    assert result['credit_unique_bytes'] == 0
    graph = cr.load_graph(tmp_path / 'measurement' / cr.GRAPH_FILE)
    datum = next(n for n in graph[0] if n[0] == 'datum')
    description = graph[3](datum)
    assert description['sources'] == ['game/data.cpp']
    assert description['include_proofs'] == {'game/data.cpp': proof}
    repaired = source if change == 'source' else header
    repaired.write_text('int g = 1; int anchor = 0;\n')
    commit(tmp_path, [str(repaired.relative_to(tmp_path))], 'repair second global')
    item = dict(function='_root', target_rva='0x00060000', source='game/root.cpp')
    kept, skipped = rq.current_bundle_items([item], measured, root=tmp_path, graph=graph)
    print(json.dumps(dict(datum=graph[3](datum), kept=len(kept), skipped=skipped), sort_keys=True))
    assert not kept and skipped[0]['reason'] == 'stale', 'selected data-object provider was lost for its second global'
