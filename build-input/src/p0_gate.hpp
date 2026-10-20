#pragma once
// Pure decision logic for an *experimental* source candidate.
// An allow result NEVER proves or overrides E5B4D / Policy B constraints.
#include <string_view>
namespace p0::gate {
enum class Decision {
    CompileDisabled,
    RuntimeDenied,
    ExperimentalRequest
};
constexpr Decision Evaluate(bool compiled_output_enabled,
                            int argc,
                            std::wstring_view first,
                            std::wstring_view second) noexcept {
    if (!compiled_output_enabled) return Decision::CompileDisabled;
    if (argc != 3 || first != L"--experimental-write-p0" ||
        second != L"--ack-non-policy-b") return Decision::RuntimeDenied;
    return Decision::ExperimentalRequest;
}
} // namespace p0::gate
