#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PDF থেকে আসা বাংলায় শব্দের ভেতরে ঢুকে পড়া ফাঁক সরানো।

গ্লিফ বসানোর কারণে poppler শব্দের মাঝখানেও ফাঁক দেয় ("নিয় ত" → "নিয়ত")।
প্রতিটি লাইনকে টুকরোর ক্রম ধরে DP চালানো হয় — এমন ভাগ বেছে নেওয়া হয় যাতে
অচেনা শব্দ সবচেয়ে কম থাকে।

শব্দ চেনা হয় **কম্পাঙ্ক** দেখে, নিছক উপস্থিতি দেখে নয়। কারণ "সু" বা "প্র"
অনুবাদে দু-একবার এলেও সেগুলো আসলে শব্দ নয়, টুকরো — ওদের জোড়া লাগা উচিত
("সুরক্ষা"), আবার "সাড়া" ও "দেওয়া" দুটোই সত্যিকার শব্দ — ওদের জোড়া লাগা উচিত নয়।
"""
import re, sys, os, functools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import q as Q

BNWORD = re.compile(r'[ঀ-৿‌‍]+')
PUNCT  = '।,:;?!“”‘’\'"()[]{}-–—.…  '
# সত্যিকারের ছোট বাংলা শব্দ — এগুলো টুকরো নয়
SHORTOK = {'ও','এ','না','নি','কি','কে','যে','সে','তা','যা','আর','এই','ওই','বা','ঐ',
           'হে','তো','ই','যদি','এক','দুই','তিন','যার','তার','এর','ও,','এবং'}

MAXJOIN   = 4     # সর্বোচ্চ কত টুকরো একসাথে
MINFREQ   = 3     # এর কম এলে শব্দ নয়, টুকরো
STRONGFRQ = 12    # এর বেশি এলে পাকা শব্দ — পাশেরটার সাথে জোড়া লাগবে না

# কুরআন-অনুবাদে নেই, কিন্তু এই নথিগুলোতে লাগে
MANUAL = """নিয়ত পাঠসংখ্যা রুকইয়াহ সেলফ গাইডলাইন সাপ্লিমেন্ট প্রোটোকল আয়াতসমূহ সমাপ্তির
উচ্চারণ তিলাওয়াত সূরা আয়াত দোয়া দুআ বদনজর হাসাদ সিহর জাদু গিঁট তাসাল্লুত ওয়াসওয়াসা
যিকির সুরক্ষা প্রার্থনা উপস্থিতি কুমন্ত্রণা আশ্রয় নেপথ্যের শয়তানি অলসতা গড়িমসি
প্রোডাক্টিভিটি রিযিক রিজিক স্থূলতা ওজন হাঁটু গোড়ালি কোমর পাকস্থলী গ্রন্থি ম্যাসাজ
অলিভ কালোজিরা বরই গোলাপজল ফজরের আসরের মাগরিবের ঘুমানোর সাপ্তাহিক দৈনিক ফোকাস
নিরুপায়ের দূরকারী আহ্বান সৃষ্টিজগতের পূর্ববর্তীদের স্থলাভিষিক্ত নিঃসহায়ের
দেওয়া নেওয়া করার হওয়া থাকা বাধা ব্লকেজ লুক্কায়িত অঞ্চল তালু ঘাড় বুক হাত পেট
শরীরে শরীরের মাথার সামনে গলার ছিটানো চলাফেরায় বিকৃতি সৌন্দর্য প্রশস্ততা প্রশান্তি
কিবলামুখী পড়ুন বসুন রাখুন করুন নিন দিন খুলে নিরিবিলি মোবাইল ধারাবাহিকতাই নিয়মিত
আকস্মিক পরিপূর্ণ কালিমাসমূহের সর্বশ্রোতা সর্বজ্ঞ অমুখাপেক্ষী সমতুল্য ওয়াকিয়াহ
মুসহাফ অনুসারে ক্রমানুসারে তালুতে বুলান হতাশ অসুবিধা বিন্যাস সংকলনের মনোযোগ""".split()

@functools.lru_cache(maxsize=1)
def freq():
    f = {}
    for t in Q._bn().values():
        for w in BNWORD.findall(t):
            f[w] = f.get(w, 0) + 1
    for w in MANUAL:
        f[w] = max(f.get(w, 0), STRONGFRQ + 1)
    return f

# বাংলা সাধারণ প্রত্যয় — "হাঁটু" চেনা থাকলে "হাঁটুর"-ও চেনা
SUFFIX = ('গুলোর','গুলোকে','গুলো','গুলি','দেরকে','দের','টির','টিকে','টি','টা',
          'খানা','এর','ের','কে','তে','রা','য়ে','য়','র','ে','ই','ও','সহ')

def _raw(w, lo):
    return freq().get(w, 0) >= lo

def known(w, lo=MINFREQ):
    if _raw(w, lo):
        return True
    for sfx in SUFFIX:                      # প্রত্যয় ছেঁটে মূল শব্দ চেনা যায় কি
        stem = w[:-len(sfx)] if w.endswith(sfx) else None
        if stem and len(stem) >= 3 and len(w) >= 4 and _raw(stem, lo):
            return True
    return False

def strong(w):
    """পাকা শব্দ — ছোট টুকরো কখনোই পাকা নয়, তাই জোড়া আটকাতে পারে না"""
    return len(w) >= 3 and known(w, STRONGFRQ)

def _core(s):
    return s.strip(PUNCT)

def despace_line(line):
    frags = [f for f in line.split(' ')]
    n = len(frags)
    if n < 2:
        return line
    INF = float('inf')
    best = [INF] * (n + 1); back = [None] * (n + 1)
    best[n] = 0
    for i in range(n - 1, -1, -1):
        for j in range(i + 1, min(i + MAXJOIN, n) + 1):
            if best[j] == INF:
                continue
            parts = frags[i:j]
            tok = ''.join(parts)
            c = _core(tok)
            single = (j == i + 1)
            if not c:                                  # শুধু যতিচিহ্ন
                cost = 0 if single else INF
            elif not BNWORD.fullmatch(c):              # বাংলা নয় — ছুঁয়ো না
                cost = 0 if single else INF
            elif single:
                if len(c) <= 2 and c not in SHORTOK:
                    cost = 2            # এক-দুই অক্ষর সাধারণত শব্দ নয়, টুকরো
                else:
                    cost = 0 if known(c) else 3
            else:
                # সব টুকরোই যদি পাকা শব্দ হয়, জোড়া লাগানো যাবে না
                if all(strong(_core(p)) for p in parts if _core(p)):
                    cost = INF               # সবগুলোই পাকা শব্দ — ফাঁকটা আসল
                elif known(c, 1):
                    cost = 0.4 + 0.1 * (j - i - 2)
                else:
                    # জোড়া লাগিয়েও চেনা গেল না — আলাদা রাখার চেয়ে খারাপ
                    cost = 3 * (j - i) + 0.5
            if cost == INF:
                continue
            if best[i] > cost + best[j]:
                best[i] = cost + best[j]; back[i] = j
    out, i = [], 0
    while i < n:
        j = back[i] or i + 1
        out.append(''.join(frags[i:j])); i = j
    s = ' '.join(out)
    s = re.sub(r'\s+([।,:;?!)\]…])', r'\1', s)         # যতিচিহ্নের আগে ফাঁক
    s = re.sub(r'([(\[“‘])\s+', r'\1', s)
    s = re.sub(r'\s{2,}', ' ', s)
    return s.strip()

def despace(text):
    return '\n'.join(despace_line(l) for l in text.split('\n'))

if __name__ == '__main__':
    print(despace(sys.stdin.read().rstrip('\n')))
