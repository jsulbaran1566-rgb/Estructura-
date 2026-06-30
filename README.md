# AgroMercado API

API REST para un mercado agrícola de pre-cosecha. Permite gestionar usuarios (productores y compradores), roles, tipos de documento, categorías, lotes de producto y reservas, además de consultar el historial de movimientos, compras y ventas.

## Tecnologías

- **FastAPI** — framework para construir la API
- **SQLAlchemy** — ORM para hablar con la base de datos
- **PostgreSQL** (`psycopg2`) — motor de base de datos
- **Pydantic** — validación de los datos que llegan en las peticiones
- **Starlette** — middleware de logging de peticiones
- **CORS Middleware** — habilitado para `http://127.0.0.1:8000`

## Estructura del proyecto

```
scr/
├── main.py                          # Punto de entrada: app, middlewares, manejadores de errores, registro de rutas
├── Utilidades/
│   └── respuesta.py                 # Funciones respuesta_ok / respuesta_error (formato estándar de respuesta)
├── Conexion/
│   └── database.py                  # Engine, SessionLocal, Base y get_db() para PostgreSQL
├── Modelos/
│   └── models.py                    # Tablas SQLAlchemy: TipoDocumento, Rol, Proveedor, Usuario, Categoria,
│                                     # Lote, Reserva, HistorialSeguimiento, Compra, Venta, HistorialReserva
├── Esquemas/
│   └── Esquemas.py                  # Schemas Pydantic de entrada/edición para cada entidad
├── Excepciones/
│   ├── excepciones_categorias.py
│   ├── excepciones_lotes.py
│   ├── excepciones_reservas.py
│   └── excepciones_usuarios.py
├── Controladores/
│   ├── controladores_categorias.py
│   ├── controladores_historial.py
│   ├── controladores_lotes.py
│   ├── controladores_reservas.py
│   ├── controladores_roles.py
│   ├── controladores_tipos_documento.py
│   └── controladores_usuarios.py
└── Rutas/
    ├── rutas_categorias.py
    ├── rutas_historial.py
    ├── rutas_lotes.py
    ├── rutas_reservas.py
    ├── rutas_roles.py
    ├── rutas_tipos_documento.py
    └── rutas_usuarios.py
```

## Modelo de datos

| Tabla | Descripción |
|---|---|
| `tipos_documento` | Catálogo de tipos de documento de identidad (código de hasta 4 caracteres + nombre) |
| `roles` | Roles del sistema (nombre, descripción, permisos) |
| `proveedores` | Proveedores externos (nombre, tipo, ciudad, contacto, estado Activo/Inactivo) |
| `usuarios` | Usuarios del sistema (productores y compradores), con `tipo_documento`, `rol_id`, estado y fecha de registro |
| `categorias` | Categorías de producto (clave primaria = nombre) |
| `lotes` | Lotes de producto agrícola asociados a un productor y una categoría, con cantidad, kg reservados y precio por kg |
| `reservas` | Reservas de un comprador sobre un lote, con estado (`Pendiente`, `Confirmada`, `Cancelada`, `Entregada`) |
| `historial_seguimiento` | Bitácora de acciones realizadas sobre los lotes |
| `historial_reservas` | Bitácora de cada cambio de estado de una reserva |
| `compras` | Registro histórico de compras |
| `ventas` | Registro histórico de ventas |

Todas las relaciones usan claves foráneas con `ON UPDATE`/`ON DELETE` definidos explícitamente (`RESTRICT`, `CASCADE` o `SET NULL` según el caso), y varias tablas tienen `CheckConstraint` para validar campos de estado y cantidades positivas.

## Instalación

1. Clonar el repositorio y entrar a la carpeta del proyecto.
2. Crear un entorno virtual (opcional, pero recomendado):
   ```
   python -m venv venv
   venv\Scripts\activate      # Windows
   source venv/bin/activate   # Linux / Mac
   ```
3. Instalar las dependencias:
   ```
   pip install -r requirements.txt
   ```
   Incluye `fastapi`, `uvicorn`, `sqlalchemy`, `psycopg2-binary` (driver de PostgreSQL) y `pydantic[email]` (necesario porque los esquemas usan `EmailStr`).

## Configuración de la base de datos

En `Conexion/database.py` se define la conexión a PostgreSQL:

```python
SQLALCHEMY_DATABASE_URL = "postgresql+psycopg2://postgres:1234@localhost/agro_mercado"
```

Antes de ejecutar el proyecto:
- Crear en PostgreSQL una base de datos llamada `agro_mercado`.
- Ajustar usuario y contraseña según tu instalación.
- Las tablas se crean automáticamente al arrancar la aplicación, gracias a `Base.metadata.create_all(bind=engine)` en `main.py`. No hay sistema de migraciones (como Alembic), así que los cambios en `models.py` requieren recrear la base de datos.

## Ejecutar el proyecto

Como el código vive dentro de la carpeta `scr`, la aplicación se levanta indicando ese directorio:

```
uvicorn main:app --app-dir scr --reload
```

La documentación interactiva queda disponible en `http://localhost:8000/docs`.

## Formato de respuesta

Todas las respuestas de la API siguen la misma estructura, definida en `Utilidades/respuesta.py`:

```json
{
  "success": true,
  "message": "Usuario obtenido",
  "data": { "id": 1, "nombre": "Ana", "rol": "Productor" },
  "error": null
}
```

En caso de error:

```json
{
  "success": false,
  "message": "No existe un usuario con el id 99",
  "data": null,
  "error": "No existe un usuario con el id 99"
}
```

Los errores no controlados (excepciones genéricas) son capturados por un manejador global en `main.py` y devuelven un código HTTP 500 con `"ok": false`.

## Endpoints principales

### Usuarios (`/usuarios`)
- `GET /usuarios` — listar usuarios (filtros opcionales: `rol`, `estado`)
- `GET /usuarios/compradores` — listar usuarios con rol Comprador (filtro opcional: `estado`)
- `GET /usuarios/productores` — listar usuarios con rol Productor (filtro opcional: `estado`)
- `GET /usuarios/{nombre}` — buscar usuario(s) por coincidencia parcial de nombre
- `POST /usuarios` — registrar un usuario
- `PUT /usuarios/{id}` — editar nombre, teléfono, dirección, ciudad, rol y/o estado
- `DELETE /usuarios/{id}` — eliminar usuario (requiere `?confirmar=true`; falla si tiene lotes activos)

### Roles (`/roles`)
- `GET /roles` — listar roles
- `GET /roles/{id}` — obtener rol por id
- `POST /roles` — registrar un rol
- `PUT /roles/{id}` — editar nombre, descripción y/o permisos
- `DELETE /roles/{id}` — eliminar rol (requiere `?confirmar=true`; falla si tiene usuarios asignados)

### Tipos de documento (`/tipos_documento`)
- `GET /tipos_documento` — listar tipos de documento
- `GET /tipos_documento/{codigo}` — obtener tipo de documento por código (CC, NIT, CE, PP...)
- `POST /tipos_documento` — registrar un tipo de documento
- `PUT /tipos_documento/{codigo}` — editar el nombre
- `DELETE /tipos_documento/{codigo}` — eliminar (requiere `?confirmar=true`; falla si tiene usuarios asignados)

### Categorías (`/categorias`)
- `GET /categorias` — listar categorías
- `GET /categorias/{nombre}/lotes` — lotes de una categoría (filtros opcionales: `cantidad_min`, `solo_activos`; soporta paginación con `limite` y orden con `ordenar`)
- `POST /categorias` — crear una categoría
- `PUT /categorias/{nombre}` — renombrar una categoría (la FK con CASCADE actualiza los lotes)
- `DELETE /categorias/{nombre}` — eliminar categoría (falla si tiene lotes asociados, FK RESTRICT)

### Lotes (`/lotes`)
- `GET /lotes` — listar lotes (filtros opcionales: `categoria`, `estado`, `productor_id`)
- `GET /lotes/{producto}` — buscar lote(s) por coincidencia parcial de nombre de producto
- `POST /lotes` — registrar un lote (el `productor_id` debe ser un usuario con rol Productor)
- `PUT /lotes/{id}` — editar producto, cantidad, categoría, precio_kg, estado y/o fecha_cosecha
- `DELETE /lotes/{id}` — eliminar lote (requiere `?confirmar=true`; falla si tiene reservas activas)

### Reservas (`/reservas`)
- `GET /reservas` — listar reservas (filtros opcionales: `estado`, `comprador_id`, `lote_id`, `fecha_desde`, `fecha_hasta`)
- `GET /reservas/fechas` — buscar reservas por rango de fechas (`fecha_desde` y `fecha_hasta` obligatorios, formato `YYYY-MM-DD`)
- `POST /reservas` — crear una reserva (descuenta kg del lote y registra el estado inicial en el historial)
- `PUT /reservas/{id}/estado` — actualizar comprador_id, fecha y/o estado (si cambia el estado, guarda bitácora)
- `DELETE /reservas/{id}` — eliminar reserva (solo si el estado es `Cancelada`; requiere `?confirmar=true`)

### Historial y reportes
- `GET /historial_seguimiento` — historial de movimientos de lotes
- `GET /compras` — historial de compras
- `GET /ventas` — historial de ventas
- `GET /historial_reservas` — historial de cambios de estado de reservas

## Manejo de errores

Cada módulo lanza sus propias excepciones (carpeta `Excepciones/`), y `main.py` las captura con `@app.exception_handler(...)` para devolver siempre el formato de respuesta estándar con el código HTTP correcto:

| Excepción | Código HTTP | Módulo |
|---|---|---|
| ErrorUsuarioNoExiste | 404 | Usuarios |
| ErrorUsuarioYaExiste | 400 | Usuarios |
| ErrorRolInvalido | 400 | Usuarios |
| ErrorLoteNoEncontrado | 404 | Lotes |
| ErrorLoteYaExiste | 400 | Lotes |
| ErrorCantidadInvalida | 400 | Lotes |
| ErrorCategoriaInvalidaEnLote | 400 | Lotes |
| ErrorCategoriaNoEncontrada | 404 | Categorías |
| ErrorCategoriaYaExiste | 400 | Categorías |
| ErrorCantidadMinNegativa | 400 | Categorías |
| ErrorCategoriaConLotes | 409 | Categorías |
| ErrorReservaNoEncontrada | 404 | Reservas |
| ErrorReservaYaExiste | 400 | Reservas |
| ErrorReservaNoEliminable | 409 | Reservas |
| ErrorStockInsuficiente | 400 | Reservas |
| ErrorProductoNoEncontrado | 404 | Reservas |
| ErrorEstadoInvalido | 400 | Reservas |

Además, cualquier excepción no controlada es capturada por un manejador genérico que responde con HTTP 500.

## Middleware

- **CORS**: habilitado solo para `http://127.0.0.1:8000`, métodos `GET`, `POST`, `PUT`, `DELETE`, con credenciales permitidas.
- **Logging**: un middleware (`LoggingMiddleware`) registra en consola el método, la ruta, el código de estado y la duración de cada petición.

## Notas

- El CORS está restringido actualmente a `http://127.0.0.1:8000`; ajustar `allow_origins` en `main.py` según el dominio real del frontend.
- Las tablas se crean automáticamente al iniciar la app (`Base.metadata.create_all`); no se usa un sistema de migraciones (como Alembic), por lo que los cambios en `models.py` requieren borrar y recrear la base de datos.
