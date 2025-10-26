from django.db import models
from django.contrib.auth.models import AbstractUser, Group
from django.dispatch import receiver
from django.db.models.signals import post_delete
from django.conf import settings
from django.utils import timezone

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
class TipoGarantia(models.Model):
    tipo = models.CharField(max_length=100, unique=True)  # Tipo de garantía
    duracion = models.PositiveIntegerField(help_text="Duración predeterminada de la garantía en meses", default=12)  # Duración predeterminada
    descripcion = models.TextField(blank=True, null=True, help_text="Descripción adicional del tipo de garantía")  # Detalles o condiciones
    activa = models.BooleanField(default=True, help_text="Indica si este tipo de garantía está activa y disponible para su uso.")
    fecha_inicio = models.DateField(null=True, blank=True, help_text="Fecha de inicio de la vigencia de la garantía.")
    fecha_fin = models.DateField(null=True, blank=True, help_text="Fecha de fin de la vigencia de la garantía.")
    limite_de_reemplazos = models.PositiveIntegerField(null=True, blank=True, help_text="Número máximo de reemplazos cubiertos por esta garantía.")
    exclusiones = models.TextField(blank=True, null=True, help_text="Exclusiones o condiciones especiales de la garantía que no están cubiertas.")
    cobertura = models.TextField(blank=True, null=True, help_text="Descripción de lo que está cubierto por la garantía.")
    documentacion = models.FileField(upload_to='documentos_garantia/', null=True, blank=True, help_text="Archivo PDF o documento relacionado con la garantía.")
    activo_para_ventas = models.BooleanField(default=True, help_text="Indica si este tipo de garantía está disponible para las ventas actuales.")
    
    def __str__(self):
        return f"{self.tipo} - {self.duracion} meses"    

class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    #por defecto lo convierte a string en el JSON para evitar pérdida de precisión.
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    marca = models.CharField(max_length=100, blank=True, null=True)  # Marca del producto
    modelo = models.CharField(max_length=100, blank=True, null=True)
    stock = models.IntegerField()
    descripcion = models.TextField()
    imagen=models.ImageField(upload_to='productos/',blank=True,null=True)
    garantia = models.ForeignKey(TipoGarantia, on_delete=models.SET_NULL, null=True, blank=True, help_text="Tipo de garantía del producto")

    def __str__(self):
        return self.nombre
class Promocion(models.Model):
    descripcion = models.CharField(max_length=200)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    descuento = models.DecimalField(max_digits=5, decimal_places=2)  # Descuento en porcentaje

    def __str__(self):
        return self.descripcion
class Carrito(models.Model):
    ESTADO = (
        ('open', 'Abierto'),
        ('converting', 'Convirtiendo'),
        ('ordered', 'Pedido')
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,  # Cambiar a CASCADE para hacer obligatoria la relación con el usuario
        related_name='carritos'
    )
    cart_token = models.CharField(max_length=64, unique=True, blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADO, default='open')
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'carrito'
        ordering = ['-actualizado']

    def save(self, *args, **kwargs):
        if not self.cart_token:
            self.cart_token = get_random_string(48)
        super().save(*args, **kwargs)

    @property
    def total(self):
        """Calcula el total del carrito."""
        return sum(item.subtotal for item in self.items.select_related('producto').all())

    def __str__(self):
        return f"Carrito de {self.user.username} - {self.estado}"    
class Venta(models.Model):
    fecha = models.DateField(default=timezone.now) 
    cliente = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    carrito = models.OneToOneField(Carrito, on_delete=models.CASCADE, null=True, blank=True)  # Relación con Carrito
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    precio_total = models.DecimalField(max_digits=10, decimal_places=2)
    promocion = models.ForeignKey(Promocion, on_delete=models.SET_NULL, null=True, blank=True)
    metodo_pago = models.CharField(max_length=50)
    estado_venta = models.CharField(max_length=20)

    def __str__(self):
        return f"Venta #{self.id} - Cliente {self.cliente.username}"


from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class Pago(models.Model):
 
    # Relación directa con el usuario que realizó el pago
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pagos',
        help_text="Usuario que realizó el pago"
    )

    # Monto y detalles del pago
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_pago = models.DateTimeField(auto_now_add=True)
    metodo_pago = models.CharField(
        max_length=50, 
        default='tarjeta',  # Establecer 'tarjeta' como valor por defecto
    )
    referencia = models.CharField(max_length=100, blank=True, null=True, help_text="N° de transacción, comprobante, etc.")
    comprobante = models.FileField(upload_to='comprobantes/', null=True, blank=True)
    observaciones = models.TextField(blank=True, null=True)

    # Relación directa con la Venta
    venta = models.ForeignKey(
        'Venta',  # Asegúrate de que la relación esté con la tabla 'Venta'
        on_delete=models.CASCADE,
        related_name='pagos',
        help_text="Venta asociada al pago",null=True, blank=True,
    )

    def __str__(self):
        return f"Pago {self.id} - {self.monto} - Usuario: {self.usuario}"


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
        from django.db import models
from django.conf import settings
from django.utils.crypto import get_random_string







# En models.py - verificar que esté así:
class CarritoItem(models.Model):
    carrito = models.ForeignKey(Carrito, related_name='items', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField(default=1)

    class Meta:
        db_table = 'carrito_item'
        unique_together = ['carrito', 'producto']  # Evitar productos duplicados en el mismo carrito

    @property
    def precio_unitario(self):
        """Retorna el precio del producto."""
        return self.producto.precio

    @property
    def subtotal(self):
        """Calcula el subtotal (cantidad * precio)."""
        return self.cantidad * self.precio_unitario

    def __str__(self):
        return f"{self.cantidad}x {self.producto.nombre} en carrito {self.carrito.id}"




