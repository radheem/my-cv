# Structured Cover Letter Harness (Why Company/Me/Now) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transition generated cover letters to a structured three-question H2-based template ("Why Company?", "Why me?", "Why now?"), update the LaTeX rendering compiler to format these headings beautifully into the PDF, and update the benchmark evaluation harness to score them with backward compatibility.

**Architecture:** 
1. Update `data/guides/how-to-write-a-cover-letter.md` and `data/prompts/cover.md` to guide the LLM to output three sections with H2 headings.
2. In `engine/latex.py`, intercept any Markdown H2 heading blocks inside `_letter_block` and compile them into clean LaTeX inline bold sections with professional spacing.
3. In `tests/experiments/harness.py`, adapt `cover_metrics` to detect the presence of headings, validate the three sections when present, and dynamically adjust paragraph and heading checks while maintaining backward compatibility with the legacy paragraph count.

**Tech Stack:** Python, pytest, LaTeX, Jinja/String formatting.

---

### File Structure Changes

The following files will be touched:
- **Modify**: `data/guides/how-to-write-a-cover-letter.md` — Rewrite to document the 3-question structure.
- **Modify**: `data/prompts/cover.md` — Instruct the LLM to output the three specific headings and paragraphs with blank lines.
- **Modify**: `engine/latex.py` — Implement heading interceptor and LaTeX formatting in `_letter_block`.
- **Modify**: `tests/experiments/harness.py` — Update evaluation scoring metrics with section verification and backward compatibility.
- **Modify**: `tests/test_experiments.py` — Add automated test coverage for the latex parser and updated scoring metrics.

---

### Task 1: Update the LaTeX Cover Letter Compiler

**Files:**
- Modify: `engine/latex.py:415-440`
- Test: `tests/test_latex.py` (Note: Moved from test_experiments.py based on review)

- [ ] **Step 1: Write a failing unit test in `tests/test_latex.py`**
  Add a test that verifies that `_letter_block` can convert a cover letter body containing H2 headings into LaTeX bold headings with correct vertical spacing, without escaping the heading symbols or collapsing them into standard paragraphs.
  
  ```python
  def test_latex_heading_rendering():
      from engine import latex
      body = (
          "## 1. Why Google?\n"
          "I love Google.\n\n"
          "## 2. Why me?\n"
          "I am a strong developer.\n\n"
          "## 3. Why now?\n"
          "It is the right time."
      )
      # We will expose a mock test function or call an internal parser if possible, 
      # or test latex.render_cover_tex directly with a dummy profile.
      meta = {"company": "Google", "recipient": "Hiring Team"}
      profile = {"name": "John Doe", "email": "john@doe.com"}
      tex = latex.render_cover_tex(body, body, meta, profile)
      
      # Verify that ## sections are converted to bold inline section highlights
      assert r"\textbf{1. Why Google?}" in tex
      assert r"\vspace{8pt}\noindent" in tex
      # Verify raw markdown hashtags or escaped hashes do not leak
      assert "##" not in tex
      assert r"\#" not in tex
  ```

- [ ] **Step 2: Run pytest to verify the test fails**
  Run: `pytest tests/test_latex.py::test_latex_heading_rendering -v`
  Expected: FAIL (either escaping `#` or failing to format them correctly)

- [ ] **Step 3: Modify `engine/latex.py` to parse and format H2/H3 headings**
  Update `_letter_block` to correctly parse blocks and handle headings by inserting formatted LaTeX text with spacing:
  
  ```python
  def _letter_block(body: str, company: str, attn: str, salutation: str,
                    signoff: str, name: str) -> str:
      blocks = [b.strip() for b in re.split(r"\n\s*\n", body.strip()) if b.strip()]
      formatted_blocks = []
      
      for block in blocks:
          # Match ## 1. Why Company? or similar
          heading_match = re.match(r"^#{2,3}\s+(.+)$", block)
          if heading_match:
              title = inline(heading_match.group(1))
              formatted_blocks.append(f"\\vspace{{8pt}}\\noindent\\textbf{{{title}}}\\par\\vspace{{3pt}}")
          else:
              formatted_blocks.append(inline(" ".join(block.splitlines())))
              
      paras = "\n\n".join(formatted_blocks)
      return "\n".join([
          "\\recipient{%s}{%s}{}" % (inline(company), attn),
          "",
          "\\opening{%s}" % inline(salutation),
          "",
          paras,
          "",
          "\\closing{%s}{%s}" % (inline(signoff), inline(name)),
      ])
  ```

- [ ] **Step 4: Run test to verify it passes**
  Run: `pytest tests/test_latex.py::test_latex_heading_rendering -v`
  Expected: PASS

- [ ] **Step 5: Commit changes**
  ```bash
  git add engine/latex.py tests/test_latex.py
  git commit -m "feat(latex): render markdown headings as inline bold headers in cover letter"
  ```

---

### Task 2: Update the Evaluation Harness (`harness.py`)

**Files:**
- Modify: `tests/experiments/harness.py:270-320`
- Test: `tests/test_experiments.py`

- [ ] **Step 1: Write a unit test for the new evaluation metrics**
  Verify that `cover_metrics` correctly handles both heading-structured and standard paragraphs:
  
  ```python
  def test_cover_metrics_handling_headings():
      # Structured with headings
      structured = (
          "## 1. Why Google?\n"
          "I am excited to work at Google because of their search infrastructure.\n\n"
          "## 2. Why me?\n"
          "I designed a distributed database that handled millions of QPS.\n\n"
          "## 3. Why now?\n"
          "I am ready to bring my database scaling expertise to a larger scale."
      )
      m1 = harness.cover_metrics(structured, "Google")
      assert m1["paragraphs"] == 3
      assert m1["has_headings"] == 1.0
      assert m1["headings_correct"] == 1.0
      assert m1["company_mention"] == 1.0
      
      # Legacy unstructured body
      legacy = "Paragraph one.\n\nParagraph two.\n\nParagraph three."
      m2 = harness.cover_metrics(legacy, "Google")
      assert m2["paragraphs"] == 3
      assert m2["has_headings"] == 0.0
      assert m2["headings_correct"] == 0.0
  ```

- [ ] **Step 2: Run test to verify it fails**
  Run: `pytest tests/test_experiments.py::test_cover_metrics_handling_headings -v`
  Expected: FAIL

- [ ] **Step 3: Modify `cover_metrics` in `tests/experiments/harness.py`**
  Modify the `cover_metrics` function to identify if headings exist, score the headings pattern (English/German matched by regex), count non-heading paragraphs, and introduce the new metrics `has_headings` and `headings_correct`.
  
  ```python
  def cover_metrics(gen_cover: str, company: str) -> dict[str, Any]:
      body = strip_front_matter(gen_cover).strip()
      wc = len(body.split())
      blocks = [b.strip() for b in re.split(r"\n\s*\n", body) if b.strip()]
      
      # Identify headings
      headings = [b for b in blocks if b.startswith("##") or b.startswith("###")]
      paras = [b for b in blocks if not (b.startswith("##") or b.startswith("###"))]
      
      has_headings = 1.0 if len(headings) > 0 else 0.0
      
      headings_correct = 0.0
      if has_headings:
          # Verify we have exactly 3 headings, matched by sequence numbers 1, 2, 3
          patterns = [
              r"1\.\s+(why|warum)\b",
              r"2\.\s+(why\s+me|warum\s+ich)\b",
              r"3\.\s+(why\s+now|warum\s+jetzt)\b"
          ]
          matched = 0
          for i, h in enumerate(headings[:3]):
              if i < len(patterns) and re.search(patterns[i], h, re.IGNORECASE):
                  matched += 1
          if matched == 3 and len(headings) == 3:
              headings_correct = 1.0
              
      no_salutation = 0.0 if _FORBIDDEN_OPENERS.search(body) else 1.0
      company_hit = 1.0
      if company:
          first = re.sub(r"[^a-z0-9]+", "", company.split()[0].lower())
          company_hit = 1.0 if first and first in _tokens(body) else 0.0
          
      # Determine effective paragraphs to count
      effective_paras_count = len(paras) if has_headings else len(blocks)
      
      return {
          "word_count": wc,
          "length_ok": round(_band(wc, 250, 400, 150), 3),
          "paragraphs": effective_paras_count,
          "paragraphs_ok": 1.0 if 3 <= effective_paras_count <= 5 else 0.5,
          "no_salutation": no_salutation,
          "company_mention": company_hit,
          "has_headings": has_headings,
          "headings_correct": headings_correct,
      }
  ```

- [ ] **Step 4: Run test to verify it passes**
  Run: `pytest tests/test_experiments.py::test_cover_metrics_handling_headings -v`
  Expected: PASS

- [ ] **Step 5: Ensure legacy gold tests still pass**
  Run all existing experiments unit tests: `pytest tests/test_experiments.py`
  Expected: PASS (shows complete backward compatibility)

- [ ] **Step 6: Update `_W` weights in `harness.py`**
  Add the new metrics `cl_has_headings` (weight: 0.02) and `cl_headings_correct` (weight: 0.03) to the heuristic scoreboard. Re-weight slightly to make room for them:
  ```python
  _W = {
      "cv_structure": 0.15,
      "skills_coverage": 0.20,
      "projects_match": 0.15,
      "jd_coverage": 0.15,
      "truthfulness": 0.15,
      "cl_length": 0.05,
      "cl_no_salutation": 0.05,
      "cl_company": 0.05,
      "cl_paragraphs": 0.02, # Demote legacy paras check slightly to accommodate headings
      "cl_has_headings": 0.01,
      "cl_headings_correct": 0.02,
  }
  ```
  And map these keys in `score_case` under `parts = { ... }`:
  ```python
  "cl_has_headings": cm["has_headings"],
  "cl_headings_correct": cm["headings_correct"],
  ```

- [ ] **Step 7: Run existing experiments unit tests to confirm weights are valid**
  Run: `pytest tests/test_experiments.py`
  Expected: PASS

- [ ] **Step 8: Commit changes**
  ```bash
  git add tests/experiments/harness.py tests/test_experiments.py
  git commit -m "feat(harness): support cover letter heading and structure evaluation"
  ```

---

### Task 3: Update Guidelines and System Prompts

**Files:**
- Modify: `data/guides/how-to-write-a-cover-letter.md`
- Modify: `data/prompts/cover.md`

- [ ] **Step 1: Rewrite House Guide (`data/guides/how-to-write-a-cover-letter.md`)**
  Update the document to specify the 3-question H2 structured template:
  *   Provide precise expectations for the hook, proof points, and logistics sections.
  *   Mandate proper double blank lines formatting between sections and headings.

- [ ] **Step 2: Update System Prompt Template (`data/prompts/cover.md`)**
  Incorporate strict Markdown H2 heading rules into `data/prompts/cover.md`.
  Ensure that we specify the headings must be:
  `## 1. Why [Company]?`, `## 2. Why me?`, and `## 3. Why now?`
  Add instructions that when translating to German (Symmetrical translates), the headings translate to `## 1. Warum [Company]?`, `## 2. Warum ich?`, `## 3. Warum jetzt?`.

- [ ] **Step 3: Commit changes**
  ```bash
  git add data/guides/how-to-write-a-cover-letter.md data/prompts/cover.md
  git commit -m "docs(guide): update cover letter instructions to enforce three-question structured template"
  ```