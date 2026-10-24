# ACK-24 — Static audit of reader thread ownership

Date: 2026-10-24. Status: STATIC_AST_PASS / NOT_RUN / NO_PATCH.

## Direct source observations

Read-only AST inspection of the original v0.55 client and the unapplied ACK22 and ACK23 proposals found the same lifecycle pattern in all three versions:

| Source | Daemon reader threads | start calls | join calls | stderr reader completion signals | stdout reader completion signals |
|---|---:|---:|---:|---:|---:|
| v0.55 original | 2 | 2 | 0 | 0 | 1 |
| ACK22 proposed | 2 | 2 | 0 | 0 | 1 |
| ACK23 proposed | 2 | 2 | 0 | 0 | 1 |

In the original source, reader thread constructors and starts are on lines 71-72, the stdout completion event is set on line 62, and stderr reads on line 66 without a matching completion event. Parent wait calls are on lines 145 and 157. No thread join call appears in the PublicChild class.

## Six audit findings

- ACK24-THREAD-01: process wait does not prove reader thread completion.
- ACK24-THREAD-02: stderr reader completion is not explicitly observed.
- ACK24-THREAD-03: reader threads and parent share stream handles without a documented close/read ownership handoff.
- ACK24-THREAD-04: MAX_WIRE, queue maxsize 2 and stderr retention cap 65536 do not bound lifetime bytes emitted and accepted.
- ACK24-THREAD-05: stdin write/flush precedes the start of the read deadline; there is no independent write/flush deadline.
- ACK24-THREAD-06: ACK23 local stream.closed checks do not establish reader completion.

These are static control-flow observations, not runtime reproductions.

## Evidence artifacts

Original ZIP SHA-256: 3d3e8b721b440362019cb5c025a2a20d7f51ad816ae27f6de6d56181a9304105.

ACK23 candidate SHA-256: 4a730ce0d2fb9e1bdd383f22aa5544265521bed2bedffb82ecf7f03f30e65a7e.

Evidence package EngineYT_Darts_ACK24_Thread_Lifecycle_Evidence_20261024.zip SHA-256: f008dec96946a66fbf3b7f3aca0269cabd69f8a881fc78b65f655d29032c6dc9.

Package contains the read-only AST inspector, JSON inventory, review report and SHA-256 manifest. ZIP CRC and manifest hashes PASS. Ten negative scenarios designed; all NOT_RUN.

## Required evidence before future integration

Define synchronized ownership of stdout/stderr readers and close operations. Observe child exit, each reader completion and stream closure separately. Specify a lifetime per-stream emitted/accepted byte accounting method and write/flush deadlines. None of these steps alone solves arbitrary scheduler suspension under model M.

ACK-02 OPEN. E5B4D_NO-GO. SEC-02 Windows NOT_RUN. RENDER_NO-GO. PUBLISH_NO-GO. No project code executed, no runtime patch and no merge to main.
