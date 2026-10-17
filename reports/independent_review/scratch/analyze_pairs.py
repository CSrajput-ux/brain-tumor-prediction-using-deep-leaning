"""Analyze pair statistics from the duplicate review CSV."""
import csv
import json
from collections import Counter

rows = []
with open(r'reports\duplicate_investigation\duplicate_pair_review.csv', newline='', encoding='utf-8-sig') as f:
    rows = list(csv.DictReader(f))

# Sort by SSIM descending
rows.sort(key=lambda r: float(r.get('export_ssim', '0')), reverse=True)

# Top 20 pairs
print("=== TOP 20 PAIRS BY SSIM ===")
for r in rows[:20]:
    print(json.dumps({
        'pair_id': r['pair_id'][:60],
        'ssim': float(r['export_ssim']),
        'phash': r['phash_hamming_distance'],
        'pearson': round(float(r.get('stored_pearson_correlation', '0')), 4),
        'pid_a': r['patient_id_a'],
        'pid_b': r['patient_id_b'],
        'class_a': r['class_a'],
        'class_b': r['class_b'],
        'fold_a': r['fold_a'],
        'fold_b': r['fold_b'],
        'src_a': r['source_path_a'].split('\\')[-1],
        'src_b': r['source_path_b'].split('\\')[-1],
        'shape_a': r['original_shape_a'],
        'shape_b': r['original_shape_b'],
        'file_eq': r['source_file_sha256_equal'],
        'arr_eq': r['stored_image_array_equal'],
        'pixel_eq': round(float(r.get('stored_pixel_equal_fraction', '0')), 4),
    }, indent=2))

print("\n=== SUMMARY STATISTICS ===")
ssim_vals = [float(r['export_ssim']) for r in rows]
print(f'Total pairs: {len(rows)}')
print(f'SSIM >= 0.80: {sum(1 for s in ssim_vals if s >= 0.80)}')
print(f'SSIM >= 0.75: {sum(1 for s in ssim_vals if s >= 0.75)}')
print(f'SSIM >= 0.70: {sum(1 for s in ssim_vals if s >= 0.70)}')
print(f'SSIM >= 0.60: {sum(1 for s in ssim_vals if s >= 0.60)}')

phash_counts = Counter(r['phash_hamming_distance'] for r in rows)
print(f'pHash distance counts: {dict(phash_counts)}')

pids = set()
for r in rows:
    pids.add(r['patient_id_a'])
    pids.add(r['patient_id_b'])
print(f'Unique PIDs involved: {len(pids)}')

fold_pairs = Counter((r['fold_a'], r['fold_b']) for r in rows)
print(f'Fold pairs: {dict(fold_pairs)}')

class_pairs = Counter((r['class_a'], r['class_b']) for r in rows)
print(f'Class pairs: {dict(class_pairs)}')

# Pairs where same class
same_class = sum(1 for r in rows if r['class_a'] == r['class_b'])
diff_class = len(rows) - same_class
print(f'Same class: {same_class}, Different class: {diff_class}')

# How many unique samples are involved
sample_ids = set()
for r in rows:
    sample_ids.add(r['sample_id_a'])
    sample_ids.add(r['sample_id_b'])
print(f'Unique sample IDs involved: {len(sample_ids)}')

# Check which PIDs appear most frequently
pid_freq = Counter()
for r in rows:
    pid_freq[r['patient_id_a']] += 1
    pid_freq[r['patient_id_b']] += 1
print(f'\nMost common PIDs in pairs:')
for pid, count in pid_freq.most_common(10):
    print(f'  {pid}: {count} pair appearances')

# For each of top 5 SSIM pairs, show detailed provenance
print("\n=== DETAILED TOP 5 PAIRS ===")
for i, r in enumerate(rows[:5]):
    print(f"\n--- Pair {i+1} ---")
    for key in ['pair_id', 'sample_id_a', 'sample_id_b', 'source_path_a', 'source_path_b',
                'patient_id_a', 'patient_id_b', 'class_a', 'class_b', 'fold_a', 'fold_b',
                'phash_hamming_distance', 'export_ssim', 'stored_pearson_correlation',
                'original_shape_a', 'original_shape_b', 'original_dtype_a', 'original_dtype_b',
                'original_intensity_min_a', 'original_intensity_max_a',
                'original_intensity_min_b', 'original_intensity_max_b',
                'source_file_sha256_equal', 'stored_image_array_equal',
                'stored_pixel_equal_fraction', 'stored_mean_absolute_difference',
                'stored_max_absolute_difference', 'automated_category']:
        print(f'  {key}: {r.get(key, "N/A")}')
