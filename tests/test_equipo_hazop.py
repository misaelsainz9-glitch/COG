import os,tempfile,unittest
from pathlib import Path
import fitz
import sasisopa18 as e
import equipo_hazop as h
from test_instalaciones import fixture

class TeamModelTests(unittest.TestCase):
 def test_initials_follow_current_name_even_with_old_manual_value(self):
  data=e.empty_project();data['people']=[{'id':'A','nombre':'Ulises Hernández Cruz','iniciales':'VIEJAS'}];data['roles']={'lider_hazop':'A'}
  self.assertEqual(e.resolve(data,'rol.lider_hazop.iniciales','II'),'UHC')
  data['people'][0]['nombre']='Ana María López Pérez'
  self.assertEqual(e.resolve(data,'rol.lider_hazop.iniciales','II'),'AMLP')
  self.assertEqual(h.initials('  ulises   hernández  cruz  '),'UHC')
 def test_dates_independent_revision_range_and_roundtrip(self):
  data=e.empty_project();data['values']={'documento.fecha_inicio_estudio':'02/11/2026','documento.fecha_fin_estudio':'05/11/2026','documento.fecha_revision':'10/10/2026'}
  e.validate_project(data)
  with tempfile.TemporaryDirectory() as folder:
   file=Path(folder)/'project.json';e.save_project(file,data);self.assertEqual(e.load_project(file),data)
  data['values']['documento.fecha_fin_estudio']='01/11/2026'
  with self.assertRaisesRegex(ValueError,'anterior'):e.validate_project(data)
 def test_saved_custom_team_positions_keep_their_original_target(self):
  data=e.empty_project();data['bindings']=[{'id':'B1','doc':'II','page':32,'key':'rol.representante_legal.nombre','replace_id':'II.33.21','rect':[25,305,380,325],'size':9}]
  e.validate_project(data)
  self.assertEqual(data['bindings'][0]['replace_id'],'II.33.equipo.representante_legal.nombre')
 def test_team_slots_and_group_are_unique_on_team_page(self):
  _,maps=e.configuration();slots=maps['II']['pages'][32]['slots'];ids=[s['id'] for s in slots]
  self.assertEqual(len(ids),len(set(ids)))
  for role in h.ROLES:
   for attr in ('nombre','puesto','empresa'):self.assertEqual(sum(s['key']==f'rol.{role}.{attr}' for s in slots),1)

def team_data(products=('Magna','Diésel','Premium')):
 data=fixture(products);names=['Ulises Hernández Cruz','Ana María López','Carlos Díaz Ruiz','Diana Vega Soto','Elena Pérez Mora','Felipe Torres León']
 data['people']=[{'id':str(i),'nombre':n,'puesto':'CARGO '+str(i),'empresa':'EMPRESA DEMO '+str(i),'iniciales':'MANUAL'} for i,n in enumerate(names)]
 data['roles']={role:str(i) for i,role in enumerate(h.ROLES)}
 data['values']={'documento.fecha_inicio_estudio':'02/11/2026','documento.fecha_fin_estudio':'05/11/2026','documento.fecha_revision':'10/10/2026'}
 return data

@unittest.skipUnless(os.environ.get('SASISOPA18_BASE'),'Requires local private PDFs')
class TeamPDFTests(unittest.TestCase):
 def test_all_team_cells_and_dates_and_absent_fuel_groups(self):
  _,maps=e.configuration();data=team_data(('Magna',));base=Path(os.environ['SASISOPA18_BASE'])
  with fitz.open(base/'PROCEDIMIENTO II.pdf') as doc:
   fonts=e.FontBook(doc);page=doc[32];original=[{k:v for k,v in d.items() if k!='seqno'} for d in page.get_drawings()]
   for pi in (32,33,34,41,48,53):e.render_page(doc,pi,maps['II'],data,'II',fonts)
   self.assertEqual([{k:v for k,v in d.items() if k!='seqno'} for d in doc[32].get_drawings()],original)
   for slot in maps['II']['pages'][32]['slots']:
    if slot.get('team_member'):
     actual=' '.join(doc[32].get_textbox(slot['rect']).split());expected=e.resolve(data,slot['key'],'II')
     self.assertEqual(actual,expected,slot['key'])
   text=doc[32].get_text();self.assertIn('02/11/2026',text);self.assertIn('05/11/2026',text);self.assertNotIn('06/08/2026',text)
   for pi in (32,33):
    for slot in maps['II']['pages'][pi]['slots']:
     if slot['key'].endswith('.iniciales'):
      value=doc[pi].get_textbox(slot['rect']).strip()
      if slot.get('hazop_product') in ('Premium','Diésel'):self.assertNotIn('UHC',value);self.assertNotIn('MANUAL',value)
      elif slot.get('hazop_product')=='Magna':self.assertIn(e.resolve(data,slot['key'],'II'),value)
   self.assertIn('UHC',doc[34].get_text());self.assertNotIn('UHC',doc[48].get_text())
 def test_session_date_override_and_unassigned_companies_are_pending(self):
  _,maps=e.configuration();data=team_data();data['documents']={'II':{'documento.fecha_sesion_hazop':'04/11/2026'}}
  data['people'][-1].pop('empresa');base=Path(os.environ['SASISOPA18_BASE'])
  with fitz.open(base/'PROCEDIMIENTO II.pdf') as doc:
   fonts=e.FontBook(doc)
   for pi in (32,33,34):e.render_page(doc,pi,maps['II'],data,'II',fonts)
   self.assertIn('04/11/2026',doc[33].get_text());self.assertNotIn('06/08/2026',doc[33].get_text())
   slot=next(s for s in maps['II']['pages'][32]['slots'] if s['key']=='rol.lider_hazop.empresa')
   self.assertIn('Pendiente',doc[32].get_textbox(slot['rect']))
 def test_full_generation_replaces_study_dates_everywhere(self):
  _,maps=e.configuration();data=team_data()
  with tempfile.TemporaryDirectory() as folder:
   paths,_=e.generate(os.environ['SASISOPA18_BASE'],Path(folder)/'batch',data,['II'])
   with fitz.open(paths[0]) as doc:
    text=''.join(p.get_text() for p in doc)
    self.assertNotIn('06/08/2026',text);self.assertNotIn('13/08/2026',text);self.assertNotIn('MANUAL',text)
    self.assertIn('02/11/2026',text);self.assertIn('05/11/2026',text);self.assertIn('UHC',text)
