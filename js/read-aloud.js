/* ספריית הקבלה: הקראה בקול.
   Every card and every heading that has text under it gets a speaker button (shown on hover).
   A click reads that card, or the text under that heading, with the computer's own voices
   (Hebrew voice for Hebrew, English voice for English). Divine Names are read by their substitutes. */
(function () {
  'use strict';
  var synth = window.speechSynthesis;
  if (!synth || !window.SpeechSynthesisUtterance) return;

  /* ---------- what is a unit ---------- */
  var CARDS = 'article.method, li.shelf-i, .deep .stage, .card, .pillar';
  var SKIP = 'script, style, svg, button, input, select, textarea, template, dialog, nav, .eras, .peek, .peek-go, .ra-player, .fd-panel, .fd-fab, ' +
             '.books, .bk, .read, .toolbar, .legend, .finder, details.toc, details.idx, .count, .totop, .lb, ' +
             '.num, .n, .stage-n, .sr, .shelf-ms, [aria-hidden="true"], [hidden]';
  var STOP = 'h1, h2, h3, h4, h5, h6, ' + CARDS + ', .deep-kicker, .extra-kicker, .book-kicker, footer.colophon';
  var LIST = '.foot, .meta';                       // short items read as a list
  var BLOCK = /^(block|list-item|table|table-row|table-cell|flex|grid|table-caption)$/;

  function isBlock(el) {
    var tag = el.tagName;
    if (/^(P|LI|DT|DD|BLOCKQUOTE|TR|TD|TH|H[1-6]|DIV|UL|OL|DL|TABLE|SECTION|HEADER|ARTICLE|SUMMARY|DETAILS|FIGCAPTION)$/.test(tag)) return true;
    try { return BLOCK.test(getComputedStyle(el).display); } catch (e) { return false; }
  }
  function next(n, root, skipKids) {
    if (!skipKids && n.firstChild) return n.firstChild;
    while (n && n !== root) {
      if (n.nextSibling) return n.nextSibling;
      n = n.parentNode;
    }
    return null;
  }
  function listText(el) {
    var loose = [].some.call(el.childNodes, function (c) { return c.nodeType === 3 && c.nodeValue.replace(/[\s·,|]/g, ''); });
    if (loose) return cleanText(el);
    var parts = [];
    [].forEach.call(el.children, function (c) {
      if (c.matches(SKIP)) return;
      var t = c.textContent.replace(/\s+/g, ' ').trim();
      if (t) parts.push(t);
    });
    return parts.length ? parts.join(', ') : el.textContent.replace(/\s+/g, ' ').trim();
  }
  function cleanText(el) {
    var c = el.cloneNode(true);
    c.querySelectorAll(SKIP).forEach(function (x) { x.remove(); });
    return c.textContent.replace(/\s+/g, ' ').trim();
  }
  /* walk from `start` (inside `root`); returns segments [{text, el}] */
  function walk(start, root, stopAt, skipStartKids) {
    var segs = [], cur = null, n = skipStartKids ? next(start, root, true) : start;
    function push(el) { cur = { text: '', el: el }; segs.push(cur); }
    while (n) {
      if (n.nodeType === 1) {
        if (n.matches(SKIP)) { n = next(n, root, true); continue; }
        if (stopAt && n.matches(stopAt)) break;
        if (n.matches(LIST)) {
          push(n); cur.text = listText(n); cur = null;
          n = next(n, root, true); continue;
        }
        if (isBlock(n)) push(n);
        n = next(n, root, false);
      } else {
        if (n.nodeType === 3 && n.nodeValue.trim()) {
          if (!cur) push(n.parentNode);
          cur.text += n.nodeValue;
        }
        n = next(n, root, false);
      }
    }
    return segs.map(function (s) { return { text: s.text.replace(/\s+/g, ' ').trim(), el: s.el }; })
               .filter(function (s) { return s.text; });
  }
  function mark(el, id) { el.setAttribute('data-ra', id); }

  var units = [];
  function cardSegs(u) { return walk(u.root, u.root, null, false); }
  function headSegs(u) {
    return [{ text: cleanText(u.head), el: u.head }].concat(walk(u.head, document.body, STOP, true));
  }
  function setup() {
    var id = 0;
    // cards
    document.querySelectorAll(CARDS).forEach(function (root) {
      if (root.closest('.peek') || root.parentNode.closest(CARDS)) return;
      var head = root.querySelector('h3, h4, h2');
      if (!head) return;
      var u = { id: id++, kind: 'card', root: root, head: head };
      units.push(u); mark(root, u.id); addButton(u);
    });
    // headings outside cards, with text under them
    document.querySelectorAll('h1, h2, h3, h4').forEach(function (h) {
      if (h.closest(CARDS) || h.closest(SKIP) || h.id === 'lb-t') return;
      var u = { id: id, kind: 'head', head: h, root: h };
      var segs = walk(h, document.body, STOP, true);
      if (!segs.length) return;
      id++; units.push(u); mark(h, u.id);
      segs.forEach(function (sg) { if (sg.el && sg.el.nodeType === 1 && !sg.el.hasAttribute('data-ra')) mark(sg.el, u.id); });   // hovering the text shows the button
      addButton(u);
    });
  }

  /* ---------- the button ---------- */
  var SPK = '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M4 9.5h3.2L12 5.6v12.8l-4.8-3.9H4z" fill="currentColor"/><path d="M15.2 9.2a3.6 3.6 0 0 1 0 5.6M17.6 6.8a7 7 0 0 1 0 10.4" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"/></svg>';
  function seekIcon(fwd) {   // a circular arrow with "5"
    var arc = fwd ? 'M12 6a7 7 0 1 0 6.06 3.5' : 'M12 6a7 7 0 1 1-6.06 3.5', head = fwd ? 'M9.6 3.6 12 6l-2.4 2.4' : 'M14.4 3.6 12 6l2.4 2.4';
    return '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="' + arc + '" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>' +
           '<path d="' + head + '" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>' +
           '<text x="12" y="16.3" text-anchor="middle" font-size="8" font-weight="700" fill="currentColor" font-family="Heebo,Arial,sans-serif">5</text></svg>';
  }
  var STOPI = '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><rect x="7" y="7" width="10" height="10" rx="1.6" fill="currentColor"/></svg>';
  var PAUSEI = '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><rect x="7" y="6" width="3.6" height="12" rx="1" fill="currentColor"/><rect x="13.4" y="6" width="3.6" height="12" rx="1" fill="currentColor"/></svg>';
  var PLAYI = '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M8 5.8v12.4L18 12z" fill="currentColor"/></svg>';
  function title(u) { return cleanText(u.head); }
  function addButton(u) {
    var b = document.createElement('button');
    b.type = 'button'; b.className = 'ra-btn'; b.innerHTML = SPK;
    b.setAttribute('aria-label', 'הקראה: ' + title(u)); b.title = 'הקראה';
    b.setAttribute('data-ra-btn', u.id);
    u.btn = b; u.head.appendChild(b);
  }

  /* ---------- text for speech ---------- */
  var HE = /[א-ת]/, EN = /[A-Za-z]/;
  var L = 'א-ת';
  var NUMWORDS = '(?:פרק|פרקים|חלק|שער|שערים|סימן|אות|אותיות|דף|כרך|פסוק|יום|מאמר|ספר|מזמור|הלכה|שורה|עמוד)';
  function speakHe(t) {
    t = t.replace(/[־]/g, ' ').replace(/[֑-ׇ]/g, '');          // maqaf, nikud and te'amim
    t = t.replace(/["“”]/g, function (q, i, s) {                                // gershayim inside a word
      return (HE.test(s.charAt(i - 1)) && HE.test(s.charAt(i + 1))) ? '״' : q; });
    t = t.replace(/'/g, '׳');
    // Divine Names: read by their substitutes
    t = t.replace(new RegExp('(^|[^' + L + '])([ובלמשהכ]{0,2})י[\\-]?ה[\\-]?ו[׳״\\-]{0,2}ה(?![' + L + '])', 'g'), '$1$2הויה');
    t = t.replace(new RegExp('(^|[^' + L + '])([ובלמשהכ]{0,2})הוי״ה(?![' + L + '])', 'g'), '$1$2הויה');
    t = t.replace(new RegExp('(^|[^' + L + '])([ובלמשהכ]{0,3})אל[הק](ים|י|יך|יו|ינו|יכם|יהם|ות|ית|יות)(?![' + L + '])', 'g'), '$1$2אלוק$3');
    t = t.replace(new RegExp('(^|[^' + L + '])([ובלמשהכ]{0,2})אדנ״?י(?![' + L + '])', 'g'), '$1$2אדנות');
    t = t.replace(new RegExp('(^|[^' + L + '])([ובלמשהכ]{0,2})שד״י(?![' + L + '])', 'g'), '$1$2שקי');
    t = t.replace(new RegExp('(^|[^' + L + '])([ובלמשהכ]{0,2})אהי״ה(?![' + L + '])', 'g'), '$1$2אקיה');
    t = t.replace(new RegExp('(?<!(?:^|[^' + L + '])[ובלמשהכ]{0,2}' + NUMWORDS + ')(^|[\\s(\\[״“„])([ובלמשכ]{0,2})ה׳(?![' + L + '])', 'g'), '$1$2השם');
    // common abbreviations
    var AB = { 'ר׳': 'רבי', 'זצלה״ה': 'זכר צדיק לברכה', 'זצ״ל': 'זכר צדיק לברכה', 'ז״ל': 'זכרונו לברכה',
               'ע״ה': 'עליו השלום', 'הקב״ה': 'הקדוש ברוך הוא', 'ע״פ': 'על פי', 'ע״י': 'על ידי',
               'וכו׳': 'וכולי', 'עמ׳': 'עמוד', 'כ״י': 'כתב יד', 'כתבי־יד': 'כתבי יד', 'אא״כ': 'אלא אם כן',
               'לפנה״ס': 'לפני הספירה', 'בעש״ט': 'בעל שם טוב', 'רשב״א': 'רשבא', 'חיד״א': 'חידא' };
    Object.keys(AB).forEach(function (k) {
      t = t.replace(new RegExp('(^|[^' + L + '])' + k + '(?![' + L + '])', 'g'), '$1' + AB[k]);
    });
    t = t.replace(/״/g, '');                                               // other acronyms: read as a word
    t = t.replace(/(\d)\s*[–—-]\s*(\d)/g, '$1 עד $2');
    t = t.replace(/[·•]/g, ',').replace(/\s[–—]\s/g, ', ').replace(/[←→]/g, ' ').replace(/\s\/\s/g, ', ');
    return t.replace(/\s+/g, ' ').trim();
  }
  function runs(text) {                       // split into Hebrew and English stretches
    var out = [], words = text.split(/\s+/);
    words.forEach(function (w) {
      var lang = HE.test(w) ? 'he' : EN.test(w) ? 'en' : null;
      var last = out[out.length - 1];
      if (!last) { out.push({ lang: lang || 'he', text: w }); return; }
      if (!lang || lang === last.lang) last.text += ' ' + w;
      else out.push({ lang: lang, text: w });
    });
    return out;
  }
  function sentences(t) {
    var out = [];
    t.split(/(?<=[.!?;])\s+/).forEach(function (s) {
      while (s.length > 220) {
        var cut = s.lastIndexOf(', ', 200); if (cut < 60) cut = s.lastIndexOf(' ', 200); if (cut < 60) cut = 200;
        out.push(s.slice(0, cut + 1)); s = s.slice(cut + 1);
      }
      if (s.trim()) out.push(s);
    });
    return out;
  }
  function queueFor(u) {
    var segs = u.kind === 'card' ? cardSegs(u) : headSegs(u), q = [];
    segs.forEach(function (s) {
      sentences(s.text).forEach(function (sen) {
        runs(sen).forEach(function (r) {
          var txt = r.lang === 'he' ? speakHe(r.text) : r.text.trim();
          if (/[\p{L}\p{N}]/u.test(txt)) q.push({ text: txt, lang: r.lang, el: s.el });
        });
      });
    });
    return q;
  }

  /* ---------- voices ---------- */
  var V = { he: null, en: null };
  function pickVoices() {
    var vs = synth.getVoices() || [];
    function best(re) {
      var c = vs.filter(function (v) { return re.test(v.lang); });
      c.sort(function (a, b) {
        function sc(v) { return (/premium|enhanced|siri/i.test(v.name) ? 4 : 0) + (v.localService ? 2 : 0) + (/^(he-IL|en-US)$/i.test(v.lang) ? 1 : 0); }
        return sc(b) - sc(a);
      });
      return c[0] || null;
    }
    V.he = best(/^(he|iw)(-|_|$)/i); V.en = best(/^en(-|_|$)/i);
  }
  pickVoices();
  if (synth.addEventListener) synth.addEventListener('voiceschanged', pickVoices); else synth.onvoiceschanged = pickVoices;

  /* ---------- player ---------- */
  var SPEEDS = [0.85, 1, 1.15, 1.3], speed = 1;
  try { var sv = parseFloat(localStorage.getItem('ra-speed')); if (SPEEDS.indexOf(sv) >= 0) speed = sv; } catch (e) {}
  var bar = document.createElement('div');
  bar.className = 'ra-player'; bar.hidden = true; bar.setAttribute('role', 'region'); bar.setAttribute('aria-label', 'הקראה');
  bar.innerHTML = '<span class="ra-tr" dir="ltr">' +
                    '<button type="button" class="ra-back" aria-label="5 שניות אחורה" title="5 שניות אחורה">' + seekIcon(false) + '</button>' +
                    '<button type="button" class="ra-pp" aria-label="השהיה">' + PAUSEI + '</button>' +
                    '<button type="button" class="ra-fwd" aria-label="5 שניות קדימה" title="5 שניות קדימה">' + seekIcon(true) + '</button>' +
                  '</span>' +
                  '<button type="button" class="ra-x" aria-label="עצירה" title="עצירה">' + STOPI + '</button>' +
                  '<span class="ra-t" aria-live="polite"></span>' +
                  '<button type="button" class="ra-sp" aria-label="מהירות ההקראה"></button>';
  var ppB = bar.querySelector('.ra-pp'), tEl = bar.querySelector('.ra-t'), spB = bar.querySelector('.ra-sp');
  spB.dir = 'ltr';
  function showSpeed() { spB.textContent = (speed === 1 ? '1' : String(speed)) + '×'; }
  showSpeed();

  var Q = [], qi = 0, cur = null, token = 0, paused = false, nowEl = null;
  /* where we are: Q[qi], from character `off`; the voice reports word starts (lastB), else time tells */
  var off = 0, lastB = -1, t0 = 0, pausedMs = 0, pauseT0 = 0;
  var CPS = { he: 13, en: 14 };                    // characters a second at speed 1; learned while reading
  function now() { return (window.performance && performance.now) ? performance.now() : Date.now(); }
  function elapsed() { if (!t0) return 0; return Math.max(0, ((paused ? pauseT0 : now()) - t0 - pausedMs) / 1000); }
  function position() {
    var it = Q[qi]; if (!it) return 0;
    var p = lastB >= 0 ? lastB : Math.round(elapsed() * CPS[it.lang] * speed);
    return Math.max(0, Math.min(it.text.length, off + p));
  }
  function learn(lang, chars) {
    var d = elapsed(); if (!t0 || d < 0.8 || chars < 15) return;
    var c = chars / d / speed; if (c > 4 && c < 40) CPS[lang] = CPS[lang] * 0.6 + c * 0.4;
  }
  function wordStart(text, p) { if (p <= 0) return 0; var sp = text.lastIndexOf(' ', p - 1); return sp < 0 ? 0 : sp + 1; }
  function clearMarks() {
    document.querySelectorAll('.ra-reading, .ra-now').forEach(function (e) { e.classList.remove('ra-reading', 'ra-now'); });
    document.querySelectorAll('.ra-btn.ra-active').forEach(function (b) { b.classList.remove('ra-active'); b.innerHTML = SPK; b.setAttribute('aria-pressed', 'false'); });
  }
  function stop() {
    token++; if (synth.paused) synth.resume(); synth.cancel(); clearMarks(); cur = null; Q = []; qi = 0; off = 0; lastB = -1; t0 = 0; paused = false; bar.hidden = true;
  }
  function setNow(el) {
    if (nowEl === el) return;
    if (nowEl) nowEl.classList.remove('ra-now');
    nowEl = el; if (el && el.nodeType === 1 && !(cur && cur.kind === 'card' && el === cur.root)) el.classList.add('ra-now');
  }
  function speakNext() {
    var my = token;
    if (qi >= Q.length) { stop(); return; }
    var it = Q[qi], text = it.text.slice(off), u = new SpeechSynthesisUtterance(text);
    var v = V[it.lang] || (it.lang === 'he' ? null : V.en);
    u.lang = it.lang === 'he' ? 'he-IL' : 'en-US'; if (v) u.voice = v;
    u.rate = speed;
    lastB = -1; t0 = 0; pausedMs = 0;
    u.onstart = function () { if (my !== token) return; t0 = now(); };
    u.onboundary = function (e) {
      if (my !== token) return;
      if (e && typeof e.charIndex === 'number' && (!e.name || e.name === 'word')) {
        lastB = e.charIndex;
        var d = elapsed(); if (d > 1.2 && lastB > 20) { var c = lastB / d / speed; if (c > 4 && c < 40) CPS[it.lang] = CPS[it.lang] * 0.85 + c * 0.15; }   // learn the voice's pace
      }
    };
    u.onend = function () { if (my !== token) return; learn(it.lang, text.length); qi++; off = 0; speakNext(); };
    u.onerror = function (e) { if (my !== token) return; if (e && (e.error === 'interrupted' || e.error === 'canceled')) return; qi++; off = 0; speakNext(); };
    setNow(it.el);
    synth.speak(u);
  }
  function play(u) {
    stop();
    if (!V.he) pickVoices();
    if (!V.he) {
      bar.hidden = false; bar.classList.add('ra-msg');
      tEl.textContent = 'לא נמצא במחשב קול עברי. אפשר להוסיף אותו בהגדרות המערכת: נגישות ← תוכן מוקרא ← קול המערכת ← ניהול קולות.';
      return;
    }
    bar.classList.remove('ra-msg');
    Q = queueFor(u); qi = 0; off = 0; cur = u; token++;
    if (!Q.length) return;
    var my = token;
    [u.btn, u.src && u.src.btn].forEach(function (bt) { if (bt) { bt.classList.add('ra-active'); bt.innerHTML = STOPI; bt.setAttribute('aria-pressed', 'true'); } });
    if (u.kind === 'card' && !u.src) u.root.classList.add('ra-reading');
    tEl.textContent = title(u); ppB.innerHTML = PAUSEI; ppB.setAttribute('aria-label', 'השהיה'); bar.hidden = false;
    setTimeout(function () { if (my === token) speakNext(); }, 80);
  }
  ppB.addEventListener('click', function () {
    if (!cur) { bar.hidden = true; return; }
    if (paused) { synth.resume(); pausedMs += now() - pauseT0; paused = false; ppB.innerHTML = PAUSEI; ppB.setAttribute('aria-label', 'השהיה'); }
    else { synth.pause(); pauseT0 = now(); paused = true; ppB.innerHTML = PLAYI; ppB.setAttribute('aria-label', 'המשך'); }
  });
  bar.querySelector('.ra-x').addEventListener('click', stop);
  function restartAt(i, p) {
    token++; if (synth.paused) synth.resume(); synth.cancel();
    paused = false; ppB.innerHTML = PAUSEI; ppB.setAttribute('aria-label', 'השהיה');
    qi = i; off = p; lastB = -1; t0 = 0;
    var my = token; setTimeout(function () { if (my === token) speakNext(); }, 80);
  }
  /* jump by seconds: walk through the sentences by their estimated length in time */
  function seek(sec) {
    if (!cur || !Q.length) return;
    var i = qi, p = position(), t = Math.abs(sec), it, r, left;
    if (sec > 0) {
      while (i < Q.length) {
        it = Q[i]; r = CPS[it.lang] * speed; left = (it.text.length - p) / r;
        if (left > t) { p += Math.round(t * r); break; }
        t -= left; i++; p = 0;
      }
      if (i >= Q.length) { stop(); return; }                 // past the end
    } else {
      while (true) {
        it = Q[i]; r = CPS[it.lang] * speed; left = p / r;
        if (left > t) { p -= Math.round(t * r); break; }
        t -= left; if (i === 0) { p = 0; break; }
        i--; p = Q[i].text.length;
      }
    }
    p = wordStart(Q[i].text, p);
    if (p >= Q[i].text.length) { i++; p = 0; if (i >= Q.length) { stop(); return; } }
    restartAt(i, p);
  }
  bar.querySelector('.ra-back').addEventListener('click', function () { seek(-5); });
  bar.querySelector('.ra-fwd').addEventListener('click', function () { seek(5); });
  spB.addEventListener('click', function () {
    speed = SPEEDS[(SPEEDS.indexOf(speed) + 1) % SPEEDS.length]; showSpeed();
    try { localStorage.setItem('ra-speed', String(speed)); } catch (e) {}
    if (cur && !paused && Q[qi]) restartAt(qi, wordStart(Q[qi].text, position()));   // go on from the current word at the new speed
  });

  /* ---------- events ---------- */
  document.addEventListener('click', function (ev) {
    var b = ev.target.closest && ev.target.closest('.ra-btn'); if (!b) return;
    ev.preventDefault(); ev.stopPropagation();
    var u = units[+b.getAttribute('data-ra-btn')]; if (!u) return;
    if (cur && (cur === u || cur.src === u)) { stop(); return; }
    var pk = b.closest('.peek');
    if (pk) {   // the card shown in the popup: read the copy in the popup, so the highlight is where the eye is
      var root = b.closest(CARDS) || pk;
      play({ id: u.id, kind: 'card', root: root, head: b.parentNode, btn: b, src: u });
      return;
    }
    play(u);
  }, true);
  var shown = null;
  document.addEventListener('mouseover', function (ev) {
    var o = ev.target.closest && ev.target.closest('[data-ra]');
    var u = o ? units[+o.getAttribute('data-ra')] : null;
    var b = u && u.btn;
    if (b === shown) return;
    if (shown) shown.classList.remove('ra-show');
    shown = b; if (b) b.classList.add('ra-show');
  });
  document.addEventListener('keydown', function (ev) { if (ev.key === 'Escape' && cur) stop(); });
  window.addEventListener('pagehide', function () { synth.cancel(); });

  /* ---------- styles ---------- */
  var css = '' +
    '.ra-btn{display:inline-grid;place-items:center;vertical-align:middle;width:30px;height:30px;margin-inline-start:8px;padding:0;border:1px solid var(--line,#dcd2c0);border-radius:50%;' +
    'background:var(--surface,var(--paper,#fffdf8));color:#8a6a2a;cursor:pointer;opacity:0;transition:opacity .15s,background .15s,color .15s;line-height:0;font-size:16px;position:relative;top:-2px}' +
    '.ra-btn svg{width:18px;height:18px}' +
    '.ra-btn.ra-show,.ra-btn:focus-visible,.ra-btn.ra-active{opacity:1}' +
    '.ra-btn:hover,.ra-btn.ra-active{background:var(--dark,#26221c);color:var(--gold2,#c9a75a);border-color:var(--dark,#26221c)}' +
    '.ra-btn:focus-visible{outline:2px solid var(--gold2,#c9a75a);outline-offset:2px}' +
    '.hero .ra-btn{background:transparent;color:var(--gold2,#c9a75a);border-color:rgba(201,167,90,.5);width:40px;height:40px;top:-8px}' +
    '.hero .ra-btn svg{width:24px;height:24px}' +
    '@media (hover:none){.ra-btn{opacity:.6}}' +
    '.ra-reading{outline:2px solid rgba(201,167,90,.55);outline-offset:4px;border-radius:6px}' +
    'article.ra-reading,.card.ra-reading,.pillar.ra-reading,li.ra-reading.shelf-i,.stage.ra-reading{outline-offset:2px;border-radius:16px}' +
    '.ra-now{background:rgba(201,167,90,.16);border-radius:6px;box-shadow:0 0 0 4px rgba(201,167,90,.16)}' +
    '.peek .ra-btn{opacity:1}' +
    '.ra-player{position:fixed;z-index:40;inset-inline:0;bottom:calc(env(safe-area-inset-bottom,0px) + 18px);margin:0 auto;width:max-content;max-width:calc(100vw - 110px);' +
    'display:flex;align-items:center;gap:8px;padding:6px 8px;border-radius:999px;background:var(--dark,#26221c);color:#f4ecdc;box-shadow:0 10px 30px rgba(30,27,23,.35);font-size:.92rem}' +
    '.ra-player[hidden]{display:none}' +
    '.ra-player button{display:grid;place-items:center;min-width:34px;height:34px;padding:0 8px;border:0;border-radius:999px;background:rgba(255,255,255,.08);color:var(--gold2,#c9a75a);cursor:pointer;font:600 .85rem inherit;font-family:inherit}' +
    '.ra-player button:hover{background:rgba(255,255,255,.18)}' +
    '.ra-player button svg{width:18px;height:18px}' +
    '.ra-tr{display:flex;align-items:center;gap:4px}' +
    '.ra-player .ra-back svg,.ra-player .ra-fwd svg{width:22px;height:22px}' +
    '.ra-t{overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:46vw;padding:0 6px}' +
    '.ra-player.ra-msg .ra-t{white-space:normal;max-width:70vw}' +
    '.ra-player.ra-msg .ra-tr,.ra-player.ra-msg .ra-sp{display:none}' +
    '@media print{.ra-btn,.ra-player{display:none!important}}';
  var st = document.createElement('style'); st.textContent = css; document.head.appendChild(st);

  function init() { setup(); document.body.appendChild(bar); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();

  /* for checking: window.__ra.texts(n) returns what would be read */
  window.__ra = { units: units, texts: function (i) { return queueFor(units[i]).map(function (x) { return x.lang + ': ' + x.text; }); } };
})();
