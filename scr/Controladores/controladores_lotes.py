from fastapi import Query, Depends
from sqlalchemy.orm import Session
from Conexion.database import get_db
import Modelos.models as models
from Excepciones.excepciones_lotes import (
    ErrorLoteNoEncontrado,
    ErrorLoteYaExiste,
    ErrorCantidadInvalida,
    ErrorCategoriaInvalidaEnLote,
)
from Utilidades.respuesta import respuesta_ok, respuesta_error
from Esquemas.Esquemas import LoteCrear, LoteEditar


# ── Helper ────────────────────────────────────────────────────────────────────

def _serializar_lote(l: models.Lote) -> dict:
    return {
        "id":             l.id,
        "producto":       l.producto,
        "cantidad":       l.cantidad,
        "kg_reservados":  l.kg_reservados,
        "precio_kg":      float(l.precio_kg) if l.precio_kg else None,
        "estado":         l.estado,
        "fecha_cosecha":  str(l.fecha_cosecha) if l.fecha_cosecha else None,
        "categoria":      l.categoria,
        "productor_id":   l.productor_id,
        "productor":      l.productor.nombre,
    }


# ── GET /lotes ────────────────────────────────────────────────────────────────
# Lista todos los lotes. Filtros opcionales por categoría, estado y productor.

def obtener_lotes(
    categoria:    str = Query(default=None, description="Filtrar por categoría"),
    estado:       str = Query(default=None, description="Filtrar por estado: Activo | Inactivo"),
    productor_id: int = Query(default=None, description="Filtrar por id de productor"),
    db: Session = Depends(get_db),
):
    query = db.query(models.Lote)

    if categoria:
        query = query.filter(models.Lote.categoria.ilike(categoria))
    if estado:
        query = query.filter(models.Lote.estado == estado)
    if productor_id:
        query = query.filter(models.Lote.productor_id == productor_id)

    lotes = query.all()
    return respuesta_ok(
        message="Lotes obtenidos",
        data=[_serializar_lote(l) for l in lotes],
    )


# ── GET /lotes/{producto} ────────────────────────────────────────────────────
# Busca lotes cuyo nombre de producto coincida (búsqueda parcial).

def obtener_lote_por_producto(
    producto: str,
    db: Session = Depends(get_db),
):
    if not producto.strip():
        return respuesta_error("El nombre del producto no puede estar vacío", status_code=400)

    lotes = (
        db.query(models.Lote)
        .filter(models.Lote.producto.ilike(f"%{producto.strip()}%"))
        .all()
    )
    if not lotes:
        return respuesta_error(f"No se encontraron lotes con producto '{producto}'", status_code=404)

    return respuesta_ok(
        message="Lote(s) obtenido(s)",
        data=[_serializar_lote(l) for l in lotes],
    )


# ── POST /lotes ───────────────────────────────────────────────────────────────
# Crea un nuevo lote. El productor_id debe ser un usuario con rol 'Productor'.

def agregar_lote(
    datos: LoteCrear,
    db: Session = Depends(get_db),
):
    if db.query(models.Lote).filter(models.Lote.id == datos.id).first():
        raise ErrorLoteYaExiste(datos.id)

    if not db.query(models.Categoria).filter(models.Categoria.nombre == datos.categoria).first():
        raise ErrorCategoriaInvalidaEnLote(datos.categoria)

    if datos.cantidad <= 0:
        raise ErrorCantidadInvalida()

    productor = db.query(models.Usuario).filter(models.Usuario.id == datos.productor_id).first()
    if not productor:
        return respuesta_error(
            f"No existe un usuario con id {datos.productor_id}",
            status_code=404,
        )
    if productor.rol != "Productor":
        return respuesta_error(
            f"El usuario {datos.productor_id} tiene rol '{productor.rol}', no 'Productor'.",
            status_code=400,
        )

    nuevo = models.Lote(
        id=datos.id,
        producto=datos.producto,
        cantidad=datos.cantidad,
        categoria=datos.categoria,
        productor_id=datos.productor_id,
        estado=datos.estado,
        fecha_cosecha=datos.fecha_cosecha,
        precio_kg=datos.precio_kg,
    )
    db.add(nuevo)
    db.add(models.HistorialSeguimiento(
        accion="Creación de lote",
        lote=datos.id,
        producto=datos.producto,
    ))
    db.commit()
    db.refresh(nuevo)

    return respuesta_ok(
        message="Lote creado",
        data=_serializar_lote(nuevo),
        status_code=201,
    )


# ── PUT /lotes/{id} ──────────────────────────────────────────────────────────
# Actualiza producto, cantidad, categoría, precio_kg, estado y fecha de cosecha.

def editar_lote(
    id: int,
    datos: LoteEditar,
    db: Session = Depends(get_db),
):
    if id <= 0:
        return respuesta_error("El id debe ser un número positivo", status_code=400)

    lote = db.query(models.Lote).filter(models.Lote.id == id).first()
    if not lote:
        raise ErrorLoteNoEncontrado(id)

    if datos.producto is not None:
        if not datos.producto.strip():
            return respuesta_error("El nombre del producto no puede estar vacío", status_code=400)
        lote.producto = datos.producto.strip()
    if datos.cantidad is not None:
        if datos.cantidad <= 0:
            raise ErrorCantidadInvalida()
        lote.cantidad = datos.cantidad
    if datos.categoria is not None:
        if not db.query(models.Categoria).filter(models.Categoria.nombre == datos.categoria).first():
            raise ErrorCategoriaInvalidaEnLote(datos.categoria)
        lote.categoria = datos.categoria
    if datos.estado is not None:
        lote.estado = datos.estado
    if datos.precio_kg is not None:
        lote.precio_kg = datos.precio_kg
    if datos.fecha_cosecha is not None:
        lote.fecha_cosecha = datos.fecha_cosecha

    db.commit()
    db.refresh(lote)

    return respuesta_ok(
        message="Lote actualizado",
        data=_serializar_lote(lote),
    )


# ── DELETE /lotes/{id} ────────────────────────────────────────────────────────
# Elimina un lote. No se permite si tiene reservas en estado Pendiente o Confirmada.

def eliminar_lote(
    id: int,
    confirmar: bool = Query(default=False, description="Debe ser true para confirmar la eliminación"),
    db: Session = Depends(get_db),
):
    if id <= 0:
        return respuesta_error("El id debe ser un número positivo", status_code=400)

    if not confirmar:
        return respuesta_error("Debe confirmar la eliminación con ?confirmar=true", status_code=400)

    lote = db.query(models.Lote).filter(models.Lote.id == id).first()
    if not lote:
        raise ErrorLoteNoEncontrado(id)

    reservas_activas = db.query(models.Reserva).filter(
        models.Reserva.lote_id == id,
        models.Reserva.estado.in_(["Pendiente", "Confirmada"]),
    ).count()

    if reservas_activas > 0:
        return respuesta_error(
            f"El lote {id} tiene {reservas_activas} reserva(s) activa(s). Cancélalas primero.",
            status_code=409,
        )

    producto = lote.producto
    db.delete(lote)
    db.commit()

    return respuesta_ok(
        message="Lote eliminado",
        data={"id": id, "producto": producto},
    )