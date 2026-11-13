def carrito_contador(request):
    if request.user.is_authenticated and not request.user.is_staff:
        carrito = request.session.get('carrito', {})
        total_unidades = sum(carrito.values())
        return {'total_unidades_carrito': total_unidades}
    return {'total_unidades_carrito': 0}