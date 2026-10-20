#include "p0_gate.hpp"
#include <cstdlib>
#include <iostream>
#include <string_view>
using p0::gate::Decision;
static unsigned checks = 0;
static void Require(bool condition, const char* why) {
    ++checks;
    if (!condition) {
        std::cerr << "FAIL: " << why << "\n";
        std::exit(1);
    }
}
int main() {
    constexpr auto flag1 = L"--experimental-write-p0";
    constexpr auto flag2 = L"--ack-non-policy-b";
    const std::wstring_view a[] = {L"", flag1, flag2, L"--EXPERIMENTAL-WRITE-P0",
                                   L"--experimental-write-p0 ", L"--ack-non-policy-b ",
                                   L"--unknown", L"--experimental-write-p0--ack-non-policy-b"};
    for (bool enabled : {false, true}) {
        for (int argc = 0; argc <= 6; ++argc) {
            for (auto first : a) {
                for (auto second : a) {
                    const auto result = p0::gate::Evaluate(enabled, argc, first, second);
                    const bool exact = enabled && argc == 3 && first == flag1 && second == flag2;
                    Require((result == Decision::ExperimentalRequest) == exact, "exact flags only");
                    Require((result == Decision::CompileDisabled) == !enabled, "compile OFF wins");
                    Require((result == Decision::RuntimeDenied) ==
                                (enabled && !exact), "runtime deny exhaustive");
                }
            }
        }
    }
    static_assert(p0::gate::Evaluate(false, 3, flag1, flag2) == Decision::CompileDisabled);
    static_assert(p0::gate::Evaluate(true, 3, flag1, flag2) == Decision::ExperimentalRequest);
    static_assert(p0::gate::Evaluate(true, 3, flag2, flag1) == Decision::RuntimeDenied);
    std::cout << "PASS " << checks << " portable gate assertions; no media execution\n";
}
