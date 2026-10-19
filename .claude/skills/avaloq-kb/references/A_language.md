# A. LANGUAGE (SEC code LANG)

Sources merged: `verified/G1_verified_partA.md`, `verified/G1_verified_partB.md`, `verified/G2_verified.md`, plus language and syntax facts from official examples in `verified/G5_verified.md` and `verified/G6_verified.md`. Verifier corrections are applied, and no entry was REJECTED. Cites are relative to `source_text/`. Secondary-note claims from G6 appear only where the official check settles them.

## What a model must know first

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

---

## A1 Lexical

### KB-LANG-01 Character set is ASCII letters, digits and a fixed symbol set
- Fact: The language uses the letters A-Z/a-z, the digits 0-9 and the symbols `~ ! @ # $ % & * ( ) _ - + = | [ ] { } : ; " ' < > ? /`. Terminal symbols are defined over ASCII. `.` and `,` are missing from the symbol row but appear in the delimiter table.
- Cite: paged/text/language-fundamentals.txt p.1 "Language fundamentals"
- Basis: STATED (treating other characters outside strings and comments as lexical errors is INFERRED)
- VERIFY: Q06 PARTIAL — the lexical layer is documented.
- Audit use: lexer character classes. Add `.` and `,`.
- From: G1-06

### KB-LANG-02 Whitespace is free-format but must not split a symbol
- Fact: Blanks and line breaks must not occur inside symbols. Comments are an exception, and so are blanks inside strings. Otherwise whitespace is ignored unless it separates two consecutive symbols.
- Avaloq form: "Blanks (space characters) and line breaks must not occur within symbols (except in comments, and, in the case of blanks, in strings)."
- Means: compound tokens such as `:=`, `<=`, `!=`, `||`, `=>`, `..`, `--`, `/*` contain no internal space. Read literally, the sentence also bars line breaks inside string literals.
- Cite: paged/text/language-fundamentals.txt p.1 "Language fundamentals" (Note)
- Basis: STATED (the rule about line breaks in strings is INFERRED from the wording)
- From: G1-07

### KB-LANG-03 Case: "uppercase and lowercase letters are distinct", yet all code must be lowercase
- Fact: The character-set note says "Uppercase and lowercase letters are considered as distinct." It does not say whether this covers identifier matching, keywords or both. The coding conventions require that "All code must be written in lower case." The docs' own examples break this with `Avaloq` (identifier example list) and `exampleProcedure` (Hints p.9). The header appears both as `[Script 1.0]` and `[script 1.0]`.
- Means: do not case-fold identifiers blindly. A mixed-case identifier is at least a convention breach. Whether the compiler is case-sensitive is unknown.
- Cite: paged/text/language-fundamentals.txt p.1 "Language fundamentals" ; paged/text/coding-conventions.txt p.2 "Code" ; paged/text/hints-and-tips-on-using-avaloq-script.txt p.9 "Use of deterministic"
- Basis: STATED (sentence and convention); INFERRED (that it means case-sensitive name resolution)
- VERIFY: Q06 EXTENDS — this differs from PL/SQL case-insensitivity, and its scope is unresolved. Q31 CONFIRMS for the lowercase convention.
- Audit use: style rule for `[A-Z]` in tokens outside strings and comments, at warning severity.
- From: G1-08, G1-53, G1-84, G6-05

### KB-LANG-04 Lexical units
- Fact: Characters group into identifiers, numbers, strings, delimiters and operators, and comments.
- Cite: paged/text/language-fundamentals.txt p.1 "Language fundamentals"
- Basis: STATED
- VERIFY: Q06 CONFIRMS
- From: G1-09

### KB-LANG-05 Identifier rule (published EBNF)
- Fact: Identifiers name constants, variables, exceptions, procedures and reserved words. They are letters, digits and underscores, and must start with a letter.
- Avaloq form:
```
ident = letter { letter | digit | _ } .
x Avaloq i_curry_id put_extl_msg
```
- Cite: paged/text/language-fundamentals.txt p.1 "Identifiers"
- Basis: STATED
- VERIFY: Q06 PARTIAL
- Audit use: base regex `[A-Za-z][A-Za-z0-9_]*`. KB-LANG-06 extends it.
- From: G1-10

### KB-LANG-06 CONFLICT: identifiers in official code contain `#` and `$`
- Fact: CONFLICT. The EBNF (KB-LANG-05) allows only letters, digits and `_`. Official examples, however, use `#` and `$` inside names: `cont#pos_id`, `cont#val_bu`, `obj#put`, `obj#text`, `code#text`, `url#simple_esc`, `person#gen`, `mba$dwh`, `acd$acad_ctx_start`, `mdb$it_addr_create`, `rm$code_it_cont_name`. A natively imported PL/SQL package is called with a trailing `#.`: `custom_package#.fill_custom_list(...)`. Observed usage: `#` marks `<object>#<operation>` method names, and `<prefix>$` marks a client-key or namespace prefix (`<client key>$IT_...`, "use the prefix it_ or the infix xxx$it_"). Neither meaning is defined in the language reference.
- Avaloq form: `function cont#pos_id(cont obj_cont, asset_key text)` ; `mba$dwh.put_line(mba$dwh.obj#text('id', obj));`
- Means: the lexer must accept `[A-Za-z][A-Za-z0-9_#$]*`. `#` is not a namespace separator, because namespaces use `$`.
- Cite: paged/text/declarations-in-avaloq-script.txt p.6 "Formal parameters" ; paged/text/hints-and-tips-on-using-avaloq-script.txt pp.5-8 "Optimizing accesses to the same database table" ; paged/text/avaloq-script-expressions.txt p.4 "References and function calls" ; paged/text/data-types.txt p.34 "Passing collections from Avaloq Script to PL/SQL procedures" ; layout/02-techbase/02_05_Language_elements_used_in_Avaloq_Script.txt "Script packages" ; layout/04-test-framework/pages/02b_Test_sources.txt p.1 "Naming conventions"
- Basis: STATED (examples); INFERRED (the meaning of `#` and `$`)
- VERIFY: Q06 CONTRADICTS (the EBNF is incomplete); Q02 PARTIAL / Q31 EXTENDS (`xxx$` reads as a custom-layer prefix)
- From: G1-11, G2-11, G2-46, G5-66, G5-74, G5-102, G6-15

### KB-LANG-07 Numbers: unsigned integer or real, both of type `number`
- Fact: A number is an unsigned integer or a real, and a real always contains a decimal point. Both have type `number`. There is no exponent form and no leading-dot form, and a sign is a unary operator.
- Avaloq form:
```
number  = integer | real .
integer = digit { digit } .
real    = digit { digit } . { digit } .
2002
3.1415926
```
- Cite: paged/text/language-fundamentals.txt pp.1-2 "Numbers"
- Basis: STATED (the regex `\d+(\.\d*)?` is INFERRED)
- Audit use: lexer. Do not read `1.` as a real when another `.` follows (`1 .. n` range).
- From: G1-12

### KB-LANG-08 Strings: single OR double quotes, escaped by doubling
- Fact: A string is enclosed in single (`'`) or double (`"`) quotes, and the opening and closing quote must match. To include the quote mark itself, write it twice. The published EBNF has a typo: both alternatives show `'`. Official code uses double-quoted strings: `l_text_set.add("hello")`, `topic => "Approval"`, `assertion => "it_cont_name_part for " || cn.intl_id`. A secondary claim that only single quotes are allowed is contradicted.
- Avaloq form:
```
'This is some text'
"This is some text"
"This is some text that includes a "" double quote in the middle of the text"
```
- Means: unlike PL/SQL, `"..."` is a string literal, not a quoted identifier (except in a path, KB-LANG-09).
- Cite: paged/text/language-fundamentals.txt p.2 "Strings" ; paged/text/data-types.txt p.15 "set<V>" ; layout/04-test-framework/pages/02c_Implementing_the_construction_tests.txt pp.3-4 "Store static data, input and expected outputs in code tables"
- Basis: STATED (the typo diagnosis is INFERRED)
- VERIFY: Q06 CONFIRMS/EXTENDS — double-quoted strings depart from PL/SQL; the single-quote-only assumption is CONTRADICTED.
- Audit use: two token forms, `'([^']|'')*'` and `"([^"]|"")*"`.
- From: G1-13, G6-10, G2-06, G2-33, G5-80

### KB-LANG-09 Keyword segments in a data-access path are quoted
- Fact: If part of a data-access expression is a keyword, you must enclose it in single or double quotes.
- Avaloq form: `node."as".val_nr`
- Means: after a `.` in a designator, a quoted token is an identifier segment, not a string literal.
- Cite: paged/text/avaloq-script-expressions.txt p.3 "Data access expressions" (Note)
- Basis: STATED
- VERIFY: Q06 EXTENDS
- From: G2-09, G6-58

### KB-LANG-10 Literal values
- Fact: The literals are numbers, strings, the booleans `true` and `false`, and `null`.
- Cite: paged/text/avaloq-script-expressions.txt p.3 "Literal values"
- Basis: STATED
- VERIFY: Q06 PARTIAL
- From: G2-10

### KB-LANG-11 Boolean data is the single character `'+'` (true) / `'-'` (false)
- Fact: SQL has no boolean, so Avaloq Script represents boolean data as one character, `"+"` for true and `"-"` for false. Methods such as `contains`, `exist` and `is_equal` return `'+'`/`'-'`, and code compares them as `= '+'`. The literals `true`/`false` also exist, and a boolean value can be a condition directly (`if l_map.get("a") then`). For PL/SQL, boolean maps to `varchar2(1) or boolean`, not `number(1)`/`char(1)`. Test logs render true as `"+"`.
- Avaloq form: `if l_text_set.contains("hello") = '+' then`
- Means: `x = '+'` is a boolean test. `sort('-')` means descending.
- Cite: paged/text/data-types.txt p.1 "Base data types" ; paged/text/data-types.txt p.16 "set<V>" ; paged/text/data-types.txt p.22 "map<K,V>" ; paged/text/data-types.txt p.43 "Mapping Avaloq Script data types to PL/SQL" ; paged/text/avaloq-script-expressions.txt p.3 "Literal values" ; layout/04-test-framework/pages/02a_Creating_a_simple_test.txt p.2 "Run the test"
- Basis: STATED
- VERIFY: Q06 EXTENDS
- Audit use: treat `= '+'` / `= '-'` and `true`/`false` as equivalent in boolean checks.
- From: G2-23, G2-34, G6-28, G5-64

### KB-LANG-12 Delimiter table (with its ambiguities)
- Fact: The delimiters are `/* */` (comment), `,` (separates elements), `.` (data access, dot notation), `;` (terminates a statement), `=` ("assignment or, in a conditional expression, equality"), `:` (host variables), `( )` (lists, expressions, iteration factors), `=>` ("locator qualification") and `'` or `"` (enclose constants). Every code example assigns with `:=`, which this table does not list, and `..` (range) is missing too. In every example `=>` is used for named arguments. Host variables are never explained.
- Cite: paged/text/language-fundamentals.txt p.2 "Delimiters and operators"
- Basis: STATED (reading `=>` as named-argument notation is INFERRED; see KB-LANG-43)
- VERIFY: Q06 PARTIAL; Q08 EXTENDS (dot notation is the data-access syntax)
- Audit use: `;` terminator. Keep a `:name` token for host variables. Do not treat `=` as assignment.
- From: G1-14, G6-06, G6-08

### KB-LANG-13 Comments: `/* ... */` and `--`, not nestable, but directive comments carry meaning
- Fact: A comment may appear between any two symbols, as `/* ... */` or as `--` to end of line. Comments cannot be nested and "do not affect the semantics of a program". Exception: the comment-shaped directives `/*postp_start*/` and `/*postp_end*/` are read by the compiler (KB-LANG-26).
- Avaloq form:
```
/*  Comment, possibly spread  over multiple lines*/
-- single line comment
```
- Cite: paged/text/language-fundamentals.txt p.4 "Comments" ; paged/text/hints-and-tips-on-using-avaloq-script.txt p.10 "Use of deterministic"
- Basis: STATED
- VERIFY: Q06 CONFIRMS; Q13 EXTENDS (directives written as comments)
- Audit use: the first `*/` closes a block comment. A lossless lexer keeps comments and recognises postp directives.
- From: G1-22, G6-11

### KB-LANG-14 Reserved words: identifiers by definition, but no list is published
- Fact: The doc says identifiers name "reserved words", but Language fundamentals and Declarations give no reserved-word list. Keywords used as path segments must be quoted (KB-LANG-09).
- Means: the following candidate keyword set is INFERRED from the EBNF fragments and examples: is, begin, end, procedure, function, return, constant, type, record, import, native, script, package, public, private, protected, final, abstract, deterministic, db_side_effect_free, declare, exception, when, others, if, then, elsif, else, case, for, in, loop, while, with, as, do, new, and, or, not, mod, like, between, null, true, false, id, table, default.
- Cite: paged/text/language-fundamentals.txt p.1 "Identifiers"
- Basis: STATED (the statement); INFERRED (the absence of a list, and the keyword set)
- Audit use: verify the keyword set on the corpus before rejecting any identifier.
- From: G1-A-ADD-04

---

## A2 Source and package structure

### KB-LANG-15 A script package is one compilable unit (no spec/body split)
- Fact: An Avaloq Script package is a source type containing Avaloq Script code. It is a compilable unit that may hold constant and variable declarations and executable functions and procedures. There is no separate specification. Visibility comes from modifiers (KB-LANG-22).
- Avaloq form: "An Avaloq Script package is a type of source that contains code written using the Avaloq Script language. It is some text that is a compilable unit."
- Cite: paged/text/what-are-avaloq-script-packages.txt p.1 ; layout/02-techbase/02_04_What_are_Avaloq_Script_packages.txt
- Basis: STATED (single unit); INFERRED ("no spec": a spec is never shown)
- VERIFY: Q01 PARTIAL (script package is a source type); Q07 EXTENDS
- From: G2-57, G6-02

### KB-LANG-16 `[script 1.0]` header line (pre-compiler statement, column 1)
- Fact: Like every source type, a script package starts with a header that declares the source type, version and name: `[script 1.0]` followed by `script package <name>` / `is`. The Coding conventions write it `[Script 1.0]` and call it a compiler- or pre-compiler-specific statement that starts in column 1, without the two-space margin. The official ATF example starts directly at `script package it_hello`, with no header.
- Avaloq form:
```
[Script 1.0]

script package format
is
```
- Cite: paged/text/what-are-avaloq-script-packages.txt p.1 ; paged/text/coding-conventions.txt pp.3-4 "Margins" ; paged/text/data-types.txt p.41 "Example for MEM_TAB vs LIST" ; layout/04-test-framework/pages/02a_Creating_a_simple_test.txt p.1 "Create the test"
- Basis: STATED (that every exported file starts with it is INFERRED)
- VERIFY: Q13 EXTENDS (pre-compiler header); Q03 PARTIAL (export format undocumented); Q01 EXTENDS
- Audit use: accept `[script N.N]` in either case, and also a missing header. Never fail a file for lacking one. Other versions and other "pre-compiler statements" are unknown.
- From: G1-57, G2-54, G2-58, G6-01

### KB-LANG-17 Package parts and order
- Fact: A package has a header, imports, package (body) variable declarations visible throughout the source, procedures and functions, and a footer (`end <name>;`). Constants also live at package level, and record types can be defined only there. Where record types go relative to variables is not stated.
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
-- Procedure
   procedure proc1
   is
   begin
     null;
   end proc1;

-- Function
   function func1
   return number
   is
   begin
     return 1;
   end func1;

end packagename;
```
- Cite: paged/text/what-are-avaloq-script-packages.txt pp.1-3 (figure "Structure of an Avaloq Script package") ; paged/text/data-types.txt p.38 "Record type definition"
- Basis: STATED
- VERIFY: Q06 EXTENDS; Q02 PARTIAL; Q03 PARTIAL
- Audit use: section-order check (warning only).
- From: G2-58, G6-03

### KB-LANG-18 `import` / `import native`, one per line, usable inside methods too
- Fact: To use another script package you import it (`import util;`), one per line, and refer to its elements as `<package-name>.<name-of-element>`. The EBNF also has `import native <ident>`, which is not explained (it is used for PL/SQL packages, KB-LANG-84). The method EBNF places an `ImportSequence` inside method bodies too. Official code uses `session.*`, `lookup.*`, `mdb_*`, `meta_typ.*` and `code_*` without imports. SESSION and LOOKUP are always-available DDICs, not packages. `import session;` is UNSUPPORTED.
- Avaloq form:
```
ImportSequence = { Import ; }.
Import = import [ native ] ident .
```
- Cite: paged/text/declarations-in-avaloq-script.txt p.5 "Syntax for declaring procedures and functions" ; layout/02-techbase/02_05_Language_elements_used_in_Avaloq_Script.txt "Script packages" ; paged/text/coding-conventions.txt p.4 "Margins" ; paged/text/what-are-data-dictionaries.txt p.7
- Basis: STATED (that a missing import is a compile error is INFERRED; the built-in namespace exemption is INFERRED from usage)
- VERIFY: Q02 PARTIAL; Q05 EXTENDS (imports are dependency edges); Q12 PARTIAL (`import native`)
- Audit use: resolve `pkg.member` against the imports, with an allowlist for built-in DDIC roots. Flag unused imports.
- From: G1-35, G1-86, G6-04, G6-71, G5-62

### KB-LANG-19 `end <name>;` repeats the method or package name
- Fact: The procedure or function identifier is repeated at the end of its declaration (`end ident` in the EBNF), and a package ends with `end <package>;`. The function and procedure diagrams in "What are Avaloq Script packages" omit the `;` after `end func1`/`end proc1`, while all code listings include it.
- Avaloq form: "The procedure or function identifier is repeated at the end of the procedure declaration."
- Cite: paged/text/declarations-in-avaloq-script.txt p.3 "Declaring procedures and functions" ; paged/text/declarations-in-avaloq-script.txt p.5 "Syntax for declaring procedures and functions" ; paged/text/what-are-avaloq-script-packages.txt pp.3-4
- Basis: STATED
- VERIFY: Q06 CONFIRMS
- Audit use: block matcher. A mismatch between the `end` identifier and the method name is a compile-level finding.
- From: G1-30, G2-60, G6-07

### KB-LANG-20 Published method-declaration EBNF (verbatim, with its defects)
- Fact: This is the published EBNF for procedures and functions. Known defects: `IndetDef` is a typo for IdentDef. The header uses `[TopLevelModifier]*` but the rule is named `TopLevelModifiers`. There is no exception section, though examples use one (KB-LANG-57). There is no exception declaration. Neither a parameterless function with a return type nor `()` can be derived (KB-LANG-37). Record type declarations are absent (KB-LANG-27).
- Avaloq form:
```
MethodDeclaration = MethodHeader
                    is
                    ImportSequence
                    DeclarationSequence
                    begin
                    StatementSequence
                    end ident .
MethodHeader = [TopLevelModifier]*
               ([db_side_effect_free] procedure | [deterministic | db_side_effect_free] function) IndetDef
               [FormalParameters] .
TopLevelModifiers = [public | private | protected] | [final | abstract]
ImportSequence = { Import ; }.
Import = import [ native ] ident .
DeclarationSequence = { Declaration ; }.
Declaration = ConstantDeclaration | VariableDeclaration | MethodDeclaration .
```
- Cite: paged/text/declarations-in-avaloq-script.txt p.5 "Syntax for declaring procedures and functions"
- Basis: STATED (EBNF checked on the PDF image); INFERRED (defect list)
- VERIFY: Q06 PARTIAL (fragmentary and inconsistent); Q07 CONFIRMS/EXTENDS
- Audit use: a grammar seed only. Extend it for exception sections, defaults, `()`, record types and generic types.
- From: G1-35

### KB-LANG-21 Nested methods, local items, recursion, visibility of outer items
- Fact: Constants, variables and procedures declared in a method's declaration sequence are local. Procedure declarations can be nested, and a call inside a procedure's own declaration is recursion. Items in the environment are visible unless a same-named local item hides them.
- Avaloq form: "Because procedures can be declared as local items, too, procedure declarations can be nested. The call of a procedure within its declaration implies recursive activation."
- Cite: paged/text/declarations-in-avaloq-script.txt p.3 "Declaring procedures and functions"
- Basis: STATED (a resolution order of local -> enclosing -> package -> imports is INFERRED)
- Audit use: the symbol extractor handles nested methods. Build a recursion edge in the call graph.
- From: G1-32, G1-33

### KB-LANG-22 Visibility and inheritance modifiers exist, but their semantics are undocumented
- Fact: The method EBNF allows `public | private | protected` and `final | abstract` as top-level modifiers. The `*` suggests a visibility and an inheritance modifier can be combined (INFERRED). Record types take an optional `private`, which makes the type invisible outside the defining package; without it the type is visible outside. No doc explains protected, final or abstract.
- Cite: paged/text/declarations-in-avaloq-script.txt p.5 "Syntax for declaring procedures and functions" ; paged/text/data-types.txt p.37 "Record type definition"
- Basis: STATED (keywords); INFERRED (combination; default-public for methods)
- VERIFY: Q07 CONFIRMS (visibility exists) / EXTENDS (final/abstract)
- Audit use: the parser accepts all five. A public-API surface check becomes possible.
- From: G1-35, G2-47, G6-22

### KB-LANG-23 `deterministic` (functions only): an unchecked compiler hint for install-time evaluation
- Fact: `deterministic` is an optional hint that lets the compiler assume the same result for the same arguments. When the arguments are known at design time, the compiler can evaluate the call and replace it with the result at the end of installation ("evaluated once, with a cached result at installation time"). The developer must guarantee three things: no side effects, the same value for the same arguments, and references only to DB objects fixed by installation time. The compiler cannot check these. The following are not evaluated at installation: private and nested functions, private and local constants, and calls with non-constant or non-deterministic arguments. The hint does not force optimisation. `deterministic` implies `db_side_effect_free`.
- Avaloq form:
```
deterministic function wfs_id(
  i_intl_id                                     text
) return id table wfc_status
```
- Cite: paged/text/declarations-in-avaloq-script.txt pp.3-4 "Deterministic functions" ; paged/text/hints-and-tips-on-using-avaloq-script.txt pp.9-10 "Use of deterministic"
- Basis: STATED
- VERIFY: Q13 EXTENDS; Q26 CONFIRMS
- Audit use: a `deterministic` function that calls `session.*`, store operations or DDIC actions, or reads mutable data, is suspect.
- From: G1-34, G1-82, G6-19

### KB-LANG-24 `db_side_effect_free` (procedures and functions, top-level and local)
- Fact: An optional, unchecked hint that the method makes no observable or readable DB changes, so the compiler may optimise queries better. The developer must ensure that no DDIC access could return a different value before and after the call. Methods that are NOT side-effect free run store operations, run actions on an OBJ or DOC layer DDIC, or run a workflow action on a MEM_DOC layer DDIC. Methods that ARE side-effect free do pure in-memory calculation or only logging.
- Avaloq form: `db_side_effect_free procedure put_line( i_text text := null )`
- Cite: paged/text/declarations-in-avaloq-script.txt pp.4-5 "Database side effect free procedures and functions" ; paged/text/hints-and-tips-on-using-avaloq-script.txt pp.7-8 "Use of db_side_effect_free"
- Basis: STATED
- VERIFY: Q13 EXTENDS; Q26 CONFIRMS
- Audit use: correctness check on marked methods that (transitively) store or run DDIC or workflow actions.
- From: G1-42, G1-81, G6-20

### KB-LANG-25 `deterministic` and `db_side_effect_free` are alternatives on a function
- Fact: The EBNF offers `[deterministic | db_side_effect_free] function`, so a function takes one or the other. Since "deterministic implies db_side_effect_free", writing both is never needed. Whether the compiler rejects both together is not stated. A secondary template stacking both is contradicted.
- Cite: paged/text/declarations-in-avaloq-script.txt p.5 "Syntax for declaring procedures and functions" ; paged/text/hints-and-tips-on-using-avaloq-script.txt p.10 "Use of deterministic"
- Basis: STATED
- VERIFY: Q07 CONTRADICTS (the stacked-modifier template)
- Audit use: flag both on one function as redundant or invalid (warning).
- From: G1-35, G6-21

### KB-LANG-26 `/*postp_start*/ ... /*postp_end*/` marks one expression as deterministic
- Fact: To mark an expression as deterministic, enclose exactly that expression between the `postp_start` and `postp_end` directives. Enclosing `:=` or `;` is wrong, and the compiler then ignores the directives silently. The same conditions apply as for deterministic functions. This is not the preferred style (it must be repeated per call), and it is only a hint. The extracted text shows the trailing comments as `–-` (an en dash), which is a typography artefact.
- Avaloq form:
```
l_foo_wfs_id := /*postp_start*/ wfs_id('foo') /*postp_end*/;
c_num constant number := /*postp_start*/ 2 + 2 /*postp_end*/; -- OK
c_num constant number /*postp_start*/ := 2 + 2 /*postp_end*/; -- NOK, ':=' does not belong to the expression
c_num constant number := /*postp_start*/ 2 + 2; /*postp_end*/ -- NOK, ';' does not belong to the expression
```
- Cite: paged/text/hints-and-tips-on-using-avaloq-script.txt p.10 "Use of deterministic"
- Basis: STATED
- VERIFY: Q13 CONFIRMS
- Audit use: keep these as directive tokens. Flag unbalanced pairs and spans that contain `:=` or `;`.
- From: G1-83

### KB-LANG-27 Record types (Compiler Framework 18.0): package level only
- Fact: `[private] type <name> is record ( <field> <type> {, ...} );` defines a record type. Fields are read and written with dot notation, and the compiler enforces type validation. Records work in procedures, functions, variables, constants and DDIC collections. They can be defined only at package level. A record variable takes assignment only from a record of the same type. Null checks and `=`/`<`/`>` comparisons on records cause compiler errors. The published EBNF restricts `data_type` to a bare identifier, which looks too narrow, and its `")";` ending does not match the `);` used in the examples. Examples use the `t_` prefix (`t_font`), but `address` has none.
- Avaloq form:
```
record_type_definition ::= [ "private" ]
                           "type" type_name "is" "record"
                           "(" field_list ")";
field_list             ::= field_definition { "," field_definition };
field_definition       ::= field_name data_type;
type_name              ::= identifier;
field_name             ::= identifier;
data_type              ::= identifier;
identifier             ::= letter { letter | digit | "_" };

private type t_font is record(
    name    text
   ,size    number
   ,color   text
);
```
- Cite: paged/text/data-types.txt pp.36-38 "Record types in Avaloq Script", "Record type definition", "Working with record variables", "Limitations" ; paged/text/data-types.txt p.34 "Avaloq Script compound (record) types"
- Basis: STATED ("if defined" in the private description reads as "if not defined", an INFERRED typo)
- VERIFY: Q06 EXTENDS; Q07 EXTENDS; Q27 EXTENDS
- Audit use: errors for a local `type ... is record`, for `<record> is null` and for `<rec> = <rec>`.
- From: G2-47, G2-48, G6-13, G6-43

### KB-LANG-28 Anonymous block `declare ... begin ... end;`
- Fact: An anonymous block is `declare <decls> begin <stmts> end;`. Scope rules apply to it ("anonymous block" is a scope kind).
- Avaloq form:
```
declare
  l_number number;
begin
  l_number := 10;
end;
```
- Cite: paged/text/hints-and-tips-on-using-avaloq-script.txt p.2 "Avoid implicit data type conversions" ; paged/text/declarations-in-avaloq-script.txt p.1
- Basis: STATED
- From: G1-47

---

## A3 Declarations and parameters

### KB-LANG-29 Every identifier must be declared; scope is textual from the declaration point
- Fact: Every identifier in a program must be declared, either in a block's declaration section or as a package global. Scope runs from the declaration to the end of the enclosing block (package, procedure, function or anonymous block), minus the scopes of same-named items in nested blocks. No identifier may be declared twice in one block. Identifiers for object fields are valid only inside object designators.
- Avaloq form: "No identifier can denote more than one item within a given scope (no identifier can be declared twice in a block)."
- Cite: paged/text/declarations-in-avaloq-script.txt p.1 "Declarations in Avaloq Script"
- Basis: STATED (that use-before-declaration is an error is INFERRED)
- VERIFY: Q08 EXTENDS
- Audit use: resolver. Exempt imports, built-ins, DDIC names and implicit loop or with variables (KB-LANG-52, -54). Field names resolve against the designator's DDIC.
- From: G1-23, G1-24, G1-25

### KB-LANG-30 Variable declaration: `ident Type [:= Expression]` (no colon, no `:=` required)
- Fact: A variable declaration is an identifier, a type and an optional `:= Expression`, terminated by `;` in a DeclarationSequence. `Type = BaseType | IdType | ObjectType`.
- Avaloq form:
```
VariableDeclaration = ident Type [ := Expression ] . Type = BaseType | IdType | ObjectType .
i                         number
l_bp_id                   id obj_bp
l_val_calc_method_id      id table code_val_calc_method
asset                     obj_asset := lookup.asset('novn')
```
- Cite: paged/text/declarations-in-avaloq-script.txt p.2 "Declaring variables"
- Basis: STATED
- VERIFY: Q06 PARTIAL
- From: G1-26

### KB-LANG-31 Defaults are evaluated at runtime on scope entry; otherwise the value is null
- Fact: The default expression is evaluated at runtime when the scope is entered. Without a default the variable starts as null. As in PL/SQL, null represents a missing or unknown value.
- Avaloq form: "If no default value is specified, the variable is initially set to null."
- Cite: paged/text/declarations-in-avaloq-script.txt p.2 "Declaring variables", "Null values"
- Basis: STATED
- VERIFY: Q06 EXTENDS
- Audit use: an accumulator used as `x := x + ...` without initialisation stays null (official examples initialise with `l_val := 0`).
- From: G1-27, G1-28, G6-24

### KB-LANG-32 Constants: `ident constant Type := Expression`, with a value that may be computed at runtime
- Fact: A constant is declared `ident constant Type := Expression`. Its value need not be known at compile time and may be evaluated at runtime. Constants and package variables are cached values that are not recalculated on a session switch, so session-related values (especially base parameters) must not be cached in them.
- Avaloq form:
```
c_max_cnt          constant number      := 100
c_na_text          constant text        := 'n.a.'
c_curr_date        constant date        := session.today
```
- Cite: paged/text/declarations-in-avaloq-script.txt pp.2-3 "Declaring constants" ; paged/text/naming-conventions.txt p.3 "Constants"
- Basis: STATED (that assigning to a constant is an error is INFERRED)
- VERIFY: Q26 EXTENDS; Q27 EXTENDS
- Audit use: flag a package-level constant or `b_` variable whose initialiser uses `session.*`.
- From: G1-29, G1-64, G6-23

### KB-LANG-33 Type forms in declarations: base, id, object/DDIC; no lengths, no `raw`, `long` is not CLOB
- Fact: `BaseType = boolean | text | long | number | date .` and `IdType = id [ table ] ident .` (e.g. `id obj_bp`, `id table code_lang`). A bare DDIC name (`obj_country`, `code_lang`, `obj_pos`, generic `obj`, order types like `doc_stex`) is a record/DDIC type that points to the whole record. `text` holds at most 4000 characters and `long` at most 32,000 (`varchar2(32000)`). Explicit text or number lengths are not supported. There is no `raw` type. Secondary claims of `raw` and `long = clob` are contradicted.
- Cite: paged/text/data-types.txt pp.1-4 "Base data types", "Business-oriented data types" ; paged/text/data-types.txt pp.43-44 "Mapping Avaloq Script data types to PL/SQL" ; layout/04-test-framework/pages/02c_Implementing_the_construction_tests.txt pp.4-5 "Create modular and stateless code"
- Basis: STATED
- VERIFY: Q06 EXTENDS / CONTRADICTS (`raw`, `long`=CLOB)
- Audit use: errors for `text(n)`, `number(p,s)`, `varchar2` and `raw` in declarations.
- From: G2-23, G2-24, G2-25, G2-26, G2-51, G1-92, G6-25, G6-26, G6-27, G6-30, G6-32

### KB-LANG-34 Generic collection types `list<V>`, `set<V>`, `map<K,V>` are auto-initialised
- Fact: Collection variables use Java-style type arguments, may nest, and are initialised automatically (kernel release 5.3 and later). Sets and map keys accept only number, text or DDIC types, so not date. Compiler errors include "Reference to template data dictionary is only allowed with type arguments" (`l_list list;`) and "Unsupported key type. Only number, text, and Avaloq Script DDIC types are allowed key types." A collection cannot be assigned null; use `.clear` (a compile error: "Incompatible types").
- Avaloq form:
```
l_number_list_list     list<list<number>>;
l_text_number_list_map map<text, list<number>>;
```
- Cite: paged/text/data-types.txt pp.7-8 "Collection types" ; paged/text/data-types.txt pp.25-26 "Declaring a collection variable", "Assigning a collection" ; paged/text/data-types.txt pp.31-32 "Compiler error messages"
- Basis: STATED
- VERIFY: Q06 EXTENDS; Q27 CONFIRMS
- Audit use: grammar `type := ident '<' type {',' type} '>'`.
- From: G2-31, G2-35, G2-36, G2-44, G6-34, G6-35

### KB-LANG-35 Function vs procedure: a function has a result type and must `return`
- Fact: A method has a header (identifier plus formal parameters) and a body (optional imports, declarations, statements). A function has a result type after the parameter list, and its body must contain a return statement. A function is called by a function designator inside an expression, and a procedure by a procedure call.
- Avaloq form:
```
function func1 (
      i_param1    number,
      i_param2    text := 'abx'
      )
      return      number
is
      l_var1      number;
begin
      ...
      return l_var1;
end func1
```
- Cite: paged/text/declarations-in-avaloq-script.txt p.3 "Declaring procedures and functions" ; paged/text/what-are-avaloq-script-packages.txt pp.3-4
- Basis: STATED (stronger checks such as all-paths-return are INFERRED)
- Audit use: flag a function without `return <expr>`.
- From: G1-30, G1-31, G2-60

### KB-LANG-36 Formal-parameter EBNF
- Fact: The published formal-parameter EBNF has no mode keyword and no default.
- Avaloq form:
```
FormalParameters = ( FormalParameter { , FormalParameter } ) [ return Type ] .
FormalParameter  = ident Type .
```
- Cite: paged/text/declarations-in-avaloq-script.txt p.6 "Formal parameters"
- Basis: STATED
- VERIFY: Q06 CONTRADICTS (completeness: defaults exist, KB-LANG-41)
- From: G1-36, G1-A-ADD-02

### KB-LANG-37 Parameterless methods: no `()` in examples, `function name()` in conventions, neither derivable from the EBNF
- Fact: Examples declare parameterless methods without parentheses (`procedure exampleProcedure is`, `function func1 return number is`). The Coding conventions header example shows `function name()`. In the EBNF, `return Type` sits inside `FormalParameters`, which needs parentheses and at least one parameter. So neither a parameterless function with a return type nor `()` can be derived. A return type may be `id table <code_table>` or `id <obj_type>`, and `return` may stand on its own line.
- Cite: paged/text/declarations-in-avaloq-script.txt pp.5-6 ; paged/text/hints-and-tips-on-using-avaloq-script.txt p.9 "Use of deterministic" ; paged/text/coding-conventions.txt p.2 "Procedure and function headers" ; paged/text/what-are-avaloq-script-packages.txt p.3
- Basis: STATED (forms); INFERRED (the EBNF gap)
- Audit use: the grammar allows an optional `()` and a `return Type` independent of the parameter list.
- From: G1-40, G1-A-ADD-02, G2-58

### KB-LANG-38 Only value parameters exist: no `in` / `out` / `in out`
- Fact: "Avaloq Script only supports one kind of parameter: value parameters." The formal parameter receives the actual's value as its initial value (copy-in). Writing a mode keyword is illegal, per the EBNF. Results reach the caller only via the function return, via writes to objects or DDICs, or via by-reference collections (KB-LANG-44).
- Avaloq form: "Value parameters are local constants to which the value of the corresponding actual parameter is assigned as the initial value."
- Cite: paged/text/declarations-in-avaloq-script.txt pp.5-6 "Formal parameters"
- Basis: STATED (value only); INFERRED ("illegal", and the results channels)
- VERIFY: Q07 CONTRADICTS (the presupposition of in/out modes)
- Audit use: error on `in`/`out`/`in out` in an Avaloq Script parameter list. Such text is PL/SQL.
- From: G1-36, G6-16

### KB-LANG-39 CONFLICT: are value parameters reassignable?
- Fact: CONFLICT. The prose says value parameters "are local constants". The official `log2` example in the same section assigns to its parameter (`x := x / 2;`). The docs do not say whether `x := ...` on a parameter compiles. Either way the caller never sees the change. Collection parameters can be mutated through their methods (`i_list.add(1)`), and that change IS visible to the caller (KB-LANG-44).
- Avaloq form:
```
function log2(x number)
return number
is
  y number;
begin
  require(x is not null and x > 0, 'x must be a positive number');
  y := 0;
  while x > 1 loop
    x := x / 2;
    y := y + 1;
  end loop;
  return y;
end log2;
```
- Cite: paged/text/declarations-in-avaloq-script.txt p.5 "Formal parameters" (prose) ; paged/text/declarations-in-avaloq-script.txt pp.6-7 (example) ; paged/text/data-types.txt p.27 "Passing a collection as an input parameter"
- Basis: STATED (both texts); INFERRED (the conflict reading)
- VERIFY: Q07 PARTIAL
- Audit use: report a reassigned parameter as a maintainability warning, never as a hard error, until the compiler or corpus confirms.
- From: G1-37, G6-17

### KB-LANG-40 Actual parameters must be assignment compatible
- Fact: If f is a formal parameter and a the actual one, then a must be assignment compatible with f. A formal parameter's scope runs to the end of the procedure block. Positional or named correspondence works the same for function calls as for procedure calls.
- Cite: paged/text/declarations-in-avaloq-script.txt p.6 "Formal parameters" ; paged/text/avaloq-script-expressions.txt pp.3-4 "References and function calls"
- Basis: STATED
- From: G1-38, G2-11

### KB-LANG-41 Parameter defaults `ident Type := expr` (beyond the EBNF)
- Fact: Official examples give parameters defaults: `i_text text := null`, `i_param2 text := 'abx'`, `i_descn text := null`, `i_date date := session.today`. A parameter with a default may be omitted. Testability guidance recommends injecting session values and base parameters as defaulted parameters.
- Avaloq form: `db_side_effect_free procedure put_line( i_text text := null )`
- Cite: paged/text/hints-and-tips-on-using-avaloq-script.txt p.8 "Use of db_side_effect_free" ; paged/text/what-are-avaloq-script-packages.txt pp.3-4 ; layout/04-test-framework/pages/02c_Implementing_the_construction_tests.txt p.3, p.4 "Create modular and stateless code"
- Basis: STATED (examples); INFERRED (the EBNF gap)
- VERIFY: Q07 EXTENDS; Q06 CONTRADICTS (EBNF completeness)
- Audit use: grammar `FormalParameter = ident Type [ := Expression ]`.
- From: G1-39, G2-60, G5-81, G5-102, G6-18

### KB-LANG-42 A collection parameter may default only to `default`
- Fact: Defaults are "not generally allowed for collection-typed parameters". The one exception is the built-in `default`, which gives the type's default (an empty collection). The example also calls itself recursively by its bare name.
- Avaloq form:
```
function example(  i_x    map<number, set<text>> := default
) return boolean
is
begin  return true or example or example(i_x);end example;
```
- Cite: paged/text/data-types.txt pp.25-26 "Declaring an optional collection input parameter"
- Basis: STATED (`booleanis` in the source is a doc typo)
- VERIFY: Q07 EXTENDS
- Audit use: error when a collection parameter defaults to anything except `default`.
- From: G2-35, G6-18

### KB-LANG-43 Named arguments `name => expr`
- Fact: Actual parameters correspond to formal ones positionally or by name with `=>`. Examples include `print_doc(i_doc => l_doc_asset)`, `lookup.code(tab_name => 'wfc_status', val => i_intl_id, fld_list => 'intl_id', cond => ...)`, `mem_doc.postit_list.add(topic => "Approval", ...)` and `l_number_list.remv(pos=>1)`. The delimiter table calls `=>` "locator qualification" and never uses the words "named notation". Leading-comma layout of argument lists is common in examples.
- Cite: paged/text/avaloq-script-expressions.txt pp.3-4 "References and function calls" ; paged/text/hints-and-tips-on-using-avaloq-script.txt p.9 "Use of deterministic" ; paged/text/language-fundamentals.txt p.2 "Delimiters and operators" ; paged/text/data-types.txt p.11 "list<V>" ; layout/04-test-framework/pages/02b_Test_sources.txt pp.5-6 "Example test implementation"
- Basis: STATED (examples); INFERRED (that "locator qualification" means named notation)
- VERIFY: Q07 EXTENDS
- Audit use: grammar `arg := [ident '=>'] expr`.
- From: G1-39, G2-06, G2-11, G2-32, G5-74

### KB-LANG-44 Collections are passed BY REFERENCE (compiled to `in out nocopy`)
- Fact: Collection parameter passing has reference semantics. The generated PL/SQL passes collections as `in out nocopy`, so the callee can modify a collection passed as an input argument. Collection assignment, by contrast, copies (KB-LANG-80). A returned collection can be assigned or used directly (`get_list.add(1)`), and the compiler avoids copies when the returned collection is an input parameter assigned back to the same variable.
- Avaloq form:
```
procedure foo(
  i_list list<number>
) is
begin
  i_list.add(1);
end foo;
...
  foo(l_list);
  l_cnt := l_list.count;  -- l_cnt becomes 1
```
- Means: an `i_` prefix does not make a collection read-only. `concat(b_list, l_list)` mutates `b_list`.
- Cite: paged/text/data-types.txt pp.27-28 "Passing a collection as an input parameter", "Returning a collection"
- Basis: STATED
- VERIFY: Q07 EXTENDS; Q31 PARTIAL
- Audit use: data-effects analysis treats collection arguments as possibly written by the callee.
- From: G2-38, G2-39, G6-36

### KB-LANG-45 Exceptions can be named by identifiers, but no exception declaration is specified
- Fact: Identifiers name "exceptions" among other things. Yet the Declaration EBNF has only constant, variable and method declarations, and no page specifies an exception declaration, `raise`, or the exception section (seen only in examples, KB-LANG-57).
- Cite: paged/text/language-fundamentals.txt p.1 "Identifiers" ; paged/text/declarations-in-avaloq-script.txt p.5 "Syntax for declaring procedures and functions"
- Basis: STATED (both texts); INFERRED (the gap)
- VERIFY: Q11 PARTIAL; Q06 CONTRADICTS (EBNF completeness)
- From: G1-A-ADD-03

---

## A4 Statements

No statement EBNF is published in the corpus. Every statement form below comes from official examples.

### KB-LANG-46 Assignment uses `:=`
- Fact: An assignment replaces the current value of a variable or field with the value of an expression, using `:=`. The target can be a DDIC field, which is how writes happen. `==` does not exist. The delimiter table's "= Indicates assignment" contradicts every example (KB-LANG-12).
- Avaloq form: `l_out := 'Hello world'`
- Cite: layout/02-techbase/02_05_Language_elements_used_in_Avaloq_Script.txt "Avaloq Script statements" ; paged/text/declarations-in-avaloq-script.txt p.6
- Basis: STATED
- VERIFY: Q08 PARTIAL; Q06 PARTIAL
- Audit use: grammar `designator ':=' expr ';'`. A field on the left-hand side is a write.
- From: G1-19, G6-08

### KB-LANG-47 `if ... then ... elsif ... else ... end if;`
- Fact: The conditional statement uses PL/SQL spelling (`elsif`, `end if`). One diagram shows `endif`, which should be read as illustrative only.
- Avaloq form:
```
if a > b then
  do_action_a;
else
  do_action_b;
end if;
```
- Cite: paged/text/coding-conventions.txt pp.2-3 "Statements" ; paged/text/hints-and-tips-on-using-avaloq-script.txt p.1 "Use case instead of elsif batteries" ; paged/text/what-are-avaloq-script-expressions.txt p.2
- Basis: STATED
- From: G1-43, G2-06

### KB-LANG-48 Bare procedure calls and parameterless calls without parentheses
- Fact: A procedure call is a statement (`do_action_a;`, `session.debug(msg);`, `collect.add_postit(i_val_1, i_val_2);`). A function used inside an expression is called when referenced, and a parameterless function is called by its bare name. Parameterless collection methods are written without parentheses (`l_list.count`, `l_list.clear;`, `l_list.sort;`).
- Means: a bare identifier may be a variable or a zero-argument call, and only the symbol table can tell which.
- Cite: paged/text/avaloq-script-expressions.txt pp.3-4 "References and function calls" ; paged/text/data-types.txt pp.8-14 "list<V>" ; paged/text/data-types.txt p.26
- Basis: STATED (calls); INFERRED (the bare zero-argument call, from examples)
- From: G2-11, G2-32, G2-35

### KB-LANG-49 `null;` statement
- Fact: The official package-structure figure has a procedure whose body is `null;`.
- Avaloq form: `procedure proc1 is begin null; end proc1;`
- Cite: paged/text/what-are-avaloq-script-packages.txt p.3 (figure)
- Basis: STATED (figure only)
- From: G2-58

### KB-LANG-50 `case` statement: `else` is required, or ORA-06592 at runtime
- Fact: Only the simple (selector) form is shown: `case <expr> when <value> then ... else ... end case;`. Values may be code constants (`mdb_meta_typ.stex`) or literals. All possible cases must be handled, otherwise ORA-06592 (CASE_NOT_FOUND) is thrown at runtime, so include a default `else`. `case` is "about 10% faster than if".
- Avaloq form:
```
case mod(i, 10)
  when 0 then l_dummy := 0;
  when 1 then l_dummy := 1;
  ...
  else l_dummy := 10;
end case;
```
- Cite: paged/text/coding-conventions.txt p.3 "Statements" ; paged/text/hints-and-tips-on-using-avaloq-script.txt pp.1-2 "Use case instead of elsif batteries"
- Basis: STATED
- VERIFY: Q27 CONFIRMS; Q11 EXTENDS (runtime errors surface as ORA codes)
- Audit use: error rule for a `case` without `else`. Suggest `case` for an if/elsif chain of 3 or more branches on the same expression.
- From: G1-44, G1-68, G1-69, G6-45

### KB-LANG-51 `case` expression form is attested only by a defective example
- Fact: Data types shows a `case` used as an expression value. The printed example has no `then`, which is probably a doc error, so do not derive syntax from it. The expression EBNF has no `case`.
- Avaloq form: `l_list := case when true list(l_doc.link_list) else list(l_doc_2.link_list) end; -- extra copy`
- Cite: paged/text/data-types.txt p.27 "Casting a list of field to a collection" ; paged/text/avaloq-script-expressions.txt pp.6-7 "Operators"
- Basis: STATED (example); INFERRED (doc error)
- From: G2-37, G2-17

### KB-LANG-52 Loops: numeric range, list field, collection `.values`/`.keys`, `while`
- Fact: The loop forms are `for i in 1 .. n loop ... end loop;`, `for p in <list field> loop`, `for v in <coll>.values loop` (or `.keys` for maps), `for id in lookup.code_list(...) loop` and `while <cond> loop ... end loop;`. The loop variable is implicitly declared. No `exit` or `continue` statement appears in the corpus.
- Avaloq form:
```
for i in 1 .. item_cnt loop
  l_item := item(i);
end loop;
for p in cont.pos_list loop ... end loop;
for val in l_text_set.values loop session.debug(val); end loop;
while x > 1 loop ... end loop;
```
- Cite: paged/text/coding-conventions.txt p.3 "Statements" ; paged/text/declarations-in-avaloq-script.txt pp.6-7 ; paged/text/data-types.txt pp.16, 22, 28-29 ; layout/04-test-framework/pages/02c_Implementing_the_construction_tests.txt pp.3-4
- Basis: STATED (the implicit loop variable is INFERRED)
- VERIFY: Q26 CONFIRMS (loop forms used in performance rules)
- Audit use: a `..` range token. The resolver adds the loop variable. An index loop `for i in 1 .. X.list.count` over `X.list(i)` is O(n²); iterate the list instead.
- From: G1-45, G1-75, G2-40, G5-80, G6-46

### KB-LANG-53 A list returned by a DDIC must be consumed immediately in a `for` loop
- Fact: Lists can be returned only by DDIC functions. A returned list must be used immediately in a `for` loop. To save, reference, edit or pass a list, cast it to a collection DDIC (`list(...)`/`set(...)`). The DB list tables LIST_CHAR, LIST_DATE and LIST_NUMBER cannot be used in script (the doc prints "LIST NUMBER").
- Cite: paged/text/hints-and-tips-on-using-avaloq-script.txt p.5 "List handling in Avaloq Script"
- Basis: STATED
- VERIFY: Q17 EXTENDS; Q08 EXTENDS
- From: G1-76, G6-42

### KB-LANG-54 `with <expr> as <alias> do ... end with;` (and `with new <ddic>(...)`)
- Fact: `with` defines an alias as a shortcut for a long designator or a DDIC instance, e.g. `with obj_bp(i_obj) as obj do`, `with doc_trans(t_id) as t do` or `with m.msg.asset as a do`. It improves performance for memory DDICs. `with new <ddic>(args) as <alias> do` calls the only constructor kind, `new`. This creates a real object or order (e.g. `with new mem_tab(...)`), not a scratch value. List-field `add` is done "using a with statement".
- Avaloq form:
```
with mem_doc_collect( b_id ) as collect do
  collect.add_postit( i_val_1, i_val_2 );
end with;
with new mem_tab(c_tab_name_obj) as obj_tab do
  ...
  obj_tab.remv;
end with;
```
- Cite: layout/02-techbase/02_05_Language_elements_used_in_Avaloq_Script.txt "Avaloq Script statements" ; paged/text/coding-conventions.txt p.3 ; paged/text/hints-and-tips-on-using-avaloq-script.txt pp.4-6 "Use with" ; paged/text/data-types.txt pp.4-5, 41 ; paged/text/what-are-data-dictionaries.txt p.7
- Basis: STATED (calling `<ddic>(<id>)` a "cast" here is INFERRED; see KB-LANG-75)
- VERIFY: Q08 EXTENDS; Q26 CONFIRMS
- Audit use: the alias takes the expression's DDIC type. Every `with new` is a creation site.
- From: G1-46, G1-74, G2-27, G2-54, G6-47, G6-49

### KB-LANG-55 `return` and `return null;`
- Fact: `return <expr>;` exits a function with a result. `return null;` is legal, including for object-returning functions, and early returns inside loops are used.
- Avaloq form: `if i_intl_id is null then return null; end if;`
- Cite: paged/text/declarations-in-avaloq-script.txt p.6 ; paged/text/hints-and-tips-on-using-avaloq-script.txt p.9
- Basis: STATED
- From: G1-48

### KB-LANG-56 `require(<condition>, <message>)` precondition
- Fact: `require(cond, msg)` is used for parameter validation, unqualified, with the condition first. The IT test package's `it.require('<text>', <condition>)` has the reverse order and stops the current procedure on failure, while `it.assert` continues. The package an unqualified `require` resolves to is not stated.
- Avaloq form: `require(x is not null and x > 0, 'x must be a positive number');`
- Cite: paged/text/declarations-in-avaloq-script.txt p.7 ; layout/04-test-framework/pages/02c_Implementing_the_construction_tests.txt p.3 ; layout/04-test-framework/pages/02b_Test_sources.txt p.2 "IT script package"
- Basis: STATED (usage); INFERRED (that `require` and `it.require` are different routines)
- VERIFY: Q11 EXTENDS; Q10 PARTIAL
- Audit use: do not hard-code a `require` argument order across packages.
- From: G1-88, G5-68, G5-102

### KB-LANG-57 Exception section `exception when others then ...` before `end <name>`
- Fact: Methods may end with a PL/SQL-style exception section before `end <name>;`, even though the method EBNF omits it. The ATF calls this "the standard pattern defined in the PL/SQL coding conventions". Only `when others` appears in the corpus. One official testability example swallows errors with `when others then return null;`, which is not to be cited as compliant style.
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
- Cite: paged/text/hints-and-tips-on-using-avaloq-script.txt p.8 "Use of db_side_effect_free" ; paged/text/data-types.txt p.42 "How to persist a SET or LIST DDIC collection" ; layout/04-test-framework/pages/02a_Creating_a_simple_test.txt p.1 "Create the test" ; layout/04-test-framework/pages/02c_Implementing_the_construction_tests.txt pp.4-5
- Basis: STATED
- VERIFY: Q11 CONFIRMS/EXTENDS; Q06 CONTRADICTS (EBNF completeness)
- Audit use: grammar `begin Stmts [exception Handlers] end ident`. Flag `when others then null` and `return null` swallowing.
- From: G1-81, G2-56, G5-62, G5-82, G6-50

### KB-LANG-58 `err.raise_fa('<pkg.method>' [, '<param>', <value>]...)` is the re-raise idiom
- Fact: The standard handler calls `err.raise_fa` with the qualified method name and optionally name/value pairs of parameters (`err.raise_fa('mba$dwh.put_line','i_text',i_text)`). A one-argument form also exists (`err.raise_fa('persist_list')`). ERR "defines error messages in a consistent way". Test packages use `it.catch('<proc>')`. What "fa" means and the rest of the ERR API are undocumented.
- Cite: paged/text/hints-and-tips-on-using-avaloq-script.txt p.8 ; paged/text/data-types.txt p.42 ; paged/text/what-are-avaloq-script-packages.txt p.2 ; layout/04-test-framework/pages/02a_Creating_a_simple_test.txt p.1
- Basis: STATED (forms); INFERRED (that the first argument should equal the enclosing method)
- VERIFY: Q11 PARTIAL; Q10 PARTIAL
- Audit use: check that the first argument matches `<package>.<method>`.
- From: G1-81, G2-56, G2-59, G5-62, G6-74

### KB-LANG-59 Transaction control: SESSION commit and rollback exist and are dangerous
- Fact: The SESSION DDIC has commit and rollback methods. The docs warn: "Be very careful when using the commit and rollback methods, especially during message processing", because atomicity can break (for example, multiple orders for one message). The exact member names are unverified.
- Cite: paged/text/what-are-data-dictionaries.txt p.8
- Basis: STATED
- VERIFY: Q11 EXTENDS; Q30 EXTENDS
- Audit use: warn on SESSION commit or rollback calls, especially in message-processing code.
- From: G6-68

---

## A5 Expressions

### KB-LANG-60 Expression elements
- Fact: An expression consists of literals, function calls (e.g. `abs(mem_doc_pay.amount)`), arithmetic and logical expressions, and data-access expressions. Expressions also appear outside script packages: in rule-loader COND/STMT columns (when RULE_KIND = expr), in CODE TAB sources and in INTF DEF responsive-form labels.
- Cite: paged/text/avaloq-script-expressions.txt p.1 "Avaloq Script expressions" ; paged/text/what-are-avaloq-script-expressions.txt p.1 "Introduction", "Structure of Avaloq Script expressions"
- Basis: STATED
- VERIFY: Q06 PARTIAL; Q19 EXTENDS; Q05 EXTENDS
- Audit use: the expression parser must work standalone on COND/STMT values.
- From: G2-01, G2-02

### KB-LANG-61 Arithmetic operators `+ - * / mod`; unary `+`/`-`
- Fact: `+`, `-`, `*`, `/` and `mod` work on numbers. As unary operators, `-` inverts the sign and `+` is identity. `mod` is listed as an infix operator (`i mod 3` in the examples), and code also calls it as a function (`mod(i, 10)`). The special function `div` returns null on division by zero.
- Cite: paged/text/language-fundamentals.txt pp.2-3 "Arithmetic operators" ; paged/text/avaloq-script-expressions.txt p.1 ; paged/text/hints-and-tips-on-using-avaloq-script.txt p.1 ; layout/02-techbase/02_05_Language_elements_used_in_Avaloq_Script.txt "Predefined functions"
- Basis: STATED
- Audit use: accept both `a mod b` and `mod(a, b)`.
- From: G1-15, G1-16, G1-87, G2-18, G6-53

### KB-LANG-62 Comparison operators, including `in`, `is [not] null`, `between`, `[not] like`
- Fact: The comparisons are `=`, `!=` or `<>`, `<`, `>`, `<=`, `>=`, `in (a, b, c)` (set membership), `is [not] null`, `between a and b` (inclusive at both ends) and `[not] like`. The result is described both as "always true, false, or null" and as "a boolean result". In `x in (...)`, x can be any type and the list values must match its type. `not in` and `not between` are absent from the EBNF (only `not like` is listed).
- Avaloq form: `x in (a, b, c)` ; `obj_bp(l_bp_id).name like '%meier%'`
- Cite: paged/text/language-fundamentals.txt p.3 "Comparison operators" ; paged/text/avaloq-script-expressions.txt pp.1, 6-7
- Basis: STATED
- VERIFY: Q06 CONFIRMS
- Audit use: flag `= null` / `!= null` (always null) and suggest `is [not] null`.
- From: G1-17, G1-A-ADD-01, G2-66, G6-09

### KB-LANG-63 CONFLICT: which operand types allow which comparisons
- Fact: CONFLICT. Language fundamentals says `=, !=, <>, <, <=, >, >=` apply to numbers, strings and dates, and only `=, !=, <>` "also apply to boolean, id types and record types". The Expressions compatibility table (garbled operator cells "<= >", ">= >") shows only `= != <>` for number and an ordering row for boolean. Language fundamentals is taken as authoritative. Separately, CF-18 record types (`type ... is record`) cannot be compared at all (KB-LANG-27).
- Cite: paged/text/language-fundamentals.txt p.3 "Comparison operators" ; paged/text/avaloq-script-expressions.txt p.8 "Table: Expression compatibility" ; paged/text/data-types.txt p.38 "Limitations"
- Basis: STATED (both); INFERRED (choice of authority; the cells read as truncated)
- VERIFY: Q06 EXTENDS
- Audit use: type checker. Ordering comparison on boolean, id or record is an error, and on number it is valid.
- From: G1-18, G2-20, G2-66

### KB-LANG-64 Logical operators `and`, `or`, `not`
- Fact: `and` is defined as "if not p then false, else q" and `or` as "if p then true, else q". `not` negates. They take boolean operands and give a boolean, with null handling "per PL/SQL documentation". Whether evaluation short-circuits is not stated; the conditional wording only suggests it.
- Cite: paged/text/language-fundamentals.txt p.3 "Logical operators"
- Basis: STATED (definitions); INFERRED (short-circuit)
- From: G1-20, G2-66

### KB-LANG-65 String concatenation `||`
- Fact: `||` concatenates two strings (`'hel' || 'lo'` gives `'hello'`). It is an exception to null propagation (KB-LANG-70). In the EBNF it sits at addition level.
- Cite: paged/text/language-fundamentals.txt p.4 "String operator"
- Basis: STATED
- From: G1-21

### KB-LANG-66 Published expression EBNF (verbatim; do not encode literally)
- Fact: The language reference publishes the grammar below (checked on the PDF image). As written, it is internally inconsistent: `and` is at Term level, so `a = 1 and b = 2` and `i between 1 and 100` do not parse. The unary alternative takes a whole `Expression`, so `not p or q` would read `not (p or q)`. `Designator`, `number` and `string` are undefined, and `case` expressions are absent. At most one comparison is allowed per Expression (non-associative).
- Avaloq form:
```
Expression = SimpleExpression [
    ( = | != | <> | < | > |<= |
    >= ) SimpleExpression
    | is [ not ] null
    | [ not ] like
    SimpleExpression
    | between SimpleExpression
    and SimpleExpression
    | in ( ExpressionList )
    )
  ] .
SimpleExpression =       Term { ( + | - | || | or ) Term } .
ExpressionList   =       Expression { , Expression } .
Term             =       Factor { ( * | / | mod | and ) Factor } .
Factor           =       null | true | false | number | string |
                 Designator |
                             ( + | - | not ) Expression | ( Expression ) .
```
- Cite: paged/text/avaloq-script-expressions.txt pp.6-7 "Operators"
- Basis: STATED (productions); INFERRED (inconsistency analysis)
- VERIFY: Q06 CONFIRMS (an EBNF exists) / PARTIAL (accuracy)
- From: G2-17

### KB-LANG-67 Prose precedence classes and associativity
- Fact: The prose names four precedence classes, highest first: unary `not`, `+`, `-`; multiplication operators; addition operators; comparison operators. Operators of equal precedence associate left to right (`x-y-z = (x-y)-z`). The prose does not place `and`, `or` or `||`.
- Avaloq form: "The unary operators not, +, and – have the highest precedence, followed by multiplication operators, addition operators, and comparison operators. Operators of the same precedence associate from left to right."
- Cite: paged/text/avaloq-script-expressions.txt p.6 "Operators"
- Basis: STATED
- VERIFY: Q06 CONFIRMS (classes)
- From: G2-16

### KB-LANG-68 CONFLICT: precedence of `and`/`or` vs comparisons, and the recommended parser precedence
- Fact: CONFLICT. Read literally, the EBNF (KB-LANG-66) places `and` at multiplication level and `or`/`||` at addition level, both binding tighter than comparisons. Official examples, however, combine comparisons with `and`/`or` without parentheses, and they are valid only under PL/SQL-style precedence: `x is not null and x > 0` (Declarations p.7), `a.issue_date.val_date = sysdate or a.pay_up_date.val_date = sysdate` (Hints p.4), `i between 1 and 100` and `not p or q` typed boolean (Expressions p.1). Recommended parser precedence, highest to lowest: unary `+`/`-`; `*` `/` `mod`; `+` `-` `||`; comparison / `is [not] null` / `[not] like` / `between..and` / `in`; `not`; `and`; `or`. After `between X`, the `and` is the between separator. How `not a = b` and `-x * y` are meant still needs a corpus check.
- Cite: paged/text/avaloq-script-expressions.txt pp.1, 6-7 ; paged/text/declarations-in-avaloq-script.txt p.7 ; paged/text/hints-and-tips-on-using-avaloq-script.txt p.4 "Use with"
- Basis: STATED (examples and EBNF); INFERRED (that the examples reflect the real precedence)
- VERIFY: Q06 PARTIAL — the EBNF is contradicted by official examples.
- Audit use: encode the PL/SQL-style table, never the literal EBNF levels for and/or/between/unary.
- From: G2-16, G2-17, G2-65

### KB-LANG-69 Golden example expressions with result types
- Fact: The reference lists these expressions and types. All nine must parse. The parentheses in `(1 <= i) and (i <= 100)` are stylistic and are not evidence for Pascal-style precedence.
- Avaloq form:
```
2002                                  -- number
i mod 3                               -- number
not p or q                            -- boolean
(i + j) * (i – j)                     -- number
i + x                                 -- number
(1 <= i) and (i <= 100)               -- boolean
i between 1 and 100                   -- boolean
l_bp_id is not null                   -- boolean
obj_bp(l_bp_id).name like '%meier%'   -- boolean
```
- Cite: paged/text/avaloq-script-expressions.txt p.1 (table)
- Basis: STATED
- VERIFY: Q06 EXTENDS
- Audit use: parser test inputs. Note `–` (en dash) in the source text.
- From: G2-18

### KB-LANG-70 Null semantics
- Fact: Any operator with a null operand yields null, with three exceptions: `||`, explicit null tests (`is null` / `is not null`), and `and`/`or`. How `||` treats null exactly is not stated (PL/SQL treats null as empty).
- Avaloq form: "Basically, any operator involving null-valued operands yields a null result, with a few exceptions"
- Cite: paged/text/avaloq-script-expressions.txt p.6 "Null values" ; paged/text/language-fundamentals.txt p.3
- Basis: STATED (the behaviour of `||` with null is INFERRED)
- VERIFY: Q06 EXTENDS; Q27 EXTENDS
- Audit use: flag `= null`, and arithmetic on possibly-null fields or uninitialised accumulators.
- From: G2-15, G1-28, G6-24

### KB-LANG-71 Data-access expressions: a dot path from a DDIC root through fields
- Fact: Data-access expressions read data in memory or in the database through DDICs. The elements are separated by dots. The root names a DDIC (or a variable, a parameter, a function returning a DDIC, or a cast), and each hop is a field of the DDIC reached so far. Record fields lead to the next DDIC, for example `obj_pos.cont.bp.name` (walking up position, container, BP). Paths can include parameterised attributes (`class('ass_type')`, `class_id('ass_type')`), indexed lists (`doc.trans_list(i)`, `.count`) and method calls on DDIC instances. Which roots are available depends on the execution context (e.g. `mem_doc` = an order loaded in memory).
- Avaloq form: `obj_pos.cont.bp.name` ; `mem_doc.order_type_id` ; `pos.asset.class_id('ass_type')`
- Cite: paged/text/what-are-avaloq-script-expressions.txt pp.2-3 "Data access expressions" ; paged/text/avaloq-script-expressions.txt pp.1-2, 4 ; paged/text/language-fundamentals.txt p.2 ; paged/text/hints-and-tips-on-using-avaloq-script.txt pp.3-6
- Basis: STATED
- VERIFY: Q08 CONFIRMS
- Audit use: designator grammar `root ('.' field ['(' args ')'])*`. Resolve each hop against the DDIC index.
- From: G2-03, G2-04, G2-05, G2-12, G1-89, G6-56

### KB-LANG-72 Data-access expressions must end in a scalar
- Fact: A data-access expression must result in a scalar (a base type or an ID type). Using a non-scalar as an expression "may yield a null result instead of the expected data".
- Cite: paged/text/avaloq-script-expressions.txt p.3 (Note)
- Basis: STATED
- VERIFY: Q27 EXTENDS (silent pitfall)
- Audit use: warn on a path ending in a record-typed field when it is used as a value.
- From: G2-08, G6-57

### KB-LANG-73 Code-table entries as expressions: `code_<table>.<entry>_id`
- Fact: Every code table has a same-named DDIC whose fields are its entries. `code_medium.phone_id` is the entry's ID and `code_medium.phone.name` is a field of that entry. Generated constant DDICs (`mdb_asset.fwd_fx`, `mdb_meta_typ.stex`, `meta_typ.bp_id`) appear in comparisons and case labels. Row access by intl_id is `code_x.lookup(intl_id).col`.
- Cite: paged/text/avaloq-script-expressions.txt pp.2-3 ; paged/text/hints-and-tips-on-using-avaloq-script.txt pp.3, 9 ; layout/04-test-framework/pages/02c_Implementing_the_construction_tests.txt pp.3-4
- Basis: STATED
- VERIFY: Q09 CONFIRMS
- From: G2-07, G1-73, G1-88, G5-80

### KB-LANG-74 References and package qualification
- Fact: Variables, constants, parameters and functions are referred to by name, qualified with the package name when referenced from outside that package (`it_char_set_util.c_iana_ascii`, `url_builder.url#simple_esc(l_url_part)`). Referring to a function calls it.
- Cite: paged/text/avaloq-script-expressions.txt pp.3-4 "References and function calls"
- Basis: STATED
- VERIFY: Q02 PARTIAL
- Audit use: `x.y` with x an imported package is a cross-package reference. Otherwise it is DDIC navigation.
- From: G2-11, G1-86

### KB-LANG-75 DDIC type cast `T(v)`: the compiler does not check it
- Fact: `T(v)` reads v as (an ID of) a DDIC of type T so its fields and methods can be accessed. It is valid if v is scalar, or if v is a DDIC value and T extends v's static type. "In the current implementation, neither of these constraints is checked by the compiler (which is a possible source of errors)." The official examples cast an `id obj_bp`, an `obj` and even a `number`.
- Avaloq form:
```
obj_bp(l_bp_id).ref_curry.name   -- l_bp_id of type id obj_bp
obj_bp(l_obj).ref_curry.name     -- l_obj of type obj
obj_bp(l_val).ref_curry.name     -- l_val of type number
```
- Means: `ident(expr)` where ident is a DDIC name is a cast plus a record load, not a function call.
- Cite: paged/text/avaloq-script-expressions.txt pp.4-5 "DDIC type casts"
- Basis: STATED (that cast-then-field loads the record is INFERRED)
- VERIFY: Q08 CONFIRMS; Q27 EXTENDS
- Audit use: flag casts from a different DDIC or ID root, and casts of plain number or text variables.
- From: G2-13, G6-31

### KB-LANG-76 Collection cast `list(<list-of field>)` / `set(...)` copies
- Fact: The cast also works for collection DDICs: v must be a "list of" field and T must be list or set, with an element type legal for T (a list of date cannot become a set). The cast copies values into a new collection, so changing it does not change the field. Casting to a set removes duplicates, and casts can be chained.
- Avaloq form: `l_cnt_unique := set(l_doc.link_list).count; -- operations on collection casts can be chained`
- Cite: paged/text/avaloq-script-expressions.txt pp.5-6 ; paged/text/data-types.txt pp.26-27 "Casting a list of field to a collection"
- Basis: STATED
- VERIFY: Q08 EXTENDS; Q26 EXTENDS
- From: G2-14, G2-37, G6-42

### KB-LANG-77 Generic static calls: `set.union<T>(a, b)`, `list.empty<T>`
- Fact: Set algebra is static and generic and returns a new set: `set.intersect<T>`, `set.union<T>`, `set.subtract<T>`, `set.sym_diff<T>`. `list.empty<T>`, `set.empty<T>` and `map.empty<L,T>` are static too. A secondary claim of instance methods (`l_set.union(...)`) is contradicted.
- Avaloq form: `l_set_animals := set.union<text>(l_set_birds, l_set_mammals);` ; `l_list_obj_bp := list.empty<obj_bp>;`
- Cite: paged/text/data-types.txt pp.13-14, 19-21, 25
- Basis: STATED
- VERIFY: Q10 CONTRADICTS (instance-method claim)
- Audit use: grammar allows type arguments after a member name (`name '<' types '>' '(' args ')'`).
- From: G2-32, G2-33, G2-34, G6-40

### KB-LANG-78 CONFLICT: does the compiler check assignment compatibility?
- Fact: CONFLICT. Expressions p.7 says expressions must be assignment compatible with the target, but "The compatibility is currently not checked by the compiler." Data types p.42 says some violations (e.g. assigning a MEM_DOC variable to OBJ) give "a warning or even an error, depending on the configuration". CF-18 records and collections are type-checked at design time. These are probably different compiler generations. The rules: same type (same identifier, or ID types with the same root); type inclusion (`long` >= `text`); record or ID extension along the DDIC inheritance list; and null is assignable to anything except collections.
- Cite: paged/text/avaloq-script-expressions.txt pp.7-9 "Expression compatibility" ; paged/text/data-types.txt p.42 ; paged/text/data-types.txt pp.36-38
- Basis: STATED (both)
- VERIFY: Q27 EXTENDS / PARTIAL; Q15 EXTENDS
- Audit use: our checker reports incompatibility itself, whatever the compiler does.
- From: G2-19, G2-21, G2-55

### KB-LANG-79 Implicit conversion exists and is discouraged; id is not text
- Fact: Assigning a number to text works through implicit conversion. Conversions are slower than using the right types from the start (`l_text := 10;` is INEFFICIENT). "In general, id types are not type compatible with the text type." `to_char` is attested, but `to_date` and `to_number` are not.
- Cite: paged/text/hints-and-tips-on-using-avaloq-script.txt pp.2-3 "Avoid implicit data type conversions" ; paged/text/data-types.txt pp.42, 44
- Basis: STATED
- VERIFY: Q26 CONFIRMS
- From: G1-71, G6-33, G2-51

### KB-LANG-80 Collection assignment copies
- Fact: Collection assignment is allowed when type and type argument match, or when the type arguments share the same underlying DDIC id fragment (`list<obj_bp>` and `list<obj>`). All collection assignments have copy semantics (PL/SQL associative arrays), and avoiding them is recommended.
- Avaloq form: "All collection variable assignments have copy semantics. So assigning huge collections may have a negative performance impact."
- Cite: paged/text/data-types.txt p.26 "Assigning a collection" ; paged/text/data-types.txt pp.30-31 "Implementation restrictions"
- Basis: STATED
- VERIFY: Q26 EXTENDS
- From: G2-36, G2-43, G6-36

### KB-LANG-81 Typed `iff` variants
- Fact: `iff(cond, a, b)` is the inline conditional. `iffb` returns one of two integers (`iff` is 2-3x slower), `iffd` one of two dates (`iff` is 10x slower), and `iffn` is named but not described. A TOC title marks `iff` and `nvl` "deprecated" (page content absent).
- Avaloq form: `l_is_auto := iff(doc.asset_a = '+', '+', '-');`
- Cite: paged/text/hints-and-tips-on-using-avaloq-script.txt p.2 "Use typed iff (iffb, iffd, iffn)" ; paged/text/naming-conventions.txt p.4
- Basis: STATED (deprecation INFERRED from the TOC title)
- VERIFY: Q10 EXTENDS; Q26 CONFIRMS
- From: G1-70, G6-52

---

## A6 Interop with PL/SQL

### KB-LANG-82 Script is compiled to PL/SQL by area-specific compilers; no direct table access
- Fact: Avaloq Script is used only in Avaloq Core. It is similar to PL/SQL, but it has no direct access to Oracle table data and uses DDICs instead, so code survives changes to the storage location. Each usage area has its own compiler, which translates the script into PL/SQL installed on the database. SQL fragments still appear as condition strings (KB-LANG-90), and SQL proper lives in separate source types.
- Avaloq form: "It is similar to PL/SQL except it doesn't provide direct access to the data in Oracle database tables."
- Cite: paged/text/getting-started-with-avaloq-script.txt p.1 "Getting Started with Avaloq Script", "Note"
- Basis: STATED (per-area dialect differences are INFERRED)
- VERIFY: Q12 PARTIAL/EXTENDS; Q17 PARTIAL; Q01 PARTIAL
- Audit use: raw table names or SQL DML at statement level in a script package are findings.
- From: G1-01, G1-02, G1-03, G6-55

### KB-LANG-83 Compiler-generated SQL: one select per DDIC attribute when possibly-writing calls intervene
- Fact: The doc shows the PL/SQL the compiler generates. Reads of `obj.bu_id`, `obj.acc_type_id` and `obj.au_sa_bp_id` on `obj_bp(i_obj)` could be merged into one select. Interleaving them with `mba$dwh.put_line`, which "might modify the value", forces one `select <attr> from obj_bp where id=i_obj` per attribute, "three database round trips (select statements) where we only needed one". The tooling shows the ASMD info marker "Missed performance optimization opportunity" ("Feature call with potential side effect 'mba$dwh.put_line' prohibits reuse of table access via 'obj'."). There are two fixes: mark the callee `db_side_effect_free`, or extract the reads into locals first.
- Avaloq form: "select bu_id from obj_bp where id=i_obj Call put_line with the returned value select acc_type_id from obj_bp where id=i_obj"
- Means: DDIC `obj_bp` attributes map to same-named columns of table `obj_bp` keyed by `id`. That this holds generally is INFERRED.
- Cite: paged/text/hints-and-tips-on-using-avaloq-script.txt pp.5-7 "Optimizing accesses to the same database table"
- Basis: STATED (the translation shown); INFERRED (generality)
- VERIFY: Q12 EXTENDS; Q14 EXTENDS; Q26 CONFIRMS; Q27 CONFIRMS; Q28 PARTIAL
- From: G1-B-ADD-01, G1-78, G1-79, G1-80, G6-48

### KB-LANG-84 Calling PL/SQL: `import native` + `<package>#.<proc>(...)`
- Fact: Script collections and records can be passed directly to PL/SQL procedures imported natively into a script package, which are called as `custom_package#.proc(...)`. The doc also prints `custom_package#create_record(...)` without the dot. The `#.` form is INFERRED to be the normal one.
- Avaloq form:
```
procedure process_custom_list is
  l_custom_text_list list<text>;
begin
  custom_package#.fill_custom_list(l_custom_text_list);
  custom_package#.consume_custom_list(l_custom_text_list);
end process_custom_list;
```
- Cite: paged/text/data-types.txt pp.34-36 "Passing collections from Avaloq Script to PL/SQL procedures" ; paged/text/declarations-in-avaloq-script.txt p.5
- Basis: STATED
- VERIFY: Q12 CONFIRMS; Q05 EXTENDS
- Audit use: `<name>#.<proc>` is a call edge into PL/SQL.
- From: G2-46, G6-04, G6-44

### KB-LANG-85 PL/SQL side: IN OUT NOCOPY, no collection- or record-returning functions, never null
- Fact: PL/SQL must declare script collection and record parameters `IN OUT NOCOPY` (pass by reference, which avoids deep copies). The result of a PL/SQL function that returns a collection or record cannot be used directly in a script expression; that is a compilation error. PL/SQL must never set a script collection to null, and nothing checks for it. The doc's PL/SQL return type `t#r#it_templ_ddic@address.t_type` uses `@`, which does not match the T#R# pattern.
- Avaloq form:
```
procedure fill_custom_list (x_out_list in out nocopy t#list#varchar2_4000.t_type);
party_address := custom_package#create_record(1001, 'Avaloq Street');  -- compilation error
```
- Cite: paged/text/data-types.txt pp.34-36 "Passing collections from Avaloq Script to PL/SQL procedures", "Restrictions"
- Basis: STATED
- VERIFY: Q12 CONFIRMS
- Audit use: errors for `l_x := pkg#.func(...)` when func returns a T# type, for PL/SQL T# parameters lacking IN OUT NOCOPY, and for null assignments to `t#...t_type` variables.
- From: G2-46, G6-44

### KB-LANG-86 Generated T# type packages for collections
- Fact: Compiling a source that references collections generates PL/SQL type packages. Simple collections become `t#<coll>#<element-PL/SQL-type>`, nested ones `t#<coll>#<inner>_t_type`, maps `t#map#<key>#<value>` and sets `t#set#<element>`. Special characters become `_`, the type is `<package>.t_type`, and names of 60 or more characters are mangled.
- Avaloq form:
```
list<text>            t#list#varchar2_4000
list<number>          t#list#number
list<obj>             t#list#obj#_t_obj_id
list<list<text>>      t#list#t#list#varchar2_4000_t_type
map<text, number>     t#map#varchar2_4000#number_t_type.t_type
```
- Cite: paged/text/data-types.txt pp.32-34, 36 "PL/SQL type names for Avaloq Script collections"
- Basis: STATED
- VERIFY: Q12 EXTENDS; Q01 EXTENDS
- Audit use: `t#...` identifiers in PL/SQL are generated, so exclude them from "unknown package" reports.
- From: G2-45

### KB-LANG-87 Generated T#R# packages for record types
- Fact: A record `address` in script package `my_script` generates package `t#r#my_script#address`, with type `<package>.t_type`. Records pass to natively imported PL/SQL procedures as IN OUT NOCOPY parameters. The doc's pattern line drops a `#` (`t#r<...>`); the example form is correct.
- Avaloq form:
```
type address is record (
  street_address text,
  city text
);
procedure update_active_address (x_address in out nocopy t#r#my_script#address.t_type);
```
- Cite: paged/text/data-types.txt pp.34-35 "Avaloq Script compound (record) types", "PL/SQL type names for Avaloq Script compound(record) types"
- Basis: STATED
- VERIFY: Q12 EXTENDS
- From: G2-49

### KB-LANG-88 T# packages used in PL/SQL must be declared in a script package
- Fact: T# packages used within PL/SQL must be declared explicitly in a script package. Defining them in another source type can cause compilation and dependency problems. For an INTF DEF, the fix is a wrapper method in a script package that calls the native implementation, with forward-declared types removed through a MIGR source.
- Cite: paged/text/data-types.txt p.39 "T# Packages used in PL/SQL need to be defined in a Script Package"
- Basis: STATED
- VERIFY: Q05 EXTENDS; Q01 EXTENDS; Q25 EXTENDS
- From: G2-50

### KB-LANG-89 Script-to-PL/SQL type mapping
- Fact: `boolean` maps to varchar2(1) or boolean (variables) and boolean (parameters). `text` maps to varchar2(4000) or varchar2, `long` to varchar2(32000) or varchar2, `number` to number and `date` to date. For ID types: `mem_doc` maps to doc_mgr#.t_doc, `doc` to doc#.t_doc_id, `mem_msg` to msg_mgr#.t_msg, `msg` to msg#.t_msg_id, `obj` to obj#.t_obj_id and code_table_x to pls_integer. Since 5.7, `id table <code table>` maps to pls_integer and `id table msg`/`doc` to number(12). Other ids map to varchar2(2000), though some "might be translated to something more specific". Explicit lengths are not supported.
- Cite: paged/text/data-types.txt pp.43-44 "Mapping Avaloq Script data types to PL/SQL"
- Basis: STATED
- VERIFY: Q12 EXTENDS; Q06 EXTENDS
- From: G2-51

### KB-LANG-90 SQL appears only as condition strings inside script
- Fact: "Some keywords can be followed by a condition in SQL notation". Conditions are written as string arguments, e.g. `cond => 'meta_typ_id = ' || meta_typ.bp_id` in `lookup.code` and `'activ is not null'` in `lookup.code_list`. Tables in SQL are usually aliased with 2-character abbreviations. The keywords that take SQL conditions are not listed.
- Cite: paged/text/naming-conventions.txt pp.4-5 "Aliases" ; paged/text/hints-and-tips-on-using-avaloq-script.txt p.9 ; layout/04-test-framework/pages/02c_Implementing_the_construction_tests.txt pp.3-4
- Basis: STATED (that concatenated condition strings are an injection hotspot is INFERRED)
- VERIFY: Q12 PARTIAL; Q30 EXTENDS (INFERRED)
- Audit use: tag these strings as embedded SQL spans.
- From: G1-67, G1-82, G5-80, G6-55

### KB-LANG-91 Collections exist only in framework-compiled script
- Fact: Collection types are available only in Avaloq Script compiled through the compiler framework. As of ACP 5.6 that excludes script embedded in the REP PRINT source type and runtime-compiled Avaloq Script.
- Cite: paged/text/data-types.txt pp.30-31 "Implementation restrictions"
- Basis: STATED (which expression contexts are runtime-compiled is INFERRED)
- VERIFY: Q01 EXTENDS; Q27 EXTENDS
- Audit use: flag `list<>`/`set<>`/`map<>` in REP PRINT or runtime-compiled snippets.
- From: G2-43

### KB-LANG-92 CONFLICT: can maps (and sets/lists) go to PL/SQL directly?
- Fact: CONFLICT. The comparison table (Data types p.40) says set and list reach PL/SQL "Via db_list#", and map only "Via manual conversion to MEM_DB_LIST or MEM_TAB". The newer interop section (pp.32-36) says lists, maps, sets and records can be passed "directly to PL/SQL code without intermediate transformations" and documents `t#map#...` types. The comparison table probably predates native T# interop.
- Cite: paged/text/data-types.txt pp.39-40 "Comparison", "Overview comparison" ; paged/text/data-types.txt pp.32-36
- Basis: STATED (both); INFERRED (that the table is outdated)
- VERIFY: Q25 EXTENDS; Q26 EXTENDS
- Audit use: accept native T# handover. Confirm on the corpus by looking for `t#map#` in PL/SQL.
- From: G2-52
