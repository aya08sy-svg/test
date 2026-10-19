# Company Claude metaprompt: find duplicate validators, remove or merge them, and rename all validators to meaningful codes

> **For the human:** paste everything between `=== BEGIN PROMPT ===` and `=== END PROMPT ===` into company Claude Code at the root of the audit tool repo. Run it AFTER `CORPUS_STANDARDS_STUDY_METAPROMPT.md` if you can (it uses `docs/study/CONCERN_MAP.md`); it also works without it. It complements `COMPANY_CLAUDE_METAPROMPT_v2.1` (it is a focused, stricter version of its Phase 2 overlap analysis and Phase 4 fixes) and the `avaloq-kb` skill. Duplicates are DELETED, not disabled. The REST payload keeps the rule identifiers the receiver knows, through an alias map, so nothing downstream breaks. It resumes from `docs/dedupe/PROGRESS.md`.

=== BEGIN PROMPT ===

## 1. Role and goal

You are the ORCHESTRATOR of a team of subagents. The audit engine has some duplicate validators. Your job:

1. **Find** every duplicate or overlapping validator pair, with proof from four independent kinds of evidence.
2. **Remove** true duplicates: delete the code, registry entry and tests of the loser. Never disable them.
3. **Merge** validators that cover the same concern in parts, into one validator that keeps all of their true positives.
4. **Rename** every surviving validator to a meaningful code, while the REST payload keeps sending the identifiers the receiver already knows.
5. **Prevent** new duplicates with registry checks and an overlap test.
6. **Ground** every surviving validator in the `avaloq-kb` skill (doc_ref KB ids) and feed back what you learn.

## 2. Binding rules

- All v2.1 rules hold: PROTECTED ZONE P1-P5 (packaging, Oracle, REST, the JSON payload contract including rule identifiers as the receiver knows them, config/secrets), PACKAGING-SAFE code (no new runtime dependencies, explicit registry, no runtime data files, Windows paths), DEV-SIDE vs RUNTIME, OFFLINE ONLY, never edit a test expectation to make it pass, confidentiality.
- **Delete, never disable.** No `enabled=False`, no feature flags, no commented-out code, no "deprecated" stubs, no empty rule classes, no `if False:`. A removed validator's file, registry import, class, fixtures folder (after its cases are moved to the survivor) and dead helpers are removed. Git history is the archive.
- **No lost coverage.** A merge or removal may drop a finding only if it is (a) a duplicate of a survivor finding on the same unit, or (b) a false positive the human approved removing. The coverage check in R4 proves this.
- **Payload compatibility.** Rule ids inside the engine may change. The identifiers in the REST JSON may not, unless the human approves a receiver migration (section R5.6). The payload builder (P4) is not edited; the mapping happens before it, in the bridge.
- **KB first.** Every subagent reads `.claude/skills/avaloq-kb/SKILL.md` first. The concern of a rule and its family are decided with KB ids where the KB has them; `UNKNOWN(KB gap)` otherwise. Never invent Avaloq semantics to justify a merge.
- One pair per step, one commit per step: `DEDUPE <survivor> <- <removed>: <what>` or `RENAME <old> -> <new>`. Update `docs/dedupe/PROGRESS.md` after every step. STOP at every gate.

## 3. Subagent roles

| Role | Job |
|---|---|
| CATALOGUER | Reads each validator's code and writes its catalogue card (R1). |
| STATIC-COMPARER | Code-level similarity between validators (R2a). |
| CORPUS-RUNNER | Runs the engine offline on the corpus and computes co-firing statistics (R2c). |
| FIXTURE-SWAPPER | Runs every rule's fixtures through every other rule (R2d). |
| JUDGE-A, JUDGE-B | Blind, independent classification of each suspect pair (R2e). They never see each other's verdict. |
| RULE-SMITH | Implements merges, removals and renames (R4, R5). |
| NAMER-A, NAMER-B | Propose names independently (R5). |
| ADVERSARY | Tries to break each verdict and each merge: finds a unit where only the loser fires, or a context where the merged rule misfires. |
| KB-GROUNDER | Maps each survivor to KB ids and writes KB feedback (R7). |

Every brief contains: the goal, exact inputs, output file and format, what not to touch, and "read the avaloq-kb SKILL.md first". Log every cross-check in `docs/dedupe/VERIFICATION_LOG.md`.

## PHASE R0 - State and safety net

1. Resume from `docs/dedupe/PROGRESS.md` if it exists.
2. Detect the engine state and write it to PROGRESS.md: is there a v2.1 `audit_core/` with `registry.py`, `rule.py` (RuleSpec with `legacy_name`, `rest_id`) and `legacy_bridge.py`? Or the original layout? Where does a validator's identifier enter the result object that the payload builder reads? Quote file:line.
3. Make sure the safety net exists and is green; build only what is missing, using the v2.1 tools if present:
   - `baseline/legacy.csv` from the full offline corpus run (source, line, rule_id, severity, method, subject, message, fingerprint)
   - `tests/payload_snapshots/` for 20 representative sources, and `tests/test_payload_contract.py`
   - fixtures per rule, `tests/test_fixtures.py`
   - `tools/check.py` (pytest, scope guard, corpus run, baseline diff, payload contract)
4. If the human has precision labels (`reviews/labels.csv`), load them; they decide survivors.

**Gate R0:** all tests green, baseline and payload snapshots recorded at the current commit. STOP and report the state.

## PHASE R1 - Catalogue every validator  [CATALOGUER xN, verified by ADVERSARY sample]

One card per validator in `docs/dedupe/CATALOG.md` (extend v2.1 CATALOG.md if it exists, do not fork it):

```
current_id     id used in the engine today
legacy_name    original name/class/function
rest_id        identifier the REST payload carries today (read from the code path, not guessed)
file:line      where the logic lives; helpers it calls
concern        the ONE question it answers, 2-4 words (use docs/study/CONCERN_MAP.md wording if present)
family         STR CFW ERR CTL ACC PRF DAT MEM TXN LYR NAM MNT FMT (v2.1 list; propose a new family only with a reason)
anchor         node types / shared fact / regex it works on
input_kind     regex-text | line | ast | facts | mixed
level          Token | Stmt | Block | Method | Package | Cross
trigger        plain-language condition under which it fires, incl. thresholds and exclusions
message        message template(s)
severity       and profile
doc_ref        current value; KB ids (KB-xxx-nn) found by KB-GROUNDER; HOUSE (owner) or NONE
fixtures       pos / neg / edge counts
corpus_hits    findings in baseline/legacy.csv; distinct sources
precision      from labels if available
```

The card's `trigger` must be written from the code, not from the rule's title or docstring; a title that disagrees with the code is itself a finding.

**Gate R1:** a card for every registered validator and every unregistered validator file (orphans are removal candidates). STOP and report the count per family and the orphans.

## PHASE R2 - Detect duplicates with four kinds of evidence

Build the suspect list as the union of a) to c); then score every suspect pair with all of a) to e).

a) **Static** (STATIC-COMPARER, dev-side script `tools/dedupe_static.py`, stdlib only: `ast`, `difflib`, `hashlib`):
   - normalised AST dump similarity of the rule functions (identifiers and literals abstracted)
   - same anchor node types, same regex (after normalisation), same helper calls, same message text or same KB/doc_ref
   - one rule calling the other, or copy-pasted helper logic

b) **Semantic**: same concern or same CONCERN_MAP row, same KB ids, same STD ids.

c) **Empirical** (CORPUS-RUNNER, `tools/dedupe_cofire.py`): from the baseline, the set of UNITS each rule fires on (unit = statement / block / method from facts, not raw line). For every pair:
   - `jaccard = |A ∩ B| / |A ∪ B|`
   - `contain_AB = |A ∩ B| / |A|` and `contain_BA`
   - also count parent/child co-firing (statement in A, enclosing block in B)
   - 5 sample units for each non-zero pair
   Suspect if jaccard >= 0.3, or either containment >= 0.8, or parent/child co-firing >= 0.5.

d) **Cross-fixture** (FIXTURE-SWAPPER): run every rule's pos/neg/edge fixtures through ALL rules. Record, per pair, how many of A's positives B also flags at the same unit, and vice versa.

e) **Blind judges** (JUDGE-A, JUDGE-B): each gets the two cards, the code and the samples, but not the scores' interpretation and not the other judge's answer, and classifies the pair:

| Class | Meaning | Action |
|---|---|---|
| EXACT | same concern, same findings (jaccard >= 0.95 and fixture swap all-same) | REMOVE the loser |
| SUBSUMED | same concern, A's findings are a subset of B's (contain_AB >= 0.95) | REMOVE A; if A has a more precise message or severity for its sub-case, MERGE that message into B as a variant |
| OVERLAP | same concern, partial overlap | MERGE into one rule with the union of true-positive logic, one finding per unit |
| VARIANT | same concern, differs only by threshold, context or source type | MERGE into one parameterised rule (parameters as Python constants in the rule) |
| SHARED-FACT | different concerns, same analysis computed twice | KEEP both; move the analysis into the facts layer once (core change, say so) |
| COINCIDENT | different concerns that happen to hit the same unit | KEEP both; add the pair to the overlap allow-list with a reason |
| EXTERNAL | duplicates a check Avaloq already does (compiler warning or ASMD marker; KB-TOOL-82..88) | REPORT only; the human decides keep or remove |
| NOT-DUP | false alarm | none |

Agreement rule: when the two judges agree and the numbers support it, the verdict is PROPOSED. When they disagree, or the numbers contradict the verdict (for example EXACT with jaccard 0.6), ADVERSARY investigates and the pair goes to the human as DISPUTED with both arguments.

**Survivor choice** for REMOVE and MERGE, in this order, stated per pair:
1. higher measured precision (labels)
2. grounded in the KB (STATED entry) over HOUSE over NONE
3. AST/facts-based over regex/line-based
4. better fixture coverage and fewer known false positives
5. the rest_id the receiver uses more (ask the human if unknown; this matters for dashboards and trend history)

Write `docs/dedupe/DEDUPE_PLAN.md`: one row per pair: pair | scores (a-d) | judge A | judge B | verdict | survivor and why | loser | expected baseline change (findings that disappear, findings that move to the survivor) | rest_id impact | KB ids. Then a list of clusters (3+ rules on one concern), each resolved into one survivor.

**Gate R2:** every suspect pair scored on all five lines; no verdict without both judges. STOP and wait for the human to approve, change or reject each row. Execute only approved rows.

## PHASE R3 - Merge design (only for MERGE / VARIANT rows)

For each approved merge, RULE-SMITH writes a short design in `docs/dedupe/merges/<survivor>.md` before any code:
- the union trigger as a decision table (condition -> fires? message variant, severity)
- which parts come from which old rule (file:line)
- conflicts between the old rules (different thresholds, different exclusions) and the chosen resolution, with KB ids or corpus counts as the reason
- the fixture plan: every pos/neg/edge of both old rules, plus new edge fixtures at each boundary where the old rules disagreed
ADVERSARY reviews the design for a unit only one old rule caught that the union would miss, and for contexts where the union now fires but neither old rule did (new false positives).

**Gate R3:** design reviewed. STOP only if the design changes a severity or adds a message variant the human has not seen.

## PHASE R4 - Execute, one pair at a time  [RULE-SMITH, ADVERSARY]

For each approved row, in the order the human gives (default: EXACT, then SUBSUMED, then MERGE/VARIANT, then SHARED-FACT):

1. **Fixtures first.** Move every fixture of the loser into `tests/fixtures/<survivor>/` (git mv, keep the file name with a `from_<loser>_` prefix). Rewrite its `-- expect:` markers to the survivor's id. Where both rules used to fire on the same line, the fixture now expects ONE survivor finding. Add the R3 boundary fixtures. Show the new fixtures failing where behaviour must change.
2. **Implement** the merge in the survivor (or nothing, for EXACT). Bump the survivor's version.
3. **Delete** the loser: its rule file, its import in the explicit registry list, its class, its old fixtures folder (now empty), tests that only tested it, and helpers no other code uses (prove "no other use" with a grep and show it). No stubs or flags remain: `grep -rn "<loser id>\|<loser legacy name>"` over the app must return only the alias map entry (step 5) and the changelog.
4. **Coverage check** (`tools/dedupe_coverage.py <survivor> <loser>`): every (source, unit) the loser flagged in the baseline is flagged by the survivor after the change, unless that row is listed in the plan as an approved false-positive removal. Any lost unit fails the step.
5. **Ids.** Add the loser to `RETIRED_RULES` in the rule-id module (R5.3): `old_id -> (survivor_id, reason, date)`. Its `rest_id` is handled by the R5.6 policy (default: the survivor's rest_id is sent; the loser's rest_id is listed as retired so it is never reused).
6. **Prove.** `tools/check.py <survivor>`: tests green; scope OK; baseline diff moves ONLY the survivor and the loser, with exactly the expected changes from the plan; payload snapshots differ only by the removed duplicate findings, shown as 5 sample diff rows. ADVERSARY reviews the diff for collateral damage.
7. Wait for review, then accept the new baseline and commit.

**Gate R4** (after all rows): registry has no loser left; `grep` for every retired id and legacy name finds only the alias map and the changelog; full corpus run, coverage check for every pair, payload contract green with the approved diff.

## PHASE R5 - Rename to meaningful codes

### R5.1 Naming scheme
```
<FAM>-<MNEMONIC>
FAM       the family code from the catalogue (3 letters, v2.1 list)
MNEMONIC  1-3 upper-case words joined by '-', max 20 characters, naming the DEFECT the
          rule finds (not the fix, not the implementation), using Avaloq vocabulary from the KB
format    ^[A-Z]{3}-[A-Z0-9]+(-[A-Z0-9]+){0,2}$ , total length <= 24
```
Illustrative examples only (the real names come from the cards): `ACC-ROW-REREAD` (same DDIC row read again across a possibly-writing call), `CTL-CASE-NO-ELSE`, `PRF-STORE-IN-LOOP`, `PRF-INDEX-LOOP-GET`, `ERR-OTHERS-SWALLOWED`, `TXN-SESSION-COMMIT`, `DAT-SESSION-CACHED`, `PRF-IFF-UNTYPED`, `NAM-PREFIX-MISSING`, `FMT-TAB-INDENT`.
Rules:
- unique; no reuse of a retired id or of any id in the alias map
- the name must be true for EVERY case the rule fires on (check against the trigger on the card and 10 random corpus findings)
- avoid vague words (CHECK, RULE, ISSUE, BAD, MISC) and internal jargon not in the KB or the standards
- if the KB D6 catalogue has a candidate for the same rule, record the D6 id on the card (do not use it as the code)

### R5.2 Proposals
NAMER-A and NAMER-B each propose a name for every survivor independently, with a one-line justification citing the trigger. Where they agree, the name is PROPOSED; where they differ, the orchestrator picks one with a reason and lists the other. Write `docs/dedupe/NAMING.md`: current_id | legacy_name | rest_id | proposed code | alternative | concern | KB ids. **STOP** for human approval of every name.

### R5.3 One rule-id module (runtime code, Python, no data file)
Create or extend one module in the engine (for example `audit_core/rule_ids.py`), imported by the registry and the bridge:
```python
RULE_ALIASES   = {...}  # every old internal id and legacy name -> new code
REST_IDS       = {...}  # new code -> identifier the REST payload must carry (unchanged values)
RETIRED_RULES  = {...}  # removed id -> (survivor code, reason, date)
def canonical(rule_id: str) -> str: ...   # resolves aliases, raises on unknown ids
```
The bridge (`legacy_bridge.py`, or the single place R0 found) writes `REST_IDS[finding.rule_id]` into the field the payload builder reads. The payload builder itself is not edited. If the identifier cannot be mapped without touching a P1-P5 file, STOP and write a proposal in `docs/refactor/PROPOSALS.md`.

### R5.4 Mechanical rename, one family per commit
For each family, RULE-SMITH renames: RuleSpec.id (keep `legacy_name` and `rest_id` fields), rule file name (`rules/<code_lower_underscored>.py`, git mv), class name, the explicit registry import list, fixture folders (git mv), `-- expect:` markers, `docs/refactor/CATALOG.md`, OVERLAPS.md, BACKLOG.md, REQUIRED_RULES.md, PATTERNS.md files, ledger entries that name rules, and the UI's rule catalogue if it has its own list.

Also keep working, through `canonical()`:
- **suppressions** in Avaloq sources (`--@NoCheck <old id>` must still suppress; add a fixture proving it for 3 renamed rules)
- **baselines and labels**: `tools/migrate_rule_ids.py` rewrites `baseline/*.csv` and `reviews/labels.csv` to new codes and recomputes fingerprints with the new code, keeping a `old_fingerprint -> new_fingerprint` map so no human label is lost or asked again
- **CLI/UI filters** that accept a rule id: old ids still work and resolve to the new code

### R5.5 Gate per family
`tools/check.py --all`: tests green; baseline diff after migration EMPTY (same findings, new codes); payload snapshots BYTE-IDENTICAL (rest ids unchanged); `grep` for old ids in app code finds only `rule_ids.py`. The exe is rebuilt with the existing, unchanged build command and smoke-tested offline on 5 sources.

### R5.6 Receiver policy (decided by the human, default A)
- **A (default):** the payload keeps the old rest ids forever; new codes are internal, in reports and in the UI.
- **B:** the receiver team adds the new codes; then flipping `REST_IDS` to identity is a one-line change with its own approval and payload snapshot update. Write the mapping table for the receiver team in `docs/dedupe/REST_ID_MAPPING.md` (old rest id | new code | retired? | survivor). Do not change the payload until they confirm.

## PHASE R6 - Prevent new duplicates

1. `registry.validate()` (runs at import and in tests) additionally checks: id matches the R5.1 format; ids unique; `(family, concern)` unique; no registered id is in `RETIRED_RULES` or is an alias key; every rule has a `REST_IDS` entry; every alias target exists; every rule has `doc_ref` (KB id, HOUSE or NONE).
2. `tests/test_overlap.py`: runs every rule's positive fixtures through all rules; a second rule firing on the same unit fails the test unless the pair is in `OVERLAP_ALLOWLIST` (in the rule-id module, with the reason from R2).
3. `tools/dedupe_cofire.py --check` in `tools/check.py`: fails if a new pair crosses the R2c thresholds on the corpus and is not allow-listed.
4. Add to `CLAUDE.md`:
   ```
   ## Validator ids and overlap
   Codes are <FAM>-<MNEMONIC> (docs/dedupe/NAMING.md). Before adding a validator, find its concern in docs/study/CONCERN_MAP.md and docs/refactor/CATALOG.md; if a rule already answers that concern, extend it instead. Never reuse a retired id. The REST payload ids come from REST_IDS in audit_core/rule_ids.py and must not change without approval. Removed validators are deleted, never disabled.
   ```
5. Update the K2 loop in `docs/avaloq_kb/KB_PATTERN_DEV_METAPROMPT.md` usage notes (in `docs/avaloq_kb/README.md` or CLAUDE.md, not the skill): step 6 "overlap check" means running `tests/test_overlap.py` and the co-firing check.

## PHASE R7 - Ground in the KB and feed it back  [KB-GROUNDER, VERIFIER]

1. Every survivor gets `doc_ref` with KB ids (`KB-STD-31`), or `KB-HSE-nn` for a company standard if the study prompt created `G_house.md`, or HOUSE (owner) / NONE. Each id is checked by a second subagent against the KB text: the rule must enforce what the entry says, with the entry's basis (do not make a CONFLICT or INFERRED entry an error-severity rule without corpus counts).
2. `docs/dedupe/KB_D6_COVERAGE.md`: every D6 candidate rule in `references/D_standards.md` -> COVERED (new code) / PARTIAL / MISSING. MISSING rows go to `docs/refactor/BACKLOG.md`.
3. Anything learned while merging that contradicts or extends the KB (for example a construct the KB calls invalid that a removed rule matched in real code) goes to `docs/avaloq_kb/KB_CORRECTIONS.md` or `KB_OPEN_QUESTIONS.md`, never into `references/` directly.
4. The message of each survivor may cite its KB id and a short "why" so the UI and the report can explain the finding. The KB itself never ships in the exe; only these strings in rule metadata do.

## Final report

- Before/after: validator count per family; pairs found per class; removed, merged, kept (with reasons); disputed pairs and how the human decided.
- The full rename table (old id | legacy name | rest id | new code).
- Gate results with outputs: R0-R6, coverage check per pair, payload contract, exe rebuild and smoke test.
- `git diff --stat` (no P1-P5 file changed), the list of retired ids, KB feedback written, open questions.

Begin: if `docs/dedupe/PROGRESS.md` exists, resume from it; otherwise start PHASE R0.

=== END PROMPT ===
