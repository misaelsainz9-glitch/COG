import tkinter as tk
from tkinter import ttk,filedialog,messagebox
from pathlib import Path
from datetime import datetime
import threading
import queue
from motor import ROOT,export_pdf
from sencillo import basic_generate
from firma_canvas import signature_dialog

app=tk.Tk();app.title('SASISOPA — Llenado básico');app.geometry('1060x760')
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
# Scroll keeps the Generate button reachable on small screens and with Windows scaling.
canvas=tk.Canvas(app,highlightthickness=0)
scroll=ttk.Scrollbar(app,orient='vertical',command=canvas.yview)
scroll.pack(side='right',fill='y');canvas.pack(side='left',fill='both',expand=True)
canvas.configure(yscrollcommand=scroll.set)
f=ttk.Frame(canvas,padding=18);window=canvas.create_window((0,0),window=f,anchor='nw')
f.bind('<Configure>',lambda e:canvas.configure(scrollregion=canvas.bbox('all')))
canvas.bind('<Configure>',lambda e:canvas.itemconfigure(window,width=e.width))
canvas.bind_all('<MouseWheel>',lambda e:canvas.yview_scroll(int(-e.delta/120),'units'))
ttk.Label(f,text='Completa los campos y genera las siete plantillas',font=('Segoe UI',15,'bold')).pack(anchor='w')
ttk.Label(f,text='Fecha, estación, nombres y puestos. Revisa los textos y la distribución de los documentos antes de utilizarlos.',wraplength=760).pack(anchor='w',pady=8)
fields={}
for label,default in [('Fecha (dd/mm/aaaa)',datetime.now().strftime('%d/%m/%Y')),('Número de estación (ej. E-02585)',''),('Nombre o razón social de la estación',''),('Dirección de la estación',''),('Revisión del encabezado (opcional)',''),('Fecha revisión (dd/mm/aaaa, opcional)','')]:
 row=ttk.Frame(f);row.pack(fill='x',pady=3);ttk.Label(row,text=label,width=38).pack(side='left');v=tk.StringVar(value=default);fields[label]=v;ttk.Entry(row,textvariable=v).pack(side='left',fill='x',expand=True)
logo=tk.StringVar()
row=ttk.Frame(f);row.pack(fill='x',pady=4)
ttk.Label(row,text='Logo de la estación (PNG/JPG)',width=38).pack(side='left')
ttk.Entry(row,textvariable=logo).pack(side='left',fill='x',expand=True)
def choose_logo():
 path=filedialog.askopenfilename(title='Seleccionar logo',filetypes=[('Imágenes','*.png *.jpg *.jpeg')])
 if path:logo.set(path)
ttk.Button(row,text='Elegir',command=choose_logo).pack(side='right')
ttk.Label(f,text='Personal: máximo 6 para este lote; deja las filas restantes vacías.',font=('Segoe UI',11,'bold')).pack(anchor='w',pady=10)
grid=ttk.Frame(f);grid.pack(fill='x');ttk.Label(grid,text='Nombre completo').grid(row=0,column=1);ttk.Label(grid,text='Puesto').grid(row=0,column=2)
people=[]
ttk.Label(grid,text='Firma (opcional)').grid(row=0,column=3)
for i in range(6):
 name=tk.StringVar();role=tk.StringVar();signature=tk.StringVar();people.append((name,role,signature))
 ttk.Label(grid,text=str(i+1),width=3).grid(row=i+1,column=0)
 ttk.Entry(grid,textvariable=name,width=32).grid(row=i+1,column=1,sticky='ew',padx=3,pady=2)
 ttk.Entry(grid,textvariable=role,width=22).grid(row=i+1,column=2,sticky='ew',padx=3)
 actions=ttk.Frame(grid);actions.grid(row=i+1,column=3,sticky='w')
 def choose_signature(v=signature):
  path=filedialog.askopenfilename(title='Seleccionar firma',filetypes=[('Imágenes','*.png *.jpg *.jpeg')])
  if path:v.set(path)
 ttk.Button(actions,text='Subir',width=7,command=choose_signature).pack(side='left')
 ttk.Button(actions,text='Dibujar',width=8,command=lambda v=signature:signature_dialog(app,v.set)).pack(side='left')
 ttk.Button(actions,text='Quitar',width=6,command=lambda v=signature:v.set('')).pack(side='left')
 indicator=tk.StringVar(value='Sin firma')
 signature.trace_add('write',lambda *args,v=signature,ind=indicator:ind.set('Firma lista' if v.get() else 'Sin firma'))
 ttk.Label(actions,textvariable=indicator,width=10).pack(side='left',padx=2)
grid.columnconfigure(1,weight=1);grid.columnconfigure(2,weight=1)
rep=tk.StringVar(value='1');sec=tk.StringVar(value='1')
for label,var in [('Fila del representante / responsable',rep),('Fila del secretario',sec)]:
 row=ttk.Frame(f);row.pack(fill='x',pady=3);ttk.Label(row,text=label,width=38).pack(side='left');ttk.Combobox(row,textvariable=var,values=[str(i) for i in range(1,7)],state='readonly',width=6).pack(side='left')
paths=[]
for label,default in [('Carpeta de plantillas',str(ROOT/'plantillas')),('Guardar documentos en',str(ROOT/'salidas'))]:
 row=ttk.Frame(f);row.pack(fill='x',pady=3);ttk.Label(row,text=label,width=25).pack(side='left');var=tk.StringVar(value=default);paths.append(var);ttk.Entry(row,textvariable=var).pack(side='left',fill='x',expand=True)
 def pick(v=var):
  p=filedialog.askdirectory()
  if p:v.set(p)
 ttk.Button(row,text='Elegir',command=pick).pack(side='right')
pdf=tk.BooleanVar();ttk.Checkbutton(f,text='Crear también PDF con Word',variable=pdf).pack(anchor='w',pady=5)
status=tk.StringVar(value='Las plantillas originales se conservan.');ttk.Label(f,textvariable=status).pack(anchor='w')
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
button=ttk.Button(f,text='Generar los siete documentos',command=generate);button.pack(anchor='w',pady=8)
if __name__=='__main__':app.mainloop()
