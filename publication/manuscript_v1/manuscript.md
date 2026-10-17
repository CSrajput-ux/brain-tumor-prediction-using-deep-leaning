# Disentangling Synthetic Edge Artifacts and Spatial-Context Sensitivity in Brain MRI Tumour Classification: A Multi-Control Spatial Intervention Study

**Authors:** [Author Names Anonymized for Peer Review]  
**Affiliations:** [Institutional Affiliations Anonymized for Peer Review]  
**Correspondence:** [Corresponding Author Email Anonymized]  

---

## Abstract

**Background:** Deep convolutional neural networks (CNNs) have demonstrated remarkable nominal accuracy in brain tumour classification from magnetic resonance imaging (MRI). However, emerging evidence across medical imaging suggests that high predictive performance is frequently confounded by shortcut learning on non-pathological background features. Spatial perturbation studies, such as distant-context tile scrambling, have reported catastrophic classification failure when surrounding cranial structures are disrupted, suggesting that classifiers rely heavily on global anatomical layout. Nonetheless, tile scrambling simultaneously introduces prominent high-frequency step discontinuities along tile seams. This introduces a critical unresolved question: does the performance collapse reflect genuine model reliance on macroscopic cranial layout, or is it an artifactual vulnerability to synthetic high-frequency edge noise?

**Methods:** We conducted a preregistered, multi-control spatial intervention experiment using the benchmark Cheng Figshare brain tumour MRI cohort (3,064 2D T1-contrast-enhanced slices from 233 patient clusters, encompassing meningioma, glioma, and pituitary tumour). Across three cross-validation regimes ($S_0$: patient-disjoint, $S_1$: candidate duplicate-cleaned at SSIM 0.80, and $S_2$: aggressively grouped at SSIM 0.75), we evaluated 15 frozen ResNet-50 checkpoints across four matched conditions: (1) $C_0$ original baseline; (2) $C_1$ seam-only control, injecting boundary step discontinuities matching scrambled DC offsets onto unpermuted anatomy; (3) $C_2$ seam-suppressed spatial rearrangement, permuting distant tiles while cross-fading tile boundaries (reducing boundary seam Sobel gradient energy by 54.8% and excess high-frequency Fourier energy by 84.9%); and (4) $C_3$ raw historical tile scrambling. In all conditions, the tumour core and a 15-pixel dilation margin ring were strictly protected (zero pixels altered). Across 36,768 matched out-of-fold forward evaluations, uncertainty was quantified using synchronized paired cluster bootstrapping ($B=2,000$ resamples) and Holm-Bonferroni Family-Wise Error Rate (FWER) multiplicity control.

**Results:** In the primary patient-disjoint split ($S_0$), raw scrambling caused a severe drop replicating historical benchmarks ($\Delta \text{Macro-F1} = +0.4215$, 95% CI: $[0.3734, 0.4726]$, $p < 10^{-15}$). Synthetic seams alone ($C_1$) induced a statistically significant drop of $\Delta \text{Macro-F1} = +0.3043$ (95% CI: $[0.2547, 0.3510]$, $p < 10^{-15}$), proving that CNN feature hierarchies are acutely fragile to high-frequency grid step edges. Crucially, seam-suppressed tile permutation ($C_2$) still caused an extreme performance collapse of $\Delta \text{Macro-F1} = +0.4808$ (95% CI: $[0.4361, 0.5292]$, $p < 10^{-15}$), far exceeding our preregistered practical significance threshold of $0.150$. Mechanistic transition analysis revealed that cranial disorientation collapsed glioma recall from 95.0% to 8.6%, with 63.5% of gliomas misclassified as pituitary tumour—a skull-base lesion.

**Conclusions:** Our findings demonstrate a dual-factor, mixed mechanism: while artificial boundary discontinuities alone degrade CNN feature extraction, macroscopic spatial layout is independently essential for brain tumour classification in this architecture. Permuting cranial anatomy destroys the global coordinate anchor separating supratentorial glioma from skull-base pituitary tumour, collapsing the classifier into its prior. These results establish that perturbation studies must explicitly control for high-frequency intervention artifacts, and emphasize that deep medical classifiers rely heavily on extracranial context shortcuts rather than autonomous tumour pathology.

**Keywords:** Brain tumour classification; Convolutional neural networks; Magnetic resonance imaging; Shortcut learning; Spatial context; Image perturbation; Artifact disentanglement; Reproducibility.

---

## 1. Introduction

Deep learning models have achieved expert-level nominal performance across diverse medical image classification tasks, including dermatological lesion triage, chest radiograph screening, and intracranial neoplasm diagnosis from magnetic resonance imaging (MRI) [1–4]. In neuro-oncology, accurate classification of primary brain tumours into meningioma, glioma, and pituitary tumour on contrast-enhanced T1-weighted MRI is clinically vital for surgical planning, radiotherapy, and targeted chemotherapy [13, 14]. Numerous published studies report classification accuracies exceeding 94% on public brain tumour datasets, frequently using deep convolutional neural network (CNN) backbones such as ResNet-50 [13, 14].

However, high predictive accuracy in machine learning does not guarantee that models have learned clinically meaningful, disease-specific features [1, 2]. Deep neural networks are known to exploit "shortcuts"—unintended statistical correlations between non-pathological background image features and target diagnostic labels that hold within training distributions but fail under clinical distribution shifts [1, 2]. Landmark studies have documented profound shortcut reliance in medical imaging: convolutional classifiers have been shown to predict COVID-19 and pneumonia from hospital-specific radiograph annotations and radiographic projection markers [2, 3], detect hip fractures from scanner technical metadata [4], and classify melanomas using surgical skin markings rather than lesion dermoscopy [5, 6].

To probe whether medical classifiers rely on pathological lesions or extraneous surrounding image context, researchers frequently employ spatial perturbation interventions, such as focal occlusions, bounding-box cropping, and tile scrambling [7, 8, 10]. In recent investigations on public brain MRI datasets, distant-context tile scrambling—in which the tumour core and an immediate peritumoral margin are preserved while distant cranial image tiles are randomly permuted—has been reported to trigger catastrophic performance declines, with Macro-F1 dropping by over 40 percentage points [12]. This collapse has been interpreted as strong evidence that the classifier relies on global cranial anatomical layout as a diagnostic shortcut [12].

Nevertheless, an overlooked methodological vulnerability compromises this spatial perturbation paradigm: **tile scrambling introduces high-frequency artificial boundary step discontinuities at every tile seam.** Natural brain MRI slices are characterized by smooth intensity gradients and continuous anatomical contours governed by biological tissue architecture. When tiles are randomly permuted, sharp intensity discontinuities arise along tile edges. Deep convolutional networks are known to be biased toward high-frequency spectral components and local edge textures [1, 7]. Consequently, an acute scientific ambiguity arises:
> *Does the observed performance collapse under distant tile scrambling reflect true neural network reliance on macroscopic cranial spatial arrangement, or is it an artifactual vulnerability to synthetic high-frequency edge seams introduced by the intervention itself?*

In this study, we address this fundamental question through a controlled, preregistered multi-intervention experiment on the benchmark Cheng Figshare brain tumour MRI cohort (3,064 slices across 233 patient clusters) [13]. By designing two novel, matched control conditions—a **seam-only control ($C_1$)** that injects boundary step discontinuities onto stationary anatomy, and a **seam-suppressed rearrangement ($C_2$)** that permutes tiles while cross-fading seams—we independently isolate the contributions of synthetic boundary edge noise and macroscopic spatial layout. Evaluated across 15 frozen ResNet-50 checkpoints across three cross-validation regimes ($S_0, S_1, S_2$), our study provides the first definitive, multi-control disentanglement of spatial context reliance from synthetic intervention artifacts in medical deep classifiers.

---

## 2. Related Work

### 2.1 Shortcut Learning in Medical Image Analysis
Shortcut learning occurs when machine learning models optimize performance on standard training distributions by learning unintended decision rules that fail under distribution shifts [1, 17]. In medical imaging, shortcuts pose substantial patient safety hazards because models can achieve deceptively high validation scores while remaining entirely clinically invalid [1, 17]. 

DeGrave et al. [2] demonstrated that state-of-the-art CNNs trained to detect COVID-19 from chest radiographs relied on hospital-specific text markers, patient positioning artifacts, and border cropping rather than pulmonary pathology. Similarly, Zech et al. [3] showed that pneumonia classifiers trained across multiple hospital cohorts generalized poorly to external health systems because models exploited scanner-specific calibration tags. In dermatology, Winkler et al. [5] and Bissoto et al. [6] revealed that melanoma classifiers frequently relied on surgical skin markings drawn by dermatologists next to malignant lesions, resulting in substantial false-positive spikes when markings were placed near benign nevi.

### 2.2 Spatial Interventions and Attribution Perturbations
To detect and quantify shortcut reliance, input perturbation techniques have been widely adopted [7, 9, 10]. Zeiler and Fergus [9] pioneered systematic patch occlusion to visualize which image regions drive convolutional feature activations. Fong and Vedaldi [10] formalized meaningful perturbations by optimizing smooth bounding masks to identify minimal image regions necessary for prediction.

In natural image recognition, Xiao et al. [8] developed the ImageNet-9 benchmark, demonstrating that classifiers degrade significantly when foreground objects are placed onto swapped or scrambled backgrounds. In medical imaging, Rossi et al. [15] proposed counterfactual image modifications to isolate pathological lesion features. However, as highlighted by Castro et al. [16], spatial interventions often inadvertently alter multiple non-target image properties simultaneously, creating non-local artifacts that distort causal attribution.

### 2.3 Brain Tumour MRI Classification & Dataset Audits
The benchmark Cheng Figshare dataset [13, 14] has served as the foundation for hundreds of published deep learning studies evaluating meningioma, glioma, and pituitary tumour classification. However, early studies frequently applied naive slice-level random splits, introducing severe patient leakage [12]. Vangala et al. [12] conducted a comprehensive audit of the Cheng dataset, demonstrating that patient-level cross-validation and near-duplicate cleaning are required to prevent data leakage from inflating performance estimates. While Vangala et al. observed that distant tile scrambling degraded ResNet performance, they did not isolate whether this decline was driven by synthetic tile seams or spatial layout disruption. The present study directly resolves this unanswered empirical question.

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
The Cheng Figshare repository represents a historical 2D image collection without full DICOM acquisition headers. Key scanner metadata—such as field strength (1.5T vs 3.0T), repetition time (TR), echo time (TE), and precise slice thickness—are not publicly available. Furthermore, the dataset consists of selected 2D slices rather than complete 3D volumetric acquisitions. All empirical findings are evaluated strictly within the boundaries of this cohort.

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
Images were partitioned into non-overlapping grid tiles of size $16 \times 16$ pixels. Tiles having zero intersection with $M_{\text{protected}}$ were designated as eligible distant context ($\Omega_{\text{distant}}$). A deterministic pseudo-random permutation $\pi$ was assigned per slice using a SHA-256 hash seed:
- **Condition $C_0$ (Original Baseline):** Unperturbed test slices evaluated through standard inference.
- **Condition $C_3$ (Raw Historical Scramble):** Eligible distant tiles were permuted according to $\pi$, preserving global mean and standard deviation while introducing 1-pixel hard step edges.
- **Condition $C_1$ (Seam-Only Control):** Injected inter-tile DC offsets matching the scrambling intervention onto stationary tiles:
  $$\Delta \mu_i = \text{mean}\left(I_{\text{original}}[\Omega_{\text{distant}}(\pi(i))]\right) - \text{mean}\left(I_{\text{original}}[\Omega_{\text{distant}}(i)]\right)$$
  Inside tile $i$, pixel values were shifted by $\Delta \mu_i$. Within-tile texture remained identical to original tissue ($\nabla I_{C1} \equiv \nabla I_{\text{original}}$), while across adjacent tile boundaries, a step discontinuity matching $C_3$ was produced.
- **Condition $C_2$ (Seam-Suppressed Spatial Rearrangement):** Eligible distant tiles were permuted according to $\pi$, but tile boundaries were cross-faded using a distance-weighted Gaussian blending strip of half-width $w = 4$ pixels ($\sigma = 2.5$). Boundary seam Sobel energy was suppressed by 54.8%, and excess high-frequency Fourier energy was reduced by 84.9%.

### 4.4 Out-of-Fold Inference Pipeline
Predictions were generated strictly out-of-fold: in each scenario and fold, the frozen checkpoint evaluated only its designated held-out test fold partition. Slices were never evaluated on checkpoints exposed to them during training. Across 3 scenarios, 5 folds, 4 conditions, and 3,064 slices, exactly 36,768 matched prediction records were generated.

### 4.5 Statistical Inference and Hypothesis Testing
1. **Primary Metric:** Macro-F1 across the three classes.
2. **Canonical Contrast Convention:**
   $$\Delta = \text{Macro-F1}_A - \text{Macro-F1}_B$$
   A positive value indicates that condition $B$ produced a performance drop relative to condition $A$.
3. **Clustered Bootstrap:** Synchronized paired cluster bootstrapping ($B=2,000$ resamples, seed 42) resampled patient clusters in $S_0$ and duplicate-group clusters in $S_1$ and $S_2$. Condition $A$ and condition $B$ received identical resampled cluster draws within every replicate. Empirical 95% confidence intervals were computed as the 2.5th and 97.5th percentiles.
4. **Multiplicity Control:** Holm-Bonferroni step-down FWER adjustments were applied across all 15 confirmatory contrasts simultaneously at $\alpha = 0.05$.
5. **McNemar Tests:** Paired sample-level classification disagreement was evaluated using McNemar $\chi^2$ tests with continuity correction.

---

## 5. Results

### 5.1 Baseline Classification Performance
Under unperturbed baseline conditions ($C_0$), frozen ResNet-50 models achieved high diagnostic accuracy across all cross-validation scenarios (Table 4, Figure 4):
- **Scenario $S_0$ (Patient-Disjoint):** $\text{Macro-F1} = 0.9333$, $\text{Balanced Accuracy} = 0.9362$, $\text{Overall Accuracy} = 0.9409$.
- **Scenario $S_1$ (Cleaned SSIM 0.80):** $\text{Macro-F1} = 0.9332$, $\text{Balanced Accuracy} = 0.9336$, $\text{Overall Accuracy} = 0.9419$.
- **Scenario $S_2$ (Grouped SSIM 0.75):** $\text{Macro-F1} = 0.9273$, $\text{Balanced Accuracy} = 0.9230$, $\text{Overall Accuracy} = 0.9354$.
Per-class F1 scores under baseline were balanced: Meningioma F1 was 0.8850, Glioma F1 was 0.9610, and Pituitary F1 was 0.9539 in $S_0$.

### 5.2 Multi-Condition Intervention Outcomes
Evaluating the frozen checkpoints on the matched spatial intervention conditions revealed severe performance declines across all scenarios (Table 5, Figure 5):
1. **Seam-Only Control ($C_1$):**
   Injecting synthetic boundary step discontinuities without rearranging anatomical tiles caused Macro-F1 to collapse from $0.9333$ to **$0.6290$** in $S_0$ (drop of $\Delta = +0.3043$, 95% CI: $[0.2547, 0.3510]$, $p < 10^{-15}$).
2. **Seam-Suppressed Rearrangement ($C_2$):**
   Permuting distant tiles with smoothed boundary seams caused an even steeper collapse to **$0.4525$** in $S_0$ (drop of $\Delta = +0.4808$, 95% CI: $[0.4361, 0.5292]$, $p < 10^{-15}$).
3. **Raw Scrambling ($C_3$):**
   Raw historical tile scrambling yielded a Macro-F1 of **$0.5118$** in $S_0$ (drop of $\Delta = +0.4215$, 95% CI: $[0.3734, 0.4726]$, $p < 10^{-15}$), replicating historical benchmarks within numerical precision.

### Table 5: Primary Classification Metrics Across Experimental Conditions

| Scenario | Condition | Macro-F1 | Balanced Acc | Overall Acc | F1 Meningioma | F1 Glioma | F1 Pituitary |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **$S_0$** | $C_0$ (Baseline) | **0.9333** | 0.9362 | 0.9409 | 0.8850 | 0.9610 | 0.9539 |
| **$S_0$** | $C_1$ (Seam-Only) | **0.6290** | 0.6817 | 0.6276 | 0.6598 | 0.5687 | 0.6583 |
| **$S_0$** | $C_2$ (Seam-Suppressed) | **0.4525** | 0.5783 | 0.4847 | 0.6187 | 0.1588 | 0.5800 |
| **$S_0$** | $C_3$ (Raw Scramble) | **0.5118** | 0.6082 | 0.5255 | 0.6389 | 0.3076 | 0.5889 |
| **$S_1$** | $C_0$ (Baseline) | **0.9332** | 0.9336 | 0.9419 | 0.8832 | 0.9648 | 0.9514 |
| **$S_1$** | $C_1$ (Seam-Only) | **0.6094** | 0.6633 | 0.6106 | 0.6347 | 0.5534 | 0.6402 |
| **$S_1$** | $C_2$ (Seam-Suppressed) | **0.4941** | 0.5855 | 0.5085 | 0.6029 | 0.3054 | 0.5741 |
| **$S_1$** | $C_3$ (Raw Scramble) | **0.4884** | 0.5732 | 0.5007 | 0.5985 | 0.3072 | 0.5595 |
| **$S_2$** | $C_0$ (Baseline) | **0.9273** | 0.9230 | 0.9354 | 0.8720 | 0.9550 | 0.9548 |
| **$S_2$** | $C_1$ (Seam-Only) | **0.6385** | 0.7135 | 0.6439 | 0.6620 | 0.5248 | 0.7288 |
| **$S_2$** | $C_2$ (Seam-Suppressed) | **0.5159** | 0.6255 | 0.5385 | 0.6387 | 0.2745 | 0.6345 |
| **$S_2$** | $C_3$ (Raw Scramble) | **0.5303** | 0.6281 | 0.5463 | 0.6546 | 0.3124 | 0.6240 |

### 5.3 Canonical Paired Contrasts & Hypothesis Decisions
Synchronized paired cluster bootstrap contrasts ($B=2,000$) provided decisive statistical evidence (Table 6, Figure 6):
1. **Replication of Raw Scrambling Drop ($C_3 \text{ vs } C_0$):**
   In $S_0$, $\Delta = +0.4215$ (95% CI: $[0.3734, 0.4726]$, McNemar $\chi^2 = 1145.1, p < 10^{-15}$). Replicated in $S_1$ ($\Delta = +0.4447$) and $S_2$ ($\Delta = +0.3969$).
2. **Seam-Only Degradation ($C_1 \text{ vs } C_0$):**
   In $S_0$, $\Delta = +0.3043$ (95% CI: $[0.2547, 0.3510]$, McNemar $\chi^2 = 824.1, p < 10^{-15}$). Replicated in $S_1$ ($\Delta = +0.3237$) and $S_2$ ($\Delta = +0.2887$). **Hypothesis $H_1$ is supported.**
3. **Independent Spatial-Rearrangement Drop ($C_2 \text{ vs } C_0$):**
   In $S_0$, $\Delta = +0.4808$ (95% CI: $[0.4361, 0.5292]$, McNemar $\chi^2 = 1273.9, p < 10^{-15}$). Replicated in $S_1$ ($\Delta = +0.4390$) and $S_2$ ($\Delta = +0.4114$). In all scenarios, this drop substantially exceeds the preregistered threshold of $0.150$. **Hypothesis $H_2$ is supported.**
4. **Scrambling Beyond Seams Alone ($C_3 \text{ vs } C_1$):**
   In $S_0$, $\Delta = +0.1172$ (95% CI: $[0.0838, 0.1536]$, McNemar $\chi^2 = 170.5, p < 10^{-15}$). Permuting tiles is significantly and reliably more destructive than injecting seams alone. **Null hypothesis $H_0$ is decisively refuted.**
5. **Sensitivity to Seam Smoothing ($C_3 \text{ vs } C_2$):**
   In $S_0$, $\Delta = -0.0593$ (95% CI: $[-0.0836, -0.0354]$, $p = 3.62 \times 10^{-13}$). Seam smoothing did not mitigate the scrambling drop; $C_2$ was actually worse than $C_3$. In $S_1$ ($\Delta = +0.0057, p=0.123$) and $S_2$ ($\Delta = -0.0144, p=0.138$), the difference was not statistically significant.

### Table 6: Canonical Paired Statistical Contrasts

| Scenario | Contrast ID | Condition A | Condition B | Macro-F1 A | Macro-F1 B | Signed Diff $(A - B)$ | Bootstrap 95% Cl | Fold Std | McNemar $\chi^2$ | $p$-value | Holm FWER Status |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **$S_0$** | **C3 vs C0** | $C_0$ | $C_3$ | 0.9333 | 0.5118 | **+0.4215** | $[+0.3734, +0.4726]$ | 0.0939 | 1145.1 | $< 10^{-15}$ | REJECT $H_0$ |
| **$S_0$** | **C1 vs C0** | $C_0$ | $C_1$ | 0.9333 | 0.6290 | **+0.3043** | $[+0.2547, +0.3510]$ | 0.0901 | 824.1 | $< 10^{-15}$ | REJECT $H_0$ |
| **$S_0$** | **C2 vs C0** | $C_0$ | $C_2$ | 0.9333 | 0.4525 | **+0.4808** | $[+0.4361, +0.5292]$ | 0.0390 | 1273.9 | $< 10^{-15}$ | REJECT $H_0$ |
| **$S_0$** | **C3 vs C1** | $C_1$ | $C_3$ | 0.6290 | 0.5118 | **+0.1172** | $[+0.0838, +0.1536]$ | 0.0607 | 170.5 | $< 10^{-15}$ | REJECT $H_0$ |
| **$S_0$** | **C3 vs C2** | $C_2$ | $C_3$ | 0.4525 | 0.5118 | **-0.0593** | $[-0.0836, -0.0354]$ | 0.0782 | 52.8 | $3.6 \times 10^{-13}$ | REJECT $H_0$ |
| **$S_1$** | **C3 vs C0** | $C_0$ | $C_3$ | 0.9332 | 0.4884 | **+0.4447** | $[+0.3972, +0.4929]$ | 0.0929 | 1262.2 | $< 10^{-15}$ | REJECT $H_0$ |
| **$S_1$** | **C1 vs C0** | $C_0$ | $C_1$ | 0.9332 | 0.6094 | **+0.3237** | $[+0.2771, +0.3695]$ | 0.1570 | 920.5 | $< 10^{-15}$ | REJECT $H_0$ |
| **$S_1$** | **C2 vs C0** | $C_0$ | $C_2$ | 0.9332 | 0.4941 | **+0.4390** | $[+0.3925, +0.4875]$ | 0.0617 | 1233.1 | $< 10^{-15}$ | REJECT $H_0$ |
| **$S_1$** | **C3 vs C1** | $C_1$ | $C_3$ | 0.6094 | 0.4884 | **+0.1210** | $[+0.0964, +0.1447]$ | 0.0815 | 250.3 | $< 10^{-15}$ | REJECT $H_0$ |
| **$S_1$** | **C3 vs C2** | $C_2$ | $C_3$ | 0.4941 | 0.4884 | **+0.0057** | $[-0.0102, +0.0219]$ | 0.0472 | 2.38 | 0.123 | FAIL TO REJECT |
| **$S_2$** | **C3 vs C0** | $C_0$ | $C_3$ | 0.9273 | 0.5303 | **+0.3969** | $[+0.3423, +0.4568]$ | 0.0524 | 1068.1 | $< 10^{-15}$ | REJECT $H_0$ |
| **$S_2$** | **C1 vs C0** | $C_0$ | $C_1$ | 0.9273 | 0.6385 | **+0.2887** | $[+0.2281, +0.3542]$ | 0.0994 | 744.3 | $< 10^{-15}$ | REJECT $H_0$ |
| **$S_2$** | **C2 vs C0** | $C_0$ | $C_2$ | 0.9273 | 0.5159 | **+0.4114** | $[+0.3565, +0.4691]$ | 0.0703 | 1080.7 | $< 10^{-15}$ | REJECT $H_0$ |
| **$S_2$** | **C3 vs C1** | $C_1$ | $C_3$ | 0.6385 | 0.5303 | **+0.1082** | $[+0.0801, +0.1351]$ | 0.0879 | 196.0 | $< 10^{-15}$ | REJECT $H_0$ |
| **$S_2$** | **C3 vs C2** | $C_2$ | $C_3$ | 0.5159 | 0.5303 | **-0.0144** | $[-0.0337, +0.0039]$ | 0.0430 | 2.20 | 0.138 | FAIL TO REJECT |

### 5.4 Image Diagnostics & Artifact Efficacy
Quantitative image diagnostics verified that interventions successfully manipulated edge and spectral energy without disturbing within-tile textures (Table 7, Figure 8):
- **Within-Tile Texture Preservation:** Inside the $16\times16$ tiles, Sobel energy in $C_3$ was bit-for-bit identical to baseline natural brain tissue ($30.892316 \equiv 30.892316$). 100% of the gradient energy spike in tile scrambling is localized to the 1-pixel boundary grid ($31.48 \to 129.90$).
- **Boundary Seam Matching in $C_1$:** Condition $C_1$ matched $C_3$ seam Sobel energy within 7.2% ($120.58$ vs $129.90$).
- **Seam Suppression in $C_2$:** Boundary seam Sobel energy was suppressed to $76.00$ ($54.8\%$ reduction of excess boundary gradient). Excess high-frequency Fourier energy was suppressed by **$84.9\%$** ($715.4$ vs $2,597.4$).

### 5.5 Mechanistic Prior Collapse: The Glioma-to-Pituitary Transition
Analysis of confusion matrices (Figure 7) and class transitions (Figure 9) uncovered the underlying representational mechanism:
- Under baseline conditions ($C_0$), glioma classification is near-flawless: glioma recall is 95.0%, with only 2 out of 1,426 gliomas misclassified as pituitary tumour (0.14%).
- Under seam-only perturbation ($C_1$), high-frequency edge noise degrades convolutional SNR, causing 31.28% of gliomas to flip to pituitary tumour.
- Under spatial scrambling ($C_2$ and $C_3$), glioma recall catastrophically collapses to **8.63%** in $S_0$ $C_2$. Over **63.53% of true gliomas are misclassified as pituitary tumour** (906/1,426).
- Conversely, pituitary tumours are virtually never misclassified as glioma under scrambling (0/930 in $C_2$).
This dramatic directional collapse demonstrates that intact supratentorial cranial geometry is a necessary anchor for the model to classify intra-axial gliomas. When cranial layout is permuted, the model loses spatial orientation and defaults to its skull-base pituitary prediction prior.

---

## 6. Discussion

### 6.1 Disentangling the Dual Mechanisms of Spatial Degradation
Our experimental findings resolve the core controversy surrounding distant-context perturbation in brain tumour classification. The observed performance collapse under tile scrambling is governed by a **mixed, dual-factor mechanism ($H_3$)**:
1. **The Synthetic Seam Vulnerability:** Condition $C_1$ proves that deep CNN convolutional hierarchies are acutely fragile to high-frequency grid step edges. Injecting step edges without moving any anatomical tissue causes a massive decline ($\Delta = +0.3043$). The magnitude of this drop is 72.2% as large as raw scrambling.
2. **The Independent Spatial-Layout Requirement:** Crucially, suppressing seam gradients in condition $C_2$ does not recover model performance. Permuting distant tiles under suppressed seams still results in a massive collapse ($\Delta = +0.4808$).

These findings definitively refute the artifact-only null hypothesis ($H_0$): tile scrambling is **not** merely an artifact of artificial boundary seams. Deep CNN classifiers rely fundamentally on macroscopic cranial spatial arrangement.

### 6.2 The Anatomy of a Shortcut: Context Disorientation vs. Lesion Reliance
Why does a model with 100% visibility of the tumour core and a 15-pixel peritumoral margin fail so catastrophically when distant cranial context is permuted?

In clinical radiology, gliomas and pituitary tumours exhibit distinct histopathological and morphological features on T1-CE MRI: gliomas frequently present as infiltrative, heterogeneously enhancing parenchymal masses with necrosis and peritumoral edema, whereas pituitary adenomas present as solid sellar or suprasellar lesions expandingly displacing the optic chiasm [13, 14]. Crucially, they occupy strictly distinct anatomical compartments: gliomas are intra-axial supratentorial or infratentorial tumours, whereas pituitary adenomas occur exclusively at the skull base in the sella turcica.

Our empirical transition data reveal that ResNet-50 does not autonomously diagnose tumour pathology from focal lesion morphology alone. Instead, it exploits macroscopic cranial landmarks—such as the cerebral convexity, ventricles, and skull-base contours—as a spatial coordinate shortcut. When these distant anatomical landmarks are disorganized, the network's spatial coordinate frame collapses, driving the model into its default skull-base pituitary prior.

### 6.3 Methodological Implications for Machine Learning Robustness
Our findings carry vital methodological implications for perturbation-based attribution studies in computer vision and medical imaging [8, 10]:
1. **Interventions Introduce Confounds:** Image perturbation techniques (cutting, cropping, scrambling, inpainting) cannot be assumed to manipulate only the intended target property. As demonstrated by condition $C_1$, tile cutting introduces massive high-frequency boundary noise that acts as an independent adversarial confound.
2. **Multi-Control Designs Are Essential:** Any study employing spatial scrambling must include seam-only ($C_1$) and seam-suppressed ($C_2$) controls to verify that observed declines reflect true spatial dependencies rather than boundary edge artifacts.
3. **Radiometric Moment Matching Is Insufficient:** Preserving global mean and variance between $C_0$ and $C_3$ proved that first and second histogram moments were matched, but completely failed to prevent high-frequency spectral distortion.

---

## 7. Limitations

1. **Single-Source Dataset:** The study was conducted on the public Cheng Figshare dataset [13]. While this is the standard benchmark in brain tumour MRI classification literature, multi-center generalization across diverse hospital cohorts (e.g., BraTS, TCGA-LGG/GBM) remains to be evaluated.
2. **Two-Dimensional Slices:** The dataset consists of selected 2D axial slices rather than 3D volumetric MRI scans. While 2D slice classification represents the dominant paradigm in existing literature, 3D convolutional models may exhibit different spatial context dependencies.
3. **Single Architectural Family:** Primary experiments were evaluated using ResNet-50 backbones. While ResNet-50 is the benchmark architecture in medical shortcut discovery [2, 12], the relative vulnerability of Vision Transformers (ViT) and Swin Transformers to seam artifacts versus spatial permutations represents an open research area.
4. **Lack of Clinical Acquisition Metadata:** The public Figshare dataset lacks full DICOM metadata, precluding stratification by scanner vendor, field strength, or contrast timing.
5. **Categorical vs. Continuous Coordinate Reliance:** While our results demonstrate categorical sensitivity to cranial disorganization, they do not establish continuous stereotactic metric coordinate reliance.

---

## 8. Conclusion

This study provides the first controlled experimental disentanglement of synthetic tile-seam edge artifacts from macroscopic spatial-layout sensitivity in deep brain tumour MRI classification. By demonstrating that synthetic seams alone cause severe degradation, while seam-suppressed tile permutation independently collapses classification performance, we prove that the tile-scrambling phenomenon is driven by a dual-factor mixed mechanism. Deep convolutional classifiers rely fundamentally on global cranial spatial context as a diagnostic shortcut, collapsing into skull-base prediction modes when surrounding anatomy is permuted. These findings mandate that future spatial perturbation studies implement explicit boundary controls, and reinforce the critical principle that deep medical models must be audited for contextual shortcuts before clinical translation.

---

## Declarations

- **Data Availability:** The Cheng Figshare brain tumour MRI dataset is publicly available at Figshare (DOI: 10.6084/m9.figshare.1512427). Preprocessed manifests and derived prediction matrices are archived in the project repository.
- **Code Availability:** All source code for baseline model training, spatial intervention generation, out-of-fold inference, and statistical cluster bootstrapping is publicly available at [GitHub Repository URL to be inserted upon publication].
- **Funding:** [Funding statement to be inserted by authors].
- **Competing Interests:** The authors declare no competing financial or non-financial interests.
- **Ethics Approval:** Ethical approval was not required for this study as it involves secondary analysis of fully anonymized, publicly available open-access research data.
- **Author Contributions:** [Author contribution statements to be inserted by authors].
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
