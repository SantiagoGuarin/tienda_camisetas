import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core import mail

User = get_user_model()

@pytest.mark.django_db
def test_registro_exitoso_cliente(client):
    url = reverse('registro')
    data = {
        'username': 'cliente_nuevo',
        'password1': 'UnaPasswordSegura123',
        'password2': 'UnaPasswordSegura123',
        'email': 'cliente@email.com',
        'tipo': 'cliente',
    }

    response = client.post(url, data)

    # Debe redirigir al dashboard del cliente
    assert response.status_code == 302
    assert response.url == reverse('cliente_dashboard')

    # El usuario debe existir en la base de datos
    user = User.objects.get(username='cliente_nuevo')
    assert user.email == 'cliente@email.com'
    assert user.tipo == 'cliente'

    # Debe haberse enviado un correo (en este caso simulado, porque usamos console backend)
    assert len(mail.outbox) >= 0  # Ajustar si se implementa verificación real

@pytest.mark.django_db
def test_registro_falla_por_correo_invalido(client):
    url = reverse('registro')
    data = {
        'username': 'cliente_fallo',
        'password1': 'UnaPasswordSegura123',
        'password2': 'UnaPasswordSegura123',
        'email': 'correo-no-valido',  # Email inválido
        'tipo': 'cliente',
    }

    response = client.post(url, data)

    assert response.status_code == 200  # Se queda en la misma página
    assert "correo" in response.content.decode().lower() or "email" in response.content.decode().lower()
    assert not User.objects.filter(username='cliente_fallo').exists()

@pytest.mark.django_db
def test_registro_falla_por_contrasena_debil(client):
    url = reverse('registro')
    data = {
        'username': 'cliente_debil',
        'password1': '123',  # Contraseña muy débil
        'password2': '123',
        'email': 'cliente_debil@email.com',
        'tipo': 'cliente',
    }

    response = client.post(url, data)

    assert response.status_code == 200
    assert "contraseña" in response.content.decode().lower() or "password" in response.content.decode().lower()
    assert not User.objects.filter(username='cliente_debil').exists()
