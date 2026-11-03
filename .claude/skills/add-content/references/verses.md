# Adding verses (פסוקים) to `pesukim-meyuchadim.html`

The user sends a verse, often only a few words of it, and it goes on the verses page. This is small work: do it yourself in the main session, with no workspace, subagents, questions up front or pipeline.

## The steps

1. **Identify the verse.** Work out each verse's Sefaria ref (`Book.Chapter.Verse`) from the user's words. "השם" in the user's message stands for the Name. "וגם הפסוק אחריו" means add the next verse too, as its own card.
2. **Dry-run the script.** It takes the text from Sefaria, so the wording never comes from memory.
   ```bash
   python3 -I .claude/skills/add-content/scripts/add_verse.py Deuteronomy.10.12 Deuteronomy.10.13 --dry-run
   ```
3. **Compare.** Read the line the script prints against what the user sent. A mismatch usually means the wrong ref.
4. **Settle the colors** from the `color:` lines the script prints. If any name's color is unclear, ask the user before saving (see "Holy names").
5. **Save:** run the script again without `--dry-run`, then apply the user's color answers by hand.
6. **Check in a browser** with one verse added or more: no horizontal scroll at 1280, 390 and 320, and the Stam font loaded.
7. **Report** the verses and their sources. Do not commit unless asked.

## When the words don't match one verse

The user's wording is often from memory, and these cases need a flag in the final message, so the user can correct it:

- **Several verses fit, or the wording differs.** Choose the best fit, and name the alternatives and the difference. Example: "הורני השם דרכיך" has no exact match. The Tanakh says "הורני ה' דרכך", in both Psalms 86:11 and 27:11, and 86:11 was chosen.
- **It is not one verse.** A phrase can be stitched from several verses, as in "ה' מלך ה' מלך ה' ימלך". Don't force it into one source. Write its card by hand in the same markup, list every source with its own link, and add `<p class="note">` saying so. Update the counts and the table of contents by hand as well. If the phrase's other sources or its use in prayer were not checked, say that to the user.
- **Words were added.** If you complete a phrase the user cut short, say so.

A partial quote from a single verse is simple: show the whole verse.

## What each card shows, and why

The user asked for the verses to look as in a Torah scroll, and for every verse to carry its source.

- **Ketav ashurit line** (`blockquote`, the Stam Sefarad font in `fonts/`): consonants only, since a scroll has no vowels, cantillation, maqaf or sof pasuk. The spelling is the verse's, even when the user spelled it differently ("ימלך", not "ימלוך").
- **Pointed line** (`p.nikud`): the Masoretic text with vowels and cantillation, so the verse is readable.
- **Large letters** stay large in both lines (`span.rab`), like the ע and ד of שמע ישראל. The script takes them from Sefaria.
- **Source** (`p.src`): "ישעיהו מג, טז" style, linked to Sefaria.

## Holy names

- The Name is written in full: `יהוה` in the ketav ashurit line, with Sefaria's pointing in the pointed line. It is plain text; `js/sefirot-methods.js` colors its letters in the תפארת colors.
- Other names are marked `<span class="nm" data-name-sef="gevura">`; the page paints their letters from `js/sefirot-methods.js` (`letterCss`), never a pill. No hex colors in the page.
- The script colors the אלהים family as גבורה, with its suffixes (אלהיך, אלהינו, האלהים), and reports each one, because the same word can be non-holy (אלהים אחרים).
- It leaves other names (אדני, אל, יה, אהיה, צבאות, שדי) uncolored and reports them, because these depend on the sense: "אֶל" is usually "to".
- **When a name's color is unclear, ask the user; don't guess.** The color is clear when the word is plainly a holy name and it appears in the CLAUDE.md list, or when it is plainly not a name (such as the preposition "אל"). Everything else is unclear:
  - the word may or may not be a holy name here (אלהים אחרים, אדני as "my master");
  - the name is not in the list (שדי, אלוה, or any other name);
  - a form or combination the list doesn't settle, such as יהוה אלהים, or a name split across words.

  Use AskUserQuestion before saving. Each question gives the whole verse, its source and the word in question, with the candidate colors as options and "no color, not a name here" when that is possible. Ask once per distinct case in one call. Keep the verse's other names as they are, and record what was decided in the final message.
- A multi-word name from the list takes the color of the whole name: אלקים צבאות is הוד, ה' צבאות is נצח, and אל חי is יסוד. The script colors the parts separately, so fix these by hand.

## What the script updates

- The page: a new `article.pasuk` with the next `p<N>` id, and the count in the hero.
- `index.html`: the count on the card's cover and tag, and a table-of-contents line. Pass `--label` when the default (the first three words plus the source) doesn't name the verse well, e.g. `--label "אין עוד מלבדו (דברים ד, לה)"`.
- `README.md`: the count in the page's row.

It refuses a ref already on the page (also one linked as part of a stitched phrase; add that verse's card by hand if the user wants it alone). If a count pattern fails after a hand edit, fix the count in the file and rerun.
