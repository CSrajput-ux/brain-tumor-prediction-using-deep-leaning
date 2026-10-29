# Study Specification: Brain MRI Counterfactual Audit

**Study Title:** *Tumour-Core, Peritumoral-Margin, and Remote-Context Evidence in Brain MRI Classification: A Sham-Controlled, Plane-Stratified Counterfactual Audit Across CNN and Vision Transformer Models*  
**Authorship (per reference draft):** Chhotu$^1$ and Rishi Gupta$^2$  
**Affiliation:** $^1$Manipal University Jaipur, Jaipur, Rajasthan, India; $^2$Department of Computer Science & Engineering, School of Computer Science and Engineering, Faculty of Science, Technology and Education, Manipal University Jaipur, Jaipur, Rajasthan, India  
**Target Venue:** *Medical Image Analysis* (MedIA) / *IEEE Transactions on Medical Imaging* (TMI)  
**Reference Template:** [`paper/Brain_MRI_Paper_Final_Corrected_v6.docx`](file:///c:/Users/jkgga/Downloads/brain/paper/Brain_MRI_Paper_Final_Corrected_v6.docx)  

---

## 1. Primary Research Question & Objectives

- **Primary Question:** In deep convolutional and transformer-based classifiers trained on contrast-enhanced brain MRI, does diagnostic evidence originate predominantly from genuine intra-lesional tumour morphology, transitional peritumoral boundary zones, or remote cranial background shortcuts ("Clever Hans" effect)?
- **Secondary Questions:**
  1. *Architectural Inductive Bias:* How do localized convolutional representations (ResNet-50) compare against global self-attention representations (DeiT-Small/16) in spatial evidence reliance and probability calibration?
  2. *Intervention Method Invariance:* Do causal sensitivity measurements generalize across distinct inpainting algorithms (boundary PDE inpainting vs locally matched Gaussian texture fill)?
  3. *Acquisition Plane Stratification:* Is the regional evidence gradient ($\tau_{\text{core}} > \tau_{\text{immediate}} > \tau_{\text{outer}} \gg \tau_{\text{remote}}$) preserved across orthogonal radiological planes (Axial, Coronal, Sagittal)?
  4. *Biological Heterogeneity:* Do sensitivity profiles reflect histopathological characteristics (e.g. infiltrative margins in gliomas vs circumscribed margins in meningiomas and sellar-confined adenomas)?
  5. *Benchmark Leakage Impact:* What is the true generalization impact of identical duplicate slices crossing train-test splits in public benchmarks (e.g. BRISC)?

---

## 2. Research Hypotheses

- **Hypothesis 1 (Primary - Spatial Evidence Decay):** Model sensitivity decays monotonically as counterfactual edits move outward from the primary neoplasm: $\tau_{\text{core}} > \tau_{\text{immediate}} > \tau_{\text{outer}} > \tau_{\text{remote}}$, with $\tau_{\text{remote}}$ showing no statistically significant departure from zero ($p > 0.05$).
- **Hypothesis 2 (Peritumoral Marginal Contribution):** Immediate transitional margins ($R_{\text{immediate}}$, 4-pixel perimeter ring) provide statistically significant diagnostic evidence ($\tau_{\text{immediate}} > 0, p < 0.05$).
- **Hypothesis 3 (ViT vs CNN Inductive Bias):** Vision Transformers (DeiT-Small) exhibit greater core feature reliance and superior probability calibration compared to CNNs (ResNet-50).
- **Hypothesis 4 (Method Invariance):** Relative regional rankings and core sensitivities exhibit significant positive correlation ($r > 0.5, p < 0.01$) across Telea boundary PDE inpainting and Gaussian texture synthesis.
- **Hypothesis 5 (Benchmark Leakage Distortion):** Official test duplicate leakage in BRISC ($10.1\%$) distorts class-balanced evaluation metrics by inflating meningioma performance.

---

## 3. Dataset Specifications & Sample Flow

| Dataset | Modality & Description | Total Available | Partitioning & Leakage Control | Evaluated Samples |
|:---|:---|:---:|:---|:---:|
| **Cheng et al. (2015)** | T1-weighted contrast-enhanced brain MRI (233 patients; Meningioma: 708, Glioma: 1,426, Pituitary: 930) | 3,064 slices | 5-fold cross-validation strictly grouped by patient ID (`patient_id`); **0 patient overlap** across folds | $N=480$ out-of-fold slices in Fold 1 test partition |
| **BRISC (Fateh et al., 2026)** | Multi-plane contrast-enhanced brain MRI (4 classes: Glioma, Meningioma, Pituitary, No-Tumour; Axial, Coronal, Sagittal) | 6,000 slices | Official Benchmark ($5,000$ train / $1,000$ test). Deduplication audit isolated 101 leaked test duplicates $\to$ **BRISC Clean Test Set** ($N=899$) | $N=480$ test slices; $N=45$ plane-stratified audit slices ($15$ Axial, $15$ Coronal, $15$ Sagittal) |

---

## 4. Model Architectures & Training Protocols

- **ResNet-50 (CNN):** 23.51 million parameters; initialized with torchvision `IMAGENET1K_V2` pretrained weights; custom Linear classification head; Dropout $p=0.2$.
- **DeiT-Small/16 (ViT):** 21.66 million parameters; initialized with `timm` ImageNet-1k pretrained weights; 12 Transformer blocks, 384 hidden dim, 6 attention heads; class token projection head.
- **Optimization:** AdamW ($\text{weight decay} = 10^{-2}$), initial learning rate $10^{-4}$, linear warmup (2 epochs), cosine annealing schedule; cross-entropy loss.
- **Input Dimensions:** Standardized $224 \times 224 \times 3$ via robust intensity scaling $[P_1, P_{99}]$ and aspect-ratio-preserving letterbox padding.

---

## 5. Counterfactual Intervention Engine

- **5 Anatomical Regions:**
  1. $R_{\text{core}}$: Lesion core segmentation mask $M$.
  2. $R_{\text{immediate}}$: Dilation $(M \oplus K_4 \setminus M) \cap S$ (4-pixel margin).
  3. $R_{\text{outer}}$: Dilation $(M \oplus K_{16} \setminus (M \oplus K_4)) \cap S$ (12-pixel margin).
  4. $R_{\text{remote}}$: Non-lesion tissue patch $> 32$ pixels away from lesion boundary within tissue support $S$.
  5. $R_{\text{sham}}$: Area- and contour-matched contralateral normal parenchyma control ($R_{\text{sham}} \cap (R_{\text{core}} \cup R_{\text{margin}}) = \emptyset$).
- **Dual Perturbation Methods:**
  - **Method A (Telea PDE Inpainting):** FMM boundary PDE reconstruction (`cv2.INPAINT_TELEA`, radius 3 px).
  - **Method B (Locally Matched Gaussian Texture Fill):** Normal distribution $\mathcal{N}(\mu_{\text{local}}, \sigma_{\text{local}})$ with 2-pixel cosine border blending.
- **Strict Invariance:** Enforced $x_{\text{edit}}(u, v) \equiv x(u, v)$ for all non-target pixels ($|\Delta| < 10^{-5}$).

---

## 6. Primary & Secondary Statistical Estimands

- **Raw Evidence Drop:** $\Delta_r(x) = p_y(x) - p_y(x_{\text{edit}, r})$
- **Sham-Corrected Sensitivity:** $\tau_r(x) = \Delta_r(x) - \Delta_{\text{sham}}(x)$
- **Prediction Flip Indicator:** $F_r(x) = \mathbb{I}[\arg\max p(x_{\text{edit}, r}) \ne \arg\max p(x)]$
- **Paired Inference:** Two-sided Wilcoxon signed-rank tests testing $H_0: \Delta_r = \Delta_{\text{sham}}$.
- **Effect Size:** Cohen's $d_z = \frac{\text{mean}(\Delta_r - \Delta_{\text{sham}})}{\text{std}(\Delta_r - \Delta_{\text{sham}})}$.

