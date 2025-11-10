# utils.py
from django.template.loader import render_to_string
from django.core.files.base import ContentFile
from xhtml2pdf import pisa  # ← Cambio aquí
from io import BytesIO
from .models import Carrito
import logging
from django.utils.crypto import get_random_string

logger = logging.getLogger(__name__)

def generar_pdf_comprobante(pago):
    """
    Genera un PDF con los datos del pago, incluyendo los detalles de la venta,
    y lo guarda en el campo 'comprobante'.
    """
    # 1. Preparar datos de la venta, calculando subtotales
    venta = pago.venta
    
    if not venta:
        logger.error(f"El pago {pago.id} no tiene una venta asociada.")
        raise Exception(f"El pago {pago.id} no tiene una venta asociada.")
    
    items_con_subtotal = []
    
    for item in venta.items_vendidos.all().select_related('producto'):
        if not item.producto or item.precio_unitario is None or item.cantidad is None:
            logger.error(f"Item con ID {item.id} tiene datos incompletos.")
            raise Exception(f"Item con ID {item.id} tiene datos incompletos.")
        
        subtotal = item.precio_unitario * item.cantidad
        items_con_subtotal.append({
            'producto_nombre': item.producto.nombre,
            'cantidad': item.cantidad,
            'precio_unitario': float(item.precio_unitario),
            'subtotal': float(subtotal),
        })
    
    # 2. Definir el contexto para el template
    contexto = {
        'pago': pago,
        'venta': venta,
        'items_vendidos': items_con_subtotal,
    }

    if not contexto['pago']:
        logger.error(f"El pago {pago.id} es nulo o incompleto.")
        raise Exception(f"El pago {pago.id} es nulo o incompleto.")
    
    if not contexto['venta']:
        logger.error(f"La venta para el pago {pago.id} es nula o incompleta.")
        raise Exception(f"La venta para el pago {pago.id} es nula o incompleta.")
    
    if not contexto['items_vendidos']:
        logger.error(f"No hay items vendidos en la venta {venta.id}.")
        raise Exception(f"No hay items vendidos en la venta {venta.id}.")
    
    logger.info(f"Contexto para el template: {contexto}")
    
    # 3. Renderizar HTML con los datos
    try:
        html_string = render_to_string('comprobantes/comprobante_pago.html', contexto)
        print(f"✅ HTML renderizado correctamente")
    except Exception as e:
        logger.error(f"Error de renderización de plantilla: {e}")
        logger.error(f"Contexto que falló: {contexto}")
        raise Exception(f"Error al renderizar la plantilla: {e}") 

    # 4. Generar PDF en memoria con xhtml2pdf
    print(f"Generando PDF para el pago {pago.id}...")
    try:
        pdf_buffer = BytesIO()
        
        # Generar PDF con xhtml2pdf
        pisa_status = pisa.CreatePDF(
            html_string,
            dest=pdf_buffer,
            encoding='utf-8'
        )
        
        if pisa_status.err:
            logger.error(f"Error de xhtml2pdf: {pisa_status.err}")
            raise Exception(f"Error al generar PDF: {pisa_status.err}")
        
        print(f"✅ PDF generado en memoria para el pago {pago.id}.")
        
    except Exception as e:
        logger.error(f"Error de xhtml2pdf (PDF generation): {e}")
        raise Exception(f"Error al generar el PDF con xhtml2pdf: {e}")

    # 5. Guardar en el campo FileField
    nombre_archivo = f"comprobante_venta_{pago.id}.pdf"
    pago.comprobante.save(
        nombre_archivo,
        ContentFile(pdf_buffer.getvalue()),
        save=True
    )
    pdf_buffer.close()
    print(f"✅ Comprobante guardado correctamente en la base de datos para el pago {pago.id}.")