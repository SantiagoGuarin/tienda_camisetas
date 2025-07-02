from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Diseño, Camiseta, Pedido, DetallePedido, Carrito, ItemCarrito

admin.site.register(Usuario, UserAdmin)
admin.site.register(Carrito)
admin.site.register(ItemCarrito)

@admin.register(Diseño)
class DiseñoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'disenador')
    readonly_fields = ('vista_previa',)

    def vista_previa(self, obj):
        if obj.imagen:
            return f'<img src="{obj.imagen.url}" width="150" />'
        return "(Sin imagen)"
    vista_previa.allow_tags = True
    vista_previa.short_description = 'Vista previa'
    
@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'fecha')

@admin.register(DetallePedido)
class DetallePedidoAdmin(admin.ModelAdmin):
    list_display = ('pedido', 'diseño', 'mostrar_camiseta', 'cantidad')

    def mostrar_camiseta(self, obj):
        if obj.camiseta_pedido:
            return f"{obj.camiseta_pedido.talla} / {obj.camiseta_pedido.color} / {obj.camiseta_pedido.calidad}"
        return "Sin camiseta"
    
    mostrar_camiseta.short_description = 'Camiseta'

@admin.register(Camiseta)
class CamisetaAdmin(admin.ModelAdmin):
    list_display = ('id', 'proveedor', 'talla', 'color', 'calidad', 'cantidad')
    list_filter = ('proveedor', 'talla', 'color', 'calidad')
    search_fields = ('proveedor__username', 'color', 'calidad')