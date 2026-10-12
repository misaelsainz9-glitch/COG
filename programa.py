from pathlib import Path
import tkinter as tk
from tkinter import filedialog,messagebox,ttk
from datetime import datetime
import threading
import queue
from motor import Base,export_pdf,ROOT

app=tk.Tk();app.title('SASISOPA — Generador de documentos');app.geometry('720x380')
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
excel=tk.StringVar(value=str(ROOT/'Base_SASISOPA.xlsx'));dest=tk.StringVar(value=str(ROOT/'salidas'));pdf=tk.BooleanVar()
frame=ttk.Frame(app,padding=20);frame.pack(fill='both',expand=True)
ttk.Label(frame,text='Generar documentos desde Excel',font=('Segoe UI',16,'bold')).pack(anchor='w')
ttk.Label(frame,text='Completa el Excel y marca Sí en la hoja Generar. Se crearán copias nuevas.',wraplength=650).pack(anchor='w',pady=12)
for label,var,choose in [('Archivo Excel',excel,lambda:filedialog.askopenfilename(filetypes=[('Excel','*.xlsx')])),('Carpeta de salida',dest,filedialog.askdirectory)]:
 ttk.Label(frame,text=label).pack(anchor='w');row=ttk.Frame(frame);row.pack(fill='x',pady=5)
 ttk.Entry(row,textvariable=var).pack(side='left',fill='x',expand=True)
 def pick(v=var,c=choose):
  value=c()
  if value:v.set(value)
 ttk.Button(row,text='Elegir…',command=pick).pack(side='right',padx=8)
ttk.Checkbutton(frame,text='Crear también PDF usando Microsoft Word',variable=pdf).pack(anchor='w',pady=8)
status=tk.StringVar(value='Revisa las fechas, los asistentes y los acuerdos antes de generar.')
def run():
 path=excel.get();folder=dest.get();want_pdf=pdf.get()
 if not path or not folder:messagebox.showerror('Faltan datos','Elige el Excel y la carpeta de salida.');return
 button.config(state='disabled');status.set('Validando y generando…')
 def worker():
  paths=[]
  try:
   out=Path(folder)/datetime.now().strftime('%Y%m%d_%H%M%S_%f')
   paths=Base(path).generate(out)
   if want_pdf:export_pdf(paths)
   msg=f'Se generaron {len(paths)} documentos en:\n{out}\n\nAbre los Word y revisa su distribución y contenido.'
   notifications.put(lambda:messagebox.showinfo('Documentos generados',msg))
  except Exception as exc:
   msg=str(exc)
   if paths:msg+='\n\nLos Word ya se generaron en '+str(paths[0].parent)+'. La exportación PDF no terminó.'
   notifications.put(lambda m=msg:messagebox.showerror('Revisa los datos',m))
  finally:notifications.put(lambda:(button.config(state='normal'),status.set('Listo para generar.')))
 threading.Thread(target=worker,daemon=False).start()
button=ttk.Button(frame,text='Generar documentos',command=run);button.pack(anchor='w',pady=8)
ttk.Label(frame,textvariable=status,wraplength=650).pack(anchor='w')
if __name__=='__main__':app.mainloop()
