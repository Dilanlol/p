# Bitácora de Uso de IA - Cafetería Flores

## Detalle de Requerimientos (Historias de Usuario, Criterios de Aceptación y Estado)

### RF-01: Modelo de datos y administración (Con IA — Implementado)
* **Historia de usuario:** Como administrador del sistema, quiero que los datos de categorías, productos, usuarios, pedidos y detalles se almacenen con integridad referencial y puedan gestionarse desde Django Admin.
* **Criterios de aceptación:**
  * Tablas creadas según tipos, relaciones y restricciones únicas (`nombre` en `Categoria`, `codigo` en `Producto`, `pedido + producto` en `DetallePedido`).
  * `on_delete=models.PROTECT` en relaciones `Categoria -> Producto` y `Producto -> DetallePedido` para impedir borrados con registros dependientes.
  * Inline de `DetallePedido` dentro de `PedidoAdmin`.
  * Comando `cargar_datos` funcional con al menos 4 categorías, 20 productos, 1 encargado y 2 clientes.

### RF-02: Autenticación y roles (Con IA — Implementado)
* **Historia de usuario:** Como usuario de la cafetería, quiero iniciar sesión con mi cuenta para acceder únicamente a las funciones de mi rol.
* **Criterios de aceptación:**
  * Todas las vistas exigen autenticación.
  * Clientes no pueden acceder a rutas `/gestion/...` y encargados no pueden acceder a rutas de cliente (`/catalogo/`, `/carrito/`, `/mis-pedidos/`), recibiendo HTTP 403.
  * Expiración de sesión configurada a 1800 segundos (30 minutos).
  * Barra de navegación muestra nombre de usuario y rol activo.

### RF-03: Catálogo para clientes (Con IA — Implementado)
* **Historia de usuario:** Como cliente, quiero ver los productos disponibles de categorías activas con filtros para elegir qué pedir.
* **Criterios de aceptación:**
  * Filtra `disponible=True` y `categoria__activa=True`.
  * Búsqueda insensible a mayúsculas por nombre y filtro por categoría.
  * Formato de moneda chilena con punto como separador de miles (`$1.500`).
  * Productos con `stock == 0` muestran etiqueta `Agotado` sin botón de compra.

### RF-04: Gestión del catálogo (SIN IA — Implementado parcialmente / No funcional en formularios)
* **Historia de usuario:** Como encargado, quiero administrar categorías y productos desde vistas propias con validaciones de negocio.
* **Criterios de aceptación:**
  * Listado, vista de detalle y eliminación segura con confirmación y captura de `ProtectedError` implementados.
  * Filtro de productos por nombre/código, categoría y disponibilidad implementado.
  * **Limitación actual:** No se desarrollaron los formularios ni las vistas de creación y edición (`crear_categoria`, `editar_categoria`, `crear_producto`, `editar_producto`), por lo que dichas acciones no están operativas desde la interfaz del encargado. De acuerdo con las condiciones de la evaluación, no se utilizó asistencia de IA para suplir esta parte.

### RF-05: Carrito y confirmación del pedido (SIN IA — Implementado)
* **Historia de usuario:** Como cliente, quiero armar mi pedido en un carrito de sesión y confirmarlo con hora de retiro válida.
* **Criterios de aceptación:**
  * Agregar, actualizar cantidad, quitar y vaciar carrito almacenado en `request.session['carrito']`.
  * Límite de stock individual y máximo 10 unidades totales por pedido.
  * Contador global de unidades visible en el menú.
  * Hora de retiro entre 08:00 y 18:00 y >= hora actual + 20 minutos.
  * Transacción atómica (`transaction.atomic` + `select_for_update`) para garantizar confirmación todo o nada, descuento de stock y vaciado de carrito.

### RF-06: Seguimiento de pedidos (Con IA — Implementado)
* **Historia de usuario:** Como cliente quiero revisar y cancelar mis pedidos pendientes, y como encargado quiero gestionar el avance de estados de los pedidos del día.
* **Criterios de aceptación:**
  * Cliente consulta solo sus pedidos (`cliente=request.user`).
  * Cancelación permitida solo en estado `Pendiente`, reponiendo el stock en transacción atómica.
  * Encargado visualiza pedidos del día actual filtrables por estado y avanza estrictamente en secuencia `Pendiente -> En preparación -> Listo -> Entregado`.

---

## Registro de Interacciones con IA

### 1. RF-01: Modelos y comando de carga
* **Prompt utilizado:** "Genera los modelos Django para Cafetería Flores con Categoria, Producto, Pedido y DetallePedido respetando restricciones únicas y protección contra borrado, además de la configuración de Django Admin con inline para DetallePedido."
* **Resultado obtenido:** Estructura inicial de modelos, clases `ModelAdmin` y `TabularInline`.
* **Decisión tomada (Aceptado / Corregido / Descartado):**
  * *Aceptado:* Uso de `models.PROTECT` y `UniqueConstraint` en `DetallePedido`.
  * *Corregido:* La IA generó `on_delete=models.CASCADE` en `Producto -> DetallePedido`, lo cual violaba la regla de negocio de impedir eliminar productos con pedidos. Se corrigió a `models.PROTECT`.
  * *Descartado:* Sugerencia de usar `UUIDField` como clave primaria, descartada para mantener el `id` entero autoincremental del diagrama.

### 2. RF-02: Decoradores de roles y expiración de sesión
* **Prompt utilizado:** "Crea decoradores en Django para separar vistas de clientes y usuarios is_staff, y configura la sesión para expirar a los 30 minutos."
* **Resultado obtenido:** Decoradores basados en `user_passes_test` y parámetros `SESSION_COOKIE_AGE`.
* **Decisión tomada (Aceptado / Corregido / Descartado):**
  * *Aceptado:* Configuración `SESSION_COOKIE_AGE = 1800` y `SESSION_SAVE_EVERY_REQUEST = True`.
  * *Corregido:* `user_passes_test` redirigía al login en bucle cuando un usuario autenticado entraba a una ruta del otro rol. Se reemplazó por decoradores propios que lanzan `PermissionDenied` (403).

### 3. RF-03: Filtro de moneda chilena y vista de catálogo
* **Prompt utilizado:** "Implementa un template tag en Django para formatear enteros como pesos chilenos con separador de miles y una vista de catálogo con filtro por categoría y búsqueda."
* **Resultado obtenido:** Filtro personalizado `clp` y consulta ORM con `icontains`.
* **Decisión tomada (Aceptado / Corregido / Descartado):**
  * *Aceptado:* Uso de `f"${numero:,}".replace(",", ".")` para formato `$1.500`.
  * *Corregido:* Se agregó explícitamente el filtro `categoria__activa=True` en la consulta de `Producto`, ya que la IA solo filtraba `disponible=True`.

### 4. RF-06: Seguimiento y flujo secuencial de estados
* **Prompt utilizado:** "Implementa las vistas de historial de pedidos del cliente con cancelación que repone stock y vista del encargado para filtrar pedidos del día y avanzar estados secuencialmente."
* **Resultado obtenido:** Vistas de listado, cancelación y transición de estados mediante diccionario.
* **Decisión tomada (Aceptado / Corregido / Descartado):**
  * *Aceptado:* Diccionario de transiciones estrictas `{'Pendiente': 'En preparación', 'En preparación': 'Listo', 'Listo': 'Entregado'}` que impide retroceder o saltar estados.
  * *Corregido:* Se envolvió la cancelación del pedido en `transaction.atomic()` con `select_for_update()` para evitar inconsistencias de stock en peticiones concurrentes.

### 5. Nota sobre RF-04 y RF-05 (Sin uso de IA)
* En cumplimiento estricto de las condiciones de evaluación, no se realizaron consultas ni generación de código con agentes de IA para RF-04 ni RF-05. En RF-04 únicamente quedaron implementadas de forma manual las vistas de listado, detalle y eliminación segura, dejando fuera los formularios de creación y edición.