---
schema_version: 1
id: RHAIBU-M5P8HJKRB05W
type: decision
---
# Infrastructure Approach: In-Place All-in-One Repo, GitOps Provisioning, Per-Student Topology on AWS g6e.12xlarge

## Context

The stock workshop template (zt-rhaibu) scaffolds two separate repositories: `zt-<slug>-showroom` for content and `zt-<slug>-automation` for environment provisioning. This workshop already has an in-progress all-in-one repo (`redhat-ai-inference`) holding content, publishing-house specs, and automation, and the cluster being targeted (rhoai-cluster-pool) is ACM + ArgoCD GitOps controlled — direct `oc` patching of cluster resources is prohibited; changes flow through the GitOps source. The design requires a per-student multinode cluster: 3 control plane (16 vCPU/64 GB) + 2 workers (16 vCPU/64 GB/100 GB disk) + 1 GPU node (NVIDIA L4 24 GB), OCP 4.22, RHOAI 3.5 with MaaS enabled. Model-serving and MaaS configuration values are drawn from the private-maas-automation platform models and the design decision set (see model-serving and maas-governance decisions).

## Decision

- **Deliberate deviation from the stock zt-rhaibu two-repo layout:** scaffold the lab **in-place** in the existing all-in-one repo `redhat-ai-inference`. No separate `zt-<slug>-showroom/` or `zt-<slug>-automation/` repos are created.
- **GitOps provisioning via `automation/gitops`:** environment resources (RHOAI, MaaS, model serving, subscriptions, monitoring) are managed as GitOps sources deployed through ACM + ArgoCD. The cluster is ACM + ArgoCD controlled — **never patch cluster resources directly with `oc`**; change the GitOps source, commit + push, and let ArgoCD/ACM sync.
- **Per-student topology on AWS g6.2xlarge (L4 24 GB):** each student gets their own environment — OCP 4.22 multinode (3 control plane + 2 workers + 1 GPU node L4 24 GB), RHOAI 3.5, MaaS enabled, no models pre-deployed.
- External services reachable from the cluster: registry.redhat.io, quay.io. No non-GA products required at the infrastructure level.

## Consequences

- Easier: single-repo continuity with existing specs and content; automation and modules evolve together (see content-format decision).
- Easier: GitOps-managed provisioning is reproducible per student and auditable — every environment state change is a commit.
- Harder: deviation from the stock template means no free upgrades from template-level fixes; the all-in-one layout must be maintained deliberately.
- Trade-off accepted: g6e.12xlarge per student is a larger per-environment footprint than a shared-cluster topology, in exchange for isolation (each student owns their GPU, model, MaaS subscriptions, and rate-limit behavior).

## Status

Accepted

## Category

Architecture

## Alternatives Considered

- **Stock zt-rhaibu two-repo layout** (`zt-<slug>-showroom` + `zt-<slug>-automation`): rejected — the all-in-one `redhat-ai-inference` repo already holds specs and content; splitting would orphan them.
- **Direct `oc` apply/patch provisioning**: rejected — the cluster is ACM + ArgoCD GitOps controlled; direct patching is prohibited and would be reverted by sync.
- **Shared-cluster topology** (multiple students per cluster): rejected — shared GPU, subscriptions, and rate-limit state break per-student reproducibility.
- **Smaller non-GPU or single-node footprint**: rejected — the design requires a multinode OCP 4.22 cluster with a dedicated L4 24 GB GPU node.

## Related Requirements

- RHAIBU-M5P8FT0JG4MK
