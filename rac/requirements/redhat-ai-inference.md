---
schema_version: 1
id: RHAIBU-M5P8FT0JG4MK
type: requirement
---
# From Model to Model as a Service: Building Scalable AI Inference

## Problem

AI platform teams can deploy a model, but that is not a production AI service. Today, teams taking models to production on Red Hat AI Enterprise face a gap between "a model pod is running" and "a shared, governed, observable Model-as-a-Service endpoint that applications integrate against". AI engineers, platform engineers, and AI operations teams (intermediate level; they know basic OpenShift/Kubernetes and AI model concepts) do not have hands-on guidance for the full serving lifecycle: deploying an open-source model on GPU-backed KServe/vLLM serving, evaluating and benchmarking inference performance with EvalHub, exposing the model as a MaaS with subscription-based access control and API keys, integrating a consuming application over the OpenAI-compatible API, validating the end-to-end request flow, and monitoring serving metrics through the observability dashboard. It matters now because organizations are moving generative AI workloads from single-team deployments to shared, scalable, governed inference services, and unmanaged deployments have no access control, no usage accounting, and no performance baselines.

This workshop requirement drives a hands-on lab (~2 hours: ~10 min intro + 1h50m across 6 modules) in a per-student Red Hat AI Enterprise environment where no models are pre-deployed — attendees build the full lifecycle from scratch.

## Requirements

- [REQ-001] MUST — An attendee can log in to the Red Hat AI Enterprise (OpenShift + OpenShift AI 3.5) console with provided lab credentials and land on the RHOAI dashboard with their assigned workspace (project) selected.
- [REQ-002] MUST — The lab environment provides a GPU worker node (NVIDIA L4, 24 GB) visible to the cluster and schedulable for model serving workloads.
- [REQ-003] MUST — Model-as-a-Service is enabled in the environment, with subscription-based governance (subscription tiers, API keys, token rate limits) available for the models served.
- [REQ-004] SHOULD — The environment provides a pre-loaded benchmark dataset for EvalHub evaluations and a sample application (pre-provided source) for the integration module.
- [REQ-005] SHOULD — Attendees have access to application logs and model server logs for the components they deploy (needed for end-to-end trace and troubleshooting).

### Model Deployment (Module 1)

- [REQ-010] MUST — An attendee can deploy the open-source model (Nemotron Nano 9B v2 FP8-dynamic) for inference via KServe/vLLM (LLMInferenceService) on the GPU node, configuring model server runtime, replicas, and resource limits (2 CPU / 16 Gi / 1xGPU with the wizard-preset vLLM serving image).
- [REQ-011] MUST — The deployed model pod reaches Ready/Running state and the model shows Ready status with a viewable inference endpoint.
- [REQ-012] MUST — An attendee can send a test inference request to the model endpoint and confirm the response matches the expected format.
- [REQ-013] MUST — The model and model-serving runtime configured in Module 1 carry forward unchanged through all subsequent modules (evaluation, MaaS exposure, application integration, validation, monitoring).

### Evaluation and Benchmarking (Module 2)

- [REQ-020] MUST — An attendee can navigate to EvalHub in the console and review available evaluation types and benchmark datasets.
- [REQ-021] MUST — An attendee can run a benchmark evaluation against the deployed model, selecting the model as evaluation target with a chosen dataset and evaluation parameters.
- [REQ-022] MUST — Evaluation results surface latency, throughput, and quality metrics that the attendee can compare against baseline thresholds.
- [REQ-023] MUST — An attendee can save the evaluation configuration as a repeatable workflow and re-trigger it to track model performance over time.
- [REQ-024] SHOULD — Evaluation payloads submitted through the MaaS gateway stay below the gateway request body limit (~3.8 MB effective, against the 4 MiB gateway body limit — RHOAIENG-99765), so evaluations do not fail on payload size.

### MaaS Exposure (Module 3)

- [REQ-030] MUST — An attendee can configure the deployed model as a Model-as-a-Service, exposing it through a stable, externally reachable API endpoint.
- [REQ-031] MUST — An attendee can create an API key scoped to a MaaS subscription (e.g., maas-premium-subscription), with a 30-day expiry and one-time masked display of the key value.
- [REQ-032] MUST — Token rate limits are enforced per subscription tier (e.g., 20K tokens/min free tier, 1M tokens/min premium tier) and visible in the API key configuration.
- [REQ-033] MUST — An attendee can send a test inference request through the MaaS endpoint using the API key and confirm the service is operational.
- [REQ-034] MUST — The recorded MaaS endpoint URL and API credentials from Module 3 are handed off and used to configure the application in Module 4.
- [REQ-035] MUST — Scaling policies configured for the MaaS endpoint carry forward to the monitoring module (Module 6).

### Application Integration (Module 4)

- [REQ-040] MUST — An attendee can identify the inference call site in the provided sample application and configure it with the MaaS endpoint URL and API credentials from Module 3.
- [REQ-041] MUST — The application integrates with the model service using standard OpenAI-compatible API patterns (Chat Completions) without custom model-specific integration code.
- [REQ-042] MUST — The application deploys to the OpenShift cluster (or a network-reachable location), its pod reaches Ready state, and it can reach the MaaS endpoint.
- [REQ-043] MUST — An attendee can send a request through the application interface that triggers an inference call and observe the model response returned through the application.

### End-to-End Validation (Module 5)

- [REQ-050] MUST — An attendee can trace a request through the full serving chain (application → MaaS endpoint → model server → model) using application logs and model server logs.
- [REQ-051] MUST — An attendee can verify the response at each layer of the serving chain matches expectations and document a healthy trace.
- [REQ-052] MUST — An attendee can introduce a simulated, reversible failure (e.g., invalid API credential), observe the error behavior, identify the failing component, and restore correct configuration.
- [REQ-053] MUST — After restoring configuration, a new request succeeds and matches the original baseline response.

### Observability and Monitoring (Module 6)

- [REQ-060] MUST — Metrics collection is active for the model server deployed in Module 1, and the observability dashboard (Cluster health + Usage analytics) is configured and accessible.
- [REQ-061] MUST — An attendee can review model serving metrics on the dashboard: request rate, latency (p50/p95/p99), throughput, error rate, and resource utilization (CPU, memory, GPU).
- [REQ-062] MUST — Generating load through the application produces visible metric changes on the dashboard (latency, throughput under higher request volume).
- [REQ-063] SHOULD — Usage analytics show per-user/per-model token accounting (total tokens, requests, rate-limited requests, success rate, active users) and confirm rate limits are applied.
- [REQ-064] SHOULD — An attendee can connect observed metrics to scaling policies, capacity planning, and alerting thresholds for production AI services.

## Success Metrics

- 100% of attendees complete all 6 modules within the ~2-hour lab window (1h50m hands-on + ~10 min intro), evidenced by each attendee's model serving, MaaS endpoint, application integration, and dashboard being functional at lab end.
- Every attendee ends the lab with: (a) a Ready model endpoint serving the open-source model on GPU; (b) at least one completed EvalHub evaluation run with results reviewed; (c) a working MaaS API key and a successful inference through the MaaS endpoint; (d) an application pod consuming the MaaS endpoint via the OpenAI-compatible API; (e) a completed trace + simulated-failure exercise; (f) observability dashboards showing serving and usage metrics for their traffic.
- Exit-survey target: ≥80% of attendees rate the workshop as meeting its objective of understanding how to move from a deployed model to a production-grade shared AI service.
- Zero unresolved environment issues during delivery: environment provisioning (RHOAI 3.5, GPU node, MaaS enabled) succeeds for 100% of students with no manual instructor intervention beyond documented steps.

## Risks

- GPU capacity: each per-student environment consumes 1 GPU (L4 24GB); cluster pool availability or AWS g6 instance quota could constrain the number of concurrent students. Mitigation: per-student topology sized at g6.2xlarge and validated in the infrastructure phase.
- Model download and cold start: pulling the model and initializing vLLM on first request can take several minutes; the 10-minute Module 1 assumes the serving image (the wizard-preset `rhaii-fast/vllm-cuda-rhel9`) and model artifacts are cached or pre-pulled. Mitigation: pre-pull during environment provisioning.
- Gateway request body limit: the MaaS gateway enforces a 4 MiB request body limit (RHOAIENG-99765); large evaluation payloads routed through the gateway will fail. Mitigation: keep eval payloads < ~3.8 MB and document the constraint in Module 2.
- Non-GA surfaces: GenAI playground and related AI-asset endpoints are Tech Preview; UI may change between RHOAI releases. Mitigation: pin RHOAI 3.5 and re-verify screenshots in the Act phase.
- Dependency on external registries (registry.redhat.io, quay.io): network egress from the cluster must reach them for serving images and application images.
- Rate-limit interplay: attendees sharing a demo model could trip the 20K tokens/min free-tier limit during load generation; lab uses premium-tier keys (1M tokens/min) for Module 6 load generation.

## Assumptions

- The environment runs OpenShift 4.22 with Red Hat OpenShift AI 3.5 (including EvalHub and the observability dashboard) and Model-as-a-Service enabled with subscription tiers (free/premium owner groups, token rate limits).
- A GPU worker node (NVIDIA L4, 24 GB) is available per student; cluster is provisioned and GitOps-managed (ACM + ArgoCD) — no direct `oc` patching of cluster resources.
- The open-source model (Nemotron Nano 9B v2 FP8-dynamic) is served via KServe/vLLM using the wizard-preset vLLM serving image with 2 CPU / 16 Gi / 1 GPU resources.
- A benchmark dataset is pre-loaded for Module 2, and a sample application is provided for Module 4; both are part of environment provisioning.
- Attendees have basic OpenShift/Kubernetes and AI model concept knowledge (workshop is Intermediate); no prior RHOAI or MaaS experience is assumed.
- Modules are strictly sequential (M1 → M6): each module's outputs are the next module's inputs (model+runtime carry forward; M3 credentials feed M4; M4 app feeds M5/M6 load).
- Placeholder hostnames (generic lab domains) are used in content; no real credentials or tokens appear in any artifact.
