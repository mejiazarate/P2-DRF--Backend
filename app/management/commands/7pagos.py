# app/management/commands/generar_pagos.py
from django.core.management.base import BaseCommand
import random
from datetime import timedelta
from django.utils import timezone
from app.models import Pago, Venta, Usuario
from decimal import Decimal
class Command(BaseCommand):
    help = 'Genera pagos aleatorios para 100 ventas'

    def handle(self, *args, **kwargs):
        self.generar_pagos(1000)

    def generar_pagos(self, num_pagos=100):
        for _ in range(num_pagos):
            # Seleccionamos una venta aleatoria
            venta = Venta.objects.order_by('?').first()

            # Seleccionamos un usuario aleatorio para el pago
            usuario = Usuario.objects.order_by('?').first()

            # Generamos un monto aleatorio, en este caso entre 50 y el precio total de la venta
            monto = Decimal(random.uniform(50, float(venta.precio_total)))
            # Elegimos un método de pago aleatorio

            # Creamos el pago
            pago = Pago.objects.create(
                usuario=usuario,
                monto=monto,
                metodo_pago='tarjeta',
                fecha_pago=timezone.now(),
                referencia=f"Referencia_{random.randint(1000, 9999)}",  # Generamos una referencia aleatoria
                observaciones="Pago realizado con éxito.",
                venta=venta  # Asociamos el pago con una venta
            )

            # Imprimir mensaje de éxito
            self.stdout.write(self.style.SUCCESS(f"Pago {pago.id} creado con éxito para la venta {venta.id} y el usuario {usuario.username}."))
