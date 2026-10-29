# Counterfactual Intervention Generation & Quality-Control Report

Date: 2026-10-29 (Updated 2026-10-30)  
Auditors: Multidisciplinary Research Team (Medical-Imaging Scientist, CV Engineer)  
Compliance: Strict adherence to Part 8 (Intervention Engine & Quality Control)

---

## 1. Executive Summary & Quality Control Pass Rate

- **Total Interventions Audited:** 1200
- **Strict Quality-Control Pass Rate:** **100.00%** (1200 / 1200)
- **Non-Target Pixel Invariance (< 1e-5):** **100.0%** (Zero corruption of pixels outside intervention mask)
- **Numerical Integrity:** Zero NaNs, zero Infs, zero out-of-bounds intensity values.
- **Evaluated Slices Coverage:** 100% of all 90 evaluated slices in `predictions/intervention_effects.csv` (45 Cheng + 45 BRISC) have verified QC records in `manifests/intervention_qc.csv`.
- **Diagnostic Visual Montages Saved:** 24 8-panel high-resolution images in `reports/intervention_montages/`.

---

## 2. Quantitative Intervention Metrics by Region and Method

| Dataset | Region | Method | Mean Mask Area (px) | Mean Inside MAD | Max Outside Diff | Boundary Discontinuity | QC Status |
|---|---|---|---|---|---|---|---|
| **BRISC** | `core` | matched_texture_fill | 1033.9 | 0.2594 | 0.00e+00 | 0.3788 | **PASS** |
| **BRISC** | `core` | telea_inpaint | 1033.9 | 0.2323 | 0.00e+00 | 0.3737 | **PASS** |
| **BRISC** | `immediate` | matched_texture_fill | 754.4 | 0.1745 | 0.00e+00 | 0.3866 | **PASS** |
| **BRISC** | `immediate` | telea_inpaint | 754.4 | 0.0774 | 0.00e+00 | 0.2065 | **PASS** |
| **BRISC** | `outer` | matched_texture_fill | 2369.4 | 0.1726 | 0.00e+00 | 0.3838 | **PASS** |
| **BRISC** | `outer` | telea_inpaint | 2369.4 | 0.0936 | 0.00e+00 | 0.1925 | **PASS** |
| **BRISC** | `remote` | matched_texture_fill | 290.3 | 0.2290 | 0.00e+00 | 0.6062 | **PASS** |
| **BRISC** | `remote` | telea_inpaint | 290.3 | 0.1537 | 0.00e+00 | 0.2903 | **PASS** |
| **BRISC** | `sham` | matched_texture_fill | 1028.5 | 0.1763 | 0.00e+00 | 0.3406 | **PASS** |
| **BRISC** | `sham` | telea_inpaint | 1028.5 | 0.0927 | 0.00e+00 | 0.1616 | **PASS** |
| **CHENG** | `core` | matched_texture_fill | 992.2 | 0.2158 | 0.00e+00 | 0.3881 | **PASS** |
| **CHENG** | `core` | telea_inpaint | 992.2 | 0.1561 | 0.00e+00 | 0.3522 | **PASS** |
| **CHENG** | `immediate` | matched_texture_fill | 511.1 | 0.1495 | 0.00e+00 | 0.3505 | **PASS** |
| **CHENG** | `immediate` | telea_inpaint | 511.1 | 0.0880 | 0.00e+00 | 0.2408 | **PASS** |
| **CHENG** | `outer` | matched_texture_fill | 2107.8 | 0.1694 | 0.00e+00 | 0.3548 | **PASS** |
| **CHENG** | `outer` | telea_inpaint | 2107.8 | 0.0873 | 0.00e+00 | 0.1725 | **PASS** |
| **CHENG** | `remote` | matched_texture_fill | 236.8 | 0.1825 | 0.00e+00 | 0.4827 | **PASS** |
| **CHENG** | `remote` | telea_inpaint | 236.8 | 0.1163 | 0.00e+00 | 0.1869 | **PASS** |
| **CHENG** | `sham` | matched_texture_fill | 990.3 | 0.2091 | 0.00e+00 | 0.4853 | **PASS** |
| **CHENG** | `sham` | telea_inpaint | 990.3 | 0.1322 | 0.00e+00 | 0.2471 | **PASS** |

---

## 3. Methodological Guarantees

1. **Non-Overlapping Regional Topology:**
   - Ground truth core ($R_{core}$), immediate margin ($R_{immediate}$, 4px), outer margin ($R_{outer}$, 12px), sham control ($R_{sham}$), and remote context ($R_{remote}$) are strictly disjoint.
   - The sham control is geometrically matched in area and contour to the core and placed within intracranial parenchyma ($S$) in normal contralateral brain tissue, ensuring zero intersection with the lesion or its peritumoral rings.
