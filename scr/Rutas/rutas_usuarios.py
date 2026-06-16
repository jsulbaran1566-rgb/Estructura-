from fastapi import APIRouter
from Controladores.controladores_usuarios import (
    obtener_usuarios,
    obtener_usuario_por_id,
    obtener_usuario_por_id_y_rol,
    agregar_usuario,
    editar_usuario,
)

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

router.get("")(obtener_usuarios)
router.get("/{id}")(obtener_usuario_por_id)
router.get("/{id}/rol/{rol}")(obtener_usuario_por_id_y_rol)
router.post("")(agregar_usuario)
router.put("/{id}/rol/{nuevo_rol}")(editar_usuario)