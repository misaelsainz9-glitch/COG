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
      self.assertEqual(image['rect'],old['signature_rect']);self.assertEqual(image['kind'],'image')
      self.assertFalse(image['clear']);self.assertTrue(fitz.Rect(page['size']).contains(fitz.Rect(image['rect'])))
  self.assertGreater(count,30)
  self.assertTrue(any(s['key']=='rol.elabora.nombre' for s in engine.slots_for(maps['I'],data,'I',0)))
 def test_uploaded_signature_is_blue_cropped_and_transparent(self):
  from firma_canvas import blue_signature,INK_BLUE
  from PIL import ImageDraw
  with tempfile.TemporaryDirectory() as folder:
   path=Path(folder)/'scan.png';image=Image.new('RGB',(400,200),'white')
   ImageDraw.Draw(image).line([(100,70),(200,130),(300,70)],fill='black',width=4);image.save(path)
   original=path.read_bytes();ink=blue_signature(path)
   self.assertLess(ink.width,220);self.assertLess(ink.height,80)
   self.assertEqual(ink.getpixel((0,ink.height-1))[3],0)
   self.assertTrue(all(ink.getpixel((x,y))[:3]==INK_BLUE for y in range(ink.height) for x in range(ink.width) if ink.getpixel((x,y))[3]))
   self.assertEqual(path.read_bytes(),original)
   Image.new('RGB',(20,20),'white').save(path)
   with self.assertRaisesRegex(ValueError,'vacía'):blue_signature(path)
 def test_large_overlay_preserves_labels_borders_and_is_blue(self):
  from firma_canvas import signature_png
  with tempfile.TemporaryDirectory() as folder:
   path=Path(folder)/'signature.png';signature_png([[(20,30),(150,100),(300,35)]]).save(path)
   doc=fitz.open();page=doc.new_page(width=220,height=120)
   page.draw_rect((10,10,210,110));page.insert_text((45,65),'EQUIPO DE TRABAJO')
   text=page.get_text();drawings=page.get_drawings()
   slot={'key':'rol.elabora.firma','rect':[12,12,208,108]}
   engine._image(page,slot,str(path))
   self.assertEqual(page.get_text(),text);self.assertEqual(page.get_drawings(),drawings)
   image=page.get_image_info()[0];bounds=fitz.Rect(image['bbox'])
   self.assertGreater(bounds.width,190);self.assertGreater(bounds.height,40)
   self.assertTrue(fitz.Rect(slot['rect']).contains(bounds))
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
