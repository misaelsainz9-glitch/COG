"""Desktop smoke test with a synthetic PDF; never needs private documents."""
import hashlib
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import tkinter as tk
import fitz
import editor_sasisopa as ui
import sasisopa18 as engine


@unittest.skipUnless(os.name == 'nt' or os.environ.get('DISPLAY'), 'Requires a desktop display')
class DesktopSmokeTests(unittest.TestCase):
    def test_window_capture_preview_save_and_generate(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            shutil.copyfile(ui.ROOT / 'campos_sasisopa_18.json', folder / 'campos_sasisopa_18.json')
            source = folder / 'PROCEDIMIENTO I.pdf'
            with fitz.open() as doc:
                page = doc.new_page(width=612, height=792)
                page.draw_rect(fitz.Rect(40, 40, 572, 140))
                page.insert_text((50, 170), 'CONTENIDO FIJO DE PRUEBA')
                doc.save(source)
            catalog = {'templates': [{'id': 'I', 'filename': source.name, 'title': 'Prueba ficticia',
                                     'pages': 1, 'sha256': hashlib.sha256(source.read_bytes()).hexdigest()}]}
            maps = {'I': {'pages': [{'size': [0.0, 0.0, 612.0, 792.0], 'tables': [], 'slots': [
                {'id': 'I.1.0', 'key': 'estacion.numero', 'rect': [50, 50, 180, 80],
                 'size': 9, 'min_size': 9, 'font': 'Arial', 'kind': 'text', 'clear': True}]}]}}
            with patch.object(engine, 'configuration', return_value=(catalog, maps)), patch.object(ui, 'ROOT', folder):
                window = tk.Tk()
                editor = None
                try:
                    editor = ui.Editor(window)
                    editor.templates.set(str(folder))
                    editor.vars['estacion.numero'].set('E-99999')
                    editor.vars['documento.revision'].set('1')
                    editor.vars['documento.fecha_revision'].set('15/10/2026')
                    window.update()
                    editor.update_preview()
                    self.assertIsNotNone(editor.photo)
                    project = editor.capture()
                    self.assertEqual(engine.resolve(project, 'documento.revision', 'I'), '1')
                    self.assertEqual(engine.resolve(project, 'documento.fecha_revision', 'I'), '15/10/2026')
                    # This synthetic page has only a station slot.
                    project['values'].pop('documento.revision')
                    project['values'].pop('documento.fecha_revision')
                    saved = folder / 'prueba.sasisopa18.json'
                    engine.save_project(saved, project)
                    self.assertEqual(engine.load_project(saved)['values']['estacion.numero'], 'E-99999')
                    paths, _ = engine.generate(folder, folder / 'resultados', project, ['I'], merge=True)
                    self.assertEqual(len(paths), 2)
                    with fitz.open(paths[0]) as result:
                        text = result[0].get_text()
                        self.assertIn('E-99999', text)
                        self.assertIn('CONTENIDO FIJO DE PRUEBA', text)
                        self.assertEqual(len(result[0].get_drawings()), 1)
                    self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(), catalog['templates'][0]['sha256'])
                finally:
                    if editor is not None:
                        editor.close()
                    else:
                        window.destroy()
