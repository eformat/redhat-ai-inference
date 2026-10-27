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
- [ ] Push → sync (`rhai-maas`) → the operator re-renders the evalhub
      deployment → the pod rolls → re-run the eval → verify `mlflow_run_id`
      is set and the run appears in the MLflow UI.
- [ ] Re-test `--experiment <name>` at submission: the server's own
      experiment-validation call sends NO workspace header ("Workspace context
      is required") — may still fail even with the URI fixed (a 1.0.2 server
      gap). If it fails, the docs skip `--experiment` and rely on run-time
      logging with the default experiment.

## Pending — screenshots (4)

- [ ] `201-evaluations-page.png`: the Evaluations page with a completed run
      visible (works — the stale Pending/Failed test records can be cleared
      by restarting the evalhub pod, sqlite on the pod resets the records)
- [ ] `202-start-evaluation-run.png`: the Start evaluation run dialog
      (benchmarks, name, source) — if the dialog's MLflow experiment selector
      works, include it; else document around it
- [ ] `203-evaluation-results.png`: the completed run's results view
- [ ] `204-run-comparison.png`: GATED on the MLflow fix — the comparison view
      needs the runs logged to MLflow; verify after the sync, else drop/gate
      the screenshot and keep Exercise 4's repeatable-config part

## Pending — rewrite module-02 (concise working instructions)

- [ ] Install step FIRST (the jumphost does NOT ship the CLI):
      `pip install --user eval-hub-sdk` (requires Python >= 3.11)
- [ ] CLI config: base_url = the evalhub Route, tenant = lab-user-dev,
      token = `oc whoami -t` (the tenant label makes this work as lab-user1)
- [ ] Auth secret step: `oc create secret generic model-auth --from-literal
      api-key=<model-tester token>` in lab-user-dev
- [ ] Eval run with the VERIFIED shape: gateway URL from the LIS status,
      `--model-auth-secret model-auth`, `--param num_examples=10`,
      `--param tokenizer=nvidia/NVIDIA-Nemotron-Nano-9B-v2`, benchmarks
      `arc_easy` + `truthfulqa_mc1` (real IDs)
- [ ] Replace the placeholder URLs ({model-name}, {project-namespace}) with
      the actual values (module-1 style), or keep attributes but make them
      resolve to the real lab values
- [ ] Cut the product-manual padding: the 4-concept table, the provider
      table, the metrics/latency sections → brief; keep the troubleshooting
      (the MaaS 4 MiB gateway note) + add the new gotchas (tokenizer param,
      the stale disk-pressure failure, Pending-forever = the namespace label)
- [ ] Exercise 4: keep the repeatable YAML config (`evalhub eval run --config
      evaljob.yaml` — verify the config-file path works), gate/drop the MLflow
      comparison view pending the fix
- [ ] Antora build 0 errors + secrets clean on the changed files
