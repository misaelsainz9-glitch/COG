"""Whole header identifiers must never be drawn as unrelated fragments."""
import os,unittest
from pathlib import Path
import fitz
import sasisopa18 as e

class CodeValuesTests(unittest.TestCase):
 def setUp(self):self.data=e.empty_project();_,self.maps=e.configuration()
 def test_station_only_revision_only_and_referenced_override(self):
  slot=next(s for s in self.maps['II']['pages'][32]['slots'] if s.get('code_suffix'))
  self.assertEqual(e.slot_value(self.data,slot,'II'),'')
  self.data['values']={'estacion.numero':'E-00007'}
  self.assertEqual(e.slot_value(self.data,slot,'II'),'E-00007.02.RE.04.R0')
  self.data['values']['documento.revision']='12'
  self.assertEqual(e.slot_value(self.data,slot,'II'),'E-00007.02.RE.04.R12')
  self.data['documents']={'II':{'documento.revision':'3'}}
  self.assertEqual(e.slot_value(self.data,slot,'II'),'E-00007.02.RE.04.R3')
  self.data['values'].pop('estacion.numero')
  self.assertEqual(e.slot_value(self.data,slot,'II'),'E-.02.RE.04.R3')
 def test_moved_station_binding_keeps_complete_identifier(self):
  spec=self.maps['II']['pages'][32]
  old=next(s for s in spec['slots'] if s.get('code_suffix'))
  self.data['values']={'estacion.numero':'E-12345','documento.revision':'2'}
  self.data['bindings']=[{'id':'B-code','doc':'II','page':32,'key':'estacion.numero','replace_id':old['id'],'rect':[450,100,620,120],'size':9,'min_size':9,'transform':'digits'}]
  slots=e.slots_for(self.maps['II'],self.data,'II',32)
  code=next(s for s in slots if s['id']=='B-code')
  self.assertEqual(e.slot_value(self.data,code,'II'),'E-12345.02.RE.04.R2')
  self.assertNotIn('transform',code)
  for s in slots:
   if s['id'] in old['code_members']:self.assertEqual(s['code_owner'],'B-code')
 def test_all_maps_have_single_line_codes_and_owned_fragments(self):
  total=0
  for layout in self.maps.values():
   for page in layout['pages']:
    by_id={s['id']:s for s in page['slots']}
    for s in page['slots']:
     if s.get('code_suffix'):
      total+=1;self.assertTrue(s['single_line']);self.assertNotIn('transform',s)
     if s.get('code_owner'):self.assertIn('code_suffix',by_id[s['code_owner']])
  self.assertGreater(total,500)

class ActualCodeTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  base=os.environ.get('SASISOPA18_BASE')
  if not base:raise unittest.SkipTest('Private base is local only.')
  cls.base=Path(base);_,cls.maps=e.configuration()
 def test_all_complete_codes_share_one_baseline_and_keep_borders(self):
  data=e.empty_project();data['values']={'estacion.numero':'E-48216','documento.revision':'2'}
  count=0
  for id,layout in self.maps.items():
   with fitz.open(self.base/f'PROCEDIMIENTO {id}.pdf') as doc:
    fonts=e.FontBook(doc)
    for pi,spec in enumerate(layout['pages']):
     codes=[s for s in spec['slots'] if s.get('code_suffix')]
     if not codes:continue
     page=doc[pi];draw=lambda:[{k:v for k,v in d.items() if k!='seqno'} for d in page.get_drawings()]
     borders=draw();e.render_page(doc,pi,layout,data,id,fonts)
     self.assertEqual(draw(),borders,(id,pi+1,'borders'))
     for slot in codes:
      rect=fitz.Rect(slot['rect'])+(-1,-1,1,1)
      chars=[c for b in page.get_text('rawdict',clip=rect)['blocks'] for l in b.get('lines',[]) for sp in l['spans'] for c in sp['chars'] if not c['c'].isspace()]
      actual=''.join(c['c'] for c in chars).replace('‐','-').replace('\xad','-')
      expected=e.slot_value(data,slot,id)
      self.assertEqual(actual.count(expected),1,(id,pi+1,actual,expected))
      start=actual.index(expected);chars=chars[start:start+len(expected)]
      self.assertLess(max(c['origin'][1] for c in chars)-min(c['origin'][1] for c in chars),.02,(id,pi+1,'baseline'))
      count+=1
  self.assertGreater(count,500)
 def test_raster_code_mask_does_not_touch_label_or_surroundings(self):
  from scripts.calibrar_codigos import RASTER
  from PIL import Image,ImageChops
  data=e.empty_project();data['values']={'estacion.numero':'E-99999','documento.revision':'2'}
  for id,(pi,rect,_,_) in RASTER.items():
   with fitz.open(self.base/f'PROCEDIMIENTO {id}.pdf') as doc:
    page=doc[pi];clip=fitz.Rect(rect)+(-4,-12,4,6)
    def pixels():
     p=page.get_pixmap(matrix=fitz.Matrix(4,4),clip=clip,alpha=False)
     return Image.frombytes('RGB',(p.width,p.height),p.samples),p
    before,pix=pixels();e.render_page(doc,pi,self.maps[id],data,id,e.FontBook(doc));after,_=pixels()
    changed=ImageChops.difference(before,after).getbbox()
    self.assertIsNotNone(changed)
    x0,y0,x1,y1=changed
    # Includes an untouched source CÓDIGO label above the text mask.
    self.assertGreaterEqual(y0+pix.y,rect[1]*4-1)
    self.assertLessEqual(y1+pix.y,rect[3]*4+1)
    self.assertGreaterEqual(x0+pix.x,rect[0]*4-1)
    self.assertLessEqual(x1+pix.x,rect[2]*4+1)
