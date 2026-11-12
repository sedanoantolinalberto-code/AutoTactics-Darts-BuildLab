"""REVIEW-ONLY R09-6 strict accounting policy. No test execution.

Consumes four *already produced* suite receipts with real log-file hashes.
It verifies receipt consistency, not that the tests exercised real code.
Never turns SKIP, XFAIL or ERROR into PASS. Synthetic unit fixtures must not
be represented as observed T21-R09 evidence.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import stat
from pathlib import Path

SCHEMA = "engineyt-r09-suite-receipts/0.1"
EXPECTED = {"official": 634, "additional": 49, "r07": 13, "r09": 14}
COUNT_FIELDS = ("passed", "failed", "errors", "skipped", "xfailed")
ROOT_UID = 0
UNPRIV_UID = 65534

def _safe_log(root: Path, name: str, expected_hash: str) -> bool:
    """Hash only a regular file from a pinned fd under a trusted log root.

    O_NOFOLLOW, O_NONBLOCK, dir_fd traversal and fstat prevent the final
    pathname from being re-opened as a blocking FIFO after validation.
    This is a receipt/log integrity helper, NOT an isolation boundary.
    """
    if not isinstance(name, str) or not name or Path(name).is_absolute():
        return False
    if not isinstance(expected_hash, str) or len(expected_hash) != 64:
        return False
    if any(c not in "0123456789abcdef" for c in expected_hash):
        return False
    if "\\" in name or "\x00" in name:
        return False
    parts = name.split("/")
    if any(part in ("", ".", "..") for part in parts):
        return False

    dir_fd = -1
    file_fd = -1
    try:
        directory_flags = os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC | os.O_NOFOLLOW
        dir_fd = os.open(root, directory_flags)
        for component in parts[:-1]:
            next_fd = os.open(component, directory_flags, dir_fd=dir_fd)
            os.close(dir_fd)
            dir_fd = next_fd
        file_fd = os.open(parts[-1], os.O_RDONLY | os.O_NONBLOCK |
                          os.O_CLOEXEC | os.O_NOFOLLOW, dir_fd=dir_fd)
        initial = os.fstat(file_fd)
        if not stat.S_ISREG(initial.st_mode) or initial.st_size > 2_000_000:
            return False

        digest = hashlib.sha256()
        total = 0
        while True:
            block = os.read(file_fd, min(65536, 2_000_001 - total))
            if not block:
                break
            total += len(block)
            if total > 2_000_000:
                return False
            digest.update(block)
        final = os.fstat(file_fd)
        if (final.st_ino != initial.st_ino or
            final.st_dev != initial.st_dev or
            final.st_size != initial.st_size or
            final.st_mtime_ns != initial.st_mtime_ns or
            final.st_ctime_ns != initial.st_ctime_ns):
            return False
        return digest.hexdigest() == expected_hash
    except (OSError, ValueError, RuntimeError, OverflowError):
        return False
    finally:
        if file_fd >= 0:
            os.close(file_fd)
        if dir_fd >= 0:
            os.close(dir_fd)


def evaluate(doc: object, log_root: Path) -> dict:
    def blocked(code: str) -> dict:
        return {"status": "BLOCKED_INVALID_OR_INCOMPLETE", "reason": code,
                "qualification": False, "production_go": False}

    if not isinstance(doc, dict) or set(doc) != {"schema", "mode", "uid", "suites", "evidence_kind"}:
        return blocked("DOCUMENT_SCHEMA")
    if doc.get("schema") != SCHEMA or doc.get("mode") not in ("root", "unprivileged"):
        return blocked("MODE_OR_VERSION")
    mode = doc["mode"]
    if type(doc.get("uid")) is not int or doc["uid"] != (ROOT_UID if mode == "root" else UNPRIV_UID):
        return blocked("UID_MODE_MISMATCH")
    if doc["evidence_kind"] not in ("SYNTHETIC_POLICY_TEST", "OBSERVED_NATIVE"):
        return blocked("EVIDENCE_KIND")
    suites = doc.get("suites")
    if not isinstance(suites, list) or len(suites) != len(EXPECTED):
        return blocked("FOUR_SUITES_REQUIRED")
    names = [x.get("name") if isinstance(x, dict) else None for x in suites]
    if any(not isinstance(name, str) or name not in EXPECTED for name in names):
        return blocked("SUITE_NAME_TYPE_OR_UNKNOWN")
    if len(set(names)) != len(EXPECTED) or set(names) != set(EXPECTED):
        return blocked("SUITE_MEMBERSHIP")

    total_pass = total_skip = total_xfail = total_fail = total_error = 0
    for item in suites:
        if set(item) != ({"name", "expected", "exit_status", "log_path", "log_sha256"} | set(COUNT_FIELDS)):
            return blocked("SUITE_EXACT_SCHEMA")
        if type(item["expected"]) is not int or item["expected"] != EXPECTED[item["name"]]:
            return blocked("SUITE_EXPECTED_COUNT")
        for field in COUNT_FIELDS:
            if type(item[field]) is not int or item[field] < 0:
                return blocked("INVALID_COUNT_" + field)
        if sum(item[field] for field in COUNT_FIELDS) != item["expected"]:
            return blocked("SUM_MISMATCH")
        if type(item["exit_status"]) is not int or not 0 <= item["exit_status"] <= 255:
            return blocked("EXIT_STATUS")
        if not _safe_log(log_root, item["log_path"], item["log_sha256"]):
            return blocked("LOG_HASH_OR_PATH")
        total_pass += item["passed"]
        total_fail += item["failed"]
        total_error += item["errors"]
        total_skip += item["skipped"]
        total_xfail += item["xfailed"]

    totals = {"passed":total_pass, "failed":total_fail, "errors":total_error,
              "skipped":total_skip, "xfailed":total_xfail, "total":sum(EXPECTED.values())}
    if any(x["exit_status"] != 0 for x in suites):
        status = "BLOCKED_EXIT_STATUS"
    elif total_fail or total_error:
        status = "BLOCKED_FAIL_OR_ERROR"
    elif total_skip or total_xfail:
        status = "BLOCKED_SKIPPED_OR_XFAIL"
    else:
        status = "COMPLETE_LOCAL_BATCHED_UNQUALIFIED_PASS"
    if doc["evidence_kind"] == "SYNTHETIC_POLICY_TEST":
        status = "SYNTHETIC_" + status

    return {"status": status, "reason": None, "counts": totals,
            "evidence_kind": doc["evidence_kind"],
            "qualification": False, "production_go": False}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("receipt", type=Path)
    parser.add_argument("--log-root", type=Path, required=True)
    args = parser.parse_args()
    try:
        doc = json.loads(args.receipt.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        print(json.dumps({"status":"BLOCKED_INVALID_OR_INCOMPLETE","reason":"RECEIPT_READ",
                          "qualification":False,"production_go":False}))
        return 2
    result = evaluate(doc, args.log_root)
    print(json.dumps(result, sort_keys=True))
    return 0 if result["status"] == "COMPLETE_LOCAL_BATCHED_UNQUALIFIED_PASS" else 2

if __name__ == "__main__":
    raise SystemExit(main())
