from fastapi import APIRouter
from Controladores.controladores_usuarios import (
    obtener_usuarios,
    obtener_compradores,
    obtener_productores,
    obtener_usuario_por_nombre,
    agregar_usuario,
    editar_usuario,
    eliminar_usuario,
)

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

router.get(
    "",
    summary="Listar usuarios",
    description="Obtiene todos los usuarios. Filtros opcionales: rol, estado.",
)(obtener_usuarios)

router.get(
    "/compradores",
    summary="Listar compradores",
    description="Obtiene todos los usuarios con rol Comprador. Filtro opcional: estado.",
)(obtener_compradores)

router.get(
    "/productores",
    summary="Listar productores",
    description="Obtiene todos los usuarios con rol Productor. Filtro opcional: estado.",
)(obtener_productores)

router.get(
    "/{nombre}",
    summary="Buscar usuario por nombre",
    description="Retorna usuario(s) cuyo nombre coincida parcialmente (insensible a mayúsculas).",
)(obtener_usuario_por_nombre)

router.post(
    "",
    summary="Registrar usuario",
    description="Crea un nuevo usuario en el sistema.",
)(agregar_usuario)

router.put(
    "/{id}",
    summary="Editar usuario",
    description="Actualiza nombre, teléfono, dirección, ciudad, rol y/o estado de un usuario.",
)(editar_usuario)

router.delete(
    "/{id}",
    summary="Eliminar usuario",
    description="Elimina un usuario. Requiere ?confirmar=true. Falla si tiene lotes activos.",
)(eliminar_usuario)