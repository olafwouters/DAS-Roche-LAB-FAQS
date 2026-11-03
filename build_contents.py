from pathlib import Path
import hashlib, json, re
import pdfplumber

SHA='caa010c06b8e46c6fa90673b1ad7c428df8a2a51a7548d8fddad2a3549b4d733'
RANGES={1:(12,128),2:(129,173),3:(174,236),4:(237,301),5:(302,338),6:(339,351),7:(352,384)}
REFERENCE_LEAVES={'1.9':[127,128],'2.7':[172,173],'3.6':[235,236],'5.4':[337,338],'6.11':[350,351]}

def extract(pdf,mode,printed):
    raw=[]
    spec=[(4,[(25,176),(177,328),(329,480)],50),(5,[(25,176),(177,328),(329,480)],45)] if mode=='general' else [(n,[(25,248),(253,480)],50 if n==6 else 20)for n in range(6,12)]
    for number,columns,top in spec:
        for left,right in columns:
            for line in pdf.pages[number-1].crop((left,top,right,309)).extract_text_lines(x_tolerance=1,y_tolerance=3,return_chars=False):
                text=line['text'].strip()
                if not text or re.fullmatch('[IVX]+',text):continue
                match=re.search(r'(\d{1,3})\s*$',text)
                reference=int(match.group(1)) if match else None
                label=text[:match.start()] if match else text
                label=re.sub(r'(?:\s*\.\s*){2,}',' ',label).strip().rstrip('.')
                raw.append({'label':label,'printed':reference,'sourcePdfPages':[number],'x':line['x0']-left,'rawLines':[text]})
    rows=[];chapter=0;pending=None
    for i,row in enumerate(raw):
        main=re.match(r'^([1-7])\.(?!\s*\d)',row['label'])
        section=re.match(r'^([1-7])\.\s*(\d{1,2})(?:\.|\s)',row['label'])
        if main or section:chapter=int((main or section).group(1))
        row.update(chapter=chapter,level=0 if main else 1 if section else 2,section=(section.group(1)+'.'+section.group(2)) if section else None)
        if pending:
            pending['label']+=' '+row['label'];pending['printed']=row['printed'];pending['rawLines']+=row['rawLines'];pending['sourcePdfPages']=sorted(set(pending['sourcePdfPages']+row['sourcePdfPages']));row=pending;pending=None
        if row['printed'] is None:
            nxt=raw[i+1] if i+1<len(raw) else None
            if nxt and (row['level']<2 or abs(nxt['x']-row['x'])<3) and not re.match(r'^[1-7]\.\s*\d*\.',nxt['label']) and not row['label'].endswith(':'):
                pending=row;continue
        rows.append(row)
    if pending:rows.append(pending)
    for i,row in enumerate(rows,1):
        row['id']=mode+'-'+str(i);row['pdfPages']=[]
        if row['printed'] is not None:
            if row['level']==0:row['pdfPages']=[RANGES[row['chapter']][0]]
            elif row['section'] in REFERENCE_LEAVES:row['pdfPages']=REFERENCE_LEAVES[row['section']]
            else:row['pdfPages']=printed[str(row['printed'])]
            first,last=RANGES[row['chapter']]
            if any(not first<=p<=last for p in row['pdfPages']):raise ValueError('TOC reference crosses a chapter boundary: '+row['label'])
    expected=53 if mode=='general' else 210
    if len(rows)!=expected or sum(r['level']==0 for r in rows)!=7 or sum(r['level']==1 for r in rows)!=46 or sum(len(r['rawLines'])for r in rows)!=len(raw):
        raise ValueError('TOC completeness audit failed for '+mode)
    return {'rows':rows,'sourceLines':len(raw),'chapters':7,'sections':46}

def main():
    if hashlib.sha256(Path('handbook.pdf').read_bytes()).hexdigest()!=SHA:raise ValueError('Source PDF changed.')
    library=json.loads(Path('library-data.json').read_text(encoding='utf-8'))
    with pdfplumber.open('handbook.pdf') as pdf:
        data={'sourceSha256':SHA,'general':extract(pdf,'general',library['printedPages']),'detailed':extract(pdf,'detailed',library['printedPages'])}
    Path('contents-data.json').write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
    audit={mode:{'rows':len(data[mode]['rows']),'sourceLines':data[mode]['sourceLines'],'chapters':7,'sections':46,'unresolvedReferences':[]}for mode in ['general','detailed']}
    Path('contents-audit.json').write_text(json.dumps(audit,indent=2),encoding='utf-8')
    path=Path('index.html');html=path.read_text(encoding='utf-8');loader='<script src="contents.js"></script>'
    if loader not in html:
        if html.count('</body>')!=1:raise ValueError('Cannot safely install contents view.')
        html=html.replace('</body>',loader+'</body>')
    path.write_text(html,encoding='utf-8')
    print(json.dumps(audit))

if __name__=='__main__':main()
