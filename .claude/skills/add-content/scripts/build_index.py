#!/usr/bin/env python3
"""Build the technique index part (<section id="techniques">) by scanning every article.card.tech in all parts.

Usage:  python3 -I build_index.py --config <ws>/project.json [--rebuild]

Modes:
  new mode, or --rebuild, or no index part yet: regenerate the whole part from the cards (below).
  existing mode (the default there): MERGE into the existing part. Every existing <tr> whose card id (its first
    href="#t<n>-<k>") still exists is kept verbatim; rows are added only for cards without a row, at their unit/card
    position; rows of deleted cards are dropped; the counts line is recomputed from all rows (kept rows count under
    the first type in their own type cell). Nothing else in the part changes, so with no card changes the part
    stays byte-identical.

It never reads manifests (old units on existing pages have none). One row per card, sorted by unit then card number:
  - unit:  a dark tag <span class="tag d">n</span> with the card's unit number (from its id t<n>-<k>), or the unit's
           "label" from project.json when it has one; rows always sort by the number
  - title: the card's h3 (tags stripped except <bdi>), linking to #t<n>-<k>
  - type:  the FIRST plain header tag after the unit tag, any word (קמיע, תפילה, השבעה, …). The unit tag (tag d),
           colored tags, and the status tags נמסר במלואו / נמסר בחלקו / הוזכר בלבד / סופר כמעשה are never types.
           Empty when the card has no such tag (counted as "ללא סוג"). TYPE_ORDER in _common.py only orders the counts.
  - why:   the first sentence of the card's <dt>מטרה</dt> <dd>, without its chips. A card without one (often a
           "הוזכר בלבד" card) falls back to the first sentence of its first <p> after the tags, else of its first
           <li>, trimmed to about 140 characters at a word boundary. Kept rows in a merge are never re-derived.
A counts-by-type line precedes the table. When the part exists already,
its h2 and lead are kept; the rest is regenerated, in the same structure and classes as the turgeman page.
Checks (exit 1 on any PROBLEM): duplicate card ids, card ids that are not t<n>-<k>, the full Name, raw "&t=",
Latin text outside <bdi>.
"""
import html
import re
import sys
from collections import Counter
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import _common as C  # noqa: E402

DEFAULT_H2 = "  <h2>כל השיטות</h2>"


def keep_bdi(s: str) -> str:
    """Strip every tag except <bdi>/</bdi>, collapse whitespace; fall back to plain text if bdi ends up unbalanced."""
    t = re.sub(r"<(?!/?bdi\b)[^>]+>", "", s)
    t = re.sub(r"<bdi\b[^>]*>", "<bdi>", t)
    t = re.sub(r"\s+", " ", t).strip()
    if t.count("<bdi>") != t.count("</bdi>"):
        t = C.strip_tags(s)
    return t


def first_sentence(dd: str) -> str:
    t = re.sub(r'<div class="srcs">.*?</div>', "", dd, flags=re.S)
    t = re.sub(r'<a\b[^>]*\bclass="(?:ts|src)"[^>]*>.*?</a>', "", t, flags=re.S)
    t = keep_bdi(t)
    t = re.sub(r"\(\s*[;,]?\s*\)", "", t)
    t = re.sub(r"\s+([.,;:!?)])", r"\1", t)
    t = re.sub(r"\s{2,}", " ", t).strip()
    m = re.match(r"(.+?[.!?])(?=\s|$)", t, re.S)
    s = (m.group(1) if m else t).strip()
    if s.count("<bdi>") != s.count("</bdi>"):
        s = C.strip_tags(s)
    return s


WHY_MAX = 140


def trim_words(s: str, limit: int = WHY_MAX) -> str:
    """Cut s to about `limit` visible characters at a word boundary and add "…"; <bdi> stays balanced."""
    if len(C.strip_tags(s)) <= limit:
        return s
    out, n = [], 0
    for w in s.split(" "):
        vis = len(C.strip_tags(w)) + (1 if out else 0)
        if out and n + vis > limit:
            break
        out.append(w)
        n += vis
    t = " ".join(out).rstrip(" ,;:–-")
    if t.count("<bdi>") != t.count("</bdi>"):
        t = trim_words(C.strip_tags(s), limit)
        return t if t.endswith("…") else t + "…"
    return t + "…"


def fallback_why(body: str) -> str:
    """No מטרה field: the first sentence of the first <p> after the tags, else of the first <li>, trimmed."""
    tg = re.search(r'<div class="tags">.*?</div>', body, re.S)
    rest = body[tg.end():] if tg else body
    for rx in (r"<p\b[^>]*>(.*?)</p>", r"<li\b[^>]*>(.*?)</li>"):
        m = re.search(rx, rest, re.S)
        if m:
            s = first_sentence(m.group(1))
            if s:
                return trim_words(s)
    return ""


def counts(cnt: Counter):
    order = [t for t in C.TYPE_ORDER if t in cnt] + sorted(t for t in cnt if t not in C.TYPE_ORDER and t != "ללא סוג")
    if "ללא סוג" in cnt:
        order.append("ללא סוג")
    return order, " · ".join("%s <bdi>%d</bdi>" % (C.esc(t), cnt[t]) for t in order)


def unit_tag(cfg, n: int) -> str:
    """The dark tag in the unit column: the unit's "label" when set (e.g. פרק ב'), else its number (as before)."""
    for u in cfg.units:
        if int(u["n"]) == int(n) and (u.get("label") or "").strip():
            return C.esc(u["label"].strip())
    return "%d" % int(n)


def row_html(cfg, r) -> str:
    n, k, tid, title, types, why = r
    return ('<tr><td><span class="tag d">%s</span></td><td><a href="#%s">%s</a></td><td>%s</td><td>%s</td></tr>'
            % (unit_tag(cfg, n), tid, title, " / ".join(C.esc(t) for t in types), why))


def text_checks(t: str) -> list:
    errs = []
    if C.NAME_ANY.search(t):
        errs.append("FULL NAME present")
    if "&t=" in t:
        errs.append("raw &t=")
    latin = C.latin_outside_bdi(t)
    if latin:
        errs.append("latin in text: %s" % latin[:10])
    return errs


def primary_type(cell: str) -> str:
    """The first type in a kept row's type cell: 'כוונה / הכנה ותנאים' -> 'כוונה' (a parenthetical is ignored)."""
    t = html.unescape(C.strip_tags(cell))
    t = re.sub(r"\s*\(.*?\)", "", re.split(r"\s*/\s*", t)[0]).strip()
    return t or "ללא סוג"


def merge(cfg, out_path: Path, rows: list, errs: list) -> int:
    old = C.read_text(out_path)
    tb = re.search(r"(<tbody\b[^>]*>)(.*?)(</tbody>)", old, re.S)
    if not tb:
        raise SystemExit("%s has no <tbody>; use --rebuild" % out_path.name)
    inner = tb.group(2)
    segs = list(re.finditer(r"[ \t]*<tr\b.*?</tr>[ \t]*\n?", inner, re.S))
    by_id = {r[2]: r for r in rows}
    key = {r[2]: (r[0], r[1]) for r in rows}
    kept, dropped, notes = [], [], []          # kept: (sort key or None, segment text, id, type)
    seen = set()
    for m in segs:
        seg = m.group(0)
        idm = re.search(r'href="#(t\d+-\d+)"', seg)
        if not idm:
            kept.append((None, seg, None, None))
            notes.append("kept a row without a card link")
            continue
        tid = idm.group(1)
        if tid not in by_id:
            dropped.append(tid)
            continue
        if tid in seen:
            dropped.append(tid + " (duplicate row)")
            continue
        seen.add(tid)
        cells = re.findall(r"<td\b[^>]*>(.*?)</td>", seg, re.S)
        kept.append((key[tid], seg, tid, primary_type(cells[2]) if len(cells) >= 3 else "ללא סוג"))
    indent = re.match(r"[ \t]*", segs[0].group(0)).group(0) if segs else "      "
    added = [r for r in rows if r[2] not in seen]
    final = list(kept)
    for r in added:
        seg = indent + row_html(cfg, r) + "\n"
        pos = next((i for i, x in enumerate(final) if x[0] is not None and x[0] > (r[0], r[1])), len(final))
        final.insert(pos, ((r[0], r[1]), seg, r[2], r[4][0] if r[4] else "ללא סוג"))
    # rebuild tbody: text before the first row, the rows, text after the last row (all original bytes kept)
    head = inner[:segs[0].start()] if segs else inner
    tail = inner[segs[-1].end():] if segs else ""
    if not segs and final and not head.endswith("\n"):
        head += "\n"
    new_inner = head + "".join(x[1] for x in final) + tail
    t = old[:tb.start(2)] + new_inner + old[tb.end(2):]

    linked = [x for x in final if x[2]]
    cnt = Counter(x[3] for x in linked)
    order, counts_line = counts(cnt)
    cm = re.search(r'(<p id="ix-counts">)(.*?)(</p>)', t, re.S)
    if cm:
        t = t[:cm.start(2)] + "סך הכול <bdi>%d</bdi> כרטיסים: %s." % (len(linked), counts_line) + t[cm.end(2):]
    else:
        notes.append('no <p id="ix-counts"> in the part; counts line not written')
    errs += text_checks("".join(x[1] for x in final if x[2] in {r[2] for r in added}))
    changed = t != old
    C.write_text(out_path, t)
    print("merged %s (%.1f KB): %d rows kept verbatim, %d added, %d dropped%s" % (
        out_path.name, len(t.encode("utf-8")) / 1024, len(kept), len(added), len(dropped),
        "" if changed else " · part unchanged"))
    if added:
        print("added:", ", ".join(r[2] for r in added))
    if dropped:
        print("dropped (card no longer on the page):", ", ".join(dropped))
    print("by type:", ", ".join("%s %d" % (x, cnt[x]) for x in order) or "-")
    for n in sorted(set(notes)):
        print("NOTE:", n)
    for e in errs:
        print("PROBLEM:", e)
    return 1 if errs else 0


def main() -> int:
    ap = C.arg_parser(__doc__)
    ap.add_argument("--rebuild", action="store_true", help="existing mode: regenerate the whole index instead of merging")
    args = ap.parse_args()
    cfg = C.Config(Path(args.config))
    sid = cfg.techniques_section
    out_path = C.part_path(cfg, sid)
    errs = []
    rows = []
    seen = Counter()
    for num, name, p in C.all_parts(cfg.parts):
        if name == sid:
            continue
        frag = C.read_text(p)
        for cd in C.tech_cards(frag):
            seen[cd["id"]] += 1
            if cd["unit"] is None:
                errs.append("%s: card id %r is not t<n>-<k>" % (p.name, cd["id"]))
                continue
            body = cd["body"]
            h3 = re.search(r"<h3\b[^>]*>(.*?)</h3>", body, re.S)
            title = keep_bdi(h3.group(1)) if h3 else cd["id"]
            plain = [t for c, t in C.header_tags(body) if c == "" and t not in C.STATUS_TAGS]
            types = plain[:1]
            goal = re.search(r"<dt>מטרה</dt>\s*<dd>(.*?)</dd>", body, re.S)
            why = first_sentence(goal.group(1)) if goal else fallback_why(body)
            rows.append((cd["unit"], cd["k"], cd["id"], title, types, why))
    dup = sorted(k for k, v in seen.items() if v > 1)
    if dup:
        errs.append("duplicate card ids: %s" % ", ".join(dup))
    rows.sort(key=lambda r: (r[0], r[1]))

    if cfg.mode == "existing" and out_path.exists() and not args.rebuild:
        return merge(cfg, out_path, rows, errs)

    cnt = Counter((r[4][0] if r[4] else "ללא סוג") for r in rows)
    order, counts_line = counts(cnt)

    h2, lead = DEFAULT_H2, None
    if out_path.exists():
        old = C.read_text(out_path)
        m = re.search(r"[ \t]*<h2\b[^>]*>.*?</h2>", old, re.S)
        if m:
            h2 = m.group(0)
        m = re.search(r'[ \t]*<p class="lead">.*?</p>', old, re.S)
        if m:
            lead = m.group(0)
    if lead is None:
        lead = ('  <p class="lead">מדד של כל כרטיסי השיטה בדף, לפי סדר ה%s. לחיצה על שם השיטה מובילה לכרטיס המלא, '
                'עם השלבים והמקורות. "סוג" הוא הסיווג שבכרטיס; "למה" הוא המשפט הראשון של המטרה שבכרטיס. '
                'שיטה ש"הוזכרה בלבד" מופיעה גם היא, כדי שלא יאבד דבר.</p>' % cfg.unit_label_plural)

    out = ['<section id="%s">' % sid, h2, lead,
           '  <p id="ix-counts">סך הכול <bdi>%d</bdi> כרטיסים: %s.</p>' % (len(rows), counts_line),
           '  <div class="tw">',
           '  <table class="idx" id="ix-table">',
           '    <thead><tr><th>%s</th><th>שם השיטה</th><th>סוג</th><th>למה</th></tr></thead>' % cfg.unit_label,
           '    <tbody>']
    for r in rows:
        out.append("      " + row_html(cfg, r))
    out += ["    </tbody>", "  </table>", "  </div>", "</section>"]
    t = "\n".join(out) + "\n"

    errs += text_checks(t)
    C.write_text(out_path, t)
    print("wrote %s (%.1f KB), %d rows from %d units" % (out_path.name, len(t.encode("utf-8")) / 1024, len(rows),
                                                       len({r[0] for r in rows})))
    print("by type:", ", ".join("%s %d" % (x, cnt[x]) for x in order) or "-")
    print("rows without a why: %d" % sum(1 for r in rows if not r[5]))
    for e in errs:
        print("PROBLEM:", e)
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
