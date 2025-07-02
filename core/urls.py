from django.urls import path
from django.urls import path, include
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('registro/', views.registro, name='registro'),
    path('logout/', LogoutView.as_view(next_page='/login/'), name='logout'),

    # Dashboards
    path('cliente/', views.cliente_dashboard, name='cliente_dashboard'),
    path('disenador/', views.disenador_dashboard, name='disenador_dashboard'),
    path('proveedor/', views.proveedor_dashboard, name='proveedor_dashboard'),
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),

    # Funciones del diseñador
    path('disenador/', views.disenador_dashboard, name='disenador_dashboard'),
    path('disenador/publicar/', views.publicar_diseno, name='publicar_diseno'),
    path('disenador/estadisticas/', views.estadisticas_diseno, name='estadisticas_diseno'),
    path('disenador/comision/', views.ver_comision, name='ver_comision'),
    
    # Funciones del cliente
    path('carrito/', views.ver_carrito, name='ver_carrito'),
    path('carrito/finalizar/', views.finalizar_compra, name='finalizar_compra'),
    path('cliente/historial/', views.historial_pedidos, name='historial_pedidos'),
    path('carrito/eliminar/<int:item_id>/', views.eliminar_item_carrito, name='eliminar_item_carrito'),
    path('carrito/agregar/<int:diseno_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('recuperar-password/', views.recuperar_password, name='recuperar_password'),
    path('favoritos/', views.ver_favoritos, name='ver_favoritos'),
    path('favorito/agregar/<int:diseno_id>/', views.agregar_favorito, name='agregar_favorito'),
    path('favorito/eliminar/<int:diseno_id>/', views.eliminar_favorito, name='eliminar_favorito'),
    path('diseno/<int:diseno_id>/', views.detalle_diseno, name='detalle_diseno'),

    # Funciones del proveedor
    path('proveedor/', views.proveedor_dashboard, name='proveedor_dashboard'),

    # Funciones de Administrador
    path('realizar-pedido/<int:pedido_id>/', views.realizar_pedido, name='realizar_pedido'),

    #Vista de los correos
    path('ver-correo/', views.vista_email_pedido_aceptado, name='ver_correo'),
    path('ver-bienvenida/', views.vista_email_bienvenida, name='ver_bienvenida'),
    path('ver-correo-recuperacion/', views.vista_email_recuperar, name='ver_correo_recuperacion'),
]

