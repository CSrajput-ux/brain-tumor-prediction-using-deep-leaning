# Limitations, Failure Modes & Epistemic Boundaries

**Document ID:** `PHASE_9_LIMITATIONS_AND_FAILURE_MODES`  
**Project:** Cheng Brain Tumor MRI Classification Robustness Study  
**Phase:** 9 — Controlled Experiment: Seam Artifacts vs. Spatial-Layout Disruption  
**Date:** 2026-10-17  
**Authoritative Standard:** Adversarial Robustness & Epistemic Boundary Audit  

---

## 1. Methodological & Intervention Limitations

1. **Inherent Confound of Spatial Disruption vs. Natural Anatomy:**
   - Any mathematical transformation that permutes or rearranges tiles of a continuous brain MRI inevitably introduces some degree of out-of-distribution (OOD) perturbation.
   - While Condition C2 ($I_{\text{seamless}}$) suppresses the sharp step-edge gradient by over 60% through distance-weighted boundary blending, the juxtaposition of mismatched parenchymal tissues (e.g. cortical gyri adjacent to lateral ventricles) remains an atypical anatomical configuration.
   - Consequently, performance degradation under C2 reflects sensitivity to disrupted macroscopic cranial spatial arrangement, but cannot be equated with a physiological or clinical state.

2. **2D Projection vs. 3D Volumetric Cranial Anatomy:**
   - All spatial interventions are performed on 2D T1-CE cross-sectional slices.
   - In clinical neuro-oncology, anatomical context is inherently 3D (axial, sagittal, coronal continuity, stereotactic coordinates, relationship to cranial nerves and skull-base foramina).
   - Manipulating 2D tiles isolates 2D convolutional filter dependencies, but does not simulate 3D anatomical disorientation.

3. **Single Architecture Scope (ResNet-50):**
   - The 15 frozen checkpoints evaluated across scenarios S0, S1, and S2 are ResNet-50 convolutional architectures.
   - Convolutional layers possess strong local inductive biases that are intrinsically sensitive to spatial translation and high-frequency textures.
   - Whether Vision Transformers (ViTs) or MLP-Mixer architectures exhibit identical sensitivity profiles to seam suppression remains an unverified question.

---

## 2. In Silico Epistemic Boundaries (No Biological or Clinical Causality)

1. **Model Representation Audit vs. Human Biology:**
   - In accordance with Castro et al. (*Nature Communications*, 2020), pixel-level image interventions probe the computational associations internal to a neural network.
   - They **do not establish biological mechanisms, cellular etiology, or surgical truth.**
2. **No Claim of Clinical Diagnostic Redundancy:**
   - If a classifier proves resilient to certain spatial context disruptions, this does not mean that radiologists or oncologists do not require cranial anatomical landmarks to diagnose brain tumors.
   - Machine learning shortcuts and clinical diagnostic workflows operate under fundamentally distinct decision principles.

---

## 3. Potential Failure Modes and Mitigation Safeguards

| Potential Failure Mode | Manifestation | Diagnostic Safeguard Implemented |
| :--- | :--- | :--- |
| **Leakage Contamination** | Near-duplicate slices inflate baseline performance | Evaluated across 3 distinct scenarios: S0 (strict patient split), S1 (SSIM 0.80), S2 (SSIM 0.75). |
| **Tumor Core Corruption** | Intervention inadvertently alters lesion pixels | 100% bit-exact verification across all 3,064 slices (`assert diff == 0`). |
| **Outlier Patient Driving Effect** | A single patient's slices produce apparent collapse | Patient-level distributions computed and verified across all 233 patient clusters. |
| **Double Edge Creation** | Overwriting tile borders introduces extra step gradients | Distance-weighted blending smoothly fades transitions rather than inserting hard strips. |
| **Cluster Resampling Violation** | Slices from same patient resampled independently | Synchronized paired patient-cluster bootstrap ($B=2,000$, seed 42) ensures identical clusters evaluate all conditions concurrently. |
