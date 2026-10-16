"""Verify right-aligned station addresses and the optional justification renderer."""
import unittest
from types import SimpleNamespace
import fitz
import sasisopa18 as engine


class AddressAlignmentTests(unittest.TestCase):
    def test_justified_lines_and_left_aligned_last_line(self):
        font = fitz.Font('helv')
        fonts = SimpleNamespace(get=lambda name, text: (font, font.buffer, 'testfont'))
        with fitz.open() as doc:
            page = doc.new_page()
            rect = fitz.Rect(40, 40, 200, 110)
            count, size = engine._write(page, {'rect': list(rect), 'align': 3, 'size': 9},
                                       'AVENIDA PRINCIPAL NUMERO 123 COLONIA CENTRO PUEBLA', fonts)
            self.assertGreater(count, 1)
            self.assertEqual(size, 9)
            lines = {}
            for word in page.get_text('words'):
                lines.setdefault(round(word[1], 2), []).append(word)
            ordered = [lines[y] for y in sorted(lines)]
            self.assertEqual(len(ordered), count)
            for words in ordered:
                self.assertAlmostEqual(words[0][0], rect.x0, delta=1)
            for words in ordered[:-1]:
                self.assertAlmostEqual(words[-1][2], rect.x1, delta=1)
            self.assertLess(ordered[-1][-1][2], rect.x1 - 10)

    def test_all_predefined_station_addresses_are_right_aligned(self):
        _, maps = engine.configuration()
        addresses = [s for d in maps.values() for p in d['pages'] for s in p['slots']
                     if s['key'] == 'estacion.direccion']
        self.assertTrue(addresses)
        self.assertTrue(all(s['align'] == 2 for s in addresses))

    def test_station_address_lines_are_right_aligned(self):
        font = fitz.Font('helv')
        fonts = SimpleNamespace(get=lambda name, text: (font, font.buffer, 'testfont'))
        with fitz.open() as doc:
            page = doc.new_page()
            rect = fitz.Rect(40, 40, 200, 110)
            count, _ = engine._write(page, {'rect': list(rect), 'align': 2, 'size': 9},
                                     'AVENIDA PRINCIPAL NUMERO 123 COLONIA CENTRO PUEBLA', fonts)
            self.assertGreater(count, 1)
            lines = {}
            for word in page.get_text('words'):
                lines.setdefault(round(word[1], 2), []).append(word)
            self.assertEqual(len(lines), count)
            for words in lines.values():
                self.assertAlmostEqual(words[-1][2], rect.x1, delta=1)

    def test_top_aligned_address_starts_at_same_height(self):
        font = fitz.Font('helv')
        fonts = SimpleNamespace(get=lambda name, value: (font, font.buffer, 'testfont'))
        tops = []
        for value in ('AV. CENTRAL 120', 'AV. CENTRAL 120 COLONIA CENTRO MUNICIPIO DE PUEBLA'):
            with fitz.open() as doc:
                page = doc.new_page()
                engine._write(page, {'rect':[40,40,180,85], 'size':9, 'align':2, 'valign':'top'}, value, fonts)
                tops.append(min(w[1] for w in page.get_text('words')))
        self.assertAlmostEqual(tops[0], tops[1], delta=.01)

    def test_station_company_and_address_have_header_gaps(self):
        _, maps = engine.configuration()
        slots = maps['I']['pages'][1]['slots']
        number = next(s for s in slots if s['key']=='estacion.numero' and s['rect'][1]<50)
        company = next(s for s in slots if s['key']=='estacion.razon_social')
        address = next(s for s in slots if s['key']=='estacion.direccion')
        self.assertGreaterEqual(company['rect'][1]-number['rect'][3], 3-.001)
        self.assertGreaterEqual(address['rect'][1]-company['rect'][3], 3-.001)
        self.assertEqual(address['valign'], 'top')
