// S34 v0.25 — explicit linker probe, no execution authorization.
// This executable is never invoked by the pipeline. Its entry point cannot
// call the media writer, even if it is launched outside the test procedure.
#if !defined(_WIN32) || !defined(_MSC_VER)
#error "Windows MSVC link probe only"
#endif
int wmain() noexcept { return 2; }
