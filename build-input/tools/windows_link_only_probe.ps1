# S34 v0.25 — LINK ONLY; NEVER invoke any media-capable binary.
[CmdletBinding()]
param([Parameter(Mandatory=$true)][string]$BuildDir)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$source = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$build = [IO.Path]::GetFullPath($BuildDir)
$cache = Join-Path $build 'CMakeCache.txt'
& python (Join-Path $source 'tools/verify_compile_plan.py') '--root' $source '--cache' $cache '--manifest'
if ($LASTEXITCODE -ne 0) { throw 'Refuse invalid OFF plan, source or manifest' }
Write-Host 'LINK-ONLY Media Foundation unresolved-symbol probe (DO NOT RUN executable)'
& cmake '--build' $build '--config' 'Release' '--target' 'mf_p0_link_only_probe'
if ($LASTEXITCODE -ne 0) { throw ('MF link-only probe failed: ' + $LASTEXITCODE) }
& python (Join-Path $source 'tools/verify_compile_plan.py') '--root' $source '--cache' $cache
if ($LASTEXITCODE -ne 0) { throw 'OFF cache changed after link; fail closed' }
$exe = Join-Path $build 'Release\mf_p0_link_only_probe.exe'
$project = Join-Path $build 'mf_p0_link_only_probe.vcxproj'
if (-not (Test-Path -LiteralPath $exe -PathType Leaf)) { throw 'Link-probe executable absent' }
if (-not (Test-Path -LiteralPath $project -PathType Leaf)) { throw 'Link-probe project absent' }
$dumpbin = Get-Command 'dumpbin.exe' -ErrorAction SilentlyContinue
if ($null -eq $dumpbin) {
    $installer = Join-Path ${env:ProgramFiles(x86)} 'Microsoft Visual Studio\Installer\vswhere.exe'
    if (-not (Test-Path -LiteralPath $installer)) { throw 'dumpbin unavailable and vswhere missing' }
    $install = & $installer '-latest' '-products' '*' '-requires' 'Microsoft.VisualStudio.Component.VC.Tools.x86.x64' '-property' 'installationPath'
    if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($install)) { throw 'MSVC tools unavailable' }
    $toolsRoot = Join-Path ($install.Trim()) 'VC\Tools\MSVC'
    $versions = @(Get-ChildItem -LiteralPath $toolsRoot -Directory | Sort-Object Name -Descending)
    foreach ($version in $versions) {
        $candidate = Join-Path $version.FullName 'bin\Hostx64\x64\dumpbin.exe'
        if (Test-Path -LiteralPath $candidate -PathType Leaf) { $dumpbin = $candidate; break }
    }
}
if ($null -eq $dumpbin) { throw 'dumpbin absent; cannot validate media import' }
$hashBefore = (Get-FileHash -LiteralPath $exe -Algorithm SHA256).Hash
$dumpPath = Join-Path $build 'MF_P0_LINK_IMPORTS_dumpbin.txt'
$imports = & $dumpbin '/IMPORTS' $exe 2>&1
if ($LASTEXITCODE -ne 0) { throw ('dumpbin link-probe imports failed: ' + $LASTEXITCODE) }
$imports | Out-File -LiteralPath $dumpPath -Encoding utf8
$hashAfter = (Get-FileHash -LiteralPath $exe -Algorithm SHA256).Hash
if ($hashBefore -cne $hashAfter) { throw 'Link-probe executable hash changed during read-only audit' }
$text = Get-Content -LiteralPath $dumpPath -Raw
if ($text -notmatch '(?i)mfreadwrite\.dll' -or $text -notmatch 'MFCreateSinkWriterFromURL') {
    throw 'Media Foundation writer import is absent: no demonstrated symbol retention'
}
Write-Host ('PASS limited MF SDK link and import evidence (never executed). SHA256: ' + $hashAfter)
Write-Host 'Does not demonstrate Media Foundation negotiation, runtime behavior or Policy B compliance.'
