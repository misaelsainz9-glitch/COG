import tkinter as tk
from tkinter import ttk,filedialog,messagebox
from pathlib import Path
from datetime import datetime
import threading
from motor import ROOT,export_pdf
from sencillo import basic_generate

app=tk.Tk();app.title('SASISOPA — Llenado básico');app.geometry('820x760')
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
for label,default in [('Fecha (dd/mm/aaaa)',datetime.now().strftime('%d/%m/%Y')),('Número de estación (ej. E-02585)',''),('Nombre o razón social de la estación','')]:
 row=ttk.Frame(f);row.pack(fill='x',pady=3);ttk.Label(row,text=label,width=38).pack(side='left');v=tk.StringVar(value=default);fields[label]=v;ttk.Entry(row,textvariable=v).pack(side='left',fill='x',expand=True)
ttk.Label(f,text='Personal: completa las filas necesarias; deja las demás vacías.',font=('Segoe UI',11,'bold')).pack(anchor='w',pady=10)
grid=ttk.Frame(f);grid.pack(fill='x');ttk.Label(grid,text='Nombre completo').grid(row=0,column=1);ttk.Label(grid,text='Puesto').grid(row=0,column=2)
people=[]
for i in range(10):
 name=tk.StringVar();role=tk.StringVar();people.append((name,role));ttk.Label(grid,text=str(i+1),width=3).grid(row=i+1,column=0);ttk.Entry(grid,textvariable=name,width=52).grid(row=i+1,column=1,sticky='ew',padx=3,pady=2);ttk.Entry(grid,textvariable=role,width=35).grid(row=i+1,column=2,sticky='ew',padx=3)
grid.columnconfigure(1,weight=1);grid.columnconfigure(2,weight=1)
rep=tk.StringVar(value='1');sec=tk.StringVar(value='1')
for label,var in [('Fila del representante / responsable',rep),('Fila del secretario',sec)]:
 row=ttk.Frame(f);row.pack(fill='x',pady=3);ttk.Label(row,text=label,width=38).pack(side='left');ttk.Combobox(row,textvariable=var,values=[str(i) for i in range(1,11)],state='readonly',width=6).pack(side='left')
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
  indexes=[i for i,(n,p) in enumerate(people) if n.get().strip() or p.get().strip()]
  if int(rep.get())-1 not in indexes or int(sec.get())-1 not in indexes:raise ValueError('El representante y el secretario deben señalar filas con personal.')
  data=[{'nombre':people[i][0].get().strip(),'puesto':people[i][1].get().strip()} for i in indexes]
  args=(paths[0].get(),Path(paths[1].get())/datetime.now().strftime('%Y%m%d_%H%M%S_%f'),date,fields['Número de estación (ej. E-02585)'].get(),fields['Nombre o razón social de la estación'].get(),data,indexes.index(int(rep.get())-1),indexes.index(int(sec.get())-1))
  if not messagebox.askokcancel('Revisar contenido fijo',
      'Se cambiarán fecha, estación, nombres y puestos.\n'
      'El domicilio, correos, teléfonos, cargos SASISOPA, horarios, temas y acuerdos seguirán como en las plantillas.\n'
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
   result=basic_generate(*args)
   if want_pdf:export_pdf(result)
   msg=f'Se generaron {len(result)} Word en:\n{args[1]}\n\nRevisa textos, paginación y firmas en Word.'
   app.after(0,lambda:messagebox.showinfo('Listo',msg))
  except Exception as exc:
   msg=str(exc)
   if result:msg+='\nLos Word están en '+str(args[1])+'. El PDF no terminó.'
   app.after(0,lambda m=msg:messagebox.showerror('No se completó',m))
  finally:app.after(0,lambda:(button.config(state='normal'),status.set('Listo.')))
 threading.Thread(target=work,daemon=True).start()
button=ttk.Button(f,text='Generar los siete documentos',command=generate);button.pack(anchor='w',pady=8)
if __name__=='__main__':app.mainloop()
