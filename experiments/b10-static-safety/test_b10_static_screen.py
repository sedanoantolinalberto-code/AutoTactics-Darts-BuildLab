"""Synthetic parse-only B41 tests; deliberately NEVER execute the code snippets."""
import tempfile
import unittest
from pathlib import Path

from b10_static_screen import scan_source, scan_tree, _int_literal
import ast


class StaticSafetyTests(unittest.TestCase):
    def codes(self, source):
        return {item["code"] for item in scan_source(source)}

    def test_direct_kill_all_blocked(self):
        self.assertIn("BROAD_SIGNAL_TARGET", self.codes("import os\nos.kill(-1, 9)\n"))

    def test_direct_process_group_zero_blocked(self):
        self.assertIn("BROAD_SIGNAL_TARGET", self.codes("kill(0, 9)\n"))

    def test_alias_kill_all_blocked(self):
        self.assertIn("BROAD_SIGNAL_TARGET",
                      self.codes("from os import kill as k\nk(-1, 9)\n"))

    def test_libc_kill_with_ctypes_int_minus_one_blocked(self):
        self.assertIn("BROAD_SIGNAL_TARGET",
                      self.codes("import ctypes\nlibc.kill(ctypes.c_int(-1), 9)\n"))

    def test_reported_incident_literal_saved_in_variable_detected(self):
        code = self.codes("custody_flags = 1 << 40\nlibc.unshare(custody_flags)\n")
        self.assertIn("UNSHARE_FLAG_OUT_OF_RANGE", code)

    def test_symbolic_all_processes_signal_detected(self):
        code = self.codes("ALL = -1\nos.kill(ALL, 9)\n")
        self.assertIn("BROAD_SIGNAL_TARGET", code)

    def test_symbolic_ctypes_narrowing_detected(self):
        code = self.codes("custody_flags = 1 << 40\nctypes.c_int(custody_flags)\n")
        self.assertIn("C_INT_NARROWING", code)

    def test_reassigned_constant_downgrades_to_manual_review(self):
        code = self.codes("custody_flags = 1 << 40\ncustody_flags = 1 << 29\nlibc.unshare(custody_flags)\n")
        self.assertIn("DYNAMIC_UNSHARE_REQUIRES_REVIEW", code)

    def test_killpg_current_group_blocked(self):
        self.assertIn("BROAD_PROCESS_GROUP", self.codes("import os\nos.killpg(0, 9)\n"))

    def test_unshare_zero_blocked(self):
        self.assertIn("UNSHARE_ZERO_NO_NAMESPACE", self.codes("libc.unshare(0)\n"))

    def test_unshare_oversized_shift_blocked(self):
        self.assertIn("UNSHARE_FLAG_OUT_OF_RANGE", self.codes("libc.unshare(1 << 40)\n"))

    def test_ctypes_overflow_independently_detected(self):
        code = self.codes("import ctypes\nctypes.c_int(1 << 40)\n")
        self.assertIn("C_INT_NARROWING", code)

    def test_ctypes_unsigned_overflow_detected(self):
        self.assertIn("C_UINT_NARROWING", self.codes("ctypes.c_uint(-1)\n"))

    def test_dynamic_unshare_needs_review(self):
        self.assertIn("DYNAMIC_UNSHARE_REQUIRES_REVIEW",
                      self.codes("libc.unshare(flags)\n"))

    def test_wrong_literal_namespace_flag_blocked(self):
        self.assertIn("UNSHARE_FLAGS_NOT_EXACT_NEWPID",
                      self.codes("libc.unshare(0x10000000)\n"))

    def test_exact_literal_flag_is_only_static_screen_not_native_authorization(self):
        self.assertFalse(self.codes("libc.unshare(0x20000000)\n"))
        with tempfile.TemporaryDirectory() as td:
            candidate = Path(td) / "sample.py"
            candidate.write_text("libc.unshare(0x20000000)\n", encoding="utf-8")
            result = scan_tree(candidate)
            self.assertEqual(result["decision"], "STATIC_SCREEN_NO_FINDINGS_NOT_QUALIFIED")
            self.assertFalse(result["native_test_authorized"])
            self.assertFalse(result["production_go"])

    def test_valid_group_kill_by_specific_id_not_flagged(self):
        # Absence of a finding is *not* a proof that pid is owned.
        self.assertFalse(self.codes("os.kill(pid, 9)\n"))

    def test_unrelated_text_is_not_evaluated_or_interpreted(self):
        fake = "print('kill(-1, SIGKILL)')\nraise RuntimeError('NOT_EXECUTED')\n"
        self.assertFalse(self.codes(fake))

    def test_source_parse_failure_blocks(self):
        self.assertIn("SOURCE_PARSE_INVALID", self.codes("def invalid(\n"))

    def test_empty_directory_blocks(self):
        with tempfile.TemporaryDirectory() as td:
            result = scan_tree(Path(td))
            self.assertEqual(result["decision"], "BLOCKED_STATIC_FINDINGS")
            self.assertIn("NO_PYTHON_FILES", {i["code"] for i in result["findings"]})

    def test_bad_source_detected_without_running_it(self):
        with tempfile.TemporaryDirectory() as td:
            f = Path(td) / "threat.py"
            f.write_text("raise RuntimeError('not executed')\nlibc.kill(-1, 9)\n",
                         encoding="utf-8")
            result = scan_tree(f)
            self.assertEqual(result["files_examined"], 1)
            self.assertIn("BROAD_SIGNAL_TARGET", {i["code"] for i in result["findings"]})

    def test_symlink_to_regular_source_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "real.py").write_text("print('safe')\n", encoding="utf-8")
            (root / "alias.py").symlink_to(root / "real.py")
            report = scan_tree(root)
            self.assertIn("SYMLINK_FILE", {x["code"] for x in report["findings"]})

    def test_directory_symlink_not_traversed(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "real").mkdir()
            (root / "real" / "child.py").write_text("print('safe')\n", encoding="utf-8")
            (root / "alias").symlink_to(root / "real", target_is_directory=True)
            report = scan_tree(root)
            self.assertIn("SYMLINK_DIRECTORY", {x["code"] for x in report["findings"]})

    def test_oversize_file_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            f = Path(td) / "big.py"
            f.write_bytes(b"#" + b"a" * 520_000)
            report = scan_tree(f)
            self.assertIn("SOURCE_UNREADABLE", {x["code"] for x in report["findings"]})

    def test_literal_shift_is_bounded_and_pure(self):
        expr = ast.parse("1 << 40", mode="eval").body
        self.assertEqual(_int_literal(expr), 2**40)
        huge = ast.parse("1 << 100000", mode="eval").body
        self.assertIsNone(_int_literal(huge))

    def test_no_candidate_code_is_ever_executed(self):
        # If the implementation imported/ran snippets, it would terminate CI.
        snippet = "import os\nos._exit(93)\n"
        self.assertFalse(self.codes(snippet))


if __name__ == "__main__":
    unittest.main(verbosity=2)
