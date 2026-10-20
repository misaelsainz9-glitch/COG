"""Aplicación de escritorio para la base limpia completa de SASISOPA."""
from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter import ttk,filedialog,messagebox
import io,json,uuid,threading,queue,copy
from PIL import Image,ImageTk
import fitz
import sasisopa18 as engine
import instalaciones
import equipo_hazop
import valores_predeterminados
import importar_requisitos
from importar18 import import_zip
from tema import configure_theme,NAVY
from firma_canvas import signature_dialog
from rutas_app import RESOURCE_ROOT,user_root
from personalizacion import validated_image
ROOT=user_root()


class Editor:
 def __init__(self,app):
  ROOT.mkdir(parents=True,exist_ok=True)
  self.app=app;app.title('SASISOPA — Datos y documentos');app.geometry('1440x920');app.minsize(1000,640);configure_theme(app)
  self.catalog,self.maps=engine.configuration();self.inventory=json.loads((RESOURCE_ROOT/'campos_sasisopa_18.json').read_text(encoding='utf-8'))
  self.data=engine.empty_project();self.busy=False;self.closed=False;self.timer=None;self.photo=None;self.scale=1.0;self.messages=queue.Queue();self.selected={}
  self.vars={};self.role_vars={};self.doc_vars={};self.table_vars={};self.custom_doc_fields={};self.field_keys={};self.tab_canvases={};self.drag=None;self.rect_item=None
  bar=tk.Frame(app,bg=NAVY);bar.pack(fill='x');tk.Label(bar,text='SASISOPA · Datos y documentos',font=('Segoe UI',19,'bold'),bg=NAVY,fg='white').pack(side='left',padx=18,pady=14)
  ttk.Button(bar,text='Cargar datos',command=self.load).pack(side='right',padx=8);ttk.Button(bar,text='Guardar datos',command=self.save).pack(side='right',padx=4)
  ttk.Button(bar,text='Importar datos desde Word',command=self.import_requirements).pack(side='right',padx=4)
  self.panes=ttk.Panedwindow(app,orient='horizontal');self.panes.pack(fill='both',expand=True,padx=12,pady=10)
  left=ttk.Frame(self.panes,width=510);right=ttk.Frame(self.panes);self.panes.add(left,weight=2);self.panes.add(right,weight=3)
  self.tabs=ttk.Notebook(left);self.tabs.pack(fill='both',expand=True)
  station=self.tab('Estación');self.shared_box=self.tab('Datos comunes');self.shared_keys=set();installation=self.tab('Instalaciones');persons=self.tab('Personas');roles=self.tab('Funciones');docs=self.tab('Documentos');tables=self.tab('Listas')
  for spec in self.inventory['fields']:
   if spec['scope']=='estacion' or spec['id'] in ('documento.revision','documento.fecha_revision'):
    self.entry(station,spec['label'],self.vars,spec['id'])
  default_logo=RESOURCE_ROOT/'assets'/'logo-pemex.png'
  if default_logo.is_file():self.vars['estacion.logo'].set(str(default_logo))
  ttk.Label(station,text='Deja los datos vacíos para conservar la base limpia. Fechas: dd/mm/aaaa.\nLa fecha de revisión es distinta de las fechas de reuniones y eventos.',wraplength=430).pack(anchor='w',pady=10)
  self.build_installation_tab(installation)
  self.people_list=ttk.Treeview(persons,columns=('name','role'),show='headings',height=7);self.people_list.heading('name',text='Nombre');self.people_list.heading('role',text='Puesto');self.people_list.column('name',width=225);self.people_list.column('role',width=140);self.people_list.pack(fill='x')
  row=ttk.Frame(persons);row.pack(fill='x',pady=7)
  ttk.Button(row,text='Agregar persona',command=self.add_person).pack(side='left');ttk.Button(row,text='Editar',command=self.edit_person).pack(side='left',padx=5);ttk.Button(row,text='Eliminar',command=self.delete_person).pack(side='left')
  ttk.Label(persons,text='Guarda cada persona una sola vez y selecciónala en las funciones que desempeñe. No hay un límite general de cinco personas.',wraplength=430).pack(anchor='w')
  for spec in self.inventory['roles']:
   row=ttk.Frame(roles);row.pack(fill='x',pady=4);ttk.Label(row,text=spec['label'],width=25).pack(side='left')
   var=tk.StringVar();self.role_vars[spec['id']]=var;combo=ttk.Combobox(row,textvariable=var,state='readonly',width=24);combo.pack(side='left',fill='x',expand=True);var.combo=combo;var.trace_add('write',self.schedule)
  ttk.Label(roles,text='Las funciones se asignan por separado. AUTORIZA no se deduce de otro cargo. Sólo se llenan los espacios que correspondan a cada función.',wraplength=430).pack(anchor='w',pady=9)
  project=ttk.LabelFrame(docs,text='Proyecto / estudio HAZOP',padding=6);project.pack(fill='x',pady=8)
  for key,label in equipo_hazop.DATES:self.entry(project,label+' (dd/mm/aaaa)',self.vars,key)
  ttk.Label(project,text='Se aplican al estudio del procedimiento II. Son independientes de revisión y reuniones. Equipo: captura en Personas y asigna en Funciones; las iniciales se calculan del nombre completo.',wraplength=430).pack(anchor='w',pady=4)
  initial_folder=str(ROOT/'plantillas')
  try:
   saved=json.loads((ROOT/'datos_locales'/'base18.json').read_text());initial_folder=saved['templates'] if Path(saved['templates']).is_dir() else initial_folder
  except (OSError,ValueError,KeyError,TypeError):pass
  self.templates=tk.StringVar(value=initial_folder);self.output=tk.StringVar(value=str(ROOT/'salidas'))
  for label,var in [('Carpeta de los 18 PDF limpios',self.templates),('Guardar resultados en',self.output)]:
   ttk.Label(docs,text=label).pack(anchor='w');row=ttk.Frame(docs);row.pack(fill='x',pady=(0,9));ttk.Entry(row,textvariable=var).pack(side='left',fill='x',expand=True);ttk.Button(row,text='Elegir',command=lambda v=var:self.pick_folder(v)).pack(side='left')
  self.import_button=ttk.Button(docs,text='Importar SASISOPA.zip',command=self.import_templates);self.import_button.pack(anchor='w',pady=(0,10))
  for meta in self.catalog['templates']:
   v=tk.BooleanVar(value=True);self.selected[meta['id']]=v;ttk.Checkbutton(docs,text=f"{meta['id']}. {meta['title']} ({meta['pages']} páginas)",variable=v).pack(anchor='w')
  self.merge=tk.BooleanVar(value=True);ttk.Checkbutton(docs,text='Crear también un PDF unido',variable=self.merge).pack(anchor='w',pady=8)
  self.doc_selector=tk.StringVar(value=self.catalog['templates'][0]['id']);self.doc_selector.trace_add('write',self.change_document)
  ttk.Label(docs,text='Datos particulares del documento visible').pack(anchor='w',pady=(12,4));self.only_page=tk.BooleanVar(value=True);ttk.Checkbutton(docs,text='Mostrar sólo campos de la página visible',variable=self.only_page,command=self.page_fields).pack(anchor='w');self.doc_fields_box=ttk.Frame(docs);self.doc_fields_box.pack(fill='x')
  ttk.Button(docs,text='Agregar otro dato al documento',command=self.add_custom_field).pack(anchor='w',pady=8)
  ttk.Button(docs,text='Usar datos actuales como predeterminados',command=self.set_defaults).pack(anchor='w',pady=4)
  ttk.Button(docs,text='Quitar valores predeterminados del proyecto',command=self.clear_defaults).pack(anchor='w',pady=4)
  ttk.Label(docs,text='Un campo vacío usa su predeterminado guardado. Si no existe, conserva la plantilla. Puedes editar los textos y resultados de los espacios marcados; el sistema no calcula riesgos ni acredita actividades.',wraplength=430).pack(anchor='w',pady=6)
  ttk.Label(docs,text='Los campos particulares se aplican sólo a este documento. Si no tienen espacio predefinido, selecciónalos en Ubicar campo y marca su espacio en la página.',wraplength=430).pack(anchor='w')
  self.table_selector=tk.StringVar();self.table_combo=ttk.Combobox(tables,textvariable=self.table_selector,state='readonly');self.table_combo.pack(fill='x');self.table_selector.trace_add('write',self.change_table)
  self.table_box=ttk.Frame(tables);self.table_box.pack(fill='x',pady=8)
  # Preview shows the actual PDF; no web view or simulated document.
  toolbar=ttk.Frame(right);toolbar.pack(fill='x',pady=(0,7));ttk.Label(toolbar,text='Documento').pack(side='left');ttk.Combobox(toolbar,textvariable=self.doc_selector,values=[m['id'] for m in self.catalog['templates']],state='readonly',width=7).pack(side='left',padx=5)
  self.page=tk.IntVar(value=1);ttk.Label(toolbar,text='Página').pack(side='left');self.page_spin=ttk.Spinbox(toolbar,from_=1,to=14,textvariable=self.page,width=5,command=self.schedule);self.page_spin.pack(side='left',padx=5);self.page.trace_add('write',self.page_changed)
  self.page_count=ttk.Label(toolbar,text='/ 14');self.page_count.pack(side='left');self.zoom=tk.StringVar(value='100 %');zoom_combo=ttk.Combobox(toolbar,textvariable=self.zoom,values=['50 %','75 %','100 %','125 %','150 %','200 %'],state='readonly',width=7);zoom_combo.pack(side='left',padx=5);zoom_combo.bind('<<ComboboxSelected>>',self.change_zoom);ttk.Button(toolbar,text='Actualizar vista',command=self.update_preview).pack(side='right')
  locator=ttk.Frame(right);locator.pack(fill='x',pady=5);ttk.Label(locator,text='Campo').grid(row=0,column=0);self.field_choice=tk.StringVar();self.field_combo=ttk.Combobox(locator,textvariable=self.field_choice,state='readonly',width=50);self.field_combo.grid(row=0,column=1,sticky='ew',padx=5)
  self.place_mode=tk.BooleanVar();ttk.Checkbutton(locator,text='Ubicar campo',variable=self.place_mode).grid(row=0,column=2)
  self.binding_size=tk.StringVar(value='9');ttk.Label(locator,text='Tamaño').grid(row=1,column=0);ttk.Spinbox(locator,from_=3,to=36,textvariable=self.binding_size,width=5).grid(row=1,column=1,sticky='w',padx=5)
  ttk.Button(locator,text='Quitar ubicación marcada',command=self.remove_binding).grid(row=1,column=2);locator.columnconfigure(1,weight=1)
  ttk.Label(right,text='Para un campo nuevo, elígelo, activa Ubicar campo y arrastra sobre su espacio. Para mover uno existente, selecciónalo en la página y vuelve a marcarlo.',wraplength=800).pack(anchor='w',pady=(0,6))
  area=ttk.Frame(right);area.pack(fill='both',expand=True);self.canvas=tk.Canvas(area,bg='#dce4ec',highlightthickness=0);v=ttk.Scrollbar(area,orient='vertical',command=self.canvas.yview);h=ttk.Scrollbar(area,orient='horizontal',command=self.canvas.xview);v.pack(side='right',fill='y');h.pack(side='bottom',fill='x');self.canvas.pack(fill='both',expand=True);self.canvas.configure(yscrollcommand=v.set,xscrollcommand=h.set)
  self.canvas.bind('<ButtonPress-1>',self.pointer_down);self.canvas.bind('<B1-Motion>',self.pointer_move);self.canvas.bind('<ButtonRelease-1>',self.pointer_up)
  self.show_regions=tk.BooleanVar(value=False);ttk.Checkbutton(right,text='Mostrar espacios editables',variable=self.show_regions,command=self.update_preview).pack(anchor='w')
  footer=ttk.Frame(app);footer.pack(fill='x',padx=15,pady=(0,12));self.status=tk.StringVar(value='Base completa: 18 PDF, 523 páginas.');ttk.Label(footer,textvariable=self.status,wraplength=950).pack(side='left',fill='x',expand=True);self.generate_button=ttk.Button(footer,text='Generar PDF',style='Primary.TButton',command=self.generate);self.generate_button.pack(side='right')
  app.bind_all('<MouseWheel>',self.wheel);app.bind_all('<Button-4>',self.wheel);app.bind_all('<Button-5>',self.wheel)
  self.current_slot=None;self.refresh_people();self.build_shared_fields();self.build_doc_fields();self.refresh_tables();self.refresh_field_choices();self.poll_timer=app.after(100,self.poll);app.protocol('WM_DELETE_WINDOW',self.close);self.schedule()
 def wheel(self,event):
  direction=-1 if getattr(event,'num',0)==4 else 1 if getattr(event,'num',0)==5 else -int(event.delta/120)
  if not direction:return
  if self.app.winfo_pointerx()-self.panes.winfo_rootx()<self.panes.sashpos(0):target=self.tab_canvases.get(self.tabs.select())
  else:target=self.canvas
  if target:target.yview_scroll(direction,'units')
 def tab(self,title):
  outer=ttk.Frame(self.tabs);self.tabs.add(outer,text=title);c=tk.Canvas(outer,highlightthickness=0);self.tab_canvases[str(outer)]=c;s=ttk.Scrollbar(outer,orient='vertical',command=c.yview);s.pack(side='right',fill='y');c.pack(fill='both',expand=True);c.configure(yscrollcommand=s.set);f=ttk.Frame(c,padding=10);w=c.create_window((0,0),window=f,anchor='nw');f.bind('<Configure>',lambda e:c.configure(scrollregion=c.bbox('all')));c.bind('<Configure>',lambda e:c.itemconfigure(w,width=e.width));return f
 def entry(self,parent,label,store,key,value=''):
  row=ttk.Frame(parent);row.pack(fill='x',pady=4);ttk.Label(row,text=label,wraplength=180,width=24).pack(side='left',anchor='n');v=tk.StringVar(value=value);store[key]=v
  v.entry=ttk.Entry(row,textvariable=v);v.entry.pack(side='left',fill='x',expand=True);v.upload=None;v.trace_add('write',self.schedule)
  if key.endswith(('.logo','.firma')):
   v.upload=ttk.Button(row,text='Subir',width=6,command=lambda:self.choose_image(v));v.upload.pack(side='left')
  return v
 def build_installation_tab(self,parent):
  self.installation_enabled=tk.BooleanVar(value=False);self.installation_tanks=[];self.equipment_vars={}
  ttk.Checkbutton(parent,text='Aplicar datos de instalaciones a los documentos',variable=self.installation_enabled,command=self.schedule).pack(anchor='w',pady=5)
  ttk.Label(parent,text='Captura cada tanque o compartimento con su producto real. Los productos sin tanque se marcan como No aplica. Los datos no capturados se indican como Pendiente.',wraplength=430).pack(anchor='w',pady=5)
  self.tank_list=ttk.Treeview(parent,columns=('number','product','capacity'),show='headings',height=5)
  for key,label,width in [('number','TQ',55),('product','Producto',110),('capacity','Litros',100)]:self.tank_list.heading(key,text=label);self.tank_list.column(key,width=width)
  self.tank_list.pack(fill='x');buttons=ttk.Frame(parent);buttons.pack(fill='x',pady=6)
  ttk.Button(buttons,text='Agregar tanque',command=self.add_tank).pack(side='left')
  ttk.Button(buttons,text='Editar',command=self.edit_tank).pack(side='left',padx=4)
  ttk.Button(buttons,text='Quitar',command=self.remove_tank).pack(side='left')
  ttk.Button(parent,text='Cargar ejemplo ficticio',command=self.example_installation).pack(anchor='w',pady=5)
  ttk.Label(parent,text='Equipos por producto. Un dispensario multiproducto puede contarse en más de un producto; no se suman como equipos únicos.',wraplength=430).pack(anchor='w',pady=5)
  for product in instalaciones.PRODUCTS:
   for field,label in [('dispensarios','Dispensarios'),('mangueras','Mangueras')]:self.entry(parent,product+' — '+label,self.equipment_vars,product+'.'+field)
  ttk.Label(parent,text='Se actualizan las tablas, almacenamiento, despacho y nodos de II y XIII. Se agrega una ficha con todos los tanques; las hojas originales mantienen sus tres filas. La valoración de riesgos HAZOP requiere revisión técnica.',wraplength=430).pack(anchor='w',pady=8)
 def refresh_tanks(self):
  self.tank_list.delete(*self.tank_list.get_children())
  for i,t in enumerate(self.installation_tanks):self.tank_list.insert('','end',iid=str(i),values=(t.get('numero',''),t.get('producto',''),t.get('litros','')))
 def add_tank(self):self.tank_dialog()
 def edit_tank(self):
  selected=self.tank_list.selection()
  if selected:self.tank_dialog(int(selected[0]))
 def tank_dialog(self,index=None):
  window=tk.Toplevel(self.app);window.title('Tanque / compartimento');window.transient(self.app);window.geometry('620x650')
  body=ttk.Frame(window,padding=10);body.pack(fill='both',expand=True);values={};tank=self.installation_tanks[index] if index is not None else {}
  for key,label in instalaciones.TANK_FIELDS:
   if key=='producto':
    row=ttk.Frame(body);row.pack(fill='x',pady=4);ttk.Label(row,text=label,width=24).pack(side='left');v=tk.StringVar(value=tank.get(key,''));values[key]=v;ttk.Combobox(row,textvariable=v,values=instalaciones.PRODUCTS,state='readonly').pack(side='left',fill='x',expand=True)
   else:self.entry(body,label,values,key,tank.get(key,''))
  def save():
   record={k:v.get().strip() for k,v in values.items()};rows=copy.deepcopy(self.installation_tanks)
   if index is None:rows.append(record)
   else:rows[index]=record
   candidate=copy.deepcopy(self.data);candidate['installation']={'enabled':True,'tanks':rows,'equipment':{}}
   try:instalaciones.validate(valores_predeterminados.effective(candidate))
   except ValueError as exc:messagebox.showerror('Revisa el tanque',str(exc),parent=window);return
   self.installation_tanks=rows;self.installation_enabled.set(True);self.refresh_tanks();window.destroy();self.schedule()
  ttk.Button(body,text='Guardar tanque',command=save).pack(anchor='e',pady=10)
 def remove_tank(self):
  selected=self.tank_list.selection()
  if selected:self.installation_tanks.pop(int(selected[0]));self.refresh_tanks();self.schedule()
 def example_installation(self):
  self.installation_tanks=[{'numero':str(i),'producto':p,'litros':c,'marca':'MARCA EJEMPLO','confinamiento':'Subterráneo','pared':'Doble pared','cupula':'No tiene','presion_vapor':'1 atm','temperatura_almacen':'Ambiente','presion_operacion':'2.45 kg/cm2','temperatura_operacion':'30 °C','flujo':'30 L/min','plano':'PLANO DEMO'} for i,p,c in [(1,'Magna','60000'),(2,'Diésel','40000'),(3,'Premium','40000')]]
  for key,var in self.equipment_vars.items():var.set('2' if key.endswith('dispensarios') else '4')
  self.installation_enabled.set(True);self.refresh_tanks();self.schedule()
 def installation_capture(self):
  return {'enabled':self.installation_enabled.get(),'tanks':copy.deepcopy(self.installation_tanks),'equipment':{p:{k:self.equipment_vars[p+'.'+k].get().strip() for k in ('dispensarios','mangueras')} for p in instalaciones.PRODUCTS}}
 def installation_load(self,data):
  inv=data.get('installation') or {};self.installation_tanks=copy.deepcopy(inv.get('tanks',[]));self.installation_enabled.set(inv.get('enabled',False))
  for key,var in self.equipment_vars.items():
   product,field=key.split('.');var.set(inv.get('equipment',{}).get(product,{}).get(field,''))
  self.refresh_tanks()
 def change_zoom(self,event=None):
  self.scale=int(self.zoom.get().split()[0])/100;self.schedule()
 def pick_folder(self,var):
  p=filedialog.askdirectory()
  if p:var.set(p);self.schedule()
 def choose_image(self,var):
  p=filedialog.askopenfilename(filetypes=[('Imágenes','*.png *.jpg *.jpeg')])
  if p:
   try:validated_image(p,'la imagen');var.set(p)
   except ValueError as exc:messagebox.showerror('Imagen inválida',str(exc))
 def refresh_people(self):
  self.people_list.delete(*self.people_list.get_children())
  self.choice_to_id={f"{i+1}. {p.get('nombre','')}":p['id'] for i,p in enumerate(self.data['people'])};self.id_to_choice={id:label for label,id in self.choice_to_id.items()};choices=['']+list(self.choice_to_id)
  for p in self.data['people']:self.people_list.insert('', 'end',iid=p['id'],values=(p.get('nombre',''),p.get('puesto','')))
  for role,var in self.role_vars.items():
   var.combo.configure(values=choices);id=self.data['roles'].get(role,'');var.set(self.id_to_choice.get(id,''))
 def add_person(self):self.person_dialog()
 def edit_person(self):
  selected=self.people_list.selection()
  if selected:self.person_dialog(next(p for p in self.data['people'] if p['id']==selected[0]))
 def person_dialog(self,person=None):
  win=tk.Toplevel(self.app);win.title('Datos de persona');win.geometry('720x650');win.transient(self.app);box=ttk.Frame(win,padding=15);box.pack(fill='both',expand=True);variables={}
  specs=[s for s in self.inventory['fields'] if s['scope']=='persona']
  for spec in specs:self.entry(box,spec['label'],variables,spec['id'].split('.')[1],(person or {}).get(spec['id'].split('.')[1],''))
  variables['iniciales'].entry.configure(state='readonly')
  def update_initials(*args):variables['iniciales'].set(equipo_hazop.initials(variables['nombre'].get()))
  variables['nombre'].trace_add('write',update_initials);update_initials()
  # Personal record fields can be bound to its existing form just like other data.
  ttk.Label(box,text='CURP, RFC, NSS, estudios y otros datos particulares se agregan en Documentos y se ubican en su ficha.',wraplength=620).pack(anchor='w',pady=8)
  sig=variables['firma'];row=ttk.Frame(box);row.pack(fill='x');ttk.Button(row,text='Subir firma',command=lambda:self.choose_image(sig)).pack(side='left');ttk.Button(row,text='Dibujar firma',command=lambda:signature_dialog(win,sig.set)).pack(side='left',padx=5);ttk.Button(row,text='Quitar firma',command=lambda:sig.set('')).pack(side='left')
  def accept():
   values={k:v.get().strip() for k,v in variables.items()}
   if not values['nombre']:messagebox.showerror('Nombre','Captura el nombre completo.',parent=win);return
   if values['firma']:
    try:validated_image(values['firma'],'la firma')
    except ValueError as exc:messagebox.showerror('Firma',str(exc),parent=win);return
   self.capture();values['id']=(person or {}).get('id','P'+uuid.uuid4().hex[:10])
   if person:self.data['people']=[values if p['id']==person['id'] else p for p in self.data['people']]
   else:self.data['people'].append(values)
   win.destroy();self.refresh_people();self.change_table();self.schedule()
  ttk.Button(box,text='Guardar persona',style='Primary.TButton',command=accept).pack(anchor='e',pady=15)
 def delete_person(self):
  ids=set(self.people_list.selection())
  if not ids:return
  self.capture();deleted_rows={row for row,id in self.data.get('table_people',{}).items() if id in ids}
  for key in list(self.data['tables']):
   if key.rsplit('.',1)[0] in deleted_rows:self.data['tables'].pop(key)
  for key,var in self.table_vars.items():
   if key.rsplit('.',1)[0] in deleted_rows:var.set('')
  self.data['table_people']={row:id for row,id in self.data.get('table_people',{}).items() if id not in ids};self.data['people']=[p for p in self.data['people'] if p['id'] not in ids];self.data['roles']={r:id for r,id in self.data['roles'].items() if id not in ids};self.refresh_people();self.change_table();self.schedule()
 def capture(self):
  self.data['installation']=self.installation_capture()
  self.data['values'].update({k:v.get().strip() for k,v in self.vars.items()})
  self.data['roles']={k:self.choice_to_id.get(v.get(),'') for k,v in self.role_vars.items() if v.get()}
  id=getattr(self,'fields_document',None)
  if id:
   current=self.data['documents'].setdefault(id,{})
   current.update({k:v.get().strip() for k,v in self.doc_vars.items()})
  self.data['tables'].update({k:v.get().strip() for k,v in self.table_vars.items() if not self.data.get('table_people',{}).get(k.rsplit('.',1)[0])})
  return copy.deepcopy(self.data)
 def build_doc_fields(self):
  for w in self.doc_fields_box.winfo_children():w.destroy()
  self.doc_vars={};id=self.doc_selector.get();self.fields_document=id;values=self.data['documents'].get(id,{})
  defaults=[(s['id'],s['label']) for s in self.inventory['fields'] if s['scope']=='documento_o_evento']
  default_ids={key for key,_ in defaults}
  baseline=(self.data.get('defaults') or {}).get('documents',{}).get(id,{})
  custom={b['key']:b for b in self.data['bindings'] if b['doc']==id and b['key'].startswith('dato.') and b.get('editable',not b['id'].startswith('TENEX.')) and not b.get('shared')}
  keys=dict.fromkeys([*values,*baseline,*custom])
  hidden={b['key'] for b in self.data['bindings'] if b['doc']==id and b['key'].startswith('dato.') and b['key'] not in custom}
  if self.only_page.get():
   try:page=int(self.page.get())-1
   except (AttributeError,tk.TclError,ValueError):page=0
   visible={b['key'] for b in self.data['bindings'] if b['doc']==id and b['page']==page}
   hidden.update(key for key in custom if key not in visible)
  defaults += [(k,custom.get(k,{}).get('label',k.split('.',1)[-1])) for k in keys if k not in default_ids and k not in hidden]
  for key,label in defaults:
   if key in custom and custom[key].get('multiline'):
    self.text_entry(self.doc_fields_box,label,self.doc_vars,key,values.get(key,''))
   else:self.entry(self.doc_fields_box,label,self.doc_vars,key,values.get(key,''))
   baseline_text=baseline.get(key,'') or custom.get(key,{}).get('default_text','')
   if baseline_text:ttk.Label(self.doc_fields_box,text='Si queda vacío: '+baseline_text.replace('\n',' ')[:180],wraplength=430,foreground='#55616b').pack(anchor='w')
 def build_shared_fields(self):
  for widget in self.shared_box.winfo_children():widget.destroy()
  for key in self.shared_keys:self.vars.pop(key,None)
  fields={b['key']:b for b in self.data['bindings'] if b.get('shared')}
  labels={s['id']:s['label'] for s in self.inventory['fields']}
  labels['dato.fecha_actual_operativa']='Fecha general de registros (dd/mm/aaaa)'
  for key in self.data['values']:
   if key not in self.vars and key not in fields:fields[key]={'label':labels.get(key,key.split('.',1)[-1])}
  self.shared_keys=set(fields)
  ttk.Label(self.shared_box,text='Un dato común se actualiza en todos sus espacios vinculados. Vacío usa el predeterminado del proyecto.',wraplength=430).pack(anchor='w',pady=6)
  for key,b in fields.items():
   label=b.get('label',key)
   if b.get('multiline'):self.text_entry(self.shared_box,label,self.vars,key,self.data['values'].get(key,''))
   else:self.entry(self.shared_box,label,self.vars,key,self.data['values'].get(key,''))
 def page_fields(self):
  self.capture();self.build_doc_fields();self.refresh_field_choices()
 def page_changed(self,*args):
  try:
   if hasattr(self,'doc_fields_box') and hasattr(self,'page') and self.only_page.get():
    int(self.page.get());self.page_fields()
  except (tk.TclError,ValueError):pass
  self.schedule()
 def text_entry(self,parent,label,store,key,value=''):
  ttk.Label(parent,text=label,wraplength=430).pack(anchor='w',pady=(8,2))
  variable=tk.StringVar(value=value);store[key]=variable
  box=tk.Text(parent,height=5,wrap='word',font=('Segoe UI',10));box.pack(fill='x');box.insert('1.0',value)
  def changed(event=None):
   if box.edit_modified():variable.set(box.get('1.0','end-1c'));box.edit_modified(False)
  box.bind('<<Modified>>',changed);box.edit_modified(False);variable.trace_add('write',self.schedule)
 def set_defaults(self):
  data=self.capture()
  try:engine.validate_project(valores_predeterminados.effective(data))
  except ValueError as exc:messagebox.showerror('Revisa los datos',str(exc));return
  self.data['defaults']=valores_predeterminados.snapshot(valores_predeterminados.effective(data))
  self.status.set('Predeterminados guardados en el proyecto. Vacío usa estos datos; no acredita validación técnica.');self.schedule()
 def clear_defaults(self):
  self.data.pop('defaults',None);self.status.set('Predeterminados retirados. Los campos vacíos conservan la plantilla.');self.schedule()
 def add_custom_field(self):
  from tkinter.simpledialog import askstring
  label=askstring('Agregar dato','Nombre del dato, por ejemplo CURP o fecha del incidente:',parent=self.app)
  if not label:return
  self.capture();id=self.doc_selector.get();key='dato.'+label.strip()
  self.data['documents'].setdefault(id,{})[key]='';self.build_doc_fields();self.refresh_field_choices();self.status.set('Selecciona el nuevo dato en Campo y marca su espacio con Ubicar campo.')
 def change_document(self,*args):
  if not hasattr(self,'page'):return
  self.capture();id=self.doc_selector.get();count=next(m['pages'] for m in self.catalog['templates'] if m['id']==id)+instalaciones.extra_pages(self.data,id);self.page_spin.configure(to=count);self.page.set(1);self.page_count.configure(text='/ '+str(count));self.build_doc_fields();self.refresh_tables();self.refresh_field_choices();self.current_slot=None;self.schedule()
 def refresh_tables(self):
  self.table_labels={}
  for i,p in enumerate(self.maps[self.doc_selector.get()]['pages']):
   for table in p['tables']:self.table_labels[f"Página {i+1} · lista {table['id']} · {table['rows']} filas"]=table
  self.table_combo.configure(values=list(self.table_labels));self.table_selector.set(next(iter(self.table_labels),''))
 def change_table(self,*args):
  self.data['tables'].update({k:v.get().strip() for k,v in self.table_vars.items() if not self.data.get('table_people',{}).get(k.rsplit('.',1)[0])});self.table_vars={}
  for w in self.table_box.winfo_children():w.destroy()
  table=getattr(self,'table_labels',{}).get(self.table_selector.get())
  if not table:return
  ttk.Label(self.table_box,text='Esta lista se entrega vacía para llenarla manualmente.\nNo se insertan nombres, puestos, teléfonos ni firmas.\nSe conservan los encabezados y las filas originales.',wraplength=340).pack(anchor='w',padx=8,pady=12)
 def refresh_field_choices(self):
  fields={s['label']:s['id'] for s in self.inventory['fields'] if s['scope']!='persona'}
  for role in self.inventory['roles']:
   for spec in self.inventory['fields']:
    if spec['scope']=='persona':fields[role['label']+' · '+spec['label']]='rol.'+role['id']+'.'+spec['id'].split('.')[1]
  fields.update({k:k for k in self.data['documents'].get(self.doc_selector.get(),{})})
  fields.update({b.get('label',b['key']):b['key'] for b in self.data['bindings'] if b['doc']==self.doc_selector.get() and b['key'].startswith('dato.') and b.get('editable',not b['id'].startswith('TENEX.')) and not b.get('shared')})
  self.field_keys=fields;self.field_combo.configure(values=list(fields))
  if self.field_choice.get() not in fields:self.field_choice.set(next(iter(fields),''))
 def schedule(self,*args):
  if not hasattr(self,'status') or self.busy or self.closed:return
  if self.timer:self.app.after_cancel(self.timer)
  self.timer=self.app.after(650,self.scheduled_preview)
 def scheduled_preview(self):
  self.timer=None;self.update_preview()
 def update_preview(self):
  if self.timer:
   try:self.app.after_cancel(self.timer)
   except tk.TclError:pass
  self.timer=None
  if self.busy:return
  try:
   id=self.doc_selector.get();data=self.capture();count=next(m['pages'] for m in self.catalog['templates'] if m['id']==id)+instalaciones.extra_pages(data,id);self.page_spin.configure(to=count);self.page_count.configure(text='/ '+str(count));index=min(int(self.page.get())-1,count-1)
   if index!=int(self.page.get())-1:self.page.set(index+1)
   blob,notes,warnings=engine.preview(self.templates.get(),data,id,index,self.scale)
   im=Image.open(io.BytesIO(blob));self.photo=ImageTk.PhotoImage(im);self.canvas.delete('all');self.canvas.create_image(0,0,image=self.photo,anchor='nw');self.canvas.configure(scrollregion=(0,0,im.width,im.height));self.current_slot=None
   if self.show_regions.get() and index<len(self.maps[id]['pages']):
    for slot in engine.slots_for(self.maps[id],data,id,index):self.canvas.create_rectangle(*[x*self.scale for x in slot['rect']],outline='#008c86',dash=(3,2))
   detail=next((n for n in notes if n['field']=='estacion.direccion'),None)
   destination_note=''
   try:engine.check_destinations(data,self.maps,[id])
   except ValueError as err:destination_note=str(err)
   self.preview_page=(id,index)
   self.status.set(destination_note or ('Dirección: '+str(detail['lines'])+' líneas · '+str(detail['size'])+' pt. ' if detail else 'Vista del PDF real. ')+(' '.join(warnings) if warnings else ''))
  except Exception as exc:
   error=str(exc)
   try:
    id=self.doc_selector.get();index=int(self.page.get())-1
    blob,_,_=engine.preview(self.templates.get(),engine.empty_project(),id,index,self.scale)
    im=Image.open(io.BytesIO(blob));self.photo=ImageTk.PhotoImage(im);self.canvas.delete('all');self.canvas.create_image(0,0,image=self.photo,anchor='nw');self.canvas.configure(scrollregion=(0,0,im.width,im.height));self.preview_page=(id,index);self.current_slot=None
    for slot in engine.slots_for(self.maps[id],self.capture(),id,index):self.canvas.create_rectangle(*[v*self.scale for v in slot['rect']],outline='#d99b22',dash=(3,2))
    self.status.set(error+' Se muestra la base para ajustar el espacio o corregir el dato.')
   except Exception:
    self.status.set(error);self.canvas.delete('all');self.photo=None

 def pointer_down(self,event):
  if self.busy or self.photo is None:return
  if getattr(self,'preview_page',('',-1))[1]>=len(self.maps[self.doc_selector.get()]['pages']):
   self.status.set('Edita los datos de esta ficha en la pestaña Instalaciones.');return
  try:
   if self.preview_page!=(self.doc_selector.get(),int(self.page.get())-1):return
  except (ValueError,tk.TclError,AttributeError):return
  x=self.canvas.canvasx(event.x);y=self.canvas.canvasy(event.y)
  if self.place_mode.get():self.drag=(x,y);self.rect_item=self.canvas.create_rectangle(x,y,x,y,outline='#e29b21',width=2);return
  data=self.capture();index=int(self.page.get())-1;point=fitz.Point(x/self.scale,y/self.scale);slots=engine.slots_for(self.maps[self.doc_selector.get()],data,self.doc_selector.get(),index)
  found=next((s for s in reversed(slots) if fitz.Rect(s['rect']).contains(point)),None)
  self.current_slot=found
  if found and found.get('locked'):
   self.status.set('Esta firma se ajusta al espacio interior del cuadro; su posición se conserva.');return
  if found:
   label=next((label for label,key in self.field_keys.items() if key==found['key']),None)
   if label:self.field_choice.set(label)
   self.binding_size.set(str(found.get('size',9)));self.status.set('Seleccionado: '+found['key']+'. Activa Ubicar campo para mover su espacio.')
 def pointer_move(self,event):
  if self.drag and self.rect_item:self.canvas.coords(self.rect_item,*self.drag,self.canvas.canvasx(event.x),self.canvas.canvasy(event.y))
 def pointer_up(self,event):
  if not self.drag:return
  x,y=self.drag;self.drag=None;u=self.canvas.canvasx(event.x);v=self.canvas.canvasy(event.y)
  try:
   if self.current_slot and self.current_slot.get('locked'):raise ValueError('La firma debe permanecer dentro del cuadro original.')
   key=self.field_keys[self.field_choice.get()];rect=[min(x,u)/self.scale,min(y,v)/self.scale,max(x,u)/self.scale,max(y,v)/self.scale];size=float(self.binding_size.get());kind='image' if key.endswith(('.logo','.firma')) else 'text'
   binding={'id':'B'+uuid.uuid4().hex,'doc':self.doc_selector.get(),'page':int(self.page.get())-1,'key':key,'rect':rect,'font':'Arial-BoldMT' if key=='estacion.razon_social' else 'ArialMT','size':size,'min_size':8 if key=='estacion.direccion' and size>=8 else size,'align':2 if key in ('estacion.direccion','estacion.razon_social') else 0,'valign':'top' if key in ('estacion.direccion','estacion.razon_social') else 'middle','kind':kind,'clear':kind!='image' or key.endswith('.logo')}
   replaced_custom=None
   if self.current_slot:
    old=self.current_slot
    for inherited in ('font','align','valign'):
     if inherited in old:binding[inherited]=old[inherited]
    if old['key']==key:
     for inherited in ('transform','flow','flow_order'):
      if inherited in old:binding[inherited]=old[inherited]
    if old['id'].startswith('B'):
     replaced_custom=old['id']
     if old.get('replace_id'):binding['replace_id']=old['replace_id']
    else:binding['replace_id']=old['id']
   candidate=self.capture()
   if replaced_custom:candidate['bindings']=[b for b in candidate['bindings'] if b['id']!=replaced_custom]
   candidate['bindings'].append(binding);engine.validate_project(candidate);self.data=candidate;self.place_mode.set(False);self.current_slot=None;self.update_preview()
  except Exception as exc:messagebox.showerror('Ubicación inválida',str(exc));self.update_preview()
 def remove_binding(self):
  if self.current_slot and self.current_slot['id'].startswith('B'):
   self.data['bindings']=[b for b in self.data['bindings'] if b['id']!=self.current_slot['id']];self.current_slot=None;self.update_preview()
  else:self.status.set('Haz clic en un espacio personalizado para quitarlo. Los espacios originales se conservan.')
 def save(self):
  path=filedialog.asksaveasfilename(defaultextension='.sasisopa18.json',filetypes=[('Datos SASISOPA 18','*.sasisopa18.json')])
  if path:
   try:engine.save_project(path,self.capture());self.status.set('Datos y ubicaciones guardados. Conserva las imágenes en sus rutas actuales.')
   except Exception as exc:messagebox.showerror('No se guardó',str(exc))
 def load(self):
  path=filedialog.askopenfilename(filetypes=[('Datos SASISOPA 18','*.sasisopa18.json')])
  if not path:return
  try:data=engine.load_project(path)
  except Exception as exc:messagebox.showerror('No se cargó',str(exc));return
  self.data=data;self.build_shared_fields();self.installation_load(data)
  for key,v in self.vars.items():v.set(data['values'].get(key,''))
  self.refresh_people();self.build_doc_fields();self.refresh_tables();self.refresh_field_choices();self.schedule()
 def import_requirements(self):
  if self.busy:return
  path=filedialog.askopenfilename(title='Importar requisitos de estación',filetypes=[('Word (.docx)','*.docx')])
  if not path:return
  try:proposals,warnings=importar_requisitos.read_candidates(path)
  except Exception as exc:messagebox.showerror('No se pudo importar',str(exc));return
  current=self.capture()
  win=tk.Toplevel(self.app);win.title('Revisar datos del Word');win.geometry('1000x720');win.transient(self.app);win.grab_set()
  ttk.Label(win,text='Revisa y corrige cada propuesta. Los valores existentes distintos quedan desmarcados. Solo se aplican las filas marcadas.',wraplength=950).pack(anchor='w',padx=12,pady=8)
  ttk.Label(win,text='\n'.join(warnings),wraplength=950).pack(anchor='w',padx=12,pady=5)
  area=ttk.Frame(win);area.pack(fill='both',expand=True,padx=12)
  canvas=tk.Canvas(area,highlightthickness=0);scroll=ttk.Scrollbar(area,orient='vertical',command=canvas.yview);canvas.configure(yscrollcommand=scroll.set);scroll.pack(side='right',fill='y');canvas.pack(side='left',fill='both',expand=True)
  rows=ttk.Frame(canvas);item=canvas.create_window((0,0),window=rows,anchor='nw');rows.bind('<Configure>',lambda event:canvas.configure(scrollregion=canvas.bbox('all')));canvas.bind('<Configure>',lambda event:canvas.itemconfigure(item,width=event.width))
  fields=[]
  for proposal in proposals:
   key=proposal['key'];old=importar_requisitos.current_value(valores_predeterminados.effective(current),key);selected=tk.BooleanVar(value=not old or old==proposal['value']);value=tk.StringVar(value=proposal['value'])
   row=ttk.LabelFrame(rows,text=proposal['label']);row.pack(fill='x',pady=4)
   ttk.Checkbutton(row,text='Aplicar',variable=selected).grid(row=0,column=0,padx=5)
   ttk.Entry(row,textvariable=value,width=70).grid(row=0,column=1,sticky='ew',padx=5,pady=4);row.columnconfigure(1,weight=1)
   ttk.Label(row,text='Actual: '+(old or '(vacío)'),wraplength=850).grid(row=1,column=1,sticky='w',padx=5)
   ttk.Label(row,text='Word: '+proposal['evidence'],wraplength=850).grid(row=2,column=1,sticky='w',padx=5,pady=(0,5))
   fields.append((key,selected,value))
  buttons=ttk.Frame(win);buttons.pack(fill='x',padx=12,pady=10)
  def apply():
   selected={key:value.get() for key,checked,value in fields if checked.get()}
   if not selected:messagebox.showinfo('Sin cambios','Selecciona al menos un campo.',parent=win);return
   try:data=importar_requisitos.apply_candidates(current,selected)
   except Exception as exc:messagebox.showerror('Revisa los datos',str(exc)+'\nLos tanques nuevos requieren número, producto y capacidad. No se aplicó ningún cambio.',parent=win);return
   self.data=data;self.build_shared_fields();self.installation_load(data)
   for key,var in self.vars.items():var.set(data['values'].get(key,''))
   self.refresh_people();self.build_doc_fields();self.refresh_tables();self.refresh_field_choices();self.schedule()
   self.status.set(f'Word importado: {len(selected)} campos aplicados. Revisa la vista previa y guarda el proyecto.');win.destroy()
  ttk.Button(buttons,text='Cancelar',command=win.destroy).pack(side='right',padx=5)
  ttk.Button(buttons,text='Aplicar seleccionados',command=apply).pack(side='right')
 def import_templates(self):
  if self.busy:return
  path=filedialog.askopenfilename(title='Importar tu ZIP original o limpio',filetypes=[('Archivo ZIP','*.zip')])
  if not path:return
  parent=ROOT/'plantillas';self.busy=True;self.generate_button.configure(state='disabled');self.import_button.configure(state='disabled');self.status.set('Preparando los 18 PDF limpios. El ZIP original se conserva…')
  def work():
   try:folder=import_zip(path,parent);self.messages.put(('import',str(folder)))
   except Exception as exc:self.messages.put(('error',str(exc)))
  threading.Thread(target=work,daemon=False).start()
 def generate(self):
  if self.busy:return
  try:
   data=valores_predeterminados.effective(self.capture());engine.validate_project(data);selected=[id for id,v in self.selected.items() if v.get()]
   if not selected:raise ValueError('Selecciona al menos un documento.')
   engine.check_destinations(data,self.maps,selected)
   if not self.output.get().strip() or not self.templates.get().strip():raise ValueError('Selecciona las carpetas de plantillas y salida.')
  except Exception as exc:messagebox.showerror('Revisa los datos',str(exc));return
  out=Path(self.output.get())/datetime.now().strftime('%Y%m%d_%H%M%S_%f');templates=self.templates.get();merge=self.merge.get();self.busy=True;self.generate_button.configure(state='disabled');self.import_button.configure(state='disabled');self.status.set('Generando copias. Los originales se conservan…')
  def work():
   try:paths,warnings=engine.generate(templates,out,data,selected,merge);self.messages.put(('success',f'{len(paths)} PDF guardados en:\n{out}\n\nRevisa las copias antes de utilizarlas.\n'+'\n'.join(warnings)))
   except Exception as exc:self.messages.put(('error',str(exc)))
  threading.Thread(target=work,daemon=False).start()
 def poll(self):
  if self.closed:return
  try:
   while True:
    kind,message=self.messages.get_nowait();self.busy=False;self.generate_button.configure(state='normal');self.import_button.configure(state='normal')
    if kind=='import':
     self.templates.set(message);local=ROOT/'datos_locales';local.mkdir(exist_ok=True)
     try:(local/'base18.json').write_text(json.dumps({'templates':message}),encoding='utf-8')
     except OSError:pass
     self.status.set('Base limpia importada: 18 PDF, 523 páginas.');self.schedule();messagebox.showinfo('Base preparada','Los 18 documentos están listos para capturar datos. Los originales se conservaron.')
    else:
     self.status.set('Lote generado.' if kind=='success' else 'No se completó la operación.')
     (messagebox.showinfo if kind=='success' else messagebox.showerror)('Resultado',message)
  except queue.Empty:pass
  if not self.closed:self.poll_timer=self.app.after(100,self.poll)
 def close(self):
  if self.busy:messagebox.showinfo('Generación en curso','Espera a que termine el lote antes de cerrar.')
  else:
   self.closed=True
   for timer in (self.timer,getattr(self,'poll_timer',None)):
    if timer:
     try:self.app.after_cancel(timer)
     except tk.TclError:pass
   self.app.destroy()


def main():
 app=tk.Tk();Editor(app);app.mainloop()

if __name__=='__main__':main()
