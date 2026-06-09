from pydantic import BaseModel
from typing import Optional


# ================================================================
# USUARIOS
# ================================================================

class UsuarioCrear(BaseModel):
    id: int
    nombre: str
    rol: str

class UsuarioEditar(BaseModel):
    nombre: Optional[str] = None
    activo: Optional[bool] = True


# ================================================================
# LOTES
# ================================================================

class LoteCrear(BaseModel):
    id: int
    producto: str
    cantidad: int
    categoria: str

class LoteEditar(BaseModel):
    cantidad: Optional[int] = None
    categoria: Optional[str] = None


# ================================================================
# COMPRADORES
# ================================================================

class CompradorCrear(BaseModel):
    id: int
    nombre: str
    ciudad: str


# ================================================================
# RESERVAS
# ================================================================

class ReservaCrear(BaseModel):
    producto: str
    cantidad: int


# ================================================================
# CATEGORIAS
# ================================================================

class CategoriaCrear(BaseModel):
    nombre: str