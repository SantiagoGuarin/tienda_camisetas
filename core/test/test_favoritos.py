import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from core.models import Diseño, Favorito

User = get_user_model()

@pytest.mark.django_db
class TestFavoritos:

    @pytest.fixture
    def cliente(self):
        return User.objects.create_user(username='cliente1', password='1234', tipo='cliente')

    @pytest.fixture
    def diseno(self):
        return Diseño.objects.create(titulo="Diseño de Prueba", descripcion="Test", imagen="test.jpg")

    def test_agregar_favorito_autenticado(self, client, cliente, diseno):
        # Login del cliente
        client.login(username='cliente1', password='1234')

        # Ejecutar la petición para agregar el favorito
        url = reverse('agregar_favorito', args=[diseno.id])
        response = client.get(url)

        # Verificaciones
        assert response.status_code == 302  # Redirección tras éxito
        assert response.url == reverse('cliente_dashboard')  # Redirige correctamente

        # Verificamos que se creó el favorito
        favorito = Favorito.objects.filter(cliente=cliente, diseño=diseno).first()
        assert favorito is not None

    def test_agregar_favorito_no_autenticado(self, client, diseno):
        url = reverse('agregar_favorito', args=[diseno.id])
        response = client.get(url)

        # Redirige al login
        assert response.status_code == 302
        assert response.url.startswith(reverse('login'))

        # No se debe crear ningún favorito
        assert Favorito.objects.count() == 0
