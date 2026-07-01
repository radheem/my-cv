# Specification: "Landing Page" CV & Scannable Cover Letter Optimization

## Overview
This track refines the LLM generation prompts (`data/prompts/cv.md` and `data/prompts/cover.md`) to enforce strict brevity constraints. The goal is to treat the CV and Cover Letter as high-signal, punchy "landing pages" that comfortably fit on one page and actively drive recruiters to the detailed web portfolio.

## Functional Requirements
### 1. CV Prompt Optimization (`data/prompts/cv.md`)
- **Ruthless Brevity Instruction:** Explicitly command the LLM to treat the CV as a "high-signal landing page" designed to encourage the viewer to visit the portfolio link.
- **Experience Constraints:** Limit the LLM to a maximum of 3 punchy bullet points for recent roles, and 2 for older roles.
- **Projects Constraints:** Limit the LLM to exactly 2-3 concise bullet points per project. Ensure the parser's expected `###` heading structure is maintained.
- **Tone:** Instruct the model to be ruthless with word count, focusing purely on technical scale and impact.

### 2. Cover Letter Prompt Optimization (`data/prompts/cover.md`)
- **Word Count Reduction:** Lower the target word count from `~250-400 words` down to `~150-250 words` for a punchier read.
- **"Highlight Bullets" Structure in 'Why Me?':** Instead of dense paragraphs, force the `## 2. Why me?` section to feature exactly 3 punchy bullet points that highlight the absolute strongest matching technical achievements from the CV.
- **Logistics Placement:** Keep the instruction that availability and work authorization facts must be woven naturally into the final sign-off sentence after the bullets.

## Non-Functional Requirements
- Both templates must remain parser-safe (the LaTeX compilation engine relies on specific Markdown structures).
- The changes must be backwards-compatible; no Python code in `engine/` needs to change, only the prompt guidance.

## Acceptance Criteria
- Generating a new CV results in a document that comfortably fits on a single LaTeX page, with roles and projects visibly restricted to 2-3 bullets each.
- Generating a new Cover Letter results in a shorter, highly scannable document where the "Why me?" section relies on a 3-bullet-point list.