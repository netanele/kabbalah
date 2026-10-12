#!/usr/bin/env python3
"""Build the transcripts section blocks (<details class="tr" id="tr-N">) for the NEW units.

Usage:  python3 -I make_transcripts.py --config <ws>/project.json

Input per unit: transcripts/<id>.json (from transcribe.py). Text units without a JSON may have transcripts/<id>.md
with [עמ' N] markers instead; each line becomes a paragraph and a leading [עמ' N] a link to url#page=N.
Holy-name rules on the transcript text: the Name with or without niqqud -> הוי"ה; "אהיה אשר אהיה" ->
אהי"ה אשר אהי"ה; שדי as a Name -> שד"י by phrase rules only, so "יעלות, שדי וחול" and שדים stay as spoken.

new mode:      writes the whole <section id="transcripts"> part (h2, lead, one block per new unit).
existing mode: inserts the new blocks into the existing transcripts part before its </section>, in unit order
               (before the first old block with a higher number, if any). A unit whose tr-N block already
               exists is skipped, old blocks are never dropped, and a count in the section lead such as
               "אחד־עשר השיעורים" is updated to the new number of blocks. Running it twice changes nothing.
Deterministic: the same JSON gives the same HTML.
"""
import html
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import _common as C  # noqa: E402

WS = re.compile(r"\s+")
TR_BLOCK = re.compile(r'<details class="tr" id="tr-(\d+)">.*?</details>', re.S)


def heb_num(n: int) -> str:
    return "{:,}".format(n)


def short_url(unit: dict) -> str:
    if unit.get("kind", "youtube") == "youtube":
        return "youtube.com/watch?v=%s" % unit["id"]
    u = urlsplit(C.unit_url(unit))
    s = (u.netloc + u.path).rstrip("/")
    return s[4:] if s.startswith("www.") else s


def render_video(cfg, unit: dict, data: dict, count_names: dict):
    n = int(unit["n"])
    lines = []
    count = 0
    for seg in data.get("segments", []):
        text = WS.sub(" ", str(seg.get("text", ""))).strip()
        if not text:
            continue
        text = html.escape(C.holy(text, count_names), quote=False)
        start = int(float(seg.get("start", 0)))
        lines.append('<p><a class="ts" href="%s" target="_blank" rel="noopener"><bdi>%s</bdi></a> %s</p>'
                     % (C.time_href(unit, start), C.hms(start), text))
        count += 1
    model = str(data.get("model", ""))
    credit = "<bdi>Whisper</bdi> של ivrit.ai" if "ivrit" in model else "<bdi>Whisper</bdi>"
    title = unit.get("title") or data.get("title") or unit["id"]
    dur = unit.get("duration_string") or data.get("duration_string") or ""
    out = ['<details class="tr" id="tr-%d">' % n,
           '  <summary><span class="serif">%s %d · %s</span> '
           '<span class="n"><bdi>%s</bdi> · %s קטעים · תמלול אוטומטי</span></summary>'
           % (cfg.unit_label, n, html.escape(title, quote=False), dur, heb_num(count)),
           '  <p class="lead">מקור: <a href="%s" target="_blank" rel="noopener"><bdi>%s</bdi></a> · '
           'תמלול אוטומטי: %s · לחיצה על חותמת הזמן פותחת את הסרטון באותה דקה.</p>'
           % (C.attr(C.unit_url(unit)), html.escape(short_url(unit), quote=False), credit),
           '  <div class="trbody">']
    out.extend(lines)
    out.append("  </div>")
    out.append("</details>")
    return "\n".join(out), count


def render_text(cfg, unit: dict, md: str, count_names: dict):
    n = int(unit["n"])
    lines = []
    count = 0
    body = md.split("\n")
    if body and body[0].startswith("# "):                 # drop the header block up to the first empty line
        i = 0
        while i < len(body) and body[i].strip():
            i += 1
        body = body[i:]
    page_rx = re.compile(r"^\s*\[עמ['׳]\s*(\d+)\]\s*")
    for raw in body:
        line = WS.sub(" ", raw).strip()
        if not line:
            continue
        m = page_rx.match(line)
        link = ""
        if m:
            p = int(m.group(1))
            link = '<a class="ts" href="%s" target="_blank" rel="noopener">עמ\' <bdi>%d</bdi></a> ' % (C.page_href(unit, p), p)
            line = line[m.end():]
        lines.append("<p>%s%s</p>" % (link, html.escape(C.holy(line, count_names), quote=False)))
        count += 1
    title = unit.get("title") or unit["id"]
    pages = unit.get("pages")
    out = ['<details class="tr" id="tr-%d">' % n,
           '  <summary><span class="serif">%s %d · %s</span> <span class="n">%s%s קטעים · טקסט המקור</span></summary>'
           % (cfg.unit_label, n, html.escape(title, quote=False),
              "<bdi>%d</bdi> עמ' · " % int(pages) if pages else "", heb_num(count)),
           '  <p class="lead">מקור: <a href="%s" target="_blank" rel="noopener"><bdi>%s</bdi></a> · '
           'לחיצה על מספר העמוד פותחת את המקור באותו עמוד.</p>'
           % (C.attr(C.unit_url(unit)), html.escape(short_url(unit), quote=False)),
           '  <div class="trbody">']
    out.extend(lines)
    out.append("  </div>")
    out.append("</details>")
    return "\n".join(out), count


def new_lead(cfg, total: int) -> str:
    """The section lead. For video-only pages it is the wording of the original turgeman build."""
    units = cfg.new_units()
    vids = any(C.is_video(u) for u in units)
    texts = any(not C.is_video(u) for u in units)
    if total > 1:
        who = "%s ה%s שעליהם" % (C.heb_count(total), cfg.unit_label_plural)
    else:
        who = "ה%s שעליו" % cfg.unit_label
    model = "(<bdi>Whisper</bdi> בכוונון העברי של ivrit.ai)" if cfg.language == "he" else "(<bdi>Whisper</bdi>)"
    out = ["%s בנוי הדף, מילה במילה." % who]
    if vids:
        out.append("התמלולים אוטומטיים %s ויש בהם שגיאות – בעיקר בשמות, במילים ארמיות, בראשי תיבות ובציטוטים; "
                   "כל פרט חשוב כדאי לאמת מול %s עצמו." % (model, "המקור" if texts else "הסרטון"))
    if texts:
        out.append("טקסט המקור חולץ אוטומטית ויש בו שגיאות%s" % ("." if vids else "; כל פרט חשוב כדאי לאמת מול המקור עצמו."))
    out.append('שמות הקודש נכתבים %s בקיצור (הוי"ה, אהי"ה, שד"י), לפי כללי הספרייה.' % ("בתמלול" if vids else "בטקסט"))
    if vids:
        out.append("חותמת הזמן בכל שורה פותחת את הסרטון באותה דקה.")
    if texts:
        out.append("מספר העמוד בכל שורה פותח את המקור באותו עמוד.")
    return '  <p class="lead">%s</p>' % " ".join(out)


def update_lead_count(cfg, part: str, total: int):
    """Replace '<count> ה<plural>' in the section's own lead (before the first block). Returns (part, changed)."""
    first = part.find('<details class="tr"')
    lm = re.search(r'<p class="lead">(.*?)</p>', part[: first if first >= 0 else len(part)], re.S)
    if not lm or total < 2:
        return part, False
    lead = lm.group(1)
    words = "|".join(re.escape(w) for w in C.HEB_COUNT_WORDS)
    rx = re.compile(r"(?<![א-ת])(?:%s|<bdi>\d+</bdi>|\d+)(?= ה%s(?![א-ת]))"
                    % (words, re.escape(cfg.unit_label_plural)))
    new, k = rx.subn(C.heb_count(total), lead, count=1)
    if not k or new == lead:
        return part, False
    return part[:lm.start(1)] + new + part[lm.end(1):], True


def main() -> int:
    ap = C.arg_parser(__doc__)
    args = ap.parse_args()
    cfg = C.Config(Path(args.config))
    units = cfg.new_units()
    if not units:
        print("no new units in %s" % cfg.path)
        return 0
    names = {}
    sid = cfg.transcripts_section
    existing = C.part_files(cfg.parts, sid)
    part_file = existing[0] if existing else C.part_path(cfg, sid, default_after=89)
    append_mode = cfg.mode == "existing" and bool(existing)
    if cfg.mode == "existing" and not existing:
        print("warning: existing mode but no %s part; writing a new section" % sid, file=sys.stderr)
    part = C.read_text(part_file) if append_mode else ""
    have = {int(x) for x in TR_BLOCK.findall(part)}

    blocks = []                    # (n, html)
    total_segments = 0
    for u in units:
        n = int(u["n"])
        if n in have:
            print("%s %d: tr-%d already in %s, skipped" % (cfg.unit_label, n, n, part_file.name))
            continue
        jf = cfg.transcripts / ("%s.json" % u["id"])
        mf = cfg.transcripts / ("%s.md" % u["id"])
        if jf.is_file():
            data = json.loads(C.read_text(jf))
            block, count = render_video(cfg, u, data, names)
        elif C.is_text(u) and mf.is_file():
            block, count = render_text(cfg, u, C.read_text(mf), names)
        else:
            print("warning: missing transcript for %s %d (%s): %s" % (cfg.unit_label, n, u["id"], jf), file=sys.stderr)
            if not append_mode:
                blocks.append((n, "<!-- transcript missing: %s %d (%s) -->" % (cfg.section_prefix, n, u["id"])))
            continue
        blocks.append((n, block))
        total_segments += count
        print("%s %d  %s  %5d segments" % (cfg.unit_label, n, u["id"], count))

    if append_mode:
        before = len(TR_BLOCK.findall(part))
        for n, block in blocks:
            nxt = next((m for m in TR_BLOCK.finditer(part) if int(m.group(1)) > n), None)
            if nxt:
                part = part[:nxt.start()] + block + "\n" + part[nxt.start():]
            else:
                end = part.rfind("</section>")
                if end < 0:
                    raise SystemExit("%s has no </section>" % part_file)
                part = part[:end] + block + "\n" + part[end:]
        after = len(TR_BLOCK.findall(part))
        if after != before + sum(1 for _, b in blocks if b.startswith("<details")):
            raise SystemExit("internal error: block count %d -> %d" % (before, after))
        part, changed = update_lead_count(cfg, part, after)
        text = part
        summary = "%d old block(s) kept, %d added, lead count %s" % (before, after - before,
                                                                    "updated to %d" % after if changed else "unchanged")
    else:
        done = sum(1 for _, b in blocks if b.startswith("<details"))
        out = ['<section id="%s">' % sid, "  <h2>תמלולים מלאים</h2>", new_lead(cfg, done)]
        out += [b for _, b in sorted(blocks, key=lambda x: x[0])]
        out.append("</section>")
        text = "\n".join(out) + "\n"
        summary = "%d unit(s)" % done

    C.write_text(part_file, text)
    print("holy-name substitutions: %s (total %d)" % (", ".join("%s %d" % kv for kv in names.items()) or "-",
                                                      sum(names.values())))
    print("wrote %s  (%s, %d new segments, %.1f KB)" % (part_file, summary, total_segments, len(text.encode("utf-8")) / 1024))
    return 0


if __name__ == "__main__":
    sys.exit(main())
