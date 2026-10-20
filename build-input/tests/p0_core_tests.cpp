// Emulate the pre-existing RGB macro in Windows.h before including p0_core.hpp.
// This macro must not rewrite any identifier declared by our header.
#define RGB(red, green, blue) 0x00AABBCCu
#include "p0_core.hpp"
#include <cassert>
#include <cstdlib>
#include <iostream>
#include <stdexcept>
#include <set>

static int checks=0;
void Must(bool value, const char* message) {
    ++checks;
    if(!value) { std::cerr << "FAIL: " << message << "\n"; std::exit(1); }
}
template<typename Fun> void MustThrow(Fun&& f) {
    ++checks;
    try { f(); } catch(const std::exception&) { return; }
    std::cerr << "FAIL: exception missing\n"; std::exit(1);
}
int main() {
    using namespace p0;
    for (auto frames: {24u,432u,480u}) {
        std::int64_t accumulated=0;
        Must(Tick(0,frames)==0,"initial time");
        for (std::uint32_t n=0; n<frames; ++n) {
            const auto d=Duration(n,frames);
            Must(d==416666 || d==416667,"quantized 24 fps duration");
            Must(d>0,"positive duration");
            Must(Tick(n+1,frames)>Tick(n,frames),"strict monotonicity");
            accumulated += d;
        }
        Must(accumulated==Tick(frames,frames),"no timing drift");
        Must(Tick(frames,frames)==static_cast<std::int64_t>(frames)*10'000'000/24,"correct endpoint");
        MustThrow([&]{ (void)Duration(frames,frames); });
        MustThrow([&]{ (void)Tick(frames+1,frames); });
    }
    MustThrow([]{ (void)Tick(0,23); });
    MustThrow([]{ (void)MakePattern(24); });
    auto f=MakePattern(0);
    Must(f.size()==static_cast<std::size_t>(W)*H,"frame size");
    Must(f[Offset(10,10)]==PackRgb32(245,25,25),"TL red");
    Must(f[Offset(W-10,10)]==PackRgb32(25,230,35),"TR green");
    Must(f[Offset(10,H-10)]==PackRgb32(25,50,235),"BL blue");
    Must(f[Offset(W-10,H-10)]==PackRgb32(235,222,24),"BR yellow");
    Must(Offset(0,0)==static_cast<std::size_t>(H-1)*W,"bottom-up row");
    Must(Offset(0,H-1)==0,"bottom row first");
    MustThrow([]{ (void)Offset(W,0); });
    MustThrow([]{ (void)Offset(0,H); });
    MustThrow([&]{ Rectangle(f,1,1,W+1,H,PackRgb32(1,2,3)); });
    Must(MakePattern(1)!=f,"moving frame differs");
    Must(MakePattern(1)!=MakePattern(2),"unique next frame");
    std::set<unsigned> visual_ids;
    for(std::uint32_t i=0;i<TEST_FRAMES;++i) {
        auto pattern=MakePattern(i);
        unsigned signature=0;
        for(std::uint32_t bit=0;bit<5;++bit)
            if(pattern[Offset(100+bit*114,755)]==PackRgb32(255,255,255))
                signature|=(1u<<bit);
        Must(signature==i,"frame identity visible as 5-bit diagnostic flags");
        visual_ids.insert(signature);
    }
    Must(visual_ids.size()==TEST_FRAMES,"all frame signatures distinct");
    std::cout << "PASS p0_core_tests " << checks << " checks; NO MEDIA EXECUTION\n";
}
