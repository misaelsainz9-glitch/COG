import hashlib
import os
import unittest
from pathlib import Path
import fitz
from openpyxl import load_workbook
from catalogo_activo import catalog_state,require_ready

class NewCatalogTests(unittest.TestCase):
    def test_three_new_documents_only(self):
        state=catalog_state()
        self.assertEqual([t['id'] for t in state['templates']],['POL-01','PEL-02','LEG-03'])
        self.assertEqual([t['pages'] for t in state['templates']],[14,53,20])
    def test_excel_catalog_matches_active_pdfs(self):
        w=load_workbook(Path(__file__).resolve().parents[1]/'Base_SASISOPA.xlsx',read_only=True)
        try:
            rows=list(w['Plantillas'].values)[1:]
            self.assertEqual([(r[0],r[1]) for r in rows],[(t['id'],t['filename']) for t in catalog_state()['templates']])
            self.assertTrue(all(r[-1]=='No' for r in list(w['Generar'].values)[1:]))
        finally:w.close()
    def test_native_pdf_mode(self):
        state=require_ready()
        self.assertEqual(state['status'],'ready_pdf')
        self.assertTrue(all(t['format']=='pdf' for t in state['templates']))
    def test_private_sources_match_catalog(self):
        directory=os.environ.get('SASISOPA1_DIR')
        if not directory:self.skipTest('Indica SASISOPA1_DIR para validar los PDF privados.')
        for t in catalog_state()['templates']:
            path=Path(directory)/t['filename']
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),t['sha256'])
            with fitz.open(path) as doc:
                self.assertEqual(len(doc),t['pages'])
                self.assertFalse(any(list(p.widgets() or []) for p in doc))
