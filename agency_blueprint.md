# High-Ticket Creator Monetization Agency — System Blueprint

This document is the master reference for the agency's operational framework. It
describes the workspace layout, the reusable prompts/components that drive each
piece of the pipeline, and the daily execution workflow used when onboarding a
new creator client.

## 1. Workspace Layout

```
high-ticket-agency/
├── core-brain/            # Shared context Claude reads before generating client work
│   ├── creator-dna.md
│   └── offer-framework.md
├── clients/                # One folder per onboarded creator
├── funnel-templates/       # Reusable application-funnel components
├── scripts/                # Automation prompts / generators
└── crm-audit/               # Pipeline exports + generated insight reports
```

Root-level `CLAUDE.md` holds the operational rules (target audience, coding
style, copywriting style, technical rules) that apply to everything generated
in this workspace.

## 2. Pre-Qualification Funnel

A multi-step application form filters out low-budget leads before they reach
the creator's booking calendar:

1. **Step 1 — Basic Info:** Name, Email, Social Link.
2. **Step 2 — Qualification:** Current monthly revenue tier (`<$5k`, `$5k–$10k`,
   `$10k–$30k`, `$30k+`).
3. **Step 3 — Core Bottleneck:** Free-text description of the prospect's
   biggest operational blocker.

Routing logic: revenue `<$5k` → downsell value-video page; revenue `>$5k` →
Cal.com booking flow.

The reference implementation lives in
[`funnel-templates/HighTicketApplication.tsx`](./funnel-templates/HighTicketApplication.tsx).

## 3. Content-to-Offer VSL Script Engine

Prompt framework (see
[`scripts/vsl_generator_prompt.md`](./scripts/vsl_generator_prompt.md)) that
turns a creator's raw brain-dump transcript into a structured 15-minute VSL
script:

1. **Pattern Interrupt Hook** (0–60s) — name the exact audience and their
   current frustration.
2. **Core Mechanism Reveal** — introduce the systemized asset, not the
   delivery mechanism.
3. **Case Study Proof** — deconstruct the numbers, timeline, and exact steps
   of a real client win.
4. **Frictionless Call To Action** — explain why an application is required
   and who should *not* apply.

## 4. Data-Driven CRM Sales Auditor

Given a `crm-audit/pipeline.csv` export (schema: `Lead Name, Stage, Created
Date, Last Interaction Date, Deal Value, Lost Reason / Notes`), the audit:

1. Calculates dollar value trapped in `Follow-Up Needed` and `No Show` stages.
2. Groups `Lost Reason / Notes` into the top 3 macro objections (e.g.
   Price/Capital, Timing, Trust).
3. Generates `crm-audit/insights_report.md` with 2 SMS + 1 email
   resurrection template per objection — conversational, no high-pressure
   tropes.

See [`crm-audit/README.md`](./crm-audit/README.md) for the schema and the
exact audit prompt.

## 5. Daily Execution Workflow Matrix

| Task / Objective        | Terminal Action                                              | Focus Area / Expected Output                                        |
|--------------------------|---------------------------------------------------------------|-----------------------------------------------------------------------|
| Onboard Creator          | `mkdir clients/creator-name && touch clients/creator-name/dna.md` | Populates the niche, offer price, and unique style guidelines.       |
| Audit Sales Pipeline     | `cp ~/Downloads/export.csv crm-audit/pipeline.csv && claude`  | Run the CRM Auditor to instantly find quick cash loops.               |
| Deploy Landing Page      | `claude "Generate the multi-step form app in client folder"`  | Clean, modern Next.js files ready for immediate production deployment.|
| Script Batching          | `claude "Turn raw_voice.txt into 3 VSL script hooks"`          | Rapid, high-impact hook variations for short/long-form video.        |
