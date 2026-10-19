"""Agreed changes for the first cover of procedure II only."""
def ajustar_portada_ii(layout):
    slots=layout['pages'][0]['slots']
    address=next(s for s in slots if s['key']=='estacion.direccion')
    old=address.get('erase_rect',address['rect'])[:]
    center=(old[0]+old[2])/2
    company=next(s for s in slots if s['key']=='estacion.razon_social')
    date=next(s for s in slots if s['key']=='documento.fecha_revision')
    address.update(rect=[center-160,company['rect'][3]+5,center+160,date['rect'][1]-4],
                   erase_rect=[old[0],company['rect'][3]+5,old[2],date['rect'][1]-4],
                   align=1,balance_lines=True)
    left=next(s for s in slots if s['key']=='rol.elabora.firma')
    right=next(s for s in slots if s['key']=='rol.autoriza.firma')
    label=next(s for s in slots if s['key']=='rol.elabora.nombre')
    center=(label['rect'][0]+label['rect'][2])/2
    width=right['rect'][2]-right['rect'][0]
    left['rect']=[center-width/2,right['rect'][1],center+width/2,right['rect'][3]]
    # The source has a bare E here. Replace it together with the digits so the
    # cover always shows the full E-00000 without duplicating the old prefix.
    top=next(s for s in slots if s['key']=='estacion.numero' and s['rect'][1]<60)
    top['rect']=[491.38,top['rect'][1],540,top['rect'][3]]
    top['erase_rect']=top['rect'][:]
    top.pop('transform',None)
    return layout
