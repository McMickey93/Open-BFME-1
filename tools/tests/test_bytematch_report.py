"""ByteMatch export: real source only, immutable input identity, no invented metrics."""
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import ExitStack
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import bytematch_report as export


class ReportTests(unittest.TestCase):
    def measure(self, rows, image, texts=None, notes=None):
        start = 0x1000
        notes = notes or {key: "" for key in rows}
        reader = lambda rva, size: image[rva - start:rva - start + size]
        with ExitStack() as stack:
            values = {
                "matched_at": rows, "notes_at": notes,
                "retail_text": (start, len(image)), "_text_image": (start, image),
            }
            for name, value in values.items():
                stack.enter_context(patch.object(export.progress, name, return_value=value))
            stack.enter_context(patch.object(export.progress.build, "read_target_bytes", side_effect=reader))
            stack.enter_context(patch.object(
                export.progress, "naked_cpp_rows_at",
                side_effect=lambda matched, ref: export.progress.naked_cpp_rows(matched, texts or {}, reader),
            ))
            stack.enter_context(patch.object(export.progress_v2, "hatch_totals", return_value={"emit": 4}))
            stack.enter_context(patch.object(export.progress_v2, "gate_debt", return_value=2))
            return export.measure("a" * 40)

    def test_padding_overlap_and_provenance(self):
        rows = {
            ("clean", "0x1000"): (4, "game/clean.cpp"),
            ("overlap", "0x1001"): (3, "game/overlap.cpp"),
            ("vendor", "0x1003"): (3, "inputs/vendor/zlib/inflate.c"),
            ("generated", "0x1006"): (3, "game/gen_small/eh.cpp"),
            ("dump", "0x1009"): (3, "game/gen_asm/dump.asm"),
            ("library", "0x100c"): (3, "inputs/vendor/library.lib"),
        }
        image = b"\x90\xcc" + b"\x90" * 16
        report, provenance = self.measure(rows, image)
        self.assertEqual(report["measures"], {
            "total_code": 17, "matched_code": 5, "matched_code_percent": 100 * 5 / 17,
        })
        self.assertEqual(provenance["source_lanes"], {
            "authored": 3, "vendored": 2, "generated": 3, "library": 3, "dump": 3,
        })
        self.assertEqual(provenance["padding_bytes"], 1)
        self.assertEqual(provenance["unclaimed_code_bytes"], 3)
        self.assertEqual(provenance["counters"]["matched_ledger_rows"], 6)
        self.assertEqual(provenance["counters"]["registered_hatches"], {"emit": 4})
        self.assertEqual(provenance["counters"]["gate_debt"], 2)

    def test_naked_and_emit_bodies_are_dump_debt(self):
        rows = {
            ("?raw@Widget@@QAEXXZ", "0x1000"): (3, "game/raw.cpp"),
            ("?spray@@YAXXZ", "0x1003"): (4, "game/spray.cpp"),
        }
        texts = {
            "game/raw.cpp": "__declspec(naked) void Widget::raw() { __asm { ret } }\n",
            "game/spray.cpp": "void spray() {\n __asm {\n __emit 0x90\n __emit 0x90\n"
                              " __emit 0x90\n __emit 0x90\n }\n}\n",
        }
        report, provenance = self.measure(rows, b"\x90" * 7, texts)
        self.assertEqual(report["measures"]["matched_code"], 0)
        self.assertEqual(provenance["source_lanes"]["dump"], 7)

    def test_generated_note_is_excluded_outside_generated_directory(self):
        key = ("helper", "0x1000")
        report, provenance = self.measure(
            {key: (3, "game/helper.cpp")}, b"\x90" * 3, notes={key: "gen-thunk"},
        )
        self.assertEqual(report["measures"]["matched_code"], 0)
        self.assertEqual(provenance["source_lanes"]["generated"], 3)

    def test_empty_and_padding_only_images_are_zero_not_complete(self):
        for image in (b"", b"\xcc" * 4):
            with self.subTest(image=image):
                report, provenance = self.measure({}, image)
                self.assertEqual(report["measures"], {
                    "total_code": 0, "matched_code": 0, "matched_code_percent": 0.0,
                })
                self.assertEqual(provenance["padding_bytes"], len(image))

    def test_outside_text_claims_do_not_inflate_progress(self):
        report, provenance = self.measure({
            ("before", "0xffe"): (4, "game/before.cpp"),
            ("after", "0x1003"): (4, "game/after.cpp"),
            ("outside", "0x2000"): (100, "game/outside.cpp"),
        }, b"\x90" * 4)
        self.assertEqual(report["measures"]["matched_code"], 3)
        self.assertEqual(provenance["unclaimed_code_bytes"], 1)

    def test_summary_does_not_invent_other_measurements(self):
        report, provenance = self.measure({}, b"\x90" * 4)
        self.assertEqual(report["version"], 2)
        self.assertEqual(set(report["measures"]), {"total_code", "matched_code", "matched_code_percent"})
        self.assertEqual(report["units"], [])
        self.assertEqual(report["categories"], [])
        self.assertEqual(provenance["unreported"], ["functions", "units", "data", "linked", "fuzzy_match"])
        self.assertIn("no fresh compilation", provenance["measurement"])
        self.assertEqual(json.loads(export.json_text(report)), report)

    def test_source_lane_policy_cannot_silently_start_crediting_generators(self):
        with patch.object(export.progress, "DECOMPILED_LANES", ("authored", "vendored", "generated")):
            with self.assertRaisesRegex(ValueError, "authored and vendored"):
                export.measure("a" * 40)

    def test_invalid_byte_counts_fail(self):
        cases = ({"authored": 5, "vendored": 0}, {"authored": -1, "vendored": 0},
                 {"authored": 1.5, "vendored": 0}, {"authored": True, "vendored": 0})
        for lanes in cases:
            with self.subTest(lanes=lanes), patch.object(export.progress, "real_split", return_value=lanes):
                with self.assertRaisesRegex(ValueError, "byte counts|retail .text"):
                    self.measure({}, b"\x90" * 4)


class CommandTests(unittest.TestCase):
    def test_explicit_target_binding_cannot_be_reported_as_game_progress(self):
        for key in ("BFME_TARGET", "BFME_TARGET_SHA256"):
            with self.subTest(key=key), patch.dict(os.environ, {key: "worldbuilder"}), \
                    patch.object(export, "measure") as measure:
                with self.assertRaisesRegex(SystemExit, key):
                    export.main([])
                measure.assert_not_called()

    def test_checkout_identity_and_dirty_tree_fail_closed(self):
        commit = "a" * 40
        clean = [subprocess.CompletedProcess([], 0, commit + "\n"), subprocess.CompletedProcess([], 0)]
        with patch.object(export.subprocess, "run", side_effect=clean):
            self.assertEqual(export.checkout_commit(commit), commit)
        with patch.object(export.subprocess, "run", return_value=clean[0]):
            with self.assertRaisesRegex(ValueError, "expected"):
                export.checkout_commit("b" * 40)
        with patch.object(export.subprocess, "run", side_effect=[clean[0], subprocess.CompletedProcess([], 1)]):
            with self.assertRaisesRegex(ValueError, "clean committed checkout"):
                export.checkout_commit(commit)

    def test_cli_writes_only_json_and_binds_provenance_to_report(self):
        report = {"version": 2, "measures": {"total_code": 10, "matched_code": 2, "matched_code_percent": 20}}
        provenance = {"commit": "a" * 40}
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory) / "output"
            with patch.object(export, "checkout_commit", return_value="a" * 40) as checkout, \
                    patch.object(export, "measure", return_value=(report, provenance)):
                self.assertEqual(export.main(["--output-dir", str(out), "--expected-commit", "a" * 40]), 0)
            self.assertEqual(checkout.call_count, 2)
            self.assertEqual({path.name for path in out.iterdir()}, {"report.json", "provenance.json"})
            raw = (out / "report.json").read_bytes()
            details = json.loads((out / "provenance.json").read_text())
            self.assertEqual(json.loads(raw), report)
            self.assertEqual(details["report_sha256"], hashlib.sha256(raw).hexdigest())
            self.assertEqual(raw, export.json_text(report).encode("utf-8"))

    def test_checkout_moving_during_measurement_writes_no_report(self):
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory) / "output"
            with patch.object(export, "checkout_commit", side_effect=["a" * 40, ValueError("checkout moved")]), \
                    patch.object(export, "measure", return_value=({}, {})):
                with self.assertRaises(SystemExit) as error:
                    export.main(["--output-dir", str(out)])
            self.assertEqual(error.exception.code, 1)
            self.assertFalse(out.exists())


if __name__ == "__main__":
    unittest.main()
