from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group

from .models import (
    Rol,
    Bitacora, DetalleBitacora,
    DispositivoMovil, NotificacionPush
)

Usuario = get_user_model()


# ---------- ROL & GROUP ----------
class RolInline(admin.StackedInline):
    """
    Permite gestionar el Rol (OneToOne con Group) dentro del admin de Group.
    """
    model = Rol
    can_delete = True
    extra = 0


class CustomGroupAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    inlines = [RolInline]


# Reemplazamos el admin por defecto de Group para mostrar el inline de Rol.
admin.site.unregister(Group)
admin.site.register(Group, CustomGroupAdmin)


@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ("nombre", "grupo")
    search_fields = ("nombre", "grupo__name")
    autocomplete_fields = ("grupo",)


# ---------- USUARIO ----------
@admin.register(Usuario)
class UserAdmin(BaseUserAdmin):
    """
    Admin para el usuario personalizado (hereda AbstractUser).
    Ajustamos fieldsets y list_display para incluir campos extra.
    """
    # Lo que se muestra en el listado
    list_display = (
        "username", "email",
        "nombre", "apellido_paterno", "apellido_materno",
        "sexo", "rol",
        "is_active", "is_staff", "is_superuser",
        "last_login", "date_joined",
    )
    list_select_related = ("rol",)
    list_filter = ("is_active", "is_staff", "is_superuser", "sexo", "rol")
    search_fields = (
        "username", "email",
        "nombre", "apellido_paterno", "apellido_materno",
    )
    ordering = ("-date_joined",)

    # Campos editables al crear/editar
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Información personal", {
            "fields": (
                "nombre", "apellido_paterno", "apellido_materno",
                "sexo", "email", "direccion", "fecha_nacimiento", "rol",
            )
        }),
        ("Permisos", {
            "fields": (
                "is_active", "is_staff", "is_superuser",
                "groups", "user_permissions",
            )
        }),
        ("Fechas importantes", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "username",
                "password1", "password2",
                "nombre", "apellido_paterno", "apellido_materno",
                "sexo", "email", "direccion", "fecha_nacimiento", "rol",
                "is_active", "is_staff", "is_superuser", "groups",
            ),
        }),
    )
    readonly_fields = ("last_login", "date_joined")


# ---------- BITÁCORA ----------
class DetalleBitacoraInline(admin.TabularInline):
    model = DetalleBitacora
    extra = 0
    can_delete = False
    readonly_fields = ("accion", "fecha", "tabla")
    fields = ("accion", "fecha", "tabla")


@admin.register(Bitacora)
class BitacoraAdmin(admin.ModelAdmin):
    list_display = ("id", "usuario", "login", "logout", "ip", "device")
    list_select_related = ("usuario",)
    list_filter = ("login", "logout")
    date_hierarchy = "login"
    search_fields = ("usuario__username", "usuario__email", "ip", "device")
    readonly_fields = ("usuario", "login", "logout", "ip", "device")
    inlines = [DetalleBitacoraInline]

    def has_add_permission(self, request):
        # La bitácora suele ser generada por el sistema (login/logout)
        return False


@admin.register(DetalleBitacora)
class DetalleBitacoraAdmin(admin.ModelAdmin):
    list_display = ("id", "bitacora", "accion", "fecha", "tabla")
    list_select_related = ("bitacora", "bitacora__usuario")
    date_hierarchy = "fecha"
    search_fields = (
        "accion", "tabla",
        "bitacora__usuario__username", "bitacora__usuario__email"
    )
    list_filter = ("tabla",)
    readonly_fields = ("bitacora", "accion", "fecha", "tabla")

    def has_add_permission(self, request):
        return False


# ---------- DISPOSITIVOS ----------
@admin.register(DispositivoMovil)
class DispositivoMovilAdmin(admin.ModelAdmin):
    list_display = (
        "id", "usuario", "modelo_dispositivo",
        "sistema_operativo", "activo",
        "fecha_registro", "ultima_conexion",
    )
    list_select_related = ("usuario",)
    list_filter = ("activo", "sistema_operativo", "fecha_registro")
    search_fields = (
        "usuario__username", "usuario__email",
        "modelo_dispositivo", "token_fcm",
    )
    readonly_fields = ("fecha_registro",)
    autocomplete_fields = ("usuario",)

    @admin.action(description="Desactivar dispositivos seleccionados")
    def desactivar(self, request, queryset):
        updated = queryset.update(activo=False)
        self.message_user(request, f"{updated} dispositivo(s) desactivado(s).")

    @admin.action(description="Activar dispositivos seleccionados")
    def activar(self, request, queryset):
        updated = queryset.update(activo=True)
        self.message_user(request, f"{updated} dispositivo(s) activado(s).")

    actions = ("activar", "desactivar")


# ---------- NOTIFICACIONES PUSH ----------
@admin.register(NotificacionPush)
class NotificacionPushAdmin(admin.ModelAdmin):
    list_display = (
        "id", "usuario", "dispositivo",
        "titulo", "tipo", "estado",
        "fecha_envio", "fecha_entrega", "fecha_lectura",
        "intento_envio",
    )
    list_select_related = ("usuario", "dispositivo")
    list_filter = ("tipo", "estado", "fecha_envio")
    date_hierarchy = "fecha_envio"
    search_fields = (
        "titulo", "cuerpo",
        "usuario__username", "usuario__email",
        "dispositivo__modelo_dispositivo",
    )
    autocomplete_fields = ("usuario", "dispositivo")
    readonly_fields = ("fecha_envio", "fecha_entrega", "fecha_lectura", "intento_envio")

    @admin.action(description="Marcar como leída")
    def marcar_leida(self, request, queryset):
        updated = queryset.update(estado="leida")
        self.message_user(request, f"{updated} notificación(es) marcadas como leídas.")

    @admin.action(description="Marcar como entregada")
    def marcar_entregada(self, request, queryset):
        updated = queryset.update(estado="entregada")
        self.message_user(request, f"{updated} notificación(es) marcadas como entregadas.")

    actions = ("marcar_leida", "marcar_entregada")


# ---------- Branding opcional del sitio admin ----------
admin.site.site_header = "Panel de Administración"
admin.site.site_title = "Admin"
admin.site.index_title = "Administración del sistema"
