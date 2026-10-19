"""Station inventory shared by storage, dispatch and process-node fields."""
import re
from decimal import Decimal,InvalidOperation
PRODUCTS=('Magna','Premium','Diésel')
TANK_FIELDS=(('numero','Número / compartimento'),('producto','Producto'),('litros','Capacidad (litros)'),('marca','Marca'),('medidas','Medidas'),('confinamiento','Tipo de confinado'),('pared','Tipo de pared / material'),('cupula','Tipo de cúpula'),('presion_vapor','Presión de vapor (con unidad)'),('temperatura_almacen','Temperatura de almacenamiento'),('presion_operacion','Presión de operación (con unidad)'),('temperatura_operacion','Temperatura de operación'),('flujo','Flujo (con unidad)'),('plano','Plano / referencia'),('deteccion','Detección / monitoreo'))

def liters(text):
 try:
  plain=text.replace(' ','')
  if not re.fullmatch(r'(?:[0-9]+|[0-9]{1,3}(?:,[0-9]{3})+)(?:\.[0-9]{1,3})?',plain):raise ValueError()
  n=Decimal(plain.replace(',',''))
  if not n.is_finite() or n<=0:raise ValueError()
  return n
 except (InvalidOperation,ValueError):raise ValueError('La capacidad debe ser mayor que cero, en litros (ejemplo: 60000).') from None

def validate(data):
 inv=data.get('installation')
 if inv is None:return
 if not isinstance(inv,dict) or type(inv.get('enabled')) is not bool:raise ValueError('Ficha de instalaciones inválida.')
 tanks=inv.get('tanks',[]);equipment=inv.get('equipment',{})
 if not isinstance(tanks,list) or len(tanks)>60 or inv['enabled'] and not tanks:raise ValueError('Agrega entre 1 y 60 tanques o compartimentos.')
 ids=[]
 for t in tanks:
  if not isinstance(t,dict):raise ValueError('Tanque inválido.')
  if any(not isinstance(v,str) or len(v)>100 or any(ord(c)<32 for c in v) for v in t.values()):raise ValueError('Revisa los datos del tanque: usa textos de hasta 100 caracteres, sin saltos de línea.')
  if not inv['enabled']:continue
  if not re.fullmatch(r'[A-Za-z0-9.-]{1,12}',t.get('numero','')):raise ValueError('Asigna un número único a cada tanque o compartimento (ejemplo: 1 o 1A).')
  if t.get('producto') not in PRODUCTS:raise ValueError('Selecciona Magna, Premium o Diésel para cada tanque.')
  liters(t.get('litros',''));ids.append(t['numero'].casefold())
 if len(set(ids))!=len(ids):raise ValueError('Hay números de tanque o compartimento repetidos.')
 if not isinstance(equipment,dict):raise ValueError('Datos de dispensarios y mangueras inválidos.')
 active={t.get('producto','') for t in tanks}
 for product,counts in equipment.items():
  if product not in PRODUCTS or not isinstance(counts,dict):raise ValueError('Producto de despacho inválido.')
  for key,value in counts.items():
   if key not in ('dispensarios','mangueras') or not isinstance(value,str) or value and not re.fullmatch(r'\d{1,4}',value):raise ValueError('Las cantidades de dispensarios y mangueras deben ser enteros no negativos.')
   if inv['enabled'] and product not in active and value and int(value):raise ValueError(f'{product}: hay equipo de despacho pero ningún tanque. Revisa la ficha.')

def enabled(data):return bool(data.get('installation',{} ) and data['installation'].get('enabled'))
def extra_pages(data,doc_id):return (len(tanks(data))+2)//3 if enabled(data) and doc_id in ('II','XIII') else 0
def tanks(data,product=None):
 rows=data['installation']['tanks']
 return [t for t in rows if product is None or t['producto']==product]
def products(data):return [p for p in PRODUCTS if tanks(data,p)]
def number(text):return format(liters(text),',f').rstrip('0').rstrip('.') if '.' in format(liters(text),',f') else format(liters(text),',f')
def pending(text):return text.strip() or 'Pendiente'
def shared(data,product,key):
 values=list(dict.fromkeys(pending(t.get(key,'')) for t in tanks(data,product)))
 return values[0] if len(values)==1 else 'Ver ficha de instalaciones'

def value(data,key):
 if not enabled(data):return ''
 parts=key.split('.')
 if parts[1]=='tanque':
  index=int(parts[2]);field=parts[3];rows=tanks(data)
  if index>=len(rows):return 'No aplica' if field=='producto' else '—'
  t=rows[index]
  return number(t['litros']) if field=='litros' else pending(t.get(field,''))
 if parts[1]=='derrame':return '1.- Derrame de '+('Diésel' if tanks(data,'Diésel') else 'combustible')+' en'
 if parts[1]=='lista':return '\n'.join(products(data))
 if parts[1]=='productos':return ', '.join(products(data))
 if parts[1]=='despacho':return 'Se despachan '+', '.join(products(data))+'. Las cantidades de dispensarios y mangueras se detallan en la ficha de instalaciones.'
 if parts[1]=='almacenamiento':
  rows=tanks(data);total=sum(liters(t['litros']) for t in rows)
  text=f'Almacenamiento de {", ".join(products(data))} en {len(rows)} tanques o compartimentos, con capacidad total de {number(str(total))} litros. '
  if len(rows)<=3:
   text+='; '.join(f'TQ {t["numero"]}: {t["producto"]}, {number(t["litros"])} L, marca {pending(t.get("marca",""))}, confinado {pending(t.get("confinamiento",""))}' for t in rows)+'. '
  return text+'Las medidas, materiales y condiciones de cada tanque se detallan en la ficha de instalaciones anexa.'
 if parts[1]=='producto':
  product=PRODUCTS[int(parts[2])];field=parts[3];rows=tanks(data,product)
  if field=='nombre':return product if rows else '—'
  if field=='no_aplica':return '' if rows else '—'
  if not rows:return 'No aplica'
  if field=='continuacion':return 'Sistema de bombeo y dispensarios.'
  if field=='incluye':return 'Tanques / compartimentos '+', '.join(t['numero'] for t in rows)+', bombeo y dispensarios.'
  if field=='condiciones':return '\n'.join(label+': '+shared(data,product,k) for label,k in [('Presión','presion_operacion'),('Temperatura','temperatura_operacion'),('Flujo','flujo')])
  return shared(data,product,field)
 raise ValueError('Campo de instalaciones desconocido: '+key)

def inactive_regions(data,doc_id,index):
 if not enabled(data) or doc_id!='II':return []
 page=index+1;regions=[]
 for product,start,end in [('Magna',34,42),('Premium',42,48),('Diésel',49,54)]:
  if tanks(data,product) or not start<=page<=end:continue
  top=340 if page==34 else 465 if page==42 and product=='Premium' else 154
  bottom=460 if page==42 and product=='Magna' else 482 if page==54 else 580
  regions.append(([10,top,775,bottom],product))
 return regions


def append_inventory(doc,data,station,write,fonts):
 """Add readable continuation sheets; never squeeze extra rows into a 3-row table."""
 for start in range(0,len(tanks(data)),3):
  page=doc.new_page(width=612,height=792)
  write(page,{'rect':[40,30,572,60],'size':14,'min_size':14,'font':'Arial-BoldMT'},'FICHA DE INSTALACIONES — '+(station or 'ESTACIÓN'),fonts)
  write(page,{'rect':[40,65,572,100],'size':9,'min_size':9},'Datos capturados por la estación. No sustituye la revisión del análisis de riesgos. Las condiciones no capturadas se indican como Pendiente.',fonts)
  y=110
  for t in tanks(data)[start:start+3]:
   text=f'TANQUE / COMPARTIMENTO {t["numero"]} — {t["producto"]} — {number(t["litros"])} L\n'
   text+='\n'.join(label+': '+pending(t.get(key,'')) for key,label in TANK_FIELDS if key not in ('numero','producto','litros'))
   write(page,{'rect':[40,y,572,y+185],'size':9,'min_size':9,'valign':'top'},text,fonts);y+=190
  if start==0:
   counts=data['installation'].get('equipment',{})
   text='DESPACHO (cantidades por producto; un dispensario multiproducto puede figurar en más de uno)\n'
   text+='\n'.join(p+': dispensarios '+pending(counts.get(p,{}).get('dispensarios',''))+', mangueras '+pending(counts.get(p,{}).get('mangueras','')) if p in products(data) else p+': No aplica' for p in PRODUCTS)
   write(page,{'rect':[40,685,572,755],'size':9,'min_size':9,'valign':'top'},text,fonts)
