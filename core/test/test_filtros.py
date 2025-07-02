import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from core.models import Diseño, DetallePedido, Pedido, Usuario
from django.test import Client
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()

@pytest.mark.django_db
def test_filtrar_por_disenador_resultado_exitoso():
    # Crear usuarios
    disenador = User.objects.create_user(username="dis1", password="1234", tipo="disenador")
    otro_disenador = User.objects.create_user(username="dis2", password="1234", tipo="disenador")
    cliente = User.objects.create_user(username="cliente", password="1234", tipo="cliente")

    # Crear diseños
    img = SimpleUploadedFile("img.jpg", b"abc", content_type="image/jpeg")
    diseno1 = Diseño.objects.create(titulo="Arte 1", descripcion="cool", imagen=img, disenador=disenador)
    diseno2 = Diseño.objects.create(titulo="Arte 2", descripcion="nice", imagen=img, disenador=otro_disenador)

    # Login y petición filtrada
    client = Client()
    client.login(username="cliente", password="1234")

    url = reverse('cliente_dashboard') + f'?disenador={disenador.id}'
    response = client.get(url)

    assert response.status_code == 200
    assert diseno1.titulo.encode() in response.content
    assert diseno2.titulo.encode() not in response.content


@pytest.mark.django_db
def test_filtrar_por_disenador_sin_resultados():
    # Crear cliente y diseñador sin diseños
    disenador = User.objects.create_user(username="vacio", password="1234", tipo="disenador")
    cliente = User.objects.create_user(username="cliente", password="1234", tipo="cliente")

    # Login y petición filtrada
    client = Client()
    client.login(username="cliente", password="1234")

    url = reverse('cliente_dashboard') + f'?disenador={disenador.id}'
    response = client.get(url)

    assert response.status_code == 200
    assert b"No hay dise\xc3\xb1os disponibles por ahora." in response.content


@pytest.mark.django_db
def test_orden_por_popularidad():
    disenador = User.objects.create_user(username="popu", password="1234", tipo="disenador")
    cliente = User.objects.create_user(username="cliente", password="1234", tipo="cliente")

    img = SimpleUploadedFile("img.jpg", b"abc", content_type="image/jpeg")

    # Diseño popular con más pedidos
    dis1 = Diseño.objects.create(titulo="Más Popular", descripcion="top", imagen=img, disenador=disenador)
    dis2 = Diseño.objects.create(titulo="Menos Popular", descripcion="meh", imagen=img, disenador=disenador)

    pedido = Pedido.objects.create(cliente=cliente)
    for _ in range(5):
        DetallePedido.objects.create(pedido=pedido, diseño=dis1, cantidad=1)

    DetallePedido.objects.create(pedido=pedido, diseño=dis2, cantidad=1)

    client = Client()
    client.login(username="cliente", password="1234")
    response = client.get(reverse('cliente_dashboard'))

    assert response.status_code == 200
    content = response.content.decode()
    assert content.index("Más Popular") < content.index("Menos Popular")
