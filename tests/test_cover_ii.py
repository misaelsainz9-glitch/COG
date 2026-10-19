"""The first two user images: procedure II cover, without changing other pages."""
import copy,os,tempfile,unittest
from pathlib import Path
from types import SimpleNamespace
import fitz
import sasisopa18 as engine
from ajustes_portada_ii import ajustar_portada_ii
from firma_canvas import signature_png

class CoverRulesTests(unittest.TestCase):
 def test_equal_signature_spaces_and_centered_address(self):
  _,maps=engine.configuration();layout=copy.deepcopy(maps['II']);other=copy.deepcopy(layout['pages'][1:])
  ajustar_portada_ii(layout);self.assertEqual(layout['pages'][1:],other)
  first=copy.deepcopy(layout);ajustar_portada_ii(layout);self.assertEqual(layout,first)
  slots=layout['pages'][0]['slots'];find=lambda key:next(s for s in slots if s['key']==key)
  left=fitz.Rect(find('rol.elabora.firma')['rect']);right=fitz.Rect(find('rol.autoriza.firma')['rect'])
  self.assertAlmostEqual(left.width,right.width);self.assertAlmostEqual(left.height,right.height)
  self.assertEqual(left.y0,right.y0);self.assertEqual(left.y1,right.y1)
  address=find('estacion.direccion');self.assertEqual(address['align'],1);self.assertEqual(address['size'],11.04)
  self.assertGreater(address['rect'][1],find('estacion.razon_social')['rect'][3])
  self.assertLess(address['rect'][3],find('documento.fecha_revision')['rect'][1])
  top=next(s for s in slots if s['key']=='estacion.numero' and s['rect'][1]<60)
  self.assertNotEqual(top.get('transform'),'digits')
 def test_balanced_lines_keep_size_and_postal_marker(self):
  font=fitz.Font('helv');fonts=SimpleNamespace(get=lambda name,value:(font,font.buffer,'coverfont'))
  text='CARRETERA AMOZOC TEZIUTLAN KM 108.5 GONZALO BAUTISTA ZACAPOAXTLA PUEBLA C.P. 73680'
  with fitz.open() as doc:
   page=doc.new_page();rect=fitz.Rect(80,100,400,140)
   count,size=engine._write(page,{'rect':list(rect),'font':'Arial','size':11.04,'min_size':11.04,'align':1,'balance_lines':True},text,fonts)
   self.assertEqual(size,11.04);self.assertGreater(count,1)
   lines=[l for b in page.get_text('dict')['blocks'] for l in b.get('lines',[])]
   widths=[]
   for line in lines:
    r=fitz.Rect(line['bbox']);self.assertAlmostEqual((r.x0+r.x1)/2,(rect.x0+rect.x1)/2,delta=.7);widths.append(r.width)
   self.assertLess(max(widths)-min(widths),70)
   self.assertTrue(any('C.P. 73680' in ''.join(s['text'] for s in l['spans']) for l in lines))
   self.assertEqual(' '.join(''.join(s['text'] for s in l['spans']) for l in lines),text)

class ActualCoverTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  base=os.environ.get('SASISOPA18_BASE')
  if not base:raise unittest.SkipTest('Private PDFs are local only.')
  cls.file=Path(base)/'PROCEDIMIENTO II.pdf'
 def test_cover_render_preserves_format_and_fits_both_signatures(self):
  _,maps=engine.configuration();data=engine.empty_project()
  data['values']={'estacion.numero':'E-48216','estacion.direccion':'CARRETERA AMOZOC TEZIUTLAN KM 108.5, GONZALO BAUTISTA, ZACAPOAXTLA, PUEBLA, C.P. 73680'}
  with tempfile.TemporaryDirectory() as folder:
   signature=Path(folder)/'signature.png';signature_png([[(10,40),(140,100),(400,30)]]).save(signature)
   data['people']=[{'id':'A','firma':str(signature)}];data['roles']={'elabora':'A','autoriza':'A'}
   with fitz.open(self.file) as doc:
    page=doc[0];drawings=lambda p:[{k:v for k,v in d.items() if k!='seqno'} for d in p.get_drawings()]
    before=drawings(page);original_text=page.get_text()
    notes=engine.render_page(doc,0,maps['II'],data,'II',engine.FontBook(doc))
    self.assertEqual(drawings(page),before)
    for label in ('ELABORO','AUTORIZO','EQUIPO DE TRABAJO','REVISION: 0'):self.assertEqual(page.get_text().count(label),original_text.count(label))
    top=''.join(page.get_textbox((345,25,545,55)).split())
    self.assertIn('E-48216',top);self.assertNotIn('EE-',top)
    report=next(n for n in notes if n['field']=='estacion.direccion');self.assertEqual(report['size'],11.04)
    images=page.get_image_info()
    for s in maps['II']['pages'][0]['slots']:
     if s['key'].endswith('.firma'):
      r=fitz.Rect(s['rect'])+(-.002,-.002,.002,.002)
      self.assertTrue(any(r.contains(fitz.Rect(im['bbox'])) for im in images))
