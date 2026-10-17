# Supplementary Methods

**Manuscript Title:** Disentangling Synthetic Edge Artifacts and Spatial-Context Sensitivity in Brain MRI Tumour Classification: A Multi-Control Spatial Intervention Study  
**Publication Package:** `publication/manuscript_v1/`  
**Date:** 2026-10-17  

---

## 1. Dataset Preprocessing & Invariant Protection Protocol

### 1.1 Dataset Provenance & Patient Grouping
The dataset originates from the open-access Cheng et al. brain tumour MRI repository (Figshare article 1512427), consisting of 3,064 2D contrast-enhanced T1-weighted axial slices acquired from 233 patients treated at Nanfang Hospital and General Hospital of Tianjin Medical University.

Each `.mat` file was preprocessed into paired 8-bit grayscale PNG images and binary segmentation masks (`prepared_full_run/`). All 233 unique patient identifiers (`PID`) were extracted directly from the underlying MATLAB data fields.

### 1.2 Protection Geometry
To prevent experimental interventions from disturbing diagnostic pathology:
1. **Tumour Core:** The original ground-truth segmentation mask $M_{\text{tumor}}$ was converted into an exact boolean mask.
2. **Peritumoral Margin Ring:** A 15-pixel dilation margin was computed via morphological dilation with an elliptical structuring element $E_{31\times31}$ (diameter 31 pixels):
   $$M_{\text{margin}} = (M_{\text{tumor}} \oplus E_{31\times31}) \setminus M_{\text{tumor}}$$
3. **Protected Zone Invariant:** The protected region mask is defined as $M_{\text{protected}} = M_{\text{tumor}} \cup M_{\text{margin}}$. In every slice and across all experimental conditions, any modification within $M_{\text{protected}}$ is strictly prohibited:
   $$\forall (x, y) \in M_{\text{protected}}, \quad I_{\text{condition}}(x, y) \equiv I_{\text{original}}(x, y)$$

---

## 2. Mathematical Definition of Experimental Interventions

Images of dimensions $H \times W$ (where $H, W \in \{512, 256\}$) are partitioned into non-overlapping grid tiles of size $P \times P$ ($P = 16$). Let $(g_y, g_x)$ denote the grid coordinate of a tile, where $g_y \in \{0, \dots, \lfloor H/P \rfloor - 1\}$ and $g_x \in \{0, \dots, \lfloor W/P \rfloor - 1\}$.

A tile is designated as eligible distant context if and only if it has zero intersection with the protected zone:
$$\Omega_{\text{distant}} = \left\{ (g_y, g_x) \mid \sum_{y=g_y P}^{(g_y+1)P - 1} \sum_{x=g_x P}^{(g_x+1)P - 1} M_{\text{protected}}(y, x) = 0 \right\}$$

Let $K = |\Omega_{\text{distant}}|$ denote the number of eligible distant tiles, and let $\pi: \{1, \dots, K\} \to \{1, \dots, K\}$ be a deterministic pseudo-random permutation seeded by:
$$\text{seed} = (42 + \text{hash}(\text{sample\_id})) \pmod{2^{32}}$$

### 2.1 Condition $C_0$ — Baseline
$$I_{C0}(x, y) = I_{\text{original}}(x, y)$$

### 2.2 Condition $C_3$ — Raw Historical Scrambling ($C_{5\text{LP}}$)
For each tile index $i \in \{1, \dots, K\}$ with grid coordinate $(g_y, g_x) = \Omega_{\text{distant}}(i)$, the image pixels are replaced by the corresponding permuted tile $\pi(i)$:
$$I_{C3}(g_y P + \Delta y, g_x P + \Delta x) = I_{\text{original}}(g_y' P + \Delta y, g_x' P + \Delta x)$$
where $(g_y', g_x') = \Omega_{\text{distant}}(\pi(i))$.

### 2.3 Condition $C_1$ — Seam-Only Control
Condition $C_1$ introduces inter-tile step discontinuities matching the local DC offsets of condition $C_3$, while leaving the interior anatomical content of every tile strictly unpermuted.

For each distant tile $i$ at coordinate $(g_y, g_x)$:
$$\Delta \mu_i = \text{mean}\left(I_{\text{original}}[\Omega_{\text{distant}}(\pi(i))]\right) - \text{mean}\left(I_{\text{original}}[\Omega_{\text{distant}}(i)]\right)$$
Inside tile $i$, pixel values are shifted by this scalar offset:
$$I_{C1}(y, x) = \text{clip}\left(I_{\text{original}}(y, x) + \Delta \mu_i, 0, 255\right)$$
Because $\Delta \mu_i$ is a uniform scalar across the tile, the internal gradient within each tile is identical to original tissue ($\nabla I_{C1} \equiv \nabla I_{\text{original}}$), while across adjacent tile boundaries, a step discontinuity of magnitude $|\Delta \mu_i - \Delta \mu_j|$ is produced.

### 2.4 Condition $C_2$ — Seam-Suppressed Spatial Rearrangement
Condition $C_2$ permutes the distant-context tiles according to $\pi$, but suppresses artificial tile-boundary discontinuities using a distance-weighted Gaussian cross-fade along tile borders.

Along all adjacent boundaries between distant tiles, a boundary transition strip of half-width $w = 4$ pixels is cross-faded using a distance weight:
$$\alpha(d) = \frac{1}{2} \left[1 + \text{erf}\left(\frac{d}{\sigma \sqrt{2}}\right)\right], \quad \sigma = 2.5$$
where $d \in [-w, w]$ is the signed Euclidean distance to the 1-pixel seam interface. Outside the blending strip, $I_{C2}$ contains the permuted tile. Within the strip, pixels smoothly interpolate between the adjacent permuted tiles, eliminating step discontinuities.

---

## 3. Radiometric & Image Diagnostic Metrics

1. **Sobel Gradient Energy:**
   Horizontal and vertical gradients are computed via $3\times3$ Sobel operators:
   $$G(x, y) = \sqrt{\left(\frac{\partial I}{\partial x}\right)^2 + \left(\frac{\partial I}{\partial y}\right)^2}$$
   - *Whole Image Sobel:* Mean $G(x, y)$ over all non-zero image pixels.
   - *Tile Boundary Seam Sobel:* Mean $G(x, y)$ over a 3-pixel-wide mask covering all inter-tile grid boundary lines within distant context.
   - *Tile Interior Sobel:* Mean $G(x, y)$ over the central $12\times12$ interior region of distant tiles (eroded by 2 pixels from all boundaries).
2. **Fourier High-Frequency Spectral Energy:**
   Computed via 2D Discrete Fourier Transform:
   $$\mathcal{F}(u, v) = \sum_{y=0}^{H-1} \sum_{x=0}^{W-1} I(y, x) e^{-j 2\pi (ux/W + vy/H)}$$
   Let $r = \sqrt{(u - H/2)^2 + (v - W/2)^2}$ denote spatial frequency radius. The high-frequency spectral energy is the mean log magnitude for $r > 0.25 \min(H, W)$.

---

## 4. Clustered Statistical Inference

1. **Cluster Bootstrap Procedure:**
   - Sample unit: Patient identifier in Scenario $S_0$ (233 clusters); combined duplicate group identifier in Scenarios $S_1$ (219 clusters) and $S_2$ (178 clusters).
   - Replicates: $B = 2,000$ independent cluster resamplings with replacement.
   - Paired Synchronization: Within replicate $b \in \{1, \dots, B\}$, the identical vector of resampled cluster IDs is used to evaluate condition $A$ and condition $B$.
   - Macro-F1 delta distribution:
     $$\Delta^{(b)} = \text{Macro-F1}_A^{(b)} - \text{Macro-F1}_B^{(b)}$$
   - 95% Confidence Intervals are calculated as the empirical 2.5th and 97.5th percentiles of $\{\Delta^{(b)}\}_{b=1}^B$.
2. **McNemar Discordance Test:**
   Constructed from paired binary sample-level classification outcomes $(y_A == y_{\text{true}}, y_B == y_{\text{true}})$:
   $$\chi^2 = \frac{(|n_{10} - n_{01}| - 1)^2}{n_{10} + n_{01}}, \quad p = 1 - F_{\chi^2_1}(\chi^2)$$
3. **Multiplicity Adjustment:**
   Holm-Bonferroni step-down procedure applied across the complete family of 15 confirmatory contrasts simultaneously at family-wise error rate $\alpha = 0.05$.
