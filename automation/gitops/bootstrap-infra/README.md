# bootstrap-infra — workshop prerequisites

Cluster prerequisite chart for the redhat-ai-inference lab, wired to the ArgoCD
`bootstrap` Application on the lab cluster (path `automation/gitops/bootstrap-infra/`,
default Helm manifest generation, automated sync). Migrated from the
`rhoai-cluster-pool` overlay `prelude-nightly-36` (RHOAI 3.6-ea2).

## What it installs

- **RHOAI 3.6 nightly** — catalog source (digest-pinned), ICSP mirror
  (`registry.redhat.io/rhoai` → `quay.io/rhoai`), rhods-operator subscription
  (channel `beta`), DSCI/DSC with MaaS (`aigateway.modelsAsAService` Managed)
- **GPU** — NFD + GPU operator (`v26.7`), ClusterPolicy with dcgm +
  dcgmExporter ServiceMonitor, DCGM dashboard for the OCP console
- **MaaS dependencies** — RHCL/Kuadrant (+ clusterWide Authorino), LWS, JobSet,
  Kueue operator, MaaS postgres + `maas-db-config`
- **RHOAI 3.6 monitoring** — Cluster Observability / OpenTelemetry / Tempo
  operators, perses NetworkPolicy + PersesDatasource, Dashboard CR
  `spec.observability` fix (partial CR + ServerSideApply)
- **Dev Spaces** — subscription + CheCluster (module 4)
- **EvalHub chain** — TrustyAI `enabledServices` (SSA), RBAC, EvalHub CR (module 2)
- **Lab access** — `Group rhods-admins` with the lab user (dashboard admin,
  deploy wizard) — *not* cluster-admin

## External prerequisites (NOT in this chart — environment setup)

| Prerequisite | Why |
|---|---|
| External Secrets Operator + `ClusterSecretStore` (vault-backed) | secrets provider |
| **Pull secret ExternalSecret** → `openshift-config/pull-secret` | required: operator bundle/operand pulls from `registry.redhat.io` (NFD, GPU operator, Dev Spaces, COO/OTel/Tempo, RHCL, postgres) and the model images (`registry.redhat.io/rhai/...`); the RHOAI nightly images are exempt via the ICSP mirror |
| cert-manager, keycloak (rhbk) | deployed by the lab pipeline |

## Knobs (values.yaml)

- `lab.adminUser` — rhods-admins group member (default `lab-user1`)
- `catalog.image` — the pinned nightly FBC digest (bump per build)
- `postgres.*` — dummy lab-internal MaaS DB credentials (pool pattern)

## Flow

Commit + push → the `bootstrap` app auto-syncs → the ICSP rolls both nodes
(~10-20 min) → operators install → RHOAI stack up → validate DSC/MaaS, then run
`qa-automation/e2e.yml` + deploy the model (module 1).
