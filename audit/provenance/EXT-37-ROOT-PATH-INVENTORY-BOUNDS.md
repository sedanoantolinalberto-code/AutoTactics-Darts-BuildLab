# EXT-37 — Full-path no-follow and bounded inventory reads

**Date:** 2026-10-24. **Status:** PASS_LIMITED / CANDIDATE_NOT_APPLIED / DARTS_NOT_RUN.

## Independently reproduced EXT-36 gaps

1. EXT-36 opened the **root directory** with `O_DIRECTORY | O_NOFOLLOW`, but that protects only its final path component. A synthetic path `temp/link/data` with intermediate symlink `link -> /mnt` was **accepted by EXT-36**, verifying 7/7 archives and 653/653 member hashes. The EXT-37 candidate rejects the same path.
2. EXT-36 read the entire untrusted inventory via `Path.read_bytes()` before enforcing `MAX_MANIFEST = 512 KiB`. Instrumentation observed **1,048,576 bytes** read before rejection for a 1 MiB synthetic inventory. EXT-37 checks `fstat` first and reads at most **524,289 bytes**.
3. EXT-36 accepted inventory paths through **final or intermediate symlinks**. EXT-37 rejects both.

## Isolated candidate and regression

The candidate walks **every root path component** through directory descriptors using `O_DIRECTORY | O_NOFOLLOW`, rejects `..` traversal, opens inventory as a regular nonblocking no-follow file relative to a separately verified directory descriptor, and uses a bounded inventory read. It preserves the EXT-35 immutable-byte ZIP snapshot.

**Observed:** historical original ZIPs 7/7 PASS_LIMITED, 653/653 member hashes matched. Intermediate root symlink: EXT-36 PASS, EXT-37 FAIL. Intermediate inventory symlink: EXT-36 PASS, EXT-37 FAIL. Final inventory symlink: EXT-36 PASS, EXT-37 FAIL. Oversize inventory: EXT-36 allocated/read 1 MiB before reject; EXT-37 FAIL with bounded read. Inventory FIFO and `..` root: EXT-37 FAIL. Normal regular-file baseline: EXT-37 PASS_LIMITED.

**Package:** `EngineYT_Darts_EXT37_Root_Path_Inventory_Bounds_20261024.zip`, SHA-256 `d3db5f27aacdeb4e8d75b23275b3011ab09646dfe1046ea6ad6373b89dbe9689`, 6 members, ZIP CRC + SHA-256 manifest PASS. Contains verifier candidate, adversarial harness, original inventory, JSON results, review, package manifest. AST parse PASS.

## Limitations and gates

POSIX-specific; Windows NOT_TESTED / fail closed. Not an OS sandbox or atomic filesystem snapshot during capture. No independently authenticated inventory anchors or chain of custody. No proof of process termination under arbitrary suspension model M. No project modules imported/executed, no Darts workers, no renders, no publication, no main merge.

**E5B4D_NO-GO; ACK-02 OPEN; SEC-02 Windows NOT_RUN; RENDER_NO-GO; PUBLISH_NO-GO.** Candidate NOT_APPLIED.