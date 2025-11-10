from django.core.management.base import BaseCommand
from app.models import TipoGarantia
from datetime import date

class Command(BaseCommand):
    help = 'Crea tipos de garantías por marca'

    def handle(self, *args, **options):
        # Diccionario de garantías por marca
        garantias = [
            {"marca": "Whirlpool", "tipo": "Garantía Whirlpool", "duracion": 12, "descripcion": "Garantía estándar para productos Whirlpool", "exclusiones": "Accidentes, mal uso, daños por agua", "cobertura": "Defectos de fabricación y funcionamiento"},
            {"marca": "Samsung", "tipo": "Garantía Samsung", "duracion": 12, "descripcion": "Garantía estándar de Samsung", "exclusiones": "Daños físicos, mal uso, caídas", "cobertura": "Defectos de fabricación"},
            {"marca": "LG", "tipo": "Garantía LG", "duracion": 24, "descripcion": "Garantía estándar de LG", "exclusiones": "Daños por mal manejo, uso inapropiado", "cobertura": "Defectos de fabricación y componentes"},
            {"marca": "Bosch", "tipo": "Garantía Bosch", "duracion": 24, "descripcion": "Garantía estándar de Bosch", "exclusiones": "Accidentes, mal uso, daños por humedad", "cobertura": "Defectos de fabricación y funcionamiento"},
            {"marca": "Electrolux", "tipo": "Garantía Electrolux", "duracion": 12, "descripcion": "Garantía estándar de Electrolux", "exclusiones": "Daños físicos, mal uso, líquidos", "cobertura": "Defectos de fabricación"},
            {"marca": "GE", "tipo": "Garantía GE", "duracion": 12, "descripcion": "Garantía estándar de GE", "exclusiones": "Accidentes, mal uso, modificaciones no autorizadas", "cobertura": "Defectos de fabricación"},
            {"marca": "Maytag", "tipo": "Garantía Maytag", "duracion": 12, "descripcion": "Garantía estándar de Maytag", "exclusiones": "Accidentes, mal uso, daños por agua", "cobertura": "Defectos de fabricación y funcionamiento"},
        ]

        creadas = 0
        existentes = 0

        # Crear o actualizar tipos de garantía
        for garantia_data in garantias:
            tipo_garantia, created = TipoGarantia.objects.get_or_create(
                tipo=garantia_data['tipo'],
                defaults={
                    'duracion': garantia_data['duracion'],
                    'descripcion': garantia_data['descripcion'],
                    'exclusiones': garantia_data['exclusiones'],
                    'cobertura': garantia_data.get('cobertura', ''),
                    'activa': True,
                    'activo_para_ventas': True
                }
            )
            
            if created:
                creadas += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Garantía creada: {garantia_data["tipo"]} ({garantia_data["duracion"]} meses)')
                )
            else:
                existentes += 1
                self.stdout.write(
                    self.style.WARNING(f'○ Ya existe: {garantia_data["tipo"]}')
                )

        # Resumen final
        self.stdout.write(self.style.SUCCESS('\n' + '='*50))
        self.stdout.write(self.style.SUCCESS(f'Garantías creadas: {creadas}'))
        self.stdout.write(self.style.WARNING(f'Garantías existentes: {existentes}'))
        self.stdout.write(self.style.SUCCESS(f'Total procesadas: {creadas + existentes}'))
        self.stdout.write(self.style.SUCCESS('='*50))
