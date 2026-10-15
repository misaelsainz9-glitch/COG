"""Checks the installed executable without loading or sending private documents."""
import hashlib
import io
import json
import sys
import platform
from pathlib import Path
import tempfile
import tkinter as tk
from unittest.mock import patch
import fitz
from PIL import Image
from PIL import ImageTk
import editor_sasisopa as ui
import importar18
import sasisopa18 as engine
from firma_canvas import signature_png
from rutas_app import RESOURCE_ROOT, user_root


def check_installation(progress=lambda stage: None):
    progress('resources')
    catalog, maps = engine.configuration()
    assert len(catalog['templates']) == 18
    assert sum(t['pages'] for t in catalog['templates']) == 523
    assert len(json.loads((importar18.ROOT / 'limpieza18.json').read_text(encoding='utf-8'))) == 18
    assert len(json.loads((RESOURCE_ROOT / 'campos_sasisopa_18.json').read_text(encoding='utf-8'))['roles']) > 0
    if getattr(sys, 'frozen', False):
        assert not any(RESOURCE_ROOT.rglob('*.pdf')), 'Private PDF unexpectedly packaged'
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
            doc.save(source)
        custom_catalog = {'templates': [{'id': 'I', 'title': 'Prueba ficticia', 'filename': source.name,
                                        'pages': 1, 'sha256': hashlib.sha256(source.read_bytes()).hexdigest()}]}
        custom_maps = {'I': {'pages': [{'size': [0., 0., 612., 792.], 'tables': [], 'slots': [
            {'id': 'I.1.0', 'key': 'estacion.numero', 'rect': [50, 50, 180, 80], 'size': 9,
             'min_size': 9, 'font': 'Arial', 'kind': 'text', 'clear': True, 'align': 0}]}]}}
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
                progress('profile_and_pdf')
                project = editor.capture()
                profile = folder / 'demo.sasisopa18.json'
                engine.save_project(profile, project)
                assert engine.load_project(profile) == project
                files, warnings = engine.generate(folder, folder / 'salida', project, ['I'], merge=True)
                assert len(files) == 2
                with fitz.open(files[0]) as result:
                    assert 'E-99999' in result[0].get_text()
                    assert 'CONTENIDO FIJO DE PRUEBA' in result[0].get_text()
                    assert len(result[0].get_drawings()) == 1
            finally:
                if editor is not None:
                    editor.close()
                else:
                    window.destroy()
    return {'ok': True, 'python': platform.python_version(), 'system': platform.system(), 'catalog_documents': 18, 'catalog_pages': 523,
            'window': True, 'preview': True, 'save_load': True, 'synthetic_pdf': True,
            'private_documents_packaged': False, 'data_directory': str(user_root())}
