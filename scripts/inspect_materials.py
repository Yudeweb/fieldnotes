"""Read-only source inventory. Extracted course text stays under ignored var/."""
import hashlib
import json
import re
import sys
import zipfile
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET

from pypdf import PdfReader


def main():
    root = Path(sys.argv[1]).resolve()
    output = Path(sys.argv[2])
    output.mkdir(parents=True, exist_ok=True)
    records = []
    for path in sorted(root.rglob('*')):
        if not path.is_file() or path.name.startswith('.'):
            continue
        relative = str(path.relative_to(root))
        record = {'path': relative, 'extension': path.suffix.lower(), 'bytes': path.stat().st_size}
        pages = []
        try:
            if path.suffix.lower() == '.pdf':
                reader = PdfReader(path)
                pages = [page.extract_text() or '' for page in reader.pages]
                record['page_count'] = len(pages)
                record['low_text_pages'] = [i + 1 for i, text in enumerate(pages) if len(text.strip()) < 80]
                record['encrypted'] = reader.is_encrypted
            elif path.suffix.lower() == '.pptx':
                with zipfile.ZipFile(path) as archive:
                    slides = sorted((n for n in archive.namelist() if re.fullmatch(r'ppt/slides/slide\d+\.xml', n)), key=lambda n: int(re.search(r'slide(\d+)', n).group(1)))
                    for slide in slides:
                        xml = ET.fromstring(archive.read(slide))
                        pages.append('\n'.join(e.text or '' for e in xml.iter('{http://schemas.openxmlformats.org/drawingml/2006/main}t')))
                    record['slide_count'] = len(pages)
                    record['media_count'] = sum(n.startswith('ppt/media/') for n in archive.namelist())
            if pages:
                record['sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
                record['characters'] = sum(len(text) for text in pages)
                record['text_file'] = hashlib.sha256(relative.encode()).hexdigest()[:16] + '.json'
                (output / record['text_file']).write_text(json.dumps({'source': relative, 'pages': pages}, ensure_ascii=False, indent=2))
        except Exception as exc:
            record['error'] = str(exc)
        records.append(record)
    manifest = {'source_root': str(root), 'files': records}
    (output / 'inventory.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
    print(json.dumps({'files': len(records), 'types': dict(Counter(r['extension'] for r in records)), 'pdf_pages': sum(r.get('page_count', 0) for r in records), 'pptx_slides': sum(r.get('slide_count', 0) for r in records), 'bytes': sum(r['bytes'] for r in records), 'errors': [r for r in records if 'error' in r]}, indent=2))
    for r in records:
        if 'text_file' in r:
            pages = json.loads((output / r['text_file']).read_text())['pages']
            print('\nFILE', r['path'], 'PAGES', len(pages), 'LOW-TEXT', r.get('low_text_pages', []))
            print(re.sub(r'\s+', ' ', ' '.join(pages[:2]))[:950])


if __name__ == '__main__':
    main()
