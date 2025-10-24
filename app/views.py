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
    @action(detail=False, methods=['get'], url_path='propietarios', url_name='propietarios')
    def propietarios(self, request):
        pass







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


class PagoViewSet(BitacoraLoggerMixin, viewsets.ModelViewSet):
    queryset = Pago.objects.select_related('usuario').all() # Optimized queryset
    serializer_class = PagoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def crear_sesion_stripe(self, request):
        """
        Crea una sesión de Stripe Checkout para pagar una cuota o reserva.
        Espera: tipo_objeto (cuota/reserva), objeto_id, success_url, cancel_url
        """
        tipo_objeto = request.data.get('tipo_objeto')  # 'cuota' o 'reserva'
        objeto_id = request.data.get('objeto_id')
        success_url = request.data.get('success_url')
        cancel_url = request.data.get('cancel_url')

        if not all([tipo_objeto, objeto_id, success_url, cancel_url]):
            return Response({"error": "Faltan parámetros."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Obtener el objeto relacionado
            if tipo_objeto == 'cuota':
                objeto = Cuota.objects.get(id=objeto_id)
                nombre_producto = f"Cuota {objeto.concepto.nombre} - {objeto.periodo.strftime('%Y-%m')}"
                monto = int(objeto.monto * 100)  # Stripe usa centavos
            elif tipo_objeto == 'reserva':
                objeto = Reserva.objects.get(id=objeto_id)
                nombre_producto = f"Reserva {objeto.area_comun.nombre} - {objeto.fecha}"
                monto = int(objeto.area_comun.costo_alquiler * 100)
            else:
                return Response({"error": "Tipo de objeto no soportado."}, status=status.HTTP_400_BAD_REQUEST)

            # Crear sesión de Stripe
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',  # o tu moneda local, ej: 'mxn', 'pen', 'cop'
                        'product_data': {
                            'name': nombre_producto,
                        },
                        'unit_amount': monto,
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=success_url + '?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=cancel_url,
                metadata={
                    'tipo_objeto': tipo_objeto,
                    'objeto_id': str(objeto_id),
                    'usuario_id': str(request.user.id),
                }
            )

            return Response({
                'id': session.id,
                'url': session.url
            })

        except (Cuota.DoesNotExist, Reserva.DoesNotExist):
            return Response({"error": "Objeto no encontrado."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    def get_queryset(self):
        """
        Este método es clave para filtrar los pagos según el rol del usuario.
        - Los administradores ven todos los pagos.
        - Otros usuarios (Propietario, Inquilino, Trabajador, Seguridad) solo ven sus propios pagos.
        """
        user = self.request.user

        # Si el usuario no está autenticado, devuelve un queryset vacío (aunque IsAuthenticated ya lo manejaría)
        if not user.is_authenticated:
            return Pago.objects.none()

        # Comprueba si el usuario tiene un rol y si es 'Administrador'
        # Asumiendo que el campo 'rol' es un ForeignKey al modelo Rol y tiene un campo 'nombre'
        is_admin = hasattr(user, 'rol') and user.rol and user.rol.nombre == 'Administrador'

        if is_admin:
            # Los administradores ven todos los pagos
            return super().get_queryset()
        else:
            # Otros usuarios solo ven los pagos que ellos mismos realizaron
            # El campo 'usuario' en el modelo Pago se relaciona con el Usuario que hizo el pago.
            return super().get_queryset().filter(usuario=user)

    # Puedes añadir lógica adicional para `perform_create`, `perform_update`, `perform_destroy`
    # si necesitas más control sobre quién puede crear, modificar o eliminar pagos.
    # Por ejemplo, quizás solo los administradores puedan crear pagos manualmente,
    # mientras que los pagos de cuotas se crean automáticamente por el sistema.

    def perform_create(self, serializer):
        user = self.request.user
        # Si no es un administrador, asegúrate de que el pago se asocie al usuario que lo crea
        if not (hasattr(user, 'rol') and user.rol and user.rol.nombre == 'Administrador'):
            serializer.save(usuario=user)
        else:
            # Los administradores pueden crear pagos y asociarlos a cualquier usuario
            serializer.save()

    def perform_update(self, serializer):
        user = self.request.user
        instance = serializer.instance
        # Los administradores pueden actualizar cualquier pago
        if hasattr(user, 'rol') and user.rol and user.rol.nombre == 'Administrador':
            serializer.save()
        else:
            # Los usuarios solo pueden actualizar sus propios pagos
            if instance.usuario == user:
                serializer.save()
            else:
                raise PermissionDenied("No tienes permiso para actualizar pagos de otros usuarios.")

    def perform_destroy(self, instance):
        user = self.request.user
        # Los administradores pueden eliminar cualquier pago
        if hasattr(user, 'rol') and user.rol and user.rol.nombre == 'Administrador':
            instance.delete()
        else:
            # Los usuarios solo pueden eliminar sus propios pagos
            if instance.usuario == user:
                instance.delete()
            else:
                raise PermissionDenied("No tienes permiso para eliminar pagos de otros usuarios.")