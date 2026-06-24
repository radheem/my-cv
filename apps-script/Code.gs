/**
 * Drive uploader for cv-tailor — a Google Apps Script web app.
 *
 * `cv-tailor upload <slug>` POSTs the compiled cv.pdf + cover-letter.pdf here as
 * base64. The web app runs AS YOU (Execute as: Me), so the files are created in
 * YOUR Drive (no service-account quota problem on a personal account), in a
 * per-application subfolder of ROOT_FOLDER_ID. Returns the folder URL.
 *
 * Setup: see apps-script/README.md. Deploy: Web app · Execute as: Me ·
 * Who has access: Anyone (the TOKEN is the guard). Paste the /exec URL + token
 * into the repo's .env (APPS_SCRIPT_URL / APPS_SCRIPT_TOKEN).
 */

var ROOT_FOLDER_ID = 'REPLACE_WITH_DRIVE_FOLDER_ID';   // the "Applications" Drive folder
var TOKEN = 'REPLACE_WITH_A_LONG_RANDOM_STRING';        // must match APPS_SCRIPT_TOKEN
var SHEET_ID = 'REPLACE_WITH_SPREADSHEET_ID';           // Google Sheets spreadsheet ID for tracker
var TRACKER_SHEET = 'Applications';

function json(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}

function findOrCreate(parent, name) {
  var it = parent.getFoldersByName(name);
  return it.hasNext() ? it.next() : parent.createFolder(name);
}

function syncTracker(csvText) {
  var ss = SpreadsheetApp.openById(SHEET_ID);
  var sh = ss.getSheetByName(TRACKER_SHEET) || ss.insertSheet(TRACKER_SHEET);
  var rows = Utilities.parseCsv(csvText);
  sh.clearContents();
  if (rows.length > 0) {
    sh.getRange(1, 1, rows.length, rows[0].length).setValues(rows);
    sh.getRange(1, 1, 1, rows[0].length).setFontWeight('bold');
  }
  return { ok: true, rows: rows.length };
}

function archiveApplication(slug) {
  var root = DriveApp.getFolderById(ROOT_FOLDER_ID);
  var archive = findOrCreate(root, 'Archive');
  var it = root.getFoldersByName(slug);
  if (!it.hasNext()) return { ok: false, error: 'folder not found: ' + slug };
  var folder = it.next();
  folder.moveTo(archive);
  return { ok: true, folderUrl: folder.getUrl() };
}

function doPost(e) {
  try {
    var body = JSON.parse(e.postData.contents);
    if (body.token !== TOKEN) return json({ ok: false, error: 'unauthorized' });

    if (body.action === 'sync_tracker') {
      if (!body.csv) return json({ ok: false, error: 'missing csv' });
      return json(syncTracker(body.csv));
    }

    if (body.action === 'get_tracker') {
      var ss = SpreadsheetApp.openById(SHEET_ID);
      var sh = ss.getSheetByName(TRACKER_SHEET);
      if (!sh || sh.getLastRow() === 0) return json({ ok: true, csv: '' });
      var data = sh.getDataRange().getValues();
      var csvLines = data.map(function(row) {
        return row.map(function(cell) {
          var s = String(cell);
          return (s.indexOf(',') !== -1 || s.indexOf('"') !== -1 || s.indexOf('\n') !== -1)
            ? '"' + s.replace(/"/g, '""') + '"' : s;
        }).join(',');
      });
      return json({ ok: true, csv: csvLines.join('\n') });
    }

    if (body.action === 'archive_application') {
      if (!body.slug) return json({ ok: false, error: 'missing slug' });
      return json(archiveApplication(body.slug));
    }

    if (!body.slug) return json({ ok: false, error: 'missing slug' });

    var folder = findOrCreate(DriveApp.getFolderById(ROOT_FOLDER_ID), body.slug);
    var out = [];
    (body.files || []).forEach(function (f) {
      // Idempotent: trash an existing same-name file before re-creating.
      var ex = folder.getFilesByName(f.name);
      while (ex.hasNext()) ex.next().setTrashed(true);
      var blob = Utilities.newBlob(Utilities.base64Decode(f.b64), 'application/pdf', f.name);
      out.push({ name: f.name, url: folder.createFile(blob).getUrl() });
    });
    return json({ ok: true, folderUrl: folder.getUrl(), files: out });
  } catch (err) {
    return json({ ok: false, error: String(err) });
  }
}

function doGet() {
  return json({ ok: true, service: 'cv-tailor drive uploader' });
}
