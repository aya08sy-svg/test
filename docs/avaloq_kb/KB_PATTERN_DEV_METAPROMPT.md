# Metaprompt: install the Avaloq KB skill and use it to develop audit patterns

Paste this into company Claude (Claude Code in the audit tool repo). It works alongside COMPANY_CLAUDE_METAPROMPT_v2.1 and does not replace it. All of v2.1's packaging rules still hold: no new runtime dependencies, no data files at runtime, explicit registry, frozen exe with no model.

---

## Role
You develop audit patterns (validators) for the Avaloq audit tool. Your Avaloq knowledge comes from the `avaloq-kb` skill, which holds 382 entries verified against the official Avaloq docs. Each entry has an id such as `KB-STD-31`, a file and page citation, and a basis of STATED, INFERRED or CONFLICT. General PL/SQL intuition is NOT a source.

## K0. Install (once)
1. Copy the folder `avaloq-kb/` to `.claude/skills/avaloq-kb/` in the repo. It contains `SKILL.md` and `references/`. Commit it. The folder is dev-side only: never import it from engine code, and never bundle it into the exe.
2. Add these lines to the repo `CLAUDE.md`, so every session and subagent knows the skill exists even when its description does not trigger:
   ```
   ## Avaloq knowledge
   For any Avaloq Script syntax, DDIC, accessor, order, effect, standard or performance question, use the avaloq-kb skill (.claude/skills/avaloq-kb). Cite KB ids in doc_ref. KB gaps are UNKNOWN, never guessed. Subagents: read .claude/skills/avaloq-kb/SKILL.md first.
   ```
3. Smoke test: ask yourself 3 questions and answer only from the skill, citing ids. (a) Can a string literal use double quotes? (b) Does Avaloq Script have OUT parameters? (c) Which effect label does `new mem_doc_bp` get? Expected: (a) yes, KB-LANG-08; (b) no, value parameters only, KB-LANG-38/39 with a CONFLICT on reassignment; (c) ORDER(create), per C11 in C_data.md. If any answer comes from memory rather than the skill, fix the CLAUDE.md pointer before going on.
4. STOP and report: skill path, smoke test answers with ids.

## K1. Grammar alignment (before any new rule)
The KB records where the official grammar is wrong or incomplete. For each item below, write a Lark parser test with a minimal snippet, run it against the current grammar, and then confirm the behaviour on real corpus files (count occurrences with file:line).
- Double-quoted strings, and doubled-quote escapes (KB-LANG-08)
- `#` and `$` inside identifiers (KB-LANG-06, a CONFLICT the code wins)
- Expression precedence: `x is not null and x > 0`, `i between 1 and 100`, `not p or q` (KB-LANG-66/68). Use PL/SQL-style precedence, not the literal EBNF.
- Quoted keyword path segments `node."as".val_nr` (KB-LANG-09)
- `exception when others then ...` after a method body (KB-LANG-57/58)
- `[script 1.0]` / `[Script 1.0]` header, and `/*postp_start*/ ... /*postp_end*/` directives (KB-LANG-16, KB-STD-09)
- Named arguments `name => value`, parameter defaults `i_x text := null`
Output: `docs/kb_grammar_check.md` (item | KB id | grammar result | corpus count | action). Fix only grammar defects that real code proves. STOP and report.

## K2. Pattern development loop (one rule at a time)
Candidate sources, in priority order: REQUIRED_RULES.md (for example ACC-01/ACC-02), the D6 catalogue in D_standards.md, and new ideas from the team. For each candidate:

1. **Ground it.** Look the rule up in the KB with INDEX.md. Record the KB ids, the Basis, and the doc's own bad/good example if there is one. With no KB entry, the rule is HOUSE: name an owner, or drop it.
2. **Check the corpus.** Count how often the pattern and the counter-pattern occur in real sources, with sample file:line. For a CONFLICT or INFERRED entry, the counts decide the rule; record them. The KB itself warns that the docs' examples break their own naming and format rules, so style rules default to info or warning.
3. **Write the RuleSpec** in the existing format, with:
   - `doc_ref: KB-xxx-nn` (one or more ids)
   - `basis: STATED | INFERRED | CONFLICT-resolved-by-corpus`
   - a severity justified by the KB entry and the corpus counts
   - `effects:` when the rule depends on data effects, using the C11 labels (READ/CREATE/MODIFY/DELETE/ORDER/SIDE_EFFECT/PURE/UNKNOWN)
4. **Fixtures first.**
   - Turn the KB's bad and good examples into positive and negative fixtures, copied verbatim. Where the KB marks a doc typo, include a corrected copy.
   - Add at least 2 corpus positives and 2 corpus negatives.
   - Add edge cases from the KB entry's Means/Audit use lines.
5. **Implement** the validator in the explicit registry, reusing the engine's facts (AST, accessor facts, effects). Do not open files or call a model at runtime.
6. **Prove it.**
   - Fixtures pass.
   - The 20-file batch comparison runs: findings before vs after, with every new finding explained.
   - Run the overlap check against existing validators: same node and same intent means merge or mark overlap.
7. **Record** the rule in the ledger: rule id, KB ids, corpus counts, fixture names, overlap result.

Start with these high-value KB rules unless REQUIRED_RULES says otherwise:
- **Repeated row access** (ACC-01): the same root plus key read again, with a call between the reads that is not `db_side_effect_free` (KB-STD performance entries, C_data repeated-access entry). The key is root plus arguments, not plus attribute. Parameter and variable keys are symbolic.
- **Loops:** `for i in 1..l.count` with `.get(i)` over list fields (n² vs n), and loop-invariant `lookup.*` or `session.*` calls inside loops.
- **Correctness:**
  - `case` without `else` (ORA-06592)
  - session values cached in package constants or `b_` variables
  - `deterministic` or `db_side_effect_free` on code that stores or runs OBJ/DOC/MEM_DOC actions
  - `when others` that swallows exceptions without re-raising
- **Performance:**
  - `.store` in loops or report `on level_*` handlers
  - `iff` where typed `iffb`/`iffd`/`iffn` exist
  - `class('x').id` instead of `class_id('x')`
- **Commit:** `session.commit` / `session.rollback`, which the KB warns about in message processing.

## K3. Effects table
Seed `generated_effects.py`, or the existing effects module, from C11 in C_data.md. Use one row per construct, with the KB id in a comment. Key facts:
- Object CREATE/MODIFY happens only through orders.
- Business objects have no DELETE.
- `doc_*.attach_postit` and `doc_*.do_wfc_action` are the documented writes on stored orders.
- `no_commit` defaults to '+' on `mem_doc_*.new`.
Constructs not in C11 stay UNKNOWN until labelled by the dual-reader flow in AVALOQ_DATA_EFFECTS_METAPROMPT.md.

## K4. Keeping the KB honest
- Never edit `references/` silently. When real code or newer docs contradict an entry, add a row to `docs/KB_CORRECTIONS.md`: KB id, what the KB says, the evidence (file:line or doc page), the proposed fix. The KB maintainer applies it and bumps the skill version.
- When a question has no KB answer, add it to `docs/KB_OPEN_QUESTIONS.md` with the Qnn number if one fits. These drive the next documentation downloads; GAPS.md ranks them.

## Gates
- K0: the smoke test answers cite KB ids.
- K1: grammar check table written, corpus counts present.
- Every new rule has doc_ref, basis, corpus counts, KB-derived fixtures, a batch comparison and an overlap result.
- No KB content, path or loader is reachable from the shipped exe. The only exception is doc_ref strings in rule metadata, so the report can show which standard a finding enforces.
