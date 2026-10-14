import sys
import tempfile
import unittest
import json
import zipfile
import shutil
from pathlib import Path
from unittest.mock import patch
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from perfiles import FIELDS,save_profile,load_profile

class ProfileTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);self.source=self.root/'origen';self.source.mkdir()
        self.image=self.source/'imagen.png';Image.new('RGBA',(50,20),(0,0,0,255)).save(self.image)
        self.state={'version':1,'fields':{k:'DATO FICTICIO' for k in FIELDS},
                    'people':[{'nombre':f'PERSONA {i}','puesto':'PUESTO','firma':str(self.image) if i==2 else ''} for i in range(6)],
                    'logo':str(self.image),'representative':2,'secretary':4}
    def test_portable_roundtrip_after_original_images_removed(self):
        profile=self.root/'estacion.sasisopa';blob=self.image.read_bytes();save_profile(profile,self.state)
        self.assertEqual(self.state['logo'],str(self.image))
        shutil.rmtree(self.source)
        restored=load_profile(profile,self.root/'cache')
        self.assertEqual(restored['fields'],self.state['fields'])
        self.assertEqual(Path(restored['logo']).read_bytes(),blob)
        self.assertEqual(Path(restored['people'][2]['firma']).read_bytes(),blob)
        self.assertEqual(restored['secretary'],4)
        self.assertNotIn('Fecha (dd/mm/aaaa)',restored['fields'])
        with zipfile.ZipFile(profile) as archive:self.assertEqual(len(archive.namelist()),2)
    def test_empty_images_and_partial_draft_can_be_saved(self):
        self.state['logo']=''
        for p in self.state['people']:p.update(nombre='',puesto='',firma='')
        profile=self.root/'borrador.sasisopa';save_profile(profile,self.state)
        restored=load_profile(profile,self.root/'cache');self.assertEqual(restored['people'],self.state['people'])
    def test_failed_save_preserves_previous_profile(self):
        profile=self.root/'estacion.sasisopa';profile.write_bytes(b'Perfil previo')
        with patch('perfiles.zipfile.ZipFile.writestr',side_effect=OSError('Fallo simulado')):
            with self.assertRaisesRegex(OSError,'simulado'):save_profile(profile,self.state)
        self.assertEqual(profile.read_bytes(),b'Perfil previo')
        self.assertFalse(list(self.root.glob('*.tmp')))
    def test_invalid_file_explained(self):
        profile=self.root/'malo.sasisopa';profile.write_text('No es un perfil')
        with self.assertRaisesRegex(ValueError,'archivo .sasisopa válido'):load_profile(profile,self.root/'cache')
    def test_missing_asset_rejected_without_cache(self):
        profile=self.root/'estacion.sasisopa';save_profile(profile,self.state)
        with zipfile.ZipFile(profile) as archive:metadata=archive.read('perfil.json')
        with zipfile.ZipFile(profile,'w') as archive:archive.writestr('perfil.json',metadata)
        with self.assertRaisesRegex(ValueError,'Falta una imagen'):load_profile(profile,self.root/'cache')
        self.assertFalse((self.root/'cache').exists())
    def test_archive_path_cannot_escape_cache(self):
        self.state['logo']='../../salir.png'
        self.state['people'][2]['firma']=''
        profile=self.root/'malo.sasisopa'
        with zipfile.ZipFile(profile,'w') as archive:archive.writestr('perfil.json',json.dumps(self.state))
        with self.assertRaisesRegex(ValueError,'referencia de imagen'):load_profile(profile,self.root/'cache')
        self.assertFalse((self.root/'cache').exists())
    def test_invalid_rows_rejected(self):
        self.state['people'].append(self.state['people'][0])
        with self.assertRaisesRegex(ValueError,'seis filas'):save_profile(self.root/'malo.sasisopa',self.state)
    def test_damaged_asset_rejected_before_cache(self):
        profile=self.root/'estacion.sasisopa';save_profile(profile,self.state)
        with zipfile.ZipFile(profile) as archive:entries={n:archive.read(n) for n in archive.namelist()}
        asset=next(n for n in entries if n!='perfil.json');entries[asset]=b'Datos incorrectos'
        with zipfile.ZipFile(profile,'w') as archive:
            for n,blob in entries.items():archive.writestr(n,blob)
        with self.assertRaisesRegex(ValueError,'dañada'):load_profile(profile,self.root/'cache')
        self.assertFalse((self.root/'cache').exists())

if __name__=='__main__':unittest.main()
