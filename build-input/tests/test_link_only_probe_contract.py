"""Pure static review of S34 v0.25: no media execution or Windows simulation."""
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
CMAKE=(ROOT/'CMakeLists.txt').read_text(encoding='utf-8')
ENTRY=(ROOT/'tests/mf_p0_link_only_entry.cpp').read_text(encoding='utf-8')
OFF=(ROOT/'tools/windows_compile_only.ps1').read_text(encoding='utf-8')
LINK=(ROOT/'tools/windows_link_only_probe.ps1').read_text(encoding='utf-8')

class LinkOnlyContract(unittest.TestCase):
    def test_separate_excluded_target(self):
        self.assertIn('add_executable(mf_p0_link_only_probe EXCLUDE_FROM_ALL', CMAKE)
        self.assertNotIn('add_test(NAME mf_p0_link_only_probe', CMAKE)
    def test_object_forced_symbol_resolution(self):
        self.assertIn('$<TARGET_OBJECTS:mf_p0_writer_compile_probe>', CMAKE)
        self.assertIn('target_link_options(mf_p0_link_only_probe PRIVATE "/INCLUDE:?RunExperimentalMedia@@YAHXZ")', CMAKE)
        self.assertIn('target_link_libraries(mf_p0_link_only_probe PRIVATE mfreadwrite mfplat mfuuid ole32)', CMAKE)
    def test_link_entry_does_not_call_writer(self):
        self.assertIn('int wmain() noexcept { return 2; }', ENTRY)
        for prohibited in ('RunExperimentalMedia(', 'MFCreate', 'WriteSample(', 'OpenSink(', 'std::system(', 'CreateProcess('):
            self.assertNotIn(prohibited, ENTRY)
    def test_default_off_executable_remains_separate(self):
        self.assertIn('target_compile_definitions(mf_p0_windows PRIVATE ENGINEYT_ALLOW_NONPOLICY_MEDIA_OUTPUT=0)', CMAKE)
        off = CMAKE.split('if(ENGINEYT_ALLOW_NONPOLICY_MEDIA_OUTPUT)',1)[1].split('else()',1)[1].split('endif()',1)[0]
        self.assertNotIn('mf_p0_writer_compile_probe', off)
    def test_link_runs_after_off_import_audit(self):
        self.assertLess(OFF.index("'tools/windows_off_binary_audit.ps1'"),OFF.index("'tools/windows_link_only_probe.ps1'"))
    def test_build_target_not_executable_invocation(self):
        self.assertIn("'--target' 'mf_p0_link_only_probe'", LINK)
        self.assertNotIn('& $exe', LINK)
        self.assertNotIn('Start-Process', LINK)
        self.assertNotIn('Invoke-Expression', LINK)
    def test_requires_off_cache(self):
        self.assertIn("'--cache' $cache", LINK)
        self.assertIn('if ($LASTEXITCODE -ne 0)', LINK)
    def test_forced_symbol_import_audited(self):
        self.assertIn("'/IMPORTS' $exe", LINK)
        self.assertIn('MFCreateSinkWriterFromURL', LINK)
        self.assertIn('mfreadwrite',LINK.lower())
        self.assertIn('Get-FileHash',LINK)
    def test_no_media_executable_in_ctest(self):
        self.assertIn("'^(source_math_and_pixel_pattern|compile_and_runtime_output_gates)$'", OFF)
        self.assertNotIn('mf_p0_link_only_probe.exe', OFF)
    def test_ci_collector_captures_both_import_tables(self):
        collector=(ROOT.parent/'ci/collect.ps1').read_text(encoding='utf-8')
        self.assertIn('MF_P0_OFF_IMPORTS_dumpbin.txt',collector)
        self.assertIn('MF_P0_LINK_IMPORTS_dumpbin.txt',collector)
        self.assertIn('mf_p0_link_only_probe.vcxproj',collector)
        self.assertNotIn('Start-Process',collector)
    def test_writer_not_executed_by_link_probe(self):
        self.assertNotIn('RunExperimentalMedia();',LINK)
        self.assertNotIn('mf_p0_link_only_probe.exe ',LINK)
if __name__=='__main__':unittest.main()
