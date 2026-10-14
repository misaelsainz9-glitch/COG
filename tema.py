"""Tema compartido para el formulario y el cuadro de firmas."""
from tkinter import ttk

NAVY='#12324e'
TEAL='#008591'
BG='#eef3f8'
TEXT='#20384e'


def configure_theme(root):
    root.configure(background=BG)
    style=ttk.Style(root)
    style.theme_use('clam')
    style.configure('.',font=('Segoe UI',10),foreground=TEXT)
    style.configure('TFrame',background='white')
    style.configure('Page.TFrame',background=BG)
    style.configure('TLabel',background='white',foreground=TEXT)
    style.configure('Muted.TLabel',foreground='#62788a',background='white',font=('Segoe UI',9))
    style.configure('Section.TLabel',foreground=TEAL,font=('Segoe UI',15,'bold'),background='white')
    style.configure('TableHeader.TLabel',background='#e5eef6',font=('Segoe UI',10,'bold'),padding=8)
    style.configure('TEntry',padding=7,fieldbackground='white',bordercolor='#c5d2df')
    style.configure('TCombobox',padding=5,fieldbackground='white')
    style.configure('TButton',padding=(10,7),background='#edf3f8',foreground=TEXT,bordercolor='#c5d2df')
    style.map('TButton',background=[('active','#dfeaf3'),('disabled','#eef1f4')])
    style.configure('Primary.TButton',padding=(22,12),background=TEAL,foreground='white',font=('Segoe UI',11,'bold'),borderwidth=0)
    style.map('Primary.TButton',background=[('disabled','#91acb3'),('active','#006f79')],foreground=[('disabled','#f2f5f7')])
    style.configure('TCheckbutton',background='white',padding=6)
    style.map('TCheckbutton',background=[('active','white')])
    return style
