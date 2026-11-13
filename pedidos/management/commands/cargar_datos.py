from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from pedidos.models import Categoria, Producto


class Command(BaseCommand):
    help = 'Carga datos iniciales de prueba para Cafetería Flores'

    def handle(self, *args, **options):
        encargado, created = User.objects.get_or_create(
            username='encargado',
            defaults={
                'first_name': 'Camila Rojas',
                'email': 'encargado@inacap.cl',
                'is_staff': True,
            }
        )
        if created:
            encargado.set_password('admin1234')
            encargado.save()

        cliente1, created = User.objects.get_or_create(
            username='cliente1',
            defaults={
                'first_name': 'Matías Soto',
                'email': 'matias.soto@inacapmail.cl',
                'is_staff': False,
            }
        )
        if created:
            cliente1.set_password('cliente1234')
            cliente1.save()

        cliente2, created = User.objects.get_or_create(
            username='cliente2',
            defaults={
                'first_name': 'Valentina Muñoz',
                'email': 'valentina.munoz@inacapmail.cl',
                'is_staff': False,
            }
        )
        if created:
            cliente2.set_password('cliente1234')
            cliente2.save()

        categorias_data = [
            ('Cafetería Caliente', 'Café de grano, té e infusiones calientes', True),
            ('Sándwiches y Fajitas', 'Preparaciones saladas listas para llevar', True),
            ('Pastelería y Dulces', 'Queques, medialunas y galletas artesanales', True),
            ('Bebidas y Jugos', 'Bebidas frías, aguas y jugos naturales', True),
            ('Promociones Verano', 'Categoría temporal inactiva', False),
        ]

        categorias = {}
        for nombre, descripcion, activa in categorias_data:
            cat, _ = Categoria.objects.get_or_create(
                nombre=nombre,
                defaults={'descripcion': descripcion, 'activa': activa}
            )
            categorias[nombre] = cat

        productos_data = [
            ('CAF-001', 'Espresso Simple', 'Cafetería Caliente', 1200, 30, True),
            ('CAF-002', 'Americano', 'Cafetería Caliente', 1500, 25, True),
            ('CAF-003', 'Cappuccino', 'Cafetería Caliente', 2000, 20, True),
            ('CAF-004', 'Latte Vainilla', 'Cafetería Caliente', 2300, 15, True),
            ('CAF-005', 'Chocolate Caliente', 'Cafetería Caliente', 2200, 0, True),
            ('CAF-006', 'Té Ceylán', 'Cafetería Caliente', 1000, 40, True),
            ('CAF-007', 'Sándwich Ave Palta', 'Sándwiches y Fajitas', 3200, 12, True),
            ('CAF-008', 'Sándwich Barros Jarpa', 'Sándwiches y Fajitas', 2800, 18, True),
            ('CAF-009', 'Sándwich Churrasco Italiano', 'Sándwiches y Fajitas', 4500, 8, True),
            ('CAF-010', 'Fajita Pollo Crispy', 'Sándwiches y Fajitas', 3800, 0, True),
            ('CAF-011', 'Empanada Pino Horno', 'Sándwiches y Fajitas', 2400, 14, True),
            ('CAF-012', 'Fajita Vegetariana', 'Sándwiches y Fajitas', 3400, 10, False),
            ('CAF-013', 'Medialuna Mantequilla', 'Pastelería y Dulces', 1100, 25, True),
            ('CAF-014', 'Muffin Arándanos', 'Pastelería y Dulces', 1600, 15, True),
            ('CAF-015', 'Brownie Chocolate', 'Pastelería y Dulces', 1800, 10, True),
            ('CAF-016', 'Trozo Queque Zanahoria', 'Pastelería y Dulces', 1700, 0, True),
            ('CAF-017', 'Galletón Avena Pasas', 'Pastelería y Dulces', 1300, 20, True),
            ('CAF-018', 'Agua Mineral Sin Gas 500ml', 'Bebidas y Jugos', 1000, 35, True),
            ('CAF-019', 'Jugo Natural Naranja 350ml', 'Bebidas y Jugos', 2100, 12, True),
            ('CAF-020', 'Bebida Lata 350ml', 'Bebidas y Jugos', 1400, 30, True),
            ('CAF-021', 'Café Helado Frappé', 'Promociones Verano', 2900, 10, True),
        ]

        for codigo, nombre, cat_nombre, precio, stock, disponible in productos_data:
            Producto.objects.get_or_create(
                codigo=codigo,
                defaults={
                    'categoria': categorias[cat_nombre],
                    'nombre': nombre,
                    'precio': precio,
                    'stock': stock,
                    'disponible': disponible,
                }
            )

        self.stdout.write(self.style.SUCCESS('Datos cargados correctamente.'))