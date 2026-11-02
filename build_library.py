from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import csv, hashlib, io, json, os, re, subprocess, tempfile, unicodedata
import pdfplumber
from pdfplumber.utils import extract_text

SOURCE_SHA = 'caa010c06b8e46c6fa90673b1ad7c428df8a2a51a7548d8fddad2a3549b4d733'

def norm(s):
    return re.sub(r'[^\w]+', ' ', unicodedata.normalize('NFKC', s).casefold()).strip()

def extract_native(source='handbook.pdf', check_images=True):
    source = Path(source)
    if hashlib.sha256(source.read_bytes()).hexdigest() != SOURCE_SHA:
        raise ValueError('PDF changed: re-audit printed page mappings before deployment.')
    records, footers, index_rows = [], {}, []
    with pdfplumber.open(source) as book:
        if len(book.pages) != 387:
            raise ValueError('Expected all 387 source pages.')
        for number, page in enumerate(book.pages, 1):
            if check_images and not Path(f'pages/{number:03d}.webp').is_file():
                raise FileNotFoundError(f'pages/{number:03d}.webp')
            records.append({'page': number, 'native': page.extract_text(x_tolerance=1, y_tolerance=3) or ''})
            chars = sorted((c for c in page.chars if c['x0'] > 449 and abs(c['top'] - 288.049) < .08 and abs(c['size'] - 9.99) < .1), key=lambda c:c['x0'])
            footer = ''.join(c['text'] for c in chars).strip()
            if re.fullmatch(r'\d{1,3}', footer):
                footers[number] = int(footer)
            if 365 <= number <= 383:
                for line in page.crop((25, 20, 480, 315)).extract_text_lines(x_tolerance=1, y_tolerance=5, return_chars=True):
                    if not line['text'].startswith(('Addresses, Abbreviations and Index', '7.4. Alphabetical index', 'The colors of the topics')):
                        index_rows.append((number, line))
    if len(footers) != 178 or list(footers.values()) != sorted(set(footers.values())):
        raise ValueError('Printed footer validation failed.')
    printed = {str(value): [page-1, page] for page, value in footers.items()}
    printed['59'] = [127, 128]
    entries, letter = [], ''
    for source_page, line in index_rows:
        raw = line['text'].strip()
        if re.fullmatch('[A-Z]', raw):
            letter = raw
            continue
        chars = sorted(line['chars'], key=lambda c:c['x0'])
        reference = ''.join(c['text'] for c in chars if c['x0'] >= 430).strip()
        refs = [int(n) for n in re.findall(r'\d+', reference)] if re.fullmatch(r'[\d,\s\-–]+', reference) else []
        label = extract_text([c for c in chars if c['x0'] < 430], x_tolerance=1, y_tolerance=5).strip() if refs else raw
        match = re.search(r'\bsee\s+(.+?)[).]*$', label, re.I)
        entries.append({'id': f'idx-{len(entries)+1}', 'letter': letter, 'label': label, 'raw': raw, 'indent': max(0, round(line['x0']-31.228, 2)), 'sourcePdfPage': source_page, 'references': refs, 'targets': [{'printed': n, 'pdfPages': printed[str(n)]} for n in refs], 'see': match.group(1).strip().rstrip(')') if match else None})
    for entry in entries:
        entry['crossTargets'] = [other['id'] for other in entries if other['id'] != entry['id'] and entry['see'] and norm(other['label']).startswith(norm(entry['see']))]
        if entry['see'] and not entry['crossTargets']:
            raise ValueError(f'Unresolved cross-reference: {entry["label"]}')
    if len(entries) != 344 or sum(bool(e['references']) for e in entries) != 335 or sum(bool(e['see']) for e in entries) != 8:
        raise ValueError('Index row audit failed; refusing to omit source entries.')
    for entry in entries:
        for target in entry['targets']:
            for n in target['pdfPages']:
                records[n-1].setdefault('indexTerms', []).append(entry['label'])
    return {'pageCount': 387, 'sourceSha256': SOURCE_SHA, 'pages': records, 'entries': entries, 'printedPages': printed, 'originalIndexPages': list(range(365,384)), 'mappingNotes': ['Printed page 59 is the unnumbered reference leaf at PDF pages 127–128. Source index references are preserved, including any errors in the published index.']}

def ocr_page(number):
    cache = Path('.ocr-cache') / f'{SOURCE_SHA}-180-eng-psm3-{number:03d}.json'
    if cache.is_file():
        result = json.loads(cache.read_text())
        if result.get('page') == number and result.get('completed') is True:
            return result
    with tempfile.TemporaryDirectory() as tmp:
        prefix = Path(tmp) / 'page'
        subprocess.run(['pdftoppm','-f',str(number),'-l',str(number),'-singlefile','-r','180','-png','handbook.pdf',str(prefix)], check=True, capture_output=True, timeout=180)
        result = subprocess.run(['tesseract',str(prefix)+'.png','stdout','-l','eng','--psm','3','tsv'], check=True, capture_output=True, text=True, timeout=180, env={**os.environ, 'OMP_THREAD_LIMIT':'1'})
    lines, words, low = {}, 0, 0
    for row in csv.DictReader(io.StringIO(result.stdout), delimiter='\t'):
        text = (row.get('text') or '').strip()
        if row.get('level') != '5' or not text:
            continue
        key = tuple(row[k] for k in ['block_num','par_num','line_num'])
        lines.setdefault(key, []).append(text)
        words += 1
        low += float(row['conf']) < 60
    result = {'page': number, 'completed': True, 'text': '\n'.join(' '.join(line) for line in lines.values()), 'words': words, 'lowConfidenceWords': low}
    cache.parent.mkdir(exist_ok=True)
    cache.write_text(json.dumps(result, ensure_ascii=False), encoding='utf-8')
    return result

def main():
    data = extract_native()
    completed = []
    with ThreadPoolExecutor(max_workers=2) as pool:
        for result in pool.map(ocr_page, range(1,388)):
            data['pages'][result['page']-1]['ocr'] = result['text']
            data['pages'][result['page']-1]['ocrLowConfidenceWords'] = result['lowConfidenceWords']
            completed.append(result['page'])
            print(f'OCR complete: {len(completed)}/387', flush=True)
    if completed != list(range(1,388)):
        raise ValueError('OCR coverage incomplete; deployment blocked.')
    data['audit'] = {'pdfPages': 387, 'ocrPagesCompleted': len(completed), 'indexRows': len(data['entries']), 'numericIndexRows': 335, 'seeCrossReferences': 8, 'unresolvedReferences': [], 'emptyAfterExtractionAndOCR': [p['page'] for p in data['pages'] if not (p['native']+p['ocr']).strip()], 'lowConfidencePages': [p['page'] for p in data['pages'] if p['ocrLowConfidenceWords'] > 0]}
    Path('library-data.json').write_text(json.dumps(data, ensure_ascii=False, separators=(',',':')), encoding='utf-8')
    Path('coverage-audit.json').write_text(json.dumps(data['audit'], indent=2), encoding='utf-8')
    html_path = Path('index.html')
    html = html_path.read_text(encoding='utf-8')
    loader = '<script src="library.js"></script>'
    if loader not in html:
        if html.count('</body>') != 1:
            raise ValueError('Cannot safely install library loader.')
        html = html.replace('</body>', loader + '</body>')
    html = html.replace('Search and question lookup use the PDF’s extracted text only to locate relevant topics/pages.', 'Search and question lookup use native PDF text plus OCR from all 387 pages. All common words and single-letter terms remain searchable. The clickable index preserves original entries and opens all PDF parts for each printed reference.')
    html = html.replace('Results show topic labels and original-page thumbnails', 'Results show PDF page references and original-page thumbnails')
    html_path.write_text(html, encoding='utf-8')

if __name__ == '__main__':
    main()
