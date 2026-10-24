---
schema_version: 1
id: RHAIBU-M5P8HJM0Y86K
type: decision
---
# Model Serving: Nemotron 3 Nano 30B A3B FP8 via KServe/vLLM on LLMInferenceService

## Context

The design left the open-source model choice as "(TBD)". Source-material evidence shows the consumption workflow demonstrated against `nemotron-3-nano-30b-a3b` (Nemotron 3 Nano 30B A3B FP8) served via vLLM, and the per-student environment provides one NVIDIA L40S (48 GB) GPU node. The serving stack must match what private-maas-automation deploys for platform models so the lab model behaves like the platform models used in production flows: KServe-based serving through LLMInferenceService with GPU resources of 1 GPU / 24 Gi memory.

## Decision

- Serve **Nemotron 3 Nano 30B A3B FP8** (`nemotron-3-nano-30b-a3b`) as the lab's open-source model.
- Deploy it via **KServe/vLLM using LLMInferenceService** with the serving image **`rhaii/vllm-cuda-rhel9:3.5.1`**.
- Allocate **GPU resources 1x GPU / 24 Gi memory** (per the private-maas-automation platform/models configuration) on the **L40S 48 GB** node.
- The model and runtime configured in Module 1 carry forward unchanged through all subsequent modules (evaluation, MaaS exposure, application integration, validation, monitoring).

## Consequences

- Easier: matching the private-maas-automation platform model configuration means the lab exercises the same serving path (LLMInferenceService + vLLM) the platform uses, and MaaS exposure/subscription flows work against a known-good runtime.
- Easier: a single L40S 48 GB with 1 GPU / 24 Gi allocation fits the model comfortably with headroom for serving overhead.
- Harder: pinning the serving image to `rhaii/vllm-cuda-rhel9:3.5.1` ties the lab to that image version; image upgrades require re-validation.
- Trade-off accepted: FP8 quantization keeps memory within 24 Gi on one GPU at the cost of some precision versus higher-precision checkpoints.

## Status

Accepted

## Category

Technical

## Alternatives Considered

- **Larger open-source checkpoint** (full-precision or bigger parameter count): rejected — does not fit 1 GPU / 24 Gi on the L40S 48 GB node with serving headroom.
- **Non-quantized FP16/BF16 serving**: rejected — memory footprint exceeds the 24 Gi allocation; FP8 keeps it within budget.
- **Raw KServe InferenceService without LLMInferenceService**: rejected — the platform (private-maas-automation) deploys models via LLMInferenceService; matching it keeps the lab on the known-good serving path.
- **Alternative serving image/version**: rejected — `rhaii/vllm-cuda-rhel9:3.5.1` is pinned and validated with RHOAI 3.5; other images are unvalidated for this lab.

## Related Requirements

- RHAIBU-M5P8FT0JG4MK
- RHAIBU-M5P8GFKKQCFM
