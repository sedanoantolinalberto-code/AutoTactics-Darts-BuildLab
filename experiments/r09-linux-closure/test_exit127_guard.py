"""Single-thread Linux tests for a *reference* R09-5 error protocol (not T21)."""
import errno
import os
import platform
import signal
import sys
import unittest

from exit127_guard import _classify, _deadline_outcome, run_guarded

LINUX = sys.platform.startswith("linux")


@unittest.skipUnless(LINUX, "Linux-specific prctl gate")
class Exit127Tests(unittest.TestCase):

    def test_legitimate_exit_127_is_test_exit(self):
        result = run_guarded(sys.executable, [sys.executable, "-c", "import sys;sys.exit(127)"])
        self.assertEqual((result.kind, result.exit_code), ("TEST_EXITED", 127))
        self.assertIsNone(result.setup_errno)

    def test_legitimate_exit_126_is_not_setup_failure(self):
        result = run_guarded(sys.executable, [sys.executable, "-c", "import sys;sys.exit(126)"])
        self.assertEqual((result.kind, result.exit_code), ("TEST_EXITED", 126))

    def test_legitimate_exit_0(self):
        result = run_guarded(sys.executable, [sys.executable, "-c", "import sys;sys.exit(0)"])
        self.assertEqual((result.kind, result.exit_code), ("TEST_EXITED", 0))

    def test_simulated_prctl_eprem_keeps_setup_identity(self):
        result = run_guarded(sys.executable, [sys.executable, "-c", "import sys;sys.exit(127)"],
                             inject_setup_errno=errno.EPERM)
        self.assertEqual(result.kind, "PDEATHSIG_SETUP_FAILED")
        self.assertEqual(result.setup_errno, errno.EPERM)
        self.assertIsNone(result.exit_code)

    @unittest.skipUnless(platform.machine().lower() in ("x86_64", "amd64"),
                         "Classic seccomp probe targets x86_64")
    def test_real_kernel_seccomp_denies_prctl(self):
        # This is a child-only kernel BPF filter, not a mock. If the host
        # refuses filter installation the lab must report BLOCKED, not PASS.
        result = run_guarded(sys.executable, [sys.executable, "-c", "import sys;sys.exit(127)"],
                             deny_prctl_with_real_seccomp=True)
        self.assertEqual(result.kind, "PDEATHSIG_SETUP_FAILED", result)
        self.assertEqual(result.setup_errno, errno.EPERM)
        self.assertIsNone(result.exit_code)

    def test_simulated_prctl_enosys_keeps_setup_identity(self):
        result = run_guarded(sys.executable, [sys.executable, "-c", "import sys;sys.exit(127)"],
                             inject_setup_errno=errno.ENOSYS)
        self.assertEqual(result.kind, "PDEATHSIG_SETUP_FAILED")
        self.assertEqual(result.setup_errno, errno.ENOSYS)
        self.assertIsNone(result.exit_code)

    def test_parent_identity_race_injection_is_not_success(self):
        result = run_guarded(sys.executable, [sys.executable, "-c", "import sys;sys.exit(0)"],
                             inject_parent_mismatch=True)
        self.assertEqual(result.kind, "PARENT_IDENTITY_CHANGED")
        self.assertIsNone(result.exit_code)

    def test_exec_nonexistent_has_distinct_kind(self):
        result = run_guarded("/definitely/not-an-engineyt-executable",
                             ["/definitely/not-an-engineyt-executable"])
        self.assertEqual(result.kind, "EXEC_SETUP_FAILED")
        self.assertEqual(result.setup_errno, errno.ENOENT)
        self.assertIsNone(result.exit_code)

    def test_signal_is_not_regular_exit_code(self):
        result = run_guarded(sys.executable,
                             [sys.executable, "-c", "import os,signal;os.kill(os.getpid(), signal.SIGTERM)"])
        self.assertEqual(result.kind, "TEST_SIGNALED")
        self.assertEqual(result.signal, signal.SIGTERM)

    def test_owned_child_timeout_is_fail_closed(self):
        result = run_guarded(sys.executable, [sys.executable, "-c", "import time;time.sleep(3)"],
                             timeout_seconds=0.12)
        self.assertEqual(result.kind, "TEST_TIMEOUT")
        self.assertIsNone(result.exit_code)

    def test_deadline_with_reaped_child_and_missing_eof_is_protocol_not_timeout(self):
        result = _deadline_outcome(0, False, 120)
        self.assertEqual(result.kind, "SETUP_PIPE_EOF_MISSING")
        self.assertIsNone(result.exit_code)

    def test_deadline_with_oversized_report_is_not_timeout(self):
        result = _deadline_outcome(None, True, 80)
        self.assertEqual(result.kind, "MALFORMED_SETUP_REPORT")

    def test_deadline_with_unreaped_child_is_timeout(self):
        result = _deadline_outcome(None, False, 120)
        self.assertEqual(result.kind, "TEST_TIMEOUT")

    def test_unknown_payload_is_not_accepted(self):
        result = _classify(127 << 8, b"FALSE_SUCCESS:127\n", 1)
        self.assertEqual(result.kind, "MALFORMED_SETUP_REPORT")
        self.assertIsNone(result.exit_code)

    def test_truncated_payload_is_not_accepted(self):
        result = _classify(127 << 8, b"PDEATHSIG:\n", 1)
        self.assertEqual(result.kind, "MALFORMED_SETUP_REPORT")

    def test_oversized_payload_is_not_accepted(self):
        result = _classify(127 << 8, b"PDEATHSIG:1" + b"x" * 300, 1)
        self.assertEqual(result.kind, "MALFORMED_SETUP_REPORT")

    def test_no_shell_or_implicit_executable_name(self):
        with self.assertRaises(ValueError):
            run_guarded("python3", ["python3"])
        with self.assertRaises(ValueError):
            run_guarded(sys.executable, ["different"])

    def test_timeout_input_is_bounded(self):
        with self.assertRaises(ValueError):
            run_guarded(sys.executable, [sys.executable], timeout_seconds=60)


if __name__ == "__main__":
    unittest.main(verbosity=2)
