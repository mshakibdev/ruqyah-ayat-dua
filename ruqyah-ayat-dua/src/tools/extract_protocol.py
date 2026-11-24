#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""রুকইয়াহ প্রোটোকল PDF → খসড়া JSON

PDF-এর আরবি টেক্সট লেয়ার ভাঙা, তাই আরবি আসে উসমানী হাফস মুসহাফ থেকে
(সূরা-আয়াত নম্বর ধরে)। বাংলা অর্থ ও পাঠসংখ্যা আসে PDF থেকে।
"""
import re, json, sys, pathlib
sys.path.insert(0, '/home/claude/quran')
import q as QURAN
from despace import despace_line

BN = '০১২৩৪৫৬৭৮৯'
B2A = {c: str(i) for i, c in enumerate(BN)}
def n2i(s):
    s = ''.join(B2A.get(c, c) for c in s)
    m = re.search(r'\d+', s)
    return int(m.group()) if m else None

# বাংলা সূরানাম → নম্বর
SURAH = {
 'আল-ফাতিহা':1,'ফাতিহা':1,'আল-বাকারা':2,'বাকারা':2,'আলে ইমরান':3,'আন-নিসা':4,
 'আল-মায়িদা':5,"আল-আন'আম":6,"আল-আ'রাফ":7,'আল-আরাফ':7,
 'আল-আনফাল':8,'আত-তাওবা':9,'ইউনুস':10,'হুদ':11,'ইউসুফ':12,"আর-রা'দ":13,'আর-রাদ':13,
 'ইবরাহীম':14,'আল-হিজর':15,'আন-নাহল':16,'আল-ইসরা':17,'আল-কাহফ':18,'মারইয়াম':19,
 'ত্বহা':20,'তোয়াহা':20,'আল-আম্বিয়া':21,'আল-হাজ্জ':22,"আল-মু'মিনূন":23,'আল-মুমিনূন':23,
 'আন-নূর':24,'আল-ফুরকান':25,'আল-ফু‌রকান':25,"আশ-শু'আরা":26,'আন-নামল':27,
 'আল-কাসাস':28,'আল-আনকাবূত':29,'আর-রূম':30,'লুকমান':31,'আস-সাজদা':32,'আল-আহযাব':33,
 'সাবা':34,'ফাতির':35,'ইয়াসীন':36,'আস-সাফফাত':37,'সোয়াদ':38,'আয-যুমার':39,
 'গাফির':40,'ফুসসিলাত':41,'ফু‌সসিলাত':41,'আশ-শূরা':42,'আয-যুখরুফ':43,'আদ-দুখান':44,
 'আল-জাসিয়া':45,'আল-আহকাফ':46,'মুহাম্মাদ':47,'আল-ফাতহ':48,'আল-হুজুরাত':49,'ক্বাফ':50,
 'আয-যারিয়াত':51,'আত-তূর':52,'আন-নাজম':53,'আল-কামার':54,'আর-রহমান':55,
 'আল-ওয়াকিয়াহ':56,'আল-হাদীদ':57,'আল-মুজাদালা':58,'আল-হাশর':59,'আল-মুমতাহিনা':60,
 'আস-সাফ':61,"আল-জুমু'আ":62,'আল-জুমুআ':62,'আল-মুনাফিকূন':63,'আত-তাগাবুন':64,
 'আত-তালাক':65,'আত-তাহরীম':66,'আল-মুলক':67,'আল-কলম':68,'আল-হাক্কাহ':69,
 'আল-মাআরিজ':70,'নূহ':71,'আল-জ্বীন':72,'আল-মুযযাম্মিল':73,'আল-মুদ্দাসসির':74,
 'আল-কিয়ামাহ':75,'আল-ইনসান':76,'আল-মুরসালাত':77,'আন-নাবা':78,'আন-নাযিআত':79,
 'আবাসা':80,'আত-তাকভীর':81,'আল-ইনফিতার':82,'আল-মুতাফফিফীন':83,'আল-ইনশিকাক':84,
 'আল-বুরূজ':85,'আত-তারিক':86,'আল-আ‌লা':87,'আল-গাশিয়া':88,'আল-ফাজর':89,
 'আল-বালাদ':90,'আশ-শামস':91,'আল-লাইল':92,'আদ-দুহা':93,'আশ-শারহ':94,'আত-তীন':95,
 'আল-আলাক':96,'আল-কদর':97,'আল-বাইয়িনাহ':98,'আয-যিলযাল':99,'আল-আদিয়াত':100,
 'আল-কারিয়াহ':101,'আত-তাকাসুর':102,'আল-আসর':103,'আল-হুমাযাহ':104,'আল-ফীল':105,
 'কুরাইশ':106,"আল-মা'ঊন":107,'আল-কাওসার':108,'আল-কাফিরূন':109,'আন-নাসর':110,
 'আল-মাসাদ':111,'আল-ইখলাস':112,'আল-ফালাক':113,'আন-নাস':114,
}

def despace(s):
    """PDF থেকে আসা বাংলায় শব্দের ভেতর ঢুকে পড়া ফাঁক সরানো"""
    s = re.sub(r'\s+', ' ', s).strip()
    # যুক্তাক্ষর/কার-চিহ্নের আগে-পরে ভুল ফাঁক
    s = re.sub(r'(?<=[ঀ-৿]) (?=[া-ৌৗ়্])', '', s)
    s = re.sub(r'(?<=[্]) (?=[ঀ-৿])', '', s)
    return s

ARABIC = re.compile(r'[؀-ۿݐ-ݿﭐ-﻿]')
HEAD = re.compile(r'^সূ\s?রা\s+(.+?)\s*[:：]\s*([০-৯0-9]+)(?:\s*-\s*([০-৯0-9]+))?\s*$')
CNT  = re.compile(r'^পাঠসংখ্যা\s*[:：]\s*(.+?)\s*$')
NIY  = re.compile(r'^নিয়\s?ত\s*[:：]\s*(.+?)\s*$')
# পাতার মাথা-পা — অর্থের সাথে যেন না মেশে
CHROME = re.compile(r'রাকী\s*ফয়\s?সাল|Raqi Faisal|Al Quran|আল\s*কু\s?রআন|Telegram|পৃ\s?ষ্ঠা|© ')

# নম্বর → প্রামাণিক বাংলা নাম (SURAH-এর প্রথম বানানটি)
NUM2NAME = {}
for _n, _i in SURAH.items():
    NUM2NAME.setdefault(_i, _n)

def surah_no(name):
    k = re.sub(r'\s+', ' ', name).strip()
    if k in SURAH: return SURAH[k]
    for a, b in SURAH.items():                 # ঢিলেঢালা মিল
        if a.replace('-', '') == k.replace('-', '').replace(' ', ''):
            return b
    return None

FIX = json.loads((pathlib.Path(__file__).parent / 'niyat_fix.json').read_text(encoding='utf-8'))

def parse(path):
    """প্রতি পাতায় একটি/দুটি আয়াত-কার্ড — শিরোনাম, পাঠসংখ্যা ও বাংলা অর্থ"""
    import subprocess
    sys.path.insert(0, str(pathlib.Path(path).parent))
    from clean import clean
    text = clean(path)
    doc = pathlib.Path(path).stem.split('-', 1)[1]
    out = []
    for blk in text.split('<<< পৃষ্ঠা ')[1:]:
        pg = int(blk.split(' >>>')[0])
        lines = [despace(l) for l in blk.split('\n')[1:] if l.strip()]
        heads  = [l for l in lines if HEAD.match(l)]
        counts = [CNT.match(l).group(1) for l in lines if CNT.match(l)]
        niyats = [despace_line(NIY.match(l).group(1)) for l in lines if NIY.match(l)]
        for i, h in enumerate(heads):
            m = HEAD.match(h)
            nm, a, b = m.group(1), n2i(m.group(2)), n2i(m.group(3) or m.group(2))
            sn = surah_no(nm)
            out.append(dict(page=pg,
                            surah_name=NUM2NAME.get(sn) or despace_line(nm), surah=sn,
                            first=a, last=b,
                            cnt=counts[i] if i < len(counts) else (counts[0] if counts else ''),
                            # আরবি ও বাংলা দুটোই নির্ভরযোগ্য উৎস থেকে — PDF থেকে নয়
                            ar=(QURAN.rng(sn, a, b) if sn else ''),
                            mn=(QURAN.bn_rng(sn, a, b) if sn else ''),
                            niyat=FIX.get(f'{doc}|{pg}',
                                  (niyats[i] if i < len(niyats) else
                                   (niyats[0] if len(niyats) == 1 and len(heads) == 1 else ''))),
                            prose=[]))
    return out

if __name__ == '__main__':
    rows = parse(sys.argv[1])
    print(json.dumps(rows, ensure_ascii=False, indent=1))
