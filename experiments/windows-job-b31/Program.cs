// B31 ISOLATED WINDOWS API PROBE. NOT the EngineYT B23-B25 native Gate V8.
// Runs only self-owned, short-lived PowerShell child processes on a disposable CI runner.
// No integration, rendering, upload, or publication authority.
using System;
using System.ComponentModel;
using System.Runtime.InteropServices;
using System.Text;
using System.IO;
using System.Diagnostics;
using System.Threading;
using System.Threading.Tasks;

internal static class Program
{
    private const uint KillOnJobClose = 0x2000;
    private const uint BreakawayOk = 0x800;
    private const uint SilentBreakawayOk = 0x1000;
    private const uint ExtendedStartupInfoPresent = 0x00080000;
    private const uint CreateSuspended = 0x00000004;
    private const uint CreateNoWindow = 0x08000000;
    private const uint CreateBreakawayFromJob = 0x01000000;
    private const uint WaitObject0 = 0;
    private const uint WaitTimeout = 258;
    private const uint DuplicateSameAccess = 2;
    private const uint Synchronize = 0x00100000;
    private const uint ProcessTerminate = 0x0001;
    private const uint ProcessQueryLimitedInformation = 0x1000;
    private const int JobObjectExtendedLimitInformation = 9;
    private const uint JobObjectQuery = 0x0004;
    private const int ErrorAlreadyExists = 183;
    private static readonly IntPtr ProcThreadAttributeJobList = new(0x0002000D);

    [StructLayout(LayoutKind.Sequential)]
    private struct JOBOBJECT_BASIC_LIMIT_INFORMATION
    {
        public long PerProcessUserTimeLimit;
        public long PerJobUserTimeLimit;
        public uint LimitFlags;
        public UIntPtr MinimumWorkingSetSize;
        public UIntPtr MaximumWorkingSetSize;
        public uint ActiveProcessLimit;
        public UIntPtr Affinity;
        public uint PriorityClass;
        public uint SchedulingClass;
    }

    [StructLayout(LayoutKind.Sequential)]
    private struct IO_COUNTERS
    {
        public ulong ReadOperationCount;
        public ulong WriteOperationCount;
        public ulong OtherOperationCount;
        public ulong ReadTransferCount;
        public ulong WriteTransferCount;
        public ulong OtherTransferCount;
    }

    [StructLayout(LayoutKind.Sequential)]
    private struct JOBOBJECT_EXTENDED_LIMIT_INFORMATION
    {
        public JOBOBJECT_BASIC_LIMIT_INFORMATION BasicLimitInformation;
        public IO_COUNTERS IoInfo;
        public UIntPtr ProcessMemoryLimit;
        public UIntPtr JobMemoryLimit;
        public UIntPtr PeakProcessMemoryUsed;
        public UIntPtr PeakJobMemoryUsed;
    }

    [StructLayout(LayoutKind.Sequential)]
    private struct STARTUPINFO
    {
        public uint cb;
        public IntPtr lpReserved;
        public IntPtr lpDesktop;
        public IntPtr lpTitle;
        public uint dwX, dwY, dwXSize, dwYSize, dwXCountChars, dwYCountChars, dwFillAttribute, dwFlags;
        public ushort wShowWindow, cbReserved2;
        public IntPtr lpReserved2, hStdInput, hStdOutput, hStdError;
    }

    [StructLayout(LayoutKind.Sequential)]
    private struct STARTUPINFOEX
    {
        public STARTUPINFO StartupInfo;
        public IntPtr lpAttributeList;
    }

    [StructLayout(LayoutKind.Sequential)]
    private struct PROCESS_INFORMATION
    {
        public IntPtr hProcess;
        public IntPtr hThread;
        public uint dwProcessId;
        public uint dwThreadId;
    }

    [DllImport("kernel32.dll", EntryPoint = "CreateJobObjectW", CharSet = CharSet.Unicode, SetLastError = true)]
    private static extern IntPtr CreateJobObject(IntPtr securityAttributes, string? name);
    [DllImport("kernel32.dll", EntryPoint = "OpenJobObjectW", CharSet = CharSet.Unicode, SetLastError = true)]
    private static extern IntPtr OpenJobObject(uint desiredAccess, [MarshalAs(UnmanagedType.Bool)] bool inherit, string name);
    [DllImport("kernel32.dll", SetLastError = true)]
    [return: MarshalAs(UnmanagedType.Bool)]
    private static extern bool SetInformationJobObject(IntPtr job, int infoClass,
        ref JOBOBJECT_EXTENDED_LIMIT_INFORMATION info, uint infoSize);
    [DllImport("kernel32.dll", SetLastError = true)]
    [return: MarshalAs(UnmanagedType.Bool)]
    private static extern bool QueryInformationJobObject(IntPtr job, int infoClass,
        out JOBOBJECT_EXTENDED_LIMIT_INFORMATION info, uint infoSize, IntPtr returnLength);
    [DllImport("kernel32.dll", SetLastError = true)]
    [return: MarshalAs(UnmanagedType.Bool)]
    private static extern bool InitializeProcThreadAttributeList(IntPtr list, int count, int flags, ref IntPtr size);
    [DllImport("kernel32.dll", SetLastError = true)]
    [return: MarshalAs(UnmanagedType.Bool)]
    private static extern bool UpdateProcThreadAttribute(IntPtr list, uint flags, IntPtr attribute,
        IntPtr value, IntPtr size, IntPtr previousValue, IntPtr returnSize);
    [DllImport("kernel32.dll")]
    private static extern void DeleteProcThreadAttributeList(IntPtr list);
    [DllImport("kernel32.dll", EntryPoint = "CreateProcessW", CharSet = CharSet.Unicode, SetLastError = true)]
    [return: MarshalAs(UnmanagedType.Bool)]
    private static extern bool CreateProcess(string applicationName, StringBuilder commandLine,
        IntPtr processAttributes, IntPtr threadAttributes, [MarshalAs(UnmanagedType.Bool)] bool inheritHandles,
        uint flags, IntPtr environment, string? currentDirectory, ref STARTUPINFOEX startup,
        out PROCESS_INFORMATION info);
    [DllImport("kernel32.dll", SetLastError = true)]
    [return: MarshalAs(UnmanagedType.Bool)]
    private static extern bool IsProcessInJob(IntPtr process, IntPtr job, [MarshalAs(UnmanagedType.Bool)] out bool result);
    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern uint ResumeThread(IntPtr thread);
    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern uint WaitForSingleObject(IntPtr handle, uint timeoutMs);
    [DllImport("kernel32.dll", SetLastError = true)]
    [return: MarshalAs(UnmanagedType.Bool)]
    private static extern bool TerminateJobObject(IntPtr job, uint exitCode);
    [DllImport("kernel32.dll", SetLastError = true)]
    [return: MarshalAs(UnmanagedType.Bool)]
    private static extern bool TerminateProcess(IntPtr process, uint exitCode);
    [DllImport("kernel32.dll", SetLastError = true)]
    [return: MarshalAs(UnmanagedType.Bool)]
    private static extern bool DuplicateHandle(IntPtr sourceProcess, IntPtr source, IntPtr targetProcess,
        out IntPtr target, uint desiredAccess, [MarshalAs(UnmanagedType.Bool)] bool inheritHandle, uint options);
    [DllImport("kernel32.dll")]
    private static extern IntPtr GetCurrentProcess();
    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern IntPtr OpenProcess(uint access, [MarshalAs(UnmanagedType.Bool)] bool inherit, uint pid);
    [DllImport("kernel32.dll", SetLastError = true)]
    [return: MarshalAs(UnmanagedType.Bool)]
    private static extern bool GetHandleInformation(IntPtr handle, out uint flags);
    [DllImport("kernel32.dll", SetLastError = true)]
    [return: MarshalAs(UnmanagedType.Bool)]
    private static extern bool SetHandleInformation(IntPtr handle, uint mask, uint flags);
    [DllImport("kernel32.dll", SetLastError = true)]
    [return: MarshalAs(UnmanagedType.Bool)]
    private static extern bool CloseHandle(IntPtr handle);

    private static void Check(bool condition, string message)
    {
        if (!condition) throw new InvalidOperationException(message);
    }

    private static void CheckWin(bool condition, string api)
    {
        if (!condition) throw new Win32Exception(Marshal.GetLastWin32Error(), api);
    }

    private static IntPtr CreateConfiguredJob(string? name = null)
    {
        IntPtr job = CreateJobObject(IntPtr.Zero, name);
        int createError = Marshal.GetLastWin32Error();
        CheckWin(job != IntPtr.Zero, "CreateJobObject");
        try
        {
            // A named Job is required for authenticated test PID resolution.
            // Reopening a preexisting name could alias somebody else's process.
            if (name is not null && createError == ErrorAlreadyExists)
                throw new InvalidOperationException("Unexpected existing Job name");
            var info = new JOBOBJECT_EXTENDED_LIMIT_INFORMATION();
            info.BasicLimitInformation.LimitFlags = KillOnJobClose;
            uint size = (uint)Marshal.SizeOf<JOBOBJECT_EXTENDED_LIMIT_INFORMATION>();
            CheckWin(SetInformationJobObject(job, JobObjectExtendedLimitInformation, ref info, size),
                "SetInformationJobObject");
            return job;
        }
        catch
        {
            CloseHandle(job);
            throw;
        }
    }

    private static string PowerShellPath()
    {
        string path = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.Windows),
            "System32", "WindowsPowerShell", "v1.0", "powershell.exe");
        Check(File.Exists(path), "PowerShell system binary missing");
        return path;
    }

    private static (bool created, PROCESS_INFORMATION process, int error) TryCreateAtomic(IntPtr job, string program, string? arguments = null)
    {
        IntPtr required = IntPtr.Zero, buffer = IntPtr.Zero, listValue = IntPtr.Zero;
        bool initialized = false;
        try
        {
            // First call intentionally fails with ERROR_INSUFFICIENT_BUFFER.
            InitializeProcThreadAttributeList(IntPtr.Zero, 1, 0, ref required);
            Check(required.ToInt64() > 0 && required.ToInt64() < (1 << 20), "Invalid attribute list size");
            buffer = Marshal.AllocHGlobal(required);
            CheckWin(InitializeProcThreadAttributeList(buffer, 1, 0, ref required),
                "InitializeProcThreadAttributeList");
            initialized = true;
            listValue = Marshal.AllocHGlobal(IntPtr.Size);
            Marshal.WriteIntPtr(listValue, job);
            CheckWin(UpdateProcThreadAttribute(buffer, 0, ProcThreadAttributeJobList,
                listValue, new IntPtr(IntPtr.Size), IntPtr.Zero, IntPtr.Zero),
                "UpdateProcThreadAttribute(JOB_LIST)");
            var startup = new STARTUPINFOEX();
            startup.StartupInfo.cb = (uint)Marshal.SizeOf<STARTUPINFOEX>();
            startup.lpAttributeList = buffer;
            // Explicit application path, no handle inheritance, no shell.
            var cmd = new StringBuilder("\"" + program + "\" " +
                (arguments ?? "-NoProfile -NonInteractive -Command \"Start-Sleep -Seconds 60\""));
            bool created = CreateProcess(program, cmd, IntPtr.Zero, IntPtr.Zero, false,
                ExtendedStartupInfoPresent | CreateSuspended | CreateNoWindow,
                IntPtr.Zero, null, ref startup, out PROCESS_INFORMATION pi);
            int error = created ? 0 : Marshal.GetLastWin32Error();
            return (created, pi, error);
        }
        finally
        {
            if (initialized) DeleteProcThreadAttributeList(buffer);
            if (listValue != IntPtr.Zero) Marshal.FreeHGlobal(listValue);
            if (buffer != IntPtr.Zero) Marshal.FreeHGlobal(buffer);
        }
    }

    private static PROCESS_INFORMATION LaunchAtomic(IntPtr job)
    {
        var x = TryCreateAtomic(job, PowerShellPath());
        if (!x.created) throw new Win32Exception(x.error, "CreateProcessW(JOB_LIST)");
        return x.process;
    }

    private static void Resume(PROCESS_INFORMATION p)
    {
        uint v = ResumeThread(p.hThread);
        CheckWin(v != uint.MaxValue, "ResumeThread");
    }

    private static void CloseJob(ref IntPtr handle)
    {
        if (handle != IntPtr.Zero)
        {
            IntPtr previous = handle;
            handle = IntPtr.Zero;
            CheckWin(CloseHandle(previous), "CloseHandle(job)");
        }
    }

    private static void DisposeOwned(ref IntPtr job, ref IntPtr duplicate, ref PROCESS_INFORMATION pi)
    {
        if (job != IntPtr.Zero) { TerminateJobObject(job, 1); CloseHandle(job); job = IntPtr.Zero; }
        if (duplicate != IntPtr.Zero) { TerminateJobObject(duplicate, 1); CloseHandle(duplicate); duplicate = IntPtr.Zero; }
        if (pi.hProcess != IntPtr.Zero)
        {
            if (WaitForSingleObject(pi.hProcess, 0) == WaitTimeout) TerminateProcess(pi.hProcess, 1);
            CloseHandle(pi.hProcess);
            pi.hProcess = IntPtr.Zero;
        }
        if (pi.hThread != IntPtr.Zero) { CloseHandle(pi.hThread); pi.hThread = IntPtr.Zero; }
    }

    private static void TestConfiguredJobAndHandleInheritance()
    {
        IntPtr job = IntPtr.Zero, duplicate = IntPtr.Zero;
        PROCESS_INFORMATION pi = default;
        try
        {
            job = CreateConfiguredJob();
            CheckWin(GetHandleInformation(job, out uint inherited), "GetHandleInformation");
            Check((inherited & 1u) == 0, "Job handle unexpectedly inheritable");
            uint size = (uint)Marshal.SizeOf<JOBOBJECT_EXTENDED_LIMIT_INFORMATION>();
            CheckWin(QueryInformationJobObject(job, JobObjectExtendedLimitInformation,
                out var state, size, IntPtr.Zero), "QueryInformationJobObject");
            Check(state.BasicLimitInformation.LimitFlags == KillOnJobClose, "Unexpected job limits or breakaway permission");
        }
        finally { DisposeOwned(ref job, ref duplicate, ref pi); }
    }

    private static void TestAtomicMembershipAndClose()
    {
        IntPtr job = IntPtr.Zero, duplicate = IntPtr.Zero;
        PROCESS_INFORMATION pi = default;
        try
        {
            job = CreateConfiguredJob();
            pi = LaunchAtomic(job);
            CheckWin(IsProcessInJob(pi.hProcess, job, out bool inside), "IsProcessInJob");
            Check(inside, "Child not in Job while CREATE_SUSPENDED (atomic association failed)");
            Resume(pi);
            CloseJob(ref job);
            Check(WaitForSingleObject(pi.hProcess, 10000) == WaitObject0,
                "Closing last Job handle did not kill the child");
        }
        finally { DisposeOwned(ref job, ref duplicate, ref pi); }
    }

    private static void TestDuplicateJobHandleDelaysTermination()
    {
        IntPtr job = IntPtr.Zero, duplicate = IntPtr.Zero;
        PROCESS_INFORMATION pi = default;
        try
        {
            job = CreateConfiguredJob();
            pi = LaunchAtomic(job);
            CheckWin(DuplicateHandle(GetCurrentProcess(), job, GetCurrentProcess(),
                out duplicate, 0, false, DuplicateSameAccess), "DuplicateHandle");
            Resume(pi);
            CloseJob(ref job);
            Check(WaitForSingleObject(pi.hProcess, 200) == WaitTimeout,
                "Child unexpectedly terminated before final handle closed");
            CloseJob(ref duplicate);
            Check(WaitForSingleObject(pi.hProcess, 10000) == WaitObject0,
                "Child survived closing last duplicated Job handle");
        }
        finally { DisposeOwned(ref job, ref duplicate, ref pi); }
    }

    private static void TestInvalidExecutableFailsClosed()
    {
        IntPtr job = IntPtr.Zero, duplicate = IntPtr.Zero;
        PROCESS_INFORMATION pi = default;
        try
        {
            job = CreateConfiguredJob();
            string invalidPath = Path.Combine(Path.GetTempPath(), "engineyt-b31-executable-does-not-exist.exe");
            Check(!File.Exists(invalidPath), "Invalid-path collision");
            var x = TryCreateAtomic(job, invalidPath);
            pi = x.process;
            Check(!x.created, "CreateProcessW accepted nonexistent executable");
            Check(x.error != 0, "Missing failure code for invalid executable");
        }
        finally { DisposeOwned(ref job, ref duplicate, ref pi); }
    }


    private static string ReadMarkerText(string path, int milliseconds = 10000)
    {
        var watch = Stopwatch.StartNew();
        while (watch.ElapsedMilliseconds < milliseconds)
        {
            if (File.Exists(path))
            {
                string value = File.ReadAllText(path).Trim();
                if (value.Length > 0) return value;
            }
            Thread.Sleep(40);
        }
        throw new TimeoutException("Disposable worker did not provide a marker");
    }

    private static int RunDisallowedBreakawayWorker(string marker)
    {
        // This worker runs inside a newly configured Job without BREAKAWAY_OK.
        // The only process requested is a disposable sleeping PowerShell child.
        PROCESS_INFORMATION child = default;
        try
        {
            var startup = new STARTUPINFOEX();
            startup.StartupInfo.cb = (uint)Marshal.SizeOf<STARTUPINFO>();
            string application = PowerShellPath();
            var args = new StringBuilder("\"" + application +
                "\" -NoProfile -NonInteractive -Command \"Start-Sleep -Seconds 60\"");
            bool created = CreateProcess(application, args,
                IntPtr.Zero, IntPtr.Zero, false,
                CreateBreakawayFromJob | CreateNoWindow,
                IntPtr.Zero, null, ref startup, out child);
            int error = created ? 0 : Marshal.GetLastWin32Error();
            File.WriteAllText(marker, created
                ? "UNEXPECTED_BREAKAWAY_CREATED"
                : "BREAKAWAY_DENIED_" + error.ToString(System.Globalization.CultureInfo.InvariantCulture));
            return created ? 3 : 0;
        }
        finally
        {
            if (child.hProcess != IntPtr.Zero)
            {
                TerminateProcess(child.hProcess, 1);
                WaitForSingleObject(child.hProcess, 5000);
                CloseHandle(child.hProcess);
            }
            if (child.hThread != IntPtr.Zero) CloseHandle(child.hThread);
        }
    }

    private static void TestDisallowedBreakaway()
    {
        IntPtr job = IntPtr.Zero, duplicate = IntPtr.Zero;
        PROCESS_INFORMATION pi = default;
        string marker = NewMarker();
        try
        {
            job = CreateConfiguredJob();
            var launched = TryCreateAtomic(job, OwnExecutablePath(),
                "--worker-breakaway \"" + marker + "\"");
            if (!launched.created) throw new Win32Exception(launched.error, "CreateProcessW(breakaway worker)");
            pi = launched.process;
            Resume(pi);
            string result = ReadMarkerText(marker);
            Check(result.StartsWith("BREAKAWAY_DENIED_", StringComparison.Ordinal),
                "Disallowed CREATE_BREAKAWAY_FROM_JOB unexpectedly succeeded: " + result);
            Check(WaitForSingleObject(pi.hProcess, 10000) == WaitObject0,
                "Breakaway worker did not terminate after reporting denial");
        }
        finally
        {
            DisposeOwned(ref job, ref duplicate, ref pi);
            if (File.Exists(marker)) File.Delete(marker);
        }
    }

    private static void TestInheritableJobHandleDoesNotLeakViaAtomicLaunch()
    {
        // A deliberately inheritable Job handle is the adversarial fixture.
        // The production-like launcher must force bInheritHandles=false.
        IntPtr job = IntPtr.Zero, duplicate = IntPtr.Zero;
        PROCESS_INFORMATION pi = default;
        try
        {
            job = CreateConfiguredJob();
            CheckWin(SetHandleInformation(job, 1u, 1u), "SetHandleInformation");
            CheckWin(GetHandleInformation(job, out uint flags), "GetHandleInformation");
            Check((flags & 1u) != 0, "Adversarial fixture did not mark handle inheritable");
            pi = LaunchAtomic(job); // bInheritHandles is hardcoded false.
            CheckWin(IsProcessInJob(pi.hProcess, job, out bool inside), "IsProcessInJob");
            Check(inside, "Atomic launcher lost membership");
            Resume(pi);
            CloseJob(ref job);
            Check(WaitForSingleObject(pi.hProcess, 10000) == WaitObject0,
                "Job handle inherited despite bInheritHandles=false");
        }
        finally { DisposeOwned(ref job, ref duplicate, ref pi); }
    }

    private static void TestInvalidJobHandleFailsClosed()
    {
        // -1 is a process pseudo-handle, never a valid Job Object handle.
        // Reject without creating an unsupervised disposable child.
        IntPtr job = IntPtr.Zero, duplicate = IntPtr.Zero;
        PROCESS_INFORMATION pi = default;
        bool rejected = false;
        try
        {
            try
            {
                var created = TryCreateAtomic(new IntPtr(-1), PowerShellPath());
                pi = created.process;
                rejected = !created.created && created.error != 0;
            }
            catch (Win32Exception error)
            {
                rejected = error.NativeErrorCode != 0;
            }
            Check(rejected, "Invalid Job handle was unexpectedly accepted");
        }
        finally { DisposeOwned(ref job, ref duplicate, ref pi); }
    }

    private static void TestNamedJobNameCollisionFailsClosed()
    {
        IntPtr job = IntPtr.Zero, duplicate = IntPtr.Zero;
        PROCESS_INFORMATION pi = default;
        try
        {
            string name = "Local\\EngineYT_B36_" + Guid.NewGuid().ToString("N");
            job = CreateConfiguredJob(name);
            bool rejected = false;
            IntPtr accidental = IntPtr.Zero;
            try
            {
                accidental = CreateConfiguredJob(name);
            }
            catch (InvalidOperationException)
            {
                rejected = true;
            }
            finally
            {
                if (accidental != IntPtr.Zero) CloseHandle(accidental);
            }
            Check(rejected, "Existing named Job accepted as new custodian identity");
        }
        finally { DisposeOwned(ref job, ref duplicate, ref pi); }
    }

    private static void TestUntrustedMarkerPidCannotTargetUnrelatedProcess()
    {
        // The marker PID is untrusted; a process outside the expected
        // disposable Job must never obtain a termination-capable handle.
        IntPtr job = IntPtr.Zero, duplicate = IntPtr.Zero;
        PROCESS_INFORMATION pi = default;
        using Process? control = Process.Start(new ProcessStartInfo(PowerShellPath())
        {
            UseShellExecute = false,
            CreateNoWindow = true,
            ArgumentList = { "-NoProfile", "-NonInteractive", "-Command",
                             "Start-Sleep -Seconds 60" }
        });
        Check(control is not null, "Could not create directly owned control process");
        try
        {
            job = CreateConfiguredJob(); // New empty Job, unrelated to control.
            Check(WaitForSingleObject(control!.Handle, 0) == WaitTimeout,
                "Control exited before verification test");
            IntPtr candidate = IntPtr.Zero;
            bool rejected = false;
            try
            {
                candidate = OpenVerifiedJobMember(control.Id, job);
            }
            catch (InvalidOperationException)
            {
                rejected = true;
            }
            finally
            {
                // Never terminate a candidate obtained from a forged PID.
                if (candidate != IntPtr.Zero) CloseHandle(candidate);
            }
            Check(rejected, "Untrusted PID was accepted outside its expected Job");
            Check(WaitForSingleObject(control.Handle, 0) == WaitTimeout,
                "Membership check unexpectedly terminated unrelated control");
        }
        finally
        {
            DisposeOwned(ref job, ref duplicate, ref pi);
            if (control is not null && !control.HasExited)
            {
                control.Kill(entireProcessTree: false); // Directly owned process handle.
                control.WaitForExit(10000);
            }
        }
    }

    private static void TestConcurrentIndependentJobLifetimes()
    {
        // Separate Job handles and process handles per worker; never enumerate
        // or terminate processes belonging to another test. The scenario
        // verifies there is no accidental shared process-custody state.
        const int workers = 6;
        using var launch = new ManualResetEventSlim(false);
        Task[] tasks = new Task[workers];
        for (int index = 0; index < workers; index++)
        {
            int slot = index;
            tasks[index] = Task.Run(() =>
            {
                IntPtr job = IntPtr.Zero, duplicate = IntPtr.Zero;
                PROCESS_INFORMATION pi = default;
                try
                {
                    launch.Wait();
                    job = CreateConfiguredJob();
                    pi = LaunchAtomic(job);
                    CheckWin(IsProcessInJob(pi.hProcess, job, out bool inside),
                        "IsProcessInJob(concurrent)");
                    Check(inside, "Concurrent Job association missing for worker " + slot);
                    Resume(pi);
                    CloseJob(ref job);
                    Check(WaitForSingleObject(pi.hProcess, 15000) == WaitObject0,
                        "Concurrent Job failed to terminate owned child " + slot);
                }
                finally { DisposeOwned(ref job, ref duplicate, ref pi); }
            });
        }
        launch.Set();
        Task.WaitAll(tasks);
    }

    private static void TestRepeatedAtomicCreationAndClose()
    {
        const int repetitions = 20;
        for (int i = 0; i < repetitions; i++)
        {
            IntPtr job = IntPtr.Zero, duplicate = IntPtr.Zero;
            PROCESS_INFORMATION pi = default;
            try
            {
                job = CreateConfiguredJob();
                pi = LaunchAtomic(job);
                CheckWin(IsProcessInJob(pi.hProcess, job, out bool inside), "IsProcessInJob");
                Check(inside, "Atomic Job membership missing in iteration " + i);
                Resume(pi);
                CloseJob(ref job);
                Check(WaitForSingleObject(pi.hProcess, 10000) == WaitObject0,
                    "A Job child survived last-handle close in iteration " + i);
            }
            finally { DisposeOwned(ref job, ref duplicate, ref pi); }
        }
    }

    private static string OwnExecutablePath()
    {
        string? path = Environment.ProcessPath;
        Check(path is not null && path.EndsWith(".exe", StringComparison.OrdinalIgnoreCase)
            && File.Exists(path), "A native apphost EXE is required for this isolated probe");
        return path!;
    }

    private static string NewMarker() =>
        Path.Combine(Path.GetTempPath(), "engineyt-b32-" + Guid.NewGuid().ToString("N") + ".pid");

    private static int WaitMarker(string path, int milliseconds = 10000)
    {
        var watch = Stopwatch.StartNew();
        while (watch.ElapsedMilliseconds < milliseconds)
        {
            if (File.Exists(path))
            {
                string value = File.ReadAllText(path).Trim();
                if (int.TryParse(value, out int pid) && pid > 0) return pid;
            }
            Thread.Sleep(50);
        }
        throw new TimeoutException("Disposable process did not write its PID marker");
    }

    // An untrusted PID marker cannot authorize termination. Verify membership
    // using a Job handle tied to the specific disposable test before returning.
    private static IntPtr OpenVerifiedJobMember(int pid, IntPtr expectedJob)
    {
        Check(expectedJob != IntPtr.Zero, "Missing Job identity for PID verification");
        IntPtr child = OpenProcess(Synchronize | ProcessTerminate | ProcessQueryLimitedInformation,
            false, checked((uint)pid));
        CheckWin(child != IntPtr.Zero, "OpenProcess(candidate Job descendant)");
        try
        {
            CheckWin(IsProcessInJob(child, expectedJob, out bool inside),
                "IsProcessInJob(candidate)");
            Check(inside, "Untrusted PID marker pointed outside the expected Job");
            return child;
        }
        catch
        {
            CloseHandle(child);
            throw;
        }
    }

    private static void DisposeOwnedHandle(ref IntPtr handle)
    {
        if (handle == IntPtr.Zero) return;
        if (WaitForSingleObject(handle, 0) == WaitTimeout) TerminateProcess(handle, 1);
        CloseHandle(handle);
        handle = IntPtr.Zero;
    }

    private static void TestKillWhileStillSuspended()
    {
        IntPtr job = IntPtr.Zero, duplicate = IntPtr.Zero;
        PROCESS_INFORMATION pi = default;
        try
        {
            job = CreateConfiguredJob();
            pi = LaunchAtomic(job);
            CheckWin(IsProcessInJob(pi.hProcess, job, out bool inside), "IsProcessInJob");
            Check(inside, "Suspended child was not born inside Job");
            CloseJob(ref job); // No ResumeThread; parent never executes user code.
            Check(WaitForSingleObject(pi.hProcess, 10000) == WaitObject0,
                "Closing Job handle did not kill suspended child");
        }
        finally { DisposeOwned(ref job, ref duplicate, ref pi); }
    }

    // Executed as a child inside a Job Object, and exits while its descendant keeps sleeping.
    private static int RunDescendantWorker(string marker)
    {
        var psi = new ProcessStartInfo(PowerShellPath())
        {
            UseShellExecute = false,
            CreateNoWindow = true
        };
        psi.ArgumentList.Add("-NoProfile");
        psi.ArgumentList.Add("-NonInteractive");
        psi.ArgumentList.Add("-Command");
        psi.ArgumentList.Add("Start-Sleep -Seconds 60");
        using Process? grandchild = Process.Start(psi);
        Check(grandchild is not null, "Failed to create disposable descendant");
        File.WriteAllText(marker, grandchild!.Id.ToString(System.Globalization.CultureInfo.InvariantCulture));
        return 0;
    }

    private static void TestGrandchildAfterParentExit()
    {
        IntPtr job = IntPtr.Zero, duplicate = IntPtr.Zero, descendant = IntPtr.Zero;
        PROCESS_INFORMATION pi = default;
        string marker = NewMarker();
        try
        {
            job = CreateConfiguredJob();
            var launched = TryCreateAtomic(job, OwnExecutablePath(),
                "--worker-descendant \"" + marker + "\"");
            if (!launched.created) throw new Win32Exception(launched.error, "CreateProcessW(worker in Job)");
            pi = launched.process;
            Resume(pi);
            int descendantPid = WaitMarker(marker);
            descendant = OpenVerifiedJobMember(descendantPid, job);
            Check(WaitForSingleObject(pi.hProcess, 10000) == WaitObject0,
                "Worker did not exit after writing descendant PID");
            Check(WaitForSingleObject(descendant, 0) == WaitTimeout,
                "Descendant terminated unexpectedly before closing Job");
            CloseJob(ref job);
            Check(WaitForSingleObject(descendant, 10000) == WaitObject0,
                "Grandchild survived final close after parent exited");
        }
        finally
        {
            DisposeOwned(ref job, ref duplicate, ref pi);
            DisposeOwnedHandle(ref descendant);
            if (File.Exists(marker)) File.Delete(marker);
        }
    }

    // Separate custodian process intentionally killed by the parent test.
    private static int RunCustodian(string marker, string jobName)
    {
        IntPtr job = IntPtr.Zero, duplicate = IntPtr.Zero;
        PROCESS_INFORMATION pi = default;
        try
        {
            job = CreateConfiguredJob(jobName);
            pi = LaunchAtomic(job);
            Resume(pi);
            File.WriteAllText(marker,
                pi.dwProcessId.ToString(System.Globalization.CultureInfo.InvariantCulture));
            Thread.Sleep(TimeSpan.FromSeconds(60));
            return 0;
        }
        finally { DisposeOwned(ref job, ref duplicate, ref pi); }
    }

    private static void TestAbruptCustodianTermination()
    {
        string marker = NewMarker();
        string jobName = "Local\\EngineYT_B35_" + Guid.NewGuid().ToString("N");
        IntPtr child = IntPtr.Zero, verificationJob = IntPtr.Zero;
        using Process? custodian = Process.Start(new ProcessStartInfo(OwnExecutablePath())
        {
            UseShellExecute = false,
            CreateNoWindow = true,
            ArgumentList = { "--custodian", marker, jobName }
        });
        Check(custodian is not null, "Could not start separate custodian");
        try
        {
            int childPid = WaitMarker(marker);
            verificationJob = OpenJobObject(JobObjectQuery, false, jobName);
            CheckWin(verificationJob != IntPtr.Zero, "OpenJobObject(own custodian)");
            child = OpenVerifiedJobMember(childPid, verificationJob);
            Check(WaitForSingleObject(child, 0) == WaitTimeout,
                "Custodian child exited before termination test");
            // Important: the verifier's own handle must be closed BEFORE
            // killing the custodian, or it would prevent KILL_ON_JOB_CLOSE.
            CheckWin(CloseHandle(verificationJob), "CloseHandle(verification Job)");
            verificationJob = IntPtr.Zero;
            // Abrupt OS termination (without managed finally) of only the owned custodian.
            custodian!.Kill(entireProcessTree: false);
            Check(custodian.WaitForExit(10000), "Custodian did not exit after Kill");
            Check(WaitForSingleObject(child, 10000) == WaitObject0,
                "Child survived abrupt custodian death: Job handle leak or policy failure");
        }
        finally
        {
            if (verificationJob != IntPtr.Zero) CloseHandle(verificationJob);
            if (custodian is not null && !custodian.HasExited)
            {
                custodian.Kill(entireProcessTree: false);
                custodian.WaitForExit(10000);
            }
            DisposeOwnedHandle(ref child);
            if (File.Exists(marker)) File.Delete(marker);
        }
    }

    public static int Main(string[] args)
    {
        if (args.Length == 2 && args[0] == "--worker-descendant") return RunDescendantWorker(args[1]);
        if (args.Length == 2 && args[0] == "--worker-breakaway") return RunDisallowedBreakawayWorker(args[1]);
        if (args.Length == 3 && args[0] == "--custodian") return RunCustodian(args[1], args[2]);
        if (!OperatingSystem.IsWindows()) { Console.Error.WriteLine("BLOCKED: Windows native required"); return 2; }
        if (IntPtr.Size != 8) { Console.Error.WriteLine("BLOCKED: 64-bit runner required"); return 2; }
        var checks = new (string, Action)[]
        {
            ("configuration-and-job-handle-inheritance", TestConfiguredJobAndHandleInheritance),
            ("atomic-job-list-and-kill-on-last-close", TestAtomicMembershipAndClose),
            ("duplicated-job-handle-lifetime", TestDuplicateJobHandleDelaysTermination),
            ("invalid-executable-fail-closed", TestInvalidExecutableFailsClosed),
            ("suspended-child-killed-before-resume", TestKillWhileStillSuspended),
            ("descendant-after-parent-exit-killed-by-job", TestGrandchildAfterParentExit),
            ("abrupt-custodian-death-kills-owned-child", TestAbruptCustodianTermination),
            ("explicit-breakaway-denied-by-job-policy", TestDisallowedBreakaway),
            ("twenty-atomic-creation-close-repetitions", TestRepeatedAtomicCreationAndClose),
            ("inheritable-job-handle-cannot-leak-with-inherit-false", TestInheritableJobHandleDoesNotLeakViaAtomicLaunch),
            ("invalid-job-handle-fail-closed", TestInvalidJobHandleFailsClosed),
            ("forged-pid-marker-never-targets-unrelated-process", TestUntrustedMarkerPidCannotTargetUnrelatedProcess),
            ("named-job-collision-rejected", TestNamedJobNameCollisionFailsClosed),
            ("six-concurrent-independent-jobs", TestConcurrentIndependentJobLifetimes)
        };
        int passed = 0;
        foreach (var (name, action) in checks)
        {
            try { action(); Console.WriteLine("PASS " + name); passed++; }
            catch (Exception e) { Console.Error.WriteLine("FAIL " + name + ": " + e); }
        }
        Console.WriteLine($"B31_RESULT pass={passed} fail={checks.Length - passed} total={checks.Length} scope=native-windows-probe-not-gate-v8");
        return passed == checks.Length ? 0 : 1;
    }
}
