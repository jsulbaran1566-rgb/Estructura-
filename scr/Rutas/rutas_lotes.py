from fastapi import APIRouter
from Controladores.controladores_lotes import (
    obtener_lotes,
    obtener_lote_por_producto,
    agregar_lote,
    editar_lote,
    eliminar_lote,
)

router = APIRouter(prefix="/lotes", tags=["Lotes"])

router.get(
    "",
    summary="Listar lotes",
    description="Obtiene todos los lotes. Filtros opcionales: categoria, estado, productor_id.",
)(obtener_lotes)

router.get(
    "/{producto}",
    summary="Buscar lote por nombre de producto",
    description="Retorna lote(s) cuyo nombre de producto coincida parcialmente.",
)(obtener_lote_por_producto)

router.post(
    "",
    summary="Crear lote",
    description="Registra un nuevo lote. El productor_id debe ser un usuario con rol 'Productor'.",
)(agregar_lote)

router.put(
    "/{id}",
    summary="Editar lote",
    description="Actualiza producto, cantidad, categoría, precio_kg, estado y/o fecha_cosecha.",
)(editar_lote)

router.delete(
    "/{id}",
    summary="Eliminar lote",
    description="Elimina un lote. Requiere ?confirmar=true. Falla si tiene reservas activas.",
)(eliminar_lote)