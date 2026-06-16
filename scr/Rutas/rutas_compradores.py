from fastapi import APIRouter
from Controladores.controladores_compradores import (
    obtener_compradores,
    obtener_comprador_por_id_y_ciudad,
    agregar_comprador,
    eliminar_comprador,
)

router = APIRouter(prefix="/compradores", tags=["Compradores"])

router.get("")(obtener_compradores)
router.get("/{id}/ciudad/{ciudad}")(obtener_comprador_por_id_y_ciudad)
router.post("")(agregar_comprador)
router.delete("/{id}/ciudad/{ciudad}")(eliminar_comprador)