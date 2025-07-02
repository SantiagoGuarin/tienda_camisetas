from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.db.models import Sum


class Usuario(AbstractUser):
    TIPO_USUARIO = [
        ('cliente', 'Cliente'),
        ('disenador', 'Diseñador'),
        ('proveedor', 'Proveedor'),
        ('admin', 'Administrador'),
    ]
    tipo = models.CharField(max_length=20, choices=TIPO_USUARIO, default='cliente')

    def __str__(self):
        return f"{self.username} ({self.get_tipo_display()})"
        
class Camiseta(models.Model):
    talla = models.CharField(max_length=5)
    color = models.CharField(max_length=20)
    calidad = models.CharField(max_length=50)
    cantidad = models.PositiveIntegerField()
    proveedor = models.ForeignKey(Usuario, on_delete=models.CASCADE, limit_choices_to={'tipo': 'proveedor'})

class Diseño(models.Model):
    titulo = models.CharField(max_length=100)
    descripcion = models.TextField()
    imagen = models.ImageField(upload_to='disenos/')
    disenador = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.titulo

class CamisetaPedido(models.Model):
    talla = models.CharField(max_length=5)
    color = models.CharField(max_length=20)
    calidad = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.talla} - {self.color} - {self.calidad}"
        
class Pedido(models.Model):
    cliente = models.ForeignKey(Usuario, on_delete=models.CASCADE, limit_choices_to={'tipo': 'cliente'})
    fecha = models.DateTimeField(auto_now_add=True)
    aceptado = models.BooleanField(default=False)

    @property
    def puede_aceptarse(self):
        for detalle in self.detalles.all():
            stock = Camiseta.objects.filter(
                talla=detalle.camiseta_pedido.talla,
                color=detalle.camiseta_pedido.color,
                calidad=detalle.camiseta_pedido.calidad
            ).aggregate(total=Sum('cantidad'))['total'] or 0
            if stock < detalle.cantidad:
                return False
        return True

class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='detalles')
    diseño = models.ForeignKey(Diseño, on_delete=models.CASCADE)
    camiseta_pedido = models.ForeignKey(CamisetaPedido, on_delete=models.SET_NULL, null=True, blank=True)
    cantidad = models.PositiveIntegerField()

    
class Carrito(models.Model):
    cliente = models.OneToOneField(Usuario, on_delete=models.CASCADE, limit_choices_to={'tipo': 'cliente'})
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"Carrito de {self.cliente.username}"

class ItemCarrito(models.Model):
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE, related_name='items')
    diseño = models.ForeignKey(Diseño, on_delete=models.CASCADE)
    talla = models.CharField(max_length=5)
    color = models.CharField(max_length=20)
    calidad = models.CharField(max_length=50)  # Por ejemplo: algodón premium, básico, etc.
    cantidad = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.cantidad}x {self.diseño.titulo} ({self.talla})"
    
    def precio_unitario(self):
        precios = {
            'Básica': 10000,
            'Media': 22000,
            'Premium': 35000
        }
        return precios.get(self.calidad, 0)

    def subtotal(self):
        return self.precio_unitario() * self.cantidad

class Favorito(models.Model):
    cliente = models.ForeignKey(Usuario, on_delete=models.CASCADE, limit_choices_to={'tipo': 'cliente'})
    diseño = models.ForeignKey(Diseño, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('cliente', 'diseño')

    def __str__(self):
        return f"{self.cliente.username} ❤ {self.diseño.titulo}"

class Valoracion(models.Model):
    cliente = models.ForeignKey(Usuario, on_delete=models.CASCADE, limit_choices_to={'tipo': 'cliente'})
    diseño = models.ForeignKey(Diseño, on_delete=models.CASCADE, related_name='valoraciones')
    puntuacion = models.IntegerField(choices=[(i, f'{i} ⭐') for i in range(1, 6)])
    fecha = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('cliente', 'diseño')

    def __str__(self):
        return f"{self.cliente.username} → {self.diseño.titulo} ({self.puntuacion}⭐)"


class Comentario(models.Model):
    cliente = models.ForeignKey(Usuario, on_delete=models.CASCADE, limit_choices_to={'tipo': 'cliente'})
    diseño = models.ForeignKey(Diseño, on_delete=models.CASCADE, related_name='comentarios')
    contenido = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.cliente.username}: {self.contenido[:30]}..."
