from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.auth import get_user_model
from app.models import Rol, Usuario  # Cambié User por Usuario

class Command(BaseCommand):
    help = 'Pobla la base de datos con los roles predeterminados, asigna permisos, asigna el rol al usuario admin y crea un superusuario'

    def handle(self, *args, **kwargs):
        # Crear los grupos si no existen
        admin_group, created = Group.objects.get_or_create(name='Administrador')
        client_group, created = Group.objects.get_or_create(name='Cliente')

        # Asignar todos los permisos a los grupos
        admin_group.permissions.set(Permission.objects.all())  # Asigna todos los permisos al grupo 'Administrador'
        client_group.permissions.set(Permission.objects.all())  # Asigna todos los permisos al grupo 'Cliente'

        # Crear los roles si no existen y asignarles los grupos
        roles = ['Administrador', 'Cliente']
        for rol in roles:
            if not Rol.objects.filter(nombre=rol).exists():
                if rol == 'Administrador':
                    Rol.objects.create(nombre=rol, grupo=admin_group)
                else:
                    Rol.objects.create(nombre=rol, grupo=client_group)

        # Buscar el usuario con username 'admin' en el modelo personalizado 'Usuario'
        try:
            user = Usuario.objects.get(username='admin')  # Usar Usuario en lugar de User
            # Buscar el rol 'Administrador' y asignarlo al usuario
            rol_admin = Rol.objects.get(nombre='Administrador')
            user.rol = rol_admin
            user.save()
            self.stdout.write(self.style.SUCCESS('Rol de Administrador asignado al usuario admin'))
        except Usuario.DoesNotExist:  # Asegúrate de que se maneje el modelo correcto
            self.stdout.write(self.style.ERROR('El usuario con username "admin" no existe'))

        # Crear un superusuario con el nombre de usuario 'admin' y la contraseña 'fail2025'
        if not Usuario.objects.filter(username='admin').exists():
            UserModel = get_user_model()
            user = UserModel.objects.create_superuser(
                username='admin',
                password='fail2025',
                email='admin@example.com'  # Cambia o deja vacío si no es necesario
            )

            # Asignar el rol de 'Administrador' al superusuario
            rol_admin = Rol.objects.get(nombre='Administrador')
            user.rol = rol_admin
            user.save()

            self.stdout.write(self.style.SUCCESS('Superusuario "admin" creado exitosamente y rol "Administrador" asignado.'))

        self.stdout.write(self.style.SUCCESS('Roles y grupos creados y configurados exitosamente'))
