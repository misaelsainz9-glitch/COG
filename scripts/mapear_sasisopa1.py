"""Construye mapas geométricos desde los tres PDF originales, sin publicar su contenido."""
import sys,json,re,hashlib
from pathlib import Path
import fitz
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from pdf_politica import spans

root=Path(__file__).resolve().parents[1]
source=Path(sys.argv[1])
files=[('POL-01','1 POLITICA.pdf','Política'),('PEL-02','2. ID DE PELIGROS.pdf','Identificación de peligros'),('LEG-03','3. REQUISITOS LEGALES.pdf','Requisitos legales')]


def rect_union(boxes):
    r=fitz.Rect(boxes[0])
    for b in boxes[1:]:r|=fitz.Rect(b)
    return list(r)


def chars_lines(page):
    # Some exported PDFs overlay extra spaces over real letters. Ignore those
    # invisible spacers, and group split font runs by baseline with tolerance.
    groups=[]
    for b in page.get_text('rawdict')['blocks']:
        for line in b.get('lines',[]):
            for span in line['spans']:
                for c in span['chars']:
                    group=next((g for g in groups if abs(g[0]-c['origin'][1])<.3),None)
                    if group is None:
                        group=[c['origin'][1],[]];groups.append(group)
                    group[1].append(c)
    result=[]
    for _,chars in groups:
        ink=[c for c in chars if not c['c'].isspace()]
        chars=[c for c in chars if not c['c'].isspace() or not any(n['bbox'][0]<(c['bbox'][0]+c['bbox'][2])/2<n['bbox'][2] for n in ink)]
        chars.sort(key=lambda c:c['bbox'][0])
        part=[]
        for c in chars:
            if part and c['bbox'][0]-part[-1]['bbox'][2]>18:
                result.append(part);part=[]
            part.append(c)
        if part:result.append(part)
    return result


def source_slice(chars,start,end):
    return rect_union([c['bbox'] for c in chars[start:end]])

catalog=[];maps={}
for id,filename,title in files:
    path=source/filename
    with fitz.open(path) as doc:
        first=spans(doc[0]);digits=re.search(r'E-?\s*(\d{5})',doc[0].get_text()).group(1)
        company=next(s['text'] for s in first if 280<s['bbox'][1]<410 and ',' in s['text'] and s['text'].strip().lower().startswith('grupo')).strip()
        words=company.split(',')[0].split();prefix=''.join(words).upper()
        company_pattern=re.compile(r'\b'+r'\s+'.join(map(re.escape,words))+r'(?:[,\s.]*S[\s.]*A[\s.]*DE[\s.]*C[\s.]*V[\s.]*)?',re.I)
        source_signs={item['xref'] for page in doc for item in page.get_image_info(xrefs=True) if (item['width'],item['height']) in ((245,125),(230,128),(167,180))}
        logos={item['xref'] for item in doc[0].get_image_info(xrefs=True) if item['bbox'][1]<100 and item['width']>1}
        author_label=next(s for s in first if s['text'].strip()=='AUTORIZO')
        author_parts=[s for s in first if s['bbox'][0]>300 and author_label['bbox'][1]+8<=s['bbox'][1]<=author_label['bbox'][3]+22]
        author_words=set(' '.join(s['text'] for s in author_parts).upper().split())
        pages=[]
        for pi,page in enumerate(doc):
            ss=spans(page);cover=any(s['text'].strip()=='AUTORIZO' for s in ss)
            info={'size':list(page.rect),'fields':[],'stations':[],'codes':[],'logos':[],'signatures':[],'attendance':[],'sign_image_rects':[]}
            def field(key,boxes,size=9,align=0,**extra):
                if boxes:info['fields'].append({'key':key,'rect':rect_union(boxes),'size':size,'align':align,**extra})
            raw=chars_lines(page)
            station_pattern=re.compile(r'(?:E-?\s*)?'+digits+r'(?!\d)')
            for line in raw:
                text=''.join(c['c'] for c in line)
                for m in station_pattern.finditer(text):
                    info['stations'].append({'rect':source_slice(line,*m.span()),'prefix':m.group()[:-5],'size':9 if line[0]['bbox'][1]<130 else 10})
                for m in re.finditer(r'E-?\s*'+digits+r'\.[A-Z0-9.]+\.R\d+',text):
                    start=m.group().index(digits)
                    info['codes'].append({'rect':source_slice(line,*m.span()),'prefix':m.group()[:start],
                                          'suffix':re.sub(r'R\d+$','R',m.group()[start+5:]),'size':9})
                if not cover:
                    for m in company_pattern.finditer(text):
                        if line[m.start()]['bbox'][1]>160:field('company',[source_slice(line,*m.span())],size=10)
            # Cover and header company/address fields, including an inline company word in a station label.
            limits=(280,410) if cover else (0,145)
            corp=[];address=[];address_started=False
            for si,s in sorted(enumerate(ss),key=lambda pair:(round(pair[1]['bbox'][1],1),pair[1]['bbox'][0])):
                text=s['text'].strip();y=s['bbox'][1];x=s['bbox'][0]
                if not limits[0]<y<limits[1] or not cover and x>page.rect.width*.43:continue
                if text.lower().startswith('carretera'):address_started=True
                if address_started:
                    if text.upper() in ('OCTUBRE 2024','OCTUBRE','2024') or text.startswith(('REVISION','REVISIÓN')):continue
                    if address and y>max(r[3] for r in address)+1.5:continue
                    if not cover and corp and x>max(r[2] for r in corp)+1:continue
                    address.append(s['bbox']);continue
                if 'ESTACION' in text or re.fullmatch(r'E-?\s*'+digits,text):
                    # The legal file has GRUPO in the same source span as ESTACION.
                    if any(w.upper() in text.upper() for w in words):
                        for line in raw:
                            joined=''.join(c['c'] for c in line)
                            at=joined.upper().find(words[0].upper())
                            if at>=0 and abs(line[at]['bbox'][1]-y)<1:
                                info['fields'].append({'key':'company','clear_only':True,'rect':source_slice(line,at,len(line)),'size':8,'align':2})
                    continue
                norm=re.sub('[^A-Z]','',text.upper())
                if text.upper() in ('OCTUBRE 2024','OCTUBRE','2024'):continue
                if norm and any(re.sub('[^A-Z]','',w.upper()) in norm for w in words) or norm in ('S,A,DE,C,V','DECV','SADECV'):
                    corp.append(s['bbox'])
                elif text in ('.',' .') and corp:corp.append(s['bbox'])
            field('company',corp,11 if cover else 8,1 if cover else 2)
            if address and not cover and corp:
                address_rect=rect_union(address)
                address_rect[2]=min(address_rect[2],max(r[2] for r in corp))
                field('address',[address_rect],8,2)
            else:field('address',address,10 if cover else 8,1 if cover else 2)
            for si,s in enumerate(ss):
                text=s['text'].strip();y=s['bbox'][1]
                if re.fullmatch(r'REVISI[OÓ]N:\s*\d+',text):field('revision_label',[s['bbox']],10)
                if (cover and 250<y<500 or not cover and y<145):
                    if re.fullmatch(r'OCTUBRE\s+2024',text,re.I):field('revision_monthyear',[s['bbox']],10)
                    elif text.upper()=='OCTUBRE':field('revision_month',[s['bbox']],8)
                    elif text=='2024':field('revision_year',[s['bbox']],8)
                    elif text=='0' and s['bbox'][0]>page.rect.width*.5:field('revision',[s['bbox']],8)
                if text in ('Convocante:','Facilitador:','Secretario:'):
                    field('secretary' if text=='Secretario:' else 'representative',[(151,y,480,y+13)],9)
                if '--/--/----' in text:field('meeting_date_label',[s['bbox']],8)
            if any('Hora:'==s['text'].strip() for s in ss):
                for s in ss:
                    if s['text'].strip()=='Fecha:' and 145<s['bbox'][1]<260:
                        y=s['bbox'][1];field('meeting_date',[(150,y,228,y+15)],9)
            if cover:
                label=next(s for s in ss if s['text'].strip()=='AUTORIZO')
                names=[s for s in ss if s['bbox'][0]>300 and label['bbox'][1]+8<=s['bbox'][1]<=label['bbox'][3]+22]
                if names:
                    name_rect=rect_union([s['bbox'] for s in names])
                    name_rect[1]=max(name_rect[1],label['bbox'][3]+.2)
                    field('representative',[name_rect],10,1)
                owner_images=[im['bbox'] for im in page.get_image_info(xrefs=True) if im['xref'] in source_signs and im['bbox'][0]>300]
                for r in owner_images:info['signatures'].append({'role':'representative','rect':list(r)})
            elif pi==10 and filename.startswith('1 '):
                owner=[s['bbox'] for s in ss if s['text'].strip().upper() in author_words and 450<s['bbox'][1]<670]
                field('representative',owner,10,1)
                for im in page.get_image_info(xrefs=True):
                    if im['xref'] in source_signs and 200<im['bbox'][0]<360 and im['bbox'][1]<630:info['signatures'].append({'role':'representative','rect':list(im['bbox'])})
            for im in page.get_image_info(xrefs=True):
                if im['xref'] in logos:info['logos'].append({'xref':im['xref'],'rect':list(im['bbox'])})
                if im['xref'] in source_signs:info['sign_image_rects'].append(list(im['bbox']))
            if any(s['text'].strip()=='Puesto' for s in ss) or any(words[-1].casefold() in s['text'].casefold() and s['bbox'][1]>160 for s in ss):
                for table in page.find_tables().tables:
                    data=table.extract()
                    if data and all(any(label in (cell or '') for cell in data[0]) for label in ('Nombre','Puesto','Firma','Teléfono')):
                        for ri,row in enumerate(table.rows[1:6]):
                            cells=[fitz.Rect(r) for r in row.cells if r]
                            unique=[]
                            for r in cells:
                                if not any(r==u for u in unique):unique.append(r)
                            unique.sort(key=lambda r:r.x0)
                            if len(unique)!=5:raise ValueError('Attendance mapping ambiguous')
                            for key,col in [('nombre',1),('puesto',2),('firma',4)]:
                                r=unique[col]+(3,2,-3,-2)
                                info['attendance'].append({'row':ri,'key':key,'rect':list(r)})
                    for row,values in zip(table.rows,data):
                        for r,value in zip(row.cells,values):
                            if r and value:
                                norm=re.sub('[^A-Z]','',value.upper())
                                if norm.startswith(prefix) and norm[len(prefix):] in ('','SADECV') and r[1]>160:
                                    field('company',[r],9,1)
            if filename.startswith('2.') and pi==33:
                suffix=[s['bbox'] for s in ss if 217<s['bbox'][1]<220 and s['bbox'][0]<125 and s['text'].strip().upper() in (',','S.A.','DE','C.V.')]
                if suffix:info['fields'].append({'key':'company','clear_only':True,'rect':rect_union(suffix),'size':9,'align':0})
            pages.append(info)
        maps[id]={'pages':pages,'signature_xrefs':sorted(source_signs)}
        catalog.append({'id':id,'filename':filename,'title':title,'format':'pdf','pages':len(doc),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
        print(id,'mapped',len(pages),'pages','fields',sum(len(p['fields']) for p in pages),'attendee cells',sum(len(p['attendance']) for p in pages),flush=True)
(root/'mapas_pdf.json').write_text(json.dumps(maps,ensure_ascii=False,indent=2)+'\n')
(root/'catalogo_activo.json').write_text(json.dumps({'version':2,'status':'ready_pdf','message':'Base SASISOPA1: tres PDF, 87 páginas. Los campos vacíos conservan el original.','templates':catalog},ensure_ascii=False,indent=2)+'\n')
