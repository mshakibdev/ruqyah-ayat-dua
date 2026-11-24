#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""pdftotext-এর আউটপুট থেকে ওয়াটারমার্কের টুকরো ছেঁটে ফেলা"""
import re, subprocess, sys, pathlib

WM = 'alquranicruqyahhealing.com'
WMSET = set()
for n in range(1, 7):                      # ওয়াটারমার্কের সব ছোট টুকরো
    for i in range(len(WM) - n + 1):
        WMSET.add(WM[i:i+n])
WMSET |= {'©', 'Al Quran Ruqyah Healing Center', 'Raqi Faisal Ahmed Sabit'}

DROP = re.compile(
    r'^(alquranicruqyahhealing\.com\s*)+$'
    r'|^©\s*Al Quran Ruqyah Healing Center'
    r'|^Al Quranic Ruqyah Healing Center\s*—'
    r'|^রাকী ফয়সাল আহমেদ সাবিত\s*✦'
)

def clean(path, first=None, last=None):
    cmd = ['pdftotext', '-enc', 'UTF-8']
    if first: cmd += ['-f', str(first)]
    if last:  cmd += ['-l', str(last)]
    cmd += [str(path), '-']
    raw = subprocess.run(cmd, capture_output=True, text=True).stdout

    out, blank = [], False
    for page_i, page in enumerate(raw.split('\f')):
        lines = []
        for ln in page.split('\n'):
            s = ln.strip()
            if not s:
                continue
            if s in WMSET or DROP.search(s):
                continue
            # ওয়াটারমার্কের অক্ষর-কলাম: ছোট, শুধু ASCII, বাংলা/আরবি নেই
            if len(s) <= 6 and re.fullmatch(r'[A-Za-z.]+', s):
                continue
            if re.fullmatch(r'[\d\s.]+', s) and len(s) <= 3:
                continue
            lines.append(re.sub(r'[ \t]{2,}', ' ', s))
        if lines:
            out.append(f'\n<<< পৃষ্ঠা {page_i + (first or 1)} >>>')
            out.extend(lines)
    return '\n'.join(out)

if __name__ == '__main__':
    a = sys.argv[1:]
    print(clean(a[0], *(int(x) for x in a[1:])))
