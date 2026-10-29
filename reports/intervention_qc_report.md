# Counterfactual Intervention Generation & Quality-Control Report

Date: 2026-10-29 (Asia/Kolkata)  
Auditors: Multidisciplinary Research Team (Medical-Imaging Scientist, CV Engineer)  
Compliance: Strict adherence to Part 8 (Intervention Engine & Quality Control)

---

## 1. Executive Summary & Quality Control Pass Rate

- **Total Interventions Audited:** 1200
- **Strict Quality-Control Pass Rate:** **100.00%** (1200 / 1200)
- **Non-Target Pixel Invariance (< 1e-5):** **100.0%** (Zero corruption of pixels outside intervention mask)
- **Numerical Integrity:** Zero NaNs, zero Infs, zero out-of-bounds intensity values.
- **Diagnostic Visual Montages Saved:** 24 8-panel high-resolution images in `reports/intervention_montages/`.

---

## 2. Quantitative Intervention Metrics by Region and Method

| Dataset | Region | Method | Mean Mask Area (px) | Mean Inside MAD | Max Outside Diff | Boundary Discontinuity | QC Status |
|---|---|---|---|---|---|---|---|
| **BRISC** | `core` | matched_texture_fill | 959.0 | 0.2579 | 0.00e+00 | 0.3779 | **PASS** |
| **BRISC** | `core` | telea_inpaint | 959.0 | 0.2281 | 0.00e+00 | 0.3672 | **PASS** |
| **BRISC** | `immediate` | matched_texture_fill | 708.0 | 0.1769 | 0.00e+00 | 0.3857 | **PASS** |
| **BRISC** | `immediate` | telea_inpaint | 708.0 | 0.0807 | 0.00e+00 | 0.2151 | **PASS** |
| **BRISC** | `outer` | matched_texture_fill | 2246.1 | 0.1654 | 0.00e+00 | 0.3713 | **PASS** |
| **BRISC** | `outer` | telea_inpaint | 2246.1 | 0.0884 | 0.00e+00 | 0.1844 | **PASS** |
| **BRISC** | `remote` | matched_texture_fill | 272.0 | 0.2566 | 0.00e+00 | 0.6419 | **PASS** |
| **BRISC** | `remote` | telea_inpaint | 272.0 | 0.1821 | 0.00e+00 | 0.3253 | **PASS** |
| **BRISC** | `sham` | matched_texture_fill | 953.5 | 0.2005 | 0.00e+00 | 0.3805 | **PASS** |
| **BRISC** | `sham` | telea_inpaint | 953.5 | 0.1083 | 0.00e+00 | 0.1921 | **PASS** |
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

2. **Dual-Method Perturbation:**
   - **Method A (Telea Inpainting):** Solves the Fast Marching Method boundary PDE to inpaint tissue smoothly across the target region.
   - **Method B (Locally Matched Texture):** Estimates local background parenchyma mean and Gaussian variance from the surrounding tissue ring, applying a 2-pixel cosine/distance taper to avoid high-frequency cliff artifacts.

3. **Strict Outside Invariance:**
   - In all interventions, outside the specified region mask $M$, $x_{edit}(u, v) \equiv x(u, v)$ to floating point precision ($|\Delta| < 10^{-5}$).
