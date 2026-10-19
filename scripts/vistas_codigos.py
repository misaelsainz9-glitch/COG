"""Export only code cells, with fictitious data, for browser review."""
import sys
from pathlib import Path
import fitz
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import sasisopa18 as e

def main(base,out):
 out.mkdir(parents=True,exist_ok=True);_,maps=e.configuration()
 cases=[('II',12,'E-48216','2'),('II',33,'E-00007','3'),('II',34,'E-99999','12'),('IV',13,'E-48216','2'),('XI',15,'E-00007','3'),('XIII',16,'E-99999','12')]
 for id,page,station,revision in cases:
  pi=page-1;data=e.empty_project();data['values']={'estacion.numero':station,'documento.revision':revision}
  with fitz.open(base/f'PROCEDIMIENTO {id}.pdf') as doc:
   e.render_page(doc,pi,maps[id],data,id,e.FontBook(doc))
   slot=next(s for s in maps[id]['pages'][pi]['slots'] if s.get('code_suffix'))
   clips={'IV':(675,105,758,146),'XI':(660,26,716,50),'XIII':(698,23,786,65)}
   clip=fitz.Rect(clips[id]) if id in clips else fitz.Rect(slot['rect'])+(-25,-15,25,4)
   doc[pi].get_pixmap(matrix=fitz.Matrix(5,5),clip=clip,alpha=False).save(out/f'{id}-{page}.png')
if __name__=='__main__':main(Path(sys.argv[1]),Path(sys.argv[2]))
