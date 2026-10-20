# S34 v0.18. COMPILE ONLY. Never launch the media binary or any renderer.
# Requires Visual Studio 2022 C++ + Windows SDK, CMake >= 3.20, Python 3.
[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)][string]$BuildDir
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$source = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$target = [IO.Path]::GetFullPath($BuildDir)
$sourcePrefix = $source.TrimEnd('\','/') + [IO.Path]::DirectorySeparatorChar
if ($target.Equals($source, [StringComparison]::OrdinalIgnoreCase) -or
    $target.StartsWith($sourcePrefix, [StringComparison]::OrdinalIgnoreCase)) {
    throw 'Build directory must be outside the source tree'
}
if (Test-Path -LiteralPath $target) {
    throw 'Build directory must not exist: use a new empty path, never reuse a cached configuration'
}
$parent = Split-Path -Parent $target
if (-not (Test-Path -LiteralPath $parent -PathType Container)) {
    throw 'Build directory parent must already exist'
}
# This is a cleanliness precaution, not full protection from hostile filesystem races.
if ((Get-Item -LiteralPath $parent -Force).Attributes -band [IO.FileAttributes]::ReparsePoint) {
    throw 'Refuse reparse-point parent'
}
function Assert-CMakeOff([string]$cachePath) {
    if (-not (Test-Path -LiteralPath $cachePath -PathType Leaf)) {
        throw 'No CMakeCache.txt after configure'
    }
    $rows = @(Get-Content -LiteralPath $cachePath | Where-Object {
        $_ -match '^ENGINEYT_ALLOW_NONPOLICY_MEDIA_OUTPUT:BOOL='
    })
    if ($rows.Count -ne 1 -or $rows[0] -cne 'ENGINEYT_ALLOW_NONPOLICY_MEDIA_OUTPUT:BOOL=OFF') {
        throw 'Refuse media-output-enabled or ambiguous CMake cache'
    }
}
$start = Get-Date -Format o
Write-Host 'COMPILE-ONLY configure'
& cmake '-S' $source '-B' $target '-G' 'Visual Studio 17 2022' '-A' 'x64' '-DENGINEYT_ALLOW_NONPOLICY_MEDIA_OUTPUT:BOOL=OFF'
if ($LASTEXITCODE -ne 0) { throw ('cmake configure failed: ' + $LASTEXITCODE) }
Assert-CMakeOff (Join-Path $target 'CMakeCache.txt')
Write-Host 'COMPILE-ONLY build'
& cmake '--build' $target '--config' 'Release'
if ($LASTEXITCODE -ne 0) { throw ('cmake build failed: ' + $LASTEXITCODE) }
Assert-CMakeOff (Join-Path $target 'CMakeCache.txt')
# Explicitly build the object-only Media Foundation compile probe. This compiles
# its APIs with MSVC/Windows SDK but does not link them to the default executable.
Write-Host 'COMPILE-ONLY Media Foundation SDK object probe'
& cmake '--build' $target '--config' 'Release' '--target' 'mf_p0_writer_compile_probe'
if ($LASTEXITCODE -ne 0) { throw ('Media Foundation SDK object probe failed: ' + $LASTEXITCODE) }
Assert-CMakeOff (Join-Path $target 'CMakeCache.txt')
# Only execute the two portable test binaries; never execute mf_p0_windows.
& ctest '--test-dir' $target '-C' 'Release' '--output-on-failure' '-R' '^(source_math_and_pixel_pattern|compile_and_runtime_output_gates)$'
if ($LASTEXITCODE -ne 0) { throw ('portable CTest failed: ' + $LASTEXITCODE) }
Assert-CMakeOff (Join-Path $target 'CMakeCache.txt')
# Review the *actual* disabled executable import table and generated linker inputs.
& (Join-Path $source 'tools/windows_off_binary_audit.ps1') -BuildDir $target
Assert-CMakeOff (Join-Path $target 'CMakeCache.txt')
& python (Join-Path $source 'tools/verify_compile_plan.py') '--root' $source '--cache' (Join-Path $target 'CMakeCache.txt') '--manifest'
if ($LASTEXITCODE -ne 0) { throw ('plan or manifest failed: ' + $LASTEXITCODE) }
Write-Host ("SOURCE-ONLY Windows compile complete; MF executable NOT run. Started: $start")
Write-Host 'Does not demonstrate Media Foundation negotiation, MP4 creation, or Policy B compliance.'
