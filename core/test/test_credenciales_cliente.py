import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import Client

User = get_user_model()

@pytest.mark.django_db
def test_login_cliente_exitoso_redireccion_dashboard():
    # Arrange
    cliente = User.objects.create_user(username='cliente1', password='1234', tipo='cliente')
    client = Client()

    # Act
    response = client.post(reverse('login'), {
        'username': 'cliente1',
        'password': '1234'
    })

    # Assert
    assert response.status_code == 302  # Redirección
    assert response.url == reverse('cliente_dashboard')


@pytest.mark.django_db
def test_login_cliente_contraseña_incorrecta():
    # Arrange
    cliente = User.objects.create_user(username='cliente2', password='correcta', tipo='cliente')
    client = Client()

    # Act
    response = client.post(reverse('login'), {
        'username': 'cliente2',
        'password': 'incorrecta'
    }, follow=True)

    # Assert
    assert response.status_code == 200  # Se queda en la misma página
    assert b'Usuario o contrase' in response.content  # Mensaje de error en español


@pytest.mark.django_db
def test_login_cliente_usuario_inexistente():
    # Arrange
    client = Client()

    # Act
    response = client.post(reverse('login'), {
        'username': 'no_existe',
        'password': 'cualquiera'
    }, follow=True)

    # Assert
    assert response.status_code == 200
    assert b'Usuario o contrase' in response.content
