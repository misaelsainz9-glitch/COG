"""Windowed executable entry point, with an unattended packaging smoke check."""
import json
from pathlib import Path
import sys
import traceback
from rutas_app import user_root


def run():
    if len(sys.argv) == 3 and sys.argv[1] == '--smoke-test':
        report = Path(sys.argv[2])
        try:
            report.write_text('Iniciando comprobación', encoding='utf-8')
            from comprobacion_instalacion import check_installation
            def progress(stage):
                report.write_text(json.dumps({'stage': stage}), encoding='utf-8')
            result = check_installation(progress)
            report.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
            return 0
        except Exception:
            report.write_text(traceback.format_exc(), encoding='utf-8')
            return 1
    from editor_sasisopa import main
    main()
    return 0


if __name__ == '__main__':
    try:
        code = run()
    except Exception:
        folder = user_root()
        folder.mkdir(parents=True, exist_ok=True)
        log = folder / 'error_inicio.txt'
        log.write_text(traceback.format_exc(), encoding='utf-8')
        if '--smoke-test' in sys.argv:
            if len(sys.argv) == 3:
                Path(sys.argv[2]).write_text(traceback.format_exc(), encoding='utf-8')
            sys.exit(1)
        import tkinter.messagebox as messagebox
        messagebox.showerror('SASISOPA', 'No se pudo iniciar el programa. El detalle se guardó en:\n' + str(log))
        code = 1
    sys.exit(code)
