from django.core.management.base import BaseCommand
from app.models import Feriado
from datetime import date

class Command(BaseCommand):
    help = 'Carga feriados nacionales de Bolivia en la base de datos'

    def handle(self, *args, **options):
        feriados = [
            # Año Nuevo
            date(2025, 1, 1),
            # Día del Estado Plurinacional
            date(2025, 1, 22),
            # Carnaval
            date(2025, 3, 3),
            date(2025, 3, 4),
            # Viernes Santo
            date(2025, 4, 18),
            # Día del Trabajo
            date(2025, 5, 1),
            # Corpus Christi
            date(2025, 6, 19),
            # Año Nuevo Andino‑Amazónico
            date(2025, 6, 21),
            # Día de la Independencia de Bolivia
            date(2025, 8, 6),
            # Día de los Difuntos (traslado)
            date(2025, 11, 3),
            # Navidad
            date(2025, 12, 25),
        ]

        for fecha in feriados:
            obj, created = Feriado.objects.get_or_create(fecha=fecha)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Feriado creado: {fecha}'))
            else:
                self.stdout.write(self.style.WARNING(f'Feriado ya existe: {fecha}'))

        self.stdout.write(self.style.SUCCESS('Carga de feriados completada.'))
