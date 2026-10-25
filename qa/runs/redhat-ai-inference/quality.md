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
