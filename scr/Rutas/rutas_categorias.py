from fastapi import APIRouter
from Controladores.controladores_categorias import (
    obtener_categorias,
    obtener_lotes_por_categoria,
    agregar_categoria,
)

router = APIRouter(prefix="/categorias", tags=["Categorías"])

router.get("")(obtener_categorias)
router.get("/{nombre}/lotes/{cantidad_min}")(obtener_lotes_por_categoria)
router.post("")(agregar_categoria)