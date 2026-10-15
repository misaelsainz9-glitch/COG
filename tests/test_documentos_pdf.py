import hashlib
import json
import os
import shutil
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch
import fitz
from PIL import Image
from catalogo_activo import catalog_state
from documentos_pdf import generate_documents
from firma_canvas import signature_png
from pdf_politica import box_text,spans

ROOT=Path(__file__).resolve().parents[1]

class MultiPDFTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if catalog_state().get('engine')=='sasisopa18':raise unittest.SkipTest('La base SASISOPA1 se retiró; se prueba sasisopa18.')
        directory=os.environ.get('SASISOPA1_DIR')
        if not directory:raise unittest.SkipTest('Los PDF son privados; indica SASISOPA1_DIR.')
        cls.source=Path(directory)
        cls.catalog=catalog_state()['templates']
        cls.maps=json.loads((ROOT/'mapas_pdf.json').read_text())
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);self.templates=self.root/'plantillas'
        self.templates.mkdir();self.out=self.root/'salidas'
        for t in self.catalog:shutil.copyfile(self.source/t['filename'],self.templates/t['filename'])
        self.people=[{'nombre':f'PERSONA EJEMPLO {i}','puesto':'OPERADOR'} for i in range(1,6)]
    def generate(self,**options):
        defaults=dict(address='AVENIDA EJEMPLO 100',revision='2',revision_date=datetime(2026,10,1))
        defaults.update(options)
        return generate_documents(self.templates,self.out,datetime(2028,2,29),'E-99999','EMPRESA FICTICIA SA',self.people,0,1,**defaults)
    def test_blank_is_exact_copy_all_three(self):
        paths=generate_documents(self.templates,self.out,None,'','',[],0,0)
        self.assertEqual(len(paths),3)
        for t,path in zip(self.catalog,paths):self.assertEqual(path.read_bytes(),(self.source/t['filename']).read_bytes())
    def test_full_batch_and_merged_preserve_geometry_and_sources(self):
        before=[hashlib.sha256((self.templates/t['filename']).read_bytes()).digest() for t in self.catalog]
        paths=self.generate(merge=True)
        self.assertEqual(len(paths),4)
        offset=0
        with fitz.open(paths[-1]) as combined:
            self.assertEqual(len(combined),87)
            for t,path in zip(self.catalog,paths):
                with fitz.open(path) as doc,fitz.open(self.source/t['filename']) as original:
                    self.assertEqual(len(doc),t['pages'])
                    import re
                    old_station=re.search(r'E-?\s*(\d{5})',original[0].get_text()).group(1)
                    old_company=next(s['text'] for s in spans(original[0]) if 280<s['bbox'][1]<410 and s['text'].strip().lower().startswith('grupo')).split(',')[0].split()[-1].upper()
                    for i,page in enumerate(doc):
                        self.assertEqual(page.rect,original[i].rect)
                        drawings=lambda p:[{k:v for k,v in item.items() if k!='seqno'} for item in p.get_drawings()]
                        self.assertEqual(drawings(page),drawings(original[i]))
                        info=self.maps[t['id']]['pages'][i]
                        masks=[fitz.Rect(f['rect']) for key in ('fields','stations','codes','attendance') for f in info[key]]
                        def untouched(p):
                            from collections import Counter
                            return Counter((c['c'],tuple(round(x,2) for x in c['bbox']))
                                for b in p.get_text('rawdict')['blocks'] for l in b.get('lines',[]) for s in l['spans'] for c in s['chars']
                                if not c['c'].isspace() and not any(fitz.Rect(c['bbox']).intersects(r) for r in masks))
                        self.assertFalse(untouched(original[i])-untouched(page),(t['id'],i+1))
                        compact=''.join(page.get_text().upper().split())
                        self.assertNotIn(old_station,compact,(t['id'],i+1))
                        self.assertNotIn(old_company,compact,(t['id'],i+1))
                        self.assertIn('99999',compact,(t['id'],i+1))
                        for code in info['codes']:
                            self.assertIn(''.join((code['prefix']+'99999'+code['suffix']+'2').upper().split()),compact)
                        for f in info['fields']:
                            if f['key']=='representative':self.assertIn('PERSONAEJEMPLO1',compact)
                        if 'AUTORIZO' in original[i].get_text():self.assertIn('AUTORIZO',page.get_text())
                        if t['id']=='PEL-02' and i==33:
                            r=fitz.Rect(40,230.2,240,258)
                            self.assertEqual(''.join(page.get_textbox(r).split()),''.join(original[i].get_textbox(r).split()))
                        self.assertEqual(combined[offset+i].get_text(),page.get_text())
                    offset+=len(doc)
        self.assertEqual(before,[hashlib.sha256((self.templates/t['filename']).read_bytes()).digest() for t in self.catalog])
    def test_blank_dates_posts_revision_and_row_positions_preserved(self):
        rows=[{'nombre':'','puesto':''},{'nombre':'SEGUNDA PERSONA','puesto':''}]
        paths=generate_documents(self.templates,self.out,None,'E-99999','EMPRESA FICTICIA',rows,0,0)
        for t,path in zip(self.catalog,paths):
            with fitz.open(path) as doc,fitz.open(self.source/t['filename']) as original:
                for i,info in enumerate(self.maps[t['id']]['pages']):
                    for f in info['fields']:
                        if f['key'].startswith(('meeting_date','revision')):
                            self.assertEqual(doc[i].get_textbox(f['rect']),original[i].get_textbox(f['rect']))
                    for f in info['attendance']:
                        if f['key']=='puesto' or f['key']=='nombre' and f['row']!=1:
                            self.assertEqual(doc[i].get_textbox(f['rect']),original[i].get_textbox(f['rect']))
                        elif f['key']=='nombre':self.assertIn('SEGUNDA PERSONA',doc[i].get_textbox(f['rect']))
    def test_select_one_and_merge_catalog_order(self):
        paths=self.generate(selected=['LEG-03','POL-01'],merge=True)
        self.assertTrue(paths[0].name.startswith('POL-01'))
        self.assertTrue(paths[1].name.startswith('LEG-03'))
        with fitz.open(paths[-1]) as doc:self.assertEqual(len(doc),34)
        self.out=self.root/'otro'
        paths=self.generate(selected=['PEL-02'])
        self.assertEqual(len(paths),1)
        with fitz.open(paths[0]) as doc:self.assertEqual(len(doc),53)
    def test_images_fit_existing_spaces_and_diagrams_survive(self):
        logo=self.root/'logo.png';Image.new('RGB',(100,100),'blue').save(logo)
        sig=self.root/'firma.png';signature_png([[(10,40),(110,80),(290,40)]]).save(sig)
        for p in self.people:p['firma']=str(sig)
        paths=self.generate(logo=str(logo),signatures=True)
        for t,path in zip(self.catalog,paths):
            with fitz.open(path) as doc,fitz.open(self.source/t['filename']) as original:
                for i,info in enumerate(self.maps[t['id']]['pages']):
                    images=doc[i].get_image_info(hashes=True)
                    for f in info['signatures']:
                        self.assertTrue(any(im['width']>1 and (fitz.Rect(f['rect'])+(-.001,-.001,.001,.001)).contains(fitz.Rect(im['bbox'])) for im in images))
                    for old in original[i].get_image_info(hashes=True,xrefs=True):
                        if old['xref'] in self.maps[t['id']]['signature_xrefs']:
                            self.assertFalse(any(im['digest']==old['digest'] for im in images))
                        if old['xref'] not in self.maps[t['id']]['signature_xrefs'] and old['bbox'][1]>=100:
                            self.assertTrue(any(im['digest']==old['digest'] and im['bbox']==old['bbox'] for im in images))
                    for f in info['logos']:
                        found=[im for im in images if im['width']==100 and im['height']==100 and (fitz.Rect(f['rect'])+(-.001,-.001,.001,.001)).contains(fitz.Rect(im['bbox']))]
                        self.assertEqual(len(found),1)
                        r=fitz.Rect(found[0]['bbox']);self.assertAlmostEqual(r.width,r.height,delta=.02)
                    for f in info['attendance']:
                        if f['key']=='firma':
                            self.assertTrue(any(im['width']>1 and (fitz.Rect(f['rect'])+(-.001,-.001,.001,.001)).contains(fitz.Rect(im['bbox'])) for im in images))
    def test_signature_only_preserves_all_text(self):
        sig=self.root/'firma.png';signature_png([[(10,40),(110,80),(290,40)]]).save(sig)
        paths=generate_documents(self.templates,self.out,None,'','',[{'nombre':'','puesto':'','firma':str(sig)}],0,0,signatures=True)
        for t,path in zip(self.catalog,paths):
            with fitz.open(path) as doc,fitz.open(self.source/t['filename']) as original:
                for i,page in enumerate(doc):self.assertEqual(page.get_text(),original[i].get_text())
    def test_modified_and_missing_sources_no_partial_output(self):
        bad=self.templates/self.catalog[-1]['filename']
        bad.write_bytes(bad.read_bytes()+b'change')
        with self.assertRaisesRegex(ValueError,'modificada'):self.generate()
        self.assertFalse(self.out.exists())
        bad.unlink()
        with self.assertRaisesRegex(ValueError,'Falta'):self.generate()
        self.assertFalse(self.out.exists())
    def test_long_text_and_excess_people_no_partial_output(self):
        self.people[0]['nombre']='MUY LARGO '*100
        with self.assertRaisesRegex(ValueError,'no cabe'):self.generate()
        self.assertFalse(self.out.exists())
        self.people.append({'nombre':'SEXTA','puesto':''})
        with self.assertRaisesRegex(ValueError,'cinco'):self.generate()
    def test_invalid_selection_and_duplicate_people(self):
        for selected in ([],['INVALIDO'],['POL-01','POL-01']):
            with self.assertRaisesRegex(ValueError,'Selecciona'):self.generate(selected=selected)
        self.people[1]['nombre']=self.people[0]['nombre'].lower()
        with self.assertRaisesRegex(ValueError,'duplicados'):self.generate()
        self.assertFalse(self.out.exists())
    def test_save_failure_cleans_new_output_only(self):
        keep=self.root/'anterior.pdf';keep.write_bytes(b'keep')
        real_open=Path.open
        def failing_open(path,*args,**kwargs):
            if args and args[0]=='xb' and path.name.startswith('PEL-02'):raise OSError('simulated disk failure')
            return real_open(path,*args,**kwargs)
        with patch.object(Path,'open',failing_open):
            with self.assertRaisesRegex(OSError,'disk failure'):self.generate()
        self.assertFalse(self.out.exists());self.assertEqual(keep.read_bytes(),b'keep')
    def test_existing_output_is_never_overwritten(self):
        self.out.mkdir();keep=self.out/'anterior.pdf';keep.write_bytes(b'keep')
        with self.assertRaisesRegex(ValueError,'ya existe'):self.generate()
        self.assertEqual(keep.read_bytes(),b'keep')

class FontFitTests(unittest.TestCase):
    def test_narrow_source_box_contains_visible_digit_ink(self):
        with fitz.open() as doc:
            page=doc.new_page();r=fitz.Rect(20,20,52,27.3)
            box_text(page,r,'99999','estación',9)
            font=fitz.Font('helv')
            for b in page.get_text('rawdict')['blocks']:
                for line in b.get('lines',[]):
                    for s in line['spans']:
                        for c in s['chars']:
                            glyph=font.glyph_bbox(ord(c['c']));x,y=c['origin'];size=s['size']
                            ink=fitz.Rect(x+glyph.x0*size,y-glyph.y1*size,x+glyph.x1*size,y-glyph.y0*size)
                            self.assertTrue((r+(-.02,-.02,.02,.02)).contains(ink))
