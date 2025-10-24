
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from django.conf.urls import handler404
from .views import  (RolViewSet, UsuarioViewSet,
      MyTokenObtainPairView,LogoutView,GroupViewSet,AuthPermissionViewSet,
         DispositivoMovilViewSet, NotificacionPushViewSet,BitacoraViewSet,DetalleBitacoraViewSet,
        )

router = DefaultRouter()
router.register(r"roles", RolViewSet)
router.register(r"usuarios", UsuarioViewSet)
router.register(r'grupos',        GroupViewSet,        basename='grupos')
router.register(r'auth-permisos', AuthPermissionViewSet, basename='auth-permisos')

router.register(r'dispositivos', DispositivoMovilViewSet, basename='dispositivo')
router.register(r'notificaciones', NotificacionPushViewSet, basename='notificacion')

router.register(r'bitacoras', BitacoraViewSet, basename='bitacora')
router.register(r'detalle-bitacoras', DetalleBitacoraViewSet, basename='detalle-bitacora')



urlpatterns = [
    path("", include(router.urls)),
    path('login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='auth_logout')
    
]
    