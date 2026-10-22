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

### 2.2 Condition $C_{1\text{,historical\_dc\_offset}}$ — Historical Whole-Tile DC-Offset Control
Condition $C_{1\text{,historical\_dc\_offset}}$ introduces whole-tile step discontinuities matching the local DC offsets of raw scrambling, while leaving the spatial tile assignments unpermuted.
For each distant tile $i$ at coordinate $(g_y, g_x)$:
$$\Delta \mu_i = \text{mean}\left(I_{\text{original}}[\Omega_{\text{distant}}(\pi(i))]\right) - \text{mean}\left(I_{\text{original}}[\Omega_{\text{distant}}(i)]\right)$$
Inside tile $i$, pixel values are shifted by this scalar offset:
$$I_{C1}(y, x) = \text{clip}\left(I_{\text{original}}(y, x) + \Delta \mu_i, 0, 255\right)$$
Within each tile, the internal gradient is identical to original tissue ($\nabla I_{C1} \equiv \nabla I_{\text{original}}$), while across adjacent tile boundaries, a whole-patch step discontinuity of magnitude $|\Delta \mu_i - \Delta \mu_j|$ is produced.

### 2.3 Condition $C_{1\text{,true\_seam\_w2}}$ — Pure 2-Pixel Boundary Seam Control
Condition $C_{1\text{,true\_seam\_w2}}$ restricts synthetic step adjustments strictly to a 1-pixel boundary strip on each side of adjacent tile interfaces ($w = 2$). The inner $14 \times 14$ pixels of every distant tile, the tumour core, and the 15-pixel margin ring remain 100% bit-for-bit identical to baseline $C_0$ (81.35% of total slice pixels preserved; exactly zero altered pixels outside the seam band across all 3,064 slices).

### 2.4 Condition $C_{1\text{,true\_seam\_w3}}$ — Amplified Seam Control (Legacy Identifier)
Condition $C_{1\text{,true\_seam\_w3}}$ applies the same two-pixel-wide boundary modification as the gain-1.0 control, but with amplification gain $\alpha = 1.8$. The `_w3` suffix is a legacy code identifier; it does not denote a three-pixel-wide modification. The control preserves tile-interior anatomy, the tumour core and the protected margin.

### 2.5 Condition $C_2$ — Locally Blended Spatial Rearrangement
Condition $C_2$ permutes the distant-context tiles according to $\pi$, but suppresses artificial tile-boundary discontinuities using a distance-weighted Gaussian cross-fade along tile borders.
Along all adjacent boundaries between distant tiles, a boundary transition strip of half-width $w = 4$ pixels is cross-faded using a distance weight:
$$\alpha(d) = \frac{1}{2} \left[1 + \text{erf}\left(\frac{d}{\sigma \sqrt{2}}\right)\right], \quad \sigma = 2.5$$
where $d \in [-w, w]$ is the signed Euclidean distance to the 1-pixel seam interface. Outside the blending strip, $I_{C2}$ contains the permuted tile. Within the strip, pixels smoothly interpolate between the adjacent permuted tiles, eliminating step discontinuities.

### 2.6 Condition $C_3$ — Raw Historical Scrambling ($C_{5\text{LP}}$)
For each tile index $i \in \{1, \dots, K\}$ with grid coordinate $(g_y, g_x) = \Omega_{\text{distant}}(i)$, the image pixels are replaced by the corresponding permuted tile $\pi(i)$:
$$I_{C3}(g_y P + \Delta y, g_x P + \Delta x) = I_{\text{original}}(g_y' P + \Delta y, g_x' P + \Delta x)$$
where $(g_y', g_x') = \Omega_{\text{distant}}(\pi(i))$.

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
   Let $r = \sqrt{(u - H/2)^2 + (v - W/2)^2}$ denote spatial frequency radius. The high-frequency spectral energy is the mean log magnitude for $r > 0.25 \min(H, W)$. Evaluated at both source resolution ($512\times512$) and model input resolution ($224\times224$).

---

## 4. Clustered Statistical Inference

1. **Primary Uncertainty Analysis: Paired Patient-Cluster Bootstrap Percentile CIs:**
   - **Resampling Unit:** Patient cluster in Scenario $S_0$ (233 clusters); combined duplicate-group cluster in Scenarios $S_1$ (219 clusters) and $S_2$ (178 clusters).
   - **Replicate Scale:** $B = 25,000$ independent cluster resamplings with replacement (zero degenerate/invalid iterations across all clusters).
   - **Paired Synchronization:** In each bootstrap replicate $b \in \{1, \dots, B\}$, identical cluster draw indices are assigned to Condition A and Condition B across all 15 checkpoints ($3 \text{ scenarios} \times 5 \text{ folds}$), fully preserving pairing across conditions and folds.
   - **Cluster Size Weighting:** Unequal cluster slice counts are preserved naturally: confusion matrices are pre-aggregated per cluster, and replicate confusion matrices are formed by weighted summation:
     $$\mathbf{C}_{\text{boot}}^{(b)} = \sum_{k=1}^K w_k^{(b)} \mathbf{C}_k$$
     where $w_k^{(b)}$ is the number of times cluster $k$ was selected in replicate $b$.
   - **Primary Metric:** Macro-F1 delta distribution $\Delta^{(b)} = \text{Macro-F1}_A^{(b)} - \text{Macro-F1}_B^{(b)}$. The primary reported uncertainty interval is the 95% percentile confidence interval: $[\text{CI}_{2.5\%}, \text{CI}_{97.5\%}]$.
   - **Multiplicity / Equivalence Status:** Unadjusted CIs are reported alongside Holm family-adjusted inference. CIs including zero do not imply statistical equivalence; equivalence claims require a pre-specified equivalence margin and formal two one-sided tests (TOST).

2. **Secondary Exploratory Metric (Davison-Hinkley Bound):**
   - The empirical bootstrap bound is defined as:
     $$p_{\text{empirical}} = \min\left(1.0, 2 \times \frac{1 + \sum_{b=1}^B \mathbb{I}(\Delta^{(b)} \le 0)}{B + 1}\right)$$
   - Documented strictly as an empirical percentile bound, NOT a formal null-hypothesis p-value.
   - Wald Studentized Asymptotic Z-Score: $z = \Delta / \text{SE}_{\text{boot}}$, with $p_{\text{wald}} = 2 \Phi(-|z|)$.

3. **Exact Log-Space McNemar Discordance Test:**
   - Evaluated on paired binary classification outcomes across all $N$ held-out slices. Let $n_{10}$ denote cases where Condition A was correct and Condition B incorrect, and $n_{01}$ vice versa ($N_{\text{discordant}} = n_{10} + n_{01}$).
   - The two-sided exact binomial p-value is computed in log space via `scipy.special.logsumexp`:
     $$\ln p_{\text{exact}} = \ln(2) + \text{logsumexp}_{i=0}^k \left[ \ln\Gamma(N+1) - \ln\Gamma(i+1) - \ln\Gamma(N-i+1) - N \ln(2) \right]$$
     where $k = \min(n_{10}, n_{01})$. For balanced discordance ($k = N/2$) or $N=0$, $p=1.0$ ($\log_{10} p = 0.0$).
   - For extreme values beyond IEEE-754 double precision ($p < 10^{-308}$), the exact log value is preserved in `mcnemar_exact_log10_p` with `mcnemar_exact_underflow = True`, avoiding underflow to uninformative 0.0.
   - Edwards continuity-corrected $\chi^2$ p-values are computed and stored as a separate asymptotic statistic (`mcnemar_asymptotic_chi2_p`), and are NEVER substituted into the exact p-value field.

4. **Multiplicity Control (Family-Wise Error Rate):**
   - Holm-Bonferroni step-down correction is applied independently within declared hypothesis families:
     1. **Primary Confirmatory Family:** 4 key contrasts $\times$ 3 scenarios = 12 comparisons.
     2. **True-Seam Control Family:** 4 control contrasts $\times$ 3 scenarios = 12 comparisons.
     3. **Exploratory Family:** 1 sensitivity contrast $\times$ 3 scenarios = 3 comparisons.
