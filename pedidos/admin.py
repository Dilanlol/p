from django.contrib import admin
from .models import Categoria, Producto, Pedido, DetallePedido


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'activa')
    list_filter = ('activa',)
    search_fields = ('nombre', 'descripcion')


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'categoria', 'precio', 'stock', 'disponible', 'creado')
    list_filter = ('categoria', 'disponible')
    search_fields = ('codigo', 'nombre')


class DetallePedidoInline(admin.TabularInline):
    model = DetallePedido
    extra = 0
    readonly_fields = ('subtotal',)


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'fecha', 'hora_retiro', 'estado', 'total')
    list_filter = ('estado', 'fecha')
    search_fields = ('cliente__username', 'cliente__first_name', 'observacion')
    inlines = [DetallePedidoInline]


@admin.register(DetallePedido)
class DetallePedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'pedido', 'producto', 'cantidad', 'precio_unitario', 'subtotal')
    list_filter = ('pedido__estado',)
    search_fields = ('producto__nombre', 'pedido__cliente__username')