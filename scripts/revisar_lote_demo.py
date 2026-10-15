"""Review the complete private base with fictional data, outside the repository."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import fitz
from PIL import Image
import sasisopa18 as engine
from firma_canvas import signature_png


def review(base, folder):
    folder.mkdir(parents=True, exist_ok=False)
    assets = folder / 'imagenes-demo'
    assets.mkdir()
    logo = assets / 'logo-demo.png'
    signature = assets / 'firma-demo.png'
    Image.new('RGB', (120, 60), '#008591').save(logo)
    signature_png([[(10, 40), (110, 80), (290, 40)]]).save(signature)
    catalog, maps = engine.configuration()
    inventory = json.loads((engine.ROOT / 'campos_sasisopa_18.json').read_text(encoding='utf-8'))
    project = engine.empty_project()
    project['values'] = {'estacion.numero': 'E-99999', 'estacion.razon_social': 'ESTACION EJEMPLO SA',
                         'estacion.direccion': 'AV. PRINCIPAL 123, COL. CENTRO, PUEBLA, C.P. 72000',
                         'estacion.logo': str(logo), 'documento.revision': '2',
                         'documento.fecha_revision': '15/10/2026'}
    for index, name in enumerate(('ANA LOPEZ', 'LUIS PEREZ', 'MARIA GARCIA')):
        project['people'].append({'id': str(index), 'nombre': name, 'puesto': 'RESPONSABLE',
                                  'iniciales': ''.join(w[0] for w in name.split()), 'firma': str(signature)})
    project['roles'] = {role['id']: str(index % 3) for index, role in enumerate(inventory['roles'])}
    for layout in maps.values():
        for page in layout['pages']:
            for table in page['tables']:
                for row in range(table['rows']):
                    project['table_people'][f"tabla.{table['id']}.{row}"] = str(row % 3)
    paths, warnings = engine.generate(base, folder / 'lote-demo', project, merge=True)
    checks = []
    for meta, path in zip(catalog['templates'], paths):
        original_path = base / meta['filename']
        assert hashlib.sha256(original_path.read_bytes()).hexdigest() == meta['sha256']
        with fitz.open(original_path) as original, fitz.open(path) as output:
            assert len(output) == len(original) == meta['pages']
            for before, after in zip(original, output):
                assert before.rect == after.rect
                drawing = lambda p: [{k: v for k, v in d.items() if k != 'seqno'} for d in p.get_drawings()]
                assert drawing(before) == drawing(after)
        checks.append({'document': meta['id'], 'pages': meta['pages'], 'geometry_and_borders': True, 'original_intact': True})
    with fitz.open(paths[-1]) as combined:
        assert len(combined) == 523 and len(combined.get_toc()) == 18
    engine.save_project(folder / 'datos-demo.sasisopa18.json', project)
    assert engine.load_project(folder / 'datos-demo.sasisopa18.json') == project
    report = {'fictional_data': True, 'documents': 18, 'pages': 523,
              'merged_pdf': True, 'profile_roundtrip': True, 'station_address_alignment': 'right',
              'logo_and_signatures': 'synthetic', 'warnings': warnings, 'checks': checks,
              'requires_user_review': ['Datos definitivos', 'Firmas definitivas', 'Campos particulares sin ubicación', 'Uso en la computadora del usuario']}
    (folder / 'informe-demo.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('base', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    print(json.dumps(review(args.base, args.output), ensure_ascii=False, indent=2))
