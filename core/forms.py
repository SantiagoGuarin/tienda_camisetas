from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario, Diseño, Camiseta, Valoracion, Comentario

# Solo una vez
TALLAS = [('S', 'S'), ('M', 'M'), ('L', 'L'), ('XL', 'XL')]
CALIDADES = [('Básica', 'Básica'), ('Premium', 'Premium')]
COLORES = [('Blanco', 'Blanco'), ('Negro', 'Negro'), ('Rojo', 'Rojo'), ('Azul', 'Azul')]

class RegistroForm(UserCreationForm):
    class Meta:
        model = Usuario
        fields = ['username', 'email', 'tipo', 'password1', 'password2']
        labels = {
            'username': 'Nombre de usuario',
            'email': 'Correo electrónico',
            'tipo': 'Tipo de usuario',
            'password1': 'Contraseña',
            'password2': 'Confirmar contraseña',
        }

from django import forms
from .models import Diseño

class DiseñoForm(forms.ModelForm):
    class Meta:
        model = Diseño
        fields = ['titulo', 'descripcion', 'imagen']

    def clean_imagen(self):
        imagen = self.cleaned_data.get('imagen')
        if imagen:
            if not imagen.content_type in ['image/jpeg', 'image/png']:
                raise forms.ValidationError('Solo se permiten imágenes JPG y PNG.')
        return imagen

class AgregarAlCarritoForm(forms.Form):
    talla = forms.ChoiceField(choices=TALLAS)
    color = forms.ChoiceField(choices=COLORES)
    calidad = forms.ChoiceField(choices=CALIDADES)
    cantidad = forms.IntegerField(min_value=1, initial=1)

class CamisetaForm(forms.ModelForm):
    talla = forms.ChoiceField(choices=TALLAS)
    color = forms.ChoiceField(choices=COLORES)
    calidad = forms.ChoiceField(choices=CALIDADES, label='Calidad')

    class Meta:
        model = Camiseta
        fields = ['talla', 'color', 'calidad', 'cantidad']

class ValoracionForm(forms.ModelForm):
    class Meta:
        model = Valoracion
        fields = ['puntuacion']
        labels = {'puntuacion': 'Tu Calificación'}
        widgets = {
            'puntuacion': forms.RadioSelect(
                choices=[(i, f'{i} ⭐') for i in range(1, 6)]
            )
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['puntuacion'].required = True
        self.fields['puntuacion'].empty_label = None


class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ['contenido']
        labels = {'contenido': 'Tu Comentario'}
        widgets = {
            'contenido': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Escribe tu opinión...'})
        }