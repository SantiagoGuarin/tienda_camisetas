import io
from PIL import Image
import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

def create_image_file(format="JPEG"):
    image = Image.new("RGB", (100, 100), color="white")
    file_io = io.BytesIO()
    image.save(file_io, format=format)
    file_io.seek(0)
    return SimpleUploadedFile(f"test.{format.lower()}", file_io.read(), content_type=f"image/{format.lower()}")

@pytest.mark.django_db
def test_publicar_diseno_invalido_tipo_mime():
    client = Client()
    disenador = User.objects.create_user(username='dise4', password='test1234', tipo='disenador')
    client.login(username='dise4', password='test1234')

    archivo = SimpleUploadedFile("archivo.jpg", b"contenido falso", content_type="application/pdf")

    response = client.post(reverse("publicar_diseno"), {
        'titulo': 'Error MIME',
        'descripcion': 'Tipo MIME inválido',
        'imagen': archivo
    })

    assert response.status_code == 200
    assert "Envíe una imagen válida" in response.content.decode()


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
def test_publicar_diseno_invalido_pdf():
    client = Client()
    disenador = User.objects.create_user(username='dise3', password='test1234', tipo='disenador')
    client.login(username='dise3', password='test1234')

    archivo = SimpleUploadedFile("archivo.pdf", b"%PDF-1.4 fake content", content_type="application/pdf")

    response = client.post(reverse("publicar_diseno"), {
        'titulo': 'PDF inválido',
        'descripcion': 'Debe fallar',
        'imagen': archivo
    })

    assert response.status_code == 200
    assert "Envíe una imagen válida" in response.content.decode()
