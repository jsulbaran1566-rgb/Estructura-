# Utilidades de seguridad — manejo de claves (bcrypt) y tokens de sesion (JWT)
# pip install passlib[bcrypt] python-jose[cryptography]

from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import jwt, JWTError

# 1. Configuracion del algoritmo de hash para las claves
contexto_clave = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 2. Configuracion del token JWT
#    En un proyecto real esto NO deberia ir escrito aqui, deberia venir de una
#    variable de entorno. Para el nivel de esta entrega lo dejamos simple.
CLAVE_SECRETA = "agrodirecto_clave_secreta_2026"
ALGORITMO = "HS256"
MINUTOS_EXPIRACION_TOKEN = 120  # el token dura 2 horas


# ── Claves ────────────────────────────────────────────────────────────────────

def hashear_clave(clave_plana: str) -> str:
    """Convierte una clave en texto plano a un hash bcrypt para guardar en la BD."""
    return contexto_clave.hash(clave_plana)


def verificar_clave(clave_plana: str, clave_hasheada: str) -> bool:
    """Compara una clave escrita por el usuario contra el hash guardado en la BD."""
    return contexto_clave.verify(clave_plana, clave_hasheada)


# ── Token JWT ─────────────────────────────────────────────────────────────────

def crear_token(datos: dict) -> str:
    """Crea un token JWT firmado con los datos del usuario (id, correo, rol)."""
    datos_token = datos.copy()
    expira = datetime.utcnow() + timedelta(minutes=MINUTOS_EXPIRACION_TOKEN)
    datos_token.update({"exp": expira})
    return jwt.encode(datos_token, CLAVE_SECRETA, algorithm=ALGORITMO)


def leer_token(token: str) -> dict | None:
    """Decodifica un token. Si es invalido o expiro, devuelve None."""
    try:
        return jwt.decode(token, CLAVE_SECRETA, algorithms=[ALGORITMO])
    except JWTError:
        return None