import sys
import os
import unittest
from pathlib import Path
from openpyxl import load_workbook
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from catalogo_activo import catalog_state,require_ready

class NewCatalogTests(unittest.TestCase):
    def test_only_new_document_is_active(self):
        state=catalog_state()
        self.assertEqual([t['id'] for t in state['templates']],['POL-I'])
        self.assertEqual(state['templates'][0]['filename'],'PROCEDIMIENTO I.pdf')
        self.assertEqual(state['templates'][0]['pages'],14)
    def test_excel_catalog_has_no_previous_templates(self):
        w=load_workbook(Path(__file__).resolve().parents[1]/'Base_SASISOPA.xlsx',read_only=True)
        try:
            rows=list(w['Plantillas'].values)
            self.assertEqual(len(rows),2);self.assertEqual(rows[1][0],'POL-I')
            self.assertEqual(list(w['Generar'].values)[1][-1],'No')
        finally:w.close()
    def test_generation_reports_pending_new_mapping(self):
        with self.assertRaisesRegex(ValueError,'pendiente de adaptar'):require_ready()
    def test_uploaded_pdf_matches_registered_source(self):
        filename=os.environ.get('SASISOPA_NEW_PDF')
        if not filename:self.skipTest('El PDF privado no se publica; indica SASISOPA_NEW_PDF para comprobarlo.')
        import hashlib
        import fitz
        state=catalog_state();path=Path(filename)
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),state['templates'][0]['sha256'])
        with fitz.open(path) as d:
            self.assertEqual(len(d),14)
            self.assertEqual(sum(len(list(p.widgets() or [])) for p in d),0)

if __name__=='__main__':unittest.main()
