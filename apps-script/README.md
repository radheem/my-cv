# Drive uploader (Google Apps Script)

`cv-tailor upload <slug>` sends the compiled `cv.pdf` + `cover-letter.pdf` to your
Google Drive through this Apps Script web app. It runs **as you**, so the files are
owned by you (a service account can't own files in a personal *My Drive* — this avoids
that trap). One subfolder per application slug.

## One-time setup

1. **Create a Drive folder** (e.g. "CV Applications"). Open it; the URL ends in
   `/folders/<FOLDER_ID>` — copy that id.
2. Go to <https://script.google.com> → **New project**. Replace the default file with
   [`Code.gs`](Code.gs).
3. Set the two constants at the top:
   - `ROOT_FOLDER_ID` = the folder id from step 1.
   - `TOKEN` = a long random string (e.g. `openssl rand -hex 24`).
4. **Deploy** → *New deployment* → type **Web app**:
   - *Execute as*: **Me**
   - *Who has access*: **Anyone** (the token is the only guard)
   - Deploy, authorize the Drive scope, and copy the **/exec** URL.
5. Put the values in the repo's gitignored `.env`:
   ```
   APPS_SCRIPT_URL=https://script.google.com/macros/s/XXXX/exec
   APPS_SCRIPT_TOKEN=<the same TOKEN>
   GDRIVE_FOLDER_ID=<FOLDER_ID>     # optional; the script already pins it
   ```

## Use

```bash
cv-tailor upload moss-senior-platform-engineer-...   # compile + upload, writes drive_url
```

The command compiles the bilingual PDFs (LaTeX), POSTs them (base64, `Content-Type:
text/plain` to avoid a CORS preflight — same pattern as the gitpress forms), then writes
`drive_url` / `drive_updated` into the application's `index.md` and refreshes
`applications/README.md`. Re-running is idempotent (same folder, files replaced).

> The `/exec` URL + token are bearer secrets — keep them in `.env`, never commit them.
