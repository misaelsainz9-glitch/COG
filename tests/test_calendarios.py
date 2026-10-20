import copy,tempfile,unittest,os
from pathlib import Path
import fitz
import calendarios as c
import sasisopa18 as e

class CalendarModelTests(unittest.TestCase):
 def data(self,date):
  data=e.empty_project();data['values']['documento.fecha_inicio_estudio']=date;return data
 def test_twelve_months_for_every_start_month_and_year_rollover(self):
  for year in (2024,2026,2027):
   for month in range(1,13):
    date=f'01/{month:02d}/{year}';data=self.data(date);before=copy.deepcopy(data);p=c.period(data)
    self.assertEqual(len(p),12);self.assertEqual(len(set(p)),12);self.assertEqual(p[0],(year,month));self.assertEqual(p[-1],(year if month==1 else year+1,12 if month==1 else month-1));self.assertEqual(data,before)
  self.assertEqual(c.period(self.data('30/11/2026'))[-1],(2027,10));self.assertEqual(c.period(self.data('29/02/2024'))[-1],(2025,1))
 def test_blank_override_and_invalid_dates(self):
  self.assertEqual(c.period(self.data('')),[])
  data=self.data('01/11/2026');data['documents']['II']={'documento.fecha_inicio_estudio':'01/01/2027'};self.assertEqual(c.period(data)[-1],(2027,12))
  data['documents']['II']['documento.fecha_inicio_estudio']='';self.assertEqual(c.period(data)[0],(2026,11))
  for date in ('31/02/2026','01/11/9999'):
   with self.assertRaises(ValueError):c.period(self.data(date))
 def test_all_seven_locations_and_duplicated_simulacros(self):
  self.assertEqual(set(c.REGIONS),{('VI',29),('VI',30),('VI',44),('XI',14),('XIII',15),('XIII',69),('XIV',9)})
  self.assertEqual(c.REGIONS['XIII',15],c.REGIONS['XIII',69])
  for spec in c.REGIONS.values():self.assertEqual(len(spec['months']),12)

class CalendarRenderTests(unittest.TestCase):
 def test_all_formats_and_years_without_changing_body(self):
  for date in ('01/11/2026','01/01/2027','31/12/2026'):
   for (doc_id,index),spec in c.REGIONS.items():
    data=e.empty_project();data['values']['documento.fecha_inicio_estudio']=date
    with fitz.open() as doc:
     p=doc.new_page(width=792,height=792)
     if spec.get('raster'):
      # Public synthetic image: old raster labels and boundaries, no private source.
      from PIL import Image,ImageDraw
      import io
      im=Image.new('RGB',(1584,1584),'white');draw=ImageDraw.Draw(im)
      for cell in spec['months']:draw.rectangle(tuple(v*2 for v in cell['rect']),fill=(0,32,96))
      draw.rectangle(tuple(v*2 for v in spec['year_band']),fill=(0,32,96));buffer=io.BytesIO();im.save(buffer,format='PNG');p.insert_image(p.rect,stream=buffer.getvalue())
     p.insert_text((50,720),'OCTUBRE 2024 - CONTENIDO FIJO');p.draw_line((40,700),(750,700));before=copy.deepcopy(data)
     report=c.apply(p,doc_id,index,data,e._write,e.FontBook(doc))
     self.assertEqual(len(report[0]['months']),12);self.assertEqual(data,before);self.assertIn('OCTUBRE 2024',p.get_text())
     for cell,(year,month) in zip(spec['months'],c.period(data)):
      r=fitz.Rect(cell['rect']);labels=[w[4] for w in p.get_text('words') if r.contains(fitz.Point((w[0]+w[2])/2,(w[1]+w[3])/2))]
      expected=c.MONTHS[month-1][0] if spec['format']=='initial' else c.MONTHS[month-1]
      self.assertEqual(labels,[expected],(doc_id,index,date,cell,labels))
 def test_blank_start_and_unrelated_page_do_not_modify_pdf(self):
  with fitz.open() as doc:
   p=doc.new_page();p.insert_text((50,50),'AGOSTO 2026');original=p.get_contents();before=p.get_text()
   self.assertEqual(c.apply(p,'VI',29,e.empty_project(),e._write,e.FontBook(doc)),[]);self.assertEqual(p.get_contents(),original);self.assertEqual(p.get_text(),before)
   data=e.empty_project();data['values']['documento.fecha_inicio_estudio']='01/11/2026'
   self.assertEqual(c.apply(p,'I',0,data,e._write,e.FontBook(doc)),[])

 def test_date_only_export_and_preview_use_the_same_calendar(self):
  import hashlib
  from unittest.mock import patch
  with tempfile.TemporaryDirectory() as tmp:
   folder=Path(tmp);source=folder/'PROCEDIMIENTO XIV.pdf'
   with fitz.open() as doc:
    for _ in range(10):doc.new_page(width=792,height=612)
    doc.save(source)
   original=source.read_bytes();catalog={'templates':[{'id':'XIV','filename':source.name,'pages':10,'sha256':hashlib.sha256(original).hexdigest()}]};maps={'XIV':{'pages':[{'size':[0.,0.,792.,612.],'slots':[],'tables':[]} for _ in range(10)]}}
   data=e.empty_project();data['values']['documento.fecha_inicio_estudio']='01/11/2026'
   with patch.object(e,'configuration',return_value=(catalog,maps)):
    paths,_=e.generate(folder,folder/'out',data,['XIV']);preview,_,_=e.preview(folder,data,'XIV',9)
    blank_paths,_=e.generate(folder,folder/'blank',e.empty_project(),['XIV'])
   with fitz.open(paths[0]) as doc:
    self.assertIn('2026-2027',doc[9].get_text());self.assertEqual(preview,doc[9].get_pixmap(alpha=False).tobytes('png'))
   self.assertEqual(source.read_bytes(),original);self.assertEqual(blank_paths[0].read_bytes(),original)

@unittest.skipUnless(os.environ.get('SASISOPA18_BASE'),'Requiere PDF privados locales')
class ActualCalendarTests(unittest.TestCase):
 def test_labels_and_pixels_outside_headers_on_all_actual_tables(self):
  from PIL import Image,ImageChops,ImageDraw
  root=Path(os.environ['SASISOPA18_BASE'])
  for date in ('01/11/2026','01/01/2027'):
   for (doc_id,index),spec in c.REGIONS.items():
    with fitz.open(root/f'PROCEDIMIENTO {doc_id}.pdf') as doc:
     p=doc[index];before=p.get_pixmap(alpha=False);data=e.empty_project();data['values']['documento.fecha_inicio_estudio']=date
     c.apply(p,doc_id,index,data,e._write,e.FontBook(doc));after=p.get_pixmap(alpha=False)
     diff=ImageChops.difference(Image.frombytes('RGB',(before.width,before.height),before.samples),Image.frombytes('RGB',(after.width,after.height),after.samples));draw=ImageDraw.Draw(diff)
     for cell in spec['months']:
      for r in [cell['rect'],cell.get('erase',cell['rect'])]:draw.rectangle((int(r[0])-3,int(r[1])-3,int(r[2])+3,int(r[3])+3),fill=(0,0,0))
     for key in ('year_band','year_range'):
      if spec.get(key):
       r=spec[key];draw.rectangle((int(r[0])-3,int(r[1])-3,int(r[2])+3,int(r[3])+3),fill=(0,0,0))
     self.assertIsNone(diff.getbbox(),(doc_id,index,date))
     for cell,(year,month) in zip(spec['months'],c.period(data)):
      r=fitz.Rect(cell['rect']);labels=[w[4] for w in p.get_text('words') if r.contains(fitz.Point((w[0]+w[2])/2,(w[1]+w[3])/2))]
      expected=c.MONTHS[month-1][0] if spec['format']=='initial' else c.MONTHS[month-1];self.assertEqual(labels,[expected],(doc_id,index,date))
