"""Measure the existing six-member table and study-date occurrences locally."""
import re
import fitz
from equipo_hazop import ROLES,DATES

def calibrar_equipo(layout,source):
 date_keys={key for key,label in DATES}
 for spec in layout['pages']:spec['slots']=[s for s in spec['slots'] if s['key'] not in date_keys]
 page=source[32];spec=layout['pages'][32]
 table=next(t for t in page.find_tables().tables if 'Cargo/especialidad' in str(t.extract()[:2]))
 for role,row in zip(ROLES,table.rows[1:7]):
  for attr,col in [('nombre',0),('puesto',2),('empresa',5)]:
   key=f'rol.{role}.{attr}';old=next((s for s in spec['slots'] if s['key']==key),None)
   rect=fitz.Rect(row.cells[col])+(3,2,-3,-2)
   slot={**(old or {}),'id':f'II.33.equipo.{role}.{attr}','key':key,'rect':list(rect),'erase_rect':list(rect),'font':'ArialMT','size':9,'min_size':8,'align':1,'kind':'text','clear':True,'erase_full':True,'team_member':True}
   if old and old['id']!=slot['id']:slot['legacy_ids']=list(dict.fromkeys(old.get('legacy_ids',[])+[old['id']]))
   spec['slots']=[s for s in spec['slots'] if s['key']!=key];spec['slots'].append(slot)
 for pi,spec in enumerate(layout['pages']):
  if pi<32:continue
  # Expand no names into adjacent cells, and retain each initial's own position.
  for slot in spec['slots']:
   if slot['key'].startswith('rol.') and slot['key'].endswith('.iniciales'):
    new_id=f'II.{pi+1}.iniciales.{slot["key"]}.{round(slot["rect"][1],2)}'
    if slot['id']!=new_id:slot['legacy_ids']=list(dict.fromkeys(slot.get('legacy_ids',[])+[slot['id']]))
    slot['id']=new_id
    slot['min_size']=6
    y=slot['rect'][1]
    if pi==32 and y>520:slot['hazop_product']='Magna'
    elif pi==33 and 184<y<241:slot['hazop_product']='Premium'
    elif pi==33 and 241<y<298:slot['hazop_product']='Diésel'
  for block in source[pi].get_text('dict')['blocks']:
   for line in block.get('lines',[]):
    text=''.join(s['text'] for s in line['spans'])
    if pi==32 and text.strip().startswith('Fecha de inicio:'):key='documento.fecha_inicio_estudio'
    elif pi==32 and text.strip().startswith('Fecha de finalización:'):key='documento.fecha_fin_estudio'
    elif pi<=53:key='documento.fecha_sesion_hazop'
    else:continue
    for date in re.findall(r'\b\d{2}/\d{2}/\d{4}\b',text):
     for rect in source[pi].search_for(date):
      if abs(rect.y0-line['bbox'][1])>.5:continue
      r=fitz.Rect(rect);r.x1=min(r.x1+12,source[pi].rect.width-20)
      slot={'id':f'II.{pi+1}.estudio.{len(spec["slots"])}','key':key,'rect':list(r),'erase_rect':list(rect),'font':'ArialMT','size':11.04,'min_size':9,'align':0,'kind':'text','clear':True,'erase_full':True}
      if key=='documento.fecha_sesion_hazop':slot['fallback_key']='documento.fecha_inicio_estudio'
      y=rect.y0
      if pi==32 and y>520:slot['hazop_product']='Magna'
      elif pi==33 and 184<y<241:slot['hazop_product']='Premium'
      elif pi==33 and 241<y<298:slot['hazop_product']='Diésel'
      spec['slots'].append(slot)
