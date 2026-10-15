"""Calibra los espacios contra originales privados y registra sólo geometría."""
import sys,json,re,hashlib,unicodedata
from pathlib import Path
import fitz
ROOT=Path(__file__).resolve().parents[1]
BASE=Path(sys.argv[1]);ORIG=BASE/'originales';CLEAN=BASE/'limpios'
ROMANS=['I','II','III','IV','V','VI','VII','VIII','IX','X','XI','XII','XIII','XIV','XV','XVI','XVII','XVIII']
META=json.loads((ROOT/'campos_sasisopa_18.json').read_text())
# The reference identities are read locally; never exported to the map.
def norm(v):return ''.join(c for c in unicodedata.normalize('NFD',v.upper()) if c.isalnum())
def spans(p):return [s for b in p.get_text('dict')['blocks'] for l in b.get('lines',[]) for s in l['spans'] if s['text'].strip()]
def union(rs):
 r=fitz.Rect(rs[0])
 for x in rs[1:]:r|=fitz.Rect(x)
 return list(r)
def matches(p,entity):
 chars=[];all_chars=[];positions={}
 for b in p.get_text('rawdict')['blocks']:
  for line in b.get('lines',[]):
   for sp in line['spans']:
    for c in sp['chars']:
     positions[id(c)]=len(all_chars);all_chars.append(c)
     for v in norm(c['c']):chars.append((v,c,sp))
 text=''.join(c[0] for c in chars);start=0
 while (at:=text.find(norm(entity),start))>=0:
  segment=chars[at:at+len(norm(entity))];parts={}
  if entity.isdigit():
   first=positions[id(segment[0][1])];last=positions[id(segment[-1][1])]
   before=all_chars[first-1]['c'] if first else ''
   after=all_chars[last+1]['c'] if last+1<len(all_chars) else ''
   if (before.isalnum() and before.upper()!='E') or after.isdigit():
    start=at+len(norm(entity));continue
  for _,c,s in segment:
   k=round(c['origin'][1],1)
   if k not in parts:parts[k]=[[],s]
   parts[k][0].append(c['bbox'])
  for order,(rs,s) in enumerate(parts.values()):
   extra={'flow':hashlib.sha256((norm(entity)+':'+str(at)).encode()).hexdigest()[:12],'flow_order':order} if len(parts)>1 else {}
   yield union(rs),{**s,**extra}
  start=at+len(norm(entity))
# Read known identities from their labelled reference rows.
with fitz.open(ORIG/'PROCEDIMIENTO II.pdf') as d:
 team=d[32].find_tables().tables
 table=next(t for t in team if any('Cargo/especialidad' in (c or '') for row in t.extract()[:2] for c in row))
 rows=table.extract();names=[row[0].strip() for row in rows[1:7]]
 station_digits=re.search(r'E-?\s*(\d{5})',d[0].get_text()).group(1)
 main_company=next(s['text'].strip() for s in spans(d[0]) if 280<s['bbox'][1]<410 and 'AUTO SERVICIO' in s['text'])
with fitz.open(ORIG/'PROCEDIMIENTO V.pdf') as d:
 source_text=d[15].get_text()
 mail=re.search(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}',source_text).group()
 phone=re.search(r'(?<!\d)\d{10}(?!\d)',source_text).group()
 # full registered station address from cover, allowing line breaks
 ss=spans(d[0]);ads=[s['text'].strip() for s in ss if 300<s['bbox'][1]<450 and (s['text'].strip().startswith('CARRETERA') or re.fullmatch(r'C[.]?\s*P[.]?\s*\d{5}',s['text'].strip()))]
 address=' '.join(ads)
initials=[''.join(norm(word)[0] for word in name.split() if norm(word)) for name in names]
company_first=norm(main_company.split()[0])
address_terms={norm(w) for w in address.split() if len(norm(w))>4}
source_images=list(json.loads((BASE/'imagenes.json').read_text()).items())
logo_hashes={source_images[i][0] for i in (0,94,130)}
keep={0,34,43,44,45,67,94,106,111,112,113,117,122,130,131,132,133,136,145}
sign_hashes={key for i,(key,_) in enumerate(source_images) if i not in keep}
MONTHS=['ENERO','FEBRERO','MARZO','ABRIL','MAYO','JUNIO','JULIO','AGOSTO','SEPTIEMBRE','OCTUBRE','NOVIEMBRE','DICIEMBRE']
roles=['representante_legal','representante_tecnico','encargado_estacion','jefe_operaciones','secretario_hazop','lider_hazop']
catalog=[];maps={}
for roman,module in zip(ROMANS,META['modules']):
 filename=f'PROCEDIMIENTO {roman}.pdf';path=CLEAN/filename
 with fitz.open(ORIG/filename) as source,fitz.open(path) as cleaned:
  pages=[];table_number=0;initial_index=0
  for pi,page in enumerate(source):
   ss=spans(page);cover=any(s['text'].strip()=='AUTORIZO' for s in ss)
   info={'size':list(page.rect),'slots':[],'tables':[]}
   def add(key,rect,s=None,*,size=None,align=0,min_size=None,transform='',kind='text',clear=True):
    r=fitz.Rect(rect)
    if r.is_empty:return
    font=(s or {}).get('font','ArialMT').split('+')[-1]
    pt=size or (s or {}).get('size',9)
    slot={'id':f'{roman}.{pi+1}.{len(info["slots"])}','key':key,'rect':list(r),'font':font,'size':round(pt,2),'min_size':round(min_size if min_size is not None else pt,2),'align':align,'kind':kind,'clear':clear}
    if s and s.get('flow'):slot.update({k:s[k] for k in ('flow','flow_order')})
    if transform=='digits':slot['erase_rect']=list(r);slot['rect'][2]+=.25
    if transform:slot['transform']=transform
    info['slots'].append(slot)
   for rect,s in matches(page,station_digits):add('estacion.numero',rect,s,transform='digits')
   # Header/cover company and address use independent original blocks.
   y0,y1=(280,425) if cover else (0,130)
   corp=[];addr=[]
   for s in ss:
    t=s['text'].strip();n=norm(t);x,y,_,_=s['bbox']
    if not y0<y<y1 or (not cover and x>page.rect.width*.47):continue
    if n in (company_first,company_first+'AUTO','AUTOSERVICIOSA','AUTOSERVICIOS','ADECV','DECV',norm(main_company)):corp.append(s['bbox'])
    if any(k in n for k in address_terms):addr.append(s['bbox'])
   if corp:
    r=union(corp);style=next((v for v in ss if list(v['bbox'])==list(corp[0])),{'font':'Arial-BoldMT','size':11.04}) if cover else {'font':'Arial-BoldMT','size':9}
    if not cover and addr and min(v[1] for v in addr)>=r[3]:r[3]=max(r[3],min(v[1] for v in addr)-2)
    add('estacion.razon_social',r,style,size=9 if not cover else style['size'],min_size=8 if not cover else style['size'],align=2 if not cover else 1)
   if addr:
    r=union(addr)
    if not cover and corp:r[2]=min(r[2],max(v[2] for v in corp))
    style=next((v for v in ss if list(v['bbox'])==list(addr[0])),{'font':'ArialMT','size':11.04}) if cover else {'font':'ArialMT','size':9}
    add('estacion.direccion',r,style,size=9 if not cover else style['size'],min_size=8,align=2)
   # Body company/address, leaving the header to the blocks above.
   for rect,s in matches(page,main_company):
    if rect[1]>160 and not cover:add('estacion.razon_social',rect,s)
   for rect,s in matches(page,address):
    if rect[1]>160 and not cover:add('rol.representante_tecnico.domicilio' if roman=='V' and pi==15 and rect[0]>page.rect.width*.47 else 'estacion.direccion',rect,s,min_size=8,align=0 if roman=='V' and pi==15 and rect[0]>page.rect.width*.47 else 2)
   for s in ss:
    t=s['text'].strip();n=norm(t);x,y,x1,y1=s['bbox']
    if (not cover and y<145 or cover and 240<y<540):
     if t=='0' and x>page.rect.width*.5:add('documento.revision',[x-8,y,x1+8,y1],s,align=1)
     if re.fullmatch(r'REVISI[OÓ]N:\s*\d+',t):add('documento.revision',s['bbox'],s,transform='revision_label')
     if t.upper() in MONTHS:add('documento.fecha_revision',[max((x+x1)/2-37,0),y,min((x+x1)/2+37,page.rect.width),y1],s,align=1,transform='month_upper' if t.isupper() else 'month')
     if re.fullmatch(r'20\d{2}',t):add('documento.fecha_revision',s['bbox'],s,transform='year')
     if re.fullmatch(r'(?:'+ '|'.join(MONTHS)+r')\s+20\d{2}',t,re.I):add('documento.fecha_revision',[x-45,y,x1+45,y1],s,align=1,transform='monthyear')
    for label,role in [('Convocante:','convocante'),('Facilitador:','facilitador'),('Secretario:','secretario_reunion')]:
     if t==label:add(f'rol.{role}.nombre',[x1+6,y,min(page.rect.width-55,x1+300),y1+2],s,size=9,min_size=9)
    if t=='Fecha:' and 145<y<600 and any(q['text'].strip()=='Hora:' and abs(q['bbox'][1]-y)<8 for q in ss):
     stop=min(q['bbox'][0] for q in ss if q['text'].strip()=='Hora:' and abs(q['bbox'][1]-y)<8)
     add('documento.fecha_reunion',[x1+5,y,stop-5,y1+2],s,size=9,min_size=9)
   # Exact source glyph rectangles, rather than estimating code widths.
   for block in page.get_text('rawdict')['blocks']:
    for line in block.get('lines',[]):
     for sp in line['spans']:
      rawtext=''.join(c['c'] for c in sp['chars'])
      for m in re.finditer(r'(?<=\.R)\d+',rawtext):
       r=union([c['bbox'] for c in sp['chars'][m.start():m.end()]])
       others=[c['bbox'][0] for bl in page.get_text('rawdict')['blocks'] for li in bl.get('lines',[]) for run in li['spans'] for c in run['chars'] if not c['c'].isspace() and c['bbox'][0]>=r[2]-.01 and c['bbox'][1]<r[3] and c['bbox'][3]>r[1]]
       r[2]=max(r[2],min(r[2]+16,min(others,default=page.rect.width-20)-.15))
       add('documento.revision',r,sp)
       code=re.search(r'(?:^|\.)(\d{1,2})\.(?:PO|RE|P0)\.[0-9.]+R\d+$',re.sub(r'\s+','',rawtext[:m.end()]))
       if code and 1<=int(code.group(1))<=18:info['slots'][-1]['reference_doc']=ROMANS[int(code.group(1))-1]
       elif cover or r[1]<145:info['slots'][-1]['reference_doc']=roman
       else:info['slots'][-1]['revision_scope']='global_only'
   # Independent designation/acceptance dates in their actual letters.
   if roman=='V' and pi in (15,16):
    date_match=re.search(r'\b(\d{1,2}\s+de\s+[A-Za-zÁÉÍÓÚáéíóú]+\s+(?:de\s+)?20\d{2})',page.get_text(),re.I)
    if date_match:
     for rect,run in matches(page,date_match.group(1)):
      add('documento.fecha_designacion' if pi==15 else 'documento.fecha_aceptacion',rect,run)
   # Names in the existing cover and footer blocks, without adding blocks.
   if cover:
    for q in ss:
     if q['text'].strip()=='EQUIPO DE TRABAJO' and q['bbox'][1]>500:add('rol.elabora.nombre',[max(40,(q['bbox'][0]+q['bbox'][2])/2-103),q['bbox'][1],min(page.rect.width/2-4,(q['bbox'][0]+q['bbox'][2])/2+103),q['bbox'][3]],q,align=1)
   else:
    for q in ss:
     text=norm(q['text']);role='elabora' if text=='ELABORO' else 'revisa' if text=='REVISADOPOR' else 'autoriza' if text=='APROBADOPOR' else ''
     if not role or q['bbox'][1]<page.rect.height*.65:continue
     cx=(q['bbox'][0]+q['bbox'][2])/2;left=max(20,cx-77);right=min(page.rect.width-20,cx+77);top=q['bbox'][3]+1
     after=[a['bbox'][1] for a in ss if a['bbox'][0]<right and a['bbox'][2]>left and top<a['bbox'][1]<top+75]
     bottom=min(after,default=top+10)-1
     if bottom-top>=8.8:add(f'rol.{role}.nombre',[left,top,right,bottom],q,size=8,min_size=8,align=1)
   # Body and cover personal identities. Same prior person is mapped by function.
   for ni,name in enumerate(names):
    if ni in (2,3):continue  # repeated reference name handled by ordered occurrences
    occurrences=list(matches(page,name))
    if not occurrences:continue
    if ni==0:role='autoriza' if cover else 'representante_legal'
    elif ni==1:role='representante_tecnico'
    else:role=roles[ni]
    for occurrence,(rect,s) in enumerate(occurrences):
     if roman=='II' and pi==32 and ni==1:role=['representante_tecnico','encargado_estacion','jefe_operaciones'][min(occurrence,2)]
     if roman=='V' and pi==5:
      if ni==0:role='alta_direccion' if rect[1]<300 else 'representante_legal'
      elif ni==1:role=['representante_tecnico','encargado_estacion','jefe_operaciones'][min(occurrence,2)]
     if cover:
      label=next(q for q in ss if q['text'].strip()=='AUTORIZO');rect[1]=max(rect[1],label['bbox'][3]+.2)
     if cover:
      center=(rect[0]+rect[2])/2;rect[0]=max(page.rect.width/2+4,center-103);rect[2]=min(page.rect.width-40,center+103)
     add(f'rol.{role}.nombre',rect,s,align=1 if cover else 0)
   if roman=='V' and pi==15:
    for run in ss:
     if norm(run['text'])=='AUXILIARADMINISTRATIVO':add('rol.representante_tecnico.puesto',run['bbox'],run)
    for value,key in [(mail,'correo'),(phone,'telefono')]:
     for rect,s in matches(page,value):add(f'rol.representante_tecnico.{key}',rect,s)
   if roman=='II' and pi==32:
    t=next(t for t in page.find_tables().tables if any('Cargo/especialidad' in (c or '') for row in t.extract()[:2] for c in row))
    for ri,row in enumerate(t.rows[1:7]):
     cell=row.cells[5]
     if not cell:continue
     r=fitz.Rect(cell)+(3,2,-3,-2)
     info['slots']=[slot for slot in info['slots'] if not (slot['key']=='estacion.razon_social' and fitz.Rect(slot['rect']).intersects(r))]
     add(f'rol.{roles[ri]}.empresa',r,size=9,min_size=9,align=1)
     if ri<4:info['slots'][-1]['fallback_key']='estacion.razon_social'
   if roman=='II' and pi>=32:
    for word in page.get_text('words'):
     n=norm(word[4])
     if n not in (initials[0],initials[1],initials[4],initials[5]):continue
     if n==initials[0]:initial_index=0;role=roles[0]
     elif n==initials[1]:initial_index+=1;role=roles[min(initial_index,3)]
     elif n==initials[4]:role=roles[4]
     else:role=roles[5]
     add(f'rol.{role}.iniciales',word[:4],size=8,min_size=8)
   # Logos and original signature spaces; avoid covering printed labels.
   sign_boxes={}
   for im in page.get_image_info(hashes=True):
    digest=im['digest'].hex();r=fitz.Rect(im['bbox'])
    if digest in logo_hashes:add('estacion.logo',r,kind='image',clear=True)
    if digest in sign_hashes and im['width']>60:
     if cover:role='elabora' if r.x0<300 else 'autoriza'
     elif roman=='I' and pi==10 and 180<r.x0<380:role='representante_legal'
     elif roman=='V' and pi==15:role='representante_legal'
     elif roman=='V' and pi==16:role='representante_tecnico'
     elif r.y0>page.rect.height*.65:role='elabora' if r.x0<page.rect.width*.35 else 'revisa' if r.x0<page.rect.width*.65 else 'autoriza'
     else:continue
     sign_boxes.setdefault(role,[]).append(list(r))
   for role,boxes in sign_boxes.items():
    r=fitz.Rect(union(boxes));texts=[q['bbox'] for q in ss if q['bbox'][0]<r.x1 and q['bbox'][2]>r.x0 and q['bbox'][1]>=r.y0 and q['bbox'][1]<r.y1]
    if texts:r.y1=min(b[1] for b in texts)-2
    if r.height>=12:add(f'rol.{role}.firma',r,kind='image',clear=False)
   # Detect attendance tables from their real cell geometry.
   if roman!='XV' and any('nombre' in s['text'].lower() for s in ss) and any('firma' in s['text'].lower() for s in ss) and any('puesto' in s['text'].lower() for s in ss):
    for ti,t in enumerate(page.find_tables().tables):
     data=t.extract();header_i=next((i for i,row in enumerate(data[:3]) if all(any(term in norm(v or '') for v in row) for term in ('NOMBRE','PUESTO','FIRMA'))),None)
     if header_i is None:continue
     header=data[header_i];cells=t.rows[header_i].cells;columns={}
     for k,term in [('nombre','NOMBRE'),('puesto','PUESTO'),('telefono','TELEFONO'),('firma','FIRMA')]:
      ci=next((i for i,v in enumerate(header) if term in norm(v or '') and cells[i]),None)
      if ci is not None:columns[k]=(cells[ci][0]+cells[ci][2])/2
     table_id=f'{roman}.{pi+1}.{ti}';count=0
     for ri,row in enumerate(t.rows[header_i+1:]):
      if row.bbox[3]-row.bbox[1]<10:continue
      for k,center in columns.items():
       target=next((r for r in row.cells if r and r[0]<=center<=r[2]),None)
       if target:
        r=fitz.Rect(target)+(2,2,-2,-2)
        add(f'tabla.{table_id}.{ri}.{k}',r,size=9,min_size=9,kind='image' if k=='firma' else 'text',clear=k!='firma')
      count=max(count,ri+1)
     if count:info['tables'].append({'id':table_id,'rows':count,'columns':list(columns),'page':pi+1})
   # Slots for header data that is baked into three schedule images.
   raster_specs={'IV':(12,106,(211,4,753,106),(1442,63,1500,79)),'XI':(14,131,(137,4,510,58),(1193,31,1232,42)),'XIII':(15,34,(195,18,549,63),(1575,40,1607,51))}
   if roman in raster_specs and pi==raster_specs[roman][0]:
    _,idx,area,code=raster_specs[roman];ref=source_images[idx][1]
    im=next(i for i in page.get_image_info() if i['width']==ref['w'] and i['height']==ref['h']);bounds=fitz.Rect(im['bbox'])
    def projected(a):return fitz.Rect(bounds.x0+a[0]/ref['w']*bounds.width,bounds.y0+a[1]/ref['h']*bounds.height,bounds.x0+a[2]/ref['w']*bounds.width,bounds.y0+a[3]/ref['h']*bounds.height)
    logo_area={'IV':(15,7,190,190),'XI':(8,6,126,130),'XIII':(8,8,188,143)}[roman]
    add('estacion.logo',projected(logo_area),kind='image',clear=True)
    r=projected(area);line=r.height/3
    for j,key in enumerate(('estacion.numero','estacion.razon_social','estacion.direccion')):
     box=fitz.Rect(r.x0,r.y0+j*line,r.x1,r.y0+(j+1)*line);pt=min(8,line*.68)
     if roman=='XIII' and key=='estacion.direccion':box.y1=projected((195,18,549,76)).y1
     add(key,box,size=pt,min_size=pt,align=2 if key=='estacion.direccion' else 1,clear=False)
    add('estacion.numero',projected(code),size=3,min_size=3,clear=False)
   aliases={}
   for slot in info['slots']:
    if slot.get('flow'):
     group=slot['flow'];aliases.setdefault(group,'G'+str(len(aliases)+1));slot['flow']=aliases[group]
   pages.append(info)
  entry={k:module[k] for k in ('id','title','filename','pages')};entry['sha256']=hashlib.sha256(path.read_bytes()).hexdigest();entry['format']='pdf'
  catalog.append(entry);maps[roman]={'pages':pages}
  print(roman,len(pages),'pages',sum(len(p['slots']) for p in pages),'slots',flush=True)
(ROOT/'catalogo18.json').write_text(json.dumps({'version':3,'status':'ready_pdf','engine':'sasisopa18','templates':catalog,'message':'Base limpia SASISOPA: 18 PDF, 523 páginas.'},ensure_ascii=False,indent=2)+'\n')
(ROOT/'mapas_sasisopa18.json').write_text('{\n'+',\n'.join(json.dumps(id)+':{"pages":[\n'+',\n'.join(json.dumps(page,ensure_ascii=False,separators=(',',':')) for page in layout['pages'])+'\n]}' for id,layout in maps.items())+'\n}\n')
