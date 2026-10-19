"""Public synthetic tables rendered with the real inventory engine and measured map."""
import sys
from pathlib import Path
import fitz
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import sasisopa18 as e
import instalaciones as inv

def demo(products):
 data=e.empty_project();data['values']={'estacion.numero':'E-48216'}
 data['installation']={'enabled':True,'tanks':[{'numero':str(i+1),'producto':p,'litros':str(75000-i*20000),'marca':'MARCA DEMO','confinamiento':'Subterráneo','cupula':'No tiene','presion_vapor':'1 atm','temperatura_almacen':'Ambiente','presion_operacion':'2.1 kg/cm2','temperatura_operacion':'25 °C','flujo':'40 L/min','plano':'PLANO DEMO'} for i,p in enumerate(products)],'equipment':{p:{'dispensarios':'2','mangueras':'4'} for p in products}}
 return data

def synthetic(doc,layout):
 for spec in layout['pages']:doc.new_page(width=spec['size'][2],height=spec['size'][3])
 page=doc[29];xs=[86.42,135.86,213.77,320.09,383.95,447.79,525.7];ys=[365.11,408.79,438.07,467.35,496.75]
 for row in range(4):
  for col in range(6):page.draw_rect([xs[col],ys[row],xs[col+1],ys[row+1]],fill=(.75,.9,.68),color=(.3,.4,.3),width=.5)
 labels=['Tanque\nNo.','Capacidad\n(litros)','Producto','Tipo de\ncúpula','Presión de\nvapor','Temperatura']
 for col,text in enumerate(labels):page.insert_textbox([xs[col]+2,370,xs[col+1]-2,406],text,fontsize=8,align=1)
 return page

def main(out):
 out.mkdir(parents=True,exist_ok=True);_,maps=e.configuration()
 for name,products in [('01-tres-productos',('Magna','Diésel','Premium')),('02-solo-magna',('Magna',)),('03-sin-magna',('Premium','Diésel'))]:
  data=demo(products)
  with fitz.open() as doc:
   page=synthetic(doc,maps['II']);fonts=e.FontBook(doc);e.render_page(doc,29,maps['II'],data,'II',fonts)
   page.get_pixmap(matrix=fitz.Matrix(2,2),clip=(80,360,532,501),alpha=False).save(out/f'{name}.png')
   if name=='01-tres-productos':
    inv.append_inventory(doc,data,'E-48216',e._write,fonts)
    doc[-1].get_pixmap(matrix=fitz.Matrix(1.4,1.4),alpha=False).save(out/'04-ficha.png')
if __name__=='__main__':main(Path(sys.argv[1]))
