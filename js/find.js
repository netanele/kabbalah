/* ספריית הקבלה: חיפוש בדף.
   Every match on the page is highlighted; "הבא" / "הקודם" go from match to match; a list shows all the results,
   grouped by card or section. Search ignores niqqud, geresh/gershayim and quotes, and Latin case and accents. */
(function () {
  'use strict';
  var SKIP = 'script, style, noscript, template, svg, button, input, select, textarea, nav, .eras, dialog, .lb, ' +
             '.fd-panel, .fd-fab, .peek, .ra-player, .finder, .toolbar, .legend, .count, details.toc, details.idx, ' +
             '.sr, [aria-hidden="true"], .totop, .num, .stage-n, .n, .shelf-ms, .bk-go, .read > a, .peek-go';
  var CARDS = 'article.method, li.shelf-i, .deep .stage, .card, .pillar';
  var INLINE = /^(A|ABBR|B|BDI|BDO|CITE|CODE|DFN|EM|I|KBD|MARK|Q|S|SAMP|SMALL|SPAN|STRONG|SUB|SUP|TIME|U|VAR|WBR|BR|LABEL)$/;
  var MAX = 1500;

  /* ---------- normalising: what counts as the same text ---------- */
  function normChar(ch) {
    var c = ch.charCodeAt(0);
    if ((c >= 0x05D0 && c <= 0x05EA) || (c >= 0x61 && c <= 0x7A) || (c >= 0x30 && c <= 0x39)) return ch;   // Hebrew letters, a-z, digits
    if (c >= 0x41 && c <= 0x5A) return String.fromCharCode(c + 32);                                       // A-Z
    if (c === 32 || c === 9 || c === 10 || c === 13 || c === 0xA0 || c === 0x05BE) return ' ';             // spaces, maqaf
    if (c === 0x200E || c === 0x200F) return '';                                                          // direction marks
    if ((c >= 0x0591 && c <= 0x05BD) || (c >= 0x05BF && c <= 0x05C7)) return '';                          // niqqud, te'amim
    if (c === 0x05F3 || c === 0x05F4 || c === 0x22 || c === 0x27 || c === 0x60 ||
        (c >= 0x2018 && c <= 0x201F) || (c >= 0x02BB && c <= 0x02BF)) return '';                          // geresh, gershayim, quotes
    if (c === 0x2D || (c >= 0x2010 && c <= 0x2015)) return ' ';                                           // dashes
    if (c <= 0x7F) return ch;
    if (c >= 0x0590 && c <= 0x05FF) return ch;
    if (/\s/.test(ch)) return ' ';
    return ch.normalize ? ch.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase() : ch.toLowerCase();   // Latin with accents
  }
  function normQuery(q) {
    var out = '';
    for (var i = 0; i < q.length; i++) { var n = normChar(q[i]); if (n === ' ' && (out === '' || out[out.length - 1] === ' ')) continue; out += n; }
    return out.trim();
  }

  /* ---------- the page's text, in blocks ---------- */
  function blockOf(el) { while (el && el !== document.body && INLINE.test(el.tagName)) el = el.parentElement; return el; }
  function isHeading(el) { return /^H[1-4]$/.test(el.tagName); }
  function collect() {
    var segs = [], cur = null, lastHead = null;
    var w = document.createTreeWalker(document.body, NodeFilter.SHOW_ELEMENT | NodeFilter.SHOW_TEXT, {
      acceptNode: function (n) { return (n.nodeType === 1 && n.matches(SKIP)) ? NodeFilter.FILTER_REJECT : NodeFilter.FILTER_ACCEPT; }
    });
    var n;
    while ((n = w.nextNode())) {
      if (n.nodeType === 1) { if (isHeading(n) && !n.closest(CARDS)) lastHead = n; continue; }
      if (!n.nodeValue) continue;
      var b = blockOf(n.parentElement);
      if (!cur || cur.block !== b) { cur = { block: b, head: lastHead, nodes: [], orig: '', norm: '', map: [], o2: [] }; segs.push(cur); }
      var ni = cur.nodes.length; cur.nodes.push(n);
      var t = n.nodeValue;
      for (var i = 0; i < t.length; i++) {
        var nc = normChar(t[i]);
        for (var k = 0; k < nc.length; k++) {
          if (nc[k] === ' ' && (cur.norm === '' || cur.norm[cur.norm.length - 1] === ' ')) continue;
          cur.norm += nc[k]; cur.map.push([ni, i]); cur.o2.push(cur.orig.length + i);
        }
      }
      cur.orig += t;
    }
    return segs;
  }

  /* ---------- state ---------- */
  var hits = [], groups = [], idx = -1, lastQ = '', onlyCards = false;

  function clearMarks() {
    var parents = [];
    document.querySelectorAll('mark.fd-hit').forEach(function (m) {
      var p = m.parentNode; if (!p) return;
      while (m.firstChild) p.insertBefore(m.firstChild, m);
      p.removeChild(m); if (parents.indexOf(p) < 0) parents.push(p);
    });
    parents.forEach(function (p) { p.normalize(); });
    document.querySelectorAll('.fd-hide').forEach(function (e) { e.classList.remove('fd-hide'); });
    document.querySelectorAll('.fd-has').forEach(function (e) { e.classList.remove('fd-has'); });
    hits = []; groups = []; idx = -1;
  }
  function cardTitle(card) {
    var h = card.querySelector('h2, h3, h4'); var t = h ? clean(h) : '';
    var num = card.querySelector('.num'); if (num && num.textContent.trim()) t = num.textContent.trim() + ' · ' + t;
    return t || clean(card).slice(0, 60);
  }
  function clean(el) {
    var c = el.cloneNode(true); c.querySelectorAll(SKIP).forEach(function (x) { x.remove(); });
    return c.textContent.replace(/\s+/g, ' ').trim();
  }
  function search(q) {
    clearMarks();
    var nq = normQuery(q); lastQ = q;
    if (nq.length < 2) return render(nq.length ? 'short' : 'empty');
    var segs = collect(), found = [];
    segs.forEach(function (s) {
      var from = 0, at;
      while (found.length < MAX && (at = s.norm.indexOf(nq, from)) >= 0) { found.push({ seg: s, s: at, e: at + nq.length }); from = at + nq.length; }
    });
    // wrap, last first, so the earlier offsets stay right
    for (var i = found.length - 1; i >= 0; i--) {
      var f = found[i], s = f.seg, a = s.map[f.s], z = s.map[f.e - 1], marks = [];
      for (var ni = z[0]; ni >= a[0]; ni--) {
        var node = s.nodes[ni], st = ni === a[0] ? a[1] : 0, en = ni === z[0] ? z[1] + 1 : node.nodeValue.length;
        if (en <= st) continue;
        var r = document.createRange(); r.setStart(node, st); r.setEnd(node, en);
        var m = document.createElement('mark'); m.className = 'fd-hit';
        try { r.surroundContents(m); marks.unshift(m); } catch (e) {}
      }
      f.marks = marks;
    }
    hits = found.filter(function (f) { return f.marks.length; });
    hits.forEach(function (h, i) {
      h.marks.forEach(function (m) { m.setAttribute('data-fd', i); });
      var card = h.marks[0].closest(CARDS);
      h.card = card && !card.closest('.peek') ? card : null;
      h.key = h.card || h.seg.head || document.body;
    });
    // groups, in page order
    hits.forEach(function (h, i) {
      var g = groups[groups.length - 1];
      if (!g || g.key !== h.key) {
        g = { key: h.key, items: [], title: h.card ? cardTitle(h.card) : (h.seg.head ? clean(h.seg.head) : document.title) };
        groups.push(g);
      }
      g.items.push(i);
      if (h.card) h.card.classList.add('fd-has');
    });
    applyOnly();
    render('ok');
    if (hits.length) go(firstInView(), true);
  }
  function firstInView() {
    var top = panelBottom();
    for (var i = 0; i < hits.length; i++) {
      var r = hits[i].marks[0].getBoundingClientRect();
      if (r.height && r.top >= top) return i;
    }
    return 0;
  }
  function applyOnly() {
    document.querySelectorAll(CARDS).forEach(function (c) {
      if (c.closest('.peek')) return;
      c.classList.toggle('fd-hide', onlyCards && hits.length > 0 && !c.classList.contains('fd-has'));
    });
  }

  /* ---------- moving between results ---------- */
  function visible(el) { return !!(el.getClientRects().length); }
  function reveal(el) {
    for (var d = el.closest('details'); d; d = d.parentElement && d.parentElement.closest('details')) d.open = true;
    if (visible(el)) return;
    var all = document.querySelector('#count button');          // meditation page: the "הצג הכול" of the level and index filters
    if (all) all.click();
    ['cat', 'conf'].forEach(function (id) {                     // Abulafia page: the two selects
      var s = document.getElementById(id); if (s && s.value) { s.value = ''; s.dispatchEvent(new Event('change', { bubbles: true })); }
    });
  }
  function scrollToEl(el) {
    var r = el.getBoundingClientRect(), top = panelBottom(), h = window.innerHeight;
    var y = Math.max(0, window.scrollY + r.top - (top + (h - top) / 2) + r.height / 2);
    if (Math.abs(y - window.scrollY) > h * 1.5) {     // far away: jump at once; near: glide
      var de = document.documentElement, old = de.style.scrollBehavior;
      de.style.scrollBehavior = 'auto'; window.scrollTo(0, y); de.style.scrollBehavior = old;
    } else window.scrollTo({ top: y, behavior: 'smooth' });
  }
  function go(i, quiet) {
    if (!hits.length) return;
    idx = (i + hits.length) % hits.length;
    document.querySelectorAll('mark.fd-cur').forEach(function (m) { m.classList.remove('fd-cur'); });
    var h = hits[idx];
    if (onlyCards && h.card) h.card.classList.remove('fd-hide');
    reveal(h.marks[0]);
    h.marks.forEach(function (m) { m.classList.add('fd-cur'); });
    scrollToEl(h.marks[0]);
    showCount();
    var row = list.querySelector('[data-i="' + idx + '"]'), grp = null;
    list.querySelectorAll('.fd-on').forEach(function (e) { e.classList.remove('fd-on'); });
    if (!row) { groups.some(function (g) { if (g.items.indexOf(idx) >= 0) { grp = g; return true; } }); row = grp && list.querySelector('[data-g="' + groups.indexOf(grp) + '"]'); }
    if (row) {
      row.classList.add('fd-on');
      if (list.offsetParent) {   // keep the row in view inside the list, without moving the page
        var lr = list.getBoundingClientRect(), rr = row.getBoundingClientRect();
        if (rr.top < lr.top) list.scrollTop -= (lr.top - rr.top) + 8; else if (rr.bottom > lr.bottom) list.scrollTop += (rr.bottom - lr.bottom) + 8;
      }
    }
  }

  /* ---------- the panel ---------- */
  var MAG = '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><circle cx="10.5" cy="10.5" r="6" fill="none" stroke="currentColor" stroke-width="2"/><path d="M15 15l5 5" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/></svg>';
  var UP = '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M6 15l6-6 6 6" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>';
  var DOWN = '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M6 9l6 6 6-6" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>';
  var X = '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M7 7l10 10M17 7L7 17" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>';
  var panel = document.createElement('div');
  panel.className = 'fd-panel'; panel.hidden = true; panel.setAttribute('role', 'search'); panel.setAttribute('aria-label', 'חיפוש בדף');
  panel.innerHTML =
    '<div class="fd-head"><h2 class="fd-title">חיפוש בדף</h2><button type="button" class="fd-close" aria-label="סגירת החיפוש" title="סגירה (Esc)">' + X + '</button></div>' +
    '<div class="fd-field">' + MAG + '<input type="search" class="fd-q" placeholder="מילה, ספר, שם חכם או מושג" aria-label="מה לחפש בדף" autocomplete="off" enterkeyhint="search">' +
      '<button type="button" class="fd-clear" aria-label="ניקוי החיפוש" title="ניקוי">' + X + '</button></div>' +
    '<div class="fd-nav"><span class="fd-count" aria-live="polite"></span>' +
      '<button type="button" class="fd-prev" title="התוצאה הקודמת (Shift+Enter)">' + UP + '<span>הקודם</span></button>' +
      '<button type="button" class="fd-next" title="התוצאה הבאה (Enter)"><span>הבא</span>' + DOWN + '</button></div>' +
    '<div class="fd-opts"><label class="fd-only"><input type="checkbox"> להציג רק כרטיסים עם תוצאות</label>' +
      '<button type="button" class="fd-lt" aria-expanded="false">כל התוצאות</button></div>' +
    '<div class="fd-list" role="list"></div>' +
    '<p class="fd-help">Enter: התוצאה הבאה · Shift+Enter: הקודמת · Esc: סגירה · "/" פותח את החיפוש</p>';
  var qIn = panel.querySelector('.fd-q'), countEl = panel.querySelector('.fd-count'), list = panel.querySelector('.fd-list');
  var lt = panel.querySelector('.fd-lt');

  function esc(s) { return s.replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function snippet(h) {
    var s = h.seg, o1 = s.o2[h.s], o2 = s.o2[h.e - 1] + 1, t = s.orig;
    var a = Math.max(0, o1 - 50), b = Math.min(t.length, o2 + 60);
    if (a > 0) { var sp = t.indexOf(' ', a); if (sp > 0 && sp < o1) a = sp + 1; }
    if (b < t.length) { var sp2 = t.lastIndexOf(' ', b); if (sp2 > o2) b = sp2; }
    return (a > 0 ? '…' : '') + esc(t.slice(a, o1).replace(/\s+/g, ' ')) + '<mark>' + esc(t.slice(o1, o2)) + '</mark>' +
           esc(t.slice(o2, b).replace(/\s+/g, ' ')) + (b < t.length ? '…' : '');
  }
  function showCount() {
    var n = hits.length, more = n >= MAX ? '+' : '';
    countEl.textContent = idx >= 0 ? (idx + 1) + ' מתוך ' + n + more : n + more + ' תוצאות';
  }
  function render(state) {
    panel.classList.toggle('fd-none', state !== 'ok' || !hits.length);
    list.textContent = '';
    if (state === 'empty') { countEl.textContent = ''; lt.textContent = 'כל התוצאות'; return; }
    if (state === 'short') { countEl.textContent = 'לפחות 2 אותיות'; lt.textContent = 'כל התוצאות'; return; }
    if (!hits.length) { countEl.textContent = 'אין תוצאות'; lt.textContent = 'כל התוצאות'; list.innerHTML = '<p class="fd-empty">לא נמצא בדף. נסה מילה אחרת, או חלק ממילה.</p>'; return; }
    showCount();
    lt.textContent = 'כל התוצאות (' + hits.length + (hits.length >= MAX ? '+' : '') + ')';
    var html = '', rows = 0;
    groups.forEach(function (g, gi) {
      html += '<div class="fd-g" role="listitem"><button type="button" class="fd-gt" data-g="' + gi + '"><span>' + esc(g.title) + '</span><b>' + g.items.length + '</b></button>';
      g.items.slice(0, 3).forEach(function (i) {
        if (rows++ > 600) return;
        html += '<button type="button" class="fd-sn" data-i="' + i + '">' + snippet(hits[i]) + '</button>';
      });
      if (g.items.length > 3) html += '<button type="button" class="fd-more" data-i="' + g.items[3] + '">ועוד ' + (g.items.length - 3) + ' כאן</button>';
      html += '</div>';
    });
    list.innerHTML = html;
  }
  list.addEventListener('click', function (ev) {
    var b = ev.target.closest('button'); if (!b) return;
    if (b.hasAttribute('data-i')) go(+b.getAttribute('data-i'));
    else if (b.hasAttribute('data-g')) go(groups[+b.getAttribute('data-g')].items[0]);
    if (window.matchMedia('(max-width:1099px)').matches) setList(false);
  });
  function setList(on) { panel.classList.toggle('fd-listopen', on); lt.setAttribute('aria-expanded', on ? 'true' : 'false'); }
  lt.addEventListener('click', function () { setList(!panel.classList.contains('fd-listopen')); });
  panel.querySelector('.fd-next').addEventListener('click', function () { go(idx + 1); });
  panel.querySelector('.fd-prev').addEventListener('click', function () { go(idx - 1); });
  panel.querySelector('.fd-close').addEventListener('click', close);
  panel.querySelector('.fd-clear').addEventListener('click', function () { qIn.value = ''; search(''); qIn.focus(); });
  panel.querySelector('.fd-only input').addEventListener('change', function (ev) {
    onlyCards = ev.target.checked; applyOnly(); if (idx >= 0) go(idx, true);
  });
  var timer = 0;
  qIn.addEventListener('input', function () { clearTimeout(timer); timer = setTimeout(function () { search(qIn.value); }, 250); });
  qIn.addEventListener('keydown', function (ev) {
    if (ev.key === 'Enter') {
      ev.preventDefault();
      if (qIn.value !== lastQ) { clearTimeout(timer); search(qIn.value); return; }
      go(ev.shiftKey ? idx - 1 : idx + 1);
    } else if (ev.key === 'ArrowDown') { ev.preventDefault(); go(idx + 1); }
    else if (ev.key === 'ArrowUp') { ev.preventDefault(); go(idx - 1); }
  });
  panel.addEventListener('keydown', function (ev) { if (ev.key === 'Escape') { ev.preventDefault(); ev.stopPropagation(); close(); } });

  function navEl() { return document.querySelector('nav.eras, nav.top'); }
  function panelBottom() {
    if (panel.hidden) { var nv = navEl(); return nv ? Math.max(0, nv.getBoundingClientRect().bottom) : 0; }
    if (window.matchMedia('(min-width:1100px)').matches) { var n2 = navEl(); return n2 ? Math.max(0, n2.getBoundingClientRect().bottom) : 0; }
    return panel.getBoundingClientRect().bottom;
  }
  function place() {
    var nv = navEl(), b = nv ? nv.getBoundingClientRect().bottom : 0;
    panel.style.setProperty('--fd-top', (b > 0 && b <= 140 ? Math.round(b + 8) : 8) + 'px');
  }
  function open() {
    var was = panel.hidden;
    panel.hidden = false; document.documentElement.classList.add('fd-open'); place();
    if (was) setList(window.matchMedia('(min-width:1100px)').matches);
    qIn.focus(); qIn.select();
    if (was && qIn.value) search(qIn.value);
  }
  function close() {
    clearTimeout(timer); clearMarks(); panel.hidden = true; document.documentElement.classList.remove('fd-open');
    var b = document.querySelector('.fd-navbtn'); if (b) b.focus({ preventScroll: true });
  }
  window.addEventListener('resize', function () { if (!panel.hidden) place(); });
  window.addEventListener('scroll', function () { if (!panel.hidden && !window.matchMedia('(min-width:1100px)').matches) place(); }, { passive: true });
  document.addEventListener('keydown', function (ev) {
    var t = ev.target, typing = t && (t.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/.test(t.tagName));
    if ((ev.key === '/' && !typing && !ev.metaKey && !ev.ctrlKey && !ev.altKey) || ((ev.metaKey || ev.ctrlKey) && (ev.key === 'k' || ev.key === 'K'))) {
      ev.preventDefault(); open();
    }
  });

  /* ---------- ways in: a button in the menu, a field where the old search was, a round button on phones ---------- */
  function launchers() {
    var nv = navEl();
    if (nv) {
      var b = document.createElement('button'); b.type = 'button'; b.className = 'fd-navbtn'; b.innerHTML = MAG + '<span>חיפוש בדף</span>';
      b.title = 'חיפוש בדף ( / )'; b.addEventListener('click', open);
      var into = nv.querySelector('.wrap') || nv; into.insertBefore(b, into.firstChild);
    }
    var old = document.getElementById('q');
    if (old) {
      var f = document.createElement('button'); f.type = 'button'; f.className = 'fd-launch';
      f.innerHTML = MAG + '<span>' + esc(old.getAttribute('placeholder') || 'חיפוש בדף') + '</span><kbd>/</kbd>';
      f.addEventListener('click', open);
      old.parentNode.insertBefore(f, old); old.classList.add('fd-oldq');
    }
    var fab = document.createElement('button'); fab.type = 'button'; fab.className = 'fd-fab'; fab.innerHTML = MAG;
    fab.setAttribute('aria-label', 'חיפוש בדף'); fab.addEventListener('click', open);
    document.body.appendChild(fab);
    document.body.appendChild(panel);
  }

  /* ---------- styles (the parchment and gold of the pages) ---------- */
  var css = '' +
    'mark.fd-hit{background:#f6df97;color:inherit;border-radius:3px;box-shadow:0 0 0 1px #e3c25f;padding:0 1px}' +
    'mark.fd-hit.fd-cur{background:#e9a822;color:#1e1b17;box-shadow:0 0 0 2px #8a6a2a;animation:fd-pulse .7s ease-out}' +
    '@keyframes fd-pulse{0%{box-shadow:0 0 0 7px rgba(233,168,34,.45)}100%{box-shadow:0 0 0 2px #8a6a2a}}' +
    '.fd-hide{display:none!important}' +
    '.fd-oldq{display:none!important}' +
    '.fd-launch{display:flex;align-items:center;gap:10px;width:100%;flex:1;min-width:220px;font:inherit;text-align:start;cursor:text;' +
      'padding:9px 12px;border:1px solid var(--line,#dcd2c0);border-radius:10px;background:#fffdf8;color:var(--muted,#6f665a)}' +
    '.fd-launch:hover{border-color:var(--gold,#9c7a33)}' +
    '.fd-launch svg{width:18px;height:18px;color:#8a6a2a;flex:none}.fd-launch span{flex:1}' +
    '.fd-launch kbd,.fd-help kbd{font:600 .78rem/1 monospace;border:1px solid var(--line,#dcd2c0);border-radius:5px;padding:2px 6px;color:#8a6a2a;background:#fff}' +
    '.fd-navbtn{display:inline-flex;align-items:center;gap:6px;font:inherit;font-size:.84rem;font-weight:700;color:#8a6a2a;background:#fffdf8;' +
      'border:1px solid #c9a75a;border-radius:999px;padding:3px 11px;cursor:pointer;flex:none;margin-inline-end:4px}' +
    '.fd-navbtn:hover{background:var(--dark,#26221c);color:#c9a75a;border-color:var(--dark,#26221c)}' +
    '.fd-navbtn svg{width:15px;height:15px}' +
    '.fd-fab{display:none;position:fixed;z-index:39;inset-inline-start:16px;bottom:calc(env(safe-area-inset-bottom,0px) + 16px);width:52px;height:52px;border-radius:50%;' +
      'border:0;background:var(--dark,#26221c);color:#c9a75a;box-shadow:0 6px 18px rgba(30,27,23,.35);cursor:pointer;place-items:center}' +
    '.fd-fab svg{width:24px;height:24px}' +
    '@media (max-width:700px){.fd-fab{display:grid}.fd-open .fd-fab{display:none}}' +
    '.fd-panel{position:fixed;z-index:50;box-sizing:border-box;background:var(--surface,var(--paper,#fffdf8));color:var(--ink,#26221c);font-family:inherit;' +
      'display:flex;flex-direction:column;gap:10px;padding:14px 16px 12px;box-shadow:0 18px 50px rgba(30,27,23,.28)}' +
    '.fd-panel[hidden]{display:none}' +
    '.fd-head{display:flex;align-items:center;justify-content:space-between}' +
    '.fd-title{margin:0;font-family:"Frank Ruhl Libre","David Libre",serif;font-size:1.3rem;font-weight:700;color:#3a2e1d}' +
    '.fd-close{display:grid;place-items:center;width:34px;height:34px;border-radius:50%;border:1px solid var(--line,#dcd2c0);background:transparent;color:#5a4423;cursor:pointer}' +
    '.fd-close svg{width:18px;height:18px}.fd-close:hover{background:#f3ecdf}' +
    '.fd-field{display:flex;align-items:center;gap:8px;border:2px solid #c9a75a;border-radius:12px;padding:4px 10px;background:#fff}' +
    '.fd-field:focus-within{border-color:#8a6a2a;box-shadow:0 0 0 3px rgba(201,167,90,.25)}' +
    '.fd-field svg{width:20px;height:20px;color:#8a6a2a;flex:none}' +
    '.fd-q{flex:1;min-width:0;border:0;outline:0;background:transparent;font:inherit;font-size:1.05rem;padding:7px 0;color:inherit}' +
    '.fd-q::-webkit-search-cancel-button{display:none}' +
    '.fd-clear{display:grid;place-items:center;width:28px;height:28px;border:0;border-radius:50%;background:#efe7d6;color:#5a4423;cursor:pointer}' +
    '.fd-clear svg{width:14px;height:14px}' +
    '.fd-nav{display:flex;align-items:center;gap:8px}' +
    '.fd-count{flex:1;font-weight:700;color:#4b3b22;font-size:.98rem}' +
    '.fd-prev,.fd-next{display:inline-flex;align-items:center;gap:4px;font:inherit;font-weight:700;font-size:.95rem;padding:7px 14px;border-radius:999px;cursor:pointer;' +
      'border:0;background:var(--dark,#26221c);color:#f4ecdc}' +
    '.fd-prev svg,.fd-next svg{width:18px;height:18px;color:#c9a75a}' +
    '.fd-prev:hover,.fd-next:hover{background:#3d352b}' +
    '.fd-none .fd-prev,.fd-none .fd-next{opacity:.35;pointer-events:none}' +
    '.fd-opts{display:flex;align-items:center;justify-content:space-between;gap:8px;font-size:.88rem;color:#5a4423}' +
    '.fd-only{display:flex;align-items:center;gap:6px;cursor:pointer}' +
    '.fd-only input{accent-color:#8a6a2a;width:16px;height:16px;flex:none;min-width:0;margin:0;padding:0}' +
    '.ra-player:not([hidden]) ~ .fd-fab{display:none!important}' +
    '.fd-lt{font:inherit;font-weight:700;color:#6d511d;background:#efe7d6;border:0;border-radius:999px;padding:4px 12px;cursor:pointer}' +
    '.fd-list{display:none;overflow:auto;overscroll-behavior:contain;border-top:1px solid var(--line,#dcd2c0);padding-top:6px;margin:0 -6px}' +
    '.fd-listopen .fd-list{display:block}' +
    '.fd-g{padding:4px 6px 8px;border-bottom:1px dashed var(--line,#dcd2c0)}' +
    '.fd-gt{display:flex;align-items:center;gap:8px;width:100%;text-align:start;font:inherit;font-family:"Frank Ruhl Libre","David Libre",serif;font-weight:700;' +
      'font-size:1.02rem;color:#3a2e1d;background:none;border:0;padding:4px 2px;cursor:pointer}' +
    '.fd-gt span{flex:1}.fd-gt b{font-family:inherit;font-size:.75rem;background:#efe7d6;color:#6a4b12;border-radius:999px;padding:1px 8px;font-weight:700}' +
    '.fd-gt:hover span{text-decoration:underline;text-decoration-color:#c9a75a}' +
    '.fd-sn,.fd-more{display:block;width:100%;text-align:start;font:inherit;font-size:.9rem;line-height:1.55;color:#3a3227;background:none;border:0;border-radius:8px;padding:5px 8px;cursor:pointer}' +
    '.fd-sn:hover,.fd-more:hover{background:#f3ecdf}' +
    '.fd-sn mark{background:#f6df97;border-radius:3px;padding:0 1px;color:inherit}' +
    '.fd-more{font-size:.82rem;color:#8a6a2a;font-weight:700}' +
    '.fd-on{background:#f6ecd2!important;box-shadow:inset 3px 0 0 #c9a75a}' +
    '.fd-empty{margin:8px 4px;color:var(--muted,#6f665a)}' +
    '.fd-help{margin:0;font-size:.76rem;color:var(--muted,#6f665a)}' +
    /* wide screens: a side panel on the left, the page moves aside */
    '@media (min-width:1100px){' +
      '.fd-panel{top:0;bottom:0;left:0;width:380px;border-right:1px solid var(--line,#dcd2c0);padding-top:18px}' +
      '.fd-list{flex:1;display:block}.fd-lt{display:none}' +
      'html.fd-open body{margin-left:380px}' +
    '}' +
    /* narrower: a sheet under the menu */
    '@media (max-width:1099px){' +
      '.fd-panel{top:var(--fd-top,8px);left:8px;right:8px;max-width:760px;margin:0 auto;border:1px solid var(--line,#dcd2c0);border-radius:16px;max-height:calc(100vh - var(--fd-top,8px) - 12px)}' +
      '.fd-list{max-height:45vh}.fd-help{display:none}' +
    '}' +
    '@media print{.fd-panel,.fd-fab,.fd-navbtn,.fd-launch{display:none!important}mark.fd-hit{background:none;box-shadow:none}}';
  var st = document.createElement('style'); st.textContent = css; document.head.appendChild(st);

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', launchers); else launchers();
  window.__fd = { open: open, search: search, go: go, state: function () { return { hits: hits.length, idx: idx, groups: groups.length }; } };
})();
