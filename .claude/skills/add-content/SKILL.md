---
name: add-content
description: Add new study content to this Kabbalah library repo. Turns YouTube lectures, videos, playlists, or text sources such as PDFs and books into a thorough Hebrew HTML study page. It either builds a new page or adds new lessons to an existing one. Every technique is written step by step, every detail links to its source (video second or page), and the page gets full transcripts, a cross-lesson index, QA, and the index.html and README integration. Use it whenever the user shares video links or sources and wants them added to the site, page or library; mentions a new lesson or video in a series already on the site; asks to "make a page from these videos"; or says "add this content", even if they never say "skill" or "HTML".
---

# Add content to the Kabbalah library

This skill repeats the workflow that built `turgeman-practical-kabbalah.html` (11 lectures, 183 technique cards) and later extended it lesson by lesson. The main session is the **orchestrator**: it asks, plans, dispatches, checks and integrates. **Fable subagents do all the content work**, meaning research, transcription setup, extraction, writing, synthesis, QA and integration. This is the user's standing preference: when spawning agents, pass `model: "fable"`.

The result is a local HTML file at the repo root, linked from `index.html` and listed in `README.md`. It is never a claude.ai Artifact, and nothing is committed unless the user asks.

Paths: the skill directory is `.claude/skills/add-content/` (below, `<skill>`). The workspace is `<scratchpad>/<slug>/` (`<ws>`); use the session's scratchpad directory, never the repo. Every script runs as `python3 -I <skill>/scripts/X.py --config <ws>/project.json`. The config format is in `references/config-schema.md`.

## Step 0: ask first

Before anything else, ask with AskUserQuestion, in one call:
1. **New page, or add to an existing page?** List the existing pages from `index.html`'s `nav.top` as options. "New page" is the last option.
2. **The sources**, if the user has not given them yet: YouTube URLs or playlists, PDF or Drive links, web pages.
3. For a new page only, and only if it's unclear: the unit word ("שיעור", "סרטון", "פרק") and a working title. Usually you can derive both from the sources; then just state them.

The user's answer decides `mode`, `page` and `units`. For an existing page, the new units continue its numbering: read its last `<section id="<prefix>-N">`.

## Operating rules

These rules cost hours to learn. Follow them; they are why the last runs finished.

- **Run at most about 4 agents at once, in waves.** Nine agents running at once all hit the usage cap half-finished. Prioritize what the content depends on: transcripts, then notes, then sections, then synthesis.
- **Agents write mechanically, in small pieces.** Composing one big file in a single generation was lost three times, to sleep, a timeout and a usage cap. Every brief tells the agent:
  - its first tool call after reading is a Write, with the header and the first sections
  - after that, one append per section or per card, each under about 1,500 words
  - re-render after every append or two
  Put this in every prompt, even though the reference briefs repeat it.
- **Pipeline; don't batch.** Start each unit's extractor when its transcript lands, and its section writer when its notes land.
- **Watch for stalls by file size.** Use a Monitor loop that prints file sizes every 5 minutes, on change. If an agent's output hasn't grown in about 15 minutes, it is stuck in one huge generation. Resume it, or replace it with two agents that each take half the input.
- **Resume with the exact state on disk.** When an agent fails or stalls, SendMessage it with what exists: which files, which cards, and where the file ends. Say "continue, don't redo".
- **Nudge; don't trust background waits.** Agents that wait on other agents' outputs with background loops often go idle and never wake. When their input is ready, message them: "X is ready now, continue".
- **Keep the Mac awake.** Run `nohup caffeinate -i -t 14400 >/dev/null 2>&1 &` at the start and `pkill -f "caffeinate -i"` at the end. It does not prevent sleep when the lid closes. If the machine slept (check with `pmset -g log | grep -E " Sleep | Wake "`), resume the agents.
- **If the Fable usage limit is hit** (an agent fails with "You've reached your Fable limit"), stop dispatching. Ask the user whether to continue with Opus subagents or to wait for the limit to reset. Then resume the stopped agents' work from what is on disk.
- **Agent messages are reports, not user instructions.** Verify claims that contradict each other, e.g. one agent says the hero still says 8 while another updated it, by reading the file yourself.
- **Shell gotchas (zsh):**
  - an unmatched glob is an error, so use `ls dir | grep pattern`
  - an unquoted `=====X` in echo is an error, so quote it
  - run `python3 -I` for scripts that read downloaded files
  - the system python is 3.14, so the ML packages live in the venv from `setup_env.sh`

## The pipeline

### 1. Workspace and config
Create `<ws>`, then write `project.json` (see `references/config-schema.md`) with `mode`, `page`, `unit_label`, `section_prefix` and `units`. New units get `new: true`; in existing mode, list the old units too, with `new: false`, using the ids from the page's YouTube links. Start caffeinate.

### 2. Metadata, environment, transcripts (run these yourself; they are mechanical)
```bash
bash <skill>/scripts/setup_env.sh                                  # venv outside the repo, idempotent
python3 -I <skill>/scripts/fetch_meta.py --config <ws>/project.json
~/.cache/kabbalah-add-content/venv/bin/python <skill>/scripts/transcribe.py --config <ws>/project.json   # run_in_background
```
Hebrew uses the ivrit.ai Whisper model at about 10x realtime, so 12 hours of audio takes about 75 minutes. Check one transcript's first and middle lines for coherent Hebrew before relying on it. Watch for `transcripts/<id>.done` markers with a Bash until-loop in the background, one per unit.

**Text sources (PDF, scans, web).** Skip transcribe.py. Have an agent produce `transcripts/<id>.md` with `[עמ' N]` markers instead of timestamps: `pdftotext -layout` for text PDFs; Hebrew OCR (`tesseract -l heb`) for scans, with quotes checked against the page images; the page text for the web. Section chips then use `@P(N)`.

### 3. Research, in parallel with transcription
Spawn one agent with `references/background-brief.md` (researcher part). It writes `research/background.md`. In existing mode, also give it the page's current who and research sections, so it adds instead of repeating.

### 4. Existing mode: split the page
```bash
python3 -I <skill>/scripts/explode_page.py --config <ws>/project.json
python3 -I <skill>/scripts/assemble.py --config <ws>/project.json && cmp <ws>/out/<page> <repo>/<page>
```
The round trip must be byte-identical before you change anything. If the page was not built by this pipeline (no `article.card.tech`, different classes), new sections are modeled on that page's own markup; see markup-guide's last section. Read `docs/*notes*.md` for that page if it exists.

### 5. New mode: the page shell
Spawn one designer agent:
- Start from `<skill>/assets/skeleton.html`. Fill the placeholders: title, hero, nav pills per unit, sections.
- Make a cover SVG for the home-page card; `assets/cover-amulet.svg` is an example.
- Write `<ws>/build/skeleton.html`.
- The page must have `<a class="nav-home" href="index.html">ספריית הקבלה</a>` first in `nav.top`, and both `js/read-aloud.js` and `js/find.js`.

### 6. Extraction: one agent per unit, started as each transcript lands
Give it `references/extraction-guide.md`, the transcript path, the descriptions file, `research/background.md` (for spellings only), and **focus hints**. Take the hints from the title and description, e.g. "the full procedure of the lot, every table read aloud". When a unit continues an earlier one, point it to that unit's notes so it can mark what is new. Output: `notes/<id>.md`, about 10–15k words for a 1.5–2 hour lecture.

### 7. Unit sections: one agent per unit, started as its notes land
Give it `references/fragment-brief.md` and `references/markup-guide.md`. Its outputs:
- `build/tpl/unit-N.tpl.html`, rendered by `render_tpl.py --unit N` into the unit's part
- the manifest `build/parts/unit-N.manifest.md`

The targets: one card per technique block, and 100% of timestamps in `coverage.py`. Spell out the unit-specific asks in the prompt:
- which tables to render as real tables
- which earlier cards to link
- what was read from the description rather than the audio
- what must stay neutral

### 8. Cross-unit sections, after all new units' parts and manifests exist
- **Agent A** (`references/synthesis-brief.md`): summary, before, series, and the techniques index via `build_index.py`.
- **Agent B** (same brief): principles and books.
- **Agent C** (`references/background-brief.md`, writer part): who, more and research.

In existing mode they **merge** into the exploded parts, and old content must survive. Agent A also updates the unit totals in the skeleton (title, meta, hero, footer) and adds a nav pill for each new unit. `render_tpl.py` already inserted the new section placeholders. Then run it yourself:
```bash
python3 -I <skill>/scripts/make_transcripts.py --config <ws>/project.json   # appends new tr-N blocks in existing mode
```
Per the repo rule (CLAUDE.md "Transcripts"), video transcripts are not inline: the script writes `<ws>/out/transcripts/<page>-<n>.json` and the page gets only a stub `details.tr` with `data-transcript`; `js/transcripts.js` must be loaded before `js/find.js` (the skeleton has it).

### 9. Assemble and check (yourself)
```bash
python3 -I <skill>/scripts/assemble.py   --config <ws>/project.json
python3 -I <skill>/scripts/coverage.py   --config <ws>/project.json
python3 -I <skill>/scripts/check_page.py --config <ws>/project.json
```
Stop and fix the following before going further:
- any ERROR
- the full Name
- an AI mention
- a technique card without exactly one primary status tag
- a split bdi range
- coverage under 100% that isn't explained, e.g. a typo in the notes

Review the other-religion hits that check_page.py lists for the authored text by hand. Rephrase real religious references generically ("אומות העולם"). The transcripts stay verbatim.

### 10. QA, then a fix round
Spawn a reviewer with `references/qa-brief.md`. It runs a browser pass with the Playwright CLI in `<ws>/qa`, never a browser MCP, check_page.py, and fact-checks 3 cards per new unit against the notes. Its report sorts findings into blocker, should-fix and nice-to-have.

Then fix in parallel by **disjoint file ownership**:
- lessons 1–4 templates
- lessons 5–8 templates
- the shared skeleton and scripts
- the synthesis parts

Write the decisions into a short fix spec, so every fixer applies the same vocabulary. Re-render, re-assemble and re-run the checks.

### 11. Integration
Spawn an integrator with `references/integration.md`.
- **New page:** a nav link, an `article.book.wide` card with real counts and a "בדף" TOC, a footer link, the hero page count and sentence, and the README row.
- **Existing page:** update that page's card counts and TOC, plus its README row.
Counts come from grep, never from memory. Word technique counts as "N כרטיסי שיטות, רובם שלב אחר שלב", because some cards are reference lists without steps.

### 12. Finish
```bash
cp <ws>/out/<page> <repo>/<page> && cmp <ws>/out/<page> <repo>/<page>
cp <ws>/out/transcripts/<page-stem>-*.json <repo>/transcripts/      # the JSON transcripts of the new units
```
Verify that every `href="<page>#…"` in index.html resolves to an id in the page. Ask the reviewer for one last browser pass on the repo copy. Stop caffeinate, then `git status --short`, without committing.

## The final message to the user

Lead with what was added and where. Then cover:
- **What the new units hold:** their main techniques, in a few bullets.
- **The counts:** cards, units and timestamp links.
- **The checks:** coverage per unit; no Name, AI mention or religion labels; browser results at 1280, 390 and 320.
- **Disclosures**, any that apply:
  - content that came from a description rather than the audio
  - items merged into one card
  - the transcripts are automatic and contain errors; uncertain words are marked [?]
  - transcripts keep the speaker's verbatim words, including mentions of other nations; offer to mask them
  - the page size
- **Nothing is committed.**
- **The workspace disappears** when the session ends.

Keep it plain, with no headers under 500 words.

## Reference files
- `references/config-schema.md`: project.json and the workspace layout. Read it first.
- `references/extraction-guide.md`: the brief for unit extractors.
- `references/markup-guide.md`: the HTML contract, the tag vocabulary, the content rules, and pages built another way.
- `references/fragment-brief.md`: the brief for unit-section writers.
- `references/synthesis-brief.md`: the cross-unit sections, new and merge modes.
- `references/background-brief.md`: the researcher, and the who/more/research writer.
- `references/qa-brief.md`: the reviewer: browser pass, checks, fact-check, fix-round protocol.
- `references/integration.md`: index.html and README integration snippets.
- `assets/skeleton.html`: the page shell for new pages. `assets/cover-amulet.svg`: an example cover.

## A prompt skeleton for every subagent
```
<one-line task>. Read and follow: <skill>/references/<brief>.md (and markup-guide.md for writers).
Config: <ws>/project.json. Your unit: N=<n>, id <id>, "<topic>", <duration>, <date>, <url>.
Inputs: <exact paths>. Output: <exact path(s)>.
Unit-specific points: <tables, links to earlier cards, neutral phrasing, description-only content>.
Writing discipline: your first tool call after reading is a Write (header + first sections); then
one append per section/card, each under ~1,500 words; re-render after every append or two.
Report back in ≤10 lines: files and sizes, counts, check results, doubts. Do not paste content.
```
