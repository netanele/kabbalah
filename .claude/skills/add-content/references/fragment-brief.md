# Fragment brief: one unit's notes into its HTML section

**Purpose.** You turn ONE unit's structured notes into the unit's `<section>` on the page, by writing a macro template that `render_tpl.py` expands into HTML. You follow `markup-guide.md` (the contract) exactly; this brief tells you the order of work, the targets and the manifest. One writer per unit; several run in parallel, so touch only your unit's files.

**Inputs** (relative to `<workspace>`; `<skill>` is the skill folder that holds `scripts/` and `references/`):
- `project.json`: your unit's `n`, `id`, `kind`, `url`, `title`, `topic`, `duration_string` or `pages`, `date`; the page's `unit_label` and `section_prefix`.
- `<skill>/references/markup-guide.md`: the whole contract. Read it fully before anything else.
- `notes/<id>.md`: your notes, all of them. This is the content; everything in it goes on the page.
- `transcripts/<id>.md`: only to verify a doubtful detail or timestamp.
- In **existing** mode: ONE existing unit section of the page, to match tone and structure: `python3 -I <skill>/scripts/explode_page.py --config <workspace>/project.json` has already produced `build/parts/NN-<section_prefix>-<k>.html` for the old units; read the first 150 lines of the one nearest to yours in subject. In **new** mode, when another unit's part already exists in `build/parts/`, read its first 120 lines for the same reason.
- `build/parts/*.html` and the page: the ids you may link to (`grep -o 'id="[^"]*"'`).

**Outputs:**
- `build/tpl/unit-<n>.tpl.html`: the template (your hand-written file).
- `build/parts/NN-<section_prefix>-<n>.html`: rendered by `render_tpl.py`; never edit it by hand. NN is any order hint; `render_tpl.py` picks it.
- `build/parts/unit-<n>.manifest.md`: the manifest for the synthesis writers.

## The macros
`render_tpl.py --config <workspace>/project.json --unit <n>` expands, using your unit's `url` and `unit_label`:
- `@S(hh:mm:ss)` → a source chip `<a class="src" …><unit_label> N · <bdi>hh:mm:ss</bdi></a>` linking to that second of the video.
- `@T(hh:mm:ss)` → an inline time link `<a class="ts" …><bdi>hh:mm:ss</bdi></a>`, for running text where the sentence already says which unit.
- `@SRCS(a|b|c)` → a `<div class="srcs">` row holding one chip per timestamp.
- `@P(12)` → a page chip for text units, linking to `url#page=12` and labelled `<unit_label> N · עמ' <bdi>12</bdi>`.

In a text unit, `@P(N)` stands wherever this brief says `@S`, `@T` or `@SRCS`. Several page chips in a row go inside a plain `<div class="srcs">…</div>`. Section 9 of `markup-guide.md` shows the self-check.
Then it checks: leftover macros, tag balance, the full Name, raw `&t=`, inline styles, forbidden tags, Latin outside `<bdi>`, duplicate ids, dangling anchors into your own unit. Fix every PROBLEM line before continuing.

## How to write: mechanically, in small appends
Writers lost hours by composing a whole section in one generation and being cut off. Nothing is on disk until a tool call completes, so write in pieces and render often.

1. **First write** creates `build/tpl/unit-<n>.tpl.html` with: `<section id="<section_prefix>-<n>">`, the `h2` (`<span class="ln"><unit_label> N</span> <topic>`), the `p.lead`, the `.meta` row, the `ul.inl` chip list (one chip per technique card you are about to write, ids `t<n>-1 …` in the notes' order), and the outline card `<div class="card" id="l<n>-outline">` built from notes section 2 (one `<li>` per bullet, each starting with `@T(…)`).
2. **One append per technique card** (`cat >> … <<'EOF'`), in the notes' order, each under about 1,500 words. Card k gets `id="t<n>-k"`.
3. **Then one append per closing block**, in this order and with these exact `h3` words (skip a block the notes have nothing for; never invent content):
   1. `עקרונות, כללים ואזהרות` → `<div class="card" id="l<n>-principles">` with `ul.plain`, each `<li>` opening with `@T(…)`. Split into two appends if large.
   2. `ספרים, חכמים ומקורות שהוזכרו` → `<div class="card" id="l<n>-books">` holding the `.tw` table from notes section 5, its last column `@SRCS(…)`.
   3. `שאלות מהקהל` → one `details.qa` per question, ids `l<n>-qa-1 …`.
   4. `סיפורים ומעשים` → `<ul class="stories" id="l<n>-stories">`.
   5. `ציטוטים` → a run of `blockquote.q`.
   6. `מה שהרב לא גילה` → `<div class="card" id="l<n>-hidden">` with `ul.plain`; each `<li>` opens with the red tag that fits (vocabulary in the markup guide) and quotes the refusal.
   7. `ספקות בתמלול` → `<div class="doubt">` from notes section 10 and from every `[?]` you kept in the body.
   8. `</section>`.
4. **Render after every append or two**: `python3 -I <skill>/scripts/render_tpl.py --config <workspace>/project.json --unit <n>`. Partial progress is then always rendered and checked.
5. **At the end** run, from anywhere:
   ```bash
   python3 -I <skill>/scripts/assemble.py --config <workspace>/project.json
   python3 -I <skill>/scripts/coverage.py --config <workspace>/project.json
   python3 -I <skill>/scripts/check_page.py --config <workspace>/project.json
   ```
   Fix every report line about your part, re-render, re-run.

## Content rules (the contract has the markup; these are the targets)
- **Everything in the notes goes on the page.** Every `###` block of notes section 3 becomes its own `article.card.tech`, numbered `t<n>-k` in the notes' order, with `dl.fields`, `ol.steps` (every step with its own `@SRCS`), `.names` for formulas, names and verses, `.warn` for the speaker's caveats, the examples, and the closing `מקור בסרטון` ranges as a single `<bdi>` each. Blocks the notes mark "הוזכר בלבד" get their own small card each, tagged `הוזכר בלבד` (markup guide §4). Gather them into ONE card "פעולות שהוזכרו בלבד", with one `<li>` and its chips per item, only if your prompt asks for it. If you do, report the notes-versus-cards difference.
- **Target: 100% of the notes' locators on the page**, and cards equal to the notes' technique blocks. `coverage.py` prints, per unit, "techniques notes X / cards Y | timestamps notes N, in page M, covered P%" and lists the missing timestamps. Place each missing one where its content belongs (a step, the outline, the principles card, a story); do not pad with meaningless chips.
- **Tables in the notes** (figures, houses, letters, hours) become real `<table>` elements inside `<div class="tw">`, inside the card they belong to.
- **Type tags**: one or two plain type tags after the unit tag. The first one is the card's type, and the manifest's סוג repeats it.
- **Status tags**: every technique card gets exactly one primary status tag and zero or more red detail tags from the vocabulary in the markup guide (§6), decided from notes section 9 and the block's own text. The specific wording of what was withheld goes into `<dt>מה הרב לא גילה</dt>`.
- **Hedges survive.** "(לא ודאי)", "כנראה" and `[?]` in the notes stay in the card. Inline `[?]` stays in body text (the assembler styles it); it never appears in an `h3` or in an `.inl` label: move the doubt into the body with `<span class="tag r">לא ברור בתמלול</span>` or into `.doubt`.
- **Conjectures outside the quotes**: `"…כנגד הארמה [כנראה: א־רמל]"`.
- **Cross-unit links** go to EXISTING card ids only. Before writing `href="#t6-1"`, check: `grep -c 'id="t6-1"' <workspace>/build/parts/*.html <repo>/<page>`. When the notes say the technique continues an earlier unit, link to the earlier card in the `p.lead` or in a `.note`, and describe what is new here.
- **A research appendix** in the notes (`## נספח: הקשר מהמחקר`) is NOT merged into technique cards. At most one short `.note` after the technique cards, starting "מהמחקר:", with its source.
- **Hebrew only; the four-letter Name never in full** (write הוי"ה or ה'); שד"י and אהי"ה with gershayim; other nations and religions generically ("אומות העולם"); political labels neutralized; no mention of AI, models or tools anywhere; no inline style, script or img; `&amp;` in URLs; ids unique. Document what was said; do not recommend.

## Manifest (last step)
Write `build/parts/unit-<n>.manifest.md`, three parts, so the synthesis writers never have to reopen your HTML:
- **(א)** the cards table, with exactly this header line, because `build_index.py` reads it: `| id | שם השיטה | סוג | למה | מקור |`. Write one row per technique card, in card order.
  - **id** is `t<n>-k`.
  - **שם השיטה** is the card's h3, without `[?]`.
  - **סוג** is one of קמיע / גורל / סגולה / כוונה / תפילה / השבעה / הכנה ותנאים / איסור ואזהרה / עיוני. It must equal the FIRST plain type tag on the card.
  - **למה** is one line: the purpose, as the speaker put it.
  - **מקור** is the book or sage the speaker cites for it, or "—".
- **(ב)** the books and sages mentioned, one line each, with the spelling used on the page (keep the `[?]`).
- **(ג)** the unit's key principles, 3–6 lines, each close to the speaker's words.
Head the file with `# <unit_label> N – <topic> (<id>, <duration or pages>, <date>)`.

## Report back (10 lines or fewer)
Template and part sizes, the number of technique cards, the `coverage.py` line for your unit, the `assemble.py` result for your part, the `check_page.py` findings that touch your part, and anything you could not place.
