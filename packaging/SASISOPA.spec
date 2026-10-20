# Only code and public maps are bundled. Never collect a user's working folders.
from pathlib import Path
repo = Path(SPECPATH).parent
resources = ['catalogo18.json', 'catalogo_activo.json', 'campos_sasisopa_18.json',
             'mapas_sasisopa18.json', 'plantilla_nueva.json', 'limpieza18.json', 'LEEME.txt']
a = Analysis([str(repo / 'lanzamiento.py')], pathex=[str(repo)],
             binaries=[], datas=[(str(repo / name), '.') for name in resources]+[(str(repo/'assets'/'logo-pemex.png'),'assets')],
             hiddenimports=[], hookspath=[], hooksconfig={}, runtime_hooks=[],
             excludes=['pytest', 'IPython', 'matplotlib', 'numpy', 'pandas'], noarchive=False)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name='SASISOPA',
          debug=False, bootloader_ignore_signals=False, strip=False, upx=False, console=False)
diagnostic = EXE(pyz, a.scripts, [], exclude_binaries=True, name='SASISOPA-Verificar',
                 debug=True, bootloader_ignore_signals=False, strip=False, upx=False, console=True)
coll = COLLECT(exe, diagnostic, a.binaries, a.datas, strip=False, upx=False, name='SASISOPA')
