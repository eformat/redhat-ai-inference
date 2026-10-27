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

## Pending — chart sync (needs push)

- [ ] Push chart changes: accelerator config rename + inference-gateway-status
      Job (74 resources, lint clean)
- [ ] After sync: old `vllm-nvidia-l40s-gpu-single-node` config pruned
- [ ] After sync: hostname Job re-runs → Gateway listener hostname patched →
      external URL `https://inference-gateway.apps.<domain>/...` resolves
- [ ] Verify the model's external endpoint from the dashboard
      (Deployments → Internal and external endpoint)

## Pending — images + docs (needs the model sorted first)

- [ ] Recapture Module 1 screenshots for the 9B flow:
      `101-model-catalog.png` (nemotron-nano-9b search),
      `101-catalog-model-card.png` (9B card),
      `101-wizard-model-details.png` (9B modelcar URI:
      `oci://registry.redhat.io/rhelai1/modelcar-nvidia-nemotron-nano-9b-v2-fp8-dynamic:1.5`),
      `101-wizard-deployment.png` (gpu-serving + "vLLM NVIDIA GPU Single Node"),
      `101-wizard-advanced.png` (new args),
      `101-wizard-review.png`
- [ ] Module 1 "What the wizard creates": actual resource name
      (`redhatainvidia-nemotron-nano-9` — model-derived, truncated), modelcar
      URI (`rhelai1/...:1.5`), resources, args incl. the reasoning parser
- [ ] Module 1 Exercise 3: model URL (internal gateway URL now; external after
      the hostname Job), model name `redhatainvidia-nemotron-nano-9`, response
      example reflecting the reasoning separation
- [ ] Module 1 config table: sizing narrative for the 9B on the L4, args
      explanation (trust-remote-code, max-model-len, reasoning parser)
- [ ] Audit Modules 2–6 for 30B model references (name/URI/size) and update
- [ ] Audit `qa-automation/e2e.yml` + `healthcheck.yml` for model references
- [ ] Decide: hardware profile display-name "GPU serving (NVIDIA L40S)" — the
      L40S mention is cosmetic-only (identifiers are GPU-generic); rename to
      "GPU serving" if wanted
