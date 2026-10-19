# SECTION C — DATA: DDIC, ACCESSORS, READ/CREATE/MODIFY, ORDERS, WORKFLOWS, DATES (SEC = DATA)

Inputs: verified/G3_verified.md, verified/G4_verified.md (main); G1_verified_partA.md, G1_verified_partB.md, G2_verified.md, G5_verified.md, G6_verified.md (accessor, DDIC, order and commit facts). Effect vocabulary from metaprompt/AVALOQ_DATA_EFFECTS_METAPROMPT.md: READ | CREATE | MODIFY | DELETE | ORDER | SIDE_EFFECT | PURE | UNKNOWN. Cites are relative to `source_text/`. G6 entries audit secondary notes; only their official cites are used here. No verified entry was REJECTED.

## What a model must know first

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

---

## C1 Data dictionaries (DDIC)

### KB-DATA-01 A DDIC is the only way script reaches data; tables are hidden
- Fact: Avaloq Script is like PL/SQL but has no direct access to Oracle tables. Code names the data it reads or writes through a DDIC without knowing where it is stored, so it keeps working when storage changes in a later release.
- Means: every data effect is keyed by DDIC name, never by Oracle table; raw SQL DML in a script package is not normal script.
- Cite: paged/text/what-are-data-dictionaries.txt p.1 "Introduction" ; paged/text/getting-started-with-avaloq-script.txt p.1 "Getting Started with Avaloq Script" ; paged/text/hints-and-tips-on-using-avaloq-script.txt p.3 "Avoid unnecessary database access"
- Basis: STATED
- VERIFY: Q14 PARTIAL — DDIC is the data-access abstraction, not a catalogue; E-Q5 PARTIAL — DDIC to accessor root shown, DDIC to Oracle table hidden; Q12 CONFIRMS (no direct SQL); Q29 EXTENDS (upgrade stability)
- Audit use: entity in the effects map = DDIC name; SQL keywords at statement level in a script package -> finding. SQL fragments do appear in `cond =>` strings of `lookup.*` (see KB-DATA-38).
- From: G3-01, G1-01, G1-02, G6-55

### KB-DATA-02 DDICs reach three layers plus session data
- Fact: Through DDICs, script reaches data on disk in the object layer (OBJ) and order persistence layer (DOC), data in memory in the order memory layer (MEM DOC), and session data such as current time and user ID.
- Means: each DDIC root belongs to exactly one layer: OBJ, DOC, MEM_DOC, or SESSION/other.
- Cite: paged/text/what-are-data-dictionaries.txt p.1 "Introduction"
- Basis: STATED
- Audit use: layer is a required attribute of every accessor fact.
- From: G3-02

### KB-DATA-03 DDIC naming prefixes (prefix -> data kind)
- Fact: DDIC names encode the data they reach. Code table DDICs have the code table's own name (namespaced ones keep the prefix). Base parameter DDICs map both `$` and `.` namespace separators to `<ns>$BASE_PAR_<name>`.
- Avaloq form:

| Prefix | Data reached | Doc examples |
|---|---|---|
| `MEM_DOC_<name>` | order memory layer (MEM DOC) | MEM_DOC_BP, MEM_DOC_STEX |
| `DOC_<name>` | order persistence layer (DOC) | DOC_BP, DOC_STEX |
| `OBJ_<name>` | object layer (OBJ) | OBJ_BP, OBJ_ADDR |
| `DTM_<name>` | datamart, data displayed in a report | DTM_BAL_CHK, DTM_FEE_PILLAR |
| `MEM_MSG_<name>` | AMI messages in memory | MEM_MSG_SIC_L80, MEM_MSG_SWIFT_MT103 |
| `<code-table-name>` | code table data | CODE_LANG, MBA$CODE_AML_THRES_TYPE, MDB$CODE_AML_CLASS_RISK |
| `<ns>$BASE_PAR_<name>` | base parameter and its items | AVQ$BASE_PAR_AGING (for AVQ$AGING), AVQ$BASE_PAR_CCM_IACTIV (for AVQ.CCM_IACTIV) |

- Means: deterministic root classifier. Default effect by prefix: OBJ_/DTM_/code table/BASE_PAR/DOC_ fields = READ; MEM_DOC_ = order in progress (READ, or MODIFY of the order on `set`).
- Cite: paged/text/what-are-data-dictionaries.txt pp.3-4 "DDIC naming conventions"
- Basis: STATED (table); INFERRED (default effect per prefix)
- VERIFY: Q14 EXTENDS; Q02 PARTIAL (namespaces as `<ns>$`); Q31 EXTENDS; Q09 PARTIAL (code table DDIC of the same name)
- Audit use: name normaliser must accept both `$` and `.` in base parameter names. In script code DDIC names appear in lower case (`obj_bp`).
- From: G3-14, G3-15, G3-16

### KB-DATA-04 One OBJ DDIC per object type; three DDICs per object type
- Fact: There is one OBJ-layer DDIC per object type (BP -> `obj_bp`, country -> `obj_country`). Because objects are created or modified with static data orders, an object type such as BP has three DDICs: `obj_bp` (object on disk), `mem_doc_bp` (in-memory static data order for BPs), `doc_bp` (stored static data orders for BPs).
- Means: `obj_bp...` = READ of the BP object; `mem_doc_bp...` = an ORDER context for BP, not a direct object write.
- Cite: paged/text/what-are-data-dictionaries.txt p.1 "Introduction" (rows "Static data orders")
- Basis: STATED
- VERIFY: Q08 PARTIAL (obj_bp is the root name; call form on other pages, KB-DATA-27); E-Q2 PARTIAL (objects changed via static data orders)
- From: G3-03, G3-05

### KB-DATA-05 Order DDICs exist per business type and per layer
- Fact: Order DDICs differ by the order's business type and layer: for business type stex, `mem_doc_stex` reaches order data in memory and `doc_stex` reaches order data on disk. The suffix is the business type (btt) defined in META_TYP.
- Means: root `mem_doc_<btt>` / `doc_<btt>` -> entity ORDER of business type <btt>.
- Cite: paged/text/what-are-data-dictionaries.txt p.1 "Introduction" (row "Booking orders") ; paged/text/what-is-a-business-type.txt p.1 "What is a business type"
- Basis: STATED
- VERIFY: Q15 PARTIAL/EXTENDS
- From: G3-04, G3-54

### KB-DATA-06 Other important DDIC families
- Fact: Besides object and order DDICs, the important DDICs for customization are datamarts (reporting), message DDICs (e.g. SIC, SWIFT), code table DDICs and base parameter DDICs.
- Cite: paged/text/what-are-data-dictionaries.txt p.1 "Introduction"
- Basis: STATED
- From: G3-06

### KB-DATA-07 A DDIC = fields + methods + optional constructor
- Fact: A DDIC defines data fields (what script can access), methods (operations script can perform on that data) and optionally a constructor used to create new orders.
- Means: a reference into a DDIC is a field (READ, or MODIFY when assigned), a method (effect per method) or `new` (ORDER create).
- Cite: paged/text/what-are-data-dictionaries.txt p.1 "Looking at a DDIC"
- Basis: STATED
- VERIFY: Q14 EXTENDS
- From: G3-07

### KB-DATA-08 Navigator sections, inheritance and the legacy term "business object type"
- Fact: The DDIC Navigator has sections Parent Business Object Types (inherited DDICs), Constructor List (only MEM DOC DDICs), Field List, Method List, Obsolete (optional) and Hidden (inherited fields this DDIC overrides). A DDIC inherits all fields and methods of its parents recursively (DOC_PAY has almost 20 parents, including DOC); script does not need to know the level a member comes from. "Business object type" in the Navigator is a legacy term the doc says to ignore; it means DDIC.
- Means: attribute resolution walks the parent DDIC list; an inherited member is not "unknown"; a Hidden field resolves to the child's definition.
- Cite: paged/text/what-are-data-dictionaries.txt pp.2-3 "Looking at a DDIC" (table "Navigator screen section")
- Basis: STATED
- VERIFY: Q14 EXTENDS; Q14/Q15 PARTIAL (terminology): AVALOQ_AUDIT_METAPROMPT lists "business object types" as DDIC content; in the docs it is a legacy name for a DDIC itself (object types live in CODE_OBJ_TYPE, KB-DATA-79)
- From: G3-09, G3-10, G3-11

### KB-DATA-09 Field List columns; fields can take parameters
- Fact: Each field shows name, data type, allowed operations, its parameters (indented, mandatory ones marked "(mandatory)"), the DDIC it was inherited from and a description. Screenshot columns: Field/Parameter Name, Field/Parameter Type, Size, Indexed, Operations, Inherited From, Default Value, Description. Example: `has_override (parameters)`, boolean, get, with mandatory `override` ("id of database table code_override") and optional `signt` (text); has_msg and has_postit are also parameterised boolean get fields.
- Means: `field(arg)` is still a field READ, not a method call.
- Cite: paged/text/what-are-data-dictionaries.txt p.3 "Looking at a DDIC" (row "Field List"; screenshot PDF p.3)
- Basis: STATED (text and screenshot); INFERRED that the example DDIC is a MEM_DOC one (it has `id` of type "id of mem_doc")
- Audit use: validator can check that mandatory field parameters are supplied.
- From: G3-12, G3-13

### KB-DATA-10 DDIC field base types
- Fact: DDIC fields are typed like variables: text (up to 4000 characters), number (integer or real), date (date and time), long (up to 32,000 characters), boolean ("+" = true, "–" = false).
- Cite: paged/text/what-are-data-dictionaries.txt p.4 "DDIC fields"
- Basis: STATED
- From: G3-18

### KB-DATA-11 ID types vs record (DDIC) types
- Fact: An ID-type field holds only the primary key (name ends in `_id`, Navigator type "id of <table-name>", e.g. `bank_bp_id` = "id of obj_bp"); IDs also identify code table records (e.g. CODE_LANG). A record-type field points to the whole record and allows reading its fields and calling its methods (e.g. `bank_bp`, type obj_bp). IDs are "lighter and quicker" and used mainly to pass references to other code such as PL/SQL. Declaration syntax `id [table] ident`; a type name alone (`obj_country`) is a record type. ID types are sometimes called reference types, DDIC types object types or business object types.
- Avaloq form: `IdType = id [ table ] ident .` ; `i_country_id id obj_country` vs `i_country obj_country`
- Means: `x.bank_bp_id` = key value only (READ of one field); `x.bank_bp.<attr>` = navigation into OBJ_BP (READ of a second entity).
- Cite: paged/text/what-are-data-dictionaries.txt p.5 "DDIC fields" (rows "ID types", "Record types") ; paged/text/data-types.txt pp.3-4 "Business-oriented data types"
- Basis: STATED
- VERIFY: Q08 EXTENDS/CONFIRMS; E-Q1 PARTIAL (only "lighter than record", nothing on caching); Q26 EXTENDS
- Audit use: paired fields `<f>`, `<f>_a`, `<f>_id` refer to one attribute family (screenshot: bank_bp / bank_bp_a / bank_bp_id, all "get").
- From: G3-19, G2-25, G2-26

### KB-DATA-12 Operations column: get / set / count / list / do / add
- Fact: In the Navigator, simple fields show "get" (read) and/or "set" (write); list fields show "count" / "list" (with or without "get"); every method shows "do"; the `new` constructor shows "add". Whether `set` exists depends on the field, not only on the layer: DOC_PAY fields and fields inherited from obj are "get" only; `abbr`/`abbr_a` are "get, set"; in MEM_DOC_PAY ID/simple fields (curry_id, dispo_bank_a) are "get, set" but record-type fields (compo_cf, curry, dispo_bank) are "get" only.
- Avaloq form:

| Operation | Member kind | Effect label |
|---|---|---|
| get | simple field | READ |
| set | simple field | MODIFY (of the DDIC's entity: an order when MEM_DOC) |
| count, list | list field | READ |
| do | method | per method (see C11) |
| add | `new` constructor | ORDER (create) |

- Cite: paged/text/what-are-data-dictionaries.txt pp.5-7 "Simple DDIC fields", "List DDIC fields", "DDIC methods", "DDIC constructors" (screenshots PDF pp.2, 3, 5, 6, 7)
- Basis: STATED (operation values, from screenshots); INFERRED (effect labels; any layer-wide get/set rule)
- VERIFY: Q14 EXTENDS; E-Q2 PARTIAL (attribute writes are DDIC "set" operations); E-Q5 PARTIAL
- Audit use: assignment to a field whose DDIC operations lack "set" is a compile-error candidate.
- From: G3-A01, G3-21

### KB-DATA-13 Rule-calculated fields have a companion `_a` flag
- Fact: Fields whose value rules can calculate appear twice: the value field (e.g. `abbr`, text, size 20, get, set) and a boolean `abbr_a` (get, set) telling whether the value was calculated automatically. In the screenshot both take parameters.
- Means: `<f>_a` is metadata of `<f>`; same attribute family in effect maps.
- Cite: paged/text/what-are-data-dictionaries.txt pp.5-6 "Simple DDIC fields"
- Basis: STATED
- From: G3-22

### KB-DATA-14 Obsolete DDIC fields: compiler warning now, de-release later
- Fact: An obsolete DDIC field will be de-released in a future release; compiling code that uses it gives a warning naming the substitute. Avaloq recommends replacing it as soon as the warning appears. MEM_DOC_PAY examples: curry_id -> asset_id, curry -> asset_id, compo_cf -> stord_compo_cf_id, dispo_bank -> dispo_bank_bp_id, dispo_bank_a -> dispo_bank_bp_a; obsolete fields carry "(obsolete)" in the name. Task 923 can filter fields by Is obsolete, Is indexed, Is list, Is calculated.
- Cite: paged/text/what-are-data-dictionaries.txt p.6 "Obsolete DDIC fields" (screenshot PDF p.6) ; p.2 "Looking at a DDIC" (task template screenshot)
- Basis: STATED
- VERIFY: Q27 CONFIRMS/EXTENDS; Q29 EXTENDS
- Audit use: upgrade-safety rule: flag obsolete DDIC fields with their substitute.
- From: G3-23, G3-A04

### KB-DATA-15 DDIC methods are procedures (DOC_PAY example)
- Fact: A DDIC method performs an action and corresponds to a procedure. DOC_PAY lists four methods on payment orders in DOC: `attach_postit` (adds a post-it to an order), `discard_dir_msg` (discards an unsent direct message), `do_wfc_action` (executes a workflow action), `send_dir_msg` (sends a direct message). CONFLICT: the text spells the second method `discard_dir_msg`, the screenshot `discd_dir_msg`; the screenshot describes both message methods as FastSIC direct messages.
- Means: attach_postit -> MODIFY(order) + lock; do_wfc_action -> ORDER; send_dir_msg / discard_dir_msg -> SIDE_EFFECT (message).
- Cite: paged/text/what-are-data-dictionaries.txt p.6 "DDIC methods" (screenshot PDF p.6)
- Basis: STATED (methods, descriptions); INFERRED (effect labels)
- VERIFY: E-Q3 PARTIAL; E-Q6 PARTIAL
- Audit use: take exact method names from a DDIC export, not from prose.
- From: G3-24

### KB-DATA-16 Constructor `new` exists only in MEM DOC DDICs
- Fact: A constructor is a special method that creates a new in-memory data structure, e.g. a new order; other methods access existing data. Constructors create new objects (via new static data orders) and initiate financial transactions (via booking orders). There is only one kind, `new`, and it appears only in MEM DOC DDICs (Constructor List is missing otherwise).
- Means: `new mem_doc_<x>(...)` = ORDER (create); object CREATE happens only when that order is finalised (KB-DATA-48).
- Cite: paged/text/what-are-data-dictionaries.txt p.7 "DDIC constructors" ; p.3 (row "Constructor List")
- Basis: STATED
- VERIFY: E-Q2 PARTIAL / E-Q3 PARTIAL — creation goes through a MEM_DOC `new` constructor, not a direct insert
- From: G3-25

### KB-DATA-17 DDIC IDs in the Navigator; task 923 shows a DDIC
- Fact: Task "Avaloq Script Data Dictionary" (task ID 923; keyword "923." or "ddic"; template .DEFAULT; layout "DDIC – Default Layout (SCREEN)"; Table Name e.g. `doc_pay`) shows a DDIC's fields, methods and constructors in the Navigator. The header shows each DDIC with numeric ID and description: "Business Object Type doc_pay (ID 25)" = Payment Order, "Business Object Type mem_doc_bp (ID 11)" = BP Order in Memory. The template has an Export button; its file format is not described.
- Cite: paged/text/what-are-data-dictionaries.txt p.2 "Looking at a DDIC", p.7 "How to open a DDIC" (screenshots PDF pp.2, 7)
- Basis: STATED (screenshots); INFERRED that the numeric IDs may differ per installation
- VERIFY: Q14 PARTIAL (viewer exists; export format not documented)
- Audit use: key a DDIC index by name, keep ID and description as metadata.
- From: G3-08, G3-A05

### KB-DATA-18 Runtime DDICs vs constant DDICs
- Fact: Many DDICs are generated at runtime and vary by context (e.g. the business type of the current order). A constant DDIC is generated at compile time from DSL source files (e.g. code tables holding object keys, additions and classifications) and is the same in every context.
- Cite: paged/text/what-are-data-dictionaries.txt p.8 "Constant DDICs"
- Basis: STATED
- VERIFY: Q24 PARTIAL; Q14 EXTENDS
- Audit use: constant-DDIC references can be resolved from DSL sources in the corpus; runtime DDICs need the DDIC export.
- From: G3-30

### KB-DATA-19 Object extensions have their own DDICs; `extn` record
- Fact: Additions, classifications and keys are accessed through separate DDICs (topic "Using DDICs to access object extensions", not in the folder). The Hidden-section example shows fields inherited from obj, all "get": bu (obj_bp), bu_id, close_date, extn (record type obj_extn, "Data extensions"), open_date. An official ATF example reads `i_doc.asset.extn.ass_type`; another uses `btt.cont.obj_extn.cont_type_id`.
- Means: `.extn.<x>` = READ of an object extension value.
- Cite: paged/text/what-are-data-dictionaries.txt p.4 "DDIC naming conventions", p.3 (Hidden screenshot) ; layout/04-test-framework/pages/02c_Implementing_the_construction_tests.txt pp.3-5 "Store static data...", "Create modular and stateless code"
- Basis: STATED (fields, examples); INFERRED (that `extn` is the general entry point for extensions; the `btt.` path meaning)
- VERIFY: Q16 PARTIAL
- From: G3-17, G3-A06, G5-82, G5-80

---

## C2 Data access layers

### KB-DATA-20 Three layers: MEM DOC, DOC, OBJ
- Fact: Objects and orders are accessed through three layers: order memory layer (MEM DOC, orders held in memory while processed), order persistence layer (DOC, orders on disk), object layer (OBJ, objects on disk, sometimes called the kernel layer). The diagram shows MEM DOC exchanging data both ways with DOC and with OBJ.
- Cite: paged/text/what-are-the-data-access-layers.txt pp.1-3 "Application architecture"
- Basis: STATED
- From: G3-31

### KB-DATA-21 MEM DOC holds unsaved order changes
- Fact: MEM DOC holds orders being modified. Opening an order form loads data from the database into it; changes stay only there until a workflow action saves them to disk or they are discarded.
- Means: `set` on a `mem_doc_*` field = MODIFY of an order in memory; persisted only via a workflow action (ORDER).
- Cite: paged/text/what-are-the-data-access-layers.txt p.2 "Data access layers" (row "Order memory layer")
- Basis: STATED
- From: G3-32

### KB-DATA-22 DOC is effectively read-only (exception: post-it)
- Fact: DOC holds saved orders, completed or awaiting processing; to continue processing an order is loaded into MEM DOC. DOC "can be thought of as" read-only; "one or two exceptions" exist, e.g. adding a post-it to an order with Avaloq Script without loading it.
- Means: `doc_*` field = READ; `doc_*.attach_postit` = documented write exception (MODIFY of order).
- Cite: paged/text/what-are-the-data-access-layers.txt p.2 (row "Order persistence layer (DOC)")
- Basis: STATED
- From: G3-33

### KB-DATA-23 OBJ is effectively read-only; objects are modified via an order
- Fact: OBJ holds saved objects and kernel data. To modify an object you create an order, which loads the object into MEM DOC where it can be modified. OBJ "can be thought of as" read-only with "one or two rare exceptions" where an object is modified directly; the exceptions are not named. (The doc's wording "modified directly in the order layer without first being loaded into memory" is apparently a slip for the object layer.)
- Means: `obj_*` access = READ; object MODIFY = ORDER (static data order) + finalisation; a `set` on an `obj_*` field is unusual and needs review.
- Cite: paged/text/what-are-the-data-access-layers.txt p.3 (row "Object layer (OBJ)") ; paged/text/what-are-orders.txt p.1 "What are orders"
- Basis: STATED
- VERIFY: E-Q2 CONTRADICTS the metaprompt's flat "attribute write -> MODIFY" on objects (writes go through an order); E-Q1 PARTIAL (obj_bp reads OBJ on disk; caching not stated); Q18 CONFIRMS
- From: G3-34, G6-64

### KB-DATA-24 Which layer a DDIC view shows; read during an open order
- Fact: Parameterisation > Data Dictionary on an open order shows the MEM DOC DDIC including unsaved values; on an orderbook entry of a non-open order, the DOC DDIC; on an object, the OBJ DDIC unless an order for that object is open, then the MEM DOC DDIC.
- Means: an OBJ read of an object while its modify order is open returns the stored, not the pending, values; read-after-write inside an order must go through MEM_DOC.
- Cite: paged/text/what-are-data-dictionaries.txt p.7 "How to open a DDIC"
- Basis: STATED (UI behaviour); INFERRED (that script reads behave the same)
- From: G3-27

### KB-DATA-25 Write lock while a modify order is open
- Fact: To modify an object, a static data order is opened and the object's data is read from OBJ into memory. The object in OBJ is write-locked (others can read, not write) until the order is finalised and saved, or discarded. At finalisation the data is saved to OBJ, the lock released and the order saved to DOC.
- Avaloq form: diagram text "The object in the object layer is locked (read-only access) until you finish processing the order"
- Means: opening a modify order = ORDER + lock; many such orders in a loop hold many locks.
- Cite: paged/text/what-are-the-data-access-layers.txt p.5 "Modifying an object"
- Basis: STATED
- VERIFY: Q26 EXTENDS (locking as a concurrency concern)
- From: G3-37

---

## C3 Accessor syntax

### KB-DATA-26 Data access expression = dot path from a DDIC root
- Fact: Data access expressions read data in memory or in the database through DDICs. Elements are separated by dots: the root names the DDIC, each next element is a field of the DDIC reached so far; record-typed fields lead to the next DDIC. Navigation walks "up the object tree" (position -> container -> BP), the reverse of the English phrasing. Dot notation is the only field-access notation (`#` occurs only inside method names).
- Avaloq form: `obj_pos.cont.bp.name` (obj_pos root; cont -> obj_cont; bp -> obj_bp; name = text field) ; also `cont.pos_list`, `p.asset.maturity_date`, `doc.meta_typ_id`, `m.msg.asset.issue_date.val_date`
- Means: READ; each hop through a record field into an `obj_*` DDIC is a READ of another entity.
- Cite: paged/text/what-are-avaloq-script-expressions.txt p.2 "Data access expressions" ; paged/text/avaloq-script-expressions.txt pp.1-2 ; paged/text/language-fundamentals.txt p.2 ; paged/text/hints-and-tips-on-using-avaloq-script.txt pp.3-6
- Basis: STATED
- VERIFY: Q08 CONFIRMS; Q14 EXTENDS
- Audit use: parser `designator := root ('.' field)*`; resolve each hop against the DDIC index. `obj_bp.pers.addr.city` (secondary note) is not attested: addresses are separate Address objects.
- From: G2-03, G2-04, G1-89, G6-56

### KB-DATA-27 DDIC type cast `T(v)`, e.g. `obj_bp(id)` — not checked by the compiler
- Fact: `T(v)` interprets v as (an ID of) a DDIC of type T so its fields and methods can be used. It applies if v is scalar, or v is a DDIC value and T extends v's static type; "neither of these constraints is checked by the compiler (which is a possible source of errors)". The doc even casts a number.
- Avaloq form: `obj_bp(l_bp_id).ref_curry.name` (l_bp_id id obj_bp) ; `obj_bp(l_obj).ref_curry.name` (obj) ; `obj_bp(l_val).ref_curry.name` (number) ; also `doc_trans(t_id)`, `mem_doc_collect(b_id)`, `with obj_bp(i_obj) as obj do`
- Means: `obj_bp(k).attr` = READ of entity OBJ_BP, key `k`, attribute `attr`. The key may be LITERAL or SYMBOLIC (parameter/variable).
- Cite: paged/text/avaloq-script-expressions.txt pp.4-5 "DDIC type casts" ; paged/text/hints-and-tips-on-using-avaloq-script.txt pp.4-6 ; paged/text/coding-conventions.txt p.3
- Basis: STATED (cast semantics); INFERRED (that cast + field loads the record)
- VERIFY: Q08 CONFIRMS — `obj_bp(id).field` is the documented lookup-by-ID syntax; Q27 EXTENDS — casts unchecked
- Audit use: parser: `ident '(' expr ')'` where ident is a DDIC name = cast, not a call. Flag casts whose argument has a different ID/DDIC type (silent wrong data).
- From: G2-13, G6-31, G1-46, G1-89

### KB-DATA-28 A function returning a DDIC can be the root
- Fact: If a function returns a DDIC value, the call can be the root of a data access expression. A parameterless function is called by its bare name.
- Means: `f(x).attr` = effects of `f` + READ of the returned DDIC's field.
- Cite: paged/text/avaloq-script-expressions.txt pp.3-4 "References and function calls"
- Basis: STATED (DDIC root); INFERRED (bare zero-argument call, from examples)
- VERIFY: Q08 EXTENDS
- From: G2-12, G2-11

### KB-DATA-29 Root availability depends on context; `mem_doc` = order in memory
- Fact: Avaloq Script always runs in a context that defines which business types are available as roots. `mem_doc.order_type_id` reads the order type (an ID into CODE_ORDER_TYPE) of the order loaded in memory. A bare root like `obj_pos.` is valid only where the context provides it; in a script package you start from a variable, parameter or cast.
- Avaloq form: `mem_doc.order_type_id`
- Means: implicit roots (`mem_doc`, ...) are context-dependent; `mem_doc.*` = READ of the in-memory order.
- Cite: paged/text/avaloq-script-expressions.txt p.2 ; paged/text/what-are-avaloq-script-expressions.txt p.3
- Basis: STATED (context rule); INFERRED (that `mem_` generally means in-memory)
- VERIFY: Q08 EXTENDS; Q05 PARTIAL
- From: G2-05, G6-56

### KB-DATA-30 Paths must end in a scalar
- Fact: Data access expressions must always result in a scalar type (base type or ID type). Using a non-scalar type as an expression may yield null instead of the expected data.
- Means: a path ending in a record field used as a value is a silent-null bug, not a READ of the record.
- Cite: paged/text/avaloq-script-expressions.txt p.3 (Note)
- Basis: STATED
- VERIFY: Q08 CONFIRMS; Q27 EXTENDS
- Audit use: flag a comparison/assignment of a record-typed path to a scalar; exceptions: assignment to a DDIC-typed variable, cast.
- From: G2-08, G6-57

### KB-DATA-31 Keyword segments in a path are quoted
- Fact: If part of a data access expression is a keyword, it must be enclosed in single or double quotes.
- Avaloq form: `node."as".val_nr`
- Means: after `.`, a quoted token is an identifier segment, not a string literal.
- Cite: paged/text/avaloq-script-expressions.txt p.3 (Note)
- Basis: STATED
- VERIFY: Q06 EXTENDS
- From: G2-09, G6-58

### KB-DATA-32 Parameterised fields: `class('x')`, `class_id('x')`
- Fact: Fields can take arguments. Accessing a DDIC field directly is always faster than going through the underlying table: use `class_id('ass_type')` instead of `class('ass_type').id` (one level shorter). The BETTER side compares with `mdb_asset.fwd_fx` (or a raw id `12345 /*fwd_fx*/`).
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
- Means: READ (parameterised field); the argument is part of the access key.
- Cite: paged/text/hints-and-tips-on-using-avaloq-script.txt p.3 "Avoid unnecessary database access"
- Basis: STATED (class_id point); INFERRED (preference for `mdb_*` constants over `lookup.code`/intl_id strings)
- VERIFY: Q08 EXTENDS; Q09 CONFIRMS/EXTENDS; Q26 CONFIRMS
- Audit use: rule `.class(x).id` / `.class(x).intl_id = '<lit>'` -> `.class_id(x) = <constant>`.
- From: G1-73, G6-59

### KB-DATA-33 List fields: operations, restrictions, collection casts
- Fact: A DDIC field can hold a list of values of any type; allowed operations are per field. Restrictions: lists can only be returned by DDIC functions, must be used immediately in a `for` loop, and can be saved, referenced, edited or passed only after casting to a collection DDIC; tables LIST_CHAR, LIST_DATE, LIST_NUMBER cannot be used in script. `list(<list of field>)` / `set(...)` copy the values; changing the copy does not change the field. Screenshot examples: `dflt_ref_by_obj_list` ("list of id of database table obj", get, count, list); `doc_block_list` (parameters ref_date, block_id; "list of doc_block"; count, list).
- Avaloq form:

| Operation | Description | Effect |
|---|---|---|
| list | iterate in `for ... loop`, or cast to a collection | READ |
| count | number of items | READ |
| get | one item, index 1..count | READ |
| set | set one item, index 1..count | MODIFY |
| clear | remove all items | MODIFY |
| add | append at end (via a with statement) | MODIFY |
| rmv | remove item at position | MODIFY |
| remv_item | remove by content (param item_nr) | MODIFY |

  Example: `set(i_doc.link_list).count` (count of unique linked documents); `mem_doc.postit_list.add(topic => "Approval", text => "Order exceeds AML threshold")` (diagram).
- Means: list READ for list/count/get; MODIFY of the owning entity for set/clear/add/rmv/remv_item; a cast is PURE copy (performance note).
- Cite: paged/text/data-types.txt pp.4-5 "List fields", pp.26-27 "Casting a list of field to a collection" ; paged/text/what-are-data-dictionaries.txt pp.5-6 "List DDIC fields" ; paged/text/hints-and-tips-on-using-avaloq-script.txt p.5 "List handling in Avaloq Script" ; paged/text/avaloq-script-expressions.txt pp.5-6 ; paged/text/what-are-avaloq-script-expressions.txt p.2 (diagram)
- Basis: STATED; effect column INFERRED
- VERIFY: Q08 CONFIRMS/EXTENDS; Q17 EXTENDS (LIST_* tables forbidden). CONFLICT (doc-internal): list-field op is `rmv` (data-types p.5) but MEM_DB_LIST item_list lists `remv`; the diagram caption names DOC_BP and SESSION while the code shows `mem_doc`.
- From: G2-27, G3-20, G1-76, G2-14, G2-37, G6-42, G2-06

### KB-DATA-34 Loop over list fields with `for x in list`, not indexed `get`
- Fact: With `get` the time to loop over n elements is proportional to n², with `list` to n.
- Avaloq form:
```
----WRONG ----
for i in 1 .. doc.trans_list.count loop
  with doc_trans(doc.trans_list(i)) as t do
  ...
----CORRECT ----
for t_id in doc.trans_list loop
  with doc_trans(t_id) as t do
```
- Means: READ inside loop; each `doc_trans(...)` cast is a READ keyed by the loop variable.
- Cite: paged/text/hints-and-tips-on-using-avaloq-script.txt pp.4-5 "Use list instead of get to loop over list fields"
- Basis: STATED
- VERIFY: Q26 CONFIRMS; Q27 CONFIRMS
- From: G1-75

### KB-DATA-35 `with <expr> as <alias> do ... end with;`
- Fact: `with` defines an alias for a long designator or a DDIC instance; the docs say it improves performance "for memory DDICs" and makes code more legible. `with` alone does not remove repeated selects on OBJ rows when writing calls sit in between (KB-DATA-41).
- Avaloq form: `with obj_bp(i_obj) as obj do` ; `with mem_doc_collect( b_id ) as collect do collect.add_postit( i_val_1, i_val_2 ); end with;` ; `with m.msg.asset as a do`
- Means: the alias binds to the DDIC (and key) of the expression; accesses through the alias are accesses to that entity.
- Cite: paged/text/hints-and-tips-on-using-avaloq-script.txt p.4 "Use with" ; paged/text/coding-conventions.txt p.3 ; layout/02-techbase/02_05_Language_elements_used_in_Avaloq_Script.txt (secondary)
- Basis: STATED
- VERIFY: Q08 EXTENDS; Q26 CONFIRMS
- From: G1-46, G1-74, G6-47

### KB-DATA-36 Code values: `code_x.<entry>_id`, `mdb_*`, `meta_typ.*`
- Fact: Every code table has a DDIC of the same name and its entries are fields: `code_medium.phone_id` = ID of entry phone, `code_medium.phone.name` = that entry's name. Examples also use constant packages `mdb_asset.fwd_fx`, `mdb_meta_typ.stex`, `meta_typ.bp_id`, and code values such as `code_addr_type.postal_id`, `code_salut.mr`. Code-table rows can be read by `code_it_person_gen.lookup(i_person_idx).birth_date` or bound with `with rm$code_it_cont_name(id) as cn do`.
- Avaloq form: `code_medium.phone_id` ; `code_medium.phone.name` ; `case doc.meta_typ_id when mdb_meta_typ.stex then ...`
- Means: READ of a code table (constant value; no business data effect).
- Cite: paged/text/avaloq-script-expressions.txt pp.2-3 "Data access expressions" ; paged/text/coding-conventions.txt p.3 "Statements" ; paged/text/hints-and-tips-on-using-avaloq-script.txt pp.3, 9 ; layout/04-test-framework/pages/02b_Test_sources.txt pp.5-6 "Example test implementation" ; layout/04-test-framework/pages/02c_Implementing_the_construction_tests.txt pp.3-4
- Basis: STATED (forms); INFERRED (that `mdb_*` packages hold code-table ID constants named by intl_id)
- VERIFY: Q09 CONFIRMS/EXTENDS
- From: G2-07, G1-88, G1-44, G5-74, G5-80

### KB-DATA-37 SESSION: always-present singleton DDIC
- Fact: SESSION and LOOKUP are special DDICs, always available, unique instances per Avaloq session (not importable packages; official code uses `session.*` with no import). SESSION gives current system time, the logged-in user ID, and methods such as `raise_ui_err` (UI error, e.g. invalid data during order validation) and commit / rollback. Attested members: `session.today` (e.g. `c_curr_date constant date := session.today`), `session.debug(msg)`, `raise_ui_err`. Field name `user_id` and members `user_name`, `is_gui`, `is_batch` (from a secondary note) are not attested.
- Means: `session.today` / user ID = READ (session); `session.debug` = SIDE_EFFECT (log); `session.raise_ui_err` = error signalling; `session.commit`/`rollback` = SIDE_EFFECT (transaction, KB-DATA-67).
- Cite: paged/text/what-are-data-dictionaries.txt pp.7-8 "Special DDICs: SESSION and LOOKUP" ; paged/text/declarations-in-avaloq-script.txt pp.3, 6
- Basis: STATED
- VERIFY: E-Q4 PARTIAL; Q10 PARTIAL; Q11 PARTIAL
- Audit use: do not flag a missing `import session`; treat `import session;` as suspicious (unsupported).
- From: G3-28, G6-71, G1-88

### KB-DATA-38 LOOKUP: object search, code lookup, date arithmetic
- Fact: LOOKUP finds objects, code tables and other information. Attested members: `lookup.date(...)` (date arithmetic), `lookup.obj_list` (find objects by looping over a list matching its parameters), `lookup.asset('novn')`, `lookup.asset_id(key)`, `lookup.code(tab_name =>, val =>, fld_list =>, cond =>)` (returns an ID, `id table <code table>`; `fld_list` names the match field; `cond` is an SQL-notation condition string), `lookup.code_list(...)`, `lookup.class_id(classif =>, class =>)`. `lookup.bp`, `lookup.bp_id`, `lookup.cont`, `lookup.cont_id` are not attested. The doc calls `lookup.code` "relatively expensive" and marks it INEFFICIENT in comparisons (prefer constant DDICs).
- Avaloq form:
```
lookup.date(''today +3w'')
return lookup.code(
    tab_name => 'wfc_status'
   ,val      => i_intl_id
   ,fld_list => 'intl_id'
   ,cond     => 'meta_typ_id = ' || meta_typ.bp_id
  );
c_eu_id number := lookup.code('obj_country_v', 'EU', 'KEY_SYM');
for id in lookup.code_list('id','rm$code_it_cont_name', 'activ is not null') loop
```
- Means: READ (query); `lookup.obj_list` is a list READ (query-in-loop candidate).
- Cite: paged/text/what-are-data-dictionaries.txt p.8 "Special DDICs: SESSION and LOOKUP" ; paged/text/hints-and-tips-on-using-avaloq-script.txt pp.3, 9-10 "Use of deterministic" ; paged/text/declarations-in-avaloq-script.txt pp.2, 6 ; layout/04-test-framework/pages/02b_Test_sources.txt pp.5-6 ; layout/04-test-framework/pages/02c_Implementing_the_construction_tests.txt pp.3-4
- Basis: STATED
- VERIFY: Q08 EXTENDS; Q10 PARTIAL; Q09 CONTRADICTS (a secondary example using `lookup.code` to return an FX `rate`); Q12 PARTIAL (SQL condition strings); Q26 CONFIRMS
- Audit use: flag `lookup.code` results used as non-ID values (assignment to `number` is fine, official example does it); flag string-concatenated `cond =>` (code-injection risk named in the TOC).
- From: G3-29, G6-72, G1-82, G1-88, G5-74, G5-80

---

## C4 How data is READ

### KB-DATA-39 Read effects by construct
- Fact: Reads come from: fields with operation get / count / list on any DDIC; OBJ and DOC layer DDICs (read-only layers); code table, DTM and base-parameter DDICs; `session` fields; `lookup.*`. ID fields return only the key; record fields and casts give access to the whole record.
- Means: READ, entity = DDIC root (after cast or navigation), key = cast argument, attribute = path; no data change.
- Cite: paged/text/what-are-data-dictionaries.txt pp.1, 4-8 ; paged/text/what-are-the-data-access-layers.txt pp.2-3
- Basis: STATED (layers, operations); INFERRED (that every such access is a READ effect)
- From: G3 cross-check summary (G3-02, G3-14, G3-33, G3-34, G3-A01)

### KB-DATA-40 Compiler translates attribute reads into selects on the backing table
- Fact: The doc shows `obj_bp(i_obj)` attribute reads compiled to PL/SQL as `select bu_id from obj_bp where id=i_obj`, one select per attribute when calls that may write come between them. The DDIC attributes map to same-named columns of table `obj_bp`, keyed by `id`.
- Avaloq form: "select bu_id from obj_bp where id=i_obj Call put_line with the returned value select acc_type_id from obj_bp where id=i_obj"
- Means: an OBJ field READ costs a DB round trip unless merged (KB-DATA-41).
- Cite: paged/text/hints-and-tips-on-using-avaloq-script.txt p.6 "Optimizing accesses to the same database table"
- Basis: STATED (shown translation); INFERRED (that the same-name mapping holds in general)
- VERIFY: Q12 EXTENDS; Q14 EXTENDS; Q17 EXTENDS
- From: G1-B-ADD-01

### KB-DATA-41 Reads of one row are merged unless a possibly-writing call sits between them
- Fact: Several attribute reads on the same DDIC instance (`obj.bu_id`, `obj.acc_type_id`, `obj.au_sa_bp_id`) could be one select, but because `mba$dwh.put_line` "might modify the value", the compiler emits three selects ("three database round trips where we only needed one"). The IDE shows the ASMD info marker "Missed performance optimization opportunity" ("Feature call with potential side effect 'mba$dwh.put_line' prohibits reuse of table access via 'obj'"). Fixes: mark the callee `db_side_effect_free` (if it truly is) or extract the attributes to locals first.
- Avaloq form:
```
with obj_bp(i_obj) as obj do
  mba$dwh.put_line(mba$dwh.obj#text('id', obj));
  mba$dwh.put_line(mba$dwh.obj#text('bu_id', obj.bu_id));
  mba$dwh.put_line(mba$dwh.code#text('acc_type_id', obj.acc_type_id, 'code_acc_type'));
  mba$dwh.put_line(mba$dwh.obj#text('au_sa_bp_id', obj.au_sa_bp_id));
end with;
-- fix
l_bu_id := obj.bu_id
l_acc_type_id := obj.acc_type_id
```
- Means: this is the documented "repeated access" semantics: reuse of a row read is a compile-time merge, broken by any call not known to be db side effect free; it is not a runtime cache.
- Cite: paged/text/hints-and-tips-on-using-avaloq-script.txt pp.5-7 "Optimizing accesses to the same database table"
- Basis: STATED
- VERIFY: Q26 CONFIRMS; Q27 CONFIRMS; Q28 PARTIAL (ASMD markers exist)
- Audit use: rule: within one block, ≥2 reads of the same DDIC instance interleaved with calls not marked `db_side_effect_free`/`deterministic` -> "missed optimisation". Same root+key, different attribute, still counts.
- From: G1-78, G1-79, G1-80, G6-48, G6-83

### KB-DATA-42 Hoist loop-invariant reads and calls
- Fact: Statements in loops run many times; statements returning a value constant across iterations should move before the loop. The doc says this is a general rule, not report-specific.
- Avaloq form (verbatim, including the doc's missing `)`):
```
---- INEFFICIENT ----
for p in cont.pos_list loop
  if p.asset.maturity_date = lookup.date(to_char(session.today) || '+3v') then
---- BETTER ----
l_date_3v := lookup.date(to_char(session.today) ||' +3v';
for p in cont.pos_list loop
  if p.asset.maturity_date = l_date_3v then
```
- Means: READ inside loop with loop-invariant arguments = performance finding.
- Cite: paged/text/hints-and-tips-on-using-avaloq-script.txt pp.2-3 "Avoid unnecessary function calls in loops"
- Basis: STATED
- VERIFY: Q26 CONFIRMS; Q37 CONFIRMS
- From: G1-72, G1-B-ADD-03

### KB-DATA-43 Documented caching: deterministic functions and package state
- Fact: A `deterministic` function called with literal arguments (e.g. a wrapper around `lookup.code`) is evaluated once "with a cached result at installation time"; `deterministic` implies `db_side_effect_free` (private/nested functions and non-constant arguments are not evaluated at installation time). Constants and package variables are cached values not recalculated on a session switch, so session-related values (especially base parameters) must not be cached in them. Body (`b_`) variables live for the session and can hold lists for the same package or report DTM.
- Means: the only documented caches are install-time deterministic results and package state; not object reads.
- Cite: paged/text/hints-and-tips-on-using-avaloq-script.txt pp.9-10 "Use of deterministic" ; paged/text/naming-conventions.txt p.3 "Constants" ; paged/text/what-are-avaloq-script-packages.txt p.3 ; paged/text/data-types.txt p.29
- Basis: STATED
- VERIFY: Q26 CONFIRMS/EXTENDS/PARTIAL; Q27 EXTENDS
- Audit use: flag package-level constants/`b_` variables initialised from `session.*` or base parameters.
- From: G1-82, G1-64, G2-62

### KB-DATA-44 Keys are not unique; names are historicized
- Fact: Object keys help find objects; any number can exist (short text or an external identifier such as passport, social security, National Insurance number, IBAN), set manually or by rules, and "They need not be unique." Names may exist in several languages and are historicized: a name change (via an order) keeps the previous value and time, and the name at a past time can be queried.
- Means: a key lookup is a READ that may return several objects; a name READ may depend on language and date; a name change = ORDER.
- Cite: paged/text/common-object-attributes.txt pp.1-2 "Object attributes" (rows "Keys", "Names")
- Basis: STATED
- VERIFY: E-Q2 PARTIAL (name change "using an order")
- From: G3-47, G3-52

---

## C5 How data is CREATED and MODIFIED

### KB-DATA-45 Every data change uses an order whose lifecycle a workflow controls
- Fact: For all object types you need an order to change the object's data. The same technique applies to any data: "an order whose lifecycle is controlled by a workflow". Static data workflows control how objects like BPs are created and modified. Exceptions are few (post-it on a stored order; rare direct OBJ modifications, unnamed).
- Means: object CREATE/MODIFY sites are ORDER sites; a direct write path that bypasses order/workflow is a deviation to flag.
- Cite: paged/text/what-are-orders.txt p.1 "What are orders" ; paged/text/what-are-workflows.txt p.2 "What are workflows" ; paged/text/what-are-the-data-access-layers.txt pp.2-3
- Basis: STATED
- VERIFY: data-effects ORDER CONFIRMS/EXTENDS; E-Q2/E-Q3 PARTIAL (concept, no API on these pages); Q18 CONFIRMS
- From: G4-01, G4-24, G6-64

### KB-DATA-46 `new` on a MEM_DOC DDIC opens an order (syntax `with new ...`)
- Fact: Constructors create new objects (with new static data orders) and initiate financial transactions (with booking orders). Statement syntax for constructors is `with new <ddic>(args) as <alias> do ... end with;` (official example with `mem_tab`). A secondary note's `with new mem_doc_pay(meta_typ_id => meta_typ.pay_ord_id, acc_id => ..., amount => ...)` has an attested shape, but its parameter names and `meta_typ.pay_ord_id` are unsupported, and "temporary order for calculation" is wrong: `new` initiates a real order in MEM_DOC.
- Avaloq form: `with new mem_tab(c_tab_name_obj) as obj_tab do ... obj_tab.remv; end with;`
- Means: `new mem_doc_<btt>(...)` = ORDER (create), entity ORDER of business type <btt>; never PURE.
- Cite: paged/text/what-are-data-dictionaries.txt p.7 "DDIC constructors" ; paged/text/data-types.txt pp.41-42 "Example for MEM_TAB vs LIST"
- Basis: STATED (constructor role; `with new` syntax); INFERRED (that `with new mem_doc_*` follows the same syntax; no official mem_doc example)
- VERIFY: Q08 PARTIAL; Q18 PARTIAL; E-Q3 PARTIAL
- From: G3-25, G6-49, G2-54

### KB-DATA-47 MEM_DOC_BP.new parameters; `no_commit` defaults to `'+'`
- Fact: The MEM_DOC_BP constructor `new (parameters)` (type mem_doc_bp, operation "add"; header "Business Object Type mem_doc_bp (ID 11)", "BP Order in Memory") has three parameters: `wfc_action_id` (mandatory, "id of database table wfc_action"), `bp_id` ("id of obj_bp"), `no_commit` (boolean, Default Value `'+'`, i.e. true). The meaning of `bp_id` and `no_commit` is not documented.
- Means: ORDER (create or modify BP order). INFERRED: with `bp_id` = modify order for an existing BP, without = create; `no_commit = '+'` suggests the constructor does not commit by default.
- Cite: paged/text/what-are-data-dictionaries.txt p.7 "DDIC constructors" (screenshot PDF p.7)
- Basis: STATED (parameters, types, default from screenshot); INFERRED (semantics)
- VERIFY: E-Q4 PARTIAL — `no_commit` exists with default `'+'`; the reader's "commit by default" was reversed by the verifier
- From: G3-26

### KB-DATA-48 Object creation lifecycle: CREATE happens at finalisation
- Fact: Creating an object (e.g. a BP): (1) a static data order is opened, data exists only in memory; (2) a workflow action saves the order to DOC for further processing (e.g. supervisor check); (3) the order is reloaded into memory (e.g. 4-eyes check); 2-3 may repeat; (4) the order is loaded, finalised and saved by a workflow action: only then is the object created in OBJ and the order stored in DOC. Without further processing, step 4 follows step 1. Financial transactions follow similar steps; if the order modifies a position (an object) all three layers, including OBJ, are involved.
- Means: constructor -> ORDER(create); workflow action -> ORDER(save/finalise) with CREATE/MODIFY of the object (or position) as consequence.
- Cite: paged/text/what-are-the-data-access-layers.txt pp.3-5 "Creating an object"
- Basis: STATED
- VERIFY: E-Q2/E-Q3 EXTENDS (mechanism); CREATE is indirect
- From: G3-35, G3-36

### KB-DATA-49 Static data orders: only Create and Modify
- Fact: Static data orders create and modify objects and do not create bookings (e.g. new Person, BP or CONT; change of marital status on marriage). They have only two order types: Create order (new object of the business type) and Modify order (existing object).
- Means: Create order -> ORDER + CREATE(entity); Modify order -> ORDER + MODIFY(entity); no booking effect.
- Cite: paged/text/what-are-orders.txt p.2 "What are orders" ; paged/text/what-is-the-type-of-an-order.txt p.1 "What is the type of an order"
- Basis: STATED
- VERIFY: data-effects ORDER sub-actions EXTENDS; Q18 PARTIAL; Q15 CONFIRMS
- From: G4-04, G4-08, G6-65, G6-80

### KB-DATA-50 `set` on fields: MODIFY of the DDIC's entity
- Fact: Simple fields allow get (read) and set (write) as listed in the DDIC. Changes on a MEM DOC order stay in memory until a workflow action saves them. Whether a field has `set` is per field (KB-DATA-12).
- Avaloq form: assignment `<designator> := <expr>` (`:=`), e.g. on a `mem_doc_*` field
- Means: `mem_doc_*` field on left of `:=` = MODIFY of ORDER (in memory); `obj_*`/`doc_*` field on left of `:=` = unusual, review.
- Cite: paged/text/what-are-data-dictionaries.txt p.5 "Simple DDIC fields" ; paged/text/what-are-the-data-access-layers.txt p.2
- Basis: STATED (operations, MEM DOC semantics); INFERRED (effect labels)
- VERIFY: E-Q2 PARTIAL
- From: G3-21, G3-32, G6-64

### KB-DATA-51 Post-it writes: `attach_postit`, `add_postit`, `postit_list.add`
- Fact: `attach_postit` (inherited from doc, operation "do") takes doc_id (mandatory, id of doc), topic (mandatory, text), msg (mandatory, text) and optional type (code_postit_type), sub_type (code_postit_sub_type), role (sec_user_role_v), prop (boolean); description "Add the given postit to the given order (order does not need to be in memory, but will be locked)". Other attested forms: `collect.add_postit(i_val_1, i_val_2)` on `mem_doc_collect(b_id)`, and the list-field add `mem_doc.postit_list.add(topic => ..., text => ...)` (diagram). Validation code may add a post-it when an optional check fails.
- Means: MODIFY of ORDER (post-it), plus lock for `doc_*.attach_postit`; not error handling.
- Cite: paged/text/what-are-data-dictionaries.txt p.6 "DDIC methods" (screenshot) ; paged/text/coding-conventions.txt p.3 ; layout/02-techbase/02_05_Language_elements_used_in_Avaloq_Script.txt (secondary) ; paged/text/what-are-avaloq-script-expressions.txt p.2 (diagram) ; paged/text/common-order-attributes.txt p.2 (row "Post-its")
- Basis: STATED
- VERIFY: E-Q6 PARTIAL; Q19 EXTENDS
- Audit use: flag attach_postit inside loops (one lock per call).
- From: G3-A03, G1-46, G2-06, G4-16

### KB-DATA-52 No DELETE of objects: hide, then wipe
- Fact: Static data orders have no delete type "because we can't delete objects". After the legal retention period (e.g. 10 years) the bank can only hide client-identifying data and then wipe it with dummy values. (A TOC module "Transaction Deletion" concerns transactions, not objects.)
- Means: DELETE does not apply to business objects; hide/wipe = MODIFY via order; a cancel of a booked transaction = ORDER (reversal, KB-DATA-62); discard of an unsaved order = ORDER sub-action.
- Cite: paged/text/what-is-the-type-of-an-order.txt p.2 "What is the type of an order"
- Basis: STATED
- VERIFY: data-effects DELETE "delete/remove/cancel of an object" CONTRADICTED (partly); DELETE may still apply to non-object records (e.g. list rows, ice issues)
- Audit use: direct SQL DELETE on object tables = high severity.
- From: G4-11, G6-63

### KB-DATA-53 What counts as a DB write (db_side_effect_free table)
- Fact: Use `db_side_effect_free` only if the method has no effect on any database content readable by any DDIC access. NOT side-effect free: store operations; actions on an OBJ or DOC layer DDIC; workflow action on a MEM_DOC layer DDIC. Side-effect free: pure in-memory calculations; logging only.
- Means: official boundary between PURE/logging and data-changing effects: `.store`, OBJ/DOC DDIC methods, MEM_DOC workflow actions are writes (MODIFY/ORDER/SIDE_EFFECT), not PURE.
- Cite: paged/text/hints-and-tips-on-using-avaloq-script.txt pp.7-8 "Use of db_side_effect_free"
- Basis: STATED
- VERIFY: Q14 EXTENDS; Q11 PARTIAL/EXTENDS
- Audit use: a `db_side_effect_free` method that reaches any of the listed actions (directly or through callees) is a correctness finding.
- From: G1-81

### KB-DATA-54 `.store` writes to the database
- Fact: `.store` persists a collection to list tables and returns an ID; each call writes to the DB and replaces existing rows. Use `.store`/`.load(id)` only to pass data to a report or for asynchronous population; PL/SQL interop needs no stored list; avoid repeated `.store` calls, particularly in `on level_xxx` report handlers; clear the stored version only for business logic (list_xxx tables are truncated regularly). MEM_DB_LIST_CHAR's constructor with `list_char_id` reads table LIST_CHAR and `store_list` writes it.
- Avaloq form: `l_id := l_numbers.store; -- persist for report` ; `l_result.load(l_id);`
- Means: `.store` = SIDE_EFFECT/MODIFY (technical list table write, not business data); `.load(id)` = READ.
- Cite: paged/text/data-types.txt pp.29-30 "Limit bad use of .store", pp.5-6 (MEM_DB_LIST_CHAR), p.42 "How to persist a SET or LIST DDIC collection"
- Basis: STATED (DB write); INFERRED (effect label)
- VERIFY: Q26 CONFIRMS/EXTENDS
- From: G2-41, G2-42, G2-29, G2-56, G6-87

### KB-DATA-55 Anything doable in a UI can be done programmatically
- Fact: All object attributes can be created/modified manually or programmatically; Avaloq says anything doable in a UI can also be done programmatically.
- Cite: paged/text/common-object-attributes.txt p.2
- Basis: STATED
- From: G3-53

---

## C6 Orders and order types

### KB-DATA-56 Order = instruction; object = data
- Fact: An order is an instruction to modify data (e.g. execute a financial transaction, change a client's address); an object (BP, POS, MACC) holds data. Transaction orders also change data associated with objects such as POS or MACC. Orders are created by an employee in a UI form or automatically by the system (e.g. from an incoming message, or recurring orders generated from a contract, such as a monthly mortgage payment whose TRX date is the generation date).
- Means: ORDER is its own entity kind; one call may carry ORDER + MODIFY(POS/MACC). Interface and batch code are expected order-creation sites.
- Cite: paged/text/what-are-orders.txt pp.1-2 "What are orders" ; paged/text/understanding-banking-dates.txt p.3 "Summary of accounting dates"
- Basis: STATED (distinction, origins); INFERRED (modelling advice)
- VERIFY: Q15 PARTIAL; Q21 PARTIAL; Q22 PARTIAL; E-Q3 PARTIAL
- From: G4-02, G4-05, G4-06

### KB-DATA-57 Two order categories: transaction (booking) and static data
- Fact: Transaction orders (also called booking orders) execute financial transactions and normally create one or more bookings on the bank's balance sheets (e.g. salary payment, buying or selling stocks, transfer to another bank). Static data orders create and modify objects and create no bookings.
- Means: ORDER carries order_category = TRANSACTION (booking effects on balance sheet and positions) or STATIC_DATA (CREATE/MODIFY of one object type).
- Cite: paged/text/what-are-orders.txt pp.1-2 "What are orders" (table "Category of order")
- Basis: STATED
- VERIFY: data-effects ORDER PARTIAL/EXTENDS
- From: G4-03, G4-04, G6-65

### KB-DATA-58 Business type (btt) per order, defined in META_TYP
- Fact: Every order has a business type (business transaction type, btt). For transaction orders it names the transaction (Payment, Stex = stock exchange); for static data orders the object type created/modified (BP, Address). Business types are defined in code table META_TYP. The business type is the product category under which workflows, date rules and the accounting method are configured.
- Avaloq form: `doc.meta_typ_id`, `mdb_meta_typ.stex`, `meta_typ.bp_id`
- Means: btt = suffix of order DDIC names (`mem_doc_stex`, `doc_bp`, `doc_pay`); META_TYP = master list of order DDIC roots.
- Cite: paged/text/what-is-a-business-type.txt p.1 "What is a business type" ; paged/text/understanding-banking-dates.txt p.6 "Trade and settlement date accounting"
- Basis: STATED
- VERIFY: Q15 EXTENDS/CONFIRMS; Q18 PARTIAL; Q09 PARTIAL (a code table name without CODE_ prefix)
- From: G3-54, G4-51, G6-66, G4-37

### KB-DATA-59 Order types: CODE_ORDER_TYPE
- Fact: Different order types belong to different business types and are defined in code table CODE_ORDER_TYPE. Static data orders have only Create and Modify; financial transaction orders usually have many order types processed differently (Stex: one for buying, one for selling). CODE_ORDER_TYPE does not establish a "code tables are named CODE_*" rule (META_TYP has no such prefix).
- Avaloq form: `mem_doc.order_type_id` (ID into CODE_ORDER_TYPE)
- Means: ORDER effects record (business type, order type) when resolvable; both resolve against META_TYP x CODE_ORDER_TYPE.
- Cite: paged/text/what-is-the-type-of-an-order.txt p.1 "What is the type of an order" ; paged/text/avaloq-script-expressions.txt p.2
- Basis: STATED
- VERIFY: Q09 PARTIAL; Q14 EXTENDS; Q15 PARTIAL
- From: G4-07, G4-09, G4-10, G2-05

### KB-DATA-60 Order fields and the four common attributes: keys, additions, post-its, links
- Fact: Avaloq defines exactly which fields each order has and their data types. Almost all orders have keys, additions (together "order extensions"), post-its and links. An order key normally stores the external system's reference number. Order additions supply fields missing from standard forms. A post-it is the order equivalent of a remark (text, type and sub-type). Links tie related orders, e.g. a collective salary order and the payment order it generates per employee.
- Means: read of order key/addition = READ(ORDER); writes of keys/additions/post-its/links = MODIFY(ORDER); collective orders may create child orders in a loop (ORDER in loop).
- Cite: paged/text/common-order-attributes.txt pp.1-3 "Common order attributes" (table "Order attributes"; diagram PDF p.1)
- Basis: STATED
- VERIFY: Q14 PARTIAL; Q16 EXTENDS; Q19 EXTENDS; Q29 PARTIAL
- Audit use: interface code creating orders should set an order key (duplicate detection).
- From: G4-12, G4-13, G4-14, G4-15, G4-16, G4-17

### KB-DATA-61 `doc_*.do_wfc_action`: workflow action without loading the order
- Fact: DOC_PAY's method `do_wfc_action` (inherited from doc, operation "do") is described as "Performs a workflow action without loading the order into memory. Attention: Only the workflow status is updated ..." (rest truncated in the screenshot). Parameters: `wfc_action_id` (id of database table wfc_action, "Workflow action to be performed"), `new_wfc_status_id` (id of database table wfc_status; "either wfc_action_id or new_wfc_status_id may be specified"), `trans_action_id` and `trans_remark` ("PAYTB only"). The Hints page lists "workflow action on a MEM_DOC layer DDIC" as a DB side effect.
- Means: ORDER (status change / workflow action on a stored order); sub-action key = wfc_action_id | new_wfc_status_id; it does not apply field changes made elsewhere.
- Cite: paged/text/what-are-data-dictionaries.txt p.6 "DDIC methods" (screenshot PDF p.6) ; paged/text/hints-and-tips-on-using-avaloq-script.txt p.8 "Use of db_side_effect_free"
- Basis: STATED (screenshot text; description truncated)
- VERIFY: E-Q3 PARTIAL/EXTENDS; E-Q6 PARTIAL
- From: G3-A02, G3-24, G1-81

### KB-DATA-62 Reversals are new orders; booking events per order
- Fact: A reversal is a reversal order that is itself verified. It produces a reversal event with its own DONE (today at verification) and BOOK dates, while the original event keeps its dates; TRX and VAL (usually PERF) are copied from the original. The order-form screenshot groups booking events under an accounting rule set ("ARB 2015/1 FINMA (Accounting Rules Banks) - PKO Primary GAAP (Avaloq Standard)") with an event ID, status "1 Booked(35)" and order-type code "B(139092)".
- Means: cancel of a booked transaction = ORDER (reverse, a new order), never DELETE or MODIFY of the original. "Booked(35)" is candidate vocabulary only (may be an event status).
- Cite: paged/text/understanding-banking-dates.txt pp.8-12 "More details about banking date types" ; p.7 "Example order form showing banking dates" (screenshot)
- Basis: STATED (reversal semantics, event existence); INFERRED (cancel = reversal; order -> events 1:n; status codes)
- VERIFY: data-effects ORDER "cancels" PARTIAL/EXTENDS, CONTRADICTS treating cancellation as DELETE; Q15 PARTIAL
- From: G4-39, G4-50, G4-38

---

## C7 Workflows

### KB-DATA-63 A workflow is the flowchart of an order's lifecycle
- Fact: Workflows control order processing and model the bank's business processes: a workflow defines an order's lifecycle, its stages and the logic for moving between them. They capture what is common across banks and let each bank fine-tune with minimal customization. Example process: after data entry, if the estimated value is "> £10,000?" a supervisor must check and approve before the trading team buys.
- Means: order state changes are workflow transitions/actions; conditions on order data gate progression.
- Cite: paged/text/what-are-workflows.txt p.1 "What are workflows" (figure "Business process for a transaction to buy shares")
- Basis: STATED
- VERIFY: Q18 PARTIAL; Q19 PARTIAL; Q02 PARTIAL; Q29 PARTIAL
- From: G4-18, G4-19, G4-20

### KB-DATA-64 One workflow per business type; paths by order type
- Fact: For every business type there is one workflow; inside it, processing paths usually depend on the order type (e.g. Payment: internal transfers, outgoing foreign/domestic payments, new standing orders). Transaction workflows are often extremely complicated. Workflows include 4-eyes checks by a supervisor.
- Cite: paged/text/what-are-workflows.txt p.2 "What are workflows" ; paged/text/what-are-the-data-access-layers.txt p.4
- Basis: STATED
- VERIFY: Q15 EXTENDS/CONFIRMS; Q18 PARTIAL/CONFIRMS; Q05 PARTIAL
- From: G4-22, G4-23, G6-66

### KB-DATA-65 Example workflow figure: states and actions (illustrative)
- Fact: The "Example workflow" figure shows circles Start, Open, Approval, Done, Discarded and boxes "New order", "Modify order", "Check?", "<50K", ">=50K", "Verify", "Discard", plus a gateway "[...]". Paths: Start -> New/Modify order -> Open -> Check? -> gateway; "<50K" -> Done; ">=50K" -> Approval -> Verify (Done) or Discard (Discarded). "Release", "book" and "cancel" do not appear as workflow actions in these docs.
- Means: candidate ORDER sub-actions: create, modify, check, verify, discard. Not real action identifiers.
- Cite: paged/text/what-are-workflows.txt p.2 "What are workflows" (figure, PDF p.2 image)
- Basis: INFERRED (labels confirmed on the image; state vs action reading from node shapes)
- VERIFY: Q18 PARTIAL; data-effects ORDER sub-actions PARTIAL
- From: G4-21

### KB-DATA-66 `env_task_ext#.task#do_wfc_action` is the ice dev-task API, not the banking order API
- Fact: A secondary note's `env_task_ext#.task_do_wfc_action(i_task_id, i_action_id)` is wrong for banking orders: `env_task_ext#` is the ice Workbench Workflow API for development tasks (PL/SQL, called as `e.env_task_ext#...`), and the real function is `task#do_wfc_action(i_task_id env_task#.t_task, i_wfc_action varchar2, i_param t_wfc_param_tab := null, i_comment varchar2 := null) return t_wfc_param_tab`. Banking orders run workflow actions through the order DDIC method `do_wfc_action` (KB-DATA-61).
- Means: `env_*_ext#` calls inside a banking script package = wrong API (finding); their effects belong to ice tasks, not orders.
- Cite: layout/03-ice-workflow/AvaloqICE/workflow_api_all_subpages/D3_Function_task_do_wfc_action.txt pp.1-2 "Signature" ; layout/03-ice-workflow/AvaloqICE/ice_workflow_api_introduction.txt p.1 ; paged/text/what-are-data-dictionaries.txt p.6 "DDIC methods"
- Basis: STATED
- VERIFY: Q18 CONTRADICTS (secondary claim)
- From: G6-67, G5-31, G5-03, G5-04

---

## C8 Transactions and commit

### KB-DATA-67 `session.commit` / `session.rollback`: exist, use with great care
- Fact: The SESSION DDIC has commit and rollback methods. "Be very careful when using the commit and rollback methods, especially during message processing": errors may not be handled correctly and atomicity can break, e.g. creating several orders for the same message. CONFLICT: a secondary note says COMMIT/ROLLBACK should be omitted entirely because a transaction manager controls them; the official text shows the methods exist and only warns (exact member names `session.commit`/`session.rollback` are not printed as code).
- Means: SIDE_EFFECT (transaction boundary); higher severity in message-processing sources, inside loops and in library methods.
- Cite: paged/text/what-are-data-dictionaries.txt pp.7-8 "Special DDICs: SESSION and LOOKUP"
- Basis: STATED
- VERIFY: E-Q4 PARTIAL; Q26 PARTIAL; Q11 EXTENDS; Q30 EXTENDS
- From: G3-28, G6-68

### KB-DATA-68 `no_commit` and order commits are not documented
- Fact: The only order-level commit hint is the MEM_DOC_BP `new` parameter `no_commit` with default `'+'` (KB-DATA-47). The G4 order/workflow pages say nothing about whether order actions commit, about savepoints or rollback; "transaction" there means a financial transaction, not a database transaction.
- Means: UNKNOWN for implicit commits of order actions; do not label an order action as a commit without evidence.
- Cite: paged/text/what-are-data-dictionaries.txt p.7 "DDIC constructors" (screenshot) ; paged/text/what-are-orders.txt p.1
- Basis: STATED (parameter, default); INFERRED (absence from G4 pages, verifier gap note)
- VERIFY: E-Q4 PARTIAL
- From: G3-26, G4 open question 2

### KB-DATA-69 Cross-reference: ice Workflow API commit rules differ by package
- Fact: In the ice Workflow API (PL/SQL, not Avaloq Script), every subprogram of env_issue_ext# and env_solution_ext# commits or rolls back itself, while "None of the functions in the package [env_task_ext#] do commit or roll back"; the client must commit, and every example ends with `commit;`.
- Means: applies only to ice Server integration code; not evidence for banking-order commit behaviour.
- Cite: layout/03-ice-workflow/AvaloqICE/workflow_api_05_package_env_task_ext.txt p.1 "Operational notes" ; layout/03-ice-workflow/AvaloqICE/workflow_api_02_package_env_issue_ext.txt p.1 ; layout/03-ice-workflow/AvaloqICE/workflow_api_04_package_env_solution_ext.txt p.1
- Basis: STATED (packages' commit behaviour); INFERRED (env_task_ext# procedures behave like its functions)
- VERIFY: Q26 EXTENDS
- From: G5-09

---

## C9 Banking dates, bank days and value days

### KB-DATA-70 Trade vs settlement; four accounting dates and their identifiers
- Fact: Trade is the agreement; settlement the later exchange of assets (Swiss stock trades settle three days later; internal transfers the same day). Four accounting dates form a 2x2 grid: TRX "order created (transaction agreed)", VAL "assets exchanged (transaction completed)" (client view); DONE "order verified", BOOK "asset exchange booked" (bank view). Bank-view dates can be later (DONE later than TRX). Lower-case identifiers in the synonym tables: `trx_date` (transaction/trade date), `done_date` (verification/trade book date), `val_date` (value date), `book_date` (book/value book date), `perf_date` (performance date). Trap: "book date" = BOOK, "trade book date" = DONE.
- Means: order date fields; READ/MODIFY of these fields is order data.
- Cite: paged/text/understanding-banking-dates.txt pp.1-4 "Difference between trade and settlement", "Summary of accounting dates", pp.8-12 "More details about banking date types"
- Basis: STATED (names, grid); INFERRED (that the snake_case names are DDIC field names)
- VERIFY: Q08 PARTIAL; Q14 PARTIAL
- From: G4-25, G4-26, G4-27, G6-69

### KB-DATA-71 TRX date: order created; basis for FX and VAT
- Fact: TRX is when the client agrees, i.e. when the order is created and stored (SmartClient: when the employee saves the completed form, pending verification if required; generated orders: the generation date). It is the basis for FX rates into the reference currency and the VAT/GST rate, is used by the Book Engine, can be made user-modifiable, and a reversal keeps the original TRX.
- Cite: paged/text/understanding-banking-dates.txt pp.3, 8
- Basis: STATED
- VERIFY: E-Q3 PARTIAL
- Audit use: FX/VAT lookups in order processing should use the order's TRX date, not the current date (INFERRED).
- From: G4-28, G4-29

### KB-DATA-72 DONE date: verification; 21.12.4712 until verified
- Fact: DONE is when the order is complete and verified (if verification is required); from then the transaction is ready to be implemented. It starts as the artificial 21.12.4712 (close to Oracle's maximum date), moves toward today but stays in year 4712, and is set to the current date on verification; afterwards only power users can change it. It is the basis for trade date accounting and normally portfolio reports (Balance and Fee Engines); a reversal gets today, the original keeps its DONE.
- Means: done_date in year 4712 = unverified order; verify = ORDER sub-action with a date effect.
- Cite: paged/text/understanding-banking-dates.txt pp.4, 9
- Basis: STATED
- VERIFY: E-Q3 PARTIAL
- Audit use: code treating 4712 as an error, or hard-coding 31.12.9999, is suspect; writes to done_date are high-risk.
- From: G4-30, G4-31, G4-47

### KB-DATA-73 VAL, BOOK and PERF dates
- Fact: VAL is the agreed (predicted) settlement date; the actual exchange date is not stored. It is normally rule-calculated (rule loader table DOC_DFLT_FLD_VAL_RULE_LD, per business type), drives interest (Interest Engine), may be user-modifiable, and a reversal keeps it. BOOK is used only when settlement date accounting is enabled by a base parameter; it is calculated from DONE or VAL (base parameter default, overridable by automatic field rules), used by the Booking Engine, and recalculated on reversal. PERF is the date an asset exchange counts for performance (not accounting); calculated from any of the four dates, manually modifiable, not present on all order forms; performance reports include exchanges whose PERF date is inside the period.
- Means: perf_date may not exist on every order type (guard access); value dates come from rules, not hand arithmetic.
- Cite: paged/text/understanding-banking-dates.txt pp.4, 7, 10-12 "Summary of accounting dates", "Performance date", "More details about banking date types"
- Basis: STATED
- VERIFY: Q19 EXTENDS; Q24 EXTENDS
- From: G4-32, G4-33, G4-34, G4-49

### KB-DATA-74 Trade dates from the order; settlement dates from rules
- Fact: TRX and DONE are based on the order (created, verified). VAL and BOOK are normally calculated by bank-defined rules from information such as the business type and can be overridden manually.
- Means: ORDER create sets TRX; ORDER verify sets DONE.
- Cite: paged/text/understanding-banking-dates.txt p.4 "Summary of accounting dates" (Note)
- Basis: STATED
- VERIFY: data-effects ORDER sub-actions CONFIRMS "creates" and "verifies"
- From: G4-35

### KB-DATA-75 Trade date accounting (TBDA) vs settlement date accounting (VBDA)
- Fact: TBDA bases the balance sheet on DONE (moment of verification); VBDA on BOOK. VBDA is either "simple" (rare) or contingency accounting (common: off-balance/pending from DONE, in-balance from BOOK; e.g. capture falling FX rates before settlement). Swiss rules allow both, but the same method for all transactions of one business type.
- Means: verify is booking-relevant under TBDA.
- Cite: paged/text/understanding-banking-dates.txt pp.5-6 "Trade and settlement date accounting" (figure PDF p.5)
- Basis: STATED
- VERIFY: Q15 EXTENDS
- From: G4-36, G4-48, G4-37

### KB-DATA-76 Order form: editable dates vs read-only booking-event dates
- Fact: On the SmartClient stock-exchange order form, four dates top right are editable (screenshot: Order Date 08-JAN-2020 12:22:37, Trade Date, Value Date, Perf Date); a middle "Events" block shows read-only dates of the booking event (Trade Date, Verif. Date, Value Date, Book date, Performance Date). Also shown: Backdated, Reversal, Related/Rectified/Rectification Order, Order Type Group "Buy".
- Cite: paged/text/understanding-banking-dates.txt p.7 "Example order form showing banking dates" (screenshot)
- Basis: STATED (text); INFERRED (meaning of screenshot labels)
- VERIFY: data-effects ORDER sub-actions PARTIAL
- From: G4-38

### KB-DATA-77 Bank days, the EOD switch, value days and calendars
- Fact: A bank day is a day the bank is open and orders can be created and processed; the end-of-day (EOD) job switches the bank date to the next bank day (Fri 10 Jan 2020 -> Mon 13 Jan 2020). TRX and DONE are bank dates. A value day is a day a transaction can be executed externally (exchange open; payment rules such as TARGET2), not to be confused with the VAL date; settlement rules count value days (e.g. VAL = TRX + 2 value days). The initiating bank may be closed on the execution day. Calendars were defined in tables COUNTRY_DAY_OFF and OBJ_STEX_DAY_OFF; calendar objects (CALDR) are now used.
- Means: bank date ≠ calendar date; adding calendar days to get a value date is a likely bug; reads of the legacy day-off tables are a modernisation finding.
- Cite: paged/text/understanding-bank-and-value-days.txt pp.1-2 "Bank days", "Value days", "Calendars"
- Basis: STATED (facts); INFERRED (validator ideas)
- VERIFY: Q22 PARTIAL; Q17 PARTIAL; Q29 EXTENDS
- From: G4-40, G4-41, G4-42, G4-43, G4-44, G4-45

### KB-DATA-78 Date functions: `session.today`, `lookup.date`, `sysdate`
- Fact: `session.today` is the official current-date member. `lookup.date` computes dates: attested offsets `+3w` and `+3v` (`lookup.date(''today +3w'')`, `lookup.date(to_char(session.today) ||' +3v'`); `b`, `m`, `y` units (secondary note) are not attested. CONFLICT: a secondary note says never use `sysdate` for banking logic; official examples use `sysdate` (`if a.issue_date.val_date = sysdate`). The rule is a sound inference from the EOD bank-date switch, but no doc states it. Testability guidance: pass `session.today` and base parameters as defaulted parameters (`i_date date := session.today`).
- Means: `session.today` / `lookup.date` = READ (session/lookup); `sysdate` = PURE (clock), info-level when compared with business dates.
- Cite: paged/text/what-are-data-dictionaries.txt p.8 ; paged/text/hints-and-tips-on-using-avaloq-script.txt pp.3-4 ; paged/text/declarations-in-avaloq-script.txt p.3 ; layout/04-test-framework/pages/02c_Implementing_the_construction_tests.txt p.4 "Create modular and stateless code"
- Basis: STATED (members, examples); INFERRED (sysdate rule)
- VERIFY: Q10 PARTIAL; Q25 PARTIAL/EXTENDS; Q26 CONFIRMS
- From: G6-70, G6-54, G3-29, G1-72, G5-81

---

## C10 Object model

### KB-DATA-79 Objects: uniform handling; object types in CODE_OBJ_TYPE; technical objects
- Fact: Avaloq runs on Oracle and models banking data as objects (Person, Address, Country, Card, Document, Direct Debit, ...). Objects hide table structure; all types are created, modified, identified, named, searched, displayed and secured the same way, and protected by security permissions uniformly. Structure strongly affects performance. Object types are defined in code table CODE_OBJ_TYPE, which also lists technical objects (printers, background processes and queues, external messages, users, business applications) with `is_to` = true, there to reuse object security. A code table is an abstraction over Oracle tables holding configuration data.
- Means: one accessor/effect pattern per layer generalises across all `obj_<type>` roots; filter `is_to` for business objects.
- Cite: paged/text/what-are-objects.txt p.1 ; paged/text/what-are-technical-objects.txt p.1
- Basis: STATED
- VERIFY: Q14 EXTENDS; Q15 EXTENDS/PARTIAL; Q17 PARTIAL; Q24 PARTIAL; Q26 PARTIAL; Q30 PARTIAL
- From: G3-38, G3-39, G3-43, G3-44, G3-A07

### KB-DATA-80 Holdings model: Person -> BP -> CONT -> POS (MACC) -> ASSET
- Fact: ASSET = ownable instrument or currency (not client-specific); POS = how much of an asset is owned; MACC = money account, a special POS for a currency asset, may be negative; CONT = container grouping positions (cannot contain containers); BP = business partner, the business relationship incl. its type; Person = name, marital status. Addresses are separate Address objects. CONFLICT: a secondary note says BP represents legal entities and natural persons; official: BP is a relationship, people are Person objects.
- Means: entity vocabulary BP, POS, MACC, CONT, ASSET, PERSON, ADDR; chained navigation between them = READs of further entities.
- Cite: paged/text/introducing-the-avaloq-object-model.txt pp.1-3 ; paged/text/more-on-bp-objects.txt p.1
- Basis: STATED
- VERIFY: Q15 EXTENDS/PARTIAL
- From: G3-40, G6-60, G4-46

### KB-DATA-81 BP = business relationship, external or internal (BU)
- Fact: A BP is a relationship between the bank and the outside world or within the bank (usually a legal entity such as a country subsidiary; departments called Business Units and sub-business units). A money account can be linked to both the client BP and the subsidiary BP.
- Means: `obj_bp(x).name` is the BP's name, not necessarily a person's (INFERRED).
- Cite: paged/text/more-on-bp-objects.txt p.1
- Basis: STATED
- From: G3-41

### KB-DATA-82 Person types and roles
- Fact: Person types include Natural Person and Person Association (no legal capacity, cannot own assets or be account owner). Lines between persons and a BP define roles: registered owner (RO), account owner (AO), beneficial owner (BO); an asset manager or internal CRM may hold authority; "member" links persons to an association. Marital status lives on Person and changes via a static data order.
- Cite: paged/text/more-on-person-objects.txt pp.1-3 ; paged/text/what-are-orders.txt p.2
- Basis: STATED
- From: G3-42, G6-61, G6-80

### KB-DATA-83 Common object attributes and extensions
- Fact: Each object type has a fixed set of attributes. Banks extend it with keys, classifications and additions ("object extensions"). Classifications categorise objects and control how the system processes them (e.g. asset_type = currency). Additions are typed bank-specific fields (e.g. first_issued = 1850). Remarks are typed text notes with type, sub-type and a "valid to" date. Relations link two objects (e.g. used_in_country = CH). Names are multilingual and historicized. Key examples in the docs are passport, social security, National Insurance numbers and IBAN (ISIN/CUSIP from a secondary note are not attested).
- Means: extension reads = READ of the object; extension changes = MODIFY via order.
- Cite: paged/text/common-object-attributes.txt pp.1-2 "Object attributes"
- Basis: STATED
- VERIFY: Q16 CONFIRMS (concepts), PARTIAL (syntax)
- Audit use: branching on additions/remarks instead of classifications is a maintainability smell (doc: "not so easy").
- From: G3-45, G3-46, G3-48, G3-49, G3-50, G3-51, G6-62

---

## C11 Effect mapping table

Effect labels use the AVALOQ_DATA_EFFECTS_METAPROMPT vocabulary. "Basis" = basis of the label (the construct itself is documented in the cited entry).

| Construct | Effect label | Cite | Basis |
|---|---|---|---|
| `obj_<type>(k).<attr>` (cast + field) | READ entity=OBJ_<type>, key=k, attr | avaloq-script-expressions.txt p.4-5; what-are-the-data-access-layers.txt p.3 | STATED (read-only layer); key semantics INFERRED |
| `<var>.<rec>.<rec>.<field>` dot path | READ, one entity per record hop | what-are-avaloq-script-expressions.txt p.2 | STATED path; INFERRED per-hop entity |
| `x.<f>_id` | READ (key value only) | what-are-data-dictionaries.txt p.5 | STATED |
| `.class('c').id` / `.class_id('c')` | READ (parameterised field) | hints-and-tips p.3 | STATED |
| `<list field>` in `for`, `.count`, `(i)` / get | READ (list) | data-types.txt p.4-5 | INFERRED from op names |
| `<list field>.add/set/clear/rmv/remv_item` | MODIFY of owning entity | data-types.txt p.4-5 | INFERRED from op names |
| `list(...)`, `set(...)` cast of list field | PURE (copy) | data-types.txt p.26-27 | STATED copy semantics |
| `doc_<btt>.<field>` | READ (DOC read-only) | what-are-the-data-access-layers.txt p.2 | STATED |
| `mem_doc[_<btt>].<field>` used as value | READ (order in memory) | avaloq-script-expressions.txt p.2 | STATED |
| `mem_doc[_<btt>].<field> := v` | MODIFY entity=ORDER (in memory) | what-are-the-data-access-layers.txt p.2 | STATED (layer); label INFERRED |
| `obj_*`/`doc_*` field `:= v` | MODIFY, flag for review (rare exception) | what-are-the-data-access-layers.txt p.2-3 | STATED (exceptions exist, unnamed) |
| `new mem_doc_<btt>(...)` / `with new mem_doc_<btt>(...) as d do` | ORDER sub-action=create (CREATE/MODIFY of object only at finalisation) | what-are-data-dictionaries.txt p.7; what-are-the-data-access-layers.txt p.3-4 | STATED |
| `mem_doc_bp.new(... no_commit ...)` | ORDER create; commit behaviour UNKNOWN (default `'+'`) | what-are-data-dictionaries.txt p.7 | STATED param; INFERRED meaning |
| workflow action finalising a static data order | ORDER (finalise) + CREATE or MODIFY of object | what-are-the-data-access-layers.txt p.3-5 | STATED |
| `doc_*.do_wfc_action(wfc_action_id \| new_wfc_status_id ...)` | ORDER (workflow action / status change, order not loaded) | what-are-data-dictionaries.txt p.6 | STATED |
| workflow action on a MEM_DOC DDIC | ORDER (DB side effect, not db_side_effect_free) | hints-and-tips p.8 | STATED |
| `doc_*.attach_postit(...)` | MODIFY entity=ORDER (post-it) + lock | what-are-data-dictionaries.txt p.6; what-are-the-data-access-layers.txt p.2 | STATED |
| `<mem_doc>.add_postit(...)`, `postit_list.add(...)` | MODIFY entity=ORDER (post-it) | coding-conventions.txt p.3; what-are-avaloq-script-expressions.txt p.2 | INFERRED |
| `doc_pay.send_dir_msg` / `discard_dir_msg` (`discd_dir_msg`) | SIDE_EFFECT (message) | what-are-data-dictionaries.txt p.6 | INFERRED |
| reversal order | ORDER (reverse = new order), never DELETE | understanding-banking-dates.txt p.8-12 | STATED order; INFERRED cancel=reversal |
| any "delete" of a business object | not possible; hide/wipe = MODIFY via order | what-is-the-type-of-an-order.txt p.2 | STATED |
| `code_<x>.<entry>_id`, `mdb_*.<c>`, `meta_typ.<c>` | READ (code constant) | avaloq-script-expressions.txt p.2-3 | STATED |
| `lookup.code/code_list/asset/asset_id/class_id/obj_list/date(...)` | READ (query; obj_list = list query) | what-are-data-dictionaries.txt p.8; hints-and-tips p.3, 9 | STATED |
| `session.today`, session user ID | READ (session) | what-are-data-dictionaries.txt p.7-8 | STATED |
| `session.debug(msg)` | SIDE_EFFECT (log); allowed in db_side_effect_free | declarations p.6; hints-and-tips p.8 | STATED |
| `session.raise_ui_err(...)` | SIDE_EFFECT (UI error signalling) | what-are-data-dictionaries.txt p.8 | INFERRED |
| `session.commit` / `session.rollback` | SIDE_EFFECT (transaction) — warn | what-are-data-dictionaries.txt p.8 | STATED |
| `<coll>.store` / `store_list` | SIDE_EFFECT (DB write to list tables) | data-types.txt p.29-30 | STATED write |
| `<coll>.load(id)` | READ (list table) | data-types.txt p.29-30 | STATED |
| `env_task_ext#.*`, `env_issue_ext#.*` | not banking; ice task/issue CREATE/MODIFY/DELETE; commit rules per package | D3_Function_task_do_wfc_action.txt; workflow_api_05 p.1 | STATED |
| local arithmetic, string/date functions, `sysdate` | PURE | data-types.txt; 02_05 | INFERRED |
| runtime-chosen root or object type | UNKNOWN (DYNAMIC) | — (metaprompt rule) | INFERRED |

### What the docs do NOT say (DOC_GAP)

1. Runtime caching: no statement anywhere that an object read (`obj_bp(k).name`) is cached per session or transaction, or re-read on each access. The only documented reuse is compile-time merging of reads on one row, broken by any intervening call not known to be `db_side_effect_free` (KB-DATA-41), plus install-time caching of `deterministic` results and package state (KB-DATA-43). E-Q1 stays open.
2. Repeated access key: the docs show merging across different attributes of one row (`obj.bu_id`, `obj.acc_type_id`), which supports root + key as the unit of a "row access". They do not say whether `obj_bp(k).currency` after `obj_bp(k).name` costs a second load when nothing intervenes. ACC_REPEATED_ACCESS_FIX_PROMPT's fallback (root + args + attribute) is not contradicted; the merging evidence argues the narrower key misses real cases.
3. Read-after-write in script: that an OBJ read during an open modify order returns stored, not pending, values is documented only for the UI DDIC view (KB-DATA-24).
4. DELETE: no API deletes business objects; no doc covers deleting orders. Only discard (unsaved order, direct message), hide/wipe and reversal exist. DELETE appears only in the ice API (issues, solutions, tasks) and for list-table rows.
5. Commit: no doc says which order actions commit implicitly; the meaning of `no_commit` is undocumented; exact names `session.commit`/`session.rollback` are not printed as code.
6. Order API: no doc shows a full script example that creates a banking order, sets fields and runs verify/release/book; "release", "book" (as an action) and "cancel" are not documented workflow actions; no list of order status codes (only screenshot "Booked(35)").
7. The "one or two rare exceptions" of direct OBJ modification are not named.
8. Workflow definition model (states, transitions, hook points for custom script) and source type are not documented.
9. DDIC export format (task 923 Export button) and the DDIC to Oracle table mapping in general are not documented; same-name mapping is shown for `obj_bp` only.
10. Object extension accessor syntax ("Using DDICs to access object extensions", "Use EXTN to access the values of Classes, Additions and Keys") and code table usage pages are named but not in the folder.
