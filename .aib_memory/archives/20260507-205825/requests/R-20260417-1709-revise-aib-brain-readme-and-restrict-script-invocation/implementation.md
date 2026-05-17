Files considered from `.aib_memory/`: `references.md`, `requests_register.md`, `context.md`.

## Implementation Log

### Entry 2026-04-17 17:15

#### Scope
Revised `.aib_brain/README.md` to remove direct lifecycle script invocation examples for `create-request.py` and `close-request.py` and to add prominent warnings prohibiting users from running `.aib_brain/tools/*.py` scripts directly. `initialize.py` is preserved as the one documented exception (first-time workspace setup). All prompt invocation instructions and the Quick Start section remain intact and unaltered.

#### Changes
- Added a prominent `⚠ Important` blockquote warning to the **Purpose** section of `.aib_brain/README.md`, stating that tool scripts are invoked by AIB prompts automatically and must not be run directly — with `initialize.py` explicitly named as the sole exception.
- Rewrote the **Common Commands** section: removed `create-request.py` and `close-request.py` command examples; added a `Note` blockquote reinforcing that only `initialize.py` is for direct user invocation; retained `initialize.py` examples for Windows and Linux/macOS.
- Revised **Typical Daily Flow** step 5: replaced `` `close-request.py` (called automatically…) `` with "Handled automatically at the end of `aib-implement.md` — no user action required."
- Revised **Scenario 1** step 5: replaced `close-request.py is called automatically…` with "The request is closed automatically at the end of implement — no user action required."
- Revised **Scenario 2** step 3: replaced `close-request.py is called automatically…` with "The request is closed automatically at the end of implement — no user action required."

#### Tests
- T1 (manual/grep) — No lifecycle script command-block examples: Searched `.aib_brain/README.md` for `create-request.py` and `close-request.py` as copyable terminal commands. Result: zero command-block occurrences; only references appear inside warning/note blockquotes. **PASS**
- T2 (manual/visual) — Warning note present: Confirmed prominent `⚠ Important` note present after the Purpose section and a `Note` blockquote in the Common Commands section. Both are clearly visible and unambiguous. **PASS**
- T3 (manual/visual) — Prompt invocations intact: Verified all three prompt invocations (`aib-analysis.md`, `aib-implement.md`, `aib-context.md`) are present and unchanged in the copy-paste section. **PASS**
- T4 (manual/visual) — Quick Start intact: Verified Quick Start section with `run.bat` (Windows) and `sh .aib_brain/run.sh` (Linux/macOS) commands is present and unmodified. **PASS**
- T5 (idempotency) — Re-running implement on the same README produces identical content; changes are stable and non-drifting. **PASS**

#### Outcome
SUCCESS — All five acceptance tests pass. `.aib_brain/README.md` no longer contains user-facing command examples for `create-request.py` or `close-request.py`. Prominent warnings prohibiting direct script invocation are present. The interactive menu entry point and prompt invocation guide remain fully intact.

#### Evidence
- `.aib_brain/README.md` line 9: `⚠ Important` warning blockquote added after Purpose heading.
- `.aib_brain/README.md` line 41: `Note` blockquote in Common Commands section naming only `initialize.py` as the direct-invocation exception.
- Grep result: 4 matches for `create-request\.py|close-request\.py` — all in warning prose, none in fenced code blocks.
