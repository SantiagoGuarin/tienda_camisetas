import pytest
from django.urls import reverse
from django.core import mail
from django.contrib.auth import get_user_model
from core.models import Usuario


@pytest.mark.django_db
def test_recuperar_password_exito(client):
    # Crear usuario válido
    usuario = Usuario.objects.create_user(
        username='cliente_test',
        email='cliente@test.com',
        password='Password123!',
        tipo='cliente'
    )

    # Enviar POST al formulario de recuperación
    response = client.post(reverse('recuperar_password'), {
        'username': 'cliente_test',
        'email': 'cliente@test.com'
    })

    # Validación de redirección al login
    assert response.status_code == 302
    assert response.url == reverse('login')

    # Validación de que se envió un correo
    assert len(mail.outbox) == 1
    assert "Recuperación de Contraseña" in mail.outbox[0].subject
    assert 'cliente@test.com' in mail.outbox[0].to
    assert 'tu nueva contraseña' in mail.outbox[0].body.lower() or 'nueva contraseña' in mail.outbox[0].alternatives[0][0].lower()


@pytest.mark.django_db
def test_recuperar_password_usuario_invalido(client):
    # No existe ningún usuario
    response = client.post(reverse('recuperar_password'), {
        'username': 'noexiste',
        'email': 'nadie@test.com'
    })

    # Se debe mantener en la página y mostrar error
    assert response.status_code == 302
    assert response.url == reverse('recuperar_password')

    # No se debe enviar ningún correo
    assert len(mail.outbox) == 0
