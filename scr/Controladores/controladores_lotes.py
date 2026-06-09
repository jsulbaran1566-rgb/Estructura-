from fastapi import Query, Depends
from sqlalchemy.orm import Session
from Conexion.database import get_db
import Modelos.models as models
from respuesta import respuesta_ok, respuesta_error
from Esquemas.Esquemas import LoteCrear, LoteEditar


def obtener_lotes(db: Session = Depends(get_db)):
    lotes = db.query(models.Lote).all()
    return respuesta_ok(
        message="Lotes obtenidos",
        data=[{"id": l.id, "producto": l.producto, "cantidad": l.cantidad, "categoria": l.categoria} for l in lotes],
    )


def obtener_lote_por_id_y_categoria(
    id: int,
    categoria: str,
    cantidad_min: int = Query(default=0,          description="Cantidad mínima disponible"),
    ordenar_por: str  = Query(default="producto",  description="Campo para ordenar: producto | cantidad"),
    db: Session = Depends(get_db),
):
    if id <= 0:
        return respuesta_error("El id debe ser un número positivo", status_code=400)
    if cantidad_min < 0:
        return respuesta_error("cantidad_min no puede ser negativo", status_code=400)

    campos_validos = ["producto", "cantidad"]
    if ordenar_por not in campos_validos:
        return respuesta_error(f"ordenar_por debe ser uno de: {campos_validos}", status_code=400)

    resultado = db.query(models.Lote).filter(
        models.Lote.id == id,
        models.Lote.categoria.ilike(categoria),
        models.Lote.cantidad >= cantidad_min
    ).all()

    if not resultado:
        return respuesta_error("Lote no encontrado con esos criterios", status_code=404)

    ordenado = sorted(resultado, key=lambda x: getattr(x, ordenar_por))
    return respuesta_ok(
        message="Lote obtenido",
        data=[{"id": l.id, "producto": l.producto, "cantidad": l.cantidad, "categoria": l.categoria} for l in ordenado],
    )


def agregar_lote(
    datos: LoteCrear,
    db: Session = Depends(get_db),
):
    if db.query(models.Lote).filter(models.Lote.id == datos.id).first():
        return respuesta_error("Ya existe un lote con ese id", status_code=400)

    if not db.query(models.Categoria).filter(models.Categoria.nombre == datos.categoria).first():
        return respuesta_error("Categoría inválida", status_code=400)

    if datos.cantidad <= 0:
        return respuesta_error("La cantidad debe ser mayor a 0", status_code=400)

    nuevo = models.Lote(id=datos.id, producto=datos.producto, cantidad=datos.cantidad, categoria=datos.categoria)
    db.add(nuevo)

    historial = models.HistorialSeguimiento(accion="Creación de lote", lote=datos.id, producto=datos.producto)
    db.add(historial)

    db.commit()
    db.refresh(nuevo)
    return respuesta_ok(
        message="Lote agregado",
        data={"id": nuevo.id, "producto": nuevo.producto, "cantidad": nuevo.cantidad, "categoria": nuevo.categoria},
        status_code=201,
    )


def editar_lote(
    id: int,
    nuevo_producto: str,
    datos: LoteEditar,
    db: Session = Depends(get_db),
):
    if id <= 0:
        return respuesta_error("El id debe ser un número positivo", status_code=400)

    lote = db.query(models.Lote).filter(models.Lote.id == id).first()
    if not lote:
        return respuesta_error("Lote no encontrado", status_code=404)

    lote.producto = nuevo_producto
    if datos.cantidad is not None:
        if datos.cantidad <= 0:
            return respuesta_error("La cantidad debe ser mayor a 0", status_code=400)
        lote.cantidad = datos.cantidad
    if datos.categoria:
        lote.categoria = datos.categoria

    db.commit()
    db.refresh(lote)
    return respuesta_ok(
        message="Lote actualizado",
        data={"id": lote.id, "producto": lote.producto, "cantidad": lote.cantidad, "categoria": lote.categoria},
    )