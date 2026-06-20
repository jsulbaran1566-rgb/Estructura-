from fastapi import Query, Depends
from sqlalchemy.orm import Session
from Conexion.database import get_db
import Modelos.models as models
from Excepciones.excepciones_compradores import (
    ErrorCompradorNoEncontrado,
    ErrorCompradorYaExiste,
    ErrorConfirmacionRequerida,
    ErrorIdInvalido,
)
from respuesta import respuesta_ok, respuesta_error
from Esquemas.Esquemas import CompradorCrear


def obtener_compradores(db: Session = Depends(get_db)):
    compradores = db.query(models.Comprador).all()
    return respuesta_ok(
        message="Compradores obtenidos",
        data=[{"id": c.id, "nombre": c.nombre, "ciudad": c.ciudad} for c in compradores],
    )


def obtener_comprador_por_id_y_ciudad(
    id: int,
    ciudad: str,
    limite: int = Query(default=10, ge=1, le=100, description="Número máximo de resultados"),
    orden:  str = Query(default="nombre",          description="Campo para ordenar: nombre | ciudad"),
    db: Session = Depends(get_db),
):
    if id <= 0:
        raise ErrorIdInvalido()

    campos_validos = ["nombre", "ciudad"]
    if orden not in campos_validos:
        return respuesta_error(f"orden debe ser uno de: {campos_validos}", status_code=400)

    resultado = db.query(models.Comprador).filter(
        models.Comprador.id == id,
        models.Comprador.ciudad.ilike(ciudad)
    ).all()

    if not resultado:
        raise ErrorCompradorNoEncontrado(id, ciudad)

    ordenado = sorted(resultado, key=lambda x: getattr(x, orden))[:limite]
    return respuesta_ok(
        message="Comprador obtenido",
        data=[{"id": c.id, "nombre": c.nombre, "ciudad": c.ciudad} for c in ordenado],
    )


def agregar_comprador(
    datos: CompradorCrear,
    db: Session = Depends(get_db),
):
    # compradores.id es FK a usuarios.id: el usuario debe existir y tener rol 'Comprador'
    usuario = db.query(models.Usuario).filter(models.Usuario.id == datos.id).first()
    if not usuario:
        return respuesta_error(
            f"No existe un usuario con id {datos.id}. Debe registrarse primero como usuario.",
            status_code=404,
        )
    if usuario.rol != "Comprador":
        return respuesta_error(
            f"El usuario {datos.id} tiene rol '{usuario.rol}', no 'Comprador'.",
            status_code=400,
        )

    if db.query(models.Comprador).filter(models.Comprador.id == datos.id).first():
        raise ErrorCompradorYaExiste(datos.id)

    nuevo = models.Comprador(id=datos.id, nombre=datos.nombre, ciudad=datos.ciudad)
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return respuesta_ok(
        message="Comprador agregado",
        data={"id": nuevo.id, "nombre": nuevo.nombre, "ciudad": nuevo.ciudad},
        status_code=201,
    )


def eliminar_comprador(
    id: int,
    ciudad: str,
    confirmar: bool = Query(default=False, description="Debe ser true para confirmar la eliminación"),
    notificar: bool = Query(default=False, description="Simula notificación al comprador eliminado"),
    db: Session = Depends(get_db),
):
    if id <= 0:
        raise ErrorIdInvalido()
    if not confirmar:
        raise ErrorConfirmacionRequerida()

    comprador = db.query(models.Comprador).filter(
        models.Comprador.id == id,
        models.Comprador.ciudad.ilike(ciudad)
    ).first()

    if not comprador:
        raise ErrorCompradorNoEncontrado(id, ciudad)

    nombre = comprador.nombre
    db.delete(comprador)
    db.commit()

    mensaje = "Comprador eliminado"
    if notificar:
        mensaje += f" — notificación enviada a {nombre}"
    return respuesta_ok(message=mensaje, data={"id": id, "nombre": nombre})
