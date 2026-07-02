from fastapi import Depends
from sqlalchemy.orm import Session
from Conexion.database import get_db
import Modelos.models as models
from Esquemas.Esquemas import LoginEntrada
from Excepciones.excepciones_auth import ErrorCredencialesInvalidas
from Utilidades.respuesta import respuesta_ok
from Utilidades.seguridad import verificar_clave, crear_token


# ── POST /auth/login ─────────────────────────────────────────────────────────
# Recibe correo y clave, verifica contra la base de datos y devuelve un token.

def iniciar_sesion(
    datos: LoginEntrada,
    db: Session = Depends(get_db),
):
    # 1. Buscar el usuario por correo
    usuario = db.query(models.Usuario).filter(models.Usuario.correo == datos.correo).first()

    # 2. Si no existe, o la clave no coincide, o esta inactivo -> mismo error
    #    (no decimos cual de las tres cosas fallo, por seguridad)
    if not usuario or not verificar_clave(datos.clave, usuario.clave):
        raise ErrorCredencialesInvalidas()

    if usuario.estado != "Activo":
        raise ErrorCredencialesInvalidas()

    # 3. Crear el token con los datos minimos necesarios
    token = crear_token({
        "sub":    str(usuario.id),
        "correo": usuario.correo,
        "rol":    usuario.rol_rel.nombre if usuario.rol_rel else None,
    })

    # 4. Responder con el token y los datos basicos del usuario
    return respuesta_ok(
        message="Inicio de sesión exitoso",
        data={
            "token": token,
            "usuario": {
                "id":     usuario.id,
                "nombre": usuario.nombre,
                "correo": usuario.correo,
                "rol":    usuario.rol_rel.nombre if usuario.rol_rel else None,
            },
        },
    )