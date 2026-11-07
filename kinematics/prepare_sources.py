"""Render only explicitly allowlisted theory pages; never serve mixed solution PDFs."""
import argparse
from pathlib import Path
import pypdfium2 as pdfium
from content import SOURCE_ROOT, SOURCES

parser=argparse.ArgumentParser()
parser.add_argument('--materials',type=Path,default=Path(SOURCE_ROOT))
args=parser.parse_args()
out=Path(__file__).resolve().parents[1]/'var/private/kinematics/source-pages'
out.mkdir(parents=True,exist_ok=True)
for id,source in SOURCES.items():
    document=pdfium.PdfDocument(args.materials/source['file'])
    for page_number in source['pages']:
        page=document[page_number-1]
        bitmap=page.render(scale=1.6)
        bitmap.to_pil().save(out/f'{id}-{page_number}.png')
        bitmap.close();page.close()
    document.close()
print(f'Rendered {sum(len(s["pages"]) for s in SOURCES.values())} allowlisted lecture pages to {out}')
