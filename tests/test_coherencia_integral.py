"""Cross-document references must agree with the procedure they identify."""
import copy,os,unittest
from pathlib import Path
import fitz
import sasisopa18 as e

class CoherenceModelTests(unittest.TestCase):
 def test_master_list_dates_and_revisions_follow_referenced_document(self):
  _,maps=e.configuration();data=e.empty_project()
  data['values']={'documento.revision':'7','documento.fecha_revision':'19/10/2026'}
  data['documents']={'II':{'documento.revision':'9','documento.fecha_revision':'23/10/2026'},'VIII':{'documento.revision':'4','documento.fecha_revision':'21/10/2026'}}
  slots=[s for pi in (10,11) for s in maps['VIII']['pages'][pi]['slots'] if '.maestro.' in s['id']]
  self.assertEqual(len(slots),38)
  for s in slots:
   expected=(data['documents'].get(s.get('reference_doc'),{}).get(s['key'],data['values'][s['key']]))
   self.assertEqual(e.slot_value(data,s,'VIII'),expected,s['id'])
 def test_moved_reference_date_keeps_its_document(self):
  _,maps=e.configuration();data=e.empty_project()
  old=next(s for s in maps['VIII']['pages'][10]['slots'] if s.get('reference_doc')=='II' and s['key']=='documento.fecha_revision')
  data['values']['documento.fecha_revision']='19/10/2026';data['documents']={'II':{'documento.fecha_revision':'23/10/2026'}}
  data['bindings']=[{'id':'moved','doc':'VIII','page':10,'key':old['key'],'replace_id':old['id'],'rect':[420,390,490,405],'size':9}]
  moved=next(s for s in e.slots_for(maps['VIII'],data,'VIII',10) if s['id']=='moved')
  self.assertEqual(e.slot_value(data,moved,'VIII'),'23/10/2026')
 def test_signature_dates_are_independent_and_optional(self):
  _,maps=e.configuration();data=e.empty_project();data['values']['documento.fecha_revision']='19/10/2026'
  slot=next(s for s in maps['I']['pages'][2]['slots'] if s['key']=='documento.fecha_firmas')
  self.assertEqual(e.slot_value(data,slot,'I'),'')
  data['documents']={'I':{'documento.fecha_firmas':'24/10/2026'}}
  self.assertEqual(e.slot_value(data,slot,'I'),'24/10/2026');e.validate_project(data)

@unittest.skipUnless(os.environ.get('SASISOPA18_BASE'),'Requires local private PDFs')
class CoherencePDFTests(unittest.TestCase):
 def test_two_digit_revisions_fit_all_cover_labels_at_original_font_size(self):
  _,maps=e.configuration();data=e.empty_project();data['values']['documento.revision']='12'
  for id,layout in maps.items():
   with fitz.open(Path(os.environ['SASISOPA18_BASE'])/f'PROCEDIMIENTO {id}.pdf') as doc:
    fonts=e.FontBook(doc)
    for pi,spec in enumerate(layout['pages']):
     labels=[s for s in spec['slots'] if s.get('transform')=='revision_label']
     if not labels:continue
     notes=e.render_page(doc,pi,layout,data,id,fonts)
     self.assertIn('12',doc[pi].get_text(),id)
     for s in labels:
      note=next(n for n in notes if n['field']=='documento.revision')
      self.assertEqual(note['size'],s['size'])
 def test_two_digit_revision_preserves_adjacent_body_text(self):
  _,maps=e.configuration();data=e.empty_project();data['values']['documento.revision']='12'
  with fitz.open(Path(os.environ['SASISOPA18_BASE'])/'PROCEDIMIENTO I.pdf') as doc:
   e.render_page(doc,6,maps['I'],data,'I',e.FontBook(doc))
   self.assertIn('Difusión y comunicación de la política.',doc[6].get_text())
   for s in maps['I']['pages'][6]['slots']:
    if s['key']=='documento.revision' and not s.get('code_owner'):
     self.assertIn('12',doc[6].get_textbox(fitz.Rect(s['rect'])+(-1,-1,1,1)))
 def test_compact_equipment_header_reports_overflow_instead_of_clipping(self):
  _,maps=e.configuration();data=e.empty_project()
  data['values']['estacion.direccion']='CALLE PRUEBA 851, COL. NUEVA, MERIDA, YUCATAN, C.P. 97000 '*8
  with fitz.open(Path(os.environ['SASISOPA18_BASE'])/'PROCEDIMIENTO XI.pdf') as doc:
   before=doc[13].get_text()
   with self.assertRaisesRegex(ValueError,'no cabe'):e.render_page(doc,13,maps['XI'],data,'XI',e.FontBook(doc))
   self.assertEqual(doc[13].get_text(),before)
 def test_real_master_list_columns_agree_with_code_revisions(self):
  _,maps=e.configuration();data=e.empty_project()
  data['values']={'estacion.numero':'E-86420','documento.revision':'7','documento.fecha_revision':'19/10/2026'}
  data['documents']={'II':{'documento.revision':'9','documento.fecha_revision':'23/10/2026'}}
  with fitz.open(Path(os.environ['SASISOPA18_BASE'])/'PROCEDIMIENTO VIII.pdf') as doc:
   fonts=e.FontBook(doc)
   for pi in (10,11):
    drawings=lambda p:[{k:v for k,v in d.items() if k!='seqno'} for d in p.get_drawings()]
    before=drawings(doc[pi]);e.render_page(doc,pi,maps['VIII'],data,'VIII',fonts)
    self.assertEqual(drawings(doc[pi]),before)
    self.assertNotIn('06/08/2026',doc[pi].get_text())
    for s in maps['VIII']['pages'][pi]['slots']:
     if '.maestro.' in s['id']:self.assertEqual(doc[pi].get_textbox(s['rect']).strip(),e.slot_value(data,s,'VIII'))
 def test_signature_dates_replace_old_values_without_erasing_labels(self):
  _,maps=e.configuration();data=e.empty_project();data['documents']={'I':{'documento.fecha_firmas':'24/10/2026'}}
  with fitz.open(Path(os.environ['SASISOPA18_BASE'])/'PROCEDIMIENTO I.pdf') as doc:
   e.render_page(doc,2,maps['I'],data,'I',e.FontBook(doc));text=doc[2].get_text()
   self.assertEqual(text.count('24/10/2026'),3);self.assertNotIn('01-10-2024',text);self.assertEqual(text.count('Fecha:'),3)
 def test_new_calibration_is_repeatable(self):
  from scripts.calibrar_coherencia import calibrate
  _,maps=e.configuration();expected=copy.deepcopy(maps)
  calibrate(maps,Path(os.environ['SASISOPA18_BASE']));self.assertEqual(maps,expected)
