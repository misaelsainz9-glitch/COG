import copy,unittest
import fitz
import sasisopa18 as e

class PolicyNameTests(unittest.TestCase):
 def test_name_below_role_and_old_location_erased_even_with_legacy_binding(self):
  _,maps=e.configuration();slot=copy.deepcopy(next(s for s in maps['I']['pages'][10]['slots'] if s['id']=='I.11.10'))
  self.assertGreater(slot['rect'][1],623);self.assertEqual(slot['align'],1)
  layout={'pages':[{'size':[0.,0.,612.,792.],'slots':[],'tables':[]} for _ in range(11)]};layout['pages'][10]['slots']=[slot]
  for legacy in (False,True):
   data=e.empty_project();data['people']=[{'id':'p','nombre':'PERSONA DE PRUEBA'}];data['roles']={'representante_legal':'p'}
   if legacy:data['bindings']=[{**slot,'id':'old','doc':'I','page':10,'replace_id':'I.11.10','rect':[226,541,396,555],'align':0}]
   original=copy.deepcopy(data)
   with fitz.open() as doc:
    for _ in range(11):doc.new_page(width=612,height=792)
    p=doc[10];p.insert_text((211.25,552),'C.',fontsize=12);p.insert_text((231,620),'REPRESENTANTE LEGAL',fontsize=12);p.draw_line((159,600),(460,600))
    e.render_page(doc,10,layout,data,'I',e.FontBook(doc))
    self.assertFalse(p.get_textbox((210,538,405,557)).strip());self.assertIn('REPRESENTANTE LEGAL',p.get_textbox((220,605,410,625)))
    self.assertIn('PERSONA DE PRUEBA',p.get_textbox((159,628,460,650)));self.assertEqual(len(p.get_drawings()),1)
   self.assertEqual(data,original)
