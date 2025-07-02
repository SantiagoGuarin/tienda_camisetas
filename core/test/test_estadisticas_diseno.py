import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from core.models import Diseño, DetallePedido, CamisetaPedido, Pedido
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client

User = get_user_model()

@pytest.mark.django_db
def test_estadisticas_disenador_con_datos():
    # Crear diseñador
    disenador = User.objects.create_user(username='disenador1', password='test1234', tipo='disenador')

    # Crear cliente y pedido
    cliente = User.objects.create_user(username='cliente1', password='test1234', tipo='cliente')
    pedido = Pedido.objects.create(cliente=cliente)

    # Login como diseñador
    client = Client()
    client.login(username='disenador1', password='test1234')

    # Crear diseño
    imagen_mock = SimpleUploadedFile("test.jpg", b"file_content", content_type="image/jpeg")
    diseno = Diseño.objects.create(titulo="Diseño 1", descripcion="desc", imagen=imagen_mock, disenador=disenador)

    # Asociar pedido con detalle
    camiseta_pedido = CamisetaPedido.objects.create(talla="M", color="Negro", calidad="Media")
    DetallePedido.objects.create(
        pedido=pedido,
        diseño=diseno,
        camiseta_pedido=camiseta_pedido,
        cantidad=3
    )

    # Acceder a estadísticas
    response = client.get(reverse('estadisticas_diseno'))

    assert response.status_code == 200
    contenido = response.context['estadisticas']
    assert "Diseño 1" in contenido
    assert contenido["Diseño 1"]['total_vendido'] == 3
    assert contenido["Diseño 1"]['ingresos'] == 3 * 22000
