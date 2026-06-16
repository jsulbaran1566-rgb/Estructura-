# pip install fastapi uvicorn sqlalchemy psycopg2-binary
# uvicorn main:app --app-dir scr --reload

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from Conexion.database import engine, Base
import Modelos.models as models

from Utilidades.respuesta import respuesta_error

# ── Excepciones por módulo ──────────────────────────────────────────────────
from Excepciones.excepciones_usuarios import (
    ErrorUsuarioNoExiste,
    ErrorUsuarioYaExiste,
    ErrorRolInvalido,
)
from Excepciones.excepciones_lotes import (
    ErrorLoteNoEncontrado,
    ErrorLoteYaExiste,
    ErrorCantidadInvalida,
    ErrorCategoriaInvalidaEnLote,
)
from Excepciones.excepciones_categorias import (
    ErrorCategoriaNoEncontrada,
    ErrorCategoriaYaExiste,
    ErrorCantidadMinNegativa,
)
from Excepciones.excepciones_compradores import (
    ErrorCompradorNoEncontrado,
    ErrorCompradorYaExiste,
    ErrorConfirmacionRequerida,
    ErrorIdInvalido,
)
from Excepciones.excepciones_reservas import (
    ErrorReservaNoEncontrada,
    ErrorReservaYaExiste,
    ErrorStockInsuficiente,
    ErrorProductoNoEncontrado,
    ErrorEstadoInvalido,
)

from Rutas import (
    rutas_usuarios,
    rutas_lotes,
    rutas_compradores,
    rutas_reservas,
    rutas_categorias,
    rutas_historial,
)

# Crea todas las tablas al arrancar
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AgroMercado API", version="3.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=False,
)


# ================================================================
# MANEJADORES DE EXCEPCIONES — USUARIOS
# ================================================================

@app.exception_handler(ErrorUsuarioNoExiste)
async def manejar_usuario_no_existe(request, error):
    return respuesta_error(message=error.mensaje, status_code=404, error=error.mensaje)

@app.exception_handler(ErrorUsuarioYaExiste)
async def manejar_usuario_ya_existe(request, error):
    return respuesta_error(message=error.mensaje, status_code=400, error=error.mensaje)

@app.exception_handler(ErrorRolInvalido)
async def manejar_rol_invalido(request, error):
    return respuesta_error(message=error.mensaje, status_code=400, error=error.mensaje)


# ================================================================
# MANEJADORES DE EXCEPCIONES — LOTES
# ================================================================

@app.exception_handler(ErrorLoteNoEncontrado)
async def manejar_lote_no_encontrado(request, error):
    return respuesta_error(message=error.mensaje, status_code=404, error=error.mensaje)

@app.exception_handler(ErrorLoteYaExiste)
async def manejar_lote_ya_existe(request, error):
    return respuesta_error(message=error.mensaje, status_code=400, error=error.mensaje)

@app.exception_handler(ErrorCantidadInvalida)
async def manejar_cantidad_invalida(request, error):
    return respuesta_error(message=error.mensaje, status_code=400, error=error.mensaje)

@app.exception_handler(ErrorCategoriaInvalidaEnLote)
async def manejar_categoria_invalida_en_lote(request, error):
    return respuesta_error(message=error.mensaje, status_code=400, error=error.mensaje)


# ================================================================
# MANEJADORES DE EXCEPCIONES — CATEGORÍAS
# ================================================================

@app.exception_handler(ErrorCategoriaNoEncontrada)
async def manejar_categoria_no_encontrada(request, error):
    return respuesta_error(message=error.mensaje, status_code=404, error=error.mensaje)

@app.exception_handler(ErrorCategoriaYaExiste)
async def manejar_categoria_ya_existe(request, error):
    return respuesta_error(message=error.mensaje, status_code=400, error=error.mensaje)

@app.exception_handler(ErrorCantidadMinNegativa)
async def manejar_cantidad_min_negativa(request, error):
    return respuesta_error(message=error.mensaje, status_code=400, error=error.mensaje)


# ================================================================
# MANEJADORES DE EXCEPCIONES — COMPRADORES
# ================================================================

@app.exception_handler(ErrorCompradorNoEncontrado)
async def manejar_comprador_no_encontrado(request, error):
    return respuesta_error(message=error.mensaje, status_code=404, error=error.mensaje)

@app.exception_handler(ErrorCompradorYaExiste)
async def manejar_comprador_ya_existe(request, error):
    return respuesta_error(message=error.mensaje, status_code=400, error=error.mensaje)

@app.exception_handler(ErrorConfirmacionRequerida)
async def manejar_confirmacion_requerida(request, error):
    return respuesta_error(message=error.mensaje, status_code=400, error=error.mensaje)

@app.exception_handler(ErrorIdInvalido)
async def manejar_id_invalido(request, error):
    return respuesta_error(message=error.mensaje, status_code=400, error=error.mensaje)


# ================================================================
# MANEJADORES DE EXCEPCIONES — RESERVAS
# ================================================================

@app.exception_handler(ErrorReservaNoEncontrada)
async def manejar_reserva_no_encontrada(request, error):
    return respuesta_error(message=error.mensaje, status_code=404, error=error.mensaje)

@app.exception_handler(ErrorReservaYaExiste)
async def manejar_reserva_ya_existe(request, error):
    return respuesta_error(message=error.mensaje, status_code=400, error=error.mensaje)

@app.exception_handler(ErrorStockInsuficiente)
async def manejar_stock_insuficiente(request, error):
    return respuesta_error(message=error.mensaje, status_code=400, error=error.mensaje)

@app.exception_handler(ErrorProductoNoEncontrado)
async def manejar_producto_no_encontrado(request, error):
    return respuesta_error(message=error.mensaje, status_code=404, error=error.mensaje)

@app.exception_handler(ErrorEstadoInvalido)
async def manejar_estado_invalido(request, error):
    return respuesta_error(message=error.mensaje, status_code=400, error=error.mensaje)


# ================================================================
# REGISTRO DE RUTAS
# ================================================================

app.include_router(rutas_usuarios.router)
app.include_router(rutas_lotes.router)
app.include_router(rutas_compradores.router)
app.include_router(rutas_reservas.router)
app.include_router(rutas_categorias.router)
app.include_router(rutas_historial.router)