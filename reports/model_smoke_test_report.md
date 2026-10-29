# Phase 4 Model Architecture and Smoke Test Report

Date: 2026-10-29 (Asia/Kolkata)  
Reviewers: Multidisciplinary Research Team (Computer-Vision & Deep-Learning Engineer)  
Execution Hardware: CPU

---

## 1. Executive Summary & Architecture Gate Decision

| Model Configuration | Classes | Dataset | Total Parameters | Trainable Parameters | Smoke Loss | Gradient Check | Checkpoint Reload | Status |
|---|---|---|---|---|---|---|---|---|
| **resnet50** | 3 | CHENG | 23,514,179 | 23,514,179 | 1.0537 | Mean: 0.6004 | Bitwise Invariant | **PASS** |
| **resnet50** | 4 | BRISC | 23,516,228 | 23,516,228 | 1.3345 | Mean: 0.4947 | Bitwise Invariant | **PASS** |
| **deit_small_patch16_224** | 3 | CHENG | 21,666,819 | 21,666,819 | 0.6315 | Mean: 1.0358 | Bitwise Invariant | **PASS** |
| **deit_small_patch16_224** | 4 | BRISC | 21,667,204 | 21,667,204 | 2.1541 | Mean: 1.7222 | Bitwise Invariant | **PASS** |

**Phase 4 Gate Decision: GO**  
Both Model A (ResNet-50) and Model B (DeiT-Small/16) have been verified end-to-end:
1. Real preprocessed brain MRI batches (224 x 224 x 3) flow through both architectures without shape, channel, or numerical exceptions.
2. Backpropagation computes valid, finite, non-zero gradient norms across all convolutional and self-attention layers.
3. Checkpoint serialization and deserialization preserve exact evaluation logits.
4. Classification metrics, expected calibration error (ECE), and Brier score calculators operate without defects.

---

## 2. Model Specifications & Checkpoint Provenance

### 2.1 Model A: ResNet-50
- **Implementation:** `torchvision.models.resnet50`
- **Pretrained Weights:** `ResNet50_Weights.IMAGENET1K_V2` (80.858% ImageNet Top-1)
- **Feature Dimensionality:** 2,048
- **Classification Head:** Linear layer with optional dropout ($p=0.2$) adapted to target classes ($K=3$ for Cheng, $K=4$ for BRISC).
- **Parameters:** ~23.5 million parameters.

### 2.2 Model B: DeiT-Small/16 (Vision Transformer)
- **Implementation:** `timm.create_model('deit_small_patch16_224')`
- **Pretrained Weights:** `deit_small_patch16_224.fb_in1k` (Data-efficient ImageNet-1k)
- **Patch Resolution:** 16 x 16 patches (196 visual tokens + 1 class token)
- **Embedding Dimension:** 384
- **Transformer Depth / Heads:** 12 layers, 6 attention heads
- **Classification Head:** Linear projection from class token representation to target classes ($K=3$ for Cheng, $K=4$ for BRISC).
- **Parameters:** ~21.7 million parameters.

---

## 3. Training & Optimization Settings

- **Optimizer:** AdamW (`betas=(0.9, 0.999)`, `eps=1e-8`, `weight_decay=1e-2`)
- **Base Learning Rate:** $1 	imes 10^{-4}$ with 3-epoch linear warmup
- **Scheduler:** Cosine annealing decay to minimum ratio 0.01
- **Loss Function:** Categorical Cross-Entropy Loss
- **Input Dimension:** 224 x 224 x 3 (ImageNet channel normalization)
- **Evaluation Estimand:** Macro-F1 with early stopping on validation split
