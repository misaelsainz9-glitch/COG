"""Llenado básico: modifica únicamente campos de identidad y fecha."""
from pathlib import Path
from datetime import datetime
import re
import json
import hashlib
import shutil
from docx import Document
from motor import ROOT,cell,cells,replace,cell_like_paragraph,fecha,MESES,fill_session_people

# Filenames are read from the supplied catalog, never from user-controlled paths.
def catalog():
    from openpyxl import load_workbook
    path=ROOT/'Base_SASISOPA.xlsx'
    if not path.is_file():
        raise ValueError('Falta Base_SASISOPA.xlsx en la carpeta del programa. Extrae todo el ZIP; el modo básico también necesita su catálogo.')
    w=load_workbook(path,read_only=True,data_only=True)
    try:
        if 'Plantillas' not in w.sheetnames:raise ValueError('El Excel no contiene la hoja Plantillas. Usa el catálogo incluido en el programa.')
        rows=list(w['Plantillas'].values)
        if not rows or tuple(rows[0][:2])!=('plantilla_id','archivo_word'):
            raise ValueError('No cambies los encabezados plantilla_id y archivo_word de la hoja Plantillas.')
        entries=[(r[0],r[1]) for r in rows[1:] if r[0]]
        if len(entries)!=7 or {r[0] for r in entries}!={f'P{i:02}' for i in range(1,8)}:
            raise ValueError('El catálogo debe contener exactamente las siete plantillas P01 a P07.')
        if any(not isinstance(filename,str) or not filename.strip() for _,filename in entries):
            raise ValueError('Hay un nombre de archivo vacío o no válido en la hoja Plantillas.')
        if len({r[1].casefold() for r in entries})!=7:raise ValueError('Hay archivos de plantilla duplicados.')
        return entries
    finally:w.close()

def basic_generate(templates,out,day,station,company,people,representative,secretary,*,address="",logo="",revision="",revision_date=None,signatures=False):
    if not station.strip() or not company.strip():raise ValueError('Completa el número y el nombre de la estación.')
    if not people or any(not p['nombre'].strip() or not p['puesto'].strip() for p in people):raise ValueError('Completa nombre y puesto de cada persona incluida.')
    if representative not in range(len(people)) or secretary not in range(len(people)):raise ValueError('Selecciona representante y secretario de la lista de personal.')
    fecha(day)
    if revision_date is not None:fecha(revision_date)
    if len({p['nombre'].strip().casefold() for p in people})!=len(people):
        raise ValueError('Hay nombres de personal duplicados; revisa las filas.')
    for value in [station,company,address,revision]+[p[k] for p in people for k in ('nombre','puesto')]:
        if any(ord(c)<32 for c in value):raise ValueError('Los campos no deben contener saltos de línea ni caracteres de control.')
    manifest=ROOT/'plantillas_compatibles.json'
    if not manifest.is_file():raise ValueError('Falta plantillas_compatibles.json. Extrae todo el ZIP del programa.')
    expected=json.loads(manifest.read_text(encoding='utf-8'))
    rep=people[representative];sec=people[secretary];prepared=[]
    for pid,filename in catalog():
        if Path(filename).name!=filename:raise ValueError('Nombre de plantilla no válido.')
        path=Path(templates)/filename
        if not path.is_file():raise ValueError('Falta la plantilla: '+filename)
        if hashlib.sha256(path.read_bytes()).hexdigest()!=expected.get(pid):
            raise ValueError('La plantilla fue modificada o no corresponde a la versión admitida: '+filename+'\nCopia el Word original del ZIP; no uses un documento generado.')
        doc=Document(path)
        replace(doc,'E-02585',station.strip())
        # These are operational dates in the originals. Historical approval dates remain fixed.
        for old in ('13/ENE /2026','13/ENE/2026','16/01/2025'):replace(doc,old,fecha(day))
        replace(doc,'13 de Enero del 2026',f'{day.day} de {MESES[day.month-1]} de {day.year}')
        replace(doc,'ABEL TREVINO GONZALEZ',company.strip())
        for table in doc.tables:
            if not table.rows:continue
            head=[c.text.strip().upper() for c in cells(table.rows[0])]
            # Name/position columns: retain other columns and row properties.
            if 'NOMBRE' in head and ('PUESTO' in head):
                ni=head.index('NOMBRE');pi=head.index('PUESTO')
                is_receipt=head[0]=='TOTAL DE COPIAS'
                rows=list(table.rows[1:-1] if is_receipt else table.rows[1:])
                if len(people)>len(rows):raise ValueError(f'{filename}: admite {len(rows)} personas; indicaste {len(people)}. No se agregaron filas.')
                for i,row in enumerate(rows):
                    cs=cells(row)
                    if i<len(people):
                        cell(cs[ni],people[i]['nombre']);cell(cs[pi],people[i]['puesto'])
                        if head[0]=='N°':cell(cs[0],i+1)
                    else:
                        for c in cs:cell(c,'')
                if is_receipt:
                    total=0
                    for row in rows[:len(people)]:
                        try:total+=int(cells(row)[0].text.strip())
                        except ValueError:pass
                    cell(cells(table.rows[-1])[0],'Total: '+str(total))
            # Explicit roles occur together in a merged cell in four templates.
            for row in table.rows:
                cs=cells(row)
                if cs[0].text.strip()=='Proceso' and len(cs)>=4 and cs[-1].text.strip()!='Tiempo asignado':
                    cell(cs[-2],rep['nombre'])
                if cs[0].text.startswith('Convocante:'):
                    cell(cs[1],'\n'.join([rep['nombre'],rep['nombre'],sec['nombre']]))
        if pid=='P02':
            if len(people)>10:raise ValueError('El plan admite hasta 10 personas.')
            table=doc.tables[1];c=table.cell(3,1)
            fill_session_people(c,station,[p['nombre'] for p in people])
            cell(table.cell(4,3),len(people))
        elif pid=='P01':
            c=doc.tables[2].cell(0,0)
            for p in c.paragraphs:
                if 'Nombre:' in p.text:cell_like_paragraph(p,f'Nombre: {rep["nombre"]}              Puesto: {rep["puesto"]}')
        elif pid=='P03':
            ps=doc.paragraphs
            # Locate signature relative to its unchanged role label.
            for i,p in enumerate(ps):
                if p.text.strip()=='Representante Técnico':
                    if i:cell_like_paragraph(ps[i-1],rep['nombre'])
                    cell_like_paragraph(p,rep['puesto'])
        from personalizacion import apply_header,apply_signatures
        apply_header(doc,address,logo,revision,revision_date)
        if signatures:apply_signatures(doc,pid,people,representative)
        slug=re.sub(r'[^A-Za-z0-9_-]','_',station.strip())[:60]
        prepared.append((f'{pid}_{slug}_{day:%Y%m%d}.docx',doc))
    out=Path(out)
    if out.exists():raise ValueError('La carpeta del lote ya existe; no se sobrescribirá.')
    out.mkdir(parents=True)
    result=[]
    try:
        for filename,doc in prepared:
            path=out/filename;doc.save(path);result.append(path)
    except Exception:
        shutil.rmtree(out)
        raise
    return result
