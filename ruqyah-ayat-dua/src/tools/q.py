#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""উসমানী হাফস মুসহাফ থেকে আয়াত তোলা (quran-text প্যাকেজের ডেটা)"""
import json, os, sys, functools

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hafs.json')

@functools.lru_cache(maxsize=1)
def _d():
    return json.load(open(DATA, encoding='utf-8'))

def _ayah_index(surah, ayah):
    """১-ভিত্তিক সূরা ও আয়াত → বিশ্বজনীন আয়াত ক্রম (০-ভিত্তিক)"""
    d = _d()
    s = d['surahs'][surah - 1]
    return s['first_ayah'] + (ayah - 1)

def ayah(surah, ayah_no):
    d = _d()
    i = _ayah_index(surah, ayah_no)
    st = d['ayah_starts']
    a, b = st[i], (st[i + 1] if i + 1 < len(st) else len(d['words']))
    return ' '.join(d['words'][a:b])

def rng(surah, first, last=None):
    last = last or first
    return ' '.join(ayah(surah, n) for n in range(first, last + 1))

if __name__ == '__main__':
    s = int(sys.argv[1]); a = int(sys.argv[2]); b = int(sys.argv[3]) if len(sys.argv) > 3 else None
    print(rng(s, a, b))


# ───────────── বাংলা অনুবাদ (মুহিউদ্দীন খান) ─────────────
_BN = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bn-mkhan.json')

@functools.lru_cache(maxsize=1)
def _bn():
    rows = json.load(open(_BN, encoding='utf-8'))['quran']
    out = {}
    for r in rows:
        out[(r['chapter'], r['verse'])] = r['text'].strip()
    return out

def bn_ayah(surah, n):
    return _bn().get((surah, n), '')

def bn_rng(surah, first, last=None):
    last = last or first
    return ' '.join(bn_ayah(surah, n) for n in range(first, last + 1)).strip()

@functools.lru_cache(maxsize=1)
def vocab():
    """পরিষ্কার বাংলা শব্দভাণ্ডার — ফাঁক জোড়া দেওয়ার সিদ্ধান্তের জন্য"""
    import re as _re
    v = set()
    for t in _bn().values():
        for w in _re.split(r'[^ঀ-৿‌‍]+', t):
            if w: v.add(w)
    return v
