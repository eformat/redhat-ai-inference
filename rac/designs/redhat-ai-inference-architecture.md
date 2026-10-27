---
schema_version: 1
id: RHAIBU-M5P8JD80ZN62
type: design
---
# Red Hat AI Inference Workshop Architecture: From Model to Model as a Service

## Context

The workshop "From Model to Model as a Service: Building Scalable AI Inference" is a hands-on lab (~2 hours: ~10 min intro + 6 modules totaling 1h50m) for AI engineers, platform engineers, and AI operations teams (Intermediate). Attendees take an open-source model through the full serving lifecycle on Red Hat AI Enterprise: deploy on GPU-backed KServe/vLLM, evaluate with EvalHub, expose as Model-as-a-Service with subscription governance, integrate a consuming application, validate the end-to-end flow, and monitor through the observability dashboard. This design defines the module flow and dependencies, the all-in-one repo structure, the infrastructure requirements, and the parameter inventory for the environment.

## User Need

- **Audience:** AI engineers, platform engineers, AI operations teams — intermediate level; they know basic OpenShift/Kubernetes and AI model concepts (training vs. inference) but not how to move from a deployed model to a production-grade shared AI service.
- **Task:** complete 6 sequential hands-on modules in a per-student environment, ending with a working chain: model pod → EvalHub evaluation → MaaS endpoint with API key → consuming application → validated trace → live dashboards.
- **Pain point addressed:** deployments without governance, baselines, or observability; this design gives every attendee the full lifecycle with strict carry-forward contracts between modules.

## Design

### Module flow and dependencies (strictly sequential: M1 → M2 → M3 → M4 → M5 → M6)

| Module | Title | Duration | Produces (carry-forward contract) |
|--------|-------|----------|-----------------------------------|
| M1 | Deploy a Model on Red Hat AI Enterprise | 10 min | Deployed model + runtime (Nemotron Nano 9B v2 FP8-dynamic, KServe/vLLM, 2 CPU/16Gi/1xGPU) — **carries through ALL modules** |
| M2 | Evaluate and Benchmark Model Performance with EvalHub | 20 min | Evaluation results (latency/throughput/quality) + saved repeatable evaluation workflow |
| M3 | Expose the Model as a Model-as-a-Service | 20 min | MaaS endpoint URL + API key (30-day expiry) + scaling policies — **endpoint must be externally reachable from the M4 app; scaling config carries to M6** |
| M4 | Integrate the Model into an Application | 20 min | Running application consuming the MaaS endpoint via OpenAI-compatible API — **load source for M5/M6** |
| M5 | Validate the End-to-End Workflow | 20 min | Documented healthy trace (app → MaaS → model server → model) + reversible failure/recovery exercise |
| M6 | Monitor Model Performance through Observability | 20 min | Dashboard baselines + load-driven metric changes + metrics→scaling-policy connection |

Dependency rules:
- Every module N lists module N-1 as prerequisite; no parallel tracks.
- Model + runtime from M1 are never reconfigured in later modules; M6 metrics collection must be active for the M1 model server.
- M3 §"record endpoint URL + credentials" feeds M4 §"configure the application" verbatim (M3→M4 handoff).
- M5's trace path is the canonical serving chain: application → MaaS endpoint → model server → model; the M5 failure simulation must be reversible so the environment is intact for M6.
- M6 generates load through the M4 application and interprets metrics against the M3 scaling configuration.

### Repo structure (all-in-one publishing house layout)

- `content/` — Antora/AsciiDoc showroom lab: `content/modules/ROOT/pages/` (index.adoc with access instructions + module table; `module-01`…`module-06` pages), `content/antora.yml`, site playbook.
- `automation/` — environment provisioning: `automation/ansible/` (per-student setup playbooks) + `automation/gitops/` (ACM + ArgoCD sources for RHOAI, MaaS subscriptions/policies, model serving, monitoring).
- `qa-automation/` — verification scripts/gates for environment readiness (GPU node Ready, RHOAI 3.5 healthy, MaaS enabled, dashboards accessible).
- No separate `zt-<slug>-showroom/` or `zt-<slug>-automation/` repos (deliberate deviation — see infrastructure-approach decision).

### Infrastructure requirements

- OCP 4.22, multinode: 3 control plane (16 vCPU / 64 GB RAM) + 2 workers (16 vCPU / 64 GB RAM / 100 GB disk) + 1 GPU node (NVIDIA L4 24 GB).
- Red Hat OpenShift AI 3.5 with Model-as-a-Service enabled (subscription tiers, API keys, rate limits) and EvalHub + observability dashboard available.
- Per-student topology on AWS g6.2xlarge (L4 24 GB); GitOps (Helm + ArgoCD) via automation/gitops; external services: registry.redhat.io, quay.io.
- No models pre-deployed (attendees build from scratch); benchmark dataset pre-loaded (M2); sample application provided (M4); log access for app + model server (M5).

### {attribute} parameter inventory (lab placeholders)

| Attribute | Purpose |
|-----------|---------|
| `{lab_name}` | Lab/session identifier used across content and provisioning |
| `{user}` | Assigned student username (lab user / workspace project owner) |
| `{password}` | Assigned student password (placeholder in content — never a real credential) |
| `{guid}` | Environment GUID used in lab URLs and resource naming |
| `{openshift_api_url}` | OpenShift API server URL for `oc login` |
| `{openshift_console_url}` | OpenShift web console URL (entry point to the RHOAI waffle) |
| `{openshift_cluster_ingress_domain}` | Cluster ingress domain used to construct MaaS/app routes |
| `{maas_endpoint_url}` | MaaS endpoint URL for the deployed model (copied in M3, consumed in M4; derived from ingress domain) |
| `{rhoai_dashboard_url}` | RHOAI observability dashboard URL (Cluster + Usage tabs, M6) |
| `{devspaces_url}` | Dev Spaces URL for the M4 exercises workspace |

All values are placeholders in content; real values are injected by provisioning per student.

## Constraints

- Cluster resources are ACM + ArgoCD GitOps controlled — never patch cluster resources directly with `oc`; change the GitOps source and sync.
- The MaaS gateway enforces a 4 MiB request body limit (RHOAIENG-99765): evaluation payloads through the gateway must stay < ~3.8 MB.
- Modules are strictly sequential; each module's outputs are the next module's inputs — no module may reconfigure the M1 model/runtime.
- No real credentials, tokens, or key values in any artifact — placeholder hostnames/attributes only.
- Serving stack pinned: Nemotron Nano 9B v2 FP8-dynamic via LLMInferenceService, wizard-preset vLLM image (`rhaii-fast/vllm-cuda-rhel9`, digest-pinned), 2 CPU/16Gi/1xGPU on L4 24 GB.
- Non-GA products: none at the infrastructure level (all GA); GenAI playground surfaces are Tech Preview and only support optional flows.

## Rationale

- Strict sequential dependency chain mirrors the real serving lifecycle (deploy → measure → expose → consume → validate → operate), making each carry-forward contract teachable and testable.
- The all-in-one repo keeps content, automation, and QA atomic — module steps and the environment that serves them cannot drift.
- Per-student topology gives each attendee isolated GPU, subscriptions, and rate-limit behavior, so Module 6 load generation and rate-limit evidence are personal and reproducible.
- Placeholder-first {attribute} parameters let one AsciiDoc source serve every student environment via provisioning-time substitution.

## Alternatives

- **Stock zt-rhaibu two-repo layout** (separate showroom + automation repos): rejected — splits content and environment management; the existing all-in-one repo already holds the specs (see infrastructure-approach decision).
- **Shared-cluster topology** (multiple students per cluster): rejected — rate limits, GPU contention, and MaaS subscription state would be shared, breaking per-student reproducibility.
- **Direct model deployment without MaaS** (single-team serving): rejected — it skips the governance layer (subscriptions, API keys, rate limits) that is the workshop's central theme.
- **Different model** (larger checkpoint or non-quantized): rejected — does not fit 2 CPU/16Gi/1xGPU on L4 24 GB with serving headroom.

## Accessibility

- AsciiDoc content follows structural heading order (single H1 per page; H2 sections; H3 subsections) for screen-reader navigation.
- Code blocks use labeled `[source,bash]` blocks; console steps name UI elements explicitly rather than relying on screenshots alone.
- All screenshots carry alt text describing the console state; placeholder-first images are replaced with described live captures in the Act phase.
- Color is never the only carrier of meaning in dashboards interpretation guidance (values are read as text: e.g., "95% success", "3 rate-limited").

## Style Guidance

- Module pages follow a consistent structure: overview → prerequisites → sections with steps → verification → key takeaways.
- Commands are copy-pasteable; every module's verification step produces observable output (pod Ready, HTTP response, dashboard value).
- Console navigation paths are written as "Menu → Submenu → Item" chains; parameters always use the {attribute} placeholder forms listed above.
- Tone: intermediate practitioner — explain what each step proves, not what OpenShift is.

## Open Questions

- Exact EvalHub UI/API surface in RHOAI 3.5 — verify against RHOAI 3.5 docs before Act-phase capture (see evaluation decision).
- Final M1 test-inference command shape (curl against the model endpoint directly vs. through the MaaS gateway) — confirm during Act phase.
- Load-generation script for M6 (client-side loop through the M4 application) — author and capture in Act phase.

## Related Requirements

- RHAIBU-M5P8FT0JG4MK
- RHAIBU-M5P8GFKKQCFM
- RHAIBU-M5P8GFKTXB5F
- RHAIBU-M5P8GFM1PBHS
- RHAIBU-M5P8GFM8WJWH
- RHAIBU-M5P8GFMF7TQ6
- RHAIBU-M5P8GFMQM00Q

## Related Decisions

- RHAIBU-M5P8HJKGVYQQ
- RHAIBU-M5P8HJKRB05W
- RHAIBU-M5P8HJM0Y86K
- RHAIBU-M5P8HJM63Q4V
- RHAIBU-M5P8HJMEP6JK
