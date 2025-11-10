from django.utils.crypto import get_random_string
from django.contrib.auth.models import Group
from app.models import Usuario, Rol  # Cambia 'app' por el nombre de tu aplicación
import random
from datetime import datetime

# Creamos un grupo ficticio para los usuarios, si es necesario
grupo_cliente, created = Group.objects.get_or_create(name='Clientes')

# Crear un rol ficticio llamado 'Cliente'
rol_cliente, created = Rol.objects.get_or_create(nombre="Cliente", grupo=grupo_cliente)

# Crear 40 usuarios ficticios
for i in range(1, 41):
    nombre = f"Cliente_{i}"
    apellido_paterno = f"Apellido_{i}"
    apellido_materno = f"Materno_{i}"
    sexo = random.choice(['M', 'F'])  # Aleatorio entre Masculino y Femenino
    email = f"cliente{i}@ejemplo.com"
    direccion = f"Direccion {i}, Ciudad Ficticia"
    fecha_nacimiento = f"1990-01-{random.randint(1, 28):02d}"  # Fecha de nacimiento aleatoria
    
    # Crear un usuario
    usuario = Usuario.objects.create(
        username=nombre,
        first_name=nombre,
        last_name=f"{apellido_paterno} {apellido_materno}",
        sexo=sexo,
        email=email,
        direccion=direccion,
        fecha_nacimiento=fecha_nacimiento,
        rol=rol_cliente
    )

    # Puedes agregar más lógica si deseas asignarles dispositivos, carrito, etc.
    print(f"Usuario {usuario.username} creado con éxito.")
