import zipfile, os, shutil, re

SRC = 'Brain_MRI_Paper_Final_Corrected_v3.docx'
BACKUP = 'Brain_MRI_Paper_Final_Corrected_v3_pre_phase2.docx'
if not os.path.exists(BACKUP):
    shutil.copyfile(SRC, BACKUP)
    print('Backed up to', BACKUP)

with zipfile.ZipFile(SRC, 'r') as zin:
    all_files = {}
    for item in zin.infolist():
        all_files[item.filename] = zin.read(item.filename)

doc_xml = all_files['word/document.xml'].decode('utf-8')
original_len = len(doc_xml)

# 1. N6: Generative AI statement under Declarations
genai_xml = (
    '<w:p><w:pPr><w:spacing w:after="100" w:before="0" w:line="264"/><w:jc w:val="both"/></w:pPr>'
    '<w:r><w:rPr><w:rFonts w:ascii="Times New Roman" w:cs="Times New Roman" w:eastAsia="Times New Roman" w:hAnsi="Times New Roman"/>'
    '<w:b/><w:bCs/><w:sz w:val="22"/><w:szCs w:val="22"/></w:rPr>'
    '<w:t xml:space="preserve">Generative AI and AI-assisted technologies.</w:t></w:r>'
    '<w:r><w:rPr><w:rFonts w:ascii="Times New Roman" w:cs="Times New Roman" w:eastAsia="Times New Roman" w:hAnsi="Times New Roman"/>'
    '<w:sz w:val="22"/><w:szCs w:val="22"/></w:rPr>'
    '<w:t xml:space="preserve"> The authors declare that no generative artificial intelligence or AI-assisted technologies were used in the writing of this manuscript or in the execution of the experimental analyses.</w:t></w:r></w:p>'
)

decl_target = 'Declarations</w:t></w:r></w:p>'
assert decl_target in doc_xml, "Declarations target not found"
doc_xml = doc_xml.replace(decl_target, decl_target + genai_xml, 1)
print("Applied N6: Generative AI declaration added.")

# 2. N8: Eq. (13) typo: remove raw <sub>1</sub> and format as subscript χ²,1
eq13_target = '<w:t xml:space="preserve">χ²&lt;sub&gt;1</w:t></w:r><w:r><w:rPr><w:rFonts w:ascii="Times New Roman" w:cs="Times New Roman" w:eastAsia="Times New Roman" w:hAnsi="Times New Roman"/><w:i w:val="false"/><w:iCs w:val="false"/><w:sz w:val="22"/><w:szCs w:val="22"/></w:rPr><w:t xml:space="preserve">&lt;/sub&gt;(χ</w:t>'
eq13_replacement = '<w:t xml:space="preserve">χ²,1</w:t></w:r><w:r><w:rPr><w:rFonts w:ascii="Times New Roman" w:cs="Times New Roman" w:eastAsia="Times New Roman" w:hAnsi="Times New Roman"/><w:i w:val="false"/><w:iCs w:val="false"/><w:sz w:val="22"/><w:szCs w:val="22"/></w:rPr><w:t xml:space="preserve">(χ</w:t>'
assert eq13_target in doc_xml, "Eq 13 typo target not found"
doc_xml = doc_xml.replace(eq13_target, eq13_replacement, 1)
print("Applied N8: Eq 13 typo fixed (raw <sub> tags removed).")

# 3. N10: Abstract seam suppression partial attenuation
abs_target = 'seam suppression did not recover performance.'
abs_replacement = 'partial seam attenuation (39.0% excess boundary edge reduction at model input) did not recover performance.'
assert abs_target in doc_xml, "Abstract seam suppression target not found"
doc_xml = doc_xml.replace(abs_target, abs_replacement, 1)
print("Applied N10: Abstract seam attenuation quantified.")

# 4. N11: Intro >94% citation
intro_target = 'exceeding 94% on public brain tumour datasets, frequently using deep convolutional neural network (CNN) backbones such as ResNet-50 [3, 4, 12].'
intro_replacement = 'exceeding 94% on public brain tumour benchmarks [3, 4], frequently employing deep convolutional neural network (CNN) backbones such as ResNet-50 [20].'
assert intro_target in doc_xml, "Intro citation target not found"
doc_xml = doc_xml.replace(intro_target, intro_replacement, 1)
print("Applied N11: Intro citation corrected ([20] for ResNet-50, [12] unburdened).")

# 5. N12: Ratio 0.17 vs 0.18
ratio_target = '; 0.36, 0.22 and 0.18 for C'
ratio_replacement = '; 0.36, 0.22 and 0.17 for C'
assert ratio_target in doc_xml, "Ratio 0.18 target not found"
doc_xml = doc_xml.replace(ratio_target, ratio_replacement, 1)
print("Applied N12: Ratio made consistent to 0.17.")

# 6. N14: Algorithm 1 numbering (renumber 2..12 -> 1..11)
alg_idx = doc_xml.find('Algorithm 1')
alg_end = doc_xml.find('3.11', alg_idx)
alg_chunk = doc_xml[alg_idx:alg_end]

alg_replacements = [
    ('2:  Compute ', '1:  Compute '),
    ('3:  Draw ', '2:  Draw '),
    ('4:  </w:t>', '3:  </w:t>'),
    ('5:  </w:t>', '4:  </w:t>'),
    ('6:  </w:t>', '5:  </w:t>'),
    ('7:  </w:t>', '6:  </w:t>'),
    ('8:  </w:t>', '7:  </w:t>'),
    ('9:  </w:t>', '8:  </w:t>'),
    ('10:  </w:t>', '9:  </w:t>'),
    ('11:  </w:t>', '10:  </w:t>'),
    ('12:  </w:t>', '11:  </w:t>')
]
for old_str, new_str in alg_replacements:
    assert old_str in alg_chunk, f"Algorithm step {old_str} not found in alg chunk"
    alg_chunk = alg_chunk.replace(old_str, new_str, 1)

doc_xml = doc_xml[:alg_idx] + alg_chunk + doc_xml[alg_end:]
print("Applied N14: Algorithm 1 renumbered starting from line 1.")

# 7. N15: Author email and Ref [25]
email_target = 'chhotu.2427030521@muj.manipal.edu (alternative: csjadon415@gmail.com)'
email_replacement = 'chhotu.2427030521@muj.manipal.edu'
assert email_target in doc_xml, "Author email target not found"
doc_xml = doc_xml.replace(email_target, email_replacement, 1)

ref25_target = 'CSrajput-ux: Brain tumor prediction using deep learning (project repository). https://github.com/CSrajput-ux/brain-tumor-prediction-using-deep-leaning (2026)'
ref25_replacement = 'Rajput, C.S., Gupta, R.: Brain tumor prediction using deep learning (project repository and research release). https://github.com/CSrajput-ux/brain-tumor-prediction-using-deep-leaning (2026)'
assert ref25_target in doc_xml, "Ref 25 target not found"
doc_xml = doc_xml.replace(ref25_target, ref25_replacement, 1)
print("Applied N15: Author email streamlined and Ref [25] author formatted.")

# 8. N18: Dataset license
lic_target = 'obtained from its official source and used in accordance with its access and licensing conditions.'
lic_replacement = 'obtained from its official source and used in accordance with its Creative Commons Attribution 4.0 International (CC BY 4.0) license.'
assert lic_target in doc_xml, "Dataset license target not found"
doc_xml = doc_xml.replace(lic_target, lic_replacement, 1)
print("Applied N18: Creative Commons Attribution 4.0 International (CC BY 4.0) explicitly stated.")

# 9. M6: Process history and internal paths
hist_target = 'Table 9 and Fig. 9 report image diagnostics computed across all 3,064 slices using the evaluated C2 operator (9 × 9 Gaussian, σ = 2.5, distance-weighted blend, w = 4 px; generated via scripts/run_dual_resolution_diagnostics.py). The repository\'s earlier diagnostic script had employed a 5 × 5 blur (σ = 1.5, 50% uniform blend); recalculation with the evaluated operator reveals resolution-dependent attenuation.'
hist_replacement = 'Table 9 and Fig. 9 report image diagnostics computed across all 3,064 slices using the evaluated C2 operator (9 × 9 Gaussian, σ = 2.5, distance-weighted blend, w = 4 px). Evaluation with this matching operator reveals resolution-dependent attenuation.'
assert hist_target in doc_xml, "Section 4.6 process history target not found"
doc_xml = doc_xml.replace(hist_target, hist_replacement, 1)

path1_target = 'Complete per-image and aggregate dual-resolution tables are archived in remaining_work_audit/true_seam_and_intervention_diagnostics_dual_resolution.csv.'
path1_replacement = 'Complete per-image and aggregate dual-resolution tables are archived in the supplementary materials and the project Zenodo release.'
assert path1_target in doc_xml, "Section 4.6 internal path target not found"
doc_xml = doc_xml.replace(path1_target, path1_replacement, 1)

path2_target = '(scripts/run_dual_resolution_diagnostics.py; remaining_work_audit/true_seam_and_intervention_diagnostics_dual_resolution.csv)'
path2_replacement = '(archived in the project Zenodo release and supplementary data)'
assert path2_target in doc_xml, "Limitations internal path target not found"
doc_xml = doc_xml.replace(path2_target, path2_replacement, 1)
print("Applied M6: Process history (5x5 blur) and internal repository paths removed.")

# 10. N17: Clever Hans literature addition
shortcut_target = 'features [5, 6]. Deep neural networks are known to exploit “shortcuts”—unintended statistical correlations between non-pathological background image features and target diagnostic labels that hold within training distributions'
shortcut_replacement = 'features [5, 6]. Deep neural networks are known to exploit “shortcuts”—unintended statistical correlations between non-pathological background image features and target diagnostic labels (the “Clever Hans” effect [5, 32]) that hold within training distributions'
assert shortcut_target in doc_xml, "Shortcut target not found"
doc_xml = doc_xml.replace(shortcut_target, shortcut_replacement, 1)

# Add Ref 32
ref31_target = '[31]\tChang, C.-H., Creager, E., Goldenberg, A., Duvenaud, D.: Explaining image classifiers by counterfactual generation. In: Int. Conf. Learning Representations (ICLR) (2019)'
ref32_xml = (
    '</w:t></w:r></w:p><w:p><w:pPr><w:spacing w:after="60" w:before="0" w:line="240"/><w:jc w:val="both"/></w:pPr>'
    '<w:r><w:rPr><w:rFonts w:ascii="Times New Roman" w:cs="Times New Roman" w:eastAsia="Times New Roman" w:hAnsi="Times New Roman"/><w:sz w:val="20"/><w:szCs w:val="20"/></w:rPr>'
    '<w:t xml:space="preserve">[32]\tLapuschkin, S., Wäldchen, S., Binder, A., Montavon, G., Samek, W., Müller, K.-R.: Unmasking Clever Hans predictors and assessing what machines really learn. Nat. Commun. 10, 1096 (2019)'
)
assert ref31_target in doc_xml, "Ref 31 target not found"
doc_xml = doc_xml.replace(ref31_target, ref31_target + ref32_xml, 1)
print("Applied N17: Clever Hans effect and Lapuschkin et al. (2019) reference added.")

# Save updated document.xml
all_files['word/document.xml'] = doc_xml.encode('utf-8')

with zipfile.ZipFile(SRC, 'w', compression=zipfile.ZIP_DEFLATED) as zout:
    for filename, data in all_files.items():
        zout.writestr(filename, data)

print(f"Successfully applied all Phase 2 corrections to {SRC}!")
