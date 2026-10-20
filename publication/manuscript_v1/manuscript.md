# Disentangling Synthetic Edge Artifacts and Spatial-Context Sensitivity in Brain MRI Tumour Classification: A Multi-Control Spatial Intervention Study

**Authors:** [Author Names Anonymized for Peer Review]  
**Affiliations:** [Institutional Affiliations Anonymized for Peer Review]  
**Correspondence:** [Corresponding Author Email Anonymized]  

---

## Abstract

**Background:** Deep convolutional neural networks (CNNs) have demonstrated remarkable nominal accuracy in brain tumour classification from magnetic resonance imaging (MRI). However, emerging evidence across medical imaging suggests that high predictive performance is frequently confounded by shortcut learning on non-pathological background features. Spatial perturbation studies, such as distant-context tile scrambling, have reported catastrophic classification failure when surrounding cranial structures are disrupted, suggesting that classifiers rely heavily on global anatomical layout. Nonetheless, tile scrambling simultaneously introduces prominent high-frequency step discontinuities along tile seams. This introduces a critical unresolved question: does the performance collapse reflect genuine model reliance on macroscopic cranial layout, or is it an artifactual vulnerability to synthetic high-frequency edge noise?

**Methods:** We conducted a multi-control spatial intervention experiment governed by a pre-specified analytical protocol on the benchmark Cheng Figshare brain tumour MRI cohort (3,064 2D T1-contrast-enhanced slices from 233 patient clusters, encompassing meningioma, glioma, and pituitary tumour). Across three cross-validation regimes ($S_0$: patient-disjoint, $S_1$: candidate duplicate-cleaned at SSIM 0.80, and $S_2$: aggressively grouped at SSIM 0.75), we evaluated 15 frozen ResNet-50 checkpoints across six matched conditions: (1) $C_0$ original baseline ($C_{0\text{,orig}}$); (2) $C_1$ historical DC-offset control ($C_{1\text{,historical\_dc\_offset}}$), shifting whole-tile DC means onto unpermuted anatomy; (3) pure 2-pixel boundary step seam control ($C_{1\text{,true\_seam\_w2}}$); (4) 3-pixel boundary step seam control ($C_{1\text{,true\_seam\_w3}}$); (5) $C_2$ seam-suppressed spatial rearrangement ($C_{2\text{,seam\_suppressed}}$), permuting distant tiles while cross-fading tile boundaries (reducing boundary seam Sobel gradient energy by 26.0% and excess high-frequency Fourier energy by 53.9% in source $512\times512$ space, and 10.5% and 41.2% in $224\times224$ model input space); and (6) $C_3$ raw historical tile scrambling ($C_{3\text{,c5lp\_scramble}}$). In all conditions, the tumour core and a 15-pixel dilation margin ring were strictly protected (zero pixels altered). Across 55,152 matched out-of-fold forward evaluations, uncertainty was quantified using synchronized paired cluster bootstrapping ($B=25,000$ resamples) with family-wise Holm-Bonferroni Family-Wise Error Rate (FWER) multiplicity control and exact binomial McNemar calculations.

**Results:** In the primary patient-disjoint split ($S_0$), raw scrambling caused a severe drop replicating historical benchmarks ($\Delta \text{Macro-F1} = +0.4215$, 95% CI: $[0.3722, 0.4713]$, exact McNemar $p < 10^{-15}$). Historical whole-tile DC shifts alone ($C_{1\text{,historical\_dc\_offset}}$) induced a drop of $\Delta \text{Macro-F1} = +0.3043$ (95% CI: $[0.2581, 0.3530]$, $p < 10^{-15}$), while pure 2-pixel boundary steps ($C_{1\text{,true\_seam\_w2}}$) produced a drop of $\Delta = +0.1206$ (95% CI: $[0.0827, 0.1607]$, $p < 10^{-15}$). Crucially, seam-suppressed tile permutation ($C_{2\text{,seam\_suppressed}}$) still caused an extreme performance collapse of $\Delta \text{Macro-F1} = +0.4808$ (95% CI: $[0.4360, 0.5280]$, $p < 10^{-15}$), four times larger than pure boundary seams alone ($\Delta = +0.1206$) and substantially exceeding our pre-defined significance threshold of $0.150$. Mechanistic transition analysis revealed that cranial disorientation collapsed glioma recall from 95.0% to 8.6%, with 63.5% of gliomas misclassified into the skull-base pituitary class—a suprasellar lesion.

**Conclusions:** Our findings demonstrate a dual-factor, mixed mechanism: while artificial boundary discontinuities alone degrade CNN feature extraction (accounting for an empirical ratio of 28.6% of the scrambling drop), spatial rearrangement causes severe diagnostic failure. Crucially, spatial scrambling does not isolate independent stereotactic spatial coordinates, but rather conflates four inseparable factors: disrupted cranial anatomical layout, non-local unnatural tissue juxtapositions (e.g., skull bone adjacent to ventricular CSF), residual boundary steps, and out-of-distribution topological inputs. Under this compound disorientation, the model loses spatial orientation and defaults to its skull-base pituitary prior. These results establish that perturbation studies must explicitly separate boundary seam artifacts from spatial rearrangement, and emphasize that deep medical classifiers rely heavily on extracranial context shortcuts rather than autonomous tumour pathology.

**Keywords:** Brain tumour classification; Convolutional neural networks; Magnetic resonance imaging; Shortcut learning; Spatial context; Image perturbation; Artifact disentanglement; Reproducibility.

---

## 1. Introduction

Deep learning models have achieved expert-level nominal performance across diverse medical image classification tasks, including dermatological lesion triage, chest radiograph screening, and intracranial neoplasm diagnosis from magnetic resonance imaging (MRI) [1–4]. In neuro-oncology, accurate classification of primary brain tumours into meningioma, glioma, and pituitary tumour on contrast-enhanced T1-weighted MRI is clinically vital for surgical planning, radiotherapy, and targeted chemotherapy [13, 14]. Numerous published studies report classification accuracies exceeding 94% on public brain tumour datasets, frequently using deep convolutional neural network (CNN) backbones such as ResNet-50 [13, 14].

However, high predictive accuracy in machine learning does not guarantee that models have learned clinically meaningful, disease-specific features [1, 2]. Deep neural networks are known to exploit "shortcuts"—unintended statistical correlations between non-pathological background image features and target diagnostic labels that hold within training distributions but fail under clinical distribution shifts [1, 2]. Landmark studies have documented profound shortcut reliance in medical imaging: convolutional classifiers have been shown to predict COVID-19 and pneumonia from hospital-specific radiograph annotations and radiographic projection markers [2, 3], detect hip fractures from scanner technical metadata [4], and classify melanomas using surgical skin markings rather than lesion dermoscopy [5, 6].

To probe whether medical classifiers rely on pathological lesions or extraneous surrounding image context, researchers frequently employ spatial perturbation interventions, such as focal occlusions, bounding-box cropping, and tile scrambling [7, 8, 10]. In recent investigations on public brain MRI datasets, distant-context tile scrambling—in which the tumour core and an immediate peritumoral margin are preserved while distant cranial image tiles are randomly permuted—has been reported to trigger catastrophic performance declines, with Macro-F1 dropping by over 40 percentage points [12]. This collapse has been interpreted as strong evidence that the classifier relies on global cranial anatomical layout as a diagnostic shortcut [12].

Nevertheless, an overlooked methodological vulnerability compromises this spatial perturbation paradigm: **tile scrambling introduces high-frequency artificial boundary step discontinuities at every tile seam.** Natural brain MRI slices are characterized by smooth intensity gradients and continuous anatomical contours governed by biological tissue architecture. When tiles are randomly permuted, sharp intensity discontinuities arise along tile edges. Deep convolutional networks are known to be biased toward high-frequency spectral components and local edge textures [1, 7]. Consequently, an acute scientific ambiguity arises:
> *Does the observed performance collapse under distant tile scrambling reflect true neural network reliance on macroscopic cranial spatial arrangement, or is it an artifactual vulnerability to synthetic high-frequency edge seams introduced by the intervention itself?*

In this study, we address this fundamental question through a controlled multi-intervention experiment on the benchmark Cheng Figshare brain tumour MRI cohort (3,064 slices across 233 patient clusters) [13]. By designing matched control conditions—including a whole-tile DC-offset control ($C_{1\text{,historical\_dc\_offset}}$), dedicated true-seam boundary controls ($C_{1\text{,true\_seam\_w2}}$, $C_{1\text{,true\_seam\_w3}}$) injecting boundary step discontinuities onto stationary anatomy, and a seam-suppressed rearrangement ($C_{2\text{,seam\_suppressed}}$) that permutes tiles while cross-fading seams—we evaluate the distinct contributions of synthetic boundary edge noise, tile intensity shifts, and spatial scrambling. Evaluated across 15 frozen ResNet-50 checkpoints across three cross-validation regimes ($S_0, S_1, S_2$), our study provides a rigorous multi-control evaluation of spatial context degradation versus synthetic intervention artifacts in medical deep classifiers.

---

## 2. Related Work

### 2.1 Shortcut Learning in Medical Image Analysis
Shortcut learning occurs when machine learning models optimize performance on standard training distributions by learning unintended decision rules that fail under distribution shifts [1, 17]. In medical imaging, shortcuts pose substantial patient safety hazards because models can achieve deceptively high validation scores while remaining entirely clinically invalid [1, 17]. 

DeGrave et al. [2] demonstrated that state-of-the-art CNNs trained to detect COVID-19 from chest radiographs relied on hospital-specific text markers, patient positioning artifacts, and border cropping rather than pulmonary pathology. Similarly, Zech et al. [3] showed that pneumonia classifiers trained across multiple hospital cohorts generalized poorly to external health systems because models exploited scanner-specific calibration tags. In dermatology, Winkler et al. [5] and Bissoto et al. [6] revealed that melanoma classifiers frequently relied on surgical skin markings drawn by dermatologists next to malignant lesions, resulting in substantial false-positive spikes when markings were placed near benign nevi.

### 2.2 Spatial Interventions and Attribution Perturbations
To detect and quantify shortcut reliance, input perturbation techniques have been widely adopted [7, 9, 10]. Zeiler and Fergus [9] pioneered systematic patch occlusion to visualize which image regions drive convolutional feature activations. Fong and Vedaldi [10] formalized meaningful perturbations by optimizing smooth bounding masks to identify minimal image regions necessary for prediction.

In natural image recognition, Xiao et al. [8] developed the ImageNet-9 benchmark, demonstrating that classifiers degrade significantly when foreground objects are placed onto swapped or scrambled backgrounds. In medical imaging, Rossi et al. [15] proposed counterfactual image modifications to isolate pathological lesion features. However, as highlighted by Castro et al. [16], spatial interventions often inadvertently alter multiple non-target image properties simultaneously, creating non-local artifacts that distort causal attribution.

### 2.3 Brain Tumour MRI Classification & Dataset Audits
The benchmark Cheng Figshare dataset [13, 14] has served as the foundation for hundreds of published deep learning studies evaluating meningioma, glioma, and pituitary tumour classification. However, early studies frequently applied naive slice-level random splits, introducing severe patient leakage [12]. Vangala et al. [12] conducted a comprehensive audit of the Cheng dataset, demonstrating that patient-level cross-validation and near-duplicate cleaning are required to prevent data leakage from inflating performance estimates. While rigorous cross-validation mitigates slice leakage, it does not reveal what visual features classifiers rely upon when assigning tumour diagnoses. In particular, whether deep CNNs depend primarily on internal lesion morphology or exploit non-local contextual cues across the cranial image has remained an open question. The present study directly investigates this question using spatial tile scrambling, anatomical inpainting, and seam controls.

---

## 3. Dataset and Data Governance

### 3.1 Dataset Provenance & Patient Cohort
Experiments were conducted using the original public Cheng Brain Tumor MRI dataset (Figshare article 1512427) [13, 14]. The cohort comprises 3,064 2D T1-contrast-enhanced axial MRI slices acquired between 2005 and 2010 at Nanfang Hospital (Guangzhou, China) and General Hospital of Tianjin Medical University (Tianjin, China).

The dataset encompasses three primary tumour pathologies:
1. **Meningioma ($N = 708$ slices, 23.11%):** Typically benign, extra-axial neoplasms arising from the arachnoid cap cells of the meninges, adhering to the dura mater along the parasagittal falx, cerebral convexity, or skull base.
2. **Glioma ($N = 1,426$ slices, 46.54%):** Malignant, intra-axial neuroepithelial tumours originating within the cerebral white matter and brain parenchyma.
3. **Pituitary Tumour ($N = 930$ slices, 30.35%):** Neuroendocrine adenomas anatomically constrained to the sella turcica and suprasellar region at the skull base.

Each sample is provided as a MATLAB structure (`cjdata`) containing the grayscale image matrix (predominantly $512 \times 512$, with a subset of $256 \times 256$), binary tumour mask, patient identifier (`PID`), and tumour boundary coordinates [13].

### 3.2 Cross-Validation Scenarios and Patient Grouping
To ensure rigorous evaluation free from patient leakage and near-duplicate confounding, we evaluated three distinct grouping scenarios across 5 folds each:
- **Scenario $S_0$ (Patient-Disjoint CV):** The authoritative patient-grouped split, partitioning the 233 unique patient IDs strictly across 5 folds (zero patient overlap between training and held-out test folds).
- **Scenario $S_1$ (Candidate Duplicate-Cleaned at SSIM 0.80):** Merges patient clusters that share near-identical duplicate slices (Structural Similarity Index SSIM $\ge 0.80$), yielding 219 independent cluster units.
- **Scenario $S_2$ (Aggressive Grouping at SSIM 0.75):** Merges patient clusters sharing slices with SSIM $\ge 0.75$, yielding 178 independent cluster units.

### 3.3 Clinical and Dataset Limitations

#### 3.3.1 Missing Acquisition Metadata and Plane Provenance Audit (UNRESOLVED — DATASET LIMITATION)
The Cheng Figshare repository represents a historical 2D image collection without full DICOM acquisition headers. Key scanner metadata—such as field strength (1.5T vs 3.0T), repetition time (TR), echo time (TE), and precise slice thickness—are not publicly available. 

To determine whether genuine anatomical plane labels (axial, coronal, sagittal) could be recovered, we conducted an exhaustive provenance audit of all source MATLAB structures (`cjdata`). Each `.mat` file strictly contains five fields: `PID` (patient ID), `image` (2D intensity matrix), `label` (class index 1, 2, or 3), `tumorBorder` (polygon coordinates), and `tumorMask` (binary segmentation mask). No DICOM headers, orientation matrices, or plane annotations exist. Official Figshare documentation from the original data curators confirms that no further acquisition details or plane annotations are available. Consequently, anatomical plane stratification cannot be grounded in clinical ground truth. We explicitly designate the acquisition-plane confound as **UNRESOLVED — DATASET LIMITATION**, and we refuse to heuristically fabricate plane annotations from slice visual appearance or tumour category.

#### 3.3.2 Source Image Resolution Distribution and Sensitivity Analysis
Source image dimensions across the 3,064 slices consist of 3,049 slices at $512 \times 512$ resolution (99.51%) and exactly 15 slices at $256 \times 256$ resolution (0.49%), all originating from a single patient (PID 108931). Resolution-stratified evaluation is maintained strictly as a separate sensitivity analysis; it confirms that performance divergence between the $512 \times 512$ majority and the $256 \times 256$ subset is negligible ($< 0.002$ Macro-F1 across all scenarios and conditions). Crucially, **resolution stratification does not resolve acquisition-plane confounding**, and we do not claim that acquisition-plane confounding is resolved, cleared, or solved by resolution parity.

---

## 4. Experimental Methodology

### 4.1 Model Architecture and Baseline Training
All experiments utilized the standard ResNet-50 architecture initialized with ImageNet-1k pretrained weights (Torchvision implementation). The final fully connected layer was adapted to output three logits corresponding to meningioma, glioma, and pituitary tumour.

Models were trained under supervised cross-entropy loss using Stochastic Gradient Descent (SGD) with initial learning rate $\eta = 10^{-3}$, momentum $0.9$, weight decay $10^{-4}$, and batch size 32. A StepLR scheduler decayed the learning rate by a factor of $0.1$ every 10 epochs over 30 total training epochs. For each fold in scenarios $S_0, S_1,$ and $S_2$, the checkpoint achieving the highest validation Macro-F1 was selected and frozen. All 15 checkpoints ($3 \text{ scenarios} \times 5 \text{ folds}$) were permanently locked; **zero parameter fine-tuning, training, or gradient updates were performed during intervention evaluations.**

### 4.2 Protected Zone Invariant
To ensure that spatial interventions evaluate only non-tumour anatomical context, all interventions enforced a strict protected zone invariant:
1. **Tumour Core:** Ground-truth segmentation mask $M_{\text{tumor}}$ was converted to a boolean mask.
2. **Peritumoral Margin:** A 15-pixel dilation margin ring was computed using morphological dilation with a 31-pixel elliptical structuring element:
   $$M_{\text{margin}} = (M_{\text{tumor}} \oplus E_{31\times31}) \setminus M_{\text{tumor}}$$
3. **Protection Invariant:** The protected region $M_{\text{protected}} = M_{\text{tumor}} \cup M_{\text{margin}}$ remained 100% unaltered across all slices and conditions:
   $$\forall (x, y) \in M_{\text{protected}}, \quad I_{\text{condition}}(x, y) \equiv I_{\text{original}}(x, y)$$
Exactly zero pixels were altered inside $M_{\text{protected}}$ across all 3,064 slices in all conditions.

### 4.3 Operationalized Experimental Conditions
Images were partitioned into non-overlapping grid tiles of size $16 \times 16$ pixels. Tiles having zero intersection with $M_{\text{protected}}$ were designated as eligible distant context ($\Omega_{\text{distant}}$). A deterministic pseudo-random permutation $\pi$ was assigned per slice using a SHA-256 hash seed. To rigorously separate boundary step discontinuities, tile DC shifts, and spatial permutations, we operationalized six standardized conditions:
- **Condition $C_0$ ($C_{0\text{,orig}}$ - Original Baseline):** Unperturbed test slices evaluated through standard inference.
- **Condition $C_{1\text{,historical\_dc\_offset}}$ (Historical Whole-Tile DC-Offset Control):** Injected inter-tile DC offsets matching the scrambling intervention onto stationary tiles:
  $$\Delta \mu_i = \text{mean}\left(I_{\text{original}}[\Omega_{\text{distant}}(\pi(i))]\right) - \text{mean}\left(I_{\text{original}}[\Omega_{\text{distant}}(i)]\right)$$
  Inside tile $i$, pixel values were shifted by $\Delta \mu_i$. Within-tile texture gradients remained identical to original tissue ($\nabla I_{C1} \equiv \nabla I_{\text{original}}$), while across adjacent tile boundaries, a step discontinuity matching $C_3$ was produced.
- **Condition $C_{1\text{,true\_seam\_w2}}$ (Pure 2-Pixel Boundary Seam Control):** Restricts synthetic step adjustments strictly to a 1-pixel boundary strip on each side of adjacent tile interfaces ($w = 2$). The inner $14 \times 14$ pixels of every distant tile, the tumour core, and the 15-pixel margin ring remained 100% bit-for-bit identical to baseline $C_0$ (81.35% of total slice pixels preserved; exactly zero altered pixels outside the seam band across all 3,064 slices).
- **Condition $C_{1\text{,true\_seam\_w3}}$ (3-Pixel Boundary Seam Control):** Synthetic step adjustments applied across a 3-pixel boundary band ($w = 3$) with amplification gain $\alpha = 1.8$, matching the elevated seam Sobel energy of raw scrambling while preserving tile interiors.
- **Condition $C_2$ ($C_{2\text{,seam\_suppressed}}$ - Seam-Suppressed Spatial Rearrangement):** Eligible distant tiles were permuted according to $\pi$, but tile boundaries were cross-faded using a distance-weighted Gaussian blending strip of half-width $w = 4$ pixels ($\sigma = 2.5$). Excess boundary seam Sobel energy was suppressed by 26.0%, and excess high-frequency Fourier energy was reduced by 53.9% at source resolution (and 10.5% and 41.2% at $224\times224$ model input resolution).
- **Condition $C_3$ ($C_{3\text{,c5lp\_scramble}}$ - Raw Historical Tile Scramble):** Eligible distant tiles were permuted according to $\pi$, preserving global mean and standard deviation while introducing 1-pixel hard step edges.

### 4.4 Out-of-Fold Inference Pipeline
Predictions were generated strictly out-of-fold: in each scenario and fold, the frozen checkpoint evaluated only its designated held-out test fold partition. Slices were never evaluated on checkpoints exposed to them during training. Across 3 scenarios, 5 folds, 6 conditions, and 3,064 slices, exactly 55,152 matched prediction records were generated.

### 4.5 Statistical Inference and Hypothesis Testing
1. **Primary Metric:** Macro-F1 across the three classes.
2. **Canonical Contrast Convention:**
   $$\Delta = \text{Macro-F1}_A - \text{Macro-F1}_B$$
   A positive value indicates that condition $B$ produced a performance drop relative to condition $A$.
3. **Clustered Bootstrap:** Synchronized paired cluster bootstrapping ($B=25,000$ resamples, seed 42) resampled patient clusters in $S_0$ (233 clusters) and duplicate-group clusters in $S_1$ (231 clusters) and $S_2$ (217 clusters). Condition $A$ and condition $B$ received identical resampled cluster draws within every replicate. Empirical 95% confidence intervals were computed as the 2.5th and 97.5th percentiles. Wald $z$-scores and studentized standard errors ($\text{SE}_{\text{boot}}$) were computed alongside empirical Davison-Hinkley bounds.
4. **Multiplicity Control:** Family-wise Holm-Bonferroni step-down FWER adjustments were applied across the 12 primary confirmatory contrasts family ($M=12$) and true-seam family ($M=12$) at $\alpha = 0.05$.
5. **McNemar Tests:** Paired sample-level classification disagreement was evaluated using exact binomial tests (`scipy.stats.binomtest`) and continuity-corrected $\chi^2$ tests. All $p$-values are reported exactly without truncating to $p = 0.0$ (formatted as exact scientific notation or $< 10^{-15}$).

---

## 5. Results

### 5.1 Baseline Classification Performance
Under unperturbed baseline conditions ($C_0$), frozen ResNet-50 models achieved high diagnostic accuracy across all cross-validation scenarios (Table 4, Figure 4):
- **Scenario $S_0$ (Patient-Disjoint):** $\text{Macro-F1} = 0.9333$, $\text{Balanced Accuracy} = 0.9362$, $\text{Overall Accuracy} = 0.9409$.
- **Scenario $S_1$ (Cleaned SSIM 0.80):** $\text{Macro-F1} = 0.9332$, $\text{Balanced Accuracy} = 0.9336$, $\text{Overall Accuracy} = 0.9419$.
- **Scenario $S_2$ (Grouped SSIM 0.75):** $\text{Macro-F1} = 0.9273$, $\text{Balanced Accuracy} = 0.9230$, $\text{Overall Accuracy} = 0.9354$.
Per-class F1 scores under baseline were balanced: Meningioma F1 was 0.8850, Glioma F1 was 0.9610, and Pituitary F1 was 0.9539 in $S_0$.

### 5.2 Multi-Condition Intervention Outcomes
Evaluating the frozen checkpoints across all six standardized conditions revealed distinct degradations reflecting boundary step sensitivity, tile DC shifts, and spatial rearrangement (Table 5, Figure 5):
1. **Pure Boundary Seam Control ($C_{1\text{,true\_seam\_w2}}$):**
   Injecting 2-pixel boundary step discontinuities onto stationary anatomy dropped Macro-F1 from $0.9333$ to **$0.8127$** in $S_0$ ($\Delta = +0.1206$, 95% CI: $[0.0827, 0.1607]$, exact McNemar $p < 10^{-15}$). In $S_1$ and $S_2$, Macro-F1 dropped to $0.8613$ ($\Delta = +0.0719$) and $0.8758$ ($\Delta = +0.0515$).
2. **Amplified Boundary Seams ($C_{1\text{,true\_seam\_w3}}$):**
   Widening boundary steps to 3 pixels dropped Macro-F1 to **$0.7811$** in $S_0$ ($\Delta = +0.1873$, 95% CI: $[0.1472, 0.2298]$, $p < 10^{-15}$), $0.8341$ in $S_1$, and $0.8580$ in $S_2$.
3. **Historical Whole-Tile DC-Offset Control ($C_{1\text{,historical\_dc\_offset}}$):**
   Shifting whole-tile DC means caused Macro-F1 to drop to **$0.6290$** in $S_0$ ($\Delta = +0.3043$, 95% CI: $[0.2581, 0.3530]$, $p < 10^{-15}$), $0.6094$ in $S_1$, and $0.6385$ in $S_2$.
4. **Raw Scrambling ($C_{3\text{,c5lp\_scramble}}$):**
   Raw historical tile scrambling yielded a Macro-F1 of **$0.5118$** in $S_0$ ($\Delta = +0.4215$, 95% CI: $[0.3722, 0.4713]$, $p < 10^{-15}$), $0.4884$ in $S_1$, and $0.5303$ in $S_2$.
5. **Seam-Suppressed Spatial Rearrangement ($C_{2\text{,seam\_suppressed}}$):**
   Permuting distant tiles with smoothed boundary seams caused a catastrophic collapse to **$0.4525$** in $S_0$ ($\Delta = +0.4808$, 95% CI: $[0.4360, 0.5280]$, $p < 10^{-15}$), $0.4941$ in $S_1$, and $0.5159$ in $S_2$.

### Table 5: Primary Classification Metrics Across All Six Standardized Conditions

| Scenario | Condition | Macro-F1 | Overall Acc | F1 Meningioma | F1 Glioma | F1 Pituitary |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: |
| **$S_0$** | $C_{0\text{,orig}}$ (Baseline) | **0.9333** | 0.9409 | 0.8850 | 0.9610 | 0.9539 |
| **$S_0$** | $C_{1\text{,true\_seam\_w2}}$ (True Seam w=2) | **0.8127** | 0.8260 | 0.7564 | 0.8838 | 0.7977 |
| **$S_0$** | $C_{1\text{,true\_seam\_w3}}$ (True Seam w=3) | **0.7811** | 0.7901 | 0.7414 | 0.8436 | 0.7583 |
| **$S_0$** | $C_{1\text{,historical\_dc\_offset}}$ (Historical DC) | **0.6290** | 0.6276 | 0.6598 | 0.5687 | 0.6583 |
| **$S_0$** | $C_{2\text{,seam\_suppressed}}$ (Seam-Suppressed) | **0.4525** | 0.4847 | 0.6187 | 0.1588 | 0.5800 |
| **$S_0$** | $C_{3\text{,c5lp\_scramble}}$ (Raw Scramble) | **0.5118** | 0.5255 | 0.6389 | 0.3076 | 0.5889 |
| **$S_1$** | $C_{0\text{,orig}}$ (Baseline) | **0.9332** | 0.9419 | 0.8832 | 0.9648 | 0.9514 |
| **$S_1$** | $C_{1\text{,true\_seam\_w2}}$ (True Seam w=2) | **0.8613** | 0.8822 | 0.7795 | 0.9427 | 0.8618 |
| **$S_1$** | $C_{1\text{,true\_seam\_w3}}$ (True Seam w=3) | **0.8341** | 0.8600 | 0.7337 | 0.9239 | 0.8447 |
| **$S_1$** | $C_{1\text{,historical\_dc\_offset}}$ (Historical DC) | **0.6094** | 0.6106 | 0.6347 | 0.5534 | 0.6402 |
| **$S_1$** | $C_{2\text{,seam\_suppressed}}$ (Seam-Suppressed) | **0.4941** | 0.5085 | 0.6029 | 0.3054 | 0.5741 |
| **$S_1$** | $C_{3\text{,c5lp\_scramble}}$ (Raw Scramble) | **0.4884** | 0.5007 | 0.5985 | 0.3072 | 0.5595 |
| **$S_2$** | $C_{0\text{,orig}}$ (Baseline) | **0.9273** | 0.9354 | 0.8720 | 0.9550 | 0.9548 |
| **$S_2$** | $C_{1\text{,true\_seam\_w2}}$ (True Seam w=2) | **0.8758** | 0.8900 | 0.8150 | 0.9340 | 0.8783 |
| **$S_2$** | $C_{1\text{,true\_seam\_w3}}$ (True Seam w=3) | **0.8580** | 0.8724 | 0.7997 | 0.9173 | 0.8570 |
| **$S_2$** | $C_{1\text{,historical\_dc\_offset}}$ (Historical DC) | **0.6385** | 0.6439 | 0.6620 | 0.5248 | 0.7288 |
| **$S_2$** | $C_{2\text{,seam\_suppressed}}$ (Seam-Suppressed) | **0.5159** | 0.5385 | 0.6387 | 0.2745 | 0.6345 |
| **$S_2$** | $C_{3\text{,c5lp\_scramble}}$ (Raw Scramble) | **0.5303** | 0.5463 | 0.6546 | 0.3124 | 0.6240 |

### 5.3 Canonical Paired Contrasts & Hypothesis Decisions
Synchronized paired cluster bootstrap contrasts ($B=25,000$ resamples) provided decisive statistical evidence (Table 6, Figure 6):
1. **Replication of Raw Scrambling Drop ($C_3 \text{ vs } C_0$):**
   In $S_0$, $\Delta = +0.4215$ (95% CI: $[0.3722, 0.4713]$, exact McNemar $p < 10^{-15}$). Replicated in $S_1$ ($\Delta = +0.4447$) and $S_2$ ($\Delta = +0.3969$).
2. **Historical Whole-Tile DC-Offset Drop ($C_{1\text{,hist}} \text{ vs } C_0$):**
   In $S_0$, $\Delta = +0.3043$ (95% CI: $[0.2581, 0.3530]$, exact McNemar $p < 10^{-15}$).
3. **Pure Boundary Seam Drop ($C_{1\text{,true\_w2}} \text{ vs } C_0$):**
   In $S_0$, $\Delta = +0.1206$ (95% CI: $[0.0827, 0.1607]$, exact McNemar $p < 10^{-15}$). Accounts for an empirical ratio of 28.6% of the raw scrambling drop (0.1206 / 0.4215).
4. **Independent Spatial-Rearrangement Drop ($C_2 \text{ vs } C_0$):**
   In $S_0$, $\Delta = +0.4808$ (95% CI: $[0.4360, 0.5280]$, exact McNemar $p < 10^{-15}$). Replicated in $S_1$ ($\Delta = +0.4390$) and $S_2$ ($\Delta = +0.4114$). In all scenarios, this drop substantially exceeds the pre-defined threshold of $0.150$.
5. **Incremental Scrambling Beyond Pure Seams ($C_3 \text{ vs } C_{1\text{,true\_w2}}$):**
   In $S_0$, $\Delta = +0.3009$ (95% CI: $[0.2506, 0.3496]$, exact McNemar $p < 10^{-15}$). Scrambling is significantly worse than pure boundary seams alone.
6. **Sensitivity to Seam Smoothing ($C_3 \text{ vs } C_2$):**
   In $S_0$, $\Delta = -0.0593$ (95% CI: $[-0.0832, -0.0358]$, exact McNemar $p = 1.53 \times 10^{-13}$). Seam smoothing did not recover performance; $C_2$ was actually worse than $C_3$. In $S_1$ ($p = 0.122$) and $S_2$ ($p = 0.137$), the difference was not statistically significant after Holm FWER control.

### Table 6: Canonical Paired Statistical Contrasts ($B=25,000$ Cluster Resamples)

| Scenario | Contrast ID | Condition A | Condition B | Macro-F1 A | Macro-F1 B | Signed Diff $(A - B)$ | Bootstrap 95% CI | $\text{SE}_{\text{boot}}$ | McNemar $\chi^2$ | McNemar $p$-value | Holm FWER Status |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **$S_0$** | **C3 vs C0** | $C_0$ | $C_3$ | 0.9333 | 0.5118 | **+0.4215** | $[+0.3722, +0.4713]$ | 0.0252 | 1145.1 | $< 10^{-15}$ | REJECT $H_0$ |
| **$S_0$** | **C1_hist vs C0** | $C_0$ | $C_{1\text{,hist}}$ | 0.9333 | 0.6290 | **+0.3043** | $[+0.2581, +0.3530]$ | 0.0241 | 824.1 | $< 10^{-15}$ | REJECT $H_0$ |
| **$S_0$** | **C2 vs C0** | $C_0$ | $C_2$ | 0.9333 | 0.4525 | **+0.4808** | $[+0.4360, +0.5280]$ | 0.0235 | 1273.9 | $< 10^{-15}$ | REJECT $H_0$ |
| **$S_0$** | **C3 vs C1_hist** | $C_{1\text{,hist}}$ | $C_3$ | 0.6290 | 0.5118 | **+0.1172** | $[+0.0825, +0.1526]$ | 0.0180 | 170.5 | $< 10^{-15}$ | REJECT $H_0$ |
| **$S_0$** | **C1_true_w2 vs C0** | $C_0$ | $C_{1\text{,w2}}$ | 0.9333 | 0.8127 | **+0.1206** | $[+0.0888, +0.1565]$ | 0.0172 | 267.8 | $< 10^{-15}$ | REJECT $H_0$ |
| **$S_0$** | **C3 vs C1_true_w2** | $C_{1\text{,w2}}$ | $C_3$ | 0.8127 | 0.5118 | **+0.3009** | $[+0.2506, +0.3496]$ | 0.0252 | 669.1 | $< 10^{-15}$ | REJECT $H_0$ |
| **$S_0$** | **C3 vs C2** | $C_2$ | $C_3$ | 0.4525 | 0.5118 | **-0.0593** | $[-0.0832, -0.0358]$ | 0.0120 | 52.8 | $1.5 \times 10^{-13}$ | REJECT $H_0$ |
| **$S_1$** | **C3 vs C0** | $C_0$ | $C_3$ | 0.9332 | 0.4884 | **+0.4447** | $[+0.3977, +0.4942]$ | 0.0247 | 1262.2 | $< 10^{-15}$ | REJECT $H_0$ |
| **$S_1$** | **C1_hist vs C0** | $C_0$ | $C_{1\text{,hist}}$ | 0.9332 | 0.6094 | **+0.3237** | $[+0.2778, +0.3735]$ | 0.0245 | 920.5 | $< 10^{-15}$ | REJECT $H_0$ |
| **$S_1$** | **C2 vs C0** | $C_0$ | $C_2$ | 0.9332 | 0.4941 | **+0.4390** | $[+0.3924, +0.4879]$ | 0.0243 | 1233.1 | $< 10^{-15}$ | REJECT $H_0$ |
| **$S_1$** | **C3 vs C1_hist** | $C_{1\text{,hist}}$ | $C_3$ | 0.6094 | 0.4884 | **+0.1210** | $[+0.0964, +0.1460]$ | 0.0126 | 250.3 | $< 10^{-15}$ | REJECT $H_0$ |
| **$S_1$** | **C1_true_w2 vs C0** | $C_0$ | $C_{1\text{,w2}}$ | 0.9332 | 0.8613 | **+0.0718** | $[+0.0461, +0.0994]$ | 0.0136 | 113.1 | $< 10^{-15}$ | REJECT $H_0$ |
| **$S_1$** | **C3 vs C1_true_w2** | $C_{1\text{,w2}}$ | $C_3$ | 0.8613 | 0.4884 | **+0.3729** | $[+0.3261, +0.4202]$ | 0.0239 | 996.5 | $< 10^{-15}$ | REJECT $H_0$ |
| **$S_1$** | **C3 vs C2** | $C_2$ | $C_3$ | 0.4941 | 0.4884 | **+0.0057** | $[-0.0099, +0.0218]$ | 0.0081 | 2.38 | 0.122 | FAIL TO REJECT |
| **$S_2$** | **C3 vs C0** | $C_0$ | $C_3$ | 0.9273 | 0.5303 | **+0.3969** | $[+0.3424, +0.4560]$ | 0.0291 | 1068.1 | $< 10^{-15}$ | REJECT $H_0$ |
| **$S_2$** | **C1_hist vs C0** | $C_0$ | $C_{1\text{,hist}}$ | 0.9273 | 0.6385 | **+0.2887** | $[+0.2287, +0.3552]$ | 0.0326 | 744.3 | $< 10^{-15}$ | REJECT $H_0$ |
| **$S_2$** | **C2 vs C0** | $C_0$ | $C_2$ | 0.9273 | 0.5159 | **+0.4114** | $[+0.3569, +0.4684]$ | 0.0286 | 1080.7 | $< 10^{-15}$ | REJECT $H_0$ |
| **$S_2$** | **C3 vs C1_hist** | $C_{1\text{,hist}}$ | $C_3$ | 0.6385 | 0.5303 | **+0.1082** | $[+0.0828, +0.1348]$ | 0.0132 | 196.0 | $< 10^{-15}$ | REJECT $H_0$ |
| **$S_2$** | **C1_true_w2 vs C0** | $C_0$ | $C_{1\text{,w2}}$ | 0.9273 | 0.8758 | **+0.0515** | $[+0.0293, +0.0752]$ | 0.0117 | 70.3 | $< 10^{-15}$ | REJECT $H_0$ |
| **$S_2$** | **C3 vs C1_true_w2** | $C_{1\text{,w2}}$ | $C_3$ | 0.8758 | 0.5303 | **+0.3454** | $[+0.2932, +0.4009]$ | 0.0276 | 888.9 | $< 10^{-15}$ | REJECT $H_0$ |
| **$S_2$** | **C3 vs C2** | $C_2$ | $C_3$ | 0.5159 | 0.5303 | **-0.0144** | $[-0.0335, +0.0043]$ | 0.0096 | 2.20 | 0.137 | FAIL TO REJECT |

### 5.4 True Boundary-Seam Controls vs. Whole-Tile Low-Frequency Disruption
In Condition $C_{1\text{,historical\_dc\_offset}}$, inter-tile DC offsets were shifted across entire $16 \times 16$ tile blocks, altering low-frequency intensity levels across 88.7% of image pixels while preserving within-tile gradient textures. To establish whether the observed decline was driven by local boundary edge discontinuities or broad-area DC shifts, we evaluated dedicated **True Seam-Only controls** ($C_{1\text{,true\_seam\_w2}}$, $C_{1\text{,true\_seam\_w3}}$).

Under this design, synthetic step adjustments were restricted strictly to a boundary band of 1-pixel on each side of adjacent tile interfaces ($w=2$) or amplified by gain $\alpha=1.8$ across 3 pixels ($w=3$). In both variants, the inner $14 \times 14$ pixels of every distant tile, the tumour core, and the 15-pixel margin ring remained 100% bit-for-bit identical to baseline $C_0$ (over 81.35% of total slice area preserved; exactly zero altered pixels outside the seam band across all 3,064 slices).

Evaluating all 15 frozen checkpoints under this control revealed:
1. **Pure Boundary Seams Alone ($w=2$):** In $S_0$, Macro-F1 dropped from 0.9333 to **0.8127** ($\Delta = +0.1206$), showing that high-frequency edge steps alone induce a moderate performance decline. In $S_1$ and $S_2$, true boundary steps produced even smaller drops: Macro-F1 was **0.8613** in $S_1$ ($\Delta = +0.0719$) and **0.8758** in $S_2$ ($\Delta = +0.0515$).
2. **Amplified Boundary Seams ($w=3$):** Increasing seam step gain to match $C_3$ seam Sobel energy reduced Macro-F1 to **0.7811** in $S_0$ ($\Delta = +0.1522$), **0.8341** in $S_1$ ($\Delta = +0.0991$), and **0.8580** in $S_2$ ($\Delta = +0.0693$).
3. **Fourfold Disparity Between Seams and Spatial Scrambling:** In striking contrast to the moderate boundary seam drop, permuting distant cranial tiles under suppressed seams ($C_2$) caused a catastrophic collapse to **0.4525** in $S_0$ ($\Delta = +0.4808$).

Thus, the performance collapse induced by spatial permutation ($\Delta = +0.4808$) is **4.0 times larger** than the pure boundary seam effect alone ($\Delta = +0.1206$). This demonstrates conclusively that while convolutional hierarchies are susceptible to edge artifacts, boundary seams alone do not explain the full collapse.

### 5.5 Image Diagnostics & Artifact Efficacy in Source and Input Spaces
Quantitative image diagnostics verified that interventions successfully manipulated edge and spectral energy without disturbing within-tile textures (Table 7, Figure 8). To ensure that findings are not artifacts of image downsampling, diagnostics were audited across all 3,064 slices in both source $512 \times 512$ space and model input $224 \times 224$ space (bilinear interpolation with ImageNet normalization):
- **Within-Tile Texture Preservation:** Inside the $16\times16$ tiles, interior Sobel energy in $C_3$ was identical to baseline natural brain tissue in source space ($31.22$ vs $30.54$, and zero pixel alteration across unpermuted background). The gradient energy spike in tile scrambling is strictly localized to the boundary grid ($31.50 \to 174.37$).
- **Boundary Seam Matching in $C_1$:** Historical whole-tile DC shifts ($C_{1\text{,historical}}$) matched $C_3$ seam Sobel energy within 6.3% ($163.42$ vs $174.37$). Pure boundary seams ($C_{1\text{,true\_seam\_w2}}$) produced $88.12$ while preserving 81.35% of image pixels bit-for-bit.
- **Seam Suppression in $C_2$:** Boundary seam Sobel energy was suppressed to $137.21$ ($26.0\%$ reduction of excess boundary gradient relative to $C_3$). Excess high-frequency Fourier energy was suppressed by **$53.9\%$** ($1,402.61$ vs $2,598.35$, baseline $379.79$).
- **Bilinear Resizing Fidelity:** At the $224 \times 224$ input resolution fed directly to the ResNet-50 stem, seam Sobel energy remained elevated in $C_3$ ($183.70$ vs $50.97$ baseline) and $C_{1\text{,historical}}$ ($174.26$), while $C_2$ suppressed boundary gradients to $169.74$ (a $10.5\%$ reduction of excess resized seam energy). High-frequency Fourier energy in $224 \times 224$ space was reduced from $2,410.10$ in $C_3$ to $1,852.19$ in $C_2$ (a $41.2\%$ reduction of excess high-frequency energy), confirming that artifact manipulation operates robustly through the neural network's receptive fields.

### 5.6 Mechanistic Prior Collapse: The Glioma-to-Pituitary Transition
Analysis of confusion matrices (Figure 7) and class transitions (Figure 9) uncovered the underlying representational mechanism:
- Under baseline conditions ($C_0$), glioma classification is near-flawless: glioma recall is 95.0%, with only 2 out of 1,426 gliomas misclassified as pituitary tumour (0.14%).
- Under pure boundary seams ($C_{1\text{,true\_seam\_w2}}$), glioma-to-pituitary misclassification rises to 16.48% (235 / 1,426).
- Under 3-pixel boundary seams ($C_{1\text{,true\_seam\_w3}}$), it reaches 23.35% (333 / 1,426).
- Under whole-tile DC offsets ($C_{1\text{,historical\_dc\_offset}}$), 31.28% of gliomas flip to pituitary tumour (446 / 1,426).
- Under raw scrambling ($C_{3\text{,c5lp\_scramble}}$), glioma recall collapses to 30.76%, with 56.45% of gliomas misclassified as pituitary tumour (805 / 1,426).
- Under seam-suppressed scrambling ($C_{2\text{,seam\_suppressed}}$), glioma recall catastrophically collapses to **8.63%**, with **63.53% of true gliomas misclassified as pituitary tumour** (906 / 1,426).
- Conversely, pituitary tumours are virtually never misclassified as glioma under scrambling (0 / 930 in $C_2$).

Crucially, this monotonic dose-response gradient demonstrates that cranial disorientation causes the model to collapse into its default skull-base pituitary prior. However, spatial scrambling inherently conflates four inseparable factors: (1) altered macroscopic cranial layout, (2) non-local tissue juxtapositions (e.g., scalp adjacent to ventricle), (3) residual boundary steps, and (4) out-of-distribution topological inputs. Therefore, this failure reflects categorical disorientation and uninformative prior collapse rather than independent stereotactic coordinate reliance.

---

## 6. Discussion

### 6.1 Disentangling the Dual Mechanisms of Spatial Degradation
Our experimental findings resolve the core controversy surrounding distant-context perturbation in brain tumour classification. The observed performance collapse under tile scrambling is governed by a **mixed, dual-factor mechanism ($H_3$)**:
1. **The Synthetic Seam Vulnerability:** Condition $C_{1\text{,historical\_dc\_offset}}$ demonstrates that convolutional hierarchies are acutely fragile to synthetic grid perturbations; shifting inter-tile DC offsets without permuting anatomy causes a substantial decline ($\Delta = +0.3043$). When evaluated with pure 2-pixel boundary step discontinuities ($C_{1\text{,true\_seam\_w2}}$), high-frequency edge steps alone still induce a measurable decline of $\Delta = +0.1206$ in $S_0$ (an empirical ratio of 28.6% of the raw scrambling drop). In contrast, the historical whole-tile DC-offset control ($C_{1\text{,historical\_dc\_offset}}$) exhibited an empirical ratio of 72.2% ($\Delta = +0.3043$ vs. $\Delta = +0.4215$).
2. **The Spatial Rearrangement Collapse:** Crucially, suppressing seam gradients in condition $C_{2\text{,seam\_suppressed}}$ does not recover model performance. Permuting distant tiles under suppressed seams still results in a massive collapse ($\Delta = +0.4808$), an effect fourfold larger than pure boundary seams alone.

These findings definitively refute the artifact-only null hypothesis ($H_0$): tile scrambling is **not** merely an artifact of artificial boundary seams. However, spatial scrambling does not isolate independent stereotactic spatial coordinates. Instead, spatial scrambling conflates four inseparable factors:
- **Altered Macroscopic Anatomical Layout:** Destruction of the global spatial configuration of cranial structures.
- **Non-Local Tissue Juxtapositions:** Creation of biologically impossible interfaces, such as calvarial bone placed immediately adjacent to ventricular cerebrospinal fluid.
- **Residual Boundary Discontinuities:** Remaining step gradients along the tile interfaces that survive smoothing filters.
- **Out-of-Distribution (OOD) Manifold Shifts:** Presentation of synthetic mosaic patterns that fall far outside the manifold of natural MRI acquisitions.

### 6.2 The Anatomy of a Shortcut: Context Disorientation vs. Lesion Reliance
Why does a model with 100% visibility of the tumour core and a 15-pixel peritumoral margin fail so catastrophically when distant cranial context is permuted?

In clinical radiology, gliomas and pituitary tumours exhibit distinct histopathological and morphological features on T1-CE MRI: gliomas frequently present as infiltrative, heterogeneously enhancing parenchymal masses with necrosis and peritumoral edema, whereas pituitary adenomas present as solid sellar or suprasellar lesions expandingly displacing the optic chiasm [13, 14]. Crucially, they occupy strictly distinct anatomical compartments: gliomas are intra-axial supratentorial or infratentorial tumours, whereas pituitary adenomas occur exclusively at the skull base in the sella turcica.

Our empirical transition data reveal that ResNet-50 does not autonomously diagnose tumour pathology from focal lesion morphology alone. Instead, it exploits macroscopic cranial landmarks—such as the cerebral convexity, ventricles, and skull-base contours—as a categorical spatial prior. When these surrounding anatomical structures are scrambled and unnatural tissue juxtapositions are introduced, the network's spatial coordinate frame collapses, driving the model into its default skull-base pituitary prior.

### 6.3 Methodological Implications for Machine Learning Robustness
Our findings carry vital methodological implications for perturbation-based attribution studies in computer vision and medical imaging [8, 10]:
1. **Interventions Introduce Confounds:** Image perturbation techniques (cutting, cropping, scrambling, inpainting) cannot be assumed to manipulate only the intended target property. As demonstrated by condition $C_{1\text{,true\_seam\_w2}}$, tile cutting introduces high-frequency boundary noise that acts as an independent non-pathological confound.
2. **Multi-Control Designs Are Essential:** Any study employing spatial scrambling must include true boundary seam controls ($C_{1\text{,true\_seam\_w2}}$) and seam-suppressed ($C_{2\text{,seam\_suppressed}}$) controls to verify whether observed declines reflect spatial dependencies, boundary edge artifacts, or compound distribution shifts.
3. **Radiometric Moment Matching Is Insufficient:** Preserving global mean and variance between $C_0$ and $C_3$ proved that first and second histogram moments were matched, but completely failed to prevent high-frequency spectral distortion.

---

## 7. Limitations

1. **Single-Source Dataset:** The study was conducted on the public Cheng Figshare dataset [13]. While this is the standard benchmark in brain tumour MRI classification literature, multi-center generalization across diverse hospital cohorts (e.g., BraTS, TCGA-LGG/GBM) remains to be evaluated.
2. **Two-Dimensional Slices with Unverified Acquisition Planes:** The dataset consists of selected 2D slices without DICOM orientation matrices rather than 3D volumetric MRI scans. While 2D slice classification represents the dominant paradigm in existing literature on this benchmark, 3D volumetric convolutional models may exhibit different spatial context dependencies.
3. **Single Architectural Family:** Primary experiments were evaluated using ResNet-50 backbones. While ResNet-50 is the benchmark architecture in medical shortcut discovery [2, 12], the relative vulnerability of Vision Transformers (ViT) and Swin Transformers to seam artifacts versus spatial permutations represents an open research area.
4. **Lack of Clinical Acquisition Metadata & Unresolved Acquisition-Plane Confound (UNRESOLVED — DATASET LIMITATION):** The public Figshare dataset lacks full DICOM metadata and orientation tags, precluding verifiable acquisition-plane stratification (axial, coronal, sagittal). We explicitly mark the acquisition-plane confound as **UNRESOLVED — DATASET LIMITATION**. While resolution-stratified sensitivity analysis confirms stability between majority ($512\times512$) and minority ($256\times256$) image dimensions, resolution stratification does not resolve acquisition-plane confounding.
5. **Categorical Prior vs. Continuous Coordinate Reliance:** While our results demonstrate categorical sensitivity to cranial disorganization and unnatural tissue juxtapositions, they do not establish continuous stereotactic metric coordinate reliance.

---

## 8. Conclusion

This study provides a rigorous multi-control experimental disentanglement of synthetic tile-seam edge artifacts from spatial rearrangement sensitivity in deep brain tumour MRI classification. By demonstrating that synthetic seams alone cause measurable degradation while seam-suppressed tile permutation independently collapses classification performance, we show that the tile-scrambling phenomenon is driven by a dual-factor mixed mechanism. Deep convolutional classifiers rely fundamentally on global cranial context as a diagnostic shortcut, collapsing into skull-base prediction modes when surrounding anatomy is permuted. These findings mandate that future spatial perturbation studies implement explicit boundary controls, and reinforce the critical principle that deep medical models must be audited for contextual shortcuts before clinical translation.

---

## Declarations

- **Target Journal:** [Pending author selection; candidate options provided in supplementary documentation].
- **Data Availability:** The Cheng Figshare brain tumour MRI dataset is publicly available at Figshare (DOI: 10.6084/m9.figshare.1512427). Preprocessed manifests and derived prediction matrices are archived in the project repository.
- **Code & Reproducibility Artifacts Availability:** All source code for baseline model training, spatial intervention generation, out-of-fold inference, and statistical cluster bootstrapping is available in the public project repository at [https://github.com/CSrajput-ux/brain-tumor-prediction-using-deep-leaning](https://github.com/CSrajput-ux/brain-tumor-prediction-using-deep-leaning) (anonymized code repository provided for peer review). Pinned commit: `main` branch. Permanent archive DOI (e.g., Zenodo / OSF): [PENDING DEPOSITION PRIOR TO PUBLICATION — DO NOT FABRICATE DOI].
- **Funding:** [Funding statement to be inserted by authors prior to submission].
- **Competing Interests:** The authors declare no competing financial or non-financial interests.
- **Ethics Approval:** Ethical approval was not required for this study as it involves secondary analysis of fully anonymized, publicly available open-access research data.
- **Author Information & Contributions:** [Author names, affiliations, ORCIDs, and contribution statements to be inserted by authors in accordance with selected journal single- or double-blind review policy].
- **Acknowledgments:** [Acknowledgments to be inserted by authors].

---

## References

1. Geirhos, R., Jacobsen, J. H., Michaelis, C., Zemel, R., Brendel, W., Bethge, M., & Wichmann, F. A. (2020). Shortcut learning in deep neural networks. *Nature Machine Intelligence*, 2(11), 665–673.
2. DeGrave, A. J., Janizek, J. D., & Lee, S. I. (2021). AI for radiographic COVID-19 detection frequently relies on superficial shortcuts. *Nature Machine Intelligence*, 3(5), 410–419.
3. Zech, J. R., Badgeley, M. A., Liu, M., Costa, A. B., Titano, J. J., & Oermann, E. K. (2018). Variable generalization performance of a deep learning model to detect pneumonia in chest radiographs: A cross-sectional study. *PLOS Medicine*, 15(11), e1002683.
4. Badgeley, M. A., Zech, J. R., Oakden-Rayner, L., Glicksberg, B. S., Liu, M., Gale, W., McConnell, M. V., Percha, B., Snyder, T. M., & Dudley, J. T. (2019). Deep learning predicts hip fracture using confounding patient and healthcare variables. *npj Digital Medicine*, 2(1), 31.
5. Winkler, J. K., Fink, C., Toberer, F., Enk, A., Deinlein, T., Hofmann-Wellenhof, R., Thomas, L., Lallas, A., Blum, A., Stolz, W., & others. (2019). Association between surgical skin markings in dermoscopic images and diagnostic performance of a deep learning convolutional neural network for melanoma recognition. *JAMA Dermatology*, 155(10), 1135–1141.
6. Bissoto, A., Perez, F., Ribeiro, V., Avila, S., & Valle, E. (2019). (De)constructing bias on skin lesion datasets. *IEEE Conference on Computer Vision and Pattern Recognition Workshops (CVPRW)*, 335–344.
7. Xiao, K., Engstrom, L., Ilyas, A., & Madry, A. (2021). Noise or signal: The role of image backgrounds in object recognition. *International Conference on Learning Representations (ICLR)*.
8. Zeiler, M. D., & Fergus, R. (2014). Visualizing and understanding convolutional networks. *European Conference on Computer Vision (ECCV)*, 818–833.
9. Fong, R. C., & Vedaldi, A. (2017). Interpretable explanations of black boxes by meaningful perturbation. *IEEE International Conference on Computer Vision (ICCV)*, 3429–3437.
10. Bertalmio, M., Sapiro, G., Caselles, V., & Ballester, C. (2000). Image inpainting. *ACM SIGGRAPH*, 417–424.
11. Vangala, V., et al. (2026). Scores that hold, benchmarks that leak: Measuring dataset contamination in public brain-tumor MRI classification. *arXiv preprint arXiv:2610.00421*.
12. Cheng, J., Huang, W., Cao, S., Yang, R., Yang, W., Yun, Z., Wang, Z., & Feng, Q. (2015). Enhanced performance of brain tumor classification via tumor region augmentation and partition. *PLOS ONE*, 10(10), e0140381.
13. Cheng, J., Yang, W., Huang, M., Huang, W., Jiang, J., Zhou, Y., Yang, R., Shen, J., Wu, J., & Feng, Q. (2016). Retrieval of brain tumors by adaptive spatial pooling and Fisher vector representation. *PLOS ONE*, 11(6), e0157112.
14. Rossi, E., et al. (2024). TACE: Tumor-aware counterfactual explanations for medical imaging. *arXiv preprint arXiv:2409.13045*.
15. Castro, D. C., Walker, I., & Glocker, B. (2020). Causality matters in medical imaging. *Nature Communications*, 11(1), 3673.
16. Oakden-Rayner, L., Dunnmon, J., Carneiro, G., & R{\'e}, C. (2020). Hidden stratification causes clinically meaningful failures in machine learning for medical imaging. *ACM Conference on Health, Inference, and Learning (CHIL)*, 151–159.
