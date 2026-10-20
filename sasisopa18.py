"""Llenado de los 18 PDF limpios con campos por función y regiones reutilizables."""
from pathlib import Path,PureWindowsPath
from datetime import datetime
import json,hashlib,re,os,shutil,copy,io
from functools import lru_cache
from fontTools.ttLib import TTFont
from fontTools.pens.boundsPen import BoundsPen
from fontTools.cffLib import CFFFontSet
import fitz
import instalaciones
import equipo_hazop
import calendarios
import valores_predeterminados
from limpieza_transparencias import normalizar_marcadores_vacios
from personalizacion import validated_image
from motor import MESES
ROOT=Path(__file__).resolve().parent


def configuration():
 return json.loads((ROOT/'catalogo18.json').read_text(encoding='utf-8')),json.loads((ROOT/'mapas_sasisopa18.json').read_text(encoding='utf-8'))


def empty_project():
 return {'version':1,'installation':None,'values':{},'people':[],'roles':{},'documents':{},'tables':{},'table_people':{},'bindings':[]}


def new_project():
 """Neutral editable template, independent of the currently loaded station."""
 data=json.loads((ROOT/'plantilla_nueva.json').read_text(encoding='utf-8'))
 validate_project(data)
 logo=ROOT/'assets'/'logo-pemex.png'
 if logo.is_file():data['values']['estacion.logo']=str(logo)
 return data


def validate_project(data,catalog=None,maps=None):
 if catalog is None:catalog,maps=configuration()
 if not isinstance(data,dict) or data.get('version')!=1:raise ValueError('El archivo no es un proyecto SASISOPA 18 válido.')
 if type(data.get('fresh_project',False)) is not bool:raise ValueError('Indicador de proyecto nuevo inválido.')
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
 if data.get('defaults') is not None:
  defaults=data['defaults']
  if not isinstance(defaults,dict) or set(defaults)-set(valores_predeterminados.SECTIONS):raise ValueError('Valores predeterminados inválidos.')
  baseline=empty_project()
  baseline.update(copy.deepcopy(defaults));baseline['bindings']=copy.deepcopy(data['bindings'])
  validate_project(baseline,catalog,maps)
 check_values(data['values']);check_values(data['tables'])
 for person in data['people']:check_values(person)
 for doc,values in data['documents'].items():
  if doc not in maps:raise ValueError('Documento desconocido: '+doc)
  check_values(values)
 instalaciones.validate(valores_predeterminados.effective(data))
 for values in [data['values']]+list(data['documents'].values()):
  for key,value in values.items():
   value=value.strip()
   if not value:continue
   if key=='estacion.numero' and not re.fullmatch(r'E-[0-9]{5}',value):raise ValueError('Número de estación: usa E-00000.')
   if key=='documento.revision' and not re.fullmatch(r'\d+',value):raise ValueError('La revisión debe ser un entero no negativo.')
   if key.startswith('documento.fecha_') or key=='dato.fecha_actual_operativa':
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
  if b.get('replace_id') and not any(s['id']==b['replace_id'] for s in pages[p]['slots']):
   aliases=[s for s in pages[p]['slots'] if s['key']==b['key'] and b['replace_id'] in s.get('legacy_ids',[])]
   if len(aliases)==1:b['replace_id']=aliases[0]['id']
   else:raise ValueError('La ubicación original de ese campo ya no existe.')
 calendarios.period(valores_predeterminados.effective(data))
 start=resolve(data,'documento.fecha_inicio_estudio','II');end=resolve(data,'documento.fecha_fin_estudio','II')
 if start and end and datetime.strptime(end,'%d/%m/%Y')<datetime.strptime(start,'%d/%m/%Y'):raise ValueError('El fin del proyecto HAZOP no puede ser anterior al inicio.')
 return data


def resolve(data,key,doc_id):
 if key.startswith('rol.'):
  _,role,attribute=key.split('.',2);person_id=data['roles'].get(role)
  person=next((p for p in data['people'] if p['id']==person_id),{})
  return equipo_hazop.initials(person.get('nombre','')) if attribute=='iniciales' else person.get(attribute,'').strip()
 if key.startswith('tabla.'):
  row,attribute=key.rsplit('.',1);person_id=data.get('table_people',{}).get(row)
  if person_id:return next((p.get(attribute,'').strip() for p in data['people'] if p['id']==person_id),'')
  return str(data['tables'].get(key,'')).strip()
 defaults=data.get('defaults') or {}
 value=data['documents'].get(doc_id,{}).get(key,'').strip() or (defaults.get('documents') or {}).get(doc_id,{}).get(key,'').strip() or data['values'].get(key,'').strip() or (defaults.get('values') or {}).get(key,'').strip()
 if key=='estacion.direccion':
  parts=[value] if value else []
  for subkey in ('estacion.localidad','estacion.estado','estacion.codigo_postal'):
   part=data['values'].get(subkey,'').strip()
   if part and part.casefold() not in ', '.join(parts).casefold():parts.append(('C.P. ' if subkey.endswith('codigo_postal') else '')+part)
  value=', '.join(parts)
 return value


def slot_value(data,slot,doc_id):
 key=slot['key']
 if doc_id=='II' and key.startswith('rol.') and key.endswith('.iniciales') and key.split('.')[1] in equipo_hazop.ROLES:
  return equipo_hazop.group_initials(data,key.split('.')[1])
 if slot.get('team_member'):
  value=resolve(data,key,doc_id)
  if not value and slot.get('fallback_key'):value=resolve(data,slot['fallback_key'],doc_id)
  return value or ('Pendiente' if equipo_hazop.active(data) else '')
 if key.startswith('instalacion.'):
  value=instalaciones.value(data,key)
  return slot.get('installation_prefix','')+value if value else ''
 if slot.get('code_suffix'):
  station=resolve(data,'estacion.numero',doc_id)
  if data.get('fresh_project') and not station:return ''
  ref=re.match(r'\.(\d+)',slot['code_suffix'])
  roman=('I','II','III','IV','V','VI','VII','VIII','IX','X','XI','XII','XIII','XIV','XV','XVI','XVII','XVIII')[int(ref.group(1))-1] if ref and 1<=int(ref.group(1))<=18 else doc_id
  revision=slot_value(data,{'key':'documento.revision','reference_doc':roman},doc_id)
  if not station and not revision:return ''
  return (station or 'E-')+slot['code_suffix']+(revision or slot['code_revision'])
 if key=='documento.revision' and slot.get('reference_doc'):
  value=data['documents'].get(slot['reference_doc'],{}).get(key,data['values'].get(key,'')).strip()
 elif slot.get('reference_doc'):value=resolve(data,key,slot['reference_doc'])
 elif slot.get('revision_scope')=='global_only':value=data['values'].get(key,'').strip()
 else:value=resolve(data,key,doc_id)
 if not value and slot.get('fallback_key'):value=resolve(data,slot['fallback_key'],doc_id)
 if not value and key=='documento.revision' and data.get('fresh_project'):value='0'
 if not value and slot.get('preserve_default'):value=slot.get('default_text','')
 return slot.get('text_prefix','')+value if value else ''


def slots_for(layout,data,doc_id,page):
 spec=layout['pages'][page]
 base=spec['slots']
 # Signatures use the measured cell interior and may overlap printed labels.
 footer={s['key'].split('.')[1]:s for s in base
         if page>0 and s['key'] in ('rol.elabora.nombre','rol.revisa.nombre','rol.autoriza.nombre')
         and s['rect'][1]>spec['size'][3]*.65}
 protected={s['id'] for s in base if s['key'].startswith('tabla.') or
            (s['key'].startswith('rol.') and s['key'].split('.')[1] in footer
             and s['key'].endswith(('.nombre','.firma')))}
 customs=[b for b in data['bindings'] if b['doc']==doc_id and b['page']==page
          and b.get('replace_id') not in protected and not b['key'].startswith('tabla.')]
 attendance=[fitz.Rect(s['rect']) for s in base if s['key'].startswith('tabla.')]
 if any(any(fitz.Rect(b['rect']).intersects(r) for r in attendance) for b in customs):
  raise ValueError('Las listas de asistencia deben permanecer vacías. Quita las ubicaciones personalizadas sobre sus filas.')
 replaced={b.get('replace_id') for b in customs}
 result=[s for s in base if s['id'] not in replaced and s['id'] not in protected]
 for role,name in footer.items():
  result.append({**name,'id':name['id']+'.firma','key':f'rol.{role}.firma','rect':name.get('signature_rect',name['rect']),'kind':'image','clear':False,'locked':True})
 # A moved station binding still represents the entire header code.
 by_id={s['id']:s for s in base}
 aliases={}
 for i,binding in enumerate(customs):
  old=by_id.get(binding.get('replace_id'))
  if old:
   binding=dict(binding)
   if old.get('hazop_product'):binding['hazop_product']=old['hazop_product']
   if old['key']==binding['key']:
    for name in ('fallback_key','team_member','installation_prefix','erase_full','reference_doc','revision_scope'):
     if name in old:binding[name]=old[name]
   customs[i]=binding
  if old and old.get('code_suffix') and binding['key']=='estacion.numero':
   binding=dict(binding)
   for name in ('code_suffix','code_revision','code_members','single_line'):binding[name]=old[name]
   binding.pop('transform',None)
   if 'baseline' in old:binding['baseline']=binding['rect'][1]+old['baseline']-old['rect'][1]
   aliases[old['id']]=binding['id'];customs[i]=binding
 result=[{**s,'code_owner':aliases[s['code_owner']]} if s.get('code_owner') in aliases else s for s in result]
 # The policy signer name belongs below the printed role, leaving the line
 # above it for the signature. Upgrade this placement in older bindings too.
 if doc_id=='I' and page==10 and 'I.11.10' in by_id:
  canonical=by_id['I.11.10']
  result=[{**slot,**{k:copy.deepcopy(canonical[k]) for k in ('rect','erase_rect','align','min_size')}}
          if slot['key']=='rol.representante_legal.nombre' and (slot['id']=='I.11.10' or slot.get('replace_id')=='I.11.10') else slot for slot in result]
  customs=[{**slot,**{k:copy.deepcopy(canonical[k]) for k in ('rect','erase_rect','align','min_size')}}
           if slot['key']=='rol.representante_legal.nombre' and slot.get('replace_id')=='I.11.10' else slot for slot in customs]
 # Cover addresses are centered even in profiles saved with the older right alignment.
 # Apply after merging custom bindings, without changing saved geometry or profiles.
 return [{**slot,'align':1} if page==0 and slot['key']=='estacion.direccion' else slot for slot in result+customs]


def destination_keys(maps,data,selected):
 return {s['key'] for id in selected for pi in range(len(maps[id]['pages'])) for s in slots_for(maps[id],data,id,pi)}


def check_destinations(data,maps,selected):
 for id in selected:
  keys=destination_keys(maps,data,[id])
  for key,value in data['documents'].get(id,{}).items():
   if value.strip() and key not in keys:raise ValueError(f'{id}: «{key}» no tiene espacio asignado. Usa Ubicar campo en la vista previa.')
 keys=destination_keys(maps,data,selected);available=None
 for key,value in data['values'].items():
  if key in {k for k,label in equipo_hazop.DATES} and 'II' not in selected:continue
  if value.strip() and key not in keys and not (key in ('estacion.localidad','estacion.estado','estacion.codigo_postal') and 'estacion.direccion' in keys):
   if available is None:available=destination_keys(maps,data,list(maps))
   if key in available or key in ('estacion.telefono','estacion.correo'):continue
   raise ValueError(f'«{key}» no aparece en los documentos seleccionados. Usa Ubicar campo o deja ese dato vacío.')


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


def _balanced_cover_lines(font,value,rect,size,lines):
 # Keep explicit line breaks. Otherwise balance the existing number of lines,
 # preserving both font size and height and keeping postal labels with numbers.
 if len(lines)<2 or '\n' in value:return lines
 words=value.split();count=len(lines);n=len(words)
 total=font.text_length(' '.join(words),fontsize=size)
 target=(total-(count-1)*font.text_length(' ',fontsize=size))/count
 states={(0,0):(0,[])}
 for k in range(1,count+1):
  for end in range(k,n+1):
   if end<n and words[end-1].upper().rstrip('.') in ('C.P','CP','KM','K.M'):continue
   best=None
   for start in range(k-1,end):
    previous=states.get((k-1,start))
    if previous is None:continue
    text=' '.join(words[start:end]);width,_=_line_width(font,text,size)
    if width>rect.width+.05:continue
    candidate=(previous[0]+(width-target)**2,previous[1]+[text])
    if best is None or candidate[0]<best[0]:best=candidate
   if best is not None:states[k,end]=best
 return states.get((count,n),(0,lines))[1]


def _write(page,slot,value,fonts):
 rect=fitz.Rect(slot['rect']);font,buffer,alias=fonts.get(slot.get('font','ArialMT'),value)
 lines,size,top,bottom,height=_layout(font,value,_logical_rect(slot),slot.get('size',9),slot.get('min_size',slot.get('size',9)))
 if slot.get('balance_lines'):lines=_balanced_cover_lines(font,value,_logical_rect(slot),size,lines)
 page.insert_font(fontname=alias,fontbuffer=buffer)
 vertical=slot.get('valign','middle')
 y=slot.get('baseline',rect.y0+(rect.height-height)*(0 if vertical=='top' else 1 if vertical=='bottom' else .5)+top*size)
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
 path,image=validated_image(path,'la imagen');r=fitz.Rect(slot['rect'])
 stream=None
 if slot['key'].endswith('.firma'):
  from firma_canvas import blue_signature
  signature=blue_signature(path);image_width,image_height=signature.size
  buffer=io.BytesIO();signature.save(buffer,format='PNG');stream=buffer.getvalue()
 else:image_width,image_height=image.px_width,image.px_height
 ratio=image_width/image_height
 width=min(r.width,r.height*ratio);height=width/ratio;x=r.x0+(r.width-width)/2;y=r.y0+(r.height-height)/2
 kwargs={'stream':stream} if stream is not None else {'filename':str(path)}
 page.insert_image((x,y,x+width,y+height),keep_proportion=True,overlay=True,**kwargs)


def render_page(doc,index,layout,data,id,fonts):
 page=doc[index];slots=slots_for(layout,data,id,index);ops=[];notes=[];extra_erases=[]
 inactive=instalaciones.inactive_regions(data,id,index)
 # Attendance is manual, including when an older profile still contains row data.
 attendance=[s for s in layout['pages'][index]['slots'] if s['key'].startswith('tabla.')]
 if list(page.rect)!=layout['pages'][index]['size']:raise ValueError('Las dimensiones del PDF no coinciden con la base.')
 for s in slots:
  if s.get('hazop_product') and instalaciones.enabled(data) and not instalaciones.tanks(data,s['hazop_product']):continue
  if any(fitz.Rect(region).intersects(fitz.Rect(s['rect'])) for region,product in inactive):continue
  if s.get('code_owner') and any(a['id']==s['code_owner'] for a in slots):continue
  value=slot_value(data,s,id)
  if not value and data.get('fresh_project') and s.get('kind','text')=='text' and not s.get('preserve_source_empty'):
   old=dict(s)
   if s.get('code_suffix'):old.update(erase_rect=s['rect'],erase_full=True)
   extra_erases.append(old)
   if s.get('replace_id'):
    original=next(a for a in layout['pages'][index]['slots'] if a['id']==s['replace_id'])
    extra_erases.append(original)
  if value:
   s=dict(s);value=_transform(value,s)
   numeric_revision=s['key']=='documento.revision' and value.isdigit()
   if numeric_revision:s['single_line']=True
   if s.get('single_line'):
    font,_,_=fonts.get(s.get('font','ArialMT'),value);width,_=_line_width(font,value,s['size']);available=fitz.Rect(s['rect']).width
    if width>available:s['x_scale']=available/width
    if s.get('x_scale',1)<(.65 if numeric_revision and len(value)<=2 else .7):raise ValueError('La revisión no cabe en su espacio. Ajusta su ubicación en la vista previa.' if numeric_revision else 'El código no cabe en una sola línea. Amplía su espacio en la vista previa.')
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
   # A final surname may be slightly wider than its original fragment.
   # Keep the physical box and font-size floor; allow at most 15% horizontal
   # compression, rather than clipping or dropping part of a person's name.
   if i==indexes[-1] and count<len(words) and slot['key'].startswith('rol.') and slot['key'].endswith('.nombre'):
    width,_=_line_width(font,' '.join(words),slot['min_size'])
    ratio=min(1,fitz.Rect(slot['rect']).width/max(width,.001))
    if ratio>=.85:
     trial=dict(slot,x_scale=ratio)
     try:_layout(font,' '.join(words),_logical_rect(trial),trial['size'],trial['min_size'])
     except ValueError:pass
     else:slot=trial;count=len(words)
   ops[i]=(slot,' '.join(words[:count]));words=words[count:]
  if words:raise ValueError('El nombre o dato no cabe en los espacios originales. Acórtalo o ajusta la ubicación: '+' '.join(words))
 ops=[(s,v) for s,v in ops if v]
 # Validate all content and images before altering a page.
 for s,value in ops:
  if s.get('kind')=='image':validated_image(value,'la imagen')
  else:
   font,_,_=fonts.get(s.get('font','ArialMT'),value)
   try:_layout(font,value,_logical_rect(s),s.get('size',9),s.get('min_size',s.get('size',9)))
   except ValueError:
    if not (s['key'].startswith('rol.') and s['key'].endswith('.nombre')):raise
    width,_=_line_width(font,value,s.get('min_size',s.get('size',9)))
    ratio=min(1,fitz.Rect(s['rect']).width/max(width,.001))
    if ratio<.85:raise
    s['x_scale']=ratio
    _layout(font,value,_logical_rect(s),s.get('size',9),s.get('min_size',s.get('size',9)))
 normalizar_marcadores_vacios(doc,page)
 for cell in attendance:page.add_redact_annot(cell['rect'],fill=None,cross_out=False)
 for old in extra_erases:
  if old.get('kind')=='image' or old.get('raster_clear'):page.add_redact_annot(old.get('erase_rect',old['rect']),fill=None,cross_out=False)
 for s,value in ops:
  if s.get('raster_clear'):page.add_redact_annot(s.get('erase_rect',s['rect']),fill=None,cross_out=False)
  elif s.get('kind')=='image' and s.get('clear',True):page.add_redact_annot(s['rect'],fill=None,cross_out=False)
 if page.first_annot:page.apply_redactions(images=2,graphics=0,text=1)
 for region,product in inactive:page.add_redact_annot(region,fill=None,cross_out=False)
 for cell in attendance:page.add_redact_annot(cell['rect'],fill=None,cross_out=False)
 for old in extra_erases:
  if old.get('kind','text')=='text':
   r=fitz.Rect(old.get('erase_rect',old['rect']))
   r+=(.02,.02,-.02,-.02) if old.get('erase_full') else (.02,r.height*.15,-.02,-r.height*.15)
   page.add_redact_annot(r,fill=None,cross_out=False)
 for s,value in ops:
  if s.get('kind','text')=='text' and s.get('clear',True):
   # Keep adjacent text: original digit slots use full glyph boxes, but redaction
   # only needs their interior. This protects code prefixes and neighbouring labels.
   r=fitz.Rect(s.get('erase_rect',s['rect']))
   r+=(.02,.02,-.02,-.02) if s.get('erase_full') else (.02,r.height*.15,-.02,-r.height*.15)
   page.add_redact_annot(r,fill=None,cross_out=False)
 if page.first_annot:page.apply_redactions(images=0,graphics=0)
 for s,value in ops:
  if s.get('kind')=='image':_image(page,s,value)
  else:
   lines,size=_write(page,s,value,fonts);notes.append({'field':s['key'],'lines':lines,'size':size})
 for region,product in inactive:
  r=fitz.Rect(region);r.y1=r.y0+28
  _write(page,{'rect':list(r),'size':10,'min_size':10},'No aplica: '+product+' no se almacena en esta estación.',fonts)
  notes.append({'field':'instalacion.no_aplica','product':product,'lines':1,'size':10})
 notes.extend(calendarios.apply(page,id,index,data,_write,fonts))
 return notes


def preview(templates,data,id,page_index,scale=1.0):
 data=valores_predeterminados.effective(data)
 catalog,maps=configuration();validate_project(data,catalog,maps)
 meta=next((m for m in catalog['templates'] if m['id']==id),None)
 if meta is None:raise ValueError('Selecciona un documento válido.')
 total=meta['pages']+instalaciones.extra_pages(data,id)
 if not isinstance(page_index,int) or not 0<=page_index<total:raise ValueError('La página no existe.')
 with fitz.open(stream=_source(templates,meta),filetype='pdf') as doc:
  fonts=FontBook(doc)
  if page_index>=meta['pages']:
   instalaciones.append_inventory(doc,data,resolve(data,'estacion.numero',id),_write,fonts);notes=[]
  else:notes=render_page(doc,page_index,maps[id],data,id,fonts)
  pix=doc[page_index].get_pixmap(matrix=fitz.Matrix(scale,scale),alpha=False)
  return pix.tobytes('png'),notes,sorted(fonts.warnings)


def generate(templates,out,data,selected=None,merge=False):
 data=valores_predeterminados.effective(data)
 catalog,maps=configuration();validate_project(data,catalog,maps)
 if data.get('fresh_project') and not resolve(data,'estacion.numero','I'):raise ValueError('Captura el número de la nueva estación antes de generar los PDF.')
 ids=[m['id'] for m in catalog['templates']];selected=ids if selected is None else list(selected)
 if not selected or len(set(selected))!=len(selected) or any(id not in ids for id in selected):raise ValueError('Selecciona al menos un documento válido, sin duplicados.')
 check_destinations(data,maps,selected)
 out=Path(out)
 if out.exists():raise ValueError('La carpeta del lote ya existe. No se sobrescribirán archivos.')
 prepared=[];warnings=set();report=[]
 available=destination_keys(maps,data,list(maps))
 for key in ('estacion.telefono','estacion.correo'):
  if data['values'].get(key,'').strip() and key not in available:
   warnings.add(f'{key}: guardado en la ficha; sin espacio asignado en las plantillas. Usa Ubicar campo si debe imprimirse.')
 for meta in catalog['templates']:
  id=meta['id']
  if id not in selected:continue
  blob=_source(templates,meta);layout=maps[id]
  active=calendarios.enabled(data,id) or (instalaciones.enabled(data) and id in ('II','III','XIII')) or any(s['key'].startswith('tabla.') for p in layout['pages'] for s in p['slots']) or any(slot_value(data,s,id) for pi in range(len(layout['pages'])) for s in slots_for(layout,data,id,pi))
  if active:
   with fitz.open(stream=blob,filetype='pdf') as doc:
    fonts=FontBook(doc)
    for pi in range(len(doc)):
     try:notes=render_page(doc,pi,layout,data,id,fonts)
     except ValueError as exc:raise ValueError(f'{id}, página {pi+1}: {exc}') from None
     report.extend({'document':id,'page':pi+1,**n} for n in notes)
    if instalaciones.enabled(data) and id in ('II','XIII'):
     instalaciones.append_inventory(doc,data,resolve(data,'estacion.numero',id),_write,fonts)
     warnings.add('Instalaciones actualizadas: revisar técnicamente HAZOP y escenarios de riesgo con los datos de esta estación; el sistema no recalcula su valoración.')
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
 validate_project(data)
 # Resolve project-relative image assets for portable project folders.
 for section in [data,data.get('defaults') or {}]:
  stores=[section.get('values',{})]+list(section.get('documents',{}).values())
  for store in stores:
   for key,value in store.items():
    if key.endswith(('.logo','.firma')) and value and not Path(value).is_absolute() and not PureWindowsPath(value).is_absolute():store[key]=str((path.parent/value).resolve())
  for person in section.get('people',[]):
   value=person.get('firma','')
   if value and not Path(value).is_absolute() and not PureWindowsPath(value).is_absolute():person['firma']=str((path.parent/value).resolve())
 return validate_project(data)
