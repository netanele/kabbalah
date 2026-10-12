#!/usr/bin/env python3
"""Assemble the page: build/skeleton.html + build/parts/NN-<name>.html -> out/<page>.

Usage:  python3 -I assemble.py --config <ws>/project.json

Each <!-- @@SECTION:name @@ --> in the skeleton is replaced by the part whose file name matches ^\\d+-<name>\\.html$
(so lesson-1 never matches lesson-10), with leading/trailing newlines stripped. A missing part leaves
<!-- missing: parts/NN-name.html --> in its place.

[?] wrapping (only when the skeleton's CSS defines .unc): every literal "[?]" in text nodes before the transcripts
section becomes <span class="unc" title="קריאה לא ודאית בתמלול">[?]</span>, or title "קריאה לא ודאית בטקסט" when
every unit is a text source (pdf/web/doc). Tags, attributes, comments, <style>,
<script>, text already inside a .unc span, and the transcripts section are never touched, so it is idempotent.

Checks: duplicate ids (ERROR), the full Name (ERROR), dangling #anchors, raw "&t=", missing sections, parts that
do not start with <section / end with </section> or whose id differs from the file name, inline styles,
<script>/<style>/<html> inside parts, several parts for one name, parts without a placeholder, ids that start
with t<digit> but are not t<n>-<k>. The page is always written; the exit code is 1 when there is an ERROR.
"""
import re
import sys
from collections import Counter
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import _common as C  # noqa: E402

UNC = '<span class="unc" title="%s">[?]</span>'
UNC_TITLE_TRANSCRIPT = "קריאה לא ודאית בתמלול"
UNC_TITLE_TEXT = "קריאה לא ודאית בטקסט"        # pages whose units are all text sources (pdf/web/doc)
TAG_SPLIT = re.compile(r"(<!--.*?-->|<[^>]*>)", re.S)
UNC_OPEN = re.compile(r'<span\b[^>]*\bclass="[^"]*\bunc\b')
UNC_CSS = re.compile(r"\.unc(?![\w-])")


def has_unc_css(skel: str) -> bool:
    return any(UNC_CSS.search(m.group(1)) for m in re.finditer(r"<style\b[^>]*>(.*?)</style\s*>", skel, re.S | re.I))


def wrap_unc(doc: str, transcripts_id: str, title: str = UNC_TITLE_TRANSCRIPT):
    """Wrap each literal [?] in text nodes before the transcripts section. Idempotent: text that already sits
    inside <span class="unc"> is left alone, and tags/attributes/comments/style/script are never touched."""
    cut = C.section_start(doc, transcripts_id)
    head, tail = (doc, "") if cut < 0 else (doc[:cut], doc[cut:])
    toks = TAG_SPLIT.split(head)            # even indices: text, odd indices: tags/comments
    n = 0
    prev_tag = ""
    raw = None                              # inside <style>/<script>: do not touch the text
    for i, tok in enumerate(toks):
        if i % 2 == 1:
            low = tok.lower()
            if raw:
                if low.startswith(raw):
                    raw = None
            elif low.startswith("<style"):
                raw = "</style"
            elif low.startswith("<script"):
                raw = "</script"
            if not low.startswith("<!--"):
                prev_tag = tok
            continue
        if raw or "[?]" not in tok or UNC_OPEN.match(prev_tag):
            continue
        n += tok.count("[?]")
        toks[i] = tok.replace("[?]", UNC % title)
    return "".join(toks) + tail, n


def main() -> int:
    ap = C.arg_parser(__doc__)
    args = ap.parse_args()
    cfg = C.Config(Path(args.config))
    if not cfg.skeleton.is_file():
        raise SystemExit("no skeleton: %s" % cfg.skeleton)
    skel = C.read_text(cfg.skeleton)
    report = []
    filled = []
    missing = []
    used = set()

    def sub(m):
        name = m.group(1)
        files = C.part_files(cfg.parts, name)
        if not files:
            missing.append(name)
            return "<!-- missing: parts/NN-%s.html -->" % name
        f = files[0]
        used.add(f.name)
        if len(files) > 1:
            report.append("warning: several parts for %s, using %s (others: %s)"
                          % (name, f.name, ", ".join(x.name for x in files[1:])))
        frag = C.read_text(f).strip("\n")
        if not re.match(r"\s*<section\b", frag):
            report.append("warning: %s does not start with <section" % f.name)
        else:
            om = re.match(r"""\s*<section\b[^>]*\bid\s*=\s*["']([^"']*)["']""", frag)
            if not om or om.group(1) != name:
                report.append("warning: %s opens <section id=%r>, expected %r"
                              % (f.name, om.group(1) if om else None, name))
        if not frag.rstrip().endswith("</section>"):
            report.append("warning: %s does not end with </section>" % f.name)
        for bad in sorted(set(re.findall(r"<(script|style|html|body|head)\b", frag, re.I))):
            report.append("warning: %s contains <%s" % (f.name, bad.lower()))
        n_style = len(re.findall(r'\sstyle="', frag))
        if n_style:
            report.append("warning: %s has %d inline style attribute(s)" % (f.name, n_style))
        filled.append((name, f.name, len(frag.encode("utf-8"))))
        return frag

    out = C.PLACEHOLDER.sub(sub, skel)
    orphans = [p.name for _, _, p in C.all_parts(cfg.parts) if p.name not in used]
    if orphans:
        report.append("warning: parts without a placeholder in the skeleton (not in the page): %s" % ", ".join(orphans))

    if has_unc_css(skel):
        all_text = bool(cfg.units) and all(C.is_text(u) for u in cfg.units)
        title = UNC_TITLE_TEXT if all_text else UNC_TITLE_TRANSCRIPT
        out, n_unc = wrap_unc(out, cfg.transcripts_section, title)
        unc_note = 'uncertain-reading markers [?] wrapped in .unc: %d (title "%s")' % (n_unc, title)
    else:
        unc_note = "[?] wrapping: off (the skeleton's CSS has no .unc)"

    # ---- sanity checks on the assembled document ----
    ids = re.findall(r'\sid="([^"]+)"', out)
    dup = [k for k, v in Counter(ids).items() if v > 1]
    if dup:
        report.append("ERROR: duplicate ids: %s" % ", ".join(sorted(dup)))
    idset = set(ids)
    hrefs = re.findall(r'href="#([^"]+)"', out)
    dangling = sorted({h for h in hrefs if h not in idset})
    if dangling:
        report.append("warning: %d dangling #anchors: %s" % (len(dangling), ", ".join(dangling[:30]) + (" …" if len(dangling) > 30 else "")))
    raw_t = out.count("&t=")
    if raw_t:
        report.append("warning: %d raw '&t=' in URLs (should be '&amp;t=')" % raw_t)
    tech_ids = sorted((i for i in ids if re.fullmatch(r"t\d+-\d+", i)),
                      key=lambda x: tuple(int(v) for v in x[1:].split("-")))
    names_full = C.NAME_ANY.findall(out)
    if names_full:
        report.append("ERROR: the full Name appears %d time(s) in the page" % len(names_full))
    bad_tech = [i for i in ids if re.match(r"t\d", i) and not re.fullmatch(r"t\d+-\d+|tr-\d+", i)]
    if bad_tech:
        report.append("warning: ids starting with t<digit> that do not follow t<n>-<k>: %s" % ", ".join(sorted(bad_tech)[:20]))

    C.write_text(cfg.out, out)

    print("sections filled (%d):" % len(filled))
    for name, fname, size in filled:
        print("  %-16s <- %-30s %8.1f KB" % (name, fname, size / 1024))
    print("sections missing (%d): %s" % (len(missing), ", ".join(missing) if missing else "-"))
    print("technique cards (t<n>-<k>): %d" % len(tech_ids))
    print(unc_note)
    for line in report:
        print(line)
    print("wrote %s  (%.1f KB)" % (cfg.out, len(out.encode("utf-8")) / 1024))
    return 1 if any(r.startswith("ERROR") for r in report) else 0


if __name__ == "__main__":
    sys.exit(main())
