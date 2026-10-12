# QA brief: the reviewer, and the fix round that follows

**Purpose.** You review the assembled page before it is integrated, in four parts: a browser pass with the Playwright CLI, the `check_page.py` content checks, a fact-check of technique cards against the notes and transcripts, and a written report that tells the fixers exactly which FILE to edit. You do not fix anything yourself. After the report, the orchestrator runs a fix round whose protocol is at the end of this file.

**Inputs** (relative to `<workspace>`): `project.json` (`repo`, `page`, `mode`, `units` with `new`, `unit_label`, `section_prefix`); `out/<page>`, the assembled page; `build/parts/*.html` and `build/tpl/unit-<n>.tpl.html` (to name the file to fix); `notes/<id>.md` and `transcripts/<id>.md` of the new units; `<skill>/references/markup-guide.md` (the contract you check against); `<repo>/index.html` after the integrator has edited it.

**Outputs.** `qa/QA_REPORT.md`, screenshots in `qa/shots/`, raw check output in `qa/check-out.txt`.

## Part 1: the browser pass
Use the Playwright CLI only; never a browser MCP server, even if one is available.

**Install** (once per workspace, in `<workspace>/qa`):
```bash
cd <workspace>/qa && npm init -y >/dev/null && npm install --save-dev @playwright/cli && npx playwright-cli install
npx playwright-cli --help          # the verbs you need: open/navigate, resize, eval (run JS), console, screenshot
```
**Serve the REPO ROOT on a temporary port.** That way `js/read-aloud.js`, `js/find.js` and `index.html` resolve by the same relative paths as in production. A page opened as `file://`, or served from the workspace alone, loses both scripts, and the search and fixed-button checks then test nothing.
```bash
PORT=8137; python3 -m http.server $PORT --directory <repo> >qa/server.log 2>&1 &   # kill it when done
```
There are two passes:
- **First pass, before integration.** The page under test is `<workspace>/out/<page>`, and the repo still has the old copy or none. Do not copy into the repo unless the orchestrator says so. Instead, make `qa/site/` holding a copy of `out/<page>`, a symlink `js -> <repo>/js` and a symlink `index.html -> <repo>/index.html`. Serve `qa/site` the same way; it resolves exactly like the repo root.
- **Final pass, after integration.** Serve `<repo>` itself and test `<repo>/<page>` and `<repo>/index.html`. Check 6 below, the home-page card, belongs to this pass.
**Check at three widths**, 1280, 390 and 320 (resize, then reload), and take a screenshot of the hero, one unit section and one technique card at each width into `qa/shots/d-*.png` and `m-*.png`:
1. **Console errors.** Anything but a `favicon.ico` 404 is a finding; a JS error is a blocker.
2. **Horizontal scroll, and which element causes it.** Run via eval:
   ```js
   (() => { const w = document.documentElement.clientWidth; const bad = [];
     document.querySelectorAll('body *').forEach(e => { const r = e.getBoundingClientRect(); if (r.right > w + 1 || r.left < -1) bad.push(e.tagName + (e.id ? '#' + e.id : '') + '.' + e.className + ' ' + Math.round(r.right - w)); });
     return { scrollW: document.documentElement.scrollWidth, clientW: w, offenders: bad.slice(0, 15) }; })()
   ```
   Any `scrollW > clientW` at 390 or 320 is a blocker; name the offender.
3. **Anchors landing below the sticky nav.** Navigate to `#<section_prefix>-N` and to a `#t<n>-k`, then eval `({target: document.querySelector(location.hash).getBoundingClientRect().top, navBottom: document.querySelector('nav.top').getBoundingClientRect().bottom})`. `target` must be ≥ `navBottom` at every width; if not, the fix is the skeleton's `scroll-padding-top` (desktop and the 640px media query).
4. **The find.js search works.** Open the search (the nav button, or press `/`), type a word that appears in a new unit, and confirm hits are highlighted and the result list groups by card. Also confirm the search opens a closed `details.qa` that contains a hit.
5. **The fixed buttons do not overlap.** The to-top button, the search button and the read-aloud player: eval their `getBoundingClientRect()` and check no two rectangles intersect at 390 and 320, with the player open (click a speaker icon) and closed.
6. **The new card on `index.html` opens the page.** Load `index.html`, find the card (`article.book` whose link is `<page>`), click its `a.go`, confirm the URL; click two "בדף" TOC links and confirm each lands on an existing section.
7. **Load time.** From the performance timing, `domContentLoadedEventEnd` and `loadEventEnd`; report the page's byte size. Over 5 MB or over 2 s locally is a should-fix with a suggestion (split transcripts, trim), not a blocker.

## Part 2: `check_page.py`
```bash
python3 -I <skill>/scripts/check_page.py --config <workspace>/project.json        # new units
python3 -I <skill>/scripts/check_page.py --config <workspace>/project.json --all  # every unit on the page
```
Save the output to `qa/check-out.txt`. Classify every finding by the list below, whatever level the script prints. If a finding prints under a name not listed here, classify it by meaning, and quote the name as printed in your report. Findings and what they mean:
- `holy-name`, `name-permutation`: the four-letter Name, or a permutation of its letters as a standalone word. Blocker, unless the hit is an ordinary word (`והיה`), which you say explicitly.
- `plain-אהיה` / `plain-אדני` / `plain-שדי` (and the vocalized variants): a Name written as a pronounced word instead of with gershayim. Should-fix; in transcripts the fix is `make_transcripts.py`'s replacement list.
- `made-by`: a mention of AI, a model, or a tool anywhere outside the allowed transcript credit. Blocker.
- `religion`: another religion named in AUTHORED text. Blocker in authored sections; in the verbatim transcripts, report and let the orchestrator decide (the default is to leave the record as spoken and keep every mention out of the cards).
- `latin-in-text`: Latin letters outside URLs and `<bdi>`. Should-fix.
- `duplicate-id`, `dangling-anchor`: ids used twice, `href="#…"` with no target. Should-fix; a dangling link in a `.inl` or the index is a blocker.
- `raw-ampersand`: `&t=` instead of `&amp;t=`. Should-fix.
- `time-without-bdi`, `chip-no-bdi`: a time or a number not isolated in `<bdi>`; renders reversed in RTL. Should-fix.
- `chip-lesson-mismatch`, `chip-time-mismatch`, `yt-unknown-id`, `yt-t-beyond-duration`, `yt-t-malformed`: a chip whose label says one unit and whose URL points at another, or a `t=` past the video's end. Should-fix, and a sign the writer copied a chip from another unit.
- `yt-other-link`: a link to a video that is not one of the units. Informational; list them so nobody "fixes" them.
- `h4-outside-steps`, `script-in-part`, inline `style=`: contract violations. Should-fix.
- `global` / status tags: cards with no primary status tag, or a tag outside the vocabulary. Should-fix.
- `stats`: counts (cards, chips, ids) for your report.

## Part 3: fact-check
Spot-read **3 technique cards per new unit**: the first card, one from the middle, and the one with the most steps. For each, compare every field, step, names block, table, warning, quote and source range with `notes/<id>.md`, and where the notes hedge, with `transcripts/<id>.md`:
- **Invented**: a number, name, source, condition, step, or quoted phrase that is not in the notes or the transcript. Any quoted string of 12+ characters must exist in the transcript within a few words. A conjecture inside quotation marks counts as invented.
- **Missing**: a step from the notes' "השלבים" list that the card lacks; a locator the notes have for this technique that the card does not link.
- **Unhedged**: "(לא ודאי)", "כנראה" or `[?]` in the notes that the card states flatly; a status tag that contradicts the notes' section 9; a `.warn` the notes have that the card dropped.
- Decode every chip's `t=` and check it is within ±3 s of the notes' locator for the same detail.
Also eyeball: the h2 has no series prefix; the closing h3s follow the contract's order and wording; `[?]` appears in no `h3` or `.inl`; time ranges are single `<bdi>`; other nations are generic.

## Part 4: the report, `qa/QA_REPORT.md`
Header: what was checked (file, timestamp, widths, browser), counts by severity, and a line listing what came out CLEAN (so the fixers do not re-check it). Then three groups:
- **Blocker**: the page cannot ship. The full Name; an AI or tool mention; another religion named in authored text; a JS error; horizontal scroll at 390 or 320; a dangling link from the index or `.inl`; invented content in a card; a missing section.
- **Should-fix**: contract violations and fact-check findings that mislead (unhedged claims, wrong tags, reversed times, Latin in text, unverified counts).
- **Nice-to-have**: polish, weight, wording.
Each item has: an id (`S3`, `N2`), **where** (part file and line, the card or element id, the width if visual, the screenshot name), **what** (one or two sentences, with the measured numbers), and **the file to fix**: the TEMPLATE `build/tpl/unit-<n>.tpl.html` for anything in a unit section (never the rendered part), the part file for a synthesis section, `build/skeleton.html` for CSS and nav, `make_transcripts.py`'s replacement list for transcripts, and the suggested change. Group items that share one cause under one id with a list of locations. End with "Re-run after the fixes" naming the commands.

## The FIX round (run by the orchestrator after the report)
0. **Write a short shared fix spec first**, `qa/FIX_SPEC.md`. It records the decisions every fixer must apply the same way: the tag a disputed card gets, the wording of a heading, how a hedge reads, and which items are deliberately left alone. Without it, parallel fixers each invent their own vocabulary, and QA finds a new inconsistency on the next pass. Each fixer reads it before editing.
1. **Split by disjoint file ownership.** One agent per unit template or per group of templates, e.g. units 1–4 and units 5–8 (`build/tpl/unit-<n>.tpl.html`), one for each synthesis part that needs changes, one for the skeleton. Nobody edits a file someone else owns; nobody edits a rendered unit part by hand.
2. Each fixer gets the report's items for its files, edits with small targeted replacements (sed or Python `str.replace` on exact strings), and **re-renders** its unit: `render_tpl.py --config … --unit <n>`. It touches nothing the report does not list, and never changes ids, timestamps or card order.
3. When all fixers are done, one agent runs `assemble.py`, `make_transcripts.py` if the transcripts changed, `coverage.py` (coverage must not drop) and `check_page.py --all`.
4. The reviewer re-runs the browser pass if any CSS or layout item was fixed, re-reads the cards the report named, and appends a "Verified fixed" list to `qa/QA_REPORT.md`. Items still open go back to step 1.

## Report back (10 lines or fewer)
Counts by severity, the blockers in one line each, the clean list, where the report and screenshots are.
