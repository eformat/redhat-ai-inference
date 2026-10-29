# Module 4 — Integrate the Application (Dev Spaces + chat client) — verify log

## CLIENT BUGS FOUND + FIXED (2026-10-29, verify-first)

Two bugs were killing the maas-chat-client pod:

1. **Secret missing** — the events showed `Error: secret "maas-credentials" not
   found` → CreateContainerConfigError. The learner flow (docs Ex 2) creates
   the Secret before Ex 3 deploys, but a manual apply without the Secret
   leaves the pod stuck. The gitops kustomization keeps
   maas-credentials-secret.yaml TEMPLATED/commented (per-session key) — the
   e2e creates it from vars (no_log).
2. **Reasoning-model crash (the deeper one)** — with `max_tokens=256`, the
   Nemotron reasoning model burns the budget on `reasoning` (1322 chars),
   `finish_reason: length`, and `content` comes back **null** →
   `choice['message']['content'].strip()` → AttributeError → CrashLoopBackOff.
   WORSE: with thinking ON, even `max_tokens=1000` + `finish: stop` returns
   content=null (the answer stays in reasoning). VERIFIED FIX: the request
   must pass `chat_template_kwargs: {"enable_thinking": false}` AND a big
   enough max_tokens → clean one-sentence answer in content, finish: stop,
   ~2.5s, reasoning_tokens: 0.

- [x] Client fixed in `maas-chat-client/maas_chat_client.py`: enable_thinking
      false + max_tokens default 1000 + a `response_content()` helper
      (falls back to `reasoning` if content is empty) + a generic
      `except Exception` in BOTH loops so one bad response can't kill the pod.
- [x] Synced the two other copies: `qa-automation/e2e.yml` (inline
      maas_chat_client_py — the e2e does NOT read the repo file) and
      `automation/gitops/workshop-apps/maas-chat-client.yaml` (the ConfigMap).
      VERIFIED identical to the repo file; ansible --syntax-check OK.
- [x] Tested interactively as lab-user1 with a freshly minted key
      (sk-oai-N... in /tmp/opencode/pw/maas-key.json — NEVER commit): clean
      answer + token usage.
- [ ] Pod still to be deployed per the learner flow (Secret → ConfigMap →
      apply) after the commit lands; capture the REAL log output for the docs.

## DEV SPACES — no prepared workspace (2026-10-29, Mike's question)

- **Zero DevWorkspaces existed cluster-wide** — the docs' "prepared workshop
  workspace" was aspirational; nothing provisions one. The repo's
  `.devfile.yaml` is the PUBLISHING-HOUSE AUTHORING devfile (Claude CLI +
  litellm against another cluster) — NOT a learner devfile.
- Factory-from-git-URL test (as lab-user1, "Import from Git" → repo URL →
  Create & Open → trust Continue): the workspace pod started (project-clone
  init Completed) but **failed: node low on ephemeral-storage** — the UDI
  image (2GB+) filled the control-plane node → disk-pressure taint →
  eviction; the retry pod can't schedule (the GPU node is
  nvidia.com/gpu=dedicated tainted). LESSON: learner devfiles must use a
  LEAN image, not UDI.

## CUSTOM DEVFILE REGISTRY — the decision (Mike: custom Devfile, ready for users)

- CheCluster CRD (3.6-ea2) knob: `spec.components.devfileRegistry.
  externalDevfileRegistries` — list of `{url}` only.
- **Registry format** (discovered from the dashboard's own network log):
  `{registry}/devfiles/index.json` →
  `[{displayName, description, tags, icon, links: {v2: "/devfiles/<name>.yaml"}}]`
  + `/devfiles/<name>.yaml` + `/images/<name>.svg` (relative paths).
- FIRST attempt (registry Deployment + Route + values.ingressDomain knob)
  REJECTED by Mike — the domain was hardcoded. FINAL SHAPE: **serve the
  registry from the repo itself** — raw.githubusercontent.com is CORS-enabled
  (`access-control-allow-origin: *` verified), so NO route, NO registry
  deployment, NO domain anywhere:
  - `automation/gitops/devfile-registry/devfiles/index.json`
  - `automation/gitops/devfile-registry/devfiles/maas-chat-client.yaml`
  - `automation/gitops/devfile-registry/images/maas-chat-client.svg`
  - CheCluster: `externalDevfileRegistries: [{url: https://raw.githubusercontent.com/rhpds/redhat-ai-inference/main/automation/gitops/devfile-registry}]`
- Learner devfile: lean image `quay.io/rhpds/openshowroom-terminal-ocp:2026-03-11`
  (the lab terminal image — python3 3.12, oc, curl, git, jq verified in the
  showroom pod; ~1/3 of UDI so no disk-pressure), mountSources /projects,
  `projects:` section clones rhpds/redhat-ai-inference from main, trust
  prompt disabled via che-code vscode-preferences.
- [ ] AFTER Mike pushes: ArgoCD rhai-rhoai syncs → verify the sample appears
      on the Create Workspace page as lab-user1 → create it → the repo
      pre-clones → oc/python3 in the terminal → THEN rewrite module-04 Ex 1
      with the real flow + captures.

## GOTCHAS (this session)

- **ArgoCD short-name gotcha AGAIN**: `oc get applications -A` resolves to the
  console app.k8s.io kind ("No resources found") — the FULL
  `oc get applications.argoproj.io -n openshift-gitops` shows the real apps:
  bootstrap, rhai-maas, rhai-model-serving, rhai-observability,
  rhai-operator-configs, rhai-operators, **rhai-rhoai** (the rhoai chart —
  the module 4 sync path). The pool hub's rhoai ApplicationSet applies the
  POOL repo's applications/rhoai (NO CheCluster there) — the CheCluster comes
  from THIS repo's chart via rhai-rhoai.
- lab-user1 kubeconfig was lost (tmp cleaned) — re-login: `oc login <api> -u
  lab-user1 -p <password>`; that CLOBBERS ~/.kube/config.ai-inference's admin
  context (oc login writes the current file) — Mike restored admin.
- The kubeconfig fallback: if /tmp/opencode/kubeconfig-lab-user1 is missing,
  log in fresh; store keys in /tmp/opencode/pw/ (gitignored).
- The internal devfile registry serves via the dashboard proxy path
  /dashboard/devfile-registry/... (the gateway proxies it); external
  registries are fetched by the BROWSER (CORS matters — GitHub raw passes).
- The MaaS key mint endpoint: POST /maas-api/v1/api-keys with the lab token;
  response keys: createdAt, ephemeral, expiresAt, id, key, keyPrefix, name,
  subscription.
