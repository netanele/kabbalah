#!/usr/bin/env python3
"""Full content QA of the assembled page.

Usage:  python3 -I check_page.py --config <ws>/project.json [--file PAGE.html] [--all]

PAGE defaults to out/<page> (or <repo>/<page> when out/ has none). Output, for grepping:
  SUMMARY            one line per check: level, code, count
  ## <code> (<n>)    one section per check, always printed (also with 0), then up to 40 hits with line and section
  ## stats           page size, link counts, a per-unit summary
  result: E errors, W warnings, R to review        (the last line; exit 1 when E > 0)
Codes:
  ERROR   name (the full Name, niqqud-aware) · ai-mention (claude, anthropic, openai, chatgpt, gpt-,
          בינה מלאכותית; whole words, so מסוכן never matches) · split-bdi (</bdi>–<bdi>) · status-tags (a technique
          card without exactly one of נמסר במלואו / נמסר בחלקו / הוזכר בלבד / סופר כמעשה) · red-tags (a red tag other
          than לא נמסר בשיעור / הרב לא מגלה / נדחה לשיעור נפרד / לא ברור בתמלול / לא פורסם) · duplicate-id ·
          dangling-anchor · yt-t-beyond-duration · chip-unit-mismatch (the chip's unit name is not the unit of
          its video id or text source) · chip-time-mismatch (the chip's hh:mm:ss differs from its t=)
  WARN    unc-in-h3-inl ("[?]" inside an h3 or .inl element) · unit-tag (a card without <span class="tag d"><display></span>,
          display = the unit's "label", else "<unit_label> N") · card-sequence (card numbers not 1..k, or ids that are
          not t<n>-<k>) · raw-ampersand ("&t=" in an
          href) · inline-style / img-iframe-script (inside sections) · chip-no-bdi · time-without-bdi (authored text)
  REVIEW  plain-name (שדי / אהיה / אדני written plainly in the authored text, i.e. before the transcripts section)
          · name-permutation (other orders of the Name's letters as a word; והיה is skipped) · religion (מוסלמ*,
          נוצרי*, נוצרים, קוראן, צלב, איסלאם/אסלאם, נצרות, כנסייה, מסגד, ישו, מוחמד, כומר, בודה*, הינדו*, with
          prefixes ו/ה/ב/ל/מ/ש/כ, authored text only) · yt-external (a YouTube id that is not a config unit) ·
          latin-in-text (Latin outside <bdi> and URLs in the authored text)
status-tags, red-tags, unit-tag and card-sequence cover only units with "new": true, unless --all.
"""
import html
import itertools
import re
import sys
from collections import Counter, OrderedDict
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import _common as C  # noqa: E402

M = "[%s]*" % C.MARKS
NOT_HEB_BEFORE = "(?<![א-ת\"'׳״])"
NOT_HEB_AFTER = "(?![א-ת\"'׳״])"
HEB_LETTER = "[" + C.HEB + "]"
PREFIX = "(?<![א-ת])(?:[ובכלמשה]{0,2})"
AI = [(re.compile(r"(?<![A-Za-z])(claude|anthropic|openai|chatgpt)(?![A-Za-z])", re.I), None),
      (re.compile(r"(?<![A-Za-z])gpt-", re.I), None),
      (re.compile("בינה מלאכותית"), None)]
REL_STAR = ["מוסלמ", "נוצרי", "בודה", "הינדו"]
REL_WORD = ["נוצרים", "קוראן", "קורא\"ן", "צלב", "איסלאם", "אסלאם", "נצרות", "כנסייה", "כנסיה", "מסגד", "ישו",
            "מוחמד", "כומר", "כמרים"]
# common words that happen to permute the Name's letters
PERM_SKIP = {"יהוה", "והיה"}
LEVELS = ("ERROR", "WARN", "REVIEW", "INFO")


class Report:
    def __init__(self):
        self.items = OrderedDict()

    def declare(self, level, key):
        self.items.setdefault(key, (level, []))

    def add(self, level, key, msg):
        self.declare(level, key)
        self.items[key][1].append(msg)


def main() -> int:
    ap = C.arg_parser(__doc__)
    ap.add_argument("--file", help="the page to check (default: out/<page>, else <repo>/<page>)")
    ap.add_argument("--all", action="store_true", help="status checks for every unit, not only new ones")
    args = ap.parse_args()
    cfg = C.Config(Path(args.config))
    path = Path(args.file) if args.file else (cfg.out if cfg.out.exists() else cfg.repo_page)
    if not path.is_file():
        raise SystemExit("page not found: %s" % path)
    doc = C.read_text(path)
    loc = C.Locator(doc)
    R = Report()
    tr = C.section_start(doc, cfg.transcripts_section)
    authored_end = tr if tr >= 0 else len(doc)
    masked = C.mask_markup(doc)
    no_bdi = C.mask_markup(re.sub(r"<bdi\b[^>]*>.*?</bdi>", lambda m: re.sub(r"[^\n]", " ", m.group(0)), doc, flags=re.S))
    scope_units = {int(u["n"]) for u in (cfg.units if args.all else cfg.new_units())}
    units_by_id = {u["id"]: u for u in cfg.units if u.get("id")}

    def ctx(off, n=50):
        return re.sub(r"\s+", " ", doc[max(0, off - n): off + n])

    for lvl, key in [("ERROR", "name"), ("ERROR", "ai-mention"), ("ERROR", "split-bdi"),
                     ("ERROR", "status-tags"), ("ERROR", "red-tags"), ("ERROR", "duplicate-id"),
                     ("ERROR", "dangling-anchor"), ("ERROR", "yt-t-beyond-duration"), ("ERROR", "chip-unit-mismatch"),
                     ("ERROR", "chip-time-mismatch"),
                     ("WARN", "unc-in-h3-inl"), ("WARN", "unit-tag"), ("WARN", "card-sequence"),
                     ("WARN", "raw-ampersand"), ("WARN", "inline-style"), ("WARN", "img-iframe-script"),
                     ("WARN", "chip-no-bdi"), ("WARN", "time-without-bdi"),
                     ("REVIEW", "plain-name"), ("REVIEW", "name-permutation"),
                     ("REVIEW", "religion"), ("REVIEW", "yt-external"), ("REVIEW", "latin-in-text"),
                     ("INFO", "stats")]:
        R.declare(lvl, key)

    # ---- holy names ----
    for m in C.NAME_ANY.finditer(doc):
        R.add("ERROR", "name", "%s · …%s…" % (loc.where(m.start()), ctx(m.start())))
    auth = masked[:authored_end]
    for w in ("שדי", "אהיה", "אדני"):
        for m in re.finditer(NOT_HEB_BEFORE + M.join(w) + NOT_HEB_AFTER, auth):
            R.add("REVIEW", "plain-name", "%s · %s · …%s…" % (w, loc.where(m.start()), ctx(m.start())))
    for p in sorted(set("".join(x) for x in itertools.permutations("יהוה")) - PERM_SKIP):
        for m in re.finditer(NOT_HEB_BEFORE + M.join(p) + NOT_HEB_AFTER, auth):
            R.add("REVIEW", "name-permutation", "%s · %s · …%s…" % (p, loc.where(m.start()), ctx(m.start())))

    # ---- how the page was made ----
    for rx, _ in AI:
        for m in rx.finditer(doc):
            R.add("ERROR", "ai-mention", "%s · %s · …%s…" % (m.group(0), loc.where(m.start()), ctx(m.start())))

    # ---- other religions (authored text only; transcripts stay verbatim) ----
    rel_hits = {}
    for w in REL_STAR:
        for m in re.finditer(PREFIX + re.escape(w) + HEB_LETTER + "*", auth):
            rel_hits.setdefault(m.start(), m.group(0))
    for w in REL_WORD:
        for m in re.finditer(PREFIX + re.escape(w) + "(?!" + HEB_LETTER + ")", auth):
            rel_hits.setdefault(m.start(), m.group(0))
    for off in sorted(rel_hits):
        R.add("REVIEW", "religion", "%s · %s · …%s…" % (rel_hits[off], loc.where(off), ctx(off, 70)))

    # ---- bdi ----
    for m in re.finditer(r"</bdi>\s*[–—-]\s*<bdi>", doc):
        R.add("ERROR", "split-bdi", "%s · …%s…" % (loc.where(m.start()), ctx(m.start())))

    # ---- technique cards ----
    cards = C.tech_cards(doc)
    per_unit = {}
    for cd in cards:
        if cd["unit"] is None:
            R.add("WARN", "card-sequence", "card id %r is not t<n>-<k> · %s" % (cd["id"], loc.where(cd["start"])))
            continue
        per_unit.setdefault(cd["unit"], []).append(cd)
        if cd["unit"] not in scope_units:
            continue
        tags = C.header_tags(cd["body"])
        status = [t for c, t in tags if t in C.STATUS_TAGS]
        if len(status) != 1:
            R.add("ERROR", "status-tags", "%s has %d primary status tags %s · %s" % (cd["id"], len(status), status, loc.where(cd["start"])))
        for c, t in tags:
            if c == "r" and t not in C.RED_TAGS:
                R.add("ERROR", "red-tags", "%s: red tag %r · %s" % (cd["id"], t, loc.where(cd["start"])))
        want = cfg.display(cd["unit"])
        if not any(c == "d" and t == want for c, t in tags):
            R.add("WARN", "unit-tag", "%s: no <span class=\"tag d\">%s</span> · %s" % (cd["id"], want, loc.where(cd["start"])))
    for n, lst in sorted(per_unit.items()):
        if n in scope_units:
            ks = [cd["k"] for cd in lst]
            if ks != list(range(1, len(ks) + 1)):
                R.add("WARN", "card-sequence", "unit %d card numbers: %s" % (n, ks))

    # ---- [?] in h3 / .inl ----
    for m in re.finditer(r"<h3\b[^>]*>(.*?)</h3>", doc, re.S):
        if "[?]" in m.group(1):
            R.add("WARN", "unc-in-h3-inl", "h3 · %s · %s" % (loc.where(m.start()), C.strip_tags(m.group(1))[:80]))
    for m in re.finditer(r'<(\w+)\b[^>]*\bclass="[^"]*\binl\b[^"]*"[^>]*>(.*?)</\1>', doc, re.S):
        if "[?]" in m.group(2):
            R.add("WARN", "unc-in-h3-inl", ".inl · %s · %d marker(s)" % (loc.where(m.start()), m.group(2).count("[?]")))

    # ---- ids and anchors ----
    id_pos = [(m.group(1), m.start()) for m in re.finditer(r'\sid="([^"]+)"', doc)]
    ids = Counter(i for i, _ in id_pos)
    for i, k in sorted(ids.items()):
        if k > 1:
            R.add("ERROR", "duplicate-id", "%s ×%d" % (i, k))
    for m in re.finditer(r'href="#([^"]+)"', doc):
        if m.group(1) not in ids:
            R.add("ERROR", "dangling-anchor", "#%s · %s" % (m.group(1), loc.where(m.start())))

    # ---- YouTube links ----
    yt_total = 0
    cross = 0
    label_rx = re.compile(re.escape(cfg.unit_label) + r"\s*(\d+)")
    displays = sorted(((C.unit_display(cfg, x), int(x["n"])) for x in cfg.units), key=lambda d: -len(d[0]))

    def claimed_unit(label):
        """The unit a chip label names: the longest config display it starts with, else '<unit_label> N'."""
        lab = label.strip()
        for disp, num in displays:
            if lab.startswith(disp) and not re.match(r"[\w'\"\u05f3\u05f4]", lab[len(disp):len(disp) + 1]):
                return num
        lm = label_rx.match(lab)
        return int(lm.group(1)) if lm else None
    sec_rx = re.compile(r"^%s-(\d+)$" % re.escape(cfg.section_prefix))
    for m in re.finditer(r'<a\b([^>]*)>(.*?)</a>', doc, re.S):
        hm = re.search(r'\bhref="(https?://(?:www\.|m\.)?(?:youtube\.com|youtu\.be)[^"]*)"', m.group(1))
        if not hm:
            continue
        yt_total += 1
        url = html.unescape(hm.group(1))
        if re.search(r"/@|/channel/|/c/|/playlist|results\?|/user/", url):
            continue
        vm = re.search(r"[?&]v=([A-Za-z0-9_-]{11})", url) or re.search(r"youtu\.be/([A-Za-z0-9_-]{11})", url)
        vid = vm.group(1) if vm else None
        u = units_by_id.get(vid)
        if u is None:
            R.add("REVIEW", "yt-external", "%s · %s" % (url, loc.where(m.start())))
            continue
        tm = re.search(r"[?&]t=(\d+)s?(?![\w])", url)
        dur = u.get("duration")
        if tm and dur and int(tm.group(1)) > int(dur):
            R.add("ERROR", "yt-t-beyond-duration", "%s (t=%s > %s) · %s" % (url, tm.group(1), dur, loc.where(m.start())))
        label_html = m.group(2)
        label = C.strip_tags(label_html)
        claim = claimed_unit(label)
        if claim is not None and claim != int(u["n"]):
            R.add("ERROR", "chip-unit-mismatch", "label %r but %s is %s · %s" % (label[:40], vid, C.unit_display(cfg, u), loc.where(m.start())))
        tl = re.search(r"(\d{1,2}):(\d{2}):(\d{2})", label)
        if tl and tm:
            secs = int(tl.group(1)) * 3600 + int(tl.group(2)) * 60 + int(tl.group(3))
            if abs(secs - int(tm.group(1))) > 1:
                R.add("ERROR", "chip-time-mismatch", "label %s vs t=%s · %s" % (tl.group(0), tm.group(1), loc.where(m.start())))
        if tl and "<bdi>" not in label_html:
            R.add("WARN", "chip-no-bdi", "%s · %s" % (label[:40], loc.where(m.start())))
        sm = sec_rx.match(loc.section(m.start()))
        if sm and int(sm.group(1)) != int(u["n"]):
            cross += 1

    # ---- page chips of text units (pdf/web/doc): the label must name the unit of the linked source ----
    text_urls = {}                       # one book's chapters often share a single PDF link
    for x in cfg.units:
        if C.is_text(x) and C.unit_url(x):
            text_urls.setdefault(C.attr(C.unit_url(x)), []).append(x)
    if text_urls:
        for m in re.finditer(r'<a\b([^>]*)>(.*?)</a>', doc, re.S):
            hm = re.search(r'\bhref="([^"#]*)(?:#[^"]*)?"', m.group(1))
            if not hm or hm.group(1) not in text_urls:
                continue
            us = text_urls[hm.group(1)]
            claim = claimed_unit(C.strip_tags(m.group(2)))
            if claim is not None and claim not in {int(x["n"]) for x in us}:
                R.add("ERROR", "chip-unit-mismatch", "label %r but the link is %s · %s" % (
                    C.strip_tags(m.group(2))[:40], " / ".join(C.unit_display(cfg, x) for x in us), loc.where(m.start())))

    # ---- markup hygiene ----
    for m in re.finditer(r'href="[^"]*&t=', doc):
        R.add("WARN", "raw-ampersand", loc.where(m.start()))
    sections = C.top_sections(doc)
    spans = [(s["start"], s["end"]) for s in sections]

    def in_section(off):
        return any(a <= off < b for a, b in spans)
    for m in re.finditer(r'<[a-zA-Z][^>]*\sstyle="', doc):
        if in_section(m.start()):
            R.add("WARN", "inline-style", loc.where(m.start()))
    for m in re.finditer(r"<(img|iframe|script)\b", doc, re.I):
        if in_section(m.start()):
            R.add("WARN", "img-iframe-script", "<%s · %s" % (m.group(1), loc.where(m.start())))
    for m in re.finditer(r"(?<![\w:])\d{1,2}:\d{2}(?::\d{2})?(?![\w:])", no_bdi[:authored_end]):
        if True:
            R.add("WARN", "time-without-bdi", "%s · %s · …%s…" % (m.group(0), loc.where(m.start()), ctx(m.start(), 40)))
    for m in re.finditer(r"\S*[A-Za-z]{2,}\S*", no_bdi[:authored_end]):
        tok = m.group(0)
        if re.search(r"https?://|www\.|\.(?:com|org|net|il|ai)\b|&[a-z]+;", tok):
            continue
        R.add("REVIEW", "latin-in-text", "%r · %s" % (tok[:40], loc.where(m.start())))

    # ---- stats ----
    size = len(doc.encode("utf-8"))
    R.add("INFO", "stats", "file %s · %.2f MB (%d bytes)" % (path, size / 1048576, size))
    R.add("INFO", "stats", "technique cards %d · YouTube links %d · cross-unit chips %d · [?] markers %d (authored %d)"
          % (len(cards), yt_total, cross, doc.count("[?]"), doc[:authored_end].count("[?]")))
    for u in cfg.units:
        n = int(u["n"])
        rng = C.find_section(doc, cfg.section_id(n))
        if not rng:
            R.add("INFO", "stats", "%s: no section %s" % (C.unit_display(cfg, u), cfg.section_id(n)))
            continue
        s = doc[rng[0]:rng[1]]
        R.add("INFO", "stats", "%s%s: cards %d · chips %d · [?] %d · %.1f KB" % (
            C.unit_display(cfg, u), " (new)" if u.get("new") else "", len(per_unit.get(n, [])),
            s.count('class="src"') + s.count('class="ts"'), s.count("[?]"), len(s.encode("utf-8")) / 1024))

    # ---- output ----
    scope = "all units" if args.all else ("new units %s" % sorted(scope_units) if scope_units else "no new units (use --all)")
    print("check_page: %s · status scope: %s" % (path.name, scope))
    print("SUMMARY")
    for lvl in LEVELS[:3]:
        for key, (l, msgs) in R.items.items():
            if l == lvl:
                print("  %-6s %-20s %d" % (lvl, key, len(msgs)))
    for key, (l, msgs) in R.items.items():
        if key == "stats":
            continue
        print("\n## %s (%d)" % (key, len(msgs)))
        for x in msgs[:40]:
            print("  - " + x)
        if len(msgs) > 40:
            print("  … %d more" % (len(msgs) - 40))
    print("\n## stats")
    for x in R.items["stats"][1]:
        print("  - " + x)
    tot = {lvl: sum(len(m) for k, (l, m) in R.items.items() if l == lvl) for lvl in LEVELS}
    errors = tot["ERROR"]
    print("\nresult: %d errors, %d warnings, %d to review" % (errors, tot["WARN"], tot["REVIEW"]))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
