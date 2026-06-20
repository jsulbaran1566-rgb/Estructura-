from fastapi import Query, Depends
from sqlalchemy.orm import Session
from Conexion.database import get_db
import Modelos.models as models
from Excepciones.excepciones_reservas import (
    ErrorReservaNoEncontrada,
    ErrorReservaYaExiste,
    ErrorStockInsuficiente,
    ErrorEstadoInvalido,
)
from respuesta import respuesta_ok, respuesta_error
from Esquemas.Esquemas import ReservaCrear

ESTADOS_VALIDOS = ["Pendiente", "Confirmada", "Entregada", "Cancelada"]


def _estado_actual(reserva: models.Reserva) -> str:
    """Estado más reciente de la reserva según su historial (historial_reservas)."""
    if reserva.historial_estados:
        return reserva.historial_estados[-1].estado
    return "Pendiente"


def _serializar_reserva(r: models.Reserva) -> dict:
    return {
        "id": r.id,
        "comprador_id": r.comprador_id,
        "comprador": r.comprador.nombre,
        "lote_id": r.lote_id,
        "producto": r.lote.producto,
        "cantidad": r.cantidad,
        "fecha": r.fecha,
        "estado": _estado_actual(r),
    }


def obtener_reservas(db: Session = Depends(get_db)):
    reservas = db.query(models.Reserva).all()
    return respuesta_ok(
        message="Reservas obtenidas",
        data=[_serializar_reserva(r) for r in reservas],
    )


def obtener_reserva(
    id: int,
    comprador: int,
    fecha:  str = Query(default=None, description="Filtrar por fecha (yyyy-mm-dd)"),
    estado: str = Query(default=None, description=f"Filtrar por estado: {ESTADOS_VALIDOS}"),
    db: Session = Depends(get_db),
):
    # NOTA: el segmento de ruta sigue llamándose "comprador" (definido en rutas_reservas.py),
    # pero ahora representa comprador_id (entero, FK a compradores.id), no un nombre.
    if id <= 0:
        return respuesta_error("El id debe ser un número positivo", status_code=400)

    if estado and estado not in ESTADOS_VALIDOS:
        raise ErrorEstadoInvalido(estado, ESTADOS_VALIDOS)

    resultado = db.query(models.Reserva).filter(
        models.Reserva.id == id,
        models.Reserva.comprador_id == comprador
    ).all()

    if fecha:
        resultado = [r for r in resultado if r.fecha == fecha]

    if estado:
        resultado = [r for r in resultado if _estado_actual(r) == estado]

    if not resultado:
        raise ErrorReservaNoEncontrada(id, comprador)

    return respuesta_ok(
        message="Reserva obtenida",
        data=[_serializar_reserva(r) for r in resultado],
    )


def crear_reserva(
    id: int,
    comprador: int,
    datos: ReservaCrear,
    db: Session = Depends(get_db),
):
    # "comprador" = comprador_id (ver nota en obtener_reserva)
    if id <= 0:
        return respuesta_error("El id debe ser un número positivo", status_code=400)

    if datos.cantidad < 1:
        return respuesta_error("La cantidad mínima a reservar es 1", status_code=400)

    if db.query(models.Reserva).filter(models.Reserva.id == id).first():
        raise ErrorReservaYaExiste(id)

    comprador_obj = db.query(models.Comprador).filter(models.Comprador.id == comprador).first()
    if not comprador_obj:
        return respuesta_error(f"No se encontró un comprador con id {comprador}", status_code=404)

    lote = db.query(models.Lote).filter(models.Lote.id == datos.lote_id).first()
    if not lote:
        return respuesta_error(f"No se encontró un lote con id {datos.lote_id}", status_code=404)

    if lote.cantidad < datos.cantidad:
        raise ErrorStockInsuficiente(lote.producto, datos.cantidad, lote.cantidad)

    lote.cantidad -= datos.cantidad

    nueva_reserva = models.Reserva(id=id, comprador_id=comprador, lote_id=lote.id, cantidad=datos.cantidad)
    db.add(nueva_reserva)

    db.add(models.HistorialSeguimiento(accion="Compra realizada", lote=lote.id, producto=lote.producto))
    db.add(models.Compra(id=id, comprador_id=comprador, lote_id=lote.id, cantidad=datos.cantidad))
    # vendedor_id = productor dueño del lote (antes se guardaba erróneamente el comprador)
    db.add(models.Venta(id=id, vendedor_id=lote.productor_id, lote_id=lote.id, cantidad=datos.cantidad))
    db.add(models.HistorialReserva(reserva_id=id, estado="Pendiente"))

    db.commit()
    db.refresh(nueva_reserva)
    return respuesta_ok(
        message="Reserva creada correctamente",
        data={
            "id": nueva_reserva.id,
            "comprador_id": nueva_reserva.comprador_id,
            "comprador": comprador_obj.nombre,
            "lote_id": nueva_reserva.lote_id,
            "producto": lote.producto,
            "cantidad": nueva_reserva.cantidad,
            "fecha": nueva_reserva.fecha,
            "estado": "Pendiente",
        },
        status_code=201,
    )
