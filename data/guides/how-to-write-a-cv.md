# How to write a tailored CV

The per-job CV (`docs/jobs/<slug>/cv.md`) is tailored to ONE job. Its purpose is to
surface the experience, projects, and skills most relevant to *that* role — a fixed,
everything-included CV dilutes the match.

Source of truth (facts): `data/master-cv.md`, `data/profile.yml`, `data/projects.yml`.
**Never invent** roles, employers, dates, skills, or metrics.

## Sections & order
1. **Body starts at Experience** — the template adds the name, tagline, and contact line.
2. **Experience** first (experienced hire). Most relevant / recent roles, each with 2-3
  tight, achievement-focused bullets — reorder and reword bullets to the job.
3. **Education** — TU Ilmenau (M.Sc. Research) and the B.Sc.
4. **Projects** — top-2 rule below.
5. **Skills** — skills-order rule below.

A summary paragraph is optional and usually omitted to keep it tight; the cover letter
carries the narrative.

## Standing rules
- **Projects: top 2 only**, highest-relevance first. Rank candidate projects against the
  JD; drop the rest. (`engine/rank.py` produces this ranking.)
- **Skills order:** `Languages` (spoken) first — always **English (fluent), Deutsch (A2)** —
  then `Programming Languages`, then exactly 3 job-tailored technical lines matching the
  prompt contract (e.g. Languages & Core, Systems & Infrastructure, Databases & Data Engineering).

## Tailoring
- Study the JD: emphasise what it repeats or lists first; mirror its real terminology
  (truthfully).
- Retitle the role tagline to fit the job (e.g. "Data & Backend Engineer") when honest.
- Cut the least-relevant content first if it overflows — aim for one page of content.
