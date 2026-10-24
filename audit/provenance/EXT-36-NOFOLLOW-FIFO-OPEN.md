# EXT-36 — No-follow archive opening and FIFO nonblocking guard

**Date:** 2026-10-24. **Status:** SYNTHETIC_DIFFERENTIAL_REPRODUCED / PASS_LIMITED / CANDIDATE_NOT_APPLIED. **Darts runtime:** NOT_RUN.

## Verified new defect

EXT-35 checks `path.is_file()` and then uses `path.open('rb')`. Both follow symlinks. Seven synthetic directory entries linking **outside the nominated root** to the seven genuine immutable historical ZIPs returned `PASS_LIMITED` (653 members) under EXT-35. This means a path policy can be bypassed even though the hash/content validation succeeds; it does not imply digest forgery.

## Isolated EXT-36 candidate and observations

The standalone candidate opens the root directory with `os.O_DIRECTORY | os.O_NOFOLLOW`, opens each basename via `os.open(..., dir_fd=root_fd, O_NOFOLLOW | O_NONBLOCK)`, and requires `stat.S_ISREG(os.fstat(fd).st_mode)` before bounded capture. The same immutable bytes are hashed and parsed. Platforms lacking the necessary POSIX primitives fail closed.

- Seven genuine historical ZIPs: **7/7 PASS_LIMITED**, **653/653** member hashes matched.
- Seven normal copied ZIPs: **7/7 PASS_LIMITED**, **653/653** member hashes matched.
- Seven external symbolic links: **EXT-35 PASS_LIMITED**, **EXT-36 FAIL 7/7**.
- Root directory symlink: **EXT-36 FAIL 7/7**.
- FIFO substituted for first expected ZIP: **EXT-36 FAIL** with `ARCHIVE_NOT_REGULAR`; process exit 2 within an 8-second synthetic guard. `O_NONBLOCK` prevents opening a FIFO from hanging before `fstat`.
- AST parse PASS; package CRC and SHA-256 member checks PASS.
- No Darts code imported/executed, no project tests, workers, renders or publication.

## Evidence package

`EngineYT_Darts_EXT36_Nofollow_Safety_Evidence_20261024.zip` SHA-256 `908dc538971ab09f1cdad7b485c37f3a3d9b2535870105c003bf4aa2c7698aec`. Five files: isolated candidate, inventory, results JSON, technical review, SHA-256 manifest.

## Limits and gates

This is **not** a cross-platform security guarantee. Windows and platforms without `dir_fd` / `O_NOFOLLOW` are unsupported (fail closed), not tested. Intermediate root path components may be symlinks. Descriptor-based final-component protection is not an OS sandbox; same-inode concurrent writes during byte capture are not atomically snapshotted. SHA-256 anchors remain untrusted without external attestation.

**E5B4D_NO-GO, ACK-02 OPEN, SEC-02 Windows NOT_RUN, RENDER_NO-GO, PUBLISH_NO-GO.** Candidate NOT_APPLIED, no main merge.
