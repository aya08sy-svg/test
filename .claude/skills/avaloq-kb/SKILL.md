---
name: avaloq-kb
description: Verified Avaloq Script knowledge from the official docs (syntax, types, DDIC accessors, orders, data effects, coding standards, performance, ice API, ATF). Use whenever reading, parsing, explaining, auditing or writing Avaloq Script, or designing a validator, grammar rule or effect label.
---

# Avaloq KB (verified from official Avaloq docs)

Every entry in `references/` cites an official doc file and page and was checked by a second reader. Entry ids look like `KB-LANG-08`. The KB OVERRIDES general knowledge and older prompt assumptions about Avaloq. PL/SQL intuition is often wrong here.

## How to use it
1. Grep `references/INDEX.md` for the topic (one line per entry: id | title, grouped by file and sub-section). Open only the file and entries you need. Do not load whole files by default.
2. Quote the KB id you rely on, in any rule spec, fixture, code comment or answer: `doc_ref: KB-STD-31`.
3. Basis matters. STATED = the doc says it. INFERRED = our reading. CONFLICT = two official pages disagree, so never encode a CONFLICT as a hard rule without checking real corpus code first (count both forms and record the result).
4. Not in the KB means UNKNOWN, not false. Say so, check `references/GAPS.md`, and do not invent API names, DDIC fields, workflow actions or intl_ids. Write `UNKNOWN(KB gap)` and add a line to the project's open-questions file.
5. When real code contradicts a KB entry, the code wins for parsing (the grammar must accept what compiles). Record the case as a KB correction with file:line evidence, so the KB maintainer can update the entry.

## Files
- `references/INDEX.md`: id | title for all 382 entries. Start here.
- `references/A_language.md`: lexical rules, package structure, declarations and parameters, statements, expressions and precedence, PL/SQL interop.
- `references/B_types.md`: base types, ID vs record types, casts, collections with full method tables, records, collection performance.
- `references/C_data.md`: DDIC, data access layers, accessor syntax, READ / CREATE / MODIFY, orders, workflows, commit, banking dates, object model. Section C11 is the construct -> effect label table.
- `references/D_standards.md`: coding conventions, naming, correctness, performance. Section D6 is a 71-rule candidate catalogue (rule id | rule | detection hint | severity | cite | basis).
- `references/E_tooling.md`: source lifecycle, ice Workflow API (PL/SQL), Avaloq Test Framework, compiler and ASMD markers.
- `references/F_verify_matrix.md`: Q01-Q38 verdicts and corrections to the project metaprompts.
- `references/GAPS.md`: open questions and the docs still to download.

## What a model must know first (from each section)

### A_language
1. Avaloq Script looks like PL/SQL, but it is a separate language. Area-specific compilers translate it to PL/SQL, and it has no direct table access. Data is read and written through DDIC dot-paths (`cont.pos_list`, `obj_bp(id).name`) (KB-LANG-82, -71, -83).
2. `"..."` is a string literal, just like `'...'`; you escape a quote by doubling it. A quoted segment is an identifier only after a `.` in a data-access path (`node."as".val_nr`) (KB-LANG-08, -09).
3. Identifiers contain `#` and `$` in practice (`cont#pos_id`, `mba$dwh`, `pkg#.proc`), even though the published EBNF forbids them. The docs say upper and lower case letters are "distinct", while the convention says all code is lowercase (KB-LANG-05..06, -03).
4. A source is `[script 1.0]` + `script package <name> is` ... `end <name>;`. There is no spec/body split. Every method repeats its name after `end` (KB-LANG-16..20).
5. Only value parameters exist: no `in`/`out`/`in out`. Whether a parameter can be reassigned is a CONFLICT in the docs. Collections are passed BY REFERENCE (compiled to `in out nocopy`), so callee changes are visible to the caller (KB-LANG-38..39, -44).
6. Declarations have no colon: `l_x number := 0;`, `c_x constant text := 'a';`. A variable with no default is null. Types have no length or precision (`text(10)` and `number(5,2)` are invalid) (KB-LANG-29..34).
7. Booleans are stored as one character, `'+'`/`'-'`. Code compares `x.contains(v) = '+'` as well as using `true`/`false` (KB-LANG-11).
8. The published expression EBNF puts `and` at `*` level and `or`/`||` at `+` level, and it cannot parse its own examples. Parse with PL/SQL-style precedence instead (KB-LANG-66, -68).
9. `ident(expr)` can be a DDIC type cast (`obj_bp(l_id)`) and not a call. The compiler checks neither casts nor assignment compatibility (KB-LANG-75, -78).
10. A `case` without `else` raises ORA-06592 at runtime. Methods may end with `exception when others then err.raise_fa('<pkg.method>', ...)`, which the method EBNF does not show (KB-LANG-50, -57..58).


### B_types
1. Base types are exactly `boolean | text | long | number | date`. There is no `raw`, no `clob`, no `text(n)` or `number(p,s)`.
2. `boolean` is stored as one character: `'+'` = true, `'-'` = false. Methods like `contains`/`exist`/`is_equal` return `'+'/'-'`, so `x.contains(v) = '+'` is a normal boolean test.
3. `text` holds up to 4000 chars; `long` holds up to 32,000 chars and maps to `varchar2(32000)` (not a CLOB). `date` holds date and time up to 31.12.4712 AD.
4. `id <ddic>` / `id table <table>` holds only a primary key and is "lighter and quicker". A bare DDIC name (`obj_bp`) is a record/DDIC type giving access to fields and methods.
5. Casts `obj_bp(x)` and `list(...)`/`set(...)` are NOT checked by the compiler, and assignment compatibility is said not to be checked. A compiler pass is no proof of type correctness.
6. Collections are `list<V>`, `set<V>`, `map<K,V>` (since 5.3, compiler framework only, not in REP PRINT or runtime-compiled script). Set elements and map keys are only number, text or DDIC/id types (no date).
7. Collections are auto-initialised and can never be null (`l_list := null` is a compile error; use `.clear`). `set.add(null)` / `map.put(null, ..)` throw `code_ap_err.adding_null_not_supported`.
8. Collection assignment `:=` deep-copies; collection parameters are passed by reference (`in out nocopy`), so a callee can modify an `i_` collection.
9. Only `.store` (and MEM_DB_LIST `store_list`) writes to the database; `.load(id)` and the MEM_DB_LIST constructor with an id read from it. Every other collection method works in memory. `map` has no store/load.
10. MEM_DB_LIST_* and MEM_TAB need manual memory release (`remv_after`, `obj_tab.remv`). Some official examples are wrong (`list.empty<K,V>` for maps, set.subtract examples that repeat union); do not copy them.


### C_data
1. Avaloq Script has no direct table access: every data read or write goes through a data dictionary (DDIC). The DDIC root name tells you the layer: `obj_*` = objects on disk (OBJ), `doc_*` = stored orders (DOC), `mem_doc_*` = order in memory (MEM DOC), plus `code_*` code tables, `dtm_*` datamarts, `mem_msg_*` messages, `<ns>$base_par_*` base parameters, and the always-present `session` and `lookup`.
2. OBJ and DOC are read-only layers. A read such as `obj_bp(l_bp_id).name` is a READ of OBJ_BP keyed by `l_bp_id`; it never changes data.
3. Objects are changed only through orders: a static data order (MEM_DOC `new` constructor) holds the change in memory, and a workflow action saves or finalises it. Only at finalisation is the object created or modified in OBJ. So object CREATE/MODIFY = ORDER first, CREATE/MODIFY as its consequence.
4. A `set` on a `mem_doc_*` field modifies an order in memory, not the object. Documented direct writes outside MEM DOC are few: `doc_*.attach_postit` (locks the order) and `doc_*.do_wfc_action` (workflow action or status change without loading the order).
5. Objects are never deleted (there is no delete order type). Data is hidden, then wiped. A cancel of a booked transaction is a new reversal order, not a DELETE.
6. `T(v)` (e.g. `obj_bp(x)`) is an unchecked DDIC cast, not a function call. Dot paths walk record fields to further DDICs, must end in a scalar (else possibly null), and keyword segments are quoted (`node."as".val_nr`).
7. `session.commit` / `session.rollback` exist but the docs warn against them, especially in message processing. The MEM_DOC_BP `new` constructor has `no_commit` with default `'+'` (true); what it does is not documented.
8. Every order has a business type (code table META_TYP) and an order type (code table CODE_ORDER_TYPE). Static data orders have only Create and Modify types. One workflow per business type.
9. Repeated attribute reads of the same row: the compiler can merge them into one select unless a call that might write sits between them (then one select per attribute). The docs say nothing about a runtime object cache.
10. Banking dates: TRX (order created) and DONE (verified, 21.12.4712 until then) are bank dates; VAL/BOOK are rule-calculated settlement dates; PERF is for performance. Bank days are not value days. `session.today` is the official current-date member; `lookup.date` does date arithmetic.


### D_standards
1. Avaloq's coding and naming conventions are recommendations ("should"; a few say "must"). Avaloq's own doc examples break them often. Report breaches as warnings or info, not errors (KB-STD-12, KB-STD-26).
2. Layout: section comments are 78-dash lines around `-- CAPITALS`. Block comments are `---- CAPITALS ----` with a blank line before them. Line comments are trailing `-- lower case`. Indent 2 spaces, never tabs, with a 2-space margin. `[Script 1.0]` and `script package` start in column 1.
3. All code is lower case. The lexer treats upper and lower case letters as distinct, so the rule is more than cosmetic. Exactly 78 dashes is the rule, but every doc example has 73-76 dashes, so match separators loosely.
4. Name prefixes: `c_` constant, `l_` local, `b_` body/package variable (lives for the session), `i_` input parameter. Booleans start with a predicate (`is_`, `do_`, `has_`, `enbl_`, `dsbl_`) after the prefix. Names are singular, built from glossary abbreviations, most significant element first. Foreign keys are named `<target table minus obj_/code_/meta_>_id`.
5. Correctness rules that are stated in the docs and checkable on the AST alone: a `case` with no `else` raises ORA-06592 at runtime. Never cache session values (`session.today`, base parameters) in constants or `b_` variables. Lists returned by DDICs can only be used directly in a `for` loop. `deterministic` and `db_side_effect_free` are unchecked promises, so misuse is a real bug.
6. Performance rules, each with a documented bad/good pair. `case` is about 10% faster than an `elsif` chain. `iff` is 2-3x slower than `iffb` and 10x slower than `iffd`. Avoid implicit type conversions. Hoist loop-invariant calls out of loops. Use `class_id('x')`, not `class('x').id`. Use `with` for long paths on memory DDICs. Use `for x in list`, not an index loop with `get` (n² vs n).
7. The most important rule: several attribute reads on the same DDIC row, interleaved with a call that might write, cost 3 selects instead of 1. Avaloq's own ASMD marker for this reads "Missed performance optimization opportunity". The fix is to read into locals first, or to mark the callee `db_side_effect_free`.
8. Collections: assignment copies, parameters are passed by reference (`in out nocopy`), and each `.store` writes to the DB. Avoid collection copies and repeated `.store` calls in loops or report `on level_*` handlers.
9. Exceptions: the house idiom is `exception when others then err.raise_fa('<pkg>.<method>', ...)`. One official example swallows errors with `when others then return null`, so never cite it as compliant code.
10. Tests (ATF): every `it_*`/`ut_*` procedure in a test package runs as a test case. `assert` logs the result and continues; `require` stops the procedure. Test code must meet production quality and be rerunnable.


### E_tooling
1. **ice Workbench** is Avaloq's IDE and source lifecycle tool: revision control, parallel development, guided workflow, build and deploy (KB-TOOL-01).
2. Work hierarchy: **solution > stream solution (one per release stream) > task > change > checked-out sources**. Sources sit in **application > module > component** (KB-TOOL-03).
3. A customer task moves Ready To Solve → Check In → Ready To Audit → Audit Code (4-eye, auditor must not own the changes) → Audited → Send To Integration → Integrated / Integration Rejected → … → Solved (KB-TOOL-05, -06). The chain order is INFERRED. The action/start-status table is STATED.
4. **ADAI's Integration Robot** installs the task, checks invalids against a test policy, runs construction tests, then sets the task to Integrated or Integration Rejected (KB-TOOL-09).
5. The **ice Workflow API is PL/SQL on the ice Server** (`e.env_*_ext#.<object>#<verb>`), meant for third-party integration of **development tasks**. It is NOT a banking-order API. Banking orders use the DDIC method `do_wfc_action` (KB-TOOL-16, -17).
6. Commit rule: `env_issue_ext#` and `env_solution_ext#` commit or roll back themselves. `env_task_ext#` does not, so the caller must `commit;`. The `eval` ref cursor must be closed by the caller (KB-TOOL-20, -24).
7. **ATF (Avaloq Test Framework)** is the official test framework, not utPLSQL. A test is a SCRIPT PACKAGE or PL/SQL PACKAGE plus one XML **TEST SCRIPT** source, kept in the **ATS** application (KB-TOOL-40, -42, -43, -46).
8. ATF runs every procedure named `it_*` / `ut_*`, in source order. `it_setup` runs first and `it_teardown` runs last. **`assert` logs and continues; `require` stops the procedure** (KB-TOOL-49, -50).
9. Tests are selected by `intg_relv` (always / module / compo / no) against the components a task touches. Results are logged in ATS_RUN / ATS_SCRIPT_RUN / ATS_SCRIPT_RUN_RES and read through ATS_RES_V (KB-TOOL-62, -66, -77, -78).
10. Area-specific compilers translate Avaloq Script to PL/SQL (STATED in G1; CONFLICT note in KB-TOOL-79). **ASMD** markers and compiler warnings are Avaloq's own static checks. ice auto-formats Avaloq sources on save (KB-TOOL-82, -84, -85, -88).

---
