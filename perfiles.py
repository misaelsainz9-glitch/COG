"""Perfiles locales portátiles: datos de estación y copias de logo/firmas."""
from pathlib import Path
import hashlib
import io
import json
import os
import re
import tempfile
import zipfile
from PIL import Image
from personalizacion import validated_image

EVENT_DATE='Fecha (dd/mm/aaaa)'
FIELDS={'Número de estación (ej. E-02585)','Nombre o razón social de la estación','Dirección de la estación','Revisión del encabezado (opcional)','Fecha revisión (dd/mm/aaaa, opcional)'}
MAX_SIZE=64*1024*1024


def validate_state(state):
    if not isinstance(state,dict) or state.get('version')!=1:raise ValueError('El perfil no es compatible con esta versión.')
    fields=state.get('fields');people=state.get('people')
    if not isinstance(fields,dict) or set(fields)!=FIELDS:raise ValueError('El perfil tiene campos de estación incompletos.')
    if any(not isinstance(v,str) or len(v)>4096 for v in fields.values()):raise ValueError('El perfil contiene datos de estación no válidos.')
    if not isinstance(people,list) or len(people)!=6:raise ValueError('El perfil debe contener seis filas de personal.')
    for person in people:
        if not isinstance(person,dict) or set(person)!={'nombre','puesto','firma'} or any(not isinstance(v,str) or len(v)>4096 for v in person.values()):
            raise ValueError('El perfil contiene una fila de personal no válida.')
    if not isinstance(state.get('logo'),str):raise ValueError('El perfil contiene un logo no válido.')
    for key in ('representative','secretary'):
        if type(state.get(key)) is not int or state[key] not in range(6):raise ValueError('Los responsables del perfil no son válidos.')


def save_profile(path,state):
    # Make a separate serializable copy; do not modify the live form's paths.
    state=json.loads(json.dumps(state,ensure_ascii=False));validate_state(state)
    path=Path(path)
    if path.suffix.lower()!='.sasisopa':raise ValueError('Guarda el perfil con extensión .sasisopa.')
    assets={}
    def collect(filename):
        if not filename:return ''
        source,_=validated_image(filename,'la imagen del perfil')
        blob=source.read_bytes();name='assets/'+hashlib.sha256(blob).hexdigest()+source.suffix.lower()
        assets[name]=blob
        return name
    state['logo']=collect(state['logo'])
    for p in state['people']:p['firma']=collect(p['firma'])
    metadata=json.dumps(state,ensure_ascii=False).encode('utf-8')
    if len(metadata)+sum(map(len,assets.values()))>MAX_SIZE:raise ValueError('Las imágenes del perfil superan 64 MB; usa imágenes más pequeñas.')
    temporary=None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent,suffix='.tmp',delete=False) as stream:temporary=Path(stream.name)
        with zipfile.ZipFile(temporary,'w',zipfile.ZIP_DEFLATED) as archive:
            archive.writestr('perfil.json',metadata)
            for name,blob in assets.items():archive.writestr(name,blob)
        os.replace(temporary,path)
    finally:
        if temporary is not None:temporary.unlink(missing_ok=True)


def load_profile(path,cache):
    try:
        with zipfile.ZipFile(path) as archive:
            members=archive.infolist()
            if len(members)>8 or len({m.filename for m in members})!=len(members) or sum(m.file_size for m in members)>MAX_SIZE:
                raise ValueError('El perfil es demasiado grande o tiene entradas duplicadas.')
            if 'perfil.json' not in archive.namelist():raise ValueError('Faltan los datos del perfil.')
            if archive.getinfo('perfil.json').file_size>65536:raise ValueError('Los datos del perfil son demasiado grandes.')
            state=json.loads(archive.read('perfil.json'));validate_state(state)
            references={state['logo'],*(p['firma'] for p in state['people'])}-{''}
            blobs={}
            for name in references:
                if not re.fullmatch(r'assets/[0-9a-f]{64}\.(png|jpg|jpeg)',name):raise ValueError('El perfil contiene una referencia de imagen no válida.')
                if name not in archive.namelist():raise ValueError('Falta una imagen incluida en el perfil.')
                blob=archive.read(name)
                if hashlib.sha256(blob).hexdigest()!=Path(name).stem:raise ValueError('Una imagen del perfil está dañada.')
                try:
                    with Image.open(io.BytesIO(blob)) as image:image.verify()
                    with Image.open(io.BytesIO(blob)) as image:image.load()
                except Exception as exc:raise ValueError('Una imagen del perfil no es válida.') from exc
                blobs[name]=blob
    except (zipfile.BadZipFile,KeyError,json.JSONDecodeError,UnicodeDecodeError) as exc:
        raise ValueError('No se puede abrir el perfil; selecciona un archivo .sasisopa válido.') from exc
    # No archive paths are extracted. Validated images use content-derived filenames.
    cache=Path(cache);cache.mkdir(parents=True,exist_ok=True)
    mapping={}
    for name,blob in blobs.items():
        target=cache/Path(name).name
        if not target.exists() or target.read_bytes()!=blob:
            temporary=None
            try:
                with tempfile.NamedTemporaryFile(dir=cache,suffix='.tmp',delete=False) as stream:
                    stream.write(blob);temporary=Path(stream.name)
                os.replace(temporary,target)
            finally:
                if temporary is not None:temporary.unlink(missing_ok=True)
        mapping[name]=str(target)
    state['logo']=mapping.get(state['logo'],'')
    for p in state['people']:p['firma']=mapping.get(p['firma'],'')
    return state
