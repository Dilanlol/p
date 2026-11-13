from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),

    path('catalogo/', views.catalogo, name='catalogo'),

    path('gestion/categorias/', views.gestion_categorias, name='gestion_categorias'),
    path('gestion/categorias/<int:pk>/', views.detalle_categoria, name='detalle_categoria'),
    path('gestion/categorias/<int:pk>/eliminar/', views.eliminar_categoria, name='eliminar_categoria'),

    path('gestion/productos/', views.gestion_productos, name='gestion_productos'),
    path('gestion/productos/<int:pk>/', views.detalle_producto, name='detalle_producto'),
    path('gestion/productos/<int:pk>/eliminar/', views.eliminar_producto, name='eliminar_producto'),

    path('carrito/', views.ver_carrito, name='ver_carrito'),
    path('carrito/agregar/<int:producto_id>/', views.agregar_carrito, name='agregar_carrito'),
    path('carrito/actualizar/<int:producto_id>/', views.actualizar_carrito, name='actualizar_carrito'),
    path('carrito/quitar/<int:producto_id>/', views.quitar_carrito, name='quitar_carrito'),
    path('carrito/vaciar/', views.vaciar_carrito, name='vaciar_carrito'),
    path('carrito/confirmar/', views.confirmar_pedido, name='confirmar_pedido'),

    path('mis-pedidos/', views.mis_pedidos, name='mis_pedidos'),
    path('mis-pedidos/<int:pk>/', views.detalle_pedido, name='detalle_pedido'),
    path('mis-pedidos/<int:pk>/cancelar/', views.cancelar_pedido, name='cancelar_pedido'),

    path('gestion/pedidos/', views.gestion_pedidos, name='gestion_pedidos'),
    path('gestion/pedidos/<int:pk>/avanzar/', views.avanzar_estado_pedido, name='avanzar_estado_pedido'),
]