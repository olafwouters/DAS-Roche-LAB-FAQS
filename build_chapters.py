from pathlib import Path
import hashlib
import json
import re
import subprocess
import pdfplumber

SOURCE_SHA = 'caa010c06b8e46c6fa90673b1ad7c428df8a2a51a7548d8fddad2a3549b4d733'
GROUPS = [
    {'id':'front','title':'Front matter','first':1,'last':11},
    {'id':'1','title':'Working with DNA','first':12,'last':128},
    {'id':'2','title':'Working with RNA','first':129,'last':173},
    {'id':'3','title':'Working with Proteins','first':174,'last':236},
    {'id':'4','title':'Working with Cells','first':237,'last':301},
    {'id':'5','title':'Preparing Buffers and Media','first':302,'last':338},
    {'id':'6','title':'Conversion Tables and Formulas','first':339,'last':351},
    {'id':'7','title':'Addresses, Abbreviations and Index','first':352,'last':384},
    {'id':'back','title':'Back matter','first':385,'last':387},
]

NODE_PATCH = r'''const fs=require('fs'),vm=require('vm');
const payload=JSON.parse(fs.readFileSync(0,'utf8')),groups=payload.groups,chapters=groups.filter(g=>/^\d+$/.test(g.id));
const sandbox={window:{}};vm.runInNewContext(fs.readFileSync('data.js','utf8'),sandbox);const book=sandbox.window.BOOK;if(!book||book.pageCount!==387)throw Error('Unexpected source data format or page count.');
const rangeFor=id=>chapters.find(g=>Number(g.id)===Number(id));
for(const topic of book.topics){const group=rangeFor(topic.chapter);if(!group||topic.pages.some(p=>p<group.first||p>group.last))throw Error('Cross-chapter topic mapping: '+topic.id);}
const alphabetical=book.topics.find(t=>t.id==='topic-7-4-175');if(!alphabetical)throw Error('Original alphabetical index topic missing.');alphabetical.pages=alphabetical.pages.filter(p=>p!==384);
function add(topic,first=false){if(book.topics.some(t=>t.id===topic.id))return;book.topics.push(topic);const chapter=book.chapters.find(c=>Number(c.id)===Number(topic.chapter));if(!chapter)throw Error('Missing chapter '+topic.chapter);if(first)chapter.topics.unshift(topic.id);else chapter.topics.push(topic.id);}
for(const group of chapters){const id=Number(group.id);add({id:'topic-'+id+'-introduction',chapter:id,section:'Chapter '+id,sectionTitle:'Introduction and contents',title:'Chapter introduction and contents',pages:[group.first]},true);const chapter=book.chapters.find(c=>Number(c.id)===id);chapter.pages=Array.from({length:group.last-group.first+1},(_,i)=>group.first+i);}
add({id:'topic-7-trademarks',chapter:7,section:'Source material',sectionTitle:'Trademarks',title:'Trademarks',pages:[384]});
const owners=new Map();for(const topic of book.topics){const group=rangeFor(topic.chapter);for(const page of topic.pages){if(page<group.first||page>group.last)throw Error('Topic outside audited chapter: '+topic.id);if(owners.has(page))throw Error('Page assigned to multiple topics: '+page);owners.set(page,topic);}}
for(const group of chapters)for(let page=group.first;page<=group.last;page++){if(!owners.has(page)||Number(owners.get(page).chapter)!==Number(group.id))throw Error('Missing or wrongly assigned chapter page: '+page);}
const sourceIndex=new Map(book.index.map(p=>[p.page,p]));for(const [page,topic]of owners){const existing=sourceIndex.get(page)||{page,text:payload.introductions[String(page)]||''};sourceIndex.set(page,{...existing,topic:topic.id,chapter:topic.chapter});}book.index=Array.from(sourceIndex.values()).sort((a,b)=>a.page-b.page);
fs.writeFileSync('data.js','window.BOOK='+JSON.stringify(book)+';\n');
const cell=v=>'"'+String(v??'').replace(/"/g,'""')+'"';const header=['chapter','chapter_title','topic_id','section','section_title','topic_title','original_pdf_pages'];const lines=[header.map(cell).join(',')];for(const chapter of book.chapters)for(const id of chapter.topics){const t=book.topics.find(t=>t.id===id);lines.push([t.chapter,chapter.title,t.id,t.section,t.sectionTitle,t.title,t.pages.join(', ')].map(cell).join(','));}fs.writeFileSync('content-map.csv','\uFEFF'+lines.join('\n')+'\n');
const assignments=[];for(const group of groups)for(let page=group.first;page<=group.last;page++)assignments.push({pdfPage:page,group:group.id,topic:owners.get(page)?.id||null});if(assignments.length!==387||new Set(assignments.map(p=>p.pdfPage)).size!==387)throw Error('Full-document partition failed.');
fs.writeFileSync('chapter-coverage-audit.json',JSON.stringify({pdfPages:387,chapterPages:owners.size,topicCount:book.topics.length,crossChapterAssignments:[],unassignedChapterPages:[],groups,pageAssignments:assignments},null,2));
console.log(JSON.stringify({chapterPages:owners.size,totalPdfPages:assignments.length,topicCount:book.topics.length}));
'''

def main():
    if hashlib.sha256(Path('handbook.pdf').read_bytes()).hexdigest() != SOURCE_SHA:
        raise ValueError('Source PDF changed; re-audit chapter boundaries.')
    introductions = {}
    with pdfplumber.open('handbook.pdf') as book:
        if len(book.pages) != 387:
            raise ValueError('Expected all 387 PDF pages.')
        for group in GROUPS:
            if not group['id'].isdigit():
                continue
            text = book.pages[group['first']-1].extract_text() or ''
            if not re.search(r'Chapter\s+' + group['id'] + r'\b', text):
                raise ValueError('Chapter divider does not match: ' + group['id'])
            introductions[str(group['first'])] = text
    subprocess.run(['node','-e',NODE_PATCH], input=json.dumps({'groups':GROUPS,'introductions':introductions}), text=True, check=True)

if __name__ == '__main__':
    main()
