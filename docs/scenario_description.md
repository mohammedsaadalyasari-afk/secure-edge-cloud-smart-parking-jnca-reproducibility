# scenario_description.md


# Experimental Scenario Description

## Overview
This document defines the matched experimental scenarios used in the manuscript:

**A Secure Edge–Cloud IoT Framework for Smart Parking: Matched Simulation-to-Hardware Evaluation with Cloud AI Inference on a RISC-V Platform**

The evaluation was designed to preserve the same sensing logic, data structure, telemetry workflow, cloud inference path, and measurement logic across all scenarios. The two controlled dimensions were:

1. **Deployment context**
   - Simulation
   - Physical hardware

2. **Telemetry-security mode**
   - Non-secure MQTT
   - Secure MQTT over TLS

## Scenario Definitions

### S1 — Simulation + Non-Secure MQTT
- **Deployment context:** Simulation
- **Input source:** Simulated parking events
- **Telemetry mode:** Non-secure MQTT
- **Transport port:** 1883
- **AI inference:** Enabled
- **Purpose:** Baseline simulation scenario for end-to-end performance measurement without transport-layer protection

### S2 — Simulation + Secure MQTT/TLS
- **Deployment context:** Simulation
- **Input source:** Simulated parking events
- **Telemetry mode:** Secure MQTT over TLS
- **Transport port:** 8883
- **AI inference:** Enabled
- **Purpose:** Simulation scenario used to quantify the effect of secure telemetry relative to S1

### S3 — Hardware + Non-Secure MQTT
- **Deployment context:** Physical hardware
- **Input source:** Physical parking sensors connected to the VisionFive 2 edge platform
- **Telemetry mode:** Non-secure MQTT
- **Transport port:** 1883
- **AI inference:** Enabled
- **Purpose:** Hardware baseline scenario for end-to-end performance measurement without transport-layer protection

### S4 — Hardware + Secure MQTT/TLS
- **Deployment context:** Physical hardware
- **Input source:** Physical parking sensors connected to the VisionFive 2 edge platform
- **Telemetry mode:** Secure MQTT over TLS
- **Transport port:** 8883
- **AI inference:** Enabled
- **Purpose:** Hardware scenario used to quantify the effect of secure telemetry relative to S3

## Common Workflow Across All Scenarios
All scenarios preserved the same operational sequence:
1. Event generation or detection
2. Edge-side normalization and orchestration in Node-RED
3. Telemetry exchange through MQTT
4. Cloud AI inference request over HTTPS
5. Dashboard update
6. Runtime logging and measurement extraction

## Controlled Experimental Principle
The methodology was intentionally designed so that only the following differed between scenarios:
- deployment context,
- telemetry-security mode.

All other workflow elements remained functionally matched.

## Repeated Phases
Each scenario was executed in repeated phases/runs to reduce run-specific variation and support more stable comparison of:
- latency,
- throughput,
- AI inference behavior,
- timeout-like rate,
- CPU usage,
- memory usage.

## Notes
- Secure telemetry refers specifically to MQTT protected with TLS.
- Cloud inference communication remained HTTPS-based across all scenarios.
- The repository contains processed result artifacts and representative raw samples corresponding to these scenario definitions.
