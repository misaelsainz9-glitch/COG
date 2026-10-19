"""Regression: redacting a blank attendance list must not blacken its footer."""
import io,os,unittest
from pathlib import Path
import fitz
from PIL import Image
from limpieza_transparencias import normalizar_marcadores_vacios
import sasisopa18 as e


class TransparentPlaceholderTests(unittest.TestCase):
 def test_empty_image_becomes_empty_form_without_changing_pixels_or_text(self):
  with fitz.open() as doc:
   page=doc.new_page();page.insert_text((40,80),'ELABORO - EQUIPO DE TRABAJO')
   page.draw_rect((35,55,330,100))
   image=Image.new('RGBA',(1,1),(0,0,0,0));buffer=io.BytesIO();image.save(buffer,format='PNG')
   page.insert_image((50,40,180,130),stream=buffer.getvalue())
   before=page.get_pixmap().samples;text=page.get_text();lines=page.get_drawings()
   self.assertEqual(normalizar_marcadores_vacios(doc,page),1)
   self.assertEqual(page.get_pixmap().samples,before)
   self.assertEqual(page.get_text(),text);self.assertEqual(page.get_drawings(),lines)
   self.assertEqual(normalizar_marcadores_vacios(doc,page),0)
   page.add_redact_annot((45,35,80,55),fill=None);page.apply_redactions(images=2,graphics=0)
   with fitz.open(stream=doc.tobytes(garbage=4,deflate=True),filetype='pdf') as saved:
    self.assertEqual(saved[0].get_pixmap().samples,before)
 def test_opaque_pixels_and_larger_images_are_preserved(self):
  with fitz.open() as doc:
   page=doc.new_page()
   for i,(size,color) in enumerate([((1,1),(0,0,255,255)),((2,2),(0,0,0,0))]):
    image=Image.new('RGBA',size,color);buffer=io.BytesIO();image.save(buffer,format='PNG')
    page.insert_image((40+i*100,40,100+i*100,100),stream=buffer.getvalue())
   before=page.get_pixmap().samples;images=page.get_images(full=True)
   self.assertEqual(normalizar_marcadores_vacios(doc,page),0)
   self.assertEqual(page.get_images(full=True),images)
   self.assertEqual(page.get_pixmap().samples,before)


@unittest.skipUnless(os.environ.get('SASISOPA18_BASE'),'Requires local private PDFs')
class PrivateFooterRegressionTests(unittest.TestCase):
 def test_policy_last_page_footer_stays_identical_after_attendance_redaction(self):
  _,maps=e.configuration();data=e.empty_project()
  with fitz.open(Path(os.environ['SASISOPA18_BASE'])/'PROCEDIMIENTO I.pdf') as doc:
   region=fitz.Rect(40,675,580,755);before=doc[13].get_pixmap(clip=region).samples
   e.render_page(doc,13,maps['I'],data,'I',e.FontBook(doc))
   self.assertEqual(doc[13].get_pixmap(clip=region).samples,before)
   with fitz.open(stream=doc.tobytes(garbage=4,deflate=True),filetype='pdf') as saved:
    self.assertEqual(saved[13].get_pixmap(clip=region).samples,before)
