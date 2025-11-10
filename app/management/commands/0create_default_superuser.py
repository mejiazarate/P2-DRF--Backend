from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group  # Usamos Group de Django
from app.models import Rol  # Asegúrate de importar el modelo Rol

class Command(BaseCommand):
    help = 'Creates default groups "Administrador" and "Cliente", roles, and a superuser.'

    def handle(self, *args, **options):
        User = get_user_model()

        # Crear los grupos si no existen
        admin_group, created = Group.objects.get_or_create(name='Administrador')
        client_group, created = Group.objects.get_or_create(name='Cliente')

        # Crear los roles y asignarles los grupos correspondientes si no existen
        admin_role, created = Rol.objects.get_or_create(nombre='Administrador', grupo=admin_group)
        client_role, created = Rol.objects.get_or_create(nombre='Cliente', grupo=client_group)

        # Verifica si el superusuario ya existe
        if not User.objects.filter(username='admin').exists():
            # Crea el superusuario
            user = User.objects.create_superuser('admin', 'admin@example.com', 'fail2025')

            # Asigna el rol de Administrador al superusuario
            user.rol = admin_role
            user.save()

            self.stdout.write(self.style.SUCCESS('Default superuser "admin" created and assigned the "Administrador" role.'))
        else:
            self.stdout.write(self.style.SUCCESS('Superuser "admin" already exists.'))

        # Puedes verificar si los roles se han creado correctamente
        self.stdout.write(self.style.SUCCESS(f'Roles created: {admin_role.nombre} and {client_role.nombre}'))
        self.stdout.write(self.style.SUCCESS(f'Groups created: {admin_group.name} and {client_group.name}'))
