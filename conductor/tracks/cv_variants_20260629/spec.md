# Specification: 5 Core Static CV Variants

## Overview
Optimize the application generation pipeline by transitioning from fully dynamic CV generation to a deterministic static-copy approach. The system will maintain 5 static CV variants mapping to core taxonomy clusters. When an application is created, the system will deterministically copy the highest-scoring CV variant. In the event of a tie, an LLM prompt will select the best variant. This dramatically reduces latency, API cost, and hallucination risk while guaranteeing perfectly typeset layouts. The cover letter will remain 100% LLM-generated to preserve deep, narrative-driven tailoring.

## Functional Requirements
- **Directory Structure:** Create `data/cv-variants/` holding 5 Markdown files corresponding to the taxonomy clusters (`platform-cloud-native.md`, `ml-ai.md`, `distributed-systems.md`, `data-persistence.md`, `5g-oran.md`).
- **Cluster Mapping:** Define a mapping in `engine/shared/config.py` associating taxonomy keys with these filenames.
- **Selection Engine:** 
  - Evaluate the JD scores from `engine/rank.py`.
  - **Single Winner:** Instantly select the highest-scoring cluster's CV variant.
  - **Tie-Breaker:** If multiple clusters tie for the top score, construct a fast, localized LLM prompt passing the JD and the tied variant names. The LLM must return the name of the winning variant.
  - **Fallback:** If the LLM tie-breaker fails, the pipeline must abort and return an explicit error to the user.
- **Dynamic Tagline Retitling:** Upon copying the winning variant to the application folder, the pipeline must parse the frontmatter and update the `tagline` field to accurately reflect the target job title.
- **Cover Letter Integration:** The cover letter generation pipeline must use the *content of the selected static CV variant* as the factual grounding, rather than the `master-cv.md`.
- **Initial Setup Script:** Provide a mechanism for the AI assistant (Gemini) to generate the initial 5 baseline variants from the user's application history.

## Non-Functional Requirements
- **Performance:** Single-winner CV selection must complete in under 50ms. LLM tie-breakers must use minimal context (just JD + titles).
- **Extensibility:** The design must allow adding a 6th variant in the future simply by adding a file and updating the configuration mapping.

## Acceptance Criteria
- A job that strongly matches the `ml-ai` cluster instantly receives the `ml-ai.md` variant.
- A job tying between `ml-ai` and `distributed-systems` triggers an LLM call which successfully breaks the tie.
- The resulting copied `cv.md` has its `tagline` correctly rewritten.
- The cover letter is successfully generated using the chosen static CV as its foundation.

## Out of Scope
- Migrating or updating historical/legacy applications to the new variants format.
- Modifying the underlying document scraping or LaTeX rendering engine.