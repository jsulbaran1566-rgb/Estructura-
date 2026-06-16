# AgroMercado API

API REST para un mercado agrícola de pre-cosecha. Permite gestionar usuarios, categorías, lotes de producto, compradores y reservas, además de consultar un historial de las operaciones realizadas.

## Tecnologías

- **FastAPI** — framework para construir la API
- **SQLAlchemy** — ORM para hablar con la base de datos
- **PostgreSQL** — motor de base de datos
- **Pydantic** — validación de los datos que llegan en las peticiones
- **CORS Middleware** — habilitado para aceptar peticiones desde cualquier origen

## Estructura del proyecto

```
scr/
├── main.py                    # Punto de entrada de la aplicación
├── Utilidades/
│   └── respuesta.py                # Funciones respuesta_ok / respuesta_error
├── Conexion/
│   └── database.py             # Configuración de conexión a PostgreSQL
├── Modelos/
│   └── models.py                # Tablas de la base de datos (SQLAlchemy)
├── Esquemas/
│   └── Esquemas.py               # Validación de datos de entrada (Pydantic)
├── Excepciones/
│   ├── excepciones_categorias.py
│   ├── excepciones_compradores.py
│   ├── excepciones_lotes.py
│   ├── excepciones_reservas.py
│   └── excepciones_usuarios.py
├── Controladores/
│   ├── controladores_categorias.py
│   ├── controladores_compradores.py
│   ├── controladores_historial.py
│   ├── controladores_lotes.py
│   ├── controladores_reservas.py
│   └── controladores_usuarios.py
└── Rutas/
    ├── rutas_categorias.py
    ├── rutas_compradores.py
    ├── rutas_historial.py
    ├── rutas_lotes.py
    ├── rutas_reservas.py
    └── rutas_usuarios.py
```

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
   pip install fastapi uvicorn sqlalchemy psycopg2-binary
   ```

## Configuración de la base de datos

En `Conexion/database.py` se define la conexión a PostgreSQL:

```python
SQLALCHEMY_DATABASE_URL = "postgresql+psycopg2://postgres:1234@localhost/agro_mercado"
```

Antes de ejecutar el proyecto:
- Crear en PostgreSQL una base de datos llamada `agro_mercado`.
- Ajustar usuario y contraseña según tu instalación.
- Las tablas se crean automáticamente al arrancar la aplicación, gracias a `Base.metadata.create_all(bind=engine)` en `main.py`.

## Ejecutar el proyecto

Como el código vive dentro de la carpeta `scr`, la aplicación se levanta indicando ese directorio:

```
uvicorn main:app --app-dir scr --reload
```

La documentación interactiva queda disponible en `http://localhost:8000/docs`.

## Formato de respuesta

Todas las respuestas de la API siguen la misma estructura, definida en `respuesta.py`:

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

## Endpoints principales

### Usuarios (`/usuarios`)
- `GET /usuarios` — listar todos los usuarios
- `GET /usuarios/{id}` — obtener un usuario por id
- `GET /usuarios/{id}/rol/{rol}` — obtener usuario por id y rol
- `POST /usuarios` — registrar un usuario
- `PUT /usuarios/{id}/rol/{nuevo_rol}` — editar el rol de un usuario

### Categorías (`/categorias`)
- `GET /categorias` — listar categorías
- `GET /categorias/{nombre}/lotes/{cantidad_min}` — lotes de una categoría con cantidad mínima
- `POST /categorias` — crear una categoría

### Lotes (`/lotes`)
- `GET /lotes` — listar lotes
- `GET /lotes/{id}/categoria/{categoria}` — buscar lote por id y categoría
- `POST /lotes` — registrar un lote
- `PUT /lotes/{id}/producto/{nuevo_producto}` — editar un lote

### Compradores (`/compradores`)
- `GET /compradores` — listar compradores
- `GET /compradores/{id}/ciudad/{ciudad}` — buscar comprador por id y ciudad
- `POST /compradores` — registrar un comprador
- `DELETE /compradores/{id}/ciudad/{ciudad}` — eliminar un comprador

### Reservas (`/reservas`)
- `GET /reservas` — listar reservas
- `GET /reservas/{id}/comprador/{comprador}` — buscar una reserva
- `POST /reservas/{id}/comprador/{comprador}` — crear una reserva (descuenta stock del lote)

### Historial y reportes
- `GET /historial_seguimiento` — historial de movimientos de lotes
- `GET /compras` — historial de compras
- `GET /ventas` — historial de ventas
- `GET /historial_reservas` — historial de reservas

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
| ErrorCompradorNoEncontrado | 404 | Compradores |
| ErrorCompradorYaExiste | 400 | Compradores |
| ErrorConfirmacionRequerida | 400 | Compradores |
| ErrorIdInvalido | 400 | Compradores |
| ErrorReservaNoEncontrada | 404 | Reservas |
| ErrorReservaYaExiste | 400 | Reservas |
| ErrorStockInsuficiente | 400 | Reservas |
| ErrorProductoNoEncontrado | 404 | Reservas |
| ErrorEstadoInvalido | 400 | Reservas |

## Notas

- El CORS está abierto a cualquier origen (`allow_origins=["*"]`), pensado para entorno de desarrollo. En producción conviene restringirlo a los dominios reales del frontend.
- Las tablas se recrean automáticamente al iniciar la app; no se está usando un sistema de migraciones (como Alembic), así que los cambios en `models.py` requieren borrar y volver a crear la base de datos en este momento.
