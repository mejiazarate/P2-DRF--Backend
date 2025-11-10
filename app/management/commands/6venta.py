from django.core.management.base import BaseCommand
import random
from datetime import timedelta, datetime
from django.utils import timezone
from app.models import Venta, VentaProducto, Producto, Usuario, Carrito, Promocion

class Command(BaseCommand):
    help = 'Genera ventas aleatorias durante el año 2024 y actualiza el stock de productos'

    def handle(self, *args, **kwargs):
        self.generar_ventas(1000)  # Puedes generar más o menos ventas según sea necesario

    def generar_ventas(self, num_ventas=100):
        # Definir el rango de fechas de enero 1, 2024 a diciembre 31, 2024
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 12, 31)
        
        for _ in range(num_ventas):
            # Generar una fecha aleatoria dentro del rango de fechas del 2024
            random_date = start_date + timedelta(days=random.randint(0, (end_date - start_date).days))
            
            # Seleccionamos un cliente aleatorio
            cliente = Usuario.objects.order_by('?').first()

            # Creamos un carrito para la venta
            carrito = Carrito.objects.create(user=cliente, estado='ordered')

            # Generamos una venta con una posible promoción
            promocion = Promocion.objects.order_by('?').first() if random.random() > 0.5 else None  # Elige una promoción aleatoria
            cantidad = random.randint(1, 5)  # Número aleatorio de productos
            productos = Producto.objects.filter(stock__gt=0)  # Productos con stock disponible

            # Elegimos productos aleatorios para la venta
            productos_seleccionados = random.sample(list(productos), min(cantidad, len(productos)))  # Selecciona productos sin repetirse
            
            # Calculamos el precio total de la venta
            precio_total = 0
            for producto in productos_seleccionados:
                precio_total += producto.precio  # Sumar el precio total de los productos seleccionados

            # Creamos la venta con la fecha aleatoria generada
            venta = Venta.objects.create(
                cliente=cliente,
                carrito=carrito,
                cantidad=cantidad,
                precio_unitario=precio_total / cantidad if cantidad else 0,
                precio_total=precio_total,
                promocion=promocion,
                metodo_pago="tarjeta",  # Puede ser 'tarjeta', 'efectivo', etc.
                estado_venta="completada",
                fecha=random_date  # Fecha aleatoria dentro del año 2024
            )

            # Crear una relación de productos con cantidades aleatorias
            for producto in productos_seleccionados:
                # Asignar una cantidad aleatoria de productos en la venta (entre 1 y el total restante de la cantidad)
                cantidad_producto = random.randint(1, cantidad)
                
                # Verificamos que haya suficiente stock
                if producto.stock >= cantidad_producto:
                    VentaProducto.objects.create(
                        venta=venta,
                        producto=producto,
                        cantidad=cantidad_producto,  # Cantidad aleatoria para este producto
                        precio_unitario=producto.precio
                    )
                    
                    # Reducir el stock del producto seleccionado
                    producto.stock -= cantidad_producto
                    producto.save()
                else:
                    self.stdout.write(self.style.WARNING(f"No hay suficiente stock para el producto {producto.nombre}."))

            self.stdout.write(self.style.SUCCESS(f"Venta {venta.id} creada con éxito para el cliente {cliente.username} en la fecha {random_date.date()}."))

        self.stdout.write(self.style.SUCCESS(f'\n¡Proceso completado! Se generaron {num_ventas} ventas aleatorias en el año 2024.'))
