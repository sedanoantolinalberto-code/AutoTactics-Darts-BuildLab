"""Conservative static QA; no rendering and no full security proof."""
import pathlib
import ast
import re
import unittest

BASE = pathlib.Path(__file__).resolve().parents[1]
CPP = (BASE / 'src/mf_p0_windows.cpp').read_text(encoding='utf-8')
WRITER = (BASE / 'src/mf_p0_writer.cpp').read_text(encoding='utf-8')
CORE = (BASE / 'src/p0_core.hpp').read_text(encoding='utf-8')
GATE = (BASE / 'src/p0_gate.hpp').read_text(encoding='utf-8')
CMAKE = (BASE / 'CMakeLists.txt').read_text(encoding='utf-8')

class Review(unittest.TestCase):
    def test_cmake_defaults_media_output_off(self):
        self.assertRegex(CMAKE, r'option\(ENGINEYT_ALLOW_NONPOLICY_MEDIA_OUTPUT\s+"[^"]+" OFF\)')

    def test_cmake_does_not_build_windows_target_on_linux(self):
        self.assertIn('if(WIN32 AND MSVC)', CMAKE)
        self.assertIn('target_compile_definitions(mf_p0_windows PRIVATE ENGINEYT_ALLOW_NONPOLICY_MEDIA_OUTPUT=0)', CMAKE)
        self.assertIn('target_compile_definitions(mf_p0_windows PRIVATE ENGINEYT_ALLOW_NONPOLICY_MEDIA_OUTPUT=1)', CMAKE)

    def test_executable_off_does_not_include_media_writer(self):
        main = CPP.split('int wmain(', 1)[1]
        before, enabled = main.split('#if ENGINEYT_ALLOW_NONPOLICY_MEDIA_OUTPUT == 0', 1)[1].split('#else', 1)
        self.assertIn('return 2;', before)
        self.assertNotIn('RunExperimentalMedia(', before)
        self.assertIn('return RunExperimentalMedia();', enabled)
        for forbidden in ('MFCreateSinkWriterFromURL','OpenSink(', 'SendFrame(',
                          'WriteSample(', 'Finalize()', 'fs::create_directory('):
            self.assertNotIn(forbidden, CPP)

    def test_sdk_writer_object_separate_and_conditional_link(self):
        self.assertIn('add_library(mf_p0_writer_compile_probe OBJECT src/mf_p0_writer.cpp)', CMAKE)
        self.assertIn('if(ENGINEYT_ALLOW_NONPOLICY_MEDIA_OUTPUT)', CMAKE)
        gated = CMAKE.split('if(ENGINEYT_ALLOW_NONPOLICY_MEDIA_OUTPUT)', 1)[1]
        on = gated.split('else()',1)[0]
        off = gated.split('else()',1)[1].split('endif()',1)[0]
        self.assertIn('target_sources(mf_p0_windows PRIVATE $<TARGET_OBJECTS:mf_p0_writer_compile_probe>)',on)
        self.assertIn('target_link_libraries(mf_p0_windows PRIVATE mfreadwrite mfplat mfuuid ole32)',on)
        self.assertNotIn('target_sources(mf_p0_windows PRIVATE $<TARGET_OBJECTS:mf_p0_writer_compile_probe>)',off)
        self.assertIn('ENGINEYT_ALLOW_NONPOLICY_MEDIA_OUTPUT=0',off)


    def test_no_runtime_write_without_exact_flags(self):
        main = CPP.split('int wmain(', 1)[1]
        self.assertIn('p0::gate::Evaluate(true, argc, first, second)', main)
        self.assertIn('p0::gate::Decision::ExperimentalRequest', main)
        self.assertTrue(main.index('p0::gate::Evaluate(') < main.index('return RunExperimentalMedia();'))
        self.assertIn('L"--experimental-write-p0"', GATE)
        self.assertIn('L"--ack-non-policy-b"', GATE)

    def test_invalid_macro_value_causes_compile_error(self):
        self.assertIn('#if ENGINEYT_ALLOW_NONPOLICY_MEDIA_OUTPUT != 0 && ENGINEYT_ALLOW_NONPOLICY_MEDIA_OUTPUT != 1', CPP)
        self.assertIn('#error "ENGINEYT_ALLOW_NONPOLICY_MEDIA_OUTPUT must be 0 or 1"', CPP)

    def test_writer_calls_in_intended_order(self):
        order = ['writer->AddStream(', 'writer->SetInputMediaType(', 'writer->BeginWriting()',
                 'writer->WriteSample(', 'writer.writer->Finalize()']
        locations = [WRITER.index(item) for item in order]
        self.assertEqual(sorted(locations), locations)

    def test_no_subprocess_launch_api_detected(self):
        for pattern in (r'\bCreateProcess[AW]?\s*\(',r'\bShellExecute(?:Ex)?[AW]?\s*\(',
                        r'\bsystem\s*\(',r'\bpopen\s*\(',r'\bWinExec\s*\('):
            self.assertIsNone(re.search(pattern, CPP + WRITER))

    def test_no_automatic_publish(self):
        for forbidden in ('MoveFile(', 'DeleteFile(', 'fs::rename(', 'github', 'youtube upload'):
            self.assertNotIn(forbidden, CPP + WRITER)
        self.assertIn('MF-P0_UNVERIFIED_EXPERIMENT.mp4', WRITER)

    def test_no_game_contract_coupling(self):
        self.assertNotIn('#include "render_', CPP + WRITER)
        self.assertNotIn('darts_sprint31_safehud', CPP + WRITER)
        self.assertIn('TEST_FRAMES = 24', CORE)

    def test_core_timestamps_exact(self):
        self.assertIn('TICKS_PER_SECOND = 10\'000\'000ULL', CORE)
        self.assertIn('num + FPS / 2', CORE)
        self.assertIn('Tick(n + 1, frame_limit) - Tick(n, frame_limit)', CORE)

    def test_output_path_guard_is_only_precaution(self):
        self.assertIn('if (fs::is_symlink(outputDir))', WRITER)
        self.assertIn('if (fs::exists(outputFile))', WRITER)
        # A filesystem path check does NOT establish exclusive access / prevent TOCTOU.

    def test_no_media_execution_during_python_tests(self):
        tree = ast.parse(pathlib.Path(__file__).read_text(encoding='utf-8'))
        imported = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module)
        self.assertNotIn('subprocess', imported)
        self.assertNotIn('os', imported)

if __name__ == '__main__':
    unittest.main(verbosity=2)
