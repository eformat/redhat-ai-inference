---
schema_version: 1
id: RHAIBU-M5P8HJM0Y86K
type: decision
---
# Model Serving: Nemotron Nano 9B v2 FP8-dynamic via KServe/vLLM on LLMInferenceService

## Context

The design left the open-source model choice as "(TBD)". The per-student environment provides one NVIDIA L4 (24 GB) GPU node (g6.2xlarge), and the earlier model choice (Nemotron 3 Nano 30B A3B FP8, ~37.6 GB VRAM) did not fit that node. The lab needs reasoning-capable output (the `reasoning` field in API responses), and NVIDIA models are preferred for USA-based associates. The serving stack must match what the RHOAI 3.6-ea2 model catalog and serving engine presets provide: KServe-based serving through LLMInferenceService with GPU resources of 2 CPU / 16 Gi / 1 GPU, with the validated Nemotron Nano 9B v2 FP8-dynamic modelcar (~11.6 GB VRAM) from `registry.redhat.io/rhelai1`.

## Decision

- Serve **Nemotron Nano 9B v2 FP8-dynamic** (`redhatainvidia-nemotron-nano-9`, modelcar `oci://registry.redhat.io/rhelai1/modelcar-nvidia-nemotron-nano-9b-v2-fp8-dynamic:1.5`) as the lab's open-source model. This **supersedes** the earlier Nemotron 3 Nano 30B A3B FP8 choice, which did not fit the L4 node.
- Deploy it via **KServe/vLLM using LLMInferenceService** with the serving image the wizard presets inject (`registry.redhat.io/rhaii-fast/vllm-cuda-rhel9`, digest-pinned in the `v3-6-0-ea-2-kserve-config-llm-single-node-template-nvidia-cuda` LLMInferenceServiceConfig).
- Allocate **GPU resources 2 CPU / 16 Gi / 1 GPU** (from the gpu-serving hardware profile) on the **L4 24 GB** node; the l4-gpu node toleration is delivered by the custom accelerator config.
- Runtime args: `--trust-remote-code --max-model-len=131072 --reasoning-parser nemotron_v3` — the `nemotron_v3` reasoning parser is BUILT INTO the vLLM image (no plugin needed), separating the model's thinking (`reasoning` field) from the final answer (`content` field).
- The model and runtime configured in Module 1 carry forward unchanged through all subsequent modules (evaluation, MaaS exposure, application integration, validation, monitoring).

## Consequences

- Easier: the 9B model fits the L4 24 GB node with plenty of headroom (9.47 GiB loaded, no OOM) — no need for a larger GPU instance type.
- Easier: matching the RHOAI serving engine preset configuration means the lab exercises the same serving path the platform uses, and MaaS exposure/subscription flows work against a known-good runtime.
- Easier: the built-in `nemotron_v3` reasoning parser gives clean reasoning/answer separation in API responses with no plugin file.
- Harder: the 9B reasons extensively (~300 tokens of thinking on simple arithmetic) — inference examples need higher max_tokens budgets (e.g. 3072) so `content` is reached.

## Status

Accepted

## Category

Technical

## Alternatives Considered

- **Nemotron 3 Nano 30B A3B FP8** (the original choice): superseded — needs ~37.6 GB VRAM, does not fit the L4 24 GB node.
- **Non-NVIDIA reasoning models** (Qwen3, DeepSeek-R1 distills): rejected — NVIDIA models preferred for USA-based associates.
- **Smaller non-GPU footprint**: rejected — the lab requires dedicated GPU serving.
- **Reasoning parser plugin from the modelcar**: rejected — the 9B modelcar ships no parser plugin; the built-in `nemotron_v3` parser matches the 9B v2 output format (verified end-to-end).

## Related Requirements

- RHAIBU-M5P8FT0JG4MK
- RHAIBU-M5P8GFKKQCFM
