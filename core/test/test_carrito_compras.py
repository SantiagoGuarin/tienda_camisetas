import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from core.models import Carrito, ItemCarrito, Diseño
from django.test import Client
from django.urls import reverse

User = get_user_model()

@pytest.mark.django_db
def test_agregar_item_al_carrito_guarda_en_sesion():
    # Crear cliente
    cliente = User.objects.create_user(username="cliente1", password="test1234", tipo="cliente")
    disenador = User.objects.create_user(username="dise1", password="test1234", tipo="disenador")

    imagen_mock = SimpleUploadedFile("img.jpg", b"abc", content_type="image/jpeg")
    diseno = Diseño.objects.create(titulo="Test Diseño", descripcion="Test", imagen=imagen_mock, disenador=disenador)

    client = Client()
    client.login(username="cliente1", password="test1234")

    # Agregar al carrito
    response = client.post(
        reverse("agregar_al_carrito", args=[diseno.id]),
        data={
            "talla": "M",
            "color": "Rojo",
            "calidad": "Básica",
            "cantidad": 2
        },
        follow=True
    )

    assert response.status_code == 200
    carrito = Carrito.objects.filter(cliente=cliente, activo=True).first()
    assert carrito is not None
    assert carrito.items.count() == 1
    item = carrito.items.first()
    assert item.diseño == diseno
    assert item.cantidad == 2
    assert item.color == "Rojo"

@pytest.mark.django_db
def test_carrito_se_vacía_al_perder_sesion():
    cliente = User.objects.create_user(username="cliente2", password="test1234")
    cliente.tipo = "cliente"
    cliente.save()

    disenador = User.objects.create_user(username="dise2", password="test1234")
    disenador.tipo = "disenador"
    disenador.save()

    imagen_mock = SimpleUploadedFile("img.jpg", b"abc", content_type="image/jpeg")
    diseno = Diseño.objects.create(titulo="Otro Diseño", descripcion="Desc", imagen=imagen_mock, disenador=disenador)

    client = Client()
    client.login(username="cliente2", password="test1234")

    # Agrega un ítem
    client.post(
        reverse("agregar_al_carrito", args=[diseno.id]),
        data={
            "talla": "L",
            "color": "Azul",
            "calidad": "Media",
            "cantidad": 1
        }
    )

    # Verifica que el carrito tenga items
    carrito = Carrito.objects.filter(cliente=cliente, activo=True).first()
    assert carrito is not None
    assert carrito.items.count() == 1

    # Simula pérdida de sesión (logout + sesión nueva)
    client.logout()
    client = Client()
    client.login(username="cliente2", password="test1234")

    nuevo_carrito = Carrito.objects.filter(cliente=cliente, activo=True).first()
    if nuevo_carrito:
        assert nuevo_carrito.items.count() == 0