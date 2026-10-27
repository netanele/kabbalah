# -*- coding: utf-8 -*-
"""Assign every Torgeman video to a stage / block / order. Output: video-assign.json"""
import json, re

import os
HERE = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.path.join(HERE, 'videos.json'), encoding='utf-8'))
V = {v['id']: v for v in D['videos']}
PL = {}
for v in D['videos']:
    for pid, n in v['pl']:
        PL.setdefault(pid, []).append((n, v['id']))
for pid in PL: PL[pid].sort()
def plids(pid): return [i for n, i in PL[pid]]
P = {t: pid for pid, t in D['playlists'].items()}
def pl(prefix):
    for t, pid in P.items():
        if t.startswith(prefix): return pid
    raise SystemExit('no playlist ' + prefix)
def num(i, pat=r'(\d+)'):
    m = re.search(pat, V[i]['title']); return int(m.group(1)) if m else 0
def bynum(ids, pat=r'(\d+)'): return sorted(ids, key=lambda i: num(i, pat))

assign, blocks = {}, []
def block(stage, core, title, ids, note=''):
    out = []
    for i in ids:
        if not i: continue
        if i not in V: raise SystemExit(f'unknown id {i} in "{title}"')
        if i in assign:
            print(f'  skip {i} {V[i]["title"][:40]} in "{title}" (already in {assign[i]["block"]})'); continue
        assign[i] = dict(stage=stage, core=core, block=title); out.append(i)
    blocks.append(dict(stage=stage, core=core, title=title, ids=out, note=note))
def alt(main, other):
    assign[other] = dict(stage=assign[main]['stage'], core=assign[main]['core'], block=assign[main]['block'], alt_of=main)
    assign[main].setdefault('alt', []).append(other)

# ================= stage 0 =================
block(0, True, 'אזהרה ראשונה', ['0YUplGYoPF0', 'CVbctA6bTp0'])
block(0, False, 'הלכה: דוגמאות משיעורי "למען תזכרו" (אבן העזר)', ['82UGD5U2MUA', 'SAdED23KTcs'])
# ================= stage 1 =================
block(1, True, 'מורה הפרישות והשקטת הנפש', plids(pl('מורה הפרישות')) + ['6hP22nn2ZSs', 'AG4UsrxVPJ4', '2cL0drPzsDY', 'WO9hhHnRynk', 'ZFVQR4MZgmI'])
block(1, True, 'טהרה: מקווה בבית ואכילת חולין בטהרה', ['Iuo65VSvhPM', 'dNTpADuG6gs', 'bKRyenyLDak', 'gMH-B4iv2uY', 'QaM8K6RKkrE'])
block(1, True, 'פרישות ונזירות בזמן הזה', ['l4Kc3rbW5lo', 'bZLs72swmDg'])
block(1, True, 'תיקונים: גלגולי שלג, תיקון הברית, המטבעות והצדקה', ['3pTab3LKz4g', 'BE3YYBijE8k', 'XwNaPWdujDU', 'M0Zkrl2WXnU', 'Jd1dXlyR2Ts', 'TPtJ2AsNFOg', 'mSRWuJ5NGGI', 'y7sMnRH4wfc', 'vWP6WoWSpmo', 'JOyP1ptIFF4', 'DhfjUWvlh88', 'U3OREC2pp7E', 'vCKTrzgPyQU'])
block(1, False, 'חיזוקים קצרים', ['6jsB-XJt1kU', '4URLrCpZsdo', 'fRDv51VirZM', 'Mk91krFKhj0', 'WkeOBx4sMvM', 'MSkZClGcJsQ', 'XGhR5rGd7Pk', 'gs0I8niChGU', 't8m_ennbMIw', 'lxa4UiOms3g', '4p_Qdvd5Kls', 'wX9mwYocmyA', 'gw0oqpSTVPk', 'ozH9-b-iy2E', '_7-oVVaJNCA', 'I4zXQVB1X4k', '2ZkMiKwyJBM', '7QpyEVUo21E', 'ohldBQIvVPA', 'VT-uI5ptRSg', '8dmTzeSI7d4', 'JHmv5Fk6rsY', '4NKrfRbZQVg', '8VB8VmcE6gE', 'CRHp_F-BprI', 'tAwvjzNBAvo', 'qJlW_dnOz_w'])
# ================= stage 2 =================
block(2, True, 'פתיחה לקבלה העיונית ולעץ חיים', ['UYlPMZfi7Hs', 'TEElqy3z_fc', 'PXrAXYGPosA', 'XkWfsSuW6vg', 'eOPG8uI9bYQ', 'mOhaD3qZdoo'])
block(2, True, 'קבלת הראשונים', ['9glfZ9v5tOA', 'i9FK-9eZALw', 'Ru74V0iSgjE', 'RmlGSmgfdr4'])
block(2, True, 'העולמות, המלאכים, הגלגלים והמזלות', ['Dz0yTA12yzg', 'xhfOfwllKXs', 'ojsrTRFdI6E'])
block(2, False, 'סוד הפרשה והמועדים', ['-ygdclYaolQ', '_uoBF8tEJ3o', 'elrP8Sg7YyA', 'mnW_zPyMelo', 'EGOxXFmuDac', 'P6koW-V7yuI', 'oM8R-_nIQsI', 'VGmmjAqLsGg', 'bt0PBqnS7jM', 'vm0Cc7ZWVt4', 'Zr81P9JIUIg', 'K7cN3HcfKY0', '4objNLLANuQ', '8YCRQ8rcaWc', 'ZqHXGQDQCBk', 'wKQXmXmdzYM', '2dI4Zc6b8F4', 'FJY0aTzlC5Y', 'wHRFDRs8caA', '7EHrPxDyhCA', 'pEzoVayUtjg', 'EbzqxAgMFmk', 'oCn7PkYnhPs', 'ZAD3BJkG-LE', 'Z-bVXoencrc', 'ALVrpzDb-SA', 'Ib2oeDL_vxk', 't-_U5MFEgxs', 'yqGt3TyjVl4', '2uHPGfEzm1c', 'EY6xNbh0gsY', 'ZjvUthpAFmE', 'yyBrI-pWdvY', '3rXyrxLFdK0', 'aIeXz2whX8g', 'GXPZxzb0R24', 'nSXLfevvER0', 'DL2Ro6yc2zY', 'sekmnbmPahY', 'SGyU7YFHuCM', '__U3HZiaAlA', 'wFcit931Z7E', 'FbWvNkRZyW4', '3DKsrfQpjAg', '8uSqSAq3e4E', 'mD9TjRk8a-s', 'MMJ7imZHjhg', 'tcuu_PivF2k'])
# ================= stage 3 =================
block(3, True, 'עליות והשגות: הרצאות בפלורידה', ['mm5-H7A6uN4', 'Ecy_XprbNf8'])
# ================= stage 4 =================
block(4, True, 'רבי יוסף צייאח: הקבלה הנבואית ושיר הספירות', ['Q1XWx-Tw-D4', 'hnl0kJv8ZwM'])
alt('hnl0kJv8ZwM', 'kBHaOHImxqA')
block(4, True, 'אוצרות חיים ועץ חיים', ['mc8grR-zNlw', 'liJdgftSTMw', '5gs4vKrahrQ', 'gqVPhKT_XWw', '4pE132kC_ns', 'FoVklW_swoc', 'Z2XtZp9-eE0', '32JUsrKuvto', 'NwrRFyJ2D3M', '_joCQej06Lk', 'cU2hNnA6Rhs', '2YyVo3Mg66U', 'CrzR05ErBTM', 'GvntJzb5GkE', 'PadYKv1IK_Y', 'tKSitCSqKWI'])
alt('32JUsrKuvto', 'CEYAFtFvW4g')
block(4, True, 'משנת חסידים', ['39ASkRZ1dMQ', 'EPHszoCKyTY', '0Bt4MTl_sos'])
block(4, True, 'שער הגלגולים', plids(pl('שער הגלגולים')))
block(4, True, 'הקדמת רחובות הנהר לרש"ש', plids(pl('הקדמת רחובות הנהר')) + ['CA0GgOvrR1Q', 'E5ghhUolHcE', '1DGayUj-o7U'])
block(4, True, 'נהר שלום ותורת חכם', ['x70FkdwzhfQ', '7QiqDTbxB8M', 'fw9_oEyESAw', 'd9-mRPI6-Co', '9DJsF2SSmUc', 'UNaa1qiM6mY', 'LSIhok2JxuQ'])
block(4, True, 'כוונות הרש"ש הלכה למעשה', ['fA07AMm3IAo', 'U5ME8KKlij4', '6ASRXwPSwdM', 'j0_c8r1gnTQ', 'BOa9B2jEBNs', '2PAwgfVUQIU', 'ayUBYo7N07o', 'Foc_d5KXrQs'])
block(4, False, 'באנגלית: סידור הרש"ש, הרמ"ק', ['yuVNLjo-Gag', 'ST9Cc90Z5PU', 'qtC8a4PWZkU', 'r4pvvQBY1Zw', 'eM6_NnMgMrA'])
# ================= stage 5 =================
block(5, True, 'חכמת הצירוף: פתיחה', ['J4WDLWMgeoc', 'jnAbC_SWzrM', '5sAzjGSeXeg', '5PzGn1GK_Xk', 'pbuCZpk0-wA', 'ogbN11gIUs8', 'HuC4nyJvVVA'])
sm = plids(pl('ספר המלכות'))
sm_sorted = bynum(sm, r'ספר ה?מלכות\s*(\d+)')
# lessons 7-10 are titled by chapter: keep playlist order for those without a leading number
def smkey(i):
    t = V[i]['title']; m = re.search(r'ספר המלכות (\d+)', t)
    if m: return int(m.group(1))
    m2 = re.search(r'(\d+)\s*$', t.strip('. '))
    return int(m2.group(1)) if m2 else 10.5
sm_order = sorted(sm, key=smkey)
pos = sm_order.index('pFeJ0bgW1Lc') + 1 if 'pFeJ0bgW1Lc' in sm_order else 10
sm_order = sm_order[:pos] + ['2IXTURow_Go'] + sm_order[pos:]
sm_order = sorted(sm_order + ['ql1JF38IxV0', '5zpOCT6Ce0E'], key=lambda i: (smkey(i) if i != '2IXTURow_Go' else 10.7))
block(5, True, 'ספר המלכות – חכמת הצירוף של מקובלי דרעא', sm_order)
tz = [i for i in plids(pl('הרב ציאח')) if i not in ('Q1XWx-Tw-D4', 'hnl0kJv8ZwM')]
tz_extra = [i for i in ['O4DSWw33emw', 'EUQSDkIGSws', 'GhdiGdzrYfk', 'z0nI_JnQvlc', 't4xl7oDvXyM', 'U6rlPfck9aQ', 'S3oGeYYYoFs'] if i not in tz]
def tzk(i):
    t = V[i]['title']
    m = re.search(r'שארית יוסף(?: אבן ציאח)?\s*(\d+)', t)
    if m: return (0, int(m.group(1)))
    m = re.search(r'שער\s*([א-ת\'"]+)', t)
    heb = {'ה':5,'ו':6,'ז':7,'ח':8,'ט':9,'י':10,'יא':11,'יב':12,'יג':13,'יד':14,'טו':15,'טז':16,'יז':17,'יח':18,'יט':19,'כ':20,'כא':21,'כב':22,'כד':24}
    if m:
        k = re.sub(r'[\'"]', '', m.group(1))
        if k in heb: return (1, heb[k])
    m = re.search(r'פרק\s*([א-ת\'"]+)', t)
    if m:
        k = re.sub(r'[\'"]', '', m.group(1))
        if k in heb: return (1, heb[k])
    return (2, 0)
block(5, True, 'רבי יוסף צייאח: שארית יוסף, אבן השהם וצרור החיים', sorted(tz + tz_extra, key=tzk))
block(5, True, 'בעלי השם, המעיינות והאבנים', ['YIQECNc8jGs', 'wveUOi2XvNU'])
# ================= stage 6 =================
block(6, True, 'חלומות, חזיונות ושאלת חלום', ['4ZSDHaEF1HE'] + plids(pl('חזיונות וחלומות')) + ['3qS0wJsY7CQ', '77Kf4ZZMekU', 'e6cox4WKs0U', 'PeyoEDpqBJg', 'CkeTJ560c5E', 'SmrxBorvkdI', 'Ib6MyZd95Ec', 'pYPngIIlwvM'])
block(6, True, 'עליית נשמה, גן עדן ונשמות', ['WUAuxsiGjoU', 'iI-aD7FsOQg', 'YjPJceng3lI', 'oviQzY8QfO8', 'WtAuAnMlk14', '-VoHOn9Zzv0'])
block(6, True, 'רוחות, דיבוקים ונפשות', plids(pl('רוחות בני אדם')) + ['efzgqclY-os'])
# ================= stage 7 =================
km = plids(pl('קבלה מעשית'))
gor = {'32zRvZ5GtSY', 'hKpqTjHZHB8', '_dtbVG8EYHA', 'WUAuxsiGjoU'}
block(7, True, 'יסודות בקבלה מעשית (הסדרה)', [i for i in km if i not in gor and i not in ('V3w_7hBjYME', 'vABsmUcjS9A', 'CVbctA6bTp0')])
block(7, True, 'הקבלה המעשית והאר"י, הרש"ש והתלמוד', ['zjUmhbRA1h8', '2Oyhk77JVR4', '8JReLLt_7QM', 'vABsmUcjS9A', 'Zkl-jYiN-mE', 'jWhTA8IRyXQ', '_RSehJbDt9I', 'dgfuoCPjSUM'])
block(7, True, 'דרישות מלאכים לרמ"ק', [i for i in plids(pl('דרישות מלאכים'))] + ['avTe38bPtbc', 'H5SxJigKqOM'])
bm = bynum(['J9MPHAPQtnA', 'ZPK3mbvwWsk', 'yIeZfYvGPdQ', 'gw0QCdzivjc', 'wYOz6rfIUYg', 'PpmoK9rDznA', '8W3eAP8bf2c', 'jfvOzxDX2jk', 'ZZqDD_Lj8Ps', 'LsFfna6M3w4', 'jAcQBQgq1SM', '3zpbiQB99mo', 'L2RYnWXIfrQ'], r'מנוחה\s*(\d+)')
block(7, True, 'ברית מנוחה', bm + ['idlmoahsOys'])
block(7, True, 'שימושי שרים ושרי השמן', ['t3gSqDlpj_w', '2KwxqY4m38s', 'Dp0XLm_Qpmw', 'DUQB9X8dfxY', '3qmuPhDH-Ws'])
block(7, True, 'שורשי הסודות לרמ"ז, שושן יסוד העולם ומראה הילדים', ['V3w_7hBjYME', '64wZE0VBPJU', 'Tp34AGlPdDk', 'chAPHu1ShcE', 'UogyyWIPX0o', 'OZkvawG81EY'])
rp = bynum(['L5vkADXtlBE', 'dc5AHoK3TRE', 'aagRPlZvwjM', '8yfQpm83XWk', '1dgY-kkfdMw', 'vDfEMRkGAc8', 'LkfdxSxloQo', 'GXLN6VBFgew', 'FpGF_qYAlPM', 'k_tPnZfQFP0', 'bBGi-HfO6Tc', 'nV-8dNYB7Ts', 'yNvLxE16aIU'], r'(\d+)\D*$')
# order by lesson number appearing anywhere
def rpk(i):
    t = V[i]['title']; m = re.search(r'רב פעלים\s*(\d+)', t)
    if m: return int(m.group(1))
    m = re.search(r'(\d+)', t); return int(m.group(1)) if m else 0
rp = sorted(set(rp), key=rpk)
block(7, True, 'רב פעלים: כשפים, רוחות ורפואות (ר\' מרדכי מלכא)', rp + ['GCjbhtx9Cf4'])
ms = bynum(['ib1S184BOzA', 'eKSyFsqG_CY', 'Ejnb8cMlE3g', 'Ta1ouonacgo', '9q10WINuieI', 'A-T0hBBINKQ', 'CGkJIXx2oRs', 'az1hA6VacNc', 'TKwxux-Xr2M', 'Cn49uveIpLM', 'MXFOpHVW58w', 'Y_7yxEGc8gA', 'QBheDbWzw7Y'], r'השביעי\s*(\d+)')
block(7, True, 'המעיין השביעי', ms)
block(7, True, 'קמיעות, חותמות ושמות', ['L8nbDMayao8', 'i2MfDd8axEw', 'srvAxFpyu4o', '8O3yzUA8zxc', '_gppRyfk70E', 'tx4ndBy0rwQ', 'IaGQIGIpnco', '-KTzOYf58F8', 'mx5ihL0QgDg'])
block(7, True, 'אבני בורלא: קמיעות וקשירות', ['9dwL7Vuw-gE', '7VMWx-p9b_c'])
block(7, False, 'נר יוסף מערבי והאלכימאי האחרון', plids(pl('רבי יוסף מערבי')) + ['gJAaJvMhSPg'])
block(7, False, 'סגולות וקצרים בקבלה מעשית', ['tE2iRHeZdBM', 'FrRgsqGVAhs', 'y_VP6EtOhY'.replace('y_VP6EtOhY', 'y_VP6EdOtHY'), '--Ays3npGTA', '-6C81ubmr34', 'wQ0bHFFmqDE', 'BGPotJgyoCo', '2Q00if8AMJU', '20Li2E3hcaE', 'guEzILUtcpE', 'qP_Yl3pRuc0', 'rHwesDjgLDE', 'Xj3dJXmya-s', 'nZdiBM2tj84', 'AM8iC-84fJU', 'fzpSfP7-w1c', 'lY4tcpFivGE', 'EFIP1awdrcY', 'CoEav-WSTwA', '5l85ZCEczOI', 'MXBfDgfWnFU', '8VT7qwdmcjQ', 'BxPrw1sRPzE', 'xSAYEsmVyBw', 'BsrB9TMN9kw'])
# ================= stage 8 =================
block(8, True, 'חכמת התכונה', ['pSbu4GXVoZE', '1cuZB_UyqZY', 'q6u6vGk-K6Y', 'NVaaqrBTTFI', 'JBwyKnnF-Uk', 'H_YcZf4grYE', 'Gyovq7zMXoE'])
pw = plids(pl('פתחי עולם')) + ['PkVwz7fz-FI', '0WARk1kc67A', 'SKDJIQAF8k8']
block(8, True, 'פתחי עולם – חכמת התכונה והגורלות', bynum(list(dict.fromkeys(pw)), r'עולם\s*(\d+)'))
block(8, True, 'הכניסה לגורלות', ['uLjhZexlYyc', 'FSNgXjSgif0', '32zRvZ5GtSY', 'hKpqTjHZHB8', '_dtbVG8EYHA', 'wDzqU2_S_Js', 'vKM-DS9NyUM', 'poe7c6rOV7U', 'snCCsA4IoxM', 'BiF-7NAXxmY'])
gh = plids(pl('גורל החול'))
block(8, True, 'גורל החול לפי "גורל כחול הים"', bynum(gh, r'(?:גורל החול|כחול הים)\D*(\d+)'))
block(8, True, 'גורלות בעיון: בתי החול למהרח"ו, אבני בורלא, גורל החולה', ['STIQg6rOYZ0', 'qY2XpC1sSqI', 'wBFRbSUpOts', 'ET8r4avp81I', 'eJsruvYyGXw'])
block(8, True, 'שיחת עופות וגורל העוף', bynum(plids(pl('שיחת עופות')), r'(\d+)'))
block(8, False, 'שרטוטי כף היד', ['GW4zpW-8V9Q', '8103nkLjjzM', 'xd_2qhM7VpA'])

# ================= catch-all: enrichment by regex =================
HIL = re.compile(r'הילול|רבי |רבנו|רב |הרב |קבר|ציון|חכמי|צדיק|אזכרה|פיוט|מערה|בית הכנסת|בית כנסת|סיפור|טינריר|אגדיר|מרקש|מראכש|וארזזת|אוריקה|מגדל העמק|קרית מלאכי|בית הקברות|הר הזיתים|דגם בית המקדש|האלכימאי|ניגונים|האדמור|דייני|תקנת|היר.א|הדיאה|הדאיה|אלפיה|פיררא|בן שושן|מולכו|כדורי|פתיא|אבוחצירא|בן ברוך|בן מלכ|נחמיאס|בלחנס|עמאר|עדס|ביטון|חבושה|ויזמאן|דיוואן|פינטו|טולדאנו|ביבאס|מוצפי|עבודי|אנקווה|ברדוגו|בן טובו|קואינקא|קלעה|רשיון|הדפסת התניא|חמדת ימים|שומרי החומות|חצוצרות|הר הבית|המימונה|מימונה|כיבוד|בין הזמנים|רגע שיא|בשידור חי|חידוש|סטטיסטיקה|תהי שבע|בעל תשובה|האוהב ישראל|אמא של|שבשתא|\d+ ב[א-ת]+ 20\d\d|המקובל|שליט|זיע')
for i, v in V.items():
    if i in assign: continue
    assign[i] = dict(stage=0, core=False, block='חכמי המערב, הילולות וסיפורי צדיקים (העשרה)')
rest = [i for i, a in assign.items() if a['block'].startswith('חכמי המערב')]
rest.sort(key=lambda i: (V[i]['date'] or '9', V[i]['title']))
blocks.append(dict(stage=0, core=False, title='חכמי המערב, הילולות וסיפורי צדיקים (העשרה)', ids=rest, note='לפי תאריך; שיעורים שאינם חלק מהמסלול אך מלמדים מי הם החכמים שהרב מביא.'))
for i in rest:
    if not HIL.search(V[i]['title']): print('CHECK catch-all:', i, V[i]['dur']//60, 'm', V[i]['title'][:80])

# ================= report =================
json.dump(dict(assign=assign, blocks=blocks), open(os.path.join(HERE, 'video-assign.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
from collections import Counter
c = Counter((a['stage'], a['core']) for a in assign.values())
print('assigned', len(assign), 'of', len(V))
for s in range(9):
    print(f'stage {s}: core {c[(s,True)]:4d}  enrich {c[(s,False)]:4d}')
hours = Counter()
for i, a in assign.items():
    if 'alt_of' not in a: hours[(a['stage'], a['core'])] += V[i]['dur'] / 3600
print({k: round(v, 1) for k, v in sorted(hours.items())})
missing = [i for i in V if i not in assign]
print('missing', missing)
