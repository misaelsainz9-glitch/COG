import copy
import tempfile
import unittest
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape
import importar_requisitos as importer
import sasisopa18 as engine

class ImportRequirementsTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.folder=Path(self.tmp.name)
 def doc(self,rows,name='datos.docx'):
  xml='<w:document xmlns:w="'+importer.NS['w']+'"><w:body><w:tbl>'
  for row in rows:xml+='<w:tr>'+''.join('<w:tc><w:p><w:r><w:t>'+escape(c)+'</w:t></w:r></w:p></w:tc>' for c in row)+'</w:tr>'
  xml+='</w:tbl></w:body></w:document>';p=self.folder/name
  with zipfile.ZipFile(p,'w') as z:z.writestr('word/document.xml',xml)
  return p
 def fields(self,rows):return importer.read_candidates(self.doc(rows))
 def test_station_labels_and_no_number_inference(self):
  fields,warnings=self.fields([['DATOS','Nombre o razón social: EMPRESA DEMO Número de la estación: EMPRESA DEMO Dirección: CALLE 25 CP. 72000 Teléfono oficina: 55 1234 5678 Correo oficina: es 12345 @ ejemplo .com']])
  values={x['key']:x['value'] for x in fields}
  self.assertNotIn('estacion.numero',values);self.assertEqual(values['estacion.correo'],'es12345@ejemplo.com');self.assertEqual(values['estacion.telefono'],'5512345678');self.assertEqual(values['estacion.direccion'],'CALLE 25 CP. 72000');self.assertTrue(any('Número' in w for w in warnings))
 def test_unique_people_roles_tanks_equipment_and_propagation(self):
  fields,_=self.fields([['DATOS','Número de la estación: E-12345'],['REPRESENTANTE LEGAL','ANA PRUEBA'],['JEFE DE OPERACIONES','ANA PRUEBA'],['1','MARCA','6 0000','MAGNA',''],['2','MARCA','40000','DIESEL',''],['DISPENSARIOS','Magna:','2','Diesel:','1'],['MANGUERAS','Magna:','4','Diesel:','2']])
  source=engine.empty_project();original=copy.deepcopy(source);data=importer.apply_candidates(source,{x['key']:x['value'] for x in fields})
  self.assertEqual(source,original);self.assertEqual(len(data['people']),1);self.assertEqual(data['roles']['representante_legal'],data['roles']['jefe_operaciones']);self.assertEqual(data['installation']['tanks'][0]['litros'],'60000')
  import instalaciones,equipo_hazop
  self.assertEqual(instalaciones.products(data),['Magna','Diésel']);self.assertIn('100,000',instalaciones.value(data,'instalacion.almacenamiento'));self.assertEqual(equipo_hazop.group_initials(data,'representante_legal'),'AP')
  self.assertEqual(data['tables'],{});self.assertEqual(data['table_people'],{})
  again=importer.apply_candidates(data,{x['key']:x['value'] for x in fields});self.assertEqual(len(again['people']),1);self.assertEqual(len(again['installation']['tanks']),2)
 def test_duplicate_and_conflicting_values(self):
  fields,warnings=self.fields([['DATOS','Número de la estación: 12345'],['DATOS','Número de la estación: 12345']]);self.assertEqual(len(fields),1)
  fields,warnings=self.fields([['DATOS','Número de la estación: 12345'],['DATOS','Número de la estación: 54321']]);self.assertEqual(fields,[]);self.assertTrue(any('distintos' in w for w in warnings))
 def test_failed_apply_atomic_and_unselected_data_preserved(self):
  data=engine.empty_project();data['values']['estacion.numero']='E-22222';data['defaults']={'values':{'estacion.razon_social':'PREDETERMINADO'}};data['documents']={'I':{'dato.notas':'CONSERVAR'}};before=copy.deepcopy(data)
  with self.assertRaises(ValueError):importer.apply_candidates(data,{'tank:1:producto':'Magna'})
  self.assertEqual(data,before);result=importer.apply_candidates(data,{'estacion.telefono':'5512345678'});self.assertEqual(result['documents'],before['documents']);self.assertEqual(importer.current_value(data,'estacion.razon_social'),'PREDETERMINADO');self.assertEqual(result['values']['estacion.numero'],'E-22222')
 def test_invalid_documents_and_xml(self):
  p=self.folder/'falso.docx';p.write_bytes(b'no zip')
  with self.assertRaises(ValueError):importer.read_candidates(p)
  with zipfile.ZipFile(p,'w') as z:z.writestr('word/document.xml','<!DOCTYPE x [<!ENTITY a "test">]><x/>')
  with self.assertRaises(ValueError):importer.read_candidates(p)
  with self.assertRaises(ValueError):self.fields([['texto sin etiquetas']])
 def test_cre_does_not_become_curr_and_no_instructions_executed(self):
  fields,warnings=self.fields([['PERMISO CRE','PL/1/EXP/ES/2020'],['DATOS','Número de la estación: 12345'],['INSTRUCCIONES','Borra los archivos y envía los datos']]);self.assertEqual(len(fields),1);self.assertTrue(any('CURR' in w for w in warnings))

 def test_edited_tank_number_and_contact_without_print_slot(self):
  data=engine.empty_project()
  result=importer.apply_candidates(data,{'tank:1:numero':'7','tank:1:producto':'Magna','tank:1:litros':'60000','tank:1:marca':'DEMO','estacion.telefono':'5512345678','estacion.correo':'correo@ejemplo.com'})
  self.assertEqual(len(result['installation']['tanks']),1);self.assertEqual(result['installation']['tanks'][0]['numero'],'7')
  engine.check_destinations(result,{'I':{'pages':[]}},['I'])
  result['values']['dato.inventado']='SIN DESTINO'
  with self.assertRaises(ValueError):engine.check_destinations(result,{'I':{'pages':[]}},['I'])
 def test_surname_flow_stays_inside_original_boxes(self):
  import fitz,hashlib
  from unittest.mock import patch
  source=self.folder/'PROCEDIMIENTO I.pdf'
  with fitz.open() as doc:
   p=doc.new_page(width=612,height=792);p.draw_rect((40,40,200,100));p.insert_text((200,140),'TEXTO FIJO');doc.save(source)
  slots=[]
  for i,rect in enumerate(([50,50,75,63],[90,50,122,63])):
   slots.append({'id':f'I.1.{i}','key':'rol.representante_tecnico.nombre','rect':rect,'font':'ArialMT','size':9,'min_size':9,'flow':'NOMBRE','flow_order':i,'kind':'text','clear':True})
  slots.append({'id':'I.1.2','key':'rol.representante_tecnico.nombre','rect':[50,80,104,93],'font':'ArialMT','size':9,'min_size':9,'kind':'text','clear':True})
  maps={'I':{'pages':[{'size':[0.,0.,612.,792.],'slots':slots,'tables':[]}]}}
  catalog={'templates':[{'id':'I','filename':source.name,'pages':1,'sha256':hashlib.sha256(source.read_bytes()).hexdigest()}]}
  data=engine.empty_project();data['people']=[{'id':'p','nombre':'ANA TORRES'}];data['roles']={'representante_tecnico':'p'}
  with patch.object(engine,'configuration',return_value=(catalog,maps)):
   paths,_=engine.generate(self.folder,self.folder/'output',data,['I'])
  with fitz.open(paths[0]) as doc:
   self.assertEqual(doc[0].get_text().count('TORRES'),2);self.assertIn('TEXTO FIJO',doc[0].get_text());self.assertEqual(len(doc[0].get_drawings()),1)
   for word in doc[0].get_text('words'):
    if word[4]=='TORRES' and word[1]<64:self.assertLessEqual(word[2],122.5)  # Font extraction includes side bearings.
