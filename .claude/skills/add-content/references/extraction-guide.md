# Extraction guide: one unit's transcript or text, into structured Hebrew notes

**Purpose.** You extract EVERYTHING of substance from ONE source unit (a recorded lecture, or a chapter or book in text form) into a structured Hebrew Markdown file. Those notes are the sole content source for the unit's section on the web page: the fragment writer never reopens the transcript except to verify a detail. Completeness is the goal: every technique, step, rule, source cited, story, warning and answer. A reader of your notes must never need the original to learn what was taught.

**Inputs** (paths are relative to `<workspace>`, the directory that holds `project.json`; read `project.json` first for `unit_label`, your unit's `n`, `id`, `kind`, `url`, `title`, `duration_string` or `pages`, `date`):
- `transcripts/<id>.md`: the transcript that `transcribe.py` wrote, one segment per line, `[hh:mm:ss] text` (same data as `<id>.json`). For a text source the same file holds the text with a `[עמ' N]` marker per page. Read ALL of it, start to finish.
- `meta/descriptions.md`: the source's own description (video description, book blurb). Descriptions are authoritative where the audio is unclear; they sometimes hold the exact verses or names the speaker uses.
- `research/background.md`, if it exists: use it ONLY to spell names and book titles correctly.
- **Focus hints** in the orchestrator's prompt, e.g. "the full procedure of the lot, every table read aloud". They tell you where depth matters most. They never let you skip anything else.
- For a unit that continues earlier units: `notes/<other-id>.md` of the earlier units, or the page itself (`grep -o '<li><a href="#t[0-9]*-[0-9]*">[^<]*' <repo>/<page>` lists existing technique titles).

**Output.** ONE Hebrew Markdown file, `notes/<id>.md`, written in many small appends (see "How to write", which is mandatory).

## The transcript is automatic
A video transcript comes from Whisper (the Hebrew ivrit.ai model for `language: he`). It is mostly accurate, but proper names, letter-by-letter spellings of holy names and angel names, numbers, Aramaic and foreign words are often garbled. Use context to recover the intended word; when you are not sure, keep the transcript's form and mark it `[?]`. Never silently "correct" a name to what you think it should be: the hedge travels all the way to the page.

## File layout: exactly these top-level sections, in this order
Keep the headings verbatim. The page build and the coverage check parse them.

```
# <unit_label> N: <title>
מקור: <url> · אורך: h:mm:ss · פורסם: dd.mm.yyyy        (video)
מקור: <url> · עמודים: N · הוצאה: <date>                (text)

## 1. תקציר
## 2. מהלך השיעור (ראשי פרקים עם זמנים)
## 3. השיטות והפעולות, שלב אחר שלב
## 4. עקרונות, כללים ואזהרות
## 5. ספרים, חכמים ומקורות שהוזכרו
## 6. סיפורים ומעשים
## 7. שאלות מהקהל ותשובות
## 8. ציטוטים חשובים
## 9. מה שהרב אמר שאינו מגלה / שצריך רשות
## 10. ספקות בתמלול
```
For a text source keep the same ten headings (the builder expects them); "מהלך השיעור" then means the chapter's outline, "שאלות מהקהל" holds the author's own rhetorical questions and answers or stays as "אין", and "ספקות בתמלול" holds OCR or reading doubts.

### Section rules
1. **תקציר**: 5–10 sentences. What the unit is about and what it teaches.
2. **מהלך השיעור**: a chronological outline, one bullet per topic block, each starting with the locator where it begins: `- [00:12:40] …` (video) or `- [עמ' 14] …` (text). Aim for 15–40 bullets depending on length.
3. **השיטות והפעולות**: THE core. One `### ` sub-heading per distinct technique, segula, lot (גורל), amulet, kavana, preparation or practice. Fixed template; omit a field only if truly nothing was said, and then write `לא נאמר`:
   ```
   ### <שם השיטה>
   - **מטרה:** למה עושים את זה
   - **המקור שהרב מציין:** ספר/חכם (ציטוט המקום אם נאמר)
   - **מי רשאי / תנאים מקדימים:** טהרה, צום, טבילה, רשות ממורה, זמן ביום/בשבוע/בחודש, מצב רוחני
   - **מה צריך להכין:** חומרים, קלף/נייר, דיו, מטפחת, טלית, חול, קלפים, ספר...
   - **השלבים:**
     1. [hh:mm:ss] שלב ראשון – בדיוק מה עושים/אומרים/כותבים, כמה פעמים, לאיזה כיוון, באיזו יד...
     2. [hh:mm:ss] ...
   - **הנוסח / השמות / הפסוקים:** exactly as said, one item per line (see the holy-name rule)
   - **איך קוראים את התוצאה:** for lots: how the result is interpreted, tables, letters→meanings
   - **אזהרות וסייגים:** everything the speaker warned about for THIS practice
   - **דוגמאות שהרב נתן:** cases, people, outcomes (brief; full stories go to section 6)
   - **המשך / שינוי לעומת יחידה קודמת:** only when the technique was taught in an earlier unit (see below)
   - **מקור בסרטון:** the ranges covering this technique, e.g. 00:14:10–00:31:55, 01:02:00–01:05:30 (text source: `- **מקור בספר:** עמ' 12–19, 40`)
   ```
   Every step gets its own locator (the start of the segment where it is said). If the speaker returns to a technique later and adds details, merge them into the same block and add the extra locators. If a technique is only MENTIONED, still list it with `- **הערה:** הוזכר בלבד`, so nothing is lost. Tables the speaker reads (houses, figures, letters, hours) become Markdown tables inside the block.
4. **עקרונות, כללים ואזהרות**: general teachings not tied to a single technique: what the field is, who may practice, dangers, halachic rulings quoted, how holy names work, spiritual preparation. One bullet each, each with a locator.
5. **ספרים, חכמים ומקורות**: a table `| שם | מי/מה זה (כפי שהרב אומר) | בהקשר של | זמנים |`. Include every book, sage, manuscript, place, and biblical or talmudic citation named. Describe each as the speaker presents it, not from your own knowledge.
6. **סיפורים ומעשים**: every anecdote: who, what happened, what the lesson was, locators.
7. **שאלות ותשובות**: every audience question (paraphrased) and the answer, with locators.
8. **ציטוטים חשובים**: 10–30 short verbatim quotes, lightly cleaned of ASR noise, each `[hh:mm:ss] "..."`. For a text source, quote longer passages when they carry the teaching, each with its `[עמ' N]`.
9. **מה שאינו מגלה**: anything the speaker explicitly declines to teach publicly, says needs permission or a teacher, defers to another lesson, or refers to a private channel (a phone number in the description, "come to me"). Quote the refusal.
10. **ספקות בתמלול**: words and names you could not resolve, with locators, and your best guess marked as a guess.

### When this unit continues an earlier one
Series often return to a technique (a lot taught in unit 6 and refined in unit 10, a book read across several chapters). Say so explicitly, so the page can link the two instead of duplicating: in the block's `המשך / שינוי לעומת יחידה קודמת` field write where it was taught before and what is NEW or DIFFERENT here ("בשיעור 6 ההטלה בשעות קבועות; כאן נוספה גרסה קצרה של שלוש שורות"). If nothing is new, say "חזרה בלי תוספת". Find the earlier treatment in the earlier notes or in the page's technique titles (see Inputs).

## Hard rules
- **Hebrew throughout.** Transliterate nothing into English. Latin letters only inside URLs and ids.
- **Fidelity.** Write only what is in the transcript or the description. Never add outside knowledge into sections 3–9. Context from `background.md` goes, if at all, into a clearly separated `## נספח: הקשר מהמחקר` at the very end, with its source.
- **Holy-name rule (mandatory).** Never write the four-letter Name in full, not even in verses or quotes: write `הוי"ה`, or `ה'` in verses ("הוֹצִיאָנוּ ה' מִמִּצְרַיִם"). The Names אהי"ה, אדנ"י and שד"י are always written with gershayim, never as plain pronounceable words. The transcript writes them plain, so add the gershayim wherever the word is used as a Name, as in "בשם שד"י" or "אהי"ה אשר אהי"ה". The ordinary word for "my field" is not a Name. Permutations of the Name are described ("צירוף הוי"ה של חודש ניסן"), never spelled. Other holy names and angel names (ע"ב שמות, שמות מלאכים) may be written letter by letter as the transcript gives them, with `[?]` on uncertain spellings.
- **Jewish framing only.** Do not compare to, or name, other religions' practices, even if a word in the transcript suggests one. Where the speaker names other nations or religions, write generically ("אומות העולם", "גוי"). Neutralize political labels.
- **Conjectures are not quotes.** If the transcript says one thing and you think the speaker meant another, quote what was heard and bracket the guess: `"…כנגד הארמה [כנראה: א־רמל]"`. Never put your conjecture inside the quotation marks.
- **Keep every hedge.** "(לא ודאי)", "כנראה", "[?]" written in the notes are preserved by every later stage, so write them wherever you are not sure. A flat statement in the notes becomes a flat statement on the page.
- **Locators.** Video: `[hh:mm:ss]` exactly as in the transcript lines (use the line's own timestamp, never an interpolated one). Text: `[עמ' N]` with the page number the file carries.
- **Length.** No upper limit. A two-hour lecture typically yields 2,500–6,000 words; a long chapter similar.
- **Do not paste the transcript wholesale**; extract and structure it. Short verbatim quotes are good.

## How to write: mandatory discipline
Whole files composed in one generation were lost, more than once, when the generation hit an output cap or the agent was interrupted. Nothing reaches disk until a tool call runs, so a 5,000-word single Write that never completes leaves no file at all. Appends keep partial progress on disk at every moment, and let the orchestrator see where you are.

1. Read the inputs fully (`transcripts/<id>.md` in a few Read calls if it is long).
2. **Your FIRST tool call after reading is a Write** of `notes/<id>.md` containing the header line, the `מקור:` line, and sections 1 and 2 complete.
3. Then **one append per section**, and in section 3 **one append per technique block**:
   ```bash
   cat >> <workspace>/notes/<id>.md <<'EOF'
   ### <שם השיטה>
   …
   EOF
   ```
   Open section 3 with its heading in the first technique's append. Keep each append under about 1,500 words. If a block or section is larger, split it into two appends at a natural point.
4. After the last section, run the coverage grep below and append whatever it finds you missed.

## Final coverage grep
Scan the whole transcript once more for instructions that are not yet in your notes:
```bash
grep -nE 'תעשה|תכתוב|תגיד|תאמר|לוקחים|צריך|אסור|מותר|שלוש פעמים|שבע פעמים|כותבים|אומרים' <workspace>/transcripts/<id>.md | cut -c1-160
```
A book uses third-person and rabbinic imperatives, so for a text source add them to the pattern: `יכתוב|יאמר|יעשה|יזהר|יטבול|יכוון|צריך ש|ואח"כ|סגולה|לחש`. Then check each hit against its page.

For each hit, check that its timestamp (or a timestamp within a few seconds) appears in `notes/<id>.md`:
```bash
grep -c '^### ' <workspace>/notes/<id>.md                                  # technique blocks
grep -oE '\[[0-9]{2}:[0-9]{2}:[0-9]{2}\]' <workspace>/notes/<id>.md | sort -u | wc -l   # distinct locators (video)
grep -oE "\[עמ' [0-9]+\]" <workspace>/notes/<id>.md | sort -u | wc -l                 # distinct locators (text)
```
Add what is missing with one more append. The page's coverage check later compares the notes' locators with the page, so a locator that is in the transcript but not in the notes is invisible to it; this grep is the only net for those.

## Report back (10 lines or fewer)
The file path and size, the number of technique blocks, the number of distinct locators, how many blocks are "הוזכר בלבד", any technique that continues an earlier unit, and the open doubts you consider most important.
