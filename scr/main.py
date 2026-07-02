# AgroMercado API — punto de entrada principal
# pip install fastapi uvicorn sqlalchemy psycopg2-binary pydantic[email]
# cd C:\Users\SENA\Downloads\fastapi\scr uvicorn main:app --reload

import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from Conexion.database import engine, Base
import Modelos.models as models

from Utilidades.respuesta import respuesta_error

# ── Excepciones ───────────────────────────────────────────────────────────────

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
    ErrorCategoriaConLotes,
)
from Excepciones.excepciones_reservas import (
    ErrorReservaNoEncontrada,
    ErrorReservaYaExiste,
    ErrorReservaNoEliminable,
    ErrorStockInsuficiente,
    ErrorProductoNoEncontrado,
    ErrorEstadoInvalido,
)
from Excepciones.excepciones_auth import ErrorCredencialesInvalidas

# ── Rutas ─────────────────────────────────────────────────────────────────────

from Rutas import (
    rutas_usuarios,
    rutas_lotes,
    rutas_reservas,
    rutas_categorias,
    rutas_historial,
    rutas_roles,
    rutas_tipos_documento,
    rutas_auth,
)

# Crea las tablas al arrancar si no existen
Base.metadata.create_all(bind=engine)

# ── App ───────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="AgroMercado API",
    version="4.0",
    description="API para la comercialización de productos agrícolas entre productores y compradores.",
)

# ── CORS ──────────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",  # Live Server (frontend)
        "http://localhost:5500",
        "http://127.0.0.1:8000",
    ],
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
    allow_credentials=True,
)

# ── Middleware de logging ─────────────────────────────────────────────────────

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        inicio    = time.time()
        response  = await call_next(request)
        duracion  = time.time() - inicio
        print(f"[{response.status_code}] {request.method} {request.url.path} — {duracion:.3f}s")
        return response

app.add_middleware(LoggingMiddleware)

# ── Manejador global de errores no controlados ────────────────────────────────

@app.exception_handler(Exception)
async def manejar_error_generico(request: Request, error: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "ok":      False,
            "message": "Error interno del servidor",
            "error":   str(error),
            "data":    None,
        },
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

@app.exception_handler(ErrorCategoriaConLotes)
async def manejar_categoria_con_lotes(request, error):
    return respuesta_error(message=error.mensaje, status_code=409, error=error.mensaje)


# ================================================================
# MANEJADORES DE EXCEPCIONES — RESERVAS
# ================================================================

@app.exception_handler(ErrorReservaNoEncontrada)
async def manejar_reserva_no_encontrada(request, error):
    return respuesta_error(message=error.mensaje, status_code=404, error=error.mensaje)

@app.exception_handler(ErrorReservaYaExiste)
async def manejar_reserva_ya_existe(request, error):
    return respuesta_error(message=error.mensaje, status_code=400, error=error.mensaje)

@app.exception_handler(ErrorReservaNoEliminable)
async def manejar_reserva_no_eliminable(request, error):
    return respuesta_error(message=error.mensaje, status_code=409, error=error.mensaje)

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
# MANEJADORES DE EXCEPCIONES — AUTENTICACIÓN
# ================================================================

@app.exception_handler(ErrorCredencialesInvalidas)
async def manejar_credenciales_invalidas(request, error):
    return respuesta_error(message=error.mensaje, status_code=401, error=error.mensaje)


# ================================================================
# REGISTRO DE RUTAS
# ================================================================

app.include_router(rutas_usuarios.router)
app.include_router(rutas_lotes.router)
app.include_router(rutas_reservas.router)
app.include_router(rutas_categorias.router)
app.include_router(rutas_historial.router)
app.include_router(rutas_roles.router)
app.include_router(rutas_tipos_documento.router)
app.include_router(rutas_auth.router)