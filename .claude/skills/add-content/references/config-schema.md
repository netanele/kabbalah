# project.json: the one config every script reads

Each run of the skill has a workspace in the session's scratchpad: `<scratchpad>/<slug>/`. Its `project.json` describes the target page and the sources. Every script takes `--config <workspace>/project.json` and resolves all paths from it, so nothing is hardcoded per page.

```json
{
  "repo": "/Users/netanele/repos/kabbalah",
  "page": "turgeman-practical-kabbalah.html",
  "mode": "existing",
  "title": "יסודות בקבלה מעשית – הרב יהודה אוהד תורג'מן",
  "unit_label": "שיעור",
  "section_prefix": "lesson",
  "language": "he",
  "units": [
    {
      "n": 12,
      "kind": "youtube",
      "id": "AbCdEfGhIjK",
      "url": "https://www.youtube.com/watch?v=AbCdEfGhIjK",
      "title": "the video's own title",
      "topic": "the short topic used in the h2 and TOC",
      "duration": 5435,
      "duration_string": "1:30:35",
      "date": "27.5.2022",
      "new": true
    },
    {
      "n": 13,
      "kind": "pdf",
      "id": "shaarei-hasaga",
      "url": "https://drive.google.com/…",
      "title": "שערי השגה",
      "topic": "…",
      "pages": 298,
      "date": "תשנ\"ו",
      "new": true
    }
  ]
}
```

## Fields
- `repo`: the repo root.
- `page`: the target HTML file at the repo root.
- `mode`: `new` (a new page) or `existing` (add to an existing page).
- `title`: the page's `<title>`.
- `unit_label`: the word chips and tags use for one source unit: "שיעור", "סרטון", "פרק", "ספר". Chips render as `<unit_label> N · <bdi>hh:mm:ss</bdi>`, and the dark tag as `<unit_label> N`.
- `section_prefix`: the section id of a unit is `<section_prefix>-<n>` (e.g. `lesson-12`). Technique card ids are `t<n>-<k>`. Other ids inside a unit use `l<n>-…`.
- `language`: the language code for transcription: `he` uses the Hebrew ivrit.ai model, anything else uses multilingual Whisper.
- `units`: one entry per source.
  - `n`: the unit number on the page. It continues the page's numbering in existing mode.
  - `kind`: `youtube`, `video` (another URL yt-dlp supports), `pdf`, `web` or `doc`.
  - `id`: the YouTube id, or a short slug for text sources. Files are named by it: `transcripts/<id>.json`, `notes/<id>.md`, `tpl/unit-<n>.tpl.html`.
  - `duration` and `duration_string`: for video units.
  - `pages`: for text units; chips link to `url#page=N`.
  - `new`: true for units added in this run. Only new units are transcribed, extracted, written and coverage-checked. Old units already live in the page.

## Workspace layout (created by the scripts as needed)
```
<workspace>/
  project.json
  meta/<id>.json, meta/descriptions.md     source metadata and descriptions
  audio/<id>.m4a                           downloaded audio (never copied to the repo)
  transcripts/<id>.json, <id>.md           timestamped transcripts
  research/background.md                   the researcher's file
  notes/<id>.md                            one extraction per unit
  build/skeleton.html                      page shell with <!-- @@SECTION:name @@ --> placeholders
  build/parts/NN-<section-id>.html         one part per section (NN = order hint, any digits)
  build/tpl/unit-<n>.tpl.html              macro templates for unit sections
  build/parts/unit-<n>.manifest.md         per-unit manifest (cards table, books, principles)
  out/<page>                               the assembled page
  qa/                                      Playwright CLI install, screenshots, reports
```

Parts are found by the regex `^\d+-<section-id>\.html$`, so `lesson-1` never matches `lesson-10`, and two-digit unit numbers just work.
