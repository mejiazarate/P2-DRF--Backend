
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from django.conf.urls import handler404
from .views import  (RolViewSet, UsuarioViewSet,ProductoViewSet,stripe_webhook,SendEmailView,VentaModelView,
      MyTokenObtainPairView,LogoutView,GroupViewSet,AuthPermissionViewSet,
         DispositivoMovilViewSet, NotificacionPushViewSet,BitacoraViewSet,DetalleBitacoraViewSet,
          PromocionViewSet, VentaViewSet, VentaProductoViewSet,DialogflowView,
          CarritoViewSet,PagoViewSet, CarritoItemViewSet,TipoGarantiaViewSet,ReporteEstaticoViewSet,ReporteDinamicoViewSet, ReporteIAViewSet,VentasHistoricasAPIView
        )



router = DefaultRouter()
router.register(r'tipo-garantias', TipoGarantiaViewSet)
router.register(r"roles", RolViewSet)
router.register(r"usuarios", UsuarioViewSet)
router.register(r'grupos',        GroupViewSet,        basename='grupos')
router.register(r'auth-permisos', AuthPermissionViewSet, basename='auth-permisos')

router.register(r'dispositivos', DispositivoMovilViewSet, basename='dispositivo')
router.register(r'notificaciones', NotificacionPushViewSet, basename='notificacion')

router.register(r'bitacoras', BitacoraViewSet, basename='bitacora')
router.register(r'detalle-bitacoras', DetalleBitacoraViewSet, basename='detalle-bitacora')
router.register(r'productos', ProductoViewSet)
router.register(r'promociones', PromocionViewSet)
router.register(r'ventas', VentaViewSet)
router.register(r'venta-productos', VentaProductoViewSet)
router.register(r'pagos', PagoViewSet, basename='pago')
router.register(r'carritos', CarritoViewSet, basename='carrito')
router.register(r'carrito-items', CarritoItemViewSet, basename='carritoitem')
router.register(r'reportes/estaticos', ReporteEstaticoViewSet)
router.register(r'reportes/dinamicos',ReporteDinamicoViewSet)
router.register(r'reportes/ia', ReporteIAViewSet)
urlpatterns = [
    path("", include(router.urls)),
    path('login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='auth_logout'),
    path('stripe-webhook/', stripe_webhook, name='stripe_webhook'),
    path('enviar-correo/', SendEmailView.as_view(), name='send_email'),
    path('ventas-historicas/', VentasHistoricasAPIView.as_view(), name='ventas-historicas'),
    path('model/', VentaModelView.as_view(), name='venta-model'),
    path('dialogflow/', DialogflowView.as_view(), name='dialogflow'),
]

    
