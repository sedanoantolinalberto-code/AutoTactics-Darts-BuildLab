"""REVIEW-ONLY R09-6 strict accounting policy. No test execution.

Consumes four receipts and exact per-test JSONL logs, with SHA-256 verified
from the same pinned file descriptor that supplies the parsed evidence.
A checksum alone never proves that declared PASS counts are correct.
It does not authenticate the test producer or qualify actual test execution.
Never turns SKIP, XFAIL or ERROR into PASS. Synthetic policy fixtures are
strictly distinct from authentic T21-R09 evidence.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import re
import stat
from pathlib import Path

SCHEMA = "engineyt-r09-suite-receipts/0.2"
RESULT_SCHEMA = "engineyt-r09-case-result/0.1"
RESULT_STATUS = {"PASS":"passed", "FAIL":"failed", "ERROR":"errors", "SKIP":"skipped", "XFAIL":"xfailed"}
CASE_PATTERN = re.compile(r"[A-Za-z0-9._:-]{1,120}\Z")
EXPECTED = {"official": 634, "additional": 49, "r07": 13, "r09": 14}
COUNT_FIELDS = ("passed", "failed", "errors", "skipped", "xfailed")
ROOT_UID = 0
UNPRIV_UID = 65534

def _read_verified_log(root: Path, name: str, expected_hash: str) -> bytes | None:
    """Return bytes from exactly the descriptor that was hashed.

    Fail closed for FIFO, symlink, traversal, malformed paths, oversized logs,
    or changes observed during reading. This is not a provenance or durability
    guarantee: an attacker who can replace *both* receipts and logs remains
    outside this reference laboratory's trust boundary.
    """
    if not isinstance(name, str) or not name or Path(name).is_absolute():
        return None
    if not isinstance(expected_hash, str) or len(expected_hash) != 64:
        return None
    if any(c not in "0123456789abcdef" for c in expected_hash):
        return None
    if "\\" in name or "\x00" in name:
        return None
    parts = name.split("/")
    if any(part in ("", ".", "..") for part in parts):
        return None

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
            return None

        digest = hashlib.sha256()
        data = bytearray()
        while True:
            block = os.read(file_fd, min(65536, 2_000_001 - len(data)))
            if not block:
                break
            data.extend(block)
            if len(data) > 2_000_000:
                return None
            digest.update(block)
        final = os.fstat(file_fd)
        if (final.st_ino != initial.st_ino or
            final.st_dev != initial.st_dev or
            final.st_size != initial.st_size or
            final.st_mtime_ns != initial.st_mtime_ns or
            final.st_ctime_ns != initial.st_ctime_ns):
            return None
        if digest.hexdigest() != expected_hash:
            return None
        return bytes(data)
    except (OSError, ValueError, RuntimeError, OverflowError):
        return None
    finally:
        if file_fd >= 0:
            os.close(file_fd)
        if dir_fd >= 0:
            os.close(dir_fd)


def _unique_json_pairs(pairs):
    """Reject duplicate JSON keys instead of trusting the last value."""
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("DUPLICATE_JSON_KEY")
        result[key] = value
    return result


def _derive_counts_from_jsonl(raw: bytes, expected: int) -> dict | None:
    """Require exactly one unambiguous record for every unique case id."""
    if not raw or not raw.endswith(b"\n") or b"\r" in raw or b"\x00" in raw:
        return None
    lines = raw.split(b"\n")[:-1]
    if len(lines) != expected:
        return None
    counts = {field: 0 for field in COUNT_FIELDS}
    seen = set()
    for line in lines:
        if not line or len(line) > 4096:
            return None
        try:
            item = json.loads(line.decode("utf-8"), object_pairs_hook=_unique_json_pairs)
        except (UnicodeError, ValueError, json.JSONDecodeError):
            return None
        if not isinstance(item, dict) or set(item) != {"schema", "case_id", "status"}:
            return None
        case_id = item["case_id"]
        status = item["status"]
        if (item["schema"] != RESULT_SCHEMA or
            not isinstance(case_id, str) or CASE_PATTERN.fullmatch(case_id) is None or
            case_id in seen or not isinstance(status, str) or
            status not in RESULT_STATUS):
            return None
        seen.add(case_id)
        counts[RESULT_STATUS[status]] += 1
    return counts


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
        raw = _read_verified_log(log_root, item["log_path"], item["log_sha256"])
        if raw is None:
            return blocked("LOG_HASH_OR_PATH")
        derived = _derive_counts_from_jsonl(raw, item["expected"])
        if derived is None:
            return blocked("LOG_CONTENT_INVALID_OR_INCOMPLETE")
        if any(item[field] != derived[field] for field in COUNT_FIELDS):
            return blocked("DECLARED_COUNTS_DISAGREE_WITH_LOG")
        total_pass += derived["passed"]
        total_fail += derived["failed"]
        total_error += derived["errors"]
        total_skip += derived["skipped"]
        total_xfail += derived["xfailed"]

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
