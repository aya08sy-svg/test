# KB index: one line per entry (id | title | file). grep this first, then open the file at the id.


## A_language.md — What a model must know first

## A_language.md — A1 Lexical
KB-LANG-01 | Character set is ASCII letters, digits and a fixed symbol set
KB-LANG-02 | Whitespace is free-format but must not split a symbol
KB-LANG-03 | Case: "uppercase and lowercase letters are distinct", yet all code must be lowercase
KB-LANG-04 | Lexical units
KB-LANG-05 | Identifier rule (published EBNF)
KB-LANG-06 | CONFLICT: identifiers in official code contain `#` and `$`
KB-LANG-07 | Numbers: unsigned integer or real, both of type `number`
KB-LANG-08 | Strings: single OR double quotes, escaped by doubling
KB-LANG-09 | Keyword segments in a data-access path are quoted
KB-LANG-10 | Literal values
KB-LANG-11 | Boolean data is the single character `'+'` (true) / `'-'` (false)
KB-LANG-12 | Delimiter table (with its ambiguities)
KB-LANG-13 | Comments: `/* ... */` and `--`, not nestable, but directive comments carry meaning
KB-LANG-14 | Reserved words: identifiers by definition, but no list is published

## A_language.md — A2 Source and package structure
KB-LANG-15 | A script package is one compilable unit (no spec/body split)
KB-LANG-16 | `[script 1.0]` header line (pre-compiler statement, column 1)
KB-LANG-17 | Package parts and order
KB-LANG-18 | `import` / `import native`, one per line, usable inside methods too
KB-LANG-19 | `end <name>;` repeats the method or package name
KB-LANG-20 | Published method-declaration EBNF (verbatim, with its defects)
KB-LANG-21 | Nested methods, local items, recursion, visibility of outer items
KB-LANG-22 | Visibility and inheritance modifiers exist, but their semantics are undocumented
KB-LANG-23 | `deterministic` (functions only): an unchecked compiler hint for install-time evaluation
KB-LANG-24 | `db_side_effect_free` (procedures and functions, top-level and local)
KB-LANG-25 | `deterministic` and `db_side_effect_free` are alternatives on a function
KB-LANG-26 | `/*postp_start*/ ... /*postp_end*/` marks one expression as deterministic
KB-LANG-27 | Record types (Compiler Framework 18.0): package level only
KB-LANG-28 | Anonymous block `declare ... begin ... end;`

## A_language.md — A3 Declarations and parameters
KB-LANG-29 | Every identifier must be declared; scope is textual from the declaration point
KB-LANG-30 | Variable declaration: `ident Type [:= Expression]` (no colon, no `:=` required)
KB-LANG-31 | Defaults are evaluated at runtime on scope entry; otherwise the value is null
KB-LANG-32 | Constants: `ident constant Type := Expression`, with a value that may be computed at runtime
KB-LANG-33 | Type forms in declarations: base, id, object/DDIC; no lengths, no `raw`, `long` is not CLOB
KB-LANG-34 | Generic collection types `list<V>`, `set<V>`, `map<K,V>` are auto-initialised
KB-LANG-35 | Function vs procedure: a function has a result type and must `return`
KB-LANG-36 | Formal-parameter EBNF
KB-LANG-37 | Parameterless methods: no `()` in examples, `function name()` in conventions, neither derivable from the EBNF
KB-LANG-38 | Only value parameters exist: no `in` / `out` / `in out`
KB-LANG-39 | CONFLICT: are value parameters reassignable?
KB-LANG-40 | Actual parameters must be assignment compatible
KB-LANG-41 | Parameter defaults `ident Type := expr` (beyond the EBNF)
KB-LANG-42 | A collection parameter may default only to `default`
KB-LANG-43 | Named arguments `name => expr`
KB-LANG-44 | Collections are passed BY REFERENCE (compiled to `in out nocopy`)
KB-LANG-45 | Exceptions can be named by identifiers, but no exception declaration is specified

## A_language.md — A4 Statements
KB-LANG-46 | Assignment uses `:=`
KB-LANG-47 | `if ... then ... elsif ... else ... end if;`
KB-LANG-48 | Bare procedure calls and parameterless calls without parentheses
KB-LANG-49 | `null;` statement
KB-LANG-50 | `case` statement: `else` is required, or ORA-06592 at runtime
KB-LANG-51 | `case` expression form is attested only by a defective example
KB-LANG-52 | Loops: numeric range, list field, collection `.values`/`.keys`, `while`
KB-LANG-53 | A list returned by a DDIC must be consumed immediately in a `for` loop
KB-LANG-54 | `with <expr> as <alias> do ... end with;` (and `with new <ddic>(...)`)
KB-LANG-55 | `return` and `return null;`
KB-LANG-56 | `require(<condition>, <message>)` precondition
KB-LANG-57 | Exception section `exception when others then ...` before `end <name>`
KB-LANG-58 | `err.raise_fa('<pkg.method>' [, '<param>', <value>]...)` is the re-raise idiom
KB-LANG-59 | Transaction control: SESSION commit and rollback exist and are dangerous

## A_language.md — A5 Expressions
KB-LANG-60 | Expression elements
KB-LANG-61 | Arithmetic operators `+ - * / mod`; unary `+`/`-`
KB-LANG-62 | Comparison operators, including `in`, `is [not] null`, `between`, `[not] like`
KB-LANG-63 | CONFLICT: which operand types allow which comparisons
KB-LANG-64 | Logical operators `and`, `or`, `not`
KB-LANG-65 | String concatenation `||`
KB-LANG-66 | Published expression EBNF (verbatim; do not encode literally)
KB-LANG-67 | Prose precedence classes and associativity
KB-LANG-68 | CONFLICT: precedence of `and`/`or` vs comparisons, and the recommended parser precedence
KB-LANG-69 | Golden example expressions with result types
KB-LANG-70 | Null semantics
KB-LANG-71 | Data-access expressions: a dot path from a DDIC root through fields
KB-LANG-72 | Data-access expressions must end in a scalar
KB-LANG-73 | Code-table entries as expressions: `code_<table>.<entry>_id`
KB-LANG-74 | References and package qualification
KB-LANG-75 | DDIC type cast `T(v)`: the compiler does not check it
KB-LANG-76 | Collection cast `list(<list-of field>)` / `set(...)` copies
KB-LANG-77 | Generic static calls: `set.union<T>(a, b)`, `list.empty<T>`
KB-LANG-78 | CONFLICT: does the compiler check assignment compatibility?
KB-LANG-79 | Implicit conversion exists and is discouraged; id is not text
KB-LANG-80 | Collection assignment copies
KB-LANG-81 | Typed `iff` variants

## A_language.md — A6 Interop with PL/SQL
KB-LANG-82 | Script is compiled to PL/SQL by area-specific compilers; no direct table access
KB-LANG-83 | Compiler-generated SQL: one select per DDIC attribute when possibly-writing calls intervene
KB-LANG-84 | Calling PL/SQL: `import native` + `<package>#.<proc>(...)`
KB-LANG-85 | PL/SQL side: IN OUT NOCOPY, no collection- or record-returning functions, never null
KB-LANG-86 | Generated T# type packages for collections
KB-LANG-87 | Generated T#R# packages for record types
KB-LANG-88 | T# packages used in PL/SQL must be declared in a script package
KB-LANG-89 | Script-to-PL/SQL type mapping
KB-LANG-90 | SQL appears only as condition strings inside script
KB-LANG-91 | Collections exist only in framework-compiled script
KB-LANG-92 | CONFLICT: can maps (and sets/lists) go to PL/SQL directly?

## B_types.md — What a model must know first

## B_types.md — B1 Base types
KB-TYPE-01 | The five base types; no `raw`
KB-TYPE-02 | boolean is one character '+' / '-'; literals true and false
KB-TYPE-03 | text: extended ASCII, max 4000 characters
KB-TYPE-04 | long: max 32,000 characters = varchar2(32000), not CLOB
KB-TYPE-05 | number: one numeric type, range 1E-84..1E127, 38 digits
KB-TYPE-06 | date: date and time, upper bound 31.12.4712 AD
KB-TYPE-07 | No length/precision specifiers; script-to-PL/SQL type mapping
KB-TYPE-08 | Type rules apply to every designator; uninitialised = null

## B_types.md — B2 ID types vs record (DDIC) types
KB-TYPE-09 | ID types hold only the primary key; "lighter and quicker"
KB-TYPE-10 | DDIC (record / object) types point to the whole record
KB-TYPE-11 | Data access expressions must end in a scalar
KB-TYPE-12 | DDIC field types, list fields and field operations

## B_types.md — B3 Type compatibility, casts, conversions
KB-TYPE-13 | Is type compatibility checked by the compiler? CONFLICT
KB-TYPE-14 | Same type, type inclusion, type extension
KB-TYPE-15 | Assignment compatibility rules
KB-TYPE-16 | Operand types per operator — CONFLICT on ordering comparisons
KB-TYPE-17 | DDIC type cast T(v) — not checked by the compiler
KB-TYPE-18 | Collection cast of a "list of" field: list(...) / set(...)
KB-TYPE-19 | Implicit conversion exists, is slower; id is not text

## B_types.md — B4 Collections
KB-TYPE-20 | No user-defined lists; collection DDICs provide them
KB-TYPE-21 | List fields: operations
KB-TYPE-22 | Lists returned by DDIC functions must be used at once or cast
KB-TYPE-23 | MEM_DB_LIST_CHAR — complete API
KB-TYPE-24 | MEM_DB_LIST_NR — complete API
KB-TYPE-25 | MEM_DB_LIST_DATE — "similar", API not documented
KB-TYPE-26 | MEM_TAB — known members only from one example
KB-TYPE-27 | Templated collections list<V>, set<V>, map<K,V> (since 5.3)
KB-TYPE-28 | Collection availability: compiler framework only
KB-TYPE-29 | Set element / map key types: number, text, DDIC/id only
KB-TYPE-30 | list<V> — complete method table (14 methods)
KB-TYPE-31 | list.remv positional argument binds to val, not pos
KB-TYPE-32 | set<V> — complete method table (11 instance + 5 static)
KB-TYPE-33 | Static set operations: set.<op><T>(a, b)
KB-TYPE-34 | map<K,V> — complete method table (11 methods)
KB-TYPE-35 | Declaring collections: auto-initialised; parameter default only `:= default`
KB-TYPE-36 | Null rules for collections
KB-TYPE-37 | Collection exceptions (code_ap_err.*)
KB-TYPE-38 | Collection compiler error messages
KB-TYPE-39 | Collection assignment type rules
KB-TYPE-40 | Iteration: for v in coll.values / map.keys
KB-TYPE-41 | Persistence: store/load, pre-allocated id
KB-TYPE-42 | Choosing a mechanism: collection DDICs vs MEM_DB_LIST vs MEM_TAB — CONFLICT on PL/SQL handover
KB-TYPE-43 | Generated PL/SQL T# type packages for collections
KB-TYPE-44 | Passing collections/records to PL/SQL

## B_types.md — B5 Records (Compiler Framework 18.0)
KB-TYPE-45 | Record type definition: package level, optional private
KB-TYPE-46 | Record variables: same-type assignment only; no null check, no comparison — CONFLICT
KB-TYPE-47 | Record <-> PL/SQL: T#R# packages

## B_types.md — B6 Collection performance facts
KB-TYPE-48 | Collection assignment copies (deep copy)
KB-TYPE-49 | Casting a list-of field copies; extra copy in some contexts
KB-TYPE-50 | Collection parameters are passed by reference — CONFLICT with "value parameters only"
KB-TYPE-51 | Returning collections; compiler copy avoidance
KB-TYPE-52 | list.remv is O(n)
KB-TYPE-53 | Limit bad use of .store (each call writes to the DB)
KB-TYPE-54 | Manual memory release for MEM_TAB / MEM_DB_LIST
KB-TYPE-55 | Loop over list fields with `for x in list`, not indexed get
KB-TYPE-56 | ID instead of record: the documented lightweight reference

## B_types.md — B7 Documentation errors not to copy
KB-TYPE-57 | Errata in the official type/collection docs
KB-TYPE-58 | Wrong type claims in secondary notes (metaprompt)

## C_data.md — What a model must know first

## C_data.md — C1 Data dictionaries (DDIC)
KB-DATA-01 | A DDIC is the only way script reaches data; tables are hidden
KB-DATA-02 | DDICs reach three layers plus session data
KB-DATA-03 | DDIC naming prefixes (prefix -> data kind)
KB-DATA-04 | One OBJ DDIC per object type; three DDICs per object type
KB-DATA-05 | Order DDICs exist per business type and per layer
KB-DATA-06 | Other important DDIC families
KB-DATA-07 | A DDIC = fields + methods + optional constructor
KB-DATA-08 | Navigator sections, inheritance and the legacy term "business object type"
KB-DATA-09 | Field List columns; fields can take parameters
KB-DATA-10 | DDIC field base types
KB-DATA-11 | ID types vs record (DDIC) types
KB-DATA-12 | Operations column: get / set / count / list / do / add
KB-DATA-13 | Rule-calculated fields have a companion `_a` flag
KB-DATA-14 | Obsolete DDIC fields: compiler warning now, de-release later
KB-DATA-15 | DDIC methods are procedures (DOC_PAY example)
KB-DATA-16 | Constructor `new` exists only in MEM DOC DDICs
KB-DATA-17 | DDIC IDs in the Navigator; task 923 shows a DDIC
KB-DATA-18 | Runtime DDICs vs constant DDICs
KB-DATA-19 | Object extensions have their own DDICs; `extn` record

## C_data.md — C2 Data access layers
KB-DATA-20 | Three layers: MEM DOC, DOC, OBJ
KB-DATA-21 | MEM DOC holds unsaved order changes
KB-DATA-22 | DOC is effectively read-only (exception: post-it)
KB-DATA-23 | OBJ is effectively read-only; objects are modified via an order
KB-DATA-24 | Which layer a DDIC view shows; read during an open order
KB-DATA-25 | Write lock while a modify order is open

## C_data.md — C3 Accessor syntax
KB-DATA-26 | Data access expression = dot path from a DDIC root
KB-DATA-27 | DDIC type cast `T(v)`, e.g. `obj_bp(id)` — not checked by the compiler
KB-DATA-28 | A function returning a DDIC can be the root
KB-DATA-29 | Root availability depends on context; `mem_doc` = order in memory
KB-DATA-30 | Paths must end in a scalar
KB-DATA-31 | Keyword segments in a path are quoted
KB-DATA-32 | Parameterised fields: `class('x')`, `class_id('x')`
KB-DATA-33 | List fields: operations, restrictions, collection casts
KB-DATA-34 | Loop over list fields with `for x in list`, not indexed `get`
KB-DATA-35 | `with <expr> as <alias> do ... end with;`
KB-DATA-36 | Code values: `code_x.<entry>_id`, `mdb_*`, `meta_typ.*`
KB-DATA-37 | SESSION: always-present singleton DDIC
KB-DATA-38 | LOOKUP: object search, code lookup, date arithmetic

## C_data.md — C4 How data is READ
KB-DATA-39 | Read effects by construct
KB-DATA-40 | Compiler translates attribute reads into selects on the backing table
KB-DATA-41 | Reads of one row are merged unless a possibly-writing call sits between them
KB-DATA-42 | Hoist loop-invariant reads and calls
KB-DATA-43 | Documented caching: deterministic functions and package state
KB-DATA-44 | Keys are not unique; names are historicized

## C_data.md — C5 How data is CREATED and MODIFIED
KB-DATA-45 | Every data change uses an order whose lifecycle a workflow controls
KB-DATA-46 | `new` on a MEM_DOC DDIC opens an order (syntax `with new ...`)
KB-DATA-47 | MEM_DOC_BP.new parameters; `no_commit` defaults to `'+'`
KB-DATA-48 | Object creation lifecycle: CREATE happens at finalisation
KB-DATA-49 | Static data orders: only Create and Modify
KB-DATA-50 | `set` on fields: MODIFY of the DDIC's entity
KB-DATA-51 | Post-it writes: `attach_postit`, `add_postit`, `postit_list.add`
KB-DATA-52 | No DELETE of objects: hide, then wipe
KB-DATA-53 | What counts as a DB write (db_side_effect_free table)
KB-DATA-54 | `.store` writes to the database
KB-DATA-55 | Anything doable in a UI can be done programmatically

## C_data.md — C6 Orders and order types
KB-DATA-56 | Order = instruction; object = data
KB-DATA-57 | Two order categories: transaction (booking) and static data
KB-DATA-58 | Business type (btt) per order, defined in META_TYP
KB-DATA-59 | Order types: CODE_ORDER_TYPE
KB-DATA-60 | Order fields and the four common attributes: keys, additions, post-its, links
KB-DATA-61 | `doc_*.do_wfc_action`: workflow action without loading the order
KB-DATA-62 | Reversals are new orders; booking events per order

## C_data.md — C7 Workflows
KB-DATA-63 | A workflow is the flowchart of an order's lifecycle
KB-DATA-64 | One workflow per business type; paths by order type
KB-DATA-65 | Example workflow figure: states and actions (illustrative)
KB-DATA-66 | `env_task_ext#.task#do_wfc_action` is the ice dev-task API, not the banking order API

## C_data.md — C8 Transactions and commit
KB-DATA-67 | `session.commit` / `session.rollback`: exist, use with great care
KB-DATA-68 | `no_commit` and order commits are not documented
KB-DATA-69 | Cross-reference: ice Workflow API commit rules differ by package

## C_data.md — C9 Banking dates, bank days and value days
KB-DATA-70 | Trade vs settlement; four accounting dates and their identifiers
KB-DATA-71 | TRX date: order created; basis for FX and VAT
KB-DATA-72 | DONE date: verification; 21.12.4712 until verified
KB-DATA-73 | VAL, BOOK and PERF dates
KB-DATA-74 | Trade dates from the order; settlement dates from rules
KB-DATA-75 | Trade date accounting (TBDA) vs settlement date accounting (VBDA)
KB-DATA-76 | Order form: editable dates vs read-only booking-event dates
KB-DATA-77 | Bank days, the EOD switch, value days and calendars
KB-DATA-78 | Date functions: `session.today`, `lookup.date`, `sysdate`

## C_data.md — C10 Object model
KB-DATA-79 | Objects: uniform handling; object types in CODE_OBJ_TYPE; technical objects
KB-DATA-80 | Holdings model: Person -> BP -> CONT -> POS (MACC) -> ASSET
KB-DATA-81 | BP = business relationship, external or internal (BU)
KB-DATA-82 | Person types and roles
KB-DATA-83 | Common object attributes and extensions

## C_data.md — C11 Effect mapping table

## D_standards.md — What a model must know first

## D_standards.md — D1 Coding conventions
KB-STD-01 | All comments must be in English
KB-STD-02 | Section comment: 78-dash line, `-- CAPITALS`, 78-dash line — CONFLICT with the doc's own examples
KB-STD-03 | Block comment: `---- CAPITALS ----` with an empty line before it
KB-STD-04 | Line comments go at the end of the line, in lower case, after `--`
KB-STD-05 | All code must be written in lower case
KB-STD-06 | A 78-dash line goes before each procedure/function header; no other header is required
KB-STD-07 | Indent two spaces, never tabs; "ice" applies the conventions on save
KB-STD-08 | Statement layouts for if / loop / with / case
KB-STD-09 | Two-space margin, except pre-compiler lines in column 1; header case — CONFLICT
KB-STD-10 | Package layout: header, imports (one per line), variables, routines, footer
KB-STD-11 | Column-aligned declarations (examples only)
KB-STD-12 | The docs break their own conventions; calibrate severity

## D_standards.md — D2 Naming conventions
KB-STD-13 | Use official Avaloq glossary abbreviations
KB-STD-14 | Compound names: `_`-separated, most significant business element first
KB-STD-15 | Names are singular (`cost_list`, not `costs`)
KB-STD-16 | Foreign keys are named `<target table without obj_/code_/meta_>_id`
KB-STD-17 | Constants: `c_` prefix, noun; boolean state names start with a predicate
KB-STD-18 | Code-table constants contain the intl_id; content-description suffix
KB-STD-19 | Variable prefixes by scope: `l_` local, `b_` body (package), `i_` input parameter
KB-STD-20 | Variable content suffix; comment variables whose meaning is not obvious
KB-STD-21 | Two-character SQL table aliases
KB-STD-22 | `t_` for record types and `x_` for PL/SQL in-out parameters (examples only)
KB-STD-23 | `#` and `$` in names: `<object>#<verb>` methods and `<ns>$` namespaces
KB-STD-24 | DDIC name prefixes encode the data kind
KB-STD-25 | Doc examples break the naming rules: report naming findings as warnings

## D_standards.md — D3 Correctness rules
KB-STD-26 | A `case` without `else` raises ORA-06592 (CASE_NOT_FOUND)
KB-STD-27 | Never cache session values in constants or package (`b_`) variables
KB-STD-28 | List handling: DDIC lists only feed a `for` loop; LIST_* tables are forbidden
KB-STD-29 | `deterministic`: an unchecked promise with strict conditions
KB-STD-30 | `db_side_effect_free`: decision table
KB-STD-31 | Do not write both `deterministic` and `db_side_effect_free` on one function
KB-STD-32 | `/*postp_start*/ ... /*postp_end*/` must enclose exactly the expression
KB-STD-33 | Exception idiom `when others then err.raise_fa(...)`; swallowing is an anti-pattern
KB-STD-34 | Collection pitfalls: assigning `null` fails to compile, a list-field cast is a copy, and `i_` collections can be changed by the callee
KB-STD-35 | The compiler does not check types or casts; paths must end in a scalar
KB-STD-36 | `session` commit/rollback are dangerous, especially in message processing
KB-STD-37 | Obsolete DDIC fields: compiler warning now, broken code later
KB-STD-38 | Null-related checks: `= null` comparisons and uninitialised accumulators
KB-STD-39 | Assigning to a parameter: the docs contradict themselves
KB-STD-40 | `sysdate` in banking logic (not a stated rule)

## D_standards.md — D4 Performance rules
KB-STD-41 | Use `case` instead of `elsif` chains (about 10% faster)
KB-STD-42 | Use typed `iffb`/`iffd`/`iffn` instead of `iff`
KB-STD-43 | Avoid implicit data type conversions
KB-STD-44 | Move loop-invariant calls out of loops (a general rule)
KB-STD-45 | Use `class_id('x')`, not `class('x').id`; DDIC field access, not table access
KB-STD-46 | Use `with` for repeated long designators (memory DDICs)
KB-STD-47 | Loop over list fields with `for x in list`, not an index loop (n² vs n)
KB-STD-48 | Attribute reads mixed with calls that may write: 3 selects instead of 1
KB-STD-49 | ASMD info marker "Missed performance optimization opportunity"
KB-STD-50 | A `deterministic` wrapper caches expensive `lookup.code` at install time
KB-STD-51 | Limit `.store`: each call writes to the DB
KB-STD-52 | Collection assignments copy; avoid them, especially in loops
KB-STD-53 | `list.remv` costs O(n); ID types are lighter than record types
KB-STD-54 | Report-specific and compiler-optimisation guidance lives elsewhere

## D_standards.md — D5 Testing standards (ATF)
KB-STD-55 | Test naming: the `it_`/`ut_` prefix runs as a test
KB-STD-56 | `assert` continues; `require` stops the procedure
KB-STD-57 | Minimal test shape: `it_main`, log_begin/log_end, `it.catch`
KB-STD-58 | Test code quality: production standard, stateless, rerunnable, kept in ATS
KB-STD-59 | Testability: inject session values; split the stateless calculation from the order wrapper

## D_standards.md — D6 Rule catalogue

## E_tooling.md — What a model must know first

## E_tooling.md — E1 Source lifecycle
KB-TOOL-01 | ice Workbench is the development, revision-control and deployment tool
KB-TOOL-02 | ice tools and interfaces (most are only named)
KB-TOOL-03 | Work and source hierarchy
KB-TOOL-04 | Check-out: the components of a change are those of its checked-out sources
KB-TOOL-05 | Task state machine: workflow actions and their start statuses
KB-TOOL-06 | Roles and the 4-eye code audit
KB-TOOL-07 | Check-in outcomes: merges, source states, audit locks
KB-TOOL-08 | Code review status and findings are stored in ice
KB-TOOL-09 | ADAI and its Integration Robot gate integration
KB-TOOL-10 | Integration is test-gated on the components a task touches
KB-TOOL-11 | Pre-approve: developer-run verification valid for about 24 h
KB-TOOL-12 | ADAI reporting, email and temporary ignore
KB-TOOL-13 | Installation packages, keys and stream-solution status
KB-TOOL-14 | Change dependencies are change-level, not code-level
KB-TOOL-15 | Task attributes are editable only in editable statuses

## E_tooling.md — E2 ice Workflow API catalogue (PL/SQL)
KB-TOOL-16 | Purpose, language and call form of the ice Workflow API
KB-TOOL-17 | Misuse: env_task_ext# is not a banking-order workflow API
KB-TOOL-18 | Terms of use
KB-TOOL-19 | Naming patterns in Avaloq PL/SQL APIs
KB-TOOL-20 | Commit semantics differ by package
KB-TOOL-21 | The four packages and ten views
KB-TOOL-22 | Parameter-mode and signature caveats (applies to all tables below)
KB-TOOL-23 | Package env_issue_ext# — issues (commits itself)
KB-TOOL-24 | Package env_item_expr_ext# — item-expression queries (READ)
KB-TOOL-25 | Item-expression syntax examples and fetch-loop pattern
KB-TOOL-26 | Package env_solution_ext# — solutions (commits itself)
KB-TOOL-27 | Package env_task_ext# — tasks and workflow actions (caller commits)
KB-TOOL-28 | env_task_ext# types: workflow parameter structure
KB-TOOL-29 | Workflow parameter keys per action
KB-TOOL-30 | Reopen: a null i_param and an empty i_param mean different things
KB-TOOL-31 | Task priority constants
KB-TOOL-32 | task#do_wfc_action return keys
KB-TOOL-33 | env_task_ext# exceptions
KB-TOOL-34 | Views require the WB - Developer role
KB-TOOL-35 | View catalogue (READ), compact
KB-TOOL-36 | Reference implementation: JIRA integration context and requirements
KB-TOOL-37 | Reference implementation: Java plug-in, REST client to PL/SQL, polling
KB-TOOL-38 | Coding pattern: build t_wfc_param_tab, call do_wfc_action, commit
KB-TOOL-39 | Coding pattern: create_task with named args and commit

## E_tooling.md — E3 Avaloq Test Framework (ATF)
KB-TOOL-40 | ATF is the official construction-test framework (not utPLSQL)
KB-TOOL-41 | ATF benefits and limitations
KB-TOOL-42 | Test environment; test sources live in the ATS application
KB-TOOL-43 | Test source types
KB-TOOL-44 | Test naming conventions: it_/ut_ and `<client key>$`
KB-TOOL-45 | Minimal Avaloq Script test package
KB-TOOL-46 | TEST SCRIPT source: XML, schema-validated, stored in ATS_SCRIPT
KB-TOOL-47 | TEST SCRIPT attribute catalogue
KB-TOOL-48 | compo_feat_list links tests to component features
KB-TOOL-49 | Test discovery: all it_*/ut_* procedures run in order; setup first, teardown last
KB-TOOL-50 | assert continues, require stops
KB-TOOL-51 | IT procedures seen in the docs
KB-TOOL-52 | CONFLICT: argument order of require
KB-TOOL-53 | Full Avaloq Script test example (address creation)
KB-TOOL-54 | Code-table sources for test data (two syntax forms)
KB-TOOL-55 | Data-driven test: code-table row access and `with ... as ... do`
KB-TOOL-56 | Test code quality: stateless, rerunnable, production-grade
KB-TOOL-57 | Test essentials and client test libraries
KB-TOOL-58 | Testability: pass session values and base parameters as defaulted parameters
KB-TOOL-59 | Testability: split stateless calc_intl from the order wrapper (example has anti-patterns)
KB-TOOL-60 | Execution flow: phases, separate session, dependency order
KB-TOOL-61 | depend changes order, not selection; a failed precondition skips its dependents
KB-TOOL-62 | Test selection by integration relevance
KB-TOOL-63 | Extending test scope: component mapping, test-script mapping, BU
KB-TOOL-64 | Parallel testing concept
KB-TOOL-65 | Parallel group rules and setup
KB-TOOL-66 | Starting tests: ATS_RUN#.subm, task 952, SQL*Plus; results via ATS_RES_V
KB-TOOL-67 | ATS_RUN#.subm parameters
KB-TOOL-68 | SQL*Plus scripts @ats / @atsc / @atsr and output format
KB-TOOL-69 | SmartClient task "ATS Test Run" (952)
KB-TOOL-70 | Preparation and post kinds
KB-TOOL-71 | ADAI configuration for construction tests
KB-TOOL-72 | Coverage runs need the database compiled in Debug Mode
KB-TOOL-73 | Coverage uses the Oracle PL/SQL profiler tables
KB-TOOL-74 | Overall coverage metrics and exclusions
KB-TOOL-75 | Coverage drill-down and colour thresholds
KB-TOOL-76 | Table ATS_SCRIPT (test metadata)
KB-TOOL-77 | Table ATS_RUN (one row per test run)
KB-TOOL-78 | Tables ATS_SCRIPT_RUN and ATS_SCRIPT_RUN_RES

## E_tooling.md — E4 Other tooling: compilers, warnings, ASMD, ice formatting
KB-TOOL-79 | CONFLICT: Avaloq Script compiles to PL/SQL — stated in one doc set, only inferred in another
KB-TOOL-80 | Compiler framework scope: collections and record types
KB-TOOL-81 | Documented compiler error messages (collections)
KB-TOOL-82 | Documented compiler warnings and compile-time checks
KB-TOOL-83 | CONFLICT: does the compiler check type compatibility?
KB-TOOL-84 | ASMD info marker "Missed performance optimization opportunity"
KB-TOOL-85 | Avaloq has its own static analysis (ASMD), language model and LSP — docs not in corpus
KB-TOOL-86 | Compiler translation of repeated DDIC reads into per-attribute selects
KB-TOOL-87 | Compiler directives in comments: /*postp_start*/ … /*postp_end*/
KB-TOOL-88 | ice applies formatting conventions on save; partial suppression exists
KB-TOOL-89 | Pre-compiler statements start in column 1 (`[Script 1.0]`, `script package`)
KB-TOOL-90 | No official source file extensions are documented
