from fastapi import Query, Depends
from sqlalchemy.orm import Session
from Conexion.database import get_db
import Modelos.models as models
from scr.Utilidades.respuesta import respuesta_ok, respuesta_error
from Esquemas.Esquemas import CategoriaCrear
from Excepciones.excepciones_categorias import (
    ErrorCategoriaNoEncontrada,
    ErrorCategoriaYaExiste,
    ErrorCantidadMinNegativa,
)


def obtener_categorias(db: Session = Depends(get_db)):
    categorias = db.query(models.Categoria).all()
    return respuesta_ok(
        message="Categorías obtenidas",
        data=[{"nombre": c.nombre} for c in categorias],
    )


def obtener_lotes_por_categoria(
    nombre: str,
    cantidad_min: int,
    ordenar: bool = Query(default=False, description="Ordenar por cantidad descendente"),
    limite:  int  = Query(default=10, ge=1, le=100, description="Límite de resultados (1-100)"),
    db: Session = Depends(get_db),
):
    if not db.query(models.Categoria).filter(models.Categoria.nombre.ilike(nombre)).first():
        raise ErrorCategoriaNoEncontrada(nombre)

    if cantidad_min < 0:
        raise ErrorCantidadMinNegativa()

    resultado = db.query(models.Lote).filter(
        models.Lote.categoria.ilike(nombre),
        models.Lote.cantidad >= cantidad_min
    ).all()

    if ordenar:
        resultado = sorted(resultado, key=lambda x: x.cantidad, reverse=True)

    return respuesta_ok(
        message="Lotes por categoría obtenidos",
        data=[{"id": l.id, "producto": l.producto, "cantidad": l.cantidad, "categoria": l.categoria} for l in resultado[:limite]],
    )


def agregar_categoria(
    datos: CategoriaCrear,
    db: Session = Depends(get_db),
):
    if db.query(models.Categoria).filter(models.Categoria.nombre == datos.nombre).first():
        raise ErrorCategoriaYaExiste(datos.nombre)

    nueva = models.Categoria(nombre=datos.nombre)
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return respuesta_ok(
        message="Categoría agregada",
        data={"nombre": nueva.nombre},
        status_code=201,
    )