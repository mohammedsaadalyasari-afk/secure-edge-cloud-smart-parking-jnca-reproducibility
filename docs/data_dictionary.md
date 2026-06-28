data_dictionary.md
# Data Dictionary

## Overview
This document describes the primary processed files included in the reproducibility package and defines the main variables used in the analysis.

---

## File: `latency_by_phase.csv`
Phase-wise end-to-end latency results.

### Columns
- `scenario` — Scenario identifier (`S1`, `S2`, `S3`, `S4`)
- `phase` — Experimental phase/run identifier
- `count` — Number of valid latency records in the phase
- `mean_ms` — Mean end-to-end latency in milliseconds
- `median_ms` — Median end-to-end latency in milliseconds
- `p90_ms` — 90th percentile latency in milliseconds
- `min_ms` — Minimum observed latency in milliseconds
- `max_ms` — Maximum observed latency in milliseconds

---

## File: `throughput_by_phase.csv`
Phase-wise throughput results.

### Columns
- `scenario` — Scenario identifier
- `phase` — Experimental phase/run identifier
- `count` — Number of throughput observations
- `mean_msgs` — Mean throughput in messages per second
- `median_msgs` — Median throughput in messages per second
- `p90_msgs` — 90th percentile throughput
- `min_msgs` — Minimum observed throughput
- `max_msgs` — Maximum observed throughput

---

## File: `inference_by_phase.csv`
Phase-wise cloud inference response results.

### Columns
- `scenario` — Scenario identifier
- `phase` — Experimental phase/run identifier
- `count` — Number of inference records
- `mean_ms` — Mean inference response time in milliseconds
- `median_ms` — Median inference response time in milliseconds
- `p90_ms` — 90th percentile inference response time
- `min_ms` — Minimum observed inference response time
- `max_ms` — Maximum observed inference response time
- `timeout_like_count` — Number of timeout-like or abnormal delay records observed in the phase

---

## File: `timeout_rate_by_phase.csv`
Derived timeout-like rate results.

### Columns
- `scenario` — Scenario identifier
- `phase` — Experimental phase/run identifier
- `total_records` — Total number of inference records
- `timeout_like_count` — Number of timeout-like records
- `timeout_like_rate_pct` — Timeout-like rate expressed as a percentage

---

## File: `resource_usage_by_phase.csv`
Phase-wise CPU and memory utilization results.

### Columns
- `scenario` — Scenario identifier
- `phase` — Experimental phase/run identifier
- `cpu_mean_pct` — Mean CPU utilization percentage
- `cpu_median_pct` — Median CPU utilization percentage
- `cpu_p90_pct` — 90th percentile CPU utilization percentage
- `mem_mean_mb` — Mean memory usage in MB
- `mem_median_mb` — Median memory usage in MB
- `mem_p90_mb` — 90th percentile memory usage in MB

---

## File: `security_overhead_summary.csv`
Relative change summary under secure telemetry compared with the non-secure baseline.

### Columns
- `context` — Deployment context (`simulation` or `hardware`)
- `metric` — Metric name
- `relative_change_pct` — Magnitude of relative change (%)
- `direction` — Direction of change (`higher` or `lower` under secure telemetry)

---

## General Notes
- All latency and inference values are expressed in milliseconds unless otherwise stated.
- Throughput is expressed in messages per second.
- CPU values are percentages.
- Memory values are MB.
- Scenario definitions are documented in `scenario_description.md`.