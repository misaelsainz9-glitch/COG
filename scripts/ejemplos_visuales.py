"""Render public examples with the real PDF engine and a wholly synthetic template.

Only public field geometry is reused. No private PDF, logo, identity or signature
is read by this script. The PNGs are PDF renderings, not AI illustrations.
"""
from pathlib import Path
import argparse
import copy
import json
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import fitz
import sasisopa18 as engine
from firma_canvas import signature_png


CASES = [
    ('01-direccion-corta', '1. DIRECCION CORTA', 'E-12345', 'SERVICIO NORTE SA',
     'AV. CENTRAL 120, PUEBLA', '1', False),
    ('02-direccion-larga', '2. DIRECCION LARGA', 'E-67890', 'SERVICIO NORTE SA',
     'CARRETERA FEDERAL 129 KM 108.5, LOCALIDAD EJEMPLO, MUNICIPIO DE PUEBLA, ESTADO DE PUEBLA, C.P. 72000', '2', False),
    ('03-razon-social-larga', '3. RAZON SOCIAL LARGA', 'E-00007',
     'ENERGETICOS Y SERVICIOS DEL VALLE SA DE CV', 'CALLE PRINCIPAL 25, COL. CENTRO, PUEBLA', '3', False),
    ('04-logo-nombres-firmas', '4. LOGO, NOMBRES Y FIRMAS', 'E-54321', 'ESTACION DEMO SA',
     'AV. EJEMPLO 450, PUEBLA', '4', True),
]


def text(page, rect, value, size=9, bold=False, align=0):
    fonts = engine.FontBook(page.parent)
    return engine._write(page, {'rect': rect, 'size': size, 'min_size': size,
                               'font': 'Arial-BoldMT' if bold else 'ArialMT', 'align': align}, value, fonts)


def template(title, signatures=False):
    doc = fitz.open()
    page = doc.new_page(width=612, height=385)
    text(page, [52, 5, 560, 25], title, 14, True)
    page.draw_rect(fitz.Rect(52.5, 33.8, 559.6, 151.9), color=(.1, .1, .1), width=.6)
    def line(x0, y0, x1, y1):
        page.draw_line((x0, y0), (x1, y1), color=(.1, .1, .1), width=.6)
    for x in (235.8, 389.5):line(x, 33.8, x, 111.9)
    line(475.5, 33.8, 475.5, 83.5)
    line(389.5, 51.5, 559.6, 51.5)
    line(389.5, 83.5, 559.6, 83.5)
    line(52.5, 111.9, 559.6, 111.9)
    text(page, [140, 36.1, 204, 46.2], 'ESTACION: E-', 9, True, 2)
    text(page, [239, 35, 386, 109], 'SISTEMA DE\nADMINISTRACION DE LA\nSEGURIDAD INDUSTRIAL,\nSEGURIDAD OPERATIVA Y\nPROTECCION AL MEDIO\nAMBIENTE', 9, align=1)
    text(page, [395, 35, 470, 48], 'PAG: 2', 9, align=1)
    text(page, [480, 35, 555, 48], 'DE: 8', 9, align=1)
    text(page, [397, 53, 470, 64], 'REVISION:', 9, align=1)
    text(page, [395, 84, 555, 94], 'CODIGO:', 9, align=1)
    text(page, [403, 94, 438, 105], 'E-', 9, align=2)
    text(page, [464, 94, 516, 105], '.01.PO.01.R', 9)
    text(page, [57, 113, 555, 124], 'I. POLITICA', 9, align=1)
    text(page, [57, 125, 555, 149], '1. PROCEDIMIENTO PARA EL ESTABLECIMIENTO, REVISION, DISPONIBILIDAD Y COMUNICACION DE LA POLITICA DEL SISTEMA DE ADMINISTRACION', 9, align=1)
    text(page, [53, 165, 559, 179], 'PRUEBA DE RENDERIZADO - PLANTILLA DE DEMOSTRACION', 10, True)
    if signatures:
        page.draw_rect(fitz.Rect(52.5, 242, 559.5, 343), color=(.1, .1, .1), width=.6)
        for x in (221.5, 390.5):line(x, 242, x, 343)
        for index, label in enumerate(('ELABORO', 'REVISO', 'AUTORIZO')):
            x0 = 52.5 + index * 169
            text(page, [x0 + 4, 244, x0 + 165, 258], label, 9, True, 1)
            text(page, [x0 + 4, 329, x0 + 165, 340], 'FIRMA SIMULADA', 7, align=1)
    text(page, [53, 354, 560, 378], 'Datos, logo y firmas ficticios. Se usa el motor del programa; no se muestra un documento privado. La fuente disponible puede diferir de la instalada en Windows.', 8)
    return doc


def generate(folder):
    folder.mkdir(parents=True, exist_ok=True)
    assets = folder / 'recursos-demo'
    assets.mkdir(exist_ok=True)
    logo = assets / 'logo-demo.png'
    svg = b'<svg xmlns="http://www.w3.org/2000/svg" width="300" height="105"><rect width="300" height="105" rx="9" fill="#008591"/><text x="150" y="66" font-family="sans-serif" font-size="48" text-anchor="middle" fill="white">DEMO</text></svg>'
    with fitz.open(stream=svg, filetype='svg') as vector:vector[0].get_pixmap(alpha=True).save(logo)
    _, maps = engine.configuration()
    summary = []
    overview = fitz.open()
    board = overview.new_page(width=1224, height=770)
    for index, (filename, title, number, company, address, revision, signatures) in enumerate(CASES):
        with template(title, signatures) as doc:
            project = engine.empty_project()
            project['values'] = {'estacion.numero': number, 'estacion.razon_social': company,
                                 'estacion.direccion': address, 'estacion.logo': str(logo),
                                 'documento.revision': revision, 'documento.fecha_revision': '16/10/2026'}
            slots = [copy.deepcopy(s) for s in maps['I']['pages'][1]['slots'] if not s['key'].startswith('rol.')]
            for slot in slots:
                # The synthetic background is already blank; no original text to remove.
                slot['clear'] = False
            if signatures:
                for i, (role, name) in enumerate(zip(('elabora', 'revisa', 'autoriza'), ('ANA LOPEZ', 'LUIS PEREZ', 'MARIA GARCIA'))):
                    image = assets / f'firma-{i + 1}-simulada.png'
                    signature_png([[(40, 120), (95, 45 + 15*i), (160, 130), (225, 65), (280, 115), (390, 80), (520, 110)]]).save(image)
                    pid = str(i)
                    project['people'].append({'id': pid, 'nombre': name, 'firma': str(image)})
                    project['roles'][role] = pid
                    x = 52.5 + 169*i
                    slots.extend([
                        {'id': f'demo-{role}-nombre', 'key': f'rol.{role}.nombre', 'rect': [x+5, 314, x+164, 326], 'font': 'ArialMT', 'size': 8, 'min_size': 8, 'align': 1, 'clear': False},
                        {'id': f'demo-{role}-firma', 'key': f'rol.{role}.firma', 'rect': [x+22, 268, x+147, 308], 'kind': 'image', 'clear': False},
                    ])
            layout = {'pages': [{'size': [0., 0., 612., 385.], 'slots': slots, 'tables': []}]}
            before = [{k: v for k, v in item.items() if k != 'seqno'} for item in doc[0].get_drawings()]
            notes = engine.render_page(doc, 0, layout, project, 'I', engine.FontBook(doc))
            after = [{k: v for k, v in item.items() if k != 'seqno'} for item in doc[0].get_drawings()]
            assert before == after
            note = next(n for n in notes if n['field'] == 'estacion.direccion')
            company_note = next(n for n in notes if n['field'] == 'estacion.razon_social')
            text(doc[0], [53, 184, 559, 209], f"Direccion: {note['lines']} linea(s), {note['size']:g} pt, alineada a la derecha.\nRazon social: {company_note['lines']} linea(s), {company_note['size']:g} pt. Bordes conservados.", 9)
            text(doc[0], [53, 215, 559, 231], 'Firmas simuladas en espacios existentes.' if signatures else 'Numero, empresa, direccion, fecha y revision capturados automaticamente.', 9)
            doc[0].get_pixmap(matrix=fitz.Matrix(2.5, 2.5), alpha=False).save(folder / (filename + '.png'))
            x = (index % 2)*612
            y = (index // 2)*385
            board.show_pdf_page(fitz.Rect(x, y, x+612, y+385), doc, 0)
            summary.append({'example': filename, 'station_number': number, 'address_lines': note['lines'], 'address_size': note['size'], 'company_lines': company_note['lines'], 'company_size': company_note['size'], 'borders_preserved': before == after, 'synthetic_template': True})
    board.get_pixmap(matrix=fitz.Matrix(1.8, 1.8), alpha=False).save(folder / '00-todas-las-pruebas.png')
    overview.close()
    (folder / 'resultados.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('output', type=Path)
    generate(parser.parse_args().output)
