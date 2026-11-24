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
    ('qareen.html',    'qareen','কারীনের দোয়া',            'أَدْعِيَةُ الْقَرِين',
     'সাতটি কর্মসূচি থেকে বেছে নেওয়া পাঠযোগ্য দোয়া'),
    ('nokkhotro.html', 'nokkhotro', 'নক্ষত্র ও আসমানের আয়াত', 'آيَاتُ النُّجُومِ وَالسَّمَاءِ',
     'তারকা, চাঁদ ও আকাশ সংক্রান্ত আয়াত ও দোয়া'),
    ('atke.html',      'atke',   'আটকে থাকা কাজ ও প্রোডাক্টিভিটি', 'عَوَائِقُ الْعَمَلِ',
     'কাজে বাধা, গড়িমসি ও অলসতা কাটানোর আয়াত ও দোয়া'),
    ('rizq.html',      'rizq',   'ফাক্কুত তা‌তিল — রিযিকের বাধা', 'فَكُّ التَّعْطِيلِ',
     'লুক্কায়িত বাধা দূরীকরণ ও রিযিকের ব্লকেজ খোলা'),
    ('git-pa.html',    'git',    'পা ও হাঁটুর গিঁট এবং ছিটানো জাদু', 'عُقَدُ الْقَدَمَيْنِ',
     'চলাফেরায় বাধা ও পথে ছিটিয়ে রাখা সিহরের আয়াত'),
    ('sthulota.html',  'sthulota', 'স্থূলতা ও ওজন বৃদ্ধি', 'السُّمْنَةُ',
     'সিহর, নজর, হাসাদ ও গিঁটের সন্দেহে স্থূলতার রুকইয়াহ'),
]

# ---------------------------------------------------------------------------
# রুকইয়াহ প্রোটোকল ছাঁচের সাধারণ নিয়ম — শুধু ম্যাসাজের জায়গাটা বিষয়ভেদে আলাদা
# ---------------------------------------------------------------------------
def protocol_method(focus, daily):
    return f'''
  <h4>পদ্ধতি — ধাপে ধাপে</h4>
  <ol class="mo">
    <li><b>অযু করে কিবলামুখী হয়ে নিরিবিলি বসুন।</b> মোবাইল দূরে রাখুন।</li>
    <li><b>নিয়ত করুন</b> — আল্লাহর কালাম দিয়ে আল্লাহর কাছে আরোগ্য চাইছি; কালামের নিজের
        কোনো শক্তি নেই, শক্তি আল্লাহর।</li>
    <li><b>শুরুর দোয়াগুলো</b> পড়ুন (প্রথম অধ্যায়)।</li>
    <li><b>আয়াতগুলো ক্রমানুসারে পড়ুন।</b> পড়ার সময় দুই হাতের তালুতে ফুঁ দিয়ে সমস্যার
        জায়গায় হাত বুলান।</li>
    <li><b>পাঠসংখ্যা যতবার বলা আছে ততবার</b> — কম-বেশি করার দরকার নেই।</li>
    <li><b>মাঝে ১৫ মিনিট নিজের ভাষায়</b> মন খুলে দোয়া করুন। কান্না আসলে আটকাবেন না।</li>
    <li><b>শেষে সমাপ্তির সূরা ও দোয়া</b> পড়ে পানিতে ফুঁ দিন।</li>
    <li><b>কমপক্ষে ৪০ দিন</b> চালিয়ে যান। মাঝে বাদ পড়লে হতাশ না হয়ে আবার শুরু করুন।</li>
  </ol>
  <h4>দৈনিক সময়সূচি</h4>
  <div class="mrow"><span class="ml">সকাল</span><span class="mv">ফজরের পর — আয়াত পাঠ ১৫ মিনিট</span></div>
  <div class="mrow"><span class="ml">সন্ধ্যা</span><span class="mv">মাগরিবের পর — আয়াত পাঠ ১৫ মিনিট</span></div>
  <div class="mrow"><span class="ml">রাত</span><span class="mv">ঘুমানোর আগে — সমাপ্তির সূরা ও দোয়া, পড়া পানি পান</span></div>
  <div class="mrow"><span class="ml">সাপ্তাহিক</span><span class="mv">সপ্তাহে একদিন রুকইয়াহ গোসল</span></div>
  <h4>পড়া তেল ম্যাসাজের জায়গা</h4>
  <p class="mp">{focus}</p>
  <h4>সাপ্লিমেন্ট</h4>
  <ul class="mu">
    <li><b>পড়া পানি</b> — এক বোতল পানিতে আয়াতগুলো পড়ে ফুঁ দিন। দিনে ৩ বার:
        সকালে খালি পেটে, দুপুরে, রাতে ঘুমানোর আগে।</li>
    <li><b>পড়া মধু</b> — খাঁটি মধুতে ফুঁ দিয়ে প্রতিদিন সকালে এক চামচ (সূরা নাহল ৬৯ পড়ে ফুঁ দিলে ভালো)।</li>
    <li><b>পড়া অলিভ অয়েল</b> — জয়তুন তেলে আয়াত পড়ে ফুঁ দিয়ে আক্রান্ত জায়গায় ম্যাসাজ,
        রাতে ঘুমানোর আগে সবচেয়ে ভালো।</li>
    <li><b>কালোজিরা</b> — প্রতিদিন সকালে ৭টি পড়া মধুর সাথে।</li>
    <li><b>রুকইয়াহ গোসল</b> — বালতি পানিতে আয়াত পড়ে ফুঁ দিন, সাথে সাত পাতা বরই পাতা বাটা।
        মাথা থেকে ঢেলে গোসল — সপ্তাহে একদিন।</li>
    <li><b>ঘরে স্প্রে</b> — পড়া পানি স্প্রে বোতলে নিয়ে ঘরের কোণা, দরজা-জানালা ও
        বিছানার নিচে ছিটিয়ে দিন।</li>
  </ul>
  <h4>দৈনিক আমল</h4>
  <div class="mrow"><span class="ml">ফজরের পর</span><span class="mv">সূরা ইয়াসীন ১ বার</span></div>
  <div class="mrow"><span class="ml">আসরের পর</span><span class="mv">সূরা ওয়াকিয়াহ ১ বার</span></div>
  <div class="mrow"><span class="ml">রাতে</span><span class="mv">সূরা ক্বাফ ৩ বার, সূরা মুলক ১ বার</span></div>
  <div class="mrow"><span class="ml">ঘুমানোর আগে</span><span class="mv">আয়াতুল কুরসী ১, বাকারার শেষ দুই আয়াত, তিন কুল ৩ করে — হাতে ফুঁ দিয়ে সারা শরীরে</span></div>
  <div class="mrow"><span class="ml">সকাল-সন্ধ্যা</span><span class="mv">হিসনুল মুসলিমের যিকির নিয়মিত</span></div>
  <div class="mrow"><span class="ml">প্রতিদিন</span><span class="mv">{daily}</span></div>
  <div class="mn2"><b>একটি কথা।</b> পাঠসংখ্যাগুলো সংকলনের নিজস্ব বিন্যাস, কুরআন-হাদীসে নির্দিষ্ট নয় —
  সংখ্যা মেলাতে না পারলে অসুবিধা নেই, মন দিয়ে পড়াটাই মূল। আর এই সংকলনে
  <b>উচ্চারণ দেওয়া হয়নি</b>, কারণ মূল নথিতেও ছিল না।</div>'''

# ---------------------------------------------------------------------------
# নিজে রুকইয়াহ করার নিয়ম — প্রতিটি উৎসের নিজস্ব, মূল নথি থেকে হুবহু
# ---------------------------------------------------------------------------
BANGLA_DUA_TAIR = ('“হে আল্লাহ আমার উড়ন্ত জ্বীন (জ্বীন আত-তাইয়ার) এবং এর ক্ষতিকর প্রভাবের সাথে '
                   'সম্পৃক্ত সকল বদনজর, হাসাদ, সেহের, জ্বীন, শরীরের ভিতরে ও বাইরে থাকা শয়তান জ্বীন '
                   'ও তাদের সকল প্রভাবকে আপনি ধ্বংস করে দিন।”')

def thirty_min(second_half):
    return f'''
  <div class="mrow"><span class="ml">১৫ মিনিট</span><span class="mv">উপরের বাংলা দোয়াটি</span></div>
  <div class="mrow"><span class="ml">১৫ মিনিট</span><span class="mv">{second_half}</span></div>
  <div class="mrow tot"><span class="ml">মোট</span><span class="mv">৩০ মিনিট</span></div>'''

AFTER = '''
  <h4>এরপর যা করবেন</h4>
  <ol class="mo">
    <li>৩০ মিনিট রুকইয়াহ শেষ করার পর <b>পানি, মধু, গোলাপজল, অলিভ অয়েল ও বড়ই পাতা</b> —
        এগুলোতে হালকা থুতু দিয়ে মিশিয়ে ফুঁ দিন।</li>
    <li>সবগুলো একসাথে জোগাড় করার অপেক্ষা করবেন না — অন্তত <b>পানি দিয়ে হলেও আজই শুরু করুন</b>,
        তারপর আস্তে আস্তে বাকিগুলো সংগ্রহ করুন।</li>
    <li>এতে একই সাথে দুটো কাজ হয় — নিজের রুকইয়াহও হলো, আবার পড়া পানি, পড়া মধু, পড়া তেল —
        সাপ্লিমেন্টগুলোও ব্যবহারের জন্য তৈরি হয়ে গেল।</li>
  </ol>'''

METHODS = {
 'tair': f'''
  <h4>যে বাংলা দোয়াটি পড়বেন</h4>
  <div class="mq">{BANGLA_DUA_TAIR}</div>
  <h4>সময় ভাগ</h4>{thirty_min('সূরা ফাতিহা, ফালাক ও নাস এবং এই পাতার আয়াতগুলো')}{AFTER}''',

 'dua': f'''
  <h4>যে বাংলা দোয়াটি পড়বেন</h4>
  <div class="mq">{BANGLA_DUA_TAIR}</div>
  <h4>সময় ভাগ</h4>{thirty_min('সূরা ফাতিহা, ফালাক ও নাস এবং রুকইয়াহর আয়াতগুলো')}{AFTER}''',

 'kayat': '''
  <h4>পড়ার নিয়ম</h4>
  <ul class="mu">
    <li><b>হলুদ দাগ দেওয়া অংশ</b> = আয়াতের যে টুকু আলাদাভাবে বারবার পড়তে বলা হয়েছে।
        ওই অংশের নিজস্ব গোনার ঘর আছে।</li>
    <li>প্রতিটি আয়াতের <b>নিজস্ব পাঠসংখ্যা</b> শিরোনামের পাশে।</li>
    <li>প্রতিটি আয়াতের সাথে <b>নিয়ত</b> দেওয়া আছে — শুধু পড়া নয়, নিয়তটা ধরে রাখাই মূল কথা।</li>
    <li>দুই PDF-এ পাঠসংখ্যা ভিন্ন হলে <b>দুটোই</b> লেখা; সেখানে গোনার ঘর দেওয়া হয়নি,
        কারণ কোনোটা বেছে নেওয়া হয়নি।</li>
  </ul>
  <div class="mn2"><b>ভয় পাবেন না।</b> শরীরে কাঁপুনি, ভারী ভাব বা কবর-মাটি সম্পর্কিত দৃশ্য মনে এলে
  তিলাওয়াত থামাবেন না — মূল নথির নির্দেশ এটাই।</div>''',

 'kdua': '''
  <h4>সেশন শুরুর আগে</h4>
  <ul class="mu">
    <li><b>অযু করে কিবলামুখী হয়ে নিরিবিলি বসুন।</b> মোবাইল দূরে রাখুন।</li>
    <li><b>নিয়ত করুন</b> — আল্লাহর কালাম দিয়ে আল্লাহর কাছে আরোগ্য চাইছি; কালামের নিজের কোনো
        শক্তি নেই, শক্তি আল্লাহর।</li>
    <li><b>ধারাবাহিকতাই মূল কথা</b> — প্রতিদিন অল্প, কিন্তু নিয়মিত।</li>
    <li><b>শেষে পানিতে ফুঁ দিয়ে পান করুন।</b></li>
  </ul>
  <h4>পূর্ণ সেশনের ক্রম</h4>
  <div class="mflow">
    <span>সেকশন ১<i>শুরুর দোয়া</i></span><b>→</b>
    <span>কবরের জাদুর আয়াত<i>আলাদা পাতায়</i></span><b>→</b>
    <span>সেকশন ২ ও ৩<i>মূল দোয়া</i></span><b>→</b>
    <span>সেকশন ৪<i>সমাপ্তি</i></span>
  </div>
  <div class="mn2">সেকশন ১–৩-এর দোয়াগুলো <b>রাকীর সাজানো</b> — কুরআনের আয়াত বা হাদীসের সরাসরি
  বর্ণনা নয়, মূল PDF-এ রেফারেন্সও নেই। সেকশন ৪-এর দোয়াগুলো <b>সহীহ হাদীস</b> থেকে, রেফারেন্সসহ।</div>''',

 'qareen': '''
  <h4>যে বাংলা দোয়াটি পড়বেন</h4>
  <div class="mq">“হে আল্লাহ আমার হাসাদুল কারীন, জাদুর নবায়ন, মানসিক ব্লকেজ ও জিন/শয়তানের প্রভাবের
  সাথে সম্পৃক্ত সকল বদনজর, হাসাদ, সেহের, জ্বীন, শরীরের ভিতরে ও বাইরে থাকা শয়তান জ্বীন ও তাদের
  সকল প্রভাবকে আপনি ধ্বংস করে দিন।”</div>
  <h4>আগে সমস্যাগুলো সাজিয়ে নিন</h4>
  <p class="mp">যে সমস্যাগুলো থেকে মুক্তি চান সেগুলো ১, ২, ৩ করে লিখে নিন। তারপর
  <b>এক নম্বরের জন্য একদিন ৩০ মিনিট</b>, দ্বিতীয় দিন দুই নম্বরের জন্য — এভাবে সিরিয়াল ধরে এগোবেন।</p>
  <h4>সময় ভাগ</h4>''' + thirty_min('সূরা ফাতিহা, ফালাক ও নাস এবং এই পাতার দোয়াগুলো') + AFTER + '''
  <h4>সপ্তাহে একদিন — রুকইয়াহ গোসল</h4>
  <p class="mp">এক বালতি পানিতে <b>১ লিটার পড়া পানি</b>, <b>১০–১৫ চামচ গোলাপজল</b>,
  <b>১–৩ চামচ অলিভ অয়েল</b> ও <b>সাতটি বড়ই পাতা</b> বেটে মেশান। মাথার ওপর থেকে আস্তে আস্তে ঢেলে
  পুরো শরীর ম্যাসাজ করুন, শেষে স্বাভাবিক পানিতে গোসল। (বড়ই পাতা না পেলে গোলাপ পাতা।)</p>
  <div class="mn2">এই নিয়মটি <b>উৎস ঙ</b>-এর — “কারীনের দোয়া ও নিজে রুকইয়াহ করার নিয়ম”।
  নিচের দোয়াগুলো সাতটি আলাদা উৎস থেকে, তাই প্রতিটির পাশে উৎসের অক্ষর দেওয়া আছে।</div>''',
}

METHODS['nokkhotro'] = protocol_method(
    'নক্ষত্র ও আসমানের আয়াতের ক্ষেত্রে ফোকাস — <b>মাথার তালু, কপাল ও বুক</b>।',
    'ফরজ নামাজ জামাতে · ইস্তিগফার ১০০ বার · দরূদ ১০০ বার · সাধ্যমতো সাদাকাহ')
for _k, (_f, _d) in {'atke': ('আটকে থাকা কাজের ক্ষেত্রে ফোকাস — <b>মাথার তালু, ঘাড়, বুক ও দুই হাত</b>।', 'ফরজ নামাজ জামাতে · ইস্তিগফার ১০০ বার · দরূদ ১০০ বার · সাধ্যমতো সাদাকাহ'), 'rizq': ('ফাক্কুত তা\u200cতিলের ক্ষেত্রে ফোকাস — <b>মাথা, ঘাড় ও বুকে</b>।', 'ফরজ নামাজ জামাতে · ইস্তিগফার ১০০ বার · দরূদ ১০০ বার · সাধ্যমতো সাদাকাহ'), 'git': ('পা ও হাঁটুর গিঁটের ক্ষেত্রে ফোকাস — <b>দুই পায়ের তলা, গোড়ালি, হাঁটু ও কোমর</b>।', 'ফরজ নামাজ জামাতে · ইস্তিগফার ১০০ বার · দরূদ ১০০ বার · সাধ্যমতো সাদাকাহ'), 'sthulota': ('স্থূলতার ক্ষেত্রে ফোকাস — <b>পেট ও গ্রন্থি-অঞ্চল (গলার সামনে, কোমর)</b>।', 'ফরজ নামাজ জামাতে · ইস্তিগফার ১০০ বার · দরূদ ১০০ বার · সাধ্যমতো সাদাকাহ')}.items():
    METHODS[_k] = protocol_method(_f, _d)

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
    if 'num' in it:                 # num/title/cnt ছাঁচ (kayat, kdua, qareen, প্রোটোকল…)
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

def method_card(key):
    """পাতার শুরুতে — এই সংকলনটি দিয়ে কীভাবে বসবেন"""
    body = METHODS.get(key)
    if not body:
        return ''
    return f'''
<details class="method" open>
  <summary><span class="mi">◉</span>নিজে রুকইয়াহ করার নিয়ম<span class="mx">লুকান</span></summary>
  <div class="mb">{body}
  </div>
</details>
'''

def surah_table(blk):
    """কারীন পাতার শেষে — যে সূরাগুলো পড়তে বলা হয়েছে (পূর্ণ সূরা, তাই আরবি দেওয়া হয়নি)"""
    rows = blk.get('surahs') or []
    if not rows:
        return ''
    tr = ''.join(f'<tr><td>{esc(a)}</td><td>{esc(b)}</td><td class="sx">{esc(c)}</td></tr>'
                 for a, b, c in rows)
    return f'''
<h2 class="ch">যে সূরাগুলো পড়তে বলা হয়েছে</h2>
<div class="it">
  <p class="mp">এগুলো পূর্ণ সূরা, তাই এখানে আরবি দেওয়া হয়নি — কোন উৎস কোনটা কতবার পড়তে বলেছে
  শুধু সেটুকু। <b>সূরা ক্বাফ</b> পাঁচটি উৎসেই আসে, সংখ্যা আলাদা।</p>
  <table class="sur">
    <tr><th>যা পড়বেন</th><th>কতবার</th><th class="sx">উৎস</th></tr>
    {tr}
  </table>
</div>
'''

def build():
    d = json.load(open(SRC, encoding='utf-8'))
    here = os.path.dirname(os.path.abspath(__file__))
    for _, key, *_ in PAGES:                 # <key>.json থাকলে সেটিই উৎস
        jp = os.path.join(here, key + '.json')
        if os.path.exists(jp):
            d[key] = json.load(open(jp, encoding='utf-8'))
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
        body.append(method_card(key))
        last = None
        for i, it in enumerate(items):
            ch = it.get('ch')
            if ch and ch != last:
                cb, ca = split_arabic_title(ch)
                arpart = f'<span class="chx">{esc(ca)}</span>' if ca else ''
                body.append(f'<h2 class="ch">{esc(cb)}{arpart}</h2>')
                last = ch
            body.append(render_item(key, i, it))
        body.append(surah_table(blk))
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
             counts['kdua'], '#2f5d44'),
            ('qareen.html', 'কারীনের দোয়া', 'أَدْعِيَةُ الْقَرِين',
             'সাতটি কর্মসূচি থেকে বেছে নেওয়া ১১টি পাঠযোগ্য দোয়া ও যিকির, উৎসের অক্ষরসহ।',
             counts['qareen'], '#7a3b3b'),
            ('nokkhotro.html', 'নক্ষত্র ও আসমানের আয়াত', 'آيَاتُ النُّجُومِ وَالسَّمَاءِ',
             'তারকা, চাঁদ ও আকাশ সংক্রান্ত ১৩টি আয়াত, শুরুর ও সমাপ্তির দোয়াসহ পূর্ণ প্রোটোকল।',
             counts['nokkhotro'], '#2b4a6f'),
            ('atke.html', 'আটকে থাকা কাজ ও প্রোডাক্টিভিটি', 'عَوَائِقُ الْعَمَلِ',
             'কাজে বাধা, গড়িমসি ও অলসতা — ১৮টি আয়াত ও ৫টি বিশেষ দোয়াসহ পূর্ণ প্রোটোকল।',
             counts['atke'], '#6b4a1f'),
            ('rizq.html', 'ফাক্কুত তা‌তিল — রিযিকের বাধা', 'فَكُّ التَّعْطِيلِ',
             'লুক্কায়িত বাধা ও রিযিকের ব্লকেজ — ১০টি আয়াত ও ১১টি বিশেষ দোয়া।',
             counts['rizq'], '#1f5f4a'),
            ('git-pa.html', 'পা ও হাঁটুর গিঁট এবং ছিটানো জাদু', 'عُقَدُ الْقَدَمَيْنِ',
             'চলাফেরায় বাধা ও পথে ছিটানো সিহর — ২৫টি আয়াত, দুই অংশে।',
             counts['git'], '#4a3a6b'),
            ('sthulota.html', 'স্থূলতা ও ওজন বৃদ্ধি', 'السُّمْنَةُ',
             'সিহর, নজর ও গিঁটের সন্দেহে স্থূলতা — ৬টি আয়াত ও ১৫টি দোয়া।',
             counts['sthulota'], '#7a5a2b')]
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
  <p>পড়ার জন্য সংকলিত আয়াত ও দোয়া — আরবি, উচ্চারণ ও অর্থসহ। মোট <b>{bn(sum(counts.values()))}টি অংশ</b>, {bn(len(counts))}টি সংকলনে।</p>
</header>

<div class="iostip" id="iostip" hidden>
  <div><b>ফোনে অ্যাপের মতো রাখতে</b> — নিচের <b>Share</b> বোতামে চাপ দিন, তারপর <b>“Add to Home Screen”</b> বেছে নিন। এরপর ইন্টারনেট ছাড়াই খুলবে।</div>
  <button type="button" aria-label="বন্ধ করুন">&times;</button>
</div>

<h2 class="sh">সংকলনগুলো</h2>
<div class="cards">
{chr(10).join(cards)}
</div>

<h2 class="sh mt">পড়ার সময় যা কাজে লাগবে</h2>
<div class="box">
  <ul class="l">
    <li><b>নিজে রুকইয়াহর নিয়ম</b> — প্রতিটি সংকলনের শুরুতেই, ওই উৎসের নিজের দেওয়া নিয়ম — কতক্ষণ, কী নিয়তে, শেষে কী করবেন। দরকার না হলে চাপ দিয়ে গুটিয়ে রাখা যায়।</li>
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
