"""Portable negative tests for compile-only scripts; no Windows/media execution."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

SOURCE=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('verify_compile_plan',SOURCE/'tools/verify_compile_plan.py')
v=importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)

class CompileOnlyPlanTests(unittest.TestCase):
    def test_source_guard(self):self.assertEqual([],v.review_source())
    def test_cache_off_only(self):
        v.verify_cache_text('ENGINEYT_ALLOW_NONPOLICY_MEDIA_OUTPUT:BOOL=OFF\n')
    def test_cache_fails_on(self):
        with self.assertRaises(v.ReviewError):v.verify_cache_text('ENGINEYT_ALLOW_NONPOLICY_MEDIA_OUTPUT:BOOL=ON\n')
    def test_cache_fails_missing(self):
        with self.assertRaises(v.ReviewError):v.verify_cache_text('A:BOOL=OFF\n')
    def test_cache_fails_duplicate(self):
        with self.assertRaises(v.ReviewError):v.verify_cache_text('ENGINEYT_ALLOW_NONPOLICY_MEDIA_OUTPUT:BOOL=OFF\nENGINEYT_ALLOW_NONPOLICY_MEDIA_OUTPUT:BOOL=OFF\n')
    def test_cache_fails_alternate(self):
        for x in ('FALSE','0','OFF # override','off','ON',''):
            with self.subTest(x=x), self.assertRaises(v.ReviewError):
                v.verify_cache_text(f'ENGINEYT_ALLOW_NONPOLICY_MEDIA_OUTPUT:BOOL={x}\n')
    def test_cache_crlf(self):
        v.verify_cache_text('A=2\r\nENGINEYT_ALLOW_NONPOLICY_MEDIA_OUTPUT:BOOL=OFF\r\n')
    def test_source_broken_default(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)
            for name in ('CMakeLists.txt','src/mf_p0_windows.cpp','src/mf_p0_writer.cpp','tools/windows_compile_only.ps1','tests/test_static_review.py'):
                dst=p/name; dst.parent.mkdir(parents=True,exist_ok=True); dst.write_bytes((SOURCE/name).read_bytes())
            c=p/'CMakeLists.txt';c.write_text(c.read_text().replace('" OFF)','" ON)'),encoding='utf-8')
            self.assertIn('CMake default not OFF',v.review_source(p))
    def test_script_requires_flag(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)
            for name in ('CMakeLists.txt','src/mf_p0_windows.cpp','src/mf_p0_writer.cpp','tools/windows_compile_only.ps1','tests/test_static_review.py'):
                dst=p/name; dst.parent.mkdir(parents=True,exist_ok=True); dst.write_bytes((SOURCE/name).read_bytes())
            ps=p/'tools/windows_compile_only.ps1'; ps.write_text(ps.read_text().replace('ENGINEYT_ALLOW_NONPOLICY_MEDIA_OUTPUT:BOOL=OFF','ENGINEYT_ALLOW_NONPOLICY_MEDIA_OUTPUT:BOOL=ON'))
            self.assertIn('PowerShell does not enforce OFF',v.review_source(p))
    def _mutate(self, replacement_file, old, new):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)
            for name in ('CMakeLists.txt','src/mf_p0_windows.cpp','src/mf_p0_writer.cpp',
                         'tools/windows_compile_only.ps1'):
                dst=p/name
                dst.parent.mkdir(parents=True,exist_ok=True)
                dst.write_bytes((SOURCE/name).read_bytes())
            target=p/replacement_file
            before=target.read_text(encoding='utf-8')
            self.assertIn(old,before)
            target.write_text(before.replace(old,new,1),encoding='utf-8')
            return v.review_source(p)

    def test_missing_object_probe_rejected(self):
        errors=self._mutate('CMakeLists.txt',
            'add_library(mf_p0_writer_compile_probe OBJECT src/mf_p0_writer.cpp)',
            'add_library(mf_p0_writer_compile_probe OBJECT src/mf_p0_windows.cpp)')
        self.assertIn('Object-only SDK probe absent',errors)

    def test_unconditional_writer_link_rejected(self):
        errors=self._mutate('CMakeLists.txt',
            'if(ENGINEYT_ALLOW_NONPOLICY_MEDIA_OUTPUT)', 'if(TRUE)')
        self.assertIn('Ambiguous experimental CMake gate',errors)

    def test_off_compile_definition_removed_rejected(self):
        errors=self._mutate('CMakeLists.txt',
            'ENGINEYT_ALLOW_NONPOLICY_MEDIA_OUTPUT=0)',
            'ENGINEYT_ALLOW_NONPOLICY_MEDIA_OUTPUT=1)')
        self.assertIn('OFF branch unexpectedly links media code',errors)

    def test_media_api_in_main_rejected(self):
        errors=self._mutate('src/mf_p0_windows.cpp',
            '#include <iostream>', '#include <iostream>\n// OpenSink( forbidden in executable')
        self.assertIn('Main executable contains writer API',errors)

    def test_off_branch_calls_writer_rejected(self):
        errors=self._mutate('src/mf_p0_windows.cpp',
            '    return 2;\n#else',
            '    return RunExperimentalMedia();\n#else')
        self.assertIn('OFF executable reaches writer',errors)

    def test_script_requires_explicit_object_probe(self):
        errors=self._mutate('tools/windows_compile_only.ps1',
            "'mf_p0_writer_compile_probe'", "'wrong_target'")
        self.assertIn('PowerShell does not explicitly build SDK probe', errors)

    def test_manifest_integrity(self):
        n,m=v.verify_manifest(SOURCE)
        self.assertEqual(n,m)
        self.assertGreater(n,10)

if __name__=='__main__':unittest.main(verbosity=2)
