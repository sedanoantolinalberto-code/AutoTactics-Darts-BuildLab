"""Pure synthetic evidence QA; never invokes a binary or dumpbin."""
from pathlib import Path
import importlib.util
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('off_binary', ROOT/'tools/audit_windows_off_link.py')
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)

IMPORTS_OK = '''Microsoft (R) COFF/PE Dumper Version 14.x
Dump of file C:\\test\\Release\\mf_p0_windows.exe
File Type: EXECUTABLE IMAGE
  Section contains the following imports:
    KERNEL32.dll
    MSVCP140.dll
  Summary
'''
VCXPROJ_OK = '''<?xml version="1.0" encoding="utf-8"?>
<Project xmlns="http://schemas.microsoft.com/developer/msbuild/2003">
  <ItemGroup><ClCompile Include="C:\\tmp\\src\\mf_p0_windows.cpp" /></ItemGroup>
  <ItemDefinitionGroup><Link><AdditionalDependencies>kernel32.lib;ole32.lib;%(AdditionalDependencies)</AdditionalDependencies></Link></ItemDefinitionGroup>
</Project>
'''

class WindowsOffLinkTests(unittest.TestCase):
    def test_clean_synthetic_imports(self):
        self.assertEqual({'kernel32.dll','msvcp140.dll'},audit.verify_import_dump(IMPORTS_OK))
    def test_clean_synthetic_project(self):
        self.assertEqual(1,audit.verify_vcxproj(VCXPROJ_OK)['compile_sources'])
    def test_missing_header_denied(self):
        with self.assertRaises(audit.LinkAuditError):
            audit.verify_import_dump(IMPORTS_OK.replace('File Type: EXECUTABLE IMAGE',''))
    def test_missing_import_section_denied(self):
        with self.assertRaises(audit.LinkAuditError):
            audit.verify_import_dump(IMPORTS_OK.replace('Section contains the following imports:',''))
    def test_empty_imports_denied(self):
        with self.assertRaises(audit.LinkAuditError):
            audit.verify_import_dump(IMPORTS_OK.replace('KERNEL32.dll','KERNEL32').replace('MSVCP140.dll','MSVCP140'))
    def test_media_dll_names_denied(self):
        for dll in sorted(audit.PROHIBITED_DLLS):
            with self.subTest(dll=dll),self.assertRaises(audit.LinkAuditError):
                audit.verify_import_dump(IMPORTS_OK.replace('MSVCP140.dll',dll))
    def test_writer_symbols_denied(self):
        for name in ('MFCreateSinkWriterFromURL','MFStartup','RunExperimentalMedia','WriteSample'):
            with self.subTest(name=name),self.assertRaises(audit.LinkAuditError):
                audit.verify_import_dump(IMPORTS_OK.replace('  Summary',f'    {name}\n  Summary'))
    def test_case_insensitive_dll(self):
        with self.assertRaises(audit.LinkAuditError):
            audit.verify_import_dump(IMPORTS_OK.replace('KERNEL32.dll','MFREADWRITE.DLL'))
    def test_xml_parse_error(self):
        with self.assertRaises(audit.LinkAuditError):audit.verify_vcxproj('<Project')
    def test_project_main_missing(self):
        with self.assertRaises(audit.LinkAuditError):
            audit.verify_vcxproj(VCXPROJ_OK.replace('mf_p0_windows.cpp','another.cpp'))
    def test_writer_compiled_in_main_target(self):
        with self.assertRaises(audit.LinkAuditError):
            audit.verify_vcxproj(VCXPROJ_OK.replace('mf_p0_windows.cpp', 'mf_p0_writer.cpp'))
    def test_writer_additional_compile_unit(self):
        mutant = VCXPROJ_OK.replace('</ItemGroup>', '<ClCompile Include="src\\mf_p0_writer.cpp" /></ItemGroup>')
        with self.assertRaises(audit.LinkAuditError):audit.verify_vcxproj(mutant)
    def test_writer_obj_link_input(self):
        with self.assertRaises(audit.LinkAuditError):
            audit.verify_vcxproj(VCXPROJ_OK.replace('kernel32.lib','mf_p0_writer.obj;kernel32.lib'))
    def test_writer_object_probe_link_input(self):
        with self.assertRaises(audit.LinkAuditError):
            audit.verify_vcxproj(VCXPROJ_OK.replace('kernel32.lib','mf_p0_writer_compile_probe;kernel32.lib'))
    def test_writer_project_reference_denied(self):
        mutant = VCXPROJ_OK.replace('</ItemGroup>',
            '<ProjectReference Include="mf_p0_writer_compile_probe.vcxproj" /></ItemGroup>')
        with self.assertRaises(audit.LinkAuditError):audit.verify_vcxproj(mutant)
    def test_compile_only_driver_calls_new_audit(self):
        ps = (ROOT/'tools/windows_compile_only.ps1').read_text(encoding='utf-8')
        self.assertIn('windows_off_binary_audit.ps1', ps)
        self.assertIn('Assert-CMakeOff', ps)
        auditor = (ROOT/'tools/windows_off_binary_audit.ps1').read_text(encoding='utf-8')
        self.assertIn("'/IMPORTS'", auditor)
        self.assertIn('Get-FileHash', auditor)
        self.assertIn('audit_windows_off_link.py', auditor)
        self.assertNotIn(' & $exe ', auditor)
    def test_media_libraries_denied(self):
        for lib in sorted(audit.PROHIBITED_LIBS):
            with self.subTest(lib=lib),self.assertRaises(audit.LinkAuditError):
                audit.verify_vcxproj(VCXPROJ_OK.replace('kernel32.lib',lib+';kernel32.lib'))
    def test_missing_files_denied_by_main(self):
        with tempfile.TemporaryDirectory() as td:
            self.assertEqual(2,self._run(td))
    def _run(self, tempdir):
        import subprocess, sys
        return subprocess.run([sys.executable,str(ROOT/'tools/audit_windows_off_link.py'),
            '--imports',str(Path(tempdir)/'none.txt'),'--vcxproj',str(Path(tempdir)/'none.vcxproj')],
            capture_output=True,text=True).returncode

if __name__=='__main__':unittest.main(verbosity=2)
