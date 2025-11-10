from django.db import models 
from rest_framework import serializers
from django.contrib.auth.hashers import check_password
#login
from django.contrib.contenttypes.models import ContentType
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from .models import (Pago,Producto,Promocion,Venta, VentaProducto,TipoGarantia,
    Rol, Usuario,Bitacora,DetalleBitacora,DispositivoMovil,NotificacionPush
)
from .fcm_service import enviar_notificacion_fcm

from django.contrib.auth.models import Group, Permission as AuthPermission
class RolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rol
        fields = ['id', 'nombre']
    def create(self, validated_data):
        print("--- Inicio del método create() en RolSerializer ---")
        
        # 1. Extrae el nombre del rol
        rol_name = validated_data.get('nombre')
        print(f"1. Nombre de rol extraído: {rol_name}")

        try:
            # 2. Busca si ya existe un grupo con ese nombre
            group = Group.objects.get(name=rol_name)
            print(f"2. Grupo existente encontrado: {group.name}")
        except Group.DoesNotExist:
            print(f"2. ¡Advertencia! No se encontró un grupo llamado '{rol_name}'.")
            # Podrías crear el grupo si no existe, o manejar el error
            raise serializers.ValidationError(f"No existe un grupo con el nombre '{rol_name}'.")

        # 3. Asigna el grupo existente al nuevo rol
        print(f"3. Intentando crear el Rol con el grupo ID: {group.id}")
        rol = Rol.objects.create(grupo=group, **validated_data)
        
        print("--- Rol creado exitosamente ---")
        return rol
#Cuando pones rol = RolSerializer(read_only=True), le estás diciendo a DRF:
#“Este campo solo se usa para lectura. Ignora cualquier valor que venga en el payload de escritura (POST/PUT/PATCH).” 
class UsuarioSerializer(serializers.ModelSerializer):
    rol = serializers.PrimaryKeyRelatedField(
        queryset=Rol.objects.all(),
        required=True
    )

    class Meta:
        model = Usuario
        fields = [
            'id', 'username', 'email', 'nombre', 'apellido_paterno', 'apellido_materno',
            'sexo', 'direccion', 'fecha_nacimiento', 'rol', 'password'
        ]
        extra_kwargs = {
            'password': {'write_only': True,'required': False}
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = Usuario(**validated_data)
        if password:
            user.set_password(password)  # ✅ ESTO HASHEA LA CONTRASEÑA
        user.save()
        return user
    def update(self, instance, validated_data):
        # 1. Handle password separately
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
        
        # 2. Call super().update() for other fields
        # This will update all fields present in validated_data
        updated_instance = super().update(instance, validated_data)
        
        # 3. Save the instance if password was changed
        if password:
            updated_instance.save() # Save only if password was updated, otherwise super().update might have saved.
                                   # More robust: always save at the end if you perform a set_password.
        
        return updated_instance

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['rol_nombre'] = instance.rol.nombre if instance.rol else None
        return rep



class MyTokenPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):#@
        username=attrs.get(self.username_field) or attrs.get('username')
        password=attrs.get('password')
        User=get_user_model()
        user=User.objects.filter(username=username).first()
        print(user)
        if not user:
            raise AuthenticationFailed('el usuario no existe')
        if not user.check_password(password):
            raise AuthenticationFailed('ingrese su contrase;a correctemetn')
        
            
        return super().validate(attrs)
class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs
    def save(self, **kwargs):
        RefreshToken(self.token).blacklist()
class GroupSerializer(serializers.ModelSerializer):
    permissions = serializers.PrimaryKeyRelatedField(
        queryset=AuthPermission.objects.all(),
        many=True
    )

    class Meta:
        model = Group
        fields = ['id', 'name', 'permissions']
class UsuarioMeSerializer(serializers.ModelSerializer):
    """
    Serializador exclusivo para el endpoint '/usuarios/me/'.
    """
    rol = RolSerializer(read_only=True) # Utiliza el RolSerializer para serializar el objeto completo

    class Meta:
        model = Usuario
        fields = [
            "id",
            "username",
            "nombre",
            "apellido_paterno",
            "apellido_materno",
            "sexo",
            "email",
            "fecha_nacimiento",
            "rol",
        ]
class AuthPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthPermission
        fields = ['id', 'codename', 'name']
class ChangePasswordSerializer(serializers.Serializer):
    # current_password será requerido condicionalmente, no por defecto
    current_password = serializers.CharField(required=False, write_only=True)
    new_password = serializers.CharField(min_length=6, write_only=True)
    confirm_new_password = serializers.CharField(min_length=6, write_only=True)

    def validate(self, data):
        request = self.context.get("request")
        target_user = self.context.get("user") # Este es el usuario CUYA contraseña se va a cambiar

        # Verificación de que new_password y confirm_new_password coinciden
        if data["new_password"] != data["confirm_new_password"]:
            raise serializers.ValidationError({"confirm_new_password": "Las nuevas contraseñas no coinciden."})

        # Si el usuario que hace la solicitud es un administrador (o superuser)
        # y no está cambiando su propia contraseña, O si es un superuser
        # podemos omitir la verificación de current_password.
        # Asumimos que un rol de ID 1 es "Administrador". Ajusta esto si tu ID de rol es diferente.
        is_request_user_admin = (request and request.user.is_authenticated and
                                 (request.user.is_superuser or (hasattr(request.user, 'rol') and request.user.rol and request.user.rol.nombre == 'Administrador')))
        
        # Lógica para cambiar la contraseña de otro usuario (solo para administradores)
        if target_user != request.user: # Si el usuario objetivo NO es el usuario autenticado
            if not is_request_user_admin:
                # Un usuario común no puede cambiar la contraseña de otro
                raise serializers.ValidationError({"detail": "No tienes permiso para cambiar la contraseña de otro usuario."})
            
            # Si es un administrador cambiando la contraseña de otro, no necesita current_password del target_user
            # Tampoco necesitamos la current_password del administrador que hace la solicitud aquí.
            data.pop('current_password', None) # Asegurarse de que no esté en los validated_data si se envió por error
        
        # Lógica para cambiar la propia contraseña (requiere current_password)
        else: # target_user == request.user (el usuario está cambiando su propia contraseña)
            current_password = data.get("current_password")
            
            # Si el usuario es administrador y está cambiando su propia contraseña,
            # no le requerimos current_password. (Esto es una elección, se podría requerir por seguridad)
            # Aquí, por la consigna, no lo requerimos si es admin.
            if is_request_user_admin and target_user == request.user:
                 data.pop('current_password', None) # Quitarlo si se envió, no es necesario
            elif not current_password:
                raise serializers.ValidationError({"current_password": "Obligatoria para cambiar tu propia contraseña."})
            elif not check_password(current_password, target_user.password): # Usar check_password para comparar
                raise serializers.ValidationError({"current_password": "Contraseña actual incorrecta."})
            
            if data["new_password"] == current_password:
                raise serializers.ValidationError({"new_password": "La nueva contraseña no puede ser igual a la actual."})

        return data
class CustomUserForBitacoraSerializer(serializers.ModelSerializer):
    rol = RolSerializer(read_only=True) # Para obtener el nombre del rol

    class Meta:
        model = Usuario
        fields = ['id', 'username', 'nombre', 'apellido_paterno', 'apellido_materno', 'rol']

class BitacoraSerializer(serializers.ModelSerializer):
    usuario = CustomUserForBitacoraSerializer(read_only=True) # Anida el serializador de usuario

    class Meta:
        model = Bitacora
        fields = '__all__'

class DetalleBitacoraSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetalleBitacora
        fields = '__all__'

class DispositivoMovilSerializer(serializers.ModelSerializer):
    class Meta:
        model = DispositivoMovil
        fields = [
            'id', 'usuario', 'token_fcm', 'modelo_dispositivo',
            'sistema_operativo', 'activo', 'fecha_registro', 'ultima_conexion'
        ]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['usuario_username'] = instance.usuario.username if instance.usuario else None
        rep['usuario_nombre_completo'] = f"{instance.usuario.nombre} {instance.usuario.apellido_paterno}" if instance.usuario else None
        return rep


class NotificacionPushSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificacionPush
        fields = [
            'id', 'usuario', 'dispositivo', 'titulo', 'cuerpo', 'tipo',
            'estado', 'fecha_envio', 'fecha_entrega', 'fecha_lectura',
            'datos_adicionales', 'intento_envio'
        ]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['usuario_username'] = instance.usuario.username if instance.usuario else None
        rep['usuario_nombre_completo'] = f"{instance.usuario.nombre} {instance.usuario.apellido_paterno}" if instance.usuario else None
        rep['dispositivo_modelo'] = instance.dispositivo.modelo_dispositivo if instance.dispositivo else None
        rep['tipo_display'] = instance.get_tipo_display()
        rep['estado_display'] = instance.get_estado_display()
        return rep
from rest_framework import serializers
from .models import Pago, Carrito
from django.contrib.contenttypes.models import ContentType

from rest_framework import serializers
from .models import Pago

class PagoSerializer(serializers.ModelSerializer):
    # Campos de solo lectura para mostrar información relacionada
    usuario_nombre = serializers.SerializerMethodField()
    tipo_pago_display = serializers.CharField(source='get_metodo_pago_display', read_only=True)

    class Meta:
        model = Pago
        fields = [
            'id', 'usuario', 'usuario_nombre', 'monto', 'fecha_pago', 'metodo_pago',
            'tipo_pago_display', 'referencia', 'comprobante', 'observaciones', 'venta'
        ]
        read_only_fields = ['fecha_pago', 'comprobante']  # El comprobante se genera por la señal

    def get_usuario_nombre(self, obj):
        """Retorna el nombre completo del usuario que hizo el pago"""
        if obj.usuario:
            return f"{obj.usuario.nombre} {obj.usuario.apellido_paterno}".strip()
        return None



    

class PromocionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Promocion
        fields = ['id', 'descripcion', 'fecha_inicio', 'fecha_fin', 'descuento']

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        # Se pueden agregar valores adicionales aquí si es necesario, por ejemplo:
        rep['descuento_formateado'] = f"{instance.descuento}%"
        return rep
from rest_framework import serializers
from .models import Carrito, CarritoItem, Producto

class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = ['id', 'nombre', 'descripcion', 'precio', 'imagen', 'stock', 'marca', 'modelo']

class VentaProductoSerializer(serializers.ModelSerializer):
    producto = ProductoSerializer()
    class Meta:
        model = VentaProducto
        fields = ['producto', 'cantidad', 'precio_unitario']

class VentaSerializer(serializers.ModelSerializer):
    items_vendidos = VentaProductoSerializer(many=True, read_only=True)

    class Meta:
        model = Venta
        fields = ['id', 'fecha', 'estado_venta', 'metodo_pago', 'precio_total', 'items_vendidos']

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['precio_total_formateado'] = f"Bs.{instance.precio_total:.2f}"
        return rep



# serializers.py
from rest_framework import serializers
from .models import Carrito, CarritoItem, Producto


class TipoGarantiaSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoGarantia
        fields = '__all__'    

class CarritoItemSerializer(serializers.ModelSerializer):
    # ✅ CORRECCIÓN: Eliminar source='precio_unitario'
    precio_unitario = serializers.ReadOnlyField()
    subtotal = serializers.ReadOnlyField()
    producto_detalle = ProductoSerializer(source='producto', read_only=True)

    class Meta:
        model = CarritoItem
        fields = ['id', 'producto', 'producto_detalle', 'cantidad', 'precio_unitario', 'subtotal']

class CarritoSerializer(serializers.ModelSerializer):
    items = CarritoItemSerializer(many=True, read_only=True)
    total = serializers.ReadOnlyField()
    cantidad_items = serializers.SerializerMethodField()

    class Meta:
        model = Carrito
        fields = ['id', 'user', 'cart_token', 'estado', 'creado', 'actualizado', 'items', 'total', 'cantidad_items']
        read_only_fields = ['cart_token', 'creado', 'actualizado']
    def get_cantidad_items(self, obj):
        """Método para calcular el total de productos en el carrito"""
        return sum(item.cantidad for item in obj.items.all())
    def to_representation(self, instance):
        """Modifica la representación del Carrito para incluir información adicional."""
        representation = super().to_representation(instance)
        
        # Si es un carrito anónimo, asegurarse de incluir el cart_token
        if not instance.user:
            representation['cart_token'] = instance.cart_token
        
        # Eliminar el user si no está autenticado
        if not instance.user:
            representation.pop('user', None)
        
        return representation
    
from rest_framework import serializers
from .models import ReporteEstatico

class ReporteEstaticoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReporteEstatico
        fields = ['id', 'nombre', 'descripcion', 'archivo_pdf', 'archivo_excel', 'fecha_creacion']
from rest_framework import serializers
from .models import ReporteDinamico

class ReporteDinamicoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReporteDinamico
        fields = ['id', 'nombre', 'descripcion', 'usuario', 'parametros', 'archivo_pdf', 'archivo_excel', 'estado', 'fecha_creacion']
from rest_framework import serializers
from .models import ReporteIA

class ReporteIASerializer(serializers.ModelSerializer):
    class Meta:
        model = ReporteIA
        fields = ['id', 'nombre', 'descripcion', 'usuario', 'datos_entrada', 'resultado_ia', 'modelo_ia', 'archivo_pdf', 'archivo_excel', 'estado', 'fecha_creacion']
