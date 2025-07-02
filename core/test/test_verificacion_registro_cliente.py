import pytest
from django.core import mail
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
class TestRegistroCliente:

    def test_registro_exitoso_envia_correo(self, client):
        datos_registro = {
            'username': 'cliente1',
            'email': 'cliente1@correo.com',
            'tipo': 'cliente',
            'password1': 'ContraseñaSegura123',
            'password2': 'ContraseñaSegura123'
        }

        response = client.post(reverse('registro'), data=datos_registro)

        # Redirección al dashboard del cliente
        assert response.status_code == 302
        assert response.url == reverse('cliente_dashboard')

        # Verificamos que se haya creado el usuario
        assert User.objects.filter(username='cliente1').exists()

        # Se debe haber enviado un correo
        assert len(mail.outbox) == 1
        email = mail.outbox[0]
        assert "¡Bienvenido a Tienda de Camisetas" in email.subject
        assert "cliente1@correo.com" in email.to
        assert "Bienvenido a Tienda de Camisetas" in email.body or email.alternatives

    def test_registro_falla_por_correo_invalido(self, client):
        datos_registro = {
            'username': 'cliente2',
            'email': 'correo-no-valido',  # Email incorrecto
            'tipo': 'cliente',
            'password1': 'OtraClave123',
            'password2': 'OtraClave123'
        }

        response = client.post(reverse('registro'), data=datos_registro)

        # Se debe quedar en la misma página (registro.html)
        assert response.status_code == 200
        assert "form" in response.context

        # No se debe haber creado el usuario
        assert not User.objects.filter(username='cliente2').exists()

        # No se debe enviar ningún correo
        assert len(mail.outbox) == 0
