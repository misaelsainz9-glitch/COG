import sys
import os
import shutil
import tempfile
import hashlib
import unittest
from pathlib import Path
from datetime import datetime
from PIL import Image
import fitz
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from pdf_politica import generate_pdf
from firma_canvas import signature_png

class PolicyPDFTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        filename=os.environ.get('SASISOPA_NEW_PDF')
        if not filename:raise unittest.SkipTest('El PDF original es privado; indica SASISOPA_NEW_PDF.')
        cls.source=Path(filename)
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);self.templates=self.root/'plantillas';self.templates.mkdir()
        shutil.copyfile(self.source,self.templates/'PROCEDIMIENTO I.pdf')
        self.people=[{'nombre':f'PERSONA FICTICIA {i}','puesto':'OPERADOR'} for i in range(1,6)]
    def run_pdf(self,**kwargs):
        return generate_pdf(self.templates,self.root/'salidas',datetime(2028,2,29),'E-99999','ESTACIÓN DE EJEMPLO SA',self.people,0,1,address='AVENIDA EJEMPLO 100, CIUDAD, C.P. 00000',revision='2',revision_date=datetime(2026,10,1),**kwargs)
    def test_full_pdf_text_geometry_and_original_preserved(self):
        before=hashlib.sha256(self.source.read_bytes()).digest()
        path=self.run_pdf()[0]
        with fitz.open(path) as d,fitz.open(self.source) as original:
            self.assertEqual(len(d),14)
            for i,p in enumerate(d):
                self.assertEqual(p.rect,original[i].rect)
                self.assertEqual([{k:v for k,v in item.items() if k!='seqno'} for item in p.get_drawings()],[{k:v for k,v in item.items() if k!='seqno'} for item in original[i].get_drawings()])
                self.assertIn('E-99999',p.get_text())
                self.assertNotIn('12792',p.get_text())
                self.assertNotIn(''.join(s['text'] for b in original[0].get_text('dict')['blocks'] for l in b.get('lines',[]) for s in l['spans'] if 340<s['bbox'][1]<360).strip().split()[0],p.get_text())
                source_name=next(s['text'].strip() for b in original[0].get_text('dict')['blocks'] for l in b.get('lines',[]) for s in l['spans'] if s['bbox'][0]>=330 and 600<=s['bbox'][1]<=635 and s['text'].strip() not in ('AUTORIZO','ELABORO',''))
                self.assertNotIn(source_name,p.get_text())
            for i in (8,9,11,12,13):self.assertIn('Hora:',d[i].get_text())
            for i in (9,12,13):
                for person in self.people:self.assertIn(person['nombre'],d[i].get_text())
            self.assertIn('29/02/2028',d[13].get_text())
            self.assertEqual(d.metadata['author'],'')
        self.assertEqual(hashlib.sha256(self.source.read_bytes()).digest(),before)
    def test_old_signature_images_not_carried_into_new_copy(self):
        path=self.run_pdf()[0]
        with fitz.open(path) as doc:
            for page in doc:
                for image in page.get_image_info():
                    if image['bbox'][1]>=500:
                        self.assertLessEqual(image['width'],1)
                        self.assertLessEqual(image['height'],1)
    def test_all_blank_preserves_original_visible_pages(self):
        path=generate_pdf(self.templates,self.root/'salidas',None,'','',[],0,0)[0]
        with fitz.open(path) as out,fitz.open(self.source) as original:
            for i in range(14):
                self.assertEqual(out[i].get_text(),original[i].get_text())
                self.assertEqual(out[i].get_pixmap(matrix=fitz.Matrix(.6,.6)).samples,original[i].get_pixmap(matrix=fitz.Matrix(.6,.6)).samples)
    def test_blank_dates_positions_revision_and_rows_keep_original(self):
        rows=[{'nombre':'','puesto':''},{'nombre':'SEGUNDA PERSONA','puesto':''}]
        path=generate_pdf(self.templates,self.root/'salidas',None,'E-99999','EMPRESA FICTICIA',rows,0,0)[0]
        with fitz.open(path) as out,fitz.open(self.source) as original:
            for i in (9,12,13):
                self.assertIn('SEGUNDA PERSONA',out[i].get_text())
                self.assertEqual(out[i].get_text().count('Fecha: --/--/----'),original[i].get_text().count('Fecha: --/--/----'))
                if i!=13:
                    for word in ('Representante','Auxiliar','Jefe'):
                        self.assertEqual(word in out[i].get_text(),word in original[i].get_text())
            self.assertIn('.R0',out[1].get_text())
            self.assertIn('2024',out[1].get_text())
            inserted=out[9].search_for('SEGUNDA PERSONA')[0]
            self.assertGreater(inserted.y0,346)
            self.assertLess(inserted.y1,375)
    def test_signature_only_keeps_original_text(self):
        sig=self.root/'firma.png';signature_png([[(10,40),(110,80),(290,40)]]).save(sig)
        rows=[{'nombre':'','puesto':'','firma':str(sig)}]
        path=generate_pdf(self.templates,self.root/'salidas',None,'','',rows,0,0,signatures=True)[0]
        with fitz.open(path) as out,fitz.open(self.source) as original:
            for i in range(14):self.assertEqual(out[i].get_text(),original[i].get_text())
    def test_images_signatures_and_logo_fit_existing_spaces(self):
        logo=self.root/'logo.png';Image.new('RGB',(100,100),'blue').save(logo)
        sig=self.root/'firma.png';signature_png([[(10,40),(110,80),(290,40)]]).save(sig)
        for p in self.people:p['firma']=str(sig)
        path=self.run_pdf(logo=str(logo),signatures=True)[0]
        with fitz.open(path) as d:
            for page in d:
                found=False
                for item in page.get_images():
                    image=d.extract_image(item[0])
                    if image['width']==100 and image['height']==100:
                        for r in page.get_image_rects(item[0]):
                            if r.y0<100:self.assertAlmostEqual(r.width,r.height,delta=.2);found=True
                self.assertTrue(found,page.number)
            for i in (9,12,13):
                self.assertEqual(sum(1 for item in d[i].get_image_info() if item['bbox'][0]>490 and item['bbox'][1]>200),5)
    def test_six_people_rejected_without_outputs(self):
        self.people.append({'nombre':'SEXTA PERSONA','puesto':'PUESTO'})
        with self.assertRaisesRegex(ValueError,'cinco'):self.run_pdf()
        self.assertFalse((self.root/'salidas').exists())
    def test_long_text_rejected_without_partial_output(self):
        self.people[0]['nombre']='NOMBRE MUY LARGO '*100
        with self.assertRaisesRegex(ValueError,'no cabe'):self.run_pdf()
        self.assertFalse((self.root/'salidas').exists())
    def test_modified_pdf_rejected(self):
        source=self.templates/'PROCEDIMIENTO I.pdf';source.write_bytes(source.read_bytes()+b'change')
        with self.assertRaisesRegex(ValueError,'modificado'):self.run_pdf()
        self.assertFalse((self.root/'salidas').exists())
    def test_no_overwrite(self):
        path=self.run_pdf()[0];blob=path.read_bytes()
        with self.assertRaisesRegex(ValueError,'ya existe'):self.run_pdf()
        self.assertEqual(path.read_bytes(),blob)

if __name__=='__main__':unittest.main()
