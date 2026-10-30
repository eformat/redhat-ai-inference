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
## RESOLVED — the workspace WORKS (2026-10-30, after ~8 push cycles)

- [x] **The root cause of every FailedPostStartHook**: the DWO injects its own
      che-code postStart hook (nohup /checode/entrypoint-volume.sh) on the
      tool container. Third-party images (ubi9/python-311) fail it — the
      hook's log redirect /checode/entrypoint-logs.txt hits a permission wall
      (the injector runs as root, creates the PVC dirs root:1001060000; the
      container: uid=1001060000 gid=0, no fsGroup, no supplemental group ->
      read-only on its own workspace). NOT fixable from the devfile:
      storage-type per-user/per-workspace both failed; pod-overrides
      supplementalGroups would have required hardcoding the namespace UID.
- [x] **THE ANSWER (Mike: "you must be missing something - search web")**: use
      Red Hat's UDI (registry.redhat.io/devspaces/udi-rhel9) — the same image
      every built-in Dev Spaces sample uses, BUILT for the che-code hook.
      VERIFIED: the built-in Python sample ran fine (the decisive test); the
      UDI has oc 4.18, python3, curl, git, jq preinstalled (no oc-install
      step needed); the pull secret covers registry.redhat.io.
- [x] FINAL learner devfile (repo root devfile.yaml + the -v3 registry copy,
      identical): UDI image, mountSources /projects, the projects section
      cloning rhpds/redhat-ai-inference from main, the trust prompt disabled.
      NO hardcoding (the image path is a registry path, not an env value).
- [x] **The workspace WORKS**: maas-chat-client-ef3d Running 2/2, the IDE URL
      live, /projects/redhat-ai-inference pre-cloned, all tools present.
- [x] **Debug techniques that worked** (for the checklist):
  - The DevWorkspace's annotations reveal the resolved devfile + the factory
    params (che.eclipse.org/devfile + devfile-source).
  - The performance entries in the browser show which registry URLs the
    dashboard actually fetched (it NEVER fetched the -v2/-v3 index until
    localStorage was cleared — the dashboard caches the sample data in
    localStorage, surviving context restarts).
  - The dashboard's sample-creation flow: links.v2 (index.json) drives the
    CARD LIST; the /index/all entry's links.self drives the CREATION
    resolution (relative links resolve against the registry base's PARENT —
    both must be the ABSOLUTE repo URL).
  - The raw CDN (bne edge) lags pushes by 10-25+ min on the same path;
    query params and etag revalidation are normalized away — a PATH bump
    (the -v2/-v3 dir renames) is the only reliable cache bust.
  - quay.io/rhpds/openshowroom-terminal-ocp went PRIVATE (401, 0 tags) —
    third-party image pulls need verification at AUTHORING time, not just
    repo visibility.
- [ ] NEXT: the module-04 docs rewrite with the real flow (the sample on the
      Create Workspace page -> the workspace with the repo pre-cloned), the
      real screenshots (401: the sample card; 402: the IDE open), the source
      block already synced to the fixed client, the real pod-log output
      captured (assistant> ... [tokens: 29 in / 38 out]).

## REGISTRY V2 API — the real contract (2026-10-30, discovered from registry.devfile.io)

The sample APPEARED from devfiles/index.json (the OLD format) but sample
CREATION failed: the dashboard ALSO fetches `{registry}/index/all` (404 on my
registry) and on failure falls back to treating `links.v2` as a GIT REPO URL
(it appended `.git` to the raw URL → clone 404 → a synthetic DevWorkspace with
NO components + a bogus project named from the file). CONFIRMED working v2
contract (from the real registry + the console error):

- `/index/all` — the metadata list: entries have
  `name, version, displayName, description, type (stack|sample), tags, icon,
  language, projectType, resources, starterProjects, links: {self}, lastModified`
- `/devfiles/{name}` — the DEVFILE CONTENT, matched by the entry's `name`
  (no .yaml suffix — /devfiles/{name}.yaml 404s on the real registry)
- /devfiles/index.json still drives the sample-card LIST for external
  registries; /index/all drives the creation resolution.

- [x] Registry layout fixed: index/all added (name maas-chat-client, type
      sample), the devfile renamed to devfiles/maas-chat-client (name-matched
      path), index.json links.v2 → /devfiles/maas-chat-client. PENDING:
      Mike's commit + push → retest the sample creation (expect: the devfile
      applies, the lean image, the repo cloned at /projects/redhat-ai-inference).

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
