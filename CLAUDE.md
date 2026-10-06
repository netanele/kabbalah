# Kabbalah library — rules for Claude

## HTML pages
- Every new `.html` page added to this repo must also be added to `index.html`, the same way the existing pages are listed:
  - a link in the top `nav.top`,
  - a card (`article.book`) in `#pages` with cover, description, tags, a "בדף" table of contents linking to the page's section ids, and a "לדף" button,
  - a link in the footer list,
  - update the page count in the hero `.dates` line (and the hero summary sentence if relevant),
  - add a row for it in `README.md`.
- All HTML pages and "artifacts" are created as local files in this repo. Never publish them as claude.ai Artifacts.

## Style and content
See `README.md` (design tokens, fonts, and the content rules for the meditation page).
