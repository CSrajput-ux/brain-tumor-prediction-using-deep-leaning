"""
Phase 9 Development Script: Test and compare candidate implementations for C1 (Seam-Only) and C2 (Seam-Suppressed).
"""

import os
import cv2
import numpy as np
import pandas as pd
from PIL import Image
import hashlib

ROOT = os.path.abspath(".")
META_PATH = os.path.join(ROOT, "prepared_full_run", "metadata.csv")
meta_df = pd.read_csv(META_PATH)

sample_row = meta_df.iloc[0]
sid = sample_row['sample_id']
img_path = os.path.join(ROOT, "prepared_full_run", sample_row['image_output_path'])
mask_path = os.path.join(ROOT, "prepared_full_run", sample_row['mask_output_path'])

img = np.array(Image.open(img_path).convert('L'))
mask = (np.array(Image.open(mask_path)) > 0).astype(np.uint8)

elem = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (31, 31))
m_dil = cv2.dilate(mask, elem, iterations=1)

patch_size = 16
h, w = img.shape
grid_y, grid_x = h // patch_size, w // patch_size
pure_distant_coords = []
for gy in range(grid_y):
    for gx in range(grid_x):
        y1, y2 = gy * patch_size, (gy + 1) * patch_size
        x1, x2 = gx * patch_size, (gx + 1) * patch_size
        if not np.any(m_dil[y1:y2, x1:x2] > 0):
            pure_distant_coords.append((gy, gx))

# 1. C5LP (Original Phase 6)
sid_hash_int = int(hashlib.sha256(str(sid).encode('utf-8')).hexdigest()[:8], 16)
sample_seed = (42 + sid_hash_int) % (2**32)
rng = np.random.RandomState(sample_seed)
perm = rng.permutation(len(pure_distant_coords))

i_c5lp = img.copy()
distant_patches = [img[gy*patch_size:(gy+1)*patch_size, gx*patch_size:(gx+1)*patch_size].copy() for gy, gx in pure_distant_coords]
for i, (gy, gx) in enumerate(pure_distant_coords):
    i_c5lp[gy*patch_size:(gy+1)*patch_size, gx*patch_size:(gx+1)*patch_size] = distant_patches[perm[i]]

# Measure Sobel energy
def get_sobel(arr):
    gx = cv2.Sobel(arr.astype(np.float32), cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(arr.astype(np.float32), cv2.CV_32F, 0, 1, ksize=3)
    return float(np.mean(np.sqrt(gx**2 + gy**2)))

print(f"C0 Sobel: {get_sobel(img):.2f}")
print(f"C5LP Sobel: {get_sobel(i_c5lp):.2f} (+{(get_sobel(i_c5lp)/get_sobel(img)-1)*100:.1f}%)")

# Test C1: Seam-Only
# Grid line mask in distant context
seam_mask = np.zeros_like(img, dtype=bool)
for gy, gx in pure_distant_coords:
    y1, y2 = gy * patch_size, (gy + 1) * patch_size
    x1, x2 = gx * patch_size, (gx + 1) * patch_size
    # Right border
    if (gy, gx + 1) in pure_distant_coords:
        seam_mask[y1:y2, x2-1:x2+1] = True
    # Bottom border
    if (gy + 1, gx) in pure_distant_coords:
        seam_mask[y2-1:y2+1, x1:x2] = True

# Never touch protected zone
seam_mask[m_dil > 0] = False

# Construct C1: take C5LP boundary values along the seam mask
# Specifically: in C5LP, the seam artifact is (i_c5lp - img) at the seam boundary
# If we blend or inject the C5LP seam step:
i_c1 = img.copy()
# Where seam_mask is True, we inject the seam contrast step
# Specifically, we can copy the C5LP pixel values along the 1-pixel border of each tile
i_c1[seam_mask] = i_c5lp[seam_mask]
print(f"C1 (Seam-Only) Sobel: {get_sobel(i_c1):.2f} (+{(get_sobel(i_c1)/get_sobel(img)-1)*100:.1f}%)")
print(f"C1 pixels altered: {np.sum(i_c1 != img)} ({np.sum(i_c1 != img)/(512*512)*100:.2f}%)")
print(f"C1 tumor altered: {np.sum(i_c1[mask > 0] != img[mask > 0])}")
print(f"C1 margin altered: {np.sum(i_c1[m_dil > 0] != img[m_dil > 0])}")

# Test C2: Seam-Suppressed Spatial Rearrangement
# In C5LP, smooth out the seam mask!
# Approach A: Bilateral / Gaussian seam blending on C5LP along the seam mask
# Create seam blend mask: dilate seam_mask by 1-2 pixels
seam_dil = cv2.dilate(seam_mask.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3)))
seam_dil[m_dil > 0] = 0

# Apply Gaussian blur along seam_dil
blurred_c5lp = cv2.GaussianBlur(i_c5lp, (5, 5), sigmaX=1.2)
i_c2_blend = i_c5lp.copy()
# Alpha blend along seam
i_c2_blend[seam_dil > 0] = blurred_c5lp[seam_dil > 0]
print(f"C2 (Gaussian Seam Blend) Sobel: {get_sobel(i_c2_blend):.2f} (+{(get_sobel(i_c2_blend)/get_sobel(img)-1)*100:.1f}%)")

# Approach B: Navier-Stokes inpainting along 2-px seam grid
i_c2_inpaint = cv2.inpaint(i_c5lp, seam_dil, inpaintRadius=2, flags=cv2.INPAINT_NS)
i_c2_inpaint[m_dil > 0] = img[m_dil > 0]
print(f"C2 (Navier-Stokes Seam Inpaint) Sobel: {get_sobel(i_c2_inpaint):.2f} (+{(get_sobel(i_c2_inpaint)/get_sobel(img)-1)*100:.1f}%)")

# Approach C: Bilateral filter along seam (preserves internal texture while smoothing step edges)
bilat = cv2.bilateralFilter(i_c5lp, d=5, sigmaColor=50, sigmaSpace=5)
i_c2_bilat = i_c5lp.copy()
i_c2_bilat[seam_dil > 0] = bilat[seam_dil > 0]
i_c2_bilat[m_dil > 0] = img[m_dil > 0]
print(f"C2 (Bilateral Seam Blend) Sobel: {get_sobel(i_c2_bilat):.2f} (+{(get_sobel(i_c2_bilat)/get_sobel(img)-1)*100:.1f}%)")
