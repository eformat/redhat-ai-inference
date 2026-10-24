---
schema_version: 1
id: RHAIBU-M5P8GFMF7TQ6
type: requirement
---
# Module 5 — Validate the End-to-End Workflow (20 min)

## Problem

Deployment, serving, access control, and application integration were built in separate modules — attendees must prove they work together. Without end-to-end validation, a shared AI service can fail silently between layers (credential errors, unreachable endpoints, misconfigured env vars). Attendees need to trace a request through the canonical serving chain (application → MaaS endpoint → model server → model), troubleshoot a simulated failure, and confirm reliability — using structured, layer-by-layer log inspection.

## Requirements

- [REQ-501] MUST — An attendee can send a request from the application interface, note the response, and trace the request path: application → MaaS endpoint → model server → model.
- [REQ-502] MUST — An attendee can inspect application logs and model server logs to confirm the outbound request was sent and the inference request was received and processed.
- [REQ-503] MUST — An attendee can verify the response returned through each layer matches expectations and document what a healthy trace looks like at each step.
- [REQ-504] MUST — An attendee can introduce a simulated, reversible failure (e.g., invalid API credential or unreachable endpoint), observe the error behavior in application and model server logs, identify the broken component, and restore the correct configuration.
- [REQ-505] MUST — After restoring configuration, another request succeeds and matches the original baseline response, confirming end-to-end reliability.
- [REQ-506] MUST — The failure simulation is reversible without disrupting the environment for Module 6.

## Success Metrics

- 100% of attendees complete the module within its 20-minute window (5 min trace / 5 min verify components / 5 min troubleshoot / 5 min confirm reliability).
- Every attendee produces a documented healthy trace at each layer and completes the failure/recovery cycle.
- Zero environments left in a broken state after the failure simulation (revert verified).

## Risks

- Log-view commands and failure-simulation steps were gaps in source material (no captures) — needs authored commands and Act-phase capture.
- An attendee may corrupt state during the failure simulation; the revert steps must be explicit and validated.

## Assumptions

- Module 4 is complete: the application is deployed and connected to the model service.
- Attendees have access to application logs and model server logs (environment contract).
- The failure scenario is reversible without disrupting the environment for subsequent modules.

## Related Requirements

- RHAIBU-M5P8FT0JG4MK
