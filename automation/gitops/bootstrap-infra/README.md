# bootstrap-infra (shim)

The former single `bootstrap-infra` Helm chart (74 resources under one ArgoCD
application — painful to debug) was split into per-chart Helm charts wired as
an app-of-apps — see `../app-of-apps/README.md`. The lab provisioning Ansible
still creates the root `bootstrap` Application pointing at this path, so this
chart keeps that reference working: it renders a single Application
(`rhai-app-of-apps`) that points at `automation/gitops/app-of-apps/`, which
creates the wave-ordered child apps.

Chain: `bootstrap` (Ansible-created, this path) → `rhai-app-of-apps` → the
seven `rhai-*` child apps.

Notes:
- `automation/gitops/app-of-apps/` remains the single source of truth for the
  child app definitions — this chart only delegates to it. Do not duplicate
  Application manifests here.
- Clusters whose root app was manually re-pointed directly at
  `automation/gitops/app-of-apps` (e.g. the config.ai-inference2 cluster)
  must NOT apply the `rhai-app-of-apps` Application — two applications
  tracking the same child manifests would fight over them. The shim is only
  for ansible-created roots pointing at this path.
