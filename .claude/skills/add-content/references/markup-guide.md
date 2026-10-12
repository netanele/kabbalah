# Markup guide: the HTML contract for every part of the page

**Purpose.** This is the one markup contract for pages built by the add-content pipeline. Every writer follows it: unit-section writers, synthesis writers, the background writer and fixers. It merges the original build guide with the rules that QA forced on the first page. Those rules are baked in here so nobody has to fix them afterwards. Every class named below already has CSS in `<skill>/assets/skeleton.html` and behaviour in `js/read-aloud.js` and `js/find.js`, so never invent new classes. The snippets are copied from the finished `turgeman-practical-kabbalah.html`, its unit 11 above all. Page-specific ids, titles and video ids appear only inside examples.

**Inputs.** Read `<workspace>/project.json` for these values:
- `unit_label`: the word for one unit, e.g. "שיעור", "פרק" or "סרטון". Below, `<unit_label>` stands for it.
- `section_prefix`: the unit section ids are `<section_prefix>-N`.
- `units`: each unit's `n`, `id`, `kind`, `url`, `topic`, `duration_string` or `pages`, and `date`.
- `mode`: `new` or `existing`.

**Outputs.** None by itself. Your part files follow it, and so do your templates under `build/tpl/unit-N.tpl.html`, which `render_tpl.py` renders. One exception: a page that was NOT built by this pipeline follows its own markup. See §10.

## Contents
1. Files, section ids and page order
2. Rules for every part
3. A unit section
4. The technique card
5. Element snippets: chips, fields, steps, names, callouts, quotes, tables, Q&A, stories, doubts, tags, external links
6. Status tags: the fixed vocabulary
7. Content rules: names, hedges, conjectures, nations, counts, no tools
8. The cross-unit sections: summary, series card, techniques index, principles, books, transcripts
9. Self-check before you report
10. Pages not built by this pipeline

---

## 1. Files, section ids and page order

`assemble.py` pours parts into `build/skeleton.html`. The shell already holds `<head>`, the CSS, the hero, `nav.top`, the footer and the two scripts. Each part is one file, `build/parts/NN-<section-id>.html`, in UTF-8 without a BOM. It holds exactly one `<section id="<section-id>">…</section>` and nothing outside it. The section id must equal the skeleton's placeholder name `<!-- @@SECTION:<section-id> @@ -->` exactly. The page order is the skeleton's placeholder order; `NN` is only a sorting hint. Parts are matched by `^\d+-<section-id>\.html$`, so `lesson-1` never picks up `lesson-10`.

| NN | section id | default nav label | content | written by |
|---|---|---|---|---|
| 10 | `summary` | תקציר | what the series or book is, one line per unit, what the page offers | synthesis agent A |
| 11 | `who` | מי הוא הרב | the teacher or author, from public sources | background writer |
| 12 | `before` | לפני שמתחילים | the speaker's own warnings and conditions, from all units | synthesis agent A |
| 13 | `series` | מפת הסדרה | one `article.card.ls` per unit (§8.2) | synthesis agent A |
| 14 | `techniques` | כל השיטות | the index of every technique card (§8.3) | `build_index.py` only |
| any | `<section_prefix>-N` | `<unit_label> N` | one unit (§3, §4) | the unit's fragment writer, rendered by `render_tpl.py` |
| 30 | `principles` | עקרונות וכללים | recurring principles, grouped by topic (§8.4) | synthesis agent B |
| 31 | `books` | ספרים וחכמים | the merged books and sages tables (§8.5) | synthesis agent B |
| 32 | `more` | המשך הסדרה | what exists at the source beyond the page | background writer |
| 33 | `research` | רקע ומקורות | outside background, not the speaker's words | background writer |
| 90 | `transcripts` | תמלולים | the full transcripts | `make_transcripts.py` only |

For a text source the nav labels may change in the skeleton, e.g. "מי הוא המחבר" or "שאר הספר". The section ids never change.

## 2. Rules for every part

1. **Hebrew only.** Latin letters appear only inside attribute values (URLs, ids) and inside `<bdi>`. `check_page.py` flags any other Latin in text.
2. **The four-letter Name is never written**, in any part, quote, verse, names block, table or transcript. Write הוי"ה, ה' or השם. `assemble.py` fails the build if the four letters ever stand together. The full rule is in §7.1.
3. **One `.card` is one self-contained unit.** read-aloud.js reads a card as one piece, and find.js groups its search results by card. Never split one technique across two cards, and never nest a card inside a card.
4. **ids** are unique across the whole page:
   - technique cards are `t<N>-<k>`, where k counts 1, 2, 3… inside unit N, in the notes' order;
   - every other id inside a unit starts `l<N>-`, e.g. `l<N>-outline`, `l<N>-principles`, `l<N>-books`, `l<N>-qa-1`, `l<N>-stories`, `l<N>-hidden`, `l<N>-research`;
   - the cross-unit sections use `sum-`, `bf-`, `sr-`, `ix-`, `pr-`, `bk-`, and the background sections use `who-`, `more-`, `rs-`.
   `assemble.py` reports duplicate ids and every `href="#…"` that has no target.
5. **No inline `style=`**, and no `<script>`, `<style>`, `<img>`, `<iframe>` or emoji. The skeleton owns all CSS and script.
6. **Every `&` in a URL is `&amp;`**: `href="https://www.youtube.com/watch?v=ID&amp;t=754s"`. External links carry `target="_blank" rel="noopener"`.
7. **Numbers, times and Latin strings go inside `<bdi>`**: `<bdi>00:12:34</bdi>`, `<bdi>1:30:35</bdi>`, `<bdi>22.8.2024</bdi>`. Hebrew letters, including Hebrew numerals like תקל"ט, need no bdi. **A time range is ONE bdi**: `<bdi>00:04:34–00:05:42</bdi>`. The reason: two bdis joined by a dash, as in `<bdi>a</bdi>–<bdi>b</bdi>`, render in reverse order inside RTL text, so the range reads backwards. Never put a bare "–" between two chips; the chips are enough.
8. **Headings.** Each section has exactly one `<h2>`, its title. Blocks inside a section and technique titles use `<h3>`. `<h4>` appears only inside `ol.steps`. Never skip a level.
9. **Typography.** Use straight `"` and `'`, because find.js normalises them and gershayim are typed the same way (ע"ב, הוי"ה). The dash is "–", and "·" separates short items.
10. **Every claim about what the speaker said carries a locator**: a chip to the second (video), or a page chip (text). See §5.1. A detail you cannot locate goes into `.doubt`, not into the body.
11. **Document; never recommend.** Write what was said. Where the speaker withheld something, say so with a red tag (§6); never fill the gap from other sources inside a unit section. Outside knowledge belongs in `research`, or in at most one `.note` per unit that starts "מהמחקר:" (§5.5).
12. **No mention of AI, models or tools anywhere.** That includes "תומלל בעזרת", model names and pipeline words. The only exception is the transcript credit already in the skeleton's footer and in the transcripts section, which `make_transcripts.py` writes. Never add another.

## 3. A unit section

Order inside a unit:
1. `h2`, `p.lead`, `.meta`, `ul.inl`
2. at most one optional opening `h3` with a card, e.g. "why this day matters"
3. `h3 מהלך השיעור` with the outline card
4. the technique cards
5. at most one `.note` "מהמחקר:"
6. the closing blocks, in the order fixed below

Leave out any block the notes have nothing for, and never invent content to fill one.

```html
<section id="<section_prefix>-N">
  <h2><span class="ln"><unit_label> N</span> <topic></h2>
  <p class="lead">על מה ה<unit_label>, בשניים–שלושה משפטים: מה נלמד, ואם הוא ממשיך <unit_label> קודם – מה חדש כאן.</p>
  <div class="meta">
    <span>אורך: <bdi>1:58:46</bdi></span>
    <span>פורסם: <bdi>22.8.2024</bdi></span>
    <span>מזהה: <bdi>AbCdEfGhIjK</bdi></span>
    <a class="yt" href="https://www.youtube.com/watch?v=AbCdEfGhIjK" target="_blank" rel="noopener">לצפייה ביוטיוב</a>
  </div>
  <ul class="inl">
    <li><a href="#tN-1">שם הכרטיס הראשון</a></li>
    <li><a href="#tN-2">שם הכרטיס השני (הוזכר בלבד)</a></li>
  </ul>

  <h3>מהלך השיעור</h3>
  <div class="card" id="lN-outline">
    <p>פסקה אחת: איך ה<unit_label> בנוי, מתחילתו ועד סופו.</p>
    <ul class="plain">
      <li><a class="ts" href="…&amp;t=0s" target="_blank" rel="noopener"><bdi>00:00:00</bdi></a> פתיחה: …</li>
      <li><a class="ts" href="…&amp;t=43s" target="_blank" rel="noopener"><bdi>00:00:43</bdi></a> …</li>
    </ul>
  </div>

  <article class="card tech" id="tN-1"> … §4 … </article>
  <article class="card tech" id="tN-2"> … </article>

  <div class="note" id="lN-research"><p><b>מהמחקר:</b> (אינו חלק מדברי הרב.) … ומקורו.</p></div>

  <h3>עקרונות, כללים ואזהרות</h3>
  <div class="card" id="lN-principles"> … ul.plain, each li opening with a ts chip … </div>
  <h3>ספרים, חכמים ומקורות שהוזכרו</h3>
  <div class="card" id="lN-books"> … table in .tw (§5.7) … </div>
  <h3>שאלות מהקהל</h3>
  <details class="qa" id="lN-qa-1"> … §5.8 … </details>
  <h3>סיפורים ומעשים</h3>
  <ul class="stories" id="lN-stories"> … §5.9 … </ul>
  <h3>ציטוטים</h3>
  <blockquote class="q"> … §5.6 … </blockquote>
  <h3>מה שהרב לא גילה</h3>
  <div class="card" id="lN-hidden"> … ul.plain, each li opening with a red tag … </div>
  <h3>ספקות בתמלול</h3>
  <div class="doubt"> … §5.10 … </div>
</section>
```

**The header.**
- **Unit display name.** Below, "<unit_label> N" always means the unit's display name: its `label` from project.json if it has one (e.g. "פרק ב'" or "מבוא" for a book), otherwise "<unit_label> N". Use it in the `.ln` badge, the dark unit tag and the chips; the scripts do the same.
- **h2.** Write `<span class="ln"><unit_label> N</span> <topic>`, with the topic from `project.json`. Never add a series prefix such as "<series name> 1 –": the `.ln` chip already says which unit it is.
- **lead.** There is exactly one `p.lead` directly under the h2. If you have more to say, write a plain `<p>` inside the first card.
- **meta.** Keep `.meta` to short spans plus one `a.yt`, and give the date in full (`d.m.yyyy`) inside a bdi.
  - Video units take the three spans and the button shown above.
  - Text units use `<span>עמודים: <bdi>298</bdi></span>`, `<span>הוצאה: …</span>`, and an `a.yt` labelled "לקריאת המקור" that links to the unit's `url`.
- **`ul.inl`.** It holds one item per technique card, in card order, labelled with a short form of the card's title. A card whose primary tag is הוזכר בלבד may say so in parentheses.

**The closing headings are fixed.** They come in this order and with exactly these words, because `check_page.py` and readers navigating across units rely on them:
1. `עקרונות, כללים ואזהרות`
2. `ספרים, חכמים ומקורות שהוזכרו`
3. `שאלות מהקהל`
4. `סיפורים ומעשים`
5. `ציטוטים`
6. `מה שהרב לא גילה`
7. `ספקות בתמלול`, the `.doubt` block

Older variants like "שאלות ותשובות", "סיפורים שסיפר", "אמירות" and "מה שהרב אמר שאינו מגלה" are all replaced by these.

**The outline heading.** It is "מהלך השיעור" for lectures, and "מהלך הפרק" or "מהלך הסרטון" when `unit_label` is פרק or סרטון.

## 4. The technique card

Every `###` block in section 3 of the notes becomes its own `article.card.tech`. It has these parts, in this order:
1. `h3`
2. `div.tags`
3. optionally a `p.lead` inside the card
4. `dl.fields`
5. `ol.steps`
6. `.names`, if not already inside a step
7. a table in `.tw`, if the block has one
8. `.warn`
9. examples
10. optionally `.good` or `.note`
11. optionally `blockquote.q`
12. the `מקור בסרטון` line and its chips

```html
<article class="card tech" id="tN-1">
  <h3>"שיר של פגעים" לפי הירושלמי – מזמור ג' ומזמור צ"א</h3>
  <div class="tags">
    <span class="tag d"><unit_label> N</span>
    <span class="tag">תפילה</span>
    <span class="tag">סגולה</span>
    <span class="tag g">נמסר בחלקו</span>
    <span class="tag r">לא נמסר בשיעור</span>
  </div>
  <p class="lead">משפט או שניים: מה הכרטיס מתעד, ומה מתוכו נמסר ומה הוזכר בלבד.</p>
  <dl class="fields">
    <dt>מטרה</dt><dd>"מועיל מאוד לכשפים…" <a class="ts" href="…&amp;t=296s" target="_blank" rel="noopener"><bdi>00:04:56</bdi></a></dd>
    <dt>המקור</dt><dd>תלמוד ירושלמי, כפי שהרב מצטט (מראה המקום לא נשמע בבירור [?]).</dd>
    <dt>מי רשאי ותנאים</dt><dd>לא נאמר.</dd>
    <dt>מה מכינים</dt><dd>…</dd>
    <dt>הנוסח</dt><dd>…</dd>
    <dt>מה הרב לא גילה</dt><dd>איזה חותם כוכב כותבים על המראה – "חותם מסוים של כוכב" – לא נמסר <a class="ts" href="…&amp;t=318s" target="_blank" rel="noopener"><bdi>00:05:18</bdi></a>.</dd>
  </dl>
  <ol class="steps">
    <li>
      <h4>אמירת "המזמור וחצי"</h4>
      <p>מה עושים, בלשון הרב, בלי להוסיף.</p>
      <div class="srcs"><a class="src" href="…&amp;t=296s" target="_blank" rel="noopener"><unit_label> N · <bdi>00:04:56</bdi></a></div>
    </li>
  </ol>
  <div class="names">
    <span class="lbl">הפסוקים</span>
    <p>מזמור ג' – "מזמור לדוד בברחו מפני אבשלום בנו", כולו</p>
    <p>מזמור צ"א – "יושב בסתר עליון", עד "עליון שמת מעונך"</p>
  </div>
  <div class="warn"><p><b>אזהרת הרב:</b> … <a class="ts" href="…" target="_blank" rel="noopener"><bdi>00:05:32</bdi></a></p></div>
  <p><b>דוגמה שהרב נתן:</b> … – ראו <a href="#lN-stories">סיפורים ומעשים</a>.</p>
  <p><b>מקור בסרטון:</b> <bdi>00:04:34–00:05:42</bdi></p>
  <div class="srcs"><a class="src" href="…&amp;t=274s" target="_blank" rel="noopener"><unit_label> N · <bdi>00:04:34</bdi></a> <a class="src" href="…&amp;t=342s" target="_blank" rel="noopener"><unit_label> N · <bdi>00:05:42</bdi></a></div>
</article>
```

**`div.tags`** comes right after the h3. It holds, in this order:
1. the dark unit tag, `<span class="tag d"><unit_label> N</span>`;
2. one or two plain type tags from this list: קמיע · גורל · סגולה · כוונה · תפילה · השבעה · הכנה ותנאים · איסור ואזהרה · עיוני. The FIRST type tag is the card's type. It must equal the סוג column of the manifest and the index;
3. exactly ONE primary status tag (§6);
4. zero or more red detail tags (§6).

**`dl.fields`.** The `dt` labels are a fixed vocabulary, used in this order: `מטרה` · `המקור` · `מי רשאי ותנאים` · `מה מכינים` · `זמן` · `איפה` · `משך` · `הנוסח` · `איך קוראים את התוצאה` · `מה הרב לא גילה`.
- Drop a field only when the notes say nothing at all about it.
- When the notes write "לא נאמר", keep the field and write `לא נאמר.`, as in the example. That tells the reader the speaker did not say, rather than that it was forgotten.
- `מה הרב לא גילה` holds the specific wording of every gap that the red tags only name.

**The source line.** Its label is `מקור בסרטון:` for video units and `מקור בספר:` for text units. The range is one bdi, e.g. `<bdi>00:04:34–00:05:42</bdi>`, or `עמ' <bdi>12–19</bdi>` for text. The `.srcs` row of chips follows it.

**"Mentioned only" items.** Each block the notes mark `הוזכר בלבד` gets its OWN small card, because the target is one card per notes block and `coverage.py` compares the two counts. The card holds:
- the unit tag, the type tag and the plain tag `הוזכר בלבד`;
- one `<p>`;
- if there are several mentions, a `ul.plain` whose items open with chips.

Gather bare mentions into ONE card titled "פעולות שהוזכרו בלבד" only when the orchestrator's prompt asks for it. Then give each item its own `<li>` and chips, and report the difference between notes blocks and cards so it can be disclosed. Either way, every mention keeps its locator.

**Container and reference cards.** Examples are a materials list, a table of letters, or "the seven strong lots". They have no `ol.steps`, and that is allowed. It is why counts are worded "N כרטיסים" and never "N שיטות שלב אחר שלב" (§7.6).

## 5. Element snippets

### 5.1 Locator chips
Unit templates never type chips by hand. `render_tpl.py --unit N` expands these macros, using the unit's `url` and `unit_label`:

| macro | renders | use it in |
|---|---|---|
| `@S(00:12:34)` | `<a class="src" href="URL&amp;t=754s" target="_blank" rel="noopener"><unit_label> N · <bdi>00:12:34</bdi></a>` | `.srcs` rows, table cells, lists |
| `@T(00:12:34)` | `<a class="ts" href="URL&amp;t=754s" target="_blank" rel="noopener"><bdi>00:12:34</bdi></a>` | running text, when the sentence already says which unit |
| `@SRCS(a\|b)` | `<div class="srcs">` holding one `@S` chip per time | after a step, an answer, a table row |
| `@P(12)` | `<a class="src" href="URL#page=12" target="_blank" rel="noopener"><unit_label> N · עמ' <bdi>12</bdi></a>` | text units, in place of `@S` |

- In `@SRCS` the times are separated by a bare `|`, with no backslash: `@SRCS(00:12:34|00:15:01)`. The backslash in the table above only escapes the Markdown.
- The seconds in `t=` are an integer and must be inside the video's length.
- The chip's "<unit_label> N" must name the unit whose URL it carries. A chip copied from another unit is a `check_page.py` finding.
- A `.srcs` row prints the word "מקור:" by itself, via CSS, so never type it.
- Parts that are not templates, such as synthesis parts, write chips out in full. Copy the exact form from a rendered unit part.

### 5.2 `dl.fields`
```html
<dl class="fields">
  <dt>מטרה</dt><dd>…</dd>
  <dt>מי רשאי ותנאים</dt><dd>רק מי שטבל באותו יום; לא בשבת. @T(00:12:10)</dd>
</dl>
```
The vocabulary and order are in §4. One `dd` per `dt`. Separate several conditions with ";".

### 5.3 `ol.steps`
```html
<ol class="steps">
  <li>
    <h4>שם קצר לשלב</h4>
    <p>מה עושים, אומרים או כותבים; כמה פעמים; לאיזה כיוון; באיזו יד – כפי שנאמר.</p>
    @SRCS(00:15:01|00:17:00)
  </li>
</ol>
```
- One `li` per step in the notes' "השלבים" list, in the same order.
- Every step gets its own `.srcs` row, with every locator the notes give for that step.
- Never merge two of the notes' steps unless both were said in the same breath. If you do merge them, keep both locators.
- `h4` appears only here.

### 5.4 `.names`: formulas, names and verses
```html
<div class="names">
  <span class="lbl">הפסוק</span>
  <p>פסוק אחד לשורה, כפי שנקרא</p>
  <span class="lbl">השמות</span>
  <p>שם ראשון</p>
  <p>שם שני – <span class="tag r">לא נמסר בשיעור</span></p>
</div>
```
- The block is set in a serif face, one `<p>` per line.
- Sub-labels are `span.lbl`. Common ones are הפסוק, הפסוקים, השם, השמות, הנוסח, "הנוסח (כפי שנאמר)", מה אומרים and הסימן.
- A string that mixes Latin or digits goes inside a bdi.
- The Name rule applies with full force here (§7.1).

### 5.5 Callouts: `.warn`, `.note`, `.good`
```html
<div class="warn"><p><b>אזהרת הרב:</b> … @T(00:18:40)</p></div>
<div class="good"><p><b>דוגמאות שהרב נתן:</b> … @T(00:41:45)</p></div>
<div class="note" id="lN-research"><p><b>מהמחקר:</b> (אינו חלק מדברי הרב.) … ומקורו.</p></div>
```
- **`.warn`** has a red bar. It holds the speaker's warnings, prohibitions and caveats for this practice. Every warning in the notes' "אזהרות וסייגים" field must appear in one.
- **`.good`** has a green bar. It holds what the speaker presents as safe or recommended, and the examples he gave.
- **`.note`** has a gold bar. It holds a neutral editorial note. Inside a unit section, a research `.note` may appear at most ONCE, after the technique cards, starting `<b>מהמחקר:</b>` and naming its source. The research appendix of the notes, `## נספח: הקשר מהמחקר`, is never merged into a technique card.

When the speaker is not a rabbi, use the speaker's own role in the label, e.g. "אזהרת המחבר".

### 5.6 Quotes
```html
<blockquote class="q">ציטוט קצר, בלשון הרב, מנוקה מרעשי תמלול.<span class="who">הרב <שם>, <unit_label> N, @T(00:00:46)</span></blockquote>
```
- Under the h3 `ציטוטים`, quotes come as a run of `blockquote.q`.
- A quote may also stand inside a card, after the callouts.
- The quoted words must exist in the transcript within a few words. A guess never goes inside the quotation marks (§7.3).

### 5.7 Tables, always inside `.tw`
```html
<div class="tw">
<table>
  <thead><tr><th>כוכב</th><th>המלאך השולט</th><th>זמן</th></tr></thead>
  <tbody>
    <tr><td>חמה</td><td>רפאל</td><td>@SRCS(01:21:04)</td></tr>
    <tr><td>שבתאי, צדק, כוכב</td><td>לא נאמרו – "ועל זה הדרך" <span class="tag r">לא נמסר בשיעור</span></td><td>@SRCS(01:21:24)</td></tr>
  </tbody>
</table>
</div>
```
- Every table the speaker reads becomes a real `<table>` inside the card it belongs to. That covers figures, houses, letters, hours, planets and angels.
- **Wrap EVERY table in `div.tw`.** It scrolls sideways on a phone instead of pushing the whole page wider than the screen. A wide table without `.tw` is the usual cause of horizontal scroll at 390 and 320 px.
- The last column holds the chips.

The unit's books card uses four columns:
```html
<div class="card" id="lN-books">
  <div class="tw">
  <table>
    <thead><tr><th>שם</th><th>מי / מה (כפי שהרב אומר)</th><th>הקשר</th><th>זמנים</th></tr></thead>
    <tbody>
      <tr><td>תלמוד ירושלמי</td><td>"יש בו כמה מקומות שיש בו לחשים…"</td><td>שיר של פגעים</td><td>@SRCS(00:04:34|00:04:56)</td></tr>
    </tbody>
  </table>
  </div>
</div>
```
Describe each book or sage as the speaker presents them, not from outside knowledge. Keep `[?]` on uncertain names.

### 5.8 Questions from the audience: `details.qa`
```html
<details class="qa" id="lN-qa-1">
  <summary>השאלה, במשפט אחד</summary>
  <div class="a">
    <p>תשובת הרב, בתמצות ובלשונו ככל האפשר.</p>
    @SRCS(00:04:28|00:04:32)
  </div>
</details>
```
- One `details` per question, with ids `lN-qa-1`, `lN-qa-2`, and so on.
- They stay closed by default. find.js opens the right one when a search hit is inside.

### 5.9 Stories
```html
<ul class="stories" id="lN-stories">
  <li><b>כותרת קצרה.</b> הסיפור בשניים–שלושה משפטים: מי, מה קרה, מה הלקח. @T(00:25:00)</li>
</ul>
```
A story that spans a range takes `<bdi>00:06:33–00:07:04</bdi>` followed by its chips.

### 5.10 Doubts, and the `[?]` marker
```html
<div class="doubt">
  <p><b>הערה כללית:</b> …</p>
  <p><b>ספק:</b> בתמלול נשמע "…"; כנראה "…". @T(00:00:10)</p>
  <p><b>לא נמצא ב<unit_label>:</b> …</p>
</div>
```
- `.doubt` sits under the h3 `ספקות בתמלול`, in small print. It collects notes section 10, plus every unresolved reading you kept in the body.
- **`[?]` inline:** type a bare `[?]` right after an uncertain word in body text. `assemble.py` turns every one into `<span class="unc" title="קריאה לא ודאית בתמלול">[?]</span>`. Never type the span yourself.
- **Never put `[?]` in an `h3` or in a `ul.inl` label.** Titles are read aloud and listed in the index, so a marker there looks like a broken title. Move the doubt into the card body instead, as a sentence, as `<span class="tag r">לא ברור בתמלול</span>`, or as a `.doubt` line.

### 5.11 Tags
| markup | meaning |
|---|---|
| `<span class="tag d"><unit_label> N</span>` | the dark unit tag. Index and books tables use just the number: `<span class="tag d">N</span>` |
| `<span class="tag">קמיע</span>` | a plain type tag, or a plain primary status (§6) |
| `<span class="tag g">נמסר במלואו</span>` | a green primary status |
| `<span class="tag r">לא נמסר בשיעור</span>` | a red detail tag (§6) |
| `<span class="tag r">לא אומת</span>` | only in `who` and `research`: a ⚠️ or ❓ source |

Tags are grouped in `<div class="tags">` right after a card's h3. A red tag may also open a `<li>` in the `lN-hidden` card, or stand inline in a names line or a table cell.

### 5.12 External links (`who`, `more`, `research`)
```html
<a href="https://www.sefaria.org.il/…" target="_blank" rel="noopener">שם המקור</a> <span class="tag r">לא אומת</span>
```
External links never get `.src` chips. Chips are reserved for the speaker's own words.

## 6. Status tags: the fixed vocabulary

The scripts match these strings exactly. `build_index.py` uses them to fill the index, and `check_page.py` flags any card that lacks one.

**Exactly ONE primary status tag per technique card:**
| tag | when |
|---|---|
| `<span class="tag g">נמסר במלואו</span>` | the procedure or content was given in full |
| `<span class="tag g">נמסר בחלקו</span>` | it was given, but some detail was not. Add red tags for the gaps |
| `<span class="tag">הוזכר בלבד</span>` | it was only mentioned, not taught. Always a plain tag, never red |
| `<span class="tag">סופר כמעשה</span>` | it was told as a story, not as an instruction |

**Zero or more red detail tags, from this list only:**
| tag | when |
|---|---|
| `<span class="tag r">לא נמסר בשיעור</span>` | a detail was not given: not read out, not specified, names not said |
| `<span class="tag r">הרב לא מגלה</span>` | the speaker explicitly refuses, or says it needs permission or a teacher |
| `<span class="tag r">נדחה לשיעור נפרד</span>` | deferred to another lesson, chapter or booklet |
| `<span class="tag r">לא ברור בתמלול</span>` | the audio, OCR or text is unclear at that point |
| `<span class="tag r">לא פורסם</span>` | the speaker says it was never published |

- **The specific wording is never lost.** Write tags only from the lists above; never invent a variant. Write the particular gap in `<dt>מה הרב לא גילה</dt>` and quote the refusal. An example would be "צירופי השמות שבלוח לא נקראו".
- **Choosing a tag.** Decide from the block's own text and notes section 9. A card whose steps were given but whose names were withheld is `נמסר בחלקו` with `לא נמסר בשיעור` or `הרב לא מגלה`. Never call something a refusal (`הרב לא מגלה`) when the speaker simply did not get to it; that is `לא נמסר בשיעור`.
- **Text sources.** These strings stay as they are even for a book source, because the scripts match them literally.

## 7. Content rules

### 7.1 Holy names
- **The four-letter Name is never written in full.** Write `הוי"ה`, `ה'` in verses (e.g. "הוֹצִיאָנוּ ה' מִמִּצְרַיִם"), or `השם`. The rule covers every form: plain, with niqqud, inside quotes, inside verses, in tables and in transcripts.
- **Permutations of the Name are described, never spelled**, e.g. "צירוף הוי"ה של חודש ניסן".
- **The Names שד"י, אהי"ה and אדנ"י are written with gershayim**, never as plain pronounceable words. Watch for שד"י, which is easily typed plain in phrases like "בשם שד"י", "מלכות שד"י" and "שד"י שאמר לעולמו די". The ordinary word "שדי" ("my field") is not a Name and stays as it is.
- Other holy names and angel names, such as the ע"ב שמות or names of angels, may be written letter by letter as the notes give them, with `[?]` on uncertain spellings.

### 7.2 Hedges survive every stage
Whatever the notes hedge stays hedged on the page. That includes "(לא ודאי)", "כנראה", "ככל הנראה", "אולי" and `[?]`. A flat statement on the page must have a flat statement in the notes. Two examples:
- notes "הרב שך [?]" → page "הרב שך (לא ודאי)"
- notes "להשתכר [?]" → page "(מילה לא ברורה בתמלול)", not a confident gloss

When your wording is an inference rather than the speaker's, say so, e.g. "פירוש האותיות (לא נאמר במפורש):".

### 7.3 Conjectures never inside quotation marks
Quote what was heard, and put your guess in square brackets outside the speaker's words:
```
"…מסדרים אותם כנגד הארמה [כנראה: א־רמל, החול]"
```
Never write `"…כנגד הרמל"` when the transcript says "הארמה". The same applies to a gloss that interprets a word, such as "בדפוס רגיל" for a garbled "חגי". Write `תנ"ך "חגי" [?]`, or drop the quotation marks altogether.

### 7.4 Jewish framing; nations generically; politics neutral
- Never compare to other religions, and never name their practices, even when the transcript does.
- Where the speaker names other nations or religions, the authored text says "אומות העולם", "גוי" or "בני אומות העולם".
- Political labels are neutralized, e.g. a party or camp becomes "קבוצה פוליטית".
- Language names are fine ("בערבית"), and so is the evening prayer ערבית.
- Transcripts stay verbatim. The orchestrator decides about masking them.

### 7.5 Fidelity
Write only what the notes say, and the transcript where you verify. Never add a step, number, name, condition, source or quote. Never "complete" a withheld detail from another source. Never change ids, timestamps or card order once they exist.

### 7.6 Counts
- Word card counts as "N כרטיסים". In the series map that is `<bdi>1:30:35</bdi> · <bdi>27.5.2022</bdi> · 14 כרטיסים`.
- On the home-page card, write "N כרטיסי שיטות, רובם שלב אחר שלב".
- Never claim that every card has steps: reference cards and "mentioned only" cards have none.
- Unit counts in words use the construct forms: שני, שלושת … עשרת, then אחד־עשר, שנים־עשר … with a maqaf.

### 7.7 No tools, no AI
No part mentions how the page was made: no AI, no model, no tool, no "pipeline". This applies to the speaker's page as much as to the background sections. The transcript credit in the footer and the transcripts section is the only allowed exception, and it is already there.

## 8. The cross-unit sections

The full markup is copied from the finished page. The synthesis brief says what goes into each section, and how to merge into an existing page.

### 8.1 `summary`
```html
<section id="summary">
  <h2>תקציר</h2>
  <p class="lead">מה זו הסדרה, מה כל <unit_label> מלמד, ומה יש בדף הזה.</p>
  <div class="card" id="sum-series"><h3>הסדרה ואיך היא בנויה</h3><p>…</p></div>
  <div class="card" id="sum-units">
    <h3>מה כל <unit_label> מלמד</h3>
    <ul class="plain">
      <li><b><a href="#<section_prefix>-1"><unit_label> 1</a> – נושא.</b> משפט אחד.</li>
    </ul>
  </div>
  <div class="card" id="sum-page"><h3>מה יש בדף</h3><p>…</p><div class="note"><p>הדף מתעד את מה שנאמר ואינו ממליץ לבצע דבר.</p></div></div>
</section>
```
An existing page may use other ids here; the turgeman page has `sum-lessons`. Keep whatever ids the page already has.

### 8.2 `series`: one card per unit
```html
<div class="lgrid">
  <article class="card ls" id="sr-N">
    <span class="ln"><unit_label> N</span>
    <h3>הנושא</h3>
    <span class="d"><bdi>1:30:35</bdi> · <bdi>27.5.2022</bdi> · 14 כרטיסים</span>
    <p>משפט אחד על ה<unit_label>.</p>
    <ul class="inl"><li><a href="#tN-1">שם קצר</a></li><li><a href="#tN-3">שם קצר</a></li></ul>
    <div class="meta"><a class="yt" href="https://www.youtube.com/watch?v=ID" target="_blank" rel="noopener">לצפייה ביוטיוב</a></div>
    <a class="go" href="#<section_prefix>-N">ל<unit_label></a>
  </article>
</div>
```
- The `ul.inl` lists the unit's 3–5 main cards.
- For a text unit the `.d` line reads `עמ' <bdi>1–40</bdi> · K כרטיסים`, and the button is "לקריאת המקור".

### 8.3 `techniques`: generated, never hand-written
`build_index.py` writes the whole section by scanning every `article.card.tech` (h3, first type tag, `מטרה` field), so never type a row. If a row is wrong, fix the card and re-run the script. Its shape:
```html
<p id="ix-counts">סך הכול <bdi>183</bdi> כרטיסים: קמיע <bdi>30</bdi> · גורל <bdi>21</bdi> · …</p>
<div class="tw">
<table class="idx" id="ix-table">
  <thead><tr><th><unit_label></th><th>שם השיטה</th><th>סוג</th><th>למה</th></tr></thead>
  <tbody>
    <tr><td><span class="tag d">1</span></td><td><a href="#t1-1">…</a></td><td>קמיע</td><td>…</td></tr>
  </tbody>
</table>
</div>
```

### 8.4 `principles`: grouped by topic, each bullet with every place it was said
```html
<div class="card" id="pr-what">
  <h3>מהי קבלה מעשית ומאין כוחה</h3>
  <ul class="plain">
    <li>משפט קרוב ללשון הרב. <a class="src" href="…&amp;t=29s" target="_blank" rel="noopener"><unit_label> 1 · <bdi>00:00:29</bdi></a> <a class="src" href="…" target="_blank" rel="noopener"><unit_label> 5 · <bdi>00:17:29</bdi></a></li>
  </ul>
</div>
```
A principle that recurs across units appears once, followed by a chip for each unit where it was said.

### 8.5 `books`: the merged tables
```html
<div class="note"><p>השמות נכתבו כפי שנשמעו … שם שלא זוהה בוודאות מסומן [?] …</p></div>
<h3 id="bk-books">ספרים, כתבי יד ומקורות</h3>
<div class="tw">
<table>
  <thead><tr><th>שם</th><th>מי / מה</th><th>ב<unit_label>ים</th></tr></thead>
  <tbody>
    <tr><td>אבן השוהם</td><td>…</td><td><a href="#<section_prefix>-1"><span class="tag d">1</span></a> <a href="#<section_prefix>-10"><span class="tag d">10</span></a></td></tr>
  </tbody>
</table>
</div>
<h3 id="bk-sages">חכמים ואישים</h3> …same table shape…
```
The column header uses the plural of `unit_label`, e.g. בשיעורים, בפרקים or בסרטונים.

### 8.6 `transcripts`
`make_transcripts.py` writes this section: one `details.tr` per unit, each with id `tr-N`. In existing mode it appends only the new units. Never edit the section by hand. Any wording fix, such as gershayim on a Name, goes into the script's replacement list.

## 8.7 Text sources (books, PDFs): wording that differs from lectures

The contract's wording above assumes a recorded lecture. For a book or PDF (`kind: pdf|web|doc`), these overrides apply. They were worked out on the first book page (דרכי השגה):
- **Units and labels.** Each part of the book (introduction, chapters) is a unit with a `label` in project.json: "מבוא", "פרק א'" and so on. Chips read `פרק ב' · עמ' <bdi>12</bdi>`, and the dark tag reads the label.
- **`.meta`.** Write `עמודים <bdi>6–17</bdi>` instead of a duration, plus a "לקובץ הספר" link to the unit's url. A Google Drive link ignores `#page`, so the chip just opens the file.
- **Source line.** `מקור בספר:` with page ranges in one bdi.
- **Voice.** Write "הספר", "המחבר", "מורנו" as the text calls its teacher, and "המלקט" for the editor. Never write "שיעור" or "הרב אמר בשיעור".
- **Headings after the cards.** Same order, but skip "שאלות מהקהל" (a book has none) and title the doubts block "ספקות בטקסט".
- **Compiler's preface.** It gets an opening card, "פתח דבר של המלקט", before the outline of the unit it belongs to.
- **Status tags keep their exact words**, because `check_page.py` matches them literally. Choose by meaning: an exercise the book defers to chapters never written is `נמסר בחלקו` plus `נדחה לשיעור נפרד`, with the explanation in `<dt>מה הרב לא גילה</dt>`. "ואכמ"ל" and similar get `לא נמסר בשיעור`.
- **Passages the editor inserted** (quoted sources, translations) are marked as such on the card when the notes say so, e.g. "(קטע שהוסיף המלקט, לא ודאי)".
- **No full text section**, unless the user asks for one. When asked, `make_transcripts.py` can build it from `transcripts/<id>.md`.

## 9. Self-check before you report

```bash
python3 -I <skill>/scripts/render_tpl.py --config <ws>/project.json --unit N     # unit writers, after every append or two
python3 -I <skill>/scripts/assemble.py   --config <ws>/project.json
python3 -I <skill>/scripts/coverage.py   --config <ws>/project.json              # unit writers
python3 -I <skill>/scripts/check_page.py --config <ws>/project.json              # add --all to check old units too
```
Then grep your own part for these. Each must return nothing:
```bash
P=<ws>/build/parts/<your part>.html
grep -n '<bdi>[^<]*</bdi>–<bdi>' $P                  # split time ranges
grep -n '<h3>[^<]*\[?\]' $P                          # [?] in a title
grep -n 'style=\|<script\|<img\|&t=' $P              # forbidden markup, raw ampersand
grep -nE 'AI|GPT|Claude|Whisper|בינה מלאכותית|מודל' $P   # tool mentions (a hit inside a URL or video id is fine)
```
Also confirm each of these by hand:
- every `article.card.tech` has exactly one primary status tag;
- every `href="#…"` you wrote resolves in `out/<page>`;
- the closing h3s match §3 word for word.

## 10. Pages not built by this pipeline

Some pages in the repo were built by hand, each in its own style. When you add a section or a unit to one of them, **copy THAT page's markup, not this contract's.** That means its element names and classes, its numbering scheme, its data attributes and its JavaScript hooks. The page's own filters, previews, search and read-aloud depend on exactly those, and a section in this guide's format would silently drop out of them.

How to tell: a pipeline page has `article.card.tech`, sections `<section_prefix>-N`, and the `.src` and `.ts` chips. If those are missing, the page is hand-built.

What to do first:
1. Read the page's notes in `<repo>/docs/` if any exist, e.g. `docs/<page>-notes.md` or `docs/<page>-review.md`. They record its structure, its rules and decisions the user made.
2. Read two complete existing items of the same kind as the one you are adding, and the script blocks at the end of the page that consume them.
3. List every attribute and class those scripts read, and fill every one of them on your new item.
4. Keep the page's numbering going. It may use Hebrew-letter numerals, continuous ids, or a count in the hero and footer.

**Example: `meditation.html`.** Its methods are `article.method` cards, not `article.card.tech`:
```html
<article class="method" id="m27" data-level="3" data-type="L" data-when="">
<span class="num" aria-hidden="true">כז</span>
<h3>…</h3>
<p class="meta">…</p>
<p class="essence">…</p>
<h4>איך מבצעים</h4>
<ol class="steps"><li>…</li></ol>
<p class="note">…</p>
<p class="foot"><span class="lvl lvl-3">…</span> <span class="typ">…</span> <span class="src">…</span></p>
```
- **Numbering.** Cards are numbered with Hebrew letters (`span.num`), and the ids are `m<number>`, continuing the last one.
- **Filters.** The level filter and the type and time keys read `data-level`, `data-type` and `data-when`.
- **Previews.** The hover preview, or peek, opens on links to `#m<number>`.
- **Book covers.** These come from the `books-data` JSON block, keyed by `data-b`.
- **Page rules.** Its own content rules are in `README.md` and `docs/meditation-page-notes.md`. They include Jewish sources only and no comparison with other religions, the "I" of the page being the user, and the Name never written in full, not even in images.

The repo-wide rules still apply on every page: the Name, no AI mention, `&amp;`, and the integration steps in `integration.md`. The rest of this guide does not.
