from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.humanize.templatetags.humanize import intcomma
from django.utils.crypto import get_random_string
from django.contrib.auth.hashers import make_password
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Q
from django.db.models import Avg
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from .models import Usuario, Diseño
from .forms import DiseñoForm
from .forms import RegistroForm , CamisetaForm
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum, Count
from .models import Carrito, ItemCarrito, Diseño, Pedido, DetallePedido, CamisetaPedido, Camiseta, Favorito, Valoracion, Comentario
from .forms import AgregarAlCarritoForm, ValoracionForm, ComentarioForm
from django.shortcuts import get_object_or_404
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
# -------------------------------
# VISTA DE LOGIN
# -------------------------------
@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # Redirección según tipo de usuario
            if user.tipo == 'cliente':
                return redirect('cliente_dashboard')
            elif user.tipo == 'disenador':
                return redirect('disenador_dashboard')
            elif user.tipo == 'proveedor':
                return redirect('proveedor_dashboard')
            elif user.tipo == 'admin':
                return redirect('admin_dashboard')
            else:
                messages.error(request, 'Tipo de usuario no válido')
                return redirect('login')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')
    
    return render(request, 'login.html')


# -------------------------------
# VISTA DE REGISTRO (NECESARIA)
# -------------------------------
def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            login(request, usuario)

            # Enviar correo solo si es cliente
            if usuario.tipo == 'cliente':
                html_content = render_to_string('emails/bienvenida_cliente.html', {'usuario': usuario})
                text_content = "Bienvenido a Tienda de Camisetas. Explora los mejores diseños y empieza tu experiencia."

                email = EmailMultiAlternatives(
                    subject="👋 ¡Bienvenido a Tienda de Camisetas!",
                    body=text_content,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[usuario.email]
                )
                email.attach_alternative(html_content, "text/html")
                email.send()

                return redirect('cliente_dashboard')

            elif usuario.tipo == 'disenador':
                return redirect('disenador_dashboard')
            elif usuario.tipo == 'proveedor':
                return redirect('proveedor_dashboard')
            else:
                return redirect('admin:index')
    else:
        form = RegistroForm()
    return render(request, 'registro.html', {'form': form})


# -------------------------------
# DASHBOARDS
# -------------------------------

@login_required
@user_passes_test(lambda u: u.tipo == 'cliente')
def cliente_dashboard(request):
    diseñador_id = request.GET.get('disenador')
    min_rating = request.GET.get('calificacion')

    disenos = (
        Diseño.objects.select_related('disenador')
        .annotate(
            total_pedidos=Count('detallepedido'),
            promedio_puntuacion=Avg('valoraciones__puntuacion')
        )
        .order_by('-total_pedidos', 'titulo')
    )

    if diseñador_id:
        disenos = disenos.filter(disenador__id=diseñador_id)

    if min_rating:
        disenos = disenos.filter(promedio_puntuacion__isnull=False) \
                 .filter(promedio_puntuacion__gte=float(min_rating), 
                         promedio_puntuacion__lt=float(min_rating) + 1)


    diseñadores = Usuario.objects.filter(tipo='disenador')
    favoritos_ids = Favorito.objects.filter(cliente=request.user).values_list('diseño_id', flat=True)

    return render(request, 'cliente_dashboard.html', {
        'disenos': disenos,
        'diseñadores': diseñadores,
        'diseñador_id': diseñador_id,
        'favoritos_ids': list(favoritos_ids),
        'min_rating': str(min_rating) if min_rating else '',
        'rating_options': ['5', '4', '3', '2', '1'],
    })
    
@login_required
@user_passes_test(lambda u: u.tipo == 'disenador')
def disenador_dashboard(request):
    return render(request, 'disenador_dashboard.html')

@login_required
@user_passes_test(lambda u: u.tipo == 'proveedor')
def proveedor_dashboard(request):
    camisetas = Camiseta.objects.filter(proveedor=request.user)

    if request.method == 'POST':
        form = CamisetaForm(request.POST)
        if form.is_valid():
            camiseta = form.save(commit=False)
            camiseta.proveedor = request.user
            camiseta.save()
            messages.success(request, "Camiseta registrada exitosamente.")
            return redirect('proveedor_dashboard')
    else:
        form = CamisetaForm()

    return render(request, 'proveedor_dashboard.html', {
        'form': form,
        'camisetas': camisetas
    })

    
@login_required
@user_passes_test(lambda u: u.tipo == 'admin')
def admin_dashboard(request):
    usuarios = Usuario.objects.all().order_by('tipo', 'username')

    pedidos_pendientes = Pedido.objects.filter(aceptado=False).select_related('cliente').prefetch_related('detalles__camiseta_pedido', 'detalles__diseño')
    pedidos_aceptados = Pedido.objects.filter(aceptado=True).select_related('cliente').prefetch_related('detalles__camiseta_pedido', 'detalles__diseño')

    camisetas = Camiseta.objects.select_related('proveedor').all()

    return render(request, 'admin_dashboard.html', {
        'usuarios': usuarios,
        'pedidos_pendientes': pedidos_pendientes,
        'pedidos_aceptados': pedidos_aceptados,
        'camisetas': camisetas,
    })

    
@login_required
@user_passes_test(lambda u: u.tipo == 'disenador')
def publicar_diseno(request):
    if request.method == 'POST':
        form = DiseñoForm(request.POST, request.FILES)
        if form.is_valid():
            diseno = form.save(commit=False)
            diseno.disenador = request.user
            diseno.save()
            return redirect('disenador_dashboard')
        else:
            print(form.errors)
    else:
        form = DiseñoForm()
    return render(request, 'publicar_diseno.html', {'form': form})


PRECIOS_CALIDAD = {
    'Básica': 10000,
    'Media': 22000,
    'Premium': 35000
}

@login_required
@user_passes_test(lambda u: u.tipo == 'disenador')
def estadisticas_diseno(request):
    detalles = (
        DetallePedido.objects
        .filter(diseño__disenador=request.user)
        .select_related('camiseta_pedido', 'diseño')
    )

    datos = {}

    for detalle in detalles:
        titulo = detalle.diseño.titulo
        calidad = detalle.camiseta_pedido.calidad if detalle.camiseta_pedido else "Básica"
        cantidad = detalle.cantidad
        precio = PRECIOS_CALIDAD.get(calidad, 0)
        subtotal = cantidad * precio

        if titulo not in datos:
            datos[titulo] = {'total_vendido': 0, 'ingresos': 0}

        datos[titulo]['total_vendido'] += cantidad
        datos[titulo]['ingresos'] += subtotal

    return render(request, 'estadisticas_diseno.html', {'estadisticas': datos})
    
@login_required
@user_passes_test(lambda u: u.tipo == 'disenador')
def ver_comision(request):
    detalles = (
        DetallePedido.objects
        .filter(diseño__disenador=request.user)
        .select_related('camiseta_pedido')
    )

    total_ingresos = 0

    for detalle in detalles:
        calidad = detalle.camiseta_pedido.calidad if detalle.camiseta_pedido else "Básica"
        precio_unitario = PRECIOS_CALIDAD.get(calidad, 0)
        total_ingresos += detalle.cantidad * precio_unitario

    comision_total = total_ingresos * 0.10

    return render(request, 'comision_diseno.html', {'comision': comision_total})

    
@login_required
@user_passes_test(lambda u: u.tipo == 'cliente')
def ver_carrito(request):
    carrito = Carrito.objects.filter(cliente=request.user, activo=True).first()
    items = carrito.items.all() if carrito else []

    for item in items:
        item.precio = item.precio_unitario()
        item.subtotal = item.subtotal()

    total = sum(item.subtotal for item in items)

    return render(request, 'ver_carrito.html', {
        'items': items,
        'total': total,
    })

@login_required
@user_passes_test(lambda u: u.tipo == 'cliente')
def agregar_al_carrito(request, diseno_id):
    diseno = get_object_or_404(Diseño, id=diseno_id)

    if request.method == 'POST':
        form = AgregarAlCarritoForm(request.POST)
        if form.is_valid():
            carrito = Carrito.objects.filter(cliente=request.user).first()

            if not carrito:
                carrito = Carrito.objects.create(cliente=request.user)
            else:
                carrito.activo = True
                carrito.save()

            ItemCarrito.objects.create(
                carrito=carrito,
                diseño=diseno,
                talla=form.cleaned_data['talla'],
                color=form.cleaned_data['color'],
                calidad=form.cleaned_data['calidad'],
                cantidad=form.cleaned_data['cantidad']
            )
            messages.success(request, 'Diseño agregado al carrito.')
            return redirect('cliente_dashboard')
    else:
        form = AgregarAlCarritoForm()

    return render(request, 'agregar_al_carrito.html', {'form': form, 'diseno': diseno})

@login_required
@user_passes_test(lambda u: u.tipo == 'cliente')
def eliminar_item_carrito(request, item_id):
    item = get_object_or_404(ItemCarrito, id=item_id, carrito__cliente=request.user)
    item.delete()
    messages.success(request, "Artículo eliminado del carrito.")
    return redirect('ver_carrito')

@login_required
@user_passes_test(lambda u: u.tipo == 'cliente')
def finalizar_compra(request):
    carrito = Carrito.objects.filter(cliente=request.user, activo=True).first()
    if not carrito:
        messages.error(request, "No tienes un carrito activo.")
        return redirect('cliente_dashboard')

    pedido = Pedido.objects.create(cliente=request.user)

    for item in carrito.items.all():
        camiseta = CamisetaPedido.objects.create(
            talla=item.talla,
            color=item.color,
            calidad=item.calidad
        )

        DetallePedido.objects.create(
            pedido=pedido,
            diseño=item.diseño,
            camiseta_pedido=camiseta,
            cantidad=item.cantidad
        )

    carrito.activo = False
    carrito.save()
    carrito.items.all().delete()

    messages.success(request, "¡Compra realizada con éxito!")
    return redirect('cliente_dashboard')
    
@login_required
@user_passes_test(lambda u: u.tipo == 'cliente')
def historial_pedidos(request):
    pedidos = Pedido.objects.filter(cliente=request.user).order_by('-fecha')
    return render(request, 'historial_pedidos.html', {'pedidos': pedidos})

@login_required
@user_passes_test(lambda u: u.tipo == 'admin')
def validar_stock_pedidos(request):
    pedidos = Pedido.objects.all()

    for pedido in pedidos:
        puede_aceptar = True
        for detalle in pedido.detalles.all():
            talla = detalle.camiseta_pedido.talla
            color = detalle.camiseta_pedido.color
            calidad = detalle.camiseta_pedido.calidad
            cantidad = detalle.cantidad

            stock_total = Camiseta.objects.filter(
                talla=talla,
                color=color,
                calidad=calidad
            ).aggregate(total=Sum('cantidad'))['total'] or 0

            if cantidad > stock_total:
                puede_aceptar = False
                break

        pedido.puede_aceptarse = puede_aceptar

    return render(request, 'admin_dashboard.html', {
        'usuarios': Usuario.objects.all().order_by('tipo', 'username'),
        'pedidos': pedidos
    })

def realizar_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)

    if pedido.aceptado:
        messages.warning(request, "Este pedido ya fue aceptado.")
        return redirect('admin_dashboard')

    if not pedido.puede_aceptarse:
        messages.error(request, "No hay suficiente stock para este pedido.")
        return redirect('admin_dashboard')

    for detalle in pedido.detalles.all():
        restar_stock(
            talla=detalle.camiseta_pedido.talla,
            color=detalle.camiseta_pedido.color,
            calidad=detalle.camiseta_pedido.calidad,
            cantidad=detalle.cantidad
        )

    pedido.aceptado = True
    pedido.save()

    html_content = render_to_string('emails/pedido_aceptado.html', {
        'pedido': pedido,
        'cliente': pedido.cliente,
        'detalles': pedido.detalles.all()
    })

    subject = "🎉 ¡Tu pedido ha sido aceptado!"
    text_content = "Gracias por tu compra. Puedes acercarte a la tienda para recoger tu pedido."

    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[pedido.cliente.email]
    )
    email.attach_alternative(html_content, "text/html")
    email.send()

    messages.success(request, "Pedido realizado exitosamente.")
    return redirect('admin_dashboard')

def restar_stock(talla, color, calidad, cantidad):
    camisetas = Camiseta.objects.filter(
        talla=talla,
        color=color,
        calidad=calidad
    ).order_by('id')

    restante = cantidad
    for camiseta in camisetas:
        if restante <= 0:
            break
        if camiseta.cantidad <= restante:
            restante -= camiseta.cantidad
            camiseta.delete()
        else:
            camiseta.cantidad -= restante
            camiseta.save()
            restante = 0

@csrf_exempt
def recuperar_password(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')

        try:
            usuario = Usuario.objects.get(username=username, email=email)
        except Usuario.DoesNotExist:
            messages.error(request, "No se encontró un usuario con esos datos.")
            return redirect('recuperar_password')

        nueva_password = get_random_string(length=10)
        usuario.password = make_password(nueva_password)
        usuario.save()

        html_content = render_to_string('emails/recuperar_password.html', {
            'usuario': usuario,
            'nueva_password': nueva_password
        })
        text_content = f"Hola {usuario.username}, tu nueva contraseña es: {nueva_password}"

        email = EmailMultiAlternatives(
            subject="🔐 Recuperación de Contraseña",
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[usuario.email]
        )
        email.attach_alternative(html_content, "text/html")
        email.send()

        messages.success(request, "Se ha enviado una nueva contraseña a tu correo.")
        return redirect('login')

    return render(request, 'recuperar_password.html')

@login_required
@user_passes_test(lambda u: u.tipo == 'cliente')
def agregar_favorito(request, diseno_id):
    diseno = get_object_or_404(Diseño, id=diseno_id)
    Favorito.objects.get_or_create(cliente=request.user, diseño=diseno)
    messages.success(request, "Diseño agregado a favoritos.")
    return redirect('cliente_dashboard')

@login_required
@user_passes_test(lambda u: u.tipo == 'cliente')
def eliminar_favorito(request, diseno_id):
    Favorito.objects.filter(cliente=request.user, diseño_id=diseno_id).delete()
    messages.success(request, "Diseño eliminado de favoritos.")
    return redirect('cliente_dashboard')

@login_required
@user_passes_test(lambda u: u.tipo == 'cliente')
def ver_favoritos(request):
    favoritos = Favorito.objects.filter(cliente=request.user).select_related('diseño__disenador')
    return render(request, 'favoritos.html', {'favoritos': favoritos})

@login_required
@user_passes_test(lambda u: u.tipo == 'cliente')
def detalle_diseno(request, diseno_id):
    diseno = get_object_or_404(Diseño, id=diseno_id)
    favorito = Favorito.objects.filter(cliente=request.user, diseño=diseno).exists()
    valoracion_existente = Valoracion.objects.filter(cliente=request.user, diseño=diseno).first()
    valoraciones = Valoracion.objects.filter(diseño=diseno).select_related('cliente')
    comentarios = Comentario.objects.filter(diseño=diseno).select_related('cliente').order_by('-fecha')

    ha_comprado = DetallePedido.objects.filter(
        pedido__cliente=request.user,
        pedido__aceptado=True,
        diseño=diseno
    ).exists()

    if request.method == 'POST':
        if not ha_comprado:
            messages.error(request, "Solo puedes valorar o comentar diseños que hayas comprado.")
            return redirect("cliente_dashboard")

        val_form = ValoracionForm(request.POST, instance=valoracion_existente)
        com_form = ComentarioForm()  # ← inicialízalo SIEMPRE aquí

        if 'puntuacion' in request.POST:
            if val_form.is_valid():
                valoracion = val_form.save(commit=False)
                valoracion.cliente = request.user
                valoracion.diseño = diseno
                valoracion.save()
                messages.success(request, "Tu valoración fue actualizada.")
                return redirect('detalle_diseno', diseno_id=diseno.id)

        if 'contenido' in request.POST:
            com_form = ComentarioForm(request.POST)
            if com_form.is_valid():
                comentario = com_form.save(commit=False)
                comentario.cliente = request.user
                comentario.diseño = diseno
                comentario.save()
                messages.success(request, "Comentario publicado.")
                return redirect('detalle_diseno', diseno_id=diseno.id)

    else:
        val_form = ValoracionForm(instance=valoracion_existente)
        com_form = ComentarioForm()

    return render(request, 'detalle_diseno.html', {
        'diseno': diseno,
        'favorito': favorito,
        'valoraciones': valoraciones,
        'comentarios': comentarios,
        'val_form': val_form,
        'com_form': com_form,
        'ha_comprado': ha_comprado,
    })


# -------------------------------
# VISTAS DE CORREOS
# -------------------------------
def vista_email_pedido_aceptado(request):
    pedido_ficticio = {
        'id': 123,
        'fecha': '2025-06-27',
        'cliente': request.user,
        'detalles': [
            {'diseño': {'titulo': 'Diseño Épico'}, 'cantidad': 2, 'camiseta_pedido': {'talla': 'M', 'color': 'Negro', 'calidad': 'Premium'}},
            {'diseño': {'titulo': 'Arte Gráfico'}, 'cantidad': 1, 'camiseta_pedido': {'talla': 'L', 'color': 'Blanco', 'calidad': 'Media'}}
        ]
    }
    return render(request, 'emails/pedido_aceptado.html', {'pedido': pedido_ficticio})

def vista_email_bienvenida(request):
    return render(request, 'emails/bienvenida_cliente.html', {'usuario': request.user})

def vista_email_recuperar(request):
    password_demo = 'NuevaClave123'

    return render(request, 'emails/recuperar_password.html', {
        'usuario': request.user,
        'nueva_password': password_demo
    })