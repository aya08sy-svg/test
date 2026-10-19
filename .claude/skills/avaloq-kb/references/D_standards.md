# SECTION D — Coding standards, naming, performance → candidate audit rules (SEC code STD)

Sources: verified files G1_verified_partA.md, G1_verified_partB.md (main), plus G2, G3, G5, G6 verified entries on standards, naming, performance and testing. Verifier corrections applied; no REJECTED entries existed in the inputs. Cites are relative to `source_text/`.

## What a model must know first

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

---

## D1 Coding conventions

### KB-STD-01 All comments must be in English
- Fact: Avaloq's coding conventions require every comment to be in English.
- Cite: paged/text/coding-conventions.txt p.1 "Comments"
- Basis: STATED
- VERIFY: Q25 PARTIAL — the rules exist but are not numbered.
- Audit use: heuristic language detection on comment text (low severity, partly manual).
- From: G1-49

### KB-STD-02 Section comment: 78-dash line, `-- CAPITALS`, 78-dash line — CONFLICT with the doc's own examples
- Fact: A section comment is two lines of 78 dashes, with the comment text between them in capital letters after `-- ` (two dashes and a space). CONFLICT: every example separator line in the docs is shorter: 74 dashes in the section example (Coding p1), 76 in the Margins example (Coding p3-4), 73-74 in the Naming examples (Naming p3-4).
- Avaloq form:
```
  ------------------------------------------------------------------------------
  -- SECTION COMMENT
  ------------------------------------------------------------------------------
```
- Means: a pure layout marker with no semantics. Typical section names: IMPORT, CONSTANTS, PACKAGE VARIABLES.
- Cite: paged/text/coding-conventions.txt p.1 "Comments"; paged/text/coding-conventions.txt pp.3-4 "Margins"; paged/text/naming-conventions.txt pp.3-4 "Constants"/"Variables"
- Basis: STATED (rule); the dash counts were measured by the verifier on the layout text and `pdftotext -raw`
- Audit use: recognise separators with `^\s*-{70,}\s*$`. Report "not exactly 78" only at low severity, and only once real ice-formatted code confirms 78.
- From: G1-50, G1-84

### KB-STD-03 Block comment: `---- CAPITALS ----` with an empty line before it
- Fact: A block comment is capital-letter text between two sets of four dashes. An empty line separates it from the code before it. The hints examples break this themselves: `---- INEFFICIENT ---` and `---- BETTER ---` have three closing dashes (Hints p2), and `----WRONG ----` / `----CORRECT ----` have no space (Hints p4).
- Avaloq form:
```
  l_pos := 0;

  ---- BLOCK COMMENT ----
  l_pos := 1;
```
- Cite: paged/text/coding-conventions.txt p.1 "Comments"; paged/text/hints-and-tips-on-using-avaloq-script.txt pp.2, 4
- Basis: STATED
- Audit use: regex `^\s*---- [A-Z0-9 _\-/]+ ----\s*$`. The previous line must be blank, unless the comment opens a block.
- From: G1-51, G1-84

### KB-STD-04 Line comments go at the end of the line, in lower case, after `--`
- Fact: A line comment is placed at the end of the code line, in small letters, after two dashes. The example also continues a trailing comment over several lines and uses leading commas in multi-line argument lists (`,y`). Both are shown only in examples.
- Avaloq form:
```
  l_my_var := f(x);          -- example of single line comment.
  l_my_var := f(             -- example of a multi-
    x                        -- line comment
   ,y
  );
```
- Cite: paged/text/coding-conventions.txt pp.1-2 "Comments"
- Basis: STATED (end of line, small letters, `--`); INFERRED (multi-line continuation and the leading-comma style come from examples only; leading commas also appear on Hints pp.8-9)
- Audit use: flag a trailing `--` comment containing upper-case words (excluding identifiers and acronyms). Leading-comma style is info only.
- From: G1-52

### KB-STD-05 All code must be written in lower case
- Fact: All code must be written in lower case. Separately, Language fundamentals says "Uppercase and lowercase letters are considered as distinct", so case can matter to the lexer. Whether that applies to identifiers, keywords or both is not stated. Doc examples break the rule: `exampleProcedure` (Hints p9) and `Avaloq` in the identifier examples (Fundamentals p1).
- Cite: paged/text/coding-conventions.txt p.2 "Code"; paged/text/language-fundamentals.txt p.1 "Language fundamentals"; paged/text/hints-and-tips-on-using-avaloq-script.txt p.9 "Use of deterministic"
- Basis: STATED
- VERIFY: Q25 PARTIAL; Q31 EXTENDS/CONFIRMS
- Audit use: flag any identifier or keyword token outside strings and comments that contains `[A-Z]`. Severity: style warning.
- From: G1-53, G1-08, G6-05

### KB-STD-06 A 78-dash line goes before each procedure/function header; no other header is required
- Fact: Procedure and function headers should be preceded by a line of 78 dashes. The doc's own example line has 76. This is the only header requirement in the docs: author, change-log and ticket headers are not mentioned at all, which is a gap, not a prohibition.
- Avaloq form:
```
  ------------------------------------------------------------------------------
  function name()
```
- Cite: paged/text/coding-conventions.txt p.2 "Procedure and function headers"
- Basis: STATED
- VERIFY: Q32 PARTIAL — only the separator line is documented.
- Audit use: the nearest non-blank line before `[modifiers] procedure|function` should match `^\s*-{70,}\s*$`. Report the exact count only at low severity. Do not invent author or changelog rules.
- From: G1-54

### KB-STD-07 Indent two spaces, never tabs; "ice" applies the conventions on save
- Fact: The default indent is two spaces, and the tab character must not be used. Internally, these conventions are applied automatically to Avaloq-created sources when they are saved in "ice". ice Workbench is Avaloq's development, revision-control and deployment tool. That ice is also the formatter is INFERRED: the doc only says "when the source is saved in ice".
- Cite: paged/text/coding-conventions.txt p.2 "Indentation"
- Basis: STATED (rule); INFERRED (ice = formatter/IDE)
- VERIFY: Q35 EXTENDS (INFERRED)
- Audit use: any `\t` in leading whitespace is a violation. Indent width should be a multiple of 2. Expect few hits in ice-formatted code.
- From: G1-55

### KB-STD-08 Statement layouts for if / loop / with / case
- Fact: Bodies of condition, loop and `with` statements are indented one level. In `case`, each `when` is indented one level and its actions two levels. `else` aligns with `when`, and `end case` aligns with `case`.
- Avaloq form:
```
if a > b then
  do_action_a;
else
  do_action_b;
end if;

for i in 1 .. item_cnt loop
  l_item := item(i);
  ...
end loop;

with mem_doc_collect( b_id ) as collect do
  collect.add_postit( i_val_1, i_val_2 );
end with;

case doc.meta_typ_id
  when mdb_meta_typ.stex then
    do_stex_action;
  ...
  else
    do_else_action;
end case;
```
- Cite: paged/text/coding-conventions.txt pp.2-3 "Statements"
- Basis: STATED
- Audit use: low-severity formatter check. Skip it if the corpus is ice-formatted.
- From: G1-56, G1-43, G1-44, G1-45, G1-46

### KB-STD-09 Two-space margin, except pre-compiler lines in column 1; header case — CONFLICT
- Fact: Leave a two-space margin before indentation, except for compiler- or pre-compiler-specific statements such as `[Script 1.0]` and `script package`, which start in column 1. CONFLICT on the header's spelling: Coding conventions writes `[Script 1.0]`, while Data types p41 and the package-structure figure write `[script 1.0]`. The ATF example starts at `script package` with no header at all.
- Avaloq form:
```
[Script 1.0]

script package format
is
  ------------------------------------------------------------------------------
  -- IMPORT
  ------------------------------------------------------------------------------
  import util;
  import err;
```
- Cite: paged/text/coding-conventions.txt pp.3-4 "Margins"; paged/text/data-types.txt p.41; paged/text/what-are-avaloq-script-packages.txt pp.1-3; layout/04-test-framework/pages/02a_Creating_a_simple_test.txt p.1
- Basis: STATED
- VERIFY: Q13 EXTENDS; Q03 PARTIAL/EXTENDS (INFERRED that exported files start with this line)
- Audit use: match the header case-insensitively. Never fail a file for a missing header. Package-level content should be indented 2 spaces.
- From: G1-57, G6-01, G2-58

### KB-STD-10 Package layout: header, imports (one per line), variables, routines, footer
- Fact: A script package has a header (source type, version, name), then imports, then package variables, then procedures and functions, then `end <name>;`. Put each imported package on its own line, and reference imported elements as `<package>.<element>`.
- Avaloq form:
```
[script 1.0]

script package packagename
is
-- Imports of other script packages
   import util;
   import format;
-- Package variables
   b_count number;
...
end packagename;
```
- Cite: paged/text/what-are-avaloq-script-packages.txt pp.1-3; paged/text/coding-conventions.txt p.4; layout/02-techbase/02_05_Language_elements_used_in_Avaloq_Script.txt "Script packages"
- Basis: STATED
- Audit use: flag several imports on one line, and flag unused imports (INFERRED rule).
- From: G2-58, G1-86

### KB-STD-11 Column-aligned declarations (examples only)
- Fact: Every multi-declaration example in the docs aligns names, types or `constant`, defaults and trailing comments in fixed columns. No rule text requires this.
- Avaloq form: `b_token_id                 number    := 0;             -- token position`
- Cite: paged/text/naming-conventions.txt pp.3-4; paged/text/hints-and-tips-on-using-avaloq-script.txt pp.5, 8, 9; paged/text/declarations-in-avaloq-script.txt pp.2-3
- Basis: INFERRED (examples only)
- Audit use: optional info check at most. Never report misalignment as a rule violation.
- From: G1-B-ADD-02

### KB-STD-12 The docs break their own conventions; calibrate severity
- Fact: Doc examples break the published conventions. `exampleProcedure` is camelCase. Many parameters lack `i_` (`msg`, `cont`, `asset_key`, `x`). Examples use `---- DEBUG ----` block comments instead of 78-dash header lines. Hints block markers are malformed. The Naming CONSTANTS example puts its dash lines and declarations in column 1. Separator lines have 73-76 dashes.
- Cite: paged/text/hints-and-tips-on-using-avaloq-script.txt pp.2, 4, 9; paged/text/declarations-in-avaloq-script.txt p.6; paged/text/naming-conventions.txt p.3
- Basis: INFERRED (comparison of examples with the rules)
- Audit use: format and naming rules default to warning or info. Expect many hits in real code.
- From: G1-84

---

## D2 Naming conventions

### KB-STD-13 Use official Avaloq glossary abbreviations
- Fact: Use abbreviations wherever possible in names of variables, constants, functions, procedures and packages. They must match the official Avaloq glossary, which is not in the folder. Abbreviations seen in the docs: bp, cont, pos, cust, curr(y), cnt, val, calc, intl, typ, msg, doc, trans, acc, au, sa, bu, wfs, wfc, enbl, dsbl, h_code, str, encryp, extl, obj, mem, collect; the PL/SQL APIs add remv, upd, descn, prio.
- Cite: paged/text/naming-conventions.txt p.1 "Abbreviations"
- Basis: STATED (rule); abbreviation list INFERRED from examples
- VERIFY: Q31 EXTENDS
- Audit use: dictionary check of name elements. Needs the glossary or a list mined from the corpus/DDIC.
- From: G1-58, G5-05

### KB-STD-14 Compound names: `_`-separated, most significant business element first
- Fact: Compound names are underscore-separated elements, ordered from most to least significant. Significance is judged from the semantic (business) view, not the technical one. Example: `cust_cont_id`, not `cont_cust_id`. The rule applies to all names.
- Cite: paged/text/naming-conventions.txt pp.1-2 "Compound names"
- Basis: STATED; the no-camelCase regex is INFERRED (from lower-case code plus underscores)
- Audit use: regex `^[a-z][a-z0-9]*(_[a-z0-9]+)*$` (extended with `#`/`$`, see KB-STD-23). The ordering itself needs manual review.
- From: G1-59

### KB-STD-15 Names are singular (`cost_list`, not `costs`)
- Fact: Names and name elements must be singular, and plurals should be avoided. Collections are named `<x>_list`.
- Cite: paged/text/naming-conventions.txt p.2 "Singular vs plural"
- Basis: STATED
- VERIFY: Q31 CONFIRMS
- Audit use: heuristic plural detector that excludes glossary words ending in s (`pos`, `status`, …).
- From: G1-60, G6-14

### KB-STD-16 Foreign keys are named `<target table without obj_/code_/meta_>_id`
- Fact: A foreign key name starts with the significant name of the target table, which is the table name without a leading obj, code or meta element, and ends with `_id`. Examples: OBJ_BP → BP_ID, CODE_MEDIUM → MEDIUM_ID, META_LINK_TYPE → LINK_TYPE_ID.
- Cite: paged/text/naming-conventions.txt p.2 "Foreign keys"
- Basis: STATED (for DB foreign keys); applying it to DDIC attributes and variables is INFERRED
- VERIFY: Q14 EXTENDS; Q16 PARTIAL
- Audit use: an attribute or variable of type `id obj_x` / `id table code_x` should end in `x_id` (`^(?:[a-z0-9_]+_)?x_id$`).
- From: G1-61

### KB-STD-17 Constants: `c_` prefix, noun; boolean state names start with a predicate
- Fact: Constant names are prefixed `c_`, and the compound name must be a noun. The exception is booleans, which start with a predicate: `is_`, `do_`, `has_`, `enbl_`, `dsbl_`. The predicate rule applies to every item that represents application state: constants, variables and functions.
- Avaloq form:
```
c_chf_obj_name                       constant  text      := 'CHF';
c_max_item_cnt                       constant  number    := 100;
```
- Cite: paged/text/naming-conventions.txt pp.2-3 "Constants"
- Basis: STATED; the predicate's position after the `c_`/`l_` prefix is INFERRED from examples (`b_do_calc`, `l_is_auto`)
- VERIFY: Q31 CONFIRMS/EXTENDS
- Audit use: `^c_[a-z0-9_]+$` for constants. Boolean constants `^c_(is|do|has|enbl|dsbl)_`, boolean variables `^[lbi]_(is|do|has|enbl|dsbl)_`, boolean functions `^(?:\w+#)?(is|do|has|enbl|dsbl)_`.
- From: G1-62, G6-12

### KB-STD-18 Code-table constants contain the intl_id; content-description suffix
- Fact: A constant that refers to a code table entry should contain that entry's intl_id. Constant names should end with a content-description suffix (`_id`, code, name, …).
- Cite: paged/text/naming-conventions.txt p.3 "Constants"
- Basis: STATED; suffixes beyond `_id`/code/name INFERRED
- VERIFY: Q09 EXTENDS; Q31 EXTENDS
- Audit use: a `c_` constant initialised with `lookup.code(...,'<intl_id>')` should contain `<intl_id>` and end in `_id`. Candidate suffixes: `_id|_code|_name|_cnt|_text|_date|_nr|_list`.
- From: G1-63

### KB-STD-19 Variable prefixes by scope: `l_` local, `b_` body (package), `i_` input parameter
- Fact: Variables begin with `l_` (local), `b_` (body variable, i.e. package variable) or `i_` (input parameter). `b_` variables can be used throughout the script package within the current session. No prefix is defined for loop variables or with-aliases, and none is needed for outputs because no out parameters exist.
- Avaloq form:
```
  b_token_id                 number    := 0;             -- token position
  b_do_calc                  boolean   := false;         -- calculate document
```
- Cite: paged/text/naming-conventions.txt pp.3-4 "Variables"; paged/text/what-are-avaloq-script-packages.txt p.3 "Functions"
- Basis: STATED
- VERIFY: Q31 CONFIRMS
- Audit use: method locals `^l_`, package variables `^b_`, parameters `^i_`. Warning severity, because doc examples often omit the prefixes.
- From: G1-65, G2-61, G6-12

### KB-STD-20 Variable content suffix; comment variables whose meaning is not obvious
- Fact: Variable names should end with a content-description suffix (`_id`, code, name, …). Add a comment when a variable's meaning is not obvious from its name.
- Cite: paged/text/naming-conventions.txt pp.3-4 "Variables"
- Basis: STATED
- Audit use: suffix-vs-type check (a variable of type `id ...` should end in `_id`).
- From: G1-66

### KB-STD-21 Two-character SQL table aliases
- Fact: Some keywords can be followed by a condition in SQL notation. Tables in SQL statements are usually aliased with 2-character abbreviations: OBJ ob, ASSET os, DOC do, DOC_TAB dt, DOC_TRL dt, EVT ev, MSG ms, LIST_NUMBER ln, WFC_STATUS ws, WFC_ACTION wa. DOC_TAB and DOC_TRL both map to `dt`, probably a doc error.
- Cite: paged/text/naming-conventions.txt pp.4-5 "Aliases"
- Basis: STATED
- VERIFY: Q12 PARTIAL; Q30 EXTENDS (INFERRED: concatenated `cond =>` strings are a dynamic-SQL hotspot)
- Audit use: style check inside embedded SQL condition strings, plus tagging of SQL spans.
- From: G1-67

### KB-STD-22 `t_` for record types and `x_` for PL/SQL in-out parameters (examples only)
- Fact: Official record examples use `t_font` and `t_dimension`, but another declares `type address is record (` with no prefix. `x_` appears on PL/SQL in-out parameters (`x_out_list`). The Naming doc defines neither rule. Avaloq PL/SQL APIs also use `o_` for outputs and `t_` for types.
- Cite: paged/text/data-types.txt pp.34, 38; layout/03-ice-workflow/AvaloqICE/workflow_api_05_package_env_task_ext.txt p.1
- Basis: INFERRED (examples only)
- Audit use: info-level suggestion only, never an error.
- From: G6-13, G2-61, G5-05

### KB-STD-23 `#` and `$` in names: `<object>#<verb>` methods and `<ns>$` namespaces
- Fact: The official identifier EBNF allows only letters, digits and `_`. Real names, however, use `#` (`cont#pos_id`, `obj#put`, `person#gen`, PL/SQL `env_task_ext#`, `custom_package#.proc`) and `$` (`mba$dwh`, `MDB$IT_ADDR_CREATE`, `AVQ$BASE_PAR_AGING`). `$` marks a client-key or namespace prefix. Test sources follow `<client key>$IT_<business type>_<name>`.
- Cite: paged/text/language-fundamentals.txt p.1 "Identifiers"; paged/text/declarations-in-avaloq-script.txt p.6; paged/text/hints-and-tips-on-using-avaloq-script.txt pp.5-8; paged/text/what-are-data-dictionaries.txt p.4; layout/04-test-framework/pages/02b_Test_sources.txt p.1 "Naming conventions"
- Basis: STATED (examples); meaning of `#`/`$` INFERRED, except the `<client key>$` test pattern, which is STATED
- VERIFY: Q06 CONTRADICTS (EBNF incomplete); Q02/Q31 EXTENDS
- Audit use: the naming regex must accept `[a-z][a-z0-9_#$]*`. Candidate patterns: `^[a-z]+\$[a-z_]+$` for packages and `^[a-z_]+#[a-z_]+$` for object-operation methods.
- From: G1-11, G6-15, G5-05, G5-66, G3-14, G3-16

### KB-STD-24 DDIC name prefixes encode the data kind
- Fact: DDIC names carry a prefix for the kind of data they reach. MEM_DOC_ = order in memory, DOC_ = stored order, OBJ_ = object layer, DTM_ = report data, MEM_MSG_ = AMI messages in memory. A code table's DDIC has the code table's own name. Base parameter DDICs are `<ns>$BASE_PAR_<name>`, and the base parameter name itself may use `$` or `.`. In script, DDIC names are written in lower case (`obj_bp`).
- Cite: paged/text/what-are-data-dictionaries.txt pp.1, 3-4 "Introduction", "DDIC naming conventions"
- Basis: STATED
- VERIFY: Q14 EXTENDS; Q31 EXTENDS
- Audit use: classify a designator's root by prefix to get its layer and default effect.
- From: G3-14, G3-16, G3-03

### KB-STD-25 Doc examples break the naming rules: report naming findings as warnings
- Fact: Parameters `cont`, `asset_key`, `msg`, `x` and locals `y`, `i`, `p`, `asset` have no prefix, and `exampleProcedure` is camelCase. The rules themselves say "should".
- Cite: paged/text/declarations-in-avaloq-script.txt pp.2-7; paged/text/hints-and-tips-on-using-avaloq-script.txt p.9
- Basis: INFERRED
- Audit use: all STD-NAM rules default to warning or info.
- From: G1-84, G1-41, G1-65

---

## D3 Correctness rules

### KB-STD-26 A `case` without `else` raises ORA-06592 (CASE_NOT_FOUND)
- Fact: Every possible case must be handled, or ORA-06592 (CASE_NOT_FOUND) is thrown at runtime. Always include a default `else` clause.
- Cite: paged/text/hints-and-tips-on-using-avaloq-script.txt pp.1-2 "Use case instead of elsif batteries" (warning box)
- Basis: STATED
- VERIFY: Q27 CONFIRMS/EXTENDS; Q11 EXTENDS
- Audit use: AST rule, high value. Flag a `case` statement with no `else` branch.
- From: G1-69, G6-45

### KB-STD-27 Never cache session values in constants or package (`b_`) variables
- Fact: Constants and package variables hold cached values that are not recalculated on a session switch. Do not cache session-related values in them, especially base parameter values; recalculate them on procedure entry. The Declarations doc's own example `c_curr_date constant date := session.today` would break this rule if declared at package level. `b_` variables live for the whole session.
- Avaloq form: `c_curr_date        constant date        := session.today` (anti-pattern at package level)
- Cite: paged/text/naming-conventions.txt p.3 "Constants"; paged/text/declarations-in-avaloq-script.txt pp.2-3 "Declaring constants"; paged/text/what-are-avaloq-script-packages.txt p.3
- Basis: STATED
- VERIFY: Q26 EXTENDS; Q27 EXTENDS
- Audit use: flag a package-level `c_` constant or `b_` variable whose initialiser (or a later assignment) uses `session.*` or a base parameter DDIC.
- From: G1-64, G1-29, G2-62

### KB-STD-28 List handling: DDIC lists only feed a `for` loop; LIST_* tables are forbidden
- Fact: Lists such as `list of obj_bp` can only be returned by DDIC functions, and the returned list must be used immediately in a `for` loop. To save, reference, edit or pass a list to another procedure, cast it to a collection DDIC: LIST, SET, MAP, MEM_DB_LIST_CHAR, MEM_DB_LIST_DATE or MEM_DB_LIST_NR. The DB list tables LIST_CHAR, LIST_DATE and LIST_NUMBER cannot be used in script (the doc prints "LIST NUMBER").
- Cite: paged/text/hints-and-tips-on-using-avaloq-script.txt p.5 "List handling in Avaloq Script"
- Basis: STATED
- VERIFY: Q17 EXTENDS; Q14 EXTENDS
- Audit use: flag a list-typed value assigned, passed or returned without a collection DDIC. Flag any reference to `list_char|list_date|list_number` in script.
- From: G1-76, G1-77

### KB-STD-29 `deterministic`: an unchecked promise with strict conditions
- Fact: `deterministic` is a hint. For calls whose arguments are known at design time, it lets the compiler evaluate the call and replace it with the result at the end of the installation. The compiler cannot check the developer's promise: no side effects, the same result for the same arguments, and only DB objects that are fixed by installation time. Calls are currently not evaluated at installation for private and nested functions, private and local constants, or non-constant/non-deterministic arguments. `deterministic` implies `db_side_effect_free`.
- Cite: paged/text/declarations-in-avaloq-script.txt pp.3-4 "Deterministic functions"; paged/text/hints-and-tips-on-using-avaloq-script.txt pp.9-10 "Use of deterministic"
- Basis: STATED; misuse detection INFERRED
- VERIFY: Q13 EXTENDS; Q26 CONFIRMS
- Audit use: flag a `deterministic` function that calls `session.*`, `.store`, DOC/OBJ actions or logging, or that reads mutable data.
- From: G1-34, G6-19, G1-82

### KB-STD-30 `db_side_effect_free`: decision table
- Fact: The optional modifier promises that a method makes no change to DB content readable by any DDIC access. The compiler cannot check it. NOT side-effect free: store operations, actions on an OBJ or DOC layer DDIC, workflow actions on a MEM_DOC layer DDIC. Side-effect free: pure in-memory calculations, and methods that only log.
- Cite: paged/text/declarations-in-avaloq-script.txt pp.4-5 "Database side effect free procedures and functions"; paged/text/hints-and-tips-on-using-avaloq-script.txt pp.7-8 "Use of db_side_effect_free"
- Basis: STATED
- VERIFY: Q13 EXTENDS; Q26 CONFIRMS; Q27 EXTENDS
- Audit use: error if a `db_side_effect_free` method executes, directly or through callees, any action from the NOT list.
- From: G1-42, G1-81, G6-20

### KB-STD-31 Do not write both `deterministic` and `db_side_effect_free` on one function
- Fact: The EBNF offers `[deterministic | db_side_effect_free] function` as alternatives, and `deterministic` implies `db_side_effect_free`, so writing both is never needed. Whether the compiler rejects the pair is not stated.
- Avaloq form: `([db_side_effect_free] procedure | [deterministic | db_side_effect_free] function)`
- Cite: paged/text/declarations-in-avaloq-script.txt p.5 "Syntax for declaring procedures and functions"; paged/text/hints-and-tips-on-using-avaloq-script.txt p.10
- Basis: STATED
- VERIFY: Q07 CONTRADICTS (vs the metaprompt template that stacks both)
- Audit use: warning when both appear.
- From: G1-35, G6-21

### KB-STD-32 `/*postp_start*/ ... /*postp_end*/` must enclose exactly the expression
- Fact: An expression can be marked deterministic by putting it between the comment directives `postp_start` and `postp_end`. If the span also covers `:=` or `;`, the directives are silently ignored. The same conditions apply as for deterministic functions. A deterministic function is preferred, because the directive must be repeated at every call.
- Avaloq form:
```
c_num constant number := /*postp_start*/ 2 + 2 /*postp_end*/; -- OK
c_num constant number /*postp_start*/ := 2 + 2 /*postp_end*/; -- NOK
c_num constant number := /*postp_start*/ 2 + 2; /*postp_end*/ -- NOK
```
- Cite: paged/text/hints-and-tips-on-using-avaloq-script.txt p.10
- Basis: STATED
- VERIFY: Q13 CONFIRMS
- Audit use: flag unbalanced directives, and directive spans that contain `:=` or `;`.
- From: G1-83

### KB-STD-33 Exception idiom `when others then err.raise_fa(...)`; swallowing is an anti-pattern
- Fact: Official examples end methods with `exception when others then err.raise_fa('<pkg>.<method>', '<param>', <value>, ...)`, or `err.raise_fa('persist_list')`. ATF tests use `it.catch('<proc>')`, following "the standard pattern defined in the PL/SQL coding conventions". The ATF testability example ends each function with `exception when others then return null;`, which swallows every error. That example is not labelled as bad, but it must not be cited as compliant code.
- Avaloq form:
```
  exception
    when others then
      err.raise_fa(
        'mba$dwh.put_line'
       ,'i_text',i_text
      );
  end put_line;
```
- Cite: paged/text/hints-and-tips-on-using-avaloq-script.txt p.8; paged/text/data-types.txt p.42; layout/04-test-framework/pages/02a_Creating_a_simple_test.txt p.1; layout/04-test-framework/pages/02c_Implementing_the_construction_tests.txt pp.4-5
- Basis: STATED (examples); the rules "no swallowing" and "first argument names the enclosing method" are INFERRED
- VERIFY: Q11 EXTENDS; Q27 PARTIAL
- Audit use: flag `when others then null;` or `return null;` (swallowed error). Flag an `err.raise_fa` whose first argument does not match `<pkg>.<method>` or the enclosing method name.
- From: G1-81, G2-56, G6-50, G5-62, G5-82

### KB-STD-34 Collection pitfalls: assigning `null` fails to compile, a list-field cast is a copy, and `i_` collections can be changed by the callee
- Fact: Collections cannot be assigned `null` (a compile error; use `.clear`). `list(x.field)` / `set(x.field)` build a new collection holding copies, so changing it does not update the field. Collection parameters are passed by reference (`in out nocopy`), so a callee can change an `i_` collection.
- Cite: paged/text/data-types.txt pp.26-28, 31 "Assigning a collection", "Casting a list of field", "Passing a collection as an input parameter", compiler error table
- Basis: STATED
- VERIFY: Q07 EXTENDS; Q31 PARTIAL (the `i_` prefix does not guarantee a collection is read-only)
- Audit use: error on `<coll> := null`. Flag a bug where a cast result is modified and the field is expected to change. Info on a mutated `i_` collection, for side-effect analysis.
- From: G2-36, G2-37, G2-38, G6-34, G6-36

### KB-STD-35 The compiler does not check types or casts; paths must end in a scalar
- Fact: Assignment compatibility is "currently not checked by the compiler". A DDIC cast `T(v)` is not checked either. A data access expression must end in a scalar (base or ID type); a non-scalar may silently give null. CONFLICT: Data types p42 says some type violations give warnings or errors "depending on the configuration".
- Cite: paged/text/avaloq-script-expressions.txt pp.3, 4-5, 7-8; paged/text/data-types.txt p.42
- Basis: STATED
- VERIFY: Q27 EXTENDS/PARTIAL
- Audit use: our own type checks add value. Flag casts from plain `number` variables, and record-typed paths used as values.
- From: G2-19, G2-13, G2-08, G2-55

### KB-STD-36 `session` commit/rollback are dangerous, especially in message processing
- Fact: The SESSION DDIC has commit and rollback methods. Using them, especially during message processing, can break framework error handling and atomicity, for example by creating several orders for the same message.
- Cite: paged/text/what-are-data-dictionaries.txt pp.7-8 "Special DDICs: SESSION and LOOKUP"
- Basis: STATED (exact member names unverified)
- VERIFY: Q11 EXTENDS; Q26 PARTIAL
- Audit use: warning on `session.commit` / `session.rollback`. Raise the severity in MSG/AMI sources and inside loops.
- From: G3-28, G6-68

### KB-STD-37 Obsolete DDIC fields: compiler warning now, broken code later
- Fact: An obsolete DDIC field will be de-released in a future release. The compiler warns and names the substitute. Avaloq recommends replacing the field as soon as the warning appears. Example: MEM_DOC_PAY `curry_id` → `asset_id`.
- Cite: paged/text/what-are-data-dictionaries.txt p.6 "Obsolete DDIC fields"
- Basis: STATED
- VERIFY: Q27 CONFIRMS; Q29 EXTENDS
- Audit use: upgrade-safety rule driven by the DDIC Obsolete section.
- From: G3-23

### KB-STD-38 Null-related checks: `= null` comparisons and uninitialised accumulators
- Fact: Comparisons yield true, false or null, and variables with no default start as null. The docs' own accumulator example initialises with `l_val := 0` before the loop.
- Cite: paged/text/language-fundamentals.txt p.3 "Comparison operators"; paged/text/declarations-in-avaloq-script.txt pp.2, 6
- Basis: STATED (semantics); the validators are INFERRED
- Audit use: flag `= null` / `!= null` (use `is [not] null`). Flag `l_x := l_x + ...` with no prior assignment.
- From: G1-17, G1-27, G1-41

### KB-STD-39 Assigning to a parameter: the docs contradict themselves
- Fact: Value parameters are described as "local constants", yet the official `log2` example assigns `x := x / 2`. Whether the compiler accepts this is not documented. The change is never visible to the caller.
- Cite: paged/text/declarations-in-avaloq-script.txt pp.5-7 "Formal parameters"
- Basis: STATED (both texts); the conflict is INFERRED by the verifier
- VERIFY: Q07 PARTIAL
- Audit use: maintainability warning only, never an error.
- From: G1-37, G6-17

### KB-STD-40 `sysdate` in banking logic (not a stated rule)
- Fact: Official examples use `sysdate` freely, even in a "BETTER" example. The bank date differs from the calendar date, and `session.today` is the official alternative. A rule against `sysdate` is a sound inference, but no doc states it.
- Cite: paged/text/hints-and-tips-on-using-avaloq-script.txt p.4; paged/text/declarations-in-avaloq-script.txt p.3
- Basis: INFERRED
- VERIFY: Q25 PARTIAL
- Audit use: info or warning when `sysdate` is compared with a business date field.
- From: G6-54

---

## D4 Performance rules

### KB-STD-41 Use `case` instead of `elsif` chains (about 10% faster)
- Fact: The case statement is about 10% faster than if, and more readable.
- Avaloq form:
```
---- INEFFICIENT ----
l_mod := mod(i, 10);
if l_mod = 0 then l_dummy := 0;
elsif l_mod = 1 then l_dummy := 1;
elsif l_mod = 2 then l_dummy := 2;
...
else l_dummy := 10;
end if;
---- BETTER ----
case mod(i, 10)
  when 0 then l_dummy := 0;
  when 1 then l_dummy := 1;
  when 2 then l_dummy := 2;
  ...
  else l_dummy := 10;
end case;
```
- Cite: paged/text/hints-and-tips-on-using-avaloq-script.txt p.1 "Use case instead of elsif batteries"
- Basis: STATED
- VERIFY: Q26 CONFIRMS; Q37 CONFIRMS
- Audit use: flag an if/elsif chain of 3 or more branches whose conditions all compare the same expression with a literal or constant.
- From: G1-68, G6-45

### KB-STD-42 Use typed `iffb`/`iffd`/`iffn` instead of `iff`
- Fact: `iffb` returns one of two integers depending on a boolean; `iff` is two to three times slower. `iffd` returns one of two dates; `iff` is ten times slower. `iffn` is named in the heading but not described. The TOC lists a guideline page "iff (deprecated)" (and "nvl (deprecated)"), but its content is not in the folder.
- Avaloq form: `l_is_auto := iff(doc.asset_a = '+', '+', '-');` (untyped `iff`, Naming p4)
- Cite: paged/text/hints-and-tips-on-using-avaloq-script.txt p.2 "Use typed iff (iffb, iffd, iffn)"
- Basis: STATED (speed factors); INFERRED (deprecation, from the TOC title only)
- VERIFY: Q26 CONFIRMS (contradicts any "use iff" advice); Q10 EXTENDS
- Audit use: flag `iff(` with date branches (use `iffd`) or integer/number branches (use `iffb`/`iffn`). Flag `nvl(` (use `coalesce`, INFERRED).
- From: G1-70, G6-52

### KB-STD-43 Avoid implicit data type conversions
- Fact: Type conversions are slower than using the correct data types to begin with. Assigning a number to text is allowed through implicit conversion. In general, id types are not type-compatible with text.
- Avaloq form:
```
---- INEFFICIENT ---
declare
  l_text text;
begin
  l_text := 10;
end;
---- BETTER ---
declare
  l_number number;
begin
  l_number := 10;
end;
```
- Cite: paged/text/hints-and-tips-on-using-avaloq-script.txt p.2 "Avoid implicit data type conversions"; paged/text/data-types.txt pp.42, 44
- Basis: STATED
- VERIFY: Q26 CONFIRMS/EXTENDS
- Audit use: flag a numeric literal or expression assigned to or compared with `text`, the reverse, and date↔text (type-aware).
- From: G1-71, G6-33, G2-55

### KB-STD-44 Move loop-invariant calls out of loops (a general rule)
- Fact: Statements in a loop run many times. A statement whose value stays constant over all iterations can be moved before the loop and run once. The doc says this is a general rule, not specific to reports or Avaloq.
- Avaloq form (verbatim, including the doc's missing `)` and the space in `' +3v'` on the BETTER side):
```
---- INEFFICIENT ----
for p in cont.pos_list loop
  if p.asset.maturity_date = lookup.date(to_char(session.today) || '+3v') then
  ..
  end if;
end loop;
---- BETTER ----
l_date_3v := lookup.date(to_char(session.today) ||' +3v';
for p in cont.pos_list loop
  if p.asset.maturity_date = l_date_3v then
  ..
  end if;
end loop;
```
- Cite: paged/text/hints-and-tips-on-using-avaloq-script.txt pp.2-3 "Avoid unnecessary function calls in loops"
- Basis: STATED
- VERIFY: Q26 CONFIRMS; Q37 CONFIRMS
- Audit use: flag a call inside a loop body whose arguments use neither the loop variable nor anything assigned in the loop (especially `lookup.*`, `session.*`, `to_char`). Applies to every source type.
- From: G1-72, G1-B-ADD-03, G6-70

### KB-STD-45 Use `class_id('x')`, not `class('x').id`; DDIC field access, not table access
- Fact: Reading a field directly in a DDIC is always faster than reading the underlying table. Using the `class_id('ass_type')` attribute instead of `class('ass_type').id` makes the expression one level shorter. The BETTER side compares with a code constant `mdb_asset.fwd_fx` or a raw id. That code constants beat `.intl_id = '...'` or `lookup.code(...)` is INFERRED from the example.
- Avaloq form:
```
---- INEFFICIENT ----
pos.asset.class('ass_type').intl_id = 'fwd_fx'
pos.asset.class('ass_type').id      = 12345 /*fwd_fx*/
pos.asset.class('ass_type').id      = lookup.code('code_obj_class','fwd_fx')
---- BETTER ----
pos.asset.class_id('ass_type') = 12345 /*fwd_fx*/
pos.asset.class_id('ass_type') = mdb_asset.fwd_fx
```
- Cite: paged/text/hints-and-tips-on-using-avaloq-script.txt p.3 "Avoid unnecessary database access"
- Basis: STATED (class_id, one level shorter, DDIC faster); INFERRED (code-constant preference)
- VERIFY: Q08 EXTENDS; Q09 CONFIRMS/EXTENDS; Q26 CONFIRMS
- Audit use: regex `\.(\w+)\(([^)]*)\)\.id\b` → use `<attr>_id(...)`. Flag `.<x>.id` where an `<x>_id` attribute exists. Flag `.intl_id = '<lit>'` and `lookup.code` in a comparison → use an `mdb_*` constant (INFERRED).
- From: G1-73, G6-55

### KB-STD-46 Use `with` for repeated long designators (memory DDICs)
- Fact: `with` improves performance for memory DDICs and makes code more legible. The doc scopes the speed gain to memory DDICs. On OBJ rows `with` alone does not prevent per-attribute selects (KB-STD-48).
- Avaloq form:
```
---- INEFFICIENT ----
if m.msg.asset.issue_date.val_date      = sysdate
  or m.msg.asset.pay_up_date.val_date   = sysdate
  or m.msg.asset.lock_date.val_date     = sysdate
  or m.msg.asset.maturity_date.val_date = sysdate
  ...
---- BETTER ----
with m.msg.asset as a do
  if a.issue_date.val_date    = sysdate
  or a.pay_up_date.val_date   = sysdate
  or a.lock_date.val_date     = sysdate
  or a.maturity_date.val_date = sysdate
  ...
```
- Cite: paged/text/hints-and-tips-on-using-avaloq-script.txt p.4 "Use with"
- Basis: STATED
- VERIFY: Q26 CONFIRMS; Q08 EXTENDS
- Audit use: flag a designator prefix of 2 or more dots repeated N or more times (e.g. 3) in one statement or block.
- From: G1-74, G6-47

### KB-STD-47 Loop over list fields with `for x in list`, not an index loop (n² vs n)
- Fact: Loop over a list field with the list operation, not indexed access (get). With get, looping over n elements takes time proportional to n². With list, it is proportional to n.
- Avaloq form:
```
----WRONG ----
for i in 1 .. doc.trans_list.count loop
  with doc_trans(doc.trans_list(i)) as t do
  ...
  end with;
end loop;
----CORRECT ----
for t_id in doc.trans_list loop
  with doc_trans(t_id) as t do
  ...
  end with;
end loop;
```
- Cite: paged/text/hints-and-tips-on-using-avaloq-script.txt pp.4-5 "Use list instead of get to loop over list fields"
- Basis: STATED
- VERIFY: Q26 CONFIRMS; Q27 CONFIRMS; Q37 CONFIRMS
- Audit use: AST rule, high value. Flag `for i in 1 .. X.<list>.count loop` whose body indexes `X.<list>(i)` or calls `.get(i)`.
- From: G1-75, G6-46

### KB-STD-48 Attribute reads mixed with calls that may write: 3 selects instead of 1
- Fact: Reads of `obj.bu_id`, `obj.acc_type_id` and `obj.au_sa_bp_id` on the same row could merge into one select. Because `mba$dwh.put_line` "might modify the value" of those fields, the compiler emits one `select <attr> from obj_bp where id=i_obj` per attribute: "three database round trips (select statements) where we only needed one". There are two fixes. Mark the callee `db_side_effect_free`, if it truly is. Or extract the attributes to local variables first, then use the locals in the calls.
- Avaloq form:
```
procedure obj#put(
  i_obj                                         obj
)
is
begin
  with obj_bp(i_obj) as obj do
    mba$dwh.put_line(mba$dwh.obj#text('id', obj));
    mba$dwh.put_line(mba$dwh.obj#text('bu_id', obj.bu_id));
    mba$dwh.put_line(mba$dwh.code#text('acc_type_id', obj.acc_type_id, 'code_acc_type'));
    mba$dwh.put_line(mba$dwh.obj#text('au_sa_bp_id', obj.au_sa_bp_id));
  end with;
end obj#put;
-- fix 2:
l_bu_id := obj.bu_id
l_acc_type_id := obj.acc_type_id
mba$dwh.put_line(..., l_bu_id);
mba$dwh.put_line(..., l_acc_type_id);
```
- Means: each DDIC attribute read compiles to a select on the backing table (same-named table and column, keyed by `id`). The compiler merges them only when no call that might write sits between them.
- Cite: paged/text/hints-and-tips-on-using-avaloq-script.txt pp.5-7 "Optimizing accesses to the same database table"
- Basis: STATED (the translation shown); INFERRED (that the same-name mapping holds in general)
- VERIFY: Q26 CONFIRMS/EXTENDS; Q27 CONFIRMS; Q12 EXTENDS
- Audit use: flag 2 or more attribute reads of the same DDIC instance in one block, separated by calls to methods not marked `db_side_effect_free`/`deterministic`. Offer either fix as the suggestion.
- From: G1-78, G1-80, G1-B-ADD-01, G6-48, G6-83

### KB-STD-49 ASMD info marker "Missed performance optimization opportunity"
- Fact: Avaloq's toolchain shows an ASMD info marker, "Missed performance optimization opportunity", on calls that could possibly be db side effect free. Screenshot text: "Feature call with potential side effect 'mba$dwh.put_line' prohibits reuse of table access via 'obj'. For additional information see DocID 1074 under 'Hints and tips on using AvaloqScript'." ASMD static checks, compiler-framework checks and obsolete-field warnings exist, but their catalogues are not in the folder.
- Cite: paged/text/hints-and-tips-on-using-avaloq-script.txt pp.6-7 (screenshot p.7)
- Basis: STATED
- VERIFY: Q28 PARTIAL/EXTENDS; Q27 CONFIRMS
- Audit use: reuse this message text for KB-STD-48 findings. Fetch the ASMD check catalogue (gaps #4-#6) to avoid duplicating Avaloq's own checks.
- From: G1-79, G6-84

### KB-STD-50 A `deterministic` wrapper caches expensive `lookup.code` at install time
- Fact: Without `deterministic`, `wfs_id` runs the "relatively expensive call to lookup.code" every time. Marked deterministic, calls with literal arguments (`wfs_id('foo')`) "will only be evaluated once, with a cached result at installation time". This only works for non-private, non-nested functions called with constant arguments (KB-STD-29).
- Avaloq form:
```
deterministic function wfs_id(
  i_intl_id                                     text
) return id table wfc_status
is
begin
  if i_intl_id is null then
    return null;
  end if;
  return lookup.code(
    tab_name => 'wfc_status'
   ,val      => i_intl_id
   ,fld_list => 'intl_id'
   ,cond     => 'meta_typ_id = ' || meta_typ.bp_id
  );
end wfs_id;
```
- Cite: paged/text/hints-and-tips-on-using-avaloq-script.txt pp.9-10 "Use of deterministic"
- Basis: STATED
- VERIFY: Q09 CONFIRMS/EXTENDS; Q26 CONFIRMS
- Audit use: flag a public wrapper around `lookup.code(...)` that is called with constants but not marked deterministic.
- From: G1-82, G6-19

### KB-STD-51 Limit `.store`: each call writes to the DB
- Fact: Use `.store`/`.load(id)` only to pass data to a report or for asynchronous population. Passing to PL/SQL needs no stored list. Keep single-session lists in memory, or in package state within the same script package or report DTM. Avoid repeated `.store` calls, particularly in `on level_xxx` report handlers: "each call writes to the DB and replaces existing rows". Clear the stored version only for business logic, not as garbage collection.
- Avaloq form:
```
-- Preferred: keep list in memory
process(l_list);
-- Unnecessary: repeated store calls add DB overhead
l_list.store;
l_list.add(1);
l_list.store;
```
- Cite: paged/text/data-types.txt pp.29-30 "Limit bad use of .store"
- Basis: STATED
- VERIFY: Q26 CONFIRMS; Q20 EXTENDS
- Audit use: flag `.store` inside a loop or an `on level_*` handler. Flag more than one `.store` on the same variable in a scope. Flag a stored id that is only passed to PL/SQL. Flag `.store` of an empty list used as cleanup.
- From: G2-41, G6-87

### KB-STD-52 Collection assignments copy; avoid them, especially in loops
- Fact: Every collection variable assignment copies the collection, so assigning huge collections may hurt performance. Collections are PL/SQL associative arrays, and Avaloq recommends avoiding collection assignments where possible. The compiler avoids copying a returned collection when it matches an input parameter collection.
- Avaloq form: `l_list := concat(l_list, b_list);  -- no copies` vs `l_list := concat(b_list, l_list);  -- copy necessary`
- Cite: paged/text/data-types.txt pp.26, 28, 31
- Basis: STATED
- VERIFY: Q26 EXTENDS
- Audit use: flag `:=` between collection variables inside a loop. Flag repeated `list(x.field)` / `set(x.field)` casts of the same field in a loop.
- From: G2-36, G2-37, G2-39, G6-36

### KB-STD-53 `list.remv` costs O(n); ID types are lighter than record types
- Fact: `remv` shifts the later items left: O(n) in the worst case, constant time only for the last element. "Using the ID to refer to an instance of an object is lighter and quicker than using a record type."
- Cite: paged/text/data-types.txt pp.3, 8-14 "Business-oriented data types", "list<V>"
- Basis: STATED
- VERIFY: Q26 EXTENDS
- Audit use: flag `remv` inside a loop (O(n²) candidate). Info: prefer `id <ddic>` parameters when only a reference is passed.
- From: G2-32, G2-25

### KB-STD-54 Report-specific and compiler-optimisation guidance lives elsewhere
- Fact: Report tips are in "Report Writer best practise", and generated-PL/SQL optimisation is in "Optimizing compilers". Neither is in the folder.
- Cite: paged/text/hints-and-tips-on-using-avaloq-script.txt p.1 "Note"
- Basis: STATED
- VERIFY: Q20 PARTIAL; Q26 PARTIAL
- Audit use: gap list. Do not invent report rules.
- From: G1-85

---

## D5 Testing standards (ATF)

### KB-STD-55 Test naming: the `it_`/`ut_` prefix runs as a test
- Fact: Integration tests use the prefix `it_` or the infix `xxx$it_`, and unit tests use `ut_` or `xxx$ut_`. The implementation is named `<client key>$IT_<business type>_<name>` (e.g. MDB$IT_ADDR_CREATE) and the test script `<client key>$<business type>.IT_<name>`. ATF calls every procedure starting with `it_` or `ut_` in order. `it_setup` runs first and `it_teardown` last; both are optional.
- Cite: layout/04-test-framework/pages/02b_Test_sources.txt pp.1-2 "Naming conventions", "Main test package"
- Basis: STATED
- VERIFY: Q31 EXTENDS; Q02 EXTENDS
- Audit use: in test packages, a helper whose name starts with `it_`/`ut_` will run as a test case.
- From: G5-66, G5-67

### KB-STD-56 `assert` continues; `require` stops the procedure
- Fact: The IT package's assert logs pass or fail and the test continues. A require must succeed, or the current procedure stops. Calls seen in examples: `it.log_begin/log_end/log_chk/log_step`, `it.assert(text, boolean)`, `it.require(text, boolean)`, `it.assert_eq_text(...)`, `it.catch(proc)`, `it.ats_script_run_id`. An unqualified `require(<cond>, <text>)` takes its arguments in the reverse order. UT is a private, smaller package.
- Cite: layout/04-test-framework/pages/02b_Test_sources.txt pp.2, 5; layout/04-test-framework/pages/02c_Implementing_the_construction_tests.txt pp.1, 3
- Basis: STATED; that unqualified `require` is a different routine is INFERRED
- Audit use: do not hard-code `require`'s argument order. Use the assert/require semantics when judging tests.
- From: G5-68, G5-69, G5-102

### KB-STD-57 Minimal test shape: `it_main`, log_begin/log_end, `it.catch`
- Fact: A test is a script package that does `import it;`. Its main procedure is by convention `it_main`. It starts with `it.log_begin` and ends with `it.log_end`, and its exception block calls `it.catch('<proc name>')`.
- Avaloq form:
```
procedure it_main
is
begin
   it.log_begin('it_hello');
   it.assert('Hello, World! Everything ok.', true);
   it.log_end('it_hello');
exception
   when others then
     it.catch('it_main');
end it_main;
```
- Cite: layout/04-test-framework/pages/02a_Creating_a_simple_test.txt p.1 "Create the test"
- Basis: STATED
- VERIFY: Q11 EXTENDS
- From: G5-62

### KB-STD-58 Test code quality: production standard, stateless, rerunnable, kept in ATS
- Fact: Test code has the same quality requirements as production code. Tests use static data from setup, leave no lasting changes (teardown rolls back), and append `it.ats_script_run_id` to unique keys and intl_ids so reruns work. Test sources go in the ATS application so they are never deployed to production.
- Cite: layout/04-test-framework/pages/02c_Implementing_the_construction_tests.txt p.1; layout/04-test-framework/pages/02b_Test_sources.txt p.1 "Source application and components"
- Basis: STATED; "production must not depend on ATS" is INFERRED
- VERIFY: Q25 EXTENDS; Q33 EXTENDS
- Audit use: flag hard-coded unique keys without `it.ats_script_run_id`, data-creating tests with no teardown, and production code that depends on ATS sources.
- From: G5-76, G5-104

### KB-STD-59 Testability: inject session values; split the stateless calculation from the order wrapper
- Fact: Pass session values (`session.today`) and base parameters into functions as parameters with defaults (`i_date date := session.today`). Put calculation logic in a function with simple parameters (`calc_intl`) behind a thin wrapper that takes the order (`calc(i_doc doc_stex)`). The same example has an unreachable branch (`if i_qty > 100 ... elsif i_qty > 1000`) and swallows errors (KB-STD-33).
- Cite: layout/04-test-framework/pages/02c_Implementing_the_construction_tests.txt pp.4-5 "Create modular and stateless code"
- Basis: STATED; anti-pattern observations INFERRED
- VERIFY: Q25 EXTENDS; Q27 PARTIAL
- Audit use: maintainability smell for direct `session.today` or base-parameter reads inside calculation functions. Flag `elsif` conditions that a previous branch already covers (unreachable).
- From: G5-81, G5-82

---

## D6 Rule catalogue

Severity scale: error (wrong at runtime or breaks a documented guarantee), warning (documented anti-pattern or "should" rule), info (style, examples only, or inferred). "INFERRED" in Basis means the rule comes from examples or our own reasoning, not from rule text.

| Rule id | Rule | Detection hint (regex / AST) | Severity | Cite | Basis |
|---|---|---|---|---|---|
| STD-FMT-01 | Comments in English | stopword/language detection on comment tokens | info | coding-conventions p.1 | STATED |
| STD-FMT-02 | Section comment = dash line / `-- CAPS` / dash line | `^\s*-{70,}\s*$` then `^\s*-- [A-Z0-9 _\-]+$` then `^\s*-{70,}\s*$` | info | coding-conventions p.1 | STATED |
| STD-FMT-03 | Separator lines have exactly 78 dashes | `-{70,}` but not `^\s*-{78}\s*$` | info (CONFLICT: doc examples have 73-76) | coding-conventions pp.1-4; naming-conventions pp.3-4 | STATED, conflicting |
| STD-FMT-04 | Block comment `---- CAPS ----` with a blank line before it | `^\s*----\s*\S.*----` not matching `^\s*---- [A-Z0-9 _\-/]+ ----\s*$`, or previous line not blank | info | coding-conventions p.1 | STATED |
| STD-FMT-05 | Trailing line comment in lower case | trailing `--` text containing `[A-Z]{2,}` words (not identifiers) | info | coding-conventions pp.1-2 | STATED |
| STD-FMT-06 | All code lower case | identifier/keyword token outside strings and comments with `[A-Z]` | warning | coding-conventions p.2 | STATED |
| STD-FMT-07 | Dash line before each procedure/function header | nearest non-blank line before `^\s*(\w+\s+)*(procedure\|function)\s` not `-{70,}` | info | coding-conventions p.2 | STATED |
| STD-FMT-08 | No tabs; indent in multiples of 2 | `^\t` / `^[ ]*\t`; leading-space count % 2 != 0 | warning (tabs), info (width) | coding-conventions p.2 | STATED |
| STD-FMT-09 | Statement layout (case/when/else alignment) | AST column check of `when`/`else`/`end case` vs `case` | info | coding-conventions p.3 | STATED |
| STD-FMT-10 | 2-space margin; `[Script 1.0]` / `script package` in column 1 | `^\s+\[script` (case-insensitive) or `^\s+script package`; package members at column < 3 | info | coding-conventions pp.3-4 | STATED |
| STD-FMT-11 | One import per line | `import\s+\w+;\s*import` on one line | info | coding-conventions p.4 | STATED |
| STD-FMT-12 | Unused import | `import x;` with no `x.` reference | info | what-are-avaloq-script-packages pp.1-3 | INFERRED |
| STD-FMT-13 | Column-aligned declarations | declaration column variance | info (optional) | naming-conventions pp.3-4 | INFERRED |
| STD-NAM-01 | Constants prefixed `c_` | `constant` declaration with name not `^c_` | warning | naming-conventions pp.2-3 | STATED |
| STD-NAM-02 | Local variables prefixed `l_` | declaration in a method body not `^l_` (excluding loop vars and aliases) | warning | naming-conventions p.3 | STATED |
| STD-NAM-03 | Package variables prefixed `b_` | package-level non-constant declaration not `^b_` | warning | naming-conventions p.3; what-are-avaloq-script-packages p.3 | STATED |
| STD-NAM-04 | Parameters prefixed `i_` | FormalParameter name not `^i_` | warning | naming-conventions p.3 | STATED |
| STD-NAM-05 | Boolean names start with a predicate | boolean-typed decl not `^[cbli]_(is\|do\|has\|enbl\|dsbl)_`; boolean function not `^(\w+#)?(is\|do\|has\|enbl\|dsbl)_` | warning | naming-conventions pp.2-3 | STATED (position INFERRED) |
| STD-NAM-06 | ID-typed names end in `<target>_id` | type `id [table] (obj_\|code_\|meta_)?X` and name not `X_id$` | warning | naming-conventions p.2 | STATED (DB FKs); INFERRED (DDIC/vars) |
| STD-NAM-07 | Singular names | name element matching an English plural (`\w+s$` minus glossary whitelist) | info | naming-conventions p.2 | STATED |
| STD-NAM-08 | Glossary abbreviations only | name element not in glossary dictionary | info | naming-conventions p.1 | STATED (needs glossary) |
| STD-NAM-09 | Underscore compounds, no camelCase | `[a-z][A-Z]` inside identifier; regex `^[a-z][a-z0-9_#$]*$` | warning | naming-conventions pp.1-2 | STATED/INFERRED |
| STD-NAM-10 | Code-table constant contains its intl_id and ends `_id` | `c_\w+ constant .* := lookup.code\(.*'(\w+)'` with name lacking `\1` or `_id$` | info | naming-conventions p.3 | STATED |
| STD-NAM-11 | Content-description suffix on constants/variables | name lacks a suffix from `_id\|_code\|_name\|_cnt\|_text\|_date\|_nr\|_list` | info | naming-conventions pp.3-4 | STATED (list INFERRED) |
| STD-NAM-12 | 2-char SQL aliases | alias in an SQL-notation string not in the alias table | info | naming-conventions pp.4-5 | STATED |
| STD-NAM-13 | Record types prefixed `t_` | `type \w+ is record` name not `^t_` | info | data-types pp.34, 38 | INFERRED |
| STD-NAM-14 | Test sources `<client>$IT_...`/`it_`/`ut_` | source name in ATS app not matching `^(\w+\$)?(it\|ut)_` (case-insensitive) | info | 02b_Test_sources p.1 | STATED |
| STD-COR-01 | `case` must have `else` | AST: CaseStatement without an Else branch | error | hints-and-tips pp.1-2 | STATED |
| STD-COR-02 | No session values cached in package constants / `b_` vars | package-level `c_`/`b_` initialiser or assignment referencing `session\.` or `\$base_par_` | error | naming-conventions p.3 | STATED |
| STD-COR-03 | DDIC list not stored, passed or returned without a collection | list-typed value on the right of `:=`, as an argument or as a return value | error | hints-and-tips p.5 | STATED |
| STD-COR-04 | No LIST_CHAR/LIST_DATE/LIST_NUMBER in script | `\blist_(char\|date\|number)\b` outside strings, not in `id table list_number` from `.store` | error | hints-and-tips p.5 | STATED |
| STD-COR-05 | `deterministic` function must be pure | deterministic body (transitively) calls `session\.`, `.store`, DDIC actions, logging, mutable reads | error | declarations pp.3-4 | STATED (detection INFERRED) |
| STD-COR-06 | `db_side_effect_free` method must not write | body (transitively) calls `.store`, OBJ/DOC DDIC actions, MEM_DOC workflow actions | error | declarations pp.4-5; hints-and-tips p.8 | STATED |
| STD-COR-07 | Not both `deterministic` and `db_side_effect_free` | both modifiers in one header | warning | declarations p.5; hints-and-tips p.10 | STATED |
| STD-COR-08 | postp directives balanced and exactly around the expression | unmatched `/*postp_start*/`/`/*postp_end*/`; span containing `:=` or `;` | warning | hints-and-tips p.10 | STATED |
| STD-COR-09 | No swallowed exceptions | `when others then (null\|return null);` | warning | 02c_Implementing... pp.4-5 (counter-example); hints-and-tips p.8 | INFERRED |
| STD-COR-10 | `err.raise_fa` names the enclosing method | first argument string ≠ `<pkg>.<method>` or `<method>` | info | hints-and-tips p.8; data-types p.42 | INFERRED |
| STD-COR-11 | No `null` assignment to a collection | `<coll var> := null` | error | data-types pp.26, 31 | STATED |
| STD-COR-12 | Modifying a list-field cast does not update the field | `list(x.f)`/`set(x.f)` result assigned then `.add/.remv` with no write-back | warning | data-types pp.26-27 | STATED (detection INFERRED) |
| STD-COR-13 | Path must end in a scalar; unchecked casts | record/DDIC-typed expression used as a value; `ddic(<number var>)` cast | warning | avaloq-script-expressions pp.3-5 | STATED |
| STD-COR-14 | Avoid `session.commit`/`rollback` | `session\.(commit\|rollback)\b` | warning (error in MSG/AMI code or loops) | what-are-data-dictionaries p.8 | STATED |
| STD-COR-15 | No obsolete DDIC fields | attribute in the DDIC "Obsolete" section | warning | what-are-data-dictionaries p.6 | STATED |
| STD-COR-16 | `= null` comparison | `(=\|!=\|<>)\s*null\b` | warning | language-fundamentals p.3 | INFERRED |
| STD-COR-17 | Accumulator used before initialisation | `l_x := l_x [+-*/\|]` with no prior assignment or default | warning | declarations pp.2, 6 | INFERRED |
| STD-COR-18 | Parameter reassigned | `i_\w+ :=` / formal parameter on the left of `:=` | info | declarations pp.5-7 | INFERRED (docs conflict) |
| STD-COR-19 | `sysdate` in business-date comparison | `sysdate` compared with a `*_date` field | info | hints-and-tips p.4 | INFERRED |
| STD-COR-20 | Unreachable `elsif` | numeric range in elsif already covered by an earlier branch | warning | 02c_Implementing... pp.4-5 | INFERRED |
| STD-PRF-01 | `case` instead of an `elsif` chain (~10% faster) | if/elsif of 3+ branches, all `<same expr> = <literal/const>` | warning | hints-and-tips p.1 | STATED |
| STD-PRF-02 | Typed `iffb`/`iffd`/`iffn` instead of `iff` (2-3x / 10x) | `\biff\s*\(`; type of branch args → suggest variant | warning | hints-and-tips p.2 | STATED |
| STD-PRF-03 | `nvl` deprecated → `coalesce` | `\bnvl\s*\(` | info | TOC only | INFERRED |
| STD-PRF-04 | Avoid implicit type conversion | number literal/expression assigned to or compared with `text` (and reverse, date↔text) | warning | hints-and-tips p.2 | STATED |
| STD-PRF-05 | Hoist loop-invariant calls | call in loop body with no dependency on the loop var or loop-assigned vars (`lookup\.`, `session\.`, `to_char`) | warning | hints-and-tips pp.2-3 | STATED |
| STD-PRF-06 | `class_id('x')`, not `class('x').id` | `\.(\w+)\(([^)]*)\)\.id\b` | warning | hints-and-tips p.3 | STATED |
| STD-PRF-07 | `<x>_id` attribute, not `.<x>.id` | `\.(\w+)\.id\b` where DDIC has `\1_id` | warning | hints-and-tips p.3 | STATED |
| STD-PRF-08 | Code constant instead of intl_id string or `lookup.code` in a comparison | `\.intl_id\s*=\s*'`; `=\s*lookup\.code\(` | info | hints-and-tips p.3 | INFERRED |
| STD-PRF-09 | `with` for repeated long paths | same prefix of ≥2 dots repeated ≥3 times in one statement/block | info (warning on memory DDICs) | hints-and-tips p.4 | STATED |
| STD-PRF-10 | `for x in list`, not an index loop (n² vs n) | `for i in 1 .. (\S+)\.count loop` with `\1\(i\)` or `.get(i)` in the body | warning | hints-and-tips pp.4-5 | STATED |
| STD-PRF-11 | Same-row reads interleaved with possibly-writing calls (3 selects vs 1) | ≥2 `alias.attr` reads of one DDIC instance separated by calls not `db_side_effect_free`/`deterministic`; message "Missed performance optimization opportunity" | warning | hints-and-tips pp.5-7 | STATED |
| STD-PRF-12 | Constant-argument `lookup.code` wrapper should be `deterministic` | public function returning `lookup.code(...)` of its params, called with literals, no `deterministic` | info | hints-and-tips pp.9-10 | STATED |
| STD-PRF-13 | `.store` in loop or `on level_*` handler | `\.store\b` inside a loop/handler body | warning | data-types pp.29-30 | STATED |
| STD-PRF-14 | Repeated `.store` on the same variable | ≥2 `x.store` in one scope | warning | data-types pp.29-30 | STATED |
| STD-PRF-15 | `.store` only to pass data to PL/SQL | stored id used only as an argument to a `#.` native call | info | data-types p.29 | STATED |
| STD-PRF-16 | Collection assignment copy in a loop | `:=` between collection-typed vars inside a loop | warning | data-types pp.26, 31 | STATED |
| STD-PRF-17 | Repeated list-field cast in a loop | `(list\|set)\(\w+(\.\w+)+\)` inside a loop on the same field | info | data-types pp.26-27 | STATED |
| STD-PRF-18 | `remv` in a loop (O(n²)) | `\.remv\(` inside a loop | info | data-types pp.8-14 | STATED |
| STD-PRF-19 | Prefer ID-typed parameters to record types | parameter of DDIC record type used only for its id | info | data-types p.3 | STATED |
| STD-TST-01 | Helper named `it_*`/`ut_*` runs as a test | procedure `^(it\|ut)_` in a test package that is not meant as a test (no assert/require) | info | 02b_Test_sources p.2 | STATED |
| STD-TST-02 | Rerunnable tests | literal unique key / intl_id in a test without `it.ats_script_run_id` | warning | 02c_Implementing... p.1 | STATED |
| STD-TST-03 | Test procedure exception block calls `it.catch('<proc>')` | `it_\w+` procedure lacking `when others then it.catch` | info | 02a_Creating_a_simple_test p.1 | STATED (as convention) |
| STD-TST-04 | Production code must not depend on ATS sources | import or reference from a non-ATS source to an ATS source | warning | 02b_Test_sources p.1 | INFERRED |
| STD-TST-05 | Inject session values into calculation functions | `session\.today` / base-parameter read inside a non-wrapper function | info | 02c_Implementing... p.4 | STATED |

Counts: 59 knowledge entries (KB-STD-01..59); 71 catalogue rules (STD-FMT 13, STD-NAM 14, STD-COR 20, STD-PRF 19, STD-TST 5); 19 rules are fully or partly INFERRED (Basis column).
