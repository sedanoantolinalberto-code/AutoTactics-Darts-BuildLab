// B31 ISOLATED WINDOWS API PROBE. NOT the EngineYT B23-B25 native Gate V8.
// Runs only self-owned, short-lived PowerShell child processes on a disposable CI runner.
// No integration, rendering, upload, or publication authority.
using System;
using System.ComponentModel;
using System.Runtime.InteropServices;
using System.Text;
using System.IO;

internal static class Program
{
    private const uint KillOnJobClose = 0x2000;
    private const uint BreakawayOk = 0x800;
    private const uint SilentBreakawayOk = 0x1000;
    private const uint ExtendedStartupInfoPresent = 0x00080000;
    private const uint CreateSuspended = 0x00000004;
    private const uint CreateNoWindow = 0x08000000;
    private const uint WaitObject0 = 0;
    private const uint WaitTimeout = 258;
    private const uint DuplicateSameAccess = 2;
    private const int JobObjectExtendedLimitInformation = 9;
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
    [return: MarshalAs(UnmanagedType.Bool)]
    private static extern bool GetHandleInformation(IntPtr handle, out uint flags);
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

    private static IntPtr CreateConfiguredJob()
    {
        IntPtr job = CreateJobObject(IntPtr.Zero, null);
        CheckWin(job != IntPtr.Zero, "CreateJobObject");
        try
        {
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

    private static (bool created, PROCESS_INFORMATION process, int error) TryCreateAtomic(IntPtr job, string program)
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
            var cmd = new StringBuilder("\"" + program +
                "\" -NoProfile -NonInteractive -Command \"Start-Sleep -Seconds 60\"");
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

    public static int Main()
    {
        if (!OperatingSystem.IsWindows()) { Console.Error.WriteLine("BLOCKED: Windows native required"); return 2; }
        if (IntPtr.Size != 8) { Console.Error.WriteLine("BLOCKED: 64-bit runner required"); return 2; }
        var checks = new (string, Action)[]
        {
            ("configuration-and-job-handle-inheritance", TestConfiguredJobAndHandleInheritance),
            ("atomic-job-list-and-kill-on-last-close", TestAtomicMembershipAndClose),
            ("duplicated-job-handle-lifetime", TestDuplicateJobHandleDelaysTermination),
            ("invalid-executable-fail-closed", TestInvalidExecutableFailsClosed)
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
