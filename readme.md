# Cafetería Flores - Sistema de Pedidos Web

Aplicación web desarrollada en Django para gestionar pedidos anticipados de estudiantes en la cafetería de Inacap.

## Estado actual del proyecto

* **Funcional:** Modelo de datos y panel de administración (RF-01), autenticación y control de acceso por roles con expiración de sesión (RF-02), catálogo de clientes con búsqueda, filtros y formato CLP (RF-03), listado/detalle/eliminación segura de categorías y productos (RF-04 parcial), carrito en sesión y confirmación atómica de pedidos (RF-05), y seguimiento/cancelación/avance de estados de pedidos (RF-06).
* **No funcional / Pendiente:** La creación y edición de categorías y productos desde las vistas propias del encargado (RF-04) no se encuentra operativa debido a que no se implementaron los formularios (`forms.py` ni vistas de alta/modificación). La gestión de alta y edición de registros puede realizarse mediante el panel de Django Admin (`/admin/`).

## Requisitos previos

* Python 3.11 o superior
* pip

## Instalación y ejecución

1. Clonar el repositorio e ingresar al directorio del proyecto:
   ```bash
   git clone [https://github.com/Dilanlol/p.git](https://github.com/Dilanlol/p.git)
   cd p
   ```

2. Crear y activar entorno virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
   En Windows:
   ```bash
   venv\Scripts\activate
   ```

3. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

4. Ejecutar migraciones:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. Cargar datos iniciales de prueba:
   ```bash
   python manage.py cargar_datos
   ```

6. Iniciar el servidor de desarrollo:
   ```bash
   python manage.py runserver
   ```

7. Acceder en el navegador a `http://127.0.0.1:8000/`.

## Usuarios de prueba

| Rol | Usuario | Contraseña |
| :--- | :--- | :--- |
| Encargado (`is_staff`) | `encargado` | `admin1234` |
| Cliente 1 | `cliente1` | `cliente1234` |
| Cliente 2 | `cliente2` | `cliente1234` |