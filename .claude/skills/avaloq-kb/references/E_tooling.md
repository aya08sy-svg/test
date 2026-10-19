# Section E — Tooling, lifecycle, ice Workflow API, Avaloq Test Framework (SEC code TOOL)

Inputs: `verified/G5_verified.md` (main), plus tooling facts from `verified/G1_verified_partA.md`, `G1_verified_partB.md`, `G2_verified.md`, `G3_verified.md`, `G6_verified.md`. No G5 entry was REJECTED. Verifier corrections are applied. All Cite paths are relative to `source_text/`.

Path abbreviations used **only inside tables** (Cite lines always carry full paths):
- `ICE/` = `layout/03-ice-workflow/AvaloqICE/`
- `WAS/` = `layout/03-ice-workflow/AvaloqICE/workflow_api_all_subpages/`
- `ATF/` = `layout/04-test-framework/pages/`

## What a model must know first

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

## E1 Source lifecycle

### KB-TOOL-01 ice Workbench is the development, revision-control and deployment tool
- Fact: The ice Workbench is the tool for customising the Avaloq Banking Suite. It provides database development tooling, development processes, revision control, parallel development, a guided best-practice workflow, and build and deployment mechanisms.
- Means: the source lifecycle (check-out, check-in, audit, integration, release) is managed in ice, not in git.
- Cite: layout/03-ice-workflow/AvaloqICE/avaloq_ice_workbench.txt p.1 "Avaloq ice Workbench"
- Basis: STATED
- VERIFY: Q04 EXTENDS — lifecycle managed in ice. Q35 PARTIAL — ice is the IDE; no grammar file or language server is mentioned here.
- From: G5-01

### KB-TOOL-02 ice tools and interfaces (most are only named)
- Fact: ice Workbench lists these tools: ice Download 2 utility, ice Import Export utility, ice workflow API, ice release administration interface, ice Workbench SDK. Only the workflow API is documented in the corpus. The Import Export utility (Exporting sources, Syntax), Reviews and Check-in validations pages exist in the Avaloq TOC but are not in the folder.
- Cite: layout/03-ice-workflow/AvaloqICE/avaloq_ice_workbench.txt p.1 "Tools and interfaces"; TOC gap list in verified G6 (rank 24, `notes/avaloq_toc.md` lines ~18345–18397)
- Basis: STATED
- VERIFY: Q03 PARTIAL — an export utility exists, but no file format is documented. Q34/Q35 PARTIAL — an SDK exists, no details.
- Audit use: do not assume an export file layout. It is unknown.
- From: G5-02, G6 gap table #24

### KB-TOOL-03 Work and source hierarchy
- Fact: Each solution needs at least one stream solution (one per release stream), and one task is created automatically per stream solution. Sources are checked out into a change, and a change belongs to a task. Every change has a client (CHANGE_CLIENT), an application (CHANGE_APP_ID) and a compilation database (CHANGE_DB). Sources are organised by application (e.g. AAA, ATS) and by module and component (code tables CODE_ENV_MODULE, CODE_ENV_COMPO).
- Avaloq form: `solution > stream solution > task > change > source versions`; `application > module > component > source`
- Cite: layout/03-ice-workflow/AvaloqICE/workflow_api_04_package_env_solution_ext.txt p.1 ; layout/03-ice-workflow/AvaloqICE/workflow_api_all_subpages/D4_Function_compo_get_code_compos.txt p.1 ; layout/03-ice-workflow/AvaloqICE/workflow_api_all_subpages/D2_Constants.txt p.2 "Workflow parameters" ; layout/04-test-framework/pages/01a_Avaloq_test_environment.txt p.1 "ice Workbench repository" ; layout/04-test-framework/pages/02e_Calculating_which_tests_to_execute.txt p.1 "Integration relevance"
- Basis: STATED (solution > stream solution > task; sources checked out in a change; module/component); INFERRED (that the full chain down to source versions is one strict hierarchy)
- VERIFY: Q04 EXTENDS; Q02 EXTENDS (applications, modules, components)
- From: G5-20, G5-28, G5-34, G5-56, G5-86

### KB-TOOL-04 Check-out: the components of a change are those of its checked-out sources
- Fact: The components a change edits are determined by the sources checked out in that change (exposed by `compo#get_code_compos`). Every source belongs to a component.
- Cite: layout/03-ice-workflow/AvaloqICE/workflow_api_all_subpages/D4_Function_compo_get_code_compos.txt p.1
- Basis: STATED
- VERIFY: Q04 CONFIRMS (check-out into a change); Q02 EXTENDS
- From: G5-34

### KB-TOOL-05 Task state machine: workflow actions and their start statuses
- Fact: `env_task_ext#` defines one constant per workflow action. Each action is valid from the start statuses listed below. All start statuses carry the suffix "(cust.)" (printed once at the end of multi-status cells). Its meaning, probably the customer task workflow, is not defined in the doc. Target statuses are mostly not given. The string values of the constants are not documented.
- Means: the table is STATED. The lifecycle chain below the table is INFERRED from action names and start statuses.

| Constant | Action label | Valid start status(es) |
|---|---|---|
| c_wfc_checkin_task | Check In... | Ready To Solve |
| c_wfc_create_chg_on_task | Create Change... | Ready To Solve |
| c_wfc_remove_task | – | Ready To Solve |
| c_wfc_get_task_and_chgs | – | Ready To Solve / Ready To Audit / Audited |
| c_wfc_reopen_task | Reopen Change(s)... | Ready To Solve / Ready To Audit / Audited / Audit Rejected / Integration Rejected / Business Test Rejected |
| c_wfc_audit_code | Audit Code... | Ready To Audit |
| c_wfc_send_to_integration | Send To / Resend To Integration | Audited / Integration Rejected |
| c_wfc_send_to_integration_ir | – | Audited |
| c_wfc_accept_integration | Accept Integration / Accept Integration Test | Ready To Integrate / Integration Test Running |
| c_wfc_accept_integration_man | Accept Manual Integration | Ready To Integrate Manual |
| c_wfc_reject_integration | Reject Integration... / Reject Manual Integration | Ready To Integrate / Ready To Integrate Manual |
| c_wfc_send_to_integr_test | – | Ready To Integrate |
| c_wfc_send_to_integr_man | – | Ready To Integrate / Integration Test Running |
| c_wfc_send_to_ready_to_integr | Back To Ready To Integrate | Ready To Integrate Manual |
| c_wfc_escape_integration | Escape Integration Test | Integration Test Running |
| c_wfc_reject_integration_test | – | Integration Test Running |
| c_wfc_reject_integr | Reject Integration | Integrated |
| c_wfc_reject_integrated | Back To Ready To Integrate | Integrated |
| c_wfc_send_to_business_test | – | Integrated |
| c_wfc_mark_as_solved | – | Integrated / Ready For Candidate |
| c_wfc_marked_for_candidate | – | Wait For Follow-On Task / Integrated |
| c_wfc_back_to_integrated | – | Solved / Ready For Candidate |
| c_wfc_send_to_integr_stbl | Reintegrate | Integration Rejected |
| c_wfc_accept_business_test | Accept Business Test | Business Test |
| c_wfc_reject_business_test | – | Business Test |
| c_wfc_send_to_wait_for_folo | – | Business Test |
| c_wfc_resend_to_business_test | – | Business Test Rejected |
| c_wfc_retest | – | Wait For Follow-On Task |

  INFERRED chain: Ready To Solve → (Check In) → Ready To Audit → (Audit Code) → Audited | Audit Rejected → (Send To Integration) → Ready To Integrate [→ Integration Test Running] → Integrated | Integration Rejected → [Business Test] → Ready For Candidate / Wait For Follow-On Task → Solved.
- Cite: layout/03-ice-workflow/AvaloqICE/workflow_api_all_subpages/D2_Constants.txt p.1-2 "Workflow actions"
- Basis: STATED (table); INFERRED (chain order, meaning of "(cust.)")
- VERIFY: Q04 EXTENDS
- Audit use: state-machine reference for any ice-client code. The audit-reject example sets status "Audit Rejected" (see KB-TOOL-38).
- From: G5-27

### KB-TOOL-06 Roles and the 4-eye code audit
- Fact: An `env_task_ext#` user needs at least the DEV_EXT workflow role. Some actions need more:
  - Reopen: the user is granted on the changes, or holds ADM_EXT.
  - Audit Code: the user holds CAUD_EXT, is a reviewer for the component (owner, deputy or additional reviewer), and is NOT granted on the changes being audited.
  - Check-In: the user is granted on all changes.

  The 4-eye checks also apply to programmatic execution. The recommended task-robot use cases are Send to / Reject / Accept Integration.
- Cite: layout/03-ice-workflow/AvaloqICE/workflow_api_05_package_env_task_ext.txt p.1 "Security model", "Operational notes"
- Basis: STATED
- VERIFY: Q04 EXTENDS (mandatory per-component code audit by a non-author); Q30 EXTENDS (segregation of duties)
- From: G5-24

### KB-TOOL-07 Check-in outcomes: merges, source states, audit locks
- Fact: Check-in can return:
  - merge info (MERGE_CHG_ID etc., set only if the task must be merged)
  - source version states (SOURCE_IS_CLOSED, SOURCE_IS_REVIVED)
  - the blocking task in integration

  Check-in is blocked with error 20901 "Audit locks may not be acquired for task" when other tasks in the integration phase lock the source versions. The doc does not define "closed" and "revived".
- Cite: layout/03-ice-workflow/AvaloqICE/workflow_api_all_subpages/D3_Function_task_do_wfc_action.txt p.1-2 "Return values" ; layout/03-ice-workflow/AvaloqICE/workflow_api_all_subpages/D12_Exceptions.txt p.1
- Basis: STATED
- VERIFY: Q04 EXTENDS
- From: G5-32, G5-40

### KB-TOOL-08 Code review status and findings are stored in ice
- Fact: Code review is tracked per task, change and component. The review status is OPEN, WAIT, ACK or NACK. Review findings have a resolution (OPEN, FIXED, WONT_FIX, FIX_LATER), a patch set, and a review item type (COMPONENT, SRC_CHG, INSTALL_SEQ, SRC_PRTY, ONLINE_INSTLN_OVR). This is a manual review store, not a static analyser. View columns are in KB-TOOL-35.
- Cite: layout/03-ice-workflow/AvaloqICE/workflow_api_all_subpages/E5_View_env_review_intf_v.txt p.1 ; layout/03-ice-workflow/AvaloqICE/workflow_api_all_subpages/E4_View_env_review_finding_ext_v.txt p.1
- Basis: STATED
- VERIFY: Q28 PARTIAL; Q04 EXTENDS
- Audit use: audit findings could mirror the ice finding schema (resolution enum, patch_set, per-source/per-component scope).
- From: G5-45, G5-46

### KB-TOOL-09 ADAI and its Integration Robot gate integration
- Fact: ADAI downloads installation packages from ice and builds the ACP instance. While building it may also start tests through the ATF API. When a developer sends a task to integration, the Integration Robot installs and verifies it, including construction tests, and then sets the ice status to "Integrated" or "Integration rejected". Installation errors and invalids are judged against a predefined test policy. A task can be rejected for installation or source invalids, and construction tests may then be skipped, depending on configuration.
- Cite: layout/04-test-framework/pages/01a_Avaloq_test_environment.txt p.1 "Initiate the execution of the automatic tests", "Retrieve and check the test results" ; p.2 "Error and result reporting"
- Basis: STATED
- VERIFY: Q04 EXTENDS/PARTIAL (invalids can block integration; no compile-error list); Q34 PARTIAL (validation runs on a built instance, not via a standalone CLI)
- From: G5-57, G5-59

### KB-TOOL-10 Integration is test-gated on the components a task touches
- Fact: ADAI passes the components a task affects to ATF. ATF picks the tests, and the results decide Integrated vs Integration Rejected. Failures show in ice Workbench views and ADAI reports.
- Cite: layout/04-test-framework/pages/01a_Avaloq_test_environment.txt p.2 "Automatically triggered test execution" ; layout/03-ice-workflow/AvaloqICE/workflow_api_all_subpages/D4_Function_compo_get_code_compos.txt p.1
- Basis: INFERRED (joins two doc sets; the mechanism linking ADAI to ice component data is not named)
- VERIFY: Q04 EXTENDS, Q33 CONFIRMS
- From: G5-101

### KB-TOOL-11 Pre-approve: developer-run verification valid for about 24 h
- Fact: ADAI's pre-approve action runs the Integration Robot on the developer's own instance. A successful pre-approval counts as verification for a set period, usually 24 hours excluding weekends. A task that stays unchanged, checked in and reviewed in that period is accepted immediately.
- Cite: layout/04-test-framework/pages/01a_Avaloq_test_environment.txt p.1 "Retrieve and check the test results"
- Basis: STATED
- From: G5-58

### KB-TOOL-12 ADAI reporting, email and temporary ignore
- Fact: The ADAI WebPortal reports installation errors, source/rule/migration invalids, and test failures and invalids. Reports filter by build, component, owner and team. "CT Runtime" (ABS Quality menu) shows the longest-running tests. The ice Workbench Images and Properties views show image errors. ADAI emails these for accepted and rejected integrations alike. If a rejection looks wrong, the component owner can mark a source or test as temporarily ignored in ADAI.
- Cite: layout/04-test-framework/pages/04b_Monitoring_in_adai.txt p.1 "Nightly builds", "Test execution time", "Views in ice Workbench", "Reporting via email"
- Basis: STATED
- VERIFY: Q28 PARTIAL (quality reporting, not a rule checker); Q04 EXTENDS (invalid categories: source, rule, migration)
- From: G5-97, G5-98

### KB-TOOL-13 Installation packages, keys and stream-solution status
- Fact: Releases ship as installation packages. Testing (T) and production (P) keys exist per customer (view env_install_pkg_intf_v). Stream solutions are "Open" or "Closed". When a stream solution is Closed and all its tasks are in the package, the package records solution and stream-solution data. Moving or assigning already downloaded or installed tasks, or reopening installed stream solutions, may cause warnings or errors on later downloads or installations, depending on the Avaloq Installer configuration.
- Cite: layout/03-ice-workflow/AvaloqICE/workflow_api_all_subpages/D11_Procedure_task_set_stream_cfg_id.txt p.1 "Usage note" ; layout/03-ice-workflow/AvaloqICE/workflow_api_all_subpages/E2_View_env_install_pkg_intf_v.txt p.1
- Basis: STATED; INFERRED (that keys "unlock" packages)
- VERIFY: Q04 EXTENDS
- From: G5-39, G5-43

### KB-TOOL-14 Change dependencies are change-level, not code-level
- Fact: ice knows two kinds of change dependency:
  - predecessor dependencies, which come from source versions
  - prerequisite dependencies, defined explicitly (CHANGE_PRE_CHG when a change is created)

  ice does not expose a code-level call or where-used graph.
- Cite: layout/03-ice-workflow/AvaloqICE/workflow_api_all_subpages/E7_View_env_stream_solution_chg_dep_intf_v.txt p.1 ; layout/03-ice-workflow/AvaloqICE/workflow_api_all_subpages/D2_Constants.txt p.2 "Workflow parameters"
- Basis: STATED
- VERIFY: Q05 PARTIAL
- From: G5-28, G5-48

### KB-TOOL-15 Task attributes are editable only in editable statuses
- Fact: A task attribute can be changed only while the task is in a workflow status that allows editing, e.g. Ready-to-Solve or Audited. `task#set_external_ref` explicitly uses the "Modify Task Properties" workflow.
- Cite: layout/03-ice-workflow/AvaloqICE/workflow_api_05_package_env_task_ext.txt p.2 "Subprograms" (create_task row) ; layout/03-ice-workflow/AvaloqICE/workflow_api_all_subpages/D8_Procedure_task_set_external_ref.txt p.1
- Basis: STATED
- From: G5-25, G5-38

---

## E2 ice Workflow API catalogue (PL/SQL)

### KB-TOOL-16 Purpose, language and call form of the ice Workflow API
- Fact: The ice Workflow API is a set of supplied **PL/SQL** packages and views that let third-party systems integrate with the ice Server. With it a client can:
  - query tasks, changes, source versions, solutions, stream solutions and issues
  - create and modify tasks, and run task workflow actions
  - create, modify, delete, associate and dissociate issues
  - create and delete solutions and stream solutions

  Every example calls it through the schema prefix `e.` with named notation (`=>`) inside anonymous PL/SQL blocks.
- Avaloq form: `begin e.env_issue_ext#.issue#remv(i_issue_uri => 'https://ticket.mycompany.com/browse/TICKET-123'); end;`
- Means: a call to `e.env_*_ext#.*` is an ice Server development-lifecycle call, not banking logic.
- Cite: layout/03-ice-workflow/AvaloqICE/ice_workflow_api_introduction.txt p.1 "ice Workflow API — Introduction", "Prerequisite knowledge" ; layout/03-ice-workflow/AvaloqICE/workflow_api_01_overview_packages_views.txt p.1
- Basis: STATED (PL/SQL, scope); INFERRED (that `e` is the ice Server schema)
- VERIFY: Q04 EXTENDS
- From: G5-03, G5-04

### KB-TOOL-17 Misuse: env_task_ext# is not a banking-order workflow API
- Fact: Secondary notes claim script code moves an order's workflow with `env_task_ext#.task_do_wfc_action(i_task_id, i_action_id)`. That claim is wrong on three counts:
  1. The package is the ice API for development tasks.
  2. The real name is the function `env_task_ext#.task#do_wfc_action`, which takes `i_wfc_action varchar2` (an action name, not an ID) and returns `t_wfc_param_tab`.
  3. Banking orders run workflow actions through the order DDIC method `do_wfc_action` (e.g. on DOC_PAY).
- Cite: layout/03-ice-workflow/AvaloqICE/ice_workflow_api_introduction.txt p.1 ; layout/03-ice-workflow/AvaloqICE/workflow_api_all_subpages/D3_Function_task_do_wfc_action.txt p.1 "Signature" ; paged/text/what-are-data-dictionaries.txt p.6
- Basis: STATED
- VERIFY: Q18 CONTRADICTS (the secondary claim)
- Audit use: error rule. Flag `env_task_ext#` inside a banking script package. `<order ddic>.do_wfc_action(...)` is a DB side effect.
- From: G6-67

### KB-TOOL-18 Terms of use
- Fact: Only technical user accounts created for the purpose may call the API. Customer applications (e.g. scripts) that access the ice Server must be certified by Avaloq before going live and must use resources economically. Avaloq can change the API, and customers adapt at their own expense.
- Cite: layout/03-ice-workflow/AvaloqICE/ice_workflow_api_introduction.txt p.1 "Terms of use", "Disclaimer"
- Basis: STATED
- VERIFY: Q29 PARTIAL (public but not guaranteed stable)
- From: G5-06

### KB-TOOL-19 Naming patterns in Avaloq PL/SQL APIs
- Fact: These conventions are used consistently but never stated as rules:
  - package names end in `#`
  - subprograms are named `<object>#<action>` (issue#upd, task#set_name, solution#create_ssol)
  - prefixes: `i_` input, `o_` output, `l_` local, `c_` constant, `t_` type
  - views end in `_v`; external API objects contain `_ext`; interface views end in `_intf_v`
  - abbreviations: remv, upd, descn, prio
  - examples use leading-comma parameter lists and `:= null` defaults
- Cite: layout/03-ice-workflow/AvaloqICE/workflow_api_05_package_env_task_ext.txt p.1 "Subprograms" ; layout/03-ice-workflow/AvaloqICE/workflow_api_01_overview_packages_views.txt p.1 ; layout/03-ice-workflow/AvaloqICE/workflow_api_all_subpages/A1_Procedure_new.txt p.1 "Signature"
- Basis: INFERRED (consistent usage across all packages)
- VERIFY: Q31 EXTENDS
- Audit use: naming validator for PL/SQL sources.
- From: G5-05, G5-11

### KB-TOOL-20 Commit semantics differ by package
- Fact: Every subprogram in `env_issue_ext#` and `env_solution_ext#` commits or rolls back itself. The `env_task_ext#` page says "None of the functions in the package do commit or roll back", so the client must commit after success. That this also covers its procedures (task#remove, task#set_*) is INFERRED: the doc does not say so, but every example ends in `commit;`.
- Cite: layout/03-ice-workflow/AvaloqICE/workflow_api_05_package_env_task_ext.txt p.1 "Operational notes" ; layout/03-ice-workflow/AvaloqICE/workflow_api_02_package_env_issue_ext.txt p.1 "Operational notes" ; layout/03-ice-workflow/AvaloqICE/workflow_api_04_package_env_solution_ext.txt p.1 "Operational notes"
- Basis: STATED (issue/solution commit; task functions do not); INFERRED (task procedures do not commit)
- VERIFY: Q26 EXTENDS
- Audit use: an `env_task_ext#` call must be followed by `commit` in the caller. `env_issue_ext#` and `env_solution_ext#` calls end the transaction implicitly, so do not put them inside a larger transaction (INFERRED).
- From: G5-09

### KB-TOOL-21 The four packages and ten views
- Fact: Packages:
  - `env_issue_ext#`: issues
  - `env_item_expr_ext#`: item-expression queries
  - `env_solution_ext#`: create and delete solutions
  - `env_task_ext#`: workflow actions and task properties

  Views (read access): env_chg_ext_v, env_install_pkg_intf_v, env_issue_ext_v, env_review_finding_ext_v, env_review_intf_v, env_solution_ext_v, env_stream_solution_chg_dep_intf_v, env_stream_solution_ext_v, env_stream_solution_ext_hist_v, env_task_ext_v. These are ice Server views, not ACP banking tables.
- Cite: layout/03-ice-workflow/AvaloqICE/workflow_api_01_overview_packages_views.txt p.1 "Packages", "Database views" ; layout/03-ice-workflow/AvaloqICE/workflow_api_06_database_views.txt p.1
- Basis: STATED
- VERIFY: Q17 EXTENDS (indirect)
- From: G5-07, G5-08

### KB-TOOL-22 Parameter-mode and signature caveats (applies to all tables below)
- Fact: No ice API signature prints IN/OUT. IN is the PL/SQL default, so every mode below is marked "IN (INFERRED)". Some signatures disagree with their parameter tables:
  - The `create_task` signatures show no `:=` defaults, although the parameter tables give defaults and an example passes only `i_stream_solution_id`.
  - `task#do_wfc_action.i_task_id` is "Number" in the table but `env_task#.t_task` in the signature.
  - `i_comment` is Default "none" / Mandatory "No" in the table but `:= null` in the signature.

  The types `env_task#.t_task`, `env_def#.t_pls_tab` and `t_varchar2_tab` are not defined. The examples assign `t_task` to `pls_integer`, which suggests an integer subtype (INFERRED).
- Cite: layout/03-ice-workflow/AvaloqICE/workflow_api_all_subpages/D5_Function_create_task.txt p.1-2 ; layout/03-ice-workflow/AvaloqICE/workflow_api_all_subpages/D3_Function_task_do_wfc_action.txt p.1 "Parameter description", "Signature"
- Basis: STATED (discrepancies); INFERRED (modes, t_task subtype)
- From: G5-31, G5-35, G5-36 (G5 open questions 2–4)

### KB-TOOL-23 Package env_issue_ext# — issues (commits itself)
- Fact: The technical user needs the WB – Manage Tasks or WB – Administrator role. Type `t_issue_uri` = varchar2(1000), the URI that links the ice issue to an external ticket. Every subprogram commits or rolls back itself.

| Subprogram | Kind | Params (name type mode default) | Returns | Data effect | Commits? | Cite (WAS/) |
|---|---|---|---|---|---|---|
| new | procedure | i_issue_uri t_issue_uri IN(INFERRED) mandatory — unique, case-sensitive, not validated; i_issue_key varchar2 IN(INFERRED) mandatory — unique, case-insensitive, stored upper, max 100, [A-Z0-9-], first char A-Z/0-9; i_title varchar2 IN(INFERRED) mandatory, max 1000; i_prio varchar2 IN(INFERRED) := null, max 100; i_ticket_type varchar2 IN(INFERRED) := null, max 100 | – | CREATE issue | yes (package) | A1_Procedure_new.txt p.1 |
| issue#upd | procedure | i_issue_uri t_issue_uri IN(INFERRED); i_title varchar2 IN(INFERRED); i_prio varchar2 IN(INFERRED) mandatory, null clears; i_stream_solution_id env_solution_ext#.t_stream_solution_id IN(INFERRED) mandatory, NULL dissociates; i_ticket_type varchar2 IN(INFERRED) := null — null keeps, single space resets to NULL | – | MODIFY issue | yes | A2_Procedure_issue_upd.txt p.1 |
| issue#remv | procedure | i_issue_uri t_issue_uri IN(INFERRED) | – | DELETE issue (only if not associated with any stream solution) | yes | A3_Procedure_issue_remv.txt p.1 |
| issue#associate | procedure | i_issue_uri t_issue_uri IN(INFERRED); i_stream_solution_id env_solution_ext#.t_stream_solution_id IN(INFERRED) | – | MODIFY (label INFERRED): links issue (only if not already associated with another) | yes | A4_Procedure_issue_associate.txt p.1 |
| issue#dissociate | procedure | i_issue_uri t_issue_uri IN(INFERRED) | – | MODIFY (label INFERRED): unlinks from current stream solution | yes | A5_Procedure_issue_dissociate.txt p.1 |

- Avaloq form:
```
begin
  e.env_issue_ext#.new(
     i_issue_uri   => 'https://ticket.mycompany.com/browse/TICKET-123'
  , i_issue_key    => 'TICKET-123'
  , i_title        => 'Some functionality broken'
  , i_prio         => 'Urgent'
  , i_ticket_type => 'Bug'
  );
end;
```
- Cite: layout/03-ice-workflow/AvaloqICE/workflow_api_02_package_env_issue_ext.txt p.1 "Security model", "Types", "Subprograms" ; layout/03-ice-workflow/AvaloqICE/workflow_api_all_subpages/A1_Procedure_new.txt p.1 ; A2_Procedure_issue_upd.txt p.1 ; A3_Procedure_issue_remv.txt p.1 ; A4_Procedure_issue_associate.txt p.1 ; A5_Procedure_issue_dissociate.txt p.1 (all under layout/03-ice-workflow/AvaloqICE/workflow_api_all_subpages/)
- Basis: STATED (signatures, effects, commit); INFERRED (modes; MODIFY label for associate/dissociate)
- From: G5-10, G5-11, G5-12, G5-13, G5-14, G5-15

### KB-TOOL-24 Package env_item_expr_ext# — item-expression queries (READ)
- Fact: The package queries the ice Server with the same item expressions the ice Workbench uses for finding and filtering. It returns all primary keys of the requested item type that match. Role: at least DEV_EXT. Its only subprogram is `eval`. The caller must close the returned cursor ("must be closed manually").

| Subprogram | Kind | Params | Returns | Data effect | Commits? | Cite (WAS/) |
|---|---|---|---|---|---|---|
| eval | function | i_item_type_id pls_integer IN(INFERRED) mandatory; i_expr varchar2 IN(INFERRED) mandatory | t_id_cur (ref cursor of t_id_rec(id number(9))) | READ | n/a (read only; not stated) | B2_Function_eval.txt p.1 |

  Constants (item types): c_task_expr = 22, c_chg_expr = 1, c_source_expr = 6, c_solution_expr = 23, c_stream_solution_expr = 24, c_issue_expr = 32.
  Types: `type t_id_rec is record(id number(9)); type t_id_cur is ref cursor return t_id_rec;`
- Cite: layout/03-ice-workflow/AvaloqICE/workflow_api_03_package_env_item_expr_ext.txt p.1 "Security model", "Operational notes" ; layout/03-ice-workflow/AvaloqICE/workflow_api_all_subpages/B1_Constants_env_item_expr_ext.txt p.1 "constants" ; layout/03-ice-workflow/AvaloqICE/workflow_api_all_subpages/B2_Function_eval.txt p.1 "Return value", "Signature"
- Basis: STATED; INFERRED (modes)
- Audit use: cursor-leak rule. Every `eval` result must reach `close <cursor>` on all paths.
- From: G5-16, G5-17, G5-18

### KB-TOOL-25 Item-expression syntax examples and fetch-loop pattern
- Fact: The examples use `'is_cwait;rel(1.2.3)'` (changes in "Ready to Audit" in release 1.2.3; the meaning of `is_cwait` is INFERRED from the heading) and `'task(1234)'` (changes of task 1234). Results are fetched in a loop with `exit when %notfound`, then the cursor is closed. The full expression syntax is only in the ice online help, which is not in the corpus.
- Avaloq form:
```
declare
  l_result e.env_item_expr_ext#.t_id_cur;
  l_result_rec e.env_item_expr_ext#.t_id_rec;
begin
  l_result := e.env_item_expr_ext#.eval(
     i_item_type_id => e.env_item_expr_ext#.c_chg_expr
  , i_expr           => 'is_cwait;rel(1.2.3)'
  );
  loop
     fetch l_result into l_result_rec;
     exit when l_result%notfound;
     -- process id in l_result_rec
  end loop;
  close l_result; -- Close Cursor after read
end;
```
- Cite: layout/03-ice-workflow/AvaloqICE/workflow_api_all_subpages/B3_Examples_env_task_ext.txt p.2 "Get all changes in release in status 'Ready to Audit'", "Find all changes for task 1234" ; layout/03-ice-workflow/AvaloqICE/workflow_api_all_subpages/B2_Function_eval.txt p.1 "Parameter description"
- Basis: STATED; INFERRED (meaning of `is_cwait`)
- From: G5-19

### KB-TOOL-26 Package env_solution_ext# — solutions (commits itself)
- Fact: The package creates and deletes solutions. Each solution needs at least one stream solution, and one task is created automatically per stream solution. Role: WB – Manage Tasks or WB – Administrator. Types: `t_solution_id pls_integer`, `t_stream_solution_id pls_integer`.

| Subprogram | Kind | Params | Returns | Data effect | Commits? | Cite (WAS/) |
|---|---|---|---|---|---|---|
| new | function | i_name varchar2 IN(INFERRED) mandatory, max 80; i_solution_owner varchar2 IN(INFERRED) mandatory; i_task_owner varchar2 IN(INFERRED) mandatory; i_stream_solution_tab t_varchar2_tab (table of varchar2(4000)) IN(INFERRED) mandatory — release stream USER_IDs, case-insensitive, ≥1; i_release_domain varchar2 IN(INFERRED) := null | t_solution_id | CREATE solution + one stream solution per stream + one task each | yes | C1_Function_new_env_solution_ext.txt p.1 |
| solution#remv | procedure | i_solution_id t_solution_id IN(INFERRED) | – | DELETE solution, stream solutions, tasks (only if no task has changes containing sources); issues dissociated automatically | yes | C2_Procedure_solution_remv.txt p.1 |
| solution#create_ssol | function | i_solution_id t_solution_id IN(INFERRED); i_stream_user_id varchar2 IN(INFERRED) | t_stream_solution_id | CREATE stream solution on existing solution | yes | C3_Function_solution_create_ssol.txt p.1 |

- Avaloq form:
```
declare
  l_solution_id e.env_solution_ext#.t_solution_id;
begin
  l_solution_id := e.env_solution_ext#.new(
     i_name                => 'Solution- and task-name'
  , i_solution_owner       => 'xibabc'
  , i_task_owner           => 'xibxyz'
  , i_stream_solution_tab => e.t_varchar2_tab('Main','FP_1','FP_2')
  , i_release_domain       => 'iceb'
  );
end;
```
- Cite: layout/03-ice-workflow/AvaloqICE/workflow_api_04_package_env_solution_ext.txt p.1 ; layout/03-ice-workflow/AvaloqICE/workflow_api_all_subpages/C1_Function_new_env_solution_ext.txt p.1 ; C2_Procedure_solution_remv.txt p.1 ; C3_Function_solution_create_ssol.txt p.1 (under layout/03-ice-workflow/AvaloqICE/workflow_api_all_subpages/)
- Basis: STATED; INFERRED (modes)
- From: G5-20, G5-21, G5-22, G5-23

### KB-TOOL-27 Package env_task_ext# — tasks and workflow actions (caller commits)
- Fact: Role: at least DEV_EXT, plus more per action (KB-TOOL-06). The functions do not commit, and the procedures are INFERRED not to commit either (KB-TOOL-20). Whether a workflow action can run depends on the task status, the user's permissions and the task attributes.

| Subprogram | Kind | Params | Returns | Data effect | Commits? | Cite (WAS/) |
|---|---|---|---|---|---|---|
| task#do_wfc_action | function | i_task_id env_task#.t_task (table: Number) IN(INFERRED) mandatory; i_wfc_action varchar2 IN(INFERRED) mandatory; i_param t_wfc_param_tab IN(INFERRED) := null; i_comment varchar2 IN(INFERRED) := null (table: Default "none", Mandatory "No") — written to task history | t_wfc_param_tab | MODIFY task status; CREATE change for c_wfc_create_chg_on_task (returns CHG_ID) | no — caller commits | D3_Function_task_do_wfc_action.txt p.1-2 |
| compo#get_code_compos | function | i_chg_id env_chg.id%type IN(INFERRED) | env_def#.t_pls_tab (component IDs) | READ | n/a | D4_Function_compo_get_code_compos.txt p.1 |
| create_task (overload 1, on release) | function | i_name env_task.name%type mandatory; i_descn env_task.descn%type default null; i_release env_release.user_id%type mandatory; i_resp_env_user env_user.oracle_user%type default calling user; i_env_prio code_env_prio.intl_id%type default c_task_prio_normal; i_task_end_date date default null; i_external_ref env_task.external_ref%type default null — all IN(INFERRED); defaults from table only | env_task#.t_task | CREATE task | no — caller commits | D5_Function_create_task.txt p.1 |
| create_task (overload 2, on stream solution) | function | as overload 1 but i_stream_solution_id env_task.env_stream_cfg_id%type mandatory replaces i_release; i_name defaults to solution name; i_resp_env_user defaults to solution owner | env_task#.t_task | CREATE task | no — caller commits | D5_Function_create_task.txt p.1-2 |
| task#remove | procedure | i_task_id number IN(INFERRED) | – | DELETE task (only in "Ready To Solve"; Release Manager or Admin rights) | no (INFERRED) | D6_Procedure_task_remove.txt p.1 |
| task#set_due_date | procedure | i_task_id number; i_due_date date — IN(INFERRED) | – | MODIFY | no (INFERRED) | D7_Procedure_task_set_due_date.txt p.1 |
| task#set_external_ref | procedure | i_task_id number; i_external_ref env_task.external_ref%type (max 200) — IN(INFERRED) | – | MODIFY via "Modify Task Properties" workflow | no (INFERRED) | D8_Procedure_task_set_external_ref.txt p.1 |
| task#set_name | procedure | i_task_id number; i_name env_task.name%type (max 80) — IN(INFERRED) | – | MODIFY | no (INFERRED) | D9_Procedure_task_set_name.txt p.1 |
| task#set_responsible_user | procedure | i_task_id number; i_user varchar2 — IN(INFERRED) | – | MODIFY (does not change owners of existing changes) | no (INFERRED) | D10_Procedure_task_set_responsible_user.txt p.1 |
| task#set_stream_cfg_id | procedure | i_task_id pls_integer; i_stream_cfg_id pls_integer — IN(INFERRED) | – | MODIFY: assign/move task to a stream solution. Needs TM_EXT or ADM_EXT; source and target "Open"; same release stream; task type "Customer Development"; not "Integration Test Running" | no (INFERRED) | D11_Procedure_task_set_stream_cfg_id.txt p.1 |

- Cite: layout/03-ice-workflow/AvaloqICE/workflow_api_05_package_env_task_ext.txt p.1-2 "Security model", "Operational notes", "Subprograms" ; layout/03-ice-workflow/AvaloqICE/workflow_api_all_subpages/D3_Function_task_do_wfc_action.txt p.1-2 ; D4..D11 (under layout/03-ice-workflow/AvaloqICE/workflow_api_all_subpages/) p.1
- Basis: STATED (signatures, rules, effects); INFERRED (modes; no-commit for procedures)
- Audit use: `%type` anchoring against tables (env_task, env_release, code_env_prio.intl_id). Code tables appear as `code_*` with an `intl_id` column.
- From: G5-25, G5-31, G5-34, G5-35, G5-36, G5-37, G5-38, G5-39

### KB-TOOL-28 env_task_ext# types: workflow parameter structure
- Fact: Workflow parameters are a key/value structure. Keys must be unique. No nulls are allowed in the tab or entry objects, and for any action that needs parameters the whole structure must be initialised. Values are varchar2(4000), measured in bytes.
- Avaloq form:
```
type t_wfc_param_values is table of varchar2(4000);
type t_wfc_param_entry is object (
   key   varchar2(100),
   value t_wfc_param_values
);
type t_wfc_param_tab is table of t_wfc_param_entry;
```
- Cite: layout/03-ice-workflow/AvaloqICE/workflow_api_all_subpages/D1_Types.txt p.1
- Basis: STATED
- From: G5-26

### KB-TOOL-29 Workflow parameter keys per action
- Fact: Most actions take no parameters (`i_param` may be null). Three need them: code audit, create change, and reopen (only when not all related components should be reopened). Every key of such an action must be supplied, even when its value is null.

| Action | Parameter constant (key) | Notes |
|---|---|---|
| c_wfc_reopen_task | c_param_reopen#change (CHANGE); c_param_reopen#compo (COMPONENT) | |
| c_wfc_audit_code | c_param_caudit#comment (COMMENT); c_param_caudit#accept (ACCEPT); c_param_caudit#compo (COMPONENT); c_param_caudit#change (CHANGE) | COMMENT nullable; ACCEPT "true"/"false" |
| c_wfc_create_chg_on_task | c_param_new_chg#name (CHANGE_NAME); #descn (CHANGE_DESCN); #db (CHANGE_DB); #pre_chg (CHANGE_PRE_CHG); #client_id (CHANGE_CLIENT); #app_id (CHANGE_APP_ID); #granted_user (CHANGE_GRANTED_USER) | DESCN, DB (compilation database), PRE_CHG (change dependencies) nullable; GRANTED_USER optional, up to 3, semicolon-separated |

- Cite: layout/03-ice-workflow/AvaloqICE/workflow_api_all_subpages/D2_Constants.txt p.2 "Workflow parameters" ; layout/03-ice-workflow/AvaloqICE/workflow_api_05_package_env_task_ext.txt p.1 intro
- Basis: STATED
- VERIFY: Q05 PARTIAL (change-level pre-change dependencies); Q02 EXTENDS (change → client, application)
- Audit use: an ice-client validator requires a full i_param only for audit, create change and (optionally) reopen.
- From: G5-28, G5-105

### KB-TOOL-30 Reopen: a null i_param and an empty i_param mean different things
- Fact: For `c_wfc_reopen_task`, omitting `i_param` reopens all changes and components. Passing an empty collection, `e.t_wfc_param_tab()`, reopens only the changes and none of the components.
- Cite: layout/03-ice-workflow/AvaloqICE/workflow_api_all_subpages/D2_Constants.txt p.2 "Workflow parameters"
- Basis: STATED
- Audit use: flag `i_param => null` vs `i_param => e.t_wfc_param_tab()` on reopen as semantically different (a possible bug source).
- From: G5-29

### KB-TOOL-31 Task priority constants
- Fact: Task priority constants (varchar2) for `create_task.i_env_prio`: c_task_prio_normal 'NL', c_task_prio_urgent 'U', c_task_prio_urgent_due_date 'U_DD', c_task_prio_project_blocker 'PB', c_task_prio_top_urgent 'TU'.
- Cite: layout/03-ice-workflow/AvaloqICE/workflow_api_all_subpages/D2_Constants.txt p.2 "Task priorities"
- Basis: STATED
- From: G5-30

### KB-TOOL-32 task#do_wfc_action return keys
- Fact: Return keys by action:
  - c_wfc_create_chg_on_task: CHG_ID.
  - c_wfc_get_task_and_chgs: CHG_ID, GRANTEE (the removed grantee when the maximum is exceeded).
  - c_wfc_checkin_task: SOURCE_ID, SOURCE_NAME, SOURCE_TYPE, MERGE_CHG_ID, MERGE_CHG_NAME, MERGE_TASK_ID, TASK_IN_INTEGRATION_ID, CHG_ID, COMPO_NAME, CHANGE_IN_INTEGRATION_AUDITORS, TASK_IN_INTEGRATION_RESP, SOURCE_IS_CLOSED, SOURCE_IS_REVIVED, MERGE_SOURCE_IS_CLOSED, MERGE_SOURCE_IS_REVIVED, TASK_IN_INTEGRATION_STATUS. An exception is raised if check-in is blocked.
  - c_wfc_reopen_task: CHANGE, COMPONENT (echoed from the input).
- Cite: layout/03-ice-workflow/AvaloqICE/workflow_api_all_subpages/D3_Function_task_do_wfc_action.txt p.1-2 "Return values"
- Basis: STATED
- VERIFY: Q04 EXTENDS
- From: G5-32

### KB-TOOL-33 env_task_ext# exceptions
- Fact: 20888 has variable text. 20901, "Audit locks may not be acquired for task", is raised when check-in is blocked because source versions are locked by tasks in the integration phase. The doc prints bare numbers.
- Cite: layout/03-ice-workflow/AvaloqICE/workflow_api_all_subpages/D12_Exceptions.txt p.1
- Basis: STATED (codes); INFERRED (ORA- prefix and `raise_application_error` mechanism, from the 20xxx range)
- VERIFY: Q11 EXTENDS
- Audit use: an ice client should handle -20901 (retry later) separately from -20888.
- From: G5-40

### KB-TOOL-34 Views require the WB - Developer role
- Fact: Every API view requires at least the WB - Developer role for the selecting user.
- Cite: layout/03-ice-workflow/AvaloqICE/workflow_api_all_subpages/E1_View_env_chg_ext_v.txt p.1 "Security model" (identical in E2–E10)
- Basis: STATED
- From: G5-41

### KB-TOOL-35 View catalogue (READ), compact
- Fact: Column lists of the ten ice API views. Types are given where printed. All views are under `e.`.

| View | Content | Columns | Cite (WAS/) |
|---|---|---|---|
| env_chg_ext_v | changes | chg_id number(9), chg_name varchar2(80), chg_descn varchar2(2000) (deprecated), chg_open_date date, task_id number(9), chg_grantees varchar2(43) (comma-separated Oracle users), chg_client_user_id varchar2(15), chg_app_user_id varchar2(8) | E1_View_env_chg_ext_v.txt p.1 |
| env_install_pkg_intf_v | installation packages ↔ changes/tasks, only packages with a T or P key | pkg_id, chg_id, task_id, key_type varchar2(1), key_valid_until (testing keys only), key_for_customer varchar2(15), key_creation_date, key_created_by varchar2(10), pkg_creation_date, pkg_created_by | E2_View_env_install_pkg_intf_v.txt p.1 |
| env_issue_ext_v | issues | id number(9) (technical, not used by API), issue_key varchar2(100) (unique per partner), issue_uri varchar2(1000), title varchar2(1000), prio varchar2(100), stream_solution_id number(9) (null = not associated), partner_id number(9), ticket_type varchar2(100) | E3_View_env_issue_ext_v.txt p.1 |
| env_review_finding_ext_v | review findings | task_id, patch_set number(9), review_item_type varchar2(30) (COMPONENT, SRC_CHG, INSTALL_SEQ, SRC_PRTY, ONLINE_INSTLN_OVR), compo varchar2(30), source_id, chg_id, source_name varchar2(160), source_type varchar2(30), summary varchar2(4000), author varchar2(10), author_name varchar2(70), published ('+'/null), published_tswtz timestamp(6) with time zone, resolution varchar2(30) (OPEN, FIXED, WONT_FIX, FIX_LATER) | E4_View_env_review_finding_ext_v.txt p.1 |
| env_review_intf_v | review status per task/change/component | task_id (null for legacy), chg_id, compo varchar2(30), review_status varchar2(4) (OPEN, WAIT, ACK, NACK), review_date, reviewed_by_env_user_id, reviewed_by_oracle_user, reviewed_by_name | E5_View_env_review_intf_v.txt p.1 |
| env_solution_ext_v | solutions | id number(9), name varchar2(80), solution_owner varchar2(10), release_domain varchar2(64), partner_id number(9), document_xml clob (latest DOCUMENTATION version) | E6_View_env_solution_ext_v.txt p.1 |
| env_stream_solution_chg_dep_intf_v | dependent changes, one level (predecessor + prerequisite; no stream-solution deps; self rows possible) | stream_solution_id, dep_chg_id, dep_task_id, dep_task_wfc_status_id, dep_task_wfc_status varchar2(40), dep_stream_solution_id | E7_View_env_stream_solution_chg_dep_intf_v.txt p.1 |
| env_stream_solution_ext_hist_v | history: creation, status changes, issue moves | stream_solution_id, timestamp_with_tz, wfc_status_id, wfc_status varchar2(40), issue_move char(1) ('+' in, '-' out, null none), partner_id | E8_View_env_stream_solution_ext_hist_v.txt p.1 |
| env_stream_solution_ext_v | stream solutions | id, solution_id, release_stream varchar2(20), wfc_status varchar2(40) (values seen: "Open", "Closed", 'CLOSED'), stream_solution_owner varchar2(10), partner_id | E9_View_env_stream_solution_ext_v.txt p.1 |
| env_task_ext_v | tasks | task_id, task_name varchar2(80), task_descn varchar2(2000), external_ref varchar2(200), task_priority varchar2(80), task_responsible varchar2(10), task_issuer, task_wfc_status_user_id varchar2(40), task_wfc_status_name, last_code_modification date (updated whenever a change or source version on the task changes), task_stream varchar2(20), task_release varchar2(25), task_start_date, task_end_date, task_open_date, task_close_date, stream_solution_id, partner_id, partner_user_id varchar2(15) | E10_View_env_task_ext_v.txt p.1 |

- Cite: layout/03-ice-workflow/AvaloqICE/workflow_api_all_subpages/E1_View_env_chg_ext_v.txt … E10_View_env_task_ext_v.txt p.1 "Attributes" ; status values also D11_Procedure_task_set_stream_cfg_id.txt p.1 and E8 example
- Basis: STATED
- VERIFY: Q01 EXTENDS (source name ≤160, type ≤30); Q05 PARTIAL (E7); Q28 PARTIAL (E4)
- Audit use: when walking E7 recursively, guard against stream_solution_id = dep_stream_solution_id cycles. '+'/null is the Avaloq boolean flag convention.
- From: G5-42, G5-43, G5-44, G5-45, G5-46, G5-47, G5-48, G5-49, G5-50, G5-51

### KB-TOOL-36 Reference implementation: JIRA integration context and requirements
- Fact: The reference implementation integrates Atlassian JIRA with the ice Workbench server. It replicates issues into ice, creates solutions and stream solutions, and syncs JIRA state from stream-solution state. Targets: sync within 30 s, replication and creation within 5 s, about 50 concurrent users, 5000 issues. An ice failure must not block JIRA, and syncs and errors are logged. Before this, traceability depended on developers typing the issue ID into change titles.
- Cite: layout/03-ice-workflow/AvaloqICE/workflow_api_all_subpages/F1_Context.txt p.1 ; layout/03-ice-workflow/AvaloqICE/workflow_api_all_subpages/F2_Requirements.txt p.1
- Basis: STATED
- From: G5-52

### KB-TOOL-37 Reference implementation: Java plug-in, REST client to PL/SQL, polling
- Fact: The plug-in is Java. Post functions extend AbstractJiraFunctionProvider and triggers implement WorkflowTrigger. An `iceRestClient` IssueClient marshals data to the `env_issue_ext#.new()` PL/SQL procedure. A SchedulerService job polls ENV_STREAM_SOLUTION_EXT_HIST_V for stream solutions changed since the last poll. Errors are wrapped in WorkflowException. The REST layer is named but not documented.
- Avaloq form:
```
select stream_solution_id as id, timestamp_with_tz, wfc_status, issue_move
from   e.env_stream_solution_ext_hist_v
where stream_solution_id = 1000
and    timestamp_with_tz > systimestamp - 1/24
order by stream_solution_id, timestamp_with_tz;
```
- Cite: layout/03-ice-workflow/AvaloqICE/workflow_api_all_subpages/F4_Code.txt p.1 ; layout/03-ice-workflow/AvaloqICE/workflow_api_all_subpages/F3_Software_Architecture.txt p.1 ; layout/03-ice-workflow/AvaloqICE/workflow_api_all_subpages/E8_View_env_stream_solution_ext_hist_v.txt p.1
- Basis: STATED; INFERRED (that the ice API has no push events, from "the plug-in needs to poll")
- From: G5-49, G5-53

### KB-TOOL-38 Coding pattern: build t_wfc_param_tab, call do_wfc_action, commit
- Fact: The reference pattern builds each `t_wfc_param_entry` with a constructor (key constant + `t_wfc_param_values(...)`), collects them into `e.t_wfc_param_tab(...)`, calls `e.env_task_ext#.task#do_wfc_action`, and ends with `commit;`. The example rejects a code audit on task 123, setting status "Audit Rejected". One B3 example declares `t_wfc_param_tab` without the `e.` prefix. The "Create a new change on a task" example is clipped at the right margin in the source, so its parameter values are unknown.
- Avaloq form:
```
declare
  l_result e.t_wfc_param_tab;
  l_param_e1 e.t_wfc_param_entry :=
     e.t_wfc_param_entry(e.env_task_ext#.c_param_caudit#comment, e.t_wfc_param_values('Task robot comment'));
  l_param_e2 e.t_wfc_param_entry :=
     e.t_wfc_param_entry(e.env_task_ext#.c_param_caudit#accept, e.t_wfc_param_values('false'));
  l_param_e3 e.t_wfc_param_entry :=
     e.t_wfc_param_entry(e.env_task_ext#.c_param_caudit#compo, e.t_wfc_param_values(789));
  l_param_e4 e.t_wfc_param_entry :=
     e.t_wfc_param_entry(e.env_task_ext#.c_param_caudit#change, e.t_wfc_param_values(456));
  l_param e.t_wfc_param_tab := e.t_wfc_param_tab(l_param_e1, l_param_e2, l_param_e3, l_param_e4);
begin
  l_result := e.env_task_ext#.task#do_wfc_action(
     i_task_id      => 123
  , i_wfc_action => e.env_task_ext#.c_wfc_audit_code
  , i_param         => l_param
  );
  commit;
end;
```
- Cite: layout/03-ice-workflow/AvaloqICE/workflow_api_all_subpages/B3_Examples_env_task_ext.txt p.1 "Send task to integration", "Audit code of a task" ; p.2 (clipped example)
- Basis: STATED
- From: G5-33

### KB-TOOL-39 Coding pattern: create_task with named args and commit
- Fact: Example: `create_task` on release 'REL_123.IN' with an urgent priority constant and due date `trunc(sysdate) +4`, result in a `pls_integer` local, then `commit;`. The minimal stream-solution form passes only `i_stream_solution_id`.
- Avaloq form:
```
declare
  l_task_id pls_integer;
begin
  l_task_id := e.env_task_ext#.create_task(
     i_name            => 'Test task'
  , i_descn            => 'Test description'
  , i_release          => 'REL_123.IN'
  , i_resp_env_user    => 'XABC'
  , i_env_prio         => e.env_task_ext#.c_task_prio_urgent
  , i_task_end_date    => trunc(sysdate) +4
  , i_external_ref     => 'EXTERNAL_REF01'
  );
  commit;
end;
```
- Cite: layout/03-ice-workflow/AvaloqICE/workflow_api_all_subpages/D5_Function_create_task.txt p.1-2
- Basis: STATED
- From: G5-35, G5-36

---

## E3 Avaloq Test Framework (ATF)

### KB-TOOL-40 ATF is the official construction-test framework (not utPLSQL)
- Fact: ATF is mainly used for unit and integration tests, called "construction tests". They run in nightly builds and task integrations, are written in ice Workbench in PL/SQL or Avaloq Script, are automated by ADAI, and can also be started manually (SmartClient, scripts). Test code is managed like production code. A secondary note that claims utPLSQL with `ut_pay_order_val` is unsupported: the official framework is ATF, whose tests use `it.assert` and procedures named `it_*` / `ut_*`.
- Cite: layout/04-test-framework/pages/00_Introduction.txt p.1 ; layout/04-test-framework/pages/02b_Test_sources.txt p.1-2 ; layout/04-test-framework/pages/02a_Creating_a_simple_test.txt p.1
- Basis: STATED
- VERIFY: Q33 CONFIRMS (ATF exists); Q33 CONTRADICTS the utPLSQL assumption
- Audit use: test-related rules target ATF (`import it;`, `it.assert`, `it.catch`, `it_setup`/`ut_teardown`).
- From: G5-54, G6-81

### KB-TOOL-41 ATF benefits and limitations
- Fact: ATF is part of ACP and supports parallel testing. It does not support user-interface testing and needs significant technical knowledge.
- Cite: layout/04-test-framework/pages/00_Introduction.txt p.1 "Benefits and limitations of ATF"
- Basis: STATED
- From: G5-55

### KB-TOOL-42 Test environment; test sources live in the ATS application
- Fact: The test environment has three parts: the ice Workbench repository (production and test sources), ADAI (orchestrates nightly builds and task integrations) and ATF. Test sources must be in the dedicated **ATS** (Avaloq Test Suite) application, so that they are never deployed to production; ATS holds test sources only. ATF itself is a component of the AAA application (Avaloq Banking System). ATS components should mirror the AAA components they test (e.g. ATS.MDB.ATF).
- Cite: layout/04-test-framework/pages/01a_Avaloq_test_environment.txt p.1 "ice Workbench repository" ; layout/04-test-framework/pages/02b_Test_sources.txt p.1 "Source application and components"
- Basis: STATED; INFERRED (rule "production sources must not depend on ATS sources")
- VERIFY: Q02 EXTENDS; Q33 EXTENDS
- Audit use: classify application-ATS sources as test code and report them separately from production rules.
- From: G5-56, G5-104

### KB-TOOL-43 Test source types
- Fact: A test needs a main test package of source type SCRIPT PACKAGE or PL/SQL PACKAGE, plus one TEST SCRIPT source (XML). Kernel helpers: IT (SCRIPT PACKAGE) for Avaloq Script tests and IT# (PACKAGE BODY) for PL/SQL tests. UT is a smaller, private package.
- Cite: layout/04-test-framework/pages/02b_Test_sources.txt p.1 "Source types" ; p.2 "IT script package"
- Basis: STATED
- VERIFY: Q01 EXTENDS (source types SCRIPT PACKAGE, PL/SQL PACKAGE, PACKAGE BODY, TEST SCRIPT)
- From: G5-65, G5-68

### KB-TOOL-44 Test naming conventions: it_/ut_ and `<client key>$`
- Fact: Integration tests use the prefix `it_` or the infix `xxx$it_`. Unit tests use `ut_` or `xxx$ut_`. Recommended patterns:
  - implementation (SCRIPT PACKAGE): `<client key>$IT_<business type>_<any name>`, e.g. MDB$IT_ADDR_CREATE
  - test script (TEST SCRIPT): `<client key>$<business type>.IT_<any name>`, e.g. MDB$ADDR.IT_CREATE
- Cite: layout/04-test-framework/pages/02b_Test_sources.txt p.1 "Naming conventions"
- Basis: STATED
- VERIFY: Q02 EXTENDS, Q31 EXTENDS (the `<client key>$` custom namespace)
- Audit use: TEST SCRIPT names use dot notation; implementation names do not.
- From: G5-66

### KB-TOOL-45 Minimal Avaloq Script test package
- Fact: A test is a script package whose main procedure is, by convention, `it_main`. Each test procedure should start with `it.log_begin` and end with `it.log_end`. The exception block "follows the standard pattern defined in the PL/SQL coding conventions" and calls `it.catch('<proc name>')`.
- Avaloq form:
```
script package it_hello
is

import it;

----------------------------------------------------------------------------
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

end it_hello;
```
- Means: `import <pkg>;` declares a dependency; `when others then it.catch(...)` is the official test handler.
- Cite: layout/04-test-framework/pages/02a_Creating_a_simple_test.txt p.1 "Create the test"
- Basis: STATED (code); INFERRED (`import` as dependency declaration)
- VERIFY: Q05/Q06/Q07/Q11 EXTENDS
- From: G5-62

### KB-TOOL-46 TEST SCRIPT source: XML, schema-validated, stored in ATS_SCRIPT
- Fact: Each construction test has exactly one TEST SCRIPT source, written in XML. Mandatory elements are name, descriptive_name and impl. The source name should start with the component name, otherwise compilation gives a warning. impl names either `package.procedure` (one procedure) or just the package (all `it_*` procedures). The content is validated against the XSD source COM.AVALOQ.SRC_TEST_SCRIPT, and the metadata is stored in table ATS_SCRIPT.
- Avaloq form:
```
<?xml version="1.0" encoding="ISO-8859-1"?>
<test_script version="[ats 1.1]" xmlns:ats="http://www.avaloq.com/src_test">
   <name>atf.it_hello</name>
   <descriptive_name>This is my first test</descriptive_name>
   <test_kind>Integration Test</test_kind>
   <impl>
     <avaloq_script>
       <procedure>it_hello.it_main</procedure>
     </avaloq_script>
   </impl>
</test_script>
```
  Package form: `<impl><avaloq_script><package>mdb$it_addr_create</package></avaloq_script></impl>` together with `<intg_relv>compo</intg_relv>`.
- Cite: layout/04-test-framework/pages/02a_Creating_a_simple_test.txt p.1-2 "Declare the test" ; layout/04-test-framework/pages/02b_Test_sources.txt p.2 "TEST SCRIPT source" ; p.6 "Example test implementation"
- Basis: STATED
- VERIFY: Q01 EXTENDS (XSD schemas are sources); Q27/Q31 EXTENDS (name warning)
- From: G5-63, G5-70, G5-75

### KB-TOOL-47 TEST SCRIPT attribute catalogue
- Fact: Elements of a TEST SCRIPT source:

| Element | Rule / values |
|---|---|
| name | mandatory; must equal source name |
| descriptive_name | mandatory; max 100 chars |
| prl_exec_grp | parallel group (CODE_ATS_PRL_EXEC_GRP) |
| test_kind | CODE_ATS_TEST_KIND (e.g. Integration Test) |
| prep_kind / post_kind | CODE_ATS_PREP_KIND / CODE_ATS_POST_KIND |
| descn, impact, purpose | free text |
| intg_relv | always / module / compo / no (default) |
| explicit | ignored by ADAI |
| skip | skip flag |
| rerunnable | ignored |
| max_exec_dur | default 6 min, max 85 |
| max_exec_dur_setup_async / _teardown_async | default 5, max 20 |
| depend | list of `<test_script>` nodes |
| bgp_hdl | default starts BGPs; bgp_none; bgp_dont_care |
| cover | BGPs counted for coverage |
| bu | default from base parameter avq.atf.dflt_test_bu_id |
| impl | mandatory; oracle_plsql or avaloq_script, then procedure or package |
| setup_async | default false |
| teardown_async | default true |
| compo_feat_list | component features covered (KB-TOOL-48) |

- Cite: layout/04-test-framework/pages/02b_Test_sources.txt p.2-3 "Key attributes of the TEST SCRIPT source"
- Basis: STATED
- Audit use: validator: name = source name; descriptive_name ≤ 100; impl present; max_exec_dur ≤ 85.
- From: G5-71

### KB-TOOL-48 compo_feat_list links tests to component features
- Fact: `<compo_feat_list>` lists component features with a test extent (e.g. cover), using CODE_COMPO_FEAT, CODE_COMPO_FEAT_TEST_EXTENT and ATS_SCRIPT_COMPO_FEAT_TEST. Two screen reports show it: "ATS feature covered by test" (task 1312) and "ATS test cover feature" (task 1311).
- Avaloq form: `<compo_feat_list><compo_feat><test_extent>cover</test_extent><name>ami$prc_single_msg</name></compo_feat></compo_feat_list>`
- Cite: layout/04-test-framework/pages/02b_Test_sources.txt p.3-4 "Key attributes of the TEST SCRIPT source"
- Basis: STATED
- From: G5-72

### KB-TOOL-49 Test discovery: all it_*/ut_* procedures run in order; setup first, teardown last
- Fact: ATF calls every procedure whose name starts with `it_` or `ut_`, one after another, in the order they appear in the package. `it_setup`/`ut_setup` (optional) always runs first and `it_teardown`/`ut_teardown` (optional) always runs last. Helper functions are not called automatically. A test can span several Avaloq Script and PL/SQL packages.
- Cite: layout/04-test-framework/pages/02b_Test_sources.txt p.2 "Main test package"
- Basis: STATED
- Audit use: a helper whose name accidentally starts with `it_`/`ut_` will run as a test case.
- From: G5-67

### KB-TOOL-50 assert continues, require stops
- Fact: The public script package IT provides precondition checks (`require`), postcondition checks (`assert`), parameter retrieval and pure logging, typed by data type and operator. An assert logs pass or fail, and the test continues either way. A require (e.g. `require_date_is_not_null`) must succeed, otherwise the current procedure stops.
- Cite: layout/04-test-framework/pages/02b_Test_sources.txt p.2 "IT script package"
- Basis: STATED
- From: G5-68

### KB-TOOL-51 IT procedures seen in the docs
- Fact: The examples use:
  - `it.log_begin(text)`, `it.log_end(text)`, `it.log_chk(text)`, `it.log_step(text)`
  - `it.assert(text, boolean)`, `it.require(text, boolean)`
  - `it.assert_eq_text(assertion =>, received_text =>, expected_text =>)`
  - `it.catch(proc_name)`
  - `it.ats_script_run_id` (unique ID of the current run)

  `it_assert_eq_boolean` and `require_date_is_not_null` are also named. The full IT API is not in the corpus.
- Cite: layout/04-test-framework/pages/02b_Test_sources.txt p.5 "Example test implementation" ; layout/04-test-framework/pages/02c_Implementing_the_construction_tests.txt p.1, p.3
- Basis: STATED
- From: G5-69

### KB-TOOL-52 CONFLICT: argument order of require
- Fact: CONFLICT. The 02a and 02b examples use `it.require('<text>', <condition>)`, message first. The 02c test-library helper `person#gen` calls an unqualified `require(i_person_idx is not null, 'i_person_idx not null')`, condition first. The package the unqualified `require` resolves to is not stated. The same helper declares parameters of Avaloq Script type `text` with defaults (`i_descn text := null`) and calls client libraries (`it_tax_lib.log`, `it_tax_omd_person.doc#new`).
- Cite: layout/04-test-framework/pages/02b_Test_sources.txt p.5 ; layout/04-test-framework/pages/02c_Implementing_the_construction_tests.txt p.3 "Store static data, input and expected outputs in code tables"
- Basis: STATED (both forms); INFERRED (that they are different routines)
- VERIFY: Q07 EXTENDS; Q10 PARTIAL
- Audit use: do not hard-code the argument order of `require`.
- From: G5-69, G5-102

### KB-TOOL-53 Full Avaloq Script test example (address creation)
- Fact: Package `mdb$it_addr_create` does the following:
  - imports `it` and `mdb$it_addr_util`
  - declares a package constant `c_eu_id number := lookup.code('obj_country_v', 'EU', 'KEY_SYM')`
  - declares a local `l_addr_id id obj_addr` (typed object ID)
  - passes code values `code_addr_type.postal_id` and `code_salut.mr`
  - has it_setup, it_main and it_teardown
- Avaloq form:
```
procedure it_main
is
   l_addr_id id obj_addr;
begin
   it.log_begin('mdb$it_addr_create.it_main check country if existing and create address');
   it.log_chk('Check ' || c_eu_id || ' if exist');
   it.require('Country is not null', c_eu_id is not null);
   it.log_step('Create address');
   l_addr_id := mdb$it_addr_util.gen_addr(
      i_sym_key      => 'ADDR.CT_TEST.01'
   , i_country       => c_eu_id
   , i_addr_type_id => code_addr_type.postal_id
   ...
   , i_salut_id      => code_salut.mr
   );
  it.assert('Address created', l_addr_id is not null);
  it.log_end('mdb$it_addr_create.it_main check country if existing and create address');
exception
  when others then
    it.catch('mdb$it_addr_create.it_main');
end it_main;
```
- Means: `id <obj_type>` is a typed-ID declaration; `code_<table>.<entry>` is a code value; `lookup.code(view, key, keycol)` resolves an ID from an object view (semantics INFERRED).
- Cite: layout/04-test-framework/pages/02b_Test_sources.txt p.5-6 "Example test implementation"
- Basis: STATED (code); INFERRED (semantics of `id obj_addr`, `lookup.code`)
- VERIFY: Q08/Q09/Q10 EXTENDS
- From: G5-74

### KB-TOOL-54 Code-table sources for test data (two syntax forms)
- Fact: Static test data, inputs and expected outputs can live in code tables and be read by intl_id. Form 1 has a `tabdef` column list and `row <intl_id> tab "<v1>" ...` lines. Form 2 has `row <intl_id>` followed by `<col> "<value>"` lines. Both end with `end code table`. Custom code tables carry a client prefix (`rm$code_...`).
- Avaloq form:
```
code table code_it_person_gen

tabdef birth_date obj_sub_type first_name last_name full_name gender lang addr tin tax_addr tax_addr_a

row atp1 tab "01.01.1961" "person_natural" "Albert" "Theis" "" "male" "g" "at1" "1001A" "at1" "-"
end code table

code table code_ats_prl_exec_grp

row prl_exec_grp_sample_1
  user_id "PRL_EXEC_GRP_SAMPLE_1"
  name "PRL_EXEC_GRP_SAMPLE_1"
  desc "Sample parallel group"

end code table
```
- Cite: layout/04-test-framework/pages/02c_Implementing_the_construction_tests.txt p.2 "Store static data, input and expected outputs in code tables" ; layout/04-test-framework/pages/02d_Setting_up_parallel_testing.txt p.1-2 "Setting up parallel tests"
- Basis: STATED
- VERIFY: Q24 EXTENDS, Q09 EXTENDS
- From: G5-79, G5-85

### KB-TOOL-55 Data-driven test: code-table row access and `with ... as ... do`
- Fact: Row values are read with `code_it_person_gen.lookup(i_person_idx).birth_date`. A data-driven test loops `for id in lookup.code_list('id','rm$code_it_cont_name','activ is not null') loop`, binds the row with `with rm$code_it_cont_name(id) as cn do ... end with`, and checks with `it.assert_eq_text`. Classes resolve with `lookup.class_id(classif => btt.cont.obj_extn.cont_type_id, class => cn.cont_type)`. The printed example omits semicolons after `return ...` and `end with`, which is a doc inconsistency.
- Avaloq form:
```
for id in lookup.code_list('id','rm$code_it_cont_name', 'activ is not null') loop
  with rm$code_it_cont_name(id) as cn do
    it.assert_eq_text(
       assertion => "it_cont_name_part for " || cn.intl_id
     ,received_text => rm$cont_name_calc.calc#name(i_cont_name => cn.cont_name, ...)
     ,expected_text => cn.exp_name
    );
  end with
end loop;
```
- Cite: layout/04-test-framework/pages/02c_Implementing_the_construction_tests.txt p.3-4 "Store static data, input and expected outputs in code tables"
- Basis: STATED (code); INFERRED (meaning of the `btt` path)
- VERIFY: Q06/Q08/Q09/Q10 EXTENDS
- From: G5-80

### KB-TOOL-56 Test code quality: stateless, rerunnable, production-grade
- Fact: Test code has the same quality requirements and conventions as production code. Tests should:
  - use static data from setup or from dependent tests, not pre-existing data
  - leave no lasting changes (teardown rolls back)
  - be rerunnable, by appending `it.ats_script_run_id` to unique keys and intl_ids
  - follow predefined test patterns and be modular
- Cite: layout/04-test-framework/pages/02c_Implementing_the_construction_tests.txt p.1 "When developing the tests"
- Basis: STATED
- VERIFY: Q25 EXTENDS
- Audit use: flag hard-coded unique keys in test packages that lack `it.ats_script_run_id`, and data-creating tests without a teardown.
- From: G5-76

### KB-TOOL-57 Test essentials and client test libraries
- Fact: Before writing a test, define the objective, preconditions (data, BGP state, session level), dependencies, test data and pass/fail criteria. Build client test libraries whose helpers take minimal input and have overridable defaults. They should cover:
  - static data: persons, BPs, containers, money accounts, addresses
  - setting classes without modifying the order
  - order booking driven to "done" (e.g. STEX buy)
  - rule creation and loading

  No fixture or mock framework is mentioned (INFERRED from absence).
- Cite: layout/04-test-framework/pages/02c_Implementing_the_construction_tests.txt p.1 "Essentials for developing effective tests" ; p.2 "Create test libraries", "Static data", "Orders", "Rule loading"
- Basis: STATED
- VERIFY: Q33 EXTENDS; Q15 EXTENDS
- From: G5-77, G5-78

### KB-TOOL-58 Testability: pass session values and base parameters as defaulted parameters
- Fact: If code depends on session values (e.g. `session.today`) or base parameters, pass them as input parameters with a default so that tests can inject values.
- Avaloq form: `,i_date date := session.today` … `if i_doc.date > i_date then (...)`
- Cite: layout/04-test-framework/pages/02c_Implementing_the_construction_tests.txt p.4 "Create modular and stateless code"
- Basis: STATED
- VERIFY: Q25 EXTENDS, Q10 EXTENDS
- Audit use: testability smell. Flag direct `session.today` or base-parameter reads inside calculation functions.
- From: G5-81

### KB-TOOL-59 Testability: split stateless calc_intl from the order wrapper (example has anti-patterns)
- Fact: Put the calculation in a function with simple parameters (`calc_intl(i_asset_type id code_obj_class, i_qty number)`) and keep a thin wrapper that takes the order (`calc(i_doc doc_stex)`, passing `i_doc.asset.extn.ass_type`, `i_doc.qty`). Each function in the official example ends with `exception when others then return null;`, which swallows every error. Its `if i_qty > 100 ... elsif i_qty > 1000` makes the second branch unreachable. Do not cite it as compliant style.
- Cite: layout/04-test-framework/pages/02c_Implementing_the_construction_tests.txt p.4-5 "Create modular and stateless code"
- Basis: STATED (code); INFERRED (anti-pattern observations)
- VERIFY: Q08/Q15 EXTENDS; Q27 PARTIAL
- From: G5-82

### KB-TOOL-60 Execution flow: phases, separate session, dependency order
- Fact: ADAI calls ATS_RUN#.subm and the parameters are logged in ATS_RUN. Tests are selected by parameters and classifications. Each selected test, including skipped or ignored ones, gets an ATS_SCRIPT_RUN row with status "inserted". Phases run Preparation → Default → Post. Tests run in a separate Oracle session, and dependencies run first. Circular dependencies are checked when the TEST SCRIPT source is compiled.
- Cite: layout/04-test-framework/pages/01b_Test_execution.txt p.1 "Steps in the execution of a test"
- Basis: STATED
- VERIFY: Q04 EXTENDS (compile-time semantic check)
- From: G5-61

### KB-TOOL-61 depend changes order, not selection; a failed precondition skips its dependents
- Fact: If a precondition test fails, the tests that depend on it are not run, and a warning is flagged for them. `depend` affects execution order, not test selection.
- Cite: layout/04-test-framework/pages/02c_Implementing_the_construction_tests.txt p.1 "When developing the tests" ; layout/04-test-framework/pages/02b_Test_sources.txt p.3 (attribute depend)
- Basis: STATED
- Audit use: a referenced dependency must also be selected (intg_relv, component or explicit list).
- From: G5-103

### KB-TOOL-62 Test selection by integration relevance
- Fact: ACP functionality is organised in modules and components (CODE_ENV_MODULE, CODE_ENV_COMPO). For a task touching component C in module M, ATF selects the compo tests of C, the module tests of M and all always tests. This is done for every involved component and module.
- Cite: layout/04-test-framework/pages/02e_Calculating_which_tests_to_execute.txt p.1 "Integration relevance"
- Basis: STATED
- VERIFY: Q02 EXTENDS
- From: G5-86

### KB-TOOL-63 Extending test scope: component mapping, test-script mapping, BU
- Fact: Component mapping (code table CODE_ATS_COMPO_MAP, read via view CODE_ATS_COMPO_MAP_V) adds components to the affected list for module and compo tests. Test-script mapping (CODE_ATS_INCL_TEST) links one test to a component. The default test BU comes from base parameter avq.atf.dflt_test_bu_id unless the TEST SCRIPT sets `<bu>`.
- Cite: layout/04-test-framework/pages/02e_Calculating_which_tests_to_execute.txt p.1-2 "Component mapping", "Test scripts mapping", "BU configuration"
- Basis: STATED
- From: G5-87

### KB-TOOL-64 Parallel testing concept
- Fact: Tests run sequentially by default. Grouped tests can run in parallel as DBMS_SCHEDULER jobs, with a default parallelisation degree of 4. Parallel testing is not supported for nightly builds. Setup and default phases of different tests overlap, and all teardowns wait until every default phase has finished. With setup_async = true, each phase completes before the next starts.
- Cite: layout/04-test-framework/pages/02d_Setting_up_parallel_testing.txt p.1 "Concept"
- Basis: STATED
- From: G5-83

### KB-TOOL-65 Parallel group rules and setup
- Fact: Tests in one parallel group:
  - should not interfere with each other (recommendation)
  - must share the same intg_relv
  - must all use bgp_none if any one does
  - must not depend on each other

  Setup: define the group in code table CODE_ATS_PRL_EXEC_GRP, reference it in `<prl_exec_grp>`, and call ATS_RUN#.subm with `i_enbl_prl = true`. Optional: `i_prl_degree` (default 4) and `i_prl_exec_grp_name_list`.
- Cite: layout/04-test-framework/pages/02d_Setting_up_parallel_testing.txt p.1-2 "Setting up parallel tests"
- Basis: STATED
- Audit use: cross-source validator for TEST SCRIPTs that share a prl_exec_grp.
- From: G5-84, G5-85

### KB-TOOL-66 Starting tests: ATS_RUN#.subm, task 952, SQL*Plus; results via ATS_RES_V
- Fact: ATF provides the procedure `ATS_RUN#.subm` to start tests. ADAI calls it with the affected components and configuration. Manual runs use the ATS Test Run task (task 952) or SQL*Plus. Results are logged in ATS_RUN, ATS_SCRIPT_RUN and ATS_SCRIPT_RUN_RES. ADAI reads a compressed view of them through ATS_RES_V for storage, reporting and the accept/reject decision, emails them, and shows them in the ADAI WebPortal.
- Cite: layout/04-test-framework/pages/01a_Avaloq_test_environment.txt p.2 "Automatically triggered test execution", "Logging the test results"
- Basis: STATED
- Audit use: test results are machine-readable through ATS_RES_V.
- From: G5-60

### KB-TOOL-67 ATS_RUN#.subm parameters
- Fact: The doc gives no data types or modes.

| Parameter | Default / note |
|---|---|
| o_run_id | references ATS_RUN.ID; OUT INFERRED from `o_` prefix |
| i_intg_relv_name_list | |
| i_purpose | |
| i_env_compo_name_list | |
| i_timeout | 30 days |
| i_script_timeout_factor | 1; raise for coverage |
| i_cover | false |
| i_script_name_list / i_ign_script_name_list / i_script_name_ptn | |
| i_incl_explicit | false |
| i_start_bgp | true |
| i_prep_kind_name_list | |
| i_incl_dflt_phase | true |
| i_post_kind_name_list | |
| i_enbl_prl | false |
| i_prl_degree | default and minimum 4 |
| i_prl_exec_grp_name_list | |
| i_no_compo_map | false |

- Cite: layout/04-test-framework/pages/03b_Executing_the_construction_tests.txt p.2-3 "ATF API"
- Basis: STATED; INFERRED (o_run_id OUT)
- VERIFY: Q34 PARTIAL (headless PL/SQL test API on an instance)
- From: G5-92

### KB-TOOL-68 SQL*Plus scripts @ats / @atsc / @atsr and output format
- Fact: Three SQL*Plus scripts:
  - `@ats <test script>` runs one test
  - `@atsc <component>` runs all tests of a component
  - `@atsr <list of changes>` runs the tests related to the sources in those changes, the same set a task integration uses

  Output appears in the SQL*Plus window in ice Workbench: a timestamped banner, the release, the final status (e.g. SUCCESS), counts of requirements and assertions satisfied, and one numbered line per log or assert. Booleans print as "+".
- Avaloq form: `> @ats atf.it_hello` … `SUCCESS: ASSERT: Hello, World! Everything ok.: Expected "+" and got "+"`
- Cite: layout/04-test-framework/pages/02a_Creating_a_simple_test.txt p.2 "Run the test" ; layout/04-test-framework/pages/03b_Executing_the_construction_tests.txt p.1 "Using the SQL scripts"
- Basis: STATED
- From: G5-64, G5-89

### KB-TOOL-69 SmartClient task "ATS Test Run" (952)
- Fact: Parameters: Layout, Testscripts, Show last result only, Hide successful Tests, Hide successful Conditions, Start BGPs, Integration relevance, Run only the tests matching the specified pattern, Preparation Kind, Exclude Default Phase, Post Kind, Enable parallel, Parallelisation degree (min 4), Parallel execution group.
- Cite: layout/04-test-framework/pages/03b_Executing_the_construction_tests.txt p.1 "Using a task in the SmartClient"
- Basis: STATED
- From: G5-90

### KB-TOOL-70 Preparation and post kinds
- Fact: Preparation-kind tests run before all others. The available kinds are pillar, rule, fk and aging, e.g. `<prep_kind>fk</prep_kind>` checks that vital foreign constraints are enabled. Post-kind tests run after all others, e.g. `<post_kind>be</post_kind>` for Book Engine data consistency.
- Cite: layout/04-test-framework/pages/03b_Executing_the_construction_tests.txt p.1-2 "Using a task in the SmartClient"
- Basis: STATED
- From: G5-91

### KB-TOOL-71 ADAI configuration for construction tests
- Fact: ADAI runs configurable action sequences (ADAI WebPortal Action Sequence Editor) with actions per test type (always, module, compo, no) and for image creation. Build templates (Template Editor) set action parameters. The ATS application must be in the build templates, and "Avaloq Test Suite" must be listed as a Test System with "Run CTs Every Time" checked in the Integration Robot configuration.
- Cite: layout/04-test-framework/pages/03_Configuring_the_tests_in_ADAI.txt p.1
- Basis: STATED
- From: G5-88

### KB-TOOL-72 Coverage runs need the database compiled in Debug Mode
- Fact: For coverage from ice Workbench:
  1. Instantiate the image.
  2. Make sure the database is in Debug Mode (otherwise run "Compile DB in Debug Mode").
  3. Run Special context action > "Run ATS Construction Tests (coverage and report)".

  Options: component expression, Run tests, Generate HTML reports (ADAI), Report Comment. Raise `i_script_timeout_factor` for coverage runs.
- Cite: layout/04-test-framework/pages/03b_Executing_the_construction_tests.txt p.3 "Using the code coverage calculation" ; p.2-3 "ATF API"
- Basis: STATED
- VERIFY: Q04 EXTENDS (database-level compile actions in ice)
- From: G5-93, G5-92

### KB-TOOL-73 Coverage uses the Oracle PL/SQL profiler tables
- Fact: Coverage is described as work in progress. Raw data comes from PLSQL_PROFILER_RUNS, PLSQL_PROFILER_UNITS and PLSQL_PROFILER_DATA. It is combined with Oracle and Avaloq source information into table ATS_COVER_SRC, with views ATS_COVER_SRC_V and ATS_COVER_COMPO_V (per component). Coverage cannot run in parallel, because the profiler is per session. Oracle sources must be compiled for debugging. The doc does not name DBMS_PROFILER.
- Cite: layout/04-test-framework/pages/04a_Code_coverage.txt p.1 "Calculation and reporting overview", "ABS/ACP side"
- Basis: STATED (mechanism)
- VERIFY: Q12 PARTIAL — see KB-TOOL-79 for the PL/SQL-translation question
- From: G5-94

### KB-TOOL-74 Overall coverage metrics and exclusions
- Fact: The overall report has these columns:
  - test counts: TEST_CNT, TEST_SUCC_CNT, TEST_PRECOND_VIOL_CNT, TEST_SKIP_IGN_CNT, TEST_FAIL_CNT
  - COVER_LINE_ADJUST_PERC = sum(line_cnt_cover_adjust) / sum(line_cnt_exec_adjust)
  - separate percentages for generated and non-generated code (code "created (not generated) in ice Workbench")
  - source and line counts

  Excluded from the adjusted counts:
  - source types REP FILE / PRINT / SCREEN, INTF DEF, TRIGGER, PACKAGE
  - names starting with "INTF_" or "CTX_ACTION_"
  - procedures prefixed "TQ_"
- Cite: layout/04-test-framework/pages/04a_Code_coverage.txt p.2 "ADAI reporting level: Overall"
- Basis: STATED
- VERIFY: Q01 EXTENDS (more source type names)
- Audit use: treat INTF_*, CTX_ACTION_* and TQ_* as excluded. The doc does not call them generated.
- From: G5-95

### KB-TOOL-75 Coverage drill-down and colour thresholds
- Fact: Reports drill down Overall > Team (ATS_COMPO_TEAM_MAP: id, compo_name, user_group_name) > Component > Source.
  - Component level: test green = pass, red = fail, yellow = not executed. Source coverage red < 0.01, white 0.01 to < 0.6, green ≥ 0.6, grey = excluded.
  - Source level: up to 10 tests per line. Lines are red (executable, not hit), white (non-executable, incl. declarations and function calls), dark green (hit by a test of the same component), light green (hit by any test) or grey (excluded, e.g. exception handlers).
- Cite: layout/04-test-framework/pages/04a_Code_coverage.txt p.2-3 "ADAI reporting level: Compo", "ADAI reporting level: Source"
- Basis: STATED
- Audit use: Avaloq's own "good" coverage threshold per source is 0.6.
- From: G5-96

### KB-TOOL-76 Table ATS_SCRIPT (test metadata)
- Fact: Columns: ID, NAME, USER_ID, ATS_PARLIST_ID (→ ATS_PARLIST), ACTIV ('+' = active), ENV_COMPO_ID, ATS_TEST_KIND_ID, ATS_IMPL_KIND_ID (PL/SQL or Avaloq Script, CODE_ATS_IMPL_KIND), PROC, IMPACT, DESCN, PURPOSE, EXPLICIT, SKIP, RERUNNABLE, MAX_EXEC_DUR, INTL_ID, BGP_PROF_LIST, SETUP_ASYNC, TEARDOWN_ASYNC, INTG_RELV_ID, ATS_PREP_KIND_ID, ATS_POST_KIND_ID, ATS_BGP_HDL_ID, BU_ID, MAX_EXEC_DUR_TEARDOWN_ASYNC, DESCRIPTIVE_NAME, MAX_EXEC_DUR_SETUP_ASYNC, ATS_PRL_EXEC_GRP_ID, ENV_COMPO.
- Cite: layout/04-test-framework/pages/02b_Test_sources.txt p.4-5 "Table: ATS_SCRIPT"
- Basis: STATED
- VERIFY: Q14 EXTENDS, Q24 EXTENDS
- Audit use: data convention. `<X>_ID` usually references `CODE_<X>` (not always: ATS_PARLIST_ID references ATS_PARLIST). Flags are '+'/null.
- From: G5-73

### KB-TOOL-77 Table ATS_RUN (one row per test run)
- Fact: One row per test execution, however it was started. Columns: ID, SEC_USER_ID, SESSION_INST_ID, SESSION_ID, RUN_START, RUN_END, DONE ('-' at start, '+' at end), PURPOSE, TIMEOUT, SCRIPT_TIMEOUT_FACTOR, COVER, SCRIPT_NAME_PTN, INCL_EXPLICIT, START_BGP, INCL_DFLT_PHASE, INTG_RELV_NAME_LIST, ENV_COMPO_NAME_LIST, ENV_COMPO_NAME_MAPPED_LIST, SCRIPT_NAME_LIST, IGN_SCRIPT_NAME_LIST, PREP_KIND_NAME_LIST, POST_KIND_NAME_LIST, ENBL_PRL, PRL_DEGREE, PRL_EXEC_GRP_NAME_LIST, NO_COMPO_MAP. The columns mirror the subm parameters.
- Cite: layout/04-test-framework/pages/04c_Test_results_logs.txt p.1-2 "Table: ATS_RUN"
- Basis: STATED
- From: G5-99

### KB-TOOL-78 Tables ATS_SCRIPT_RUN and ATS_SCRIPT_RUN_RES
- Fact: ATS_SCRIPT_RUN has one row per test per run: ID, ATS_SCRIPT_ID, ATS_RUN_ID (→ K.ATS_RUN), SCRIPT_RUN_START, SCRIPT_RUN_END, ERR_LOG_ID (→ LOG), ATS_SCRIPT_RES, ATS_EXEC_STATUS_ID (CODE_ATS_EXEC_STATUS). ATS_SCRIPT_RUN_RES holds the detail rows: ID, ATS_SCRIPT_RUN_ID, ATS_EXEC_STATUS_ID, ATS_RES_KIND_ID (CODE_ATS_STEP_KIND), ERR_LOG_ID, TIMESTAMP, DESCN (info, or the result of a require/assert), ATS_TEST_STEP_ID (CODE_ATS_TEST_STEP), ENV_COMPO_ID, CALL_STACK, INST_ID, SID, SERIAL#.
- Cite: layout/04-test-framework/pages/04c_Test_results_logs.txt p.2 "Table: ATS_SCRIPT_RUN", "Table: ATS_SCRIPT_RUN_RES"
- Basis: STATED (columns); INFERRED (K = kernel schema)
- VERIFY: Q11 EXTENDS (central LOG table, call stacks); Q17 EXTENDS
- From: G5-100

---

## E4 Other tooling: compilers, warnings, ASMD, ice formatting

### KB-TOOL-79 CONFLICT: Avaloq Script compiles to PL/SQL — stated in one doc set, only inferred in another
- Fact: CONFLICT on Basis. The Getting Started page states that each area where Avaloq Script is used has its own compiler, and that the compilers translate Avaloq Script into PL/SQL installed directly on the database, adapting when tables change. The G5 verifier found no such statement in the ATF and ice docs: there, compilation to PL/SQL is only inferred from coverage using the PLSQL_PROFILER_* tables mapped back to Avaloq sources. Resolution: STATED in the Getting Started doc. The areas are not listed.
- Cite: paged/text/getting-started-with-avaloq-script.txt p.1 "Note" ; layout/04-test-framework/pages/04a_Code_coverage.txt p.1 "Calculation and reporting overview"
- Basis: STATED (G1 source); INFERRED (G5 source)
- VERIFY: Q12 EXTENDS (G1) / PARTIAL (G5); Q01 PARTIAL; Q34 PARTIAL
- Audit use: expect area-specific compilers. Per-area dialect differences are INFERRED.
- From: G1-03, G5-94

### KB-TOOL-80 Compiler framework scope: collections and record types
- Fact: Collection types (list, set, map) exist only in Avaloq Script compiled via the compiler framework. As of ACP 5.6 that excludes Avaloq Script embedded in REP PRINT and runtime-compiled Avaloq Script. Record types arrive with Compiler Framework 18.0, can be defined only at package level, and are strictly type-checked.
- Cite: paged/text/data-types.txt p.30-31 "Implementation restrictions" ; p.36-38 "Record types in Avaloq Script"
- Basis: STATED
- VERIFY: Q01/Q26/Q27 EXTENDS
- Audit use: flag list<>/set<>/map<> in REP PRINT sources.
- From: G2-43, G2-47

### KB-TOOL-81 Documented compiler error messages (collections)
- Fact: The doc lists these errors:
  - "Reference to template data dictionary is only allowed with type arguments" (`l_list list;`)
  - "Wrong count of DDIC template type parameters" (`list<text, number>`)
  - "Incompatible types: expected type <1> but found type <2>"
  - "Unsupported field operation 'store' for type <1>. Not supported for nested DDIC collections."
  - "Unsupported key type. Only number, text, and Avaloq Script DDIC types are allowed key types."
- Cite: paged/text/data-types.txt p.31-32 "Compiler error messages"
- Basis: STATED
- VERIFY: Q27 CONFIRMS; Q34 PARTIAL
- Audit use: pre-compile validator rules that use the official message text.
- From: G2-44

### KB-TOOL-82 Documented compiler warnings and compile-time checks
- Fact: Three are documented:
  - Code using an obsolete DDIC field compiles with a warning that names the substitute. The field will be de-released, so replace it as soon as the warning appears.
  - A TEST SCRIPT source whose name does not start with its component name compiles with a warning.
  - Circular test dependencies are checked when the TEST SCRIPT source is compiled.
- Cite: paged/text/what-are-data-dictionaries.txt p.6 "Obsolete DDIC fields" ; layout/04-test-framework/pages/02a_Creating_a_simple_test.txt p.1-2 "Declare the test" ; layout/04-test-framework/pages/01b_Test_execution.txt p.1
- Basis: STATED
- VERIFY: Q27 CONFIRMS/EXTENDS; Q29 EXTENDS
- From: G3-23, G5-63, G5-61

### KB-TOOL-83 CONFLICT: does the compiler check type compatibility?
- Fact: CONFLICT. Expressions p.7 says assignment compatibility "is currently not checked by the compiler". Data types p.42 says some violations (e.g. a MEM_DOC variable assigned to an OBJ variable) produce "a warning or even an error, depending on the configuration", and that collection type violations warn at design time. Record types have strict type checking. The statements may reflect different compiler generations. Implicit number→text conversion is allowed.
- Cite: paged/text/avaloq-script-expressions.txt p.7-8 "Expression compatibility" ; paged/text/data-types.txt p.42
- Basis: STATED (both)
- VERIFY: Q27 PARTIAL/EXTENDS; Q28 PARTIAL
- Audit use: report type incompatibility as our own finding, whatever the compiler's configured severity.
- From: G2-19, G2-55

### KB-TOOL-84 ASMD info marker "Missed performance optimization opportunity"
- Fact: The IDE/compiler shows an ASMD info marker "Missed performance optimization opportunity" on a call that blocks reuse of a table access. Screenshot text: "Feature call with potential side effect 'mba$dwh.put_line' prohibits reuse of table access via 'obj'. For additional information see DocID 1074 under 'Hints and tips on using AvaloqScript'." Doc ID 1074 is the Avaloq Script language reference. Linking it to the URL token RG-1074 is INFERRED.
- Means: the fix is to mark the callee `db_side_effect_free` (if it truly is) or to copy the attributes into locals first.
- Cite: paged/text/hints-and-tips-on-using-avaloq-script.txt p.6-7 ; paged/text/how-to-use-docs-avaloq-com.txt p.6-7 "Searching for PDFs" ; paged/text/declarations-in-avaloq-script.txt p.4
- Basis: STATED
- VERIFY: Q27 CONFIRMS; Q28 PARTIAL (no rule list, headless mode or output format documented)
- Audit use: mirror this marker as a rule with the same message. A method marked `db_side_effect_free` that calls `.store`, a DDIC action or a workflow action is an error.
- From: G1-79, G1-90, G6-20

### KB-TOOL-85 Avaloq has its own static analysis (ASMD), language model and LSP — docs not in corpus
- Fact: A secondary note claims Avaloq Script has no public grammar and no lint. That is contradicted. The official EBNF fragments exist, and the Avaloq TOC lists:
  - ASMD static code analysis checks (Check-in validation, Integration-relevant validation, Check configuration)
  - Avaloq coding standard principles, Working with markers, Integrating static code analysis, the ASMD public API
  - DSL model reference > AvqScript Model
  - LSP languages setup
  - Compiler framework > "Checks provided by the compiler framework" and "Optimizing compilers"

  None of these pages is in the folder.
- Cite: TOC entries per verified G6 (`notes/avaloq_toc.md` lines ~18056, 18072–18126, 18255–18258) ; paged/text/hints-and-tips-on-using-avaloq-script.txt p.6
- Basis: STATED (existence via TOC)
- VERIFY: Q06 CONFIRMS; Q27/Q28/Q35 EXTENDS
- Audit use: get the ASMD check catalogue and the compiler-framework checks before building rules, so rules do not duplicate or contradict Avaloq's own markers.
- From: G6-77, G6-84, G6 gap table #4–#7

### KB-TOOL-86 Compiler translation of repeated DDIC reads into per-attribute selects
- Fact: The doc shows the compiler turning `obj_bp(i_obj)` attribute reads into one `select <attr> from obj_bp where id=i_obj` per attribute when calls that may write come in between. DDIC attributes map to same-named columns of the backing table.
- Avaloq form: `select bu_id from obj_bp where id=i_obj` … `select acc_type_id from obj_bp where id=i_obj`
- Cite: paged/text/hints-and-tips-on-using-avaloq-script.txt p.6 "Optimizing accesses to the same database table"
- Basis: STATED (translation shown); INFERRED (that same-name mapping holds generally)
- VERIFY: Q12/Q14/Q17 EXTENDS
- From: G1-B-ADD-01

### KB-TOOL-87 Compiler directives in comments: /*postp_start*/ … /*postp_end*/
- Fact: Enclosing exactly one expression between `/*postp_start*/` and `/*postp_end*/` marks it deterministic. Enclosing `:=` or `;` makes the compiler silently ignore the directives. The directive is only a hint and is less preferred than a deterministic function. Block comments do not nest.
- Avaloq form: `c_num constant number := /*postp_start*/ 2 + 2 /*postp_end*/; -- OK`
- Cite: paged/text/hints-and-tips-on-using-avaloq-script.txt p.10
- Basis: STATED
- VERIFY: Q13 CONFIRMS
- Audit use: the lexer must keep these as directive tokens. Flag unbalanced directives and spans that contain `:=` or `;`.
- From: G1-83

### KB-TOOL-88 ice applies formatting conventions on save; partial suppression exists
- Fact: The default indent is two spaces, never tabs. Avaloq applies its coding conventions automatically to Avaloq-created sources "when the source is saved in ice". The doc does not define ice as an IDE or formatter (INFERRED). The ABR/S guidelines include a page "Partial Suppression of Automatic Formatting", which is not in the corpus.
- Cite: paged/text/coding-conventions.txt p.2 "Indentation" ; TOC entry per verified G6 gap table #3 (ABR/S > Structuring Script Packages)
- Basis: STATED; INFERRED (ice = formatter on save)
- VERIFY: Q35 EXTENDS (INFERRED)
- Audit use: format rules are low severity and can be skipped for ice-formatted corpora.
- From: G1-55, G6 gap table #3

### KB-TOOL-89 Pre-compiler statements start in column 1 (`[Script 1.0]`, `script package`)
- Fact: Leave a two-space margin before indentations, except for compiler- or pre-compiler-specific statements such as `[Script 1.0]` and `script package`, which start in column 1. The header `[Script 1.0]` (also seen as `[script 1.0]`) precedes `script package <name> is`.
- Cite: paged/text/coding-conventions.txt p.3-4 "Margins" ; paged/text/data-types.txt p.41
- Basis: STATED
- VERIFY: Q13 EXTENDS; Q01 EXTENDS
- From: G1-57

### KB-TOOL-90 No official source file extensions are documented
- Fact: Secondary notes assume `.avq .sql .pck` and the source types "AVL, PL/SQL, ODB/DDL, ACE". This is unsupported. The official vocabulary includes script package, REP PRINT, INTF DEF, CODE TAB, DSL sources, MIGR, TEST SCRIPT (XML) and WFD. The full list is the TOC page "Summary of source types", which is not in the corpus.
- Cite: paged/text/data-types.txt p.30, p.39 ; layout/04-test-framework/pages/02a_Creating_a_simple_test.txt p.1
- Basis: INFERRED (the secondary claim is unverified)
- VERIFY: Q01 PARTIAL, Q03 PARTIAL
- From: G6-85
