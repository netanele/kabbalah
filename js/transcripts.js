/* transcripts.js – טעינת תמלולים מקובצי JSON בתיקיית transcripts/.
   כל <details class="tr" data-transcript="transcripts/<file>.json"> מקבל את שורות התמלול
   לתוך ה-.trbody שלו. הקבצים נטענים ברקע אחרי טעינת הדף, בזה אחר זה, כדי שחיפוש בדף
   (find.js) ימצא גם את התמלולים.
   מבנה הקובץ: { page, id, title, meta, video:{id,url}, count, lines:[{t, ts, text, html?, href?, cls?}] }
   t = שניות; ts = חותמת זמן להצגה; text = הטקסט (אם html=true, הטקסט הוא HTML); href = קישור מיוחד לשורה (אם אינו video.url&t=);
   cls = מחלקת CSS לפסקה (למשל "song" לשורות שיר הספירות). */
(function () {
  'use strict';
  function esc(s) { return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;'); }

  function lineHref(data, ln) {
    if (ln.href) return ln.href;
    var base = (data.video && data.video.url) || '';
    if (!base) return '';
    return base + (base.indexOf('?') >= 0 ? '&' : '?') + 't=' + Math.max(0, Math.floor(ln.t || 0)) + 's';
  }

  function render(box, data) {
    var frag = document.createDocumentFragment();
    var lines = data.lines || [];
    for (var i = 0; i < lines.length; i++) {
      var ln = lines[i];
      var p = document.createElement('p');
      if (ln.cls) p.className = ln.cls;
      if (ln.ts != null) {
        var a = document.createElement('a');
        a.className = 'ts';
        var href = lineHref(data, ln);
        if (href) { a.href = href; a.target = '_blank'; a.rel = 'noopener'; }
        var b = document.createElement('bdi');
        b.textContent = ln.ts;
        a.appendChild(b);
        p.appendChild(a);
        p.appendChild(document.createTextNode(' '));
      }
      if (ln.html) {
        var span = document.createElement('span');
        span.innerHTML = ln.text || '';
        while (span.firstChild) p.appendChild(span.firstChild);
      } else {
        p.appendChild(document.createTextNode(ln.text || ''));
      }
      frag.appendChild(p);
    }
    box.innerHTML = '';
    box.appendChild(frag);
    box.dataset.loaded = '1';
  }

  function fail(box, src, err) {
    var local = location.protocol === 'file:';
    box.innerHTML = '<p class="tr-error">התמלול לא נטען' + (err ? ' (' + esc(err) + ')' : '') + '. ' +
      (local
        ? 'כשפותחים את הדף מקובץ מקומי הדפדפן חוסם טעינת קבצים. פתחו את הדף מהאתר <a href="https://netanele.github.io/kabbalah/" target="_blank" rel="noopener">netanele.github.io/kabbalah</a>, או הריצו שרת מקומי בתיקיית הפרויקט (<bdi dir="ltr">python3 -m http.server</bdi>) ופתחו <bdi dir="ltr">http://localhost:8000</bdi>. '
        : '') +
      'קובץ התמלול: <a href="' + esc(src) + '" target="_blank" rel="noopener"><bdi>' + esc(src) + '</bdi></a>.</p>';
    box.dataset.loaded = 'error';
  }

  function load(det) {
    var src = det.getAttribute('data-transcript');
    var box = det.querySelector('.trbody');
    if (!src || !box || box.dataset.loaded) return Promise.resolve();
    box.dataset.loaded = 'loading';
    return fetch(src, { cache: 'force-cache' })
      .then(function (r) { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); })
      .then(function (data) { render(box, data); det.dispatchEvent(new CustomEvent('transcript:loaded', { bubbles: true })); })
      .catch(function (e) { fail(box, src, e && e.message); });
  }

  function start() {
    var dets = Array.prototype.slice.call(document.querySelectorAll('details.tr[data-transcript]'));
    if (!dets.length) return;
    // תמלול שנפתח ידנית נטען מיד; השאר ברקע, אחד אחרי השני
    dets.forEach(function (d) {
      d.addEventListener('toggle', function () { if (d.open) load(d); });
    });
    var i = 0;
    function next() {
      if (i >= dets.length) return;
      var d = dets[i++];
      load(d).then(function () { setTimeout(next, 0); });
    }
    if (location.hash) {
      var target = document.getElementById(location.hash.slice(1));
      var td = target && target.closest ? target.closest('details.tr[data-transcript]') : null;
      if (td) { td.open = true; load(td); }
    }
    if ('requestIdleCallback' in window) requestIdleCallback(next, { timeout: 1500 }); else setTimeout(next, 300);
  }

  var style = document.createElement('style');
  style.textContent = '.trbody .tr-loading,.trbody .tr-error{color:#7a6a4a;font-size:.95em}.trbody .tr-error a{color:inherit}';
  document.head.appendChild(style);

  window.KabbalahTranscripts = { load: load, loadAll: function () { return Promise.all(Array.prototype.map.call(document.querySelectorAll('details.tr[data-transcript]'), load)); } };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start); else start();
})();
