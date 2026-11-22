#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""রুকইয়াহ — আয়াত ও দোয়া  ·  data.json থেকে PWA-র পাতা তৈরি করে"""
import json, re, os, html, shutil

SRC  = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data.json')
OUT  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BN   = '০১২৩৪৫৬৭৮৯'
B2A  = {c: str(i) for i, c in enumerate(BN)}

def bn2int(s):
    """প্রথম বাংলা সংখ্যাটি বের করে আনে"""
    m = re.search(r'[০-৯]+', s or '')
    return int(''.join(B2A[c] for c in m.group())) if m else 0

def bn(n):
    """ইংরেজি অঙ্ককে বাংলায়"""
    return ''.join(BN[int(c)] if c.isdigit() else c for c in str(n))

AR_RE = re.compile(r'[؀-ۿݐ-ݿﭐ-﷿ﹰ-﻿]')

def split_arabic_title(t):
    """'এক · নাম (عربي)' → ('এক · নাম', 'عربي') — না থাকলে আরবি অংশ ফাঁকা"""
    m = re.search(r'\s*[\(（]\s*([^()）]*)\s*[\)）]\s*$', t or '')
    if m and AR_RE.search(m.group(1)):
        return t[:m.start()].strip(), m.group(1).strip()
    return (t or '').strip(), ''

def mark(t):
    """»...« অংশ হাইলাইট করে, বাকিটা escape করে"""
    out, i = [], 0
    for m in re.finditer(r'»(.*?)«', t):
        out.append(html.escape(t[i:m.start()]))
        out.append('<span class="hl">' + html.escape(m.group(1)) + '</span>')
        i = m.end()
    out.append(html.escape(t[i:]))
    return ''.join(out)

def esc(t):
    return html.escape(t or '').replace('»', '“').replace('«', '”')

PAGES = [
    ('tair.html',      'tair',  'আয়াতুত তাইর',            'آيَاتُ الطَّيْرِ',
     'উড়ন্ত জ্বীন সংক্রান্ত আয়াত ও সম্বোধন'),
    ('dua.html',       'dua',   'রুকইয়াহর দোয়াসমূহ',       'أَدْعِيَةُ الرُّقْيَةِ',
     'উড়ন্ত জ্বীন, জাদুকর, জাদুর গিঁট ও শয়তানের ঢাল'),
    ('kobor-ayat.html','kayat', 'কবরের জাদুর আয়াত',        'آيَاتُ السِّحْرِ الْمَدْفُونِ',
     'পুঁতে রাখা জাদু ভাঙার আয়াত ও দোয়া'),
    ('kobor-dua.html', 'kdua',  'কবরের জাদুর দোয়া',        'أَدْعِيَةُ السِّحْرِ الْمَدْفُونِ',
     'পূর্ণ সেশনের দোয়া — শুরু থেকে সমাপ্তি'),
]

NAV = [('index.html', 'হোম')] + [(f, t) for f, _, t, _, _ in PAGES]

def head(title, cur):
    links = '\n    '.join(
        '<a href="%s"%s>%s</a>' % (f, ' aria-current="page"' if f == cur else '', t)
        for f, t in NAV)
    return f'''<!DOCTYPE html>
<html lang="bn">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<link rel="stylesheet" href="style.css">
<link rel="manifest" href="manifest.json">
<meta name="theme-color" content="#1b3a4b">
<meta name="theme-color" content="#101a20" media="(prefers-color-scheme: dark)">
<link rel="icon" href="icons/icon-192.png" type="image/png">
<link rel="apple-touch-icon" href="icons/apple-touch-icon.png">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="apple-mobile-web-app-title" content="আয়াত ও দোয়া">
<script>try{{var t=localStorage.getItem('rad-theme');if(t)document.documentElement.setAttribute('data-theme',t);
var f=localStorage.getItem('rad-ar');if(f)document.documentElement.style.setProperty('--arsize',f+'px');}}catch(e){{}}</script>
</head>
<body>
<div class="wrap">

<div class="topbar">
    {links}
</div>
'''

FOOT = '''
<footer>
  <b>রুকইয়াহ — আয়াত ও দোয়া</b><br>
  সংকলন ও সম্পাদনা — <b>ইবনে নাঈম</b> · Ibn Naim
</footer>

</div>

<div class="tools">
  <button class="tool" id="fminus" aria-label="আরবি ছোট">A−</button>
  <button class="tool" id="fplus" aria-label="আরবি বড়">A+</button>
  <button class="tool" id="wake" aria-label="স্ক্রিন জাগিয়ে রাখুন">☀</button>
  <button class="tool" id="tb" aria-label="থিম">◐</button>
</div>
<button class="installbtn" id="install" hidden>⤓ ইনস্টল করুন</button>
<script src="app.js" defer></script>
</body>
</html>
'''

def bn_max(s):
    """লেখায় যত বাংলা সংখ্যা আছে তার সবচেয়ে বড়টি — '১ বার (৩ বার পুনরাবৃত্তি)' → ৩"""
    ns = [int(''.join(B2A[c] for c in m)) for m in re.findall(r'[০-৯]+', s or '')]
    return max(ns) if ns else 0

def split_notes(s):
    """মূল TXT-এ ** দিয়ে টীকা আলাদা করা — ('মূল লেখা', ['টীকা', ...])"""
    parts = [x.strip() for x in (s or '').split('**')]
    return parts[0], [x for x in parts[1:] if x]

REP_RE = re.compile(r'পুনরাবৃত্তি\s*[:：]\s*[“"\'‘]?(.+?)[”"\'’]?\s*অংশটি\s*(.+?)\s*।?\s*$')

def counter(label, cid):
    """সংখ্যা থাকলে গোনার বোতাম, না থাকলে শুধু লেখা"""
    # '৭ বার / ৩ বার' — উৎস দুটি ভিন্ন সংখ্যা বলছে, তাই কোনোটি বেছে নেওয়া হচ্ছে না
    if '/' in (label or ''):
        return f'<span class="cnt flat">{esc(label)}</span>'
    tgt = bn_max(label)
    if not tgt:
        return f'<span class="cnt flat">{esc(label)}</span>'
    # 'অধিক'/'অন্তত' মানে সংখ্যাটা সর্বনিম্ন — তাই লক্ষ্য ছাড়িয়েও গোনা চলবে
    op = ' data-open="1"' if re.search(r'অধিক|অন্তত|বেশি', label or '') else ''
    return (f'<button class="cnt" data-id="{cid}" data-target="{tgt}"{op}>'
            f'<span class="cv">০</span><span class="cs">/</span>'
            f'<span class="ct">{esc(label)}</span></button>')

def render_item(k, idx, it):
    """একটি আয়াত বা দোয়ার কার্ড"""
    cid = f'{k}-{idx}'
    tag = ''
    if k in ('kayat', 'kdua'):
        no    = it['num']
        title, tar = split_arabic_title(it['title'])
        badge = counter(it.get('cnt', ''), cid)
        reps  = []
    else:
        m = re.match(r'^([০-৯]+)\s*[।·\.]?\s*(.*)$', it['head'])
        no    = m.group(1) if m else str(idx + 1)
        rest  = (m.group(2) if m else it['head']).strip()
        # শেষের [...] অংশটি আলাদা চিপ — আয়াত নম্বর, বা 'কুরআনের আয়াত নয়'-এর মতো টীকা
        bm = re.search(r'\[(.*?)\]\s*$', rest)
        if bm:
            tag  = bm.group(1).strip()
            rest = rest[:bm.start()].strip()
        if not rest:                 # উৎসে শিরোনাম নেই — চিপটাই শিরোনাম
            rest, tag = tag or 'দোয়া', ''
        title, tar = split_arabic_title(rest)
        badge = ''
        reps  = it.get('rep', [])

    p = [f'<article class="it" id="{cid}">']
    p.append('<div class="ih">')
    p.append(f'<span class="no">{esc(no)}</span>')
    tx = f'<span class="tix">{esc(tar)}</span>' if tar else ''
    p.append(f'<span class="ti">{esc(title)}{tx}</span>')
    if tag:
        warn = ' warn' if 'নয়' in tag else ''
        p.append(f'<span class="tag{warn}">{esc(tag)}</span>')
    if badge: p.append(badge)
    p.append('</div>')

    notes, pairs = [], []        # pairs = (অংশ, সংখ্যা) — গোনার সারি

    def take(field):
        """মূল লেখা ফিরিয়ে দেয়, ** দিয়ে আলাদা করা টীকা জমা রাখে"""
        main, extra = split_notes(it.get(field))
        for n in extra:
            m = REP_RE.search(n)
            if m: pairs.append((m.group(1).strip(), m.group(2).strip()))
            else: notes.append(n)
        return main

    ar = ' '.join(it['ar'])
    p.append(f'<div class="arx">{mark(ar)}</div>')

    tr, mn, ny = take('tr'), take('mn'), take('niyat')
    if tr: p.append(f'<div class="tr">{mark(tr)}</div>')
    if mn: p.append(f'<div class="mn">{esc(mn)}</div>')
    if ny: p.append(f'<div class="ny"><b>নিয়ত ·</b> {esc(ny)}</div>')

    # প্রতি-অংশ পুনরাবৃত্তি
    for r in reps:
        r, extra = split_notes(r)
        notes.extend(extra)
        if not r: continue
        if '—' in r:
            part, num = [x.strip() for x in r.rsplit('—', 1)]
        elif re.search(r'[০-৯]', r):
            part, num = r.strip(), ''
        else:
            notes.append(r.strip())     # নির্দেশনা নয়, টীকা
            continue
        pairs.append((part, num))

    if pairs:
        rows = []
        for ri, (part, num) in enumerate(pairs):
            lab = f'<span class="ar">{esc(part)}</span>' if AR_RE.search(part) else esc(part)
            rows.append(f'<div class="rr"><span class="rl">{lab}</span>'
                        f'{counter(num, cid + "-r" + str(ri))}</div>')
        p.append('<div class="reps"><div class="rh">পুনরাবৃত্তি</div>' + ''.join(rows) + '</div>')

    for n in notes:
        p.append(f'<div class="nt">{esc(n)}</div>')
    if it.get('note'):
        p.append(f'<div class="nt">{esc(split_notes(it["note"])[0])}</div>')
    if it.get('src'):
        p.append(f'<div class="nt"><b>উৎস ·</b> {esc(split_notes(it["src"])[0])}</div>')
    p.append('</article>')
    return '\n'.join(p)

def build():
    d = json.load(open(SRC, encoding='utf-8'))
    os.makedirs(OUT, exist_ok=True)

    for fn, key, title, arabic, sub in PAGES:
        blk = d[key]
        items = blk['items']
        body = [head(f'{title} — রুকইয়াহ', fn)]
        body.append(f'''
<header>
  <h1>{esc(title)}</h1>
  <div class="ar">{esc(arabic)}</div>
  <p>{esc(sub)} · {bn(len(items))}টি অংশ</p>
  <div class="hbar">
    <span class="hint">সংখ্যার ঘরে চাপ দিলে গোনা বাড়ে · চেপে ধরে রাখলে শূন্য</span>
    <button class="rst" id="reset">সব শূন্য করুন</button>
  </div>
</header>
''')
        last = None
        for i, it in enumerate(items):
            ch = it.get('ch')
            if ch and ch != last:
                cb, ca = split_arabic_title(ch)
                arpart = f'<span class="chx">{esc(ca)}</span>' if ca else ''
                body.append(f'<h2 class="ch">{esc(cb)}{arpart}</h2>')
                last = ch
            body.append(render_item(key, i, it))
        body.append(FOOT)
        open(os.path.join(OUT, fn), 'w', encoding='utf-8').write('\n'.join(body))
        print('✓', fn, f'({len(items)} আইটেম)')

    # ---------- হোম ----------
    counts = {k: len(d[k]['items']) for k in d}
    cards = []
    meta = [('tair.html',  'আয়াতুত তাইর', 'آيَاتُ الطَّيْرِ',
             'উড়ন্ত জ্বীন সংক্রান্ত ১৩টি আয়াত ও সম্বোধন, তিন অধ্যায়ে। প্রতিটির নির্দিষ্ট অংশ আলাদা করে পড়ার নির্দেশ আছে।',
             counts['tair'], '#1b3a4b'),
            ('dua.html', 'রুকইয়াহর দোয়াসমূহ', 'أَدْعِيَةُ الرُّقْيَةِ',
             'উড়ন্ত জ্বীন, জাদুকর, জাদুর গিঁট ও শয়তানের ঢাল ভাঙার ১৫টি দোয়া, চার অধ্যায়ে।',
             counts['dua'], '#5c3b6e'),
            ('kobor-ayat.html', 'কবরের জাদুর আয়াত', 'آيَاتُ السِّحْرِ الْمَدْفُونِ',
             'পুঁতে রাখা জাদু ভাঙার ১৪টি আয়াত ও দোয়া, পাঠসংখ্যা ও নিয়তসহ।',
             counts['kayat'], '#6b4522'),
            ('kobor-dua.html', 'কবরের জাদুর দোয়া', 'أَدْعِيَةُ السِّحْرِ الْمَدْفُونِ',
             'পূর্ণ সেশনের ১৪টি দোয়া — শুরু, বিশেষ দোয়া, জিন ধ্বংস ও সমাপ্তি।',
             counts['kdua'], '#2f5d44')]
    for f, t, a, p, n, c in meta:
        cards.append(f'''  <a class="tc" href="{f}" style="--tc:{c}">
    <h3>{esc(t)}</h3>
    <div class="ar">{esc(a)}</div>
    <p>{esc(p)}</p>
    <div class="go">{bn(n)}টি অংশ · খুলুন →</div>
  </a>''')

    home = [head('রুকইয়াহ — আয়াত ও দোয়া', 'index.html')]
    home.append(f'''
<header>
  <h1>রুকইয়াহ — আয়াত ও দোয়া</h1>
  <p>পড়ার জন্য সংকলিত আয়াত ও দোয়া — আরবি, উচ্চারণ ও অর্থসহ। মোট <b>{bn(sum(counts.values()))}টি অংশ</b>, চারটি সংকলনে।</p>
</header>

<h2 class="sh">সংকলনগুলো</h2>
<div class="cards">
{chr(10).join(cards)}
</div>

<h2 class="sh mt">পড়ার সময় যা কাজে লাগবে</h2>
<div class="box">
  <ul class="l">
    <li><b>গোনার ঘর</b> — পাঠসংখ্যার ঘরে চাপ দিলে এক এক করে বাড়ে, লক্ষ্যে পৌঁছালে সবুজ হয়ে যায়। চেপে ধরে রাখলে আবার শূন্য। বন্ধ করে পরে খুললেও গোনা যেখানে ছিল সেখানেই থাকে।</li>
    <li><b>হলুদ দাগ</b> — মূল নথিতে লাল কালিতে যে অংশ আলাদা করে পড়তে বলা হয়েছে, সেটি এখানে দাগ দেওয়া।</li>
    <li><b>A− / A+</b> — আরবির আকার ছোট-বড় করা যায়, পছন্দ মনে থাকে।</li>
    <li><b>☀ বোতাম</b> — পড়ার সময় স্ক্রিন নিভে যাওয়া বন্ধ রাখে।</li>
    <li><b>অফলাইন</b> — একবার খোলার পর ইন্টারনেট ছাড়াই পুরোটা চলে।</li>
  </ul>
</div>

<div class="note">
  <b>একটি কথা।</b> কোন অংশ কতবার — এই সংখ্যাগুলো মূল সংকলকের দেওয়া, কুরআন-হাদীসে নির্দিষ্ট করা নেই। <b>সংখ্যা মেলাতে না পারলে দুশ্চিন্তার কিছু নেই</b>, নিয়মিত পড়াটাই মূল। আর আয়াতুত তাইরের ১১ নম্বর ও রুকইয়াহর দোয়াসমূহের বেশিরভাগ <b>কুরআনের আয়াত নয়</b> — সংকলকের রচিত সম্বোধন; নিজ নিজ পাতায় তা চিহ্নিত আছে।
</div>
''')
    home.append(FOOT)
    open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8').write('\n'.join(home))
    print('✓ index.html')

if __name__ == '__main__':
    build()
