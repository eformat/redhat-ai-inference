# Module 3: Model-as-a-Service — tracking list

Module 3 (`content/modules/ROOT/pages/module-03-model-as-a-service.adoc`):
543 lines, 4 exercises (Ex 1 Review the MaaS approach / Ex 2 Configure the
model as a shared service / Ex 3 Configure access controls and API endpoints /
Ex 4 Configure scaling policies), 0 TODOs, 6 screenshots. Same treatment as
module 2: verify the flow live → rewrite concise → retrofit terminal renders
→ recapture screenshots.

## Verified — environment seed (2026-10-27)

- [x] MaaS STACK LIVE on the app-of-apps cluster: the maas-gateway Route
      `maas.apps.ocp.ddrcj.sandbox4732.opentlc.com` (the Service type
      LoadBalancer + the status hostname via the maas-gateway-status Job —
      Completed), the maas-controller Running, the maas-ui Running. The maas
      chart (rhai-maas, 21 resources): postgres, the maas-default-gateway +
      status Job, MLflow, EvalHub, Kuadrant/Authorino, TelemetryPolicy.
- [x] The 6 screenshots exist at 1600x900 with real content (301
      maas-governance-layer 142KB, 302 ai-asset-endpoints 90KB, 303
      maas-subscription-tiers 67KB, 304 api-key-create 96KB, 305
      api-key-created 100KB, 306 maas-inference-test 115KB) — from the
      earlier quality pass; recapture if the flow changed.
- [x] KNOWN GOTCHAS from earlier work: the MaaS gateway 4 MiB request-body
      limit (RHOAIENG-99765); the router 30s default timeout on
      NON-streaming MaaS requests (the optional timeout annotation on
      maas-gateway-route was DEFERRED — the module 4 playground streams so
      it is safe, but a non-streaming MaaS curl would 504); the maas-chat
      client 404/405/502 gotchas (module 4's e2e); the MaaS API keys have
      expiry (transient AUTH_FAILURE on fresh keys — retry succeeds).

## Verified — 2026-10-27 verify-first pass (BLOCKING BUGS FOUND)

- [x] BLOCKING BUG — AUTHORINO TOKENREVIEW RBAC PRUNED BY ARGOCD: the
      Authorino operator creates ClusterRoleBindings `authorino-authorino`
      (-> ClusterRole authorino-manager-role) and `authorino-authorino-k8s-auth`
      (-> authorino-manager-k8s-auth-role, tokenreviews + subjectaccessreviews
      create) when it reconciles the Authorino CR (operator log "create object"
      at install time, each created 2x). The rhai-maas ArgoCD app has
      `automated: {prune: true}` — cluster-scoped objects outside the app
      manifest are PRUNED on every sync, so both bindings are GONE. Without
      them the maas-gateway-auth AuthPolicy's openshift-identities
      (kubernetesTokenReview) never authenticates -> EVERY OpenShift-token
      request through the MaaS gateway returns 401 (UNAUTHENTICATED, empty
      body). IMPACT CHAIN: the dashboard's MaaS page is BROKEN ("Error loading
      API keys: unknown error when invoking maas-api (unmarshall): unexpected
      end of JSON input") — the dashboard proxies /maas/api/* to the maas-ui
      backend (odh-dashboard-maas-ui:8243) which calls the maas-api THROUGH THE
      GATEWAY (https://maas.apps.../maas-api/v1/...) with the user's OpenShift
      token -> 401 empty body -> JSON unmarshall fails -> 500. api_keys table
      EMPTY (zero keys ever created — the flow never worked on this cluster).
      API-KEY REALM WORKS: a fake sk-oai- key gets 403 (authentication passes,
      validation denies) vs 401 for OpenShift tokens — so the sk-oai- path is
      structurally fine; ONLY the TokenReview RBAC is missing.
      FIX: both ClusterRoleBindings added to
      automation/gitops/maas/templates/40-kuadrant.yaml (ArgoCD owns them now,
      operator's reconcile sees them as existing).
- [x] NO GOVERNANCE OBJECTS EXIST (the page's Ex 2/Ex 3 claims are FALSE for
      this cluster): zero MaaSModelRefs cluster-wide, zero MaaSSubscription/
      MaaSAuthPolicy in models-as-a-service, the ISVC router.gateway is EMPTY
      ({}) — the model is NOT attached to the maas gateway. The page's two-tier
      design (maas-free/maas-premium-subscription, premium-users group) —
      premium-users DOES NOT EXIST on this cluster (only rhods-admins).
      FIX: MaaSSubscription maas-free-subscription + MaaSAuthPolicy
      maas-free-subscription-policy added to
      automation/gitops/workshop-apps/maas-subscriptions.yaml (single tier,
      owner group system:authenticated:oauth, tokenMetadata na/na, modelRefs
      -> redhatainvidia-nemotron-nano-9 in lab-user-dev, tokenRateLimits
      20000/1m + 1000/1s). kustomize builds; namespaces correct.
- [x] PAGE GROUP BUG (the 6.1 reference repo is the authority): the page says
      `system:authenticated` — the actual identity presents
      `system:authenticated:oauth`; plain never matches the generated
      AuthPolicy's allowed_groups -> 403 (ph-deploy-configure-rhoai
      manifests/05-maas/subscription/maassubscription.yaml comment). Fix in the
      rewrite.
- [x] tokenMetadata REQUIRED: costCenter/organizationId placeholders (na/na) —
      the TelemetryPolicy's CEL label expressions are evaluated strictly;
      absent values -> the labeled descriptor fails to build -> Limitador never
      records authorized_hits -> the Usage dashboard token panels stay empty
      (the reference repo pattern; fixed upstream in a 3.4 z-stream, harmless
      to keep).
- [x] tenantRef IS a valid MaaSModelRef field (spec: endpointOverride,
      modelRef, tenantRef) — "name of the AITenant this model belongs to; when
      omitted the controller auto-resolves from the HTTPRoute's gateway
      parentRef via reverse lookup". The aitenant here IS models-as-a-service
      (maastenantconfig default-tenant, annotations maas.opendatahub.io/
      aitenant-name: models-as-a-service). The page's YAML is valid.
- [x] ENVIRONMENT FACTS: the dashboard canonical URL is https://rh-ai.apps.
      ocp.ddrcj.sandbox4732.opentlc.com (the SECOND ingress domain —
      GATEWAY_DOMAIN/dashboard-url maas-params values are CORRECT, not stale;
      rhods-dashboard route redirects there via dashboard-redirect). Login via
      Keycloak sso.apps... (idp-4-ocp), lab-user1 / the lab password. The
      maas-api serves the OpenAI surface THROUGH the gateway: HTTPRoute
      maas-api-route (redhat-ai-gateway-infra, parent maas-default-gateway,
      no hostnames) paths /v1/models, /v1/subscriptions, /v1/api-keys,
      /maas-api/v1, /maas-api/health -> maas-api:8443. /maas-api/health is
      UNAUTHENTICATED (200). The AuthPolicy maas-gateway-auth (openshift-ingress,
      targets the Gateway): authn api-keys (plain, ^Bearer sk-oai-.*,
      validated via metadata http POST to maas-api /internal/v1/api-keys/
      validate — keys live in the maas-api's POSTGRES, not K8s secrets) +
      openshift-identities (TokenReview, BROKEN — RBAC); authz auth-valid
      (OPA: allow if apiKeyValidation.valid, allow if no apiKeyValidation),
      deny-api-key-management (sk-oai- keys denied on /maas-api/v1/api-keys —
      only OpenShift identities manage keys there), require-group-membership +
      subscription-valid (MODEL paths only, not /v1/* or /maas-api/*).

## Verified — END-TO-END FLOW WORKS (2026-10-27, after the sync + apply)

- [x] RBAC FIX CONFIRMED: both ClusterRoleBindings landed (ArgoCD synced
      a22a7da after a hard refresh — oc annotate
      application.argoproj.io/rhai-maas argocd.argoproj.io/refresh=hard), the
      Authorino SA can create TokenReviews, and the gateway OpenShift-token
      auth WORKS (GET /v1/models with the lab-user1 token → 200).
- [x] SUBSCRIPTIONS APPLIED + ACTIVE: MaaSSubscription
      maas-free-subscription + MaaSAuthPolicy maas-free-subscription-policy
      (PHASE=Active). NOTE: the FIRST apply was DELETED within ~60s (cause
      unclear — possibly a race with the MaaSModelRef reconcile); the re-apply
      survived and has been stable 5m+. If subscriptions vanish on a fresh
      cluster, re-apply.
- [x] Ex 2 LEARNER FLOW VERIFIED as lab-user1: (1) oc apply the MaaSModelRef
      (tenantRef models-as-a-service) → PHASE=Failed with GATEWAY=
      openshift-ai-inference (the HTTPRoute still on the direct gateway);
      (2) oc patch the LIS router to maas-default-gateway → PHASE=Pending
      (BackendNotReady "Awaiting governance pairing", GovernanceAttached=False
      "NoPairingFound"); (3) after the subscriptions exist → PHASE=Ready, ALL
      conditions True (Ready/GovernanceAttached/RuntimeReady/
      ModelIdentityUnique). The page's Ex 2 must present the router patch +
      the modelRef in the RIGHT ORDER (patch router first or show the Failed
      progression).
- [x] KEY CREATION VERIFIED: POST /maas-api/v1/api-keys with the OpenShift
      token → 201, key sk-oai- prefix, 67 chars. The dashboard Create API key
      dialog verified: Name + Description + Subscription (typeahead: "Select a
      subscription to scope this API key to. The key will work only with
      models that belong to the selected subscription") + Expiration (default
      30 days, "Must be between 1 and 365, inclusive"). The keys table shows
      Active + Subscription + Owner + Created/Last used/Expires. The
      Subscriptions tab: Subscription view | Model view toggle, the expanded
      row shows the model + "Token limits: 20,000 / 1 minute, 1,000 / 1
      second".
- [x] INFERENCE VERIFIED (streaming AND non-streaming): GET /v1/models with
      the key → the model ready=true, id publishers/lab-user-dev/models/
      redhatainvidia-nemotron-nano-9, url https://maas.apps.../ (the gateway
      ROOT — matches the page's endpoint shape). POST /v1/chat/completions →
      HTTP 200 in 3.4s (well under the 30s router timeout). REAL RESPONSE
      SHAPE: the response's model field is the SHORT name
      "redhatainvidia-nemotron-nano-9" (NOT the publisher path — the page's
      example is WRONG); Nemotron is a REASONING model — with max_tokens 150
      the content is reasoning-style ("Okay, the user is asking...") and
      finish_reason=length (chat_template_kwargs enable_thinking:false moves
      the text to content but the style stays); system_fingerprint
      vllm-0.28.0+rhaiv.7. Streaming: SSE chunks (delta.reasoning for
      Nemotron) + "data: [DONE]".
- [x] Ex 4 SCALE IMPOSSIBLE ON THIS LAB (1 GPU): oc patch replicas 2 → the
      second pod SchedulingGated (kueue.x-k8s.io/admission + topology gates;
      the ClusterQueue default nominalQuota nvidia.com/gpu=1, the node has ONE
      L4 — ip-10-0-16-235). The pod NEVER schedules. Scale back to 1 restores
      (the gated pod deleted; the modelRef phase dips Unhealthy then Ready).
      The page's "expected output" (both pods Running) is FICTION for this
      lab — rewrite honestly: scale → SchedulingGated (the Kueue GPU quota)
      → scale back to 1.
- [x] The dashboard flow VERIFIED END-TO-END as lab-user1: Gen AI studio →
      API keys loads (no more error), both test keys Active with
      maas-free-subscription, the Subscriptions tab with the token limits,
      the Create dialog complete.

## DONE — module-03 rewrite complete (2026-10-27)

- [x] PAGE REWRITTEN: content/modules/ROOT/pages/module-03-model-as-a-service.
      adoc — 432 lines (from 543), 4 exercises, 10 image references (5 live
      dashboard captures 301-305 + 5 terminal renders 303b/304b/306b/306c/
      306d), 0 TODOs, Antora 0 errors, secrets clean.
- [x] TERMINAL RENDERS (the zt-rhaibu pipeline, term.py + playwright #term):
      303b-modelref-pending (1000x126), 304b-subscriptions-active (1000x189),
      306b-modelref-conditions (900x168), 306c-maas-models (900x482),
      306d-maas-inference (900x963) — all the REAL captured outputs (the
      /v1/models + /v1/chat/completions responses re-captured live; the
      keyredacted — the command lines templated).
- [x] DASHBOARD SCREENSHOTS RECAPTURED from THIS cluster (the old ones were
      from prelude2): 302 (the AI asset endpoints page, the model Ready with
      View), 303 (the Subscriptions tab expanded with the token limits), 304
      (the Create dialog filled: Name Workshop + subscription selected), 305
      (the API key created dialog — the key is MASKED by default sk-oai-••••
      with a Show button, safe to capture).
- [x] 306-maas-inference-test.png ORPHANED (the reference removed — the 306d
      terminal render covers the inference response). Candidate for deletion
      at commit time (Mike's call).
- [x] CLEANUP: all test API keys revoked ("Revoke user API keys" in the
      dashboard — all active keys for lab-user1 revoked) so the learner starts
      with an empty keys table.
- [x] KEY PAGE CHANGES vs the old version: the single tier
      (maas-free-subscription, system:authenticated:oauth — NOT the two-tier
      free/premium design; premium-users does not exist on this cluster); Ex 2
      presents the router patch FIRST then the MaaSModelRef (the verified
      Failed→Pending→Ready progression); Ex 4's scale is honest (the second
      pod SchedulingGated — the Kueue GPU quota is 1, the node has a single
      L4 — then scale back to 1); the inference example matches the REAL
      response (content null + reasoning filled + finish_reason length; the
      model field echoes the SHORT name); the /v1/models example shows the
      REAL catalog shape (kind/url/subscriptions fields).

## PARAMETERIZED (2026-10-28): antora.yml attributes per the house pattern

- [x] Mike's call: the per-environment coordinates SHOULD be antora.yml
      attributes, not hardcoded — the house pattern (ph-deploy-configure-rhoai
      content/antora.yml) parameterizes project_name, maas_gateway_url
      (https://maas.apps.cluster.example.com), openshift_cluster_ingress_domain,
      model_endpoint_url with placeholder defaults overridden per environment
      by the publishing-house yq merge (user_data.yml *= asciidoc.attributes).
      KEY MECHANIC: a DEFINED attribute substitutes at BUILD time, so the
      role="execute" blocks stay runnable with the baked value (placeholder
      default in the repo build; the real value in the deployed showroom).
      The earlier bug was an UNDEFINED attribute ({project-namespace} —
      renders literally). LESSON: parameterize + ALWAYS ensure the block has
      subs="specialcharacters,attributes" — four blocks lacked it and
      rendered {…} literally (module-03 oc apply heredoc, module-02 evalhub
      config + evaljob.yaml, module-01 ISVC status output — a plain ----
      listing block has verbatim subs, NO attributes).
- [x] IMPLEMENTED: content/antora.yml adds project_namespace 'lab-user-dev',
      maas_gateway_url, evalhub_base_url, inference_gateway_url,
      openshift_cluster_ingress_domain (placeholder defaults, cluster.example.com).
      module-03: 6x {project_namespace} + {maas_gateway_url}. module-02:
      {evalhub_base_url}, {inference_gateway_url}/{project_namespace},
      tenant {project_namespace}. module-01: 8x {project_namespace} +
      {inference_gateway_url}/{project_namespace} + subs added to 3 blocks.
      VERIFIED: Antora 0 errors, 0 literal placeholders in all four built
      pages, heredoc escaping intact (&lt;&lt;'EOF'), rendered samples show
      the placeholder defaults baked (namespace: lab-user-dev, the
      cluster.example.com URLs), secrets clean.

- [x] ALL ANTORA PLACEHOLDER COMMANDS FIXED: the page used
      `{project-namespace}` 6x and `{maas_url}`/`{maas_api_key}` — NONE are
      defined in content/antora.yml (only guid/user/password/openshift_*_url
      are), so they rendered LITERALLY and the role="execute" blocks were not
      runnable (modules 1-2 use lab-user-dev directly, 0 placeholders — the
      house style is real lab values inline). FIX: all 6
      `{project-namespace}` -> `lab-user-dev`; `export MAAS_URL` -> the real
      gateway URL https://maas.apps.ocp.ddrcj.sandbox4732.opentlc.com;
      `export MAAS_API_KEY` -> `<your sk-oai- API key>` (angle brackets, the
      per-learner key). VERIFIED in the built site
      (www/modules/module-03-...html): every command renders runnable, 0
      literal placeholders, Antora 0 errors.

## GOVERNANCE SETTINGS SCREENSHOT (2026-10-28, Mike's request)

- [x] Ex 3 gains the Settings → MaaS governance admin view: captured
      303c-maas-governance.png (73KB, 1600x900) from the live cluster (the
      Overview tab: the model Ready with 1 subscription + 1 authorization
      policy, Create subscription/Create authorization policy buttons, the
      Settings nav with MaaS governance). The page URL is /maas/maas-governance
      (NOT /settings/...). Added to Ex 3 after the 304b oc-get render: the
      pairing is visible in the console + how to add tiers. Module-03 now has
      11 image references, Antora 0 errors, secrets clean.

## Environment state left behind

- The MaaSModelRef redhatainvidia-nemotron-nano-9 (lab-user-dev): Ready, all
  conditions True.
- The subscription + authpolicy in models-as-a-service: Active.
- The model's LIS router: attached to maas-default-gateway; replicas back to 1.
- Zero API keys (all test keys revoked).


## Pending — module 4 (Integrate the Application)

- [ ] The maas-credentials-secret.yaml in workshop-apps is TEMPLATED —
      substitute a freshly minted MaaS API key before enabling.
- [ ] Verify the module-4 learner flow with the module-3 handoff (the
      endpoint URL + the API key).
