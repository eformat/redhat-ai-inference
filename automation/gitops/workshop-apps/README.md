# workshop-apps — redhat-ai-inference lab automation (GitOps)

Workshop-level Kubernetes YAML for the redhat-ai-inference lab that is **not**
under the `rhoai-cluster-pool` GitOps control (that repo owns platform-level
resources: DSCI/DSC, RHOAI operators, MaaS gateway, ACM policies). Everything
here is lab-scoped and applied manually with `oc apply -k`.

## Files

| File | Unblocks | Notes |
|---|---|---|
| `namespace-labels.yaml` | M1/M4 — projects UI visibility, e2e M1 | `opendatahub.io/dashboard=true` — without it the lab project is invisible in the RHOAI projects UI (2026-10-25 cluster-drift gap) |
| `model-serviceaccount.yaml` | M1/M3 — model token minting, MaaS calls | `model-tester` SA used to mint model tokens |
| `maas-chat-client.yaml` | M4 — 404/405/502 | code ConfigMap + Deployment, mirrored from `qa-automation/e2e.yml` M4 |
| `maas-credentials-secret.yaml` | M4 — 405/502 | **TEMPLATED** — substitute a freshly minted MaaS API key before enabling |

`devspaces.yaml` and `observability.yaml` **migrated** to the `bootstrap-infra`
Helm chart (`automation/gitops/bootstrap-infra`, wired to the ArgoCD `bootstrap`
app on the lab cluster) — the platform prerequisites (RHOAI, GPU, RHCL/Kuadrant,
monitoring operators, Dev Spaces, EvalHub chain, observability fixes) are
GitOps-managed there now and must not be applied from here anymore.

## Apply

```sh
export KUBECONFIG=~/.kube/config.ai-inference
# 1. verify the rendered output
kustomize build automation/gitops/workshop-apps
# 2. mint a fresh MaaS API key (1h expiry — see module-03) and substitute it
#    into maas-credentials-secret.yaml, then uncomment that resource
# 3. apply
oc apply -k automation/gitops/workshop-apps
```

The platform prerequisites themselves are NOT applied here — they come from the
`bootstrap-infra` Helm chart via the ArgoCD `bootstrap` app on the lab cluster.

## Secrets

The MaaS API key is runtime-minted per session (1h expiry) and is never
committed. The `maas-credentials-secret.yaml` file contains a placeholder
only. Model tokens come from `oc create token model-tester -n lab-user-dev`.
