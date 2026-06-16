from fastapi import Query, Depends
from sqlalchemy.orm import Session
from Conexion.database import get_db
import Modelos.models as models
from Excepciones.excepciones_reservas import (
    ErrorReservaNoEncontrada,
    ErrorReservaYaExiste,
    ErrorStockInsuficiente,
    ErrorProductoNoEncontrado,
    ErrorEstadoInvalido,
)
from scr.Utilidades.respuesta import respuesta_ok, respuesta_error
from Esquemas.Esquemas import ReservaCrear


def obtener_reservas(db: Session = Depends(get_db)):
    reservas = db.query(models.Reserva).all()
    return respuesta_ok(
        message="Reservas obtenidas",
        data=[{"id": r.id, "comprador": r.comprador, "producto": r.producto, "cantidad": r.cantidad} for r in reservas],
    )


def obtener_reserva(
    id: int,
    comprador: str,
    fecha:  str = Query(default=None, description="Filtrar por fecha (dd/mm/aaaa)"),
    estado: str = Query(default=None, description="Filtrar por estado: activa | cancelada"),
    db: Session = Depends(get_db),
):
    if id <= 0:
        return respuesta_error("El id debe ser un número positivo", status_code=400)

    estados_validos = ["activa", "cancelada"]
    if estado and estado not in estados_validos:
        raise ErrorEstadoInvalido(estado, estados_validos)

    resultado = db.query(models.Reserva).filter(
        models.Reserva.id == id,
        models.Reserva.comprador.ilike(comprador)
    ).all()

    if fecha:
        resultado = [r for r in resultado if r.fecha == fecha]

    if not resultado:
        raise ErrorReservaNoEncontrada(id, comprador)

    return respuesta_ok(
        message="Reserva obtenida",
        data=[{"id": r.id, "comprador": r.comprador, "producto": r.producto, "cantidad": r.cantidad} for r in resultado],
    )


def crear_reserva(
    id: int,
    comprador: str,
    datos: ReservaCrear,
    db: Session = Depends(get_db),
):
    if id <= 0:
        return respuesta_error("El id debe ser un número positivo", status_code=400)

    if datos.cantidad < 1:
        return respuesta_error("La cantidad mínima a reservar es 1", status_code=400)

    if db.query(models.Reserva).filter(models.Reserva.id == id).first():
        raise ErrorReservaYaExiste(id)

    lote = db.query(models.Lote).filter(models.Lote.producto.ilike(datos.producto)).first()
    if not lote:
        raise ErrorProductoNoEncontrado(datos.producto)

    if lote.cantidad < datos.cantidad:
        raise ErrorStockInsuficiente(datos.producto, datos.cantidad, lote.cantidad)

    lote.cantidad -= datos.cantidad

    nueva_reserva = models.Reserva(id=id, comprador=comprador, producto=datos.producto, cantidad=datos.cantidad)
    db.add(nueva_reserva)

    db.add(models.HistorialSeguimiento(accion="Compra realizada", lote=lote.id, producto=datos.producto))
    db.add(models.Compra(id=id, comprador=comprador, producto=datos.producto, cantidad=datos.cantidad))
    db.add(models.Venta(id=id, comprador=comprador, producto=datos.producto, cantidad=datos.cantidad))
    db.add(models.HistorialReserva(comprador=comprador, producto=datos.producto, cantidad=datos.cantidad))

    db.commit()
    db.refresh(nueva_reserva)
    return respuesta_ok(
        message="Reserva creada correctamente",
        data={
            "id": nueva_reserva.id,
            "comprador": nueva_reserva.comprador,
            "producto": nueva_reserva.producto,
            "cantidad": nueva_reserva.cantidad,
        },
        status_code=201,
    )