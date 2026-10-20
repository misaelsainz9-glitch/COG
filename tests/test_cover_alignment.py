"""Cover centering also applies to bindings saved before the correction."""
import copy,hashlib,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import fitz
import sasisopa18 as engine

class CoverAlignmentTests(unittest.TestCase):
 def test_all_eighteen_covers_and_legacy_bindings(self):
  _,maps=engine.configuration();count=0
  for doc_id,layout in maps.items():
   data=engine.empty_project()
   for slot in layout['pages'][0]['slots']:
    if slot['key']=='estacion.direccion':
     count+=1;self.assertEqual(slot['align'],1)
     data['bindings'].append({**slot,'id':'legacy.'+slot['id'],'doc':doc_id,'page':0,'replace_id':slot['id'],'align':2})
   before=copy.deepcopy(data)
   for slot in engine.slots_for(layout,data,doc_id,0):
    if slot['key']=='estacion.direccion':self.assertEqual(slot['align'],1)
   self.assertEqual(data,before)
   if len(layout['pages'])>1:
    base={s['id']:s for s in layout['pages'][1]['slots']}
    for slot in engine.slots_for(layout,data,doc_id,1):
     if slot['key']=='estacion.direccion':self.assertEqual(slot['align'],base[slot['id']]['align'])
  self.assertGreaterEqual(count,18)
 def test_generated_lines_centered_header_stays_right_and_original_unchanged(self):
  with tempfile.TemporaryDirectory() as tmp:
   folder=Path(tmp);source=folder/'PROCEDIMIENTO I.pdf'
   with fitz.open() as doc:
    for _ in range(2):
     page=doc.new_page(width=612,height=792);page.draw_rect((40,40,572,160));page.insert_text((50,200),'TEXTO FIJO')
    doc.save(source)
   original=source.read_bytes();slot={'id':'I.1.direccion','key':'estacion.direccion','rect':[50,60,550,110],'kind':'text','font':'ArialMT','size':12,'min_size':12,'align':2}
   header={**slot,'id':'I.2.direccion'}
   maps={'I':{'pages':[{'size':[0.,0.,612.,792.],'slots':[slot],'tables':[]},{'size':[0.,0.,612.,792.],'slots':[header],'tables':[]}]}}
   catalog={'templates':[{'id':'I','filename':source.name,'pages':2,'sha256':hashlib.sha256(original).hexdigest()}]}
   data=engine.empty_project();data['values']['estacion.direccion']='AVENIDA CENTRAL 123\nCP. 72000';data['bindings']=[{**slot,'id':'legacy','doc':'I','page':0,'replace_id':slot['id']}]
   with patch.object(engine,'configuration',return_value=(catalog,maps)):paths,_=engine.generate(folder,folder/'out',data,['I'])
   with fitz.open(paths[0]) as doc:
    for i,page in enumerate(doc):
     spans=[s for b in page.get_text('dict')['blocks'] for line in b.get('lines',[]) for s in line['spans'] if s['bbox'][1]<150]
     self.assertEqual(len(spans),2)
     for span in spans:
      left,_,right,_=span['bbox']
      self.assertAlmostEqual((left+right)/2,300,delta=1.5) if i==0 else self.assertAlmostEqual(right,550,delta=1.5)
     self.assertIn('TEXTO FIJO',page.get_text());self.assertEqual(len(page.get_drawings()),1)
   self.assertEqual(source.read_bytes(),original)
