---
schema_version: 1
id: RHAIBU-M5P8GFM8WJWH
type: requirement
---
# Module 4 — Integrate the Model into an Application (20 min)

## Problem

The MaaS endpoint only creates value when applications consume it. Attendees need to connect the Module 3 endpoint to a consuming application using standard API patterns (REST / OpenAI-compatible Chat Completions) — no custom model-specific integration code — configure it with the recorded endpoint URL and API credentials, deploy it to the cluster, and observe inference responses flowing through the integration. This module produces the running application that Modules 5 and 6 validate and monitor.

## Requirements

- [REQ-401] MUST — An attendee can open the provided sample application in the lab environment (Dev Spaces workspace), review its architecture, and identify where inference calls are made.
- [REQ-402] MUST — An attendee can configure the application with the MaaS API endpoint URL and the API credentials generated in Module 3 (env vars/config), using the explicit M3→M4 handoff values.
- [REQ-403] MUST — The application integrates over standard OpenAI-compatible API patterns (Chat Completions against the MaaS `/v1` endpoint) without model-specific integration code.
- [REQ-404] MUST — The application deploys to the OpenShift cluster (same cluster or network access to the MaaS endpoint), and its pod reaches Ready state.
- [REQ-405] MUST — An attendee can send a request through the application interface that triggers an inference call, observe the model response through the interface, and confirm the application successfully consumes the MaaS endpoint.

## Success Metrics

- 100% of attendees complete the module within its 20-minute window (3 min review app / 7 min configure / 5 min deploy / 5 min requests).
- Every attendee ends with a Running application pod that returns a model response through its interface.
- Zero integration code changes are required beyond configuration (endpoint URL + credentials) — proving the standard-API pattern.

## Risks

- Sample-app description gap: source material had no app source view (purpose, language/framework, call site) — needs description text and capture in the Act phase.
- Credential propagation mistakes (typos in endpoint URL/key) are the most likely failure; Module 5 exercises diagnosing exactly this.
- Client-side VS Code BYOK config must not be confused with the on-cluster app deployment — both consume the same endpoint but are separate steps.

## Assumptions

- Module 3 is complete: the model is exposed as MaaS with a reachable API endpoint and recorded credentials.
- A sample application is provided in the lab environment (environment contract).
- The application is deployed to the same cluster or has network access to the MaaS endpoint.

## Related Requirements

- RHAIBU-M5P8FT0JG4MK
