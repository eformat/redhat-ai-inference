---
schema_version: 1
id: RHAIBU-M5P8GFMQM00Q
type: requirement
---
# Module 6 — Monitor Model Performance through Observability (20 min)

## Problem

A production AI service needs ongoing visibility: latency, throughput, error rate, and resource utilization under real usage — not just a one-time evaluation. Attendees need to use the Red Hat AI Enterprise observability dashboard to monitor the serving chain under load, understand how metrics change with demand, and connect those metrics to scaling policies, capacity planning, and alerting thresholds. This module closes the loop with the scaling configuration set in Module 3 and requires metrics collection active for the Module 1 model server.

## Requirements

- [REQ-601] MUST — Metrics collection is active for the Module 1 model server, and the observability dashboard is configured and accessible (Cluster health + Usage analytics tabs).
- [REQ-602] MUST — An attendee can navigate to the observability dashboard and review model serving metrics: request rate, latency (p50, p95, p99), throughput, error rate, and resource utilization (CPU, memory, GPU).
- [REQ-603] MUST — An attendee can observe current metric values reflecting traffic from the Module 4 application and note baselines for latency, throughput, and error rate.
- [REQ-604] MUST — Generating load through the application (multiple concurrent requests) produces visible dashboard updates — latency and throughput changes under higher request volume.
- [REQ-605] MUST — An attendee can analyze the relationship between request rate, latency, and resource utilization, identify trends or thresholds where serving behavior changes, and connect the metrics to scaling policies and capacity decisions.
- [REQ-606] SHOULD — Usage analytics show per-user/per-model token accounting (total tokens, requests, rate-limited requests, success rate, active users) and evidence that MaaS rate limits from Module 3 are applied.

## Success Metrics

- 100% of attendees complete the module within its 20-minute window (5 min explore / 5 min monitor metrics / 5 min generate load / 5 min analyze trends).
- Every attendee observes metric changes under generated load and records at least one trend or threshold observation.
- Dashboards show live data for 100% of attendees' model servers (metrics collection verified per student).

## Risks

- Dashboard annotation gap: dashboards are captured in source material but without the required instructor annotations pointing at key panels — Act-phase capture needed.
- Load-generation command was a gap in source material — needs an authored load-generation script and Act-phase capture.
- Metrics pipeline latency: dashboards may lag load generation by a scrape interval; account for the delay in the 5-minute load slot.

## Assumptions

- Module 5 is complete: the end-to-end workflow is validated and the application actively sends requests to the model service.
- The observability dashboard is configured and metrics collection is active for the Module 1 model server (environment contract).
- The scaling configuration from Module 3 carries forward and provides the production lens for metric interpretation.

## Related Requirements

- RHAIBU-M5P8FT0JG4MK
