# pip install fastapi uvicorn sqlalchemy pymysql cryptography
# uvicorn main:app --app-dir scr --reload

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from Conexion.database import engine, Base
import Modelos.models as models

from excepciones import ErrorUsuarioNoExiste, ErrorStockInsuficiente
from respuesta import respuesta_error

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
# EXCEPCIONES PERSONALIZADAS
# ================================================================

@app.exception_handler(ErrorUsuarioNoExiste)
async def manejar_usuario_no_existe(request, error):
    return respuesta_error(message=error.mensaje, status_code=404, error=error.mensaje)

@app.exception_handler(ErrorStockInsuficiente)
async def manejar_stock_insuficiente(request, error):
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