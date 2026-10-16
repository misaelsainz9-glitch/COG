"""Current footer and manual attendance rules, independent of private PDFs."""
import unittest
import tempfile
from pathlib import Path
import fitz
from PIL import Image
import sasisopa18 as engine

class SignaturePolicyTests(unittest.TestCase):
 def test_footer_signatures_use_name_gaps_and_preserve_cover_names(self):
  _,maps=engine.configuration();data=engine.empty_project();count=0
  for key,layout in maps.items():
   for pi,page in enumerate(layout['pages']):
    slots=engine.slots_for(layout,data,key,pi)
    for old in page['slots']:
     if pi and old['key'] in ('rol.elabora.nombre','rol.revisa.nombre','rol.autoriza.nombre') and old['rect'][1]>page['size'][3]*.65:
      count+=1
      self.assertFalse(any(s['key']==old['key'] for s in slots))
      image=next(s for s in slots if s['key']==old['key'].replace('.nombre','.firma'))
      self.assertEqual(image['rect'],old['rect']);self.assertEqual(image['kind'],'image')
  self.assertGreater(count,30)
  self.assertTrue(any(s['key']=='rol.elabora.nombre' for s in engine.slots_for(maps['I'],data,'I',0)))
 def test_stale_list_values_images_and_bindings_cannot_fill_attendance(self):
  with tempfile.TemporaryDirectory() as folder:
   image=Path(folder)/'signature.png';Image.new('RGB',(30,10),'red').save(image)
   doc=fitz.open();page=doc.new_page(width=200,height=200)
   page.draw_rect((20,40,180,90));page.insert_text((25,35),'NOMBRE / FIRMA');page.insert_text((25,60),'OLD JOB')
   page.insert_image((110,50,150,65),filename=str(image))
   slots=[{'id':'name','key':'tabla.X.0.nombre','rect':[22,42,98,88]}, {'id':'signature','key':'tabla.X.0.firma','kind':'image','rect':[102,42,178,88]}]
   layout={'pages':[{'size':list(page.rect),'slots':slots,'tables':[]}]}
   data=engine.empty_project();data['tables']={'tabla.X.0.nombre':'SHOULD NOT PRINT','tabla.X.0.firma':str(image)}
   before=page.get_drawings()
   engine.render_page(doc,0,layout,data,'X',engine.FontBook(doc))
   self.assertEqual(page.get_text().strip(),'NOMBRE / FIRMA');self.assertFalse(page.get_image_info())
   self.assertEqual(page.get_drawings(),before)
   data['bindings']=[{'doc':'X','page':0,'id':'custom','key':'estacion.numero','rect':[30,50,80,70]}]
   with self.assertRaisesRegex(ValueError,'vacías'):engine.slots_for(layout,data,'X',0)
