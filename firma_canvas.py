"""Captura de una firma dibujada como PNG; no captura la pantalla."""
from PIL import Image,ImageDraw,ImageOps,ImageChops

INK_BLUE=(20,55,165)


def blue_signature(path):
    """Remove white paper, preserve stroke opacity, and fit only the ink bounds."""
    with Image.open(path) as source:
        rgba=source.convert('RGBA')
    darkness=ImageOps.invert(ImageOps.grayscale(rgba))
    # Suppress near-white paper and compression noise while keeping antialiasing.
    alpha=darkness.point(lambda v:0 if v<28 else min(255,round((v-28)*255/190)))
    alpha=ImageChops.multiply(alpha,rgba.getchannel('A'))
    bounds=alpha.getbbox()
    if bounds is None:raise ValueError('La imagen de firma está vacía; selecciona una imagen con trazos visibles.')
    ink=Image.new('RGBA',rgba.size,INK_BLUE+(255,));ink.putalpha(alpha)
    return ink.crop(bounds)


def signature_png(strokes,width=600,height=200):
    if not strokes or not any(len(s)>=2 for s in strokes):
        raise ValueError('Dibuja la firma antes de guardarla.')
    scale=3
    image=Image.new('RGBA',(width*scale,height*scale),(255,255,255,0))
    draw=ImageDraw.Draw(image)
    for stroke in strokes:
        if len(stroke)<2:continue
        points=[]
        for x,y in stroke:
            if not (0<=x<width and 0<=y<height):raise ValueError('La firma contiene puntos fuera del área de dibujo.')
            points.append((x*scale,y*scale))
        draw.line(points,fill=INK_BLUE+(255,),width=3*scale,joint='curve')
    return image.resize((width,height),Image.Resampling.LANCZOS)


def signature_dialog(parent,on_saved):
    import tkinter as tk
    from tkinter import ttk,filedialog,messagebox
    dialog=tk.Toplevel(parent);dialog.title('Dibujar firma');dialog.transient(parent);dialog.grab_set()
    dialog.configure(background='white')
    dialog.resizable(False,False)
    ttk.Label(dialog,text='Dibuja tu firma con el mouse. Se guardará en tinta azul con fondo transparente.').pack(padx=12,pady=8)
    canvas=tk.Canvas(dialog,width=600,height=200,bg='white',cursor='crosshair',highlightthickness=1)
    canvas.pack(padx=12,pady=8)
    strokes=[];active=None
    def start(event):
        nonlocal active
        active=[(max(0,min(599,event.x)),max(0,min(199,event.y)))];strokes.append(active)
    def move(event):
        if active is None:return
        point=(max(0,min(599,event.x)),max(0,min(199,event.y)))
        canvas.create_line(*active[-1],*point,fill='#1437a5',width=3,capstyle='round',smooth=True)
        active.append(point)
    def stop(event):
        nonlocal active
        active=None
    canvas.bind('<Button-1>',start);canvas.bind('<B1-Motion>',move);canvas.bind('<ButtonRelease-1>',stop)
    def clear():
        nonlocal active
        canvas.delete('all');strokes.clear();active=None
    def save():
        try:image=signature_png(strokes)
        except ValueError as exc:messagebox.showerror('Firma vacía',str(exc),parent=dialog);return
        path=filedialog.asksaveasfilename(parent=dialog,title='Guardar firma PNG',defaultextension='.png',filetypes=[('PNG','*.png')])
        if not path:return
        try:image.save(path,format='PNG')
        except OSError as exc:messagebox.showerror('No se pudo guardar',str(exc),parent=dialog);return
        on_saved(path);dialog.destroy()
    row=ttk.Frame(dialog);row.pack(pady=10)
    ttk.Button(row,text='Borrar',command=clear).pack(side='left',padx=5)
    ttk.Button(row,text='Guardar y usar',style='Primary.TButton',command=save).pack(side='left',padx=5)
    ttk.Button(row,text='Cancelar',command=dialog.destroy).pack(side='left',padx=5)
    return dialog
