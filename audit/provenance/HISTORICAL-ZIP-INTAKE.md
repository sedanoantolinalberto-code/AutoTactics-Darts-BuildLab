# P1 — Historical ZIP intake and evidence promotion rules

**Status:** documentary protocol, not proof that the 25 reported ZIPs have been independently reprocessed in this repository.

## Why this exists

A ZIP can be byte-identical to a reference hash yet be unrelated to Git commit ancestry. Nested files can establish containment, but not authorship, release authorization, or independent test execution. We preserve all three relationships separately:

1. **Package identity:** exact bytes of a specific ZIP, size, SHA-256, source, acquisition date.
2. **Package containment:** member paths and SHA-256 values, including nested baselines; verify every claimed pair of bytes.
3. **Git provenance:** repo/ref/commit/tree/blob; only claim when fetched from GitHub and compared with the corresponding content.

## Intake record per ZIP (required fields)

```json
{
  "artifact_id": "UNASSIGNED",
  "filename": null,
  "source_kind": null,
  "source_reference": null,
  "acquired_date": null,
  "size_bytes": null,
  "sha256": null,
  "zip_crc_check": "NOT_RUN",
  "entries": null,
  "manifest_schema": null,
  "manifest_validation": "NOT_RUN",
  "duplicate_paths": "NOT_RUN",
  "casefold_collisions": "NOT_RUN",
  "unsafe_paths": "NOT_RUN",
  "symlinks": "NOT_RUN",
  "content_sensitive_review": "NOT_RUN",
  "git_commit_evidence": null,
  "classification": "UNVERIFIED_INTAKE",
  "raw_log_reference": null
}
```

Do not use an artifact ID derived solely from version numbers if two variants share the same version.

## Review gates before uploading any historical ZIP

- Verify the local file bytes, not only the package title.
- Review members for secrets, personal data, source licensing restrictions and embedded binaries.
- Preserve original package unchanged; use hashes and references in Git by default, not wholesale ZIP uploads.
- Store machine-readable test output separately from the test script and tool version.
- Confirm nested manifest root semantics before claiming PASS.
- Mark CRC, manifest checks, and line-by-line inclusion comparisons as `DOCUMENTARY_REPORTED` until independently re-run with retained inputs and logs.

## Known external anchors from owner terminal

| Artifact | Bytes | SHA-256 | Class |
|---|---:|---|---|
| v0.55 Integrated SourceOnly | 171747 | `3d3e8b721b440362019cb5c025a2a20d7f51ad816ae27f6de6d56181a9304105` | OBSERVED_OWNER_TERMINAL |
| v0.55 ReviewOnly | 3351 | `feb35c690e126428642f306c67feec5ed879438085369ccd3d0b1fc63816e795` | OBSERVED_OWNER_TERMINAL |

Earlier documentary reports assert 25 S34 ZIPs, 98 manifests, 4605 member references, and byte-identical nested baselines from v0.49 through v0.55. These are **not** promoted by this document.

## Conditions for marking P1 complete

- Each ZIP has its own intake record and independent hash evidence.
- Every claimed containment edge references both exact member paths and computed hashes.
- All historical manifest variants have explicit interpretation, including v0.35 and v0.48.
- No Git ancestry claim is inferred from package nesting.
- Independent reviewer can reproduce each check using retained inputs and raw logs.
- Main remains unchanged unless a separate human gate explicitly authorizes a merge.

**No-GO gates remain in force:** E5B4D, render, publication.
