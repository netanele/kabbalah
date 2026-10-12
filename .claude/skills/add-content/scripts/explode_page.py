#!/usr/bin/env python3
"""Split an existing page into build/skeleton.html + build/parts/NN-<id>.html (existing mode).

Usage:  python3 -I explode_page.py --config <ws>/project.json [--force]

Every TOP-LEVEL <section id="…"> inside <main> becomes one part, NN = its 2-digit order (3 digits when there are
more than 99), and is replaced in the skeleton by <!-- @@SECTION:<id> @@ -->. Everything else (head, inline
<style> and <script>, hero, nav, footer, script tags, text between sections, and top-level sections WITHOUT an id)
stays in the skeleton byte for byte. Nested sections stay inside their parent's part. When <main> holds no
sections with ids, top-level sections of <body> are used; when there are none, it fails with a message.

Round-trip guarantee: explode, then assemble.py with no edits, reproduces the page byte for byte. The script
proves it on the spot (it re-inserts every part into the skeleton in memory and compares) and fails otherwise.
It refuses to overwrite a non-empty build/parts unless --force.
"""
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import _common as C  # noqa: E402


def main() -> int:
    ap = C.arg_parser(__doc__)
    ap.add_argument("--force", action="store_true", help="overwrite existing build/skeleton.html and build/parts")
    ap.add_argument("--page", help="page to explode (default: <repo>/<page> from the config)")
    args = ap.parse_args()
    cfg = C.Config(Path(args.config))
    src = Path(args.page) if args.page else cfg.repo_page
    if not src.is_file():
        raise SystemExit("page not found: %s" % src)
    if not args.force and (cfg.skeleton.exists() or (cfg.parts.is_dir() and any(cfg.parts.iterdir()))):
        raise SystemExit("%s already has a skeleton or parts; pass --force to overwrite them" % cfg.build)
    doc = C.read_text(src)

    rng = C.main_range(doc)
    if rng is None:
        raise SystemExit("FAIL: %s has neither <main> nor <body>" % src.name)
    secs = [s for s in C.top_sections(doc, rng[0], rng[1])]
    where = "<%s>" % rng[2]
    if not any(s["id"] for s in secs) and rng[2] == "main":
        mb_o = re.search(r"<body\b[^>]*>", doc, re.I)
        mb_c = re.search(r"</body\s*>", doc, re.I)
        if mb_o and mb_c:
            secs = C.top_sections(doc, mb_o.end(), mb_c.start())
            where = "<body>"
    with_id = [s for s in secs if s["id"]]
    if not with_id:
        raise SystemExit("FAIL: no top-level <section id=…> in <main> or <body> of %s; this page cannot be exploded. "
                         "Model new sections on its markup by hand instead." % src.name)

    problems = []
    seen = {}
    for s in with_id:
        if not s["closed"]:
            problems.append("section #%s (offset %d) is never closed" % (s["id"], s["start"]))
        if not C.SECTION_ID_OK.match(s["id"]):
            problems.append("section id %r cannot be a placeholder name (allowed: A-Z a-z 0-9 _ -)" % s["id"])
        if s["id"] in seen:
            problems.append("duplicate top-level section id %r" % s["id"])
        seen[s["id"]] = True
    if C.PLACEHOLDER.search(doc):
        problems.append("the page already contains a <!-- @@SECTION:… @@ --> placeholder")
    if problems:
        raise SystemExit("FAIL: %s cannot be exploded:\n  " % src.name + "\n  ".join(problems))

    width = 3 if len(with_id) > 99 else 2
    skel = []
    pos = 0
    parts = []
    for i, s in enumerate(with_id, 1):
        skel.append(doc[pos:s["start"]])
        skel.append(C.placeholder(s["id"]))
        frag = doc[s["start"]:s["end"]]
        parts.append(("%0*d-%s.html" % (width, i, s["id"]), s["id"], frag, s["nested"]))
        pos = s["end"]
    skel.append(doc[pos:])
    skeleton = "".join(skel)

    # prove the round trip before writing anything
    rebuilt = skeleton
    for name, sid, frag, _ in parts:
        rebuilt = rebuilt.replace(C.placeholder(sid), frag.strip("\n"), 1)
    if rebuilt != doc:
        raise SystemExit("FAIL: in-memory round trip differs from the page; nothing written")

    if args.force and cfg.parts.is_dir():
        for _, _, p in C.all_parts(cfg.parts):
            p.unlink()
    cfg.parts.mkdir(parents=True, exist_ok=True)
    C.write_text(cfg.skeleton, skeleton)
    for name, sid, frag, nested in parts:
        C.write_text(cfg.parts / name, frag + "\n")

    no_id = [s for s in secs if not s["id"]]
    print("exploded %s (%.1f KB) from %s:" % (src.name, len(doc.encode("utf-8")) / 1024, where))
    for name, sid, frag, nested in parts:
        cards = len(C.tech_cards(frag))
        print("  %-28s %8.1f KB%s%s" % (name, len(frag.encode("utf-8")) / 1024,
                                        "  %d nested section(s)" % nested if nested else "",
                                        "  %d technique cards" % cards if cards else ""))
    for s in no_id:
        print("note: a top-level <section> without an id (line %d) stays in the skeleton"
              % (doc.count("\n", 0, s["start"]) + 1))
    print("skeleton: %s (%.1f KB), %d placeholders" % (cfg.skeleton, len(skeleton.encode("utf-8")) / 1024, len(parts)))
    print("in-memory round trip: identical")
    return 0


if __name__ == "__main__":
    sys.exit(main())
