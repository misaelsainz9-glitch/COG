"""Public synthetic files for the Windows bootstrap test. No private PDF is read."""
import hashlib,json,shutil,sys
from pathlib import Path
import fitz
root=Path(sys.argv[1]);root.mkdir(parents=True,exist_ok=True)
repo=Path(__file__).resolve().parents[1]
for name in ('Preparar-SASISOPA.ps1','INSTALAR-TODO.bat'):shutil.copy2(repo/'packaging'/name,root/name)
base=root/'Proyecto/plantillas';base.mkdir(parents=True,exist_ok=True)
manifest={'documents':[]}
for meta in json.loads((repo/'catalogo18.json').read_text())['templates']:
 path=base/meta['filename']
 with fitz.open() as doc:
  for _ in range(meta['pages']):doc.new_page()
  doc.save(path,deflate=True)
 manifest['documents'].append({**meta,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
manifest['installer_sha256']=hashlib.sha256((root/'SASISOPA-Instalador-Windows.exe').read_bytes()).hexdigest()
(root/'procedimientos-incluidos.json').write_text(json.dumps(manifest),encoding='utf-8')
