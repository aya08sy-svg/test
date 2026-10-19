# Gaps and open questions (consolidated)

Merged from the "Open questions" sections of `verified/G1_verified_partB.md` (G1 OQn), `G2_verified.md` (G2 OQn), `G3_verified.md` (G3 OQn), `G4_verified.md` (G4 OQn) and `G5_verified.md` (G5 OQn), plus the G6 gap table. Duplicates are merged. Per-question verdicts are in `consolidated/F_verify_matrix.md`.

## (a) Top open questions, by impact on the audit tool

| # | Open question | Why it matters for the audit tool | Raised by |
|---|---|---|---|
| 1 | Full statement grammar: exit/continue, while/for details, `raise`, `null;`, labels, exception declaration, reserved-word list | The P2 grammar has no documented statement EBNF; every statement form is taken from examples | G1 OQ1, OQ3, OQ4; G1-A-ADD-03; G6-50 |
| 2 | Real expression precedence: and/or vs comparisons, `not a = b`, `-x * y`, `not in`, `not between`, `case` expressions | The literal EBNF misparses official code. A wrong tree gives wrong conditions in every validator | G2 OQ1, OQ2; G2-17, G2-65 |
| 3 | Is the compiler case-sensitive for identifiers and/or keywords? Does ice lower-case code? | Symbol resolution and the keyword lexer; whether a mixed-case name is a bug or only a style finding | G1 OQ6; G1-08 |
| 4 | Does assigning to a value parameter compile? (prose says "local constants"; the `log2` example assigns `x`) | ACC-01 reset logic, the "parameter reassigned" rule, and EFFECTS E4 parameter binding | G1 OQ7; G1-37 |
| 5 | Are object reads cached across statements? Exact rules for same-row select merging and lazy loading of path hops | Decides the ACC-01 key (row versus row + attribute) and every "load in loop" cost model | G2 OQ3; G3 OQ2; G3-A07; G1-78; ACC L99-104 |
| 6 | Commit semantics: what `no_commit` (default '+') means; which APIs and workflow actions commit; savepoints | SIDE_EFFECT(commit) labels; the commit rules; no transaction semantics are documented at all | G3 OQ3; G4 OQ2; G5 OQ5; G3-26; G5-09 |
| 7 | Script-level order API: exact `mem_doc_<btt>.new(...)` syntax, field set, workflow action names (verify, discard, book, reverse), order status codes ("Booked(35)") | Every ORDER leaf label in the effects map depends on it | G4 OQ1, OQ3, OQ4, OQ5; G3 OQ3, OQ12; G3-A02 |
| 8 | Which "one or two rare exceptions" allow writing OBJ directly? Does an OBJ read during an open order return pre-change values in script? | MODIFY-outside-order rule; read-after-write rule | G3 OQ4, OQ9; G3-34, G3-27 |
| 9 | Full built-in and standard package API: UTIL, ERR, FORMAT, SESSION/LOOKUP members, iffn, `require` (argument order conflicts with `it.require`) | Built-in whitelist (Q10); unresolved-call counts in P5; wrong-argument rules | G1 OQ11; G2 OQ5; G5 OQ8; G5-102; G6-71..74 |
| 10 | Exception semantics: named exceptions, `raise`, what `err.raise_fa` does ("fa"?) | Error-handling rules (swallowed errors, re-raise pattern) | G1 OQ4; G6-50 |
| 11 | Meaning of `#` and `$` in identifiers; host variables (`:`); `=>` "locator qualification"; `import native` | Tokenizer, namespace/ownership derivation, native-call edges | G1 OQ5, OQ8, OQ9; G1-11; G6-15 |
| 12 | Semantics of public/private/protected and final/abstract for script packages; `private` on non-type members | Visibility facts; dead-code and API-surface rules | G1 OQ10; G2 OQ6 |
| 13 | Which keywords take "a condition in SQL notation"? | The only SQL in script: sql facts and injection rules | G1 OQ17; G1-67 |
| 14 | ASMD markers: full list, export, headless run; compiler type-check configuration (Expressions p7 says unchecked, Data types p42 says configurable) | Avoid duplicating Avaloq's checks; mirror them; SARIF mapping | G1 OQ14; G2 OQ9; G1-79; G2-55 |
| 15 | Collection availability by release and compiler framework; map handover to PL/SQL (manual vs T#); `set.store` table; record field types; MEM_TAB API | Collection-usage error rules per source type | G2 OQ7, OQ8, OQ10, OQ11, OQ12; G6-86 |
| 16 | DDIC export file format; code-table DDIC and extension-DDIC syntax; exact method names (`discard_dir_msg` vs `discd_dir_msg`) | P4 DDIC index; resolution of every attribute reference | G3 OQ5, OQ6, OQ7, OQ11; G4 OQ7 |
| 17 | Source export format, the full source-type inventory, other `[Script x.y]` header versions, compile errors that block activation | P0 survey and P1 classifier | G5 OQ9, OQ10; G1 OQ16 |
| 18 | Is there a code-level where-used export? ice exposes only change dependencies | P5 comparison target | G5 OQ11 |
| 19 | Format and source type of configuration artifacts: base parameters, rule loader tables, CODE_ORDER_TYPE, calendars | Parameter-only versus code-bearing sources (Q24) | G4 OQ9 |
| 20 | Is "custom code must not modify standard sources" true? The TOC has "Overriding and replacing kernel sources" | AUDIT §8.1 ownership model and upgrade-safety rules | AUDIT L443; G6 gap #19 |
| 21 | How do business types relate to object classes? When can verification be skipped? | Q15 model; order-lifecycle rules | G4 OQ6, OQ8 |
| 22 | Official abbreviation glossary | Naming validator for abbreviations | G1 OQ15 |
| 23 | Doc defects to hold in mind before hard-coding rules: 78 dashes vs 73-76 in examples; typos ("LIST NUMBER", "determistic"); clipped ice B3 example; inconsistent ice signatures; omitted `;` in ATF examples; unreachable `calc` example | Avoid false-positive rules copied from flawed examples | G1 OQ20, OQ22; G5 OQ1, OQ2, OQ3, OQ13, OQ14 |
| 24 | Referenced but missing pages: Report Writer best practice, Optimizing compilers, collection Comparison page, List fields, item-expression syntax (ice help) | Rule rationale; report-specific rules | G1 OQ12, OQ13; G3 OQ5; G5 OQ6 |

## (b) Docs to download next: the verified top-25 TOC gap list

TOC line numbers are from `notes/avaloq_toc.md`, as verified in `G6_verified.md` Task B. "LR" stands for Technology > Fundamentals > Technical Base > Avaloq Script (language reference). "BPM" stands for Business Process Management.

| # | Topic | TOC path | TOC line(s) |
|---|---|---|---|
| 1 | Avaloq Script statements | LR > Avaloq Script statements | 16880 |
| 2 | Predefined functions (7 pages) | LR > Predefined functions > General / Numeric / Alphanumeric / … / Avaloq functions | 16881–16888 |
| 3 | ABR/S Avaloq Script coding guidelines | ABR/S > Customization guidelines > Coding Conventions > Avaloq Script > Coding Patterns (+ Structuring Script Packages, Useful Existing Script Packages) | 205–244 |
| 4 | ASMD static code analysis checks | Tools and Frameworks > ASMD > Using ASMD > Features of ASMD > Implementing static code analysis checks (+ DSL model reference > AvqScript Model) | 18072–18082 |
| 5 | Coding standard principles; markers; integrating analysis | … > Features of ASMD > Avaloq coding standard principles / Working with markers / Integrating static code analysis / ASMD public API | 18123–18126 |
| 6 | Checks provided by the compiler framework | Tools and Frameworks > Compiler framework > Checks provided by the compiler framework | 18258 |
| 7 | Optimizing compilers | Compiler framework > Optimizing compilers (+ Migrating Avaloq Script to the new CF) | 18255–18257 |
| 8 | Standard script packages ERR / UTIL / FORMAT / TEXT_LIST / DUPL_CTRL; package conventions and keywords | LR > Avaloq Script packages > … | 16889–16899 |
| 9 | Exception handling architecture; Error logging; CODE_UI_ERR | BPM > Error messages > … | 14593–14601 |
| 10 | ABR/S Code Optimization (Performance, Robustness, Upgradeability, …) | ABR/S > Customization guidelines > Code Optimization | 359–366 |
| 11 | Performance on the customization layer; frequent problem areas | System Operations & Monitoring > System performance guide > … | 16826–16833 |
| 12 | Lookup DDIC (incl. code injection risk, base parameters) | Enterprise-wide Object Model > Lookup | 15515–15518 |
| 13 | Source type: DDIC; Vocabulary extensions of a script type | LR > Source type: DDIC / Vocabulary extensions | 16900–16901 |
| 14 | SQL in customizations; Using PL/SQL APIs; Avaloq Script and DDICs | ABR/S > … > By Source Type > SQL; Technical Base > Customization overview > … | 273; 16931–16935 |
| 15 | Using DDICs to access object extensions; Use EXTN; order keys and additions | Enterprise-wide Object Model > Common object extension features > …; ABR/S > … > Use EXTN …; BPM > Common order functionality > … | 15482; 219; 14580 |
| 16 | Code tables: Concepts, Naming, CODE TAB / CODE TAB DEF | Technical Base > Code tables > … | 16918–16922 |
| 17 | WFD concepts and workflow commands; DDIC lookup for workflow actions | BPM > Workflow definition (WFD) > Concepts; Generic workflow commands > Workflow command reference; Customizing workflows > … | 14602–14603; 14731; 14736–14747 |
| 18 | Order validation (DOC VALID); DDIC validation; UI errors and overrides | BPM > Order validation; DDIC validation; ABR/S > … | 14586–14592; 14701–14706; 349–350 |
| 19 | Source customization: summary of source types, compilers, naming, API script# / src_intf#, overriding kernel sources | Technical Base > Source customization > … | 17023–17035 |
| 20 | Post-processor (postp_start/postp_end) usage; Pre-Processor | ABR/S > Coding Conventions > Post-processor …; Pre-Processor & Configurations > … | 346–347; 294–296 |
| 21 | Report Writer best practice / performance / script layout statements | Reporting Engine > Report Writer > … | 16263, 16281–16282 |
| 22 | Security guidelines: input/output validation; security development process | Access & User Security > Security guidelines for the Avaloq ecosystem > … | 17322–17323 |
| 23 | Rules for tuning Avaloq software | Technical Base > Rules for tuning Avaloq software | 17000 |
| 24 | ice Workbench: code reviewer, reviews, check-in validations, import/export utility (export syntax) | Tools and Frameworks > ice Workbench > Online help > … | 18345–18397 |
| 25 | ABR/S cross-cutting: no hard-coded IDs; Lists/Sets/Maps; compile-time over run-time detection; no to_char for numbers; Exceptions | ABR/S > Customization guidelines > Coding Conventions > … | 206, 351, 357, 355, 315 |

Lower priority (rank 26+):
- Base parameter DDIC (16908)
- Rule loader tables (~14707)
- Automatic field calculation (~14528)
- Task Engine (16289)
- Garbage collection (16979)
- ADAI REST API (17956)
- AICA (17989)
- ASMD LSP setup (18056)
- ABMD EBNF (18182)

## (c) Which questions need new downloads (gap # from table b)

- **No download needed** (the folder answers them enough): Q07, Q14, Q15, Q31, Q33.
- **Download needed:**
  - Q01: 19
  - Q02: 19
  - Q03: 24
  - Q04: ice online help (24)
  - Q05: 5, 19
  - Q06: 1, 4
  - Q08 (extension syntax only): 13, 15
  - Q09: 16
  - Q10: 2, 8
  - Q11: 9, 8
  - Q12: 14
  - Q13: 20
  - Q16: 15
  - Q17: 14
  - Q18: 17, 18
  - Q19: rule loader tables, ABMD (26+)
  - Q20: 21
  - Q21: AMI / INTF DEF (not ranked)
  - Q22: Task Engine (26+)
  - Q23: Forms (not ranked)
  - Q24: base parameters (26+), 16
  - Q25: 3, 5, 25
  - Q26: 7, 10, 11
  - Q27: 6, 5
  - Q28: 4
  - Q29: 10, 19
  - Q30: 22, 12
  - Q32: 8, 3
  - Q34: 19 (API: script#)
  - Q35: 4, LSP setup (26+)
  - Q36: customization examples (19)
  - Q37: 3
  - Q38: 3, 4, 5, 6 combined
- **Most leverage per download:** #1 (statements), #3 (ABR/S coding guidelines), #4/#5 (ASMD checks), #17 (WFD) and #19 (source customization). Together they close or advance Q01, Q02, Q05, Q06, Q18, Q25, Q27, Q28, Q34, Q37 and Q38.
