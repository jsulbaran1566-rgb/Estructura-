from fastapi import Query, Depends
from sqlalchemy.orm import Session
from Conexion.database import get_db
import Modelos.models as models
from Excepciones.excepciones_lotes import (
    ErrorLoteNoEncontrado,
    ErrorLoteYaExiste,
    ErrorCantidadInvalida,
    ErrorCategoriaInvalidaEnLote,
)
from respuesta import respuesta_ok, respuesta_error
from Esquemas.Esquemas import LoteCrear, LoteEditar


def obtener_lotes(db: Session = Depends(get_db)):
    lotes = db.query(models.Lote).all()
    return respuesta_ok(
        message="Lotes obtenidos",
        data=[
            {
                "id": l.id,
                "producto": l.producto,
                "cantidad": l.cantidad,
                "categoria": l.categoria,
                "productor_id": l.productor_id,
                "productor": l.productor.nombre,
            }
            for l in lotes
        ],
    )


def obtener_lote_por_id_y_categoria(
    id: int,
    categoria: str,
    cantidad_min: int = Query(default=0,          description="Cantidad mínima disponible"),
    ordenar_por: str  = Query(default="producto",  description="Campo para ordenar: producto | cantidad"),
    db: Session = Depends(get_db),
):
    if id <= 0:
        return respuesta_error("El id debe ser un número positivo", status_code=400)
    if cantidad_min < 0:
        return respuesta_error("cantidad_min no puede ser negativo", status_code=400)

    campos_validos = ["producto", "cantidad"]
    if ordenar_por not in campos_validos:
        return respuesta_error(f"ordenar_por debe ser uno de: {campos_validos}", status_code=400)

    resultado = db.query(models.Lote).filter(
        models.Lote.id == id,
        models.Lote.categoria.ilike(categoria),
        models.Lote.cantidad >= cantidad_min
    ).all()

    if not resultado:
        raise ErrorLoteNoEncontrado(id)

    ordenado = sorted(resultado, key=lambda x: getattr(x, ordenar_por))
    return respuesta_ok(
        message="Lote obtenido",
        data=[
            {
                "id": l.id,
                "producto": l.producto,
                "cantidad": l.cantidad,
                "categoria": l.categoria,
                "productor_id": l.productor_id,
                "productor": l.productor.nombre,
            }
            for l in ordenado
        ],
    )


def agregar_lote(
    datos: LoteCrear,
    db: Session = Depends(get_db),
):
    if db.query(models.Lote).filter(models.Lote.id == datos.id).first():
        raise ErrorLoteYaExiste(datos.id)

    if not db.query(models.Categoria).filter(models.Categoria.nombre == datos.categoria).first():
        raise ErrorCategoriaInvalidaEnLote(datos.categoria)

    if datos.cantidad <= 0:
        raise ErrorCantidadInvalida()

    # lotes.productor_id es FK a usuarios.id: el usuario debe existir y tener rol 'Productor'
    productor = db.query(models.Usuario).filter(models.Usuario.id == datos.productor_id).first()
    if not productor:
        return respuesta_error(f"No existe un usuario con id {datos.productor_id}", status_code=404)
    if productor.rol != "Productor":
        return respuesta_error(
            f"El usuario {datos.productor_id} tiene rol '{productor.rol}', no 'Productor'.",
            status_code=400,
        )

    nuevo = models.Lote(
        id=datos.id,
        producto=datos.producto,
        cantidad=datos.cantidad,
        categoria=datos.categoria,
        productor_id=datos.productor_id,
    )
    db.add(nuevo)

    historial = models.HistorialSeguimiento(accion="Creación de lote", lote=datos.id, producto=datos.producto)
    db.add(historial)

    db.commit()
    db.refresh(nuevo)
    return respuesta_ok(
        message="Lote agregado",
        data={
            "id": nuevo.id,
            "producto": nuevo.producto,
            "cantidad": nuevo.cantidad,
            "categoria": nuevo.categoria,
            "productor_id": nuevo.productor_id,
        },
        status_code=201,
    )


def editar_lote(
    id: int,
    nuevo_producto: str,
    datos: LoteEditar,
    db: Session = Depends(get_db),
):
    if id <= 0:
        return respuesta_error("El id debe ser un número positivo", status_code=400)

    lote = db.query(models.Lote).filter(models.Lote.id == id).first()
    if not lote:
        raise ErrorLoteNoEncontrado(id)

    lote.producto = nuevo_producto
    if datos.cantidad is not None:
        if datos.cantidad <= 0:
            raise ErrorCantidadInvalida()
        lote.cantidad = datos.cantidad
    if datos.categoria:
        lote.categoria = datos.categoria

    db.commit()
    db.refresh(lote)
    return respuesta_ok(
        message="Lote actualizado",
        data={
            "id": lote.id,
            "producto": lote.producto,
            "cantidad": lote.cantidad,
            "categoria": lote.categoria,
            "productor_id": lote.productor_id,
        },
    )
