from django.core.management.base import BaseCommand
from app.models import Promocion
from datetime import date

class Command(BaseCommand):
    help = 'Llena la tabla de promociones con datos reales'

    def handle(self, *args, **options):
        # Lista de promociones a insertar
        promociones = [
            {
                'descripcion': 'Descuento del 10% en todos los productos por tiempo limitado',
                'fecha_inicio': '2025-11-01',
                'fecha_fin': '2025-11-30',
                'descuento': 10.00
            },
            {
                'descripcion': 'Oferta del 15% en productos de tecnología',
                'fecha_inicio': '2025-11-15',
                'fecha_fin': '2025-12-15',
                'descuento': 15.00
            },
            {
                'descripcion': 'Descuento del 20% en todas las compras mayores a 100€',
                'fecha_inicio': '2025-11-20',
                'fecha_fin': '2025-12-31',
                'descuento': 20.00
            },
            {
                'descripcion': 'Black Friday: 30% de descuento en todos los productos',
                'fecha_inicio': '2025-11-25',
                'fecha_fin': '2025-11-28',
                'descuento': 30.00
            },
            {
                'descripcion': 'Navidad: 25% de descuento en productos seleccionados',
                'fecha_inicio': '2025-12-01',
                'fecha_fin': '2025-12-24',
                'descuento': 25.00
            }
        ]
        
        # Crear promociones
        for promo in promociones:
            # Convierte las fechas a objetos de tipo date
            fecha_inicio = date.fromisoformat(promo['fecha_inicio'])
            fecha_fin = date.fromisoformat(promo['fecha_fin'])

            # Verifica si la promoción ya existe para evitar duplicados
            if not Promocion.objects.filter(descripcion=promo['descripcion']).exists():
                Promocion.objects.create(
                    descripcion=promo['descripcion'],
                    fecha_inicio=fecha_inicio,
                    fecha_fin=fecha_fin,
                    descuento=promo['descuento']
                )
                self.stdout.write(self.style.SUCCESS(f'Promoción creada: {promo["descripcion"]}'))
            else:
                self.stdout.write(self.style.SUCCESS(f'La promoción ya existe: {promo["descripcion"]}'))

        self.stdout.write(self.style.SUCCESS('Promociones creadas correctamente.'))
