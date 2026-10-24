---
schema_version: 1
id: RHAIBU-M5P8GFKKQCFM
type: requirement
---
# Module 1 — Deploy a Model on Red Hat AI Enterprise (10 min)

## Problem

Before any evaluation, exposure, or integration can happen, a model must be deployed and verified as serving inference requests. Attendees arriving at the lab have no model running — the environment ships with no models pre-deployed — and intermediate AI/platform engineers need a guided, fast path from console login to a GPU-backed KServe/vLLM endpoint responding to inference. The model and runtime configured here are the foundation for every subsequent module.

## Requirements

- [REQ-101] MUST — An attendee can log in to the Red Hat AI Enterprise console with lab credentials and navigate to the model serving area within OpenShift AI (RHOAI dashboard, project/workspace selected).
- [REQ-102] MUST — An attendee can review the available model server runtimes and select the open-source model (Nemotron 3 Nano 30B A3B FP8) to deploy via KServe/vLLM (LLMInferenceService, serving image `rhaii/vllm-cuda-rhel9:3.5.1`).
- [REQ-103] MUST — An attendee can configure the model server parameters — runtime, replicas, resource limits (1xGPU / 24 Gi memory on the L40S 48 GB GPU node) — and deploy the model to the platform.
- [REQ-104] MUST — The model pod reaches Ready/Running state and the model shows Ready status with a viewable inference endpoint in the console.
- [REQ-105] MUST — An attendee can send a test inference request to the model endpoint (curl) and confirm the response matches the expected output format.
- [REQ-106] MUST — The model and runtime configured in this module carry forward unchanged through all subsequent modules (Modules 2–6).

## Success Metrics

- 100% of attendees complete the module within its 10-minute window (3 min explore / 5 min deploy / 2 min verify).
- Every attendee ends the module with a Ready model pod and a successful test inference response.
- Zero instructor interventions required for the deploy step in a pilot cohort.

## Risks

- First-pull latency: downloading the model and initializing vLLM can exceed the 5-minute deploy window on first use. Mitigation: pre-pull the model and serving image during environment provisioning.
- GPU scheduling contention: multiple concurrent students on the same cluster node. Mitigation: per-student topology (one L40S GPU per environment).

## Assumptions

- RHOAI 3.5 is installed and the GPU node (L40S 48 GB) is Ready and schedulable before the module starts.
- The serving image `rhaii/vllm-cuda-rhel9:3.5.1` and model artifacts are cached/pre-pulled in the environment.
- Attendees have basic OpenShift/Kubernetes familiarity; no prior RHOAI model-serving experience is assumed.

## Related Requirements

- RHAIBU-M5P8FT0JG4MK
