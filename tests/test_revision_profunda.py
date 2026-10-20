"""Regression cases found by auditing real boundaries and saved placements."""
import copy,os,tempfile,unittest
from pathlib import Path
import fitz
import instalaciones as inv
import equipo_hazop as team
import sasisopa18 as e
from test_instalaciones import fixture

class DeepModelTests(unittest.TestCase):
 def test_document_station_override_is_validated(self):
  data=e.empty_project();data['documents']={'II':{'estacion.numero':'INVALIDO'}}
  with self.assertRaisesRegex(ValueError,'E-00000'):e.validate_project(data)
 def test_project_dates_do_not_block_other_selected_procedures(self):
  _,maps=e.configuration();data=e.empty_project();data['values']={'documento.fecha_inicio_estudio':'02/11/2026','documento.fecha_fin_estudio':'05/11/2026'}
  for selected in (['I'],['V'],['VIII'],['II']):e.check_destinations(data,maps,selected)
  data['values']['dato.sin_ubicacion']='NO OCULTAR'
  with self.assertRaisesRegex(ValueError,'Ubicar campo'):e.check_destinations(data,maps,['V'])
 def test_zero_and_unknown_equipment_do_not_claim_dispatch(self):
  for zero in ('0','00','000'):
   data=fixture(('Magna',));data['installation']['equipment']['Magna']['dispensarios']=zero
   text=inv.value(data,'instalacion.despacho')
   self.assertIn('Sin despacho: Magna',text);self.assertNotIn('Despacho registrado',text)
  data['installation']['equipment']['Magna']={}
  self.assertIn('por confirmar',inv.value(data,'instalacion.despacho'))
 def test_dates_or_inventory_activate_pending_team_instead_of_old_companies(self):
  data=fixture(('Magna',));self.assertTrue(team.active(data))
  data=e.empty_project();data['values']['documento.fecha_inicio_estudio']='02/11/2026';self.assertTrue(team.active(data))
  self.assertEqual(e.slot_value(data,{'key':'rol.lider_hazop.empresa','team_member':True},'II'),'Pendiente')
 def test_moved_date_keeps_fallback_and_product_condition(self):
  _,maps=e.configuration();old=next(s for s in maps['II']['pages'][33]['slots'] if s.get('hazop_product')=='Diésel' and s['key']=='documento.fecha_sesion_hazop')
  data=fixture(('Magna',));data['values']['documento.fecha_inicio_estudio']='02/11/2026'
  data['bindings']=[{'id':'Bdate','doc':'II','page':33,'replace_id':old['id'],'key':old['key'],'rect':[650,248,740,266],'size':9}]
  slot=next(s for s in e.slots_for(maps['II'],data,'II',33) if s['id']=='Bdate')
  self.assertEqual(slot['hazop_product'],'Diésel');self.assertEqual(e.slot_value(data,slot,'II'),'02/11/2026')
  self.assertNotIn('hazop_product',data['bindings'][0])
 def test_long_cards_have_consistent_page_count(self):
  data=fixture();data['installation']['tanks'][1]['marca']='DOCUMENTACION '*7
  # One long field can wrap into the short card; make all details lengthy.
  for key,label in inv.TANK_FIELDS:
   if key not in ('numero','producto','litros'):data['installation']['tanks'][1][key]='DOCUMENTACION '*7
  self.assertEqual(inv.extra_pages(data,'II'),3);self.assertEqual(inv.extra_pages(data,'XIII'),3)
  self.assertEqual(inv.extra_pages(data,'I'),0)

@unittest.skipUnless(os.environ.get('SASISOPA18_BASE'),'Requires local private PDFs')
class DeepPDFTests(unittest.TestCase):
 def setUp(self):self.base=Path(os.environ['SASISOPA18_BASE']);_,self.maps=e.configuration()
 def test_sixty_tanks_fit_nodes_and_annex_without_losing_any_tank(self):
  data=fixture(('Magna',));data['installation']['tanks']=[{**data['installation']['tanks'][0],'numero':str(i+1)} for i in range(60)]
  with fitz.open(self.base/'PROCEDIMIENTO II.pdf') as doc:
   fonts=e.FontBook(doc)
   for pi in (29,32,33,34):e.render_page(doc,pi,self.maps['II'],data,'II',fonts)
   inv.append_inventory(doc,data,'E-48216',e._write,fonts)
   self.assertEqual(len(doc),77);text=' '.join(''.join(p.get_text() for p in list(doc)[57:]).split())
   for i in range(60):self.assertIn(f'COMPARTIMENTO {i+1} — Magna',text)
 def test_long_values_and_unbroken_words_fit_on_continuation_cards(self):
  data=fixture()
  for t in data['installation']['tanks']:
   t['numero']='ALMACEN-000'+t['numero']
   for key,label in inv.TANK_FIELDS:
    if key not in ('numero','producto','litros'):t[key]='W'*100
  e.validate_project(data)
  with fitz.open(self.base/'PROCEDIMIENTO II.pdf') as doc:
   fonts=e.FontBook(doc)
   for pi in (29,32,33,34):e.render_page(doc,pi,self.maps['II'],data,'II',fonts)
   inv.append_inventory(doc,data,'E-48216',e._write,fonts)
   self.assertEqual(len(doc),57+inv.extra_pages(data,'II'))
   for page in list(doc)[57:]:
    text=page.get_text();self.assertEqual(text.count('W'),1200)
    spans=[s for b in page.get_text('dict')['blocks'] for l in b.get('lines',[]) for s in l['spans']]
    self.assertTrue(all(s['bbox'][3]<760 for s in spans))
 def test_moving_a_paragraph_erases_first_and_last_original_lines(self):
  data=fixture();old=next(s for s in self.maps['II']['pages'][29]['slots'] if s['key']=='instalacion.almacenamiento')
  data['bindings']=[{'id':'Bmoved','doc':'II','page':29,'replace_id':old['id'],'key':old['key'],'rect':[85,155,531,335],'size':9,'min_size':8}]
  with fitz.open(self.base/'PROCEDIMIENTO II.pdf') as doc:
   e.render_page(doc,29,self.maps['II'],data,'II',e.FontBook(doc));text=doc[29].get_text()
   self.assertNotIn('Tipsa',text);self.assertNotIn('Cada tanque de almacenamiento cuenta',text)
   self.assertIn('MARCA',text)
 def test_moved_initials_of_absent_fuel_stay_absent(self):
  data=fixture(('Magna',));data['people']=[{'id':'U','nombre':'Ulises Hernández Cruz'}];data['roles']={'representante_legal':'U'}
  old=next(s for s in self.maps['II']['pages'][33]['slots'] if s['key']=='rol.representante_legal.iniciales' and s.get('hazop_product')=='Diésel')
  data['bindings']=[{'id':'Binitials','doc':'II','page':33,'replace_id':old['id'],'key':old['key'],'rect':[650,248,740,266],'size':9}]
  with fitz.open(self.base/'PROCEDIMIENTO II.pdf') as doc:
   e.render_page(doc,33,self.maps['II'],data,'II',e.FontBook(doc));self.assertNotIn('UHC',doc[33].get_textbox([519,241,760,297]))
 def test_team_calibration_is_repeatable(self):
  from scripts.calibrar_equipo_hazop import calibrar_equipo
  layout=copy.deepcopy(self.maps['II'])
  with fitz.open(self.base/'PROCEDIMIENTO II.pdf') as source:calibrar_equipo(layout,source);first=copy.deepcopy(layout);calibrar_equipo(layout,source)
  self.assertEqual(layout,first);self.assertEqual(layout,self.maps['II'])
 def test_all_seven_product_combinations_hide_inactive_hazop_and_groups(self):
  from itertools import combinations
  from test_equipo_hazop import team_data
  for count in (1,2,3):
   for fuels in combinations(inv.PRODUCTS,count):
    data=team_data(fuels)
    with fitz.open(self.base/'PROCEDIMIENTO II.pdf') as doc:
     fonts=e.FontBook(doc)
     for pi in range(32,54):
      e.render_page(doc,pi,self.maps['II'],data,'II',fonts)
      for region,product in inv.inactive_regions(data,'II',pi):
       text=doc[pi].get_textbox(region)
       self.assertIn('No aplica:',text,(fuels,pi+1));self.assertNotIn('UHC',text);self.assertNotIn('02/11/2026',text)
      for slot in self.maps['II']['pages'][pi]['slots']:
       if slot['key'].endswith('.iniciales') and slot.get('hazop_product') not in fuels and slot.get('hazop_product'):
        self.assertNotIn('UHC',doc[pi].get_textbox(slot['rect']))

 def test_team_names_also_fit_designation_and_acceptance_letters(self):
  from test_equipo_hazop import team_data
  data=team_data()
  with tempfile.TemporaryDirectory() as folder:
   paths,_=e.generate(self.base,Path(folder)/'letters',data,['V'])
   with fitz.open(paths[0]) as doc,fitz.open(self.base/'PROCEDIMIENTO V.pdf') as original:
    for pi in (15,16):
     text=' '.join(doc[pi].get_text().split())
     self.assertIn('Ana María López',text)
     if pi==15:self.assertIn('Ulises Hernández Cruz',text)
     drawings=lambda p:[{k:v for k,v in d.items() if k!='seqno'} for d in p.get_drawings()]
     self.assertEqual(drawings(doc[pi]),drawings(original[pi]))

 def test_long_imported_station_data_fits_special_register_headers(self):
  data=e.empty_project();data['values']={'estacion.numero':'E-99999','estacion.razon_social':'ESTACION LAS PALMAS AUTO SERVICIO SA DE CV','estacion.direccion':'CARRETERA FEDERAL 123 KM 108.5, COLONIA CENTRO, MUNICIPIO DE EJEMPLO, PUEBLA. CP. 72000'}
  _,maps=e.configuration()
  for doc_id,pi in [('XI',13),('XI',14),('XI',16),('XIII',15)]:
   with fitz.open(self.base/f'PROCEDIMIENTO {doc_id}.pdf') as doc,fitz.open(self.base/f'PROCEDIMIENTO {doc_id}.pdf') as original:
    e.render_page(doc,pi,maps[doc_id],data,doc_id,e.FontBook(doc))
    self.assertIn('72000',doc[pi].get_text());self.assertEqual(doc[pi].rect,original[pi].rect)
    drawings=lambda p:[{k:v for k,v in d.items() if k!='seqno'} for d in p.get_drawings()]
    self.assertEqual(drawings(doc[pi]),drawings(original[pi]))
