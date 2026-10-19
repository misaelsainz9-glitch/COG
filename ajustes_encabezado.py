"""Spacing rules inside existing station header cells; no table is resized."""
def ajustar_encabezados(layout):
    for index, page in enumerate(layout['pages']):
        for slot in page['slots']:
            if slot['key'] == 'documento.revision' and slot.get('transform') == 'revision_label':
                center = (slot['rect'][0] + slot['rect'][2]) / 2
                slot['rect'][0] = max(0, center - 50)
                slot['rect'][2] = min(page['size'][2], center + 50)
                slot['align'] = 1
        if index == 0:
            continue  # Covers retain their own layout.
        slots = page['slots']
        addresses = [s for s in slots if s['key'] == 'estacion.direccion' and s['rect'][1] < 160]
        for address in addresses:
            address['valign'] = 'top'
            companies = [s for s in slots if s['key'] == 'estacion.razon_social'
                         and s['rect'][1] < address['rect'][1] and s['rect'][1] < 160]
            for company in companies:
                # Numeric station fragments in the same left-hand header block.
                numbers = [s for s in slots if s['key'] == 'estacion.numero'
                           and s['rect'][3] <= company['rect'][1] + .5
                           and abs(s['rect'][2] - company['rect'][2]) < 15]
                top = max([company['rect'][1]] + [s['rect'][3] + 3 for s in numbers])
                bottom = min(company['rect'][3], address['rect'][1] - 3)
                if bottom - top >= 18:
                    company['rect'][1] = top
                    company['rect'][3] = bottom
                    company['valign'] = 'top'
                for logo in (s for s in slots if s['key'] == 'estacion.logo'
                             and s['rect'][1] < 160 and s['rect'][2] + 2 <= company['rect'][0]):
                    logo['rect'][3] = max(logo['rect'][3], address['rect'][1] - 3)
    return layout
