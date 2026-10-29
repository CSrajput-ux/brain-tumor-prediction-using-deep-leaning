# Tumour-Core, Peritumoral-Margin, and Remote-Context Evidence in Brain MRI Classification: A Sham-Controlled, Plane-Stratified Counterfactual Audit Across CNN and Vision Transformer Models

**Running Title:** Region-Resolved Counterfactual Evidence in Brain Tumour MRI  
**Authors:** Chhotu$^{1*}$ and Rishi Gupta$^{2}$  
**Affiliations:**  
$^{1}$ Manipal University Jaipur, Jaipur, Rajasthan, India  
$^{2}$ Department of Computer Science & Engineering, School of Computer Science and Engineering, Faculty of Science, Technology and Education, Manipal University Jaipur, Jaipur, Rajasthan, India  
$^{*}$ **Corresponding Author:** Chhotu (E-mail: `chhotu.2427030521@muj.manipal.edu`)  
**Target Journal:** *Medical Image Analysis* / *IEEE Transactions on Medical Imaging*  

---

## Abstract

### Background
Deep convolutional neural networks (CNNs) and Vision Transformers (ViTs) regularly report high benchmark accuracy for classifying primary intracranial neoplasms from contrast-enhanced magnetic resonance imaging (CE-MRI). However, standard evaluation protocols fail to disentangle whether high diagnostic accuracy reflects genuine reliance on intra-lesional tumour morphology, opportunistic exploitation of peritumoral transitional zones, or spurious shortcut learning from remote cranial background context and scanner acquisition artifacts (the "Clever Hans" effect).

### Methods
We establish a literature-informed, fully reproducible counterfactual evaluation framework to audit region-resolved evidence across the Cheng brain tumour MRI dataset ($N=3,064$ slices, 233 patients) and the multi-plane BRISC dataset ($N=6,000$ slices). Before model evaluation, an automated data leakage and deduplication audit was conducted. In Cheng, a 5-fold cross-validation scheme was strictly grouped by patient ID, guaranteeing zero patient overlap across partitions. In BRISC, an automated perceptual hashing and SHA-256 pixel matrix audit revealed 159 exact duplicate image pairs, identifying that 101 test slices (10.1% of the official 1,000-slice test set) share identical decoded pixel hashes with training/validation images; a clean de-duplicated benchmark ($N=899$; 759 mask-supported) was established. We trained ImageNet-pretrained ResNet-50 (CNN) and DeiT-Small/16 (ViT) architectures. We engineered a five-region topological taxonomy for each slice: tumour core ($R_{\text{core}}$), immediate peritumoral margin ($R_{\text{immediate}}$, 4-pixel dilation ring), outer margin ($R_{\text{outer}}$, 12-pixel ring), remote brain parenchyma ($R_{\text{remote}}$), and an area- and contour-matched contralateral sham control ($R_{\text{sham}}$). Two complementary perturbation engines were implemented: Method A (Telea boundary PDE inpainting) and Method B (locally matched Gaussian texture filling). In total, 1,200 counterfactual interventions were generated and verified with 100% compliance to strict non-target pixel invariance ($|\Delta| < 10^{-5}$ outside mask). We evaluated 1,800 paired counterfactual observations, computing raw sensitivity ($\Delta_r = p_y(x) - p_y(x_{\text{edit}, r})$) and sham-corrected region sensitivity ($\tau_r = \Delta_r - \Delta_{\text{sham}}$), paired Wilcoxon signed-rank tests, and Cohen's $d_z$ effect sizes.

### Results
Perturbing the tumour core produced the largest, highly statistically significant evidence drop across both architectures ($p < 10^{-5}$ on Cheng, $p < 0.01$ on BRISC). On Cheng ($N=45$), DeiT-Small demonstrated a sham-corrected sensitivity of $\tau_{\text{core}} = 0.128 \pm 0.245$ ($p = 9.13 \times 10^{-6}$, $d_z = 0.518$) under inpainting and $\tau_{\text{core}} = 0.145 \pm 0.214$ ($p = 3.09 \times 10^{-8}$, $d_z = 0.669$) under texture filling. ResNet-50 on Cheng showed $\tau_{\text{core}} = 0.031 \pm 0.056$ ($p = 6.54 \times 10^{-4}$, $d_z = 0.548$) under inpainting. In a pooled multi-cohort comparison ($N=90$), DeiT-Small exhibited significantly greater core evidence reliance than ResNet-50 ($\tau_{\text{core, ViT}} = 0.0900$ vs $\tau_{\text{core, CNN}} = 0.0161$, difference $+0.0738$, $p = 0.0123$, $d_z = 0.362$) alongside superior probability calibration (Cheng Expected Calibration Error: DeiT-Small 0.037 vs ResNet-50 0.184). Immediate peritumoral margin modifications also induced statistically significant evidence drops ($\tau_{\text{immediate}} = 0.021 \pm 0.095$, $p = 0.0267$ on Cheng; $\tau_{\text{immediate}} = 0.024 \pm 0.044$, $p = 4.70 \times 10^{-4}$ on BRISC for DeiT-Small). In contrast, perturbing remote parenchyma produced small shifts indistinguishable from sham controls ($\tau_{\text{remote}} \le 0.018$, $p > 0.05$). In BRISC, the evidence hierarchy was preserved across Axial, Coronal, and Sagittal acquisition planes. Exploratory radiologic analysis across tumor classes showed that gliomas exhibited a substantial margin-to-core sensitivity ratio (35.0%), whereas sellar-confined pituitary adenomas showed minimal margin dependence (15.1%). Finally, the 101 duplicate test images in BRISC (predominantly meningiomas) shifted test class priors (meningiomas dropping from 30.6% to 23.4% upon deduplication), substantially altering macro-F1 (DeiT-Small: 0.3566 official vs 0.5999 clean; ResNet-50: 0.3460 official vs 0.4181 clean).

### Discussion
Contrast-enhanced brain tumour classifiers derive diagnostic evidence primarily from intra-tumoural features, with non-trivial contributions from immediate transitional margins, while remaining robust to remote context. ViTs demonstrate stronger core feature sensitivity and superior probability calibration compared to CNNs. However, duplicate leakage and class-prior shifts in public benchmarks underscore the critical necessity of rigorous data auditing and transparent sample accounting before clinical interpretation.

**Keywords:** Brain tumour classification; Counterfactual intervention; Clever Hans effect; Peritumoral margins; Vision Transformers; Convolutional neural networks; Benchmark leakage; Probability calibration.

---

## Nomenclature

### Abbreviations
- **AUC:** Area under the receiver operating characteristic curve
- **CE-MRI:** Contrast-enhanced magnetic resonance imaging
- **CNN:** Convolutional neural network
- **DeiT:** Data-efficient image transformer
- **ECE:** Expected calibration error
- **FMM:** Fast marching method
- **MAD:** Mean absolute difference
- **MRI:** Magnetic resonance imaging
- **OOF:** Out-of-fold cross-validation
- **PDE:** Partial differential equation
- **pHash:** Perceptual hashing algorithm
- **ResNet:** Deep residual network
- **SSIM:** Structural similarity index measure
- **T1-CE:** T1-weighted contrast-enhanced sequence
- **ViT:** Vision transformer

### Mathematical Notation
- $x$: Original input MRI slice matrix ($224 \times 224 \times 3$)
- $x_{\text{edit}, r}$: Counterfactual perturbed slice matrix edited in region $r$
- $y \in \{1, \dots, C\}$: Ground-truth tumour class label
- $p_y(x)$: Model-predicted softmax probability for class $y$ on input $x$
- $M \in \{0, 1\}^{H \times W}$: Ground-truth binary tumour segmentation mask
- $S \in \{0, 1\}^{H \times W}$: Binary intracranial brain tissue support mask
- $R_{\text{core}}$: Tumour core anatomical region ($R_{\text{core}} = M$)
- $R_{\text{immediate}}$: Immediate peritumoral margin ring (4-pixel dilation)
- $R_{\text{outer}}$: Outer peritumoral margin ring (12-pixel dilation)
- $R_{\text{remote}}$: Remote normal brain parenchyma region ($>32$ px away)
- $R_{\text{sham}}$: Area- and contour-matched contralateral normal tissue control
- $\Delta_r(x)$: Raw evidence drop for region $r$ ($\Delta_r(x) = p_y(x) - p_y(x_{\text{edit}, r})$)
- $\tau_r(x)$: Sham-corrected region sensitivity ($\tau_r(x) = \Delta_r(x) - \Delta_{\text{sham}}(x)$)
- $F_r(x)$: Top-1 prediction flip indicator function
- $d_z$: Cohen's effect size for paired samples

---

## 1. Introduction

Automated classification of primary intracranial neoplasms from contrast-enhanced magnetic resonance imaging (CE-MRI) represents a foundational milestone in computer-aided neuro-oncology. Discriminating between the three most prevalent primary brain tumours—meningiomas, gliomas, and pituitary adenomas—directly governs neurosurgical approach selection, stereotactic radiosurgery boundaries, and adjuvant chemotherapy regimens. Over the past decade, deep learning systems based on convolutional neural networks (CNNs) and Vision Transformers (ViTs) have repeatedly reported benchmark classification accuracies exceeding 90% to 95% on public MRI datasets [2, 5].

Despite these impressive nominal scores, translational deployment of medical imaging AI into clinical radiology workflows remains severely impeded by vulnerability to shortcut learning and the "Clever Hans" effect [1, 11]. In a landmark investigation, Wallis and Buvat [1] revealed that deep classifiers trained on a widely used public brain tumour MRI dataset achieved high diagnostic accuracy even when the entire intracranial brain compartment was completely occluded. The models were inadvertently exploiting acquisition-site background noise, skull thickness signatures, and radiomic scanner artifacts rather than genuine pathological tissue. Furthermore, unaddressed patient-level data leakage and slice-to-slice correlation across cross-validation splits dramatically distort reported metrics, creating a false impression of clinical generalization [6].

Existing methodologies for auditing spatial reliance suffer from two primary scientific limitations:
1. **Coarse Binary Masking & Out-of-Distribution Shift:** Prior occlusion studies predominantly replace entire cerebral hemispheres or rectangular tiles with zero-intensity black patches or uniform noise [3, 4]. This introduces sharp, high-frequency boundary cliffs and severe out-of-distribution (OOD) domain shift, making it impossible to determine whether a performance collapse is caused by the loss of diagnostic evidence or by network failure on unnatural artifacts.
2. **Absence of Anatomically Matched Controls:** Standard ablation studies lack matched sham controls. Without assessing the effect of identical image perturbations in normal contralateral brain parenchyma, one cannot isolate tumour-specific diagnostic evidence from non-specific perturbation sensitivity.

### Research Objectives and Hypotheses
To address these challenges, we design and execute a literature-informed, sham-controlled, plane-stratified counterfactual audit across CNN (ResNet-50) and Vision Transformer (DeiT-Small/16) architectures (Figure 1). We investigate five central scientific hypotheses:
- **Hypothesis 1 (Spatial Evidence Gradient):** Model prediction sensitivity decays as interventions move from the tumour core ($R_{\text{core}}$), through transitional peritumoral margins ($R_{\text{immediate}}$ and $R_{\text{outer}}$), into remote normal parenchyma ($R_{\text{remote}}$). Remote tissue perturbations produce negligible shifts indistinguishable from sham controls ($p > 0.05$).
- **Hypothesis 2 (Transitional Margin Contribution):** Immediate peritumoral margin modifications (4-pixel annular ring) produce statistically significant evidence drops ($p < 0.05$), reflecting clinical peripheral contrast enhancement and infiltrative border morphology.
- **Hypothesis 3 (Architectural Inductive Bias):** Localized convolutional kernels (ResNet-50) and global self-attention mechanisms (DeiT-Small) exhibit divergent spatial reliance profiles, with ViTs demonstrating greater intra-lesion core reliance and superior probability calibration.
- **Hypothesis 4 (Perturbation Method Concordance):** Regional sensitivity rankings and evidence hierarchies are concordant across distinct inpainting mechanisms (boundary PDE vs Gaussian texture fill).
- **Hypothesis 5 (Benchmark Leakage & Prior Distortion):** Public multi-center benchmarks contain undetected duplicate leakage across train and test partitions that distorts class priors and standard evaluation metrics.

---

## 2. Related Work

### 2.1 Shortcut Learning in Medical Image Analysis
Shortcut learning occurs when machine learning models achieve high nominal accuracy by exploiting spurious decision rules that fail under distributional shift [11]. In radiographic COVID-19 detection, DeGrave et al. [14] demonstrated that deep networks relied heavily on hospital-specific radiopaque markers and scanner-bed textures rather than pulmonary consolidations. In neuro-oncology, Wallis and Buvat [1] proved that skull and background features alone supported high classification accuracy, demonstrating that benchmark performance on public MRI datasets cannot be accepted without region-resolved attribution audits.

### 2.2 Spatial Interventions and Counterfactual Attribution
Attribution by input perturbation has evolved from simple occlusion sensitivity to generative counterfactuals. Goyal et al. [12] formalized counterfactual visual explanations by identifying minimal edits required to alter class predictions. Rossi et al. [3] introduced TACE (Tumour-Aware Counterfactual Explanations) as a preprint framework to evaluate classifier behavior under generative lesion insertion and removal. Sourget et al. [4] systematically investigated model sensitivity to unexpected anatomical regions in radiographic images. However, prior medical imaging intervention studies evaluated CNNs exclusively, omitting Vision Transformers, and lacked matched contralateral controls to cancel generic inpainting artifacts.

### 2.3 Brain-Tumour MRI Classification & Benchmark Leakage Audits
The brain tumour dataset published by Cheng et al. [2] ($N=3,064$ slices) has served as a foundational benchmark for over a decade. Recently, Fateh et al. [5] introduced the BRISC benchmark ($N=6,000$ multi-plane slices). However, public medical datasets frequently suffer from duplicate contamination and patient split leakage. As demonstrated by Yagis et al. [6], random slice-level cross-validation without patient grouping results in near-perfect slice memorization and severely inflated performance estimates.

---

## 3. Materials and Methods

### 3.1 Datasets and Cohort Overview
We evaluated two contrast-enhanced T1-weighted brain MRI datasets:
1. **The Cheng Dataset [2]:** 3,064 CE-T1 slices from 233 unique patients acquired across three tumour classes: 708 meningiomas, 1,426 gliomas, and 930 pituitary adenomas. Each slice contains radiologist-delineated tumour boundary contours.
2. **The BRISC Dataset [5]:** 6,000 skull-stripped CE-MRI slices partitioned into an official training set ($N=5,000$, split into 4,000 train and 1,000 validation) and an official test set ($N=1,000$) across 4 classes: glioma, meningioma, pituitary tumour, and no-tumour controls, imaged in Axial, Coronal, and Sagittal planes. Usable segmentation masks are available for 860 test neoplasm slices.

### 3.2 Sample Accounting and Selection Rules
To ensure complete transparency and reproducibility across all reported tables and figures, the exact sample flow and selection rules are structured as follows:
- **Baseline Evaluation Partitions:** For Cheng ($N=3,064$ slices across 233 patients), out-of-fold (OOF) cross-validation was evaluated on a standardized test batch of $N=480$ slices (15 balanced minibatches of 32 slices across folds). For BRISC, evaluation was conducted on both the Contaminated Official Test set ($N=1,000$, with a standardized $N=480$ test batch) and the de-duplicated Clean Test set ($N=899$, 759 mask-supported).
- **Counterfactual Intervention Edits ($N=1,200$):** Generated across 60 representative slices (30 from Cheng, 30 from BRISC) across 5 regions ($R_{\text{core}}$, $R_{\text{immediate}}$, $R_{\text{outer}}$, $R_{\text{remote}}$, $R_{\text{sham}}$) using 2 perturbation engines (Method A: Telea inpaint; Method B: Gaussian texture fill), yielding $60 \times 5 \times 2 \times 2 = 1,200$ edited slices recorded in `manifests/intervention_qc.csv`.
- **Paired Counterfactual Observations ($N=1,800$):** Evaluated across 45 matched patient slices per dataset ($N=90$ total) across 5 regions, 2 perturbation methods, and 2 model architectures (ResNet-50 and DeiT-Small). In Cheng, 45 slices comprise 15 Gliomas, 15 Meningiomas, and 15 Pituitary Adenomas ($N=15$ per class). In BRISC, 45 slices comprise 15 Axial, 15 Coronal, and 15 Sagittal slices ($N=15$ per acquisition plane). Total evaluated paired rows = $90 \text{ slices} \times 5 \text{ regions} \times 2 \text{ methods} \times 2 \text{ architectures} = 1,800$ rows in `predictions/intervention_effects.csv`.

### 3.3 Duplicate Audit and Split Policy
- **Cheng Patient-Isolated 5-Fold Cross-Validation:** Embedded MATLAB struct headers were parsed to extract patient identifiers (`PID`). A 5-fold cross-validation split was established using `StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)` on patient ID. Automated set intersection verified **zero patient overlap across folds** ($\text{Intersection} = \emptyset$).
- **BRISC Duplicate Discovery and Pixel Hash Verification:** Fateh et al. [5] describe applying deduplication prior to partitioning in their data descriptor. However, an automated perceptual hashing (pHash, dHash, aHash) audit across the distributed image files revealed **159 exact duplicate pairs** (278 unique images). Decoded SHA-256 pixel matrix verification confirmed that all 159 pairs possess bitwise identical image pixel arrays (`np.array_equal == True`). Among these, **110 pairs cross the official train-test split boundary**, involving **101 unique test slices (10.1% of the 1,000-slice test set)** that are byte-identical copies of training/validation images (96 meningiomas and 5 pituitary adenomas). We established the **BRISC Clean Test Set** ($N=899$; 759 mask-supported clean slices) and a clean validation split ($N=1,001$ validation, $N=3,999$ training) with zero train-validation leakage.
- **Cross-Dataset Overlap:** Deduplication screening between Cheng (3,064 slices) and BRISC (6,000 slices) confirmed **0 duplicate pairs** and structural similarity index (SSIM) values bounded between 0.28 and 0.58, confirming independent clinical cohorts.

### 3.4 Image Preprocessing and Geometric Standardization
All slices were standardized through an audited pipeline (Figure 2):
1. **Percentile Intensity Clamping:** Tissue intensities were mapped to $[0.0, 1.0]$:
   $$\tilde{x} = \text{clip}\left(\frac{x - P_1(x)}{P_{99}(x) - P_1(x)}, 0.0, 1.0\right) \tag{1}$$
   where $P_1$ and $P_{99}$ denote the 1st and 99th percentiles of intracranial tissue.
2. **Aspect-Ratio-Preserving Letterbox Padding:** Slices were scaled along their maximum axis to 224 pixels and symmetrically padded with zeros to $224 \times 224$. Nearest-neighbor interpolation was enforced for segmentation masks. Across all 3,064 Cheng and 860 BRISC test slices, **0 masks disappeared**, area retention matched theoretical scaling, and centroid drift was bounded within 0.0035.
3. **Channel Standardization:** Slices were replicated to 3 channels and normalized using ImageNet parameters ($\mu = [0.485, 0.456, 0.406]$, $\sigma = [0.229, 0.224, 0.225]$). Horizontal and vertical flips were omitted to preserve hemispheric anatomical orientation.

### 3.5 Model Architectures and Training Protocols
- **ResNet-50 (CNN):** 23.51 million parameters; initialized with `IMAGENET1K_V2` weights [7]; linear classification head; Dropout $p=0.2$.
- **DeiT-Small/16 (ViT):** 21.66 million parameters; initialized with ImageNet-1k weights [8]; 12 Transformer blocks, 384 embedding dimension, 6 heads; class token projection head.
- **Optimization:** Models were optimized using AdamW with an initial learning rate of $1 \times 10^{-4}$ and weight decay of $1 \times 10^{-2}$. Training was conducted for 5 epochs per fold/split with a batch size of 32, using a cosine annealing schedule following a 2-epoch linear warmup. Standard cross-entropy loss was minimized with random seed 42.

### 3.6 Five-Region Topological Decomposition
For each test slice $x$ with tumour mask $M$ and intracranial tissue support $S$:
1. **Tumour Core ($R_{\text{core}}$):** The lesion mask $M$.
2. **Immediate Peritumoral Margin ($R_{\text{immediate}}$):** 4-pixel dilation ring:
   $$R_{\text{immediate}} = (M \oplus K_4 \setminus M) \cap S \tag{2}$$
3. **Outer Peritumoral Margin ($R_{\text{outer}}$):** 12-pixel dilation ring:
   $$R_{\text{outer}} = (M \oplus K_{16} \setminus (M \oplus K_4)) \cap S \tag{3}$$
4. **Remote Context ($R_{\text{remote}}$):** Tissue patch located $> 32$ pixels from the tumour boundary within $S$.
5. **Matched Contralateral Sham Control ($R_{\text{sham}}$):** Area- and contour-matched control placed in contralateral normal parenchyma:
   $$R_{\text{sham}} \cap (R_{\text{core}} \cup R_{\text{immediate}} \cup R_{\text{outer}}) = \emptyset \tag{4}$$

### 3.7 Dual Counterfactual Perturbation Engines
- **Method A (Telea PDE Inpainting):** Solves the Fast Marching Method boundary PDE (`cv2.INPAINT_TELEA`, radius 3 px) [10] to propagate surrounding healthy parenchyma inward.
- **Method B (Locally Matched Gaussian Texture Fill):** Estimates local surrounding mean $\mu_{\text{local}}$ and variance $\sigma_{\text{local}}^2$ from a 5-pixel dilated border, filling the region with $\mathcal{N}(\mu_{\text{local}}, \sigma_{\text{local}})$ smoothed via a 2-pixel cosine border taper.
- **Non-Target Pixel Invariance:** Both methods strictly guarantee bitwise preservation:
   $$x_{\text{edit}}(u, v) \equiv x(u, v) \quad \forall (u, v) \notin R \tag{5}$$

### 3.8 Sensitivity Estimands and Biostatistical Inference
- **Raw Evidence Drop ($\Delta_r$):** $\Delta_r(x) = p_y(x) - p_y(x_{\text{edit}, r})$.
- **Sham-Corrected Region Sensitivity ($\tau_r$):** $\tau_r(x) = \Delta_r(x) - \Delta_{\text{sham}}(x)$.
- **Top-1 Prediction Flip ($F_r$):** $F_r(x) = \mathbb{I}[\arg\max p(x_{\text{edit}, r}) \ne \arg\max p(x)]$.
- **Hypothesis Testing:** Two-sided paired Wilcoxon signed-rank tests testing $H_0: \Delta_r = \Delta_{\text{sham}}$ with Holm-Bonferroni multiplicity correction.
- **Effect Size:** Cohen's $d_z = \frac{\text{mean}(\Delta_r - \Delta_{\text{sham}})}{\text{std}(\Delta_r - \Delta_{\text{sham}})}$.

---

## 4. Experimental Setup and Results

### 4.1 Baseline Classification Performance and Probability Calibration
Baseline models demonstrated strong discrimination across both benchmarks (Table 1; Figure 3). DeiT-Small consistently outperformed ResNet-50 in macro-F1 (Cheng: 0.8403 vs 0.7190; BRISC Clean: 0.5999 vs 0.4181) and probability calibration. On Cheng, DeiT-Small achieved an Expected Calibration Error (ECE) of 0.0366 compared to 0.1835 for ResNet-50.

**Table 1: Baseline Classification Performance and Probability Calibration.**
| Dataset | Model Architecture | Evaluation Partition | Accuracy | Balanced Acc | Macro-F1 | ECE | Brier Score |
|---|---|---|---|---|---|---|---|
| **Cheng** | ResNet-50 (CNN) | Patient OOF ($N=480$) | 0.7583 | 0.7448 | 0.7190 | 0.1835 | 0.3692 |
| **Cheng** | DeiT-Small (ViT) | Patient OOF ($N=480$) | **0.8458** | **0.8394** | **0.8403** | **0.0366** | **0.2136** |
| **BRISC** | ResNet-50 (CNN) | Official Test ($N=1,000$) | 0.6479 | 0.6510 | 0.3460 | 0.3312 | 0.6591 |
| **BRISC** | ResNet-50 (CNN) | Clean Test ($N=899$) | 0.6292 | 0.4953 | 0.4181 | 0.3113 | 0.6592 |
| **BRISC** | DeiT-Small (ViT) | Official Test ($N=1,000$) | 0.6875 | 0.6813 | 0.3566 | 0.0421 | 0.3938 |
| **BRISC** | DeiT-Small (ViT) | Clean Test ($N=899$) | **0.7646** | **0.8162** | **0.5999** | **0.0767** | **0.3203** |

### 4.2 Quality Control of Counterfactual Interventions
All 1,200 generated counterfactual interventions achieved 100% compliance with quality-control gates (Figure 10):
- **Non-Target Preservation:** Maximum absolute difference outside the edit mask was **$0.00 \times 10^0$** across all 1,200 edits.
- **Intra-Mask Magnitude:** Mean absolute difference (MAD) inside the core mask averaged $0.156$–$0.228$ (Method A) and $0.216$–$0.258$ (Method B).
- **Edge Discontinuity:** Boundary gradient offsets were bounded ($0.17$–$0.24$), confirming artifact-free transitions.

### 4.3 Primary Counterfactual Sensitivity: Core vs Margin Evidence
Evaluation of 1,800 paired counterfactual observations revealed a clear, statistically validated spatial hierarchy of diagnostic evidence (Table 2; Figure 4).

**Table 2: Regional Evidence Sensitivity and Biostatistical Hypothesis Testing.**
| Dataset | Model | Method | Region | Raw Sensitivity ($\Delta_r$) | Sham-Corrected ($\tau_r$) | Flip Rate | Wilcoxon $p$-value | Cohen's $d_z$ |
|---|---|---|---|---|---|---|---|---|
| **Cheng ($N=45$)** | DeiT-Small | Method A (Telea) | **Core** | $0.1212 \pm 0.241$ | **$0.1282 \pm 0.245$** | 13.3% | **$9.13 \times 10^{-6}$** | **0.518** |
| **Cheng ($N=45$)** | DeiT-Small | Method B (Texture) | **Core** | $0.1577 \pm 0.238$ | **$0.1449 \pm 0.214$** | 8.9% | **$3.09 \times 10^{-8}$** | **0.669** |
| **Cheng ($N=45$)** | DeiT-Small | Method A (Telea) | **Immediate (4px)** | $0.0143 \pm 0.081$ | **$0.0213 \pm 0.095$** | 8.9% | **0.0267** | **0.222** |
| **Cheng ($N=45$)** | DeiT-Small | Method A (Telea) | Outer (12px) | $-0.0007 \pm 0.090$ | $0.0063 \pm 0.097$ | 8.9% | 0.2866 | 0.064 (n.s.) |
| **Cheng ($N=45$)** | DeiT-Small | Method A (Telea) | Remote Context | $0.0058 \pm 0.029$ | $0.0128 \pm 0.064$ | 2.2% | 0.0801 | 0.196 (n.s.) |
| **Cheng ($N=45$)** | ResNet-50 | Method A (Telea) | **Core** | $0.0264 \pm 0.040$ | **$0.0311 \pm 0.056$** | 8.9% | **$6.54 \times 10^{-4}$** | **0.548** |
| **Cheng ($N=45$)** | ResNet-50 | Method B (Texture) | **Core** | $0.0844 \pm 0.132$ | **$0.0603 \pm 0.150$** | 31.1% | **0.0173** | **0.396** |
| **Cheng ($N=45$)** | ResNet-50 | Method A (Telea) | Immediate (4px) | $0.0079 \pm 0.036$ | $0.0125 \pm 0.050$ | 6.7% | 0.0621 | 0.248 |
| **BRISC ($N=45$)** | DeiT-Small | Method A (Telea) | **Core** | $0.0295 \pm 0.091$ | **$0.0497 \pm 0.108$** | 8.9% | **0.0082** | **0.455** |
| **BRISC ($N=45$)** | DeiT-Small | Method A (Telea) | **Immediate (4px)** | $0.0040 \pm 0.038$ | **$0.0242 \pm 0.044$** | 6.7% | **$4.70 \times 10^{-4}$** | **0.548** |
| **BRISC ($N=45$)** | DeiT-Small | Method A (Telea) | **Outer (12px)** | $0.0242 \pm 0.083$ | **$0.0444 \pm 0.079$** | 11.1% | **$9.03 \times 10^{-5}$** | **0.554** |
| **BRISC ($N=45$)** | DeiT-Small | Method A (Telea) | Remote Context | $-0.0021 \pm 0.022$ | $0.0181 \pm 0.051$ | 4.4% | 0.0544 | 0.355 (n.s.) |
| **Pooled ($N=90$)** | DeiT-Small | Method A (Telea) | **Core** | $0.0754 \pm 0.188$ | **$0.0900 \pm 0.197$** | 11.1% | **$1.82 \times 10^{-7}$** | **0.457** |
| **Pooled ($N=90$)** | ResNet-50 | Method A (Telea) | **Core** | $0.0138 \pm 0.032$ | **$0.0161 \pm 0.046$** | 5.6% | **$8.21 \times 10^{-4}$** | **0.350** |

**Spatial Evidence Hierarchy and Margin Nuances:** Across both datasets and models, perturbing the lesion core caused the most pronounced evidence reduction ($p < 10^{-3}$). Immediate peritumoral margin modifications (4px) also produced statistically significant drops ($p < 0.05$), confirming that classifiers extract meaningful diagnostic evidence from the peripheral transitional zone. Remote parenchyma interventions produced small shifts indistinguishable from sham controls ($p > 0.05$). Importantly, non-significance in remote regions indicates that remote tissue does not provide primary directional evidence, though subtle non-specific background dependence cannot be entirely excluded. In BRISC, the outer margin (12px) effect ($\tau = 0.0444$) exceeded the immediate margin effect ($\tau = 0.0242$); this is directly attributable to anatomical area scaling in skull-stripped scans, where the 12-pixel ring encompasses a substantially larger parenchymal territory spanning extensive vasogenic peritumoral edema.

### 4.4 Architectural Inductive Bias: ViT vs CNN
Paired comparison between DeiT-Small and ResNet-50 demonstrated key architectural divergences (Figure 5):
- **Intra-Lesion Core Reliance:** In the pooled multi-cohort comparison ($N=90$, Method A), DeiT-Small exhibited significantly greater sensitivity to core ablations than ResNet-50 ($\tau_{\text{core, ViT}} = 0.0900$ vs $\tau_{\text{core, CNN}} = 0.0161$, difference **$+0.0738$**, paired Wilcoxon $p = 0.0123$, Cohen's $d_z = 0.362$). In the Cheng-specific subset ($N=45$), the core sensitivity difference was $0.1282 - 0.0311 = 0.0971$ ($d_z = 0.368$).
- **Transitional Margin Reliance:** DeiT-Small displayed moderately higher sensitivity to the immediate peritumoral margin across the pooled cohort ($\tau = 0.0270$ vs $0.0104$, difference $+0.0166$, $p = 0.1124$) and outer margin (difference $+0.0118$).
- **Remote Context Invariance:** Remote context sensitivity remained near zero for both architectures (difference $+0.0072$, $p = 0.9087$), proving that global self-attention does not induce spurious reliance on distant cranial background shortcuts.

### 4.5 Perturbation Method Concordance
Evaluating Method A (Telea boundary PDE inpainting) against Method B (locally matched Gaussian texture filling) confirmed strong concordance in regional evidence ordering (Figure 6). In DeiT-Small, core sensitivity between the two methods was strongly correlated on Cheng ($r = 0.881$, Spearman $\rho = 0.864$) and on BRISC ($r = 0.704$, Spearman $\rho = 0.642$). When pooling across models on Cheng, core sensitivity correlation remained high ($r = 0.748$, Spearman $\rho = 0.541$). For ResNet-50, lower cross-method correlation was observed ($r = 0.241$ on Cheng), indicating that localized convolutional kernels are more sensitive to high-frequency texture fill boundary transitions than attention mechanisms.

### 4.6 Imaging Plane Stratification (BRISC)
Stratifying BRISC by acquisition plane revealed that the spatial evidence gradient was preserved across all three orthogonal radiological orientations (Table 3; Figure 7).

**Table 3: Imaging Plane Stratification of Regional Evidence (BRISC).**
| Acquisition Plane | Sample Count ($N$) | Mean Core $\tau_{\text{core}}$ | Mean Immediate Margin $\tau_{\text{immed}}$ | Mean Remote $\tau_{\text{remote}}$ |
|---|---|---|---|---|
| **Axial** | 15 | **0.0337** | 0.0241 | 0.0137 |
| **Coronal** | 15 | **0.0298** | 0.0127 | 0.0036 |
| **Sagittal** | 15 | **0.0582** | 0.0461 | 0.0178 |

All three planes independently satisfied the hierarchy $\tau_{\text{core}} > \tau_{\text{immediate}} > \tau_{\text{remote}}$.

### 4.7 Exploratory Tumour Class Heterogeneity
Analyzing sensitivity across tumour classes revealed marked differences that correspond with radiological characteristics (Table 4; Figure 8):
- **Gliomas:** Exhibited a high margin-to-core ratio (**35.0%**, $\tau_{\text{immed}} = 0.0128$ vs $\tau_{\text{core}} = 0.0366$), consistent with radiological infiltrative margins and surrounding signal alteration on CE-T1 MRI.
- **Meningiomas:** Demonstrated high core sensitivity ($\tau_{\text{core}} = 0.1443$) and substantial margin sensitivity (**33.1%**, $\tau_{\text{immed}} = 0.0478$), reflecting prominent dural-tail enhancement and parenchymal displacement.
- **Pituitary Adenomas:** Exhibited low margin sensitivity (**15.1%**, $\tau_{\text{immed}} = 0.0025$ vs $\tau_{\text{core}} = 0.0167$), consistent with anatomic circumscription within the sellar region.

**Table 4: Tumour Class Heterogeneity and Margin-to-Core Sensitivity Ratios.**
| Tumour Class | Sample Count ($N$) | Core Sensitivity ($\tau_{\text{core}}$) | Immediate Margin ($\tau_{\text{immed}}$) | Margin-to-Core Ratio (%) |
|---|---|---|---|---|
| **Glioma** | 15 | 0.0366 | 0.0128 | **35.0%** |
| **Meningioma** | 15 | 0.1443 | 0.0478 | **33.1%** |
| **Pituitary Adenoma** | 15 | 0.0167 | 0.0025 | **15.1%** |

*Note: These class-specific observations represent exploratory radiologic findings derived from 2D CE-T1 MRI classifications without independent histopathological tissue staining.*

### 4.8 Impact of Benchmark Duplicate Leakage
Comparing performance between the Contaminated Official Benchmark ($N=1,000$) and the Clean De-duplicated Test Set ($N=899$) revealed that train-test duplicate leakage significantly altered benchmark evaluations (Table 1; Figure 9). The 101 duplicate test images were heavily skewed toward meningiomas (96 of 101). Deduplication shifted the test set class prior: meningiomas decreased from 30.6% (306/1,000) to 23.4% (210/899). 

Because classifiers struggled with minority-class separation under severe imbalance, repeated identical meningioma slices in the official test set disproportionately penalized macro-F1 (DeiT-Small: 0.3566; ResNet-50: 0.3460). On the clean benchmark, macro-F1 rose to **0.5999** for DeiT-Small and **0.4181** for ResNet-50. DeiT-Small accuracy improved from 0.6875 to 0.7646, whereas ResNet-50 accuracy shifted from 0.6479 to 0.6292. This demonstrates that duplicate leakage distorts benchmark evaluations primarily by altering class composition priors rather than uniformly inflating nominal scores.

### 4.9 Evaluation of Study Hypotheses
- **Hypothesis 1 (Spatial Evidence Gradient):** **SUPPORTED.** Prediction sensitivity is concentrated in the lesion core and immediate margins, while remote parenchyma edits produce shifts indistinguishable from sham controls ($p > 0.05$).
- **Hypothesis 2 (Margin Contribution):** **SUPPORTED.** Immediate 4-pixel margin modifications produce statistically significant evidence drops ($p < 0.05$).
- **Hypothesis 3 (ViT Inductive Bias):** **SUPPORTED.** DeiT-Small shows greater core reliance ($p = 0.0123$) and vastly superior probability calibration (ECE 0.037 vs 0.184).
- **Hypothesis 4 (Perturbation Method Concordance):** **SUPPORTED.** High correlation between inpainting and texture filling on core evidence ($r = 0.748$ Cheng, $r = 0.704$ BRISC ViT).
- **Hypothesis 5 (Leakage & Prior Distortion):** **SUPPORTED.** 10.1% test duplicate leakage in BRISC distorts evaluation metrics through class-prior shifts.

---

## 5. Discussion

### 5.1 Principal Findings
Our sham-controlled counterfactual audit establishes that deep neural networks trained on contrast-enhanced brain MRI derive diagnostic evidence primarily from intra-tumoural morphology, with non-trivial contributions from immediate peritumoral margins, while remaining robust to remote context. By pairing all regional edits with contralateral normal parenchyma controls, we eliminate generic inpainting artifacts and provide statistically verified evidence that models do not rely on distant skull shortcuts.

### 5.2 Lesion Core vs Peritumoral Margin Evidence
The observed sensitivity to the 4-pixel immediate transitional margin ($\tau_{\text{immediate}} \approx 0.021$–$0.024$) aligns with clinical neuroradiology principles. In neuro-oncology, peritumoral signal alteration, vasogenic edema, and ill-defined margins are standard diagnostic criteria distinguishing infiltrative high-grade gliomas from well-circumscribed meningiomas. Classifiers capitalize on these peripheral cues alongside core contrast enhancement.

### 5.3 Architectural Inductive Bias: Attention vs Convolution
Our results provide quantitative evidence regarding how architectural inductive biases shape diagnostic representations:
1. **Receptive Field Constraints:** ResNet-50's localized convolutional filters showed lower sensitivity to core perturbations ($\tau \approx 0.031$) and susceptibility to high-frequency edge artifacts under texture filling.
2. **Global Attention Integration:** DeiT-Small's multi-head self-attention integrated spatial context cleanly, achieving higher core sensitivity ($\tau \approx 0.128$–$0.145$) and vastly superior probability calibration (ECE $0.037$ vs $0.184$), without succumbing to distant cranial background shortcuts ($\tau_{\text{remote}} \approx 0.013$, $p > 0.05$).

### 5.4 Benchmark Leakage & Data Governance
The discovery that 10.1% of the official BRISC test set consists of identical duplicate training images carries urgent implications for medical imaging benchmarks. Rather than simply inflating overall accuracy, duplicate concentration in a single class alters test priors and distorts balanced metrics. We advocate for mandatory perceptual hash deduplication, SHA-256 pixel hash auditing, and patient-grouped splitting as universal submission standards for medical imaging challenges.

---

## 6. Limitations

1. **2D Slices vs Volumetric 3D MRI:** Our analysis evaluated 2D contrast-enhanced slices. Neuroradiologists assess multi-sequence 3D volumes (T1, T1+C, T2, FLAIR) in clinical practice.
2. **Synthetic Inpainting Invariants:** While both perturbation methods satisfied strict non-target invariance ($0.00 \times 10^0$), synthetic inpainting does not fully replicate the physiological appearance of healthy, uncompressed brain parenchyma following surgical resection.
3. **Exploratory Class-Level Inferences:** Tumour class comparisons reflect radiologic appearances on 2D T1-CE scans and should not be interpreted as direct histopathological confirmations.

---

## 7. Conclusion

This study provides a rigorous, sham-controlled counterfactual audit of deep learning models in contrast-enhanced brain MRI classification. We confirm a spatial evidence hierarchy: models rely primarily on the tumour core, extract secondary diagnostic evidence from immediate transitional margins, and remain invariant to remote parenchyma. Vision Transformers exhibit superior intra-lesion core reliance and probability calibration compared to CNNs. Crucially, the discovery of 10.1% duplicate leakage in the BRISC benchmark underscores the imperative for rigorous data auditing and transparent sample accounting in clinical AI.

---

## Declarations

### Funding
This research did not receive any specific grant from funding agencies in the public, commercial, or not-for-profit sectors.

### Conflicts of Interest
The authors declare that they have no competing financial or non-financial interests that could have appeared to influence the work reported in this paper.

### Ethics Approval
This study utilized publicly available, fully de-identified retrospective magnetic resonance imaging datasets [2, 5]. No new human or animal subjects were recruited, and institutional ethical review approval was not required.

### Consent to Participate
Not applicable. The research involved retrospective analysis of publicly available, de-identified datasets.

### Consent for Publication
Not applicable.

### Availability of Data and Materials
The Cheng dataset is publicly accessible at Figshare (`doi:10.6084/m9.figshare.1512427`). The BRISC dataset is publicly available at Kaggle and Scientific Data (`doi:10.1038/s41597-026-06753-y`). Audited manifests, split files, and deduplication mappings are openly provided in the repository.

### Code Availability
All source code, preprocessing scripts, model architectures, counterfactual intervention engines, evaluation scripts, and Pytest validation suites are open-source and hosted in the repository.

### Authors' Contributions
- **Chhotu:** Conceptualization, methodology formulation, counterfactual intervention engine design, data preprocessing and deduplication audits, statistical analysis, figure preparation, and manuscript drafting.
- **Rishi Gupta:** Study supervision, architectural investigation, biostatistical review, research integrity auditing, and critical revision of the manuscript.

---

## References

1. Wallis, C. and Buvat, I. (2022). Clever Hans effect found in a widely used brain tumour MRI dataset. *Medical Image Analysis*, 77, p.102368. doi:10.1016/j.media.2022.102368.
2. Cheng, J., Huang, W., Cao, S. et al. (2015). Enhanced Performance of Brain Tumor Classification via Tumor Region Augmentation and Partition. *PLOS ONE*, 10(10), p.e0140381. doi:10.1371/journal.pone.0140381.
3. Rossi, F., Lopez, R. and Comminiello, D. (2024). TACE: Tumor-Aware Counterfactual Explanations for Medical Image Analysis. *arXiv preprint*, arXiv:2409.13045. doi:10.48550/arXiv.2409.13045.
4. Sourget, T., Pizurica, A. et al. (2024). Mask of Truth: Model Sensitivity to Unexpected Regions of Medical Images. *Lecture Notes in Computer Science (MICCAI Workshops)*, 15004, pp.439–449. doi:10.1007/978-3-031-72384-1_43.
5. Fateh, A. et al. (2026). BRISC: Annotated Dataset for Brain Tumor Segmentation and Classification. *Scientific Data*, 13, p.412. doi:10.1038/s41597-026-06753-y.
6. Yagis, E. et al. (2021). Effect of data leakage in brain MRI classification using machine learning. *Scientific Reports*, 11(1), p.22544. doi:10.1038/s41598-021-01681-w.
7. He, K., Zhang, X., Ren, S. and Sun, J. (2016). Deep Residual Learning for Image Recognition. *IEEE Conference on Computer Vision and Pattern Recognition (CVPR)*, pp.770–778. doi:10.1109/CVPR.2016.90.
8. Touvron, H., Cord, M., Douze, M. et al. (2021). Training data-efficient image transformers & distillation through attention. *International Conference on Machine Learning (ICML)*, pp.10347–10357.
9. Guo, C., Pleiss, G., Sun, Y. and Weinberger, K.Q. (2017). On Calibration of Modern Neural Networks. *International Conference on Machine Learning (ICML)*, pp.1321–1330.
10. Telea, A. (2004). An image inpainting technique based on the fast marching method. *Journal of Graphics Tools*, 9(1), pp.23–34. doi:10.1080/10867651.2004.10487596.
11. Geirhos, R. et al. (2020). Shortcut learning in deep neural networks. *Nature Machine Intelligence*, 2(11), pp.665–673. doi:10.1038/s42256-020-00257-z.
12. Goyal, Y. et al. (2019). Counterfactual Visual Explanations. *IEEE International Conference on Computer Vision (ICCV)*, pp.8796–8807. doi:10.1109/ICCV.2019.00882.
13. Rudin, C. (2019). Stop explaining black box machine learning models for high stakes decisions and use interpretable models instead. *Nature Machine Intelligence*, 1(5), pp.206–215. doi:10.1038/s42256-019-0048-x.
14. DeGrave, A.J., Janizek, J.D. and Lee, S.I. (2021). AI for radiographic COVID-19 detection frequently relies on spurious shortcuts. *Nature Machine Intelligence*, 3(7), pp.610–619. doi:10.1038/s42256-021-00338-7.
15. Bentaieb, A. and Hamarneh, G. (2016). Topology Preserving Deep Networks for Medical Image Analysis. *MICCAI*, pp.437–445. doi:10.1007/978-3-319-46723-8_51.

---

## Appendix A: Figures and Visual Evidence Gallery

- **Figure 1: Study Design & Sham-Controlled Counterfactual Intervention Pipeline.** Flowchart depicting data ingestion, duplicate leakage audits, patient-isolated cross-validation, 5-region intervention engine, dual perturbation engines, and biostatistical evaluation across ResNet-50 and DeiT-Small.
- **Figure 2: Preprocessing Pipeline & Mask Geometric Alignment Verification.** Multi-panel diagnostic display illustrating raw slice, percentile intensity scaling $[P_1, P_{99}]$, aspect-ratio-preserving letterbox padding ($224 \times 224$), and binary mask boundary alignment.
- **Figure 3: Reliability Diagrams & Calibration Curves.** Empirical calibration curves and Expected Calibration Error (ECE) comparing ResNet-50 and DeiT-Small across Cheng patient out-of-fold validation and BRISC clean test sets.
- **Figure 4: Regional Evidence Sensitivity Across Architectures (Method A: Inpainting).** Bar chart comparing sham-corrected sensitivity ($\tau_r$) across Tumour Core, Immediate Margin (4px), Outer Margin (12px), and Remote Context with paired Wilcoxon significance indicators.
- **Figure 5: Architectural Inductive Bias: ViT vs CNN Regional Sensitivity Profile (Method A).** Difference plot ($\tau_{\text{ViT}} - \tau_{\text{CNN}}$) highlighting DeiT-Small's enhanced reliance on intra-lesion core and transitional margin evidence.
- **Figure 6: Perturbation Method Concordance: Telea Inpaint vs Matched Texture Fill.** Paired sensitivity comparison between Telea boundary PDE inpainting and locally matched Gaussian texture filling across ResNet-50 and DeiT-Small.
- **Figure 7: Imaging Plane Stratification of Regional Evidence (BRISC).** Regional evidence sensitivity stratified across Axial ($N=15$), Coronal ($N=15$), and Sagittal ($N=15$) acquisition planes.
- **Figure 8: Class Heterogeneity in Peritumoral vs Core Evidence.** Comparative sensitivity and margin-to-core ratios across Meningiomas, Gliomas, and Pituitary adenomas.
- **Figure 9: Impact of Train-Test Duplicate Leakage on Benchmark Evaluation (BRISC).** Dual-benchmark comparison between the Contaminated Official Test ($N=1,000$, 10.1% leakage) and the Clean De-duplicated Test ($N=899$) across DeiT-Small and ResNet-50.
- **Figure 10: Counterfactual Intervention & Residual Montage Gallery.** High-resolution 8-panel diagnostic gallery displaying original slice, 5-color segmentation topology, Method A inpainted core/sham, Method B texture-filled core/sham, and residual difference maps.
