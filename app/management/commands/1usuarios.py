from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from app.models import Rol
from django.contrib.auth.models import Group
import random
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Creates 90 users with the role "Cliente" and sets is_recurrente=True'

    def handle(self, *args, **options):
        User = get_user_model()

        # Obtener el grupo "Cliente" y el rol "Cliente"
        client_group, created = Group.objects.get_or_create(name='Cliente')
        client_role, created = Rol.objects.get_or_create(nombre='Cliente', grupo=client_group)

        # Lista de nombres y apellidos reales (puedes agregar más o personalizarla)
        nombres_apellidos = [
            ("Juan", "Pérez", "Lopez"),
            ("Ana", "González", "Martínez"),
            ("Carlos", "Ramírez", "Hernández"),
            ("Laura", "Martínez", "Sánchez"),
            ("José", "Hernández", "Moreno"),
            ("María", "López", "Gómez"),
            ("David", "García", "Jiménez"),
            ("Sofía", "Rodríguez", "Molina"),
            ("Luis", "Sánchez", "Pérez"),
            ("Marta", "Díaz", "Torres"),
            ("Pedro", "Torres", "Ramírez"),
            ("Isabel", "Vázquez", "Méndez"),
            ("Javier", "Moreno", "Torres"),
            ("Carmen", "Muñoz", "Salazar"),
            ("Antonio", "Romero", "Castro"),
            ("Sara", "Gómez", "Cordero"),
            ("Miguel", "Jiménez", "Hidalgo"),
            ("Pablo", "Molina", "Serrano"),
            ("Eva", "Suárez", "Vega"),
            ("Francisco", "Álvarez", "Castro"),
            ("Raquel", "Fernández", "Medina"),
            ("Andrés", "Ruiz", "Cano"),
            ("Claudia", "Jiménez", "Bravo"),
            ("Ricardo", "Gómez", "Romero"),
            ("Inés", "Santos", "Vega"),
            ("Alejandro", "Méndez", "Romero"),
            ("Patricia", "García", "Navarro"),
            ("Felipe", "López", "Vázquez"),
            ("Beatriz", "Torres", "López"),
            ("Jorge", "Martínez", "Gutiérrez"),
            ("Julia", "Mora", "Gómez"),
            ("Alberto", "Cruz", "Salazar"),
            ("Elena", "Vidal", "Martínez"),
            ("Raúl", "Ramírez", "Serrano"),
            ("Montserrat", "Salazar", "Torres"),
            ("Tomás", "Hidalgo", "González"),
            ("Ángel", "Cano", "Gómez"),
            ("Marina", "Navarro", "López"),
            ("Víctor", "Luna", "Ruiz"),
            ("Gabriela", "Serrano", "Ramírez"),
            ("Adrián", "Castro", "Rodríguez"),
            ("Nuria", "Bravo", "Suárez"),
            ("Martín", "Blanco", "Pérez"),
            ("Eva", "Romero", "Molina"),
            ("Óscar", "Paredes", "Castro"),
            ("Patricia", "Castro", "Gómez"),
            ("Fernando", "Cordero", "González"),
            ("Mónica", "Ruiz", "Serrano"),
            ("David", "Gil", "Navarro"),
            ("Vera", "Medina", "Suárez"),
            ("Rocío", "Rivas", "Vega"),
            ("Antonio", "García", "Torres"),
            ("José Luis", "Méndez", "Gómez"),
            ("Lucía", "Hernández", "Morales"),
            ("Raquel", "Montoya", "Serrano"),
            ("Santiago", "López", "Gómez"),
            ("Carolina", "Palacios", "González"),
            ("Carlos", "Rodríguez", "Vega"),
            ("Sara", "Díaz", "Castro"),
            ("Julio", "Gutiérrez", "Bravo"),
            ("Manuel", "Pérez", "Ramírez"),
            ("María José", "Sánchez", "Vega"),
            ("Rafael", "Jiménez", "Gómez"),
            ("Susana", "Morales", "Méndez"),
            ("Eduardo", "Pérez", "Serrano"),
            ("Alba", "Martínez", "Morales"),
            ("Pilar", "Martín", "Ramírez"),
            ("Juan Carlos", "Romero", "Vega"),
            ("Lucía", "Torres", "Rodríguez"),
            ("Jorge", "López", "Martínez"),
            ("Silvia", "Hernández", "Vázquez"),
            ("Antonio", "Vásquez", "Bravo"),
            ("Pedro", "Rodríguez", "Torres"),
            ("Mónica", "Ramírez", "Serrano"),
            ("Begoña", "González", "Cano"),
            ("Nerea", "García", "Vega"),
            ("Sandra", "Ruiz", "Ramírez"),
            ("Ángel", "Vega", "Vázquez"),
            ("David", "Martínez", "Navarro"),
            ("María Teresa", "Gómez", "Méndez"),
            ("María Pilar", "Sánchez", "Castro"),
            ("Miguel Ángel", "Serrano", "Rodríguez"),
            ("José María", "Romero", "González"),
            ("Isabel", "Torres", "Bravo"),
            ("Rosa", "Jiménez", "Vega"),
            ("José Antonio", "Hernández", "Vega"),
            ("Carolina", "Gómez", "Navarro"),
            ("César", "Vázquez", "Bravo"),
            ("Manuel", "Rodríguez", "Hernández"),
            ("Antonio", "González", "Méndez"),
            ("Inés", "Ruiz", "Gómez"),
            ("David", "Torres", "Morales"),
            ("Esther", "Suárez", "Vega"),
            ("Rafael", "Cruz", "Rodríguez")
        ]

        # Lista de direcciones
        direcciones = [
            "Calle Falsa 123, Madrid, España",
            "Av. de la Constitución 456, Barcelona, España",
            "Calle Mayor 789, Sevilla, España",
            "Paseo de la Castellana 101, Valencia, España",
            "Calle de Gran Vía 202, Málaga, España"
        ]

        # Crear 90 usuarios
        for nombre, apellido_paterno, apellido_materno in nombres_apellidos:
            username = f'{nombre.lower()}_{apellido_paterno.lower()}'  # Usar un formato diferente para el nombre de usuario
            email = f'{nombre.lower()}.{apellido_paterno.lower()}@example.com'  # Crear un email único
            if not User.objects.filter(username=username).exists():
                # Generar fecha de nacimiento aleatoria entre 18 y 60 años
                fecha_nacimiento = datetime.today() - timedelta(days=random.randint(6570, 21900))  # entre 18 y 60 años

                # Seleccionar sexo aleatorio
                sexo = random.choice(['M', 'F'])

                # Seleccionar dirección aleatoria
                direccion = random.choice(direcciones)

                # Asignar si el usuario es recurrente aleatorio
                es_recurrente = random.choice([True, False])

                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password='defaultpassword123',  # Puedes cambiar la contraseña si es necesario
                    nombre=nombre,
                    apellido_paterno=apellido_paterno,
                    apellido_materno=apellido_materno,
                    sexo=sexo,
                    direccion=direccion,
                    fecha_nacimiento=fecha_nacimiento,
                    es_recurrente=es_recurrente
                )

                # Asigna el rol de "Cliente" y establece is_recurrente=True
                user.rol = client_role
                user.is_recurrente = es_recurrente
                user.save()

                # Añadir el usuario al grupo "Cliente"
                user.groups.add(client_group)

                self.stdout.write(self.style.SUCCESS(f'User {nombre} {apellido_paterno} {apellido_materno} created and assigned to the "Cliente" role.'))
            else:
                self.stdout.write(self.style.SUCCESS(f'User {nombre} {apellido_paterno} {apellido_materno} already exists.'))

        self.stdout.write(self.style.SUCCESS('Successfully created 90 users with the "Cliente" role.'))
