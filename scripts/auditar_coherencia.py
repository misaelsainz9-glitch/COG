"""Audit all generated procedures against an explicitly supplied local profile.

Run with private inputs and an output directory outside the public repository.
The report stores field identifiers and page references, never private field values.
Text extraction checks are complemented by geometry, attendance and image checks;
they do not assess engineering conclusions or text baked into source images.
"""
import argparse,collections,hashlib,json,re,sys,unicodedata
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import fitz
import instalaciones as inv
import sasisopa18 as e


def normalized(text):
 return re.sub(r'[^a-z0-9]','',unicodedata.normalize('NFKD',text).casefold())


def master_references(base,maps):
 """List source master-list identifiers absent from the referenced procedure.

 These are documentary findings, not authorization to renumber source records.
 """
 findings=[]
 ids=tuple(maps)
 with fitz.open(base/'PROCEDIMIENTO VIII.pdf') as doc:
  for pi in (10,11):
   for table in doc[pi].find_tables().tables:
    if table.col_count!=6:continue
    for row in table.extract():
     if not re.fullmatch(r'\d+',str(row[0] or '').strip()) or int(row[0])==1:continue
     id=ids[int(row[0])-2]
     match=re.search(r'(\.\d+\.PO\.\d+\.R)\d+',re.sub(r'\s+','',row[1] or ''))
     available=sorted({s['code_suffix'] for p in maps[id]['pages'] for s in p['slots'] if s.get('code_suffix') and '.PO.' in s['code_suffix']})
     if not match or match[1] not in available:findings.append({'document':'VIII','page':pi+1,'reference_document':id,'listed_suffix':match[1] if match else None,'procedure_suffixes':available,'status':'confirmar_identificador_documental'})
 return findings


def record_references(base,maps):
 """Check the existing record index against identifiers found in the base."""
 findings=[];ids=tuple(maps);checked=0
 with fitz.open(base/'PROCEDIMIENTO VIII.pdf') as doc:
  for pi in (13,14,15):
   for table in doc[pi].find_tables().tables:
    if table.col_count!=7:continue
    for row in table.extract():
     if not re.fullmatch(r'\d+',str(row[0] or '').strip()):continue
     checked+=1
     match=re.search(r'(\.(\d+)\.RE\.\d+\.R)\d+',re.sub(r'\s+','',row[2] or ''))
     if not match or not 1<=int(match[2])<=18:continue
     id=ids[int(match[2])-1]
     available={s['code_suffix'] for p in maps[id]['pages'] for s in p['slots'] if s.get('code_suffix')}
     if match[1] not in available:
      canonical=lambda code:re.sub(r'^\.(\d+)\.',lambda m:'.'+str(int(m[1]))+'.',code)
      variants=sorted(code for code in available if canonical(code)==canonical(match[1]))
      findings.append({'document':'VIII','page':pi+1,'reference_document':id,'listed_suffix':match[1],'variants':variants,'status':'diferencia_de_ceros_en_identificador' if variants else 'identificador_no_localizado_en_mapas'})
 return {'checked':checked,'findings':findings}


def audit(base,profile,output):
 data=e.load_project(profile);catalog,maps=e.configuration()
 paths,warnings=e.generate(base,output,data,merge=True)
 report={'documents':[],'warnings':warnings,'failures':[],
         'master_reference_findings':master_references(base,maps),
         'record_index':record_references(base,maps),
         'limits':['No valida conclusiones ni valoraciones de riesgo.',
                   'No lee texto incrustado dentro de imágenes.',
                   'Los campos opcionales vacíos conservan la base.',
                   'Los registros particulares requieren captura y revisión expresa.']}
 preserved=collections.Counter();pending=collections.Counter()
 def failure(id,pi,key,kind):report['failures'].append({'document':id,'page':pi+1,'field':key,'check':kind})
 for meta,path in zip(catalog['templates'],paths):
  id=meta['id'];counts=collections.Counter()
  blob=e._source(base,meta)
  with fitz.open(stream=blob,filetype='pdf') as source,fitz.open(path) as doc:
   for pi,spec in enumerate(maps[id]['pages']):
    page=doc[pi];tp=page.get_textpage();slots=e.slots_for(maps[id],data,id,pi)
    if page.rect!=source[pi].rect:failure(id,pi,'page','dimensions')
    drawings=lambda p:[{k:v for k,v in d.items() if k!='seqno'} for d in p.get_drawings()]
    if drawings(page)!=drawings(source[pi]):failure(id,pi,'page','borders')
    counts['pages']+=1;images=page.get_image_info();flows={}
    for s in spec['slots']:
     if s['key'].startswith('tabla.'):
      counts['attendance_cells']+=1
      if tp.extractTextbox(fitz.Rect(s['rect'])).strip():failure(id,pi,s['key'],'attendance_not_empty')
    inactive=inv.inactive_regions(data,id,pi)
    for s in slots:
     if inv.enabled(data) and s.get('hazop_product') and not inv.tanks(data,s['hazop_product']):continue
     if any(fitz.Rect(r).intersects(fitz.Rect(s['rect'])) for r,p in inactive):continue
     if s.get('code_owner') and any(a['id']==s['code_owner'] for a in slots):continue
     value=e.slot_value(data,s,id)
     if not value:
      if not s['key'].startswith('tabla.'):preserved[s['key']]+=1
      continue
     if value=='Pendiente':pending[s['key']]+=1
     if s.get('kind')=='image':
      counts['images']+=1
      if not any((fitz.Rect(s['rect'])+(-.1,-.1,.1,.1)).contains(fitz.Rect(im['bbox'])) for im in images):failure(id,pi,s['key'],'image_outside_field')
      continue
     value=e._transform(value,s);r=fitz.Rect(s['rect'])+(-1,-2,1,2)
     if s.get('flow'):
      flows.setdefault(s['flow'],[]).append((s,value,tp.extractTextbox(r)));continue
     counts['text_fields']+=1
     if normalized(value) not in normalized(tp.extractTextbox(r)):failure(id,pi,s['key'],'value_not_in_field')
    for group in flows.values():
     group.sort(key=lambda item:item[0].get('flow_order',0));counts['text_flows']+=1
     if normalized(group[0][1]) not in normalized(' '.join(item[2] for item in group)):failure(id,pi,group[0][0]['key'],'value_not_in_flow')
    for region,product in inactive:
     if 'No aplica:' not in tp.extractTextbox(fitz.Rect(region)):failure(id,pi,'instalacion.no_aplica','missing_no_aplica')
   if len(doc)!=meta['pages']+inv.extra_pages(data,id):failure(id,0,'annex','page_count')
  if hashlib.sha256((base/meta['filename']).read_bytes()).hexdigest()!=meta['sha256']:failure(id,0,'source','source_modified')
  report['documents'].append({'id':id,**counts})
 with fitz.open(paths[-1]) as merged:
  report['merged_pages']=len(merged);report['bookmarks']=len(merged.get_toc())
  if len(merged.get_toc())!=18:failure('MERGED',0,'bookmarks','bookmark_count')
 report['optional_fields_preserved']=dict(preserved);report['pending_fields']=dict(pending)
 report['passed']=not report['failures']
 report['passed_scope']='Captura de campos, geometría, imágenes y conservación de originales; no certifica coherencia técnica.'
 report['coherence_status']='requiere_revision_documental_y_tecnica'
 (output/'auditoria_coherencia.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 return report


if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('base',type=Path);parser.add_argument('profile',type=Path);parser.add_argument('output',type=Path)
 args=parser.parse_args();result=audit(args.base,args.profile,args.output)
 print(json.dumps(result,ensure_ascii=False,indent=2));sys.exit(0 if result['passed'] else 1)
