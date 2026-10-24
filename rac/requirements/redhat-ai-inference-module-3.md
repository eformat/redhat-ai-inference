---
schema_version: 1
id: RHAIBU-M5P8GFM1PBHS
type: requirement
---
# Module 3 — Expose the Model as a Model-as-a-Service (20 min)

## Problem

A model only one team can reach is not production. Attendees must learn to transform the single-team deployment into a shared, scalable Model-as-a-Service: a stable externally reachable API endpoint governed by subscription-based access control (subscriptions, API keys with expiry, token rate limits) and scaling policies. This is the module that produces the credentials and endpoint the application (Module 4) consumes — the explicit M3→M4 handoff.

## Requirements

- [REQ-301] MUST — An attendee can navigate to the model serving configuration for the deployed model and review how Model-as-a-Service differs from a direct single-team deployment (concept: API gateway between consumers and models).
- [REQ-302] MUST — An attendee can configure the model as a shared service, exposing it through a stable, externally reachable API endpoint (MaaS endpoint URL copyable from the AI asset endpoints page).
- [REQ-303] MUST — MaaS subscription governance is in place: subscription tiers (free/premium backed by owner groups), MaaSSubscription + MaaSAuthPolicy custom resources, and an API key creatable through the console.
- [REQ-304] MUST — An attendee can create an API key scoped to a subscription (e.g., maas-premium-subscription) with a 30-day expiry and one-time masked display, respecting per-tier token rate limits (20K tokens/min free, 1M tokens/min premium).
- [REQ-305] MUST — An attendee can configure scaling policies for concurrent consumers and send a test inference request through the MaaS endpoint (OpenAI-compatible `/v1` surface, `sk-oai-` key) to confirm the service is operational.
- [REQ-306] MUST — The attendee records the endpoint URL + API credentials and uses them in Module 4 (explicit M3→M4 handoff), and the scaling configuration carries forward to Module 6.

## Success Metrics

- 100% of attendees complete the module within its 20-minute window (3 min review / 7 min configure shared service / 5 min access controls + endpoints / 5 min scaling).
- Every attendee ends with a working API key (30-day expiry) and a successful test inference through the MaaS endpoint.
- 100% of attendees carry the recorded endpoint URL + credentials into Module 4 without re-deriving them.

## Risks

- The exposure act itself is never shown in source material (only its end state): console steps for enabling MaaS exposure need live capture in the Act phase.
- Rate-limit misconfiguration could block attendees during later load generation. Mitigation: use premium-tier keys (1M tokens/min) for Module 6 load generation.

## Assumptions

- Module 1 (model deployed) and Module 2 (model evaluated) are complete.
- Model-as-a-Service is enabled in the environment with subscription tiers (free/premium owner groups) and token rate limits configured.
- The MaaS endpoint is externally accessible from the application deployed in Module 4 (same cluster or network reachability).

## Related Requirements

- RHAIBU-M5P8FT0JG4MK
