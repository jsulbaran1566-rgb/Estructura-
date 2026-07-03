from fastapi import Query, Depends
from datetime import date
from sqlalchemy import func
from sqlalchemy.orm import Session
from Conexion.database import get_db
import Modelos.models as models
from Excepciones.excepciones_reservas import (
    ErrorReservaNoEncontrada,
    ErrorReservaYaExiste,
    ErrorReservaNoEliminable,
    ErrorStockInsuficiente,
    ErrorEstadoInvalido,
)
from Utilidades.respuesta import respuesta_ok, respuesta_error
from Esquemas.Esquemas import ReservaCrear, ReservaEditar

ESTADOS_VALIDOS = ["Pendiente", "Confirmada", "Entregada", "Cancelada"]


def _siguiente_id(db: Session, modelo) -> int:
    """Calcula el próximo id disponible para tablas sin autoincremento (id INTEGER PRIMARY KEY)."""
    maximo = db.query(func.max(modelo.id)).scalar()
    return (maximo or 0) + 1


# ── Helpers ──────────────────────────────────────────────────────────────────

def _serializar_reserva(r: models.Reserva) -> dict:
    return {
        "id":           r.id,
        "comprador_id": r.comprador_id,
        "comprador":    r.comprador.nombre,
        "lote_id":      r.lote_id,
        "producto":     r.lote.producto,
        "cantidad":     r.cantidad,
        "fecha":        str(r.fecha),
        "estado":       r.estado,
    }


# ── GET /reservas ─────────────────────────────────────────────────────────────
# Lista todas las reservas con filtros opcionales por estado, comprador, lote y fechas.

def obtener_reservas(
    estado:       str  = Query(default=None, description=f"Filtrar por estado: {ESTADOS_VALIDOS}"),
    comprador_id: int  = Query(default=None, description="Filtrar por id de comprador"),
    lote_id:      int  = Query(default=None, description="Filtrar por id de lote"),
    fecha_desde:  date = Query(default=None, description="Fecha inicio del rango (YYYY-MM-DD)"),
    fecha_hasta:  date = Query(default=None, description="Fecha fin del rango (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
):
    if estado and estado not in ESTADOS_VALIDOS:
        raise ErrorEstadoInvalido(estado, ESTADOS_VALIDOS)

    if fecha_desde and fecha_hasta and fecha_desde > fecha_hasta:
        return respuesta_error("fecha_desde no puede ser posterior a fecha_hasta", status_code=400)

    query = db.query(models.Reserva)

    if estado:
        query = query.filter(models.Reserva.estado == estado)
    if comprador_id:
        query = query.filter(models.Reserva.comprador_id == comprador_id)
    if lote_id:
        query = query.filter(models.Reserva.lote_id == lote_id)
    if fecha_desde:
        query = query.filter(models.Reserva.fecha >= fecha_desde)
    if fecha_hasta:
        query = query.filter(models.Reserva.fecha <= fecha_hasta)

    reservas = query.all()
    return respuesta_ok(
        message="Reservas obtenidas",
        data=[_serializar_reserva(r) for r in reservas],
    )


# ── GET /reservas/fechas ──────────────────────────────────────────────────────
# Obtiene reservas dentro de un rango de fechas. Ambos parámetros son obligatorios.

def obtener_reservas_por_fecha(
    fecha_desde: date = Query(..., description="Fecha inicio del rango (YYYY-MM-DD)"),
    fecha_hasta: date = Query(..., description="Fecha fin del rango (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
):
    if fecha_desde > fecha_hasta:
        return respuesta_error("fecha_desde no puede ser posterior a fecha_hasta", status_code=400)

    reservas = (
        db.query(models.Reserva)
        .filter(
            models.Reserva.fecha >= fecha_desde,
            models.Reserva.fecha <= fecha_hasta,
        )
        .all()
    )

    return respuesta_ok(
        message=f"Reservas entre {fecha_desde} y {fecha_hasta}",
        data=[_serializar_reserva(r) for r in reservas],
    )


# ── POST /reservas ────────────────────────────────────────────────────────────
# Crea una nueva reserva. Descuenta cantidad del lote y registra en historial.

def crear_reserva(
    datos: ReservaCrear,
    db: Session = Depends(get_db),
):
    # Verificar que no exista ya esa reserva
    if db.query(models.Reserva).filter(models.Reserva.id == datos.id).first():
        raise ErrorReservaYaExiste(datos.id)

    # Verificar que el comprador exista y tenga rol Comprador
    comprador = (
        db.query(models.Usuario)
        .join(models.Rol, models.Usuario.rol_id == models.Rol.id)
        .filter(
            models.Usuario.id == datos.comprador_id,
            models.Rol.nombre == "Comprador",
        )
        .first()
    )
    if not comprador:
        return respuesta_error(
            f"No se encontró un comprador con id {datos.comprador_id}",
            status_code=404,
        )

    # Verificar que el lote exista y esté activo
    lote = db.query(models.Lote).filter(models.Lote.id == datos.lote_id).first()
    if not lote:
        return respuesta_error(
            f"No se encontró un lote con id {datos.lote_id}",
            status_code=404,
        )
    if lote.estado != "Activo":
        return respuesta_error(
            f"El lote {datos.lote_id} está inactivo y no acepta reservas",
            status_code=400,
        )

    # Verificar stock disponible (cantidad - kg_reservados)
    disponible = lote.cantidad - lote.kg_reservados
    if disponible < datos.cantidad:
        raise ErrorStockInsuficiente(lote.producto, datos.cantidad, disponible)

    # Descontar del lote y aumentar kg_reservados
    lote.kg_reservados += datos.cantidad

    # Crear la reserva con estado inicial Pendiente
    nueva_reserva = models.Reserva(
        id=datos.id,
        comprador_id=datos.comprador_id,
        lote_id=datos.lote_id,
        cantidad=datos.cantidad,
        estado="Pendiente",
    )
    db.add(nueva_reserva)

    # Registrar en historial de reservas (bitácora)
    db.add(models.HistorialReserva(reserva_id=datos.id, estado="Pendiente"))

    # Registrar en historial de seguimiento del lote
    db.add(models.HistorialSeguimiento(
        accion="Reserva creada",
        lote=lote.id,
        producto=lote.producto,
    ))

    db.commit()
    db.refresh(nueva_reserva)

    return respuesta_ok(
        message="Reserva creada correctamente",
        data=_serializar_reserva(nueva_reserva),
        status_code=201,
    )


# ── PUT /reservas/{id}/estado ─────────────────────────────────────────────────
# Actualiza comprador_id, fecha y/o estado de una reserva. Registra en historial si cambia estado.

def actualizar_estado_reserva(
    id: int,
    datos: ReservaEditar,
    db: Session = Depends(get_db),
):
    if id <= 0:
        return respuesta_error("El id debe ser un número positivo", status_code=400)

    reserva = db.query(models.Reserva).filter(models.Reserva.id == id).first()
    if not reserva:
        raise ErrorReservaNoEncontrada(id)

    # Cambio de comprador
    if datos.comprador_id is not None:
        comprador = (
            db.query(models.Usuario)
            .join(models.Rol, models.Usuario.rol_id == models.Rol.id)
            .filter(
                models.Usuario.id == datos.comprador_id,
                models.Rol.nombre == "Comprador",
            )
            .first()
        )
        if not comprador:
            return respuesta_error(
                f"No se encontró un comprador activo con id {datos.comprador_id}",
                status_code=404,
            )
        reserva.comprador_id = datos.comprador_id

    # Cambio de fecha
    if datos.fecha is not None:
        reserva.fecha = datos.fecha

    # Cambio de estado con lógica de stock
    if datos.estado is not None:
        estado_anterior = reserva.estado

        if datos.estado == "Cancelada" and estado_anterior != "Cancelada":
            reserva.lote.kg_reservados = max(0, reserva.lote.kg_reservados - reserva.cantidad)

        if estado_anterior == "Cancelada" and datos.estado != "Cancelada":
            disponible = reserva.lote.cantidad - reserva.lote.kg_reservados
            if disponible < reserva.cantidad:
                raise ErrorStockInsuficiente(reserva.lote.producto, reserva.cantidad, disponible)
            reserva.lote.kg_reservados += reserva.cantidad

        # Al pasar a "Entregada" se generan automáticamente la compra y la venta
        if datos.estado == "Entregada" and estado_anterior != "Entregada":
            lote = reserva.lote
            total = (lote.precio_kg * reserva.cantidad) if lote.precio_kg else None

            db.add(models.Compra(
                id=_siguiente_id(db, models.Compra),
                comprador_id=reserva.comprador_id,
                lote_id=lote.id,
                cantidad=reserva.cantidad,
                total=total,
            ))
            db.add(models.Venta(
                id=_siguiente_id(db, models.Venta),
                vendedor_id=lote.productor_id,
                lote_id=lote.id,
                cantidad=reserva.cantidad,
                total=total,
            ))

        reserva.estado = datos.estado
        db.add(models.HistorialReserva(reserva_id=id, estado=datos.estado))

    db.commit()
    db.refresh(reserva)

    return respuesta_ok(
        message="Reserva actualizada",
        data=_serializar_reserva(reserva),
    )


# ── DELETE /reservas/{id} ─────────────────────────────────────────────────────
# Elimina una reserva. Solo se permite si el estado es 'Cancelada'.

def eliminar_reserva(
    id: int,
    confirmar: bool = Query(default=False, description="Debe ser true para confirmar la eliminación"),
    db: Session = Depends(get_db),
):
    if id <= 0:
        return respuesta_error("El id debe ser un número positivo", status_code=400)

    if not confirmar:
        return respuesta_error(
            "Debe confirmar la eliminación con ?confirmar=true",
            status_code=400,
        )

    reserva = db.query(models.Reserva).filter(models.Reserva.id == id).first()
    if not reserva:
        raise ErrorReservaNoEncontrada(id)

    if reserva.estado != "Cancelada":
        raise ErrorReservaNoEliminable(id, reserva.estado)

    producto  = reserva.lote.producto
    comprador = reserva.comprador.nombre

    db.delete(reserva)
    db.commit()

    return respuesta_ok(
        message="Reserva eliminada correctamente",
        data={"id": id, "producto": producto, "comprador": comprador},
    )