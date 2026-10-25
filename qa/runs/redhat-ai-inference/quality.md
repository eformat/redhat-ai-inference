# Quality Enrichment Report — redhat-ai-inference

Date: 2026-10-25 · Mode: single-workshop · Skill: zt-rhaibu/quality-enrichment
Cluster during audit: prelude2 (RHOAI 3.6-ea2), e2e re-run green (ok=36 failed=0)

## Triage

- Score before: 1 (+4 pending Phase-2 content-match audit)
- Score after: 0 static; 3 env-gated `// TODO(wrong-capture)` directives remain (sanctioned)

## Phase 1 — RAC validation

- 68 criteria mapped across top-level + module requirements
- 0 GAP, 5 PARTIAL (REQ-001, REQ-004, REQ-022, REQ-101, REQ-102), rest COVERED
- No "## Verified By" sections in any RAC requirement file (7 files checked)

## Phase 2 — screenshot audit (visual content-match, all 11 real captures opened)

Before: 2 OK / 8 WRONG / 1 orphan / 23 placeholders.

| Image | Verdict | Issue |
|---|---|---|
| 001-getting-connected-console | WRONG | logged-in console w/ loading spinner, not login |
| 101-project-layout | WRONG | Projects page mid-load, "Loading" spinner, no project |
| 101-deployment-status | WRONG | dup of 302 capture (byte-identical pair) |
| 101-inference-endpoint | WRONG | dup of same capture |
| 201-evaluations-page | WRONG | "Evaluations unavailable" error (no EvalHub CRs on prelude2) |
| 304-api-key-create | WRONG | "Error loading API keys" error |
| 602-cluster-dashboard | WRONG | "Unable to reach observability dashboards" error |
| 603-usage-dashboard | WRONG | Infrastructure tab, step wants Dashboard tab |
| 401-gen-ai-playground | orphan | empty-state playground ("No available model deployments") |

## Fixes applied

1. 5 screenshots re-captured live from prelude2 (1600x900), topical states verified pixel-by-pixel:
   - 001 → RHOAI dashboard home after login (placed under "Navigating the console")
   - 101-project-layout → Projects page with lab-user-dev visible ("1-3 of 3")
   - 101-deployment-status → AI asset endpoints, model Ready
   - 101-inference-endpoint → Endpoints dialog (external + internal API URLs)
   - 304-api-key-create → populated Create API key dialog (name, subscription, token limit 50,000/1m visible, 30-day expiration)
2. 3.6-era UI prose fixes in module-01: wizard verification + endpoint/token steps now describe the verified path (Gen AI studio → AI asset endpoints → View dialog; token via `oc create token model-tester`); removed 3.5-era "Deployments tab → Token secret" instructions.
3. e2e.yml: M1 labels the project `opendatahub.io/dashboard=true` so it appears in the RHOAI projects UI (the unlabelled namespace was invisible in the projects page — root cause of the earlier "lab-user-dev no longer exists" false reading).

## Phase 3/4 — numbering + quality (second pass)

- Exercise headings: `N.N — Title` → `Exercise N: <sentence-case title>` across all 6 modules; `Learning Objectives` → `Learning objectives`; 25 `section N.N` cross-refs rewritten to `Exercise N`
- All 6 modules: `== Key takeaways` → `== Module summary` (What you accomplished / Key takeaways / Next steps)
- Phase 4: 2 verify sections made concrete, 12 exercise transitions inserted, 5 callouts on the deployment YAML, 10 placeholder tokens → `{attribute}` style with `subs` (learner-supplied values flagged, not guessed), 23 source blocks got `subs="specialcharacters,attributes"`
- module-06 prose: capture-value citations reworded to "for example" phrasing

## Gates

- `npx antora site.yml`: 0 errors; all 34 images in build output; headings/anchors/images verified in rendered HTML
- `ph-check.py`: intake + review — All checks PASSED
- Secrets: clean (only the `sk-oai-` prose prefix mention)

## Items needing human attention

1. [env] module-02/06: 3 env-gated TODOs remain — Evaluations page: EvalHub CRs are now configured (see Follow-up); the eval service itself awaits the platform operator build. observability Dashboard tab needs the observability proxy working on prelude2 (602/603/201 stay placeholders)
2. [orphan files] 201-evaluations-page, 602-cluster-dashboard, 603-usage-dashboard (wrong captures) + 401-gen-ai-playground (empty-state) — candidates for deletion at commit time
3. [RAC] 5 PARTIAL criteria are content-accurate but UI-verify-dependent (dashboard/workspace checks are UI prose; latency/throughput needs a real eval run) — acceptable, or close via M2/M6 captures when the environment has EvalHub + observability
4. [cluster drift] lab-user-dev was intact (15h) but invisible in the projects UI due to the missing dashboard label — fixed in the e2e; re-run `e2e.yml` idempotently after any cluster rebuild

## Follow-up (2026-10-25, post-audit)

**EvalHub unblocked to its final platform gap.** The evalhubs CRD and the
EvalHub CR are now deployed on prelude2 (shipped-CRD stopgap in
`rhoai-cluster-pool` `applications/rhoai/overlay/prelude-nightly-36/evalhub.yaml`,
mirroring the trustyai-llm-demo bundle; the CRD comes from
trustyai-service-operator `config/components/evalhub/crd/` — the demo bundle's
CRD is an OLDER schema and strict-decoding rejects the CR on
`spec.collections/database/providers`). The Evaluations page message advanced
from "complete the EvalHub custom resources configuration" to "enable the
evaluation service using the TrustyAI Operator" (Project: lab-user-dev).

- **M2's only remaining gap**: the pinned 3.6.0-ea.2
  `odh-trustyai-module-operator` predates the enabledServices injection
  (trustyai-service-operator #915/#920, main since 2026-09-13 — flag value
  `EVALHUB`, no underscore; an empty `--enable-services` enables ALL
  services). The service operator still runs `--enable-services=NEMO_GUARDRAILS`
  only and the operator enforces it (reverting external patches in 30s), so
  the EvalHub CR sits unserved. Nothing left to do in the repo — the chain
  (CRD → CR → evaluations list → 201/202–204 captures → RAC PARTIALs close)
  completes when the platform ships the newer operator build.
- **module-02 TODO updated** with the sealed status (the 201 file on disk
  shows the previous error state; re-capture when the eval service runs).
- Item 4 (cluster drift): **resolved** — root cause was the missing
  `opendatahub.io/dashboard=true` namespace label, fixed at the source in
  `e2e.yml` M1.
- Gates after the updates: antora 0 errors, ph-check.py All checks PASSED.

---

# Screenshot completion run (2026-10-25, 4-subagent parallel execution)

All 20 gray placeholders in modules 3–6 replaced with real 1600x900 PNGs
(19 subagent-captured + 2 duplicate fixes re-captured in the main session).
Environment unblocked where possible; 406 is the only scoped shot that stays
a placeholder (platform blocker, sealed note in module-04).

## Per-module status

- **M3 (4/4)**: 301 governance-layer diagram (arch-diagram-svg), 303
  subscription tiers (live, real MaaSSubscription 50,000/1m), 305 one-time
  API key dialog (live, key masked), 306 inference test (terminal mock from
  real output — no browser terminal on prelude2).
- **M4 (5/6)**: Dev Spaces installed via
  `automation/gitops/workshop-apps/devspaces.yaml` (CSV
  devspacesoperator.v3.30.2, AllNamespaces). 401 dashboard + workshop
  workspace Running, 402 genuine trust modal, 403 chatLanguageModels.json
  (apiKey as ${input:...} reference — no key material), 404 Deployment 1/1
  Running, 405 Dev Spaces terminal response + token usage. **406 blocked
  (platform)**: MaaS gateway payload processing feeds the whole conversation
  into the NeMo guardrails forbidden-word scan; the VS Code chat system
  prompt always contains scanned terms -> every editor chat request 403
  regardless of key. Verified by curl (plain message 200; message with
  "harmful" in a system prompt 403). Needs guardrail scoping off the model
  path or input rails on the last user message only.
- **M5 (6/6)**: 501 serving-chain diagram, 502/503/504 real console Logs
  views (client completions + tokens; gateway istio-proxy 200s; model server
  engine throughput), 505 real revoke dialog (throwaway key revoked through
  the dialog flow), 506 genuine ext_proc_error line
  (received_message_larger_than_max 4500128 vs 4194304) after a 4.5MB probe.
- **M6 (4/4)**: observability stack revived in 3 layers — (1) missing
  OperatorHub operators (opentelemetry-product, cluster-observability-operator,
  tempo-product Subscriptions in redhat-ods-operator) fixed DSCI
  MonitoringDependenciesReady=False; (2) /perses proxy workaround (upstream
  odh-dashboard bug: EA2 dashboard-operator cannot apply the rhods-dashboard
  Deployment — invalid value+valueFrom env — DSC DashboardReady=Error
  persists; ConfigMap workaround converges with upstream fix); (3) new
  NetworkPolicy perses-operator access + PersesDatasource mirror. 601 nav,
  604 token table (2 real rows, ~400 completions traffic), 605 GPU 93%
  during 3-worker load, 606 filtered by user+subscription.

## Dup fixes (byte-identical copies re-captured)

- 101-rhoai-dashboard.png (was identical to 001) — re-captured with the left
  navigation pane expanded per its alt text; no longer a copy of 001.
- 101-deployment-status.png (was identical to 302) — re-captured fresh from
  the AI asset endpoints page with Ready status.

## automation/gitops/workshop-apps/ (NEW — workshop-level YAML, not pool-controlled)

kustomization (13 objects) + README + per-file module/shot annotations:
namespace-labels, model-serviceaccount, maas-chat-client (code ConfigMap +
Deployment mirrored from e2e), templated maas-credentials Secret, devspaces
(Namespace/OperatorGroup/Subscription/CheCluster), observability.yaml
(3-layer fix), NetworkPolicy, PersesDatasource. Builds clean with
`oc kustomize`; secrets scan clean.

## Pool repo (UNCOMMITTED proposal — Mike to commit)

`applications/rhoai/overlay/prelude-nightly-36/monitoring-operators.yaml`
(3 Subscriptions) + kustomization resource line. 3.6-only; applied live on
prelude2 (user-approved).

## Gates

- `npx antora site.yml`: 0 errors, 39 PNGs in build output
- `ph-check.py` intake + review: All checks PASSED
- Secrets scan over changed files (password/AKIA/sk-oai-<material>): clean
- Only remaining placeholders: 203/204 (M2 EvalHub — platform operator build)
  and 406 (guardrails scoping — platform), all with sealed notes in the adoc

## For Mike (decisions/items)

1. antora.yml `ssh_user: 'lab-user'` + `ssh_password` are docs placeholders —
   the QA cluster has no lab-user IdP (realm user is prelude). Reconcile for
   the real workshop env or keep as scaffold values.
2. Docs drift (not changed): module-03 tier table (20,000/1m + 1,000/1s,
   priority 10/20) vs live MaaSSubscription (50,000/1m, no priority);
   module-05 gateway deployment name (`-openshift-default`, not `-istio`);
   module-05 504 expected-output block (this vLLM build emits no per-request
   log lines); module-05 502 (client prints completions + tokens, not POST
   lines); Nemotron reasoning model needs max_tokens >= 1000 (docs example
   100 can return content: null).
3. Module client bug: `maas_chat_client.py` hardcodes max_tokens=256 ->
   reasoning model flakiness (content None -> AttributeError crash loop).
   Recommend >=1000 in module-04 source, e2e.yml, and the workshop-apps
   ConfigMap.
4. Transient MaaS gateway warmup: first request on a fresh key can return
   AUTH_FAILURE "Exception thrown while generating token" — worth a
   troubleshooting bullet.
5. maas-chat-client/ repo dir added (module-04 Exercise 1 says it ships the
   cloned repo) — keep-or-remove at commit time.
6. 3.6.0-ea.2 operator bugs: dashboard-operator can never apply the
   rhods-dashboard Deployment (upstream fixed, needs newer build);
   data-science-tempo-traces dashboard 400s (bad panel schema, cosmetic).

