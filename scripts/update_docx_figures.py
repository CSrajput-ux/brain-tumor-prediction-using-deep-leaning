import zipfile, os, shutil, re

SRC = 'Brain_MRI_Paper_Final_Corrected_v3.docx'
BACKUP = 'Brain_MRI_Paper_Final_Corrected_v3_pre_phase1.docx'
if not os.path.exists(BACKUP):
    shutil.copyfile(SRC, BACKUP)
    print('Backed up to', BACKUP)

FIG_DIR = 'publication/manuscript_v1/figures'

UPDATES = {
    'word/media/805b69a90c1c9fa72e1473df7b230683b83fedcb.png': os.path.join(FIG_DIR, 'fig5_intervention_macro_f1.png'),
    'word/media/8a948329a61cfdc4ca2f34f51d76175ddc5772b2.png': os.path.join(FIG_DIR, 'fig6_contrast_forest_plot.png'),
    'word/media/a46ce5e5c5230baddc5b0c41df0da8ce5dbf7782.png': os.path.join(FIG_DIR, 'fig7_confusion_matrices.png'),
    'word/media/bc8649cde77f217ecec4eab85a8438c4af12e0d2.png': os.path.join(FIG_DIR, 'fig9_glioma_prior_collapse.png'),
    'word/media/7512c806bb86b98ee0041bbf3b07169c63a9bd9f.png': os.path.join(FIG_DIR, 'fig8_artifact_diagnostics.png'),
    'word/media/5e8edb921f00b52b103e783afc69ae820e41511b.png': os.path.join(FIG_DIR, 'fig10_cross_validation_stability.png'),
}

with zipfile.ZipFile(SRC, 'r') as zin:
    all_files = {}
    for item in zin.infolist():
        if item.filename == 'word/media/fig9_artifact_diagnostics_final.png':
            print('Removing unused duplicate media file:', item.filename)
            continue
        all_files[item.filename] = zin.read(item.filename)

# Clean up rels if rId19 is present
rels = all_files['word/_rels/document.xml.rels'].decode('utf-8')
if 'fig9_artifact_diagnostics_final.png' in rels:
    rels = re.sub(r'<Relationship Id="rId19"[^>]+/>\s*', '', rels)
    all_files['word/_rels/document.xml.rels'] = rels.encode('utf-8')
    print('Removed rId19 relationship from document.xml.rels')

# Replace figure images
for zip_path, file_path in UPDATES.items():
    with open(file_path, 'rb') as f:
        all_files[zip_path] = f.read()
    print(f'Updated {zip_path} with {file_path} ({len(all_files[zip_path])} bytes)')

# Write back
with zipfile.ZipFile(SRC, 'w', compression=zipfile.ZIP_DEFLATED) as zout:
    for filename, data in all_files.items():
        zout.writestr(filename, data)

print('Updated Brain_MRI_Paper_Final_Corrected_v3.docx successfully with new figures!')
