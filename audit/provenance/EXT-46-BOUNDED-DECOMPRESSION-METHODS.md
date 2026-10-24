# EXT-46 — Bounded decompression method allowlist

**2026-10-24 | SYNTHETIC_REPRODUCED | PASS_LIMITED | ISOLATED_CANDIDATE_NOT_APPLIED | DARTS_NOT_RUN**

## Falsifiable resource defect in EXT-45

EXT-45 checked ZIP-declared member size (2 MiB), aggregate size (32 MiB), ratio (100:1) and read chunks of 65,536 bytes, but allowed BZIP2 and LZMA. Python 3.13.5's `ZipExtFile._read1` invokes these decompressors without an output-length bound, **then truncates the decompressed result** to the declared uncompressed size.

Instrumented standalone stdlib synthetic ZIP test with a 1,048,576-byte payload and 65,536-byte read request:

| ZIP method | Caller receives | Largest internal decompressor return |
| --- | ---: | ---: |
| BZIP2 | 65,536 | **1,048,576** |
| LZMA | 65,536 | **1,048,576** |
| DEFLATE | 65,536 | **65,536** |

Two temporary v040 repacks contain a synthetic **1 MiB** BZIP2/LZMA member but declare only **131,072 bytes** in local/central headers. The ZIP CRC and embedded manifest SHA-256 bind only the 131,072-byte prefix; the outer ZIP SHA-256 is recomputed in a **synthetic** inventory. EXT-45 returns **PASS** with 98/98 member hashes for each, even though the underlying decompressor can allocate 1 MiB per call. This is not a SHA-256 collision or a change to the seven originals.

## EXT-46 isolated candidate

Reject ZIP member compression types other than **STORED (0) and DEFLATE (8)** before reading any member or manifest data. All **660/660 ZIP entries** in the seven original historical archives use DEFLATE; the 653 non-manifest member hashes remain unchanged.

| Run | Passed | Total |
| --- | ---: | ---: |
| EXT-45 with three additional tests | **52** | 54 |
| EXT-46 | **54** | 54 |
| EXT-46 `python -O` including subprocesses | **54** | 54 |
| Original seven ZIPs | **7/7 PASS_LIMITED** | **653/653 hashes** |

STORED synthetic repack remains accepted. This closes **only the reproduced BZIP2/LZMA unbounded-per-call decompression path**, not a formal worst-case resource guarantee.

## Evidence and gates

`EngineYT_Darts_EXT46_Bounded_Decompression_Evidence_20261024.zip` SHA-256 **`681ff6221ea94b628b0af4cfad3e46848b3b4520629aed6443d247231518c464`**, **12 members**, ZIP CRC and per-member SHA-256 PASS. Contains isolated candidate (SHA-256 `8bb22490265a64617323396c2eaa85d5a0e2f2f21955abe92ff3e6bf01058a44`), 54-case harness, independent decompressor output probe, inventory, pre-fix/normal/optimized/historical/differential results, review and manifest. Original ZIPs are not redistributed.

Open proof obligations: resource/ZIP preflight review issue #13; independently authenticated original anchors issue #12; Windows parity, OS-level memory and deadline guarantees. No Darts code imported or executed, no workers, project tests, main merge, render, publication or production integration.

**E5B4D_NO-GO; ACK-02 OPEN; SEC-02 Windows NOT_RUN; RENDER_NO-GO; PUBLISH_NO-GO.**