import os,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import tkinter as tk
from tkinter import ttk
import editor_sasisopa as ui
import sasisopa18 as e

@unittest.skipUnless(os.environ.get('DISPLAY') and os.environ.get('SASISOPA18_BASE'),'Requires display and local private base')
class InstallationUITests(unittest.TestCase):
 def test_edit_save_load_old_profile_and_preview_annex(self):
  with tempfile.TemporaryDirectory() as folder,patch.object(ui,'ROOT',Path('/tmp')/'ui-installation-test'):
   window=tk.Tk();editor=ui.Editor(window)
   try:
    editor.templates.set(os.environ['SASISOPA18_BASE']);editor.example_installation()
    self.assertTrue(editor.capture()['installation']['enabled']);self.assertEqual(len(editor.installation_tanks),3)
    editor.doc_selector.set('II');editor.page.set(30);editor.update_preview();window.update()
    self.assertIsNotNone(editor.photo);self.assertNotIn('no cabe',editor.status.get())
    editor.page.set(58);editor.show_regions.set(True);editor.update_preview();window.update()
    self.assertIsNotNone(editor.photo);self.assertEqual(editor.preview_page,('II',57));self.assertEqual(editor.page_count.cget('text'),'/ 58')
    editor.installation_tanks[1]['litros']='45000';saved=Path(folder)/'station.json'
    with patch.object(ui.filedialog,'asksaveasfilename',return_value=str(saved)):editor.save()
    editor.installation_tanks=[]
    with patch.object(ui.filedialog,'askopenfilename',return_value=str(saved)):editor.load()
    self.assertEqual(editor.installation_tanks[1]['litros'],'45000')
    legacy=Path(folder)/'legacy.json';d=e.empty_project();d.pop('installation');e.save_project(legacy,d)
    with patch.object(ui.filedialog,'askopenfilename',return_value=str(legacy)):editor.load()
    self.assertFalse(editor.installation_enabled.get());self.assertEqual(editor.installation_tanks,[])
    editor.doc_selector.set('II');editor.add_tank();window.update()
    dialog=next(w for w in window.winfo_children() if isinstance(w,tk.Toplevel));body=dialog.winfo_children()[0]
    rows=[w for w in body.winfo_children() if isinstance(w,ttk.Frame)]
    for row in rows:
     children=row.winfo_children();label=children[0].cget('text');widget=children[1]
     if label=='Número / compartimento':widget.insert(0,'1A')
     elif label=='Capacidad (litros)':widget.insert(0,'50000')
     elif label=='Producto':widget.set('Diésel')
    next(w for w in body.winfo_children() if isinstance(w,ttk.Button)).invoke();window.update()
    self.assertEqual(editor.installation_tanks[0]['numero'],'1A');self.assertTrue(editor.installation_enabled.get())
   finally:editor.close()
