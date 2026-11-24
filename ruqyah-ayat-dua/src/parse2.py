import re, json
BN='০১২৩৪৫৬৭৮৯'
def isar(s): return bool(re.search(r'[؀-ۿ]',s))

# ---------- style A : ==== header ====  (Ayatut Tair, Ruqyah Duasomuho) ----------
def parseA(path):
    lines=open(path,encoding='utf-8').read().split('\n'); n=len(lines)
    chapters=[]; cur=None; items=[]; i=0
    while i<n:
        L=lines[i]
        if L.startswith('####') and i+2<n and lines[i+2].startswith('####'):
            cur=lines[i+1].strip(); chapters.append(cur); i+=3; continue
        if L.startswith('====') and i+2<n and lines[i+2].startswith('===='):
            head=lines[i+1].strip()
            if head and head[0] in BN:
                it={'ch':cur,'head':head,'ar':[],'tr':'','mn':'','rep':[],'note':''}
                j=i+3; last=None
                while j<n:
                    M=lines[j]
                    if M.startswith('====') and j+2<n and lines[j+2].startswith('===='): break
                    if M.startswith('####') or M.startswith('*****'): break
                    s=M.strip()
                    if s.startswith('উচ্চারণ:'): it['tr']=s.split(':',1)[1].strip(); last='tr'
                    elif s.startswith('অর্থ:'): it['mn']=s.split(':',1)[1].strip(); last='mn'
                    elif s.startswith('পুনরাবৃত্তি:'): it['rep'].append(s.split(':',1)[1].strip()); last=None
                    elif s.startswith('│'):
                        t=s.lstrip('│').strip()
                        if t and not t.startswith('**'): it['rep'].append(t)
                        last=None
                    elif s.startswith('┌') or s.startswith('└'): last=None
                    elif s.startswith('**'): it['note']+=' '+s.strip('* '); last=None
                    elif isar(s): it['ar'].append(s); last=None
                    elif s and last in ('tr','mn'): it[last]+=' '+s
                    elif not s: last=last
                    j+=1
                items.append(it); i=j; continue
        i+=1
    return chapters,items

# ---------- style B : header then ---- line  (Kobor ayat / dua) ----------
def parseB(path):
    lines=open(path,encoding='utf-8').read().split('\n'); n=len(lines)
    sections=[]; cur=None; items=[]; i=0
    while i<n:
        L=lines[i]
        if L.startswith('====') and i+2<n and lines[i+2].startswith('===='):
            h=lines[i+1].strip()
            if h.startswith('সেকশন'): cur=h; sections.append(h)
            i+=3; continue
        s=L.strip()
        if s and s[0] in BN and i+1<n and lines[i+1].startswith('----'):
            m=re.match(r'^([০-৯]+)\s*·\s*(.*?)\s*\[\s*(.*?)\s*\]\s*$', s)
            if m: num,title,cnt=m.group(1),m.group(2),m.group(3)
            else: num,title,cnt=s.split('·')[0].strip(),s,''
            it={'ch':cur,'num':num,'title':title,'cnt':cnt,'ar':[],'tr':'','mn':'','niyat':'','src':''}
            j=i+2; last=None
            while j<n:
                M=lines[j]; t=M.strip()
                if t and t[0] in BN and j+1<n and lines[j+1].startswith('----'): break
                if M.startswith('====') or M.startswith('*****'): break
                if t.startswith('উচ্চারণ:'): it['tr']=t.split(':',1)[1].strip(); last='tr'
                elif t.startswith('অর্থ:'): it['mn']=t.split(':',1)[1].strip(); last='mn'
                elif t.startswith('নিয়ত:'): it['niyat']=t.split(':',1)[1].strip(); last='niyat'
                elif t.startswith('উৎস:'): it['src']=t.split(':',1)[1].strip(); last='src'
                elif t.startswith('↑'): last=None
                elif isar(t): it['ar'].append(t); last=None
                elif t and last: it[last]+=' '+t
                j+=1
            items.append(it); i=j; continue
        i+=1
    return sections,items

out={}
for f,fn,key in [('Ayatut_Tair.txt',parseA,'tair'),('Ruqyah_Duasomuho.txt',parseA,'dua'),
                 ('Kobor_Jadur_Ayat.txt',parseB,'kayat'),('Kobor_Jadur_Dua.txt',parseB,'kdua')]:
    ch,it=fn(f); out[key]={'chapters':ch,'items':it}
    bad=[x.get('head') or x.get('title') for x in it if not x['ar']]
    print(f'{key:6} অধ্যায়/সেকশন {len(ch)}  আইটেম {len(it)}' + ('  ⚠ আরবি নেই: '+str(bad) if bad else ''))
json.dump(out,open('/tmp/claude-0/-home-claude/6e916ca0-b256-52d6-8ec4-1b35c315a69e/scratchpad/data.json','w'),ensure_ascii=False,indent=1)
print('\n→ data.json লেখা হয়েছে')
