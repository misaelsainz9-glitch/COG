import os,json,hashlib,tempfile,unittest,copy
from pathlib import Path
from unittest.mock import patch
from zipfile import ZipFile
import fitz
from PIL import Image
import sasisopa18 as e
from importar18 import import_zip,clean_bytes
from firma_canvas import signature_png

class Model18Tests(unittest.TestCase):
 def setUp(self):self.p=e.empty_project();self.c,self.m=e.configuration()
 def test_catalog_and_coordinates(self):
  self.assertEqual(len(self.c['templates']),18);self.assertEqual(sum(t['pages'] for t in self.c['templates']),523)
  for meta in self.c['templates']:
   self.assertEqual(meta['pages'],len(self.m[meta['id']]['pages']))
   for p in self.m[meta['id']]['pages']:
    for s in p['slots']:self.assertTrue(fitz.Rect(p['size']).contains(fitz.Rect(s['rect'])),s)
 def test_same_person_can_hold_distinct_roles(self):
  self.p['people']=[{'id':'A','nombre':'PERSONA A','puesto':'PUESTO'}];self.p['roles']={'representante_legal':'A','representante_tecnico':'A'}
  e.validate_project(self.p);self.assertEqual(e.resolve(self.p,'rol.representante_legal.nombre','I'),'PERSONA A')
  self.assertEqual(e.resolve(self.p,'rol.representante_tecnico.nombre','V'),'PERSONA A')
 def test_role_dates_and_contact_are_independent(self):
  self.p['people']=[{'id':'A','nombre':'A','telefono':'111','domicilio':'DOMICILIO PERSONAL'}];self.p['roles']={'representante_tecnico':'A'}
  self.p['values']={'estacion.telefono':'222','estacion.direccion':'DOMICILIO ESTACION','documento.fecha_revision':'01/10/2026'};self.p['documents']={'I':{'documento.fecha_reunion':'02/10/2026'},'V':{'documento.fecha_designacion':'03/10/2026'}}
  self.assertEqual(e.resolve(self.p,'rol.representante_tecnico.telefono','V'),'111')
  self.assertEqual(e.resolve(self.p,'documento.fecha_reunion','V'),'')
  self.assertEqual(e.resolve(self.p,'documento.fecha_revision','I'),'01/10/2026')
 def test_document_revision_does_not_change_other_document_versions(self):
  self.p['documents']={'I':{'documento.revision':'2'}}
  slot={'key':'documento.revision','reference_doc':'VI'}
  self.assertEqual(e.slot_value(self.p,slot,'I'),'')
  self.p['documents']['VI']={'documento.revision':'3'};self.assertEqual(e.slot_value(self.p,slot,'I'),'3')
  self.p['values']['documento.revision']='5';self.assertEqual(e.slot_value(self.p,{'key':'documento.revision','reference_doc':'I'},'I'),'2')
 def test_linked_list_tracks_person_changes(self):
  slot=next(s for p in self.m['I']['pages'] for s in p['slots'] if s['key'].startswith('tabla.') and s['key'].endswith('.nombre'));key=slot['key'];prefix=key.rsplit('.',1)[0]
  self.p['people']=[{'id':'A','nombre':'NOMBRE ANTERIOR'}];self.p['table_people'][prefix]='A';self.p['tables'][key]='NO DEBE USARSE'
  self.p['people'][0]['nombre']='NOMBRE NUEVO';self.assertEqual(e.resolve(self.p,key,'I'),'NOMBRE NUEVO')
 def test_bad_input_rejected(self):
  for values in [{'estacion.numero':'E-12'},{'documento.fecha_revision':'31/02/2026'},{'documento.revision':'-1'}]:
   p=e.empty_project();p['values']=values
   with self.assertRaises(ValueError):e.validate_project(p)
  self.p['roles']={'autoriza':'MISSING'}
  with self.assertRaises(ValueError):e.validate_project(self.p)
 def test_custom_binding_bounds_and_replacement(self):
  self.p['bindings']=[{'id':'B1','doc':'I','page':1,'key':'dato.CURP','rect':[50,200,250,230],'size':9}];e.validate_project(self.p)
  self.p['bindings'][0]['rect']=[-10,200,250,230]
  with self.assertRaises(ValueError):e.validate_project(self.p)
 def test_missing_destination_is_not_silently_ignored(self):
  self.p['documents']={'VI':{'dato.CURP':'VALOR'}}
  with self.assertRaisesRegex(ValueError,'Ubicar campo'):e.check_destinations(self.p,self.m,['VI'])
 def test_failed_profile_save_preserves_existing_files(self):
  with tempfile.TemporaryDirectory() as root:
   p=Path(root)/'datos.json';p.write_text('previous');tmp=p.with_name(p.name+'.tmp');tmp.write_text('user file')
   with self.assertRaises(FileExistsError):e.save_project(p,self.p)
   self.assertEqual(p.read_text(),'previous');self.assertEqual(tmp.read_text(),'user file')
 def test_project_roundtrip_roles_tables_bindings(self):
  with tempfile.TemporaryDirectory() as root:
   path=Path(root)/'proyecto.json';self.p['bindings']=[{'id':'B1','doc':'I','page':1,'key':'dato.Mi campo','rect':[50,200,250,230],'size':9}];self.p['documents']={'I':{'dato.Mi campo':'EJEMPLO'}}
   e.save_project(path,self.p);self.assertEqual(e.load_project(path),self.p)

class Integration18Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  folder=os.environ.get('SASISOPA18_BASE')
  if not folder:raise unittest.SkipTest('Indica SASISOPA18_BASE con los 18 PDF limpios privados.')
  cls.base=Path(folder);cls.catalog,cls.maps=e.configuration()
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name);self.out=self.root/'lote';self.p=e.empty_project()
 def test_empty_all_18_identical_and_merged_523(self):
  paths,warnings=e.generate(self.base,self.out,self.p,merge=True);self.assertEqual(len(paths),19);self.assertEqual(warnings,[])
  for meta,path in zip(self.catalog['templates'],paths):self.assertEqual(path.read_bytes(),(self.base/meta['filename']).read_bytes())
  with fitz.open(paths[-1]) as doc:self.assertEqual(len(doc),523);self.assertEqual(len(doc.get_toc()),18)
 def test_all_18_common_data_and_structure_preserved(self):
  self.p['values']={'estacion.numero':'E-99999','estacion.razon_social':'ESTACION EJEMPLO SA','estacion.direccion':'AV. PRINCIPAL 123, COL. CENTRO, PUEBLA, C.P. 72000','documento.revision':'2','documento.fecha_revision':'15/10/2026'}
  paths,warnings=e.generate(self.base,self.out,self.p,merge=True);self.assertEqual(len(paths),19)
  with fitz.open(paths[-1]) as merged:
   offset=0
   for meta,path in zip(self.catalog['templates'],paths):
    with fitz.open(path) as out,fitz.open(self.base/meta['filename']) as original:
     self.assertEqual(len(out),meta['pages'])
     for i,page in enumerate(out):
      self.assertEqual(page.rect,original[i].rect)
      drawings=lambda p:[{k:v for k,v in d.items() if k!='seqno'} for d in p.get_drawings()]
      self.assertEqual(drawings(page),drawings(original[i]),(meta['id'],i+1))
      self.assertEqual(page.get_text(),merged[offset+i].get_text())
      slots=self.maps[meta['id']]['pages'][i]['slots']
      if any(s['key']=='estacion.numero' for s in slots):self.assertIn('99999',''.join(page.get_text().split()),(meta['id'],i+1))
      self.assertEqual(original[i].get_text().count('AUTORIZO'),page.get_text().count('AUTORIZO'))
     offset+=len(out)
    self.assertEqual(hashlib.sha256((self.base/meta['filename']).read_bytes()).hexdigest(),meta['sha256'])
 def test_roles_organigram_names_initials(self):
  self.p['people']=[{'id':'A','nombre':'PERSONA UNO','iniciales':'PU'},{'id':'B','nombre':'PERSONA DOS','iniciales':'PD'}]
  role_ids=json.loads((e.ROOT/'campos_sasisopa_18.json').read_text())['roles'];self.p['roles']={r['id']:'A' if i%2 else 'B' for i,r in enumerate(role_ids)}
  paths,_=e.generate(self.base,self.out,self.p,selected=['I','II','V'])
  with fitz.open(paths[1]) as doc:
   text=' '.join(doc[32].get_text().split());self.assertIn('PERSONA UNO',text);self.assertIn('PERSONA DOS',text)
   self.assertIn('PU',text);self.assertIn('PD',text)
  with fitz.open(paths[2]) as doc:
   text=' '.join(doc[5].get_text().split());self.assertIn('PERSONA UNO',text);self.assertIn('PERSONA DOS',text);self.assertIn('ALTA DIRECCIÓN',text)
 def test_custom_data_binding_date_and_actual_preview(self):
  self.p['documents']={'VI':{'dato.CURP':'PRUEBA123'}}
  self.p['bindings']=[{'id':'B1','doc':'VI','page':27,'key':'dato.CURP','rect':[50,290,190,310],'font':'ArialMT','size':9,'min_size':9}]
  blob,notes,warnings=e.preview(self.base,self.p,'VI',27);self.assertTrue(blob.startswith(b'\x89PNG'))
  paths,_=e.generate(self.base,self.out,self.p,selected=['VI'])
  with fitz.open(paths[0]) as doc:self.assertIn('PRUEBA123',doc[27].get_text());self.assertEqual(len(doc),45)
 def test_designation_and_acceptance_dates_independent(self):
  self.p['documents']={'V':{'documento.fecha_designacion':'15/10/2026','documento.fecha_aceptacion':'16/10/2026'}}
  paths,_=e.generate(self.base,self.out,self.p,selected=['V'])
  with fitz.open(paths[0]) as doc:
   self.assertIn('15/10/2026',doc[15].get_text());self.assertNotIn('16/10/2026',doc[15].get_text())
   self.assertIn('16/10/2026',doc[16].get_text());self.assertNotIn('15/10/2026',doc[16].get_text())
 def test_logo_signature_and_table_fit_existing_spaces(self):
  logo=self.root/'logo.png';Image.new('RGB',(100,100),'blue').save(logo);sig=self.root/'firma.png';signature_png([[(10,40),(110,80),(290,40)]]).save(sig)
  self.p['values']={'estacion.logo':str(logo)};self.p['people']=[{'id':'A','nombre':'PERSONA UNO','puesto':'OPERADOR','firma':str(sig)}];self.p['roles']={'autoriza':'A'}
  table=next(p['tables'][0] for p in self.maps['I']['pages'] if p['tables']);prefix='tabla.'+table['id']+'.0';self.p['table_people'][prefix]='A'
  paths,_=e.generate(self.base,self.out,self.p,selected=['I'])
  with fitz.open(paths[0]) as doc:
   for pi,info in enumerate(self.maps['I']['pages']):
    images=doc[pi].get_image_info()
    for slot in info['slots']:
     if slot['key']=='estacion.logo' or slot['key']=='rol.autoriza.firma' or slot['key']==prefix+'.firma':
      matches=[im for im in images if im['width']>1 and (fitz.Rect(slot['rect'])+(-.002,-.002,.002,.002)).contains(fitz.Rect(im['bbox']))]
      self.assertTrue(matches,(pi+1,slot['key']))
 def test_moving_revision_clears_original_value(self):
  old=next(slot for slot in self.maps['I']['pages'][1]['slots'] if slot['key']=='documento.revision' and slot['rect'][1]<90)
  self.p['values']={'documento.revision':'2'};self.p['bindings']=[{'id':'B1','doc':'I','page':1,'key':'documento.revision','replace_id':old['id'],'rect':[50,450,100,470],'size':9,'min_size':9}]
  paths,_=e.generate(self.base,self.out,self.p,selected=['I'])
  with fitz.open(paths[0]) as doc:
   self.assertNotIn('0',doc[1].get_textbox(old['rect']));self.assertIn('2',doc[1].get_textbox([50,450,100,470]))
 def test_personal_address_does_not_copy_station_address(self):
  self.p['values']={'estacion.direccion':'AVENIDA TEST 100'}
  self.p['people']=[{'id':'A','nombre':'PERSONA UNO','domicilio':'DOMICILIO PERSONAL'}];self.p['roles']={'representante_tecnico':'A'}
  paths,_=e.generate(self.base,self.out,self.p,selected=['V'])
  with fitz.open(paths[0]) as doc:
   text=' '.join(doc[15].get_text().split());self.assertIn('DOMICILIO PERSONAL',text);self.assertIn('AVENIDA TEST 100',text)
 def test_blank_fields_and_unmodified_text_remain(self):
  self.p['values']={'estacion.numero':'E-99999'};paths,_=e.generate(self.base,self.out,self.p,selected=['I'])
  with fitz.open(paths[0]) as out,fitz.open(self.base/'PROCEDIMIENTO I.pdf') as original:
   for i,page in enumerate(out):
    for slot in self.maps['I']['pages'][i]['slots']:
     if slot['key'].startswith('documento.fecha_revision'):self.assertEqual(page.get_textbox(slot['rect']),original[i].get_textbox(slot['rect']))
 def test_long_text_no_partial_batch_and_no_overwrite(self):
  self.p['values']={'estacion.direccion':'DIRECCION MUY LARGA '*100}
  with self.assertRaisesRegex(ValueError,'no cabe'):e.generate(self.base,self.out,self.p)
  self.assertFalse(self.out.exists());self.out.mkdir();keep=self.out/'user.txt';keep.write_text('keep')
  with self.assertRaisesRegex(ValueError,'ya existe'):e.generate(self.base,self.out,e.empty_project())
  self.assertEqual(keep.read_text(),'keep')
 def test_missing_or_altered_template_rejected_before_output(self):
  with self.assertRaisesRegex(ValueError,'Falta'):e.generate(self.root,self.out,self.p,selected=['I'])
  p=self.root/'PROCEDIMIENTO I.pdf';p.write_bytes((self.base/p.name).read_bytes()+b'changed')
  with self.assertRaisesRegex(ValueError,'no coincide'):e.generate(self.root,self.out,self.p,selected=['I'])
  self.assertFalse(self.out.exists())
 def test_invalid_selection_and_save_failure(self):
  for selection in [[],['INVALIDO'],['I','I']]:
   with self.assertRaisesRegex(ValueError,'Selecciona'):e.generate(self.base,self.out,self.p,selection)
  real_open=Path.open
  def fail(path,*args,**kwargs):
   if args and args[0]=='xb' and path.name=='PROCEDIMIENTO II.pdf':raise OSError('disk failure')
   return real_open(path,*args,**kwargs)
  keep=self.root/'keep';keep.write_text('safe')
  with patch.object(Path,'open',fail):
   with self.assertRaisesRegex(OSError,'disk failure'):e.generate(self.base,self.out,self.p,selected=['I','II'])
  self.assertFalse(self.out.exists());self.assertEqual(keep.read_text(),'safe')

class Import18Tests(unittest.TestCase):
 def test_missing_zip_members_does_not_write_anything(self):
  with tempfile.TemporaryDirectory() as r:
   r=Path(r);z=r/'input.zip'
   with ZipFile(z,'w') as f:f.writestr('../unrelated.txt','do not extract')
   with self.assertRaisesRegex(ValueError,'Faltan'):import_zip(z,r/'plantillas')
   self.assertFalse((r/'plantillas').exists());self.assertFalse((r.parent/'unrelated.txt').exists())
 def test_original_zip_import_exact_clean_hashes(self):
  source=os.environ.get('SASISOPA18_ZIP')
  if not source:self.skipTest('Indica SASISOPA18_ZIP con el ZIP original privado.')
  with tempfile.TemporaryDirectory() as root:
   root=Path(root);out=import_zip(source,root);records=json.loads((e.ROOT/'limpieza18.json').read_text())
   self.assertEqual(len(list(out.glob('*.pdf'))),18)
   for name,record in records.items():self.assertEqual(hashlib.sha256((out/name).read_bytes()).hexdigest(),record['target_sha256'])
