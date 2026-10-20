$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$build = Join-Path $env:RUNNER_TEMP 's34-off-build'
$evidence = Join-Path $env:RUNNER_TEMP 's34-evidence'
New-Item -ItemType Directory -Path $evidence | Out-Null
@{commit=$env:GITHUB_SHA; run=$env:GITHUB_RUN_ID; image=$env:ImageVersion; policy='NO-GO'; media_executed=$false} |
    ConvertTo-Json | Set-Content (Join-Path $evidence 'context.json')
try {
    & ./build-input/tools/windows_compile_only.ps1 -BuildDir $build
    if ($LASTEXITCODE -ne 0) { throw 'Compile driver failed' }
    $before = @(Get-ChildItem $build -Recurse -File | Where-Object { $_.Extension -in '.exe','.obj' } |
        ForEach-Object { @{path=$_.FullName.Substring($build.Length); sha256=(Get-FileHash $_.FullName -Algorithm SHA256).Hash} })
    $before | ConvertTo-Json | Set-Content (Join-Path $evidence 'binary-sha256-pre.json')
    & ./build-input/tools/windows_off_binary_audit.ps1 -BuildDir $build
    if ($LASTEXITCODE -ne 0) { throw 'Repeated read-only audit failed' }
    $after = @(Get-ChildItem $build -Recurse -File | Where-Object { $_.Extension -in '.exe','.obj' } |
        ForEach-Object { @{path=$_.FullName.Substring($build.Length); sha256=(Get-FileHash $_.FullName -Algorithm SHA256).Hash} })
    $after | ConvertTo-Json | Set-Content (Join-Path $evidence 'binary-sha256-post.json')
    if (($before | ConvertTo-Json -Compress) -cne ($after | ConvertTo-Json -Compress)) { throw 'Binary hashes changed' }
} finally {
    foreach ($name in @('CMakeCache.txt','mf_p0_windows.vcxproj','mf_p0_writer_compile_probe.vcxproj','MF_P0_OFF_IMPORTS_dumpbin.txt','mf_p0_link_only_probe.vcxproj','MF_P0_LINK_IMPORTS_dumpbin.txt')) {
        $item = Join-Path $build $name
        if (Test-Path $item) { Copy-Item -LiteralPath $item -Destination $evidence }
    }
    $ctest = Join-Path $build 'Testing/Temporary/LastTest.log'
    if (Test-Path $ctest) { Copy-Item -LiteralPath $ctest -Destination $evidence }
}
