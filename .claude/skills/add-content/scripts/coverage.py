#!/usr/bin/env python3
"""Coverage check for the NEW units: notes/<id>.md against the unit's part build/parts/NN-<prefix>-N.html.

Usage:  python3 -I coverage.py --config <ws>/project.json [--all]

Per unit, one line, starting with the unit's display name ("label" when set, else "<unit_label> N"):
  - technique blocks (### headings in notes section "## 3.", up to "## 4." or the end) vs article.card.tech
    cards with id t<N>-<k> in the part
  - video units: distinct timestamps (h:mm:ss) in the notes vs distinct timestamps in the part (t=…s in links to
    this unit's video, plus hh:mm:ss text; chips that link to another video are ignored)
  - text units: distinct [עמ' N] page refs in the notes vs #page=N links (and "עמ' N" text) in the part
then the timestamps/pages that are in the notes but not in the part.
--all checks every unit, not only "new": true. Exit 1 when a unit is below 100% or a file is missing.
"""
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import _common as C  # noqa: E402

TS = re.compile(r"(?<![\d:])(\d{1,2}:\d\d:\d\d)(?![\d:])")
TSEC = re.compile(r"[?&](?:amp;)?t=(\d+)s?")
PAGE_NOTE = re.compile(r"\[עמ['׳]\s*(\d+)\]")
PAGE_TEXT = re.compile(r"עמ['׳]\s*(?:<bdi>)?(\d+)")
PAGE_HREF = re.compile(r"#page=(\d+)")
YT_ID = re.compile(r"(?:[?&](?:amp;)?v=|youtu\.be/)([A-Za-z0-9_-]{11})")


def section3(md: str) -> str:
    m = re.search(r"^## 3\..*?$(.*?)(?=^## 4\.|\Z)", md, re.S | re.M)
    return m.group(1) if m else ""


def drop_foreign_links(html: str, unit: dict) -> str:
    """Remove <a> elements whose href points to a different YouTube video than this unit's."""
    def repl(m):
        vm = YT_ID.search(m.group(1))
        return "" if vm and vm.group(1) != unit.get("id") else m.group(0)
    return re.sub(r'<a\b[^>]*\bhref="([^"]*)"[^>]*>.*?</a>', repl, html, flags=re.S)


def main() -> int:
    ap = C.arg_parser(__doc__)
    ap.add_argument("--all", action="store_true", help="check every unit, not only the new ones")
    args = ap.parse_args()
    cfg = C.Config(Path(args.config))
    units = cfg.units if args.all else cfg.new_units()
    if not units:
        print("no new units (use --all to check every unit)")
        return 0
    bad = 0
    for u in units:
        n = int(u["n"])
        label = C.unit_display(cfg, u)
        nf = cfg.notes / ("%s.md" % u["id"])
        pf = C.part_files(cfg.parts, cfg.section_id(n))
        if not nf.exists():
            print("%s: notes MISSING (%s)" % (label, nf))
            bad += 1
            continue
        md = C.read_text(nf)
        tech_notes = len(re.findall(r"^### ", section3(md), re.M))
        text_unit = C.is_text(u)
        if text_unit:
            refs_notes = {int(p) for p in PAGE_NOTE.findall(md)}
        else:
            refs_notes = {C.norm_ts(t) for t in TS.findall(md)}
        what = "pages" if text_unit else "timestamps"
        if not pf:
            print("%s: notes %d techniques, %d %s | part MISSING" % (label, tech_notes, len(refs_notes), what))
            bad += 1
            continue
        html = C.read_text(pf[0])
        cards = sum(1 for cd in C.tech_cards(html) if cd["unit"] == n)
        if text_unit:
            refs_html = {int(p) for p in PAGE_HREF.findall(html)} | {int(p) for p in PAGE_TEXT.findall(html)}
            fmt = str
        else:
            own = drop_foreign_links(html, u)
            refs_html = {C.hms(s) for s in TSEC.findall(own)} | {C.norm_ts(t) for t in TS.findall(own)}
            fmt = str
        missing = sorted(refs_notes - refs_html)
        pct = 100.0 * (len(refs_notes) - len(missing)) / max(1, len(refs_notes))
        print("%s: techniques notes %d / cards %d | %s notes %d, in page %d, covered %s"
              % (label, tech_notes, cards, what, len(refs_notes), len(refs_html),
                 "100%" if not missing else "%.1f%%" % min(pct, 99.9)))
        if missing:
            print("   missing %s (%d): %s" % (what, len(missing), " ".join(fmt(x) for x in missing[:60]) + (" …" if len(missing) > 60 else "")))
            bad += 1
        if tech_notes != cards:
            print("   technique blocks and cards differ (%d vs %d)" % (tech_notes, cards))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
