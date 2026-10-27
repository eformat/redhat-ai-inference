# Module 2: Evaluate with EvalHub — tracking list

Module 2 (`content/modules/ROOT/pages/module-02-evaluate-benchmark.adoc`): the
page is a 478-line product manual with 4 blank/error screenshots and
placeholder URLs that do not match the 9B deployment. Rebuild: verify → write
→ capture, mirroring the module-1 approach.

## Verified — environment + flow (2026-10-27, app-of-apps cluster)

- [x] VERSIONS: RHOAI `rhods-operator.3.6.0-ea.2` (CSV); EvalHub server **1.0.2**
      (`odh-eval-hub-rhel9` image label `org.opencontainers.image.version:
      1.0.2`); MLflow CR/server `3.15.2` (`odh-mlflow-rhel9`); the trustyai
      module runs INSIDE the RHOAI operator (no separate CSV) in 3.6-ea2.
      Workstation CLI = `eval-hub-sdk` 1.0.5 (PyPI latest 1.0.6) —
      forward-versioned client vs the 1.0.2 server, backward compatible,
      verified working end-to-end.
- [x] CR CREATION ORDER CORRECT: MLflow CR (02:35:50) → mlflow deployment
      (02:35:52) → EvalHub CR (02:36:14) → evalhub deployment (02:36:21).
      The EvalHub CR is created after the MLflow CR; the generated evalhub
      deployment has MLFLOW_TRACKING_URI + MLFLOW_WORKSPACE set.
- [x] TENANT LABEL (Mike's suggestion — saves all per-resource RBAC):
      `evalhub.trustyai.opendatahub.io/tenant: "true"` on `lab-user-dev`
      makes the evalhub CLI work as **lab-user1** with `--token $(oc whoami
      -t)`. The proxy-access Role (bound to system:authenticated) grants
      evalhubs/proxy; the service authorizes tenant namespaces via the label.
      WITHOUT it lab-user1 403s (partial LMEval legacy RBAC only: evalhubs
      list + lmevaljobs create; providers/evaluations denied). Label added to
      `workshop-apps/namespace-labels.yaml` + applied live. A ClusterRoleBinding
      rhods-admins → aggregate-evalhub-permissions was tried and REVERTED —
      unnecessary with the tenant label (the aggregate role only aggregates
      into OpenShift admin, which lab-user1 does not have — custom
      data-science-admingroupcluster-role instead).
- [x] MISSING-NETWORK-LABEL ROOT CAUSE (the "Pending forever" bug): the
      redhat-ods-applications namespace-wide default-deny ingress policy only
      allows from namespaces labeled `opendatahub.io/generated-namespace:
      "true"` (dashboard-created projects), the ingress router, or monitoring.
      lab-user-dev lacked that label → the eval pods' status-event POSTs to
      the EvalHub service TIMED OUT (context deadline exceeded, sidecar
      proxy.go:111) and the run stayed Pending in the dashboard even though
      the K8s jobs Completed. FIX: label lab-user-dev
      `opendatahub.io/generated-namespace=true` (same class as the 2026-10-25
      dashboard-label gap). Added to `workshop-apps/namespace-labels.yaml` +
      applied live. NOT a GPU scheduling issue — the eval pods are tiny
      (adapter + sidecar proxy, no GPU) and run on the worker.
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
- [x] FULL EVAL VERIFIED END-TO-END (2026-10-27, job 48962059): submit as
      lab-user1 → pods run in lab-user-dev → benchmarks complete → status
      events reach the server → State=completed. REAL results: arc_easy
      acc 0.9 / acc_norm 0.7, truthfulqa_mc1 acc 0.4 (10 examples, stderr
      ~0.1-0.16). Runtime ~3.5 min end to end.
- [x] DISK-PRESSURE GOTCHA: the worker node hit DiskPressure (image pulls:
      vLLM ~20 GB + modelcar 11.6 GB + the eval job image) → the eval pods
      went Pending (untolerated taints: worker disk-pressure + GPU node's
      nvidia.com/gpu) AND the evalhub service marked the job FAILED with a
      stale "pod unschedulable" even though the pods scheduled and ran after
      the GC cleared the taint. Re-run clean on a healthy node; deleting the
      failed jobs' pods helps GC. Documented as a troubleshooting note.
- [x] DASHBOARD: the Evaluations page RENDERS on this cluster (no error
      state — that was the prelude2 gap) and shows the runs (Pending/Failed/
      Completed) filtered to lab-user-dev via the tenant label.

## MLflow root cause + fix (2026-10-27)

- [x] MLflow server runs with `--enable-workspaces
      --workspace-store-uri=kubernetes:// --app-name=kubernetes-auth
      --static-prefix=/mlflow` — workspaces ENABLED and required.
- [x] WORKSPACE MECHANISM: the header is `X-MLFLOW-WORKSPACE`, and each
      workspace maps **1:1 to a namespace**. `X-MLFLOW-WORKSPACE: lab-user-dev`
      resolves; `redhat-ods-applications` does NOT ("Workspace not found in
      the Kubernetes cluster"). The evalhub server's default
      MLFLOW_WORKSPACE=redhat-ods-applications is wrong for workspaces mode.
- [x] TRACKING URI BUG: the API is served under the `/mlflow` static prefix —
      `/api/2.0/mlflow/experiments/search` + a VALID workspace → 404;
      `/mlflow/api/2.0/mlflow/experiments/search` + the same workspace → 200.
      The EvalHub CR's MLFLOW_TRACKING_URI lacked the prefix → the eval jobs'
      sidecar configs inherited it → the run-time logging 404'd silently
      (mlflow_run_id: None).
- [x] FIX LANDED (chart): the EvalHub CR's MLFLOW_TRACKING_URI in
      `automation/gitops/maas/templates/50-evalhub.yaml` now carries the
      prefix (`https://mlflow.redhat-ods-applications.svc.cluster.local:8443/
      mlflow`), lint clean. The sidecar config gets the tenant workspace
      (lab-user-dev) per job already — only the URI was wrong.
- [x] FIX VERIFIED END-TO-END (2026-10-27): push → sync (`rhai-maas`) → the
      operator re-rendered the evalhub deployment (new pod with the prefixed
      URI) → re-ran the eval → **mlflow_run_id =
      07c04f2a2fcf4bef9708ec31b934fe5a** — the run logged to MLflow and
      appears in the dashboard's Experiments page (Develop & train →
      Experiments → `nemotron-9-eval` → Evaluation runs) with the metrics:
      acc 0.9, acc_stderr 0.0999, acc_norm 0.7, acc_norm_stderr 0.1527,
      overall_score 0.9.
- [x] `--experiment <name>` WORKS at submission with the prefixed URI (the
      earlier "Workspace context is required" was the URI 404ing, not a
      missing header) — the experiment `nemotron-9-eval` was created and the
      runs land in it. NOTE: the workspace must be the TENANT namespace —
      `redhat-ods-applications` does not resolve as a workspace.
- [x] MLFLOW COMPARISON VIEW UNBLOCKED: the runs are in MLflow → screenshot
      204 (the comparison view) is captureable. ALSO a good extra screenshot:
      the dashboard's Experiments page (Experiments → <experiment> →
      Evaluation runs) showing the runs with metrics — pairs with Exercise 4.

## Screenshots — DONE (2026-10-27, all 1600x900 real captures)

- [x] `201-evaluations-page.png`: the Evaluations page (/evaluation) with the
      runs list (Running + Complete + Failed — realistic)
- [x] `202-start-evaluation-run.png`: the filled Start evaluation run form —
      external endpoint flow (model name + the gateway URL + the auth secret
      name + "Connection established successfully") + Benchmark parameters
      expanded with the tokenizer JSON
- [x] `202b-run-in-progress.png`: the run detail dialog mid-run — "Elapsed
      time: 1m 16s", the benchmark tree In progress, Stop evaluation
- [x] `202c-run-events-log.png`: the same dialog's Events log tab
- [x] `203-evaluation-results.png`: the results view — Result 55%, Arc Easy
      70% / Truthfulqa Mc1 40% (Pass), the benchmark threshold 25%, the tabs
      (Overview/Model metrics/System metrics/Traces/Artifacts)
- [x] `204-run-comparison.png`: the comparison view — "Comparing
      nemotron-9-baseline and nemotron-9-recheck" with the Parallel
      Coordinates Plot (the visualization tabs: Scatter/Box/Contour)
- [x] `205-mlflow-experiments.png`: the dashboard's Experiments page —
      nemotron-9-baseline → Evaluation runs with the per-benchmark runs and
      the metric columns (acc, acc_stderr, overall_score, acc_norm)

## Findings from the capture pass (2026-10-27)

- [x] DASHBOARD FLOW REQUIRES THE TOKENIZER TOO: the dashboard-submitted eval
      failed with the SAME HF tokenizer error — the "Benchmark parameters"
      section needs `{"num_examples": 10, "tokenizer": "nvidia/
      NVIDIA-Nemotron-Nano-9B-v2"}` (both flows, not just the CLI)
- [x] DELETED-EXPERIMENT NAME GOTCHA: after Mike deleted the MLflow result,
      re-creating the experiment with the SAME name failed — "experiment
      nemotron-9-eval is not active after create" (MLflow keeps deleted
      experiment names). Use a new experiment name (troubleshooting note)
- [x] THE MODEL DROPDOWN DOES NOT LIST THE DEPLOYED MODEL: the "Choose model"
      dropdown only shows "Other (External endpoint)" — the deployed 9B model
      is not listed as an AI asset endpoint. The docs use the external
      endpoint flow: Model name + the gateway URL + the auth secret name
      (exactly the verified CLI shape) + "Validate connection"
- [x] RUNS ARE FAST: 10 examples × 2 benchmarks completes in ~1-2 min
      (Pending ~30-50s for the pods + ~1 min Running). 50 examples gives a
      ~3-4 min run — use a larger sample if you want time to explore the
      in-progress view
- [x] EVALUATIONS PAGE URL: /evaluation (not /evaluations — direct navigation
      404s; navigate via Develop & train → Evaluations)
- [x] COMPARE FLOW: select 2+ completed runs in the list → Compare → select
      the benchmarks per run → Compare → the comparison view (Parallel
      Coordinates/Scatter/Box/Contour tabs)

## Pending — rewrite module-02 (DONE — 2026-10-27)

- [x] REWRITTEN: module-02-evaluate-benchmark.adoc 478 → ~300 lines, concise
      working instructions. Structure: Ex 1 Set up the EvalHub CLI (pip
      install --user eval-hub-sdk, config base_url/tenant/token + the
      model-auth secret) → Ex 2 Run a benchmark evaluation (the verified CLI
      shape: gateway URL, --model-auth-secret, --experiment, --param
      num_examples=10 + the tokenizer param; monitor; results) → Ex 3 Run an
      evaluation from the dashboard (the external endpoint flow + the
      Benchmark parameters tokenizer + the during-run progress + the results
      view) → Ex 4 Compare runs and make it repeatable (the comparison view +
      the MLflow experiments page + the evaljob.yaml config with `id:` per
      benchmark — NOT benchmark_id) + Troubleshooting (the tokenizer param,
      Pending-forever = the namespace labels, the stale disk-pressure
      failure, the deleted-experiment name, the MaaS 4 MiB note).
- [x] All 7 screenshots wired in (201, 202, 202b, 202c, 203, 204, 205) with
      descriptive alt text, width=700.
- [x] Antora build 0 errors (exit 0) + secrets clean on the changed files.
- [x] INSTALL INSTRUCTIONS BULLETPROOFED (2026-10-27, Mike hit `evalhub:
      command not found` on the jumphost): the install step now covers the
      Python version check, `pip3 install --user eval-hub-sdk`, the
      `~/.local/bin` PATH export (the #1 gotcha — the installer drops the
      binary off-PATH), and the venv fallback for
      `externally-managed-environment` (RHEL images refuse bare pip installs).
- [ ] Optional polish: the module-02 nav title/overview wording review,
      ph-check.py if the publishing house runs it.
