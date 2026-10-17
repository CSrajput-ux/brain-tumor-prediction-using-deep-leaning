"""Phase 1.7 — Sensitivity Analysis: Transitive Closure & Regrouped Fold Generation.

Performs transitive closure analysis of cross-fold candidate pairs across SSIM thresholds
[0.80, 0.75, 0.70, 0.60], builds similarity components and combined evaluation groups,
and deterministically assigns indivisible groups to 5 folds using StratifiedGroupKFold.
"""
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
import networkx as nx
from sklearn.model_selection import StratifiedGroupKFold

ROOT = Path(__file__).resolve().parents[1]
SPLITS_CSV = ROOT / "prepared_full_run" / "patient_splits.csv"
REVIEW_CSV = ROOT / "reports" / "duplicate_investigation" / "duplicate_pair_review.csv"
OUTPUT_DIR = ROOT / "experiments" / "phase_1_7"
MANIFEST_DIR = OUTPUT_DIR / "candidate_grouped_manifests"


def run_phase_1_7_pipeline():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Load authoritative samples
    with open(SPLITS_CSV, newline="", encoding="utf-8-sig") as f:
        split_rows = list(csv.DictReader(f))

    samples = {r["sample_id"]: r for r in split_rows}
    all_sample_ids = sorted(list(samples.keys()))
    assert len(all_sample_ids) == 3064, f"Expected 3064 samples, got {len(all_sample_ids)}"

    # 2. Load candidate pairs
    with open(REVIEW_CSV, newline="", encoding="utf-8-sig") as f:
        pair_rows = list(csv.DictReader(f))
    assert len(pair_rows) == 236, f"Expected 236 candidate pairs, got {len(pair_rows)}"

    thresholds = [0.80, 0.75, 0.70, 0.60]
    threshold_data = {}
    membership_table = {s: {"sample_id": s, "patient_id": samples[s]["patient_id"], "class": samples[s]["class"], "original_fold": samples[s]["fold"]} for s in all_sample_ids}
    summary_rows = []

    for t in thresholds:
        t_key = f"{t:.2f}".replace(".", "_")
        # Edge definition: export_ssim >= t
        valid_edges = [
            (p["sample_id_a"], p["sample_id_b"])
            for p in pair_rows
            if float(p["export_ssim"]) >= t
        ]

        # --- A. Candidate Similarity Components ---
        G_sim = nx.Graph()
        G_sim.add_nodes_from(all_sample_ids)
        G_sim.add_edges_from(valid_edges)

        sim_comps_raw = list(nx.connected_components(G_sim))
        # Deterministic sort: by descending size, then lexicographical order of first sample
        sim_comps = sorted(sim_comps_raw, key=lambda c: (-len(c), sorted(list(c))[0]))

        sim_comp_map = {}
        for idx, comp in enumerate(sim_comps, 1):
            comp_id = f"sim_{t_key}_{idx:04d}"
            for s in comp:
                sim_comp_map[s] = comp_id
                membership_table[s][f"sim_comp_{t_key}"] = comp_id

        non_singleton_sim = [c for c in sim_comps if len(c) > 1]
        singleton_sim = [c for c in sim_comps if len(c) == 1]
        samples_in_non_singleton = sum(len(c) for c in non_singleton_sim)

        sim_multi_pid = 0
        sim_multi_fold = 0
        sim_pids_affected = set()
        sim_samples_affected = set()

        for c in non_singleton_sim:
            c_pids = set(samples[s]["patient_id"] for s in c)
            c_folds = set(samples[s]["fold"] for s in c)
            if len(c_pids) > 1:
                sim_multi_pid += 1
            if len(c_folds) > 1:
                sim_multi_fold += 1
            sim_pids_affected.update(c_pids)
            sim_samples_affected.update(c)

        # --- B. Combined Evaluation Groups (Preserving Both PID and Similarity Components) ---
        G_comb = nx.Graph()
        G_comb.add_nodes_from(all_sample_ids)
        G_comb.add_edges_from(valid_edges)

        pid_to_samples = defaultdict(list)
        for s_id, row in samples.items():
            pid_to_samples[row["patient_id"]].append(s_id)
        for pid, s_list in pid_to_samples.items():
            for i in range(len(s_list) - 1):
                G_comb.add_edge(s_list[i], s_list[i + 1])

        comb_comps_raw = list(nx.connected_components(G_comb))
        comb_comps = sorted(comb_comps_raw, key=lambda c: (-len(c), sorted(list(c))[0]))

        comb_comp_map = {}
        for idx, comp in enumerate(comb_comps, 1):
            grp_id = f"comb_{t_key}_{idx:04d}"
            for s in comp:
                comb_comp_map[s] = grp_id
                membership_table[s][f"comb_grp_{t_key}"] = grp_id

        comb_multi_pid = [c for c in comb_comps if len(set(samples[s]["patient_id"] for s in c)) > 1]
        comb_multi_fold = [c for c in comb_comps if len(set(samples[s]["fold"] for s in c)) > 1]
        total_pids_in_comb_multi = sum(len(set(samples[s]["patient_id"] for s in c)) for c in comb_multi_pid)
        total_slices_in_comb_multi = sum(len(c) for c in comb_multi_pid)

        # --- C. StratifiedGroupKFold Fold Assignment ---
        rows_ordered = [samples[s] for s in all_sample_ids]
        labels = [r["class"] for r in rows_ordered]
        groups = [comb_comp_map[r["sample_id"]] for r in rows_ordered]

        sgkf = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)
        fold_assignment = {}
        for fold_no, (_, test_indices) in enumerate(sgkf.split(rows_ordered, labels, groups), 1):
            for idx in test_indices:
                fold_assignment[rows_ordered[idx]["sample_id"]] = f"fold_{fold_no}"

        # Verify no violations
        pid_folds = defaultdict(set)
        for r in rows_ordered:
            pid_folds[r["patient_id"]].add(fold_assignment[r["sample_id"]])
        assert all(len(f) == 1 for f in pid_folds.values()), f"Patient crossing detected at {t}!"

        comp_folds = defaultdict(set)
        for c in comb_comps:
            for s in c:
                comp_folds[comb_comp_map[s]].add(fold_assignment[s])
        assert all(len(f) == 1 for f in comp_folds.values()), f"Component crossing detected at {t}!"

        # Calculate fold metrics
        fold_metrics = defaultdict(lambda: {"total": 0, "classes": Counter(), "patients": set()})
        for r in rows_ordered:
            f = fold_assignment[r["sample_id"]]
            fold_metrics[f]["total"] += 1
            fold_metrics[f]["classes"][r["class"]] += 1
            fold_metrics[f]["patients"].add(r["patient_id"])

        min_class_count = min(
            fold_metrics[f]["classes"][c_name]
            for f in fold_metrics
            for c_name in ["glioma", "meningioma", "pituitary"]
        )
        ge_50_satisfied = (min_class_count >= 50)
        fold_totals = [fold_metrics[f]["total"] for f in sorted(fold_metrics.keys())]
        disparity = max(fold_totals) - min(fold_totals)

        # Save candidate regrouped manifest
        manifest_path = MANIFEST_DIR / f"split_regrouped_ssim_{t_key}.csv"
        with open(manifest_path, "w", newline="", encoding="utf-8-sig") as mf:
            writer = csv.DictWriter(mf, fieldnames=["sample_id", "patient_id", "class", "fold", "sim_comp_id", "combined_group_id"])
            writer.writeheader()
            for r in rows_ordered:
                s = r["sample_id"]
                writer.writerow({
                    "sample_id": s,
                    "patient_id": r["patient_id"],
                    "class": r["class"],
                    "fold": fold_assignment[s],
                    "sim_comp_id": sim_comp_map[s],
                    "combined_group_id": comb_comp_map[s]
                })

        summary_rows.append({
            "threshold": f"{t:.2f}",
            "num_edges": len(valid_edges),
            "num_similarity_components": len(sim_comps),
            "num_singleton_samples": len(singleton_sim),
            "num_non_singleton_components": len(non_singleton_sim),
            "samples_in_non_singleton_components": samples_in_non_singleton,
            "num_components_multi_pid": sim_multi_pid,
            "num_components_multi_fold": sim_multi_fold,
            "total_pids_affected": len(sim_pids_affected),
            "total_samples_affected": len(sim_samples_affected),
            "max_similarity_component_size": len(sim_comps[0]),
            "num_combined_groups": len(comb_comps),
            "num_combined_multi_pid": len(comb_multi_pid),
            "num_combined_multi_fold": len(comb_multi_fold),
            "total_pids_in_combined_multi": total_pids_in_comb_multi,
            "total_slices_in_combined_multi": total_slices_in_comb_multi,
            "max_combined_group_size": len(comb_comps[0]),
            "min_class_count_across_folds": min_class_count,
            "five_fold_ge_50_satisfied": ge_50_satisfied,
            "max_fold_size_disparity": disparity,
            "fold_1_samples": fold_metrics["fold_1"]["total"],
            "fold_2_samples": fold_metrics["fold_2"]["total"],
            "fold_3_samples": fold_metrics["fold_3"]["total"],
            "fold_4_samples": fold_metrics["fold_4"]["total"],
            "fold_5_samples": fold_metrics["fold_5"]["total"]
        })

        threshold_data[t_key] = {
            "threshold": t,
            "edges": len(valid_edges),
            "sim_comps": sim_comps,
            "comb_comps": comb_comps,
            "fold_metrics": {k: {"total": v["total"], "classes": dict(v["classes"]), "pts": len(v["patients"])} for k, v in fold_metrics.items()}
        }

    # Write summary CSV
    summary_csv = OUTPUT_DIR / "component_summary_by_threshold.csv"
    with open(summary_csv, "w", newline="", encoding="utf-8-sig") as sf:
        writer = csv.DictWriter(sf, fieldnames=list(summary_rows[0].keys()))
        writer.writeheader()
        writer.writerows(summary_rows)

    # Write membership CSV
    membership_csv = OUTPUT_DIR / "component_membership.csv"
    membership_fields = [
        "sample_id", "patient_id", "class", "original_fold",
        "sim_comp_0_80", "comb_grp_0_80",
        "sim_comp_0_75", "comb_grp_0_75",
        "sim_comp_0_70", "comb_grp_0_70",
        "sim_comp_0_60", "comb_grp_0_60"
    ]
    with open(membership_csv, "w", newline="", encoding="utf-8-sig") as mf:
        writer = csv.DictWriter(mf, fieldnames=membership_fields)
        writer.writeheader()
        for s in all_sample_ids:
            writer.writerow(membership_table[s])

    print("Phase 1.7 pipeline executed successfully.")
    return threshold_data, summary_rows


if __name__ == "__main__":
    run_phase_1_7_pipeline()
