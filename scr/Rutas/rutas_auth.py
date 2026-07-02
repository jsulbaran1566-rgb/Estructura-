from fastapi import APIRouter
from Controladores.controladores_auth import iniciar_sesion

router = APIRouter(prefix="/auth", tags=["Autenticación"])

router.post(
    "/login",
    summary="Iniciar sesión",
    description="Valida correo y clave, y devuelve un token JWT junto con los datos del usuario.",
)(iniciar_sesion)