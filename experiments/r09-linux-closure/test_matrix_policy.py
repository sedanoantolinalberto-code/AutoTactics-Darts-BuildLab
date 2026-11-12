"""Synthetic tests ONLY: no claims about real T21-R09 suites."""
import copy
import hashlib
import os
import time
import tempfile
import unittest
import json
from pathlib import Path

from matrix_policy import EXPECTED, SCHEMA, RESULT_SCHEMA, evaluate

_DEFAULT = object()


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
            content = self.make_log(name, count)
            (self.root / fname).write_bytes(content)
            suites.append({"name":name, "expected":count, "passed":count,
                "failed":0, "errors":0, "skipped":0, "xfailed":0,
                "exit_status":0, "log_path":fname,
                "log_sha256":hashlib.sha256(content).hexdigest()})
        return {"schema":SCHEMA, "mode":mode, "uid":uid, "suites":suites,
                "evidence_kind":"SYNTHETIC_POLICY_TEST"}

    @staticmethod
    def make_log(name, count, replacements=None):
        replacements = replacements or {}
        rows = [
            {"schema": RESULT_SCHEMA, "case_id": f"{name}:{i:04d}",
             "status": replacements.get(i, "PASS")}
            for i in range(count)
        ]
        return (("\n".join(json.dumps(r, separators=(",", ":"), sort_keys=True)
                           for r in rows)) + "\n").encode("utf-8")

    def set_log(self, suite_idx, content):
        item = self.doc["suites"][suite_idx]
        (self.root / item["log_path"]).write_bytes(content)
        item["log_sha256"] = hashlib.sha256(content).hexdigest()

    def result(self, doc=_DEFAULT):
        return evaluate(self.doc if doc is _DEFAULT else doc, self.root)

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
        item = doc["suites"][0]
        newlog = self.make_log("official", item["expected"], {0:"SKIP",1:"SKIP"})
        (self.root / item["log_path"]).write_bytes(newlog)
        item["log_sha256"] = hashlib.sha256(newlog).hexdigest()
        self.assertEqual(self.blocked(doc)["status"], "SYNTHETIC_BLOCKED_SKIPPED_OR_XFAIL")

    def test_xfail_does_not_pass(self):
        self.doc["suites"][2]["passed"] -= 1
        self.doc["suites"][2]["xfailed"] = 1
        self.set_log(2, self.make_log("r07", 13, {0:"XFAIL"}))
        self.assertEqual(self.blocked(self.doc)["status"], "SYNTHETIC_BLOCKED_SKIPPED_OR_XFAIL")

    def test_fail_does_not_pass(self):
        self.doc["suites"][1]["passed"] -= 1
        self.doc["suites"][1]["failed"] = 1
        self.set_log(1, self.make_log("additional", 49, {0:"FAIL"}))
        self.assertEqual(self.blocked(self.doc)["status"], "SYNTHETIC_BLOCKED_FAIL_OR_ERROR")

    def test_error_does_not_pass(self):
        self.doc["suites"][1]["passed"] -= 1
        self.doc["suites"][1]["errors"] = 1
        self.set_log(1, self.make_log("additional", 49, {0:"ERROR"}))
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

    def test_fifo_log_rejected_without_writer_or_hang(self):
        path = self.root / "synthetic-r07.log"
        path.unlink()
        os.mkfifo(path)
        start = time.monotonic()
        self.blocked(self.doc)
        self.assertLess(time.monotonic() - start, 0.8, "Opening FIFO blocked the verifier")

    def test_symlink_log_rejected_even_if_target_is_valid(self):
        path = self.root / "synthetic-r07.log"
        target = self.root / "good-data.log"
        path.rename(target)
        path.symlink_to(target)
        self.blocked(self.doc)

    def test_intermediate_symlink_directory_rejected(self):
        real = self.root / "real"
        real.mkdir()
        (real / "log.txt").write_bytes(b"safe")
        (self.root / "alias").symlink_to(real, target_is_directory=True)
        self.doc["suites"][0]["log_path"] = "alias/log.txt"
        self.doc["suites"][0]["log_sha256"] = hashlib.sha256(b"safe").hexdigest()
        self.blocked(self.doc)

    def test_oversized_log_is_rejected(self):
        path = self.root / "synthetic-r07.log"
        big = b"A" * 2_000_001
        path.write_bytes(big)
        self.doc["suites"][2]["log_sha256"] = hashlib.sha256(big).hexdigest()
        self.blocked(self.doc)

    def test_valid_nested_log_still_works(self):
        subdir = self.root / "nested"
        subdir.mkdir()
        payload = self.make_log("official", 634)
        (subdir / "log.txt").write_bytes(payload)
        self.doc["suites"][0]["log_path"] = "nested/log.txt"
        self.doc["suites"][0]["log_sha256"] = hashlib.sha256(payload).hexdigest()
        result = self.result()
        self.assertEqual(result["status"], "SYNTHETIC_COMPLETE_LOCAL_BATCHED_UNQUALIFIED_PASS")

    def test_null_log_path_is_rejected(self):
        self.doc["suites"][0]["log_path"] = None
        self.blocked(self.doc)

    def test_f1_forged_all_pass_receipt_with_skipped_log_rejected(self):
        # Reproduce Claude F1: matching SHA is not a trustworthy PASS count.
        self.set_log(0, self.make_log("official", 634, {0:"SKIP"}))
        out = self.blocked(self.doc)
        self.assertEqual(out["reason"], "DECLARED_COUNTS_DISAGREE_WITH_LOG")

    def test_f1_hashed_plaintext_skipped_log_rejected(self):
        self.set_log(0, b"skipped\n")
        self.assertEqual(self.blocked(self.doc)["reason"], "LOG_CONTENT_INVALID_OR_INCOMPLETE")

    def test_exact_legacy_receipt_version_rejected(self):
        self.doc["schema"] = "engineyt-r09-suite-receipts/0.1"
        self.blocked(self.doc)

    def test_log_extra_json_field_rejected(self):
        raw = self.make_log("r09", 14)
        obj = json.loads(raw.splitlines()[0])
        obj["authorized"] = True
        rows = raw.splitlines()
        rows[0] = json.dumps(obj).encode()
        self.set_log(3, b"\n".join(rows) + b"\n")
        self.blocked(self.doc)

    def test_log_duplicate_case_id_rejected(self):
        rows = self.make_log("r07", 13).splitlines()
        rows[1] = rows[0]
        self.set_log(2, b"\n".join(rows) + b"\n")
        self.blocked(self.doc)

    def test_duplicate_json_status_field_rejected(self):
        rows = self.make_log("r07", 13).splitlines()
        rows[0] = (b'{"schema":"engineyt-r09-case-result/0.1",'
                   b'"case_id":"r07:0000","status":"SKIP","status":"PASS"}')
        self.set_log(2, b"\n".join(rows) + b"\n")
        self.assertEqual(self.blocked(self.doc)["reason"],
                         "LOG_CONTENT_INVALID_OR_INCOMPLETE")

    def test_log_unexpected_status_rejected(self):
        self.set_log(2, self.make_log("r07", 13, {0:"UNEXPECTED_SUCCESS"}))
        self.blocked(self.doc)

    def test_log_truncated_rejected(self):
        self.set_log(2, self.make_log("r07", 12))
        self.blocked(self.doc)

    def test_log_invalid_utf8_rejected(self):
        self.set_log(2, b"\xff\n")
        self.blocked(self.doc)

    def test_log_missing_final_newline_rejected(self):
        self.set_log(2, self.make_log("r07", 13).rstrip(b"\n"))
        self.blocked(self.doc)

    def test_log_summary_solely_with_claimed_passes_rejected(self):
        self.set_log(2, b"13 passed, 0 skipped\n")
        self.blocked(self.doc)

    def test_log_forged_omission_and_fresh_digest_cannot_pass(self):
        self.set_log(2, self.make_log("r07", 13, {3:"XFAIL"}))
        self.assertEqual(self.blocked(self.doc)["reason"],
                         "DECLARED_COUNTS_DISAGREE_WITH_LOG")

    def test_hash_on_valid_jsonl_is_accepted_for_policy_only(self):
        self.assertEqual(self.result()["status"],
                         "SYNTHETIC_COMPLETE_LOCAL_BATCHED_UNQUALIFIED_PASS")

    def test_invalid_receipt_object_is_blocked(self):
        self.blocked(None)


if __name__ == "__main__":
    unittest.main(verbosity=2)
