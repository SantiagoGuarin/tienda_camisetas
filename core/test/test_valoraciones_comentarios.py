import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from core.models import Diseño, CamisetaPedido, Pedido, DetallePedido, Valoracion, Comentario

User = get_user_model()

@pytest.mark.django_db
def test_cliente_puede_valorar_y_comentar_producto_comprado(client):
    cliente = User.objects.create_user(username="cliente1", password="test1234", tipo="cliente")
    client.login(username="cliente1", password="test1234")

    disenador = User.objects.create_user(username="dise1", password="test1234", tipo="disenador")
    diseno = Diseño.objects.create(titulo="Arte", descripcion="Arte urbano", disenador=disenador, imagen="disenos/test.jpg")

    camiseta_pedido = CamisetaPedido.objects.create(talla="M", color="Negro", calidad="Básica")
    pedido = Pedido.objects.create(cliente=cliente, aceptado=True)
    DetallePedido.objects.create(pedido=pedido, diseño=diseno, camiseta_pedido=camiseta_pedido, cantidad=1)

    url = reverse('detalle_diseno', args=[diseno.id])

    # 1. POST para valoración
    response_val = client.post(url, {'puntuacion': 5}, follow=True)
    assert response_val.status_code == 200
    assert Valoracion.objects.filter(cliente=cliente, diseño=diseno).exists()

    # 2. POST para comentario
    response_com = client.post(url, {'contenido': 'Me encantó el diseño'}, follow=True)
    assert response_com.status_code == 200
    assert Comentario.objects.filter(cliente=cliente, diseño=diseno).exists()


@pytest.mark.django_db
def test_cliente_no_puede_comentar_valorar_sin_compra(client):
    cliente = User.objects.create_user(username="cliente2", password="test1234", tipo="cliente")
    disenador = User.objects.create_user(username="dise2", password="test1234", tipo="disenador")
    client.login(username="cliente2", password="test1234")

    diseno = Diseño.objects.create(
        titulo="No Comprado", descripcion="No comprado", disenador=disenador, imagen="disenos/test.jpg"
    )

    url = reverse('detalle_diseno', args=[diseno.id])

    response = client.post(url, {
        'puntuacion': 4,
        'contenido': 'Lo comento aunque no lo compré'
    }, follow=True)

    assert response.status_code == 200
    assert not Valoracion.objects.filter(cliente=cliente, diseño=diseno).exists()
    assert not Comentario.objects.filter(cliente=cliente, diseño=diseno).exists()

    html = response.content.decode('utf-8')
    # ✅ Ahora revisa un texto que sí está en el dashboard del cliente
    assert '🎨 Diseños Disponibles' in html