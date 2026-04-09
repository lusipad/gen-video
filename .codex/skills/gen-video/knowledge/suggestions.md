# Knowledge Suggestions

Generated from `status.json`, `candidates.json`, `issue-inbox.json`, `nightly-review.json`, `video-learning.json`, `video-review-actions.json`, `query-log.json`, and discovery/source registries by `scripts/build_knowledge_suggestions.py`.

## High Priority

### Strengthen blogger discovery coverage

- kind: `discovery-gap`
- reason: blogger watchlists exist, but the latest discovery run surfaced 0 blogger candidates
- update_targets: [`knowledge/discovery-registry.json`](discovery-registry.json), [`knowledge/wiki/concepts/karpathy-gap-analysis.md`](wiki/concepts/karpathy-gap-analysis.md), [`knowledge/log.md`](log.md)
- evidence: [`knowledge/candidates.md`](candidates.md), [`knowledge/discovery-registry.json`](discovery-registry.json)

### Write back recurring question `blogger-watchlist-coverage`

- kind: `query-writeback`
- reason: high-value user question is still pending distillation into persistent knowledge
- update_targets: [`knowledge/wiki/concepts/karpathy-gap-analysis.md`](wiki/concepts/karpathy-gap-analysis.md), [`knowledge/discovery-registry.json`](discovery-registry.json)
- evidence: [`knowledge/query-log.json`](query-log.json)

## Medium Priority

### Review discovery candidate: Introducing Camera Angle Concepts

- kind: `candidate-promotion`
- reason: untracked official candidate from `luma-news` matched camera
- update_targets: [`knowledge/source-registry.json`](source-registry.json), [`knowledge/wiki/concepts/promotion-and-retirement.md`](wiki/concepts/promotion-and-retirement.md)
- evidence: [`knowledge/candidates.md`](candidates.md)

### Review discovery candidate: Introducing Camera Motion Concepts

- kind: `candidate-promotion`
- reason: untracked official candidate from `luma-news` matched camera
- update_targets: [`knowledge/source-registry.json`](source-registry.json), [`knowledge/wiki/concepts/promotion-and-retirement.md`](wiki/concepts/promotion-and-retirement.md)
- evidence: [`knowledge/candidates.md`](candidates.md)

### Review discovery candidate: Introducing Modify Video

- kind: `candidate-promotion`
- reason: untracked official candidate from `luma-news` matched video
- update_targets: [`knowledge/source-registry.json`](source-registry.json), [`knowledge/wiki/concepts/promotion-and-retirement.md`](wiki/concepts/promotion-and-retirement.md)
- evidence: [`knowledge/candidates.md`](candidates.md)

### Review discovery candidate: Introducing Ray3 Modify

- kind: `candidate-promotion`
- reason: untracked official candidate from `luma-news` matched ray3
- update_targets: [`knowledge/source-registry.json`](source-registry.json), [`knowledge/wiki/concepts/promotion-and-retirement.md`](wiki/concepts/promotion-and-retirement.md)
- evidence: [`knowledge/candidates.md`](candidates.md)

### Review discovery candidate: Introducing the Gen-4 Image API Runway / May 16, 2025

- kind: `candidate-promotion`
- reason: untracked official candidate from `runway-news` matched gen-4, image
- update_targets: [`knowledge/source-registry.json`](source-registry.json), [`knowledge/wiki/concepts/promotion-and-retirement.md`](wiki/concepts/promotion-and-retirement.md)
- evidence: [`knowledge/candidates.md`](candidates.md)

### Review discovery candidate: Introducing the Runway API for Gen-3 Alpha Turbo Runway / September 16, 2024

- kind: `candidate-promotion`
- reason: untracked official candidate from `runway-news` matched gen-3
- update_targets: [`knowledge/source-registry.json`](source-registry.json), [`knowledge/wiki/concepts/promotion-and-retirement.md`](wiki/concepts/promotion-and-retirement.md)
- evidence: [`knowledge/candidates.md`](candidates.md)

### Review discovery candidate: Luma AI launches Ray3

- kind: `candidate-promotion`
- reason: untracked official candidate from `luma-news` matched ray3
- update_targets: [`knowledge/source-registry.json`](source-registry.json), [`knowledge/wiki/concepts/promotion-and-retirement.md`](wiki/concepts/promotion-and-retirement.md)
- evidence: [`knowledge/candidates.md`](candidates.md)

### Review discovery candidate: Ray3 Evaluation Report – State-of-the-Art Performance for Pro Video Generation

- kind: `candidate-promotion`
- reason: untracked official candidate from `luma-news` matched ray3, video
- update_targets: [`knowledge/source-registry.json`](source-registry.json), [`knowledge/wiki/concepts/promotion-and-retirement.md`](wiki/concepts/promotion-and-retirement.md)
- evidence: [`knowledge/candidates.md`](candidates.md)

### Review discovery candidate: Ray3.14 is here: Native 1080p, 3x cheaper and 4x faster.

- kind: `candidate-promotion`
- reason: untracked official candidate from `luma-news` matched ray3
- update_targets: [`knowledge/source-registry.json`](source-registry.json), [`knowledge/wiki/concepts/promotion-and-retirement.md`](wiki/concepts/promotion-and-retirement.md)
- evidence: [`knowledge/candidates.md`](candidates.md)

### Review discovery candidate: Runway Advances Video Generation and World Models With NVIDIA Rubin Platform Runway / January 5, 2026

- kind: `candidate-promotion`
- reason: untracked official candidate from `runway-news` matched video
- update_targets: [`knowledge/source-registry.json`](source-registry.json), [`knowledge/wiki/concepts/promotion-and-retirement.md`](wiki/concepts/promotion-and-retirement.md)
- evidence: [`knowledge/candidates.md`](candidates.md)

### Review discovery candidate: Serviceplan Group Deploys Creative AI Across Global Operations in Partnership with Luma AI

- kind: `candidate-promotion`
- reason: untracked official candidate from `luma-news` matched creative
- update_targets: [`knowledge/source-registry.json`](source-registry.json), [`knowledge/wiki/concepts/promotion-and-retirement.md`](wiki/concepts/promotion-and-retirement.md)
- evidence: [`knowledge/candidates.md`](candidates.md)

### Review nightly intelligence item: An experiment in voice text editing with Gemini Live

- kind: `nightly-review`
- reason: nightly review surfaced a new community item from `Hacker News`
- update_targets: [`knowledge/wiki/concepts/karpathy-gap-analysis.md`](wiki/concepts/karpathy-gap-analysis.md), [`knowledge/source-registry.json`](source-registry.json)
- evidence: [`knowledge/nightly-review.md`](nightly-review.md), https://public.grugnotes.com/keizo/blog/text-editing-at-the-speed-of-thought/

### Review nightly intelligence item: I Deploy Apps to My Homelab (A Love Story in 9 Acts)

- kind: `nightly-review`
- reason: nightly review surfaced a new community item from `Hacker News`
- update_targets: [`knowledge/wiki/concepts/karpathy-gap-analysis.md`](wiki/concepts/karpathy-gap-analysis.md), [`knowledge/source-registry.json`](source-registry.json)
- evidence: [`knowledge/nightly-review.md`](nightly-review.md), https://blog.laurentcharignon.com/post/2025-12-14-homelab-deployment-flow/

## Low Priority

- None.
