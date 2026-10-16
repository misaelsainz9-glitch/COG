"""Llenado de los 18 PDF limpios con campos por función y regiones reutilizables."""
from pathlib import Path
from datetime import datetime
import json,hashlib,re,os,shutil,copy,io
from functools import lru_cache
from fontTools.ttLib import TTFont
from fontTools.pens.boundsPen import BoundsPen
from fontTools.cffLib import CFFFontSet
import fitz
from personalizacion import validated_image
from motor import MESES
ROOT=Path(__file__).resolve().parent


def configuration():
 return json.loads((ROOT/'catalogo18.json').read_text(encoding='utf-8')),json.loads((ROOT/'mapas_sasisopa18.json').read_text(encoding='utf-8'))


def empty_project():
 return {'version':1,'values':{},'people':[],'roles':{},'documents':{},'tables':{},'table_people':{},'bindings':[]}


def validate_project(data,catalog=None,maps=None):
 if catalog is None:catalog,maps=configuration()
 if not isinstance(data,dict) or data.get('version')!=1:raise ValueError('El archivo no es un proyecto SASISOPA 18 válido.')
 for k,kind in [('values',dict),('people',list),('roles',dict),('documents',dict),('tables',dict),('bindings',list)]:
  if not isinstance(data.get(k),kind):raise ValueError('Datos de proyecto inválidos: '+k)
 data.setdefault('table_people',{})
 if not isinstance(data['table_people'],dict):raise ValueError('Asignaciones de listas inválidas.')
 ids=[]
 for person in data['people']:
  if not isinstance(person,dict) or not isinstance(person.get('id'),str) or not person['id']:raise ValueError('Cada persona necesita un identificador.')
  ids.append(person['id'])
 if len(ids)!=len(set(ids)):raise ValueError('Hay identificadores de persona duplicados.')
 for role,id in data['roles'].items():
  if not isinstance(role,str) or not isinstance(id,str):raise ValueError('Asignación de función inválida.')
  if id and id not in ids:raise ValueError('La función '+role+' apunta a una persona que ya no existe.')
 for row,id in data['table_people'].items():
  if not isinstance(row,str) or not isinstance(id,str) or id and id not in ids:raise ValueError('Asignación de lista inválida.')
 def check_values(values):
  if not isinstance(values,dict):raise ValueError('Los campos deben ser un objeto de datos.')
  for key,value in values.items():
   if not isinstance(key,str) or not isinstance(value,str):raise ValueError('Los valores de captura deben ser textos.')
   if len(value)>12000 or any(ord(c)<32 and c!='\n' for c in value):raise ValueError('Hay un texto demasiado largo o con caracteres de control.')
 check_values(data['values']);check_values(data['tables'])
 for person in data['people']:check_values(person)
 for doc,values in data['documents'].items():
  if doc not in maps:raise ValueError('Documento desconocido: '+doc)
  check_values(values)
 for key,value in data['values'].items():
  if key=='estacion.numero' and value.strip() and not re.fullmatch(r'E-\d{5}',value.strip()):raise ValueError('Número de estación: usa E-00000.')
 for values in [data['values']]+list(data['documents'].values()):
  for key,value in values.items():
   value=value.strip()
   if not value:continue
   if key=='documento.revision' and not re.fullmatch(r'\d+',value):raise ValueError('La revisión debe ser un entero no negativo.')
   if key.startswith('documento.fecha_'):
    try:datetime.strptime(value,'%d/%m/%Y')
    except ValueError:raise ValueError(key+': usa una fecha real con formato dd/mm/aaaa.') from None
 all_keys={s['key'] for layout in maps.values() for p in layout['pages'] for s in p['slots']}
 all_keys.update(b['key'] for b in data['bindings'] if isinstance(b,dict) and isinstance(b.get('key'),str))
 for key,value in data['tables'].items():
  if value and key not in all_keys:raise ValueError('Un dato de lista no tiene ubicación válida: '+key)
 for prefix in data['table_people']:
  if not any(key.startswith(prefix+'.') for key in all_keys):raise ValueError('Una fila de lista no existe en esta base: '+prefix)
 for b in data['bindings']:
  if not isinstance(b,dict) or b.get('doc') not in maps:raise ValueError('Hay una ubicación de campo inválida.')
  pages=maps[b['doc']]['pages'];p=b.get('page')
  if not isinstance(p,int) or not 0<=p<len(pages):raise ValueError('La página de una ubicación no es válida.')
  try:r=fitz.Rect(b['rect']);size=float(b.get('size',9))
  except (ValueError,TypeError,KeyError):raise ValueError('Coordenadas inválidas.') from None
  if not all(__import__('math').isfinite(v) for v in list(r)+[size]) or r.width<3 or r.height<3 or not fitz.Rect(pages[p]['size']).contains(r):raise ValueError('La ubicación debe quedar dentro de la página y tener espacio suficiente.')
  if not isinstance(b.get('key'),str) or not b['key'] or not 3<=size<=36:raise ValueError('Campo o tamaño de letra inválido.')
  minimum=b.get('min_size',size)
  if not isinstance(minimum,(int,float)) or not 3<=minimum<=size:raise ValueError('El tamaño mínimo de letra es inválido.')
  if b.get('align',0) not in (0,1,2,3):raise ValueError('Alineación inválida.')
  if b.get('valign','middle') not in ('top','middle','bottom'):raise ValueError('Alineación vertical inválida.')
  if b.get('flow') and not isinstance(b['flow'],str):raise ValueError('Grupo de campo inválido.')
  if b.get('kind','text') not in ('text','image'):raise ValueError('Tipo de campo inválido.')
  if b.get('replace_id') and not any(s['id']==b['replace_id'] for s in pages[p]['slots']):raise ValueError('La ubicación original de ese campo ya no existe.')
 return data


def resolve(data,key,doc_id):
 if key.startswith('rol.'):
  _,role,attribute=key.split('.',2);person_id=data['roles'].get(role)
  return next((p.get(attribute,'').strip() for p in data['people'] if p['id']==person_id),'')
 if key.startswith('tabla.'):
  row,attribute=key.rsplit('.',1);person_id=data.get('table_people',{}).get(row)
  if person_id:return next((p.get(attribute,'').strip() for p in data['people'] if p['id']==person_id),'')
  return str(data['tables'].get(key,'')).strip()
 value=data['documents'].get(doc_id,{}).get(key,data['values'].get(key,'')).strip()
 if key=='estacion.direccion':
  parts=[value] if value else []
  for subkey in ('estacion.localidad','estacion.estado','estacion.codigo_postal'):
   part=data['values'].get(subkey,'').strip()
   if part and part.casefold() not in ', '.join(parts).casefold():parts.append(('C.P. ' if subkey.endswith('codigo_postal') else '')+part)
  value=', '.join(parts)
 return value


def slot_value(data,slot,doc_id):
 key=slot['key']
 if key=='documento.revision' and slot.get('reference_doc'):
  value=data['documents'].get(slot['reference_doc'],{}).get(key,data['values'].get(key,'')).strip()
 elif key=='documento.revision' and slot.get('revision_scope')=='global_only':value=data['values'].get(key,'').strip()
 else:value=resolve(data,key,doc_id)
 if not value and slot.get('fallback_key'):value=resolve(data,slot['fallback_key'],doc_id)
 return value


def slots_for(layout,data,doc_id,page):
 customs=[b for b in data['bindings'] if b['doc']==doc_id and b['page']==page]
 replaced={b.get('replace_id') for b in customs}
 return [s for s in layout['pages'][page]['slots'] if s['id'] not in replaced]+customs


def destination_keys(maps,data,selected):
 return {s['key'] for id in selected for pi in range(len(maps[id]['pages'])) for s in slots_for(maps[id],data,id,pi)}


def check_destinations(data,maps,selected):
 for id in selected:
  keys=destination_keys(maps,data,[id])
  for key,value in data['documents'].get(id,{}).items():
   if value.strip() and key not in keys:raise ValueError(f'{id}: «{key}» no tiene espacio asignado. Usa Ubicar campo en la vista previa.')
 keys=destination_keys(maps,data,selected)
 for key,value in data['values'].items():
  if value.strip() and key not in keys and not (key in ('estacion.localidad','estacion.estado','estacion.codigo_postal') and 'estacion.direccion' in keys):raise ValueError(f'«{key}» no aparece en los documentos seleccionados. Usa Ubicar campo o deja ese dato vacío.')


def _source(templates,meta):
 path=Path(templates)/meta['filename']
 if not path.is_file():raise ValueError('Falta '+meta['filename']+'. Copia los 18 PDF de SASISOPA_LIMPIO.zip en plantillas.')
 blob=path.read_bytes()
 if hashlib.sha256(blob).hexdigest()!=meta['sha256']:raise ValueError(meta['filename']+': no coincide con la base limpia actual. Usa la copia SASISOPA_LIMPIO actualizada.')
 return blob


@lru_cache(maxsize=16)
def _canonical_hyphen(buffer):
 # Some Windows fonts map hyphen and soft hyphen to one glyph. MuPDF's
 # reverse map may pick U+00AD, breaking search/copy of station identifiers.
 # Edit only the new embedded font, leaving original PDF fonts untouched.
 try:
  with TTFont(io.BytesIO(buffer)) as tt:
   changed=False
   for table in tt['cmap'].tables:
    if table.isUnicode() and table.cmap.get(0x2d) and table.cmap.get(0xad)==table.cmap[0x2d]:
     del table.cmap[0xad];changed=True
   if changed:
    out=io.BytesIO();tt.save(out);return out.getvalue()
 except Exception:
  # Raw CFF buffers do not have a TrueType cmap.
  pass
 return buffer


class FontBook:
 def __init__(self,doc):self.doc=doc;self.buffers={};self.cache={};self.warnings=set()
 def get(self,name,text):
  name=name.split('+')[-1];key=(name,tuple(sorted(set(text))))
  if key in self.cache:return self.cache[key]
  bold='bold' in name.lower();italic=any(v in name.lower() for v in ('italic','oblique'))
  win=Path(os.environ.get('WINDIR','C:/Windows'))/'Fonts'
  requested='arialbi.ttf' if bold and italic else 'arialbd.ttf' if bold else 'ariali.ttf' if italic else 'arial.ttf'
  if 'calibri' in name.lower():requested='calibriz.ttf' if bold and italic else 'calibrib.ttf' if bold else 'calibrii.ttf' if italic else 'calibri.ttf'
  if 'aptos' in name.lower():requested='Aptos-BoldItalic.ttf' if bold and italic else 'Aptos-Bold.ttf' if bold else 'Aptos-Italic.ttf' if italic else 'Aptos.ttf'
  candidates=[]
  local=Path(os.environ.get('LOCALAPPDATA','C:/missing'))/'Microsoft'/'Windows'/'Fonts'
  for folder in (win,local):
   if (folder/requested).is_file():candidates.append((folder/requested).read_bytes())
  if name not in self.buffers:
   self.buffers[name]=[];seen=set()
   for p in self.doc:
    for f in p.get_fonts():
     if f[3].split('+')[-1]==name and f[0] not in seen:
      seen.add(f[0]);_,_,_,buffer=self.doc.extract_font(f[0])
      if buffer:self.buffers[name].append(buffer)
  candidates+=self.buffers[name]
  for buffer in candidates:
   if '-' in text and '\xad' not in text:buffer=_canonical_hyphen(buffer)
   font=fitz.Font(fontbuffer=buffer)
   if all(c.isspace() or font.has_glyph(ord(c)) for c in text):
    result=(font,buffer,'SF'+hashlib.sha256(buffer).hexdigest()[:10]);self.cache[key]=result;return result
  # A full installed Arial is a fallback when the PDF subset lacks a new glyph.
  fallback=win/('arialbd.ttf' if bold else 'arial.ttf')
  if fallback.is_file():
   buffer=fallback.read_bytes()
   if '-' in text and '\xad' not in text:buffer=_canonical_hyphen(buffer)
   font=fitz.Font(fontbuffer=buffer)
  else:
   font=fitz.Font('hebo' if bold else 'helv');buffer=font.buffer
  if not all(c.isspace() or font.has_glyph(ord(c)) for c in text):raise ValueError('La fuente disponible no contiene todos los caracteres. Instala la fuente original o utiliza caracteres compatibles.')
  self.warnings.add('Algunos textos nuevos usaron '+font.name+' porque la fuente original no incluye esos caracteres.')
  result=(font,buffer,'SF'+hashlib.sha256(buffer).hexdigest()[:10]);self.cache[key]=result;return result


def _transform(value,slot):
 kind=slot.get('transform','')
 if kind=='digits':return value[2:]
 if kind=='revision_label':return 'REVISION: '+str(int(value))
 if kind in ('month','month_upper','year','monthyear'):
  d=datetime.strptime(value,'%d/%m/%Y');m=MESES[d.month-1]
  return str(d.year) if kind=='year' else m.upper()+' '+str(d.year) if kind=='monthyear' else m.upper() if kind=='month_upper' else m.capitalize()
 return value


@lru_cache(maxsize=64)
def _font_outlines(buffer):
 tt=TTFont(io.BytesIO(buffer));return tt,tt.getBestCmap(),tt.getGlyphSet(),tt['head'].unitsPerEm,{}


@lru_cache(maxsize=8)
def _cff_outlines(buffer):
 cff=CFFFontSet();cff.decompile(io.BytesIO(buffer),None);top=cff.topDictIndex[0]
 return top,top.CharStrings,1/top.FontMatrix[0],{}


def _glyph_bounds(font,characters):
 try:tt,cmap,glyphs,units,cache=_font_outlines(font.buffer)
 except Exception:
  top,glyphs,units,cache=_cff_outlines(font.buffer)
  cmap={ord(c):top.charset[font.has_glyph(ord(c))] for c in characters if font.has_glyph(ord(c))}

 result={}
 for c in set(characters):
  if c not in cache:
   name=cmap.get(ord(c));bounds=None
   if name:
    pen=BoundsPen(glyphs);glyphs[name].draw(pen)
    if pen.bounds:bounds=tuple(x/units for x in pen.bounds)
   cache[c]=bounds
  result[c]=cache[c]
 return result


def _ink_metrics(font,text):
 try:
  bounds=[b for b in _glyph_bounds(font,text).values() if b]
  if bounds:return max(b[3] for b in bounds),min(b[1] for b in bounds)
 except Exception:pass
 return font.ascender,font.descender


def _line_width(font,text,size):
 try:
  bounds=_glyph_bounds(font,text);left=0;right=0;x=0
  for c in text:
   b=bounds.get(c)
   if b:left=min(left,x+b[0]*size);right=max(right,x+b[2]*size)
   x+=font.glyph_advance(ord(c))*size
  return right-left,left
 except Exception:return font.text_length(text,fontsize=size),0


def _layout(font,text,rect,size,min_size):
 rect=fitz.Rect(rect);size=float(size);minimum=float(min_size)
 while True:
  lines=[];failed=False
  for paragraph in text.split('\n'):
   line=''
   for word in paragraph.split():
    if _line_width(font,word,size)[0]>rect.width+.05:failed=True;break
    candidate=(line+' '+word).strip()
    if line and _line_width(font,candidate,size)[0]>rect.width+.05:lines.append(line);line=word
    else:line=candidate
   lines.append(line)
  top,bottom=_ink_metrics(font,text)
  height=(top-bottom)*size+max(0,len(lines)-1)*size*1.15
  if not failed and height<=rect.height+.05:return lines,size,top,bottom,height
  if size<=minimum+.001:break
  size=max(minimum,round(size-.25,3))
 raise ValueError('El texto no cabe en su espacio: «'+text[:65]+'». Acórtalo o ajusta su ubicación en la vista previa.')


def _logical_rect(slot):
 r=fitz.Rect(slot['rect']);r.x1=r.x0+r.width/slot.get('x_scale',1);return r


def _write(page,slot,value,fonts):
 rect=fitz.Rect(slot['rect']);font,buffer,alias=fonts.get(slot.get('font','ArialMT'),value)
 lines,size,top,bottom,height=_layout(font,value,_logical_rect(slot),slot.get('size',9),slot.get('min_size',slot.get('size',9)))
 page.insert_font(fontname=alias,fontbuffer=buffer)
 vertical=slot.get('valign','middle')
 y=rect.y0+(rect.height-height)*(0 if vertical=='top' else 1 if vertical=='bottom' else .5)+top*size
 paragraph_ends=set();word_count=0
 for paragraph in value.split('\n'):
  word_count+=len(paragraph.split());paragraph_ends.add(word_count)
 consumed=0
 for line in lines:
  words=line.split();consumed+=len(words)
  width,left=_line_width(font,line,size);xscale=slot.get('x_scale',1);width*=xscale;left*=xscale;align=slot.get('align',0)
  x=rect.x0-left+(rect.width-width)*(.5 if align==1 else 1 if align==2 else 0)
  if align==3 and len(words)>1 and consumed not in paragraph_ends:
   extra=max(0,rect.width-width)/(len(words)-1)
   for index,word in enumerate(words):
    page.insert_text((x,y),word,fontname=alias,fontsize=size,morph=(fitz.Point(x,y),fitz.Matrix(xscale,1)))
    if index<len(words)-1:x+=font.text_length(word+' ',fontsize=size)*xscale+extra
  else:page.insert_text((x,y),line,fontname=alias,fontsize=size,morph=(fitz.Point(x,y),fitz.Matrix(xscale,1)))
  y+=size*1.15
 return len(lines),size


def _image(page,slot,path):
 path,image=validated_image(path,'la imagen');r=fitz.Rect(slot['rect']);ratio=image.px_width/image.px_height
 width=min(r.width,r.height*ratio);height=width/ratio;x=r.x0+(r.width-width)/2;y=r.y0+(r.height-height)/2
 page.insert_image((x,y,x+width,y+height),filename=str(path),keep_proportion=True)


def render_page(doc,index,layout,data,id,fonts):
 page=doc[index];slots=slots_for(layout,data,id,index);ops=[];notes=[];extra_erases=[]
 if list(page.rect)!=layout['pages'][index]['size']:raise ValueError('Las dimensiones del PDF no coinciden con la base.')
 for s in slots:
  value=slot_value(data,s,id)
  if value:
   s=dict(s);value=_transform(value,s)
   if s.get('transform')=='digits':
    font,_,_=fonts.get(s.get('font','ArialMT'),value);width,_=_line_width(font,value,s['size']);available=fitz.Rect(s['rect']).width
    if width>available:
     ratio=available/width
     if ratio<.85:raise ValueError('El número no cabe en el espacio original. Ajusta su ubicación en la vista previa.')
     s['x_scale']=ratio
   if s.get('replace_id'):
    old=next(a for a in layout['pages'][index]['slots'] if a['id']==s['replace_id']);extra_erases.append(old)
   ops.append((s,value))
 # A reference name may wrap at the end of a paragraph. Fill its separate
 # blank fragments in order, never the bounding rectangle around other text.
 groups={}
 for i,(s,value) in enumerate(ops):
  if s.get('flow'):groups.setdefault(s['flow'],[]).append(i)
 for indexes in groups.values():
  indexes.sort(key=lambda i:ops[i][0].get('flow_order',0));words=ops[indexes[0]][1].split()
  for i in indexes:
   slot,_=ops[i];font,_,_=fonts.get(slot.get('font','ArialMT'),' '.join(words) or ' ')
   count=0
   for n in range(1,len(words)+1):
    try:_layout(font,' '.join(words[:n]),slot['rect'],slot['size'],slot['min_size'])
    except ValueError:break
    count=n
   ops[i]=(slot,' '.join(words[:count]));words=words[count:]
  if words:raise ValueError('El nombre o dato no cabe en los espacios originales. Acórtalo o ajusta la ubicación: '+' '.join(words))
 ops=[(s,v) for s,v in ops if v]
 # Validate all content and images before altering a page.
 for s,value in ops:
  if s.get('kind')=='image':validated_image(value,'la imagen')
  else:
   font,_,_=fonts.get(s.get('font','ArialMT'),value)
   _layout(font,value,_logical_rect(s),s.get('size',9),s.get('min_size',s.get('size',9)))
 for old in extra_erases:
  if old.get('kind')=='image':page.add_redact_annot(old['rect'],fill=None,cross_out=False)
 for s,value in ops:
  if s.get('kind')=='image' and s.get('clear',True):page.add_redact_annot(s['rect'],fill=None,cross_out=False)
 if page.first_annot:page.apply_redactions(images=2,graphics=0,text=1)
 for old in extra_erases:
  if old.get('kind','text')=='text':
   r=fitz.Rect(old.get('erase_rect',old['rect']));r+=(.02,r.height*.15,-.02,-r.height*.15);page.add_redact_annot(r,fill=None,cross_out=False)
 for s,value in ops:
  if s.get('kind','text')=='text' and s.get('clear',True):
   # Keep adjacent text: original digit slots use full glyph boxes, but redaction
   # only needs their interior. This protects code prefixes and neighbouring labels.
   r=fitz.Rect(s.get('erase_rect',s['rect']));r+=(.02,r.height*.15,-.02,-r.height*.15)
   page.add_redact_annot(r,fill=None,cross_out=False)
 if page.first_annot:page.apply_redactions(images=0,graphics=0)
 for s,value in ops:
  if s.get('kind')=='image':_image(page,s,value)
  else:
   lines,size=_write(page,s,value,fonts);notes.append({'field':s['key'],'lines':lines,'size':size})
 return notes


def preview(templates,data,id,page_index,scale=1.0):
 catalog,maps=configuration();validate_project(data,catalog,maps)
 meta=next((m for m in catalog['templates'] if m['id']==id),None)
 if meta is None:raise ValueError('Selecciona un documento válido.')
 if not isinstance(page_index,int) or not 0<=page_index<meta['pages']:raise ValueError('La página no existe.')
 with fitz.open(stream=_source(templates,meta),filetype='pdf') as doc:
  fonts=FontBook(doc);notes=render_page(doc,page_index,maps[id],data,id,fonts)
  pix=doc[page_index].get_pixmap(matrix=fitz.Matrix(scale,scale),alpha=False)
  return pix.tobytes('png'),notes,sorted(fonts.warnings)


def generate(templates,out,data,selected=None,merge=False):
 catalog,maps=configuration();validate_project(data,catalog,maps)
 ids=[m['id'] for m in catalog['templates']];selected=ids if selected is None else list(selected)
 if not selected or len(set(selected))!=len(selected) or any(id not in ids for id in selected):raise ValueError('Selecciona al menos un documento válido, sin duplicados.')
 check_destinations(data,maps,selected)
 out=Path(out)
 if out.exists():raise ValueError('La carpeta del lote ya existe. No se sobrescribirán archivos.')
 prepared=[];warnings=set();report=[]
 for meta in catalog['templates']:
  id=meta['id']
  if id not in selected:continue
  blob=_source(templates,meta);layout=maps[id]
  active=any(slot_value(data,s,id) for pi in range(len(layout['pages'])) for s in slots_for(layout,data,id,pi))
  if active:
   with fitz.open(stream=blob,filetype='pdf') as doc:
    fonts=FontBook(doc)
    for pi in range(len(doc)):
     try:notes=render_page(doc,pi,layout,data,id,fonts)
     except ValueError as exc:raise ValueError(f'{id}, página {pi+1}: {exc}') from None
     report.extend({'document':id,'page':pi+1,**n} for n in notes)
    warnings.update(fonts.warnings);doc.set_metadata({});blob=doc.tobytes(garbage=4,deflate=True)
  prepared.append((f'PROCEDIMIENTO {id}.pdf',blob))
 if merge:
  with fitz.open() as combined:
   toc=[]
   for filename,blob in prepared:
    toc.append([1,filename[:-4],len(combined)+1])
    with fitz.open(stream=blob,filetype='pdf') as doc:combined.insert_pdf(doc)
   combined.set_toc(toc);prepared.append(('SASISOPA_UNIDO.pdf',combined.tobytes(garbage=4,deflate=True)))
 out.mkdir(parents=True)
 try:
  paths=[]
  for name,blob in prepared:
   p=out/name
   with p.open('xb') as stream:stream.write(blob)
   paths.append(p)
  audit={'warnings':sorted(warnings),'fields':report,'documents':selected}
  with (out/'revision_del_lote.json').open('x',encoding='utf-8') as f:json.dump(audit,f,ensure_ascii=False,indent=2)
 except Exception:
  shutil.rmtree(out);raise
 return paths,sorted(warnings)


def save_project(path,data):
 catalog,maps=configuration();validate_project(data,catalog,maps)
 path=Path(path);temporary=path.with_name(path.name+'.tmp');created=False
 try:
  with temporary.open('x',encoding='utf-8') as f:
   created=True;json.dump(data,f,ensure_ascii=False,indent=2)
  temporary.replace(path)
 except Exception:
  if created and temporary.exists():temporary.unlink()
  raise


def load_project(path):
 try:
  path=Path(path)
  if path.stat().st_size>8*1024*1024:raise ValueError('El archivo de datos es demasiado grande.')
  data=json.loads(path.read_text(encoding='utf-8'))
 except (OSError,json.JSONDecodeError) as exc:raise ValueError('No se pudo leer el archivo de datos SASISOPA 18.') from exc
 return validate_project(data)
