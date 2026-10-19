# Company Claude metaprompt: enhance the Windows audit UI (after the suggestion tab)

> **For the human:** paste everything between `=== BEGIN PROMPT ===` and `=== END PROMPT ===` into company Claude Code at the root of the audit tool repo. It extends the UI built with `WINDOWS_UI_METAPROMPT.md` and your suggestion tab; it does not rebuild them. Best run after `VALIDATOR_DEDUPE_RENAME_METAPROMPT.md`, so the UI can show the new rule codes. Every feature is optional: at STOP U1 you pick which ones to build.

=== BEGIN PROMPT ===

## 1. Role and constraints

You are the ORCHESTRATOR (subagents: SCOUT, UI-SMITH, VERIFIER, ADVERSARY, as in `WINDOWS_UI_METAPROMPT.md`). Enhance the existing audit UI. All constraints of the UI metaprompt stay binding:
- ONE ENGINE: the UI shows what the engine produces; no validator logic, filtering or severity remapping in the UI that the batch path does not do.
- OFFLINE, no Oracle/REST imports, no secrets; Tkinter/ttk + stdlib only; no new runtime dependency; no model or network at runtime; explicit imports; Windows paths.
- Engine untouched unless a feature needs data the engine does not expose yet: then STOP and propose the smallest core change in `docs/ui/PROPOSALS.md` (it goes through the normal rule/core task process with baseline and payload gates).
- The avaloq-kb skill is dev-side only. The UI may show KB ids and short texts that are stored as Python metadata on each rule (RuleSpec), never the KB files.
- Gates G1-G5 of the UI metaprompt must still pass after every feature (same findings as batch, batch baseline unchanged, existing exe unchanged).

## PHASE U0 - Discovery (no code changes)  [SCOUT]

Write `docs/ui/ENHANCE_DISCOVERY.md`: current tabs and widgets including the suggestion tab (what it shows, where suggestions come from, how they are keyed to rules, file:line); the finding fields the UI receives; whether findings carry related lines, method/package, effects, fingerprint, rule version; whether the rule-id module (`RULE_ALIASES`, `REST_IDS`, `canonical()`) and RuleSpec `doc_ref` exist; UI test status.

## PHASE U1 - Choose features  [orchestrator]

Score each candidate below as: value for the developer, engine data needed (available / needs core change), effort, risk. Present the table and STOP for the human's choice and order.

| # | Feature | What it does |
|---|---|---|
| F1 | Rule explain panel | Selecting a finding shows the rule code, its old ids (aliases), concern, severity, `doc_ref` KB ids, a one-paragraph "why" and a bad/good example. Text comes from RuleSpec metadata, generated dev-side from the KB into Python constants. |
| F2 | Suggestion tab upgrade | Suggestions keyed by `canonical(rule_id)` so renamed rules still match; each suggestion shows its provenance (KB id, house standard id, or "team"), and a read-only before/after diff preview with a Copy button. Never auto-edits the source. |
| F3 | Baseline / diff mode | Compare the current run with a saved run (or a batch baseline CSV) by fingerprint: New, Fixed, Unchanged. Useful for the ice "Audit Code" step, where the auditor reviews one task's changes. |
| F4 | Changed lines only | Given an old and a new version of a source, show only findings on changed lines (stdlib `difflib`). |
| F5 | Triage and labels | Mark a finding TP / FP / Won't fix with a note; saved to a local `reviews/labels.csv` in the v2.1 format (fingerprint + rule_version), so precision sampling and the dedupe survivor choice use it. A "Copy suppression" button produces the `--@NoCheck <CODE> -- reason` comment text; the UI never edits sources. |
| F6 | Multi-line evidence | For rules whose findings carry related lines (for example repeated row access: first read, the possibly-writing call, the re-read), highlight all of them in the preview in different colours, with a small legend. |
| F7 | Effects view | Per method: the data-effect labels the engine computes (READ / CREATE / MODIFY / ORDER / SIDE_EFFECT / PURE / UNKNOWN) and where each comes from. Only if the effects module exists. |
| F8 | Overlap tab after dedupe | "Rules firing together" marks allow-listed pairs as expected and flags any other pair as "possible duplicate, report to the rule owner". |
| F9 | Rule catalogue tab | Searchable list grouped by family: code, old ids, concern, severity, KB ids, profile. Replaces the plain "Active rules" table. |
| F10 | HTML report export | One self-contained HTML file (stdlib string templates, no external assets) with summary, findings grouped by file and rule, and rule explanations; for sharing in reviews. |
| F11 | Navigation | Group findings by package/method in a tree; F8 / Shift+F8 next/previous finding; jump to the next finding of the same rule. |
| F12 | Run info | Engine version, rule catalogue hash and rule count in the status bar and in every export, so a result can be reproduced. |
| F13 | Remembered settings | Last folders, filters and window layout in `%APPDATA%\AvaloqAuditUI\settings.json` (UI preferences only; missing or corrupt file = defaults). |

## PHASE U2 - Build, one feature per step  [UI-SMITH, VERIFIER, ADVERSARY]

For each chosen feature: write tests first in `tests/ui/` (pure functions in `analysis.py` or a new module, testable without Tk); implement; ADVERSARY tries edge cases (no findings, 50k findings, renamed and retired rule ids, missing metadata, unicode paths, corrupt labels or settings file); re-run G1-G5; update `docs/ui/USER_GUIDE.md`; commit `UI F<n>: <what>`. STOP after each feature with screenshots.

## Final report

Features built, tests, gate outputs G1-G5, screenshots, proposals for core changes, and anything learned for the KB (written to `docs/avaloq_kb/KB_OPEN_QUESTIONS.md`).

Begin with PHASE U0.

=== END PROMPT ===
