# reproducibility_notes.md


# Reproducibility Notes

## Purpose
This document provides additional notes for reproducing the main results reported in the manuscript:

**A Secure Edge–Cloud IoT Framework for Smart Parking: Matched Simulation-to-Hardware Evaluation with Cloud AI Inference on a RISC-V Platform**

It explains the intended reproducibility scope of the repository, clarifies exclusions, and summarizes how the shared artifacts relate to the reported results.

## Reproducibility Scope
This repository is intended to support reproduction of the main reported findings at the level of:
- processed result tables,
- representative runtime logs,
- measurement workflow logic,
- figure-generation scripts,
- scenario definitions.

The repository is designed to help readers understand and reproduce the reported:
- end-to-end latency analysis,
- throughput analysis,
- AI inference response analysis,
- timeout-like rate analysis,
- CPU and memory utilization analysis,
- secure vs. non-secure comparison summaries.

## Included Artifacts
The repository includes:
- processed CSV files used to generate the main paper figures and tables,
- representative raw log samples from the evaluated scenarios,
- Node-RED flow exports used for orchestration and measurement,
- figure-generation and aggregation scripts,
- scenario descriptions and data field definitions.

## Excluded Artifacts
The repository does **not** include:
- private TLS keys,
- certificates containing sensitive deployment material,
- cloud secrets,
- authentication tokens,
- personal account credentials,
- infrastructure-specific confidential configuration,
- unpublished private institutional assets.

These materials are excluded for security and confidentiality reasons.

## Representative Rather Than Exhaustive Sharing
Where full raw traces are large, redundant, or infrastructure-specific, representative runtime samples are provided instead of exhaustive archival dumps. The main reproducibility objective is to support regeneration of the paper’s reported processed results rather than to mirror the complete operational environment byte-for-byte.

## Cloud and External Service Dependence
Some aspects of the original experiments depended on external services, including:
- a cloud-hosted inference endpoint,
- network connectivity,
- runtime service availability.

For this reason, exact reproduction of every timing value may depend on network and service conditions at the time of re-execution. The repository therefore prioritizes:
- processed measurement artifacts,
- workflow transparency,
- figure-generation reproducibility,
over exact replay of every live runtime condition.

## Scenario Consistency
The experiments were designed so that simulation and hardware scenarios shared:
- the same logical event structure,
- the same edge orchestration logic,
- the same telemetry workflow,
- the same cloud inference pathway,
- the same measurement logic.

Only the deployment context and telemetry-security mode were intentionally varied.

## Notes on Interpretation
The processed result files represent the values used to build the figures and tables reported in the manuscript. Where summary metrics depend on phase-wise aggregation, percent-change calculation, or timeout-like filtering, the supporting scripts in the `scripts/` folder should be used as the reference implementation.

## Recommended Reading Order
For users of this repository, the recommended reading order is:
1. `README.md`
2. `docs/scenario_description.md`
3. `docs/data_dictionary.md`
4. files in `data/processed/`
5. relevant scripts in `scripts/`
6. representative logs in `data/raw_samples/`

## Contact
For questions regarding the repository contents, please contact the corresponding author:

**Mohammed Saad Obaid Alyasari**  
mohammed_alyasari@student.usm.my
mohammed.saad.alyasari@gmail.com
