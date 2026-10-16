"""Bundle an already verified Windows installer and its matching public source."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
from zipfile import ZipFile, ZIP_DEFLATED

README = '''SASISOPA — PAQUETE COMPLETO PARA WINDOWS 10/11 DE 64 BITS

1. Extrae todo este ZIP en una carpeta.
2. Ejecuta SASISOPA-Instalador-Windows.exe y sigue sus pasos.
3. Abre SASISOPA desde el menú Inicio.
4. En Documentos → Importar SASISOPA.zip, selecciona tu ZIP original.
5. Captura tus datos, revisa la vista previa y guarda tu perfil.

El instalador incluye Python y los componentes necesarios. No requiere Word.
No necesitas ejecutar los archivos .bat para usar el programa instalado.

CONTENIDO
- SASISOPA-Instalador-Windows.exe: instalador autónomo.
- Proyecto/: código fuente completo, Instalar.bat, Iniciar.bat y dependencias
  declaradas. Es la alternativa para desarrollo; sus .bat requieren Python
  instalado y conexión para descargar las dependencias.
- Comprobaciones/: informes de pruebas del instalador en Windows y SHA-256.

Tus documentos SASISOPA, datos personales y firmas reales no se incluyen
  en este paquete público. Importa tu SASISOPA.zip original desde el programa.
Las imágenes de logos y firmas elegidas deben mantenerse en sus rutas.
'''


def bundle(source_zip, release_dir, output):
    source_zip, release_dir, output = map(Path, (source_zip, release_dir, output))
    installer = release_dir/'SASISOPA-Instalador-Windows.exe'
    expected = (release_dir/'SHA256SUMS.txt').read_text(encoding='utf-8-sig').split()[0].lower()
    assert hashlib.sha256(installer.read_bytes()).hexdigest() == expected, 'Installer checksum mismatch'
    for name in ('comprobacion-instalado.json', 'comprobacion-actualizado.json'):
        report = json.loads((release_dir/name).read_text(encoding='utf-8-sig'))
        assert report['system'] == 'Windows'
        assert all(report[k] for k in ('ok','window','preview','save_load','synthetic_pdf','large_blue_signatures','manual_attendance'))
    lifecycle = json.loads((release_dir/'comprobacion-instalador.json').read_text(encoding='utf-8-sig'))
    assert all(lifecycle[k] for k in ('install','update','uninstall','user_data_preserved'))
    output.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(source_zip) as source:
        names = source.namelist()
        assert all(name in names for name in ('Iniciar.bat','Instalar.bat','editor_sasisopa.py','requirements.txt'))
        assert not any(n.lower().endswith('.pdf') or n.startswith(('.git/','datos_locales/','firmas/')) for n in names)
        for name in names:
            path = PurePosixPath(name)
            assert not path.is_absolute() and '..' not in path.parts and '\\' not in name
        with ZipFile(output, 'w', compression=ZIP_DEFLATED, compresslevel=6) as target:
            target.writestr('SASISOPA/LEEME-PRIMERO.txt', README.encode('utf-8-sig'))
            target.write(installer, 'SASISOPA/'+installer.name)
            for name in ('SHA256SUMS.txt','comprobacion-instalado.json','comprobacion-actualizado.json','comprobacion-instalador.json'):
                target.write(release_dir/name, 'SASISOPA/Comprobaciones/'+name)
            for name in names:
                target.writestr('SASISOPA/Proyecto/'+name, source.read(name))
    with ZipFile(output) as check:
        assert check.testzip() is None
        assert hashlib.sha256(check.read('SASISOPA/'+installer.name)).hexdigest() == expected
    checksum = output.with_name('SHA256SUMS-COMPLETO.txt')
    checksum.write_text(hashlib.sha256(output.read_bytes()).hexdigest()+'  '+output.name+'\n',encoding='utf-8')
    print(json.dumps({'package': output.name, 'bytes': output.stat().st_size,
                      'installer_sha256_verified': True, 'zip_integrity_verified': True,
                      'source_files': len(names)}, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-zip', required=True, type=Path)
    parser.add_argument('--release-dir', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    bundle(args.source_zip, args.release_dir, args.output)
