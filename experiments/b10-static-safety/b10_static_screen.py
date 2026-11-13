"""B41 STATIC-ONLY screen for high-risk B10 custody source patterns.

This module MUST NOT import, fork, signal, unshare, execute, or probe the
candidate code. Positive screening does NOT attest isolation, confinement,
process safety, native behavior, or production readiness.

Only use for pre-review of disposable laboratory code. Requires independent,
external containment before *any* native/destructive test campaign.
"""
from __future__ import annotations

import argparse
import ast
import json
import os
import stat
from pathlib import Path

CLONE_NEWPID = 0x20000000
MAX_SOURCE_BYTES = 512_000
MAX_SOURCES = 1_000


def _name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return None


def _int_literal(node: ast.AST, depth: int = 0) -> int | None:
    """Conservative integer expression evaluation, never Python eval()."""
    if depth > 8:
        return None
    if isinstance(node, ast.Constant) and type(node.value) is int:
        return node.value
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd)):
        inner = _int_literal(node.operand, depth + 1)
        return None if inner is None else (-inner if isinstance(node.op, ast.USub) else inner)
    if isinstance(node, ast.BinOp):
        a = _int_literal(node.left, depth + 1)
        b = _int_literal(node.right, depth + 1)
        if a is None or b is None or abs(a) > 2**65 or abs(b) > 2**65:
            return None
        if isinstance(node.op, ast.LShift) and 0 <= b <= 64:
            return a << b
        if isinstance(node.op, ast.BitOr):
            return a | b
        if isinstance(node.op, ast.BitAnd):
            return a & b
        if isinstance(node.op, ast.Add):
            return a + b
        if isinstance(node.op, ast.Sub):
            return a - b
    if isinstance(node, ast.Call) and len(node.args) == 1 and not node.keywords:
        if _name(node.func) in ("c_int", "c_uint", "c_ulong", "int"):
            return _int_literal(node.args[0], depth + 1)
    return None


def scan_source(source: str, filename: str = "<static fixture>") -> list[dict]:
    """Parse-only. No exec, import, eval, os.kill, syscall or fork."""
    issues = []
    try:
        tree = ast.parse(source, filename=filename)
    except (SyntaxError, ValueError, UnicodeError) as exc:
        return [{"file": filename, "line": 0, "code": "SOURCE_PARSE_INVALID",
                 "detail": type(exc).__name__}]

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = _name(node.func)
        if not node.args:
            continue
        value = _int_literal(node.args[0])
        def flag(code: str, detail: str):
            issues.append({"file": filename, "line": node.lineno,
                           "code": code, "detail": detail})

        if name == "kill" and value in (-1, 0):
            flag("BROAD_SIGNAL_TARGET", "kill(-1/0) may signal processes outside custody")
        elif name == "killpg" and value in (-1, 0):
            flag("BROAD_PROCESS_GROUP", "killpg(-1/0) is not an owned PID-boundary proof")

        if name == "unshare":
            if value is None:
                flag("DYNAMIC_UNSHARE_REQUIRES_REVIEW",
                     "Flag provenance/range must be checked at runtime; static screen cannot prove it")
            elif value == 0:
                flag("UNSHARE_ZERO_NO_NAMESPACE", "unshare(0) is not a PID namespace")
            elif value < 0 or value > 0xffffffff:
                flag("UNSHARE_FLAG_OUT_OF_RANGE", "C integer narrowing may alter namespace flags")
            elif value != CLONE_NEWPID:
                flag("UNSHARE_FLAGS_NOT_EXACT_NEWPID",
                     "Custody path expects exactly CLONE_NEWPID")

        if name == "c_int" and value is not None and not -(2**31) <= value <= 2**31-1:
            flag("C_INT_NARROWING", "ctypes.c_int will narrow an integer outside int32")
        if name == "c_uint" and value is not None and not 0 <= value <= 2**32-1:
            flag("C_UINT_NARROWING", "ctypes.c_uint will narrow an integer outside uint32")

    return sorted(issues, key=lambda x: (x["line"], x["code"]))


def _read_regular_no_follow(path: Path) -> str:
    fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        before = os.fstat(fd)
        if not stat.S_ISREG(before.st_mode) or before.st_size > MAX_SOURCE_BYTES:
            raise ValueError("NOT_REGULAR_OR_TOO_LARGE")
        chunks = bytearray()
        while len(chunks) <= MAX_SOURCE_BYTES:
            b = os.read(fd, min(65536, MAX_SOURCE_BYTES + 1 - len(chunks)))
            if not b:
                break
            chunks.extend(b)
        after = os.fstat(fd)
        if len(chunks) > MAX_SOURCE_BYTES:
            raise ValueError("TOO_LARGE")
        if (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns,
                before.st_ctime_ns) != (after.st_dev, after.st_ino, after.st_size,
                                       after.st_mtime_ns, after.st_ctime_ns):
            raise ValueError("SOURCE_CHANGED_WHILE_READING")
        return bytes(chunks).decode("utf-8")
    finally:
        os.close(fd)


def scan_tree(root: Path) -> dict:
    """Fail closed for a symlink, unreadable file, or missing candidate code."""
    root = Path(root)
    issues = []
    files = []
    if root.is_symlink():
        issues.append({"file": str(root), "line": 0, "code": "SYMLINK_ROOT", "detail": "not followed"})
    elif root.is_file():
        files = [root]
    elif root.is_dir():
        for directory, dirs, names in os.walk(root, followlinks=False):
            for name in dirs[:]:
                candidate = Path(directory) / name
                if candidate.is_symlink():
                    issues.append({"file": str(candidate), "line": 0,
                                   "code": "SYMLINK_DIRECTORY", "detail": "not followed"})
                    dirs.remove(name)
            for name in names:
                candidate = Path(directory) / name
                if candidate.is_symlink():
                    issues.append({"file": str(candidate), "line": 0,
                                   "code": "SYMLINK_FILE", "detail": "not followed"})
                elif name.endswith(".py"):
                    files.append(candidate)
    else:
        issues.append({"file": str(root), "line": 0, "code": "NO_SUCH_SOURCE",
                       "detail": "input must be an existing regular .py file or directory"})
    if not files:
        issues.append({"file": str(root), "line": 0, "code": "NO_PYTHON_FILES",
                       "detail": "nothing reviewed"})
    if len(files) > MAX_SOURCES:
        issues.append({"file": str(root), "line": 0, "code": "TOO_MANY_SOURCES",
                       "detail": "bounded static scan required"})
        files = files[:MAX_SOURCES]
    for path in sorted(files):
        try:
            source = _read_regular_no_follow(path)
        except (OSError, ValueError, UnicodeError) as exc:
            issues.append({"file": str(path), "line": 0, "code": "SOURCE_UNREADABLE",
                           "detail": type(exc).__name__})
            continue
        issues.extend(scan_source(source, str(path)))
    return {"schema": "engineyt-b10-static-screen/1",
            "classification": "STATIC_SCREEN_ONLY_NOT_ISOLATION_ATTESTATION",
            "files_examined": len(files),
            "decision": "BLOCKED_STATIC_FINDINGS" if issues else "STATIC_SCREEN_NO_FINDINGS_NOT_QUALIFIED",
            "production_go": False, "native_test_authorized": False,
            "findings": issues}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    args = parser.parse_args()
    result = scan_tree(args.source)
    print(json.dumps(result, sort_keys=True))
    return 2 if result["findings"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
