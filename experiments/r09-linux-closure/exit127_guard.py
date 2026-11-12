"""REVIEW-ONLY R09-5 laboratory. NOT the EngineYT T21-R09 supervisor.

Isolated single-thread Linux experiment: distinguish an exec'ed command's exit 127
from a PDEATHSIG setup failure using a CLOEXEC error pipe. No shell/network.
All children are forked by this process and directly reaped; no grandchild tests.
"""
import ctypes
import errno
import os
import signal
import sys
import time
from dataclasses import asdict, dataclass

PR_SET_PDEATHSIG = 1
MAX_ERROR_BYTES = 256


@dataclass(frozen=True)
class Outcome:
    kind: str
    exit_code: int | None
    signal: int | None
    setup_errno: int | None
    elapsed_ms: int


def _prctl_pdeathsig_or_errno() -> int | None:
    """Return actual errno on failure, or None on kernel success."""
    libc = ctypes.CDLL(None, use_errno=True)
    prctl = libc.prctl
    prctl.argtypes = [ctypes.c_int, ctypes.c_ulong, ctypes.c_ulong,
                      ctypes.c_ulong, ctypes.c_ulong]
    prctl.restype = ctypes.c_int
    if prctl(PR_SET_PDEATHSIG, signal.SIGKILL, 0, 0, 0) == -1:
        return ctypes.get_errno() or errno.EINVAL
    return None


def _report_and_exit(write_fd: int, category: bytes, number: int) -> None:
    payload = category + b":" + str(number).encode("ascii") + b"\n"
    try:
        os.write(write_fd, payload)
    finally:
        os._exit(126)


def _classify(status: int, error_bytes: bytes, elapsed_ms: int) -> Outcome:
    if error_bytes:
        lines = error_bytes.splitlines()
        if len(lines) != 1 or len(error_bytes) > MAX_ERROR_BYTES:
            return Outcome("MALFORMED_SETUP_REPORT", None, None, None, elapsed_ms)
        parts = lines[0].split(b":")
        if len(parts) != 2 or not parts[1].isdigit():
            return Outcome("MALFORMED_SETUP_REPORT", None, None, None, elapsed_ms)
        if parts[0] == b"PDEATHSIG":
            return Outcome("PDEATHSIG_SETUP_FAILED", None, None, int(parts[1]), elapsed_ms)
        if parts[0] == b"PARENT_CHANGED":
            return Outcome("PARENT_IDENTITY_CHANGED", None, None, int(parts[1]), elapsed_ms)
        if parts[0] == b"EXECV":
            return Outcome("EXEC_SETUP_FAILED", None, None, int(parts[1]), elapsed_ms)
        return Outcome("MALFORMED_SETUP_REPORT", None, None, None, elapsed_ms)
    if os.WIFSIGNALED(status):
        return Outcome("TEST_SIGNALED", None, os.WTERMSIG(status), None, elapsed_ms)
    if os.WIFEXITED(status):
        code = os.WEXITSTATUS(status)
        return Outcome("TEST_EXITED", code, None, None, elapsed_ms)
    return Outcome("UNEXPECTED_WAIT_STATUS", None, None, None, elapsed_ms)


def run_guarded(
    executable: str,
    argv: list[str],
    *,
    timeout_seconds: float = 3.0,
    inject_setup_errno: int | None = None,
    inject_parent_mismatch: bool = False,
) -> Outcome:
    if not sys.platform.startswith("linux"):
        raise RuntimeError("BLOCKED: linux-only")
    if not os.path.isabs(executable):
        raise ValueError("Executable path must be absolute")
    if timeout_seconds <= 0 or timeout_seconds > 10:
        raise ValueError("Only short-lived disposable tests are allowed")
    if not isinstance(argv, list) or not argv or argv[0] != executable:
        raise ValueError("argv[0] must match the explicit executable")
    if inject_setup_errno is not None and not (1 <= inject_setup_errno <= 4095):
        raise ValueError("Injected errno must be a plausible positive errno")

    start = time.monotonic()
    expected_ppid = os.getpid()
    read_fd, write_fd = os.pipe2(os.O_CLOEXEC | os.O_NONBLOCK)
    pid = None
    waited = False
    try:
        pid = os.fork()
        if pid == 0:
            # Single-thread-only fork laboratory. Don't use this pattern in a
            # multithreaded production supervisor without a separate launcher.
            os.close(read_fd)
            os.set_blocking(write_fd, True)
            if inject_setup_errno is not None:
                _report_and_exit(write_fd, b"PDEATHSIG", inject_setup_errno)
            setup_error = _prctl_pdeathsig_or_errno()
            if setup_error is not None:
                _report_and_exit(write_fd, b"PDEATHSIG", setup_error)
            if inject_parent_mismatch or os.getppid() != expected_ppid:
                _report_and_exit(write_fd, b"PARENT_CHANGED", errno.ESRCH)
            try:
                os.execv(executable, argv)
            except OSError as exc:
                _report_and_exit(write_fd, b"EXECV", exc.errno or errno.EIO)
            os._exit(125)  # Unreachable unless execv returns unexpectedly.

        os.close(write_fd)
        write_fd = -1
        pieces = bytearray()
        eof = False
        status = None
        while time.monotonic() - start < timeout_seconds:
            try:
                b = os.read(read_fd, 256)
                if not b:
                    eof = True
                else:
                    pieces.extend(b)
                    if len(pieces) > MAX_ERROR_BYTES:
                        # Report size abuse is fail-closed.
                        break
            except BlockingIOError:
                pass
            if status is None:
                done, s = os.waitpid(pid, os.WNOHANG)
                if done == pid:
                    status = s
                    waited = True
            if status is not None and eof:
                elapsed = int((time.monotonic() - start) * 1000)
                return _classify(status, bytes(pieces), elapsed)
            time.sleep(0.005)

        # Terminate *only* our own directly forked child and reap it.
        if status is None:
            try:
                os.kill(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            os.waitpid(pid, 0)
            waited = True
        return Outcome("TIMEOUT_OR_PROTOCOL_FAILURE", None, None, None,
                       int((time.monotonic() - start) * 1000))
    finally:
        if pid is not None and pid > 0 and not waited:
            # Never leave an owned child behind if the reader itself fails.
            try:
                os.kill(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            try:
                os.waitpid(pid, 0)
            except ChildProcessError:
                pass
        if read_fd >= 0:
            os.close(read_fd)
        if write_fd >= 0:
            os.close(write_fd)


if __name__ == "__main__":
    import json
    # Explicit opt-in small demonstration; never uses a shell or external assets.
    result = run_guarded(sys.executable, [sys.executable, "-c", "import sys;sys.exit(127)"])
    print(json.dumps(asdict(result), sort_keys=True))
    sys.exit(0 if result.kind == "TEST_EXITED" and result.exit_code == 127 else 1)
