# Company Claude metaprompt: study the corpus and coding standards with subagents, and grow the KB

> **For the human:** fill in the three paths in section 0, then paste everything between `=== BEGIN PROMPT ===` and `=== END PROMPT ===` into company Claude Code at the root of the audit tool repo. It complements `COMPANY_CLAUDE_METAPROMPT_v2.1` and `docs/avaloq_kb/KB_PATTERN_DEV_METAPROMPT.md`; it replaces neither. Run it BEFORE `VALIDATOR_DEDUPE_RENAME_METAPROMPT.md`, because the dedupe prompt uses the concern map and rule candidates this one produces. It resumes from `docs/study/PROGRESS.md`, so you can paste it again in a new session.

=== BEGIN PROMPT ===

## 0. Inputs (the human fills these in)

```
CORPUS_PATH    = {{CORPUS_PATH}}       # exported Avaloq sources (the "defined path")
STANDARDS_PATH = {{STANDARDS_PATH}}    # company coding standards / guidelines / review checklists
EXTRA_DOCS     = {{EXTRA_DOCS_PATH}}   # optional: newly downloaded official Avaloq docs; "none" if empty
KB_PATH        = .claude/skills/avaloq-kb
```
If any path is still a `{{...}}` placeholder or does not exist, STOP and ask the human. Never guess a path.

## 1. Role and goal

You are the ORCHESTRATOR of a team of subagents. Goal: study the whole corpus and every coding standards document comprehensively, and turn what you learn into durable, cited knowledge that every later session and the audit engine can use without re-reading the corpus:

1. **Corpus atlas**: what source types exist, how much of each, which constructs and idioms really occur, with counts and file:line samples.
2. **Standards catalogue**: every rule in the company standards, normalised, each mapped to KB ids, to an existing validator, or to the backlog.
3. **KB growth**: proposed additions and corrections to the `avaloq-kb` skill, in its own entry format, verified by a second reader, applied only through the KB change process in section 7.
4. **Rule candidates and concern map**: input for the validator dedupe/rename prompt and for the KB pattern-development loop (K2).

You do NOT change engine code, validators, grammar or tests in this prompt. Everything you write lives under `docs/study/`, `devkit/` or `tools/`, plus KB proposals.

## 2. Binding rules (inherited, do not relax)

- All PROTECTED ZONE (P1-P5), PACKAGING-SAFE, DEV-SIDE vs RUNTIME, OFFLINE ONLY and confidentiality rules of v2.1 apply. Never connect to Oracle or the REST API.
- The KB skill is the source of Avaloq truth. Every subagent reads `KB_PATH/SKILL.md` first and greps `KB_PATH/references/INDEX.md` before answering any Avaloq question. Cite KB ids (`doc_ref: KB-STD-31`). Not in the KB = `UNKNOWN(KB gap)`, never invented.
- When real code contradicts a KB entry, the code wins for parsing. Record it as a KB correction (section 7), never edit `references/` directly.
- Evidence or it did not happen: every claim carries file:line (corpus), file + section/page (standards), or a KB id. Counts come from scripts, never from a model's estimate.
- Scripts print summaries, not whole files. Source code stays in this environment.
- Resume: if `docs/study/PROGRESS.md` exists, read it and continue from the recorded next step. Update it at the end of every step (phase, step, next step, subagents used, open questions).

## 3. Subagent roles

Run independent subagents in parallel (different shards, different documents). Give every brief: the goal, the exact inputs (file list or shard id), the output file and its format, what NOT to touch, and "read KB_PATH/SKILL.md first".

| Role | Job |
|---|---|
| SURVEYOR | Deterministic inventory of CORPUS_PATH and STANDARDS_PATH with scripts. No model reading. |
| CORPUS-READER (xN) | Reads one shard of the corpus; records constructs, idioms, deviations from KB, candidate rules. |
| STANDARDS-READER (xN) | Reads one standards document (or chapter); extracts every rule in normal form. |
| DOCS-READER (xN) | Only if EXTRA_DOCS is set: extracts new KB entries from official docs in the KB entry format. |
| VERIFIER | Blind second reader. Re-derives a sample of another reader's items from the cited evidence, without seeing that reader's conclusion first. |
| CENSUS | Turns every reader claim of the form "X is common / rare / never" into a script count over the WHOLE corpus. |
| KB-CURATOR | Merges verified items into KB proposals, dedupes against existing KB entries, assigns ids, writes the change files. |
| ADVERSARY | Attacks conclusions: finds counterexamples in the corpus, doc conflicts, and rules that would produce false positives. |

**Cross-check protocol.** A reader's item becomes VERIFIED only when (a) a VERIFIER independently reached the same conclusion from the evidence, and (b) any frequency claim has a CENSUS count. Disagreements go to `docs/study/DISAGREEMENTS.md` with both readings; the orchestrator resolves them from evidence or asks the human. Log every check in `docs/study/VERIFICATION_LOG.md` (item, reader, verifier, result).

## PHASE S0 - Survey (deterministic, no model reading)  [SURVEYOR]

1. `tools/study_survey.py`: walk CORPUS_PATH. Per file: path, size, line count, header (`[script x.y]` etc.), first declaration (`script package <name>`, other source kinds), source type as the engine's existing classifier assigns it (call it, do not reimplement it), parse OK or the first parse error from the existing parser.
2. Walk STANDARDS_PATH. Per document: path, format, page/section count, title. Convert to text in `docs/study/standards_text/` with page or section markers (use only tools already available; if a format cannot be converted, list it and ask the human).
3. Shard plan `docs/study/SHARDS.md`: group corpus files by source type, then by module/namespace prefix, into shards of about 40-80 files or 15k lines. Every file is in exactly one shard. For a very large corpus, mark a stratified sample per source type for deep reading and keep the full corpus for census.
4. Write `docs/study/SURVEY.md`: file counts and lines per source type, parse success rate per type, top 20 parse errors with counts, list of standards documents, shard plan summary.

**STOP.** Report SURVEY.md and wait for approval of the shard plan.

## PHASE S1 - Read the coding standards  [STANDARDS-READER xN, VERIFIER, KB-CURATOR]

Every rule in every standards document becomes one row in `docs/study/STANDARDS_RULES.md`:

```
std_id     STD-<DOC>-<NN>          (DOC = short doc code from SURVEY.md)
source     document + section/page
text       the rule, quoted verbatim (short) or closely paraphrased
normal     one-line normal form: "<construct> must/should/never <condition>"
modality   MUST | SHOULD | MAY | INFO   (from the wording, quote the keyword)
category   STRUCTURE | NAMING | FORMAT | CORRECTNESS | PERFORMANCE | DATA-ACCESS |
           ORDERS-WORKFLOW | TRANSACTIONS | EXCEPTIONS | SECURITY | TESTING |
           DOCUMENTATION | PROCESS (not checkable in code)
checkable  AST | TEXT | FACTS (needs accessors/effects/graph) | CROSS-SOURCE | NO
kb_ids     matching KB ids, or NONE
kb_relation SAME | STRICTER | LOOSER | CONTRADICTS | NEW   (vs the KB entry)
example    the document's own good/bad example, if any (verbatim)
```

Rules:
- A STANDARDS-READER per document (or per chapter of a long document). It extracts every rule, including ones hidden in examples, tables and review checklists.
- VERIFIER re-reads a random 25% of each document blind and must find the same rules; any rule it finds that the reader missed means the reader redoes that document.
- CONTRADICTS rows (company standard vs official KB) are never resolved silently. They go to `docs/study/STANDARDS_CONFLICTS.md` with both texts, and the corpus decides what the real practice is in S3.
- Dedupe rules that appear in several documents: one row, several sources.

**STOP.** Report counts per document, per category, per modality, per kb_relation; list every CONTRADICTS row.

## PHASE S2 - Read the corpus  [CORPUS-READER xN, VERIFIER]

Each CORPUS-READER gets one shard and writes `docs/study/shards/<shard>.md` with these sections. Every item has file:line and, where relevant, KB ids.

1. **Shape**: source types in the shard, package structure, typical method sizes, nesting depth.
2. **Constructs seen**: statements, expressions, accessors (`obj_*`, `doc_*`, `mem_doc_*`, `code_*`, `lookup.*`, `session.*`, base parameters), collections and their methods, orders and workflow actions, exception handling, SQL-notation conditions, native/PL/SQL calls. Mark each as KB-KNOWN (with id) or KB-UNKNOWN.
3. **Idioms**: recurring multi-statement patterns the team uses (for example read-into-locals, `with` blocks, `err.raise_fa` handlers, order creation sequences). Give each a short name, a minimal anonymised skeleton, and 3 file:line samples.
4. **Deviations from KB**: code that contradicts a KB entry (syntax the KB says is invalid but compiles, a different precedence, an unlisted method). These become KB correction candidates.
5. **Standards observations**: places where the code follows or breaks a STD-* or KB-STD-* rule. Do not judge severity yet.
6. **Candidate rules**: things that look like bugs or performance problems no existing validator catches (check the engine's current findings for the shard first: run the existing engine offline on the shard and read its output).
7. **Questions**: anything the reader could not explain from the KB or the standards.

VERIFIER takes 3 random items per section per shard and re-derives them blind from the cited lines. A shard with more than 1 wrong item in 10 is re-read by a different reader.

Readers never paste more than 15 lines of real code into a report. Skeletons must be anonymised (no customer names, no real ids, no business data).

**STOP** after every 10 shards with progress, and at the end with totals.

## PHASE S3 - Census and synthesis  [CENSUS, ADVERSARY, orchestrator]

1. `tools/study_census.py`: for every construct, idiom and deviation claimed in S2, count occurrences over the WHOLE corpus using the existing parser or facts layer (regex only on comment-masked text and only when the parser cannot express it; say which). Output `docs/study/CENSUS.csv`: item, method (ast/facts/regex), count, files, 5 sample file:line.
2. Resolve every STANDARDS_CONFLICTS.md row and every KB CONFLICT entry the corpus touches with counts of both forms. Record the verdict and the counts; never resolve by opinion.
3. Write `docs/study/CORPUS_ATLAS.md`: per source type, the construct inventory (construct | KB id | count | coverage by the grammar), the idiom catalogue (name | skeleton | count | KB ids), parse gaps ranked by count.
4. Write `docs/study/CONCERN_MAP.md`: one row per distinct "concern" (the one question a check answers, 2-4 words, same vocabulary as v2.1 CATALOG.md), with the KB ids, STD ids, current validators that address it (by current rule id), and census counts. This is the main input of the dedupe/rename prompt: two validators on the same concern row are overlap suspects.
5. Write `docs/study/RULE_CANDIDATES.md`: candidate | concern | evidence counts | KB ids | STD ids | basis (STATED / INFERRED / HOUSE / OBSERVED) | proposed severity with reason | existing validator that partly covers it. ADVERSARY must give, for each candidate, the most likely false-positive context found in the corpus.
6. Append MISSING checkable rules to `docs/refactor/BACKLOG.md` (do not duplicate existing rows), and the human-requested ones to `docs/refactor/REQUIRED_RULES.md` only if the human approves.

**STOP.** Report atlas totals, concern map size, top 20 rule candidates by evidence, and resolved conflicts.

## PHASE S4 - Grow the KB  [KB-CURATOR, VERIFIER, DOCS-READER if EXTRA_DOCS]

This is how new knowledge reaches the KB skill. Three kinds of input, three tiers. Keep the tiers apart: the official tier must stay "verified from official docs".

| Tier | Source | Basis values | Where it goes |
|---|---|---|---|
| OFFICIAL | new official Avaloq docs in EXTRA_DOCS | STATED / INFERRED / CONFLICT | existing files A-E, next free id in the right section |
| HOUSE | company standards (S1) | HOUSE (with std_id) | new file `references/G_house.md`, ids `KB-HSE-nn` |
| OBSERVED | corpus facts with census counts (S3) | OBSERVED (with count and date) | same file `references/G_house.md`, ids `KB-OBS-nn` |

1. **Entry format.** Match the existing entries exactly (open two entries in `references/` and copy their structure). Each entry has: id, title, the statement, Means / Audit use lines, citation (doc file + page, or std_id + section, or census row), basis, and the verifier's initials/role. OBSERVED entries also carry the census count and the corpus snapshot date, because they can change.
2. **Dedupe** against INDEX.md before assigning an id. If an existing entry covers it, the new material is either a correction (section 7) or extra evidence appended as a proposal, not a new entry.
3. **Verification.** Every proposed entry is checked by a VERIFIER who reads only the cited evidence. Unverified entries stay in the proposal file marked PENDING.
4. **Write proposals, not edits**, to:
   - `docs/avaloq_kb/KB_ADDITIONS.md` (new entries, full text, ready to paste)
   - `docs/avaloq_kb/KB_CORRECTIONS.md` (KB id | what the KB says | evidence | proposed fix), same file the KB pattern prompt (K4) uses
   - `docs/avaloq_kb/KB_OPEN_QUESTIONS.md` (questions from S2 section 7 that no source answers; reuse GAPS.md numbering where it fits)
   - `docs/avaloq_kb/GAPS_ANSWERED.md` (GAPS.md items that the corpus or new docs now answer, with evidence)
5. **Apply** only after the human approves the proposal files (section 7).

**STOP.** Report counts per tier, PENDING vs VERIFIED, corrections, answered gaps.

## PHASE S5 - Make it reusable  [orchestrator]

1. `docs/study/STUDY_SUMMARY.md` (max 2 pages): what the corpus is, the top idioms, the top standards conflicts and how they were resolved, the top rule candidates, and what a new session must read first.
2. Add to the repo `CLAUDE.md` (keep the existing avaloq-kb lines):
   ```
   ## Corpus study
   Before designing or changing a validator, read docs/study/STUDY_SUMMARY.md, CONCERN_MAP.md and the census row for the construct. House standards and observed corpus facts are KB-HSE-* / KB-OBS-* in the avaloq-kb skill (references/G_house.md).
   ```
3. Re-runnability: `tools/study_census.py --diff <previous CENSUS.csv>` reports which counts moved after a new corpus export, so OBSERVED entries can be refreshed instead of re-studying everything.

## 7. KB change process (how the skill is updated)

1. The human reviews `KB_ADDITIONS.md` and `KB_CORRECTIONS.md` and marks each row APPROVE / REJECT.
2. KB-CURATOR applies approved rows to `KB_PATH/references/` in one commit:
   - new OFFICIAL entries into A-E; corrections edited in place with a `Corrected <date>: <old> -> <new>, evidence <ref>` line kept under the entry
   - HOUSE / OBSERVED entries into `G_house.md` (create it on first use, with a header that says these are company and corpus facts, not official docs)
   - regenerate `references/INDEX.md` (one line per entry, grouped by file and sub-section), and keep the entry count in SKILL.md correct
   - add a `G_house` block to SKILL.md "What a model must know first" (max 10 lines) and add the file to the Files list
   - bump a `version:` line at the top of SKILL.md and add a line to `KB_PATH/CHANGELOG.md`
3. Remove applied rows from the proposal files (move them to an `## Applied` section with the commit hash).
4. Re-run the K0 smoke test from KB_PATTERN_DEV_METAPROMPT.md plus 3 new questions answered only from the new entries.
5. The KB stays dev-side: never imported by engine code, never bundled in the exe. Only `doc_ref` strings reach rule metadata.

## Gates

- S0: every corpus file in exactly one shard; parse rate per type reported.
- S1: every standards document read and blind-sampled; every rule has kb_relation; CONTRADICTS listed.
- S2: every shard read and verified; no report pastes more than 15 real lines.
- S3: every frequency claim has a census count; CONCERN_MAP and RULE_CANDIDATES written.
- S4: every KB proposal verified by a second reader and deduped against INDEX.md.
- No engine, validator, grammar, test or protected file changed by this prompt (`git diff --stat` shows only docs/, devkit/, tools/, CLAUDE.md, and the KB after approval).

## Final report

What you did; subagents used and what each produced; gate results; counts (files, shards, standards rules, idioms, candidates, KB proposals per tier); open questions for the human; next recommended step (normally: run VALIDATOR_DEDUPE_RENAME_METAPROMPT.md, then KB_PATTERN_DEV K2 on the top candidates).

Begin: if `docs/study/PROGRESS.md` exists, resume from it; otherwise check section 0 and start PHASE S0.

=== END PROMPT ===
