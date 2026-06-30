from fastapi import Depends
from sqlalchemy.orm import Session
from Conexion.database import get_db
import Modelos.models as models
from Utilidades.respuesta import respuesta_ok


def ver_historial_seguimiento(db: Session = Depends(get_db)):
    registros = db.query(models.HistorialSeguimiento).all()
    return respuesta_ok(
        message="Historial de seguimiento obtenido",
        data=[
            {
                "id": r.id,
                "accion": r.accion,
                "lote_id": r.lote,
                "producto": r.producto,
                "fecha": r.fecha.isoformat() if r.fecha else None,
            }
            for r in registros
        ],
    )


def ver_compras(db: Session = Depends(get_db)):
    compras = db.query(models.Compra).all()
    return respuesta_ok(
        message="Compras obtenidas",
        data=[
            {
                "id": c.id,
                "comprador_id": c.comprador_id,
                "comprador": c.comprador.nombre,
                "lote_id": c.lote_id,
                "producto": c.lote.producto,
                "cantidad": c.cantidad,
                "fecha": c.fecha.isoformat() if c.fecha else None,
            }
            for c in compras
        ],
    )


def ver_ventas(db: Session = Depends(get_db)):
    ventas = db.query(models.Venta).all()
    return respuesta_ok(
        message="Ventas obtenidas",
        data=[
            {
                "id": v.id,
                "vendedor_id": v.vendedor_id,
                "vendedor": v.vendedor.nombre,
                "lote_id": v.lote_id,
                "producto": v.lote.producto,
                "cantidad": v.cantidad,
                "fecha": v.fecha.isoformat() if v.fecha else None,
            }
            for v in ventas
        ],
    )


def ver_historial_reservas(db: Session = Depends(get_db)):
    registros = db.query(models.HistorialReserva).all()
    return respuesta_ok(
        message="Historial de reservas obtenido",
        data=[
            {
                "id": r.id,
                "reserva_id": r.reserva_id,
                "comprador": r.reserva_rel.comprador.nombre,
                "producto": r.reserva_rel.lote.producto,
                "estado": r.estado,
                "fecha": r.fecha,
            }
            for r in registros
        ],
    )