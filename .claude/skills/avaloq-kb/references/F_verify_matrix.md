# F. VERIFY matrix and metaprompt corrections

Inputs: `verified/G1_verified_partA.md`, `G1_verified_partB.md`, `G2_verified.md`, `G3_verified.md`, `G4_verified.md`, `G5_verified.md`, `G6_verified.md`. The verifiers' corrected marks are used. No entry in any file was REJECTED. Questions come from `metaprompt/AVALOQ_DOCS_QUESTIONS.md`. Assumptions come from the `[VERIFY-Qnn]` tags in `metaprompt/AVALOQ_AUDIT_METAPROMPT.md` (cited as `AUDIT Lnnn`) and from the concrete statements in `COMPANY_CLAUDE_METAPROMPT_v2.md` (`V2 Lnnn`), `AVALOQ_DATA_EFFECTS_METAPROMPT.md` (`EFFECTS Lnnn`) and `ACC_REPEATED_ACCESS_FIX_PROMPT.md` (`ACC Lnnn`).

**Cite shorthand.** `<name> pN` means `source_text/paged/text/<name>.txt`, page marker N, for example `declarations-in-avaloq-script p5`. Paths that start with `layout/` are relative to `source_text/` and are cited by page where the file has pages. Entry ids such as G1-36 point to the verified files.

**Verdicts.**
- CONFIRMED: the docs answer the question, and any metaprompt assumption holds.
- CONTRADICTED: the docs say something different from the assumption (or from the question's presupposition).
- PARTIAL: part of the question is answered; the rest needs more docs.
- EXTENDED: answered, and the docs add facts the metaprompt does not have.
- NOT ANSWERED: nothing in the folder answers it beyond scattered names.

**Tag coverage in AVALOQ_AUDIT_METAPROMPT.md.**
- Tagged: Q01, Q02, Q05, Q08–Q12, Q14–Q18, Q24–Q26, Q29–Q32 and Q37. Q19–Q23 are tagged only through the range on L463.
- Never tagged: Q03, Q04, Q06, Q07, Q13, Q27, Q28, Q33–Q36 and Q38. For these, the verdict judges whether the docs answer the question. Where an untagged question still touches a concrete assumption, that assumption is named (for example Q07 and `Param.mode`).

**Verdict counts (38):** CONFIRMED 3 · CONTRADICTED 1 · PARTIAL 23 · EXTENDED 5 · NOT ANSWERED 6.

---

## 1. Per-question matrix

### A. Source object model

**Q01: Complete list of source types and what each contains.**
- Tag: AUDIT L463 "All names, boundaries and arrows in this table are `[VERIFY-Q01, Q05, Q15, Q18..Q24]`." (the §8.2 family table).
- Verdict: **PARTIAL**.
- The docs name these source types: script package, REP PRINT, REP FILE, REP SCREEN, INTF DEF, CODE TAB, MIGR, TEST SCRIPT (XML, schema-validated), PL/SQL PACKAGE / PACKAGE BODY, TRIGGER, DSL sources, XSD sources (COM.AVALOQ.*), and generated T# packages. Each script area has its own compiler. There is no full inventory.
- Evidence:
  - G1-03 (getting-started-with-avaloq-script p1)
  - G1-57 (coding-conventions p3-4)
  - G2-01 (what-are-avaloq-script-expressions p1)
  - G2-43 (data-types p30-31)
  - G2-45, G2-50 (data-types p32-34, p39)
  - G2-57 (what-are-avaloq-script-packages p1)
  - G5-63, G5-65, G5-70 (layout/04-test-framework/pages/02a p1-2, 02b p1-2)
  - G5-95 (04a_Code_coverage p2)
  - G6-85
- Change the metaprompt to say: "Seed `source_types.yaml` with the documented type names (SCRIPT PACKAGE, PL/SQL PACKAGE, PACKAGE BODY, TRIGGER, REP PRINT/FILE/SCREEN, INTF DEF, CODE TAB, MIGR, TEST SCRIPT, DSL, WFD, XSD). The §8.2 'families' stay hypotheses until 'Summary of source types' is downloaded."

**Q02: Packages, layers, namespaces, mandatory naming.**
- Tags:
  - AUDIT L331 "`layer: str | None   # standard/custom [VERIFY-Q02]`"
  - AUDIT L443 "custom code must not modify these, only extend via hooks/parameters"
  - AUDIT L444 "the bank's own sources, usually with a naming prefix"
- Verdict: **PARTIAL**.
- Documented: the `<ns>$` namespace prefixes (AVQ$, MBA$, MDB$, `<client key>$`). Sources are organised as application > module > component > source. ATS application sources never reach production. Script packages are linked with `import` and referenced as `<pkg>.<elem>`.
- Not in the folder: the standard-versus-custom rule. The TOC topic "Overriding and replacing kernel sources" suggests overriding is possible.
- Evidence:
  - G1-11 (declarations-in-avaloq-script p6)
  - G1-86 (layout/02-techbase/02_05; coding-conventions p4)
  - G3-14 (what-are-data-dictionaries p3-4)
  - G5-56 (01a p1)
  - G5-66 (02b p1)
  - G5-86 (02e)
  - G5-104 (02b p1)
  - G6-15
- Change the metaprompt to say: "In Avaloq docs, 'layer' means the data access layers OBJ, DOC and MEM_DOC. Derive source ownership from the `<ns>$` prefix and the ice application and component. Rename `SourceRecord.layer` to `owner_ns`. Keep 'must not modify standard sources' as an assumption until 'Overriding and replacing kernel sources' is read."

**Q03: Export to files: extensions, directory layout, metadata header.**
- Tag: none.
- Verdict: **NOT ANSWERED**.
- Known: the source text starts with a pre-compiler header `[Script 1.0]` / `[script 1.0]` that declares type, version and name. One official ATF example has no header. An "ice Import Export utility" exists, but its file format is not documented.
- Evidence: G1-57 (coding-conventions p3-4), G2-58 (what-are-avaloq-script-packages p1-3), G6-01 (data-types p41), G5-02 (layout/03-ice-workflow/AvaloqICE/avaloq_ice_workbench p1).
- Change the metaprompt to say: "The P0 survey must detect headers case-insensitively (`[script 1.0]`) and must not fail a file that has no header."

**Q04: Source lifecycle and compile errors that block activation.**
- Tag: none.
- Verdict: **PARTIAL**.
- Documented: the ice task lifecycle: Ready To Solve > Check In > Ready To Audit > Audited/Rejected > Integration > Solved. A mandatory 4-eye code audit applies per component. Sources are checked out into changes. Releases ship as installation packages. Under the test policy, source, rule and migration "invalids" can reject a task. There is no list of compile errors.
- Evidence:
  - G5-01, G5-03 (avaloq_ice_workbench p1; ice_workflow_api_introduction p1)
  - G5-24, G5-27 (workflow_api_05 p1; D2_Constants)
  - G5-34 (D4)
  - G5-57, G5-59 (01a p1-2)
  - G5-97 (04b p1)

**Q05: Which source types call which; official where-used export.**
- Tags:
  - AUDIT L194 "`triggers` (workflow/order type to script, `[VERIFY-Q05, Q18]`)"
  - AUDIT L197 "If Avaloq offers an official where-used/dependency export `[VERIFY-Q05]`, compare on a sample"
- Verdict: **PARTIAL**.
- Documented: `import` / `import native` lines give code edges. Script calls PL/SQL through native import. INTF DEF uses a script package that wraps T# for PL/SQL. Rule loader tables, CODE TAB and INTF DEF embed script expressions.
- ice exposes only change-level and version-level dependencies (`env_stream_solution_chg_dep_intf_v`). No code-level where-used export is documented.
- Evidence:
  - G1-86 (02_05)
  - G2-01 (what-are-avaloq-script-expressions p1)
  - G2-46 (data-types p34-36)
  - G2-50 (data-types p39)
  - G5-48 (E7 view)
  - G5-62 (02a p1)
- Change the metaprompt to say: "No official code-level where-used export is documented in the folder. Build edges from `import`, `import native` and expressions embedded in rule loader, CODE TAB and INTF DEF sources. ASMD 'Overview of the ASMD public API' is the candidate comparison source (not downloaded)."

### B. Avaloq Script language

**Q06: Formal grammar / EBNF.**
- Tag: none.
- Verdict: **PARTIAL**.
- Published EBNF fragments exist: lexical rules, declarations, methods, expressions and records. They are incomplete and partly wrong:
  - The ident rule omits the `#` and `$` that every example uses.
  - The string EBNF has a typo.
  - Parameter defaults, named arguments and the exception section are missing.
  - The expression EBNF puts `and` at Term level and `or`/`||` at SimpleExpression level, so `a = 1 and b = 2` and `i between 1 and 100` do not parse literally. The official examples use PL/SQL precedence.
  - There is no statement grammar.
- Lexical facts that are settled: letters are "distinct" by case; strings use single or double quotes; comments are `--` and `/* */` and do not nest; keywords inside data paths must be quoted.
- Evidence:
  - G1-06, G1-08, G1-10, G1-11, G1-13, G1-22 (language-fundamentals p1-4)
  - G1-35, G1-39 (declarations-in-avaloq-script p5; hints-and-tips-on-using-avaloq-script p8-9)
  - G2-09 (avaloq-script-expressions p3)
  - G2-16, G2-17 (avaloq-script-expressions p6-7)
  - G2-65 (declarations-in-avaloq-script p7; hints-and-tips p4; avaloq-script-expressions p1)
  - G2-66 (language-fundamentals p3)
  - G6-77, G6-84
- Change the metaprompt to say (add to P2): "Use the published EBNF only as a starting point. Do not encode the expression precedence literally. Use PL/SQL-like precedence, from high to low: unary +/-; `* / mod`; `+ - ||`; comparisons, `is [not] null`, `[not] like`, `between..and`, `in`; `not`; `and`; `or`. Identifiers may contain `#` and `$`."

**Q07: Function/procedure declaration, parameters, in/out modes, return, visibility.**
- Tag: none. The assumption it touches is AUDIT L168 "parameters (name, type, mode)" and L341 `class Param ... mode: str | None`. The same assumption appears in EFFECTS L180-183 ("record per parameter: mode"), EFFECTS L252 (E-Q9) and ACC L30-33, L85-87, L121-122.
- Verdict: **CONTRADICTED**.
- "Avaloq Script only supports one kind of parameter: value parameters". The EBNF is `FormalParameter = ident Type`, with no mode keyword.
- What exists instead:
  - defaults (`i_text text := null`; collections only `:= default`)
  - named arguments `name => value`
  - visibility `public | private | protected` and `final | abstract`
  - `deterministic | db_side_effect_free` as alternatives, not stacked
  - the routine name repeated after `end`
- Collections are passed by reference (`in out nocopy` in the generated PL/SQL), so a callee can change a caller's collection.
- Parameter reassignment is unresolved: the prose says "local constants", but the official `log2` example assigns `x := x / 2`.
- Evidence:
  - G1-30, G1-35, G1-36, G1-37, G1-39, G1-40 (declarations-in-avaloq-script p3-7; hints-and-tips p8-9)
  - G2-11 (avaloq-script-expressions p3-4)
  - G2-35, G2-38 (data-types p25-28)
  - G2-47 (data-types p36-38)
  - G6-16, G6-17, G6-18, G6-21, G6-22
  - G5-102 (02c p3)
- Change the metaprompt to say: "Avaloq Script parameters have no mode. `Param.mode` is the constant 'value' for script sources (keep the field for PL/SQL). Add `Param.default`, `Symbol.modifiers` (deterministic, db_side_effect_free, final, abstract) and visibility. A parameter's value never flows back to the caller. Collection parameters are by-reference."

**Q08: Referencing business objects, attributes and DDIC fields (read, write, lookup).**
- Tag: AUDIT L169 "DDIC/business-object attribute access `[VERIFY-Q08]`".
- Verdict: **EXTENDED**.
- Reads:
  - Dot paths from a DDIC root (`obj_pos.cont.bp.name`). A path must end in a scalar, otherwise it may silently return null.
  - `T(v)` DDIC casts (`obj_bp(l_bp_id).ref_curry.name`). The compiler does not check them.
  - `with <designator> as x do ... end with;` aliases.
  - Parameterised attributes such as `class_id('ass_type')`.
  - ID types (`id obj_bp`, key only, "lighter and quicker") versus record/DDIC types (the whole record). Record fields lead to the next DDIC.
  - List fields with get/count/list operations.
- Writes are DDIC `set` operations. Whether a field allows `set` depends on the field.
- Lookups: `lookup.obj_list`, `lookup.code`.
- Evidence:
  - G1-14, G1-46, G1-73, G1-74, G1-89 (language-fundamentals p2; hints-and-tips p3-4)
  - G2-03, G2-04, G2-05 (what-are-avaloq-script-expressions p2-3)
  - G2-08, G2-12, G2-13, G2-14 (avaloq-script-expressions p3-6)
  - G2-25, G2-26, G2-27 (data-types p3-5)
  - G3-19, G3-21 (what-are-data-dictionaries p5)
  - G3-29 (what-are-data-dictionaries p8)
  - G6-30, G6-31, G6-56, G6-57

**Q09: Code tables and keyword lists; resolving a code to its meaning.**
- Tag: AUDIT L169 "code table/keyword references `[VERIFY-Q09]`".
- Verdict: **EXTENDED**.
- Every code table has a DDIC of the same name. Entries are identified by `intl_id`.
- Forms in use:
  - constant DDICs `mdb_<x>.<intl_id>`, generated at compile time
  - `lookup.code(tab_name =>, val =>, fld_list =>)`, which returns an id
  - `code_x.lookup(intl_id).col`
  - `with code_x(id) as cn do`
- Configuration code tables named in the docs: META_TYP, CODE_ORDER_TYPE, CODE_OBJ_TYPE.
- Evidence:
  - G1-63 (naming-conventions p3)
  - G1-73, G1-82 (hints-and-tips p3, p9-10)
  - G2-07 (avaloq-script-expressions p2-3)
  - G3-15, G3-30 (what-are-data-dictionaries p4, p8)
  - G3-43 (what-are-technical-objects p1)
  - G4-10 (what-is-the-type-of-an-order p1)
  - G5-74, G5-79, G5-80 (02b p5-6; 02c)
  - G6-72

**Q10: Built-in functions and standard libraries.**
- Tag: AUDIT L169 "built-ins `[VERIFY-Q10]`".
- Verdict: **PARTIAL**.
- Documented: the predefined function categories; iff/iffb/iffd/iffn; coalesce, div, abs, sign, concat, regexp_*, sysdate; the SESSION and LOOKUP DDICs (always available, never imported); the UTIL, ERR and FORMAT packages (only a few members attested); the complete list/set/map method tables.
- The full function reference is missing.
- Evidence:
  - G1-70 (hints-and-tips p2)
  - G1-87, G1-88 (02_05)
  - G2-31, G2-32, G2-33, G2-34 (data-types p7-25)
  - G2-59 (what-are-avaloq-script-packages p2)
  - G3-28, G3-29 (what-are-data-dictionaries p7-8)
  - G6-51, G6-53, G6-71, G6-73, G6-74
- Change the metaprompt to say: "Keep two built-in lists: verified (attested in the docs) and unverified. Do not treat `import session` / `import lookup` as required."

**Q11: Error handling (exceptions, messages, logging).**
- Tags:
  - AUDIT L169 "message/error codes `[VERIFY-Q11]`"
  - AUDIT L243 "error handling ... transaction/commit handling `[VERIFY-Q11, Q26]`"
- Verdict: **PARTIAL**.
- Standard pattern: `exception when others then err.raise_fa('<pkg.method>', '<param>', value);`.
- Other mechanisms:
  - `require(cond, text)` (argument order differs from `it.require(text, cond)`)
  - `session.raise_ui_err`
  - `code_ap_err.<name>` codes
  - ORA-06592 from a `case` without `else`
  - ice APIs raise numbers in the 20000 range
  - errors are logged to a LOG table
- There are no rules for declaring or raising exceptions.
- Evidence:
  - G1-69, G1-81 (hints-and-tips p2, p7-8)
  - G1-A-ADD-03 (language-fundamentals p1)
  - G2-32 (data-types p8-14)
  - G2-56 (data-types p42)
  - G3-28 (what-are-data-dictionaries p7-8)
  - G5-40 (D12)
  - G5-100 (04c p2)
  - G5-102 (02c p3)
  - G6-50

**Q12: Embedding or calling SQL/PL/SQL from script.**
- Tags:
  - AUDIT L154 "Embedded languages (SQL inside script, etc. `[VERIFY-Q12]`): treat as opaque spans first"
  - AUDIT L446 "Oracle schema underneath; PL/SQL packages and tables/views"
- Verdict: **PARTIAL** (the L154 premise is partly contradicted).
- Avaloq Script "doesn't provide direct access to the data in Oracle database tables". It is compiled to PL/SQL. DDIC attribute reads compile to `select <attr> from obj_bp where id=...`.
- SQL appears in script only as "a condition in SQL notation" passed as a string, for example `cond => '...' || ...`.
- PL/SQL is called through `import native` with T# / T#R# types, collections passed `in out nocopy`, and no collection-returning functions.
- Evidence:
  - G1-01, G1-03 (getting-started-with-avaloq-script p1)
  - G1-67 (naming-conventions p4-5)
  - G1-82 (hints-and-tips p9-10)
  - G1-B-ADD-01 (hints-and-tips p6)
  - G2-45, G2-46, G2-49, G2-51 (data-types p32-36, p43-44)
  - G6-44, G6-55
- Change the metaprompt to say: "Script sources contain no SQL statements. SQL-shaped text in script exists only as condition strings passed as arguments. Tag those as embedded SQL conditions. SQL statements live in PL/SQL and SQL sources."

**Q13: Pragmas, annotations, directives, special comments.**
- Tag: none.
- Verdict: **EXTENDED**.
- Documented directives:
  - the `[Script 1.0]` pre-compiler header
  - `/*postp_start*/ ... /*postp_end*/` post-processor comments, which the compiler evaluates as deterministic expressions
  - the modifiers `deterministic` and `db_side_effect_free`
- The `--@NoCheck` and `--#ifdef` assumed in V2 L251-252, L371, L453 and REFACTOR_PROMPT_ADDITIONS L119-120 are **not in the docs**. A pre-processor exists only as a TOC title.
- Evidence:
  - G1-22 (language-fundamentals p4)
  - G1-34, G1-42 (declarations-in-avaloq-script p3-5)
  - G1-57 (coding-conventions p3-4)
  - G1-83 (hints-and-tips p10)
  - G6-11

### C. Data dictionary and business objects

**Q14: What the DDIC describes; export and fields.**
- Tag: AUDIT L178 "a complete, queryable DDIC: business object types, attributes, keys, code tables, values `[VERIFY-Q14..Q16]`".
- Verdict: **PARTIAL**.
- A DDIC is the script data-access abstraction. Its parts are fields, methods and an optional constructor. Operations are get, set, count, list, do and add.
- There are three DDICs per object type: `obj_`, `mem_doc_` and `doc_`. Naming prefixes encode the kind of data.
- Fields can be obsolete (compiler warning, later removal).
- Task 923 shows a DDIC and has an Export button, but the export format is undocumented.
- "Business object type" is a legacy name for a DDIC, not a separate entity.
- Evidence:
  - G1-02 (getting-started-with-avaloq-script p1)
  - G3-01, G3-05, G3-07, G3-08, G3-11, G3-14 (what-are-data-dictionaries p1-4)
  - G3-23 (what-are-data-dictionaries p6)
  - G3-A01, G3-A04 (What are data dictionaries.pdf p2-7)
  - G1-B-ADD-01 (hints-and-tips p6)
- Change the metaprompt to say: "DDIC entities are DDICs (one per layer per object type, plus code-table, constant, collection, SESSION and LOOKUP DDICs) with fields, methods and a constructor. 'Business object type' is not a separate kind. Object types come from CODE_OBJ_TYPE."

**Q15: Business object types, object classes, meta types, order types.**
- Tag: AUDIT L463 (Q15).
- Verdict: **EXTENDED**.
- Business types (btts) are defined in code table META_TYP. Order types belong to business types and are defined in CODE_ORDER_TYPE. Static data orders have only the types Create and Modify.
- There is one workflow per business type, and one accounting method per business type.
- Order DDICs are named per business type (`mem_doc_<btt>`, `doc_<btt>`). Object types are defined in CODE_OBJ_TYPE.
- The object model is Person > BP > CONT > POS (MACC is a kind of POS) > ASSET.
- Object classes are not covered.
- Evidence:
  - G3-04 (what-are-data-dictionaries p1)
  - G3-40 (introducing-the-avaloq-object-model p1-3)
  - G3-43 (what-are-technical-objects p1)
  - G3-54 (what-is-a-business-type p1)
  - G4-07, G4-08, G4-10 (what-is-the-type-of-an-order p1)
  - G4-22 (what-are-workflows p2)
  - G4-37 (understanding-banking-dates p6)
  - G6-60, G6-65, G6-66

**Q16: Custom attributes and extensions.**
- Tag: AUDIT L178 (Q16).
- Verdict: **PARTIAL**.
- Objects are extended through keys, classifications and additions. Orders are extended through keys, additions, post-its and links.
- An `extn` / `obj_extn` record DDIC exists. Extension DDICs exist.
- Naming and accessor syntax are not given.
- Evidence:
  - G3-17 (what-are-data-dictionaries p4)
  - G3-46 (common-object-attributes p1)
  - G3-A06 (What are data dictionaries.pdf p3)
  - G4-13, G4-15 (common-order-attributes p1-2)
  - G1-61 (naming-conventions p2)
  - G6-62

**Q17: Tables and views developers may or may not read directly.**
- Tags:
  - AUDIT L169 "SQL table/view access `[VERIFY-Q17]`"
  - AUDIT L446 "PL/SQL packages and tables/views `[VERIFY-Q12, Q17]`"
- Verdict: **PARTIAL**.
- Script never reads tables directly. "Accessing a field directly in a DDIC is always faster than accessing the underlying database table."
- LIST_CHAR, LIST_DATE and LIST_NUMBER cannot be used in script.
- COUNTRY_DAY_OFF and OBJ_STEX_DAY_OFF are legacy tables.
- The ice views are readable by third parties (development repository only).
- There is no allowed or forbidden list for PL/SQL.
- Evidence:
  - G1-01 (getting-started-with-avaloq-script p1)
  - G1-73 (hints-and-tips p3)
  - G1-76 (hints-and-tips p5)
  - G3-38 (what-are-objects p1)
  - G4-45 (understanding-bank-and-value-days p2)
  - G5-08 (workflow_api_01)

### D. Source families

**Q18: Order types and workflows; where custom script hooks in.**
- Tags:
  - AUDIT L194 (Q05, Q18)
  - AUDIT L463 (Q18)
- Verdict: **PARTIAL**.
- Every data change goes through an order whose lifecycle a workflow controls. A workflow is states plus actions (verify, discard, save/finalize).
- Script-level APIs: MEM_DOC `new` constructor; `doc_<btt>.do_wfc_action` (a workflow action on a stored order, status only, without loading the order); `attach_postit` (locks the order).
- There are no WFD source definitions or hook points. `env_task_ext#.task#do_wfc_action` belongs to the ice development-task API, not to banking orders.
- Evidence:
  - G4-01 (what-are-orders p1)
  - G4-18, G4-21, G4-24 (what-are-workflows p1-2)
  - G3-24 (what-are-data-dictionaries p6)
  - G3-25 (what-are-data-dictionaries p7)
  - G3-A02, G3-A03 (What are data dictionaries.pdf p6)
  - G6-64, G6-67
- Change the metaprompt to say: "`triggers` edges come from WFD sources (not yet documented). Banking workflow actions in script are DDIC methods (`do_wfc_action`) on order DDICs. Calls to `env_task_ext#` belong to the ice workflow and are a wrong-API finding in banking code."

**Q19: Rule kinds, structure, triggering.**
- Tag: AUDIT L463 (Q18..Q24).
- Verdict: **PARTIAL**.
- Rule loader tables hold script expressions in COND and STMT columns. Default-field-value rules exist (DOC_DFLT_FLD_VAL_RULE_LD). Order checks are mandatory or optional; failed optional checks produce post-its. A supervisor check can gate progression above a value limit.
- Evidence:
  - G2-01 (what-are-avaloq-script-expressions p1)
  - G4-16 (common-order-attributes p2)
  - G4-20 (what-are-workflows p1)
  - G4-32 (understanding-banking-dates p4, p10)

**Q20: Reports and report writer.**
- Tag: AUDIT L463.
- Verdict: **NOT ANSWERED**.
- Only fragments: the source types REP PRINT, REP FILE and REP SCREEN; collections are unavailable in REP PRINT; `.store` appears in `on level_*` handlers; "Report Writer best practise" is referenced but not in the folder.
- Evidence: G1-85 (hints-and-tips p1), G2-41 (data-types p29-30), G2-43 (data-types p30), G6-86.

**Q21: Interfaces and their mapping code.**
- Tag: AUDIT L463.
- Verdict: **NOT ANSWERED**.
- Only fragments: the source type INTF DEF; inbound messages create orders; commit and rollback are dangerous during message processing.
- Evidence: G2-50 (data-types p39), G4-05 (what-are-orders p2), G3-28 (what-are-data-dictionaries p8).

**Q22: Batch jobs and schedulers.**
- Tag: AUDIT L463.
- Verdict: **NOT ANSWERED**.
- Only fragments: an EOD bank-date switch, and contract-driven recurring orders.
- Evidence: G4-06 (understanding-banking-dates p3), G4-40 (understanding-bank-and-value-days p1).

**Q23: Forms, GUI and screen definitions.**
- Tag: AUDIT L463.
- Verdict: **NOT ANSWERED**.
- Nothing in the folder.

**Q24: Parameter-only sources versus code sources.**
- Tags:
  - AUDIT L445 "configuration data (code tables, classifications, settings) maintained as sources or tables `[VERIFY-Q24]`"
  - AUDIT L463
- Verdict: **PARTIAL**.
- Code tables are text sources with their own syntax (`code table ... tabdef ... row ...`). Keys, additions and classifications code tables live in DSL sources.
- Rule loader tables carry code, so they are not parameter-only. Base parameters exist.
- Evidence:
  - G2-01 (what-are-avaloq-script-expressions p1)
  - G3-30 (what-are-data-dictionaries p8)
  - G3-44 (what-are-technical-objects p1)
  - G4-33 (understanding-banking-dates p4, p11)
  - G5-79 (02c)
  - G5-85 (02d)
- Change the metaprompt to say: "Rule loader tables, CODE TAB and INTF DEF can embed Avaloq Script expressions. Parse them as code-bearing."

### E. Standards, performance, anti-patterns

**Q25: Official coding guidelines with rule ids.**
- Tag: AUDIT L209 "id (keep Avaloq's id if numbered `[VERIFY-Q25]`)".
- Verdict: **PARTIAL**.
- The coding conventions (English comments, lower-case code, 2-space indent and no tabs, 78-dash header line, margins) and the naming conventions exist, but they are **unnumbered** and mix "should" and "must". The ABR/S guideline catalogue is not in the folder.
- Evidence:
  - G1-49..G1-57 (coding-conventions p1-4)
  - G1-58..G1-67 (naming-conventions p1-5)
  - G2-52, G2-53 (data-types p39-40)
  - G5-76 (02c)
- Change the metaprompt to say: "Avaloq rules in the folder have no ids. Assign house ids (for example CC-n, NC-n, HT-n) that cite file and page. Replace them with ABR/S ids when that catalogue is downloaded."

**Q26: Performance best practices.**
- Tags:
  - AUDIT L243 (Q11, Q26)
  - AUDIT L477 "DB access from script (bulk vs. row-by-row `[VERIFY-Q26]`)"
  - AUDIT L481 "SQL or object load inside a loop; repeated identical lookups in one function without caching; unbounded queries without filters; commit inside loops `[VERIFY-Q26]`"
- Verdict: **EXTENDED** (with corrections).
- Documented rules:
  - `case` instead of elsif batteries
  - typed iff
  - no implicit conversions
  - hoist loop-invariant calls
  - use DDIC id attributes (`class_id`) instead of navigating
  - `with` for memory DDICs
  - `for x in list` instead of indexed `get` (n² versus n)
  - do not interleave same-row reads with calls that might write, because it stops select merging (ASMD marker)
  - deterministic functions are evaluated at install time
  - do not cache session values in constants
  - limit `.store`
  - collection assignment copies, parameters pass by reference
  - ID types are lighter than record types
  - modify orders hold write locks
- **Nothing** on commit frequency, bulk processing, unbounded queries or object caching across statements.
- Evidence:
  - G1-64 (naming-conventions p3)
  - G1-68..G1-75, G1-78, G1-79, G1-82, G1-B-ADD-03 (hints-and-tips p1-10)
  - G2-25 (data-types p3)
  - G2-36, G2-38 (data-types p26-28)
  - G2-41 (data-types p29-30)
  - G3-37 (what-are-the-data-access-layers p5)
  - G6-48, G6-83
- Change the metaprompt to say: "Seed performance validators from Hints and tips (cite the page). 'Commit inside loops' and 'unbounded queries' are not Avaloq doc rules (mark them HOUSE). 'Repeated identical lookups' becomes the documented same-row rule (see §2 row 10)."

**Q27: Documented anti-patterns and compiler warnings.**
- Tag: none.
- Verdict: **CONFIRMED**.
- The docs label pairs INEFFICIENT/BETTER, WRONG/CORRECT and OK/NOK.
- Compiler and tool output:
  - the ASMD info marker "Missed performance optimization opportunity"
  - obsolete DDIC field warnings
  - a collection compiler-error table
  - type warnings whose level depends on configuration
- The compiler does **not** check casts or expression compatibility. A non-scalar path silently returns null. A `case` without `else` raises ORA-06592 at runtime.
- Evidence:
  - G1-69, G1-75, G1-78, G1-79 (hints-and-tips p2-7)
  - G2-08 (avaloq-script-expressions p3)
  - G2-13 (avaloq-script-expressions p4-5)
  - G2-19 (avaloq-script-expressions p7-8)
  - G2-44 (data-types p31-32)
  - G2-55 (data-types p42)
  - G3-23 (what-are-data-dictionaries p6)
  - G5-63 (02a)

**Q28: Avaloq static code analysis tool.**
- Tag: none.
- Verdict: **PARTIAL**.
- ASMD markers exist. ADAI reports installation errors, invalids, tests and coverage. ice stores manual review findings.
- The rule list, headless mode and output format are not in the folder.
- Evidence: G1-79 (hints-and-tips p6-7), G5-45 (E4 view), G5-97 (04b p1), G6-84.

**Q29: Upgrade-safety rules.**
- Tags:
  - AUDIT L443 (Q02, Q29)
  - AUDIT L481 "use of internal/non-public standard APIs `[VERIFY-Q29]`"
- Verdict: **PARTIAL**.
- DDIC access is the documented upgrade-stability mechanism. Obsolete DDIC fields give warnings and are later removed. The docs are release-specific. Additions are the sanctioned extension point. The ice API may change.
- There is no public-versus-internal API list.
- Evidence:
  - G1-02 (getting-started-with-avaloq-script p1)
  - G1-91 (how-to-use-docs-avaloq-com p1)
  - G3-23 (what-are-data-dictionaries p6)
  - G4-15 (common-order-attributes p2)
  - G5-06 (ice_workflow_api_introduction)

**Q30: Security rules.**
- Tag: AUDIT L481 "dynamic SQL built from input, missing authorisation checks, sensitive data in logs `[VERIFY-Q30]`".
- Verdict: **PARTIAL**.
- Objects are security-protected uniformly. Commit and rollback can break atomicity. 4-eye principle in orders and ice.
- That concatenated SQL condition strings are an injection point is INFERRED.
- There are no script security rules. The TOC lists "Lookup DDIC code injection risk".
- Evidence:
  - G3-39 (what-are-objects p1)
  - G3-28 (what-are-data-dictionaries p8)
  - G5-24 (workflow_api_05)
  - G1-67 (naming-conventions p4-5)
- Change the metaprompt to say: "For script, 'dynamic SQL from input' means string concatenation into `cond =>` arguments, and Lookup DDIC calls whose arguments are built from input."

**Q31: Naming conventions.**
- Tags:
  - AUDIT L444 (Q02, Q31)
  - AUDIT L481 "naming conventions `[VERIFY-Q31]`"
- Verdict: **CONFIRMED**.
- Prefixes: `c_` constants, `l_` locals, `b_` body variables, `i_` input parameters. Names are singular. Abbreviations come from the official glossary.
- Foreign keys are named `<target>_id`. Code-table constants include the intl_id. Boolean constants start with a predicate. Table aliases have two characters.
- Namespaces use `<ns>$`. Test sources are named `<client key>$IT_...` with `it_`/`ut_` procedures.
- Evidence:
  - G1-58..G1-67 (naming-conventions p1-5)
  - G2-61 (what-are-avaloq-script-packages p3)
  - G5-66 (02b p1)
  - G6-12, G6-14

**Q32: Required documentation and comment headers.**
- Tag: AUDIT L481 "missing header/doc `[VERIFY-Q32]`".
- Verdict: **PARTIAL**.
- Only a 78-dash line before procedure and function headers, plus section comments, is documented. The doc examples show 73-76 dashes.
- Author, changelog and ticket headers are not mentioned.
- Evidence: G1-49, G1-54 (coding-conventions p1-2).
- Change the metaprompt to say: "The only documented header rule is the dash separator line before each procedure and function header. Author, changelog and ticket header rules are HOUSE rules."

### F. Testing and tooling

**Q33: Unit and regression testing.**
- Tag: none.
- Verdict: **CONFIRMED**.
- The Avaloq Test Framework (ATF): TEST SCRIPT XML plus script or PL/SQL packages, `it.assert` / `it.require`, test libraries, parallel groups, integration-relevance selection, coverage through the PL/SQL profiler, and ATS_RUN#.subm.
- Evidence:
  - G5-54 (00_Introduction)
  - G5-62, G5-63, G5-65 (02a, 02b)
  - G5-78 (02c)
  - G5-92 (03b)
  - G5-94 (04a)
  - G5-101 (01a)
  - G6-81

**Q34: API or CLI to compile/validate without deploying.**
- Tag: none.
- Verdict: **PARTIAL**.
- Compilers per area translate to PL/SQL. Validation runs through ADAI on a built instance. ATS_RUN#.subm runs tests headless. A debug-mode compile exists.
- There is no standalone compiler CLI. The TOC lists "API: script#" and "API: src_intf#".
- Evidence:
  - G1-03 (getting-started-with-avaloq-script p1)
  - G2-44 (data-types p31-32)
  - G5-57 (01a p1)
  - G5-92, G5-93 (03b)

**Q35: IDE, language server, syntax definitions.**
- Tag: none.
- Verdict: **PARTIAL**.
- ice Workbench is the development tool. "ice" applies the formatting conventions on save. An SDK exists.
- No grammar file is in the folder. The TOC lists ASMD "LSP languages setup" and the "AvqScript Model".
- Evidence:
  - G1-55 (coding-conventions p2)
  - G5-01, G5-02 (avaloq_ice_workbench p1)
  - G6-77

**Q36: Minimal complete example per source type.**
- Tag: none.
- Verdict: **PARTIAL**.
- Examples exist only for: script package, MEM_TAB example, TEST SCRIPT XML, ATF test package and code-table source.
- Evidence:
  - G2-54 (data-types p41-42)
  - G5-62 (02a p1)
  - G5-63 (02a p1-2)
  - G5-79 (02c)

**Q37: Violating and compliant example per rule.**
- Tag: AUDIT L209 "one violating + one compliant example (from docs `[VERIFY-Q37]`, else synthesised and marked)".
- Verdict: **PARTIAL**.
- Hints and tips gives example pairs for the performance rules. The coding and naming conventions give compliant examples only.
- Evidence:
  - G1-68, G1-71, G1-72, G1-73, G1-74, G1-75, G1-83 (hints-and-tips p1-10)
  - G6-59
- Change the metaprompt to say: "Doc pairs exist only for Hints and tips rules. Every other RuleSpec example is synthesised and must be marked so."

**Q38: Rule overlap and supersession.**
- Tag: none.
- Verdict: **NOT ANSWERED**.
- This needs the ABR/S, ASMD and compiler-check lists, which are not downloaded.

---

## 2. Concrete corrections for the metaprompts

| # | File and location | Current assumption | What the docs say | Cite (entries) | Change to |
|---|---|---|---|---|---|
| 1 | AUDIT L168, L341 (`Param.mode`); EFFECTS L180-183, L252 (E-Q9); ACC L30-33, L85-87 (reset by "out / in-out argument"), L121-122 (`neg_param_passed_as_out`) | Parameters have modes (in / out / in out). A variable passed as out/in-out resets an access key. | "Avaloq Script only supports one kind of parameter: value parameters." The EBNF is `FormalParameter = ident Type` with no mode. Defaults (`:= expr`, collections `:= default`) and named args (`=>`) exist. Collections are passed by reference. **Reassignment conflict:** the prose says "local constants", but the official `log2` example does `x := x / 2`. | declarations-in-avaloq-script p5-7; data-types p25-28; hints-and-tips p8-9 (G1-36, G1-37, G1-39, G2-35, G2-38, G6-16, G6-17) | `mode` = "value" for script. Delete `neg_param_passed_as_out`. ACC reset: a scalar parameter changes only through a direct assignment in the body. Do not assume assignment is impossible until the corpus or compiler shows it. A collection passed to a call may be changed by the callee. |
| 2 | AUDIT P2 L148-152 and V2 Phase 1B L249-252 (grammar and TRANSLATION built "from the docs") | The published grammar can be encoded directly. | The expression EBNF puts `and` in Term (beside `*`) and `or`/`||` in SimpleExpression (beside `+`), both above comparisons. `a = 1 and b = 2` and `i between 1 and 100` do not parse literally, and unary takes a whole Expression. Official examples write `x is not null and x > 0` and `a = sysdate or b = sysdate`. The intended precedence is PL/SQL-like. | avaloq-script-expressions p1, p6-7; declarations-in-avaloq-script p7; hints-and-tips p4 (G2-16, G2-17, G2-65, G2-66) | Add a P2 rule: "do not encode the expression EBNF literally". Precedence from high to low: unary; `* / mod`; `+ - ||`; comparisons / `is null` / `like` / `between..and` / `in`; `not`; `and`; `or`. Confirm on corpus samples, including `not a = b`. |
| 3 | AUDIT L161 (red-team "quotes in strings") and V2 TRANSLATION, with no statement of the string forms; user notes §1.2 | Implicitly PL/SQL strings: `'...'` only, and `"..."` a quoted identifier. | "Strings are ... enclosed in single (') or double (\") quote marks". Opening and closing quotes match, and a quote inside is doubled. The EBNF typo shows `'` twice. Keywords inside data paths are quoted with either kind (`node."as".val_nr`). The ATF examples use `"..."` strings. | language-fundamentals p2; avaloq-script-expressions p3 (G1-13, G2-09, G6-10, G6-58) | Lexer: two string tokens `'([^']|'')*'` and `"([^"]|"")*"`. `"..."` is never an identifier, except as a quoted keyword segment inside a data path. |
| 4 | AUDIT L161 ("keywords as identifiers") and V2 L453 (noise "case"). No case statement anywhere. | Silent, so a PL/SQL habit (case-insensitive) is likely. | "Uppercase and lowercase letters are considered as distinct." The scope (identifiers or keywords) is not stated. "All code must be written in lower case." The docs themselves show `Avaloq` and `exampleProcedure`, and both `[Script 1.0]` and `[script 1.0]`. | language-fundamentals p1; coding-conventions p2-4 (G1-08, G1-53, G6-01, G6-05) | Do not case-fold identifiers when resolving symbols. Report mixed or upper case as a convention finding (CC-5). Decide keyword case handling from the corpus. Match the header case-insensitively. |
| 5 | EFFECTS L12, L42 (`DELETE delete/remove/cancel of an object or record`) | Objects and orders can be deleted or cancelled, labelled DELETE. | "There is no type of order for deleting objects. That's because we can't delete objects." Retention ends only in hide, then wipe. A booked transaction is cancelled by a **reversal order** (a new verified order), and the original event remains. An unbooked order is "Discarded". | what-is-the-type-of-an-order p2; understanding-banking-dates p8-12; what-are-workflows p2 (G4-11, G4-39, G4-21, G6-63) | DELETE never applies to business objects. Hide/wipe = MODIFY through an order. Cancel = ORDER(reverse) or ORDER(discard). Keep DELETE for non-object records only (for example MEM_TAB rows, temp structures). A SQL DELETE on object tables is a high-severity finding. |
| 6 | EFFECTS L40-41 (CREATE "insert, object creation API"; MODIFY "attribute write"), L152 (`ATTR_WRITE_FORMS assignment form -> MODIFY`); AUDIT L224, L481 ("writes to standard-layer attributes") | An attribute assignment on an object is a MODIFY, and creation is a direct API. | "For all types of object, you need an order if you want to change the object's data." OBJ is effectively read-only, with "one or two rare exceptions". Objects are created only when a static data order (MEM_DOC constructor `new`, operation "add") is finalized by a workflow action. Static data orders are only Create or Modify. `set` exists per field, and MEM_DOC record fields are get-only. | what-are-orders p1-2; what-are-the-data-access-layers p3-5; what-are-data-dictionaries p5-7; what-is-the-type-of-an-order p1 (G4-01, G4-04, G4-08, G3-21, G3-25, G3-34, G3-35, G6-64) | `mem_doc_<btt>.new(...)` = ORDER(create or modify). A field write on `mem_doc_*` = MODIFY of order data under that ORDER. A write on `obj_*` = flag (rare or forbidden). Object CREATE/MODIFY is derived from the ORDER finalize action (MODIFY+ORDER), never from a bare assignment. Fix the AUDIT seed rule to "writes outside an order context". |
| 7 | EFFECTS L48 (SIDE_EFFECT "commit or rollback"), L244 (E-Q4) | Unknown which APIs commit. | MEM_DOC_BP `new` has the parameter `no_commit` (boolean, **Default Value '+'**, so no_commit is true by default; screenshot). Its meaning is not documented. The reader's "commits by default" was reversed by the verifier. | what-are-data-dictionaries p7 screenshot (G3-26) | Label constructor calls as non-committing by default (INFERRED, confidence medium). An explicit `no_commit => '-'` is a candidate SIDE_EFFECT(commit) pending docs. Add a DOC_GAP. |
| 8 | AUDIT L243, L481 ("commit inside loops"); EFFECTS L219 ("commit/rollback reached inside a loop or from a library method") | Commit frequency is a documented performance rule. | Avaloq Script commits through **SESSION DDIC methods** `session.commit` / `session.rollback`, with an explicit warning: "Be very careful ... especially during message processing ... atomicity requirements can be broken". There is no rule on commit frequency or bulk commit. In the ice API, env_issue_ext# and env_solution_ext# subprograms commit themselves, while env_task_ext# functions do not and the client commits. This is the development API, not banking. "Transaction" on the order pages means a financial transaction, not a DB transaction. | what-are-data-dictionaries p7-8; layout/03-ice-workflow/AvaloqICE/workflow_api_02/04/05 "Operational notes" (G3-28, G5-09, G6-68; G4 open question 2) | Rule: any `session.commit` / `session.rollback` in script is a finding, more severe in message-processing sources and in loops (cite p8). Make "commit inside loops" a HOUSE rule. Never apply ice-API commit semantics to banking code. |
| 9 | ACC L14-18, L56-62 (key = root + args + attribute); EFFECTS L85-86, L148 (`ACCESSOR_ROOTS root -> entity, key arg position`); V2 L170-174 | `obj_bp(<expr>)` is an accessor call with a key argument, and a chain is one access. | `T(v)` is a **DDIC type cast**: it interprets v (an id, a DDIC value, even a number) as a DDIC of type T. "Neither of these constraints is checked by the compiler". `x_id` fields are ID types (key only, "lighter and quicker"). `x` fields are record types, and a dot through them reads **another** DDIC. Paths must end in a scalar. `with obj_bp(i_obj) as obj do` aliases a designator. Use `class_id('x')`, not `class('x').intl_id`. | avaloq-script-expressions p3-5; data-types p3-4; what-are-data-dictionaries p5; hints-and-tips p3-4 (G2-03, G2-08, G2-13, G2-25, G2-26, G3-19, G1-46, G1-73) | Parse `name(expr)` as a cast when `name` is a DDIC, and as a call otherwise (symbol table plus DDIC index). Each record-field hop is a READ of a further entity with its own key. `p.bp_id` and `p.bp` refer to the same object. A `with` alias carries the key of the aliased designator. Validator: casts from plain number variables. |
| 10 | ACC L99-104 (open question; default key includes the attribute); EFFECTS L106-107 ("whether repeated accessor reads hit a cache"), L237-239 (E-Q1); AUDIT L481 ("repeated identical lookups ... without caching") | Docs say whether reads are cached. ACC defaults to key = root + args + attribute. | **No doc statement on object caching or repeated access across statements** (G3 open question 2, G2 open question 3). What *is* documented: each OBJ attribute read compiles to `select <attr> from obj_bp where id=...`. The compiler merges reads of the **same row** into one select unless a call that "might modify" the data (not `db_side_effect_free`/`deterministic`) sits between them ("three database round trips ... where we only needed one"). ASMD flags this as "Missed performance optimization opportunity". `with` improves performance "for memory DDICs". Deterministic calls with known args are evaluated at install time. Body variables persist for the session. Session values must not be cached in constants. | hints-and-tips p3-10; naming-conventions p3; what-are-avaloq-script-packages p3; what-are-objects p1 (G1-74, G1-78, G1-79, G1-82, G1-B-ADD-01, G1-64, G2-62, G6-48, G6-83, G3-A07) | ACC-01 key = root + normalised args (the **row**). List the attributes in the message. Fire when two or more reads of the same row are separated by a call not known to be side-effect-free (mirrors the ASMD marker), and when the same attribute is re-read. Keep a DOC_GAP for cross-statement caching. Use `i_`/`l_` names (row 12). |
| 11 | AUDIT L154 ("SQL inside script"), L169 and L345 (`sql_table` refs), L481 ("SQL ... inside a loop", "dynamic SQL"); V2 L175 (`sql [{tables, mode, joins}]` per unit); EFFECTS L89-90 (E0 c, "embedded SQL statement kind") | Script sources embed SQL statements with tables and joins. | Script "doesn't provide direct access to the data in Oracle database tables. Instead it uses data dictionaries". SQL appears only as "a condition in SQL notation" after some keywords or as string arguments (`cond => ...`). PL/SQL is reached through `import native`. LIST_CHAR, LIST_DATE and LIST_NUMBER "cannot be used within Avaloq Script". | getting-started-with-avaloq-script p1; naming-conventions p4-5; hints-and-tips p3, p5, p9-10; declarations-in-avaloq-script p5 (G1-01, G1-67, G1-76, G1-82, G2-46, G6-55) | For script, `sql` facts come only from condition-string arguments and native PL/SQL calls. Statement kinds and joins apply to PL/SQL and SQL sources. "SQL in loop" for script = DDIC reads or native calls in loop. "Dynamic SQL" = concatenated `cond` strings. |
| 12 | ACC L14-18, L114-122 (`p_bp_id`, `v_id`); V2 L488; EFFECTS L176-179 | Fixture names use `p_` and `v_` prefixes. | Prefixes: `i_` input parameters, `l_` locals, `b_` body variables, `c_` constants. The official example is `procedure obj#put(i_obj obj) ... with obj_bp(i_obj) as obj do`. | naming-conventions p2-3; what-are-avaloq-script-packages p3; hints-and-tips p5-6 (G1-62, G1-65, G2-61, G1-78) | Write fixtures as `i_bp_id` / `l_id`. Use the official `obj#put` snippet as the first `pos_corpus`-style fixture. Otherwise naming validators fire on the fixtures themselves. |
| 13 | V2 L251-252, L371, L453; REFACTOR_PROMPT_ADDITIONS L119-120 | `--@NoCheck` and `--#ifdef` are Avaloq pragmas. | Not in any doc in the folder. The documented directives are the `[Script 1.0]` header, `/*postp_start*/ ... /*postp_end*/` and the modifiers `deterministic` / `db_side_effect_free`. A pre-processor exists (TOC title only). | coding-conventions p3-4; hints-and-tips p10; declarations-in-avaloq-script p3-5 (G1-57, G1-83, G1-34, G1-42) | Mark `--@NoCheck` / `--#ifdef` as HOUSE or corpus-observed, with no doc_ref. Add `postp_start`/`postp_end` and the modifiers to TRANSLATION.md. |
| 14 | AUDIT L178, L453 (DDIC = "business object types, attributes, keys, meta types, object classes") | "Business object type" is an entity kind beside attributes and meta types. | "Business object type" is a **legacy term for a DDIC**. Object types are in CODE_OBJ_TYPE, business types (btt) in META_TYP, and order types in CODE_ORDER_TYPE. Each object type has three DDICs (`obj_`, `mem_doc_`, `doc_`). | what-are-data-dictionaries p1-2; what-are-technical-objects p1; what-is-a-business-type p1; what-is-the-type-of-an-order p1 (G3-05, G3-11, G3-43, G3-54, G4-10) | `DdicEntity.kind` ∈ {obj, mem_doc, doc, code_table, constant, collection, session, lookup, extension, ...}. Add `layer` ∈ {OBJ, DOC, MEM_DOC}. Model object type, btt and order type as code-table values. |
| 15 | AUDIT L331, L441-446 ("Layers": standard / custom / parameterisation / database) | "Layer" means product versus bank code. | In the docs, layers are the data access layers OBJ, DOC and MEM_DOC. Code is organised as application > module > component > source, with namespace prefixes `<ns>$`. ATS sources are test-only. The "no modification of standard sources" rule is not in the folder. | what-are-the-data-access-layers p1-5; what-are-data-dictionaries p3-4; layout/04-test-framework/pages/01a, 02b, 02e (G3-14, G3-34, G5-56, G5-66, G5-86, G5-104) | Rename the §8.1 concept to "ownership". Derive it from the namespace and the ice application. Reserve "layer" for OBJ/DOC/MEM_DOC. |
| 16 | EFFECTS L43-44 (ORDER sub-actions "creates, changes, verifies, releases, books or cancels") | These six are the lifecycle verbs. | Documented: create and modify (static data), save, finalize, discard, verify, reversal, and `do_wfc_action` on a stored order. "Booking" is the result of transaction orders. **"Release" does not appear.** | what-is-the-type-of-an-order p1; what-are-workflows p2; what-are-the-data-access-layers p3-5; understanding-banking-dates p4, p8-12 (G4-08, G4-21, G4-35, G4-39, G3-35, G3-A02) | Sub-actions: create, modify, save, finalize, verify, discard, reverse, workflow_action(<name>), attach_postit. Make "release" a candidate only. |
| 17 | AUDIT L481 ("missing header/doc `[VERIFY-Q32]`") | Header and doc comment rules exist. | Only the dash separator line before procedure and function headers, and section comments, are documented. Author, changelog and ticket are not mentioned. | coding-conventions p1-2 (G1-54) | Header-content rules = HOUSE. |

---

## 3. Corrections for the user's own older notes (G6 CONTRADICTED entries)

Source: `notes/AVALOQ_SCRIPT_METAPROMPT.md`. `_archive/agents-skill-copy/skills/avaloq-script/SKILL.md` is byte-identical apart from its front-matter, so fix both.

| Entry | Note § | Note says | Official | Cite |
|---|---|---|---|---|
| G6-10 | §1.2 | Strings: single quotes only | Single **or** double quotes, doubled to escape | language-fundamentals p2 |
| G6-18 | §1.4 | No optional parameters | Defaults are legal (`i_text text := null`). Collection params only `:= default` | hints-and-tips p8; data-types p25-26 |
| G6-21 | §1.1 L43 | `deterministic db_side_effect_free function` | EBNF alternatives. "deterministic implies db_side_effect_free" | declarations-in-avaloq-script p5; hints-and-tips p10 |
| G6-22 | §1.1, §1.5 | No visibility modifiers | `public \| private \| protected`, `final \| abstract`; records may be `private` | declarations-in-avaloq-script p5; data-types p37 |
| G6-25 | §2.1 | Base type `raw` | `BaseType = boolean \| text \| long \| number \| date` | data-types p1 |
| G6-26 | §2.1, §8 | `long` = CLOB | long = varchar2(32000) | data-types p1, p43 |
| G6-28 | §2.1 | boolean = number(1)/char(1) | One character `'+'`/`'-'`; varchar2(1) or boolean; literals true/false | data-types p1, p43; avaloq-script-expressions p3 |
| G6-34 | §2.4, §10 | Null to a collection = runtime error | Compile-time error ("Incompatible types"); use `clear` | data-types p26, p31 |
| G6-38 | §2.4 | `remv(idx)` removes by index | First positional argument is `val`; use `remv(pos=>n)` | data-types p11 |
| G6-39 | §2.4 | `.first`, `.next(i)`, `.cnv_to(T)` | Not in list<V>; use `cnv_to_text`, `list_from_text`, `for v in l.values` | data-types p8-14 |
| G6-40 | §2.4 | Set ops as instance methods | Static generic: `set.union<text>(a, b)`, also intersect, subtract, sym_diff | data-types p19-21 |
| G6-48 | §3.3 | (omits) repeated same-row access | Same-row reads split by a possibly-writing call cost one select each | hints-and-tips p5-7 |
| G6-50 | §3, §7.4, §8 | (omits) exception handling | `exception when others then err.raise_fa('<pkg.method>', ...)` | hints-and-tips p8; data-types p42 |
| G6-52 | §3.5, §8 | Recommend `iff` | Use typed iffb/iffd/iffn (iff 2-3× and 10× slower) | hints-and-tips p2 |
| G6-59 | §4.3, §9 | `p.asset.class('RISK_LEVEL').intl_id = 'HIGH'` | Marked INEFFICIENT; use `class_id('x') = mdb_<x>.<intl_id>` | hints-and-tips p3 |
| G6-60 | §4, §4.1 | BP = legal entity or natural person | BP = business relationship; Person sits above BP; MACC ⊂ POS | more-on-bp-objects p1; introducing-the-avaloq-object-model p2-3 |
| G6-67 | §5.3 | `env_task_ext#.task_do_wfc_action(i_task_id, i_action_id)` moves workflow state | ice **development-task** API, actually `task#do_wfc_action(i_task_id, i_wfc_action varchar2, ...)` returning `t_wfc_param_tab`. Banking orders use the order DDIC `do_wfc_action` | layout/03-ice-workflow/.../D3_Function_task_do_wfc_action; what-are-data-dictionaries p6 |
| G6-72 | §7.2, §9 | `lookup.code` returns a rate field | Returns a code-table **id**; `fld_list` names the match field. Assigning to `number` is fine (ATF) | hints-and-tips p9; layout/04-test-framework/pages/02b p5-6 |
| G6-73 | §7.3 | Max date 31.12.9999 | Max 31.12.4712 AD (SDS and non-SDS) | data-types p2 |
| G6-77 | Avaloq_Studio_Architecture ADR-003 | Syntax "proprietary and undocumented" | EBNF published (language-fundamentals, declarations, expressions, data-types) | declarations-in-avaloq-script p5; avaloq-script-expressions p6-7 |
| G6-79 | avaloq_studio_ide.html | GOTO/STAGE/LET "workflow script" | Invented. Workflows are WFD sources; comments `--` / `/* */`; `:=`; lower case | language-fundamentals p4; coding-conventions p2 |
| G6-81 | AvqPrompt §1, §4, §10 | utPLSQL tests | Avaloq Test Framework (ATF): TEST SCRIPT plus `it_`/`ut_` procedures | layout/04-test-framework/pages/02b p1 |
| G6-84 | avaloq-code-audit/discussion.md §7, §10 | No public grammar, no lint | EBNF fragments; ASMD markers; compiler warnings | hints-and-tips p6; what-are-data-dictionaries p6 |
| G6-86 | §2.4 | Collections usable everywhere | Only in compiler-framework script; not in REP PRINT or runtime-compiled script; LIST_* tables forbidden | data-types p30; hints-and-tips p5 |

Also treat these note claims as **UNSUPPORTED** (unverified, do not encode):
- `t_` as a required record prefix (G6-13)
- "never use sysdate" (G6-54); official examples use it
- `round`, `trunc`, `to_date`, `to_number` and the other built-ins outside the 02_05 table (G6-53)
- `import session` (G6-71); SESSION and LOOKUP are always available
- `lookup.bp` / `lookup.cont` (G6-72)
- the members `err.raise_appl`, `err.msg` and every `format.*` name (G6-74)
- `util.max_date` and the other exact util names (G6-73)
- `doc_order` (G6-30); order DDICs are named per btt
