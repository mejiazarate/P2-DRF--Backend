# utils.py
from django.template.loader import render_to_string
from django.core.files.base import ContentFile
from weasyprint import HTML
from io import BytesIO

def generar_pdf_comprobante(pago):
    """
    Genera un PDF con los datos del pago y lo guarda en el campo 'comprobante'.
    """
    # Renderizar HTML con los datos del pago
    html_string = render_to_string('comprobantes/comprobante_pago.html', {'pago': pago})

    # Generar PDF en memoria
    print(f"Generando PDF para el pago {pago.id}...")
    html = HTML(string=html_string)
    pdf_buffer = BytesIO()
    html.write_pdf(pdf_buffer)
    print(f"PDF generado en memoria para el pago {pago.id}.")

    # Guardar en el campo FileField
    nombre_archivo = f"comprobante_pago_{pago.id}.pdf"
    pago.comprobante.save(
        nombre_archivo,
        ContentFile(pdf_buffer.getvalue()),
        save=True  # Guarda el modelo automáticamente
    )
    pdf_buffer.close()
    print(f"Comprobante guardado correctamente en la base de datos para el pago {pago.id}.")
