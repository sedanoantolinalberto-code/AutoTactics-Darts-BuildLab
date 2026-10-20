// Engine YT / AutoTactics S34 v0.19. Windows executable entry only.
// OFF builds do not link the Media Foundation writer object.
// This is not a Policy B/E5B4D-compliant execution system.
#include <iostream>
#include <string_view>
#include "p0_gate.hpp"
#ifndef ENGINEYT_ALLOW_NONPOLICY_MEDIA_OUTPUT
#error "Explicitly define ENGINEYT_ALLOW_NONPOLICY_MEDIA_OUTPUT as 0 or 1"
#endif
#if ENGINEYT_ALLOW_NONPOLICY_MEDIA_OUTPUT != 0 && ENGINEYT_ALLOW_NONPOLICY_MEDIA_OUTPUT != 1
#error "ENGINEYT_ALLOW_NONPOLICY_MEDIA_OUTPUT must be 0 or 1"
#endif
#if ENGINEYT_ALLOW_NONPOLICY_MEDIA_OUTPUT == 1
// Only defined and linked in an explicitly enabled experimental build.
int RunExperimentalMedia();
#endif
int wmain(int argc, wchar_t** argv) {
#if ENGINEYT_ALLOW_NONPOLICY_MEDIA_OUTPUT == 0
    (void)argc;
    (void)argv;
    std::wcout << L"MF-P0 MEDIA WRITER NOT LINKED (default OFF).\n"
               << L"Windows SDK source probe may compile, but cannot be run by this binary.\n";
    return 2;
#else
    const auto first = (argc > 1 && argv[1] != nullptr)
        ? std::wstring_view(argv[1]) : std::wstring_view{};
    const auto second = (argc > 2 && argv[2] != nullptr)
        ? std::wstring_view(argv[2]) : std::wstring_view{};
    if (p0::gate::Evaluate(true, argc, first, second) !=
        p0::gate::Decision::ExperimentalRequest) {
        std::wcout << L"MF-P0 SOURCE EXPERIMENT ONLY. Default: NO MEDIA WRITE.\n"
                   << L"No E5B4D Policy B execution authorization is implied.\n"
                   << L"An independently authorized isolated fault model is required.\n";
        return 2;
    }
    return RunExperimentalMedia();
#endif
}
