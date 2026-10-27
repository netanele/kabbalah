# -*- coding: utf-8 -*-
"""Build js/seder-halimud-data.js and js/books.js from stages.py (the hand-written path), video-assign.json (from curate.py), videos.json (the channel dump) and drive-books.json + book-drive-map.json (the Drive library).
Run from anywhere: python3 -I tools/seder-halimud/build_data.py"""
import json, re, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import stages

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
VID = json.load(open(f'{HERE}/videos.json', encoding='utf-8'))
V = {v['id']: v for v in VID['videos']}
A = json.load(open(f'{HERE}/video-assign.json', encoding='utf-8'))
BL = {b['title']: b for b in A['blocks']}

# pages in the library: for "already in the library" marks
LIB = {}
for f in os.listdir(REPO):
    if f.endswith('.html'):
        s = open(f'{REPO}/{f}', encoding='utf-8').read()
        for m in re.finditer(r'youtube\.com/watch\?v=([\w-]{11})', s):
            LIB.setdefault(m.group(1), set()).add(f)
# only count pages that have the video as a transcript/lesson (many links) – threshold 20 links
LIBP = {}
for f in os.listdir(REPO):
    if f.endswith('.html'):
        s = open(f'{REPO}/{f}', encoding='utf-8').read()
        from collections import Counter
        c = Counter(re.findall(r'youtube\.com/watch\?v=([\w-]{11})', s))
        for vid, n in c.items():
            if n >= 20: LIBP.setdefault(vid, []).append(f)

PAGE_TITLES = {
 'abulafia.html': 'כתבי רבי אברהם אבולעפיה', 'meditation.html': 'שיטות המדיטציה היהודית', 'sages-timeline.html': 'ציר הזמן של חכמי ישראל',
 'yosef-shani-aliyat-neshama.html': 'עליית נשמה בשיטת הרב יוסף שני', 'turgeman-practical-kabbalah.html': 'יסודות בקבלה מעשית',
 'turgeman-ari-rashash.html': 'קבלה מעשית וקבלת האר"י והרש"ש', 'turgeman-moreh-haprishut.html': 'מורה הפרישות', 'darkey-hasaga.html': 'דרכי השגה',
 'yurovitz-darkey-hahasaga.html': 'שיעורי דרכי השגה', 'yichudim.html': 'יסודות הייחודים', 'tzayach-shir-hasefirot.html': 'שיר הספירות בצבעים',
 'otzar-hayichudim.html': 'אוצר הייחודים', 'sefirot-colors.html': 'שיטות בצבעי הספירות',
}

# drive inventory
DRIVE = {}
try:
    inv = json.load(open(f'{HERE}/drive-books.json', encoding='utf-8'))
    for it in inv:
        if it.get('mime') != 'folder': DRIVE[it['id']] = it
except Exception as e:
    print('no drive inventory yet:', e)
try:
    BOOK_DRIVE = json.load(open(f'{HERE}/book-drive-map.json', encoding='utf-8'))  # key -> [file ids]
except Exception:
    BOOK_DRIVE = {}

def hms(sec):
    sec = int(sec or 0); h, m, s = sec // 3600, sec % 3600 // 60, sec % 60
    return f'{h}:{m:02d}:{s:02d}' if h else f'{m}:{s:02d}'
def date_he(d):
    return f'{int(d[6:8])}.{int(d[4:6])}.{d[:4]}' if d else ''

out_stages = []
unit_of_video = {}
books_used = {}
for st in stages.STAGES:
    units = []
    k = 0
    hk = 0
    def add(u):
        global k, hk
        if u['type'] == 'head':
            hk += 1; u['no'] = f"{st['n']}.h{hk}"; units.append(u); return u
        k += 1; u['no'] = f"{st['n']}.{k}"; units.append(u); return u
    for u in st['units']:
        t = u['type']
        if t == 'page':
            f = u['href'].split('#')[0]
            add(dict(type='page', title=u['title'], href=u['href'], page=PAGE_TITLES.get(f, u.get('page') or ''), why=u['why'], core=True))
        elif t == 'practice':
            add(dict(type='practice', title=u['title'], why=u['why'], dur=u['dur'], core=True))
        elif t == 'book':
            b = stages.BOOKS[u['key']]
            ids = BOOK_DRIVE.get(u['key'], [])
            books_used.setdefault(u['key'], []).append(st['n'])
            add(dict(type='book', key=u['key'], title=b['title'], author=b['author'], parts=u['parts'], why=u['why'], core=True))
        elif t == 'videos':
            b = BL[u['block']]
            core = b['core']
            add(dict(type='head', title=u['block'], why=u['why'] or b.get('note', ''), core=core, count=len(b['ids'])))
            for vid in b['ids']:
                v = V[vid]; a = A['assign'][vid]
                uu = add(dict(type='video', id=vid, title=v['title'].strip(), dur=hms(v['dur']), secs=v['dur'], date=date_he(v['date']), core=core,
                              live='live' in v['src'] and 'upload' not in v['src'], short='short' in v['src'], old='old' in v['src'] and 'upload' not in v['src'] and 'live' not in v['src'],
                              lib=LIBP.get(vid, []), alt=a.get('alt', [])))
                unit_of_video[vid] = uu['no']
                for o in a.get('alt', []): unit_of_video[o] = uu['no']
        elif t == 'note':
            add(dict(type='note', text=u['text'], core=True))
    out_stages.append(dict(n=st['n'], key=st['key'], title=st['title'], level=st['level'], goal=st['goal'], why=st['why'], units=units, gate=st['gate'], dangers=st['dangers']))

# books table -> js/books.js (the single place for Drive file ids)
EXTRA = {  # files outside the inventory (Desktop sync folder), known from the pages
 '1A62M3Al4MvuyAyQjDOj7I8fktnAZAMis': dict(title='DarkeyHasagaHaravYorovits.pdf', path='(Desktop)', ext='pdf', sizeKB=276),
 '1dtNOalS-hmAgAoKfJekX-DG1jQGzRznP': dict(title='שמוש-תהילים.pdf', path='(Desktop)', ext='pdf', sizeKB=549),
 '1ZQ0anzXeu-OgMod75o0cRtQUB95kmw6t': dict(title='פרקי-היכלות.pdf', path='(Desktop)', ext='pdf', sizeKB=1355),
 '1L33KhmIu6MoOz2RsxEKU3VBEGQi-eGla': dict(title='פרקי-היכלות-דפןס-ישן.pdf', path='(Desktop)', ext='pdf', sizeKB=4949),
}
books = {}
missing_ids = []
for key, b in stages.BOOKS.items():
    ids = BOOK_DRIVE.get(key, [])
    files = []
    for i in ids:
        d = DRIVE.get(i) or EXTRA.get(i)
        if not d: missing_ids.append((key, i)); continue
        ext = (d.get('ext') or '').lower() or ('html' if 'html' in d.get('mime', '') else '')
        files.append(dict(id=i, title=d['title'], path=d.get('path', ''), ext=ext, sizeKB=d.get('sizeKB')))
    books[key] = dict(title=b['title'], author=b['author'], note=b['note'], find=b['find'], drive=files, stages=sorted(set(books_used.get(key, []))))
assert not missing_ids, missing_ids
bjs = ('/* המקום האחד של הספרים: כותר, מחבר, ואיפה הקובץ בתיקיית הספרים בדרייב (Torah/Books, '
       'https://drive.google.com/drive/folders/1xseNntc6xbkkVhNdppPMGO_rAaE9Q_0N). קובץ PDF נפתח לקריאה בתוך הדף '
       '(drive.google.com/file/d/<id>/preview); קובצי html/djvu נפתחים בדרייב בלבד. ספר בלי drive: למצוא לפי find ולהוסיף לתיקייה. '
       'נבנה מ-tools/seder-halimud/build_data.py. */\n'
       'window.BOOKS = ' + json.dumps(books, ensure_ascii=False, indent=0) + ';\n')
open(f'{REPO}/js/books.js', 'w', encoding='utf-8').write(bjs)
print('books.js:', len(books), 'books,', sum(1 for b in books.values() if b['drive']), 'with drive files')

# catalog by series
series = []
for pid, title in VID['playlists'].items():
    ids = [i for n, i in sorted((n, v['id']) for v in VID['videos'] for p, n in v['pl'] if p == pid)]
    series.append(dict(id=pid, title=title, videos=[dict(id=i, title=V[i]['title'].strip(), dur=hms(V[i]['dur']), unit=unit_of_video.get(i, '')) for i in ids]))
rest = [v for v in VID['videos'] if not v['pl']]
catalog_rest = [dict(id=v['id'], title=v['title'].strip(), dur=hms(v['dur']), date=date_he(v['date']), unit=unit_of_video.get(v['id'], ''), src=v['src']) for v in sorted(rest, key=lambda v: (v['date'] or '9', v['title']))]

missing = [i for i in V if i not in unit_of_video]
assert not missing, missing[:5]
nvid = sum(1 for s in out_stages for u in s['units'] if u['type'] == 'video')
tot_secs = sum(u['secs'] for s in out_stages for u in s['units'] if u['type'] == 'video')
stats = dict(videos=nvid, videos_with_alt=len(unit_of_video), hours=round(tot_secs / 3600), units=sum(1 for s in out_stages for u in s['units'] if u['type'] != 'head'), blocks=sum(1 for s in out_stages for u in s['units'] if u['type'] == 'head'),
             pages=sum(1 for s in out_stages for u in s['units'] if u['type'] == 'page'), books=sum(1 for s in out_stages for u in s['units'] if u['type'] == 'book'),
             practices=sum(1 for s in out_stages for u in s['units'] if u['type'] == 'practice'), gates=len(out_stages))
data = dict(built='27.10.2026', stats=stats, stages=out_stages, series=series, rest=catalog_rest)
js = 'window.SEDER = ' + json.dumps(data, ensure_ascii=False, separators=(',', ':')) + ';\n'
open(f'{REPO}/js/seder-halimud-data.js', 'w', encoding='utf-8').write('/* נבנה אוטומטית מ-tools/seder-halimud/build_data.py: המסלול, היחידות, הספרים והקטלוג. לא לערוך ידנית. */\n' + js)
print(stats); print('size', len(js))
for s in out_stages:
    vids = [u for u in s['units'] if u['type'] == 'video']
    print(s['n'], s['title'], 'units', len(s['units']), 'videos', len(vids), 'core', sum(1 for u in vids if u['core']), 'hours', round(sum(u['secs'] for u in vids) / 3600, 1))
