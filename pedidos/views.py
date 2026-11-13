from datetime import datetime, time, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.db.models import Q, ProtectedError
from django.utils import timezone
from django.views.decorators.http import require_POST
from .models import Categoria, Producto, Pedido, DetallePedido
from .decorators import solo_cliente, solo_encargado


@login_required
def inicio(request):
    if request.user.is_staff:
        return redirect('gestion_pedidos')
    return redirect('catalogo')


class CustomLoginView(auth_views.LoginView):
    template_name = 'registration/login.html'
    redirect_authenticated_user = True


class CustomLogoutView(auth_views.LogoutView):
    next_page = '/login/'


@solo_cliente
def catalogo(request):
    productos = Producto.objects.filter(disponible=True, categoria__activa=True).select_related('categoria')
    categorias = Categoria.objects.filter(activa=True)

    busqueda = request.GET.get('q', '').strip()
    categoria_id = request.GET.get('categoria', '').strip()

    if busqueda:
        productos = productos.filter(nombre__icontains=busqueda)
    if categoria_id:
        productos = productos.filter(categoria_id=categoria_id)

    return render(request, 'pedidos/catalogo.html', {
        'productos': productos,
        'categorias': categorias,
        'busqueda': busqueda,
        'categoria_seleccionada': categoria_id,
    })


@solo_encargado
def gestion_categorias(request):
    categorias = Categoria.objects.all()
    return render(request, 'pedidos/gestion_categorias.html', {'categorias': categorias})


@solo_encargado
def detalle_categoria(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    return render(request, 'pedidos/categoria_detalle.html', {'categoria': categoria})


@solo_encargado
def eliminar_categoria(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    if request.method == 'POST':
        try:
            categoria.delete()
            messages.success(request, 'Categoría eliminada correctamente.')
        except ProtectedError:
            messages.error(request, 'No se puede eliminar la categoría porque tiene productos asociados.')
        return redirect('gestion_categorias')
    return render(request, 'pedidos/categoria_confirmar_eliminar.html', {'categoria': categoria})


@solo_encargado
def gestion_productos(request):
    productos = Producto.objects.select_related('categoria').all()
    categorias = Categoria.objects.all()

    busqueda = request.GET.get('q', '').strip()
    categoria_id = request.GET.get('categoria', '').strip()
    disponible = request.GET.get('disponible', '').strip()

    if busqueda:
        productos = productos.filter(Q(nombre__icontains=busqueda) | Q(codigo__icontains=busqueda))
    if categoria_id:
        productos = productos.filter(categoria_id=categoria_id)
    if disponible in ['0', '1']:
        productos = productos.filter(disponible=(disponible == '1'))

    return render(request, 'pedidos/gestion_productos.html', {
        'productos': productos,
        'categorias': categorias,
        'busqueda': busqueda,
        'categoria_seleccionada': categoria_id,
        'disponible_seleccionado': disponible,
    })


@solo_encargado
def detalle_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    return render(request, 'pedidos/producto_detalle.html', {'producto': producto})


@solo_encargado
def eliminar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        try:
            producto.delete()
            messages.success(request, 'Producto eliminado correctamente.')
        except ProtectedError:
            messages.error(request, 'No se puede eliminar el producto porque figura en uno o más pedidos.')
        return redirect('gestion_productos')
    return render(request, 'pedidos/producto_confirmar_eliminar.html', {'producto': producto})


@solo_cliente
def ver_carrito(request):
    carrito = request.session.get('carrito', {})
    items = []
    total_general = 0
    total_unidades = 0

    for prod_id_str, cantidad in list(carrito.items()):
        producto = Producto.objects.filter(pk=int(prod_id_str), disponible=True, categoria__activa=True).first()
        if not producto:
            del carrito[prod_id_str]
            request.session.modified = True
            continue
        subtotal = producto.precio * cantidad
        total_general += subtotal
        total_unidades += cantidad
        items.append({
            'producto': producto,
            'cantidad': cantidad,
            'subtotal': subtotal,
        })

    return render(request, 'pedidos/carrito.html', {
        'items': items,
        'total_general': total_general,
        'total_unidades': total_unidades,
    })


@solo_cliente
@require_POST
def agregar_carrito(request, producto_id):
    producto = get_object_or_404(Producto, pk=producto_id, disponible=True, categoria__activa=True)
    try:
        cantidad = int(request.POST.get('cantidad', 1))
    except ValueError:
        cantidad = 1

    if cantidad < 1:
        messages.error(request, 'La cantidad debe ser al menos 1.')
        return redirect('catalogo')

    if producto.stock <= 0:
        messages.error(request, 'El producto está agotado.')
        return redirect('catalogo')

    carrito = request.session.get('carrito', {})
    clave = str(producto.id)
    cantidad_actual = carrito.get(clave, 0)
    nueva_cantidad = cantidad_actual + cantidad

    if nueva_cantidad > producto.stock:
        messages.error(request, f'No hay stock suficiente para {producto.nombre}. Máximo disponible: {producto.stock}.')
        return redirect('catalogo')

    total_unidades = sum(carrito.values()) - cantidad_actual + nueva_cantidad
    if total_unidades > 10:
        messages.error(request, 'Un pedido no puede superar las 10 unidades en total.')
        return redirect('catalogo')

    carrito[clave] = nueva_cantidad
    request.session['carrito'] = carrito
    messages.success(request, f'{producto.nombre} agregado al carrito.')
    return redirect('catalogo')


@solo_cliente
@require_POST
def actualizar_carrito(request, producto_id):
    producto = get_object_or_404(Producto, pk=producto_id)
    carrito = request.session.get('carrito', {})
    clave = str(producto.id)

    if clave not in carrito:
        return redirect('ver_carrito')

    try:
        cantidad = int(request.POST.get('cantidad', 1))
    except ValueError:
        messages.error(request, 'Cantidad inválida.')
        return redirect('ver_carrito')

    if cantidad < 1:
        del carrito[clave]
        request.session['carrito'] = carrito
        messages.info(request, f'{producto.nombre} eliminado del carrito.')
        return redirect('ver_carrito')

    if cantidad > producto.stock:
        messages.error(request, f'Stock insuficiente para {producto.nombre}. Disponible: {producto.stock}.')
        return redirect('ver_carrito')

    total_unidades = sum(carrito.values()) - carrito[clave] + cantidad
    if total_unidades > 10:
        messages.error(request, 'Un pedido no puede superar las 10 unidades en total.')
        return redirect('ver_carrito')

    carrito[clave] = cantidad
    request.session['carrito'] = carrito
    messages.success(request, 'Cantidad actualizada.')
    return redirect('ver_carrito')


@solo_cliente
@require_POST
def quitar_carrito(request, producto_id):
    carrito = request.session.get('carrito', {})
    clave = str(producto_id)
    if clave in carrito:
        del carrito[clave]
        request.session['carrito'] = carrito
        messages.info(request, 'Producto quitado del carrito.')
    return redirect('ver_carrito')


@solo_cliente
@require_POST
def vaciar_carrito(request):
    request.session['carrito'] = {}
    messages.info(request, 'Carrito vaciado.')
    return redirect('ver_carrito')


@solo_cliente
@require_POST
def confirmar_pedido(request):
    carrito = request.session.get('carrito', {})
    if not carrito:
        messages.error(request, 'El carrito está vacío.')
        return redirect('ver_carrito')

    hora_str = request.POST.get('hora_retiro', '').strip()
    observacion = request.POST.get('observacion', '').strip()

    try:
        hora_retiro = datetime.strptime(hora_str, '%H:%M').time()
    except ValueError:
        messages.error(request, 'Debes ingresar una hora de retiro válida.')
        return redirect('ver_carrito')

    if hora_retiro < time(8, 0) or hora_retiro > time(18, 0):
        messages.error(request, 'La hora de retiro debe estar entre las 08:00 y las 18:00.')
        return redirect('ver_carrito')

    ahora_local = timezone.localtime()
    retiro_dt = timezone.make_aware(datetime.combine(ahora_local.date(), hora_retiro))
    if retiro_dt < ahora_local + timedelta(minutes=20):
        messages.error(request, 'La hora de retiro debe ser al menos 20 minutos después de la hora actual.')
        return redirect('ver_carrito')

    total_unidades = sum(carrito.values())
    if total_unidades > 10:
        messages.error(request, 'El pedido excede el máximo de 10 unidades.')
        return redirect('ver_carrito')

    with transaction.atomic():
        productos_bloqueados = {}
        for prod_id_str, cantidad in carrito.items():
            producto = Producto.objects.select_for_update().filter(
                pk=int(prod_id_str),
                disponible=True,
                categoria__activa=True
            ).first()

            if not producto or producto.stock < cantidad:
                nombre_prod = producto.nombre if producto else f'ID {prod_id_str}'
                messages.error(request, f'Stock insuficiente para "{nombre_prod}". No se creó el pedido.')
                return redirect('ver_carrito')

            productos_bloqueados[producto.id] = (producto, cantidad)

        pedido = Pedido.objects.create(
            cliente=request.user,
            hora_retiro=hora_retiro,
            estado='Pendiente',
            total=0,
            observacion=observacion
        )

        total_pedido = 0
        for producto, cantidad in productos_bloqueados.values():
            subtotal = producto.precio * cantidad
            DetallePedido.objects.create(
                pedido=pedido,
                producto=producto,
                cantidad=cantidad,
                precio_unitario=producto.precio,
                subtotal=subtotal
            )
            producto.stock -= cantidad
            producto.save()
            total_pedido += subtotal

        pedido.total = total_pedido
        pedido.save()

    request.session['carrito'] = {}
    messages.success(request, f'Pedido #{pedido.id} confirmado correctamente.')
    return redirect('mis_pedidos')


@solo_cliente
def mis_pedidos(request):
    pedidos = Pedido.objects.filter(cliente=request.user).prefetch_related('detalles__producto')
    return render(request, 'pedidos/mis_pedidos.html', {'pedidos': pedidos})


@solo_cliente
def detalle_pedido(request, pk):
    pedido = get_object_or_404(Pedido, pk=pk, cliente=request.user)
    return render(request, 'pedidos/pedido_detalle.html', {'pedido': pedido})


@solo_cliente
@require_POST
def cancelar_pedido(request, pk):
    with transaction.atomic():
        pedido = get_object_or_404(Pedido.objects.select_for_update(), pk=pk, cliente=request.user)
        if pedido.estado != 'Pendiente':
            messages.error(request, 'Solo se pueden cancelar pedidos en estado Pendiente.')
            return redirect('mis_pedidos')

        for detalle in pedido.detalles.select_related('producto').all():
            producto = Producto.objects.select_for_update().get(pk=detalle.producto.id)
            producto.stock += detalle.cantidad
            producto.save()

        pedido.estado = 'Cancelado'
        pedido.save()

    messages.success(request, f'Pedido #{pedido.id} cancelado y stock repuesto.')
    return redirect('mis_pedidos')


@solo_encargado
def gestion_pedidos(request):
    hoy = timezone.localdate()
    pedidos = Pedido.objects.filter(fecha__date=hoy).select_related('cliente').prefetch_related('detalles__producto')

    estado_filtro = request.GET.get('estado', '').strip()
    estados_validos = ['Pendiente', 'En preparación', 'Listo', 'Entregado', 'Cancelado']

    if estado_filtro in estados_validos:
        pedidos = pedidos.filter(estado=estado_filtro)

    return render(request, 'pedidos/gestion_pedidos.html', {
        'pedidos': pedidos,
        'hoy': hoy,
        'estados': estados_validos,
        'estado_seleccionado': estado_filtro,
    })


@solo_encargado
@require_POST
def avanzar_estado_pedido(request, pk):
    transiciones = {
        'Pendiente': 'En preparación',
        'En preparación': 'Listo',
        'Listo': 'Entregado',
    }
    pedido = get_object_or_404(Pedido, pk=pk)
    siguiente = transiciones.get(pedido.estado)

    if not siguiente:
        messages.error(request, 'Este pedido no puede avanzar más de estado.')
        return redirect('gestion_pedidos')

    pedido.estado = siguiente
    pedido.save()
    messages.success(request, f'Pedido #{pedido.id} actualizado a "{siguiente}".')
    return redirect('gestion_pedidos')