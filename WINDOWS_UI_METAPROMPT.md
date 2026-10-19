# Company Claude metaprompt: build the Windows audit UI

> **For the human:** open company Claude Code at the root of the audit tool repo and paste everything between `=== BEGIN PROMPT ===` and `=== END PROMPT ===`. Then type `Start.`
> It works whether or not the refactor from `COMPANY_CLAUDE_METAPROMPT_v2.md` is done: it finds whatever validator entry point exists today.
> Optional: copy `audit_ui/` from this project into `docs/ui_reference/` first. It is a working Tkinter prototype running demo rules. The prompt treats it as a layout reference only, never as code to trust.
> The prompt stops at each `STOP` and waits for you. Reply `approved` (or your corrections) to continue.

=== BEGIN PROMPT ===

==========================================================================
ROLE
You are the ORCHESTRATOR of a small team of subagents. Build a Windows
desktop UI for our existing, working Avaloq Script audit tool. The tool
reads Avaloq sources from Oracle, runs deterministic validators (Lark +
AST), and sends results as JSON over a REST API. It ships as a frozen exe.

The UI lets a developer:
  - paste code, OR pick one or more files, OR pick a corpus folder;
  - run EVERY validator the batch tool runs, on that input;
  - browse the violations, see the offending source line, filter, export;
  - spot rules that fire together on the same line (overlap hints).

The UI must report exactly what the batch tool reports for the same source.
It is a second front end to the SAME engine, not a second engine.

You do not do the heavy work yourself. You brief subagents, make them check
each other, re-run every acceptance command yourself, and accept nothing
until a gate passes and the human approves.

==========================================================================
0. NON-NEGOTIABLE CONSTRAINTS (read twice)

PROTECTED ZONE. Do not modify, move, rename or reformat:
  P1 Packaging: existing build/spec files, PyInstaller/cx_Freeze/Nuitka
     config, hooks, build scripts, installer files, version files, the
     existing app entry point, vendored libraries, build requirements.
  P2 Oracle access.   P3 REST client.   P4 The JSON payload contract.
  P5 Anything reading config, secrets or environment.
If docs/refactor/INVENTORY.md exists, its P1-P5 list is binding. If a change
there seems necessary, STOP and write it in docs/ui/PROPOSALS.md instead.

ONE ENGINE. The UI calls the SAME function the batch tool uses to validate
one source (the same one tools/run_corpus.py calls, if it exists). No
copied, re-implemented or simplified validator logic in the UI. No rule
filtering, deduplication or severity remapping that the batch path does not
also do. Display-only mapping (field names, severity labels) is allowed.

OFFLINE ONLY. The UI never imports or calls Oracle (P2) or REST (P3) code,
directly or through the modules it imports. It never reads credentials or
config secrets. If the validator entry point is tangled with Oracle/REST
imports, STOP and propose the smallest separation in PROPOSALS.md.

ENGINE UNTOUCHED. Do not change any validator, parser, grammar, facts or
registry code. Batch findings and REST JSON must be byte-for-byte identical
before and after this work (Gate G4 proves it).

PACKAGING-SAFE CODE.
  - Tkinter + ttk only, standard library only. No new runtime dependency
    (no PyQt, wx, customtkinter, pandas). PyInstaller is a build-time tool.
  - No dynamic discovery (pkgutil, importlib on computed names, glob of .py).
  - Locate grammar/resource files exactly as the app does (sys._MEIPASS
    logic); reuse its helper, do not copy-paste a new one.
  - Must work with Windows paths, spaces in paths, and long corpora.
  - The model is build-time only: no LLM, network call or learned data file
    is used by the UI exe.

SEPARATE BUILD. The UI gets its own entry point and its own spec file. The
existing exe build command and spec stay unchanged and still produce the
same exe (G5).

Write all UI work in NEW files only:
  audit_ui/                    # new package, next to the app package
    __init__.py
    __main__.py                # python -m audit_ui
    adapter.py                 # ONLY module that imports the engine
    model.py                   # UIFinding dataclass, severity order
    app.py                     # Tkinter window
    runner.py                  # background worker + queue
    analysis.py                # summary + co-firing (pure functions)
    io_utils.py                # read with encoding fallback, folder walk,
                               #  binary/size skip, CSV/JSON export
  AvaloqAuditUI.spec           # new spec, or build/ui/ if specs live there
  build_ui.bat                 # one-command build of the UI exe
  tests/ui/                    # tests for all of the above
  tools/ui_compare.py          # G3 comparison tool
  docs/ui/                     # DISCOVERY.md, PROPOSALS.md, VERIFY_LOG.md,
                               #  USER_GUIDE.md
If the repo's layout makes another place more natural, propose it at STOP 0.

==========================================================================
1. SUBAGENTS

  SCOUT          read-only. Finds the validator entry point, finding
                 object, severities, required metadata, grammar location,
                 build command, Python/Tk versions. Cites file:line.
  ADAPTER-SMITH  writes audit_ui/adapter.py, model.py and their tests.
  UI-SMITH       writes app.py, runner.py, analysis.py, io_utils.py and
                 their tests, from the UI SPEC below. Never imports the
                 engine directly; only adapter.py.
  PACKAGER       writes the spec and build_ui.bat; builds and smoke-tests
                 the exe.
  VERIFIER       blind to the adapter code. Writes tools/ui_compare.py and
                 runs the comparison against the batch output.
  ADVERSARY      tries to break each result: odd encodings, empty files,
                 huge files, binary files, deep folders, parse failures,
                 paths with spaces/unicode, Stop mid-run, double-click Run,
                 import leaks into Oracle/REST.

Every brief you give contains: goal (one sentence), exact input paths,
exact output paths, the acceptance command that must pass, the files it
may NOT touch (P1-P5, engine code, other subagents' files), and: "Cite
file:line for every claim about the codebase. Say UNKNOWN rather than
guess. Return what you produced, the acceptance output, and every
assumption."

You re-run every acceptance command yourself and log it in
docs/ui/VERIFY_LOG.md (subagent, check, command, result).

==========================================================================
PHASE 0 - DISCOVERY  [SCOUT, ADVERSARY]  (no code changes)

Write docs/ui/DISCOVERY.md:
  1. The function that validates ONE source today (module, name,
     signature, file:line). How the batch path calls it. What it needs
     besides text: script/object type, object name, package, version,
     profile, config. Where each of those comes from today (Oracle row,
     file name, header, config).
  2. The finding/result object: every field, type, example values;
     severity values; how rule ids and messages are formed.
  3. How parse errors surface (exception type, PARSE findings, None).
  4. Import graph from that entry point: list every module it pulls in.
     Flag any that import Oracle (P2), REST (P3) or read config/secrets (P5).
  5. Grammar/resource files and how they are located when frozen.
  6. The existing build command, spec path, Python version, PyInstaller
     version, whether tkinter is importable in that Python.
  7. Whether tools/run_corpus.py (or another batch-to-CSV path) exists.
     If not, how to produce batch findings offline for given files.
  8. File extensions and encodings found in the local corpus.
  9. Protected file list P1-P5 with paths.
ADVERSARY: find anything SCOUT missed, especially hidden Oracle/REST
imports and metadata the engine silently needs.
STOP. Report items 1-9, the proposed file layout, and the metadata plan:
how the UI gets each required metadata value without Oracle (file name
rule, header comment, or a "Source type" dropdown with "Auto-detect").

==========================================================================
PHASE 1 - ADAPTER  [ADAPTER-SMITH, ADVERSARY]

audit_ui/model.py
  UIFinding(source, line, rule_id, severity, message, column=0,
            end_line=0, extra: dict) where severity is error|warning|info.
  Keep the engine's original severity and any extra fields in `extra` so
  nothing is lost in export.

audit_ui/adapter.py  (the ONLY module importing the engine)
  engine_label() -> str            name/version shown in the window title
  rule_catalog() -> list of (rule_id, severity, title) from the registry
                    or the explicit validator list
  source_types() -> list of types the UI may offer (from Phase 0)
  audit_source(text, source_name, source_type=None) -> list[UIFinding]
      calls the entry point exactly as the batch path does, maps results,
      sorts by (line, severity, rule_id). Parse errors raise AuditError
      with a readable message; the UI shows them and continues.

tests/ui/test_adapter.py
  - every fixture (tests/fixtures/ or the corpus sample) through
    audit_source gives the same {(rule_id, line, message)} as the batch
    entry point called directly;
  - parse failure raises AuditError, does not crash;
  - test_offline: import audit_ui.adapter in a fresh interpreter and assert
    no P2/P3/P5 module is in sys.modules.
Gate G1: pytest tests/ui/test_adapter.py green.
STOP. Report mapping table (engine field -> UIFinding field), metadata
handling, G1 output.

==========================================================================
PHASE 2 - UI  [UI-SMITH, ADVERSARY]

UI SPEC (follow it; the reference prototype in docs/ui_reference/, if
present, shows one possible layout):

Window: title "Avaloq Code Audit - <engine_label()>". 1280x820, min
900x600. ttk theme "vista" when available. DPI aware on Windows
(ctypes.windll.shcore.SetProcessDpiAwareness(1), in try/except).
Vertical split: input area on top, results below; both resizable.

Input area, three tabs:
  1. "Paste code": monospaced Text (Consolas 10) with undo and scrollbar.
     Ctrl+Enter runs the audit. Optional "Source name" entry, default
     "<pasted code>". "Source type" dropdown if Phase 0 requires it.
  2. "Files / corpus folder": list of selected paths (multi-select) with
     buttons Add files..., Add folder..., Remove selected, Clear.
     Extension filter entry (blank = all; accepts ".txt;.sql" or "txt,sql"),
     "Include subfolders" checkbox (on), duplicates ignored, hidden folders
     skipped, binary files (NUL byte in first 4 KB) and files > 10 MB
     skipped and counted. Shows "N files selected".
  3. "Active rules": table of rule_catalog() (rule, severity, title).
Run bar under the tabs, always visible: Run audit, Stop, progress bar,
status text. Run audits the active tab's input.

Execution (runner.py):
  - Runs in a background thread; results reach Tk via a queue polled with
    root.after. The UI never freezes and Tk is only touched on the main
    thread.
  - One file at a time; read with encoding fallback utf-8-sig -> cp1252 ->
    latin-1. A file that fails to read or parse becomes an error entry and
    the run continues.
  - Stop finishes the current file, then ends. Run is disabled while
    running.
  - Status at end: "Done. X errors, Y warnings, Z info, F file(s) failed"
    (+ "(stopped)").

Results area, filter row then tabs:
  Filter row: Error / Warning / Info checkboxes, Rule dropdown ("(all)" +
  rules seen), Search box (rule, message, file; case-insensitive), Export
  CSV..., Export JSON... (exports the CURRENT filtered rows, CSV as
  utf-8-sig so Excel opens it).
  1. "Violations (N)": table Severity | Rule | File | Line | Message, text
     colour by severity, sortable by clicking headers (numeric sort for
     Line). Selecting a row loads the source below with line numbers and
     highlights line..end_line, scrolled into view.
  2. "Summary by rule": Rule | Severity | Violations | Files, errors first,
     then by count. Double-click filters Violations to that rule.
  3. "Rules firing together": pairs of rules reporting the same source and
     line: Rule A | Rule B | Same line count | Example (file:line). Sorted
     by count. A caption explains that high counts suggest overlapping
     validators.
  4. "Errors (N)": File | Error, for read and parse failures.
  Source preview pane under the tabs: read-only, monospaced, horizontal and
  vertical scroll.

analysis.py holds summary and co-firing as pure functions over
list[UIFinding] so they are unit-tested without Tk.

Tests (tests/ui/):
  test_analysis.py   summary and co-firing on hand-made findings.
  test_io_utils.py   encodings, binary skip, size skip, extension filter,
                     folder walk with subfolders, Windows paths with spaces.
  test_runner.py     runner on 3 files incl. one parse failure and one
                     binary; Stop mid-run; no Tk needed.
  test_app_smoke.py  creates the window (skip if no display), pastes a
                     fixture, runs, waits for completion, asserts the
                     Violations count equals adapter.audit_source on the
                     same text, selects the first row and asserts the
                     preview highlight is on the right line. Destroys root.
  test_isolation.py  the app package never imports audit_ui; audit_ui
                     imports the engine only in adapter.py (AST scan).
Gate G2: pytest tests/ui green; ADVERSARY's list of edge cases each has a
test or a written reason why not.
STOP. Report test output, screenshots of each tab after a real run (save
under docs/ui/screens/), and ADVERSARY findings.

==========================================================================
PHASE 3 - VERIFY AGAINST BATCH  [VERIFIER, ADVERSARY]

VERIFIER works blind to adapter.py.
  1. Pick 20 corpus files: cover every source type from Phase 0, the 5
     files with the most findings, 3 with none, 2 that fail to parse,
     and the largest file. List them in docs/ui/compare_set.txt.
  2. Batch side: produce findings for those 20 files with the batch path
     (tools/run_corpus.py or the Phase 0 offline method) -> out/ui/batch.csv.
  3. UI side: tools/ui_compare.py drives the UI's runner (no window) on the
     same 20 files -> out/ui/ui.csv. Also export CSV from the real window
     for the same set once, by hand or by script, -> out/ui/ui_window.csv.
  4. Compare per file, per rule, by (source, rule_id, line, message):
     MISSING_IN_UI, EXTRA_IN_UI, FIELD_DIFF. Write out/ui/compare.csv and a
     per-rule summary.
Gate G3: zero differences across all three files. Any difference is a bug
in the adapter or runner, never "close enough". Fix and re-run.
Gate G4: the batch tool's own baseline is unchanged (tools/baseline_diff.py
with no --allow, and tests/test_payload_contract.py, if they exist;
otherwise run the batch path on the 20 files before and after and diff).
STOP. Report the compare summary, G3/G4 output, and timing (seconds per
file, total for the 20).

==========================================================================
PHASE 4 - PACKAGE  [PACKAGER, ADVERSARY]

  1. AvaloqAuditUI.spec (new): entry audit_ui/__main__.py, onefile,
     windowed (no console), name AvaloqAuditUI, hiddenimports for the
     engine modules found in Phase 0, datas for grammar/resource files
     placed where the app's locator expects them. Exclude Oracle/REST
     modules and drivers if the import graph would otherwise pull them in.
  2. build_ui.bat: one command that builds from the spec into dist\.
  3. Build. Then run the exe on the 20-file set via its window and export
     CSV -> out/ui/exe.csv; compare with batch.csv using ui_compare.py.
  4. Rebuild the EXISTING exe with its existing command, unchanged, and
     confirm it still builds and its smoke test passes.
Gate G5: exe.csv identical to batch.csv; existing exe build unchanged; git
diff shows no changes in P1-P5 or engine files (tools/scope_guard.py if it
exists, else `git diff --stat` reviewed against the protected list).
STOP. Report exe size, startup time, G5 output, and the git diff --stat.

==========================================================================
PHASE 5 - HAND-OVER

  1. docs/ui/USER_GUIDE.md: how to run (python -m audit_ui and the exe),
     each tab, filters, export, what "Rules firing together" means, known
     limits.
  2. docs/ui/MAINTAINING.md: new validators appear in the UI automatically
     through the registry; the only file to touch if the engine API changes
     is audit_ui/adapter.py; how to rebuild; how to re-run G3.
  3. Final report: files added, gates G1-G5 with outputs, open proposals,
     anything left UNKNOWN.

=== END PROMPT ===
