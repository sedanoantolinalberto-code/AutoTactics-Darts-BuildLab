#pragma once
// Engine YT Darts Stories S34 v0.16 — MF-P0 synthetic source only.
// No sports contracts, no source S31 renderer, no FFmpeg and no process execution.
#include <array>
#include <cstdint>
#include <limits>
#include <stdexcept>
#include <vector>

namespace p0 {
constexpr std::uint32_t W = 720;
constexpr std::uint32_t H = 1280;
constexpr std::uint32_t FPS = 24;
constexpr std::uint64_t TICKS_PER_SECOND = 10'000'000ULL;
constexpr std::uint32_t TEST_FRAMES = 24;

// Only 0 <= n <= 480 is supported by the frozen series fixtures.
inline std::int64_t Tick(std::uint32_t n, std::uint32_t frame_limit) {
    if (frame_limit != TEST_FRAMES && frame_limit != 432 && frame_limit != 480)
        throw std::invalid_argument("unsupported frame limit");
    if (n > frame_limit) throw std::out_of_range("timestamp outside episode");
    const auto num = static_cast<std::uint64_t>(n) * TICKS_PER_SECOND;
    return static_cast<std::int64_t>((num + FPS / 2) / FPS);
}
inline std::int64_t Duration(std::uint32_t n, std::uint32_t frame_limit) {
    if (n >= frame_limit) throw std::out_of_range("sample index outside episode");
    return Tick(n + 1, frame_limit) - Tick(n, frame_limit);
}

inline constexpr std::uint32_t PackRgb32(std::uint8_t r, std::uint8_t g, std::uint8_t b) {
    // DWORD memory layout on little-endian Windows: B,G,R,0.
    return (std::uint32_t(r) << 16) | (std::uint32_t(g) << 8) | b;
}
// RGB32 DIB pixels stored in memory bottom-up, explicitly checked in tests.
inline std::size_t Offset(std::uint32_t x, std::uint32_t visual_y) {
    if (x >= W || visual_y >= H) throw std::out_of_range("pixel coordinate");
    return static_cast<std::size_t>(H - 1 - visual_y) * W + x;
}
using Frame = std::vector<std::uint32_t>;
inline void Rectangle(Frame& pixels, std::uint32_t x0, std::uint32_t y0,
                      std::uint32_t x1, std::uint32_t y1, std::uint32_t rgb) {
    if (x0 > x1 || y0 > y1 || x1 > W || y1 > H)
        throw std::out_of_range("rectangle coordinate");
    for (std::uint32_t y=y0; y<y1; ++y)
        for (std::uint32_t x=x0; x<x1; ++x)
            pixels[Offset(x,y)] = rgb;
}
inline Frame MakePattern(std::uint32_t index) {
    if (index >= TEST_FRAMES) throw std::out_of_range("P0 index");
    Frame f(static_cast<std::size_t>(W)*H, PackRgb32(22,22,29));
    constexpr std::uint32_t block = 140;
    Rectangle(f, 0,0,block,block, PackRgb32(245,25,25));          // TL red
    Rectangle(f, W-block,0,W,block, PackRgb32(25,230,35));       // TR green
    Rectangle(f, 0,H-block,block,H, PackRgb32(25,50,235));       // BL blue
    Rectangle(f, W-block,H-block,W,H, PackRgb32(235,222,24));   // BR yellow
    Rectangle(f, 0, H/3, W, H/3+9, PackRgb32(255,255,255));   // asymmetric horizontal guide
    Rectangle(f, W/2,0,W/2+9,H, PackRgb32(200,40,210));      // vertical guide
    // 24 distinctive synthetic frames: clear white motion block and 5-bit index flags.
    const auto x0 = std::uint32_t(60 + index * 22);
    Rectangle(f, x0, 480, x0+35, 540, PackRgb32(246,246,246));
    for (std::uint32_t bit=0; bit<5; ++bit) {
        const bool on = (index & (1u<<bit)) != 0;
        Rectangle(f, 70 + bit*114, 730, 140 + bit*114, 840,
                  on ? PackRgb32(255,255,255) : PackRgb32(65,65,65));
    }
    return f;
}
}  // namespace p0
