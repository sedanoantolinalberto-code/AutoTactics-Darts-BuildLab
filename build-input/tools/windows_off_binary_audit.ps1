# S34 v0.20: compile-only OFF binary evidence collection; NEVER runs media executable.
[CmdletBinding()]
param([Parameter(Mandatory=$true)][string]$BuildDir)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$source = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$build = [IO.Path]::GetFullPath($BuildDir)
$cache = Join-Path $build 'CMakeCache.txt'
& python (Join-Path $source 'tools/verify_compile_plan.py') '--root' $source '--cache' $cache
if ($LASTEXITCODE -ne 0) { throw 'OFF CMake cache verification failed' }
$exe = Join-Path $build 'Release\mf_p0_windows.exe'
$project = Join-Path $build 'mf_p0_windows.vcxproj'
if (-not (Test-Path -LiteralPath $exe -PathType Leaf)) { throw 'OFF executable absent' }
if (-not (Test-Path -LiteralPath $project -PathType Leaf)) { throw 'Visual Studio project evidence absent' }
$dumpbin = Get-Command 'dumpbin.exe' -ErrorAction SilentlyContinue
if ($null -eq $dumpbin) {
    $installer = Join-Path ${env:ProgramFiles(x86)} 'Microsoft Visual Studio\Installer\vswhere.exe'
    if (-not (Test-Path -LiteralPath $installer)) { throw 'No dumpbin or vswhere; cannot claim link verification' }
    $install = & $installer '-latest' '-products' '*' '-requires' 'Microsoft.VisualStudio.Component.VC.Tools.x86.x64' '-property' 'installationPath'
    if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($install)) { throw 'Cannot locate VS C++ installation' }
    $toolsRoot = Join-Path ($install.Trim()) 'VC\Tools\MSVC'
    if (-not (Test-Path -LiteralPath $toolsRoot)) { throw 'MSVC tools not found' }
    $versions = @(Get-ChildItem -LiteralPath $toolsRoot -Directory | Sort-Object Name -Descending)
    foreach ($version in $versions) {
        $candidate = Join-Path $version.FullName 'bin\Hostx64\x64\dumpbin.exe'
        if (Test-Path -LiteralPath $candidate -PathType Leaf) { $dumpbin = $candidate; break }
    }
}
if ($null -eq $dumpbin) { throw 'No dumpbin available; fail closed' }
$hashBefore = (Get-FileHash -LiteralPath $exe -Algorithm SHA256).Hash
$dumpPath = Join-Path $build 'MF_P0_OFF_IMPORTS_dumpbin.txt'
# Dump import tables only; DO NOT run mf_p0_windows.exe.
$dump = & $dumpbin '/IMPORTS' $exe 2>&1
if ($LASTEXITCODE -ne 0) { throw ('dumpbin /IMPORTS failed: ' + $LASTEXITCODE) }
$dump | Out-File -LiteralPath $dumpPath -Encoding utf8
$hashAfter = (Get-FileHash -LiteralPath $exe -Algorithm SHA256).Hash
if ($hashBefore -cne $hashAfter) { throw 'Executable changed during import audit; evidence invalid' }
& python (Join-Path $source 'tools/audit_windows_off_link.py') '--imports' $dumpPath '--vcxproj' $project
if ($LASTEXITCODE -ne 0) { throw 'OFF link/import audit rejected the evidence' }
Write-Host ('PASS limited Windows OFF artifact audit. Executable SHA256: ' + $hashAfter)
Write-Host ('Import evidence: ' + $dumpPath)
Write-Host 'Does NOT prove absence of every possible code path or compliance with Policy B.'
