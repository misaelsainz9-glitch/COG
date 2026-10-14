import tkinter as tk
from tkinter import ttk,filedialog,messagebox
from pathlib import Path
from datetime import datetime
import threading
import queue
from PIL import Image as PILImage,ImageTk
from motor import ROOT,export_pdf
from sencillo import basic_generate
from firma_canvas import signature_dialog
from personalizacion import validated_image
from tema import configure_theme,NAVY,BG
from perfiles import save_profile,load_profile,EVENT_DATE

app=tk.Tk();app.title('SASISOPA — Generador de documentos');app.geometry('1100x850');app.minsize(850,560)
configure_theme(app)
notifications=queue.Queue()
def poll_notifications():
 try:
  while True:notifications.get_nowait()()
 except queue.Empty:pass
 app.after(100,poll_notifications)
app.after(100,poll_notifications)
def close_window():
 if 'button' in globals() and str(button.cget('state'))=='disabled':
  messagebox.showinfo('Generación en curso','Espera a que termine la generación antes de cerrar.')
 else:app.destroy()
app.protocol('WM_DELETE_WINDOW',close_window)
header=tk.Frame(app,bg=NAVY)
header.pack(fill='x')
tk.Label(header,text='SASISOPA — Generador de documentos',font=('Segoe UI',19,'bold'),bg=NAVY,fg='white').pack(anchor='w',padx=24,pady=18)
canvas=tk.Canvas(app,bg=BG,highlightthickness=0)
scroll=ttk.Scrollbar(app,orient='vertical',command=canvas.yview)
scroll.pack(side='right',fill='y');canvas.pack(side='left',fill='both',expand=True)
canvas.configure(yscrollcommand=scroll.set)
f=ttk.Frame(canvas,padding=18,style='Page.TFrame');window=canvas.create_window((0,0),window=f,anchor='nw')
f.bind('<Configure>',lambda e:canvas.configure(scrollregion=canvas.bbox('all')))
canvas.bind('<Configure>',lambda e:canvas.itemconfigure(window,width=e.width))
def scroll_page(event):
 if event.widget.winfo_toplevel()==app:
  canvas.yview_scroll(int(-event.delta/120),'units')
canvas.bind_all('<MouseWheel>',scroll_page)
def section(title):
 border=tk.Frame(f,bg='white',highlightbackground='#d2dee8',highlightthickness=1)
 border.pack(fill='x',pady=(0,14))
 inner=ttk.Frame(border,padding=18);inner.pack(fill='x')
 ttk.Label(inner,text=title,style='Section.TLabel').pack(anchor='w',pady=(0,12))
 return inner
station_section=section('Datos de la estación')
station_body=ttk.Frame(station_section);station_body.pack(fill='x')
station_form=ttk.Frame(station_body);station_form.pack(side='left',fill='x',expand=True)
logo_box=ttk.Frame(station_body,padding=(18,0,0,0));logo_box.pack(side='right',fill='y')
fields={}
for label,display,default in [
 ('Fecha (dd/mm/aaaa)','Fecha (dd/mm/aaaa)',datetime.now().strftime('%d/%m/%Y')),
 ('Número de estación (ej. E-02585)','Número de estación',''),
 ('Nombre o razón social de la estación','Nombre de la estación',''),
 ('Dirección de la estación','Dirección',''),
 ('Revisión del encabezado (opcional)','Revisión (opcional)',''),
 ('Fecha revisión (dd/mm/aaaa, opcional)','Fecha revisión (opcional)','')]:
 row=ttk.Frame(station_form);row.pack(fill='x',pady=3)
 ttk.Label(row,text=display,width=25).pack(side='left')
 v=tk.StringVar(value=default);fields[label]=v
 ttk.Entry(row,textvariable=v).pack(side='left',fill='x',expand=True)
logo=tk.StringVar();logo_photo=None
logo_preview=tk.Label(logo_box,text='Tu logo aquí',width=22,height=7,bg='#f5f8fb',fg='#6b8192',relief='solid',bd=1)
logo_preview.pack(pady=(4,10))
def show_logo(path):
 global logo_photo
 validated_image(path,'el logo')
 with PILImage.open(path) as source:
  preview=source.convert('RGBA');preview.thumbnail((180,110))
 logo_photo=ImageTk.PhotoImage(preview,master=app)
 logo.set(path);logo_preview.configure(image=logo_photo,text='',width=180,height=110)
def choose_logo():
 path=filedialog.askopenfilename(title='Seleccionar logo',filetypes=[('Imágenes','*.png *.jpg *.jpeg')])
 if not path:return
 try:show_logo(path)
 except Exception as exc:messagebox.showerror('No se pudo cargar el logo',str(exc))
def clear_logo():
 global logo_photo
 logo.set('');logo_preview.configure(image='',text='Tu logo aquí',width=22,height=7);logo_photo=None
ttk.Button(logo_box,text='Elegir logo',command=choose_logo).pack(fill='x')
ttk.Button(logo_box,text='Quitar logo',command=clear_logo).pack(fill='x',pady=(4,0))
ttk.Label(station_section,text='Deja los campos opcionales vacíos para conservar el encabezado original. La revisión muestra mes y año.',style='Muted.TLabel',wraplength=900).pack(anchor='w',pady=(10,0))
personal_section=section('Personal y firmas')
ttk.Label(personal_section,text='Hasta seis personas. Puedes subir una firma o dibujarla con el mouse.',style='Muted.TLabel').pack(anchor='w',pady=(0,8))
grid=ttk.Frame(personal_section);grid.pack(fill='x')
for col,label in [(0,'N.º'),(1,'Nombre completo'),(2,'Puesto'),(3,'Firma')]:
 ttk.Label(grid,text=label,style='TableHeader.TLabel').grid(row=0,column=col,sticky='ew')
people=[]
for i in range(6):
 name=tk.StringVar();role=tk.StringVar();signature=tk.StringVar();people.append((name,role,signature))
 ttk.Label(grid,text=str(i+1),width=3).grid(row=i+1,column=0,pady=8)
 ttk.Entry(grid,textvariable=name,width=25).grid(row=i+1,column=1,sticky='ew',padx=4,pady=5)
 ttk.Entry(grid,textvariable=role,width=18).grid(row=i+1,column=2,sticky='ew',padx=4)
 actions=ttk.Frame(grid);actions.grid(row=i+1,column=3,sticky='w',padx=4)
 def choose_signature(v=signature):
  path=filedialog.askopenfilename(title='Seleccionar firma',filetypes=[('Imágenes','*.png *.jpg *.jpeg')])
  if not path:return
  try:validated_image(path,'la firma')
  except Exception as exc:messagebox.showerror('No se pudo cargar la firma',str(exc));return
  v.set(path)
 ttk.Button(actions,text='Subir',width=6,command=choose_signature).pack(side='left',padx=2)
 ttk.Button(actions,text='Dibujar',width=7,command=lambda v=signature:signature_dialog(app,v.set)).pack(side='left',padx=2)
 ttk.Button(actions,text='Quitar',width=6,command=lambda v=signature:v.set('')).pack(side='left',padx=2)
 indicator=tk.StringVar(value='Sin firma')
 signature.trace_add('write',lambda *args,v=signature,ind=indicator:ind.set('Firma lista' if v.get() else 'Sin firma'))
 ttk.Label(actions,textvariable=indicator,style='Muted.TLabel',width=9).pack(side='left',padx=3)
grid.columnconfigure(1,weight=2);grid.columnconfigure(2,weight=1)
rep=tk.StringVar(value='1');sec=tk.StringVar(value='1')
roles=ttk.Frame(personal_section);roles.pack(fill='x',pady=(10,0))
for label,var in [('Fila del representante',rep),('Fila del secretario',sec)]:
 row=ttk.Frame(roles);row.pack(side='left',padx=(0,20))
 ttk.Label(row,text=label).pack(side='left',padx=(0,8))
 ttk.Combobox(row,textvariable=var,values=[str(i) for i in range(1,7)],state='readonly',width=4).pack(side='left')
profile_row=ttk.Frame(station_section);profile_row.pack(fill='x',pady=(12,0))
def save_station():
 path=filedialog.asksaveasfilename(title='Guardar datos de estación',defaultextension='.sasisopa',filetypes=[('Perfil SASISOPA','*.sasisopa')])
 if not path:return
 try:
  state={'version':1,'fields':{k:v.get() for k,v in fields.items() if k!=EVENT_DATE},
         'people':[{'nombre':n.get(),'puesto':p.get(),'firma':sig.get()} for n,p,sig in people],
         'logo':logo.get(),'representative':int(rep.get())-1,'secretary':int(sec.get())-1}
  save_profile(path,state)
 except Exception as exc:messagebox.showerror('No se pudo guardar la estación',str(exc));return
 status.set('Estación guardada con copias de su logo y firmas.')
 messagebox.showinfo('Estación guardada','El archivo contiene los datos, logo y firmas. Puedes cargarlo en otra sesión. La fecha de reunión se captura por separado.')
def load_station():
 path=filedialog.askopenfilename(title='Cargar datos de estación',filetypes=[('Perfil SASISOPA','*.sasisopa')])
 if not path:return
 try:
  state=load_profile(path,ROOT/'datos_locales'/'perfiles')
  if state['logo']:show_logo(state['logo'])
  else:clear_logo()
 except Exception as exc:messagebox.showerror('No se pudo cargar la estación',str(exc));return
 for k,value in state['fields'].items():fields[k].set(value)
 for (n,p,sig),person in zip(people,state['people']):
  n.set(person['nombre']);p.set(person['puesto']);sig.set(person['firma'])
 rep.set(str(state['representative']+1));sec.set(str(state['secretary']+1))
 status.set('Estación cargada. Revisa la fecha de reunión antes de generar.')
 messagebox.showinfo('Estación cargada','Se recuperaron la estación, el personal, el logo y las firmas. La fecha de reunión actual se conserva: revísala antes de generar.')
ttk.Button(profile_row,text='Guardar estación',command=save_station).pack(side='left',padx=(0,8))
ttk.Button(profile_row,text='Cargar estación',command=load_station).pack(side='left')
files_section=section('Configuración de archivos')
paths=[]
for label,default in [('Carpeta de plantillas',str(ROOT/'plantillas')),('Guardar documentos en',str(ROOT/'salidas'))]:
 row=ttk.Frame(files_section);row.pack(fill='x',pady=4)
 ttk.Label(row,text=label,width=25).pack(side='left')
 var=tk.StringVar(value=default);paths.append(var)
 ttk.Entry(row,textvariable=var).pack(side='left',fill='x',expand=True,padx=(0,8))
 def pick(v=var):
  p=filedialog.askdirectory()
  if p:v.set(p)
 ttk.Button(row,text='Elegir',command=pick).pack(side='right')
pdf=tk.BooleanVar();ttk.Checkbutton(files_section,text='Crear también PDF con Word',variable=pdf).pack(anchor='w',pady=8)
status=tk.StringVar(value='Las plantillas originales se conservan. Revisa los documentos generados en Word.')
def generate():
 try:
  if not all(p.get().strip() for p in paths):raise ValueError('Selecciona ambas carpetas.')
  date=datetime.strptime(fields['Fecha (dd/mm/aaaa)'].get().strip(),'%d/%m/%Y')
  indexes=[i for i,(n,p,sig) in enumerate(people) if n.get().strip() or p.get().strip() or sig.get().strip()]
  if int(rep.get())-1 not in indexes or int(sec.get())-1 not in indexes:raise ValueError('El representante y el secretario deben señalar filas con personal.')
  data=[{'nombre':people[i][0].get().strip(),'puesto':people[i][1].get().strip(),'firma':people[i][2].get().strip()} for i in indexes]
  args=(paths[0].get(),Path(paths[1].get())/datetime.now().strftime('%Y%m%d_%H%M%S_%f'),date,fields['Número de estación (ej. E-02585)'].get(),fields['Nombre o razón social de la estación'].get(),data,indexes.index(int(rep.get())-1),indexes.index(int(sec.get())-1))
  revision_value=fields['Fecha revisión (dd/mm/aaaa, opcional)'].get().strip()
  options={'address':fields['Dirección de la estación'].get().strip(),'logo':logo.get().strip(),
           'revision':fields['Revisión del encabezado (opcional)'].get().strip(),
           'revision_date':datetime.strptime(revision_value,'%d/%m/%Y') if revision_value else None,
           'signatures':any(p['firma'] for p in data)}
  if not messagebox.askokcancel('Revisar contenido fijo',
      'Se cambiarán los campos y las imágenes que capturaste.\n'
      'Los campos sin captura, contactos, cargos SASISOPA, horarios, temas y acuerdos conservarán los datos originales.\n'
      'Las firmas seleccionadas se insertarán solo en los espacios definidos: acuse, difusión y nota.\n'
      'La misma lista se usará como asistentes y receptores en los siete documentos.\n\n'
      'Continúa solo si esos datos y esas participaciones son correctos. '
      'Los textos largos pueden cambiar la paginación.'):
   return
  want_pdf=pdf.get()
 except Exception as exc:messagebox.showerror('Revisa los campos',str(exc));return
 button.config(state='disabled');status.set('Generando…')
 def work():
  result=[]
  try:
   result=basic_generate(*args,**options)
   if want_pdf:export_pdf(result)
   msg=f'Se generaron {len(result)} Word en:\n{args[1]}\n\nRevisa textos, paginación y firmas en Word.'
   notifications.put(lambda:messagebox.showinfo('Listo',msg))
  except Exception as exc:
   msg=str(exc)
   if result:msg+='\nLos Word están en '+str(args[1])+'. El PDF no terminó.'
   notifications.put(lambda m=msg:messagebox.showerror('No se completó',m))
  finally:notifications.put(lambda:(button.config(state='normal'),status.set('Listo.')))
 threading.Thread(target=work,daemon=False).start()
button=ttk.Button(files_section,text='Generar documentos',style='Primary.TButton',command=generate)
button.pack(pady=(8,14))
ttk.Label(files_section,textvariable=status,style='Muted.TLabel',wraplength=850).pack(anchor='w')
if __name__=='__main__':app.mainloop()
