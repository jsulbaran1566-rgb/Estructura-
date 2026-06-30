from fastapi import Query, Depends
from sqlalchemy.orm import Session
from Conexion.database import get_db
import Modelos.models as models
from Excepciones.excepciones_categorias import (
    ErrorCategoriaNoEncontrada,
    ErrorCategoriaYaExiste,
    ErrorCantidadMinNegativa,
    ErrorCategoriaConLotes,
)
from Utilidades.respuesta import respuesta_ok
from Esquemas.Esquemas import CategoriaCrear, CategoriaEditar


# ── Helper ────────────────────────────────────────────────────────────────────

def _serializar_lote(l: models.Lote) -> dict:
    return {
        "id":           l.id,
        "producto":     l.producto,
        "cantidad":     l.cantidad,
        "kg_reservados":l.kg_reservados,
        "precio_kg":    float(l.precio_kg) if l.precio_kg else None,
        "estado":       l.estado,
        "categoria":    l.categoria,
        "productor_id": l.productor_id,
        "productor":    l.productor.nombre,
    }


# ── GET /categorias ───────────────────────────────────────────────────────────
# Lista todas las categorías disponibles en el sistema.

def obtener_categorias(db: Session = Depends(get_db)):
    categorias = db.query(models.Categoria).all()
    return respuesta_ok(
        message="Categorías obtenidas",
        data=[{"nombre": c.nombre} for c in categorias],
    )


# ── GET /categorias/{nombre}/lotes ────────────────────────────────────────────
# Lista los lotes de una categoría. Filtra por cantidad mínima disponible.

def obtener_lotes_por_categoria(
    nombre:      str,
    cantidad_min: int  = Query(default=0,     ge=0,  description="Cantidad mínima disponible"),
    ordenar:     bool  = Query(default=False,        description="Ordenar por cantidad descendente"),
    limite:      int   = Query(default=10,    ge=1, le=100, description="Límite de resultados"),
    solo_activos: bool = Query(default=True,         description="Mostrar solo lotes activos"),
    db: Session = Depends(get_db),
):
    if not db.query(models.Categoria).filter(models.Categoria.nombre == nombre).first():
        raise ErrorCategoriaNoEncontrada(nombre)

    if cantidad_min < 0:
        raise ErrorCantidadMinNegativa()

    query = db.query(models.Lote).filter(
        models.Lote.categoria.ilike(nombre),
        models.Lote.cantidad >= cantidad_min,
    )

    if solo_activos:
        query = query.filter(models.Lote.estado == "Activo")

    resultado = query.all()

    if ordenar:
        resultado = sorted(resultado, key=lambda x: x.cantidad, reverse=True)

    return respuesta_ok(
        message=f"Lotes de la categoría '{nombre}' obtenidos",
        data=[_serializar_lote(l) for l in resultado[:limite]],
    )


# ── POST /categorias ──────────────────────────────────────────────────────────
# Crea una nueva categoría.

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
        message="Categoría creada",
        data={"nombre": nueva.nombre},
        status_code=201,
    )


# ── PUT /categorias/{nombre} ──────────────────────────────────────────────────
# Renombra una categoría. La FK con ON UPDATE CASCADE propaga el cambio a lotes.

def editar_categoria(
    nombre: str,
    datos: CategoriaEditar,
    db: Session = Depends(get_db),
):
    categoria = db.query(models.Categoria).filter(models.Categoria.nombre == nombre).first()
    if not categoria:
        raise ErrorCategoriaNoEncontrada(nombre)

    if db.query(models.Categoria).filter(models.Categoria.nombre == datos.nombre_nuevo).first():
        raise ErrorCategoriaYaExiste(datos.nombre_nuevo)

    categoria.nombre = datos.nombre_nuevo   # CASCADE en lotes.categoria actualiza automático
    db.commit()

    return respuesta_ok(
        message=f"Categoría renombrada: '{nombre}' → '{datos.nombre_nuevo}'",
        data={"nombre": datos.nombre_nuevo},
    )


# ── DELETE /categorias/{nombre} ───────────────────────────────────────────────
# Elimina una categoría solo si no tiene lotes asociados (FK RESTRICT).

def eliminar_categoria(
    nombre: str,
    db: Session = Depends(get_db),
):
    categoria = db.query(models.Categoria).filter(models.Categoria.nombre == nombre).first()
    if not categoria:
        raise ErrorCategoriaNoEncontrada(nombre)

    total_lotes = db.query(models.Lote).filter(models.Lote.categoria == nombre).count()
    if total_lotes > 0:
        raise ErrorCategoriaConLotes(nombre, total_lotes)

    db.delete(categoria)
    db.commit()

    return respuesta_ok(
        message=f"Categoría '{nombre}' eliminada",
        data={"nombre": nombre},
    )