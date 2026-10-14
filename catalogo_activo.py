from pathlib import Path
import json


def catalog_state():
    return json.loads((Path(__file__).resolve().parent/'catalogo_activo.json').read_text(encoding='utf-8'))


def require_ready():
    state=catalog_state()
    if state['status'] not in ('ready','ready_pdf'):raise ValueError(state['message'])
    return state
