# Model switch: Nemotron 3 Nano 30B (L40S) → Nemotron Nano 9B v2 (L4)

Tracking list for switching the lab from the 30B model (needs ~37.6 GB, L40S) to
the 9B model (11.6 GB, fits the lab's g6.2xlarge / L4 24 GB node).

## Done

- [x] Module 1 text: model choice narrative (9B v2 FP8, 11.6 GB VRAM, L4 fit)
- [x] Module 1 text: catalog flow (9B card), deployment step (`nemotron-nano-9b-v2`, GPU serving profile, accelerator config)
- [x] Runtime args: copy block updated to minimal set — `--trust-remote-code` + `--max-model-len=131072`
  - the nano_v3 reasoning parser from the 30B args is for the 3-family and the
    9B modelcar does NOT ship a nano_v2 parser plugin
- [x] `nemotron_v3` reasoning parser found BUILT IN to the RHOAI vLLM image
      (no plugin needed) — Nemotron reasoning stays in-platform, USA-friendly
- [x] Args patch applied live: LIS `VLLM_ADDITIONAL_ARGS` =
      `--trust-remote-code --max-model-len=131072 --reasoning-parser nemotron_v3`
      (verified in `ps`: `--reasoning-parser nemotron_v3` present)
- [x] Stop/start verified: `serving.kserve.io/stop=true` / `=false` annotations
      stop and restart the deployment cleanly (frees the kueue GPU slot)
- [x] Accelerator config renamed: `vllm-nvidia-l40s-gpu-single-node` →
      `vllm-nvidia-gpu-single-node` (display-name "vLLM NVIDIA GPU Single Node")
- [x] 9B deployed via wizard: gpu-serving profile + accelerator config; pod has
      2 CPU/16Gi/1 GPU, l4-gpu toleration, scheduled on the GPU node
- [x] Model loaded: 9.47 GiB on the L4 — no OOM; LIS READY True
- [x] Inference verified: chat completion via gateway + model-tester token
- [x] Hostname Job drafted: `inference-gateway-status` (SA + ClusterRole +
      RoleBinding + Job, wave 3 hook) patches the Gateway's https listener
      hostname with `inference-gateway.apps.<domain>` read live from
      ingress.config/cluster (the maas-gateway-status precedent)

## Verified — args patch (reasoning parser)

- [x] Response test with `--reasoning-parser nemotron_v3`: **WORKS** — the
      built-in `nemotron_v3` parser matches the 9B v2 format
- [x] Separation confirmed: `finish: stop`, 1296 completion tokens;
      `reasoning` holds the chain-of-thought (2931 chars), `content` holds only
      the formatted answer (`**Answer:** 391` for "What is 17 * 23?")
- [x] Note: the 9B reasons extensively (~300 tokens of thinking on simple
      arithmetic) — max_tokens 500 was consumed by reasoning (finish: length);
      examples in docs should use higher budgets (e.g. 3072)
- [x] `hy_v3` fallback not needed

## App-of-apps restructure (DONE — migrated 2026-10-27)

- [x] The 74-resource bootstrap-infra chart split into 6 functional Helm
      charts wired as an app-of-apps (`automation/gitops/app-of-apps/`):
      operators (31), rhoai (7), operator-configs (4), maas (21),
      model-serving (9), observability (2) — total 74, verified.
      Each child chart: Chart.yaml + values.yaml + templates/; knobs per chart
      (operators: catalog fragment, rhoai: lab admin user, maas: postgres
      dummy creds). Child apps wave-ordered 0-5; per-app prune + retry +
      RespectIgnoreDifferences; the ConfigMap /data drift ignore carried to
      the apps with controller-mutated ConfigMaps.
- [x] MIGRATED: the push landed before prune was disabled — the root hit a
      ComparisonError ("app path does not exist") which luckily BLOCKED the
      prune (no comparison = no desired state = nothing deleted). Then the
      README order completed: prune off → root pointed at app-of-apps → the
      six children created and adopted the existing resources (no churn) →
      all Synced/Healthy with the full 74-resource inventory → prune
      re-enabled + the stale root-level ignoreDifferences removed. Smoke
      test: /v1/models via the gateway OK, model READY.
- [x] Debugging is now per-function: `rhai-model-serving` for gateway issues,
      `rhai-maas` for MaaS, etc. instead of the 74-resource wall.


- [x] Push chart changes: accelerator config rename + inference-gateway-status
      Job (74 resources, lint clean)
- [x] Chart pushed and synced: ArgoCD `bootstrap` app Synced/Healthy at the
      commit carrying the rename + Job; old `vllm-nvidia-l40s-gpu-single-node`
      config pruned; `vllm-nvidia-gpu-single-node` in place
- [x] Hostname Job ran (Complete) and patched the Gateway listener hostname
- [x] FIXED: the first run produced a double-apps hostname
      (`inference-gateway.apps.apps.<cluster-domain>`) — the ingress.config
      domain ALREADY includes the `apps` prefix; the Job script now builds
      `inference-gateway.${DOMAIN}` (the maas-gateway precedent, same
      convention). Pending: push → sync → Job re-run → verify the hostname and
      the external URL resolves
- [x] Verify the external URL `https://inference-gateway.apps.<cluster-domain>/...`
      resolves — VERIFIED END-TO-END (line 127 below) + re-confirmed after the
      app-of-apps migration: `/v1/models` via the external URL → HTTP 200

## Screenshots (recaptured for the 9B flow)

- [x] Recaptured all 10 Module 1 screenshots at 1600x900 for the 9B flow:
      catalog (nemotron search + 9B card visible), 9B model card, wizard model
      details (9B modelcar URI), wizard deployment ("GPU serving (NVIDIA GPU)"
      profile + "vLLM NVIDIA GPU Single Node" accelerator), wizard advanced
      (model-tester + the 3 args), wizard review, deployment status (Ready on
      AI asset endpoints), endpoints dialog
- [x] Wizard walked WITHOUT clicking Deploy (screenshots only) the first time —
      but the deploy wizard opened in update/cleanup mode for the already-
      deployed model and Cancel DELETED the live deployment (events: the
      config cleanup attempted mid-deletion). GOTCHA for docs/QA: never reopen
      the deploy wizard for an already-deployed model — it is not safe to walk
      it without deploying.
- [x] Redeployed the 9B via the wizard for real (name `nemotron-nano-9b-v2`,
      gpu-serving + vLLM NVIDIA GPU Single Node, model-tester SA, the 3 args,
      AI asset endpoint) — READY True again, inference smoke-tested OK
- [x] AFTER the hostname fix sync: recaptured `101-inference-endpoint.png`
      (1600x900) with the correct external URL — superseded again by the full
      maas-gateway pattern fix; final recapture at line 140 below
- [x] SNI finding: once the Gateway listener has a hostname, connections with
      a different SNI are reset ("Connection reset by peer") — the dialog's
      Internal API endpoint (service-name SNI) does NOT work with a listener
      hostname; the docs use the external hostname (resolves in-cluster via
      the router wildcard, SNI matches) — same shape as the maas gateway
- [x] 503 ROOT CAUSE (final): the listener hostname and the reencrypt Route
      are incompatible — the router's reencrypt backend sends
      SNI = the Service name (`verifyhost` in the generated haproxy config),
      but a listener hostname makes the gateway accept ONLY that hostname's
      SNI → the gateway resets the router's backend connection → 503
      ("Application is not available" page). Verified: no-SNI → reset,
      service-name SNI → reset, external-hostname SNI → 200.
- [x] FIXED with the full maas-gateway pattern: the Job NO LONGER patches the
      listener hostname (the chart Gateway has no hostname — ArgoCD's
      re-apply clears any stale one); it patches the Service status with the
      external hostname (reflected into gateway.status.addresses, which the
      KServe URL and the endpoints dialog derive from) and creates the Route.
      ClusterRole: gateways patch dropped, services/services-status added.
- [x] ClusterIP Service FORBIDS the status.loadBalancer.ingress patch
      ("may only be used when spec.type is 'LoadBalancer'") — FIXED: the
      chart's parametersRef ConfigMap (`openshift-ai-inference-config`)
      service override is now `spec.type: LoadBalancer` (the maas
      gateway's Service is LoadBalancer for exactly this reason). On AWS the
      cloud provider also provisions a real LB address; the Job's status
      patch then sets the Route hostname. reference:
      ph-deploy-configure-rhoai/manifests/05-maas/gateway/{clusterip,loadbalancer}/
- [x] VERIFIED END-TO-END: Service type LoadBalancer with the status hostname,
      gateway.status.addresses = the external hostname, the LIS URL = the
      external hostname, and the EXACT docs flow works via DNS (router →
      route → gateway → model): finish: stop, reasoning separated. The
      Endpoints dialog shows the correct external URL.
- [x] NOTES on the landing sequence: (1) the app's ignoreDifferences
      blanket-ignores ConfigMap /data, so the chart's ConfigMap change never
      applied in-cluster — the Job's spec.type patch is the self-healing
      workaround (fresh clusters: the controller renders ClusterIP, the Job
      fixes it). (2) sync operations kept terminating at ~2.5 min because
      ArgoCD waits on operator Subscriptions' health in the early waves —
      the hook Job never ran; a manual sync via the Application CR's
      operation field ran it to completion.
- [x] Endpoint screenshot recaptured with the correct external URL
- [x] Exercise 3 split into 3 CLI steps: MODEL_URL from
      `oc get llminferenceservice -o jsonpath='{.status.url}'`, TOKEN from the
      deployment's `model-tester-<model>-sa` secret (base64 -d), then the curl —
      verified end-to-end (the UI token works; finish: stop, reasoning
      separated)
- [x] New screenshot `101-token-secret.png` (1600x900): the deployment row's
      Token authentication section with the token name + revealed secret


## Images + docs (all done)

- [x] Recapture Module 1 screenshots for the 9B flow:
      `101-model-catalog.png` (nemotron-nano-9b search),
      `101-catalog-model-card.png` (9B card),
      `101-wizard-model-details.png` (9B modelcar URI:
      `oci://registry.redhat.io/rhelai1/modelcar-nvidia-nemotron-nano-9b-v2-fp8-dynamic:1.5`),
      `101-wizard-deployment.png` (gpu-serving + "vLLM NVIDIA GPU Single Node"),
      `101-wizard-advanced.png` (new args),
      `101-wizard-review.png`
      (all 10 recaptured at 1600x900 — see the Screenshots section above)
- [x] Module 1 "What the wizard creates": actual resource name
      (`redhatainvidia-nemotron-nano-9` — model-derived, truncated), modelcar
      URI (`rhelai1/...:1.5`), resources, args incl. the reasoning parser
- [x] Module 1 Exercise 3: gateway URL, model name `redhatainvidia-nemotron-nano-9`,
      response example with the `reasoning` field (real captured response,
      finish: stop, 325 completion tokens)
- [x] Hardware profile display-names renamed to GPU-generic: profile
      display-name "GPU serving (NVIDIA GPU)", GPU identifier "NVIDIA GPU"
      (was "GPU serving (NVIDIA L40S)" / "NVIDIA L40S GPU" — the L4 lab made
      the L40S names misleading in wizard screenshots)
- [x] Modules 3-6 + getting-connected updated: 9B model name (pod names use
      the -kserve suffix), L4 node references, Nemotron Nano 9B v2 display names
- [x] e2e.yml updated: model_name `redhatainvidia-nemotron-nano-9`, 9B
      modelcar, wizard-preset serving image (digest-pinned), verified args,
      l4-gpu toleration, 2/16Gi resources
- [x] healthcheck.yml + publishing-house/spec.yaml updated: L4 gpu_type
      (g6.2xlarge), ai_model_name filled with the 9B
- [x] rac/ records updated: model-serving decision superseded to the 9B,
      architecture design + requirements on L4/9B

## Open — router 504 on long completions (fix landed, needs push)

- [x] FOUND (2026-10-27): non-streaming completions via the external URL
      intermittently 504 ("Gateway Time-out") — the OpenShift router's default
      30s backend timeout vs the 9B reasoning model: "What is 6 * 7?" takes
      ~20s direct (434 completion tokens, finish: stop); under workshop load or
      longer reasoning it tips past 30s. /v1/models is unaffected (fast).
      Streaming clients never hit it (data flows continuously) — the risk is
      the docs' Exercise 3 curl (max_tokens 3072, worst case ~150s on the L4).
- [x] FIX: `haproxy.router.openshift.io/timeout: 300s` annotation added to
      `inference-gateway-route` in
      `automation/gitops/model-serving/templates/50-inference-gateway.yaml`
      (lint clean, 9 resources).
- [x] Push → sync → the Route gets the annotation → VERIFIED (2026-10-27):
      `timeout: 300s` on `inference-gateway-route`, non-streaming curl through
      the external URL works (finish: stop).
      GOTCHA: pushing a HOOK-ONLY change does not trigger the automated sync —
      hook resources are excluded from the diff, so the app stays "Synced" and
      auto-sync never fires (the Job re-ran at 05:42 from the PREVIOUS commit,
      `route unchanged`). Needed a manual sync via the Application CR
      `operation` field pinned to the pushed revision → Job re-ran →
      `route configured`.
- [ ] Optional: same annotation on `maas-gateway-route` (45-maas-gateway.yaml)
      — module 4's MaaS playground streams so it's safe, but a non-streaming
      curl against the MaaS gateway would hit the same 30s limit. Deviates
      from the ph-deploy-configure-rhoai pool pattern — Mike's call.

## Open — module 2 (EvalHub) verify pass (2026-10-27)

Environment + flow findings, all verified live on the app-of-apps cluster:

- [x] VERSIONS: RHOAI 3.6-ea2 ships EvalHub server **1.0.2**
      (`odh-eval-hub-rhel9` image label `org.opencontainers.image.version:
      1.0.2`, `version: v3.6.0-ea.2`); workstation CLI = `eval-hub-sdk` 1.0.5
      (PyPI latest 1.0.6) — forward-versioned client vs the 1.0.2 server,
      backward compatible, verified working end-to-end. The trustyai module
      runs INSIDE the RHOAI operator (no separate CSV) in 3.6-ea2.
- [x] TENANT LABEL (Mike's suggestion — saves all per-resource RBAC):
      `evalhub.trustyai.opendatahub.io/tenant: "true"` on `lab-user-dev`
      makes the evalhub CLI work as **lab-user1** with `--token $(oc whoami
      -t)`. The proxy-access Role (bound to system:authenticated) grants
      evalhubs/proxy; the service authorizes tenant namespaces via the label.
      WITHOUT it lab-user1 403s (partial LMEval legacy RBAC only: evalhubs
      list + lmevaljobs create; providers/evaluations denied). Label added to
      `workshop-apps/namespace-labels.yaml` + applied live.
- [x] REVERTED: the ClusterRoleBinding rhods-admins → aggregate-evalhub-
      permissions I added to the maas chart — unnecessary with the tenant
      label (aggregate role only aggregates into OpenShift admin, which
      lab-user1 does not have — custom data-science-admingroupcluster-role).
- [x] EVALHUB ENDPOINT: Route `evalhub-redhat-ods-applications.apps.<domain>`
      (the service itself: evalhub.redhat-ods-applications.svc:8443);
      `evalhub config set base_url https://evalhub-redhat-ods-applications
      .apps.<domain>` + `config set tenant lab-user-dev`.
- [x] MODEL AUTH: the eval runs against the gateway URL (same as module 1's
      Exercise 3 — the external hostname resolves in-cluster, valid cert that
      chains to the pod's SA ca.crt, so NO TLS config needed) with a secret
      `--model-auth-secret` carrying key `api-key` = the model-tester token.
      The job's sidecar proxy resolves the auth ref. Students CAN create
      secrets in lab-user-dev (their project).
- [x] TOKENIZER GOTCHA: the lm_evaluation_harness adapter runs
      local-completions via the sidecar proxy correctly, but loads the
      TOKENIZER from HuggingFace by model name — `redhatainvidia-nemotron-
      nano-9` is not an HF ID → job fails with "not a valid model identifier
      listed on huggingface.co". Fix: `--param tokenizer=nvidia/
      NVIDIA-Nemotron-Nano-9B-v2` (the modelcar's HF tokenizer).
- [x] BENCHMARK IDS: the docs' `mmlu`/`hellaswag` IDs DO NOT EXIST in this
      build (191 benchmarks; variants like cmmlu_*, global_mmlu_full_*,
      darijahellaswag). Verified English quick picks: `arc_easy` (reasoning,
      acc/acc_norm), `truthfulqa_mc1` (safety, acc),
      `global_mmlu_full_en_high_school_mathematics` (math, exact_match/acc).
- [x] JOB RUNS IN THE STUDENT'S PROJECT: eval pods (one K8s Job per
      benchmark, adapter + sidecar proxy) run in lab-user-dev with the
      evalhub job ID prefixed — visible via `oc get jobs -n lab-user-dev`.
- [x] DISK-PRESSURE GOTCHA: the worker node hit DiskPressure (image pulls:
      vLLM ~20 GB + modelcar 11.6 GB + the eval job image) → the eval pods
      went Pending (untolerated taints: worker disk-pressure + GPU node's
      nvidia.com/gpu) AND the evalhub service marked the job FAILED with a
      stale "pod unschedulable" even though the pods scheduled and ran after
      the GC cleared the taint. Re-run clean on a healthy node.
- [ ] Verify a full eval completes + results (arc_easy + truthfulqa_mc1,
      num_examples 10) — IN PROGRESS, job bc375247-98dd-4a89-8291-4147b1a29651.
- [ ] Verify the dashboard Evaluations page renders (was an error state on
      prelude2; EvalHub is Ready here) + the Start evaluation run dialog +
      results view + MLflow comparison view (screenshots 201-204).
- [ ] Rewrite module-02 concise: actual values (model name, project,
      endpoints), real benchmark IDs, the verified CLI flow (whoami -t +
      tenant label + auth secret + tokenizer param), dashboard/CLI split.
