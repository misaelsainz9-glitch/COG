"""Importación local y revisable de tablas DOCX; nunca ejecuta contenido de Word."""
import copy
import re
import unicodedata
import uuid
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
ROLE_LABELS={'representante_legal':'Representante legal','representante_tecnico':'Representante técnico propuesto','encargado_estacion':'Encargado de estación','jefe_operaciones':'Jefe de operaciones'}

def norm(text):
 return ' '.join(''.join(c for c in unicodedata.normalize('NFD',text) if unicodedata.category(c)!='Mn').upper().split())

def read_candidates(path):
 """Devuelve propuestas con evidencia; ninguna modifica el proyecto."""
 if Path(path).suffix.lower()!='.docx':raise ValueError('Selecciona un documento Word .docx.')
 if Path(path).stat().st_size>16*1024*1024:raise ValueError('El Word supera el límite de 16 MB.')
 try:
  with zipfile.ZipFile(path) as z:
   info=z.getinfo('word/document.xml')
   if info.file_size>12*1024*1024:raise ValueError('El contenido del Word es demasiado grande.')
   xml=z.read(info)
  if b'<!DOCTYPE' in xml.upper() or b'<!ENTITY' in xml.upper():raise ValueError('El documento contiene declaraciones XML no admitidas.')
  root=ET.fromstring(xml)
 except (zipfile.BadZipFile,KeyError,ET.ParseError) as exc:raise ValueError('No se pudo leer un documento Word válido.') from exc
 rows=[]
 for row in root.findall('.//w:tr',NS):
  # Direct cells only: nested tables are visited separately, avoiding duplicate parsing.
  cells=[' '.join(''.join(t.text or '' for t in p.findall('.//w:t',NS)) for p in cell.findall('w:p',NS)).strip() for cell in row.findall('w:tc',NS)]
  if cells:rows.append(cells)
 found={};warnings=[]
 def add(key,label,value,evidence):
  value=' '.join(value.split()).strip()
  if not value:return
  item={'key':key,'label':label,'value':value,'evidence':evidence[:800]}
  if key not in found:found[key]=item
  elif found[key]['value']!=value:
   if key not in conflicts:warnings.append(f'{label}: aparecen valores distintos; revisa el Word y captura el dato manualmente.')
   conflicts.add(key)
 conflicts=set()
 field_patterns=[('estacion.razon_social','Razón social',r'Nombre\s*o\s*raz[oó]n\s*social'),('estacion.numero','Número de estación',r'N[uú]mero\s*de\s*(?:la\s*)?estaci[oó]n'),('estacion.direccion','Dirección',r'Direcci[oó]n'),('estacion.telefono','Teléfono',r'Tel[eé]fono\s*(?:oficina)?'),('estacion.correo','Correo',r'Correo\s*(?:oficina)?')]
 boundary='|'.join(p for _,_,p in field_patterns)
 for cells in rows:
  text=' '.join(cells);label=norm(cells[0])
  for key,title,pattern in field_patterns:
   match=re.search(r'(?:'+pattern+r')\s*:\s*(.*?)(?=(?:'+boundary+r')\s*:|$)',text,re.I)
   if not match:continue
   value=match.group(1).strip()
   if key=='estacion.numero':
    number=re.fullmatch(r'(?:E\s*[-–]?\s*)?(\d{1,5})',value,re.I)
    if not number:
     warnings.append('Número de estación: el Word no contiene un número válido en ese campo; captúralo manualmente.');continue
    value='E-'+number.group(1).zfill(5)
   if key=='estacion.telefono':
    value=re.sub(r'[\s().-]','',value)
    if not re.fullmatch(r'\+?\d{10,15}',value):warnings.append('Teléfono: formato ambiguo; revisa el Word.');continue
   if key=='estacion.correo':
    value=re.sub(r'\s+','',value)
    if not re.fullmatch(r'[^@\s]+@[^@\s]+\.[^@\s]+',value):warnings.append('Correo: formato ambiguo; revisa el Word.');continue
   add(key,title,value,match.group(0))
  role=next((r for r,p in [('encargado_estacion','ENCARGADO DE LA ESTACION'),('representante_legal','REPRESENTANTE LEGAL'),('jefe_operaciones','JEFE DE OPERACIONES'),('representante_tecnico','DATOS DEL REPRESENTANTE TECNICO')] if label.startswith(p)),None)
  if role and len(cells)>1:add('role:'+role,ROLE_LABELS[role],cells[1],text)
  if label in ('DISPENSARIOS','MANGUERAS'):
   for i in range(1,len(cells)-1,2):
    product={'MAGNA:':'Magna','PREMIUM:':'Premium','DIESEL:':'Diésel','MAGNA':'Magna','PREMIUM':'Premium','DIESEL':'Diésel'}.get(norm(cells[i]))
    count=re.sub(r'\s+','',cells[i+1])
    if product and re.fullmatch(r'\d{1,4}',count):add('equipment:'+product+':'+label.lower(),product+' / '+label.lower(),count,text)
  if len(cells)>=4 and re.fullmatch(r'\d{1,2}[A-Za-z]?',cells[0]):
   product={'MAGNA':'Magna','PREMIUM':'Premium','DIESEL':'Diésel'}.get(norm(cells[3]))
   capacity=re.sub(r'[\s,]','',cells[2])
   if product and re.fullmatch(r'\d+(?:\.\d+)?',capacity) and float(capacity)>0:
    for field,value,title in [('numero',cells[0],'Número'),('marca',cells[1],'Marca'),('litros',capacity,'Capacidad (litros)'),('producto',product,'Producto'),('confinamiento',cells[4] if len(cells)>4 else '','Confinamiento')]:
     add('tank:'+cells[0]+':'+field,'Tanque '+cells[0]+' / '+title,value,text)
 if not found:raise ValueError('No se reconocieron campos. Se admiten tablas con etiquetas de requisitos, tanques y equipo de despacho.')
 for key in conflicts:found.pop(key,None)
 if any(norm(c[0])=='PERMISO CRE' for c in rows):warnings.append('El permiso CRE no se importa: el campo CURR es otro dato. Consérvalo para su revisión y captura en el campo correspondiente.')
 warnings.append('Teléfono y correo se guardan en la ficha. Si las plantillas no tienen un espacio asignado, no se imprimen; puedes asignarlo con Ubicar campo.')
 warnings.append('No se importan firmas, fechas, logotipos ni listas de asistencia. Revisa espacios y cifras de la dirección tal como vienen en el Word.')
 return list(found.values()),list(dict.fromkeys(warnings))

def current_value(data,key):
 if key.startswith('role:'):
  pid=data['roles'].get(key.split(':')[1]);return next((p.get('nombre','') for p in data['people'] if p['id']==pid),'')
 if key.startswith('tank:'):
  _,number,field=key.split(':');return next((t.get(field,'') for t in (data.get('installation') or {}).get('tanks',[]) if t['numero']==number),'')
 if key.startswith('equipment:'):
  _,product,field=key.split(':');return (data.get('installation') or {}).get('equipment',{}).get(product,{}).get(field,'')
 # Inherited defaults count as existing values, too.
 return data['values'].get(key,'') or data.get('defaults',{}).get('values',{}).get(key,'')

def apply_candidates(data,selected):
 """Aplica solo filas seleccionadas a una copia; valida todo antes de devolverla."""
 import sasisopa18 as engine
 import equipo_hazop
 result=copy.deepcopy(data);tank_targets={}
 for key,value in selected.items():
  value=value.strip()
  if not value:raise ValueError('Una propuesta seleccionada está vacía; desmárcala para omitirla.')
  if key.startswith('role:'):
   role=key.split(':')[1]
   if role not in ROLE_LABELS:raise ValueError('Función no admitida.')
   matches=[p for p in result['people'] if norm(p.get('nombre',''))==norm(value)]
   if len(matches)>1:raise ValueError('Hay personas con el mismo nombre; resuelve la duplicidad antes de importar.')
   person=matches[0] if matches else {'id':uuid.uuid4().hex,'nombre':value,'puesto':'','iniciales':equipo_hazop.initials(value),'firma':''}
   if not matches:result['people'].append(person)
   result['roles'][role]=person['id']
  elif key.startswith(('tank:','equipment:')):
   inv=result.get('installation')
   if inv is None:inv={'enabled':False,'tanks':[],'equipment':{}};result['installation']=inv
   if key.startswith('tank:'):
    _,number,field=key.split(':')
    if field not in ('numero','marca','litros','producto','confinamiento'):raise ValueError('Campo de tanque no admitido.')
    tank=tank_targets.get(number)
    if tank is None:
     tank=next((t for t in inv['tanks'] if t['numero']==number),None)
     if tank is None:tank={'numero':number};inv['tanks'].append(tank)
     tank_targets[number]=tank
    tank[field]=value
   else:
    _,product,field=key.split(':');inv['equipment'].setdefault(product,{})[field]=value
   inv['enabled']=True
  elif key in ('estacion.numero','estacion.razon_social','estacion.direccion','estacion.telefono','estacion.correo'):result['values'][key]=value
  else:raise ValueError('Campo de importación no admitido.')
 engine.validate_project(result)
 return result
