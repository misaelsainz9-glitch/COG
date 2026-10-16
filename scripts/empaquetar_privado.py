"""Create a local delivery including the user's validated clean PDFs. Never upload it."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
from zipfile import ZipFile, ZIP_DEFLATED
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import fitz
import sasisopa18 as engine


def bundle(public_zip, templates, output):
    catalog,_=engine.configuration();templates=Path(templates);output=Path(output)
    manifest={'documents':catalog['templates']}
    for meta in manifest['documents']:
        path=templates/meta['filename']
        assert hashlib.sha256(path.read_bytes()).hexdigest()==meta['sha256']
        with fitz.open(path) as doc:assert len(doc)==meta['pages']
    output.parent.mkdir(parents=True,exist_ok=True)
    with ZipFile(public_zip) as source:
        manifest['installer_sha256']=hashlib.sha256(source.read('SASISOPA/SASISOPA-Instalador-Windows.exe')).hexdigest()
        with ZipFile(output,'w',compression=ZIP_DEFLATED,compresslevel=6) as target:
            for name in source.namelist():
                if name!='SASISOPA/LEEME-PRIMERO.txt':target.writestr(name,source.read(name))
            for meta in manifest['documents']:
                target.write(templates/meta['filename'],'SASISOPA/Proyecto/plantillas/'+meta['filename'])
            for name in ('Preparar-SASISOPA.ps1','INSTALAR-TODO.bat'):
                target.write(engine.ROOT/'packaging'/name,'SASISOPA/'+name)
            target.writestr('SASISOPA/procedimientos-incluidos.json',json.dumps(manifest,ensure_ascii=False,indent=2).encode('utf-8'))
            target.writestr('SASISOPA/LEEME-PRIMERO.txt',('''PAQUETE PRIVADO SASISOPA — CON LOS 18 PROCEDIMIENTOS (523 PAGINAS)

1. Extrae TODO el ZIP en una carpeta de tu computadora Windows 10/11 de 64 bits.
2. Ejecuta INSTALAR-TODO.bat. Instala el programa y carga los 18 PDF automaticamente.
3. Al terminar se abre SASISOPA. No necesitas importar otro ZIP ni copiar documentos.
4. Captura tus datos, revisa la vista previa, guarda el perfil y genera los PDF.

El instalador incluye Python y las dependencias. No necesitas Word.
Los PDF incluidos son las plantillas limpias, sin las firmas y nombres retirados.
Se guardan en tu carpeta local de SASISOPA. No se borran tus perfiles ni resultados.
Si ya habia otra base configurada, se guarda una copia de esa configuracion.
El codigo fuente tambien esta incluido, con los PDF en Proyecto/plantillas.

ESTE ZIP CONTIENE TUS DOCUMENTOS. NO LO PUBLIQUES EN UN REPOSITORIO PUBLICO.
''').encode('utf-8-sig'))
    with ZipFile(output) as check:
        assert check.testzip() is None
        for meta in manifest['documents']:
            assert hashlib.sha256(check.read('SASISOPA/Proyecto/plantillas/'+meta['filename'])).hexdigest()==meta['sha256']
    digest=hashlib.sha256(output.read_bytes()).hexdigest()
    output.with_suffix('.sha256').write_text(digest+'  '+output.name+'\n')
    print(json.dumps({'private_package':str(output),'documents':18,'pages':523,'sha256':digest,'bytes':output.stat().st_size},indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--public-zip',required=True,type=Path);p.add_argument('--templates',required=True,type=Path);p.add_argument('--output',required=True,type=Path)
    a=p.parse_args();bundle(a.public_zip,a.templates,a.output)
