# SABER: saliency validation, recovery and normalisation in pruned IoT intrusion detectors

This repository holds the protocols, notebooks and results for the manuscript

**Saliency Validation Does Not Certify Deployment: Recovery and a Silent Batch-Normalisation Failure in Pruned IoT Intrusion Detectors**

Every result reported in the manuscript is present at commit `06b3cbd` and later commits. The plan commit and results commit of each notebook are listed in the manuscript's Appendix A; each listed hash opens the commit on GitHub.

## History

This repository was split from [iot-trust-compression](https://github.com/anasbiswas1/iot-trust-compression) (branch `saber-ids-method`, head `e4ea5af`) with its complete commit history, so every commit hash in the manuscript's pre-registration ledger resolves here as well as in the original repository. The files of the earlier diagnostic study were removed from the current tree; they remain in this history at commit `4c85cdf` and in the original repository.

## Data

- **CICIoT2023** (Canadian Institute for Cybersecurity). The frozen stratified split (2,563,172 / 549,253 / 549,271 rows), the train-fitted standard scaler (no clipping) and the shallow CNN baseline are reused from the earlier diagnostic study and are pinned at commit `4c85cdf`, which is part of this repository's history. `src/saber/bridge_ciciot.py` rebuilds them.
- **CIC-IoMT-2024** (Canadian Institute for Cybersecurity, WiFi/MQTT subset), loaded through the data loader of the `iomt-compression-research` repository by `src/saber/bridge_iomt.py`. Only the official training side is opened; exact duplicates are removed; a 20% validation partition is carved out stratified by attack type; clipping bounds (0.1 and 99.9 percentiles) and standardisation are fitted on the remaining training rows. The official test files are never opened.

Raw data are not stored in this repository.

## Run order

Run the notebooks in numeric order: 14, 15, 16, 16b, 17, 17b, 18, 19, 20, 20b, 21, 22, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39. Each writes only to its own folder under `results/saber/`.

- Notebook 21 is the one-shot test audit. It was run once and is permanently locked; it must not be rerun or used for any selection.
- Notebook 23 was never run. Notebook 24 is an exploratory single run from which no claim is drawn. Notebook 25 is a figure notebook from an earlier draft.
- The results of notebook 26 are in `results/saber/25_recovery_seed_factorial/`.
- The results of notebook 31 are in `results/saber/31_consistent_normalisation/`; its pre-registration was committed under its earlier number in `results/saber/36_consistent_normalisation/`.

## Where each manuscript result comes from

| Manuscript item | Notebook(s) | Folder(s) under `results/saber/` |
|---|---|---|
| Section 3.2, vulnerability graph and cost profiles | 14 | `14_risk_graph` |
| Table 1 | 16, 16b, 20, 33 | `16_score_validation`, `16b_score_v2`, `20_depth_probe`, `33_iomt_scores_structures` |
| Figure 2 | 33 | `33_iomt_scores_structures` |
| Section 4.2, budget overshoot | 17 | `17_structured_selection` |
| Figure 3, calibrated structures | 17b | `17b_calibrated_checkpoint_freeze` |
| Table 2, Figure 4 | 36 | `36_hardware_proxy` |
| Figure 5 | 19, 26 | `19_recovery_regimes`, `25_recovery_seed_factorial` |
| Table 3 | 26, 29, 31, 34, 37, 38 | `25_recovery_seed_factorial`, `29_competent_teacher_arm`, `31_consistent_normalisation`, `34_iomt_factorial`, `37_audit_followups`, `38_capacity_duplicates_iomt20` |
| Table 4, Figure 6 | 37, 38 | `37_audit_followups`, `38_capacity_duplicates_iomt20` |
| Table 5 | 16, 16b, 20, 33, 34, 37, 38 | the folders of Tables 1 and 4, and `34_iomt_factorial` |
| Table 6, Figure 7 | 34 | `34_iomt_factorial` |
| IoMT data bridge, teachers and graph | 32 | `32_iomt_bridge` |
| Table 7, Figure 8 | 28 | `28_collapse_diagnosis` |
| Figure 9 | 31 | `31_consistent_normalisation` |
| Table 8, Figure 10 | 35 | `35_trigger_isolation` |
| Table 9, Figure 11 | 30 | `30_remedy_and_trigger` |
| Section 4.5, Table S1 (Supplementary Materials), Figure 12 | 21 | `21_one_shot_test` |
| Section 4.5, duplicate audit | 38 | `38_capacity_duplicates_iomt20` |
| Figure 13 | 37 | `37_audit_followups` |
| Table B.1 | 16b, 20 | `16b_score_v2`, `20_depth_probe`, `postg5_offline_audit` |
| Text S1 (Supplementary Materials), recovery objective | 18 | `18_hierarchical_distillation` |
| Text S1 (Supplementary Materials), set-level benchmark | 22 | `22_set_interaction` |
| Table C.1 | 20b, 37, 38 | `20b_depth_checkpoint_freeze`, `37_audit_followups`, `38_capacity_duplicates_iomt20` |
| Table S2 (Supplementary Materials) | 27 | `27_recovery_efficiency` |
| Table C.2, Figure C.1 | 39, 37 | `39_endpoint_prevention_allocation`, `37_audit_followups` |
| Table S3 (Supplementary Materials) | 20, 38 | `20_depth_probe`, `38_capacity_duplicates_iomt20` |

**Calibration slice.** Every recalibration in notebooks 31, 34, 37, 38 and 39 uses one common slice: the first 51,200 rows of a permutation of the training rows drawn with seed 2026. The remedy experiment in notebook 30 (Table 9 and Figure 11) instead uses, for each run, the 51,200 rows that follow that run's recovery subset in its own seeded permutation, so they are disjoint from the recovery subset and differ between seeds. No row-index file was saved for either slice; both are recomputed from the seed and the training-set size.

The REI on ground-truth risk in Table 3, the endpoint-matched correlations of Table 5 and Table C.2 and Table S3 are summary statistics computed from the run-level files in these folders after the notebooks ran.

## Environment

All notebooks were run in Python on Google Colab with PyTorch, NumPy, pandas, SciPy and scikit-learn (see `requirements.txt`). Package versions were those of the Colab runtime on each run date and were not pinned per notebook; the hardware measurement of notebook 36 used PyTorch 2.11.0 on a single CPU thread. A current environment built from `requirements.txt` is not guaranteed to match those historical runtimes exactly.

## Committing

All commits go through `tools/commit_cell.py`, which restores the git identity from the Drive project folder, strips notebook outputs, leaves checkpoints and data unstaged, commits and pushes the current branch.
