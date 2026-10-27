# Integration: putting the page into the repo, per CLAUDE.md

**Purpose.** You copy the assembled page into the repo and make the home page, the README and the page itself agree with the repo rules in `<repo>/CLAUDE.md`: every page is linked from `index.html` in four places, carries a card with real counts and a table of contents, has a README row, and links back home. Snippets below are copied from the real `index.html`; replace the page name, texts and counts.

**Inputs:** `<workspace>/project.json` (`repo`, `page`, `mode`, `title`, `unit_label`, `section_prefix`, `units` with `topic`); `<workspace>/out/<page>`; `<repo>/index.html`; `<repo>/README.md`; `<repo>/CLAUDE.md`; a cover SVG (new page only; `<skill>/assets/cover-amulet.svg` is an example, draw a new motif).

**Outputs:** `<repo>/<page>`, `<repo>/index.html`, `<repo>/README.md` edited. Nothing committed, nothing published.

## Rules that are not negotiable
- **Never publish a claude.ai Artifact** of any page or part. Pages are local files.
- **Never commit.** Leave the working tree for the user to review.
- Work on the real files with small edits (Edit, or Python `str.replace` on exact strings); read each target before editing.
- Run the tag-balance check at the end (below) on `index.html` and on the page.

## Step 0: copy the page and compute the counts
```bash
cp <workspace>/out/<page> <repo>/<page>
cp <workspace>/out/transcripts/<page-stem>-*.json <repo>/transcripts/   # JSON transcripts (CLAUDE.md "Transcripts"); cmp each
cd <repo>
grep -c '<article class="card tech"' <page>                          # technique cards
echo $(( $(grep -o 'class="src"' <page> | wc -l) + $(grep -o 'class="ts"' <page> | wc -l) ))   # source chips
grep -c '<details class="tr"' <page>                                 # transcripts
grep -c '<section id="<section_prefix>-' <page>                      # units on the page
```
The unit count and years come from `project.json`. Round the chip count ("כ־8,250 קישורים"), never the card count.

## New page

### 1. Nav link, in `nav.top` after the last page link and before `#between`
```html
  <a href="<page>">כותרת קצרה של הדף</a>
```

### 2. The card, an `article.book.wide` at the end of `#pages`, before `</section>`
```html
<article class="book wide">
  <a class="cover" href="<page>">
    <span>
      <span class="k">הנושא</span>
      <h3>כותרת הדף</h3>
      <span class="s">כותרת משנה: המורה או המחבר</span>
      <span class="d">מקום · N <unit_label>ים, YYYY–YYYY</span>
    </span>
    <svg class="<cover-class>" viewBox="0 0 100 100" aria-hidden="true" focusable="false">…</svg>
  </a>
  <div class="book-in">
    <p>משפט או שניים: מה יש בדף ולמי. בלי מספרים; המספרים בתגיות שלמטה.</p>
    <div class="meta"><span class="tag c">N כרטיסי שיטות, רובם שלב אחר שלב</span><span class="tag g">מקור (שיעור ודקה) לכל פרט</span><span class="tag p">N תמלולים מלאים</span><span class="tag">מקורות יהודיים בלבד</span></div>
    <h4>בדף</h4>
    <ul class="toc">
      <li><a href="<page>#summary">תקציר</a></li>
      <li><a href="<page>#who">מי הוא הרב</a></li>
      <li><a href="<page>#before">לפני שמתחילים</a></li>
      <li><a href="<page>#series">מפת הסדרה</a></li>
      <li><a href="<page>#techniques">כל השיטות</a></li>
      <li><a href="<page>#<section_prefix>-1"><unit_label> 1: <topic of unit 1></a></li>
      <li><a href="<page>#<section_prefix>-2"><unit_label> 2: <topic of unit 2></a></li>
      <li><a href="<page>#principles">עקרונות וכללים</a></li>
      <li><a href="<page>#books">ספרים וחכמים</a></li>
      <li><a href="<page>#more">המשך הסדרה</a></li>
      <li><a href="<page>#research">רקע ומקורות</a></li>
      <li><a href="<page>#transcripts">תמלולים מלאים</a></li>
    </ul>
    <a class="go" href="<page>">לדף <b aria-hidden="true">←</b></a>
  </div>
</article>
```
- One `.toc` item per unit, "`<unit_label> N: topic`", in order, using `project.json`'s `topic`. Every `href` must hit an existing section id in the page (check with `grep -c 'id="<section_prefix>-N"' <page>`).
- `.meta` tags: `tag c` for the card count, `tag g` for the source-per-detail promise, `tag p` for the transcript count, plain `tag` for the sources rule. The counts are the ones you computed; word it "N כרטיסי שיטות", never "כל כרטיס עם שלבים".
- **The cover.** Paste the SVG inline (no `<img>`, no file). Give it its own class and, if it needs a size other than the default 96 px, one rule next to the existing ones: `.cover svg.<cover-class>{width:104px;height:104px}` (see `.cover svg.seal`, `.cover svg.bars`, `.cover svg.ring` in `index.html`'s CSS). Use `currentColor` only, no text, no raster, and the motif must not contain any holy name.

### 3. Footer link, in the footer `<ul>` after the last page
```html
<li><a href="<page>">כותרת הדף</a></li>
```

### 4. The hero `.dates` line and the hero sentence
```html
  <div class="dates">5 דפים · 35 חיבורים · 123 שיטות · 58 ספרי מקור · 151 חכמים · 183 כרטיסי שיטות</div>
```
Bump "N דפים" and append one item for the new page ("· N כרטיסי שיטות" or the page's own measure). Add a clause for the new page to the hero `<p>` above it, matching the sentence's rhythm (one clause per page, joined by commas and a final ו־).

### 5. The README row, in the table of `README.md`
```
| `<page>` | כותרת הדף: מה יש בו (N <unit_label>ים, YYYY–YYYY), N כרטיסי שיטות, רובם שלב אחר שלב, עם מקור (שיעור ודקה) לכל פרט (כ־K קישורים), הספרים והחכמים שהוזכרו, העקרונות החוזרים, רקע ומקורות, ותמלולים מלאים |
```
Also update the `index.html` row's page count ("חמשת הדפים" → "ששת הדפים") and the two `js/` rows if the page uses read-aloud and find ("בשלושה דפי התוכן" → "בארבעה דפי התוכן (…)").

### 6. The page's own home link
The skeleton already puts it first in the page's nav; confirm:
```bash
grep -c '<a class="nav-home" href="index.html">ספריית הקבלה</a>' <repo>/<page>     # must be 1
grep -c 'nav.top a.nav-home{color:var(--gold);font-weight:700}' <repo>/<page>     # must be 1
```

## Existing page
The page is already linked everywhere; only the numbers and the TOC change.
1. In its `article.book` card: update the `tag c` card count and the `tag p` transcript count; update the `.d` line ("N <unit_label>ים, YYYY–YYYY"); add one `.toc` `<li>` per new unit, in order, before the `#principles` item; if the hero `.dates` carries this page's card count, update it there too.
2. In `README.md`: update the page's row (unit count, years, card count, chip count, the unit-count words such as "אחד־עשר השיעורים").
3. Confirm the page's hero, footer, summary and series already say the new unit count (the synthesis agents own that; if not, report it rather than editing the page by hand).

## Final checks
Tag balance with the standard library, on both files:
```bash
python3 -I - <repo>/index.html <repo>/<page> <<'EOF'
import sys
from html.parser import HTMLParser
VOID={"br","hr","img","input","meta","link","wbr","source"}
class P(HTMLParser):
    def __init__(s): super().__init__(convert_charrefs=False); s.st=[]; s.bad=[]
    def handle_starttag(s,t,a):
        if t not in VOID: s.st.append((t,s.getpos()))
    def handle_endtag(s,t):
        if t in VOID: return
        if s.st and s.st[-1][0]==t: s.st.pop()
        else: s.bad.append("mismatch </%s> at %s open=%s"%(t,s.getpos(),s.st[-3:]))
for f in sys.argv[1:]:
    p=P(); p.feed(open(f,encoding="utf-8").read()); p.close()
    print(f, "OK" if not p.st and not p.bad else ("unclosed %s; %s"%(p.st[-5:], p.bad[:5])))
EOF
```
Then: every `href` in the new or changed card resolves (`grep -o 'href="<page>#[^"]*"' index.html` against `grep -o 'id="[^"]*"' <page>`); the four places in `index.html` all name the page (`grep -c '<page>' index.html` is at least 4 plus the TOC items); `git status` shows only the intended files; no four-letter Name in the files you edited.

## Report back (10 lines or fewer)
The files changed, the counts you wrote and how you computed them, the tag-balance result, the `git status` line, and anything the synthesis agents still need to update inside the page.
