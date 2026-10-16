"""Measure existing footer cells without changing their text or borders."""
import fitz


def calibrar_firmas(layout,doc):
    for pi,spec in enumerate(layout['pages']):
        names=[s for s in spec['slots'] if pi and s['key'] in
               ('rol.elabora.nombre','rol.revisa.nombre','rol.autoriza.nombre')
               and s['rect'][1]>spec['size'][3]*.65]
        if not names:continue
        lines=[d['rect'] for d in doc[pi].get_drawings()]
        for slot in names:
            r=fitz.Rect(slot['rect']);x=(r.x0+r.x1)/2;y=(r.y0+r.y1)/2
            hs=[a for a in lines if a.height<2 and a.width>50 and a.x0<x<a.x1]
            vs=[a for a in lines if a.width<2 and a.height>10 and a.y0<y<a.y1]
            top=max((a.y1 for a in hs if a.y1<y),default=0)
            bottom=min((a.y0 for a in hs if a.y0>y),default=doc[pi].rect.height)
            left=max((a.x1 for a in vs if a.x1<x),default=0)
            right=min((a.x0 for a in vs if a.x0>x),default=doc[pi].rect.width)
            if not(10<bottom-top<100 and 90<right-left<250):
                raise ValueError(f'No se pudo delimitar el cuadro: página {pi+1}, {slot["id"]}')
            slot['signature_rect']=[round(left+2,3),round(top+2,3),round(right-2,3),round(bottom-2,3)]
    return layout
