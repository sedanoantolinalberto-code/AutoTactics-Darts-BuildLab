"""Native Linux counterexamples to PDEATHSIG-based descendant containment.

This is intentionally separate from the reference launcher and T21-R09.
Runs only with directly-owned, short-lived self-forked children. Never
performs orphan-escape or non-owned-process termination tests.
"""
import ctypes
import errno
import os
import select
import signal
import sys
import unittest

PR_SET_PDEATHSIG = 1
PR_GET_PDEATHSIG = 2


def prctl(option: int, arg: int) -> int:
    libc = ctypes.CDLL(None, use_errno=True)
    call = libc.prctl
    call.argtypes = [ctypes.c_int, ctypes.c_ulong, ctypes.c_ulong,
                     ctypes.c_ulong, ctypes.c_ulong]
    call.restype = ctypes.c_int
    if call(option, arg, 0, 0, 0) == -1:
        raise OSError(ctypes.get_errno(), "prctl")
    return 0


def pdeathsig() -> int:
    value = ctypes.c_int(0)
    prctl(PR_GET_PDEATHSIG, ctypes.addressof(value))
    return value.value


def observe(disable_privileges: bool) -> str:
    """Execute in controlled short-lived child; report before:after."""
    readfd, writefd = os.pipe2(os.O_CLOEXEC)
    pid = os.fork()
    if pid == 0:
        os.close(readfd)
        try:
            signal.alarm(3)
            prctl(PR_SET_PDEATHSIG, signal.SIGKILL)
            before = pdeathsig()
            if disable_privileges:
                os.setuid(65534)
                after = pdeathsig()
                os.write(writefd, f"{before}:{after}".encode("ascii"))
            else:
                grandchild = os.fork()
                if grandchild == 0:
                    try:
                        after = pdeathsig()
                        os.write(writefd, f"{before}:{after}".encode("ascii"))
                    finally:
                        os._exit(0)
                os.waitpid(grandchild, 0)
            os._exit(0)
        except BaseException:
            os._exit(120)
    os.close(writefd)
    try:
        ready, _, _ = select.select([readfd], [], [], 4)
        if not ready:
            raise TimeoutError("no native PDEATHSIG observation")
        message = os.read(readfd, 100).decode("ascii")
        waitpid, status = os.waitpid(pid, 0)
        if waitpid != pid or not os.WIFEXITED(status) or os.WEXITSTATUS(status) != 0:
            raise AssertionError("owned laboratory child did not exit normally")
        return message
    finally:
        try:
            os.kill(pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        try:
            os.waitpid(pid, os.WNOHANG)
        except ChildProcessError:
            pass
        os.close(readfd)


@unittest.skipUnless(sys.platform.startswith("linux"), "Linux-only native proof")
class KernelPdeathsigTests(unittest.TestCase):
    def test_grandchild_does_not_inherit_pdeathsig(self):
        self.assertEqual(observe(disable_privileges=False), f"{signal.SIGKILL}:0")

    @unittest.skipUnless(os.geteuid() == 0, "Requires root for UID drop")
    def test_uid_drop_clears_pdeathsig(self):
        self.assertEqual(observe(disable_privileges=True), f"{signal.SIGKILL}:0")


if __name__ == "__main__":
    unittest.main(verbosity=2)
