"""Measure complete identifiers from private originals; export geometry only."""
import re
import fitz

ROMANS=['I','II','III','IV','V','VI','VII','VIII','IX','X','XI','XII','XIII','XIV','XV','XVI','XVII','XVIII']
CODE=re.compile(r'E\s*-\s*\d{5}(\s*\.\s*\d+\s*\.\s*(?:PO|RE|P0)\s*\.\s*[\d.]+\s*R\s*)(\d+)')
RASTER={
 'IV':(12,[680,119,750,131],6.8,'.04.RE.02.R'),
 'XI':(14,[665,37,711,43],4.8,'.11.RE.02.R'),
 'XIII':(15,[720,40,772,52],6,'.13.RE.01.R'),
}

def attach(spec,slot,rect,suffix,revision,font,size,baseline=None,raster=False):
 members=[]
 for other in spec['slots']:
  r=fitz.Rect(other.get('erase_rect',other['rect']))
  if other['key']=='documento.revision' and fitz.Rect(rect).intersects(r):
   other['code_owner']=slot['id'];members.append(other['id'])
 slot.update(rect=list(rect),erase_rect=list(rect),font=font.split('+')[-1],size=round(size,2),min_size=round(size,2),align=1,clear=True,
             code_suffix=re.sub(r'\s+','',suffix),code_revision=revision,code_members=members,single_line=True)
 slot.pop('transform',None)
 if baseline is not None:slot['baseline']=baseline
 if raster:slot['raster_clear']=True


def calibrar_codigos(layout,source,roman):
 count=0
 for pi,page in enumerate(source):
  spec=layout['pages'][pi]
  for block in page.get_text('rawdict')['blocks']:
   for line in block.get('lines',[]):
    chars=[(c,s) for s in line['spans'] for c in s['chars']]
    text=''.join(c['c'] for c,s in chars)
    # Headers and cover identifiers only: body references retain their own layout.
    if line['bbox'][1]>150 and not (pi==0 and line['bbox'][1]<280):continue
    for match in CODE.finditer(text):
     selected=chars[match.start():match.end()];rect=fitz.Rect(selected[0][0]['bbox'])
     for c,s in selected[1:]:rect|=fitz.Rect(c['bbox'])
     station=next((s for s in spec['slots'] if s['key']=='estacion.numero' and fitz.Rect(s.get('erase_rect',s['rect'])).intersects(rect)),None)
     if not station:raise ValueError(f'No station slot for code: {roman} {pi+1}')
     style=selected[0][1]
     attach(spec,station,rect,match.group(1),match.group(2),style['font'],style['size'],selected[0][0]['origin'][1]);count+=1
  if roman in RASTER and pi==RASTER[roman][0]:
   _,rect,size,suffix=RASTER[roman]
   station=next(s for s in spec['slots'] if s['key']=='estacion.numero' and fitz.Rect(rect).intersects(fitz.Rect(s['rect'])))
   attach(spec,station,rect,suffix,'0','ArialMT',size,raster=True);count+=1
 return count
