"""Importación local del ZIP original o limpio, sin publicar documentos privados."""
from pathlib import Path
from zipfile import ZipFile,BadZipFile
from datetime import datetime
import hashlib,json,shutil
import fitz
ROOT=Path(__file__).resolve().parent


def clean_bytes(blob,record):
 if hashlib.sha256(blob).hexdigest()!=record['source_sha256']:raise ValueError('El PDF no coincide con el original registrado.')
 with fitz.open(stream=blob,filetype='pdf') as doc:
  if len(doc)!=len(record['pages']):raise ValueError('Cantidad de páginas inesperada.')
  for xref in record['remove_images']:doc[0].delete_image(xref)
  for i,regions in enumerate(record['pages']):
   page=doc[i]
   for rect in regions['text']:page.add_redact_annot(rect,fill=None,cross_out=False)
   if regions['text']:page.apply_redactions(images=0,graphics=0)
   for rect in regions['raster']:page.add_redact_annot(rect,fill=None,cross_out=False)
   if regions['raster']:page.apply_redactions(images=2,graphics=0,text=1)
  doc.set_metadata({});doc.del_xml_metadata()
  for name in doc.embfile_names():doc.embfile_del(name)
  doc.xref_set_key(-1,'ID',record['trailer_id'])
  clean=doc.tobytes(garbage=4,deflate=True,no_new_id=True)
 if hashlib.sha256(clean).hexdigest()!=record['target_sha256']:raise ValueError('La limpieza no coincide con la base verificada. Actualiza las dependencias con Instalar.bat.')
 return clean


def import_zip(path,parent):
 records=json.loads((ROOT/'limpieza18.json').read_text(encoding='utf-8'));prepared=[]
 try:
  with ZipFile(path) as archive:
   entries={}
   for item in archive.infolist():
    name=Path(item.filename.replace('\\','/')).name
    if name not in records:continue
    if name in entries:raise ValueError('El ZIP contiene dos copias de '+name+'. Usa un único lote.')
    if item.flag_bits&1 or item.file_size>32*1024*1024:raise ValueError('Archivo cifrado o demasiado grande: '+name)
    entries[name]=item
   missing=set(records)-set(entries)
   if missing:raise ValueError('Faltan procedimientos en el ZIP: '+', '.join(sorted(missing)))
   for name,record in records.items():
    blob=archive.read(entries[name]);digest=hashlib.sha256(blob).hexdigest()
    if digest==record['target_sha256']:clean=blob
    elif digest==record['source_sha256']:clean=clean_bytes(blob,record)
    else:raise ValueError(name+': no corresponde al SASISOPA original o limpio verificado.')
    prepared.append((name,clean))
 except BadZipFile as exc:raise ValueError('El archivo no es un ZIP válido o está dañado.') from exc
 folder=Path(parent)/('base18_'+datetime.now().strftime('%Y%m%d_%H%M%S_%f'));folder.mkdir(parents=True)
 try:
  for name,blob in prepared:
   with (folder/name).open('xb') as f:f.write(blob)
 except Exception:
  shutil.rmtree(folder);raise
 return folder
