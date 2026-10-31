# Contralateral Sham Placement Geometry Audit Report

- **Total Unique QC Slices Evaluated:** 120 (60 Cheng, 60 BRISC)
- **Route 1 (Exact Vertical Midline Reflection):** 27 / 120 (22.5%)
- **Route 2 (Affine Translated Mirrored Contour in Tissue):** 93 / 120 (77.5%)
- **Route 3 (Circular Fallback Patch):** 0 / 120 (0.0%)
- **Contour Template Retention Rate:** 100.0% (120 / 120 slices)
- **Mean Sham-to-Core Area Ratio:** 0.9975 +/- 0.0227 (range [0.7525, 1.0000])
- **Mean Template Dice Similarity:** 0.9986 +/- 0.0130
- **Peripheral Intracranial Boundary Clipping:** 5 / 120 (4.2%) slices experienced slight intracranial tissue masking (minimum area ratio 0.7525).
- **Unclipped Exact Parity (Ratio = 1.0000):** 115 / 120 (95.8%) slices achieved exact pixel-for-pixel contour area parity.

## Conclusion & Scientific Verification
Across all 120 unique evaluated MRI slices:
1. 100% of sham interventions (120/120) utilized the patient's actual lesion-derived mirrored contour template (27 via direct midline reflection, 93 via rigid affine translation within normal brain parenchyma). Zero slices required unconstrained circular fallback patches.
2. In 115 out of 120 slices (95.8%), the placed sham contour achieved exact 1.0000 geometric parity with the tumour core.
3. In 5 slices (4.2%), slight boundary clipping against the intracranial tissue mask reduced the placed sham area (minimum ratio 0.7525), yielding an overall mean sham-to-core area ratio of 0.9975 +/- 0.0227 and mean template Dice overlap of 0.9986 +/- 0.0130.
