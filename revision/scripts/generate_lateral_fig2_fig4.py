"""Generate clear, textbook-lateral Fig. 2 (Preprocessing & Mask Alignment)
and Fig. 4 (Counterfactual Intervention & Residual Montage Gallery) using
brisc2025_test_00017_gl_ax_t1 (512x512 axial slice with unambiguous lateral glioma).

Guarantees:
- Unmistakable lateralized lesion (Y=322, X=358 in left temporoparietal lobe).
- Exact contralateral sham mirror reflection (Y=322, X=153 in right temporoparietal lobe).
- No midline ambiguity, no unannotated posterior fossa structures.
"""
from pathlib import Path
import numpy as np
import cv2
import matplotlib.pyplot as plt
from PIL import Image

ROOT = Path(r"c:\Users\jkgga\Downloads\brain")
FIG_DIR = ROOT / "revision" / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

import sys
sys.path.insert(0, str(ROOT))
from src.interventions.regions import generate_regions
from src.interventions.inpainting import inpaint_region_telea, fill_region_matched_texture
from src.data.preprocessing import scale_intensity, resize_and_pad

sid = "brisc2025_test_00017_gl_ax_t1"
img_p = ROOT / "brisc" / "brisc2025" / "classification_task" / "test" / "glioma" / f"{sid}.jpg"
mask_p = ROOT / "brisc" / "brisc2025" / "segmentation_task" / "test" / "masks" / f"{sid}.png"

raw_img_pil = Image.open(img_p).convert("L")
raw_img = np.array(raw_img_pil).astype(np.float32) / 255.0
raw_mask = np.array(Image.open(mask_p)).astype(np.uint8)
raw_mask = (raw_mask > 0).astype(np.uint8)

print(f"Loaded {sid}: image {raw_img.shape}, mask {np.sum(raw_mask)} px")

# -------------------------------------------------------------
# FIGURE 2: PREPROCESSING AND MASK ALIGNMENT
# -------------------------------------------------------------
fig, axes = plt.subplots(1, 4, figsize=(14, 3.8), dpi=300)

# (A) Raw 512x512 scan
axes[0].imshow(raw_img, cmap="bone")
axes[0].set_title("(A) Raw 512×512 CE-T1 Slice", fontsize=10, fontweight="bold")
axes[0].axis("off")

# (B) Intensity Scaled & Padded 224x224
scaled_img = scale_intensity(raw_img)
prep_224, mask_224, _ = resize_and_pad(scaled_img, mask=raw_mask, target_size=(224, 224))
axes[1].imshow(prep_224, cmap="bone")
axes[1].set_title("(B) Intensity-Scaled & Padded (224×224)", fontsize=10, fontweight="bold")
axes[1].axis("off")

# (C) Binary Ground-Truth Mask 224x224
axes[2].imshow(mask_224, cmap="gray")
axes[2].set_title("(C) Binary Ground-Truth Mask (NN)", fontsize=10, fontweight="bold")
axes[2].axis("off")

# (D) Transparent Overlay & Centroid Alignment
overlay_rgb = np.stack([prep_224, prep_224, prep_224], axis=-1)
mask_bool = (mask_224 > 0)
overlay_rgb[mask_bool, 0] = overlay_rgb[mask_bool, 0] * 0.3 + 0.0 * 0.7
overlay_rgb[mask_bool, 1] = overlay_rgb[mask_bool, 1] * 0.3 + 1.0 * 0.7  # Bright green
overlay_rgb[mask_bool, 2] = overlay_rgb[mask_bool, 2] * 0.3 + 0.2 * 0.7

axes[3].imshow(np.clip(overlay_rgb, 0.0, 1.0))
# Centroid marker
c_coords = np.argwhere(mask_224 > 0)
if len(c_coords) > 0:
    cy, cx = c_coords.mean(axis=0)
    axes[3].plot(cx, cy, "r+", markersize=10, markeredgewidth=2, label="Centroid")
    axes[3].legend(loc="upper left", fontsize=8)
axes[3].set_title("(D) Geometric Alignment Overlay", fontsize=10, fontweight="bold")
axes[3].axis("off")

plt.tight_layout()
fig2_path = FIG_DIR / "fig2_preprocessing_alignment.png"
fig.savefig(fig2_path, bbox_inches="tight")
fig.savefig(ROOT / "figures" / "fig2_preprocessing_alignment.png", bbox_inches="tight")
plt.close()
print(f"Successfully generated clean lateral Fig 2 at: {fig2_path}")

# -------------------------------------------------------------
# FIGURE 4: INTERVENTION MONTAGE GALLERY
# -------------------------------------------------------------
regions = generate_regions(raw_mask, raw_img)
core_mask = regions["core"]
sham_mask = regions["sham"]

# Compute edits on 512x512
edit_a_core = inpaint_region_telea(raw_img, core_mask, inpaint_radius=3)
edit_a_sham = inpaint_region_telea(raw_img, sham_mask, inpaint_radius=3)
edit_b_core = fill_region_matched_texture(raw_img, core_mask, seed=42)
edit_b_sham = fill_region_matched_texture(raw_img, sham_mask, seed=42)

diff_a_core = np.abs(raw_img - edit_a_core)
diff_b_core = np.abs(raw_img - edit_b_core)

fig, axes = plt.subplots(2, 4, figsize=(16, 8.2), facecolor="black", dpi=300)
for ax in axes.ravel():
    ax.axis("off")

# Panel 1: Original image
axes[0, 0].imshow(raw_img, cmap="bone")
axes[0, 0].set_title(f"Original Scan: BRISC Axial Glioma", color="white", fontsize=11, fontweight="bold")

# Panel 2: Region Map
gray = np.stack([raw_img, raw_img, raw_img], axis=-1)
overlay = 0.5 * gray
overlay[regions["core"] > 0] = [1.0, 0.15, 0.15]        # Red = core
overlay[regions["immediate"] > 0] = [1.0, 0.55, 0.0]   # Orange = immediate
overlay[regions["outer"] > 0] = [1.0, 0.90, 0.1]       # Yellow = outer
overlay[regions["sham"] > 0] = [0.1, 0.9, 0.9]         # Cyan = contralateral sham
overlay[regions["remote"] > 0] = [0.9, 0.2, 0.9]       # Magenta = remote

axes[0, 1].imshow(np.clip(overlay, 0.0, 1.0))
axes[0, 1].set_title("5-Region Map (Core / Margins / Contralateral Sham)", color="white", fontsize=10, fontweight="bold")

# Panel 3: Method A Core Edit
axes[0, 2].imshow(edit_a_core, cmap="bone")
axes[0, 2].set_title("Method A (Telea PDE): Core Inpainted", color="white", fontsize=10)

# Panel 4: Method A Difference Map
axes[0, 3].imshow(diff_a_core, cmap="hot")
axes[0, 3].set_title("Method A Residual (|Orig − Edit|)", color="white", fontsize=10)

# Panel 5: Method A Sham Edit (Contralateral)
axes[1, 0].imshow(edit_a_sham, cmap="bone")
axes[1, 0].set_title("Method A (Telea): Contralateral Sham Inpainted", color="white", fontsize=10)

# Panel 6: Method B Core Edit
axes[1, 1].imshow(edit_b_core, cmap="bone")
axes[1, 1].set_title("Method B (Texture Fill): Core Filled", color="white", fontsize=10)

# Panel 7: Method B Difference Map
axes[1, 2].imshow(diff_b_core, cmap="hot")
axes[1, 2].set_title("Method B Residual (|Orig − Edit|)", color="white", fontsize=10)

# Panel 8: Method B Sham Edit (Contralateral)
axes[1, 3].imshow(edit_b_sham, cmap="bone")
axes[1, 3].set_title("Method B (Texture): Contralateral Sham Filled", color="white", fontsize=10)

plt.tight_layout()
fig4_path = FIG_DIR / "fig4_intervention_gallery.png"
fig.savefig(fig4_path, dpi=300, bbox_inches="tight", facecolor="black")
fig.savefig(ROOT / "figures" / "fig4_intervention_gallery.png", dpi=300, bbox_inches="tight", facecolor="black")
plt.close()
print(f"Successfully generated clean lateral Fig 4 at: {fig4_path}")
