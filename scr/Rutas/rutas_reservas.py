from fastapi import APIRouter
from Controladores.controladores_reservas import (
    obtener_reservas,
    obtener_reserva,
    crear_reserva,
)

router = APIRouter(prefix="/reservas", tags=["Reservas"])

router.get("")(obtener_reservas)
router.get("/{id}/comprador/{comprador}")(obtener_reserva)
router.post("/{id}/comprador/{comprador}")(crear_reserva)