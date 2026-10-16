"""Render detailed, fictional addresses with the logos supplied for visual testing."""
import argparse
import copy
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import fitz
import sasisopa18 as engine
from scripts.ejemplos_visuales import template, text

CASES = [
 ('01-fullok-avenida','FULLOK: avenida, local y colonia','fullok','SERVICIOS DEMO SA',
  'AV. REFORMA 125, LOCAL 2, COL. CENTRO, PUEBLA, PUEBLA, C.P. 72000'),
 ('02-fullok-alcaldia','FULLOK: alcaldía y código postal','fullok','SERVICIOS DEMO SA',
  'CALZ. IGNACIO ZARAGOZA 1845, COL. AGRÍCOLA ORIENTAL, ALC. IZTACALCO, CIUDAD DE MÉXICO, C.P. 08500'),
 ('03-mongas-kilometro','MonGas: carretera y kilómetro','mongas','COMBUSTIBLES DEMO SA',
  'CARRETERA FEDERAL 129, KM 108+500, COL. CENTRO, ZACAPOAXTLA, PUEBLA, C.P. 73680'),
 ('04-mongas-localidad','MonGas: localidad y municipio','mongas','COMBUSTIBLES DEMO SA',
  'CARRETERA AMOZOC-TEZIUTLÁN, KM 108+500, TENEXTATILOYAN, ZAUTLA, PUEBLA, C.P. 73750'),
 ('05-chavana-esquina','Chavana: esquina y municipio largo','chavana','SERVICIO DEMO SA',
  'AV. UNIVERSIDAD 350, ESQ. MORELOS, COL. CENTRO, SAN NICOLÁS DE LOS GARZA, NUEVO LEÓN, C.P. 66400'),
 ('06-chavana-industrial','Chavana: lote y parque industrial','chavana','SERVICIO DEMO SA',
  'BLVD. MIGUEL ALEMÁN 1200, LOTE 8, PARQUE INDUSTRIAL, APODACA, NUEVO LEÓN, C.P. 66600'),
 ('07-arco-local','ARCO: local y colonia','arco','OPERADORA DEMO SA',
  'BLVD. AGUA CALIENTE 1050, LOCAL A, COL. AVIACIÓN, TIJUANA, BAJA CALIFORNIA, C.P. 22014'),
 ('08-arco-carretera','ARCO: carretera, lote y estado','arco','OPERADORA DEMO SA',
  'CARRETERA TRANSPENINSULAR, KM 28+700, LOTE 12, COL. LOS PINOS, ENSENADA, BAJA CALIFORNIA, C.P. 22785'),
]
OVERFLOW = ('CARRETERA FEDERAL AMOZOC-TEZIUTLÁN, KILÓMETRO 108+500, MARGEN DERECHO, '
            'PREDIO LAS FLORES, LOTE 12, MANZANA 8, JUNTA AUXILIAR DE TENEXTATILOYAN, '
            'REFERENCIA FRENTE AL ENTRONQUE PRINCIPAL, MUNICIPIO DE ZAUTLA, ESTADO DE PUEBLA, C.P. 73750')


def slots_for_example(maps):
    slots = [copy.deepcopy(s) for s in maps['I']['pages'][1]['slots']
             if not s['key'].startswith('rol.')
             and not (s['key']=='estacion.numero' and s['rect'][1]>80)
             and not (s['key']=='documento.revision' and s['rect'][1]>80)]
    for slot in slots:slot['clear']=False
    slots.append({'id':'demo-code','key':'dato.codigo','rect':[400,96,550,108],
                  'font':'ArialMT','size':9,'min_size':9,'align':1,'clear':False})
    return slots


def generate(folder):
    folder.mkdir(parents=True,exist_ok=True)
    _,maps=engine.configuration()
    overview=fitz.open()
    board=overview.new_page(width=1224,height=1240)
    reports=[]
    for index,(name,title,brand,company,address) in enumerate(CASES):
        logo=engine.ROOT/'assets'/'pruebas-marcas'/(brand+'.png')
        if not logo.is_file():raise FileNotFoundError(logo)
        with template(title) as doc:
            number=f'E-{30101+index}'
            code=f'{number}.01.PO.01.R1'
            data=engine.empty_project()
            data['values']={'estacion.numero':number,'estacion.razon_social':company,
                            'estacion.direccion':address,'estacion.logo':str(logo),
                            'documento.revision':'1','documento.fecha_revision':'16/10/2026'}
            data['documents']={'I':{'dato.codigo':code}}
            slots=slots_for_example(maps)
            layout={'pages':[{'size':[0.,0.,612.,385.],'slots':slots,'tables':[]}]}
            drawing=lambda p:[{k:v for k,v in d.items() if k!='seqno'} for d in p.get_drawings()]
            before=drawing(doc[0])
            notes=engine.render_page(doc,0,layout,data,'I',engine.FontBook(doc))
            assert drawing(doc[0])==before
            compact=lambda value:''.join(value.split())
            assert compact(address) in compact(doc[0].get_text()),'Se perdió parte de la dirección'
            assert code in doc[0].get_text()
            slot=next(s for s in slots if s['key']=='estacion.logo')
            inserted=next(im for im in doc[0].get_image_info() if fitz.Rect(slot['rect']).contains(fitz.Rect(im['bbox'])+(.001,.001,-.001,-.001)))
            actual=fitz.Rect(inserted['bbox'])
            ratio=inserted['width']/inserted['height']
            assert abs(actual.width/actual.height-ratio)<.001,'Logo deformado'
            note=next(n for n in notes if n['field']=='estacion.direccion')
            text(doc[0],[53,184,559,209],f"Dirección completa: {len(address)} caracteres, {note['lines']} líneas a {note['size']:g} pt.\nAlineada a la derecha, sin recortar ni abreviar automáticamente.",9)
            text(doc[0],[53,215,559,247],'Ubicación ficticia para probar el formato. No identifica una estación real ni una sucursal de la marca.',9)
            # Render the actual PDF page region; no illustrative image generation.
            clip=fitz.Rect(0,0,612,310)
            text(doc[0],[53,263,559,295],'Logo proporcionado para la prueba, colocado sin deformarlo. Plantilla de demostración; los datos y números de estación son ficticios.',8)
            doc[0].get_pixmap(matrix=fitz.Matrix(3,3),clip=clip,alpha=False).save(folder/(name+'.png'))
            x=(index%2)*612;y=(index//2)*310
            board.show_pdf_page(fitz.Rect(x,y,x+612,y+310),doc,0,clip=clip)
            reports.append({'example':name,'brand':brand,'fictional_address':address,
                            'characters':len(address),'lines':note['lines'],'font_size':note['size'],
                            'right_aligned':True,'all_address_text_present':True,
                            'logo_proportions_preserved':True,'borders_preserved':True})
    board.get_pixmap(matrix=fitz.Matrix(1.8,1.8),alpha=False).save(folder/'00-todas-las-ubicaciones.png')
    overview.close()
    with template('9. PRUEBA: DIRECCIÓN QUE NO CABE') as doc:
        slots=slots_for_example(maps)
        layout={'pages':[{'size':[0.,0.,612.,385.],'slots':slots,'tables':[]}]}
        data=engine.empty_project();data['values']={'estacion.direccion':OVERFLOW}
        before=doc[0].get_text()
        try:
            engine.render_page(doc,0,layout,data,'I',engine.FontBook(doc))
        except ValueError as error:
            assert 'no cabe' in str(error)
            assert doc[0].get_text()==before
            slot=next(s for s in slots if s['key']=='estacion.direccion')
            doc[0].draw_rect(fitz.Rect(slot['rect']),color=(.8,.1,.1),width=1)
            text(doc[0],[53,184,559,202],'RECHAZADA: el dato no cabe en el espacio del encabezado.',10,True)
            text(doc[0],[53,207,559,245],'La generación se detiene; no se recorta texto ni se invade otra celda. Es necesario revisar el dato o ajustar su ubicación antes de generar.',9)
            text(doc[0],[53,252,559,310],OVERFLOW,8)
            doc[0].get_pixmap(matrix=fitz.Matrix(3,3),alpha=False).save(folder/'09-direccion-rechazada.png')
            reports.append({'example':'09-direccion-rechazada','fictional_address':OVERFLOW,
                            'characters':len(OVERFLOW),'rejected_as_expected':True,'page_unchanged_before_displaying_error':True})
        else:raise AssertionError('La dirección extrema debería rechazarse')
    (folder/'resultados.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(reports,ensure_ascii=False,indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('output',type=Path)
    generate(parser.parse_args().output)
