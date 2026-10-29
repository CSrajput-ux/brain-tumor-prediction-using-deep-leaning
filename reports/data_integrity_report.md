# Data Integrity, Modality, and Quality Control Report

**Date:** 2026-10-29  
**Datasets:** Cheng CE-T1 MRI ($N=3,064$) & BRISC Multi-Plane CE-MRI ($N=6,000$)  

---

## 1. Cheng Dataset Auditing (Cheng et al., 2015)

- **Modality & Contrast:** T1-weighted contrast-enhanced magnetic resonance imaging (CE-T1).
- **Format:** MATLAB v7 `.mat` files containing 512 × 512 slice matrices, patient IDs (`PID`), ground-truth label codes (1: meningioma, 2: glioma, 3: pituitary), and radiologist-delineated contour coordinates.
- **Audit Findings:**
  - 3,064 / 3,064 files readable (100% integrity).
  - Patient distribution: 233 unique patients. Slices per patient range from 1 to 78 (mean 13.15).
  - Class distribution: Meningioma: 708 slices (23.1%); Glioma: 1,426 slices (46.5%); Pituitary: 930 slices (30.4%).
  - Zero missing or corrupt masks.
  - After robust percentile intensity scaling ($[P_1, P_{99}]$) and aspect-ratio-preserving letterbox padding to $224 \times 224$, exactly 0 / 3,064 masks disappeared. Mask centroid drift was bounded within 0.00166 normalized units.

---

## 2. BRISC Dataset Auditing (Fateh et al., 2026)

- **Modality & Partition:** Multi-plane contrast-enhanced brain MRI (Axial, Coronal, Sagittal) across 4 classes: Glioma, Meningioma, Pituitary tumour, and No-tumour controls.
- **Official Split:** 5,000 training images, 1,000 testing images.
- **Audit Findings:**
  - 6,000 / 6,000 files readable.
  - Class distribution: Glioma: 1,401 (23.4%); Meningioma: 1,635 (27.2%); Pituitary: 1,757 (29.3%); No-tumour: 1,207 (20.1%).
  - Mask availability: 860 out of 1,000 test slices contain usable ground-truth segmentation masks.
  - Preprocessing alignment: 0 / 860 masks lost; centroid drift bounded within 0.00351 normalized units.

---

## 3. Cross-Dataset Overlap (Cheng vs BRISC)

- **Exact Duplicate Audit:** 0 exact duplicate pairs detected across all 3,064 Cheng and 6,000 BRISC slices.
- **Structural Similarity (SSIM):** Pairwise SSIM values across datasets ranged from 0.28 to 0.58 (mean 0.42, all $< 0.70$), confirming distinct clinical cohorts and independent scanner acquisitions.

