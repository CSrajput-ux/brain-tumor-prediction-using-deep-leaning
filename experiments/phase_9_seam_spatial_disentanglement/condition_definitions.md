# Mathematical & Architectural Condition Definitions

**Document ID:** `PHASE_9_CONDITION_DEFINITIONS`  
**Phase:** 9 — Controlled Experiment: Seam Artifacts vs. Spatial-Layout Disruption  
**Date:** 2026-10-17  
**Authoritative Standard:** Geometric & Algorithmic Intervention Specification  

---

## 1. Geometric Foundations

Let $I \in [0, 255]^{H \times W}$ denote the native 2D T1-CE MRI slice ($H=W=512$).  
Let $M_{\text{tumor}} \in \{0, 1\}^{H \times W}$ denote the binary tumor segmentation mask.  
Let $E_{15}$ denote the structuring element of radius $r=15$ pixels with elliptical geometry:
$$E_{15} = \{(dx, dy) : dx^2 + dy^2 \le 15^2\}$$

The protected anatomical zone $M_{\text{protected}}$ is defined by morphological dilation:
$$M_{\text{protected}} = M_{\text{tumor}} \oplus E_{15}$$

### Distant Grid Partition:
The image is partitioned into a regular grid of non-overlapping $16 \times 16$ pixel patches ($G_y = 32, G_x = 32$, total 1,024 patches):
$$P_{gy, gx} = I[16 \cdot gy : 16 \cdot (gy + 1), 16 \cdot gx : 16 \cdot (gx + 1)]$$

The set of **eligible distant coordinates** $\Omega_{\text{distant}}$ includes only patches that have zero intersection with the protected anatomical zone:
$$\Omega_{\text{distant}} = \left\{(gy, gx) : \sum_{y=16gy}^{16(gy+1)-1} \sum_{x=16gx}^{16(gx+1)-1} M_{\text{protected}}[y, x] = 0\right\}$$

For each sample $s$, a deterministic pseudo-random permutation $\pi_s$ of $\Omega_{\text{distant}}$ is generated:
$$\text{seed}_s = (42 + \text{SHA256}(s)_{0:8}) \pmod{2^{32}}$$

---

## 2. Formal Specification of Evaluated Conditions

### Condition C0: Original Baseline ($I_{\text{orig}}$)
$$I_{\text{C0}} = I$$
- Unmanipulated native slice.
- Serves as the ground-truth reference for performance and image statistics.

---

### Condition C1: Seam-Only Control ($I_{\text{seam\_only}}$)
- **Objective:** Introduce artificial tile-boundary discontinuities matching C5LP without permuting the underlying anatomical content.
- **Mathematical Definition:**
  For each eligible patch $(gy, gx) \in \Omega_{\text{distant}}$, the anatomical structures remain in their original positions, but the tile is shifted by the DC mean difference of the scrambled patch that would have occupied that location under permutation $\pi_s$:
  $$\Delta \mu_{gy, gx} = \mu(P_{\pi_s(gy, gx)}) - \mu(P_{gy, gx})$$
  $$I_{\text{C1}}[y, x] = \begin{cases}
  \text{clip}(I[y, x] + \Delta \mu_{gy, gx}, 0, 255) & \text{if } (gy, gx) \in \Omega_{\text{distant}} \\
  I[y, x] & \text{if } M_{\text{protected}}[y, x] = 1
  \end{cases}$$
- **Key Invariants:**
  1. Anatomical content within every tile is **100% unpermuted and intact**.
  2. Across every tile boundary in $\Omega_{\text{distant}}$, an artificial DC step discontinuity $\Delta \mu_{gy, gx} - \Delta \mu_{gy', gx'}$ is generated, reproducing the high-frequency seam edge jump of C5LP.
  3. Tumor core and 15px margin have **exactly 0 pixels altered**.

---

### Condition C2: Seam-Suppressed Spatial Rearrangement ($I_{\text{seamless}}$)
- **Objective:** Rearrange macroscopic cranial layout (permuting tiles) while suppressing the sharp high-frequency boundary seams.
- **Mathematical Definition:**
  First, distant patches are permuted under $\pi_s$ (identical to C5LP):
  $$I_{\text{permuted}}[16gy : 16(gy+1), 16gx : 16(gx+1)] = P_{\pi_s(gy, gx)}$$
  Second, let $S_{\text{grid}} \in \{0, 1\}^{H \times W}$ denote the 1-pixel boundary grid separating adjacent patches in $\Omega_{\text{distant}}$.  
  Let $D(y, x)$ denote the Euclidean distance to the nearest seam grid line.  
  A distance-weighted blending kernel with window width $w_b = 4$ pixels and Gaussian smoothing ($\sigma = 2.5$, $k=9$) is applied along the seam transitions:
  $$\alpha(y, x) = \max\left(0, 1 - \frac{D(y, x)}{w_b}\right)$$
  $$I_{\text{C2}}[y, x] = \begin{cases}
  I[y, x] & \text{if } M_{\text{protected}}[y, x] = 1 \\
  (1 - \alpha(y, x)) \cdot I_{\text{permuted}}[y, x] + \alpha(y, x) \cdot \text{Blur}(I_{\text{permuted}})[y, x] & \text{otherwise}
  \end{cases}$$
- **Key Invariants:**
  1. Distant anatomical patches are **completely rearranged** across the brain slice.
  2. The boundary step gradient along tile seams is suppressed by over $60\%$, holding high-frequency edge energy close to the baseline level.
  3. Tumor core and 15px margin have **exactly 0 pixels altered**.

---

### Condition C3: Original Scramble Reference ($I_{\text{C5LP}}$)
- **Objective:** Historical reference condition reproducing Phase 6.
- **Mathematical Definition:**
  $$I_{\text{C3}}[16gy : 16(gy+1), 16gx : 16(gx+1)] = \begin{cases}
  P_{\pi_s(gy, gx)} & \text{if } (gy, gx) \in \Omega_{\text{distant}} \\
  I[y, x] & \text{if } M_{\text{protected}}[y, x] = 1
  \end{cases}$$
- Replicates the $+97.9\%$ Sobel gradient spike and the reported $\Delta \approx +0.42$ collapse.
