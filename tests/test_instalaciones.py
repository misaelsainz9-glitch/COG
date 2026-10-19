import copy,os,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import fitz
import instalaciones as inv
import sasisopa18 as e

def fixture(products=('Magna','Diésel','Premium')):
 data=e.empty_project()
 data['installation']={'enabled':True,'tanks':[{'numero':str(i+1),'producto':p,'litros':str(75000-i*20000),'marca':'MARCA DEMO','medidas':'2.5 x 8 m','confinamiento':'Subterráneo','pared':'Doble pared','cupula':'No tiene','presion_vapor':'0.9 atm','temperatura_almacen':'Ambiente','presion_operacion':'2.1 kg/cm2','temperatura_operacion':'25 °C','flujo':'40 L/min','plano':'PLANO PRUEBA'} for i,p in enumerate(products)],'equipment':{p:{'dispensarios':'2','mangueras':'4'} for p in products}}
 return data

class InstallationTests(unittest.TestCase):
 def test_validation_duplicates_missing_and_impossible_counts(self):
  data=fixture();e.validate_project(data)
  for change in ('duplicate','zero','negative','unknown','missing_product','equipment'):
   with self.subTest(change=change):
    d=fixture();t=d['installation']['tanks'][1]
    if change=='duplicate':t['numero']='1'
    if change=='zero':t['litros']='0'
    if change=='negative':t['litros']='-40000'
    if change=='unknown':t['producto']='Gas inventado'
    if change=='missing_product':t['producto']=''
    if change=='equipment':d=fixture(('Magna',));d['installation']['equipment']['Diésel']={'dispensarios':'2'}
    with self.assertRaises(ValueError):e.validate_project(d)
 def test_reordered_tanks_are_found_by_product_and_repeated_products(self):
  data=fixture()
  self.assertIn('3',inv.value(data,'instalacion.producto.1.incluye'))
  self.assertIn('2',inv.value(data,'instalacion.producto.2.incluye'))
  data['installation']['tanks'].append({**data['installation']['tanks'][0],'numero':'4','presion_operacion':'3 atm'})
  self.assertIn('1, 4',inv.value(data,'instalacion.producto.0.incluye'))
  self.assertEqual(inv.value(data,'instalacion.producto.0.presion_operacion'),'Ver ficha de instalaciones')
 def test_missing_values_do_not_reuse_example_conditions(self):
  data=fixture(('Magna',));data['installation']['tanks'][0]['presion_operacion']=''
  self.assertEqual(inv.value(data,'instalacion.producto.0.presion_operacion'),'Pendiente')
  self.assertEqual(inv.value(data,'instalacion.producto.1.nombre'),'—')
  self.assertEqual(inv.value(data,'instalacion.tanque.1.producto'),'No aplica')
 def test_legacy_and_disabled_profiles_do_not_change_documents(self):
  self.assertEqual(inv.value(e.empty_project(),'instalacion.lista'),'')
  data=fixture();data['installation']['enabled']=False
  self.assertEqual(inv.value(data,'instalacion.lista'),'')
  self.assertEqual(inv.inactive_regions(data,'II',48),[])
 def test_save_and_load_inventory_and_legacy(self):
  with tempfile.TemporaryDirectory() as folder:
   path=Path(folder)/'inventory.json';data=fixture();e.save_project(path,data)
   self.assertEqual(e.load_project(path),data)
   data.pop('installation');e.save_project(path,data);self.assertEqual(e.load_project(path),data)

@unittest.skipUnless(os.environ.get('SASISOPA18_BASE'),'Private base is local only')
class InstallationPDFTests(unittest.TestCase):
 def setUp(self):self.base=Path(os.environ['SASISOPA18_BASE']);_,self.maps=e.configuration()
 def test_inventory_changes_both_tables_and_narratives_without_moving_borders(self):
  for id,table,narrative in [('II',29,29),('XIII',35,34)]:
   with fitz.open(self.base/f'PROCEDIMIENTO {id}.pdf') as doc:
    fonts=e.FontBook(doc);data=fixture();page=doc[table]
    original=[{k:v for k,v in d.items() if k!='seqno'} for d in page.get_drawings()]
    e.render_page(doc,table,self.maps[id],data,id,fonts)
    self.assertEqual([{k:v for k,v in d.items() if k!='seqno'} for d in page.get_drawings()],original)
    texts=[]
    for i in range(3):
     slot=next(s for s in self.maps[id]['pages'][table]['slots'] if s['key']==f'instalacion.tanque.{i}.producto')
     texts.append(page.get_textbox(slot['rect']).strip())
    self.assertEqual(texts,['Magna','Diésel','Premium'])
    self.assertIn('75,000',page.get_text());self.assertNotIn('60,000',page.get_text())
    if narrative!=table:e.render_page(doc,narrative,self.maps[id],data,id,fonts)
    text=doc[narrative].get_text().replace('\xa0',' ');self.assertNotIn('Tipsa',text);self.assertIn('MARCA DEMO',text)
 def test_absent_fuels_clear_hazop_body_but_keep_headers_and_tables(self):
  data=fixture(('Magna',))
  with fitz.open(self.base/'PROCEDIMIENTO II.pdf') as doc:
   fonts=e.FontBook(doc)
   for pi in range(41,54):
    page=doc[pi];draw=lambda:[{k:v for k,v in d.items() if k!='seqno'} for d in page.get_drawings()]
    labels={label:page.get_text().count(label) for label in ('ELABORÓ:','REVISADO POR:','APROBADO POR:')}
    before=draw();e.render_page(doc,pi,self.maps['II'],data,'II',fonts);self.assertEqual(draw(),before)
    for region,p in inv.inactive_regions(data,'II',pi):
     text=page.get_textbox(region)
     self.assertIn('No aplica',text);self.assertNotIn('2.45',text);self.assertNotIn('Desviación:',text)
    self.assertIn('CÓDIGO',page.get_text())
    for label,count in labels.items():self.assertEqual(page.get_text().count(label),count)
 def test_active_operating_conditions_and_tank_numbers_propagate(self):
  data=fixture()
  with fitz.open(self.base/'PROCEDIMIENTO II.pdf') as doc:
   fonts=e.FontBook(doc)
   for pi in (32,33,34,41,42,48,53):
    e.render_page(doc,pi,self.maps['II'],data,'II',fonts);text=doc[pi].get_text().replace('\xa0',' ')
    self.assertNotIn('2.45',text,(pi+1,text));self.assertNotIn('30°C',text)
    if pi!=53:self.assertIn('2.1 kg/cm2',text)
   for idx,tq in [(1,'3'),(2,'2')]:
    slot=next(s for s in self.maps['II']['pages'][33]['slots'] if s['key']==f'instalacion.producto.{idx}.incluye')
    self.assertIn(tq,doc[33].get_textbox(slot['rect']))
 def test_generation_for_three_fuel_combinations_and_overflow_annex(self):
  for products in [('Magna',),('Premium','Diésel'),('Magna','Diésel','Premium','Magna')]:
   data=fixture(products);data['values']={'estacion.numero':'E-48216'}
   with tempfile.TemporaryDirectory() as folder:
    paths,warnings=e.generate(self.base,Path(folder)/'batch',data,['II','III','XIII'],merge=True)
    self.assertEqual(len(paths),4);self.assertTrue(any('HAZOP' in w for w in warnings))
    annex=(len(products)+2)//3
    for id,count in [('II',57),('XIII',70)]:
     with fitz.open(Path(folder)/'batch'/f'PROCEDIMIENTO {id}.pdf') as doc:
      self.assertEqual(len(doc),count+annex)
      text=''.join(p.get_text() for p in list(doc)[count:])
      for t in data['installation']['tanks']:self.assertIn('COMPARTIMENTO '+t['numero'],text)
      self.assertIn('MARCA DEMO',text)
    with fitz.open(paths[-1]) as merged:self.assertEqual(len(merged),57+26+70+annex*2)
