"""Measure revision/date references and independent signature dates in the private base.

Only coordinates and field rules are saved; no source text or private PDF is published.
"""
import re
import fitz

ROMANS=('I','II','III','IV','V','VI','VII','VIII','IX','X','XI','XII','XIII','XIV','XV','XVI','XVII','XVIII')


def calibrate(maps,base):
 for id,layout in maps.items():
  with fitz.open(base/f'PROCEDIMIENTO {id}.pdf') as source:
   for pi,spec in enumerate(layout['pages']):
    spec['slots']=[s for s in spec['slots'] if not s.get('coherence_calibration')]
    page=source[pi]
    # Approval/signature dates are independent of a document's revision date.
    for block in page.get_text('dict')['blocks']:
     for line in block.get('lines',[]):
      for span in line['spans']:
       if span['bbox'][1]<page.rect.height*.65:continue
       match=re.search(r'Fecha:\s*(\d{2}-\d{2}-\d{4})',span['text'])
       if not match:continue
       for rect in page.search_for(match.group(1)):
        if abs(rect.y0-span['bbox'][1])>1 or rect.x0<span['bbox'][0]-.1 or rect.x1>span['bbox'][2]+.1:continue
        spec['slots'].append({'id':f'{id}.{pi+1}.firmas.fecha.{len(spec["slots"])}','key':'documento.fecha_firmas','rect':list(rect+(0,0,5,1)),'erase_rect':list(rect),'font':span['font'],'size':span['size'],'min_size':span['size'],'kind':'text','clear':True,'erase_full':True,'coherence_calibration':True})
    if id!='VIII' or pi not in (10,11):continue
    tables=[t for t in page.find_tables().tables if t.col_count==6]
    table=next(t for t in tables if any(re.fullmatch(r'\d+',str(row[0] or '').strip()) for row in t.extract()))
    for row,values in zip(table.rows,table.extract()):
     if not re.fullmatch(r'\d+',str(values[0] or '').strip()):continue
     index=int(values[0])-1;ref=ROMANS[index-1] if index else None
     for col,key in ((2,'documento.revision'),(4,'documento.fecha_revision')):
      rect=fitz.Rect(row.cells[col])+(2,2,-2,-2)
      slot={'id':f'VIII.{pi+1}.maestro.{index}.{col}','key':key,'rect':list(rect),'erase_rect':list(rect),'font':'ArialMT','size':10,'min_size':9,'align':1,'kind':'text','clear':True,'erase_full':True,'coherence_calibration':True}
      if ref:slot['reference_doc']=ref
      else:slot['revision_scope']='global_only'
      spec['slots'].append(slot)
