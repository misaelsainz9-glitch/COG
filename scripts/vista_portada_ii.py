"""Public illustration of the reviewed cover; no private PDF is loaded."""
import argparse,copy,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import fitz
import sasisopa18 as engine
from firma_canvas import signature_png
from scripts.ejemplos_visuales import text


def generate(folder):
    folder.mkdir(parents=True,exist_ok=True)
    resources=folder/'recursos-demo';resources.mkdir(exist_ok=True)
    _,maps=engine.configuration();spec=copy.deepcopy(maps['II']['pages'][0])
    slots=spec['slots']
    find=lambda key:next(s for s in slots if s['key']==key)
    # The public illustration uses Helvetica; the private PDF retains Aptos.
    for slot in slots:
        if slot.get('transform')=='revision_label':slot['size']=slot['min_size']=10
    data=engine.empty_project();data['values']={
        'estacion.numero':'E-48216','estacion.razon_social':'SERVICIOS DEMO SA DE CV',
        'estacion.direccion':'CARRETERA FEDERAL 129 KM 108.5, COL. CENTRO, ZAUTLA, PUEBLA, C.P. 73750',
        'estacion.logo':str(engine.ROOT/'assets/logo-pemex.png'),
        'documento.revision':'2','documento.fecha_revision':'16/10/2026'}
    signature=resources/'trazo-simulado.png'
    signature_png([[(30,130),(75,60),(120,140),(195,55),(250,135),(335,70),(420,125),(535,90)],[(45,165),(540,140)]]).save(signature)
    with fitz.open() as source:
        page=source.new_page(width=612,height=792)
        text(page,[330,35.35,490,48.83],'ESTACIÓN DE SERVICIO NO:',11.04,align=2)
        text(page,[75,137,537,169],'II.1. PROCEDIMIENTO PARA LA IDENTIFICACIÓN DE ASPECTOS AMBIENTALES Y PARA LA EVALUACIÓN DE IMPACTOS AMBIENTALES.',11.04,align=1)
        text(page,[210,197.73,288.53,211.21],'CÓDIGO: E-',11.04,True,2)
        code_tail='.02.PO.01.R';width,_=engine._line_width(fitz.Font('hebo'),code_tail,11.04)
        engine._write(page,{'rect':[318.20,197.73,376.37,211.21],'font':'Arial-BoldMT','size':11.04,'min_size':11.04,'x_scale':(376.37-318.20)/width},code_tail,engine.FontBook(source))
        text(page,[230,299.64,326.45,313.12],'ESTACIÓN: E-',11.04,True,2)
        text(page,[160,547.49,233,560.97],'ELABORÓ',11.04,align=1)
        text(page,[382,547.49,453,560.97],'AUTORIZÓ',11.04,align=1)
        text(page,[135,561.41,258,574.89],'EQUIPO DE TRABAJO',11.04,align=1)
        text(page,[65,651,547,677],'VISTA ILUSTRATIVA CON DATOS FICTICIOS. Distribución basada en los espacios reales de la portada II. Las guías no se imprimen.',9,align=1)
        blob=source.tobytes()
    for signed in (False,True):
        project=copy.deepcopy(data)
        if signed:
            project['people']=[{'id':'DEMO','firma':str(signature)}]
            project['roles']={'elabora':'DEMO','autoriza':'DEMO'}
        with fitz.open(stream=blob,filetype='pdf') as doc:
            layout={'pages':[copy.deepcopy(spec)]}
            for s in layout['pages'][0]['slots']:s['clear']=False
            engine.render_page(doc,0,layout,project,'II',engine.FontBook(doc))
            for slot in slots:
                if not signed or slot['key'].endswith('.firma'):
                    doc[0].draw_rect(slot['rect'],color=(0,.63,.65),width=.65,dashes='[3 2]')
            if not signed:
                doc[0].get_pixmap(matrix=fitz.Matrix(1.6,1.6),alpha=False).save(folder/'01-portada-campos.png')
            name='03-firmas-cargadas.png' if signed else '02-firmas-espacios.png'
            doc[0].get_pixmap(matrix=fitz.Matrix(3,3),clip=(85,455,525,585),alpha=False).save(folder/name)
    left=fitz.Rect(find('rol.elabora.firma')['rect']);right=fitz.Rect(find('rol.autoriza.firma')['rect'])
    report={'scope':'II, primera portada; siguientes imágenes pendientes de revisión',
            'synthetic_public_illustration':True,'cover_address':'centered_balanced_lines',
            'address_font_size':find('estacion.direccion')['size'],
            'left_signature_size':[left.width,left.height],
            'right_signature_size':[right.width,right.height],
            'same_top_and_bottom':left.y0==right.y0 and left.y1==right.y1,
            'top_station_uses_full_E_hyphen_prefix':True}
    (folder/'resultados.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('output',type=Path)
    generate(parser.parse_args().output)
