# Reproducibility Package for:
## A Secure Edge–Cloud IoT Framework for Smart Parking: Matched Simulation-to-Hardware Evaluation with Cloud AI Inference on a RISC-V Platform

### Authors
- Mohammed Saad Obaid Alyasari


## Overview
This repository provides the reproducibility package associated with the manuscript:

**A Secure Edge–Cloud IoT Framework for Smart Parking: Matched Simulation-to-Hardware Evaluation with Cloud AI Inference on a RISC-V Platform**

The package contains processed result tables, representative runtime logs, Node-RED workflow exports, figure-generation scripts, and supporting documentation used to reproduce the main experimental findings reported in the paper.

## Repository Structure


.
├── README.md
├── CITATION.cff
├── .zenodo.json
├── data/
│   ├── processed/
│   └── raw_samples/
├── flows/
├── scripts/
├── docs/
│   ├── scenario_description.md
│   ├── data_dictionary.md
│   └── reproducibility_notes.md
└── models/
Included Materials
data/processed/

This folder contains processed CSV files used to generate the main figures and result tables reported in the manuscript. Typical files include:

Table_4_2_latency_by_phase_full.csv 
Table_4_2_latency_by_phase_mainplot.csv 
Table_4_2_latency_timeout_counts_by_phase.csv 
Table_4_3_throughput_by_phase.csv
Table_4_4_inference_by_phase_full.csv 
Table_4_4_inference_by_phase_mainplot.csv 
Table_4_4_inference_timeout_counts_by_phase.csv
Table_4_4a_cpu_by_phase.csv 
Table_4_4b_memory_by_phase.csv 
Table_4_5_security_overhead_corrected.csv
raw_samples/


This folder contains representative raw runtime logs for the four evaluated scenarios:

S1: Simulation + non-secure MQTT
S2: Simulation + secure MQTT/TLS
S3: Hardware + non-secure MQTT
S4: Hardware + secure MQTT/TLS

These are representative samples rather than a complete archival dump of all runtime traces.

flows/

This folder contains exported Node-RED workflow files used for:

Node-res flows
scripts/

This folder contains scripts used to:

run_figures_final_by_rounds_local_AllTables_AllFig

docs/

This folder contains supporting documentation, including:

scenario definitions,
data-field descriptions,
reproducibility notes.
models/

This folder may contain model metadata and non-sensitive deployment artifacts such as:

models 
main.py 
model_loader.py 
models\parking_log_1.csv 
requirements.txt

Private credentials, API keys, certificates, and other sensitive deployment files are intentionally excluded.

Experimental Scenarios

The repository supports four matched experimental scenarios:

S1 — Simulation with non-secure MQTT
S2 — Simulation with secure MQTT over TLS
S3 — Hardware with non-secure MQTT
S4 — Hardware with secure MQTT over TLS

Detailed scenario definitions are provided in docs/scenario_description.md.

Reproducibility Scope

This repository is intended to reproduce the main reported results of the paper, including:

end-to-end latency analysis,
throughput analysis,
AI inference response behavior,
timeout-like rate analysis,
edge CPU and memory utilization,
relative change under secure telemetry compared with non-secure baselines.
How to Use This Repository
Review the scenario definitions in docs/scenario_description.md
Review the variable descriptions in docs/data_dictionary.md
Use the processed CSV files in data/processed/
Run the plotting and aggregation scripts in scripts/
Compare the generated outputs with the figures and tables reported in the manuscript
Confidentiality and Exclusions

The following items are intentionally not shared:

private TLS keys and certificates
API secrets and authentication tokens
cloud account credentials
infrastructure-specific confidential configuration
personally identifiable information
Citation

If you use this repository, please cite the associated paper and this repository release.

See CITATION.cff for citation metadata.

License





Corresponding author:
Mohammed Saad Obaid Alyasari
mohammed_alyasari@student.usm.my
mohammed.saad.alyasari@gmail.com