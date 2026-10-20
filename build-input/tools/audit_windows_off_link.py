"""Review-only Windows OFF binary audit, no binary execution.

Inputs must be real dumpbin /IMPORTS text and generated Visual Studio .vcxproj.
Passing means only that those artifacts show no detected writer imports/link inputs;
it is NOT an execution, sandbox, or E5B4D certification.
"""
import argparse
import pathlib
import re
import sys
import xml.etree.ElementTree as ET

class LinkAuditError(ValueError):
    pass

# The default OFF executable must not import these media/encoder libraries.
PROHIBITED_DLLS = {
    'mfreadwrite.dll', 'mfplat.dll', 'mf.dll', 'mfcore.dll',
    'evr.dll', 'msmpeg2venc.dll', 'mfmp4srcsnk.dll',
    'avcodec.dll', 'avformat.dll', 'avutil.dll', 'swscale.dll',
}
PROHIBITED_LIBS = {
    'mfreadwrite.lib', 'mfplat.lib', 'mfuuid.lib', 'mf.lib',
    'evr.lib', 'msmpeg2venc.lib', 'mfmp4srcsnk.lib',
    'avcodec.lib', 'avformat.lib', 'avutil.lib', 'swscale.lib',
}
WRITER_SYMBOL = re.compile(r'\b(?:MFCreateSinkWriterFromURL|MFStartup|RunExperimentalMedia|OpenSink|SendFrame|WriteSample)\b', re.I)
DLL_LINE = re.compile(r'^\s*([a-zA-Z0-9_.+-]+\.dll)\s*$', re.I | re.M)


def verify_import_dump(text: str) -> set[str]:
    """Conservatively parse English dumpbin.exe /IMPORTS output."""
    if not re.search(r'(?im)^\s*File Type:\s*EXECUTABLE IMAGE\s*$', text):
        raise LinkAuditError('No validated dumpbin executable-image header')
    # Require an import table, rather than falsely accepting empty/truncated text.
    if not re.search(r'(?i)Section contains the following imports:', text):
        raise LinkAuditError('Missing dumpbin import-section evidence')
    dlls = {s.lower() for s in DLL_LINE.findall(text)}
    if not dlls:
        raise LinkAuditError('No DLL import entries; dumpbin text may be incomplete')
    prohibited = dlls & PROHIBITED_DLLS
    if prohibited:
        raise LinkAuditError('Prohibited media DLL imports: ' + ', '.join(sorted(prohibited)))
    if WRITER_SYMBOL.search(text):
        raise LinkAuditError('Media/writer symbol appears in executable imports')
    return dlls


def verify_vcxproj(text: str) -> dict[str, int]:
    """Review active compile/link entries of the generated target project."""
    try:
        root = ET.fromstring(text)
    except ET.ParseError as ex:
        raise LinkAuditError(f'Invalid .vcxproj XML: {ex}') from ex
    compile_sources: list[str] = []
    link_fields: list[str] = []
    for node in root.iter():
        tag = node.tag.rpartition('}')[2]
        if tag == 'ClCompile' and node.get('Include'):
            compile_sources.append(node.get('Include', '').replace('/', '\\').lower())
        if tag in ('AdditionalDependencies', 'AdditionalOptions', 'AdditionalLibraryDirectories'):
            link_fields.append(node.text or '')
        if tag in ('Link', 'ProjectReference', 'Object') and node.get('Include'):
            link_fields.append(node.get('Include', ''))
    if not any(s.endswith('\\mf_p0_windows.cpp') or s == 'mf_p0_windows.cpp'
               for s in compile_sources):
        raise LinkAuditError('Default executable entry translation unit missing')
    if any(s.endswith('\\mf_p0_writer.cpp') or s == 'mf_p0_writer.cpp'
           for s in compile_sources):
        raise LinkAuditError('Writer translation unit compiled into executable target')
    link_text = ' '.join(link_fields).lower()
    if 'mf_p0_writer_compile_probe' in link_text or 'mf_p0_writer.obj' in link_text:
        raise LinkAuditError('Writer object referenced by executable linker')
    for lib in PROHIBITED_LIBS:
        if re.search(r'(?<![\w.])' + re.escape(lib) + r'(?![\w.])', link_text):
            raise LinkAuditError('Prohibited link library: ' + lib)
    # Project may include imported DLLs via other targets; checking link inputs
    # cannot replace inspection of actual imports.
    return {'compile_sources': len(compile_sources), 'link_fields': len(link_fields)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--imports', type=pathlib.Path, required=True)
    parser.add_argument('--vcxproj', type=pathlib.Path, required=True)
    args = parser.parse_args()
    try:
        for path in (args.imports, args.vcxproj):
            if not path.is_file():
                raise LinkAuditError(f'Evidence file absent: {path}')
        dlls = verify_import_dump(args.imports.read_text(encoding='utf-8-sig'))
        project = verify_vcxproj(args.vcxproj.read_text(encoding='utf-8-sig'))
    except (LinkAuditError, UnicodeError, OSError) as ex:
        print(f'FAIL: {ex}', file=sys.stderr)
        return 2
    print(f'PASS limited OFF binary evidence: {len(dlls)} DLLs inspected; '
          f'{project["compile_sources"]} source entries; media writer not detected. '
          'NOT an E5B4D/Policy B guarantee.')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
