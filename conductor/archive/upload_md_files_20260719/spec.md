# Specification: Upload Markdown Source Files to Google Drive

## Overview
This feature track enhances the application compilation and synchronization pipeline by uploading the raw, generated Markdown files alongside the compiled PDFs. This allows users to easily view, review, or retrieve the underlying text (English and German drafts) directly from their organized Google Drive folders without needing to access the local filesystem.

---

## Functional Requirements

### 1. Python CLI Pipeline Updates (`engine/cli.py`)
*   **Target Scope**: The `_build_app(slug)` helper method currently only returns successfully compiled `.pdf` files. It must be updated to additionally search the target application's directory for all raw Markdown source files.
*   **Behavior**: 
    1.  After executing the `_compile` step, the engine must collect all `.pdf` targets.
    2.  The engine must run a glob search to collect all `.md` files in the directory (e.g., `cv.md`, `cover-letter.md`, `cv.de.md`, `cover-letter.de.md`).
    3.  **Constraint**: The internal local state file (`index.md`) must be strictly ignored/filtered out of this collection.
    4.  All collected valid files must be returned as a unified list to `cmd_upload()`, which will Base64 encode them and dispatch the unified payload to the Apps Script proxy.

### 2. Google Apps Script Proxy Updates (`apps-script/Code.gs`)
*   **Target Scope**: The remote Apps Script endpoint currently forces an `application/pdf` MIME type on all incoming files within the `doPost` upload loop.
*   **Behavior**:
    1.  The `doPost` loop must dynamically parse the incoming `f.name` file extension.
    2.  If the file extension ends with `.md`, it must instantiate the blob with the `text/markdown` MIME type instead of `application/pdf`.
    3.  The files must be dropped into the identical Drive folder as the PDFs (Same Folder approach).
    4.  Idempotency logic must remain intact: if a file with the same name already exists in the folder, it is moved to the trash before writing the updated blob.

---

## Non-Functional Requirements
*   **Backwards Compatibility**: The Apps Script change must not disrupt the existing PDF uploads. PDF blobs must continue to receive the `application/pdf` MIME type.
*   **Security**: Ensure that local Git secrets, environment files, or `.json` metadata from the application folder are not accidentally glob-collected or uploaded.

---

## Acceptance Criteria
*   Calling `cv-tailor upload` or executing the Stage 2 compilation workflow successfully transmits both PDFs and `.md` files to the Apps Script endpoint.
*   The Apps Script correctly assigns `text/markdown` to Markdown files, ensuring they are viewable natively in Google Drive.
*   The `index.md` file is explicitly ignored and NOT uploaded.
*   Unit tests for `cli._build_app` verify that the returned list contains the correct combination of PDFs and Markdowns while excluding ignored files.
