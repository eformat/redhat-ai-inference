# App-of-apps layout

The former single `bootstrap-infra` Helm chart (74 resources under one ArgoCD
application — painful to debug) is split into six functional Helm charts wired
as an app-of-apps. The root application (named `bootstrap`) points at
`automation/gitops/app-of-apps/`; each file there is a child Application.

| Child app | Path | Wave | Resources | Function |
|-----------|------|------|-----------|----------|
| `rhai-operators` | `operators/` | 0 | 31 | Namespaces, catalog source, ICSP, OperatorGroups, Subscriptions, NFD ClusterPolicy |
| `rhai-rhoai` | `rhoai/` | 1 | 7 | DSCInitialization, DataScienceCluster, CheCluster, dashboard configs, rhods-admins group |
| `rhai-operator-configs` | `operator-configs/` | 2 | 4 | Kueue/LWS/JobSet operator configs + model-serving ClusterQueue |
| `rhai-maas` | `maas/` | 3 | 21 | Postgres DB, maas-default-gateway + status Job, MLflow, EvalHub, Kuadrant/Authorino, TelemetryPolicy |
| `rhai-model-serving` | `model-serving/` | 4 | 9 | gpu-serving HardwareProfile, accelerator config, openshift-ai-inference gateway |
| `rhai-observability` | `observability/` | 5 | 2 | Perses datasource, network policy |

Each child chart is a self-contained Helm chart (`Chart.yaml` + `values.yaml` +
`templates/`). Knobs live in each chart's `values.yaml` (operators: the catalog
fragment; rhoai: the lab admin user; maas: the dummy postgres credentials).
Child apps are wave-ordered by the root: the root's sync waits for each child
to go Healthy before creating the next, preserving the former cross-chart
deployment order. Within a child app its own resource sync-waves apply.

## Migration (one-time, ORDER MATTERS)

The root application currently has `prune: true` and points at
`automation/gitops/bootstrap-infra/`. Pointing it at `app-of-apps/` with prune
still on would prune all 74 tracked resources before the child apps recreate
them — a full environment rebuild (operators uninstall/reinstall, DSC
teardown). Follow this order:

1. **Disable prune on the root app** (one-time):
   `oc patch applications.argoproj.io bootstrap -n openshift-gitops --type merge -p '{"spec":{"syncPolicy":{"automated":{"prune":false}}}}'`
2. **Push this commit** (the new structure; `bootstrap-infra/` is removed).
3. **Point the root app at the app-of-apps path**:
   `oc patch applications.argoproj.io bootstrap -n openshift-gitops --type merge -p '{"spec":{"source":{"path":"automation/gitops/app-of-apps"}}}'`
   The sync creates the six child apps; with prune off nothing old is deleted.
   The children adopt the existing resources (identical specs — no churn).
4. **Wait for all six child apps to be Synced/Healthy**, then confirm each
   child app shows its resources (ArgoCD UI or
   `oc get applications.argoproj.io -n openshift-gitops`).
5. **Re-enable prune on the root app**:
   `oc patch applications.argoproj.io bootstrap -n openshift-gitops --type merge -p '{"spec":{"syncPolicy":{"automated":{"prune":true}}}}'`
   The root now tracks only the six child Applications — prune is safe.
6. Optionally delete the stale root-level `ignoreDifferences` (the two
   ConfigMap `/data` entries on `bootstrap`) — the children carry their own.

Notes:
- If a sync operation shows `Operation terminated`, it was superseded (e.g. by
  a repeated refresh annotation) or ArgoCD is waiting on operator Subscription
  health in an early wave — re-trigger with a single
  `argocd.argoproj.io/refresh=hard` annotation and let it run.
- The root app's sync hooks from the old chart (the gateway/maas status Jobs)
  live inside the child apps now; they re-run on each child app's sync.
