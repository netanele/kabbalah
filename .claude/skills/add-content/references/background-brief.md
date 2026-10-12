# Background brief: the researcher, and the writer of `who`, `more`, `research`

**Purpose.** Two roles, usually two agents, run in sequence. The **researcher** gathers everything public about the teacher or author, the source books, the halachic cautions and the public reactions, with every URL verified and marked, into `research/background.md`. The **writer** turns that file into the page sections `who`, `more` and `research` (new mode), or updates them (existing mode). Nothing in these sections comes from the lectures themselves; that is the point of them, and the page says so.

**Inputs** (relative to `<workspace>`): `project.json` (title, units, urls, ids, dates); `meta/descriptions.md` and `meta/<id>.json` (titles, descriptions, tags, channel or publisher); `notes/<id>.md` if they exist (to know which books and sages the units cite, so the research covers THOSE); in existing mode the exploded parts `build/parts/11-who.html`, `32-more.html`, `33-research.html`. Tools: WebSearch and WebFetch; `yt-dlp` from the skill's venv for channel, playlist and comment data: `~/.cache/kabbalah-add-content/venv/bin/yt-dlp`, created by `bash <skill>/scripts/setup_env.sh`. `meta/<id>.json` from `fetch_meta.py` already holds each unit's title, description, tags, channel and dates.

**Outputs.** Researcher: `research/background.md`. Writer: `build/parts/11-who.html`, `32-more.html`, `33-research.html`.

---

## Part 1: the researcher

### What to cover
1. **Who the teacher or author is.** Name and titles as they appear in the sources, role and institution, place, published books (a table: book, what it is, year, source), the channel or publisher (subscribers, video count, playlists, recurring tags), press and podcasts, contact details published in the source descriptions (quote where they appear; do not search for private details beyond what the descriptions publish). Say explicitly what was NOT found (birth year, teachers, ordination, Wikipedia entry).
2. **The source books** the units lean on: for each, what it is, author and era, editions and where it can be read online (Sefaria, HebrewBooks, the National Library, publishers), what scholarship says, and known confusions (two books with one name, a disputed attribution). Flag anything that exists only in the lectures' own words.
3. **The halachic cautions.** The classical definitions and the poskim on the field, with Sefaria links to the primary texts (Sha'ar HaMitzvot, Sha'arei Kedusha, Shulchan Aruch and its commentaries, modern responsa), and secondary summaries marked as secondary. Primary first, secondary second.
4. **Public reactions.** Comments under the videos (yt-dlp can fetch them), forum threads, press coverage, launch events, clarification videos; positive and critical alike, dated.
5. **Gaps.** A closing list of what could not be verified and what has no public trace outside the lectures.

### Verification marks: every URL carries one
- ✅ the address was loaded directly (WebFetch, API, yt-dlp) and is about the right subject.
- ⚠️ the address exists but did not load for an automated tool (Cloudflare, 403, login); the detail was confirmed only from search snippets and must be checked by hand in a browser.
- ❓ a claim with no independent public source (only the speaker's own words, or your inference).
Put the legend at the top of the file. Never cite a page you did not at least see in a snippet. Do not invent catalogue numbers, years or prices; write "—" when not found.

### Rules
- **Jewish sources only.** For the field, the books and the halacha, cite Jewish sources: primary texts (Sefaria, HebrewBooks, the National Library), poskim, Jewish scholarship, and Jewish press or forums for reactions. Never bring in another religion's sources or practices, and never compare to them.
- Hebrew for the body; Latin only in URLs, ids and foreign titles. The four-letter Name is never written in full, even inside a quoted description that contains it (write הוי"ה or ה' and say the original was changed). Other religions are not named or compared; nations generically.
- Dated snapshot: open with "נאסף ב־DD.MM.YYYY. כל נתוני הצפיות, המנויים והמחירים הם לתאריך זה."
- Structure the file as `## א. <the teacher or author>`, `## ב. ספרי המקור`, `## ג. תגובות ציבוריות`, `## ד. סיכום פערים`, with tables where the data is tabular (`| פרט | מה נמצא | מקור |`).
- **Write first, then search.** Your FIRST tool call is a Write that creates `research/background.md` with the header, a section א summarizing what the source itself says about its author (read only that much before writing), and empty headings for the other sections. Then research one section at a time, spend at most about 8 minutes of searching on each, write "לא נמצא" when nothing turns up, and append each section as soon as it is done (under about 1,500 words per append). A researcher that searched for 75 minutes before writing produced nothing and had to be replaced; other agents also read this file for spellings while you work.
- Keep it under about 250 lines; depth goes into the links, not into prose.

---

## Part 2: the writer of `who`, `more`, `research`

Read `research/background.md`, `<skill>/references/markup-guide.md` (§1, §2, §5.7 tables, §5.11 tags, §5.12 external links, §7) and, in existing mode, the three exploded parts.

### Markup used in these sections
Plain `.card` blocks with `h3`, `ul.plain` or `p`, tables in `.tw`. External links are `<a href="…" target="_blank" rel="noopener">label</a>` with `&amp;` for `&`. A ⚠️ or ❓ item carries `<span class="tag r">לא אומת</span>` after its link. No `.src` chips: nothing here is from the lectures, except an explicit pointer "מה שהרב עצמו אמר – ב<a href="#<section_prefix>-N">…</a>". Where a research card concerns a specific unit, open it with `<div class="tags"><span class="tag d"><unit_label> N</span><span class="tag">ספר מקור</span></div>`. ids: `who-…`, `more-…`, `rs-…`.

### `who` (`11-who.html`)
`h2` "מי הוא <the teacher or author>"; `p.lead` explaining that only public sources are used, what `לא אומת` means, and the snapshot date `נכונים ל־<bdi>DD.MM.YYYY</bdi>`. Cards: identity, role and place (`who-id`); what was not found (`who-gaps`); books authored or published (`who-books`, a table); the channel or publisher (`who-channel`); related series in the channel (`who-series`). Each bullet ends with its links and, where due, the red tag.

### `more` (`32-more.html`)
`h2` "המשך הסדרה" (or "שאר הספר" for a text source); `p.lead` saying which units the page covers (`<bdi>1–N</bdi>`). Cards: the playlist or table of contents with what is and is not on the page (`more-playlist`, each covered unit linking to `#<section_prefix>-N`); side videos or appendices not transcribed (`more-clip`); a `.tw` table of units or chapters not yet covered, with title, date, length and link (`more-next`). Nothing about future work by anyone; only what exists at the source.

### `research` (`33-research.html`)
`h2` "רקע ומקורות"; `p.lead`: "רקע חיצוני לשיעורים … שום דבר בחלק הזה אינו מדברי הרב", the `לא אומת` legend, the snapshot date. Cards: what the field is, by the classical definitions (`rs-what`); one card per source book (`rs-<slug>`) with "מהו", confusions, where to read, links; the poskim, primary sources (`rs-poskim`) then secondary (`rs-poskim-2`); reactions and discussions (`rs-reactions`). Where the research contradicts or cannot confirm something the lectures say, state it neutrally ("לא נמצא תיעוד ציבורי … מה שהרב עצמו אמר – בשיעור N") and never edit the unit section to match.

### Existing mode: update, do not rewrite
- Change every range and count: "שיעורים 1–9" → "1–11", "תשעת השיעורים" → "אחד־עשר השיעורים", the snapshot dates to today.
- In `more`, move the newly covered units from the "not yet on the page" table into the covered list, each with its `#<section_prefix>-N` link; add any new videos or chapters the source has gained since.
- In `research`, add a card for each source book the new units introduce, and a `tag d` for the new unit on an existing book's card it uses; add new reactions dated after the old snapshot.
- In `who`, add newly published books, new channel numbers (with the new date), new press.
- Keep every existing link and every existing `לא אומת`; `diff` against the exploded part and confirm the change is additions and count updates.

### Checks
`python3 -I <skill>/scripts/assemble.py --config <workspace>/project.json` clean for your parts; every `href="#…"` resolves; no full Name (`grep` the three parts); no AI, model or tool names; the Latin in text is only inside URLs, `<bdi>` or foreign titles.

## Report back (10 lines or fewer)
Researcher: the file's size, how many URLs by mark (✅ / ⚠️ / ❓), and the three most important gaps. Writer: the three parts' sizes, the counts and dates you changed, the assemble result.
