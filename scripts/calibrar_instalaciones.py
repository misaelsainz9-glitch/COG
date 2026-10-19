"""Geometry of variable installation data; contains no private identities."""
import re
import fitz

def calibrar_instalaciones(layout,source,roman):
 def add(pi,key,rect,size=11.04,minimum=8,align=0):
  slots=layout['pages'][pi]['slots'];id=f'{roman}.{pi+1}.inst.{len(slots)}'
  slots.append({'id':id,'key':'instalacion.'+key,'rect':list(rect),'font':'ArialMT','size':size,'min_size':minimum,'align':align,'kind':'text','clear':True,'erase_full':True})
 if roman=='II':
  xs=[86.42,135.86,213.77,320.09,383.95,447.79,525.7];ys=[408.79,438.07,467.35,496.75];pi=29
 elif roman=='XIII':
  xs=[85.34,155.9,218.21,290.69,361.27,431.83,509.86];ys=[199.46,229.85,260.21,290.57];pi=35
 else:pi=None
 if pi is not None:
  for row in range(3):
   for col,field in enumerate(['numero','litros','producto','cupula','presion_vapor','temperatura_almacen']):
    add(pi,f'tanque.{row}.{field}',[xs[col]+1,ys[row]+1,xs[col+1]-1,ys[row+1]-1],9,7,1)
 if roman=='II':
  add(29,'almacenamiento',[85.1,177,531,335]);add(29,'despacho',[85.1,539,531,567],10,8)
  add(28,'productos',[238,285,379,301],9,7,1)
  # The node number is independent of the physical tank number.
  for pi,product,top,bottom in [(32,0,522,560),(33,1,184.8,241),(33,2,241.5,297)]:
   for field,left,right in [('nombre',23,141),('incluye',147,265),('condiciones',271,389),('plano',395,513)]:
    add(pi,f'producto.{product}.{field}',[left,top,right,bottom],9,7)
   add(pi,f'producto.{product}.no_aplica',[519,top,760,bottom],9,7)
  # Continuation of Magna's node from page 33.
  add(33,'producto.0.continuacion',[147,158.8,265,184.3],8,7)
  add(33,'producto.0.flujo',[271,158.8,389,184.3],9,7)
  for pi in range(33,54):
   for block in source[pi].get_text('dict')['blocks']:
    for line in block.get('lines',[]):
     text=''.join(s['text'] for s in line['spans']);box=fitz.Rect(line['bbox'])
     if box.y0<154 or box.y0>580 or pi==33 and box.y0<340:continue
     product=0 if pi<41 or pi==41 and box.y0<465 else 1 if pi<48 else 2
     for pattern,field,label in [(r'(?i).*Presión de operación\s*:?\s*2\.45\s*kg/cm2','presion_operacion','Presión de operación: '),(r'Temperatura:\s*30°C','temperatura_operacion','Temperatura: '),(r'Flujo:\s*30\s*Lts/min\.','flujo','Flujo: '),(r'Planos/ Referencias:\s*(?:PE-03|IM-01)','plano','Planos / referencias: ')]:
      if re.fullmatch(pattern,text.strip()):
       # Whole labelled line, not a new fragment on the old baseline.
       add(pi,f'producto.{product}.{field}',[53.4,box.y0,540,box.y1],11.04,8)
       layout['pages'][pi]['slots'][-1]['installation_prefix']=label
  for pi in range(54,57):
   for product,word in enumerate(['Magna','Premium','Diesel']):
    for rect in source[pi].search_for(word):
     if 220<rect.x0<290:add(pi,f'producto.{product}.nombre',rect,11.04,8)
 elif roman=='XIII':
  add(34,'almacenamiento',[85.1,564,531,665]);add(35,'despacho',[85.1,335.5,531,364],10,8)
  add(32,'lista',[85.1,588,531,647]);add(39,'lista',[85.1,329,531,388])
 elif roman=='III':
  # A generic spill consequence must not assert that absent diesel is stored.
  for block in source[24].get_text('dict')['blocks']:
   for line in block.get('lines',[]):
    text=''.join(s['text'] for s in line['spans'])
    if 'Derrame de Diesel en' in text:
     rect=fitz.Rect(line['bbox']);rect.x1+=10
     style=line['spans'][0];add(24,'derrame',rect,style['size'],8)
