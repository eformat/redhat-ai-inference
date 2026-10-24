---
schema_version: 1
id: RHAIBU-M5P8HJM63Q4V
type: decision
---
# MaaS Governance: Subscription Tiers, MaaSSubscription + MaaSAuthPolicy, API Keys with 30-Day Expiry

## Context

Module 3 exposes the deployed model as Model-as-a-Service for shared, scalable consumption. Source-material evidence shows the MaaS surface in practice: AI asset endpoints with copyable external URLs, API keys scoped to a subscription (maas-premium-subscription) with one-time masked display and 30-day expiry, per-tier token rate limits (1M tokens/min on the premium tier shown in the create dialog; 20K/min on the free tier), and OpenAI-compatible consumption (`sk-oai-` keys, `/v1` endpoint, Chat Completions). Governance must be expressed as GitOps-managed custom resources because the cluster is ACM + ArgoCD controlled.

## Decision

- Govern MaaS consumption through **subscription tiers** backed by **free and premium owner groups**: free tier at **20K tokens/min**, premium tier at **1M tokens/min** token rate limits.
- Model the governance with **MaaSSubscription + MaaSAuthPolicy + groups custom resources**, provisioned through the GitOps source (automation/gitops) — never patched directly on the cluster.
- Issue **API keys with 30-day expiry and one-time masked display**, scoped to a subscription (e.g., maas-premium-subscription), consumed over the OpenAI-compatible surface (`sk-oai-` keys, `/v1` endpoint, Chat Completions).
- The MaaS endpoint URL and API credentials recorded in Module 3 are the explicit handoff values for the Module 4 application integration.

## Consequences

- Easier: CR-based governance fits the GitOps/ArgoCD deployment model — tier changes are commits, not console surgery.
- Easier: rate limits at 20K/min free and 1M/min premium give attendees a visible, enforceable governance story (usage analytics in Module 6 show rate-limited requests).
- Harder: attendees tripping the free-tier limit during load generation would see throttling — Module 6 load generation uses premium-tier keys (1M/min).
- Trade-off accepted: 30-day key expiry means lab-issued keys are short-lived by design; content must never embed real key values (placeholders only).

## Status

Accepted

## Category

Architecture

## Alternatives Considered

- **Single subscription tier, no owner groups**: rejected — the workshop teaches tiered governance; a single tier hides the rate-limit differentiation (20K vs 1M tokens/min) that Module 6 usage analytics evidence.
- **Console-only governance** (no MaaSSubscription/MaaSAuthPolicy CRs): rejected — the cluster is GitOps controlled; console changes would be reverted and are not reproducible per student.
- **Long-lived API keys without expiry**: rejected — 30-day expiry with one-time masked display matches the platform behavior shown in source evidence and avoids long-lived credentials.
- **Per-user API tokens instead of subscription-scoped keys**: rejected — the MaaS surface governs consumption through subscription-scoped keys (`sk-oai-`, OpenAI-compatible `/v1`).

## Related Requirements

- RHAIBU-M5P8FT0JG4MK
- RHAIBU-M5P8GFM1PBHS
