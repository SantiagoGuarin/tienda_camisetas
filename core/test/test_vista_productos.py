import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from core.models import Diseño, Usuario, DetallePedido, CamisetaPedido, Pedido
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client

User = get_user_model()

@pytest.mark.django_db
def test_inicio_muestra_productos_populares():
    cliente = User.objects.create_user(username='cliente', password='1234', tipo='cliente')
    disenador = User.objects.create_user(username='dise1', password='1234', tipo='disenador')

    imagen = SimpleUploadedFile("img.jpg", b"abc", content_type="image/jpeg")
    dis1 = Diseño.objects.create(titulo="Diseño 1", descripcion="...", imagen=imagen, disenador=disenador)
    dis2 = Diseño.objects.create(titulo="Diseño 2", descripcion="...", imagen=imagen, disenador=disenador)

    pedido1 = Pedido.objects.create(cliente=cliente)
    pedido2 = Pedido.objects.create(cliente=cliente)

    camiseta = CamisetaPedido.objects.create(talla='M', color='Negro', calidad='Media')
    
    # dis2 debe tener MÁS pedidos para ser el más popular
    DetallePedido.objects.create(pedido=pedido1, diseño=dis2, camiseta_pedido=camiseta, cantidad=1)
    DetallePedido.objects.create(pedido=pedido2, diseño=dis2, camiseta_pedido=camiseta, cantidad=1)
    DetallePedido.objects.create(pedido=pedido1, diseño=dis1, camiseta_pedido=camiseta, cantidad=1)

    client = Client()
    client.login(username='cliente', password='1234')
    response = client.get(reverse('cliente_dashboard'))

    assert response.status_code == 200
    disenos = list(response.context['disenos'])
    assert disenos[0].titulo == "Diseño 2"
    assert disenos[1].titulo == "Diseño 1"

@pytest.mark.django_db
def test_inicio_sin_productos_muestra_mensaje():
    cliente = User.objects.create_user(username='cliente2', password='1234', tipo='cliente')

    client = Client()
    client.login(username='cliente2', password='1234')
    response = client.get(reverse('cliente_dashboard'))

    assert response.status_code == 200
    assert "No hay diseños disponibles por ahora.".encode() in response.content
