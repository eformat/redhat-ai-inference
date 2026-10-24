---
schema_version: 1
id: RHAIBU-M5P8GFKTXB5F
type: requirement
---
# Module 2 — Evaluate and Benchmark Model Performance with EvalHub (20 min)

## Problem

A deployed model that has never been measured is a risk: teams cannot make serving decisions (expose, scale, or tune) without latency, throughput, and quality baselines. Attendees need hands-on experience with EvalHub — the evaluation feature of Red Hat AI Enterprise — to run a benchmark against the deployed model, interpret the results, and configure a repeatable evaluation workflow that tracks performance over time. No visual evidence of this flow existed in source material, so this module defines the authoritative steps for content and live capture.

## Requirements

- [REQ-201] MUST — An attendee can navigate to EvalHub within the Red Hat AI Enterprise console and review the available evaluation types and benchmark datasets (pre-loaded in the environment).
- [REQ-202] MUST — An attendee can select the Module 1 model as the evaluation target, choose a benchmark dataset, configure evaluation parameters, and run the benchmark evaluation.
- [REQ-203] MUST — The evaluation run completes and surfaces latency, throughput, and quality metrics on a results dashboard.
- [REQ-204] MUST — An attendee can compare the evaluation results against baseline thresholds and interpret what the metric values mean for serving decisions.
- [REQ-205] MUST — An attendee can save the evaluation configuration as a repeatable workflow and verify it can be re-triggered to track performance over time.
- [REQ-206] SHOULD — Any evaluation payloads submitted through the MaaS gateway stay below ~3.8 MB (the gateway enforces a 4 MiB request body limit — RHOAIENG-99765), so benchmark/eval requests do not fail on payload size.

## Success Metrics

- 100% of attendees complete the module within its 20-minute window (3 min explore / 7 min run eval / 5 min analyze / 5 min repeatable workflow).
- Every attendee ends with one completed evaluation run whose results they have compared against thresholds, plus a saved repeatable workflow verified as re-triggerable.
- Zero eval requests fail due to gateway payload size during the run.

## Risks

- EvalHub availability and UI churn: EvalHub must be enabled in the environment; the UI is newer and may differ across RHOAI releases. Mitigation: pin RHOAI 3.5 and re-verify in the Act phase.
- Gateway body limit: large eval payloads routed through the MaaS gateway trip the 4 MiB limit (RHOAIENG-99765). Mitigation: keep payloads < ~3.8 MB and document the constraint.
- Evaluation duration: benchmark runs may take longer than the 7-minute run slot on a shared GPU. Mitigation: pre-select a dataset sized for the window.

## Assumptions

- Module 1 is complete: the model is deployed and serving inference requests.
- The benchmark dataset is pre-loaded in the environment (environment contract).
- EvalHub is available in the RHOAI 3.5 environment.

## Related Requirements

- RHAIBU-M5P8FT0JG4MK
