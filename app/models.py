from django.db import models
from django.contrib.auth.models import AbstractUser, Group
from django.dispatch import receiver
from django.db.models.signals import post_delete

class Rol(models.Model):
    nombre = models.CharField(max_length=50)
    grupo = models.OneToOneField(Group, on_delete=models.CASCADE, related_name='rol')
    def __str__(self): return self.nombre

class Usuario(AbstractUser):
    SEXO_CHOICES = (('M', 'Masculino'), ('F', 'Femenino'))
    nombre = models.CharField(max_length=255)
    apellido_paterno = models.CharField(max_length=255)
    apellido_materno = models.CharField(max_length=255)
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES, blank=True, null=True)
    email = models.EmailField(unique=True, blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE, blank=True, null=True)
    def __str__(self):
        return self.username or f"User {self.id}" 
class Bitacora(models.Model):
    login = models.DateTimeField()
    logout = models.DateTimeField(null=True, blank=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    ip = models.GenericIPAddressField(null=True, blank=True, help_text="Dirección IPv4 o IPv6 del dispositivo")
    device = models.CharField(max_length=255, null=True, blank=True, help_text="Ubicación aproximada (p.ej. 'Ciudad, País' o 'lat,lon')")
    class Meta: db_table = 'bitacora'

class DetalleBitacora(models.Model):
    bitacora = models.ForeignKey(Bitacora, on_delete=models.CASCADE, related_name='detallebitacoras')
    accion = models.CharField(max_length=100)
    fecha = models.DateTimeField()
    tabla = models.CharField(max_length=50)
    class Meta: db_table = 'detallebitacora'




#push notification
class DispositivoMovil(models.Model):
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='dispositivos',
        help_text="Usuario propietario del dispositivo"
    )
    token_fcm = models.TextField(
        unique=True,
        help_text="Token de Firebase Cloud Messaging para enviar notificaciones push"
    )
    modelo_dispositivo = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Ej: iPhone 14, Samsung Galaxy S23"
    )
    sistema_operativo = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="iOS, Android, etc."
    )
    activo = models.BooleanField(
        default=True,
        help_text="Indica si el dispositivo sigue recibiendo notificaciones"
    )
    fecha_registro = models.DateTimeField(auto_now_add=True)
    ultima_conexion = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Última vez que la app se conectó o renovó el token"
    )

    class Meta:
        verbose_name = "Dispositivo Móvil"
        verbose_name_plural = "Dispositivos Móviles"
        ordering = ['-fecha_registro']

    def __str__(self):
        return f"{self.usuario.username} - {self.modelo_dispositivo or 'Dispositivo'}"
class NotificacionPush(models.Model):
    TIPO_NOTIFICACION_CHOICES = [
        ('seguridad', 'Seguridad'),
        ('finanzas', 'Finanzas'),
        ('areas_comunes', 'Áreas Comunes'),
        ('mantenimiento', 'Mantenimiento'),
        ('comunicado', 'Comunicado'),
        ('sistema', 'Sistema'),
    ]

    ESTADO_CHOICES = [
        ('enviada', 'Enviada'),
        ('entregada', 'Entregada'),
        ('leida', 'Leída'),
        ('fallida', 'Fallida'),
    ]

    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='notificaciones_push',
        help_text="Usuario destinatario de la notificación"
    )
    dispositivo = models.ForeignKey(
        DispositivoMovil,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notificaciones_enviadas',
        help_text="Dispositivo al que se envió la notificación"
    )
    titulo = models.CharField(max_length=150)
    cuerpo = models.TextField()
    tipo = models.CharField(max_length=50, choices=TIPO_NOTIFICACION_CHOICES, default='sistema')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='enviada')
    fecha_envio = models.DateTimeField(auto_now_add=True)
    fecha_entrega = models.DateTimeField(null=True, blank=True, help_text="Cuando FCM confirma entrega")
    fecha_lectura = models.DateTimeField(null=True, blank=True)
    datos_adicionales = models.JSONField(
        null=True,
        blank=True,
        help_text="Payload adicional (ej: id de incidente, url, acción)"
    )
    intento_envio = models.PositiveSmallIntegerField(default=1)

    class Meta:
        verbose_name = "Notificación Push"
        verbose_name_plural = "Notificaciones Push"
        ordering = ['-fecha_envio']

    def __str__(self):
        return f"[{self.get_tipo_display()}] {self.titulo} → {self.usuario.username}"
    

class Producto(models.Model):
    id_producto = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    categoria = models.CharField(max_length=50)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
    descripcion = models.TextField()

    def __str__(self):
        return self.nombre
class Promocion(models.Model):
    id_promocion = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=200)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    descuento = models.DecimalField(max_digits=5, decimal_places=2)  # Descuento en porcentaje

    def __str__(self):
        return self.descripcion
class Venta(models.Model):
    id_venta = models.AutoField(primary_key=True)
    fecha = models.DateField()
    cliente = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    precio_total = models.DecimalField(max_digits=10, decimal_places=2)
    promocion = models.ForeignKey(Promocion, on_delete=models.SET_NULL, null=True, blank=True)
    metodo_pago = models.CharField(max_length=50)
    estado_venta = models.CharField(max_length=20)
    ubicacion = models.CharField(max_length=100)
    hora_venta = models.TimeField()
    garantia = models.CharField(max_length=100, null=True, blank=True, help_text="Detalles de la garantía proporcionada con la venta")

    def __str__(self):
        return f"Venta #{self.id_venta} - Cliente {self.cliente.nombre}"

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class Pago(models.Model):
    TIPO_PAGO_CHOICES = [
        ('cuota', 'Cuota'),
        ('reserva', 'Reserva de Área Común'),
        ('multa', 'Multa'),
        ('gasto_comun', 'Gasto Común'),
        ('otro', 'Otro'),
    ]

    METODO_PAGO_CHOICES = [
        ('tarjeta', 'Tarjeta de crédito/débito'),
        ('transferencia', 'Transferencia bancaria'),
        ('efectivo', 'Efectivo'),
        ('qr', 'Pago QR'),
    ]

    # Relación directa con el usuario que realizó el pago
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pagos',
        help_text="Usuario que realizó el pago"
    )
    tipo_pago = models.CharField(max_length=20, choices=TIPO_PAGO_CHOICES,default='cuota')

    # Monto y detalles del pago
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_pago = models.DateTimeField(auto_now_add=True)
    metodo_pago = models.CharField(max_length=50, choices=METODO_PAGO_CHOICES)
    referencia = models.CharField(max_length=100, blank=True, null=True, help_text="N° de transacción, comprobante, etc.")
    comprobante = models.FileField(upload_to='comprobantes/', null=True, blank=True)
    observaciones = models.TextField(blank=True, null=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

class VentaProducto(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        # Verificar que haya suficiente stock para el producto
        if self.producto.stock >= self.cantidad:
            self.producto.stock -= self.cantidad  # Restamos la cantidad vendida
            self.producto.save()  # Guardamos el producto con el stock actualizado
            super().save(*args, **kwargs)  # Guardamos el registro de la venta del producto
        else:
            raise ValueError(f"No hay suficiente stock para el producto {self.producto.nombre}")