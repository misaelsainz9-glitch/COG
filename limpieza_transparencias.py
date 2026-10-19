"""Keep empty image placeholders invisible when MuPDF applies redactions.

Some cleaned PDFs contain a 1x1 image with a fully transparent soft mask.
Cropping that image during a later redaction can make it paint an opaque box.
An empty Form XObject has the same visible result and nothing to crop.
"""
import fitz


def normalizar_marcadores_vacios(doc, page):
    removed = set()
    for image in page.get_images(full=True):
        xref, mask, width, height = image[:4]
        if xref in removed or (width, height) != (1, 1) or not mask:
            continue
        alpha = fitz.Pixmap(doc, mask)
        if not alpha.samples or any(alpha.samples):
            continue
        doc.update_object(xref, '<< /Type /XObject /Subtype /Form /FormType 1 '
                          '/BBox [0 0 1 1] /Resources << >> >>')
        doc.update_stream(xref, b'')
        removed.add(xref)
    return len(removed)
