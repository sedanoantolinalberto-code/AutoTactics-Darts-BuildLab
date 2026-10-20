"""Fail-closed provenance and compile-only plan verifier; never runs executables."""
from __future__ import annotations
import argparse
import hashlib
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]

class ReviewError(ValueError):
    pass

def _load(root: pathlib.Path, path: str) -> str:
    return (root / path).read_text(encoding='utf-8')

def review_source(root: pathlib.Path = ROOT) -> list[str]:
    """Static checks only: never substitute this for an MSVC link inspection."""
    cmake = _load(root, 'CMakeLists.txt')
    main = _load(root, 'src/mf_p0_windows.cpp')
    writer = _load(root, 'src/mf_p0_writer.cpp')
    ps = _load(root, 'tools/windows_compile_only.ps1')
    errors: list[str] = []
    def require(ok: bool, condition: str) -> None:
        if not ok: errors.append(condition)
    require(bool(re.search(r'option\(ENGINEYT_ALLOW_NONPOLICY_MEDIA_OUTPUT\s+"[^"]+" OFF\)', cmake)), 'CMake default not OFF')
    require('if(WIN32 AND MSVC)' in cmake, 'Windows target not restricted')
    require('add_library(mf_p0_writer_compile_probe OBJECT src/mf_p0_writer.cpp)' in cmake, 'Object-only SDK probe absent')
    require('add_executable(mf_p0_windows src/mf_p0_windows.cpp)' in cmake, 'Windows entry executable absent')
    guard = 'if(ENGINEYT_ALLOW_NONPOLICY_MEDIA_OUTPUT)'
    guarded_link = 'target_sources(mf_p0_windows PRIVATE $<TARGET_OBJECTS:mf_p0_writer_compile_probe>)'
    guarded_libs = 'target_link_libraries(mf_p0_windows PRIVATE mfreadwrite mfplat mfuuid ole32)'
    require(cmake.count(guard) == 1, 'Ambiguous experimental CMake gate')
    require(cmake.count(guarded_link) == 1 and cmake.count(guarded_libs) == 1, 'Writer object or libraries not linked exactly once')
    if guard in cmake and guarded_link in cmake and guarded_libs in cmake:
        branch = cmake.split(guard, 1)[1].split('else()', 1)[0]
        require(guarded_link in branch and guarded_libs in branch and
                'ENGINEYT_ALLOW_NONPOLICY_MEDIA_OUTPUT=1' in branch,
                'Writer object or libraries not exclusively within ON branch')
        off = cmake.split(guard, 1)[1].split('else()', 1)[1].split('endif()', 1)[0]
        require('ENGINEYT_ALLOW_NONPOLICY_MEDIA_OUTPUT=0' in off and
                guarded_link not in off and guarded_libs not in off,
                'OFF branch unexpectedly links media code')
    require('#if ENGINEYT_ALLOW_NONPOLICY_MEDIA_OUTPUT == 0' in main, 'Disabled executable branch absent')
    require('#if ENGINEYT_ALLOW_NONPOLICY_MEDIA_OUTPUT == 1' in main, 'Enabled-only symbol declaration absent')
    require('return RunExperimentalMedia();' in main, 'Enabled path invocation absent')
    if '#if ENGINEYT_ALLOW_NONPOLICY_MEDIA_OUTPUT == 0' in main:
        off_branch = main.split('#if ENGINEYT_ALLOW_NONPOLICY_MEDIA_OUTPUT == 0', 1)[1].split('#else', 1)[0]
        require('return 2;' in off_branch and 'RunExperimentalMedia(' not in off_branch,
                'OFF executable reaches writer')
    require(all(word not in main for word in
                ('MFCreateSinkWriterFromURL', 'OpenSink(', 'WriteSample(', 'Finalize()',
                 'SendFrame(', 'fs::create_directory(', '#include <mfreadwrite.h>')),
            'Main executable contains writer API')
    require('MFCreateSinkWriterFromURL' in writer and 'WriteSample(' in writer and
            'Finalize()' in writer and 'int RunExperimentalMedia()' in writer,
            'Writer SDK probe does not contain all expected APIs')
    require('ENGINEYT_ALLOW_NONPOLICY_MEDIA_OUTPUT:BOOL=OFF' in ps and
            'Assert-CMakeOff' in ps, 'PowerShell does not enforce OFF')
    require("'mf_p0_writer_compile_probe'" in ps, 'PowerShell does not explicitly build SDK probe')
    require('mf_p0_windows.exe' not in ps and 'mf_p0_windows ' not in ps,
            'PowerShell may invoke media executable')
    require('source_math_and_pixel_pattern|compile_and_runtime_output_gates' in ps,
            'PowerShell portable CTest allowlist absent')
    return errors

def verify_cache_text(text: str) -> None:
    vals = re.findall(r'^ENGINEYT_ALLOW_NONPOLICY_MEDIA_OUTPUT:BOOL=([^\n]+)$', text.replace('\r\n', '\n'), re.M)
    if vals != ['OFF']:
        raise ReviewError(f'Expected exactly one OFF cache value, got {vals}')

def verify_manifest(root: pathlib.Path, reference: str = 'MANIFEST_SHA256.json') -> tuple[int,int]:
    import json
    raw=json.loads((root/reference).read_text(encoding='utf-8'))
    entries=raw['files'] if isinstance(raw, dict) and 'files' in raw else raw
    if isinstance(entries,list):
        raise ReviewError('Manifest format unsupported')
    checked=0
    for name,digest in entries.items():
        path=pathlib.PurePosixPath(name)
        if path.is_absolute() or '..' in path.parts:
            raise ReviewError('Manifest path escapes root')
        data=(root/name).read_bytes()
        if isinstance(digest,dict): digest=digest.get('sha256')
        if hashlib.sha256(data).hexdigest()!=digest:
            raise ReviewError(f'SHA mismatch: {name}')
        checked+=1
    return checked,len(entries)

def main() -> int:
    a=argparse.ArgumentParser()
    a.add_argument('--root',type=pathlib.Path,default=ROOT)
    a.add_argument('--cache',type=pathlib.Path)
    a.add_argument('--manifest',action='store_true')
    args=a.parse_args()
    errors=review_source(args.root)
    if errors:
        print('FAIL source: '+'; '.join(errors),file=sys.stderr)
        return 2
    if args.cache:
        try:verify_cache_text(args.cache.read_text(encoding='utf-8'))
        except (OSError,ReviewError) as e:
            print(f'FAIL cache: {e}',file=sys.stderr)
            return 2
    if args.manifest:
        try:
            print('manifest PASS', *verify_manifest(args.root))
        except (OSError,ReviewError,KeyError,ValueError) as e:
            print('FAIL manifest:',e,file=sys.stderr)
            return 2
    print('PASS compile-only plan (static inspection, not Windows SDK compilation)')
    return 0
if __name__=='__main__':raise SystemExit(main())
