import copy,os,tempfile,unittest
from pathlib import Path
import fitz
import sasisopa18 as e
import valores_predeterminados as defaults

class DefaultsTests(unittest.TestCase):
 def test_defaults_are_project_local_and_explicit_values_win(self):
  d=e.empty_project();d['values']={'estacion.numero':'E-12345'};d['documents']={'II':{'dato.estudio':'Valor base'}};d['defaults']=defaults.snapshot(d)
  d['values']['estacion.numero']=' ';d['documents']['II']['dato.estudio']='';d['documents']['II']['dato.otro']='Nuevo'
  result=defaults.effective(d)
  self.assertEqual(result['values']['estacion.numero'],'E-12345');self.assertEqual(result['documents']['II']['dato.estudio'],'Valor base');self.assertEqual(d['documents']['II']['dato.estudio'],'')
  d['documents']['II']['dato.estudio']='Sustitución';self.assertEqual(defaults.effective(d)['documents']['II']['dato.estudio'],'Sustitución')
  d.pop('defaults');self.assertEqual(defaults.effective(d)['values']['estacion.numero'],' ')
 def test_deleted_fuel_is_not_restored_and_zero_counts_win(self):
  d=e.empty_project();d['installation']={'enabled':True,'tanks':[{'numero':'1','producto':'Magna','litros':'60000','presion_operacion':'2 bar'},{'numero':'2','producto':'Diésel','litros':'40000'}],'equipment':{'Magna':{'dispensarios':'2','mangueras':'4'},'Diésel':{'dispensarios':'1','mangueras':'2'}}};d['defaults']=defaults.snapshot(d)
  d['installation']['tanks'].pop();d['installation']['tanks'][0].update(litros='',presion_operacion='');d['installation']['equipment']['Diésel']={'dispensarios':'','mangueras':''};d['installation']['equipment']['Magna']['mangueras']='0'
  e.validate_project(d);result=defaults.effective(d)
  self.assertEqual(len(result['installation']['tanks']),1);self.assertEqual(result['installation']['tanks'][0]['litros'],'60000');self.assertEqual(result['installation']['equipment']['Magna']['mangueras'],'0');self.assertEqual(result['installation']['equipment']['Diésel']['dispensarios'],'')
  result['installation']['tanks'][0]['producto']='Premium';result['installation']['tanks'][0]['presion_operacion']='';self.assertEqual(defaults.effective(result)['installation']['tanks'][0]['presion_operacion'],'')
 def test_role_and_person_fields_fall_back_without_filling_attendance(self):
  d=e.empty_project();d['people']=[{'id':'p','nombre':'Persona Ejemplo','puesto':'Responsable','firma':''}];d['roles']={'representante_legal':'p'};d['defaults']=defaults.snapshot(d);d['roles']={};d['people']=[]
  result=defaults.effective(d);e.validate_project(result)
  self.assertEqual(result['roles']['representante_legal'],'p');self.assertEqual(result['people'][0]['nombre'],'Persona Ejemplo');self.assertFalse(result['tables'])
 def test_invalid_and_inconsistent_defaults_rejected(self):
  d=e.empty_project();d['defaults']={'values':{'estacion.numero':'MAL'}}
  with self.assertRaises(ValueError):e.validate_project(d)
  d['defaults']={'defaults':{}}
  with self.assertRaises(ValueError):e.validate_project(d)
  d['defaults']={'values':{'documento.fecha_inicio_estudio':'20/10/2026','documento.fecha_fin_estudio':'19/10/2026'}}
  with self.assertRaises(ValueError):e.validate_project(d)

@unittest.skipUnless(os.environ.get('SASISOPA18_BASE'),'Requiere base real')
class DefaultsPDFTests(unittest.TestCase):
 def test_empty_values_render_default_at_multiple_locations_after_save_load(self):
  base=Path(os.environ['SASISOPA18_BASE']);d=e.empty_project();d['values']={'estacion.numero':'E-12345'};d['documents']={'I':{'dato.comentario':'Texto predeterminado'}}
  for i,rect in enumerate([[85,250,400,275],[85,280,400,305]]):d['bindings'].append({'id':'Bdefault'+str(i),'doc':'I','page':0,'key':'dato.comentario','rect':rect,'size':9})
  d['defaults']=defaults.snapshot(d);d['values']['estacion.numero']='';d['documents']['I']['dato.comentario']=''
  with tempfile.TemporaryDirectory() as tmp:
   profile=Path(tmp)/'datos.json';e.save_project(profile,d);loaded=e.load_project(profile);paths,_=e.generate(base,Path(tmp)/'salida',loaded,selected=['I'])
   with fitz.open(paths[0]) as doc:
    for b in d['bindings']:self.assertIn('Texto predeterminado',doc[0].get_textbox(b['rect']))
    self.assertGreaterEqual(doc[0].get_text().count('12345'),1)
   self.assertEqual(loaded['documents']['I']['dato.comentario'],'')

class SharedDefaultsTests(unittest.TestCase):
 def test_shared_text_uses_per_location_numbering(self):
  d=e.empty_project();d['values']['dato.normativa']='Referencia del proyecto';d['defaults']=defaults.snapshot(d);d['values']['dato.normativa']=''
  a={'key':'dato.normativa','text_prefix':'6. '};b={'key':'dato.normativa','text_prefix':'14. '}
  self.assertEqual(e.slot_value(d,a,'II'),'6. Referencia del proyecto');self.assertEqual(e.slot_value(d,b,'III'),'14. Referencia del proyecto')

class PortableDefaultsTests(unittest.TestCase):
 def test_project_relative_images_resolve_for_values_and_defaults(self):
  d=e.empty_project();d['values']['estacion.logo']='assets/logo.png';d['defaults']=defaults.snapshot(d)
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp)/'proyecto.json';e.save_project(p,d);loaded=e.load_project(p)
   self.assertEqual(loaded['values']['estacion.logo'],str(Path(tmp)/'assets/logo.png'));self.assertEqual(loaded['defaults']['values']['estacion.logo'],str(Path(tmp)/'assets/logo.png'))

class CorrectedDefaultsTests(unittest.TestCase):
 def test_clearing_project_defaults_does_not_restore_an_unsafe_source_passage(self):
  d=e.empty_project();slot={'key':'dato.protocolo','preserve_default':True,'default_text':'Texto corregido de la plantilla'}
  self.assertEqual(e.slot_value(d,slot,'XIII'),'Texto corregido de la plantilla')
  d['documents']['XIII']={'dato.protocolo':'Protocolo capturado'};self.assertEqual(e.slot_value(d,slot,'XIII'),'Protocolo capturado')
  d['documents']['XIII']['dato.protocolo']='';self.assertEqual(e.slot_value(d,slot,'XIII'),'Texto corregido de la plantilla')
