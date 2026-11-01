import pandas as pd

df = pd.read_csv('manifests/cheng_splits.csv')
print("Columns in cheng_splits.csv:", df.columns.tolist())
print("Head:")
print(df.head(2))

label_col = 'label' if 'label' in df.columns else ('class' if 'class' in df.columns else 'tumor_type')
for col in df.columns:
    if 'class' in col or 'type' in col or 'label' in col:
        label_col = col

print("Using label column:", label_col)
total_p = 0
for f in sorted(df['fold'].unique()):
    sub = df[df['fold'] == f]
    vc = sub[label_col].value_counts().to_dict()
    n_p = sub['patient_id'].nunique()
    total_p += n_p
    print(f"  {f}: {len(sub)} slices ({n_p} patients; {vc})")
print(f"Total unique patients: {df['patient_id'].nunique()}, sum of patients across folds: {total_p}")

df_oof = pd.read_csv('predictions/oof_predictions_resnet50_cheng.csv')
print("Columns in oof_predictions:", df_oof.columns.tolist())
merged = df_oof.merge(df, on='sample_id', how='left')
print(f"OOF predictions: {len(df_oof)} slices, {merged['patient_id'].nunique()} unique patients")
vc_oof = df_oof['true_class'].value_counts().to_dict()
print(f"OOF class distribution: {vc_oof}")
