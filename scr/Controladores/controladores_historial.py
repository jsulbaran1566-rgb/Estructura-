from fastapi import Depends
from sqlalchemy.orm import Session
from Conexion.database import get_db
import Modelos.models as models
from Utilidades.respuesta import respuesta_ok


def ver_historial_seguimiento(db: Session = Depends(get_db)):
    registros = db.query(models.HistorialSeguimiento).all()
    return respuesta_ok(
        message="Historial de seguimiento obtenido",
        data=[{"id": r.id, "accion": r.accion, "lote": r.lote, "producto": r.producto} for r in registros],
    )


def ver_compras(db: Session = Depends(get_db)):
    compras = db.query(models.Compra).all()
    return respuesta_ok(
        message="Compras obtenidas",
        data=[{"id": c.id, "comprador": c.comprador, "producto": c.producto, "cantidad": c.cantidad} for c in compras],
    )


def ver_ventas(db: Session = Depends(get_db)):
    ventas = db.query(models.Venta).all()
    return respuesta_ok(
        message="Ventas obtenidas",
        data=[{"id": v.id, "comprador": v.comprador, "producto": v.producto, "cantidad": v.cantidad} for v in ventas],
    )


def ver_historial_reservas(db: Session = Depends(get_db)):
    registros = db.query(models.HistorialReserva).all()
    return respuesta_ok(
        message="Historial de reservas obtenido",
        data=[{"id": r.id, "comprador": r.comprador, "producto": r.producto, "cantidad": r.cantidad} for r in registros],
    )