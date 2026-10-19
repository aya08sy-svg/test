# SECTION B — TYPES AND METHOD CATALOGUE (SEC code TYPE)

Sources: verified/G2_verified.md (main), G1_verified_partA.md, G1_verified_partB.md, G3_verified.md, G6_verified.md. No entry in these files for this section was REJECTED. Cites are relative to `source_text/`. "DT" below means `paged/text/data-types.txt`; "EXPR" means `paged/text/avaloq-script-expressions.txt`.

## What a model must know first

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

---

## B1 Base types

### KB-TYPE-01 The five base types; no `raw`
- Fact: `BaseType = boolean | text | long | number | date .` A declared type is a BaseType, an IdType or an ObjectType (DDIC type). Collections (list/set/map) and record types (CF 18.0) are further type families. There is no `raw` type anywhere in the official text.
- Avaloq form: `BaseType = boolean | text | long | number | date .` ; `Type = BaseType | IdType | ObjectType .`
- Means: any other type keyword (raw, clob, varchar2, integer) in a script declaration is not Avaloq Script.
- Cite: DT p.1 "Base data types" ; paged/text/declarations-in-avaloq-script.txt p.2 "Declaring variables" ; DT pp.1-4, 7, 36-38
- Basis: STATED
- VERIFY: Q06 CONTRADICTS — secondary notes list `raw`; official EBNF does not.
- Audit use: a declaration with type `raw` is an error.
- From: G2-23, G1-26, G1-92, G6-25, G6-32

### KB-TYPE-02 boolean is one character '+' / '-'; literals true and false
- Fact: Because SQL has no boolean, Avaloq Script represents boolean data as a single character: "+" = true, "-" = false. The literals `true` and `false` also exist. PL/SQL mapping: `varchar2(1)` or `boolean` for variables, `boolean` for parameters (not number(1)/char(1)).
- Avaloq form: `if l_text_set.contains("hello") = '+' then`
- Means: `= '+'` / `= '-'` are boolean tests; `sort('-')` means descending.
- Cite: DT p.1 "Base data types" ; DT p.16 (set contains example) ; DT p.43 "Mapping Avaloq Script data types to PL/SQL" ; EXPR p.3 "Literal values" ; paged/text/what-are-data-dictionaries.txt p.4 "DDIC fields"
- Basis: STATED
- VERIFY: Q06 EXTENDS; secondary claim "boolean = number(1)/char(1)" CONTRADICTED (G6-28).
- Audit use: treat `= '+'` and `true` as equivalent when checking boolean comparisons.
- From: G2-23, G3-18, G6-28, G2-51

### KB-TYPE-03 text: extended ASCII, max 4000 characters
- Fact: `text` is a string of extended-ASCII characters (chr(0)..chr(255)) with a maximum length of 4000 characters; maps to PL/SQL `varchar2(4000)` (variables) / `varchar2` (parameters).
- Cite: DT pp.1-2 "Base data types" ; DT p.43 ; paged/text/what-are-data-dictionaries.txt p.4
- Basis: STATED
- Audit use: concatenations accumulating into `text` may exceed 4000 — use `long`.
- From: G2-24, G3-18, G6-27, G2-51

### KB-TYPE-04 long: max 32,000 characters = varchar2(32000), not CLOB
- Fact: `long` is like text with a maximum length of 32,000 characters and maps to `varchar2(32000)` / `varchar2`. Type inclusion: long >= text. It is not a CLOB; text larger than 32,000 chars has no Avaloq Script type.
- Cite: DT p.1 "Base data types" ; DT p.43 ; EXPR p.7 "Expression compatibility"
- Basis: STATED
- VERIFY: Q06 CONTRADICTS — secondary claim "long = CLOB" is wrong (G6-26).
- Audit use: do not translate PL/SQL CLOB to `long`; flag it.
- From: G2-24, G2-19, G2-51, G6-26, G3-18

### KB-TYPE-05 number: one numeric type, range 1E-84..1E127, 38 digits
- Fact: `number` is an integer or real between 1E-84 and 1E127 with precision 38 digits. It is the only numeric type. Number literals are unsigned integers or reals (a real always contains a decimal point); both have type number. No exponent form; sign is a unary operator.
- Avaloq form: `number = integer | real . integer = digit { digit } . real = digit { digit } . { digit } .` ; `2002` `3.1415926`
- Cite: DT pp.1-2 "Base data types" ; paged/text/language-fundamentals.txt pp.1-2 "Numbers" ; EXPR p.7
- Basis: STATED
- Audit use: lexer must not read `1.` as real in `1 .. n`.
- From: G2-24, G2-19, G1-12

### KB-TYPE-06 date: date and time, upper bound 31.12.4712 AD
- Fact: `date` holds date (and time). Non-SDS environment: 31.12.4712 BC to 31.12.4712 AD. SDS environment: 01.01.0001 AD to 31.12.4712 AD, plus (31.12.4712 BC, 30.12.4712 BC). Maps to Oracle `date`. "High precision" is not documented.
- Cite: DT pp.1-2 "Base data types" ; DT p.43
- Basis: STATED
- Audit use: date is NOT allowed as set element or map key (KB-TYPE-29).
- From: G2-24, G6-29, G3-18

### KB-TYPE-07 No length/precision specifiers; script-to-PL/SQL type mapping
- Fact: Explicit text or number lengths are not supported. Mapping: boolean -> varchar2(1) or boolean (vars) / boolean (params); text -> varchar2(4000)/varchar2; long -> varchar2(32000)/varchar2; number -> number; date -> date. ID types: mem_doc -> doc_mgr#.t_doc; doc -> doc#.t_doc_id; mem_msg -> msg_mgr#.t_msg; msg -> msg#.t_msg_id; obj -> obj#.t_obj_id; code_table_x -> pls_integer; since 5.7 `id table <code table>` -> pls_integer, `id table msg`/`doc` -> number(12), `id table obj` -> pls_integer; other -> varchar2(2000)/varchar2, but "other id types might be translated to something more specific than varchar2".
- Means: mem_doc / mem_msg are in-memory manager handles; doc / msg / obj are ids.
- Cite: DT pp.43-44 "Mapping Avaloq Script data types to PL/SQL"
- Basis: STATED
- VERIFY: Q12 EXTENDS; Q06 EXTENDS.
- Audit use: `text(10)`, `number(5,2)`, `varchar2` in a script declaration are errors; do not hard-code varchar2(2000) for all other ids.
- From: G2-51, G6-27

### KB-TYPE-08 Type rules apply to every designator; uninitialised = null
- Fact: Statements about variables of a type also apply to constants, fields and parameters. A variable without a default is null; a default expression is evaluated at runtime on scope entry. Null works like PL/SQL. (Exception: collections are auto-initialised to empty, KB-TYPE-35.)
- Cite: DT p.1 intro ; paged/text/declarations-in-avaloq-script.txt p.2 "Declaring variables", "Null values"
- Basis: STATED
- Audit use: accumulator used before assignment (`l_val := l_val + x` with no init) stays null.
- From: G2-22, G1-27, G1-28

---

## B2 ID types vs record (DDIC) types

### KB-TYPE-09 ID types hold only the primary key; "lighter and quicker"
- Fact: An ID type holds only the primary key of a database record (e.g. a BP in OBJ_BP, a language in CODE_LANG), not its fields. Syntax `id [table] ident`. DDIC fields of this type end in `_id`; the Navigator shows "id of <table-name>". IDs are used mainly to pass object references to other code such as PL/SQL; "Using the ID to refer to an instance of an object is lighter and quicker than using a record type." ID types are sometimes called reference types.
- Avaloq form: `IdType = id [ table ] ident .` ; `l_bp_id id obj_bp` ; `l_val_calc_method_id id table code_val_calc_method` ; `return id table wfc_status`
- Means: an `_id` value is a key only; no data is loaded until it is cast/navigated.
- Cite: DT p.3 "Business-oriented data types" (row ID types) ; DT p.4 Note ; paged/text/what-are-data-dictionaries.txt p.5 "DDIC fields" ; paged/text/declarations-in-avaloq-script.txt p.2 ; paged/text/hints-and-tips-on-using-avaloq-script.txt p.9
- Basis: STATED
- VERIFY: Q08 EXTENDS; Q26 EXTENDS — documented lightweight-reference guidance. Secondary example `id doc_order` is UNSUPPORTED (official order DDICs are doc_pay, doc_stex, doc_bp, generic `doc`).
- Audit use: prefer `id <ddic>` parameters over record parameters when only passing references.
- From: G2-25, G3-19, G6-30

### KB-TYPE-10 DDIC (record / object) types point to the whole record
- Fact: A DDIC type (bare DDIC name, no `id`) points to an entire database record and allows access to its fields and calling its methods. DDIC types are sometimes called object types or business object types. Example field triple: `bank_bp` (type obj_bp), `bank_bp_a` (boolean), `bank_bp_id` (id of obj_bp).
- Avaloq form: `function my_function( i_country obj_country` vs `( i_country_id id obj_country`
- Means: `x.bank_bp.<attr>` navigates to a second entity (read); `x.bank_bp_id` is the key only.
- Cite: DT p.4 row "DDIC types" and Note ; paged/text/what-are-data-dictionaries.txt p.5 (rows ID types, Record types; screenshot)
- Basis: STATED
- VERIFY: Q08 CONFIRMS; Q15 PARTIAL.
- From: G2-26, G3-19

### KB-TYPE-11 Data access expressions must end in a scalar
- Fact: A data access expression must result in a scalar type (base type or ID type); using a non-scalar (record/DDIC) as an expression may silently yield null.
- Cite: EXPR p.3 Note
- Basis: STATED
- VERIFY: Q27 EXTENDS — pitfall not caught by the compiler.
- Audit use: flag a record-typed path used as a value (compared, assigned to scalar).
- From: G2-08, G6-57

### KB-TYPE-12 DDIC field types, list fields and field operations
- Fact: DDIC fields are typed like variables (base, id, record). A field can also be a list of any type ("list of" in the type column, e.g. "list of id of database table obj", "list of doc_block"); list fields may take parameters. Navigator Operations column: get/set for simple fields, count/list (with or without get) for list fields, do for methods, add for the `new` constructor. "set" availability depends on the field (e.g. MEM_DOC record-type fields are get-only).
- Cite: paged/text/what-are-data-dictionaries.txt pp.4-7 "DDIC fields", "List DDIC fields", "Simple DDIC fields" (screenshots)
- Basis: STATED (operation values read from screenshots); mapping operations to effects INFERRED
- VERIFY: Q14 EXTENDS.
- Audit use: get -> read, set -> modify, count/list -> list read, do -> method, add -> constructor.
- From: G3-18, G3-20, G3-21, G3-A01

---

## B3 Type compatibility, casts, conversions

### KB-TYPE-13 Is type compatibility checked by the compiler? CONFLICT
- Fact: CONFLICT. EXPR p.7 says expressions must be assignment compatible but "The compatibility is currently not checked by the compiler." DT p.42 says assigning a MEM_DOC variable to an OBJ variable "will produce a warning or even an error, depending on the configuration", collection type violations give design-time warnings, and CF 18.0 record types have strict type checking. Probably different compiler generations.
- Cite: EXPR pp.7-8 "Expression compatibility" ; DT p.42 ; DT pp.36-38
- Basis: STATED (both sides)
- VERIFY: Q27 EXTENDS / PARTIAL — compiler severity is configurable.
- Audit use: report type incompatibility as an own finding regardless of compiler output.
- From: G2-19, G2-55, G2-47

### KB-TYPE-14 Same type, type inclusion, type extension
- Fact: Same type = same type identifier, or both ID types referring to the same root type. Inclusion: textual long >= text; numeric has only number. Extension: Tb directly extends Ta if Tb lists Ta in its inheritance list; extension is reflexive and transitive.
- Cite: EXPR pp.7-8 "Expression compatibility"
- Basis: STATED
- VERIFY: Q15 EXTENDS — business types have inheritance lists.
- From: G2-19

### KB-TYPE-15 Assignment compatibility rules
- Fact: e (type Te) is assignment compatible with v (type Tv) if: same type; both numeric or both textual and Tv includes Te; both record or ID types and Te (or its root) extends Tv (or its root); or e is null (not for collections, KB-TYPE-36). Actual parameters must be assignment compatible with formals.
- Cite: EXPR pp.8-9 Example box ; paged/text/declarations-in-avaloq-script.txt pp.5-6
- Basis: STATED
- Audit use: implement `assignable(Te, Tv)`; text <- long is narrowing.
- From: G2-21, G1-38

### KB-TYPE-16 Operand types per operator — CONFLICT on ordering comparisons
- Fact: CONFLICT. The EXPR p.8 table (operator column printed truncated: "<= >", ">= >") gives: + - * / mod on number -> number; or/and/not on boolean -> boolean; = != <> on number -> boolean; ordering on string, date and boolean -> boolean; = != <> on boolean or business type (ID or record) -> boolean; is [not] null on any -> boolean. Language fundamentals p.3 says =, !=, <>, <, <=, >, >= apply to numbers, strings and dates, and only =, !=, <> also apply to boolean, id types and record types. Prefer Language fundamentals. `in (a,b,c)`: x any type, list values must match. Comparison results are "always true, false, or null".
- Cite: EXPR p.8 "Table: Expression compatibility" ; paged/text/language-fundamentals.txt p.3 "Comparison operators"
- Basis: STATED (both); that "<= >" is truncated "< <= > >=" is INFERRED
- VERIFY: Q06 EXTENDS.
- Audit use: ordering comparison on boolean/id/record = error; on number = valid. CF-18 records cannot be compared at all (KB-TYPE-46).
- From: G2-20, G2-66, G1-18

### KB-TYPE-17 DDIC type cast T(v) — not checked by the compiler
- Fact: `T(v)` interprets v as (an ID of) a DDIC of type T so its fields/methods can be accessed. Valid if v is scalar, or v is a DDIC value and T extends v's static type; neither constraint is checked by the compiler. Official examples cast an `id obj_bp`, an `obj`, and even a `number` to obj_bp.
- Avaloq form: `obj_bp(l_bp_id).ref_curry.name` ; `obj_bp(l_obj).ref_curry.name` ; `obj_bp(l_val).ref_curry.name`
- Means: lookup by ID then field read; cast + field implies loading the record (INFERRED).
- Cite: EXPR pp.4-5 "DDIC type casts"
- Basis: STATED (semantics, unchecked); INFERRED (record load)
- VERIFY: Q08 CONFIRMS; Q27 EXTENDS.
- Audit use: `ident(expr)` where ident is a DDIC = cast, not call; flag casts of a different DDIC/ID root or of plain number/text variables.
- From: G2-13, G6-31

### KB-TYPE-18 Collection cast of a "list of" field: list(...) / set(...)
- Fact: The DDIC cast also applies to collections: v must be a "list of" field and T is list or set; the field's element type must be a legal type parameter (a list of date cannot be cast to set). The cast copies every value into a new collection; changing it does not change the field. Casting to set removes duplicates; operations on casts can be chained.
- Avaloq form: `set(i_doc.link_list).count` ; `l_list := list(l_doc.link_list);`
- Cite: EXPR pp.5-6 ; DT pp.26-27 "Casting a list of field to a collection"
- Basis: STATED
- VERIFY: Q08 EXTENDS; Q26 EXTENDS.
- Audit use: `set(<list of date field>)` is illegal; modifying a cast result expecting the field to change is a bug.
- From: G2-14, G2-37, G6-42

### KB-TYPE-19 Implicit conversion exists, is slower; id is not text
- Fact: Assigning a number to text works through implicit conversion, but "Type conversions are slower than using correct data types to begin with." In general, id types are not type compatible with text. `to_char` is attested in official code; `to_date`/`to_number` are not attested in these docs.
- Avaloq form: `l_text := 10;` (INEFFICIENT) vs `l_number := 10;` (BETTER)
- Cite: paged/text/hints-and-tips-on-using-avaloq-script.txt p.2 "Avoid implicit data type conversions" ; DT p.42 ; DT p.44 ; hints-and-tips p.3
- Basis: STATED
- VERIFY: Q26 CONFIRMS.
- Audit use: number literal assigned to text (or reverse, date<->text) = performance finding; id assigned to text = type finding.
- From: G1-71, G2-55, G6-33, G2-51

---

## B4 Collections

### KB-TYPE-20 No user-defined lists; collection DDICs provide them
- Fact: The language does not allow user-defined lists or tables. Provided by DDICs: MEM_DB_LIST_CHAR (text), MEM_DB_LIST_DATE (dates), MEM_DB_LIST_NR (numbers), MEM_TAB (memory tables), and templated LIST, MAP, SET. DB list tables LIST_CHAR, LIST_DATE, LIST_NUMBER cannot be used directly in script (doc prints "LIST NUMBER").
- Cite: DT p.5 ; paged/text/hints-and-tips-on-using-avaloq-script.txt p.5 "List handling in Avaloq Script"
- Basis: STATED
- VERIFY: Q10 EXTENDS; Q14 EXTENDS; Q17 EXTENDS.
- Audit use: reference to `list_char|list_date|list_number` tables in script = error.
- From: G2-28, G1-76, G1-77

### KB-TYPE-21 List fields: operations
- Fact: A DDIC field can hold a list of values; available operations depend on the field. Indexes are 1-based.

| Operation | Params | Returns | Description | Data effect |
|---|---|---|---|---|
| list | - | items | iterate in `for ... loop`, or DDIC cast to a collection | read |
| count | - | number | number of items | read |
| get | index 1..count | item | single item | read |
| set | index 1..count | - | set single item | write (field) |
| clear | - | - | remove all items | write (field) |
| add | (named fields) | - | append new item at end, using a with statement | write (field) |
| rmv | position 1..count | - | remove item at position | write (field) |
| remv_item | item_nr = value | - | remove item by content | write (field) |

- Avaloq form: `mem_doc.postit_list.add(topic => "Approval", text => "Order exceeds AML threshold") ;` ; `for p in cont.pos_list loop`
- Means: count/get/list = read; set/clear/add/rmv/remv_item = modify the object's list field.
- Cite: DT pp.4-5 "List fields" ; paged/text/what-are-avaloq-script-expressions.txt pp.1-2 (diagram) ; paged/text/what-are-data-dictionaries.txt pp.5-6
- Basis: STATED
- VERIFY: Q08 CONFIRMS/EXTENDS.
- Audit use: validate operation against the DDIC "Operations" column.
- From: G2-27, G2-06, G3-20

### KB-TYPE-22 Lists returned by DDIC functions must be used at once or cast
- Fact: Lists can only be returned by DDIC functions; the returned list must be used immediately in a for loop; to save, reference, edit or pass it to another script procedure, cast it to a collection DDIC.
- Cite: paged/text/hints-and-tips-on-using-avaloq-script.txt p.5 "List handling in Avaloq Script"
- Basis: STATED
- Audit use: list-of value assigned/passed/returned without `list(...)`/`set(...)` = error.
- From: G1-76, G6-42

### KB-TYPE-23 MEM_DB_LIST_CHAR — complete API
- Fact: Text list DDIC persisted in table LIST_CHAR, with manual memory management.

| Item type | Name | Params | Returns | Description | Data effect |
|---|---|---|---|---|---|
| Constructor | n/a | list_char_id number (opt), remv_after boolean (opt) | list | create; if list_char_id given, fill from LIST_CHAR; if remv_after true, list removed at end of statement | DB read if id given; memory alloc |
| Field (get/set) | name | - | text | list name | in-memory |
| Field (get) | to_string | - | text | list as comma-separated string | in-memory read |
| Field (get/set) | list_char_id | - | number | id assigned to list | in-memory |
| Field (get/set) | item | idx number | text | item at position idx | in-memory |
| List | item_list | - | list | the list; ops count, get, list, clear, add, remv | in-memory |
| Action | store_list | - | - | store list to table LIST_CHAR | DB write |

- Cite: DT pp.5-6 (verified on PDF p.6)
- Basis: STATED
- VERIFY: Q17 EXTENDS; Q26 EXTENDS.
- Audit use: without `remv_after` the list must be released manually (KB-TYPE-54). Note `remv` here vs `rmv` on list fields.
- From: G2-29

### KB-TYPE-24 MEM_DB_LIST_NR — complete API
- Fact: Same structure as MEM_DB_LIST_CHAR, for numbers, persisted in table LIST_NUMBER.

| Item type | Name | Params | Returns | Description | Data effect |
|---|---|---|---|---|---|
| Constructor | n/a | list_nr_id number (opt), remv_after boolean (opt) | list | create; fill from LIST_NUMBER if id given; remove at end of statement if remv_after | DB read if id given |
| Field (get/set) | name | - | text | list name | in-memory |
| Field (get) | to_string | - | text | comma-separated string | in-memory read |
| Field (get/set) | list_nr_id | - | number | id assigned to list | in-memory |
| Field (get/set) | item | idx number | number | item at position idx | in-memory |
| List | item_list | - | list | ops count, get, list, clear, add, remv | in-memory |
| Action | store_list | - | - | store list to table LIST_NUMBER | DB write |

- Cite: DT pp.6-7
- Basis: STATED
- VERIFY: Q17 EXTENDS.
- From: G2-30

### KB-TYPE-25 MEM_DB_LIST_DATE — "similar", API not documented
- Fact: MEM_DB_LIST_DATE (lists of dates) is described only as "similar" to MEM_DB_LIST_CHAR; its full API is not in the verified docs.
- Cite: DT pp.5-6 ; paged/text/hints-and-tips-on-using-avaloq-script.txt p.5
- Basis: STATED ("similar"); exact member names not documented
- From: G2-29, G1-77

### KB-TYPE-26 MEM_TAB — known members only from one example
- Fact: MEM_TAB is a memory table created in a `with new mem_tab(<name>) as obj_tab do ... end with;` block. Members seen: `obj_tab.cols.add_base(col_name =>, base_type =>)`, `obj_tab.type_number`, `obj_tab.remv` (release memory, "often forgotten"). Runtime type checks, no persistence, PL/SQL API tab#. Full API not documented here.
- Avaloq form:
```
with new mem_tab(c_tab_name_obj) as obj_tab do
  obj_tab.cols.add_base(
    col_name  => 'col1'
   ,base_type => obj_tab.type_number
  );
  ...
  -- often forgotten releasing of memory
  obj_tab.remv;
end with;
```
- Cite: DT pp.41-42 "Example for MEM_TAB vs LIST" ; DT pp.39-40
- Basis: STATED
- VERIFY: Q26 EXTENDS.
- From: G2-54, G2-52

### KB-TYPE-27 Templated collections list<V>, set<V>, map<K,V> (since 5.3)
- Fact: Three DDIC types that must be instantiated with type parameters, introduced in kernel release 5.3: list<V> (items of one type), set<V> (V only text, number or business type), map<K,V> (K only text, number or business type). Nesting is allowed.
- Avaloq form:
```
l_number_list          list<number>;
l_number_list_list     list<list<number>>;
l_text_set             set<text>;
l_person_set           set<obj_person>;
l_text_boolean_map     map<text, boolean>;
l_text_number_list_map map<text, list<number>>;
l_bp_person_map        map<obj_bp, obj_person>;
```
- Cite: DT pp.7-8 "Collection types"
- Basis: STATED
- VERIFY: Q06 EXTENDS; Q10 EXTENDS.
- From: G2-31

### KB-TYPE-28 Collection availability: compiler framework only
- Fact: Collection types exist only in Avaloq Script compiled via the compiler framework; as of ACP 5.6 this excludes Avaloq Script embedded in REP PRINT sources and runtime-compiled Avaloq Script. Collections are implemented as PL/SQL associative arrays.
- Cite: DT pp.30-31 "Implementation restrictions"
- Basis: STATED; which expression contexts (rule loader COND/STMT etc.) count as runtime compiled is INFERRED/unknown
- VERIFY: Q01 EXTENDS; Q27 EXTENDS.
- Audit use: `list<`/`set<`/`map<` in REP PRINT or runtime-compiled script = error.
- From: G2-43, G6-86

### KB-TYPE-29 Set element / map key types: number, text, DDIC/id only
- Fact: Set element and map key types are limited to number or text (or assignable to them, e.g. DDICs and id table types). `set<date>` and `map<date, ..>` are compiler errors ("Unsupported key type. Only number, text, and Avaloq Script DDIC types are allowed key types."). `set<obj_person>` and `map<obj_bp, ..>` are legal.
- Cite: DT pp.7-8 ; DT p.30 ; DT p.32 "Compiler error messages"
- Basis: STATED
- Audit use: flag set/map keys of date, boolean, long or record; do not flag `set<obj_bp>`.
- From: G2-31, G2-43, G2-44, G6-35

### KB-TYPE-30 list<V> — complete method table (14 methods)
- Fact: list<V> has exactly these methods (verified against DT pp.8-14, none missing). `first`, `next`, `cnv_to(T)` do NOT exist.

| Method | Params | Returns | Description | Data effect | Example |
|---|---|---|---|---|---|
| add | val V | - | add item to tail | in-memory write | `l_number_list.add(1);` |
| contains | val V | boolean | does list contain value? | in-memory read | (none) |
| get | pos number | V | item by position; returns null if position is not populated | in-memory read | `l_number := l_number_list.get(1);` |
| set | pos number, val V | - | set item by position; throws if pos < 1 or > count | in-memory write | `l_number_list.set(1, l_number);` |
| count | - | number | item count | in-memory read | `l_cnt := l_number_list.count;` |
| clear | - | - | clear list | in-memory write | `l_number_list.clear;` |
| store | list_id (optional) | id table list_<datatype> | persists list to DB, returns new list_id; with an existing id clears stored rows then replaces them; not for nested lists | DB write | `l_id := l_list.store;` `l_list.store(l_id);` |
| load | list_id number (mandatory) | - | loads stored contents into the variable | DB read into memory | `l_list.load(l_id);` |
| remv | val V, pos number | - | remove first item = val, or item at pos; shifts later items left; scalar lists only; exception if both set; out-of-bounds pos does nothing; worst case O(n), last element constant time | in-memory write | `l_number_list.remv(l_number);` `l_number_list.remv(pos=>1);` |
| values | - | list of V | iterate over all values | in-memory read | `for val in l.values loop ... end loop;` |
| sort | asc boolean ('+' default) | - | in-place sort; '+'/empty asc, '-' desc; scalar lists only | in-memory write | `l_number_list.sort;` `l_number_list.sort('-');` |
| cnv_to_text | delim text (';' default) | text | join to text; only text-convertible types; throws code_ap_err.text_length_exceeds_maximum above 32,000 chars | in-memory read | `l_text := l_list.cnv_to_text(','); -- 'a,b'` |
| list_from_text | input text, delim text (';' default) | - | split text into list; throws code_ap_err.text_length_exceeds_maximum if an item exceeds V size (list<text>: 4000/element) | in-memory write | `l_list.list_from_text('a,b,c,d,e',',');` |
| <T> empty (static) | - | list<T> | empty list | none | `l_list_obj_bp := list.empty<obj_bp>;` |

- Means: parameterless methods are called without parentheses (`.count`, `.clear`, `.sort`).
- Cite: DT pp.8-14 "Collection type methods / list<V>" ; DT p.32
- Basis: STATED; data-effect column for store/load from DT p.9, pp.29-30; others INFERRED from "in memory" descriptions
- VERIFY: Q10 CONFIRMS/EXTENDS; Q11 EXTENDS; Q26 EXTENDS. Secondary `.first/.next(i)/.cnv_to(T)` CONTRADICTED (G6-39).
- Audit use: unknown list method = finding.
- From: G2-32, G6-37, G6-39

### KB-TYPE-31 list.remv positional argument binds to val, not pos
- Fact: The remv parameters are listed as `val V, pos number`. `remv(l_number)` removes by value; `remv(pos=>1)` removes the first element. So `remv(1)` on list<number> removes the first element equal to 1, not index 1.
- Avaloq form: `l_number_list.remv(pos=>1); -- removes the first element in this list`
- Cite: DT p.11 "remv"
- Basis: STATED (signature, examples); INFERRED (positional binding to val)
- VERIFY: Q10 CONTRADICTS — secondary claim `.remv(idx)` removes by index is wrong.
- Audit use: require `pos=>` or `val=>` for remv with a numeric argument.
- From: G6-38, G2-32

### KB-TYPE-32 set<V> — complete method table (11 instance + 5 static)
- Fact: set<V> has these 11 instance methods plus static empty and four static set operations (verified against DT pp.14-21; the G2 verifier summary counts "14" but its table has 16 rows).

| Method | Params | Returns | Description | Data effect | Example |
|---|---|---|---|---|---|
| add | val V | - | add item; null throws code_ap_err.adding_null_not_supported | in-memory write | `l_text_set.add("hello");` |
| count | - | number | item count | in-memory read | `l_cnt := l_text_set.count;` |
| clear | - | - | clear set | in-memory write | `l_text_set.clear;` |
| store | set_id (optional) | id table set_<datatype> | persist set (stored as a list) to DB, return new set_id; existing id: clear then replace | DB write | `l_id := l_set.store;` `l_set.store(l_id);` |
| load | set_id number (mandatory) | - | load stored contents | DB read into memory | `l_set.load(l_id);` |
| remv | val V | - | remove item matching value | in-memory write | `l_text_set.remv("hello");` |
| contains | val V | boolean | does set contain value? | in-memory read | `if l_text_set.contains("hello") = '+' then l_text_set.add("world"); end if;` |
| values | - | list of V | iterate all values | in-memory read | `for val in l_text_set.values loop session.debug(val); end loop;` |
| cnv_to_text | delim text (';') | text | join; throws text_length_exceeds_maximum > 32,000 | in-memory read | `l_text := l_set.cnv_to_text(',');` |
| set_from_text | input text, delim text (';') | - | split into set, duplicates removed; empty set if input null/empty; throws text_length_exceeds_maximum if item exceeds V size; throws adding_null_not_supported if an entry adds null | in-memory write | `l_set.set_from_text('a,b,c,d,e',',');` `l_set.set_from_text('1;') -- throws` |
| is_equal | set1 set<V> | boolean | '+' if same members | in-memory read | `if l_set1.is_equal(l_set2) = '+' then do_x; end if;` |
| <T> empty (static) | - | set<T> | empty set | none | `l_set_obj_bp := set.empty<obj_bp>;` |
| <T> intersect (static) | set1, set2 set<T> | set<T> | intersection; sets must be mutually assignable (same underlying PL/SQL type) | none (new set) | `set.intersect<obj_person>(l_set_first_name_john, l_set_last_name_doe)` |
| <T> union (static) | set1, set2 | set<T> | union | none (new set) | `set.union<text>(l_set_birds, l_set_mammals);` |
| <T> subtract (static) | set1, set2 | set<T> | set1 minus set2 | none (new set) | (doc example repeats union) |
| <T> sym_diff (static) | set1, set2 | set<T> | in set1 or set2 but not both | none (new set) | (doc example repeats union) |

- Cite: DT pp.14-21 "set<V>"
- Basis: STATED (whether set_<datatype> tables exist is unclear: store "stores the set values as a list")
- VERIFY: Q10 EXTENDS; Q11 EXTENDS.
- Audit use: `set.exist` is not a documented method (map uses exist).
- From: G2-33, G6-41

### KB-TYPE-33 Static set operations: set.<op><T>(a, b)
- Fact: intersect, union, subtract and sym_diff are static generic methods returning a new set, not instance methods. intersect: members in both (sets must be mutually assignable, same underlying PL/SQL type); union: members in either; subtract: set1 minus set2; sym_diff: in set1 or set2 but not both.
- Avaloq form: `l_set_john_doe := set.intersect<obj_person>(l_set_first_name_john, l_set_last_name_doe)` ; `l_set_animals := set.union<text>(l_set_birds, l_set_mammals);`
- Cite: DT pp.19-21
- Basis: STATED (official examples for subtract and sym_diff repeat the union example)
- VERIFY: Q10 CONTRADICTS — secondary `l_set.union(other)` instance form is wrong.
- Audit use: grammar must allow type arguments after a method name; `<setvar>.union(` = error.
- From: G2-33, G6-40

### KB-TYPE-34 map<K,V> — complete method table (11 methods)
- Fact: map<K,V> has these methods (verified DT pp.21-25). It has NO store/load, and uses `exist` (not `contains`).

| Method | Params | Returns | Description | Data effect | Example |
|---|---|---|---|---|---|
| put | key K, val V | - | add key-value pair; null key throws code_ap_err.adding_null_not_supported | in-memory write | `l_text_boolean_map.put("a", true);` |
| count | - | number | item count | in-memory read | `l_cnt := l_text_boolean_map.count;` |
| get | key K | V | value for key ("null if absent" not stated) | in-memory read | `if l_text_boolean_map.get("a") then ... end if;` |
| clear | - | - | clear map | in-memory write | `l_text_boolean_map.clear;` |
| remv | key K | - | remove item matching key | in-memory write | `l_text_boolean_map.remv("a");` |
| exist | key K | boolean (+/-) | does map contain key? | in-memory read | `if l_text_boolean_map.exist("a") = '+' then l_text_boolean_map.put("b", false); end if;` |
| keys | - | list of K | iterate all keys | in-memory read | `for key in l_text_boolean_map.keys loop session.debug(key); end loop;` |
| values | - | list of V | iterate all values | in-memory read | `for val in l_text_boolean_map.values loop ... end loop;` |
| cnv_to_text | key_delim text (':'), item_delim text (';') | text | serialise; throws text_length_exceeds_maximum > 32,000 | in-memory read | `cnv_to_text(':', ',') -- 'one:1,two:2'` |
| map_from_text | key_delim text (':' default), item_delim text (';' default); input text appears only in examples | - | parse; only text-convertible maps; throws text_length_exceeds_maximum if a key exceeds K size or value exceeds V size (map<text,long> keys max 4000); adding_null_not_supported if an entry adds a null key | in-memory write | `l_text_map.map_from_text('one:1;two:2');` `l_text_map.map_from_text('a:1;b:2;:c'); -- throws` |
| <L,T> empty (static) | - | map<L,T> | empty map | none | correct form `map.empty<obj_person, text>`; doc prints `list.empty<obj_person, text>` (error) |

- Cite: DT pp.21-25 "map<K,V>"
- Basis: STATED (`map.empty` spelling INFERRED from the doc error)
- VERIFY: Q10 EXTENDS.
- Audit use: `map.contains`, `map.store` are not documented methods.
- From: G2-34, G6-41, G2-64

### KB-TYPE-35 Declaring collections: auto-initialised; parameter default only `:= default`
- Fact: Collection variables are declared with list/set/map and type arguments (nestable) and are automatically initialised (empty). Collection-typed parameters cannot normally have a default; the one exception is the built-in `default`, which gives the empty collection.
- Avaloq form:
```
function example(  i_x    map<number, set<text>> := default
) return boolean is
```
- Cite: DT pp.25-26 "Declaring a collection variable", "Declaring an optional collection input parameter"
- Basis: STATED
- VERIFY: Q07 EXTENDS.
- Audit use: no need to null-check or initialise collections.
- From: G2-35

### KB-TYPE-36 Null rules for collections
- Fact: (a) Collections cannot be assigned null; `l_list := null;` is a compile-time error "Incompatible types" (not a runtime error); use `.clear`. (b) `set.add(null)`, `map.put(null, ..)`, and set_from_text/map_from_text entries producing null throw `code_ap_err.adding_null_not_supported`. (c) `list.get(pos)` returns null if the position is not populated. (d) PL/SQL must never set a script collection to null — there is no check.
- Cite: DT p.26 "Assigning a collection" ; DT p.31 ; DT pp.8, 15, 21, 25 ; DT p.36 "Restrictions"
- Basis: STATED
- VERIFY: secondary claim "null assignment = runtime exception" CONTRADICTED on timing (G6-34).
- Audit use: `set.add(x)` / `map.put(x, ..)` with x possibly null (DDIC field read) and no guard = runtime risk.
- From: G2-36, G2-44, G2-32, G2-33, G2-34, G2-46, G6-34, G6-41

### KB-TYPE-37 Collection exceptions (code_ap_err.*)
- Fact: Documented runtime exceptions: `code_ap_err.text_length_exceeds_maximum` (cnv_to_text result > 32,000 chars; *_from_text item exceeds element size); `code_ap_err.adding_null_not_supported` (null added to set / null map key). list.set out of bounds throws (exception name not given); list.remv with both pos and val throws (name not given).
- Cite: DT pp.9, 11, 13-15, 18, 21, 23-25
- Basis: STATED
- VERIFY: Q11 EXTENDS — exceptions are code_ap_err.<name> codes.
- From: G2-32, G2-33, G2-34

### KB-TYPE-38 Collection compiler error messages
- Fact: Five documented compiler errors:

| Message | Trigger | Fix |
|---|---|---|
| Reference to template data dictionary is only allowed with type arguments | `l_list list;` | `l_list list<number>;` |
| Wrong count of DDIC template type parameters | `list<text, number>` | `list<text>` |
| Incompatible types: expected type <1> but found type <2> | list<number> to list<text>; list to set; `:= null` | matching types / `.clear` |
| Unsupported field operation 'store' for type <1>. Not supported for nested DDIC collections. | `.store` on `list<list<number>>` | store inner lists, keep a list of ids |
| Unsupported key type. Only number, text, and Avaloq Script DDIC types are allowed key types. | `map<date, obj_person>`, `set<date>` | use number/text/DDIC key |

- Cite: DT pp.31-32 "Compiler error messages"
- Basis: STATED
- VERIFY: Q27 CONFIRMS; Q34 PARTIAL.
- From: G2-44

### KB-TYPE-39 Collection assignment type rules
- Fact: Assignment is allowed if type and type argument match, or the type arguments share the same underlying DDIC id fragment (obj_bp and obj are both obj#.t_obj_id, so list<obj_bp> <-> list<obj>). Copy semantics apply (KB-TYPE-48).
- Avaloq form: `l_list_2 := l_list_1;` ; `l_list_1 := l_list_of_list.get(1);`
- Cite: DT p.26 "Assigning a collection"
- Basis: STATED
- From: G2-36

### KB-TYPE-40 Iteration: for v in coll.values / map.keys
- Fact: Collection operations are used like other DDIC operations; iterate with `for <var> in <coll>.values loop ... end loop;` or `.keys` for maps. The loop variable is not declared.
- Avaloq form: `for i in l_list.values loop l_sum := l_sum + i; end loop;`
- Cite: DT pp.28-29 "Operations on a collection"
- Basis: STATED
- From: G2-40

### KB-TYPE-41 Persistence: store/load, pre-allocated id
- Fact: `.store` persists list/set to DB tables (list_xxx) and returns an id; `.load(id)` reads back. Legitimate use: pass data to a report, or call `.store` once to allocate an id that an asynchronous process (e.g. background report in another session) fills, then `.load(id)`. `.store` is called a "field action". map has no store/load; it persists only via manual conversion to MEM_DB_LIST (or MEM_TAB).
- Avaloq form:
```
l_id := l_input.store;
submit_async_report('ASYNC_PROCESS', p_id => l_id);
l_result.load(l_id);
```
- Cite: DT pp.29-30 ; DT p.42 "How to persist a SET or LIST DDIC collection" ; DT pp.39-40
- Basis: STATED (`call_report`/`submit_async_report` are illustrative names, not confirmed built-ins)
- VERIFY: Q26 EXTENDS.
- From: G2-41, G2-42, G2-56, G2-52

### KB-TYPE-42 Choosing a mechanism: collection DDICs vs MEM_DB_LIST vs MEM_TAB — CONFLICT on PL/SQL handover
- Fact: Collection DDICs fix MEM_DB_LIST/MEM_TAB problems (cluttered API, missing type validation, easy-to-forget manual memory management). set/list: scope-managed memory, design-time type checks, store/load, PL/SQL via db_list#. map: scope-managed, design-time checks, persistence/PL/SQL only via manual conversion to MEM_DB_LIST or MEM_TAB. MEM_DB_LIST: manual memory, no type checking, store/load, db_list#. MEM_TAB: manual memory, runtime checks, no persistence, tab#. Use collection DDICs when the collection is local, needs no PL/SQL handover or DDIC-field I/O, and no session persistence. CONFLICT: the newer interop section (DT pp.32-36) says lists, maps, sets and records pass directly to PL/SQL via T# types, contradicting the table's PL/SQL column (table likely outdated, INFERRED).
- Cite: DT pp.39-40 "Comparison", "Overview comparison", "Recommendations for using the collection DDICs" ; DT pp.32-36
- Basis: STATED (both sides); which is current INFERRED
- VERIFY: Q25 EXTENDS; Q26 EXTENDS.
- Audit use: info-level finding for MEM_TAB/MEM_DB_LIST in purely local scope.
- From: G2-52, G2-53

### KB-TYPE-43 Generated PL/SQL T# type packages for collections
- Fact: Compiling sources that reference collections generates PL/SQL type packages: `t#list#<elem>`, nested `t#list#<inner>_t_type`, `t#map#<key>#<value>`, `t#set#<elem>`; special characters become `_`; the type is `<package>.t_type`; names of 60+ chars are mangled.
- Avaloq form: `list<text> -> t#list#varchar2_4000` ; `list<obj> -> t#list#obj#_t_obj_id` ; `list<list<text>> -> t#list#t#list#varchar2_4000_t_type` ; `map<text, number> -> t#map#varchar2_4000#number_t_type.t_type`
- Cite: DT pp.32-34, 36 "PL/SQL type names for Avaloq Script collections"
- Basis: STATED
- VERIFY: Q12 EXTENDS; Q01 EXTENDS.
- Audit use: `t#...` names in PL/SQL are generated, not hand-written packages.
- From: G2-45

### KB-TYPE-44 Passing collections/records to PL/SQL
- Fact: Collections and records pass directly to natively imported PL/SQL procedures (`custom_package#.proc(...)`); PL/SQL must declare them IN OUT NOCOPY. A PL/SQL function returning a collection or record cannot be used in a script expression (compile error). T# packages used in PL/SQL must be declared in a script package; for INTF DEF, call a wrapper method in a script package.
- Avaloq form: `procedure fill_custom_list (x_out_list in out nocopy t#list#varchar2_4000.t_type);` ; `custom_package#.fill_custom_list(l_custom_text_list);`
- Cite: DT pp.34-36 "Passing collections from Avaloq Script to PL/SQL procedures", "Restrictions" ; DT p.39
- Basis: STATED
- VERIFY: Q12 CONFIRMS/EXTENDS; Q05 EXTENDS.
- From: G2-46, G2-50, G6-44

---

## B5 Records (Compiler Framework 18.0)

### KB-TYPE-45 Record type definition: package level, optional private
- Fact: Compiler Framework 18.0 adds `[private] type <name> is record ( <field> <type> {, <field> <type>} );`. Fields are read and written with dot notation; the compiler validates types; records work in procedures, functions, variables, constants and DDIC collections. Records can only be defined at package level. `private` hides the type outside the defining script package; otherwise it is visible (doc text says "if defined, it is visible", read as "if not defined" — typo).
- Avaloq form:
```
record_type_definition ::= [ "private" ] "type" type_name "is" "record" "(" field_list ")";
field_list             ::= field_definition { "," field_definition };
field_definition       ::= field_name data_type;
data_type              ::= identifier;

private type t_font is record(
    name    text
   ,size    number
   ,color   text
);
```
- Cite: DT pp.36-38 "Record types in Avaloq Script", "Record type definition"
- Basis: STATED; `data_type ::= identifier` would exclude `id obj_bp`/`list<number>` field types — whether those are allowed is not stated
- VERIFY: Q06 EXTENDS; Q07 EXTENDS; Q31 PARTIAL (`t_` prefix).
- Audit use: record type declared inside a procedure = error.
- From: G2-47, G6-43, G6-13

### KB-TYPE-46 Record variables: same-type assignment only; no null check, no comparison — CONFLICT
- Fact: A record variable can be assigned only from a record of the same type; fields can be set with dot notation. Null checks and =/</> comparisons on records are not supported and give compiler errors. CONFLICT: EXPR p.8 and Language fundamentals p.3 allow = != <> on "record types" (these may mean DDIC record types, not CF-18 records); trust DT p.38 for CF-18 records.
- Cite: DT p.38 "Working with record variables", "Limitations" ; EXPR p.8 ; paged/text/language-fundamentals.txt p.3
- Basis: STATED (both)
- VERIFY: Q27 EXTENDS.
- Audit use: `<record> is null`, `<record> = <record>` = errors.
- From: G2-48, G6-43, G2-20, G2-66

### KB-TYPE-47 Record <-> PL/SQL: T#R# packages
- Fact: Compiling a source defining a record generates package `t#r#<script-package>#<record>` with type `<package>.t_type` (e.g. `t#r#my_script#address.t_type`); records pass to natively imported PL/SQL procedures as IN OUT NOCOPY.
- Avaloq form: `procedure update_active_address (x_address in out nocopy t#r#my_script#address.t_type);`
- Cite: DT pp.34-35 "PL/SQL type names for Avaloq Script compound(record) types"
- Basis: STATED (pattern line prints `t#r<...>` without `#`; example has `t#r#` — use the example)
- VERIFY: Q12 EXTENDS.
- From: G2-49

---

## B6 Collection performance facts

### KB-TYPE-48 Collection assignment copies (deep copy)
- Fact: "All collection variable assignments have copy semantics. So assigning huge collections may have a negative performance impact." Collections are PL/SQL associative arrays; Avaloq recommends considering avoiding collection assignments.
- Cite: DT p.26 "Assigning a collection" ; DT pp.30-31 "Implementation restrictions"
- Basis: STATED
- VERIFY: Q26 EXTENDS.
- Audit use: `l_a := l_b` between collections, especially in loops = performance finding.
- From: G2-36, G2-43, G6-36

### KB-TYPE-49 Casting a list-of field copies; extra copy in some contexts
- Fact: `list(x.field)` / `set(x.field)` copy all values. In direct assignment, argument passing or return there is no intermediate variable (one copy); in other contexts (e.g. inside case) an extra copy happens.
- Avaloq form: `l_list := list(l_doc.link_list); -- copied directly` ; `l_list := case when true list(l_doc.link_list) else list(l_doc_2.link_list) end; -- extra copy` (doc example lacks `then`)
- Cite: DT pp.26-27
- Basis: STATED
- Audit use: repeated casts of the same field in a loop = repeated copies.
- From: G2-37

### KB-TYPE-50 Collection parameters are passed by reference — CONFLICT with "value parameters only"
- Fact: CONFLICT. Declarations p.5 says Avaloq Script supports only value parameters ("local constants"). DT p.27 says collection parameter passing has reference semantics (PL/SQL `in out nocopy`), so a callee can modify a collection passed as input; the change is visible to the caller. Both are stated; collections are the exception.
- Avaloq form:
```
procedure foo( i_list list<number> ) is
begin
  i_list.add(1);
end foo;
-- in bar: foo(l_list); l_cnt := l_list.count;  -- l_cnt becomes 1
```
- Cite: DT pp.27-28 "Passing a collection as an input parameter" ; paged/text/declarations-in-avaloq-script.txt p.5 "Formal parameters"
- Basis: STATED (both)
- VERIFY: Q07 EXTENDS; Q31 PARTIAL (`i_` prefix does not guarantee read-only for collections).
- Audit use: an `i_` collection may be mutated by the callee — record as a side effect.
- From: G2-38, G1-36, G6-16, G6-17, G6-36

### KB-TYPE-51 Returning collections; compiler copy avoidance
- Fact: Returned collections can be assigned or used directly (`get_list.add(1)`). The compiler avoids copies where possible, e.g. no copy when the returned collection is the input parameter and the result is assigned back to the same variable; `concat(b_list, l_list)` needs a copy (and also mutates b_list by reference).
- Avaloq form: `l_list := concat(l_list, b_list); -- no copies necessary` ; `l_list := concat(b_list, l_list); -- copy necessary`
- Cite: DT p.28 "Returning a collection"
- Basis: STATED (b_list mutation INFERRED from reference semantics)
- VERIFY: Q26 EXTENDS.
- From: G2-39

### KB-TYPE-52 list.remv is O(n)
- Fact: list remv shifts later items left; worst case O(n); removing the last element is constant time.
- Cite: DT pp.11-12 "remv"
- Basis: STATED
- VERIFY: Q26 EXTENDS.
- Audit use: remv by value or `remv(pos=>1)` inside a loop = O(n^2) candidate.
- From: G2-32

### KB-TYPE-53 Limit bad use of .store (each call writes to the DB)
- Fact: Use `.store`/`.load(id)` only to pass data to a report or for asynchronous population. PL/SQL interop needs no stored list. Keep local/single-session lists in memory (also in package state within the same script package or report DTM). Avoid repeated `.store` calls, particularly in `on level_xxx` handlers of report layouts: "each call writes to the DB and replaces existing rows". Use `.clear` for in-memory reset; clear the stored version only for business logic, not "garbage collection" (list_xxx tables are truncated regularly).
- Avaloq form: `l_list.store; l_list.add(1); l_list.store; -- Unnecessary`
- Cite: DT pp.29-30 "Limit bad use of .store"
- Basis: STATED
- VERIFY: Q26 CONFIRMS; Q20 EXTENDS.
- Audit use: `.store` in loops or `on level_*`; >1 `.store` on the same variable; `.store` whose id only goes to PL/SQL; `.store(id)` of an empty list as cleanup.
- From: G2-41, G2-62, G6-87

### KB-TYPE-54 Manual memory release for MEM_TAB / MEM_DB_LIST
- Fact: MEM_DB_LIST and MEM_TAB need manual memory management (easy to forget); `obj_tab.remv` releases a MEM_TAB ("often forgotten releasing of memory"); MEM_DB_LIST constructors take `remv_after` to remove the list at end of statement. Collection DDICs are scope-bound and need no release.
- Cite: DT pp.5-7 ; DT pp.39-42
- Basis: STATED
- VERIFY: Q26 EXTENDS.
- Audit use: `with new mem_tab(...)` block without `.remv` before `end with` = leak warning.
- From: G2-54, G2-52, G2-29, G6-86

### KB-TYPE-55 Loop over list fields with `for x in list`, not indexed get
- Fact: With indexed get, looping over n list-field elements costs time proportional to n^2; with the list operation, proportional to n.
- Avaloq form:
```
----WRONG ----
for i in 1 .. doc.trans_list.count loop
  with doc_trans(doc.trans_list(i)) as t do
----CORRECT ----
for t_id in doc.trans_list loop
  with doc_trans(t_id) as t do
```
- Cite: paged/text/hints-and-tips-on-using-avaloq-script.txt pp.4-5 "Use list instead of get to loop over list fields"
- Basis: STATED
- VERIFY: Q26 CONFIRMS; Q27 CONFIRMS; Q37 CONFIRMS.
- From: G1-75

### KB-TYPE-56 ID instead of record: the documented lightweight reference
- Fact: "Using the ID to refer to an instance of an object is lighter and quicker than using a record type." No G2 doc says which data access hops trigger SQL; that field access on an obj_ DDIC equals a query is INFERRED (see hints-and-tips p.6 example of per-attribute selects).
- Cite: DT p.3 ; paged/text/what-are-data-dictionaries.txt p.5 ; paged/text/hints-and-tips-on-using-avaloq-script.txt p.6
- Basis: STATED (lighter/quicker); INFERRED (DB-access per hop)
- VERIFY: Q26 EXTENDS.
- From: G2-25, G2-63, G3-19, G1-B-ADD-01

---

## B7 Documentation errors not to copy

### KB-TYPE-57 Errata in the official type/collection docs
- Fact: Do not copy these official examples literally: set.subtract and set.sym_diff examples repeat the union example; map empty example reads `list.empty<obj_person, text>` (should be map.empty); map cnv_to_text example has `:=_text_text_map.cnv_to_text`; set_from_text example comment refers to l_list; list-field op is `rmv` but MEM_DB_LIST item_list lists `remv`; compatibility table operator column truncated ("<= >"); record `private` text says "if defined, it is visible outside"; T#R# pattern line lacks a `#`; intro diagram caption says DOC_BP/SESSION but code uses mem_doc, and writes `endif`; map keys example `l_text_boolean_map.keysloop`; `case when true list(...)` without `then`; `return booleanis`; PL/SQL type `t#r#it_templ_ddic@address.t_type` with `@`; expression EBNF unary takes `Expression` and `between ... and` conflicts with `and` at Term level; DT p.29 "Passing date to and from PL/SQL" (should be data).
- Avaloq form: `l_map_name_by_person := list.empty<obj_person, text>;` (wrong)
- Cite: DT pp.5-6, 18, 20-23, 25-27, 29, 35-37 ; EXPR pp.6-8 ; paged/text/what-are-avaloq-script-expressions.txt pp.1-2 ; paged/text/language-fundamentals.txt p.3
- Basis: INFERRED (comparing the doc's tables with its examples)
- Audit use: do not encode `list.empty<K,V>` as valid.
- From: G2-64

### KB-TYPE-58 Wrong type claims in secondary notes (metaprompt)
- Fact: These secondary claims are wrong against the official text: `raw` base type; `long` = CLOB; boolean maps to number(1)/char(1); `l_list := null` is a runtime (it is compile-time) error; `list.remv(idx)` removes by index; `list.first`/`.next(i)`/`.cnv_to(T)` exist; set union/intersect/subtract are instance methods; `id doc_order` type; set elements only "hashable scalars" (DDIC types are also legal); map.get returns null if absent (not stated).
- Cite: DT p.1 ; DT p.43 ; DT pp.8-14, 11, 19-21, 26, 31 ; DT pp.7, 30, 32 ; paged/text/what-are-data-dictionaries.txt p.1
- Basis: STATED (official text); the secondary claims come from notes/AVALOQ_SCRIPT_METAPROMPT.md
- VERIFY: Q06 CONTRADICTS (raw, long); Q10 CONTRADICTS (remv, union).
- Audit use: remove these from any prompt or rule set.
- From: G6-25, G6-26, G6-28, G6-30, G6-34, G6-35, G6-38, G6-39, G6-40, G6-41
