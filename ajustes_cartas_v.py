"""Keep names inside the existing designation/acceptance letter spaces."""
def ajustar_cartas_v(layout):
 for pi in (15,16):
  for slot in layout['pages'][pi]['slots']:
   if slot['key'] in ('rol.representante_legal.nombre','rol.representante_tecnico.nombre'):
    slot['min_size']=min(slot['size'],9)
    if pi==15 and slot.get('flow_order')==1 and slot['key']=='rol.representante_legal.nombre':
     slot.setdefault('erase_rect',list(slot['rect']))
     # This continuation occupies the empty left cell, up to the next column.
     slot['rect'][2]=288
 return layout
