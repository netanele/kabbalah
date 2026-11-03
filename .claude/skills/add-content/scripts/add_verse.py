#!/usr/bin/env python3
"""Add verses to pesukim-meyuchadim.html from Sefaria's text, and update index.html and README.md.

Run: python3 -I add_verse.py Psalms.86.11 [Deuteronomy.10.12 ...] [--label "..."] [--repo DIR] [--dry-run]
A ref is a Sefaria ref (Book.Chapter.Verse). --label applies to a single ref only.
Nothing is written unless every ref succeeds. See ../references/verses.md.
"""
import argparse
import html
import json
import pathlib
import re
import sys
import urllib.parse
import urllib.request

PAGE = 'pesukim-meyuchadim.html'
NAME = 'יהוה'  # written in full, as plain text: js/sefirot-methods.js colors its letters on every page
PREFIX = '[ובלכמהש]*'
RE_NAME = re.compile(f'^{PREFIX}יהוה$')
RE_ELOHIM = re.compile(f'^{PREFIX}אלה(ים|י|יך|יכם|יכן|ינו|יו|יה|יהם|יהן)$')
# Other names depend on the sense of the word, so a person decides: the script only reports them.
ASK = {'אדני': 'מלכות', 'אל': 'חסד', 'יה': 'חכמה', 'אהיה': 'כתר', 'צבאות': 'נצח/הוד', 'שדי': '?'}
RAB_OPEN, RAB_CLOSE = '', ''  # stand-ins for <big> while the text is split into words
RE_REF = re.compile(r'[A-Za-z_]+\.\d+\.\d+')
RE_VERSE = re.compile(f'[֑-ׇא-ת {RAB_OPEN}{RAB_CLOSE}]+')  # letters, marks, maqaf, paseq, sof pasuk
RE_HE_REF = re.compile('[א-ת׳״ :]+')


def cons(word):
    return ''.join(c for c in word if 'א' <= c <= 'ת')


def named(sef, text):
    return f'<span class="nm" data-name-sef="{sef}">{text}</span>'


def fetch(ref):
    url = f'https://www.sefaria.org/api/v3/texts/{urllib.parse.quote(ref)}?version=hebrew'
    data = json.load(urllib.request.urlopen(url, timeout=30))
    text = data['versions'][0]['text']
    if not isinstance(text, str):
        sys.exit(f'{ref}: not a single verse')
    text = re.sub(r'<i class="footnote.*?</i>', '', text, flags=re.S)
    text = text.replace('<big>', RAB_OPEN).replace('</big>', RAB_CLOSE)
    text = re.sub(r'<[^>]+>', '', text)
    text = text.replace('&thinsp;', ' ').replace('&nbsp;', ' ')
    text, he_ref = re.sub(r'\s+', ' ', text).strip(), data['heRef']
    # The API's reply goes into a published page, so anything but verse text stops the run.
    if not RE_VERSE.fullmatch(text):
        sys.exit(f'{ref}: unexpected characters in the verse text: {text!r}')
    if not RE_HE_REF.fullmatch(he_ref):
        sys.exit(f'{ref}: unexpected characters in the source name: {he_ref!r}')
    return text, he_ref


def source_he(he_ref):
    """'תהילים מ״ו:י״א' -> 'תהילים מו, יא'."""
    return he_ref.replace('״', '').replace('׳', '').replace(':', ', ')


def rab(text):
    return text.replace(RAB_OPEN, '<span class="rab">').replace(RAB_CLOSE, '</span>')


def stam_word(part):
    """The consonants of a word, keeping the marks of large letters."""
    keep = ''.join(c for c in part if 'א' <= c <= 'ת' or c in (RAB_OPEN, RAB_CLOSE))
    return rab(keep)


def split_prefix(part):
    """Split a word before its name: 'לַ' + the Name. Returns the prefix with its vowels."""
    for i, c in enumerate(part):
        if c in 'יא' and RE_NAME.match(cons(part[i:])) or (c == 'א' and RE_ELOHIM.match(cons(part[i:]))):
            return part[:i], part[i:]
    return '', part


def build(text):
    """Returns (ketav-ashurit line, pointed line, words a person must decide on)."""
    stam, pointed, ask = [], [], []
    for token in text.split(' '):
        if token == '׀':  # the paseq stays in the pointed line; a scroll has no such mark
            pointed.append(token)
            continue
        parts = []
        for part in token.split('־'):
            c = cons(part)
            if RE_NAME.match(c):
                before, name = split_prefix(part)
                parts.append(before + name)  # keeps Sefaria's pointing
                stam.append(cons(before) + NAME)
            elif RE_ELOHIM.match(c):
                end = '׃' if part.endswith('׃') else ''
                parts.append(named('gevura', part.rstrip('׃')) + end)
                stam.append(named('gevura', c))
                ask.append(f'{c}: colored as גבורה; if it may not be a holy name here, ask the user')
            else:
                if c in ASK:
                    ask.append(f'{c}: not colored; expected color if a holy name: {ASK[c]}. If unclear, ask the user')
                parts.append(rab(part))
                stam.append(stam_word(part))
        pointed.append('־'.join(parts))
    return ' '.join(stam), ' '.join(pointed), ask


def default_label(stam, source):
    words = [re.sub(r'<[^>]+>', '', w) for w in re.split(r' (?![^<]*>)', stam)[:3]]
    return ' '.join(words) + f' ({source})'


def sub_once(text, pattern, repl, where):
    new, n = re.subn(pattern, repl, text)
    if n != 1:
        sys.exit(f'{where}: expected one match of {pattern!r}, found {n}')
    return new


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('refs', nargs='+')
    ap.add_argument('--label', help='home-page table-of-contents label (single ref only)')
    ap.add_argument('--repo', default=str(pathlib.Path(__file__).resolve().parents[4]))
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()
    if args.label and len(args.refs) > 1:
        sys.exit('--label works with one ref')

    repo = pathlib.Path(args.repo)
    page = (repo / PAGE).read_text(encoding='utf-8')
    index = (repo / 'index.html').read_text(encoding='utf-8')
    readme = (repo / 'README.md').read_text(encoding='utf-8')

    numbers = [int(n) for n in re.findall(r'<article class="pasuk" id="p(\d+)">', page)]
    last = max(numbers)
    articles, toc = '', ''
    for offset, ref in enumerate(args.refs, 1):
        if not RE_REF.fullmatch(ref):
            sys.exit(f'{ref}: expected a ref like Psalms.86.11 or I_Samuel.2.2')
        if f'/{ref}?' in page:
            sys.exit(f'{ref} is already on the page')
        text, he_ref = fetch(ref)
        stam, pointed, ask = build(text)
        n, source = last + offset, source_he(he_ref)
        articles += (
            f'  <article class="pasuk" id="p{n}">\n'
            f'    <blockquote>{stam}</blockquote>\n'
            f'    <p class="nikud">{pointed}</p>\n'
            f'    <p class="src"><b>מקור:</b> <a href="https://www.sefaria.org/{ref}?lang=he" target="_blank" rel="noopener">{source}</a></p>\n'
            f'  </article>\n\n'
        )
        label = html.escape(args.label, quote=False) if args.label else default_label(stam, source)
        toc += f'      <li><a href="{PAGE}#p{n}">{label}</a></li>\n'
        print(f'p{n} {source} | {re.sub(r"<[^>]+>", "", stam)}')
        for line in ask:
            print(f'  color: {line}')

    old, new = len(numbers), len(numbers) + len(args.refs)
    page = page.replace('</section>\n</main>', articles + '</section>\n</main>', 1)
    page = sub_once(page, f'<div class="dates">{old} פסוקים</div>', f'<div class="dates">{new} פסוקים</div>', PAGE)
    index = sub_once(index, f'<span class="d">{old} פסוקים</span>', f'<span class="d">{new} פסוקים</span>', 'index.html')
    index = sub_once(index, f'<span class="tag c">{old} פסוקים</span>', f'<span class="tag c">{new} פסוקים</span>', 'index.html')
    index = sub_once(index, rf'(<li><a href="{PAGE}#p{last}">[^\n]*\n)', lambda m: m.group(1) + toc, 'index.html')
    readme = sub_once(readme, f'פסוקים מיוחדים: {old} פסוקים', f'פסוקים מיוחדים: {new} פסוקים', 'README.md')

    if args.dry_run:
        print('dry run: nothing saved')
        return
    (repo / PAGE).write_text(page, encoding='utf-8')
    (repo / 'index.html').write_text(index, encoding='utf-8')
    (repo / 'README.md').write_text(readme, encoding='utf-8')
    print(f'saved: {new} verses')


if __name__ == '__main__':
    main()
