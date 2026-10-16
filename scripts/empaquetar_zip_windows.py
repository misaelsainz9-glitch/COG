"""Make a standard, unencrypted ZIP that Windows can extract directly.

Only the inner payload is encrypted. The password is never included here.
"""
import argparse,hashlib,json
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
ROOT=Path(__file__).resolve().parents[1]


def bundle(payload,extractor,license_file,output):
    payload,extractor,license_file,output=map(Path,(payload,extractor,license_file,output))
    with ZipFile(payload) as encrypted:
        assert all(i.is_dir() or (i.flag_bits&1 and i.compress_type==99) for i in encrypted.infolist())
        assert 'SASISOPA/Preparar-SASISOPA.ps1' in encrypted.namelist()
    assert extractor.read_bytes()[:2]==b'MZ'
    metadata={'payload_sha256':hashlib.sha256(payload.read_bytes()).hexdigest(),
              'extractor_sha256':hashlib.sha256(extractor.read_bytes()).hexdigest(),
              'extractor_source':'https://github.com/ip7z/7zip/releases/tag/25.01'}
    output.parent.mkdir(parents=True,exist_ok=True)
    with ZipFile(output,'w',compression=ZIP_DEFLATED,compresslevel=6) as z:
        z.write(payload,'SASISOPA/Componentes/procedimientos.sasisopa')
        z.write(extractor,'SASISOPA/Componentes/7za.exe')
        z.write(license_file,'SASISOPA/Componentes/License-7zip.txt')
        z.write(ROOT/'packaging/Preparar-paquete.ps1','SASISOPA/Preparar-paquete.ps1')
        z.write(ROOT/'packaging/INSTALAR-PAQUETE-NORMAL.bat','SASISOPA/INSTALAR-TODO.bat')
        z.writestr('SASISOPA/Componentes/paquete.json',json.dumps(metadata,indent=2))
        z.writestr('SASISOPA/LEEME-PRIMERO.txt',('''SASISOPA — ZIP NORMAL PARA WINDOWS

1. Usa "Extraer todo" de Windows sobre este ZIP. No pide contrasena al extraer.
2. Abre la carpeta SASISOPA extraida y ejecuta INSTALAR-TODO.bat.
3. Pega la contrasena del chat cuando se solicite. Incluye el guion final.
   La contrasena no se muestra mientras la pegas. Pulsa Enter.
4. Espera a que termine. El programa se instala y carga los 18 procedimientos
   de 523 paginas automaticamente. No necesitas importar otro ZIP.

No necesitas instalar 7-Zip, Python ni Word. El componente de extraccion
esta incluido. No abras los archivos de Componentes manualmente.
El instalador, codigo fuente y PDF se preparan en tu carpeta local SASISOPA.
Los documentos viajan protegidos dentro del paquete; la contrasena no esta
publicada ni incluida en este ZIP. No es la contrasena de tu cuenta Windows.

Componente incluido: 7-Zip 25.01, de Igor Pavlov. Licencia adjunta en
Componentes/License-7zip.txt. Codigo: https://github.com/ip7z/7zip
''').encode('utf-8-sig'))
    with ZipFile(output) as z:
        assert z.testzip() is None
        assert all(not i.flag_bits&1 and i.compress_type==ZIP_DEFLATED for i in z.infolist())
        assert hashlib.sha256(z.read('SASISOPA/Componentes/procedimientos.sasisopa')).hexdigest()==metadata['payload_sha256']
    output.with_suffix('.sha256').write_text(hashlib.sha256(output.read_bytes()).hexdigest()+'  '+output.name+'\n')
    print(json.dumps({'file':output.name,'bytes':output.stat().st_size,'standard_zip':True,'outer_password_required':False,'inner_payload_encrypted':True},indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser()
    for name in ('payload','extractor','license-file','output'):p.add_argument('--'+name,required=True,type=Path)
    a=p.parse_args();bundle(a.payload,a.extractor,a.license_file,a.output)
