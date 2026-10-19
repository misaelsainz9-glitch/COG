from pathlib import Path
import sys,json,hashlib,shutil
from zipfile import ZipFile,ZIP_DEFLATED
import fitz,pyzipper
root=Path(sys.argv[1]);root.mkdir(parents=True);content=root/'fuente'/'TENEX';(content/'01_PDF').mkdir(parents=True)
ids='I II III IV V VI VII VIII IX X XI XII XIII XIV XV XVI XVII XVIII'.split()
for id in ids:
 with fitz.open() as doc:
  p=doc.new_page();p.insert_text((50,50),'DOCUMENTO SINTETICO DE PRUEBA - '+id);doc.save(content/'01_PDF'/('PROCEDIMIENTO '+id+'.pdf'))
with fitz.open() as doc:
 for id in ids:
  with fitz.open(content/'01_PDF'/('PROCEDIMIENTO '+id+'.pdf')) as part:doc.insert_pdf(part)
 doc.save(content/'01_PDF'/'SASISOPA_UNIDO.pdf')
(content/'02_DATOS').mkdir();(content/'02_DATOS'/'Datos.json').write_text(json.dumps({'station':'E-99999','fictional':True}))
(content/'03_REVISION').mkdir();manifest={'files':[{'path':p.relative_to(content).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in content.rglob('*') if p.is_file()]}
(content/'03_REVISION'/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False),encoding='utf-8')
package=root/'paquete';(package/'Componentes').mkdir(parents=True)
payload=package/'Componentes'/'procedimientos.sasisopa'
with pyzipper.AESZipFile(payload,'w',compression=pyzipper.ZIP_DEFLATED,encryption=pyzipper.WZ_AES) as z:
 z.setpassword(b'PRUEBA-PUBLICA-SIN-DATOS-REALES');z.setencryption(pyzipper.WZ_AES,nbits=256)
 for p in content.rglob('*'):
  if p.is_file():z.write(p,'TENEX/'+p.relative_to(content).as_posix())
shutil.copy2('Abrir-procedimientos.ps1',package/'Abrir-procedimientos.ps1');shutil.copy2('7za.exe',package/'Componentes'/'7za.exe')
metadata={'payload_sha256':hashlib.sha256(payload.read_bytes()).hexdigest(),'extractor_sha256':hashlib.sha256(Path('7za.exe').read_bytes()).hexdigest()}
(package/'Componentes'/'paquete.json').write_text(json.dumps(metadata),encoding='utf-8')
with ZipFile(root/'normal.zip','w',compression=ZIP_DEFLATED) as z:
 for p in package.rglob('*'):
  if p.is_file():z.write(p,p.relative_to(package).as_posix())
print(json.dumps({'synthetic':True,'procedures':18,'wrapper_sha256':hashlib.sha256((package/'Abrir-procedimientos.ps1').read_bytes()).hexdigest()}))
