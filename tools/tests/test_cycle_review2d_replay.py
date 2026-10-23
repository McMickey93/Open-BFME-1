"""Fresh round-4 audit of 21 rows removed by delta4, read-only recorded inputs.

Twenty expected-behavior assertions fail on c36d018872; 22 byte-evidence and
short-vtable controls pass. No census, native tool or link is executed.
"""
import csv
import hashlib
import json
from pathlib import Path

import pytest

from test_cycle_review2c_replay import RecordedObjects, RUN, lc

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = Path(__file__).parent / "fixtures/cycle_review2d_audit.json"
EVIDENCE = json.loads(FIXTURE.read_text())
ROWS = {int(r["rva"], 16): r for r in EVIDENCE["rows"]}
FALSE_REFUSALS = [a for a, r in ROWS.items() if r["classification"] == "wrongly refused"]


def digest(path):
    with Path(path).open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


@pytest.fixture(scope="module")
def replay():
    if not (RUN / "base.exe").is_file():
        pytest.skip("owner-supplied run7_replay is unavailable")
    inputs = {name: RUN / name for name in EVIDENCE["inputs"] if name != "retail"}
    inputs["retail"] = lc.build.EXE
    for name, path in inputs.items():
        assert digest(path) == EVIDENCE["inputs"][name]
    for name, sha in EVIDENCE["sources"].items():
        assert digest(ROOT / name) == sha
    with (ROOT / "targets/game/reverse/functions.csv").open(newline="") as f:
        rows = [r for r in csv.DictReader(f) if r["status"] == "matched"
                and int(r["target_rva"], 16) in ROWS
                and r["name"] == ROWS[int(r["target_rva"], 16)]["name"]]
    assert len(rows) == 21
    names, _ = lc.zz_names(RUN)
    objs = RecordedObjects(names)
    original = lc.row_obj
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(lc, "row_obj", lambda row: Path("/recorded") / original(row).name.lower())
        units, _ = lc.analyze(rows, objs)
    _, R, rsecs, rimp = lc.pe_view(lc.build.EXE)
    _, I, isecs, limp = lc.pe_view(RUN / "base.exe")
    mapped = lc.read_map((RUN / "base.map").read_text(encoding="latin-1"), lc.BASE, names)
    m = lc.Measure(units, [], mapped, I, R, isecs, rimp, limp, {}, objs,
                   {int(r["target_rva"], 16): int(r["target_size"]) for r in rows})
    m.rsecs, m.retail_sites = rsecs, lc.retail_relocs.site_rvas()
    records = m.run()
    sh = lc.Shifted(RUN, I, isecs, rsecs, True, lc.SHIFT_BASE, set())
    yield m, {r["row"]["rva"]: r for r in records}, sh
    # The recorded run is an input, including its existing reports and receipts.
    for name, path in inputs.items():
        assert digest(path) == EVIDENCE["inputs"][name]


def selected_refs(m, rec, evidence):
    names = {r["name"] for r in evidence["refs"]}
    refs = {}
    for owner, ref in m.pending:
        if owner is rec and ref[2] in names:
            refs[ref[:3] + ref[7:9]] = ref
    return list(refs.values())


@pytest.mark.parametrize("rva", sorted(ROWS), ids=lambda a: f"{a:08X}")
def test_recorded_extent_evidence_and_all_verified_bytes(replay, rva):
    m, records, sh = replay
    rec, evidence = records[rva], ROWS[rva]
    at, size = rec["linked"], rec["row"]["size"]
    assert rec["placed"]
    assert lc.nonreloc_diffs(m.I[at:at+size], m.R[rva:rva+size], rec["masked"]) == 0
    assert sh.words(at, size, rec["masked"], rec["rels"]) is None
    refs = selected_refs(m, rec, evidence)
    assert len(refs) == len(evidence["refs"])
    for ref, recorded in zip(refs, evidence["refs"]):
        kind = m.resolve(ref)
        assert kind[0] == "datum"
        a, b, z = kind[1]
        node = m.dnodes[kind[1]]
        assert [hex(a), hex(b), z] == recorded["key"]
        assert not node["fails"]
        assert sh.data(kind[1], node) is None
        assert lc.nonreloc_diffs(m.I[a:a+z], m.R[b:b+z], node["masked"]) == 0
        assert bytes(m.R[b:b+min(z,64)]).hex() == recorded["raw"]
        assert ref[7] == recorded["width"] and ref[8] == recorded["indexed"]
        if recorded["width"] and not recorded["indexed"]:
            assert 0 <= ref[0]-a <= z-recorded["width"]
    assert evidence["full_run_status"]["closed_strict"] == "0"
    assert evidence["full_run_status"]["failures"].startswith("data-access-extent:")


@pytest.mark.parametrize("rva", sorted(FALSE_REFUSALS), ids=lambda a: f"{a:08X}")
def test_verified_datum_is_not_enlarged_by_inventory_padding(replay, rva):
    m, records, _ = replay
    evidence = ROWS[rva]
    # Keep the actual consumer eligible for ordinary copies, register
    # overwrites and branch-local address tags; fixing extent refusals must
    # not replace them with an unsupported numeric-observation refusal.
    assert not any(f.startswith('address-numeric-use:') for f in records[rva]['fails'])
    refs = selected_refs(m, records[rva], evidence)
    failures = [f for ref in refs for f in m.ref_check(ref)[0] if f.startswith("data-access-extent:")]
    if rva == 0x9D5980:
        # Final owner decision: bint also RETURNS &j. Its caller's range is
        # unknown, unlike the separate fixed dword store. Source allocation
        # and the inventory gap do not independently prove retail sizeof(j).
        fixed = [ref for ref in refs if ref[7] == 4]
        assert fixed and all(not m.ref_check(ref)[0] for ref in fixed)
        assert failures == ["data-access-extent:" + refs[-1][2]]
    else:
        assert not failures, (evidence["proof"], failures)


def test_real_short_vtable_still_refuses(replay):
    m, records, _ = replay
    rec, evidence = records[0x95C6F0], ROWS[0x95C6F0]
    ref, = selected_refs(m, rec, evidence)
    _, rstart, size = m.resolve(ref)[1]
    assert size == 4
    # Six retail entries: the destructor followed by five pure-call slots.
    assert [lc.u32(m.R, rstart+4*i)-lc.BASE for i in range(6)] == [0x95C6F0] + [0x88C500]*5
    assert "data-access-extent:" + ref[2] in m.ref_check(ref)[0]
