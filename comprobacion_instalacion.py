"""Checks the installed executable without loading or sending private documents."""
import hashlib
import io
import json
import sys
import platform
from pathlib import Path
import tempfile
import zipfile
import importar_requisitos
import calendarios
import tkinter as tk
from unittest.mock import patch
import fitz
from PIL import Image
from PIL import ImageTk
import editor_sasisopa as ui
import importar18
import sasisopa18 as engine
from firma_canvas import signature_png, INK_BLUE
from rutas_app import RESOURCE_ROOT, user_root


def check_installation(progress=lambda stage: None):
    progress('resources')
    catalog, maps = engine.configuration()
    assert (RESOURCE_ROOT/'assets'/'logo-pemex.png').is_file()
    assert len(catalog['templates']) == 18
    assert sum(t['pages'] for t in catalog['templates']) == 523
    assert len(json.loads((importar18.ROOT / 'limpieza18.json').read_text(encoding='utf-8'))) == 18
    assert len(json.loads((RESOURCE_ROOT / 'campos_sasisopa_18.json').read_text(encoding='utf-8'))['roles']) > 0
    if getattr(sys, 'frozen', False):
        assert not any(RESOURCE_ROOT.rglob('*.pdf')), 'Private PDF unexpectedly packaged'
    neutral = engine.new_project()
    assert neutral['fresh_project'] and not neutral['people'] and not neutral['roles']
    assert not neutral.get('defaults') and len(neutral['bindings']) > 3000
    data = engine.empty_project()
    data['values'] = {'estacion.numero': 'E-99999'}
    progress('synthetic_document')
    with tempfile.TemporaryDirectory() as temporary:
        folder = Path(temporary)
        signature_png([[(10, 40), (110, 80), (290, 40)]]).save(folder / 'firma-demo.png')
        source = folder / 'PROCEDIMIENTO I.pdf'
        with fitz.open() as doc:
            page = doc.new_page(width=612, height=792)
            page.draw_rect(fitz.Rect(40, 40, 572, 140))
            page.insert_text((50, 170), 'CONTENIDO FIJO DE PRUEBA')
            page = doc.new_page(width=612, height=792)
            page.insert_text((50, 270), 'NOMBRE / PUESTO / FIRMA')
            page.draw_rect((40, 280, 570, 320))
            page.insert_text((50, 300), 'DATOS ANTERIORES')
            page.insert_image((410,285,490,315),filename=str(folder/'firma-demo.png'))
            for left in (50,220,390):
                page.draw_rect((left,680,left+160,740))
                page.insert_text((left+10,695),'ELABORO / REVISO / APROBO',fontsize=7)
                page.insert_text((left+10,722),'PUESTO FIJO',fontsize=8)
                page.insert_text((left+10,735),'Fecha: 01-10-2024',fontsize=8)
            doc.save(source)
        custom_catalog = {'templates': [{'id': 'I', 'title': 'Prueba ficticia', 'filename': source.name,
                                        'pages': 2, 'sha256': hashlib.sha256(source.read_bytes()).hexdigest()}]}
        custom_maps = {'I': {'pages': [{'size': [0., 0., 612., 792.], 'tables': [], 'slots': [
            {'id': 'I.1.0', 'key': 'estacion.numero', 'rect': [50, 50, 180, 80], 'size': 9,
             'min_size': 9, 'font': 'Arial', 'kind': 'text', 'clear': True, 'align': 0},
            {'id':'I.1.1','key':'estacion.logo','rect':[190,50,260,80],'kind':'image','clear':False}]}]}}
        footer_slots=[]
        for left,role in zip((50,220,390),('elabora','revisa','autoriza')):
            footer_slots.append({'id':f'I.2.{role}','key':f'rol.{role}.nombre',
                                 'rect':[left+3,699,left+157,710],
                                 'signature_rect':[left+2,682,left+158,738],
                                 'font':'Arial','size':8,'min_size':8,'kind':'text'})
        attendance=[{'id':'I.2.rowname','key':'tabla.I.2.1.0.nombre','rect':[45,282,390,318],'kind':'text'},
                    {'id':'I.2.rowsign','key':'tabla.I.2.1.0.firma','rect':[400,282,568,318],'kind':'image'}]
        custom_maps['I']['pages'].append({'size':[0.,0.,612.,792.],
                                         'tables':[{'id':'I.2.1','rows':1,'columns':['nombre','firma'],'page':2}],
                                         'slots':footer_slots+attendance})
        with patch.object(engine, 'configuration', return_value=(custom_catalog, custom_maps)), patch.object(ui, 'ROOT', folder):
            progress('create_window')
            window = tk.Tk()
            editor = None
            try:
                progress('create_editor')
                editor = ui.Editor(window)
                editor.templates.set(str(folder))
                editor.vars['estacion.numero'].set('E-99999')
                progress('update_window')
                window.update()
                progress('preview')
                editor.update_preview()
                assert editor.photo is not None
                progress('import_word')
                word=folder/'requisitos-demo.docx'
                xml='<w:document xmlns:w="'+importar_requisitos.NS['w']+'"><w:body><w:tbl><w:tr><w:tc><w:p><w:r><w:t>Nombre o razón social: EMPRESA DEMO</w:t></w:r></w:p></w:tc></w:tr></w:tbl></w:body></w:document>'
                with zipfile.ZipFile(word,'w') as archive:archive.writestr('word/document.xml',xml)
                proposals,_=importar_requisitos.read_candidates(word)
                assert proposals[0]['value']=='EMPRESA DEMO'
                with patch.object(ui.filedialog,'askopenfilename',return_value=str(word)):
                    editor.import_requirements()
                window.update()
                dialog=next(w for w in window.winfo_children() if isinstance(w,tk.Toplevel))
                assert 'Revisar' in dialog.title()
                dialog.destroy()
                progress('monthly_calendars')
                calendar_data=engine.empty_project()
                calendar_data['values']['documento.fecha_inicio_estudio']='01/11/2026'
                with fitz.open() as calendar_doc:
                    calendar_page=calendar_doc.new_page(width=792,height=612)
                    calendar_report=calendarios.apply(calendar_page,'XIV',9,calendar_data,engine._write,engine.FontBook(calendar_doc))
                    assert calendar_report[0]['months'][0]=='2026-11'
                    assert calendar_report[0]['months'][-1]=='2027-10'
                    assert len(calendar_report[0]['months'])==12
                    assert '2026-2027' in calendar_page.get_text()
                progress('profile_and_pdf')
                project = editor.capture()
                project['people']=[{'id':'DEMO','nombre':'PERSONA NO IMPRIMIR','firma':str(folder/'firma-demo.png')}]
                project['roles']={role:'DEMO' for role in ('elabora','revisa','autoriza')}
                project['table_people']={'tabla.I.2.1.0':'DEMO'}
                profile = folder / 'demo.sasisopa18.json'
                engine.save_project(profile, project)
                assert engine.load_project(profile) == project
                files, warnings = engine.generate(folder, folder / 'salida', project, ['I'], merge=True)
                assert len(files) == 2
                with fitz.open(files[0]) as result:
                    assert 'E-99999' in result[0].get_text()
                    assert 'CONTENIDO FIJO DE PRUEBA' in result[0].get_text()
                    assert len(result[0].get_drawings()) == 1
                    assert len(result)==2
                    page=result[1]
                    assert 'PERSONA NO IMPRIMIR' not in page.get_text()
                    assert 'DATOS ANTERIORES' not in page.get_text()
                    assert page.get_text().count('PUESTO FIJO')==3
                    assert page.get_text().count('01-10-2024')==3
                    assert len(page.get_drawings())==4
                    assert not page.get_textbox((45,282,568,318)).strip()
                    images=page.get_image_info(xrefs=True)
                    assert len(images)==3
                    for slot in engine.slots_for(custom_maps['I'],project,'I',1):
                        if not slot.get('locked'):continue
                        bounds=fitz.Rect(slot['rect'])+(-.002,-.002,.002,.002)
                        image=next(im for im in images if bounds.contains(fitz.Rect(im['bbox'])))
                        assert fitz.Rect(image['bbox']).width>150
                        assert fitz.Rect(image['bbox']).height>20
                        with Image.open(io.BytesIO(result.extract_image(image['xref'])['image'])) as ink:
                            assert any(color==INK_BLUE and count>10 for count,color in ink.convert('RGB').getcolors(ink.width*ink.height))
                progress('new_project')
                neutral_demo=engine.empty_project();neutral_demo['fresh_project']=True
                with patch.object(engine,'new_project',return_value=neutral_demo),patch.object(ui.messagebox,'askyesnocancel',return_value=False):
                    assert editor.new_project()
                assert editor.data['fresh_project'] and not editor.data['people']
                assert not editor.vars['estacion.numero'].get()
            finally:
                if editor is not None:
                    editor.close()
                else:
                    window.destroy()
    return {'ok': True, 'python': platform.python_version(), 'system': platform.system(), 'catalog_documents': 18, 'catalog_pages': 523,
            'new_project': True, 'neutral_template': True, 'monthly_calendars': True, 'word_import_review': True, 'window': True, 'preview': True, 'save_load': True, 'synthetic_pdf': True,
            'large_blue_signatures': True, 'manual_attendance': True, 'private_documents_packaged': False, 'data_directory': str(user_root())}
