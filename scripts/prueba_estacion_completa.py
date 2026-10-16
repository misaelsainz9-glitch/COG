"""Fictional full-profile test; public previews use a synthetic document only."""
import argparse
import copy
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import fitz
import sasisopa18 as engine
from scripts.ejemplos_visuales import template,text
from scripts.ubicaciones_detalladas import slots_for_example
from scripts.vistas_firmas import person_data


def generate(folder,templates=None,batch_output=None):
    folder.mkdir(parents=True,exist_ok=True)
    assets=folder.resolve()/'recursos-demo';assets.mkdir(exist_ok=True)
    data=person_data(assets)
    for person,name in zip(data['people'],('CARLOS MEDINA','ELENA TORRES','JAVIER RUIZ')):
        person['nombre']=name
    inventory=json.loads((engine.ROOT/'campos_sasisopa_18.json').read_text())
    for i,role in enumerate(inventory['roles']):data['roles'].setdefault(role['id'],str(i%3))
    logo=engine.ROOT/'assets/pruebas-marcas/mongas.png'
    data['values']={'estacion.numero':'E-48216','estacion.razon_social':'SERVICIOS DEMO SA',
                    'estacion.direccion':'AV. REFORMA 125, ZAUTLA, PUEBLA, C.P. 73750',
                    'estacion.logo':str(logo),'documento.revision':'2','documento.fecha_revision':'16/10/2026'}
    catalog,maps=engine.configuration()
    report={'fictional_data':True,'public_previews':'synthetic_template_real_engine',
            'logo':'MonGas (aportado por el usuario)',
            'station':{k:v for k,v in data['values'].items() if k!='estacion.logo'},
            'people':[{'nombre':p['nombre'],'puesto':p['puesto']} for p in data['people']],
            'signatures':'Trazos simulados para demostración; no pertenecen a personas reales.'}
    # Public example: same header rules and measured footer spaces, no private PDF.
    with template('PRUEBA CON DATOS FICTICIOS',height=792) as doc:
        page=doc[0]
        page.add_redact_annot((45,345,570,385),fill=(1,1,1));page.apply_redactions()
        text(page,[55,195,558,220],'Vista de prueba: encabezado y firmas',15,True)
        text(page,[55,230,558,275],'Este ejemplo muestra la distribución con datos inventados. Las firmas se colocan en azul dentro de los cuadros, sin nombres de personas.',10)
        source=maps['II']['pages'][19]
        footer=[copy.deepcopy(s) for s in source['slots'] if s['key'] in
                ('rol.elabora.nombre','rol.revisa.nombre','rol.autoriza.nombre')]
        for s,heading,job in zip(footer,('ELABORÓ:','REVISADO POR:','APROBADO POR:'),
                                ('EQUIPO DE TRABAJO','REPRESENTANTE TÉCNICO','ALTA DIRECCIÓN')):
            r=fitz.Rect(s['signature_rect']);outer=r+(-2,-2,2,2)
            page.draw_rect(outer,color=(.2,.2,.2),width=.5)
            text(page,[outer.x0+3,689,outer.x1-3,700],heading,8,align=1)
            text(page,[outer.x0+3,711,outer.x1-3,723],job,7.5,align=1)
            text(page,[outer.x0+3,730,outer.x1-3,741],'Fecha: 01-10-2024',7.5,align=1)
        slots=slots_for_example(maps)
        slots.extend(s for s in engine.slots_for(maps['II'],data,'II',19) if s['key'].endswith('.firma'))
        data_preview=copy.deepcopy(data)
        data_preview['documents']={'DEMO':{'dato.codigo':'E-48216.01.PO.01.R2'}}
        layout={'pages':[{'size':list(page.rect),'slots':slots,'tables':[]}]}
        text(page,[55,760,558,783],'Datos, domicilio y firmas ficticios. Vista ilustrativa; no es una estación real de la marca.',8)
        drawings=page.get_drawings()
        engine.render_page(doc,0,layout,data_preview,'DEMO',engine.FontBook(doc))
        assert page.get_drawings()==drawings
        assert all(p['nombre'] not in page.get_textbox((50,680,560,750)) for p in data['people'])
        assert 'EQUIPO DE TRABAJO' in page.get_text()
        page.get_pixmap(matrix=fitz.Matrix(1.8,1.8),alpha=False).save(folder/'01-documento-completo.png')
        page.get_pixmap(matrix=fitz.Matrix(3,3),clip=(50,30,562,155),alpha=False).save(folder/'02-encabezado.png')
        page.get_pixmap(matrix=fitz.Matrix(3,3),clip=(50,680,562,750),alpha=False).save(folder/'03-firmas.png')
    # Attendance remains manual, with its original geometry and row numbering.
    with fitz.open() as doc:
        page=doc.new_page(width=612,height=520)
        text(page,[55,20,560,45],'LISTA DE ASISTENCIA: VACÍA',16,True)
        text(page,[55,52,560,90],'Sin nombres, puestos, teléfonos ni firmas. Se conservan las filas para llenado manual.',10)
        cells=[copy.deepcopy(s) for s in maps['I']['pages'][9]['slots'] if s['key'].startswith('tabla.I.10.2.')]
        rows=[]
        for i in range(5):
            row=[s for s in cells if s['key'].startswith(f'tabla.I.10.2.{i}.')]
            rows.append((min(s['rect'][1] for s in row)-2,max(s['rect'][3] for s in row)+2))
        edges=[65,96.38,287.45,400.87,492.97,566.6];top=rows[0][0]-24;bottom=rows[-1][1]
        page.draw_rect((edges[0],top,edges[-1],bottom),color=(.2,.2,.2),width=.5)
        for x in edges[1:-1]:page.draw_line((x,top),(x,bottom),color=(.2,.2,.2),width=.5)
        for y,_ in rows:page.draw_line((edges[0],y),(edges[-1],y),color=(.2,.2,.2),width=.5)
        for i,label in enumerate(('N.º','NOMBRE','PUESTO','TELÉFONO','FIRMA')):
            text(page,[edges[i]+2,top+4,edges[i+1]-2,rows[0][0]-4],label,8,True,1)
        for i,row in enumerate(rows):text(page,[67,row[0]+3,94,row[1]-3],str(i+1),9,align=1)
        layout={'pages':[{'size':list(page.rect),'slots':cells,'tables':[]}]}
        engine.render_page(doc,0,layout,data,'DEMO',engine.FontBook(doc))
        assert not page.get_image_info()
        page.get_pixmap(matrix=fitz.Matrix(2.2,2.2),clip=(55,top-10,577,bottom+10),alpha=False).save(folder/'04-asistencia-vacia.png')
    if templates:
        if not batch_output:raise ValueError('Indica --batch-output fuera del repositorio para los PDF privados.')
        paths,warnings=engine.generate(templates,batch_output,data,merge=True)
        rows=0;footer_count=0
        for meta,path in zip(catalog['templates'],paths):
            with fitz.open(path) as doc,fitz.open(Path(templates)/meta['filename']) as original:
                assert len(doc)==meta['pages']
                for pi,spec in enumerate(maps[meta['id']]['pages']):
                    assert doc[pi].rect==original[pi].rect
                    drawings=lambda p:[{k:v for k,v in d.items() if k!='seqno'} for d in p.get_drawings()]
                    assert drawings(doc[pi])==drawings(original[pi]),(meta['id'],pi,'borders')
                    for s in spec['slots']:
                        if s['key'].startswith('tabla.'):
                            assert not doc[pi].get_textbox(fitz.Rect(s['rect'])).strip(),(meta['id'],pi,s['key'])
                    rows+=sum(t['rows'] for t in spec['tables'])
                    for s in engine.slots_for(maps[meta['id']],data,meta['id'],pi):
                        if s.get('locked') and s['key'].endswith('.firma'):
                            footer_count+=1;r=fitz.Rect(s['rect'])+(-.002,-.002,.002,.002)
                            assert any(r.contains(fitz.Rect(im['bbox'])) for im in doc[pi].get_image_info()),(meta['id'],pi,s['key'])
        with fitz.open(paths[-1]) as merged:
            assert len(merged)==523 and len(merged.get_toc())==18
        engine.save_project(Path(batch_output)/'prueba.sasisopa18.json',data)
        report['actual_batch']={'procedures':18,'pages':523,'merged_bookmarks':18,'blank_attendance_rows':rows,
                                'footer_signatures_inside_cells':footer_count,'page_dimensions_and_table_lines':'preserved','warnings':warnings,'passed':True}
    (folder/'resultados.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('output',type=Path)
    parser.add_argument('--templates',type=Path);parser.add_argument('--batch-output',type=Path)
    args=parser.parse_args();generate(args.output,args.templates,args.batch_output)
