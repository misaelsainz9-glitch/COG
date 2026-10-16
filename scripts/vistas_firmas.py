"""Public signature placement proposals using real map geometry and invented names.

No private PDF or real signature is read. New positioning proposals are marked
explicitly; this script does not change production maps or program settings.
"""
import argparse
import copy
import json
import math
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import fitz
import sasisopa18 as engine
from firma_canvas import signature_png
from scripts.ejemplos_visuales import text


def drawings(page):
    return [{k:v for k,v in d.items() if k!='seqno'} for d in page.get_drawings()]


def base_doc():
    doc=fitz.open();doc.new_page(width=612,height=792);return doc


def person_data(assets):
    data=engine.empty_project()
    for i,name in enumerate(('ANA LÓPEZ','LUIS PÉREZ','MARÍA GARCÍA')):
        path=assets/f'firma-{i+1}-simulada.png'
        stroke=[]
        for j in range(160):
            x=35+j*3.2
            y=95+35*math.sin(j*.17+i)+12*math.sin(j*.43)
            stroke.append((x,y))
        signature_png([stroke,[(55,160),(500,140)]]).save(path)
        data['people'].append({'id':str(i),'nombre':name,'puesto':('OPERADOR','SUPERVISOR','RESPONSABLE')[i],
                               'telefono':f'55501000{i+1:02d}','firma':str(path)})
    data['roles']={'elabora':'0','revisa':'1','autoriza':'2','representante_legal':'2','representante_tecnico':'1'}
    return data


def choose(maps,document,page,keys):
    return [copy.deepcopy(s) for s in maps[document]['pages'][page-1]['slots'] if s['key'] in keys]


def generate(folder):
    folder.mkdir(parents=True,exist_ok=True)
    assets=folder/'recursos-demo';assets.mkdir(exist_ok=True)
    data=person_data(assets)
    _,maps=engine.configuration()
    cases=[]

    # Existing two-column cover, with no invented signature table.
    doc=base_doc();page=doc[0]
    text(page,[130,596,280,609],'ELABORÓ',11,True,1)
    text(page,[350,596,500,609],'AUTORIZÓ',11,True,1)
    slots=choose(maps,'I',1,{'rol.elabora.nombre','rol.elabora.firma','rol.autoriza.nombre','rol.autoriza.firma'})
    cases.append(('01-portada','1. Portada: elaboración y autorización',doc,slots,copy.deepcopy(data),
                  fitz.Rect(72,505,540,635),'Posiciones existentes: procedimiento I, página 1.','existing'))

    # Footer labels and name positions from II/20; propose equal safe ink boxes.
    doc=base_doc();page=doc[0]
    page.draw_rect(fitz.Rect(55,685.9,558,745),color=(.2,.2,.2),width=.5)
    for x in (221.5,389):page.draw_line((x,685.9),(x,745),color=(.2,.2,.2),width=.5)
    for i,(label,job) in enumerate(zip(('ELABORÓ:','REVISADO POR:','APROBADO POR:'),('EQUIPO DE TRABAJO','REPRESENTANTE TÉCNICO','ALTA DIRECCIÓN'))):
        x=55+i*(503/3)
        text(page,[x+4,687.9,x+503/3-4,698],label,8,align=1)
        text(page,[x+4,710,x+503/3-4,722],job,7.5,align=1)
        text(page,[x+4,729,x+503/3-4,741],'Fecha: 01-10-2024',7.5,align=1)
    keys={f'rol.{role}.{field}' for role in ('elabora','revisa','autoriza') for field in ('nombre','firma')}
    slots=[s for s in engine.slots_for(maps['II'],data,'II',19) if s['key'] in keys]
    cases.append(('02-pie-tres-firmas','2. Pie: firmas dentro de los cuadros, sin nombres',doc,slots,copy.deepcopy(data),
                  fitz.Rect(45,680,567,752),'Firmas dentro de cada cuadro. Se conservan puestos, rótulos y fechas; no se insertan nombres.','inside_cells_no_names'))

    # Legal representative: leave a gap below Atentamente and above the line.
    doc=base_doc();page=doc[0]
    page.draw_rect(fitz.Rect(155.15,680.22,487.8,753.42),color=(.2,.2,.2),width=.5)
    text(page,[290.33,684.45,355.82,696.76],'Atentamente',10)
    page.draw_line((161.18,723),(481.89,723),color=(.2,.2,.2),width=.6)
    text(page,[239,725,252,738],'C.',11.04)
    slots=[s for s in choose(maps,'V',16,{'rol.representante_legal.nombre','rol.representante_legal.firma'})
           if s['key'].endswith('.firma') or s['rect'][1]>700]
    for slot in slots:
        if slot['key'].endswith('.firma'):slot['rect'][1]=699
    cases.append(('03-representante-legal','3. Carta: firma del representante legal',doc,slots,copy.deepcopy(data),
                  fitz.Rect(140,674,500,762),'Propuesta: bajo «Atentamente», sin tocar el nombre ni la línea.','proposed_label_gap'))

    # Acceptance letter has a real line but no saved automatic signature slot.
    doc=base_doc();page=doc[0]
    text(page,[260.81,543.16,340,556.54],'Atentamente',11.04)
    page.draw_line((150.02,611.5),(439.75,611.5),color=(.2,.2,.2),width=.6)
    text(page,[202,613.39,220,626],'C.',11.04)
    slots=[s for s in choose(maps,'V',17,{'rol.representante_tecnico.nombre'}) if s['rect'][1]>600]
    slots.append({'id':'propuesta-aceptacion','key':'rol.representante_tecnico.firma','kind':'image',
                  'rect':[253.78,570,350.02,608.5],'clear':False})
    cases.append(('04-aceptacion-tecnico','4. Aceptación: firma del representante técnico',doc,slots,copy.deepcopy(data),
                  fitz.Rect(135,532,455,640),'Propuesta nueva en la línea existente; esta firma aún requiere guardar su ubicación.','proposed_unmapped_signature'))

    # Five original row positions; fill three and leave two empty.
    doc=base_doc();page=doc[0]
    slots=[copy.deepcopy(s) for s in maps['I']['pages'][9]['slots'] if s['key'].startswith('tabla.I.10.2.')]
    rows=[]
    for i in range(5):
        row=[s for s in slots if s['key'].startswith(f'tabla.I.10.2.{i}.')]
        rows.append((min(s['rect'][1] for s in row)-2,max(s['rect'][3] for s in row)+2))
    edges=[65,96.38,287.45,400.87,492.97,566.6]
    top=rows[0][0]-24;bottom=rows[-1][1]
    page.draw_rect(fitz.Rect(edges[0],top,edges[-1],bottom),color=(.2,.2,.2),width=.5)
    for x in edges[1:-1]:page.draw_line((x,top),(x,bottom),color=(.2,.2,.2),width=.5)
    for y in [r[0] for r in rows]:page.draw_line((edges[0],y),(edges[-1],y),color=(.2,.2,.2),width=.5)
    for i,label in enumerate(('N.º','NOMBRE','PUESTO','TELÉFONO','FIRMA')):
        text(page,[edges[i]+2,top+4,edges[i+1]-2,rows[0][0]-4],label,8,True,1)
    linked=copy.deepcopy(data)
    for i in range(5):
        text(page,[67,rows[i][0]+3,94,rows[i][1]-3],str(i+1),9,align=1)
        if i<3:linked['table_people'][f'tabla.I.10.2.{i}']=str(i)
    cases.append(('05-lista-asistencia','5. Asistencia: todas las filas vacías',doc,slots,linked,
                  fitz.Rect(55,top-8,576,bottom+9),'Sin nombres, puestos, teléfonos ni firmas. Se conservan las cinco filas para llenado manual.','existing'))

    overview=fitz.open();board=overview.new_page(width=1224,height=1200)
    reports=[]
    for index,(name,title,doc,slots,project,clip,caption,status) in enumerate(cases):
        pair=fitz.open();sheet=pair.new_page(width=1224,height=240)
        text(sheet,[18,5,1205,28],title,14,True)
        text(sheet,[18,30,602,44],'ESPACIOS MARCADOS (guías azules)',9,True)
        text(sheet,[630,30,1206,44],'RESULTADO SEGÚN LAS REGLAS ACTUALES',9,True)
        base_bytes=doc.tobytes()
        for slot in slots:
            if slot['key'].endswith('.firma') and not slot['key'].startswith('tabla.'):
                doc[0].draw_rect(fitz.Rect(slot['rect']),color=(0,.45,.8),width=.6,dashes='[3 2]')
        sheet.show_pdf_page(fitz.Rect(18,48,600,194),doc,0,clip=clip)
        clean=fitz.open(stream=base_bytes,filetype='pdf')
        for slot in slots:slot['clear']=False
        before=drawings(clean[0])
        layout={'pages':[{'size':[0.,0.,612.,792.],'slots':slots,'tables':[]}]}
        engine.render_page(clean,0,layout,project,'DEMO',engine.FontBook(clean))
        assert drawings(clean[0])==before
        image_slots=[s for s in slots if s['key'].endswith('.firma') and not s['key'].startswith('tabla.') and engine.resolve(project,s['key'],'DEMO')]
        for slot in image_slots:
            assert any(fitz.Rect(slot['rect']).contains(fitz.Rect(im['bbox'])+(.001,.001,-.001,-.001)) for im in clean[0].get_image_info())
        sheet.show_pdf_page(fitz.Rect(630,48,1212,194),clean,0,clip=clip)
        sheet.insert_textbox(fitz.Rect(18,198,1206,218),caption,fontname='helv',fontsize=10)
        sheet.insert_textbox(fitz.Rect(18,220,1206,237),'Vista de demostración basada en espacios existentes. Las guías no se imprimen. Ninguna firma pertenece a una persona real.',fontname='helv',fontsize=8)
        sheet.get_pixmap(matrix=fitz.Matrix(1.8,1.8),alpha=False).save(folder/(name+'.png'))
        board.show_pdf_page(fitz.Rect(0,index*240,1224,(index+1)*240),pair,0)
        reports.append({'example':name,'status':status,'synthetic_names_and_signatures':True,
                        'signature_count':len(image_slots),'signature_bounds_verified':True,
                        'production_maps_changed':False})
        clean.close();pair.close();doc.close()
    board.get_pixmap(matrix=fitz.Matrix(1.6,1.6),alpha=False).save(folder/'00-todas-las-firmas.png')
    overview.close()
    (folder/'resultados.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(reports,ensure_ascii=False,indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('output',type=Path)
    generate(parser.parse_args().output)
