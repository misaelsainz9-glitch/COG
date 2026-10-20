"""Pruebas de interacción reales de Tk; requieren un DISPLAY, no Windows simulado."""
import os,tempfile,time,unittest,shutil
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import tkinter as tk
from tkinter import ttk
import sasisopa18 as engine
import editor_sasisopa as ui
import valores_predeterminados as defaults


def descendants(widget):
 for child in widget.winfo_children():
  yield child;yield from descendants(child)

@unittest.skipUnless(os.environ.get('DISPLAY') and os.environ.get('SASISOPA18_BASE'),'Requiere DISPLAY y SASISOPA18_BASE para probar Tk real.')
class Editor18Tests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.folder=Path(self.tmp.name)
  shutil.copyfile(engine.ROOT/'campos_sasisopa_18.json',self.folder/'campos_sasisopa_18.json')
  self.root_patch=patch.object(ui,'ROOT',self.folder);self.root_patch.start();self.addCleanup(self.root_patch.stop)
  self.window=tk.Tk();self.editor=ui.Editor(self.window);self.addCleanup(self.editor.close);self.editor.templates.set(os.environ['SASISOPA18_BASE']);self.window.update();self.editor.update_preview();self.window.update()
 def wait_for_work(self):
  deadline=time.monotonic()+40
  while self.editor.busy and time.monotonic()<deadline:self.window.update();time.sleep(.02)
  self.assertFalse(self.editor.busy,'El trabajo no terminó');self.window.update()
 def test_form_roles_list_binding_save_load_and_generate(self):
  ed=self.editor;self.assertIsNotNone(ed.photo)
  ed.vars['estacion.numero'].set('E-99999');ed.vars['estacion.razon_social'].set('EMPRESA TEST SA');ed.update_preview();self.assertIsNotNone(ed.photo)
  ed.add_person();self.window.update();dialog=next(w for w in self.window.winfo_children() if isinstance(w,tk.Toplevel))
  entries=[w for w in descendants(dialog) if isinstance(w,ttk.Entry)];entries[0].insert(0,'PERSONA UNO');entries[1].insert(0,'OPERADOR')
  next(w for w in descendants(dialog) if isinstance(w,ttk.Button) and w.cget('text')=='Guardar persona').invoke();self.window.update()
  self.assertEqual(len(ed.data['people']),1);person=ed.data['people'][0];label=ed.id_to_choice[person['id']]
  ed.role_vars['representante_legal'].set(label);ed.role_vars['representante_tecnico'].set(label);ed.capture()
  self.assertEqual(ed.data['roles']['representante_legal'],ed.data['roles']['representante_tecnico'])
  ed.change_table();self.assertEqual(ed.table_vars,{})
  self.assertFalse(any(isinstance(w,ttk.Combobox) for w in descendants(ed.table_box)))
  ed.people_list.selection_set(person['id']);ed.delete_person();self.assertFalse(ed.data['people'])
  ed.doc_selector.set('VI');ed.page.set(28);ed.data['documents'].setdefault('VI',{})['dato.CURP']='PRUEBA123';ed.build_doc_fields();ed.refresh_field_choices();ed.update_preview();self.window.update()
  ed.field_choice.set('dato.CURP');ed.place_mode.set(True);ed.canvas.xview_moveto(0);ed.canvas.yview_moveto(0)
  ed.pointer_down(SimpleNamespace(x=50,y=440));ed.pointer_move(SimpleNamespace(x=210,y=465));ed.pointer_up(SimpleNamespace(x=210,y=465));self.assertEqual(len(ed.data['bindings']),1);self.assertIsNotNone(ed.photo)
  project=self.folder/'proyecto.sasisopa18.json'
  with patch.object(ui.filedialog,'asksaveasfilename',return_value=str(project)):ed.save()
  self.assertTrue(project.is_file());ed.vars['estacion.numero'].set('E-88888')
  with patch.object(ui.filedialog,'askopenfilename',return_value=str(project)):ed.load()
  self.assertEqual(ed.vars['estacion.numero'].get(),'E-99999');self.assertEqual(len(ed.data['bindings']),1)
  for id,var in ed.selected.items():var.set(id=='VI')
  with patch.object(ui.messagebox,'showinfo'),patch.object(ui.messagebox,'showerror') as error:
   ed.generate();self.wait_for_work();error.assert_not_called()
  self.assertEqual(len(list((self.folder/'salidas').glob('*/PROCEDIMIENTO VI.pdf'))),1)
 def test_text_that_does_not_fit_keeps_preview_for_adjustment(self):
  ed=self.editor;ed.vars['estacion.direccion'].set('DIRECCION MUY LARGA '*100);ed.update_preview()
  self.assertIsNotNone(ed.photo);self.assertIn('no cabe',ed.status.get())
 def test_import_button_worker_and_remembered_folder(self):
  ed=self.editor
  with patch.object(ui.filedialog,'askopenfilename',return_value='original.zip'),patch.object(ui,'import_zip',return_value=Path(os.environ['SASISOPA18_BASE'])) as importer,patch.object(ui.messagebox,'showinfo'):
   ed.import_templates();self.wait_for_work();importer.assert_called_once()
  self.assertEqual(ed.templates.get(),os.environ['SASISOPA18_BASE']);self.assertTrue((self.folder/'datos_locales'/'base18.json').is_file())
 def test_project_dates_and_person_initials_are_editable_through_form(self):
  ed=self.editor;ed.add_person();self.window.update()
  dialog=next(w for w in self.window.winfo_children() if isinstance(w,tk.Toplevel))
  entries=[w for w in descendants(dialog) if isinstance(w,ttk.Entry)]
  entries[0].insert(0,'Ulises Hernández Cruz');self.window.update()
  self.assertEqual(entries[2].get(),'UHC');self.assertIn('readonly',entries[2].state())
  next(w for w in descendants(dialog) if isinstance(w,ttk.Button) and w.cget('text')=='Guardar persona').invoke();self.window.update()
  person=ed.data['people'][0];ed.role_vars['representante_legal'].set(ed.id_to_choice[person['id']])
  ed.vars['documento.fecha_inicio_estudio'].set('02/11/2026');ed.vars['documento.fecha_fin_estudio'].set('05/11/2026')
  ed.doc_selector.set('II');ed.page.set(33);ed.update_preview();self.window.update()
  self.assertIsNotNone(ed.photo);self.assertNotIn('no cabe',ed.status.get())
  data=ed.capture();self.assertEqual(engine.resolve(data,'rol.representante_legal.iniciales','II'),'UHC')
  self.assertEqual(data['values']['documento.fecha_inicio_estudio'],'02/11/2026')

 def test_project_defaults_multiline_and_hidden_corrections_survive_save_load(self):
  ed=self.editor;ed.vars['estacion.numero'].set('E-12345');ed.doc_selector.set('I')
  ed.data['documents']['I']={'dato.editable':'Primera línea\nSegunda línea','dato.interno':'Corrección fija'}
  ed.data['bindings']=[{'id':'TENEX.editable','doc':'I','page':0,'key':'dato.editable','rect':[85,250,400,300],'size':9,'label':'Información del estudio','multiline':True,'editable':True},{'id':'TENEX.interno','doc':'I','page':0,'key':'dato.interno','rect':[85,310,400,330],'size':9}]
  ed.build_doc_fields();self.window.update()
  self.assertIn('dato.editable',ed.doc_vars);self.assertNotIn('dato.interno',ed.doc_vars)
  ed.set_defaults();ed.vars['estacion.numero'].set('');ed.doc_vars['dato.editable'].set('');data=ed.capture()
  self.assertEqual(data['documents']['I']['dato.interno'],'Corrección fija');self.assertEqual(defaults.effective(data)['documents']['I']['dato.editable'],'Primera línea\nSegunda línea')
  project=self.folder/'predeterminados.json';engine.save_project(project,data);loaded=engine.load_project(project)
  self.assertEqual(engine.resolve(loaded,'estacion.numero','I'),'E-12345')
  ed.build_doc_fields();self.assertIn('dato.editable',ed.doc_vars);ed.clear_defaults();self.assertNotIn('defaults',ed.capture())

 def test_shared_fields_and_page_filter_keep_values_between_pages(self):
  ed=self.editor;ed.data['values']['dato.comun']='Texto común'
  ed.data['bindings']=[{'id':'Bshared','doc':'I','page':0,'key':'dato.comun','rect':[85,250,400,275],'size':9,'shared':True,'label':'Normativa compartida'}, {'id':'Blater','doc':'I','page':1,'key':'dato.otro','rect':[85,250,400,275],'size':9,'label':'Página dos'}]
  ed.data['documents']['I']={'dato.otro':'Texto de página dos'};ed.build_shared_fields();ed.build_doc_fields();self.window.update()
  self.assertIn('dato.comun',ed.vars);self.assertNotIn('dato.comun',ed.doc_vars);self.assertNotIn('dato.otro',ed.doc_vars)
  ed.vars['dato.comun'].set('Nuevo texto común');ed.page.set(2);self.window.update();self.assertEqual(ed.doc_vars['dato.otro'].get(),'Texto de página dos')
  ed.doc_vars['dato.otro'].set('Cambio conservado');ed.page.set(1);self.window.update();self.assertNotIn('dato.otro',ed.doc_vars)
  self.assertEqual(ed.capture()['documents']['I']['dato.otro'],'Cambio conservado');self.assertEqual(ed.capture()['values']['dato.comun'],'Nuevo texto común')

 def test_loaded_global_dates_remain_editable_and_are_not_lost_on_capture(self):
  ed=self.editor;ed.data['values']['documento.fecha_firmas']='19/10/2026';ed.data['values']['dato.fecha_actual_operativa']='19/10/2026';ed.build_shared_fields()
  self.assertIn('documento.fecha_firmas',ed.vars);self.assertIn('dato.fecha_actual_operativa',ed.vars)
  ed.vars['dato.fecha_actual_operativa'].set('20/10/2026');data=ed.capture();self.assertEqual(data['values']['documento.fecha_firmas'],'19/10/2026');self.assertEqual(data['values']['dato.fecha_actual_operativa'],'20/10/2026')
  ed.vars['dato.fecha_actual_operativa'].set('31/02/2026')
  with self.assertRaises(ValueError):engine.validate_project(ed.capture())
