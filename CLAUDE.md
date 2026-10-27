# Kabbalah library — rules for Claude

## HTML pages
- Every new `.html` page added to this repo must also be added to `index.html`, the same way the existing pages are listed:
  - a link in the top `nav.top`,
  - a card (`article.book`) in `#pages` with cover, description, tags, a "בדף" table of contents linking to the page's section ids, and a "לדף" button,
  - a link in the footer list,
  - update the page count in the hero `.dates` line (and the hero summary sentence if relevant),
  - add a row for it in `README.md`.
- Every page except `index.html` links back to the home page: `<a class="nav-home" href="index.html">ספריית הקבלה</a>` as the first item of its top nav, styled gold and bold (`nav.top a.nav-home{color:var(--gold);font-weight:700}`).
- All HTML pages and "artifacts" are created as local files in this repo. Never publish them as claude.ai Artifacts.

## Sefirot colors (always)
- Whenever a page, drawing, yichud or diagram shows sefirot or holy names, use ONLY the sefirot colors from `tzayach-shir-hasefirot.html` (שיר הספירות). The colors themselves live in ONE place: `js/sefirot-methods.js` (README.md mirrors them under "צבעי הספירות"). Never invent other colors.
- `js/sefirot-methods.js` is the single source for all sefirot colors: ours (שיר הספירות, the default) and every other method from the comparison table in `sefirot-colors.html`. To change a color or add a method, edit only that file:
  - the comparison table in `sefirot-colors.html#compare` is generated from it (do not hand-edit a table there);
  - pages paint from it: load `<script src="js/sefirot-methods.js"></script>` and mark colored elements with `data-sef="<keter|chochma|bina|chesed|gevura|tiferet|netzach|hod|yesod|malchut>"` (SVG circles/shapes get a fill, SVG gradients get their stop colors, HTML swatches get `data-sef-as="bg"` or the default dot style; `data-sef-m="<method id>"` for a method other than ours). Inline hex in the HTML is only a fallback;
  - a whole list of swatches for one method: `<ul data-sef-list="<method id>">` is filled from the file (used on the meditation page for the Ramak);
  - in JS use `SEFIROT.entry(sefira, methodId)`, `SEFIROT.bg(...)`, `SEFIROT.letterCss(...)`, `SEFIROT.pillCss(...)`.
  - New drawings must use `data-sef` (or these helpers), never new hard-coded hex values. If a color changes, also update the README table.
- A holy name takes the color of the sefira where it is said in the song: אהי"ה = כתר, י"ה = חכמה, אלקים חיים = בינה, אל = חסד, אלקים = גבורה, הוי"ה = תפארת, ה' צבאות = נצח, אלקים צבאות = הוד, אל חי = יסוד, אדנ"י = מלכות. אין סוף has no sefira color, only light.
- In combined (interleaved) names, each letter keeps the color of the name it came from.
- New yichudim go into `otzar-hayichudim.html`.

## Holy names
- Do not write the name הוי"ה in full anywhere (text or images); write הוי"ה instead.

## Style and content
See `README.md` (design tokens, fonts, sefirot colors, and the content rules for the meditation page).

## Transcripts (תמלולים)
- Transcripts are never inline in the HTML. Every video transcript lives in `transcripts/<page>-<n>.json` (one file per lesson/video; `<page>` = the html file name without `.html`, `<n>` = the number in the `<details class="tr" id="tr-<n>">`). Schema: `{page, id, title, meta, video:{id,url}, count, lines:[{t, ts, text, html?, href?, cls?}]}` (`t` seconds, `ts` display stamp, `text` plain text unless `html:true`, `href` only when the line's link is not `video.url&t=<t>s`, `cls` a paragraph class such as `song`).
- The page keeps only the `<details class="tr" id="tr-<n>" data-transcript="transcripts/<page>-<n>.json">` with its `<summary>`, the lead paragraph and an empty `<div class="trbody"><p class="tr-loading">טוען תמלול…</p></div>`; `js/transcripts.js` (loaded before `js/find.js`) fetches and renders the lines. New pages with transcripts follow the same pattern; never paste transcript lines into the HTML.
- Loading needs HTTP (the site at netanele.github.io/kabbalah, or `python3 -m http.server` locally); from `file://` the loader shows an explanation instead.

## Books (ספרים) – Google Drive
- The user's book library is the Google Drive folder **"Torah/Books"**: https://drive.google.com/drive/folders/1xseNntc6xbkkVhNdppPMGO_rAaE9Q_0N (id `1xseNntc6xbkkVhNdppPMGO_rAaE9Q_0N`, with sub-folders). Every book that a page offers the learner to read is shown **inside the page as a PDF preview** of the file from this folder (`<iframe src="https://drive.google.com/file/d/<FILE_ID>/preview">`), never as a copy in the repo.
- If a needed book is not in the folder: find a downloadable PDF online (hebrewbooks, Sefaria, NLI, archive.org, publisher), give the user the link, and the user downloads it into the folder; then add its Drive file id to the page. Do not embed the external PDF directly.
- Book ids and titles live in one place, `js/books.js` (Drive file id, title, author, folder); pages reference books by key.
