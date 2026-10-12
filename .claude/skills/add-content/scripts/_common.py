"""Shared helpers for the add-content scripts (stdlib only).

Every script starts with
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import _common as C
because `python3 -I` does not put the script's own directory on sys.path, and ignores
PYTHONDONTWRITEBYTECODE (no __pycache__ may land in the repo).
"""
import argparse
import bisect
import json
import re
from html.parser import HTMLParser
from pathlib import Path

# ---- Hebrew / library rules -------------------------------------------------------------------
MARKS = "\u0591-\u05c7"            # niqqud + te'amim
HEB = "\u05d0-\u05ea"              # letters alef..tav
# the four-letter Name, with or without marks between the letters (never written in full in the library)
NAME_ANY = re.compile("\u05d9[%s]*\u05d4[%s]*\u05d5[%s]*\u05d4" % (MARKS, MARKS, MARKS))
STATUS_TAGS = ("נמסר במלואו", "נמסר בחלקו", "הוזכר בלבד", "סופר כמעשה")
RED_TAGS = ("לא נמסר בשיעור", "הרב לא מגלה", "נדחה לשיעור נפרד", "לא ברור בתמלול", "לא פורסם")
# the known technique types, in the order the index lists them; unknown types follow alphabetically
TYPE_ORDER = ["קמיע", "גורל", "סגולה", "כוונה", "תפילה", "השבעה", "הכנה ותנאים", "איסור ואזהרה", "עיוני"]
VIDEO_KINDS = ("youtube", "video")
TEXT_KINDS = ("pdf", "web", "doc")
VOID_TAGS = {"br", "hr", "img", "input", "meta", "link", "wbr", "source", "track", "col", "area", "base", "embed", "param"}

PLACEHOLDER = re.compile(r"<!-- @@SECTION:([A-Za-z0-9_-]+) @@ -->")
SECTION_ID_OK = re.compile(r"^[A-Za-z0-9_-]+$")
TS_STRICT = re.compile(r"^\d\d:\d\d:\d\d$")


def placeholder(name: str) -> str:
    return "<!-- @@SECTION:%s @@ -->" % name


# ---- config -------------------------------------------------------------------------------------
class Config:
    def __init__(self, path: Path):
        self.path = Path(path).expanduser().resolve()
        if not self.path.is_file():
            raise SystemExit("config not found: %s" % self.path)
        self.ws = self.path.parent
        d = json.loads(read_text(self.path))
        self.data = d
        for key in ("repo", "page"):
            if not d.get(key):
                raise SystemExit("%s: the field %r is required" % (self.path, key))
        self.repo = Path(d["repo"]).expanduser()
        self.page = d["page"]
        self.mode = d.get("mode", "new")
        if self.mode not in ("new", "existing"):
            raise SystemExit("%s: mode must be 'new' or 'existing', not %r" % (self.path, self.mode))
        self.title = d.get("title", "")
        self.unit_label = d.get("unit_label", "שיעור")
        self.unit_label_plural = d.get("unit_label_plural") or (self.unit_label + "ים")
        self.section_prefix = d.get("section_prefix", "lesson")
        self.language = d.get("language", "he")
        self.units = sorted(d.get("units", []), key=lambda u: int(u["n"]))
        self.transcripts_section = d.get("transcripts_section", "transcripts")
        self.techniques_section = d.get("techniques_section", "techniques")
        # workspace layout
        self.meta = self.ws / "meta"
        self.audio = self.ws / "audio"
        self.transcripts = self.ws / "transcripts"
        self.notes = self.ws / "notes"
        self.logs = self.ws / "logs"
        self.build = self.ws / "build"
        self.parts = self.build / "parts"
        self.tpl = self.build / "tpl"
        self.skeleton = self.build / "skeleton.html"
        self.out = self.ws / "out" / self.page
        self.repo_page = self.repo / self.page

    def save(self) -> None:
        write_text(self.path, json.dumps(self.data, ensure_ascii=False, indent=2) + "\n")

    def unit(self, n: int) -> dict:
        for u in self.units:
            if int(u["n"]) == int(n):
                return u
        raise SystemExit("unit %s is not in %s" % (n, self.path))

    def unit_by_id(self, vid: str):
        for u in self.units:
            if u.get("id") == vid:
                return u
        return None

    def new_units(self) -> list:
        return [u for u in self.units if u.get("new")]

    def section_id(self, n: int) -> str:
        return "%s-%d" % (self.section_prefix, int(n))


def arg_parser(doc: str) -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=(doc or "").strip().splitlines()[0] if doc else None,
                                epilog=doc, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--config", required=True, help="<workspace>/project.json")
    return p


def load_config(argv=None) -> Config:
    """Parse --config from argv (or sys.argv) and return the Config. Other arguments are left alone."""
    import sys
    args = list(sys.argv[1:] if argv is None else argv)
    if "--config" not in args:
        raise SystemExit("usage: ... --config <workspace>/project.json")
    i = args.index("--config")
    if i + 1 >= len(args):
        raise SystemExit("--config needs a path")
    return Config(Path(args[i + 1]))


def is_video(unit: dict) -> bool:
    return unit.get("kind", "youtube") in VIDEO_KINDS


def is_text(unit: dict) -> bool:
    return unit.get("kind", "youtube") in TEXT_KINDS


def unit_url(unit: dict) -> str:
    """The unit's canonical URL (raw, not HTML-escaped). YouTube units always use watch?v=<id>."""
    if unit.get("kind", "youtube") == "youtube" and unit.get("id"):
        return "https://www.youtube.com/watch?v=%s" % unit["id"]
    return unit.get("url") or ""


def attr(url: str) -> str:
    """A URL ready for an href attribute: every & becomes &amp; (already escaped ones stay as they are)."""
    return url.replace("&amp;", "&").replace("&", "&amp;").replace('"', "%22")


# ---- files --------------------------------------------------------------------------------------
def read_text(p: Path) -> str:
    """Read UTF-8 text without newline translation (byte-faithful round trips)."""
    with open(p, encoding="utf-8", newline="") as f:
        return f.read()


def write_text(p: Path, s: str) -> None:
    Path(p).parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8", newline="") as f:
        f.write(s)


def part_files(parts_dir: Path, name: str) -> list:
    """Parts for a section id: files named ^\\d+-<name>\\.html$ (so lesson-1 never matches lesson-10)."""
    if not parts_dir.is_dir():
        return []
    rx = re.compile(r"^\d+-%s\.html$" % re.escape(name))
    return sorted((p for p in parts_dir.iterdir() if rx.match(p.name)), key=lambda p: (int(p.name.split("-", 1)[0]), p.name))


def all_parts(parts_dir: Path) -> list:
    """Every part file, as (number, section-id, path), sorted by number then name."""
    out = []
    if parts_dir.is_dir():
        for p in parts_dir.iterdir():
            m = re.match(r"^(\d+)-(.+)\.html$", p.name)
            if m:
                out.append((int(m.group(1)), m.group(2), p))
    return sorted(out)


def part_number_width(parts_dir: Path) -> int:
    w = 2
    for n, _, p in all_parts(parts_dir):
        w = max(w, len(p.name.split("-", 1)[0]))
    return w


def next_free_number(parts_dir: Path, after: int) -> int:
    used = {n for n, _, _ in all_parts(parts_dir)}
    n = after + 1
    while n in used:
        n += 1
    return n


def part_path(cfg: Config, sid: str, default_after: int = None) -> Path:
    """The part file for section id `sid`: the existing one if there is one; otherwise a new number that follows
    the nearest preceding placeholder (in skeleton order) that already has a part, or `default_after`."""
    have = part_files(cfg.parts, sid)
    if have:
        return have[0]
    width = part_number_width(cfg.parts)
    after = None
    if cfg.skeleton.is_file():
        order = PLACEHOLDER.findall(read_text(cfg.skeleton))
        if sid in order:
            for prev in reversed(order[:order.index(sid)]):
                pf = part_files(cfg.parts, prev)
                if pf:
                    after = int(pf[0].name.split("-", 1)[0])
                    break
    if after is None:
        if default_after is not None:
            after = default_after
        else:
            nums = [n for n, _, _ in all_parts(cfg.parts)]
            after = max(nums) if nums else 0
    n = next_free_number(cfg.parts, after)
    return cfg.parts / ("%0*d-%s.html" % (width, n, sid))


# ---- time ---------------------------------------------------------------------------------------
def hms(sec) -> str:
    s = int(sec)
    return "%02d:%02d:%02d" % (s // 3600, (s % 3600) // 60, s % 60)


def to_secs(ts: str) -> int:
    parts = [int(x) for x in ts.strip().split(":")]
    while len(parts) < 3:
        parts.insert(0, 0)
    h, m, s = parts[-3:]
    return h * 3600 + m * 60 + s


def norm_ts(ts: str) -> str:
    return hms(to_secs(ts))


def date_from_upload(upload_date: str) -> str:
    """'20220527' -> '27.5.2022' (the page's own unpadded d.m.yyyy)."""
    if not upload_date or not re.fullmatch(r"\d{8}", upload_date):
        return ""
    return "%d.%d.%s" % (int(upload_date[6:8]), int(upload_date[4:6]), upload_date[:4])


# ---- chips --------------------------------------------------------------------------------------
def time_href(unit: dict, secs: int) -> str:
    base = attr(unit_url(unit))
    return base + ("&amp;t=%ds" if "?" in base else "?t=%ds") % secs


def page_href(unit: dict, page: int) -> str:
    return attr(unit_url(unit)) + "#page=%d" % page


def chip_src(cfg: Config, unit: dict, ts: str) -> str:
    """a.src chip. The label shows the timestamp exactly as written in the template (like the original renderer)."""
    ts = ts.strip()
    return '<a class="src" href="%s" target="_blank" rel="noopener">%s %d · <bdi>%s</bdi></a>' % (
        time_href(unit, to_secs(ts)), cfg.unit_label, int(unit["n"]), ts)


def chip_ts(unit: dict, ts: str) -> str:
    ts = ts.strip()
    return '<a class="ts" href="%s" target="_blank" rel="noopener"><bdi>%s</bdi></a>' % (time_href(unit, to_secs(ts)), ts)


def chip_page(cfg: Config, unit: dict, page: int) -> str:
    return '<a class="src" href="%s" target="_blank" rel="noopener">%s %d · עמ\' <bdi>%d</bdi></a>' % (
        page_href(unit, page), cfg.unit_label, int(unit["n"]), page)


# ---- holy names (transcripts) -------------------------------------------------------------------
NAME_SUB = re.compile("\u05d9[%s]*\u05d4[%s]*\u05d5[%s]*\u05d4[%s]*" % (MARKS, MARKS, MARKS, MARKS))
EHYEH = re.compile("אהיה אשר אהיה")
# phrase rules only, so the ordinary words שדים / שדיין / "יעלות, שדי וחול" (a book title) stay as spoken
SHADDAI_AFTER_WORD = re.compile("(בשם|שם|מלכות|של|חותם|אל|כותבים|כל) שדי(?![\u05d0-\u05ea])")
SHADDAI_BEFORE_WORD = re.compile("(?<![\u05d0-\u05ea])שדי (שאמר|הוויה)")


def holy(text: str, count: dict = None) -> str:
    """Library rule for spoken Names: the Name -> הוי"ה, אהיה אשר אהיה -> אהי"ה אשר אהי"ה, שדי as a Name -> שד"י."""
    count = {} if count is None else count
    for key in ('הוי"ה', 'אהי"ה', 'שד"י'):
        count.setdefault(key, 0)
    text, n = NAME_SUB.subn('הוי"ה', text)
    count['הוי"ה'] += n
    text, n = EHYEH.subn('אהי"ה אשר אהי"ה', text)
    count['אהי"ה'] += n
    text, n = SHADDAI_AFTER_WORD.subn('\\1 שד"י', text)
    count['שד"י'] += n
    text, n = SHADDAI_BEFORE_WORD.subn('שד"י \\1', text)
    count['שד"י'] += n
    return text


# ---- HTML scanning ------------------------------------------------------------------------------
_SKIP = r"<!--.*?-->|<script\b.*?</script\s*>|<style\b.*?</style\s*>"
_SECTION_TOKENS = re.compile(_SKIP + r"|<section\b[^>]*>|</section\s*>", re.S | re.I)
_MARKUP = re.compile(_SKIP + r"|<[^>]*>", re.S | re.I)


def main_range(doc: str):
    """(start, end, tag) of the content of <main>…</main>; falls back to <body>…</body>; None if neither."""
    for tag in ("main", "body"):
        mo = re.search(r"<%s\b[^>]*>" % tag, doc, re.I)
        mc = re.search(r"</%s\s*>" % tag, doc, re.I)
        if mo and mc and mc.start() > mo.end():
            return mo.end(), mc.start(), tag
    return None


def top_sections(doc: str, lo: int = 0, hi: int = None) -> list:
    """Top-level <section> elements between lo and hi, skipping comments, <script> and <style>.
    Returns dicts {id, start, end, nested, closed} where end is the offset just after </section>."""
    hi = len(doc) if hi is None else hi
    out = []
    depth = 0
    cur = None
    for m in _SECTION_TOKENS.finditer(doc, lo, hi):
        tok = m.group(0)
        low = tok[:9].lower()
        if low.startswith("<!--") or low.startswith("<script") or low.startswith("<style"):
            continue
        if low.startswith("</section"):
            if depth == 0:
                continue                      # stray close: belongs to an enclosing section outside the range
            depth -= 1
            if depth == 0 and cur is not None:
                cur["end"] = m.end()
                cur["closed"] = True
                out.append(cur)
                cur = None
            continue
        # opening <section ...>
        if depth == 0:
            idm = re.search(r"""\bid\s*=\s*(?:"([^"]*)"|'([^']*)')""", tok)
            cur = {"id": (idm.group(1) if idm and idm.group(1) is not None else (idm.group(2) if idm else None)),
                   "start": m.start(), "end": None, "nested": 0, "closed": False}
        elif cur is not None:
            cur["nested"] += 1
        depth += 1
    if cur is not None:                       # unclosed at the end of the range
        cur["end"] = hi
        out.append(cur)
    return out


def find_section(doc: str, sid: str):
    """(start, end) of the <section id="sid">…</section>, or None."""
    m = re.search(r"""<section\b[^>]*\bid\s*=\s*["']%s["'][^>]*>""" % re.escape(sid), doc)
    if not m:
        return None
    secs = top_sections(doc, m.start(), len(doc))
    if secs and secs[0]["start"] == m.start() and secs[0]["closed"]:
        return secs[0]["start"], secs[0]["end"]
    return None


def section_start(doc: str, sid: str) -> int:
    """Offset of <section … id="sid" …>, or -1."""
    m = re.search(r"""<section\b[^>]*\bid\s*=\s*["']%s["'][^>]*>""" % re.escape(sid), doc)
    return m.start() if m else -1


def mask_markup(doc: str) -> str:
    """Same length as doc, with comments, <script>, <style> and every tag blanked to spaces (newlines kept),
    so regexes see text nodes only and offsets still point into the original."""
    return _MARKUP.sub(lambda m: re.sub(r"[^\n]", " ", m.group(0)), doc)


class Locator:
    """Fast offset -> (line, section id) lookups on a big document."""

    def __init__(self, doc: str):
        self.nl = [m.start() for m in re.finditer("\n", doc)]
        self.sec_pos = []
        self.sec_id = []
        for m in re.finditer(r"""<section\b[^>]*\bid\s*=\s*["']([^"']+)["']""", doc):
            self.sec_pos.append(m.start())
            self.sec_id.append(m.group(1))

    def line(self, off: int) -> int:
        return bisect.bisect_right(self.nl, off - 1) + 1

    def section(self, off: int) -> str:
        i = bisect.bisect_right(self.sec_pos, off) - 1
        return self.sec_id[i] if i >= 0 else "-"

    def where(self, off: int) -> str:
        return "line %d · section %s" % (self.line(off), self.section(off))


def strip_tags(s: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", s)).strip()


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def latin_outside_bdi(fragment: str) -> list:
    """Latin words in text nodes, ignoring <bdi>…</bdi> content, anything inside tags (URLs live in attributes),
    and character references such as &amp;."""
    t = re.sub(r"<bdi\b[^>]*>.*?</bdi>", "", fragment, flags=re.S)
    t = re.sub(r"<!--.*?-->", "", t, flags=re.S)
    t = re.sub(r"<[^>]+>", "", t)
    t = re.sub(r"&(?:[A-Za-z][A-Za-z0-9]*|#\d+|#x[0-9A-Fa-f]+);", "", t)
    return sorted(set(re.findall(r"[A-Za-z]+", t)))


class Balance(HTMLParser):
    """Tag balance + id collection for a fragment."""

    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.stack = []
        self.errors = []
        self.ids = []

    def handle_starttag(self, tag, attrs):
        for k, v in attrs:
            if k == "id" and v is not None:
                self.ids.append(v)
        if tag in VOID_TAGS:
            return
        self.stack.append((tag, self.getpos()))

    def handle_startendtag(self, tag, attrs):
        for k, v in attrs:
            if k == "id" and v is not None:
                self.ids.append(v)

    def handle_endtag(self, tag):
        if tag in VOID_TAGS:
            return
        if self.stack and self.stack[-1][0] == tag:
            self.stack.pop()
            return
        self.errors.append("</%s> at line %d closes nothing (open: %s)" % (
            tag, self.getpos()[0], ", ".join("%s@%d" % (t, p[0]) for t, p in self.stack[-3:]) or "-"))
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                return


def check_balance(fragment: str):
    p = Balance()
    p.feed(fragment)
    p.close()
    errs = list(p.errors)
    if p.stack:
        errs.append("unclosed: %s" % ", ".join("<%s> line %d" % (t, pos[0]) for t, pos in p.stack[-5:]))
    return errs, p.ids


# ---- technique cards ----------------------------------------------------------------------------
CARD_OPEN = re.compile(r"<article\b[^>]*>")


def tech_cards(fragment: str) -> list:
    """Every article.card.tech in a fragment: dicts {id, start, end, body, unit, k}. Cards never nest."""
    out = []
    for m in CARD_OPEN.finditer(fragment):
        tag = m.group(0)
        cm = re.search(r'\bclass\s*=\s*"([^"]*)"', tag)
        classes = cm.group(1).split() if cm else []
        if "card" not in classes or "tech" not in classes:
            continue
        im = re.search(r'\bid\s*=\s*"([^"]*)"', tag)
        cid = im.group(1) if im else ""
        close = fragment.find("</article>", m.end())
        if close < 0:
            close = len(fragment)
        body = fragment[m.end():close]
        um = re.fullmatch(r"t(\d+)-(\d+)", cid)
        out.append({"id": cid, "start": m.start(), "end": close + len("</article>"), "body": body,
                    "unit": int(um.group(1)) if um else None, "k": int(um.group(2)) if um else None})
    return out


def header_tags(body: str) -> list:
    """(class-suffix, text) for the spans of the card's first <div class="tags"> block. '' = plain tag."""
    m = re.search(r'<div class="tags">(.*?)</div>', body, re.S)
    if not m:
        return []
    return [(c.strip(), strip_tags(t)) for c, t in re.findall(r'<span class="tag((?: [a-z])?)">(.*?)</span>', m.group(1), re.S)]


# ---- Hebrew numerals for the transcripts lead ---------------------------------------------------
# construct forms used before a definite plural noun: "שלושת השיעורים", "אחד־עשר השיעורים"
HEB_COUNT = {1: "", 2: "שני", 3: "שלושת", 4: "ארבעת", 5: "חמשת", 6: "ששת", 7: "שבעת", 8: "שמונת", 9: "תשעת", 10: "עשרת",
             11: "אחד־עשר", 12: "שנים־עשר", 13: "שלושה־עשר", 14: "ארבעה־עשר", 15: "חמישה־עשר", 16: "שישה־עשר",
             17: "שבעה־עשר", 18: "שמונה־עשר", 19: "תשעה־עשר", 20: "עשרים"}
# every spelling we recognise when updating an existing lead
HEB_COUNT_WORDS = sorted({w for w in HEB_COUNT.values() if w} | {
    "שניים", "שלושה", "ארבעה", "חמישה", "שישה", "ששה", "שבעה", "שמונה", "תשעה", "עשרה",
    "אחד עשר", "שנים עשר", "שלושה עשר", "ארבעה עשר", "חמישה עשר", "שישה עשר", "שבעה עשר", "שמונה עשר", "תשעה עשר",
    "אחד-עשר", "שנים-עשר", "שלושה-עשר", "ארבעה-עשר", "חמישה-עשר", "שישה-עשר", "שבעה-עשר", "שמונה-עשר", "תשעה-עשר"},
    key=len, reverse=True)


def heb_count(n: int) -> str:
    """'אחד־עשר' for 11, '<bdi>23</bdi>' above twenty."""
    return HEB_COUNT.get(n) or "<bdi>%d</bdi>" % n
