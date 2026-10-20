import copy,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import fitz
import sasisopa18 as e

class NewProjectTests(unittest.TestCase):
 def test_neutral_template_has_no_station_people_or_inherited_defaults(self):
  data=e.new_project();self.assertTrue(data['fresh_project']);self.assertGreater(len(data['bindings']),3000);self.assertFalse(data['people']);self.assertFalse(data['roles']);self.assertIsNone(data['installation']);self.assertNotIn('defaults',data);self.assertNotIn('source_information',data)
  raw=json.dumps(data).upper()
  for marker in ('TENEX','12792','ALFREDO','GUZMAN','ZACAPOAXTLA','233107','73680','19/10/2026','06/08/2026'):self.assertNotIn(marker,raw)
  self.assertFalse(data['values'].get('estacion.numero'));self.assertFalse(data['values'].get('documento.fecha_inicio_estudio'));self.assertFalse(data['tables']);self.assertFalse(data['table_people'])
  other=e.new_project();data['values']['estacion.numero']='E-99999';self.assertFalse(other['values'].get('estacion.numero'))
 def test_save_load_keeps_neutral_and_station_is_required_for_export(self):
  with tempfile.TemporaryDirectory() as tmp:
   data=e.new_project();path=Path(tmp)/'nuevo.sasisopa18.json';e.save_project(path,data);loaded=e.load_project(path);self.assertEqual(data,loaded)
   with self.assertRaisesRegex(ValueError,'número de la nueva estación'):e.generate(tmp,Path(tmp)/'out',loaded,['I'])
   self.assertFalse((Path(tmp)/'out').exists())
 def test_empty_slots_erased_without_erasing_fixed_revision_date(self):
  with fitz.open() as doc:
   p=doc.new_page(width=612,height=792);p.insert_text((50,80),'ESTACION ANTERIOR');p.insert_text((50,120),'OCTUBRE 2024');p.draw_rect((40,40,570,180))
   layout={'pages':[{'size':[0.,0.,612.,792.],'tables':[],'slots':[{'id':'I.1.0','key':'estacion.razon_social','rect':[45,60,350,90],'kind':'text'},{'id':'I.1.1','key':'dato.fecha_original','rect':[45,100,350,130],'kind':'text','preserve_source_empty':True}]}]}
   data=e.empty_project();data['fresh_project']=True;e.render_page(doc,0,layout,data,'I',e.FontBook(doc));self.assertNotIn('ANTERIOR',p.get_text());self.assertIn('OCTUBRE 2024',p.get_text());self.assertEqual(len(p.get_drawings()),1)
 def test_neutral_revision_zero_does_not_depend_on_previous_station(self):
  data=e.new_project();data['values']['documento.revision']=''
  self.assertEqual(e.slot_value(data,{'key':'documento.revision'},'I'),'0')
  self.assertEqual(e.slot_value(data,{'key':'estacion.numero','code_suffix':'.01.PO.01.R','code_revision':'7'},'I'),'')
  data['values']['estacion.numero']='E-99999'
  self.assertEqual(e.slot_value(data,{'key':'estacion.numero','code_suffix':'.01.PO.01.R','code_revision':'7'},'I'),'E-99999.01.PO.01.R0')
 def test_invalid_root_and_missing_recipe_do_not_reset_silently(self):
  for data in ([],None):
   with self.assertRaises(ValueError):e.validate_project(data)
  with tempfile.TemporaryDirectory() as tmp,patch.object(e,'ROOT',Path(tmp)):
   with self.assertRaises(FileNotFoundError):e.new_project()
