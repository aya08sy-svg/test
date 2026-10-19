# Setup prompt: install the Avaloq KB skill in this repo

Paste everything below the line into Claude Code, started at the root of the audit tool repo, after the bundle files are in the repo (see "How the files get here" at the end).

---

You are setting up the `avaloq-kb` skill in this repository. Do the steps in order, and stop at the end with a report. Do not change any engine code in this task.

## 1. Check the files
Confirm these 10 files exist and are non-empty. Print the path and size of each.
```
.claude/skills/avaloq-kb/SKILL.md
.claude/skills/avaloq-kb/references/INDEX.md
.claude/skills/avaloq-kb/references/A_language.md
.claude/skills/avaloq-kb/references/B_types.md
.claude/skills/avaloq-kb/references/C_data.md
.claude/skills/avaloq-kb/references/D_standards.md
.claude/skills/avaloq-kb/references/E_tooling.md
.claude/skills/avaloq-kb/references/F_verify_matrix.md
.claude/skills/avaloq-kb/references/GAPS.md
docs/avaloq_kb/KB_PATTERN_DEV_METAPROMPT.md
```
If the files sit somewhere else in the repo, for example in an `avaloq-kb-bundle/` folder, move them to exactly these paths and delete the empty bundle folder. If any file is missing, stop and list what is missing.

Check that `SKILL.md` starts with a front-matter block containing `name: avaloq-kb` and a `description:` line. Check that `.gitignore` does not exclude `.claude/` or `docs/`. If it does, add negation lines (`!.claude/skills/`) and say so.

## 2. Add the pointer to CLAUDE.md
Create `CLAUDE.md` at the repo root if it does not exist. If it does not already contain a section `## Avaloq knowledge`, append this section exactly:
```
## Avaloq knowledge
For any Avaloq Script syntax, DDIC, accessor, order, data effect, coding standard or performance question, use the avaloq-kb skill (.claude/skills/avaloq-kb). Start from references/INDEX.md and open only the entries you need.
- Cite KB ids (e.g. KB-STD-31) in every RuleSpec doc_ref, fixture header and design note.
- STATED = doc says it; INFERRED = our reading; CONFLICT = docs disagree, so decide with corpus counts before encoding a rule.
- Not in the KB means UNKNOWN: never invent Avaloq APIs, DDIC fields, workflow actions or intl_ids. Log it in docs/KB_OPEN_QUESTIONS.md.
- Real code that contradicts the KB: log it in docs/KB_CORRECTIONS.md with file:line evidence. Never edit the skill's references silently.
- Subagents: read .claude/skills/avaloq-kb/SKILL.md before doing Avaloq work.
- The KB is dev-side only. No engine module may import or read .claude/ or docs/avaloq_kb/, and the exe must not bundle them.
```
If the section already exists, leave it unchanged and say so.

## 3. Create the two log files
If they do not exist, create them with only these headers:
- `docs/KB_CORRECTIONS.md`: `| KB id | KB says | Evidence (file:line or doc page) | Proposed fix | Status |`
- `docs/KB_OPEN_QUESTIONS.md`: `| Question | Why it matters | Qnn (if any) | Raised by (rule/file) | Status |`

## 4. Keep the KB out of the exe
Find the build and packaging config (PyInstaller `.spec`, `build*.bat`, `setup.py`/`pyproject`, any datas or include lists). Confirm that nothing includes `.claude/` or `docs/avaloq_kb/`. Search the engine source for the strings `avaloq-kb`, `.claude` and `avaloq_kb`, and confirm there are no hits outside docs and CLAUDE.md. Report what you checked. Change nothing here unless something does include those paths. If it does, stop and ask first.

## 5. Smoke test
Answer these three questions ONLY by reading the skill (INDEX.md, then the cited entries), and quote the KB ids:
1. Can an Avaloq Script string literal use double quotes?
2. Does Avaloq Script have OUT or IN OUT parameters?
3. What data-effect label does `new mem_doc_bp(...)` get, and when is the business object actually created?

Expected answers: (1) yes, KB-LANG-08; (2) no, value parameters only, KB-LANG-38, with a CONFLICT on reassignment in KB-LANG-39; (3) ORDER (create); the object is created only when the order is finalised by a workflow action (C_data.md, KB-DATA-46/48 and the C11 table). If your answers differ, show where you looked. Do not answer from memory.

## 6. Commit
Create a branch `chore/avaloq-kb-skill`. Commit only the files from steps 1 to 3 with the message `Add avaloq-kb skill, CLAUDE.md pointer and KB logs`, and push the branch. Open a pull request only if this repo normally uses them. Do not merge.

## 7. Report and stop
Report:
- the file check table
- whether CLAUDE.md was created, appended or left unchanged
- the packaging check result
- the smoke test answers with KB ids
- the branch name

Then stop. The next task is the pattern work in `docs/avaloq_kb/KB_PATTERN_DEV_METAPROMPT.md`, starting at K1 (K0 is this setup). Wait for the user to start it.

---

## How the files get here (for the person, not for Claude)
- Easiest: unzip `avaloq-kb-bundle.zip` and copy its contents (the `.claude` folder, the `docs` folder and this file) into the root of your local clone. Then run this prompt; step 6 commits and pushes.
- If you upload through the GitHub website instead: macOS Finder hides folders whose names start with a dot, so `.claude` may be skipped. Press Cmd+Shift+. in Finder to show it before you drag the folders in, or upload the unzipped `avaloq-kb-bundle` folder as is; step 1 then moves the files into place.
