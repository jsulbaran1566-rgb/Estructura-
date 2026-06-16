from fastapi import Query, Depends
from sqlalchemy.orm import Session
from Conexion.database import get_db
import Modelos.models as models
from Excepciones.excepciones_usuarios import (
    ErrorUsuarioNoExiste,
    ErrorUsuarioYaExiste,
    ErrorRolInvalido,
)
from Utilidades.respuesta import respuesta_ok, respuesta_error
from Esquemas.Esquemas import UsuarioCrear, UsuarioEditar


def obtener_usuarios(db: Session = Depends(get_db)):
    usuarios = db.query(models.Usuario).all()
    return respuesta_ok(
        message="Usuarios obtenidos",
        data=[{"id": u.id, "nombre": u.nombre, "rol": u.rol} for u in usuarios],
    )


def obtener_usuario_por_id(
    id: int,
    db: Session = Depends(get_db),
):
    if id <= 0:
        return respuesta_error("El id debe ser un número positivo", status_code=400)

    usuario = db.query(models.Usuario).filter(models.Usuario.id == id).first()
    if not usuario:
        raise ErrorUsuarioNoExiste(id)

    return respuesta_ok(
        message="Usuario obtenido",
        data={"id": usuario.id, "nombre": usuario.nombre, "rol": usuario.rol},
    )


def obtener_usuario_por_id_y_rol(
    id: int,
    rol: str,
    activo: bool = Query(default=True, description="Filtrar usuarios activos o inactivos"),
    db: Session = Depends(get_db),
):
    if id <= 0:
        return respuesta_error("El id debe ser un número positivo", status_code=400)

    roles_validos = ["Productor", "Comprador", "Administrador"]
    if rol not in roles_validos:
        raise ErrorRolInvalido(rol, roles_validos)

    resultado = db.query(models.Usuario).filter(
        models.Usuario.id == id,
        models.Usuario.rol == rol
    ).all()

    if not resultado:
        raise ErrorUsuarioNoExiste(id)

    return respuesta_ok(
        message="Usuario obtenido",
        data={
            "activo": activo,
            "usuarios": [{"id": u.id, "nombre": u.nombre, "rol": u.rol} for u in resultado],
        },
    )


def agregar_usuario(
    datos: UsuarioCrear,
    db: Session = Depends(get_db),
):
    roles_validos = ["Productor", "Comprador", "Administrador"]
    if datos.rol not in roles_validos:
        raise ErrorRolInvalido(datos.rol, roles_validos)

    if db.query(models.Usuario).filter(models.Usuario.id == datos.id).first():
        raise ErrorUsuarioYaExiste(datos.id)

    nuevo = models.Usuario(id=datos.id, nombre=datos.nombre, rol=datos.rol)
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return respuesta_ok(
        message="Usuario registrado",
        data={"id": nuevo.id, "nombre": nuevo.nombre, "rol": nuevo.rol},
        status_code=201,
    )


def editar_usuario(
    id: int,
    nuevo_rol: str,
    datos: UsuarioEditar,
    db: Session = Depends(get_db),
):
    if id <= 0:
        return respuesta_error("El id debe ser un número positivo", status_code=400)

    roles_validos = ["Productor", "Comprador", "Administrador"]
    if nuevo_rol not in roles_validos:
        raise ErrorRolInvalido(nuevo_rol, roles_validos)

    usuario = db.query(models.Usuario).filter(models.Usuario.id == id).first()
    if not usuario:
        raise ErrorUsuarioNoExiste(id)

    usuario.rol = nuevo_rol
    if datos.nombre:
        usuario.nombre = datos.nombre

    db.commit()
    db.refresh(usuario)
    return respuesta_ok(
        message="Usuario actualizado",
        data={"activo": datos.activo, "id": usuario.id, "nombre": usuario.nombre, "rol": usuario.rol},
    )