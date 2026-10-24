---
schema_version: 1
id: RHAIBU-M5P8HJMEP6JK
type: decision
---
# Evaluation: EvalHub Benchmark/Evaluation Workflow with Gateway Body-Limit Constraint

## Context

Module 2 requires benchmarking the deployed model with EvalHub, the evaluation feature of Red Hat AI Enterprise. Source material contained zero EvalHub captures (only commentary steps), so the workflow must be verified against the RHOAI 3.5 documentation before content and screenshots are finalized. A known platform constraint applies: the MaaS gateway enforces a 4 MiB request body limit (RHOAIENG-99765), so any evaluation/benchmark payloads routed through the gateway must stay below that limit.

## Decision

- Use the **EvalHub benchmark/evaluation workflow** for Module 2: navigate to EvalHub → review evaluation types and benchmark datasets → select the deployed model as target → choose a dataset and configure parameters → run the benchmark → analyze latency, throughput, and quality results against baseline thresholds → save the configuration as a repeatable workflow.
- **Verify the workflow against RHOAI 3.5 documentation** before authoring steps and capturing screenshots (no source screenshots exist — the adoc workflow is the authority, confirmed against docs).
- Treat the **4 MiB gateway request body limit (RHOAIENG-99765)** as a hard constraint: evaluation payloads submitted through the gateway must stay **< ~3.8 MB** to leave margin below the limit.
- The benchmark dataset is pre-loaded in the environment (environment contract); the saved evaluation configuration is re-triggerable to track performance over time.

## Consequences

- Easier: a repeatable evaluation workflow gives attendees an artifact they can re-trigger in later modules to see performance trends (pairs with Module 6 monitoring).
- Easier: doc-verification before authoring avoids writing steps against a UI or API that differs in RHOAI 3.5.
- Harder: payload size must be managed — large eval datasets or long prompts routed through the gateway will fail on the 4 MiB limit; content must document the ~3.8 MB effective ceiling.
- Trade-off accepted: running evals within the gateway constraint means dataset/parameter choices are bounded; oversized runs must be restructured rather than pushed through as-is.

## Status

Accepted

## Category

Technical

## Alternatives Considered

- **Hand-rolled evaluation scripts** (curl loops + metric scraping): rejected — EvalHub provides the structured benchmark/evaluation workflow within Red Hat AI Enterprise that the workshop must teach.
- **Authoring steps without doc verification**: rejected — zero EvalHub captures exist in source material; RHOAI 3.5 docs are the only authority for the UI/API surface before Act-phase capture.
- **Oversized eval payloads through the gateway**: rejected — the 4 MiB body limit (RHOAIENG-99765) makes this a hard failure; the < ~3.8 MB ceiling is a constraint, not a preference.

## Related Requirements

- RHAIBU-M5P8FT0JG4MK
- RHAIBU-M5P8GFKTXB5F
