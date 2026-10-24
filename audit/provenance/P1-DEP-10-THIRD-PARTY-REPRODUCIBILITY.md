# P1-DEP-10 — Third-party dependency declaration gap

**Date:** 2026-10-24. **Status:** STATIC_REPRODUCED / DOCUMENTARY GAP.  
**Input:** exact v0.55 Integrated SourceOnly ZIP SHA-256 `3d3e8b721b440362019cb5c025a2a20d7f51ad816ae27f6de6d56181a9304105`.

## Static evidence

- Inspector `EngineYT_Darts_P1_Dependency_Inventory_2026-10-24.py`: SHA-256 `3704f2a9e16ae9708485ec234a764fa97e9cc2bcca75f97cb790c152e5823d08`.
- Results `EngineYT_Darts_P1_Dependency_Inventory_2026-10-24.json`: SHA-256 `b55926411e536420c0514a279ce32ee6277cdee45d552afa55a9f12e33d88e0d`.
- Scope: eight modules in the worker's static import closure plus `public_process_client_v055.py` (nine Python files).
- Direct third-party import observed: `cryptography`, used for Ed25519.
- Dependency declaration or lockfile matches in the integrated ZIP: **0** (searched requirements*.txt, pyproject.toml, Pipfile/Pipfile.lock, poetry.lock, uv.lock, setup.cfg, environment.yaml/yml, conda-lock.yaml/yml and SBOM-named files).
- `README.md:22` says Python 3.11+ with `cryptography` is required.
- `README.md:30` describes one historical Linux test environment: Python 3.13 test launcher and Python 3.11 worker with `cryptography 43.0.0`. This is **not** a declared locked dependency version.

## Consequence and proposed documentary remedy

This source-only ZIP does not by itself contain a complete reproducible dependency specification for the parent and child environments. That is a packaging/provenance gap, **not** evidence of an exploitable library vulnerability or that external environment specifications do not exist.

**Proposal, not applied:** maintain a reviewed environment record containing OS/build, Python executable paths and versions for parent/worker, `cryptography` version, hashes of installed distributions, installation source, and package resolution constraints. Retain this record separately from original immutable ZIPs. Do not install or execute dependencies while model M / Policy B gate is frozen.

**Unchanged:** E5B4D_NO-GO; SEC-02 Windows NOT_RUN; RENDER_NO-GO; PUBLISH_NO-GO; main unchanged.
