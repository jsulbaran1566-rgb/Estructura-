from fastapi import APIRouter
from Controladores.controladores_lotes import (
    obtener_lotes,
    obtener_lote_por_id_y_categoria,
    agregar_lote,
    editar_lote,
)

router = APIRouter(prefix="/lotes", tags=["Lotes"])

router.get("")(obtener_lotes)
router.get("/{id}/categoria/{categoria}")(obtener_lote_por_id_y_categoria)
router.post("")(agregar_lote)
router.put("/{id}/producto/{nuevo_producto}")(editar_lote)