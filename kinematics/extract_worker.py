"""Isolated local PDF/PPTX/image processing. No network or API credentials."""
import argparse
import base64
import io
import json
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree


def process(file,render=None,student=False):
    suffix=file.suffix.lower();pages=[];images=[]
    if suffix=='.pdf':
        from pypdf import PdfReader
        reader=PdfReader(file)
        if reader.is_encrypted:raise ValueError('Unlock the PDF before uploading it.')
        limit=3 if student else 400
        if len(reader.pages)>limit:raise ValueError(f'This workflow accepts at most {limit} pages. Split the PDF first.')
        for i,page in enumerate(reader.pages):
            text=page.extract_text() or ''
            pages.append({'page':i+1,'text':text[:18000],'low_text':len(text.strip())<60})
        selected=list(range(1,len(pages)+1)) if student else [render] if render else []
        if selected:
            import pypdfium2 as pdfium
            document=pdfium.PdfDocument(file)
            for number in selected:
                if not 1<=number<=len(pages):raise ValueError('Unknown PDF page.')
                page=document[number-1];w,h=page.get_size();bitmap=page.render(scale=min(1.5,1200/max(w,h)))
                output=io.BytesIO();bitmap.to_pil().convert('RGB').save(output,format='JPEG',quality=80)
                images.append({'page':number,'data':'data:image/jpeg;base64,'+base64.b64encode(output.getvalue()).decode()})
                bitmap.close();page.close()
            document.close()
    elif suffix=='.pptx':
        with zipfile.ZipFile(file) as archive:
            slides=sorted((n for n in archive.namelist() if re.fullmatch(r'ppt/slides/slide\d+\.xml',n)),key=lambda n:int(re.search(r'slide(\d+)',n)[1]))
            if len(slides)>400:raise ValueError('Split presentations with more than 400 slides.')
            if sum(i.file_size for i in archive.infolist())>250*1024*1024:raise ValueError('Expanded presentation is too large.')
            for i,name in enumerate(slides):
                root=ElementTree.fromstring(archive.read(name));text='\n'.join(n.text or '' for n in root.iter() if n.tag.endswith('}t'))
                pages.append({'page':i+1,'text':text[:18000],'low_text':len(text.strip())<60})
    else:
        from PIL import Image,ImageOps
        Image.MAX_IMAGE_PIXELS=20_000_000
        with Image.open(file) as original:
            image=ImageOps.exif_transpose(original).convert('RGB');image.thumbnail((1200,1200));output=io.BytesIO();image.save(output,format='JPEG',quality=80)
        pages=[{'page':1,'text':'','low_text':True}]
        images=[{'page':1,'data':'data:image/jpeg;base64,'+base64.b64encode(output.getvalue()).decode()}]
    return {'pages':pages,'images':images}


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('file',type=Path);parser.add_argument('--render',type=int);parser.add_argument('--student',action='store_true');args=parser.parse_args()
    try:print(json.dumps(process(args.file,args.render,args.student)))
    except Exception as e:
        print(json.dumps({'error':str(e)[:250]}));sys.exit(1)
