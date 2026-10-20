# Task 13: Checksum and Test Count Reconciliation Audit

**Audit Date:** October 2026  
**Auditor:** Independent Scientific Audit Lead (Antigravity IDE)  
**Target Invariants:** `publication/manuscript_v1/checksums.json` and `test_results.txt`.

---

## 1. Executive Status of Verification

- **Bitwise Verification of `checksums.json`:**
  - Every single one of the 48 files listed in `publication/manuscript_v1/checksums.json` was independently verified against disk using SHA-256.
  - **Result: 48 / 48 files (100%) match bit-for-bit.**
  - `test_results.txt` actual SHA-256: `82c92ec0e3f2667e52d9dc7be9a1c5748fb53bcd4c65305fc1bdc2254592b7f8` (Matches `checksums.json` line 15 exactly).

---

## 2. Root Cause of Reported Conflict (167 vs 172 Tests)

A documentation conflict was flagged in earlier audit summaries regarding whether 167 or 172 tests passed:

1. **Source of "167":**
   - Found in `publication/manuscript_v1/reproducibility_checklist.md`, line 59:
     `- [x] **Automated Regression Suite:** 167 repository tests passing across all 11 phases.`
2. **Source of "172":**
   - Found in `publication/manuscript_v1/test_results.txt`, lines 6 and 181:
     `collected 172 items ... 172 passed in 26.53s`
3. **Reconciliation & Root Cause:**
   - Phases 1 through 9.2 originally comprised 167 tests across 16 test files.
   - When the final publication package validation suite was constructed (`tests/test_publication_package_v1.py`), exactly **5 new verification tests** were added:
     1. `test_publication_package_deliverables_exist`
     2. `test_all_publication_figures_exist_in_png_and_pdf`
     3. `test_publication_tables_numerical_fidelity`
     4. `test_manuscript_docx_validity`
     5. `test_manuscript_claims_and_safeguards`
   - Total test count: $167 + 5 = 172$ tests.
   - When `pytest tests/ -v` was executed, all 172 tests passed, and the full output was saved into `test_results.txt`.
   - However, the markdown prose in `reproducibility_checklist.md` line 59 was written during Phase 9.2 before the 5 publication tests were appended, leaving a stale static string `167`.

---

## 3. Resolution Action

- `test_results.txt` is the authoritative, verified execution log.
- `reproducibility_checklist.md` must be updated to reflect the true count of 172 passing tests.
- Zero checksums were corrupted; the file contents match their hashes bit-for-bit.
