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

## Pending — after Mike commits + syncs

- [ ] Mike: commit + push 40-kuadrant.yaml (the bindings) + workshop-apps
      (maas-subscriptions.yaml); ArgoCD syncs rhai-maas (the bindings land);
      oc apply -k workshop-apps (the subscriptions) — or verify ArgoCD applied
      them if moved to a chart.
- [ ] Re-verify: the Authorino SA can create TokenReviews (oc auth can-i);
      the dashboard API keys page loads; a key created via the dashboard works.
- [ ] Walk Ex 2 as lab-user1: the LIS router patch to maas-default-gateway +
      the MaaSModelRef apply — verify the conditions (Ready/GovernanceAttached/
      RuntimeReady/ModelIdentityUnique) and /v1/models with the key.
- [ ] Test inference with the key (streaming AND non-streaming — watch the
      deferred 30s timeout on maas-gateway-route) + the key expiry behavior.


## Pending — rewrite module-03 (concise working instructions)

- [ ] Cut to ~250-300 lines like module 2: real values (the model name, the
      maas endpoint, the actual key flow), the verified gotchas as
      troubleshooting, cut the product-manual padding.
- [ ] Retrofit the terminal renders for the CLI expected outputs (the
      zt-rhaibu workshop-screenshot pipeline — the memory note has the full
      pattern; modules 1+2 are the reference).
- [ ] Recapture the screenshots that changed (the 3.6-ea2 UI flows).
- [ ] Antora build 0 errors + secrets clean (NEVER commit a MaaS API key —
      the keys are transient with expiry; redact to short prefixes in any
      captured output).
