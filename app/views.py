from django.utils.crypto import get_random_string
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import api_view
from rest_framework import generics
from django.shortcuts import get_object_or_404
from django.db import models 
from django.shortcuts import render
from rest_framework.decorators import action,permission_classes
from .permissions import IsAdministrador, IsPropietario
from rest_framework.parsers import JSONParser
from rest_framework import viewsets,status
from  django.utils import timezone
from django.core.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.models import Group, Permission as AuthPermission
from rest_framework import serializers
import logging
from django.conf import settings
import stripe 

stripe.api_key = settings.STRIPE_SECRET_KEY

#pago
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
import stripe
from django.db.models import Prefetch
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated


logger = logging.getLogger(__name__)

from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.utils import timezone
import logging
from rest_framework.response import Response
from rest_framework import status





from rest_framework import viewsets
from .models import (
    Rol, Usuario,Bitacora,DetalleBitacora,Pago,
    NotificacionPush,DispositivoMovil)
from  .mixin import BitacoraLoggerMixin
from .serializers import (ChangePasswordSerializer,PagoSerializer,
    RolSerializer,UsuarioSerializer, UsuarioMeSerializer,
    LogoutSerializer,MyTokenPairSerializer,GroupSerializer,
    DispositivoMovilSerializer,NotificacionPushSerializer,BitacoraSerializer,DetalleBitacoraSerializer
   
)
class MyTokenObtainPairView(TokenObtainPairView): 
    serializer_class = MyTokenPairSerializer
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.user  # ← ESTE es el usuario autenticado

        # IP (X-Forwarded-For si hay proxy; si no, REMOTE_ADDR)
        xff = request.META.get('HTTP_X_FORWARDED_FOR')
        ip = (xff.split(',')[0].strip() if xff else request.META.get('REMOTE_ADDR')) or None

        # User-Agent como "device" (o None si vacío)
        device = request.META.get('HTTP_USER_AGENT') or None

        # Registrar login en bitácora
        Bitacora.objects.create(
            usuario=user,
            login=timezone.now(),
            ip=ip,
            device=device
        )
        logger.info('el usuario ingreso al perfil',)

        return Response(serializer.validated_data, status=status.HTTP_200_OK)

from rest_framework.permissions import IsAuthenticated



class RolViewSet(BitacoraLoggerMixin,viewsets.ModelViewSet):
    
    queryset = Rol.objects.all()
    serializer_class = RolSerializer
    # Puedes añadir permisos aquí si necesitas restringir el acceso
    # permission_classes = [IsAuthenticated]
    def create(self, request, *args, **kwargs):
        # Muestra los datos que llegan a la vista
        print("Datos de la solicitud (request.data):", request.data)
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Muestra los datos validados antes de la creación
        print("Datos validados por el serializer:", serializer.validated_data)
        
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class UsuarioViewSet(BitacoraLoggerMixin,viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    filter_backends = [DjangoFilterBackend]  # 👈 AÑADE ESTO
    filterset_fields = ['rol__nombre']  # 👈
    permission_classes = [IsAuthenticated] # Asegúrate de tener la seguridad adecuada

    def get_queryset(self):
        # Obtener el queryset base
        queryset = super().get_queryset()

        # Si el usuario autenticado es un Administrador
        # y no está pidiendo el endpoint 'me' (que maneja su propio serializador)
        # excluye al propio usuario de la lista.
        # Es importante que el usuario autenticado no sea excluido cuando accede a '/me'
        # o cuando un administrador necesita ver su propio perfil en otra parte.

        if self.request.user.is_authenticated:
            # Comprobamos si el usuario tiene un rol asignado y si ese rol es 'Administrador'
            # Asumiendo que el campo 'rol' es un ForeignKey al modelo Rol y tiene un campo 'nombre'
            is_admin = hasattr(self.request.user, 'rol') and \
                       self.request.user.rol and \
                       self.request.user.rol.nombre == 'Administrador'

            # Además, podemos verificar si la acción actual NO es 'retrieve' o 'me'
            # para evitar excluir al administrador de su propio detalle o del endpoint 'me'.
            # La acción 'list' es donde generalmente querrías esta exclusión.
            if is_admin and self.action == 'list':
                queryset = queryset.exclude(id=self.request.user.id)
            
            # Si se está filtrando por rol, también aplicamos ese filtro
            # filterset_fields ya maneja esto, pero si lo haces manualmente...
            # rol_nombre_param = self.request.query_params.get('rol__nombre')
            # if rol_nombre_param:
            #     queryset = queryset.filter(rol__nombre=rol_nombre_param)

        return queryset
   
    @action(
        detail=False,
        methods=['get'],
        url_path='me',
        permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        """
        Endpoint exclusivo para el usuario autenticado.
        """
        # Usa el nuevo serializador específico en lugar del serializador por defecto del ViewSet
        serializer = UsuarioMeSerializer(request.user)
        return Response(serializer.data)
    @action(
        detail=True,
        methods=['post'],
        url_path='set-password',
        # Aquí es donde aplicamos los permisos específicos para esta acción
        permission_classes=[IsAuthenticated] # Todos los autenticados pueden intentar cambiar,
                                             # pero el serializer y has_object_permission filtrarán.
    )
    def set_password(self, request, pk=None):
        print("📥 Payload recibido en backend (set_password):", request.data)

        target_user = get_object_or_404(Usuario, pk=pk) # Obtener el usuario objetivo

        # --- Lógica de Permisos de Vista ---
        # 1. Si el usuario autenticado es un administrador o superusuario:
        #    Puede cambiar la contraseña de CUALQUIER usuario.
        is_request_user_admin = (request.user.is_superuser or
                                 (hasattr(request.user, 'rol') and request.user.rol and request.user.rol.nombre == 'Administrador'))

        if not is_request_user_admin: # Si el usuario no es admin/superuser
            # 2. Solo puede cambiar SU PROPIA contraseña.
            if target_user.id != request.user.id:
                return Response(
                    {"detail": "No tienes permiso para cambiar la contraseña de otro usuario."},
                    status=status.HTTP_403_FORBIDDEN
                )
        # Fin de la lógica de permisos de vista. Si llega aquí, el usuario tiene derecho
        # a intentar cambiar la contraseña de `target_user`.

        # Se pasa el request y el target_user al serializer para la validación detallada
        ser = ChangePasswordSerializer(
            data=request.data,
            context={"request": request, "user": target_user} # Pasar el usuario objetivo al serializer
        )
        ser.is_valid(raise_exception=True)

        # Si pasa validación, se setea la nueva contraseña
        new_pwd = ser.validated_data["new_password"]
        target_user.set_password(new_pwd)
        target_user.save(update_fields=["password"])

        # (Opcional) registrar en bitácora esta acción específica
        try:
            # Reemplaza self._log y self._tabla() con tu implementación si la tienes
            pass # self._log(request, "CAMBIAR_PASSWORD", self._tabla())
        except Exception:
            pass

        # 204 sin contenido (front solo necesita saber que fue OK)
        return Response(status=status.HTTP_204_NO_CONTENT)
    @action(detail=False, methods=['get'], url_path='clientes', url_name='clientes')
    def clientes(self, request):
        clientes=self.queryset.filter(rol__nombre="Cliente")
        serializer=self.get_serializer(clientes,many=True)
        return Response(serializer.data)







class MyTokenObtainPairView(TokenObtainPairView): 
    serializer_class = MyTokenPairSerializer
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.user  # ← ESTE es el usuario autenticado

        # IP (X-Forwarded-For si hay proxy; si no, REMOTE_ADDR)
        xff = request.META.get('HTTP_X_FORWARDED_FOR')
        ip = (xff.split(',')[0].strip() if xff else request.META.get('REMOTE_ADDR')) or None

        # User-Agent como "device" (o None si vacío)
        device = request.META.get('HTTP_USER_AGENT') or None

        # Registrar login en bitácora
        Bitacora.objects.create(
            usuario=user,
            login=timezone.now(),
            ip=ip,
            device=device
        )
        logger.info('el usuario ingreso al perfil',)

        return Response(serializer.validated_data, status=status.HTTP_200_OK)
#vistas
"""
{
  "refresh": "...",
  "password": "..."
}

"""
class LogoutView(APIView):
    """
    Endpoint de **logout**.
    Requiere `{"refresh": "<jwt-refresh-token>"}` en el cuerpo (JSON).
    Blacklistea el refresh token mediante SimpleJWT y registra el logout en Bitacora si corresponde.
    Retorna 204 en caso de éxito.
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]  # fuerza a intentar parsear JSON

    def post(self, request):
        # --- DEBUG: cuerpo crudo + datos parseados + headers ---
        raw = request.body.decode("utf-8", errors="replace")
        headers = {
            k: v for k, v in request.META.items()
            if k.startswith("HTTP_") or k in ("CONTENT_TYPE", "CONTENT_LENGTH")
        }

        #logger.info("=== RAW BODY === %s", raw)
        #logger.info("=== PARSED DATA === %s", request.data)
        #logger.info("=== HEADERS === %s", headers)
    
        # invalidamos el refresh token
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # ——————— Registro de logout ———————
        bit = Bitacora.objects.filter(
            usuario=request.user,
            logout__isnull=True
        ).last()
        if bit:
            print('no se esta cerrando seccion ')
            bit.logout = timezone.now()
            bit.save()

        return Response(status=status.HTTP_204_NO_CONTENT)
class AuthPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthPermission
        fields = ['id', 'codename', 'name']  
class AuthPermissionViewSet(BitacoraLoggerMixin,viewsets.ReadOnlyModelViewSet):
    """
    Lista todas las Django Permissions.
    """
    queryset = AuthPermission.objects.all()
    serializer_class = AuthPermissionSerializer
    permission_classes = [IsAdministrador]  
class GroupViewSet(BitacoraLoggerMixin,viewsets.ModelViewSet):

    queryset = Group.objects.all()
    serializer_class = GroupSerializer

class DispositivoMovilViewSet(BitacoraLoggerMixin,viewsets.ModelViewSet):
    queryset = DispositivoMovil.objects.all()
    serializer_class = DispositivoMovilSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend] 
    filterset_fields = ['activo', 'usuario', 'token_fcm'] # <-- ¡AQUÍ ESTÁ LA CLAVE!
    search_fields = ['modelo_dispositivo', 'sistema_operativo', 'token_fcm']
    ordering_fields = ['fecha_registro', 'ultima_conexion']


class NotificacionPushViewSet(BitacoraLoggerMixin,viewsets.ModelViewSet):
    queryset = NotificacionPush.objects.all()
    serializer_class = NotificacionPushSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['estado', 'tipo', 'usuario']
    search_fields = ['titulo', 'cuerpo']
    ordering_fields = ['fecha_envio', 'fecha_lectura']


class BitacoraViewSet(BitacoraLoggerMixin,viewsets.ModelViewSet):
    queryset=Bitacora.objects.all()
    serializer_class=BitacoraSerializer
    permission_classes=[IsAuthenticated]

class DetalleBitacoraViewSet(BitacoraLoggerMixin,viewsets.ModelViewSet):
    queryset=DetalleBitacora.objects.all()
    serializer_class=DetalleBitacoraSerializer
    permission_classes=[IsAuthenticated]
    
class DetalleBitacoraViewSet(BitacoraLoggerMixin,viewsets.ModelViewSet):
    queryset=DetalleBitacora.objects.all()
    serializer_class=DetalleBitacoraSerializer
    permission_classes=[IsAuthenticated]


import stripe
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from .models import Carrito

from django.db import transaction  # Para garantizar que todo se guarde correctamente en caso de error

class PagoViewSet(BitacoraLoggerMixin, viewsets.ModelViewSet):
    queryset = Pago.objects.all()  # Aquí defines el queryset
    serializer_class = PagoSerializer

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def crear_sesion_stripe(self, request):
        """
        Crea una sesión de Stripe Checkout para pagar un carrito de compras.
        Espera: tipo_objeto ('carrito'), objeto_id (id del carrito), success_url, cancel_url
        """
        tipo_objeto = request.data.get('tipo_objeto')  # 'carrito'
        objeto_id = request.data.get('objeto_id')
        success_url = request.data.get('success_url')
        cancel_url = request.data.get('cancel_url')

        # Verificar si todos los parámetros están presentes
        print(f"Datos recibidos: tipo_objeto={tipo_objeto}, objeto_id={objeto_id}, success_url={success_url}, cancel_url={cancel_url}")

        if not all([tipo_objeto, objeto_id, success_url, cancel_url]):
            print("Faltan parámetros.")
            return Response({"error": "Faltan parámetros."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Comenzamos una transacción para asegurarnos de que todo se ejecute correctamente
            with transaction.atomic():
                # Obtener el carrito
                if tipo_objeto == 'carrito':
                    try:
                        carrito = Carrito.objects.get(id=objeto_id, user=request.user)
                    except Carrito.DoesNotExist:
                        print(f"Carrito no encontrado o no pertenece al usuario: {objeto_id}")
                        return Response({"error": "Carrito no encontrado o no pertenece al usuario."}, status=status.HTTP_404_NOT_FOUND)

                    print(f"Carrito encontrado: {carrito.id}, usuario: {carrito.user.username}")

                    # Crear la venta (o simularla)
                    venta = Venta.objects.create(
                        cliente=request.user,
                        carrito=carrito,
                        cantidad=carrito.items.count(),
                        precio_unitario=carrito.total / carrito.items.count() if carrito.items.count() else 0,
                        precio_total=carrito.total,
                        metodo_pago="tarjeta",
                        estado_venta="pendiente",
                    )

                    # Crear línea de items de carrito para Stripe
                    line_items = []
                    for item in carrito.items.all():
                        line_items.append({
                            'price_data': {
                                'currency': 'usd',  # Puedes cambiar esto a tu moneda local
                                'product_data': {
                                    'name': item.producto.nombre,
                                },
                                'unit_amount': int(item.producto.precio * 100),  # Stripe usa centavos
                            },
                            'quantity': item.cantidad,
                        })

                    # Verificar que los items están siendo procesados correctamente
                    print(f"Líneas de items para Stripe: {line_items}")

                    # Crear sesión de Stripe
                    session = stripe.checkout.Session.create(
                        payment_method_types=['card'],
                        line_items=line_items,
                        mode='payment',
                        success_url=success_url + '?session_id={CHECKOUT_SESSION_ID}',
                        cancel_url=cancel_url,
                        metadata={
                            'tipo_objeto': tipo_objeto,  # 'carrito' en este caso
                            'objeto_id': str(objeto_id),  # ID del carrito
                            'usuario_id': str(request.user.id),
                            'venta_id': str(venta.id)  # Agregar el ID de la venta que se está creando
                        }
                    )

                    print(f"Sesión de Stripe creada: {session.id}, URL: {session.url}")

                    # Devolver el ID de la sesión y la URL para redirigir al usuario
                    return Response({
                        'id': session.id,
                        'url': session.url
                    })

                else:
                    print(f"Tipo de objeto no soportado: {tipo_objeto}")
                    return Response({"error": "Tipo de objeto no soportado."}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print(f"Error al procesar la sesión de Stripe: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


from rest_framework import viewsets
from .models import Promocion
from .serializers import PromocionSerializer

class PromocionViewSet(viewsets.ModelViewSet):
    queryset = Promocion.objects.all()
    serializer_class = PromocionSerializer
         
from .models import Venta
from .serializers import VentaSerializer

class VentaViewSet(viewsets.ModelViewSet):
    queryset = Venta.objects.all()
    serializer_class = VentaSerializer
from .models import VentaProducto
from .serializers import VentaProductoSerializer

class VentaProductoViewSet(viewsets.ModelViewSet):
    queryset = VentaProducto.objects.all()
    serializer_class = VentaProductoSerializer
from .models import Producto
from .serializers import ProductoSerializer

class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer

# views.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Carrito, CarritoItem
from .serializers import CarritoSerializer, CarritoItemSerializer
from django.shortcuts import get_object_or_404
from django.shortcuts import get_object_or_404
from django.utils.crypto import get_random_string
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Carrito, CarritoItem, Producto
from .serializers import CarritoSerializer, CarritoItemSerializer

class CarritoViewSet(viewsets.ModelViewSet):
    queryset = Carrito.objects.all()
    serializer_class = CarritoSerializer

    def get_queryset(self):
        """ Devuelve los carritos del usuario o el carrito anónimo. """
        if self.request.user.is_authenticated:
            return Carrito.objects.filter(user=self.request.user, estado='open')
        cart_token = self.request.query_params.get('cart_token')
        if cart_token:
            return Carrito.objects.filter(cart_token=cart_token, estado='open')
        return Carrito.objects.none()

    def perform_create(self, serializer):
        """ Crear un carrito con un cart_token si no es un carrito autenticado. """
        if not self.request.user.is_authenticated:
            cart_token = self.request.data.get('cart_token', get_random_string(48))
            serializer.save(cart_token=cart_token)
        else:
            serializer.save(user=self.request.user)

    def get_or_create_cart(self):
        """
        Obtiene o crea un carrito para el usuario actual o anónimo.
        Este método NO usa self.get_object() porque es para acciones de lista.
        """
        if self.request.user.is_authenticated:
            # Usuario autenticado: buscar o crear carrito por usuario
            carrito, created = Carrito.objects.get_or_create(
                user=self.request.user,
                estado='open',
                defaults={'cart_token': get_random_string(48)}
            )
        else:
            # Usuario anónimo: usar cart_token de la sesión o crear uno nuevo
            cart_token = self.request.data.get('cart_token')
            
            if not cart_token:
                # Intentar obtener del query params
                cart_token = self.request.query_params.get('cart_token')
            
            if not cart_token:
                # Generar nuevo token
                cart_token = get_random_string(48)
            
            carrito, created = Carrito.objects.get_or_create(
                cart_token=cart_token,
                estado='open',
                defaults={'user': None}
            )
        
        return carrito
    @action(detail=False, methods=['post'], url_path='add_item')
    def add_item(self, request):
        """
        qAgregar un producto al carrito del usuario actual o anónimo.
        URL: POST /api/carritos/add_item/
        Body: { "producto": 1, "cantidad": 2 }
        """
        try:
            carrito = self.get_or_create_cart()
        # Log cart details
            print(f"Carrito: {carrito.id}, Token: {carrito.cart_token}")
        
            producto_id = request.data.get('producto')
            cantidad = int(request.data.get('cantidad', 1))
        
            if not producto_id:
                return Response(
                    {'error': 'El ID del producto es requerido'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
            if cantidad <= 0:
                return Response(
                    {'error': 'La cantidad debe ser mayor a 0'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
            producto = get_object_or_404(Producto, id=producto_id)
        
        # Log producto details
            print(f"Producto: {producto.nombre}, Stock: {producto.stock}, Cantidad: {cantidad}")
        
        # Verificar stock disponible
            if producto.stock < cantidad:
                return Response(
                    {'error': f'Stock insuficiente. Solo hay {producto.stock} unidades disponibles'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Crear o actualizar el carrito item
            item, created = CarritoItem.objects.get_or_create(
                carrito=carrito,
                producto=producto,
                defaults={'cantidad': cantidad}
            )
        
            if not created:
                nueva_cantidad = item.cantidad + cantidad
                if producto.stock < nueva_cantidad:
                    return Response(
                        {'error': f'Stock insuficiente. Solo hay {producto.stock} unidades disponibles'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                item.cantidad = nueva_cantidad
                item.save()

        # Log item details
            print(f"Item agregado al carrito: {item.id}, Cantidad: {item.cantidad}")

            return Response({
                'message': 'Producto agregado al carrito exitosamente',
                'item': CarritoItemSerializer(item).data,
                'carrito': CarritoSerializer(carrito).data,
                'cart_token': carrito.cart_token  # Devolver token para usuarios anónimos
            }, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            print(f"Error: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    

    @action(detail=False, methods=['post'], url_path='remove_item')
    def remove_item(self, request):
        """
        Eliminar un ítem del carrito.
        URL: POST /api/carritos/remove_item/
        Body: { "producto": 1 }
        """
        try:
            carrito = self.get_or_create_cart()
            producto_id = request.data.get('producto')
            
            if not producto_id:
                return Response(
                    {'error': 'El ID del producto es requerido'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            item = get_object_or_404(CarritoItem, carrito=carrito, producto_id=producto_id)
            item.delete()

            return Response({
                'message': 'Producto eliminado del carrito',
                'carrito': CarritoSerializer(carrito).data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'], url_path='update_item')
    def update_item(self, request):
        """
        Actualizar la cantidad de un producto en el carrito.
        URL: POST /api/carritos/update_item/
        Body: { "producto": 1, "cantidad": 3 }
        """
        try:
            carrito = self.get_or_create_cart()
            producto_id = request.data.get('producto')
            cantidad = int(request.data.get('cantidad', 1))
            
            if not producto_id:
                return Response(
                    {'error': 'El ID del producto es requerido'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if cantidad <= 0:
                return Response(
                    {'error': 'La cantidad debe ser mayor a 0'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            item = get_object_or_404(CarritoItem, carrito=carrito, producto_id=producto_id)
            
            # Verificar stock
            if item.producto.stock < cantidad:
                return Response(
                    {'error': f'Stock insuficiente. Solo hay {item.producto.stock} unidades disponibles'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            item.cantidad = cantidad
            item.save()

            return Response({
                'message': 'Cantidad actualizada',
                'item': CarritoItemSerializer(item).data,
                'carrito': CarritoSerializer(carrito).data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'], url_path='my_cart')
    def my_cart(self, request):
        """
        Obtener el carrito actual del usuario.
        URL: GET /api/carritos/my_cart/
        Query params (opcional para anónimos): ?cart_token=xxx
        """
        try:
            carrito = self.get_or_create_cart()
            return Response(CarritoSerializer(carrito).data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'], url_path='clear_cart')
    def clear_cart(self, request):
        """
        Vaciar el carrito completamente.
        URL: POST /api/carritos/clear_cart/
        """
        try:
            carrito = self.get_or_create_cart()
            carrito.items.all().delete()
            
            return Response({
                'message': 'Carrito vaciado exitosamente',
                'carrito': CarritoSerializer(carrito).data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CarritoItemViewSet(viewsets.ModelViewSet):
    queryset = CarritoItem.objects.all()
    serializer_class = CarritoItemSerializer
    
    def get_queryset(self):
        """Filtrar items según el carrito del usuario."""
        if self.request.user.is_authenticated:
            return CarritoItem.objects.filter(carrito__user=self.request.user)
        cart_token = self.request.query_params.get('cart_token')
        if cart_token:
            return CarritoItem.objects.filter(carrito__cart_token=cart_token)
        return CarritoItem.objects.none()



from .models import TipoGarantia
from .serializers import TipoGarantiaSerializer

class TipoGarantiaViewSet(viewsets.ModelViewSet):
    queryset = TipoGarantia.objects.all()
    serializer_class = TipoGarantiaSerializer
from django.utils import timezone

# Webhook to handle Stripe events
@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

    if not sig_header:
        print("No se recibió firma de Stripe")
        return HttpResponse(status=400)

    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        print(f"Payload inválido: {str(e)}")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        print(f"Firma inválida: {str(e)}")
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']

        # Obtener metadata
        metadata = session.get('metadata', {})
        venta_id = metadata.get('venta_id')  # Asegúrate de que esta metadata se esté enviando correctamente
        usuario_id = metadata.get('usuario_id')

        print(f"Webhook recibido - Venta ID: {venta_id}, Usuario ID: {usuario_id}")

        if not all([venta_id, usuario_id]):
            logger.error(f"Metadata incompleta: {metadata}")
            return HttpResponse(status=400)

        try:
            usuario = Usuario.objects.get(id=usuario_id)

            # Monto total (convertir de centavos a unidades)
            monto = session['amount_total'] / 100  # Stripe's amount is in cents
            referencia = session.get('payment_intent') or session.get('id')

            print(f"Procesando pago - Usuario: {usuario.email}, Monto: {monto}, Referencia: {referencia}")

            # Evitar duplicados de pago
            existing_pago = Pago.objects.filter(
                referencia=referencia, 
                usuario=usuario
            ).first()

            if existing_pago:
                logger.info(f"Pago duplicado detectado con referencia: {referencia}")
                return HttpResponse(status=200)

            # Crear la venta (precio_total es el monto total de la venta)
            venta = Venta.objects.create(
                cliente=usuario,  # Correcto: 'cliente' en vez de 'usuario'
                precio_total=monto,  # Correcto: 'precio_total' en vez de 'monto_total'
                estado_venta='pagado',
                metodo_pago='tarjeta',  # Agregar el método de pago
            )

            # Asociar productos a la venta (añadir productos al carrito)
            carrito = Carrito.objects.get(id=venta_id)  # Usar el carrito_id
            for item in carrito.items.all():
                VentaProducto.objects.create(
                    venta=venta,
                    producto=item.producto,
                    cantidad=item.cantidad,
                    precio_unitario=item.precio_unitario
                )

            print(f"Venta creada exitosamente: ID {venta.id}")

            # Actualizar el estado del carrito
            carrito.estado = 'ordered'
            carrito.save()

            # Crear el Pago asociado a esta venta
            pago = Pago.objects.create(
                usuario=usuario,
                tipo_pago='carrito',
                monto=monto,
                metodo_pago='tarjeta',
                referencia=referencia,
                fecha_pago=timezone.now(),
                content_type=ContentType.objects.get_for_model(venta),
                object_id=venta.id
            )

            print(f"Pago creado exitosamente: ID {pago.id} para la venta {venta.id}")

        except Exception as e:
            logger.error(f"Error inesperado en webhook: {str(e)}", exc_info=True)
            return HttpResponse(status=500)

    return HttpResponse(status=200)




    