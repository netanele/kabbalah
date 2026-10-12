#!/usr/bin/env python3
"""Render one unit's macro template into its part: build/tpl/unit-N.tpl.html -> build/parts/<NN>-<prefix>-N.html.

Usage:  python3 -I render_tpl.py --config <ws>/project.json --unit N

Macros (expanded in this order):
  @SRCS(a|b|…)  -> <div class="srcs"> with one chip per item, joined by one space
                   (hh:mm:ss items give @S chips; for text units, plain numbers give @P chips)
  @S(hh:mm:ss)  -> <a class="src" href="URL&amp;t=SSSs" target="_blank" rel="noopener"><display> · <bdi>hh:mm:ss</bdi></a>
  @T(hh:mm:ss)  -> <a class="ts" href="URL&amp;t=SSSs" …><bdi>hh:mm:ss</bdi></a>
  @P(12)        -> text units: <a class="src" href="URL#page=12" …><display> · עמ' <bdi>12</bdi></a>
<display> is the unit's "label" from project.json when set (e.g. "פרק ב'"), else "<unit_label> N".
The timestamp is printed exactly as written; @S and @T accept only hh:mm:ss, so anything else is a leftover.

NN: the existing part's number when a part for <prefix>-N exists; otherwise the next free number after the part
of the closest earlier unit (or after the last unit part; or 20+N when there are no unit parts yet).
In existing mode, when the skeleton has no <!-- @@SECTION:<prefix>-N @@ --> yet, one is inserted right after the
closest earlier unit's placeholder (same spacing as between the earlier units), and a NOTE says so.

Checks (exit 1 on any PROBLEM): leftover macros, tag balance, duplicate ids, the full Name (niqqud-aware), raw "&t=",
inline style, forbidden tags (script, style, img, iframe), Latin text outside <bdi> and URLs, timestamps beyond the
unit's duration. Dangling anchors are only a WARNING (cross-unit links resolve at assembly); anchors to this unit's
own ids (t<N>-…, l<N>-…, <prefix>-N) get their own warning line, since only this template can define them.
Prints the counts of t<N>-k cards and chips.
"""
import re
import sys
from collections import Counter
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import _common as C  # noqa: E402

TS = r"(\d\d:\d\d:\d\d)"


def choose_part(cfg, n: int) -> Path:
    sid = cfg.section_id(n)
    have = C.part_files(cfg.parts, sid)
    if have:
        return have[0]
    rx = re.compile(r"^%s-(\d+)$" % re.escape(cfg.section_prefix))
    unit_parts = []                                   # (unit n, part number)
    for num, name, p in C.all_parts(cfg.parts):
        m = rx.match(name)
        if m:
            unit_parts.append((int(m.group(1)), num))
    earlier = [x for x in unit_parts if x[0] < n]
    if earlier:
        after = max(earlier)[1]
    elif unit_parts:
        after = max(num for _, num in unit_parts)
    else:
        after = 20 + n - 1
    width = C.part_number_width(cfg.parts)
    return cfg.parts / ("%0*d-%s.html" % (width, C.next_free_number(cfg.parts, after), sid))


def ensure_placeholder(cfg, n: int) -> str:
    """Existing mode: add the unit's placeholder to the skeleton after the closest earlier unit. Returns a note."""
    if not cfg.skeleton.is_file():
        return ""
    sid = cfg.section_id(n)
    skel = C.read_text(cfg.skeleton)
    if C.placeholder(sid) in skel:
        return ""
    if cfg.mode != "existing":
        return "WARNING: the skeleton has no %s; add it where the section belongs" % C.placeholder(sid)
    rx = re.compile(r"<!-- @@SECTION:%s-(\d+) @@ -->" % re.escape(cfg.section_prefix))
    found = [(int(m.group(1)), m) for m in rx.finditer(skel)]
    earlier = [x for x in found if x[0] < n]
    if not earlier:
        return "WARNING: the skeleton has no %s and no earlier unit to follow; add it by hand" % C.placeholder(sid)
    prev_n, prev_m = max(earlier, key=lambda x: x[0])
    gap = "\n\n"
    ordered = sorted(found, key=lambda x: x[1].start())
    for (a, ma), (b, mb) in zip(ordered, ordered[1:]):
        between = skel[ma.end():mb.start()]
        if between.strip() == "":
            gap = between
    skel = skel[:prev_m.end()] + gap + C.placeholder(sid) + skel[prev_m.end():]
    C.write_text(cfg.skeleton, skel)
    return "NOTE: added %s to the skeleton after %s-%d" % (C.placeholder(sid), cfg.section_prefix, prev_n)


def main() -> int:
    ap = C.arg_parser(__doc__)
    ap.add_argument("--unit", type=int, required=True, help="unit number N")
    args = ap.parse_args()
    cfg = C.Config(Path(args.config))
    n = args.unit
    unit = cfg.unit(n)
    video = C.is_video(unit)
    tpl = cfg.tpl / ("unit-%d.tpl.html" % n)
    if not tpl.is_file():
        raise SystemExit("template not found: %s" % tpl)
    out_path = choose_part(cfg, n)
    errs, warns = [], []
    stamps = []

    def src(ts):
        ts = ts.strip()
        if not video:
            errs.append("@S/@T used in a text unit: %s" % ts)
        if not C.TS_STRICT.match(ts):
            errs.append("timestamp not hh:mm:ss: %r" % ts)
            return "@S(%s)" % ts
        stamps.append(ts)
        return C.chip_src(cfg, unit, ts)

    def tsc(ts):
        if not video:
            errs.append("@S/@T used in a text unit: %s" % ts)
        stamps.append(ts)
        return C.chip_ts(unit, ts)

    def page(p):
        if video:
            errs.append("@P used in a video unit: %s" % p)
        return C.chip_page(cfg, unit, int(p))

    def srcs_item(x):
        x = x.strip()
        if not video and re.fullmatch(r"\d+", x):
            return page(x)
        return src(x)

    t = C.read_text(tpl)
    t = re.sub(r"@SRCS\(([^)]*)\)", lambda m: '<div class="srcs">' + " ".join(srcs_item(x) for x in m.group(1).split("|")) + "</div>", t)
    t = re.sub(r"@S\(" + TS + r"\)", lambda m: src(m.group(1)), t)
    t = re.sub(r"@T\(" + TS + r"\)", lambda m: tsc(m.group(1)), t)
    t = re.sub(r"@P\((\d+)\)", lambda m: page(m.group(1)), t)
    t = t.strip("\n") + "\n"
    C.write_text(out_path, t)

    left = re.findall(r"@(?:SRCS|S|T|P)\([^)]*\)", t)
    if left:
        errs.append("leftover macros (%d): %s" % (len(left), left[:5]))
    elif re.search(r"@(?:SRCS|S|T|P)\(", t):
        errs.append("macro text remains")
    if C.NAME_ANY.search(t):
        errs.append("FULL NAME present (%d)" % len(C.NAME_ANY.findall(t)))
    if "&t=" in t:
        errs.append("raw &t= (%d)" % t.count("&t="))
    if re.search(r'\sstyle="', t):
        errs.append("inline style (%d)" % len(re.findall(r'\sstyle="', t)))
    for bad in ("script", "style", "img", "iframe"):
        if re.search(r"<%s\b" % bad, t, re.I):
            errs.append("forbidden <%s" % bad)
    latin = C.latin_outside_bdi(t)
    if latin:
        errs.append("latin in text: %s" % latin[:10])
    if not re.match(r'\s*<section id="%s"' % re.escape(cfg.section_id(n)), t):
        errs.append('the part does not open with <section id="%s">' % cfg.section_id(n))
    dur = unit.get("duration")
    if video and dur:
        over = sorted({s for s in stamps if C.to_secs(s) > int(dur)})
        if over:
            errs.append("timestamps beyond the duration %s: %s" % (unit.get("duration_string") or dur, over[:10]))

    bal_errs, ids = C.check_balance(t)
    errs += bal_errs
    dup = [k for k, v in Counter(ids).items() if v > 1]
    if dup:
        errs.append("dup ids: %s" % dup)
    idset = set(ids)
    own = re.compile(r"^(?:t%d-|l%d-|%s$)" % (n, n, re.escape(cfg.section_id(n))))
    dang = sorted({h for h in re.findall(r'href="#([^"]+)"', t) if h not in idset})
    own_dang = [h for h in dang if own.match(h)]
    other_dang = [h for h in dang if not own.match(h)]
    if own_dang:
        warns.append("own-unit anchors with no target here (will NOT resolve at assembly unless written): %s"
                     % ", ".join(own_dang[:20]))
    if other_dang:
        warns.append("anchors outside this unit (resolved at assembly): %s" % ", ".join(other_dang[:20]))

    note = ensure_placeholder(cfg, n)
    tech = [i for i in ids if re.fullmatch(r"t%d-\d+" % n, i)]
    chips = t.count('class="src"') + t.count('class="ts"')
    print("wrote %s (%.1f KB), %d tech cards (t%d-k), %d ids, %d chips" % (
        out_path.name, len(t.encode("utf-8")) / 1024, len(tech), n, len(ids), chips))
    print("tech ids:", ", ".join(tech) if tech else "-")
    if note:
        print(note)
    for w in warns:
        print("WARNING:", w)
    for e in errs:
        print("PROBLEM:", e)
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
