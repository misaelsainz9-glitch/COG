"""Genera copias de los PDF seleccionados usando mapas calibrados de SASISOPA1."""
from pathlib import Path
from datetime import date,datetime
import hashlib
import json
import re
import shutil
import fitz
from catalogo_activo import require_ready
from personalizacion import validated_image
from pdf_politica import box_text
from motor import MESES

ROOT=Path(__file__).resolve().parent


def _image(page,rect,path):
    _,image=validated_image(path,'la imagen')
    rect=fitz.Rect(rect);ratio=image.px_width/image.px_height
    width=min(rect.width,rect.height*ratio);height=width/ratio
    x=rect.x0+(rect.width-width)/2;y=rect.y0+(rect.height-height)/2
    page.insert_image((x,y,x+width,y+height),filename=path,keep_proportion=True)


def _render(source,metadata,layout,day,station,company,people,representative,secretary,address,logo,revision,revision_date,signatures):
    if not source.is_file():raise ValueError('Falta la plantilla: '+metadata['filename'])
    source_bytes=source.read_bytes()
    if hashlib.sha256(source_bytes).hexdigest()!=metadata['sha256']:raise ValueError('La plantilla fue modificada: '+metadata['filename']+'. Usa el archivo original de SASISOPA1.zip.')
    rep=people[representative] if people else {'nombre':'','puesto':''}
    secret=people[secretary] if people else {'nombre':'','puesto':''}
    with fitz.open(stream=source_bytes,filetype='pdf') as doc:
        if len(doc)!=metadata['pages'] or len(layout['pages'])!=len(doc):raise ValueError('El mapa no coincide con las páginas de '+metadata['filename'])
        digits=re.search(r'E-?\s*(\d{5})',doc[0].get_text()).group(1)
        values={'company':company,'address':address,'revision':revision,
                'revision_label':'REVISION: '+revision if revision else '',
                'revision_month':MESES[revision_date.month-1].capitalize() if revision_date else '',
                'revision_year':str(revision_date.year) if revision_date else '',
                'revision_monthyear':MESES[revision_date.month-1].upper()+' '+str(revision_date.year) if revision_date else '',
                'meeting_date':day.strftime('%d/%m/%Y') if day else '',
                'meeting_date_label':'Fecha: '+day.strftime('%d/%m/%Y') if day else '',
                'representative':rep['nombre'],'secretary':secret['nombre']}
        anything=any(values.values()) or bool(station or logo) or any(p['nombre'] or p['puesto'] or signatures and p.get('firma') for p in people)
        if not anything:return source_bytes,digits
        identity_changed=bool(station or company or any(p['nombre'] for p in people))
        if identity_changed:
            for xref in layout['signature_xrefs']:doc[0].delete_image(xref)
        if logo:
            for xref in {p['xref'] for item in layout['pages'] for p in item['logos']}:doc[0].delete_image(xref)
        for pi,page in enumerate(doc):
            info=layout['pages'][pi]
            if list(page.rect)!=info['size']:raise ValueError('Las dimensiones del mapa no coinciden.')
            ops=[];clear=[];pictures=[]
            def write(rect,value,label,size=9,align=0):
                if value.strip():ops.append((fitz.Rect(rect),value,label,size,align))
            for f in info['fields']:
                value=values[f['key']]
                if f.get('clear_only'):
                    if value:clear.append(fitz.Rect(f['rect']))
                else:write(f['rect'],value,f['key'],f['size'],f['align'])
            code_rects=[]
            if revision:
                for op in info['codes']:
                    value=op['prefix']+(station[2:] if station else digits)+op['suffix']+revision
                    write(op['rect'],value,'Código documental',op['size']);code_rects.append(fitz.Rect(op['rect']))
            if station:
                for f in info['stations']:
                    rect=fitz.Rect(f['rect'])
                    if not any(rect.intersects(r) for r in code_rects):write(rect,f['prefix']+station[2:],'Número estación',f['size'])
            for f in info['attendance']:
                if f['row']>=len(people):continue
                person=people[f['row']]
                if f['key']=='firma':
                    if signatures and person.get('firma'):pictures.append((f['rect'],person['firma']))
                else:write(f['rect'],person[f['key']],'Asistente '+f['key'])
            if signatures and rep.get('firma'):
                for f in info['signatures']:pictures.append((f['rect'],rep['firma']))
                if not identity_changed:
                    for f in info['signatures']:
                        target=fitz.Rect(f['rect'])
                        for old in info['sign_image_rects']:
                            if fitz.Rect(old).intersects(target):page.add_redact_annot(old,fill=None,cross_out=False)
                    page.apply_redactions(images=1,graphics=0,text=1)
            if logo:
                for f in info['logos']:pictures.append((f['rect'],logo))
            for rect,value,label,size,align in ops:page.add_redact_annot(rect,fill=None,cross_out=False)
            for rect in clear:page.add_redact_annot(rect,fill=None,cross_out=False)
            page.apply_redactions(images=0,graphics=0)
            for rect,value,label,size,align in ops:box_text(page,rect,value,label,size,align)
            for rect,path in pictures:_image(page,rect,path)
        doc.set_metadata({})
        return doc.tobytes(garbage=4,deflate=True),digits


def generate_documents(templates,out,day,station,company,people,representative,secretary,*,address='',logo='',revision='',revision_date=None,signatures=False,selected=None,merge=False):
    if require_ready().get('engine')=='sasisopa18':raise ValueError('Usa el editor de 18 documentos desde Iniciar.bat.')
    catalog=require_ready()['templates'];ids=[t['id'] for t in catalog]
    selected=ids if selected is None else list(selected)
    if not selected or len(set(selected))!=len(selected) or any(id not in ids for id in selected):raise ValueError('Selecciona uno o más documentos válidos, sin duplicados.')
    if day is not None and not isinstance(day,(date,datetime)):raise ValueError('Introduce una fecha válida.')
    if revision_date is not None and not isinstance(revision_date,(date,datetime)):raise ValueError('Introduce una fecha de revisión válida.')
    station=station.strip();company=company.strip();address=address.strip();revision=revision.strip()
    if station and not re.fullmatch(r'E-\d{5}',station):raise ValueError('La estación debe tener formato E-00000.')
    if revision and not re.fullmatch('[0-9]+',revision):raise ValueError('La revisión debe ser un entero no negativo.')
    if revision:revision=str(int(revision))
    if len(people)>5:raise ValueError('Las listas de Política admiten hasta cinco personas.')
    names=[p['nombre'].strip().casefold() for p in people if p['nombre'].strip()]
    if len(set(names))!=len(names):raise ValueError('Hay nombres duplicados.')
    if people and (representative not in range(len(people)) or secretary not in range(len(people))):raise ValueError('Selecciona responsables válidos.')
    for value in [station,company,address,revision]+[p[k] for p in people for k in ('nombre','puesto')]:
        if any(ord(c)<32 for c in value):raise ValueError('Los campos no deben tener saltos de línea o caracteres de control.')
    if logo:validated_image(logo,'el logo')
    if signatures:
        for p in people:
            if p.get('firma'):validated_image(p['firma'],'la firma')
    layouts=json.loads((ROOT/'mapas_pdf.json').read_text(encoding='utf-8'))
    out=Path(out)
    if out.exists():raise ValueError('La carpeta del lote ya existe; no se sobrescribirá.')
    prepared=[]
    for metadata in catalog:
        if metadata['id'] not in selected:continue
        blob,digits=_render(Path(templates)/metadata['filename'],metadata,layouts[metadata['id']],day,station,company,people,representative,secretary,address,logo,revision,revision_date,signatures)
        date_label=day.strftime('%Y%m%d') if day else 'fecha_original'
        prepared.append((f'{metadata["id"]}_{station or "E-"+digits}_{date_label}.pdf',blob))
    if merge:
        with fitz.open() as combined:
            for _,blob in prepared:
                with fitz.open(stream=blob,filetype='pdf') as doc:combined.insert_pdf(doc)
            prepared.append(('SASISOPA_unificado.pdf',combined.tobytes(garbage=4,deflate=True)))
    out.mkdir(parents=True)
    paths=[]
    try:
        for filename,blob in prepared:
            path=out/filename
            with path.open('xb') as stream:stream.write(blob)
            paths.append(path)
    except Exception:
        shutil.rmtree(out);raise
    return paths
