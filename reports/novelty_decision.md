# Phase 0 novelty decision

Date: 2026-10-29 (Asia/Kolkata)

## Decision: GO, with a narrowed non-priority claim

The project may proceed as a reproducible model-behaviour audit, subject to data-integrity gates. It must **not** claim to be the first study of tumour context, region masking, or tumour-aware counterfactual explanations.

The literature audit identifies overlapping precedents: Cheng et al. use dilated/ring tumour regions for classification; Wallis & Buvat show that non-tumour cues can drive classification on the Cheng collection; TACE generates ROI-restricted tumour-aware counterfactuals; and Mask of Truth studies models after clinically relevant ROI masking. The resulting distinct, testable protocol is the combined use of:

1. fixed annotation-derived core, immediate-margin, outer-margin and remote non-lesion regions;
2. same-edit, area/shape-recorded matched sham controls and the prespecified sham-corrected estimand;
3. two reproducible non-generative edit methods, retained as sensitivity analyses rather than realism claims;
4. paired ResNet-50 and DeiT-Small/16 test-image comparisons;
5. Cheng patient-grouped out-of-fold evaluation plus official-split BRISC analysis; and
6. a documented within- and cross-release duplicate audit before interpreting replication.

This is a design-level distinction, not a verified novelty claim. The final manuscript will describe it as a region-resolved, sham-controlled audit and will cite the prior work above. If the duplicate/split audit or mask-alignment validation fails, the relevant experiment will remain incomplete rather than be re-framed as a completed replication.
