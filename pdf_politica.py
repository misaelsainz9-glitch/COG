"""Llenado específico del PDF original de Política; mantiene 14 páginas."""
from pathlib import Path
from datetime import date,datetime
import hashlib
import re
import fitz
from catalogo_activo import catalog_state
from personalizacion import validated_image
from motor import MESES


def spans(page):
    return [s for b in page.get_text('dict')['blocks'] for l in b.get('lines',[]) for s in l['spans'] if s['text'].strip()]


def box_text(page,rect,text,label,size=9,align=0):
    if not text:return
    try:text.encode('latin-1')
    except UnicodeEncodeError:raise ValueError(f'{label}: utiliza caracteres latinos compatibles con la fuente del PDF.') from None
    rect=fitz.Rect(rect)
    font=fitz.Font('helv')
    single=min(size,(rect.height-.2)/(font.ascender-font.descender))
    while single>=6:
        width=font.text_length(text,fontsize=single)
        if '\n' not in text and width<=rect.width:
            x=rect.x0+(rect.width-width)*(0.5 if align==1 else 1 if align==2 else 0)
            page.insert_text((x,rect.y0+font.ascender*single),text,fontname='helv',fontsize=single)
            return
        single-=.25
    with fitz.open() as trial:
        check=trial.new_page(width=page.rect.width,height=page.rect.height)
        while size>=6:
            if check.insert_textbox(rect,text,fontname='helv',fontsize=size,align=align)>=0:
                page.insert_textbox(rect,text,fontname='helv',fontsize=size,align=align)
                return
            size-=.25
    raise ValueError(f'{label}: el texto no cabe en su espacio. Acórtalo antes de generar.')


def generate_pdf(templates,out,day,station,company,people,representative,secretary,*,address='',logo='',revision='',revision_date=None,signatures=False):
    if not isinstance(day,(date,datetime)):raise ValueError('Introduce una fecha válida.')
    station=station.strip();company=company.strip()
    if not re.fullmatch(r'E-\d{5}',station):raise ValueError('El número de estación debe tener el formato E-00000.')
    if not company or not people or len(people)>5:raise ValueError('Completa la estación y entre una y cinco personas; las listas del PDF tienen cinco filas.')
    if any(not p['nombre'].strip() or not p['puesto'].strip() for p in people):raise ValueError('Completa nombre y puesto de cada persona.')
    if len({p['nombre'].strip().casefold() for p in people})!=len(people):raise ValueError('Hay nombres de personal duplicados.')
    if representative not in range(len(people)) or secretary not in range(len(people)):raise ValueError('Selecciona responsables incluidos en el personal.')
    for value in [station,company,address,revision]+[p[k] for p in people for k in ('nombre','puesto')]:
        if any(ord(c)<32 for c in value):raise ValueError('Los campos no deben contener caracteres de control.')
    if revision and not re.fullmatch(r'[0-9]+',revision):raise ValueError('La revisión debe ser un entero no negativo.')
    if revision:revision=str(int(revision))
    if revision_date is not None and not isinstance(revision_date,(date,datetime)):raise ValueError('Introduce una fecha de revisión válida.')
    if logo:validated_image(logo,'el logo')
    if signatures:
        for p in people:
            if p.get('firma'):validated_image(p['firma'],'la firma')
    metadata=catalog_state()['templates'][0]
    source=Path(templates)/metadata['filename']
    if not source.is_file():raise ValueError('Copia PROCEDIMIENTO I.pdf del nuevo ZIP en la carpeta plantillas.')
    if hashlib.sha256(source.read_bytes()).hexdigest()!=metadata['sha256']:raise ValueError('El PDF fue modificado o no es el original de 14 páginas. Copia el archivo del ZIP recibido.')
    out=Path(out)
    if out.exists():raise ValueError('La carpeta del lote ya existe; no se sobrescribirá.')
    rep=people[representative];secret=people[secretary]
    with fitz.open(source) as doc:
        if len(doc)!=14:raise ValueError('La base debe tener 14 páginas.')
        original=[spans(p) for p in doc]
        old_digits=re.search(r'E-?(\d{5})',doc[0].get_text()).group(1)
        cover_company=next(s['text'].strip() for s in original[0] if 340<s['bbox'][1]<360)
        # Remove embedded old signature/seal images from existing signature areas only.
        logo_xref=doc[0].get_images()[0][0]
        logo_rectangles=[p.get_image_rects(logo_xref) for p in doc]
        removed=set()
        for page in doc:
            for item in page.get_images():
                xref=item[0];rects=page.get_image_rects(xref)
                if xref!=logo_xref and rects and all(r.y0>=500 for r in rects):removed.add(xref)
        for xref in removed:doc[0].delete_image(xref)
        if logo:doc[0].delete_image(logo_xref)
        for index,page in enumerate(doc):
            operations=[];extra=[]
            def field(rect,value,label,size=9,align=0):
                operations.append((fitz.Rect(rect),value,label,size,align))
            if index==0:
                company_box=fitz.Rect(175,343,440,361)
                field(company_box,company,'Nombre de estación',11,1)
                address_box=fitz.Rect(85,366,530,399)
                if address:field(address_box,address,'Dirección de portada',10,1)
            else:
                station_span=next(s for s in original[index] if s['text'].startswith('ESTACION:'))
                y=station_span['bbox'][1]
                company_box=fitz.Rect(134 if index<8 else 139,y+10.3,233 if index<8 else 238,y+41.1)
                field(company_box,company,'Razón social del encabezado',8,2)
                address_box=fitz.Rect(61 if index<8 else 66,y+41.4,234 if index<8 else 239,y+72.5)
                if address:field(address_box,address,'Dirección del encabezado',8,2)
            # Rebuild only spans whose identity/code changes; retain the surrounding body.
            for span in original[index]:
                rect=fitz.Rect(span['bbox']);text=span['text']
                if rect.intersects(company_box) or address and rect.intersects(address_box):continue
                value=re.sub(r'E-?'+old_digits,station,text)
                if index==10:value=value.replace(old_digits,station[2:]).replace(cover_company,company)
                if revision:value=re.sub(r'\.R0\b',f'.R{revision}',value)
                if value!=text:field(rect,value,'Identidad/código',span['size'])
            if revision:
                if index==0:
                    r=page.search_for('REVISION: 0')[0];field(r,'REVISION: '+revision,'Revisión',10)
                else:
                    zero=next((s for s in original[index] if s['text'].strip()=='0' and s['bbox'][1]<110),None)
                    if zero:field(zero['bbox'],revision,'Revisión',8)
            if revision_date:
                if index==0:
                    r=page.search_for('OCTUBRE 2024')[0];field(r,MESES[revision_date.month-1].upper()+' '+str(revision_date.year),'Fecha revisión',10)
                else:
                    for span in original[index]:
                        if span['bbox'][1]<110 and span['text'].strip().lower()=='octubre':field(span['bbox'],MESES[revision_date.month-1].capitalize(),'Mes revisión',8)
                        if span['bbox'][1]<110 and span['text'].strip()=='2024':field(span['bbox'],str(revision_date.year),'Año revisión',8)
            if logo:
                rects=logo_rectangles[index]
                for rect in rects:extra.append(('image',rect,logo))
            if index in (8,9,11,12,13):
                date_span=next(s for s in original[index] if s['text'].strip()=='Fecha:' and 150<s['bbox'][1]<260)
                y=date_span['bbox'][1]
                field((150,y,229,y+16),day.strftime('%d/%m/%Y'),'Fecha reunión',9)
                for span in original[index]:
                    if '--/--/----' in span['text']:field(span['bbox'],'Fecha: '+day.strftime('%d/%m/%Y'),'Fecha lista',8)
            if index in (8,11,13):
                for label,person in [('Convocante:',rep),('Facilitador:',rep),('Secretario:',secret)]:
                    span=next(s for s in original[index] if s['text'].strip()==label);y=span['bbox'][1]
                    field((153,y,480,y+13),person['nombre'],label,9)
            if index in (9,12,13):
                # Physical table column/row boundaries calibrated against this exact original.
                starts={9:[316.5,346.2,375.0,400.2,425.4],12:[298.1,327.9,356.7,381.9,407.1],13:[517.2,547.0,574.9,600.1,625.3]}[index]
                ends={9:[345.6,374.5,399.7,424.9,450.0],12:[327.3,356.2,381.4,406.6,431.8],13:[546.5,574.4,599.6,624.8,650.0]}[index]
                for i,(top,bottom) in enumerate(zip(starts,ends)):
                    name=people[i]['nombre'] if i<len(people) else '';post=people[i]['puesto'] if i<len(people) else ''
                    field((101,top+2,283,bottom-2),name,'Nombre asistente',9)
                    field((292,top+2,396,bottom-2),post,'Puesto asistente',9)
                    if signatures and i<len(people) and people[i].get('firma'):
                        extra.append(('image',fitz.Rect(497,top+2,561,bottom-2),people[i]['firma']))
            if index in (0,10):
                if index==0:
                    target=next(s for s in original[index] if s['bbox'][0]>=330 and 600<=s['bbox'][1]<=635 and s['text'].strip() not in ('AUTORIZO','ELABORO'))
                else:
                    target=next(s for s in original[index] if 180<=s['bbox'][0]<=430 and 530<=s['bbox'][1]<=565)
                r=fitz.Rect(target['bbox']);r.x0=309 if index==0 else 190;r.x1=525 if index==0 else 425
                field(r,rep['nombre'],'Representante legal / autoriza',10,1)
                if signatures and rep.get('firma'):
                    extra.append(('image',fitz.Rect(376,550,459,594) if index==0 else fitz.Rect(276,557,350,604),rep['firma']))
            # Text-only redaction keeps table rules and original vector graphics.
            for rect,value,label,size,align in operations:page.add_redact_annot(rect,fill=None,cross_out=False)
            page.apply_redactions(images=0,graphics=0)
            for rect,value,label,size,align in operations:box_text(page,rect,value,label,size,align)
            for _,rect,path in extra:
                _,image=validated_image(path,'la imagen')
                ratio=image.px_width/image.px_height
                width=min(rect.width,rect.height*ratio);height=width/ratio
                x=rect.x0+(rect.width-width)/2;y=rect.y0+(rect.height-height)/2
                page.insert_image(fitz.Rect(x,y,x+width,y+height),filename=path,keep_proportion=True)
        # Saved data must not retain the source PDF's author metadata or unused signature images.
        doc.set_metadata({})
        blob=doc.tobytes(garbage=4,deflate=True)
    out.mkdir(parents=True)
    target=out/f'POL-I_{station}_{day:%Y%m%d}.pdf'
    try:
        with target.open('xb') as stream:stream.write(blob)
    except Exception:
        target.unlink(missing_ok=True);out.rmdir();raise
    return [target]
