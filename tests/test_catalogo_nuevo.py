import hashlib
import os
import unittest
from pathlib import Path
import fitz
from openpyxl import load_workbook
from catalogo_activo import catalog_state,require_ready

class NewCatalogTests(unittest.TestCase):
    def test_18_documents_only(self):
        state=catalog_state()
        self.assertEqual([t['id'] for t in state['templates']],['I','II','III','IV','V','VI','VII','VIII','IX','X','XI','XII','XIII','XIV','XV','XVI','XVII','XVIII'])
        self.assertEqual(sum(t['pages'] for t in state['templates']),523)
        self.assertEqual(state['engine'],'sasisopa18')
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
        directory=os.environ.get('SASISOPA18_BASE')
        if not directory:self.skipTest('Indica SASISOPA18_BASE para validar los PDF privados.')
        for t in catalog_state()['templates']:
            path=Path(directory)/t['filename']
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),t['sha256'])
            with fitz.open(path) as doc:
                self.assertEqual(len(doc),t['pages'])
                self.assertFalse(any(list(p.widgets() or []) for p in doc))
