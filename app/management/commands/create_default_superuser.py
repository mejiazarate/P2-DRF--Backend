from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from app.models import Rol  # Asegúrate de importar el modelo Rol

class Command(BaseCommand):
    help = 'Creates a default superuser if one does not exist.'

    def handle(self, *args, **options):
        User = get_user_model()

        # Verifica si el superusuario ya existe
        if not User.objects.filter(username='admin').exists():
            # Crea el rol "Administrador" si no existe
            admin_role, created = Rol.objects.get_or_create(nombre='Administrador')

            # Crea el superusuario
            user = User.objects.create_superuser('admin', 'ab@g.com', 'fail2025')

            # Asigna el rol de administrador al superusuario
            user.rol = admin_role
            user.save()

            self.stdout.wwrite(self.style.SUCCESS('Default superuser "admin" created and assigned the "Administrador" role.'))
        else:
            self.stdout.write(self.style.SUCCESS('Superuser "admin" already exists.'))
