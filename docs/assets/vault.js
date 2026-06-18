/* cv-tailor client-side gate.
 *
 * The gated CV / cover-letter / job-description pages are AES-256-GCM sealed at
 * build time (see encrypt.py / build.py). This script asks for the password,
 * derives the key with PBKDF2-SHA256 via Web Crypto, and decrypts each blob in
 * memory: HTML is shown in a sandboxed iframe, PDFs download as a Blob.
 *
 * Two modes (dispatched on #vault-app data attributes):
 *   - Landing (data-mode="index"): decrypt an encrypted manifest of applications
 *     (titles live only in the ciphertext, so nothing leaks pre-sign-in) and
 *     render the list of links.
 *   - Per-job (data-slug=...): decrypt that application's CV / cover-letter / PDF.
 *
 * Sign in once: on a successful unlock the password is cached in sessionStorage
 * (salt-scoped, per tab) so the per-job hubs auto-unlock without re-prompting.
 * The derived key never leaves the browser. A direct visit to a per-job URL with
 * no cached password still shows its own prompt.
 *
 * Blob format (base64): iv[12] || ciphertext||GCM-tag — matching encrypt.seal().
 */
(function () {
  "use strict";

  function b64ToBytes(b64) {
    var bin = atob(b64.trim());
    var out = new Uint8Array(bin.length);
    for (var i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i);
    return out;
  }

  async function deriveKey(password, saltBytes, iterations) {
    var enc = new TextEncoder();
    var base = await crypto.subtle.importKey(
      "raw", enc.encode(password), "PBKDF2", false, ["deriveKey"]
    );
    return crypto.subtle.deriveKey(
      { name: "PBKDF2", salt: saltBytes, iterations: iterations, hash: "SHA-256" },
      base,
      { name: "AES-GCM", length: 256 },
      false,
      ["decrypt"]
    );
  }

  async function decryptBlob(key, encB64) {
    var raw = b64ToBytes(encB64);
    var iv = raw.slice(0, 12);
    var data = raw.slice(12);
    return crypto.subtle.decrypt({ name: "AES-GCM", iv: iv }, key, data);
  }

  async function fetchEnc(file) {
    var resp = await fetch("vault/" + file, { cache: "no-store" });
    if (!resp.ok) throw new Error("missing " + file);
    return resp.text();
  }

  function el(tag, attrs, text) {
    var node = document.createElement(tag);
    if (attrs) Object.keys(attrs).forEach(function (k) { node.setAttribute(k, attrs[k]); });
    if (text) node.textContent = text;
    return node;
  }

  function renderUnlocked(app, key, assets) {
    app.innerHTML = "";
    var actions = el("div", { class: "vault-actions" });
    var viewer = el("div", { class: "vault-viewer" });

    assets.forEach(function (a) {
      var view = el("button", { class: "md-button", type: "button" }, "View " + a.label);
      view.addEventListener("click", async function () {
        try {
          var buf = await decryptBlob(key, await fetchEnc(a.html));
          var html = new TextDecoder().decode(buf);
          viewer.innerHTML = "";
          var frame = el("iframe", {
            class: "vault-frame",
            sandbox: "allow-same-origin allow-popups",
            title: a.label
          });
          viewer.appendChild(frame);
          frame.srcdoc = html;
        } catch (e) { viewer.textContent = "Could not display " + a.label + "."; }
      });
      actions.appendChild(view);

      if (a.pdf) {
        var dl = el("button", { class: "md-button md-button--primary", type: "button" },
          "Download " + a.label + " (PDF)");
        dl.addEventListener("click", async function () {
          try {
            var buf = await decryptBlob(key, await fetchEnc(a.pdf));
            var url = URL.createObjectURL(new Blob([buf], { type: "application/pdf" }));
            var link = el("a", { href: url, download: a.key + ".pdf" });
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
          } catch (e) { alert("Could not decrypt the PDF."); }
        });
        actions.appendChild(dl);
      }
    });

    app.appendChild(actions);
    app.appendChild(viewer);
  }

  // Sign-in-once: cache the password per tab, scoped by build salt (one salt is
  // shared across the landing manifest and every per-job hub in a build), so the
  // hubs auto-unlock from the landing sign-in. Caching the password (not the raw
  // key) keeps the key non-extractable and re-derives per page. Demo polish.
  function pwKey(config) { return "cvtailor.pw." + config.salt; }
  function cachePassword(config, pw) {
    try { sessionStorage.setItem(pwKey(config), pw); } catch (e) { /* ignore */ }
  }
  function getCachedPassword(config) {
    try { return sessionStorage.getItem(pwKey(config)); } catch (e) { return null; }
  }
  function clearCachedPassword(config) {
    try { sessionStorage.removeItem(pwKey(config)); } catch (e) { /* ignore */ }
  }

  function renderList(app, apps) {
    app.innerHTML = "";
    var list = el("div", { class: "vault-actions vault-list" });
    apps.forEach(function (a) {
      var link = el("a", { class: "md-button", href: a.url });
      link.appendChild(document.createTextNode(a.title + (a.company ? " · " + a.company : "")));
      if (a.status) {
        // Status drives a CSS class; restrict to a safe token to avoid markup.
        var token = String(a.status).toLowerCase().replace(/[^a-z]/g, "");
        link.appendChild(
          el("span", { class: "vault-badge vault-badge--" + token }, a.status)
        );
      }
      list.appendChild(link);
    });
    app.appendChild(list);
  }

  // Decrypt the landing manifest and render the application list.
  async function unlockIndex(app, config, password) {
    var key = await deriveKey(password, b64ToBytes(config.salt), config.iterations);
    var buf = await decryptBlob(key, await fetchEnc(config.index));
    var apps = JSON.parse(new TextDecoder().decode(buf));
    cachePassword(config, password);
    renderList(app, apps);
  }

  // Decrypt a single application's assets and render its viewer.
  async function unlockJob(app, config, password) {
    var key = await deriveKey(password, b64ToBytes(config.salt), config.iterations);
    // Validate by decrypting the first asset — a wrong password fails the GCM
    // auth tag and throws.
    await decryptBlob(key, await fetchEnc(config.assets[0].html));
    cachePassword(config, password);
    renderUnlocked(app, key, config.assets);
  }

  // Build the sign-in form. `unlock(password)` decrypts + renders, or throws on a
  // wrong password.
  function renderForm(app, unlock) {
    var form = el("form", { class: "vault-form" });
    var input = el("input", {
      type: "password",
      placeholder: "Password",
      autocomplete: "current-password",
      "aria-label": "Password"
    });
    var submit = el("button", { class: "md-button md-button--primary", type: "submit" }, "Unlock");
    var error = el("p", { class: "vault-error", hidden: "hidden" });

    form.appendChild(input);
    form.appendChild(submit);
    app.appendChild(form);
    app.appendChild(error);

    form.addEventListener("submit", async function (ev) {
      ev.preventDefault();
      error.hidden = true;
      submit.disabled = true;
      submit.textContent = "Unlocking…";
      try {
        await unlock(input.value);
      } catch (e) {
        submit.disabled = false;
        submit.textContent = "Unlock";
        error.textContent = "Incorrect password.";
        error.hidden = false;
      }
    });
  }

  // Try a cached password first (auto-unlock); fall back to the form.
  async function gate(app, config, unlock) {
    var cached = getCachedPassword(config);
    if (cached) {
      try { await unlock(cached); return; }
      catch (e) { clearCachedPassword(config); }
    }
    renderForm(app, function (pw) { return unlock(pw); });
  }

  function init() {
    var app = document.getElementById("vault-app");
    var cfgEl = document.getElementById("vault-config");
    if (!app || !cfgEl) return;
    var config;
    try { config = JSON.parse(cfgEl.textContent); } catch (e) { return; }

    if (app.dataset.mode === "index") {
      if (!config.index) {
        app.textContent = "No protected documents are available yet.";
        return;
      }
      gate(app, config, function (pw) { return unlockIndex(app, config, pw); });
      return;
    }

    if (!config.assets || !config.assets.length) {
      app.textContent = "No protected documents are available yet.";
      return;
    }
    gate(app, config, function (pw) { return unlockJob(app, config, pw); });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
