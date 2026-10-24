---
schema_version: 1
id: RHAIBU-M5P8HJKGVYQQ
type: decision
---
# Content Format: Antora/AsciiDoc Showroom in an All-in-One Publishing House Repo

## Context

The workshop "From Model to Model as a Service: Building Scalable AI Inference" needs a hands-on lab content format and a repository layout decision before authoring. Existing workshop commentary lives as AsciiDoc module pages (`content/modules/ROOT/pages/*.adoc`) in the `redhat-ai-inference` repo, and Red Hat Showroom-format labs (Antora + AsciiDoc) are the established delivery vehicle for Red Hat hands-on workshops. Source material analysis shows 17 TODO placeholders and 10 empty code blocks that will need screenshots and live-captured evidence. Prior workshops in this space (e.g., ph-deploy-configure-rhoai) use an all-in-one publishing house repo layout — content, environment automation, and QA automation in a single repository — rather than splitting content and automation across separate repos.

## Decision

- Author the lab as an Antora/AsciiDoc Red Hat Showroom lab: `content/` holds the Antora site with `modules/ROOT/pages` (index.adoc + 6 module pages in AsciiDoc).
- Use an **all-in-one publishing house repo layout**, following the `~/git/ph-deploy-configure-rhoai` pattern: `content/` (Antora/AsciiDoc lab pages), `automation/` (Ansible + GitOps environment provisioning), and `qa-automation/` (verification) all live in ONE repository — the existing `redhat-ai-inference` repo — not split across separate content and automation repos.
- Screenshots are **placeholder-first**: author the AsciiDoc with placeholder image references and TODO markers, then replace them with live captures from a real environment during the Act phase (per the live-capture TODO inventory: deploy wizard, EvalHub UI, model-server logs, annotated dashboards, M3 expose steps, M4 sample-app deploy, M5 failure simulation, M1 curl inference).

## Consequences

- Easier: a single repo carries content + automation + QA in lockstep — module steps and the environment that serves them never drift apart; one clone gives a contributor everything.
- Easier: placeholder-first authoring unblocks writing now and defers live capture to a single Act-phase pass against a real environment.
- Harder: the repo mixes concerns (docs, Ansible, GitOps, QA) — directory conventions (`content/`, `automation/`, `qa-automation/`) must be enforced to keep it navigable.
- Trade-off accepted: no reuse of the stock two-repo scaffolding (see infrastructure-approach decision) in exchange for single-repo atomicity.

## Status

Accepted

## Category

Process

## Alternatives Considered

- **Stock zt-rhaibu two-repo layout** (separate showroom + automation repos): rejected — splits content from environment automation; see infrastructure-approach decision for the full rationale.
- **Markdown-only lab content** (no Antora/AsciiDoc): rejected — Red Hat Showroom delivery and existing module commentary are Antora/AsciiDoc; converting would lose the established structure and preview tooling.
- **Screenshots-first authoring** (block writing until a live environment exists): rejected — placeholder-first unblocks writing now; live capture is deferred to a single Act-phase pass.

## Related Requirements

- RHAIBU-M5P8FT0JG4MK
