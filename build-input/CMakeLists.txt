cmake_minimum_required(VERSION 3.20)
project(EngineYT_Darts_MF_P0_Experimental LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
add_executable(p0_core_tests tests/p0_core_tests.cpp)
target_include_directories(p0_core_tests PRIVATE src)
add_executable(p0_gate_tests tests/p0_gate_tests.cpp)
target_include_directories(p0_gate_tests PRIVATE src)
enable_testing()
add_test(NAME source_math_and_pixel_pattern COMMAND p0_core_tests)
add_test(NAME compile_and_runtime_output_gates COMMAND p0_gate_tests)
option(ENGINEYT_ALLOW_NONPOLICY_MEDIA_OUTPUT
    "Compile a non-Policy-B experimental write path (requires separate authorization)" OFF)
if(WIN32 AND MSVC)
    # Compile SDK-specific code to OBJECT files, not an executable.
    # Default OFF builds DO NOT LINK these objects to any executable.
    add_library(mf_p0_writer_compile_probe OBJECT src/mf_p0_writer.cpp)
    target_include_directories(mf_p0_writer_compile_probe PRIVATE src)
    target_compile_options(mf_p0_writer_compile_probe PRIVATE /W4)
    add_executable(mf_p0_windows src/mf_p0_windows.cpp)
    target_include_directories(mf_p0_windows PRIVATE src)
    target_compile_options(mf_p0_windows PRIVATE /W4)
    if(ENGINEYT_ALLOW_NONPOLICY_MEDIA_OUTPUT)
        target_compile_definitions(mf_p0_windows PRIVATE ENGINEYT_ALLOW_NONPOLICY_MEDIA_OUTPUT=1)
        target_sources(mf_p0_windows PRIVATE $<TARGET_OBJECTS:mf_p0_writer_compile_probe>)
        target_link_libraries(mf_p0_windows PRIVATE mfreadwrite mfplat mfuuid ole32)
    else()
        target_compile_definitions(mf_p0_windows PRIVATE ENGINEYT_ALLOW_NONPOLICY_MEDIA_OUTPUT=0)
    endif()
    # Explicit, separate link-only probe, never part of the default ALL build.
    # Its entry point returns 2 and NEVER calls Media Foundation or any writer.
    # Force the RunExperimentalMedia symbol to stay in the link to validate
    # SDK/import-library resolution (avoid an optimized-away false PASS).
    add_executable(mf_p0_link_only_probe EXCLUDE_FROM_ALL
        tests/mf_p0_link_only_entry.cpp
        $<TARGET_OBJECTS:mf_p0_writer_compile_probe>)
    target_compile_options(mf_p0_link_only_probe PRIVATE /W4)
    target_link_options(mf_p0_link_only_probe PRIVATE "/INCLUDE:?RunExperimentalMedia@@YAHXZ")
    target_link_libraries(mf_p0_link_only_probe PRIVATE mfreadwrite mfplat mfuuid ole32)
else()
    message(STATUS "MF-P0 Windows targets NOT built on this platform; source tests only")
endif()
