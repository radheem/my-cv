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

    if (body.action === 'search_emails') {
      return json(searchEmails(body.query || '', body.limit || 20, body.includeBodies));
    }
    if (body.action === 'get_thread') {
      return json(getThread(body.threadId));
    }
    if (body.action === 'batch_modify_threads') {
      return json(batchModifyThreads(body.threadIds || [], body.markRead, body.markStarred, body.markImportant));
    }
    if (body.action === 'batch_send_emails') {
      return json(batchSendEmails(body.emails || []));
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

function searchEmails(query, limit, includeBodies) {
  var threads = GmailApp.search(query || '', 0, limit || 20);
  var results = [];
  for (var i = 0; i < threads.length; i++) {
    var thread = threads[i];
    var messages = thread.getMessages();
    var lastMessage = messages[messages.length - 1];
    var snippet = "";
    if (lastMessage) {
      var body = lastMessage.getPlainBody() || "";
      // Strip newlines/multiple spaces and grab first 150 characters
      snippet = body.replace(/\s+/g, ' ').substring(0, 150);
    }
    
    var threadData = {
      id: thread.getId(),
      subject: thread.getFirstMessageSubject(),
      date: thread.getLastMessageDate().getTime(),
      snippet: snippet,
      isUnread: thread.isUnread(),
      isStarred: thread.hasStarredMessages(),
      isImportant: thread.isImportant(),
      messages: []
    };
    if (includeBodies) {
      for (var j = 0; j < messages.length; j++) {
        var msg = messages[j];
        var plainBody = msg.getPlainBody() || '';
        if (plainBody.length > 32768) {
          plainBody = plainBody.substring(0, 32768) + "\n... [TRUNCATED BY PROXY] ...";
        }
        threadData.messages.push({
          id: msg.getId(),
          sender: msg.getFrom(),
          to: msg.getTo(),
          date: msg.getDate().getTime(),
          body: plainBody
        });
      }
    }
    results.push(threadData);
  }
  return { ok: true, threads: results };
}

function batchModifyThreads(threadIds, markRead, markStarred, markImportant) {
  if (!threadIds || threadIds.length === 0) return { ok: true, modifiedCount: 0 };
  var threads = [];
  for (var i = 0; i < threadIds.length; i++) {
    try {
      var t = GmailApp.getThreadById(threadIds[i]);
      if (t) threads.push(t);
    } catch (e) {}
  }
  if (threads.length === 0) return { ok: true, modifiedCount: 0 };
  
  if (markRead === true) GmailApp.markThreadsRead(threads);
  else if (markRead === false) GmailApp.markThreadsUnread(threads);
  
  if (markImportant === true) threads.forEach(function(t) { t.markImportant(); });
  else if (markImportant === false) threads.forEach(function(t) { t.markUnimportant(); });
  
  if (markStarred === true) {
    threads.forEach(function(t) {
      var msgs = t.getMessages();
      if (msgs.length > 0) msgs[0].star();
    });
  } else if (markStarred === false) {
    threads.forEach(function(t) {
      t.getMessages().forEach(function(m) { m.unstar(); });
    });
  }
  return { ok: true, modifiedCount: threads.length };
}

function batchSendEmails(emails) {
  var results = [];
  var successCount = 0;
  for (var i = 0; i < emails.length; i++) {
    var email = emails[i];
    try {
      var options = {};
      if (email.attachments && email.attachments.length > 0) {
        options.attachments = email.attachments.map(function(att) {
          return Utilities.newBlob(Utilities.base64Decode(att.b64), att.mimeType || 'application/octet-stream', att.name);
        });
      }
      MailApp.sendEmail({to: email.to, subject: email.subject, body: email.body, attachments: options.attachments});
      results.push({ to: email.to, status: 'success' });
      successCount++;
    } catch (e) {
      results.push({ to: email.to, status: 'failed', error: String(e) });
    }
  }
  return { ok: true, sentCount: successCount, details: results, remainingQuota: MailApp.getRemainingDailyQuota() };
}

function getThread(threadId) {
  try {
    var thread = GmailApp.getThreadById(threadId);
    if (!thread) return { ok: false, error: 'Thread not found: ' + threadId };
    
    var messages = thread.getMessages();
    var lastMessage = messages[messages.length - 1];
    var snippet = "";
    if (lastMessage) {
      var body = lastMessage.getPlainBody() || "";
      snippet = body.replace(/\s+/g, ' ').substring(0, 150);
    }
    
    var threadData = {
      id: thread.getId(),
      subject: thread.getFirstMessageSubject(),
      date: thread.getLastMessageDate().getTime(),
      snippet: snippet,
      isUnread: thread.isUnread(),
      isStarred: thread.hasStarredMessages(),
      isImportant: thread.isImportant(),
      messages: []
    };
    
    for (var j = 0; j < messages.length; j++) {
      var msg = messages[j];
      var plainBody = msg.getPlainBody() || '';
      if (plainBody.length > 32768) {
        plainBody = plainBody.substring(0, 32768) + "\n... [TRUNCATED BY PROXY] ...";
      }
      threadData.messages.push({
        id: msg.getId(),
        sender: msg.getFrom(),
        to: msg.getTo(),
        date: msg.getDate().getTime(),
        body: plainBody
      });
    }
    return { ok: true, thread: threadData };
  } catch (e) {
    return { ok: false, error: String(e) };
  }
}
