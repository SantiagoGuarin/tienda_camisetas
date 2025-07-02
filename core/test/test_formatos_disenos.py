import io
import pytest
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


def create_image_file(format="JPEG", size=(100, 100)):
    image = Image.new("RGB", size, color="white")
    buffer = io.BytesIO()
    image.save(buffer, format=format)
    buffer.seek(0)
    return SimpleUploadedFile(f"test.{format.lower()}", buffer.read(), content_type=f"image/{format.lower()}")


@pytest.mark.django_db
def test_publicar_diseno_valido_jpg():
    client = Client()
    disenador = User.objects.create_user(username='dise1', password='test1234', tipo='disenador')
    client.login(username='dise1', password='test1234')

    archivo = create_image_file("JPEG")

    response = client.post(reverse("publicar_diseno"), {
        'titulo': 'Diseño JPG',
        'descripcion': 'Imagen válida',
        'imagen': archivo
    }, follow=True)

    assert response.status_code == 200
    assert "Panel del Diseñador" in response.content.decode()


@pytest.mark.django_db
def test_publicar_diseno_valido_png():
    client = Client()
    disenador = User.objects.create_user(username='dise2', password='test1234', tipo='disenador')
    client.login(username='dise2', password='test1234')

    archivo = create_image_file("PNG")

    response = client.post(reverse("publicar_diseno"), {
        'titulo': 'Diseño PNG',
        'descripcion': 'Imagen válida',
        'imagen': archivo
    }, follow=True)

    assert response.status_code == 200
    assert "Panel del Diseñador" in response.content.decode()


@pytest.mark.django_db
def test_publicar_diseno_extension_invalida():
    client = Client()
    disenador = User.objects.create_user(username='dise3', password='test1234', tipo='disenador')
    client.login(username='dise3', password='test1234')

    archivo = SimpleUploadedFile("archivo.pdf", b"%PDF-1.4 fake content", content_type="application/pdf")

    response = client.post(reverse("publicar_diseno"), {
        'titulo': 'Archivo PDF',
        'descripcion': 'Debe fallar',
        'imagen': archivo
    })

    assert response.status_code == 200
    assert "Solo se permiten imágenes JPG y PNG" in response.content.decode()


@pytest.mark.django_db
def test_publicar_diseno_tamano_excedido():
    client = Client()
    disenador = User.objects.create_user(username='dise4', password='test1234', tipo='disenador')
    client.login(username='dise4', password='test1234')

    archivo = SimpleUploadedFile("imagen.jpg", b"\x00" * (2_500_000), content_type="image/jpeg")

    response = client.post(reverse("publicar_diseno"), {
        'titulo': 'Archivo grande',
        'descripcion': 'Debe fallar por tamaño',
        'imagen': archivo
    })

    assert response.status_code == 200
    assert "El archivo excede el tamaño máximo de 2MB." in response.content.decode()
