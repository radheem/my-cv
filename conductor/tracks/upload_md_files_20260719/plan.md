# Implementation Plan: Upload Markdown Source Files to Google Drive

## Phase 1: Engine Collection Update
- [x] Task: Update local file collection (a75611b)
    - [ ] Write failing unit tests in `tests/test_cli_paths.py` (or similar) ensuring `_build_app` collects `.md` files alongside `.pdf` files, while explicitly ignoring `index.md`.
    - [ ] Modify `engine/cli.py` -> `_build_app()` to glob all `*.md` files in the directory.
    - [ ] Implement filter to safely exclude `index.md`.
    - [ ] Ensure tests pass (Green phase).
- [x] Task: Conductor - User Manual Verification 'Phase 1: Engine Collection Update' (Protocol in workflow.md) (a75611b)

## Phase 2: Apps Script MIME Type Detection
- [x] Task: Update Google Apps Script logic (ebab9ad)
    - [ ] Modify `apps-script/Code.gs` inside the `doPost` file processing loop.
    - [ ] Add dynamic MIME type detection: check if `f.name` ends with `.md` and assign `text/markdown`, otherwise default to `application/pdf`.
    - [ ] Verify there are no syntax errors in the JS file.
    - [ ] Note: Since this is an external script, automated tests are skipped. Manual deployment will be required by the user.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Apps Script MIME Type Detection' (Protocol in workflow.md)
