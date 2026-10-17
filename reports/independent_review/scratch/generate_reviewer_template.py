"""Generate reviewer_decision_template.csv from the duplicate_pair_review.csv."""
import csv
from pathlib import Path

REVIEW_CSV = Path(r'reports\duplicate_investigation\duplicate_pair_review.csv')
OUTPUT_CSV = Path(r'reports\independent_review\reviewer_decision_template.csv')

with REVIEW_CSV.open(newline='', encoding='utf-8-sig') as f:
    rows = list(csv.DictReader(f))

# Sort by SSIM descending for reviewer convenience
rows.sort(key=lambda r: float(r.get('export_ssim', '0')), reverse=True)

# Assign review priority tiers
def priority_tier(ssim: float) -> str:
    if ssim >= 0.80:
        return 'tier_1_highest'
    elif ssim >= 0.75:
        return 'tier_2_high'
    elif ssim >= 0.70:
        return 'tier_3_moderate'
    elif ssim >= 0.60:
        return 'tier_4_standard'
    else:
        return 'tier_5_low'

output_fields = [
    # Pair identification
    'pair_id',
    'review_priority',
    'review_rank',
    'sample_id_a',
    'sample_id_b',
    'patient_id_a',
    'patient_id_b',
    'class_a',
    'class_b',
    'fold_a',
    'fold_b',
    # Source provenance
    'source_mat_a',
    'source_mat_b',
    'original_shape_a',
    'original_shape_b',
    # Automated evidence summary
    'export_ssim',
    'phash_hamming_distance',
    'stored_pearson_correlation',
    'stored_pixel_equal_fraction',
    'source_file_sha256_equal',
    'stored_image_array_equal',
    'intensity_range_a',
    'intensity_range_b',
    # Contact sheet reference
    'contact_sheet_reference',
    # Human reviewer fields (BLANK — to be filled by reviewer)
    'reviewer_id',
    'review_date',
    'review_decision',
    'evidence_notes',
    'confidence',
    'follow_up_required',
]

output_rows = []
for rank, r in enumerate(rows, 1):
    ssim = float(r.get('export_ssim', '0'))
    src_a = r['source_path_a'].replace('\\', '/').split('/')[-1]
    src_b = r['source_path_b'].replace('\\', '/').split('/')[-1]
    
    # Determine contact sheet group
    if ssim >= 0.80:
        cs_group = 'ssim_ge_0_80'
    elif ssim >= 0.70:
        cs_group = 'ssim_0_70_to_0_80'
    else:
        cs_group = 'ssim_lt_0_70'
    
    output_rows.append({
        'pair_id': r['pair_id'],
        'review_priority': priority_tier(ssim),
        'review_rank': rank,
        'sample_id_a': r['sample_id_a'],
        'sample_id_b': r['sample_id_b'],
        'patient_id_a': r['patient_id_a'],
        'patient_id_b': r['patient_id_b'],
        'class_a': r['class_a'],
        'class_b': r['class_b'],
        'fold_a': r['fold_a'],
        'fold_b': r['fold_b'],
        'source_mat_a': src_a,
        'source_mat_b': src_b,
        'original_shape_a': r['original_shape_a'],
        'original_shape_b': r['original_shape_b'],
        'export_ssim': f'{ssim:.6f}',
        'phash_hamming_distance': r['phash_hamming_distance'],
        'stored_pearson_correlation': r.get('stored_pearson_correlation', ''),
        'stored_pixel_equal_fraction': r.get('stored_pixel_equal_fraction', ''),
        'source_file_sha256_equal': r['source_file_sha256_equal'],
        'stored_image_array_equal': r['stored_image_array_equal'],
        'intensity_range_a': f"[{r['original_intensity_min_a']}, {r['original_intensity_max_a']}]",
        'intensity_range_b': f"[{r['original_intensity_min_b']}, {r['original_intensity_max_b']}]",
        'contact_sheet_reference': f'See {cs_group}_page_*.png',
        # Human fields — intentionally blank
        'reviewer_id': '',
        'review_date': '',
        'review_decision': '',
        'evidence_notes': '',
        'confidence': '',
        'follow_up_required': '',
    })

OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
with OUTPUT_CSV.open('w', newline='', encoding='utf-8-sig') as f:
    writer = csv.DictWriter(f, fieldnames=output_fields)
    writer.writeheader()
    writer.writerows(output_rows)

print(f'Created {OUTPUT_CSV} with {len(output_rows)} rows')
print(f'Priority distribution:')
from collections import Counter
tiers = Counter(r['review_priority'] for r in output_rows)
for tier in sorted(tiers):
    print(f'  {tier}: {tiers[tier]}')
