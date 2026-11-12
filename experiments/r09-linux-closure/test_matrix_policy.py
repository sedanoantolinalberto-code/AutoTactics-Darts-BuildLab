"""Synthetic tests ONLY: no claims about real T21-R09 suites."""
import copy
import hashlib
import tempfile
import unittest
from pathlib import Path

from matrix_policy import EXPECTED, SCHEMA, evaluate


class MatrixTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.doc = self.new_doc("root")

    def new_doc(self, mode):
        uid = 0 if mode == "root" else 65534
        suites = []
        for index, (name, count) in enumerate(EXPECTED.items()):
            fname = f"synthetic-{name}.log"
            content = f"SYNTHETIC POLICY CHECK {index} - NOT A T21 RUN\n".encode()
            (self.root / fname).write_bytes(content)
            suites.append({"name":name, "expected":count, "passed":count,
                "failed":0, "errors":0, "skipped":0, "xfailed":0,
                "exit_status":0, "log_path":fname,
                "log_sha256":hashlib.sha256(content).hexdigest()})
        return {"schema":SCHEMA, "mode":mode, "uid":uid, "suites":suites,
                "evidence_kind":"SYNTHETIC_POLICY_TEST"}

    def result(self, doc=None):
        return evaluate(self.doc if doc is None else doc, self.root)

    def blocked(self, doc):
        out = self.result(doc)
        self.assertNotIn(out["status"], ("COMPLETE_LOCAL_BATCHED_UNQUALIFIED_PASS",))
        self.assertFalse(out["production_go"])
        self.assertFalse(out["qualification"])
        return out

    def test_synthetic_root_all_pass_is_not_real_run(self):
        out = self.result()
        self.assertEqual(out["status"], "SYNTHETIC_COMPLETE_LOCAL_BATCHED_UNQUALIFIED_PASS")
        self.assertEqual(out["counts"]["passed"], 710)

    def test_root_all_pass_observed_receipt_policy_only(self):
        doc = copy.deepcopy(self.doc)
        doc["evidence_kind"] = "OBSERVED_NATIVE"
        self.assertEqual(self.result(doc)["status"], "COMPLETE_LOCAL_BATCHED_UNQUALIFIED_PASS")
        # This only proves that a syntactically native-marked receipt can satisfy
        # the policy. It does NOT authenticate the provenance of its logs.

    def test_unprivileged_two_skips_do_not_pass(self):
        doc = self.new_doc("unprivileged")
        doc["suites"][0]["passed"] -= 2
        doc["suites"][0]["skipped"] = 2
        self.assertEqual(self.blocked(doc)["status"], "SYNTHETIC_BLOCKED_SKIPPED_OR_XFAIL")

    def test_xfail_does_not_pass(self):
        self.doc["suites"][2]["passed"] -= 1
        self.doc["suites"][2]["xfailed"] = 1
        self.assertEqual(self.blocked(self.doc)["status"], "SYNTHETIC_BLOCKED_SKIPPED_OR_XFAIL")

    def test_fail_does_not_pass(self):
        self.doc["suites"][1]["passed"] -= 1
        self.doc["suites"][1]["failed"] = 1
        self.assertEqual(self.blocked(self.doc)["status"], "SYNTHETIC_BLOCKED_FAIL_OR_ERROR")

    def test_error_does_not_pass(self):
        self.doc["suites"][1]["passed"] -= 1
        self.doc["suites"][1]["errors"] = 1
        self.assertEqual(self.blocked(self.doc)["status"], "SYNTHETIC_BLOCKED_FAIL_OR_ERROR")

    def test_nonzero_exit_blocks_even_if_all_green(self):
        self.doc["suites"][3]["exit_status"] = 1
        self.assertEqual(self.blocked(self.doc)["status"], "SYNTHETIC_BLOCKED_EXIT_STATUS")

    def test_missing_suite_is_blocked(self):
        self.doc["suites"].pop()
        self.blocked(self.doc)

    def test_duplicate_suite_is_blocked(self):
        self.doc["suites"][3]["name"] = "r07"
        self.blocked(self.doc)

    def test_wrong_expected_count_is_blocked(self):
        self.doc["suites"][0]["expected"] = 633
        self.blocked(self.doc)

    def test_missing_completed_test_is_blocked(self):
        self.doc["suites"][0]["passed"] -= 1
        self.blocked(self.doc)

    def test_negative_count_is_blocked(self):
        self.doc["suites"][1]["passed"] = -1
        self.blocked(self.doc)

    def test_boolean_count_is_blocked(self):
        self.doc["suites"][2]["passed"] = True
        self.blocked(self.doc)

    def test_tampered_log_hash_is_blocked(self):
        (self.root / "synthetic-r07.log").write_text("MODIFIED")
        self.blocked(self.doc)

    def test_log_path_escape_is_blocked(self):
        self.doc["suites"][0]["log_path"] = "../escape.log"
        self.blocked(self.doc)

    def test_unexpected_schema_field_is_blocked(self):
        self.doc["suites"][0]["all_passed"] = True
        self.blocked(self.doc)

    def test_uid_mode_mismatch_is_blocked(self):
        self.doc["uid"] = 65534
        self.blocked(self.doc)

    def test_unexpected_evidence_kind_is_blocked(self):
        self.doc["evidence_kind"] = "CLAUDE_CERTIFIED"
        self.blocked(self.doc)

    def test_unhashable_suite_name_must_not_raise(self):
        self.doc["suites"][0]["name"] = ["official"]
        self.blocked(self.doc)

    def test_invalid_receipt_object_is_blocked(self):
        self.blocked(None)


if __name__ == "__main__":
    unittest.main(verbosity=2)
