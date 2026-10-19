"""Synthetic public previews and an actual Tk validation dialog; no private PDFs."""
import hashlib,sys,tempfile
from pathlib import Path
from unittest.mock import patch
import fitz
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import sasisopa18 as e
import equipo_hazop as h
from scripts.vistas_instalaciones import demo,synthetic


def profile(products=('Magna','Diésel','Premium')):
 data=demo(products)
 names=['Ulises Hernández Cruz','Ana María López','Carlos Díaz Ruiz','Diana Vega Soto','Elena Pérez Mora','Felipe Torres León']
 data['people']=[{'id':str(i),'nombre':name,'puesto':'CARGO DEMO '+str(i+1),'empresa':'EMPRESA DEMO '+str(i+1)} for i,name in enumerate(names)]
 data['roles']={role:str(i) for i,role in enumerate(h.ROLES)}
 data['values'].update({'documento.fecha_inicio_estudio':'02/11/2026','documento.fecha_fin_estudio':'05/11/2026'})
 return data


def put(page,text,rect,size=10,align=0):
 from types import SimpleNamespace
 font=fitz.Font('helv');fonts=SimpleNamespace(get=lambda name,value:(font,font.buffer,'DemoFont'))
 e._write(page,{'rect':list(rect),'size':size,'min_size':size,'align':align},text,fonts)


def team_table(doc,layout):
 page=doc[32]
 # All labels and grid in this demonstration are synthetic.
 put(page,'Inicio del estudio:',[53,222,139,235],9)
 put(page,'Fin del estudio:',[53,235,170,248],9)
 columns=[18.24,392.47,602.25,768.72]
 for j,label in enumerate(['Nombre','Cargo / especialidad','Compañía']):
  page.draw_rect((columns[j],285,columns[j+1],301.33),color=(.3,.4,.45),fill=(.28,.65,.73),width=.5)
  put(page,label,[columns[j]+2,288,columns[j+1]-2,301],9,1)
 for s in layout['pages'][32]['slots']:
  if s.get('team_member'):
   r=fitz.Rect(s['rect'])+(-3,-2,3,2);page.draw_rect(r,color=(.35,.35,.35),width=.5)
 xs=[18.24,141.5,265.5,389.5,513.5,637.5,762.65]
 for i,label in enumerate(['Nodo','Incluye','Condiciones','Plano','Grupo multidisciplinario','Fecha']):
  page.draw_rect([xs[i],496,xs[i+1],522],fill=(.28,.65,.73),color=(.35,.35,.35),width=.5)
  put(page,label,[xs[i]+3,499,xs[i+1]-3,521],9)
  page.draw_rect([xs[i],522,xs[i+1],560.53],color=(.35,.35,.35),width=.5)
 return page


def save(page,out,name,clip,scale=1.7):
 page.get_pixmap(matrix=fitz.Matrix(scale,scale),clip=clip,alpha=False).save(out/name)


def validation_photo(out,layout):
 import tkinter as tk
 from PIL import ImageGrab
 import editor_sasisopa as ui
 with tempfile.TemporaryDirectory() as folder:
  folder=Path(folder);source=folder/'PROCEDIMIENTO II.pdf'
  with fitz.open() as doc:
   synthetic(doc,layout);team_table(doc,layout);doc.save(source)
  catalog={'templates':[{'id':'II','filename':source.name,'pages':57,'title':'Plantilla sintética de prueba','sha256':hashlib.sha256(source.read_bytes()).hexdigest()}]}
  with patch.object(e,'configuration',return_value=(catalog,{'II':layout})),patch.object(ui,'ROOT',folder):
   window=tk.Tk();editor=ui.Editor(window)
   try:
    window.geometry('1450x940+0+0');editor.templates.set(str(folder));editor.page.set(33);editor.tabs.select(4)
    editor.vars['documento.fecha_inicio_estudio'].set('02/11/2026');editor.vars['documento.fecha_fin_estudio'].set('01/11/2026')
    editor.update_preview();window.update();captured=[]
    def capture():
     path='.__tk__messagebox'
     if window.tk.call('winfo','exists',path):
      x=int(window.tk.call('winfo','rootx',path));y=int(window.tk.call('winfo','rooty',path))
      w=int(window.tk.call('winfo','width',path));height=int(window.tk.call('winfo','height',path))
      ImageGrab.grab(bbox=(x,y,x+w,y+height),xdisplay=window.winfo_screen()).save(out/'06-fecha-invalida.png')
      captured.append(True);window.tk.call('destroy',path)
    window.after(500,capture);editor.generate();window.update()
    assert captured,'The actual validation dialog was not captured'
    assert not Path(editor.output.get()).exists(),'Invalid data produced output'
   finally:editor.close()


def main(out):
 out.mkdir(parents=True,exist_ok=True);_,maps=e.configuration();layout=maps['II']
 for name,products in [('01-tres-combustibles.png',('Magna','Diésel','Premium')),('02-solo-magna.png',('Magna',))]:
  with fitz.open() as doc:
   page=synthetic(doc,layout);e.render_page(doc,29,layout,profile(products),'II',e.FontBook(doc))
   save(page,out,name,(80,360,532,501),2)
 for name,missing in [('03-equipo-iniciales-fechas.png',False),('05-datos-pendientes.png',True)]:
  data=profile()
  if missing:data['people'][5]['empresa']='';data['installation']['tanks'][0]['presion_operacion']=''
  with fitz.open() as doc:
   synthetic(doc,layout);page=team_table(doc,layout)
   e.render_page(doc,32,layout,data,'II',e.FontBook(doc))
   save(page,out,name,(14,222,772,563))
 with fitz.open() as doc:
  synthetic(doc,layout);page=doc[48]
  for y in (192,220,270,320,370,420,470,520,565):page.draw_line((12,y),(772,y),color=(.4,.4,.4),width=.5)
  for x in (12,130,260,400,580,772):page.draw_line((x,192),(x,565),color=(.4,.4,.4),width=.5)
  put(page,'DATOS DEMO ANTERIORES',[18,230,760,260],12)
  e.render_page(doc,48,layout,profile(('Magna',)),'II',e.FontBook(doc))
  assert 'DATOS DEMO ANTERIORES' not in page.get_text()
  save(page,out,'04-hazop-sin-diesel.png',(8,150,778,571),1.4)
 validation_photo(out,layout)
if __name__=='__main__':main(Path(sys.argv[1]))
