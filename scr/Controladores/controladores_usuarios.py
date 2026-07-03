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
from Utilidades.seguridad import hashear_clave
from Esquemas.Esquemas import UsuarioCrear, UsuarioEditar, ESTADOS_VALIDOS


# ── Helper ────────────────────────────────────────────────────────────────────

def _serializar_usuario(u: models.Usuario) -> dict:
    return {
        "id":             u.id,
        "tipo_documento": u.tipo_documento,
        "nombre":         u.nombre,
        "correo":         u.correo,
        "telefono":       u.telefono,
        "direccion":      u.direccion,
        "ciudad":         u.ciudad,
        "empresa":        u.empresa,
        "rol_id":         u.rol_id,
        "rol":            u.rol_rel.nombre if u.rol_rel else None,
        "estado":         u.estado,
        "fecha_registro": str(u.fecha_registro),
    }


# ── GET /usuarios ─────────────────────────────────────────────────────────────
# Lista todos los usuarios. Permite filtrar por rol y/o estado.

def obtener_usuarios(
    rol_id: int = Query(default=None, description="Filtrar por id de rol"),
    estado: str = Query(default=None, description="Filtrar por estado: Activo | Inactivo"),
    db: Session = Depends(get_db),
):
    query = db.query(models.Usuario)

    if rol_id:
        query = query.filter(models.Usuario.rol_id == rol_id)
    if estado:
        query = query.filter(models.Usuario.estado == estado)

    usuarios = query.all()
    return respuesta_ok(
        message="Usuarios obtenidos",
        data=[_serializar_usuario(u) for u in usuarios],
    )


# ── GET /usuarios/compradores ─────────────────────────────────────────────────
# Lista todos los usuarios con rol Comprador.

def obtener_compradores(
    estado: str = Query(default=None, description="Filtrar por estado: Activo | Inactivo"),
    db: Session = Depends(get_db),
):
    query = (
        db.query(models.Usuario)
        .join(models.Rol, models.Usuario.rol_id == models.Rol.id)
        .filter(models.Rol.nombre == "Comprador")
    )
    if estado:
        query = query.filter(models.Usuario.estado == estado)

    compradores = query.all()
    return respuesta_ok(
        message="Compradores obtenidos",
        data=[_serializar_usuario(u) for u in compradores],
    )


# ── GET /usuarios/{nombre} ───────────────────────────────────────────────────
# Obtiene usuario(s) cuyo nombre coincida (búsqueda parcial, insensible a mayúsculas).

def obtener_usuario_por_nombre(
    nombre: str,
    db: Session = Depends(get_db),
):
    if not nombre.strip():
        return respuesta_error("El nombre no puede estar vacío", status_code=400)

    usuarios = (
        db.query(models.Usuario)
        .filter(models.Usuario.nombre.ilike(f"%{nombre.strip()}%"))
        .all()
    )
    if not usuarios:
        return respuesta_error(f"No se encontró ningún usuario con nombre '{nombre}'", status_code=404)

    return respuesta_ok(
        message="Usuario(s) obtenido(s)",
        data=[_serializar_usuario(u) for u in usuarios],
    )


# ── GET /usuarios/productores ─────────────────────────────────────────────────
# Lista todos los usuarios con rol Productor.

def obtener_productores(
    estado: str = Query(default=None, description="Filtrar por estado: Activo | Inactivo"),
    db: Session = Depends(get_db),
):
    query = (
        db.query(models.Usuario)
        .join(models.Rol, models.Usuario.rol_id == models.Rol.id)
        .filter(models.Rol.nombre == "Productor")
    )
    if estado:
        query = query.filter(models.Usuario.estado == estado)

    productores = query.all()
    return respuesta_ok(
        message="Productores obtenidos",
        data=[_serializar_usuario(u) for u in productores],
    )


# ── POST /usuarios ────────────────────────────────────────────────────────────
# Registra un nuevo usuario en el sistema.

def agregar_usuario(
    datos: UsuarioCrear,
    db: Session = Depends(get_db),
):
    if db.query(models.Usuario).filter(models.Usuario.id == datos.id).first():
        raise ErrorUsuarioYaExiste(datos.id)

    if db.query(models.Usuario).filter(models.Usuario.correo == datos.correo).first():
        return respuesta_error(
            f"Ya existe un usuario con el correo '{datos.correo}'",
            status_code=400,
        )

    if db.query(models.Usuario).filter(models.Usuario.telefono == datos.telefono).first():
        return respuesta_error(
            f"Ya existe un usuario con el teléfono '{datos.telefono}'",
            status_code=400,
        )

    tipo_doc = db.query(models.TipoDocumento).filter(models.TipoDocumento.codigo == datos.tipo_documento).first()
    if not tipo_doc:
        return respuesta_error(f"No existe un tipo de documento con código '{datos.tipo_documento}'", status_code=400)

    rol = db.query(models.Rol).filter(models.Rol.id == datos.rol_id).first()
    if not rol:
        return respuesta_error(f"No existe un rol con id {datos.rol_id}", status_code=400)

    nuevo = models.Usuario(
        id=datos.id,
        tipo_documento=datos.tipo_documento,
        nombre=datos.nombre,
        correo=datos.correo,
        telefono=datos.telefono,
        clave=hashear_clave(datos.clave),
        direccion=datos.direccion,
        ciudad=datos.ciudad,
        empresa=datos.empresa,
        rol_id=datos.rol_id,
        estado=datos.estado,
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)

    return respuesta_ok(
        message="Usuario registrado",
        data=_serializar_usuario(nuevo),
        status_code=201,
    )


# ── PUT /usuarios/{id} ───────────────────────────────────────────────────────
# Actualiza nombre, teléfono, dirección, ciudad, rol y/o estado de un usuario.

def editar_usuario(
    id: int,
    datos: UsuarioEditar,
    db: Session = Depends(get_db),
):
    if id <= 0:
        return respuesta_error("El id debe ser un número positivo", status_code=400)

    usuario = db.query(models.Usuario).filter(models.Usuario.id == id).first()
    if not usuario:
        raise ErrorUsuarioNoExiste(id)

    if datos.tipo_documento is not None:
        tipo_doc = db.query(models.TipoDocumento).filter(models.TipoDocumento.codigo == datos.tipo_documento).first()
        if not tipo_doc:
            return respuesta_error(f"No existe un tipo de documento con código '{datos.tipo_documento}'", status_code=400)
        usuario.tipo_documento = datos.tipo_documento
    if datos.nombre is not None:
        usuario.nombre = datos.nombre
    if datos.correo is not None:
        duplicado = db.query(models.Usuario).filter(
            models.Usuario.correo == datos.correo,
            models.Usuario.id != id,
        ).first()
        if duplicado:
            return respuesta_error(
                f"Ya existe un usuario con el correo '{datos.correo}'",
                status_code=400,
            )
        usuario.correo = datos.correo
    if datos.clave is not None:
        usuario.clave = hashear_clave(datos.clave)
    if datos.telefono is not None:
        duplicado = db.query(models.Usuario).filter(
            models.Usuario.telefono == datos.telefono,
            models.Usuario.id != id,
        ).first()
        if duplicado:
            return respuesta_error(
                f"Ya existe un usuario con el teléfono '{datos.telefono}'",
                status_code=400,
            )
        usuario.telefono = datos.telefono
    if datos.direccion is not None:
        usuario.direccion = datos.direccion
    if datos.ciudad is not None:
        usuario.ciudad = datos.ciudad
    if datos.rol_id is not None:
        rol = db.query(models.Rol).filter(models.Rol.id == datos.rol_id).first()
        if not rol:
            return respuesta_error(f"No existe un rol con id {datos.rol_id}", status_code=400)
        usuario.rol_id = datos.rol_id
    if datos.estado is not None:
        usuario.estado = datos.estado

    db.commit()
    db.refresh(usuario)

    return respuesta_ok(
        message="Usuario actualizado",
        data=_serializar_usuario(usuario),
    )


# ── DELETE /usuarios/{id} ─────────────────────────────────────────────────────
# Elimina un usuario del sistema.

def eliminar_usuario(
    id: int,
    confirmar: bool = Query(default=False, description="Debe ser true para confirmar la eliminación"),
    db: Session = Depends(get_db),
):
    if id <= 0:
        return respuesta_error("El id debe ser un número positivo", status_code=400)

    if not confirmar:
        return respuesta_error("Debe confirmar la eliminación con ?confirmar=true", status_code=400)

    usuario = db.query(models.Usuario).filter(models.Usuario.id == id).first()
    if not usuario:
        raise ErrorUsuarioNoExiste(id)

    # Verificar que no sea productor con lotes activos
    lotes_activos = db.query(models.Lote).filter(
        models.Lote.productor_id == id,
        models.Lote.estado == "Activo",
    ).count()

    if lotes_activos > 0:
        return respuesta_error(
            f"El usuario {id} tiene {lotes_activos} lote(s) activo(s). Desactívelos primero.",
            status_code=409,
        )

    nombre = usuario.nombre
    db.delete(usuario)
    db.commit()

    return respuesta_ok(
        message="Usuario eliminado",
        data={"id": id, "nombre": nombre},
    )